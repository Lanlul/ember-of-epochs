import json
import re
import logging
from typing import Optional

from ...models.action import LLMOutput
from ...models.world import SceneTags
from ...models.session import Choice

logger = logging.getLogger(__name__)


def _sanitize_json(raw: str) -> str:
    """Fix common LLM JSON errors before parsing."""
    s = raw.strip()

    s = re.sub(r",\s*}", "}", s)
    s = re.sub(r",\s*]", "]", s)

    s = re.sub(r"(?<!\\)'", "\"", s)

    s = re.sub(r"\bNone\b", "null", s)
    s = re.sub(r"\bTrue\b", "true", s)
    s = re.sub(r"\bFalse\b", "false", s)

    s = re.sub(r"//[^\n]*", "", s)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)

    s = re.sub(r"([{,])\s*(\w+)\s*:", r'\1"\2":', s)

    return s


class StructParser:
    def parse(self, raw: str) -> LLMOutput:
        story = self._extract_story(raw)
        visual_prompt = self._extract_visual_prompt(raw)
        options = self._extract_options(raw)

        try:
            cleaned = self._extract_json(story)
        except ValueError:
            return self._parse_text_fallback(raw, visual_prompt, options)

        sanitized = _sanitize_json(cleaned)

        try:
            data = json.loads(sanitized)
        except json.JSONDecodeError as exc:
            logger.error(
                "JSON parse failed. Raw excerpt (first 600):\n%s\n\nSanitized (first 600):\n%s",
                cleaned[:600], sanitized[:600],
            )
            data = self._fallback_parse(cleaned)
            if data is None:
                raise ValueError(
                    f"JSON parse error after sanitization: {exc}\n"
                    f"Raw (first 500): {cleaned[:500]}"
                ) from exc

        choices = []
        for c in data.get("choices", []):
            if "text" not in c or not c.get("text"):
                c["text"] = ""
            if c.get("alignment_delta"):
                c["alignment_delta"] = {
                    k: v for k, v in c["alignment_delta"].items()
                    if v is not None
                }
            choices.append(Choice(**c))

        return LLMOutput(
            narrative=data.get("narrative", ""),
            choices=choices,
            scene_tags=SceneTags(**data.get("scene_tags", {})),
            alignment_delta=data.get("alignment_delta"),
            visual_prompt=visual_prompt,
            options=options,
        )

    def parse_ending(self, raw: str) -> dict:
        story = self._extract_story(raw)
        cleaned = self._extract_json(story)
        sanitized = _sanitize_json(cleaned)
        try:
            return json.loads(sanitized)
        except json.JSONDecodeError as exc:
            data = self._fallback_parse(cleaned)
            if data is None:
                raise ValueError(
                    f"Ending JSON parse error: {exc}\nRaw: {cleaned[:500]}"
                ) from exc
            return data

    def _parse_text_fallback(self, raw: str, visual_prompt: str, options: list) -> LLMOutput:
        """When LLM outputs plain text narrative + tags (no JSON inside <story>)."""
        narrative = raw
        opt_m = re.search(r"<options>", raw)
        vp_m = re.search(r"<visual_prompt>", raw)
        if opt_m:
            narrative = raw[:opt_m.start()].strip()
        elif vp_m:
            narrative = raw[:vp_m.start()].strip()

        choices = []
        for i, opt in enumerate(options):
            choices.append(Choice(id=f"c{i+1}", text=opt, alignment_delta=None))

        return LLMOutput(
            narrative=narrative,
            choices=choices,
            scene_tags=SceneTags(
                setting="",
                mood="",
                lighting="",
                color_palette=[],
                style="ruins_gothic",
                focus="",
                character_state="",
            ),
            alignment_delta=None,
            visual_prompt=visual_prompt,
            options=options,
        )

    def _fallback_parse(self, raw: str) -> Optional[dict]:
        """Try lenient extraction when strict JSON fails."""
        m = re.search(r'"narrative"\s*:\s*"([^"]+)"', raw)
        if not m:
            return None

        narrative = m.group(1)
        choices_raw = re.findall(
            r'"id"\s*:\s*"([^"]+)".*?"text"\s*:\s*"([^"]+)"', raw, re.DOTALL
        )
        choices = []
        for cid, ctext in choices_raw:
            choices.append({"id": cid, "text": ctext, "alignment_delta": None})

        setting = self._grep_field(raw, "setting") or ""
        mood = self._grep_field(raw, "mood") or ""
        lighting = self._grep_field(raw, "lighting") or ""
        style = self._grep_field(raw, "style") or "ruins_gothic"
        focus = self._grep_field(raw, "focus") or ""
        char_state = self._grep_field(raw, "character_state") or ""

        palette_m = re.search(r'"color_palette"\s*:\s*\[(.*?)\]', raw, re.DOTALL)
        colors = []
        if palette_m:
            colors = re.findall(r'"([^"]+)"', palette_m.group(1))

        return {
            "narrative": narrative,
            "choices": choices,
            "scene_tags": {
                "setting": setting,
                "mood": mood,
                "lighting": lighting,
                "color_palette": colors,
                "style": style,
                "focus": focus,
                "character_state": char_state,
            },
            "alignment_delta": None,
        }

    @staticmethod
    def _grep_field(raw: str, field: str) -> Optional[str]:
        m = re.search(rf'"{field}"\s*:\s*"([^"]+)"', raw)
        return m.group(1) if m else None

    def _extract_story(self, raw: str) -> str:
        m = re.search(r"<story>(.*?)</story>", raw, re.DOTALL)
        if m:
            return m.group(1).strip()
        return raw

    def _extract_visual_prompt(self, raw: str) -> str:
        m = re.search(r"<visual_prompt>(.*?)</visual_prompt>", raw, re.DOTALL)
        if m:
            return m.group(1).strip()
        return ""

    def _extract_options(self, raw: str) -> list:
        m = re.search(r"<options>(.*?)</options>", raw, re.DOTALL)
        if m:
            return [p.strip() for p in m.group(1).split("|") if p.strip()]
        return []

    def _extract_json(self, raw: str) -> str:
        raw = raw.strip()

        code_block = re.search(
            r"```(?:json)?\s*\n(.*?)\n```", raw, re.DOTALL
        )
        if code_block:
            return code_block.group(1).strip()

        brace_start = raw.find("{")
        brace_end = raw.rfind("}")
        if brace_start != -1 and brace_end != -1:
            return raw[brace_start : brace_end + 1]

        raise ValueError(
            f"Cannot extract JSON from LLM output:\n{raw[:500]}"
        )
