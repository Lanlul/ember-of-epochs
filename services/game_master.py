import logging
from pathlib import Path
from typing import Dict, Optional, List

from ..config import settings
from ..models.action import ActionResponse, EndingResponse, EndingInfo, ChronicleData, LLMOutput
from ..models.session import Session, Choice
from ..models.world import Alignment, WorldState, SceneTags
from .alignment import AlignmentService
from .llm import PromptGenerator, StructParser, create_provider
from .llm.provider import LLMProvider
from .image import (
    SceneCompiler,
    BigPicklePipeline,
    StyleController,
    GuidanceScheduler,
    ImageCache,
)
from .ending import EndingService, ENDINGS_BY_ID
from .chronicle import ChronicleService
from .script_config import (
    get_chapter_goal,
    get_continent_for_turn,
    get_plot_directive,
    get_stage_config,
    is_final_stage,
    chapter_stage_from_turn,
    EVENT_THEMES,
    TRIGGER_STAGES,
    TRIGGER_PROBABILITY,
)

logger = logging.getLogger(__name__)

OPENING_NARRATIVE = (
    "你睜開眼，身下是冰冷的石台。頭頂的蒼穹裂開一道橫亙天際的傷痕，"
    "流雲在裂縫中緩慢旋轉。空氣中飄浮著金屬與塵土的氣味。"
    "一塊殘破的碑文豎立在石台邊緣，上頭的文字隱約發著微光。"
)

OPENING_CHOICES = [
    Choice(id="c1", text="環顧四周，確認所在位置"),
    Choice(id="c2", text="伸手觸碰碑文上的發光文字"),
    Choice(id="c3", text="閉上眼，嘗試回憶昏迷前的事"),
]

from ..models.world import SceneTags

OPENING_SCENE_TAGS = SceneTags(
    setting="ancient stone platform with broken stele, apocalyptic sky with a massive rift",
    mood="mysterious, solemn",
    lighting="dim ambient light from glowing runes and sky rift",
    color_palette=["dark grey", "pale blue", "golden glow"],
    style="ruins_gothic",
    focus="a cracked stone stele with glowing inscriptions",
    character_state="confused, disoriented",
)


class GameMaster:
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        bigpickle_pipeline: Optional[BigPicklePipeline] = None,
    ):
        self._sessions: Dict[str, Session] = {}
        self._scene_counters: Dict[str, int] = {}

        self._alignment = AlignmentService()
        self._prompt_gen = PromptGenerator()
        self._parser = StructParser()
        self._scene_compiler = SceneCompiler()
        self._style_controller = StyleController()
        self._guidance_scheduler = GuidanceScheduler(
            base_cfg=settings.bigpickle_cfg_scale,
        )
        self._image_cache = ImageCache(
            cache_dir=settings.image_output_dir,
        )

        self._llm: Optional[LLMProvider] = llm_provider
        self._bigpickle: Optional[BigPicklePipeline] = bigpickle_pipeline
        self._ending_service = EndingService()
        self._chronicle_service = ChronicleService(llm_provider=llm_provider)

        self._static_system_prompt: Optional[str] = None

    def _get_llm(self) -> LLMProvider:
        if self._llm is None:
            self._llm = create_provider()
        return self._llm

    def _get_bigpickle(self) -> BigPicklePipeline:
        if self._bigpickle is None:
            self._bigpickle = BigPicklePipeline(
                style_controller=self._style_controller,
                guidance_scheduler=self._guidance_scheduler,
                image_cache=self._image_cache,
            )
        return self._bigpickle

    def _get_static_system_prompt(self) -> str:
        if self._static_system_prompt is None:
            self._static_system_prompt = self._prompt_gen.build_static_system_prompt()
        return self._static_system_prompt

    # ── Session Management ──────────────────────────────

    def create_session(self, player_name: str, difficulty: str = "normal") -> Session:
        from uuid import uuid4

        session = Session(
            session_id=str(uuid4()),
            player_name=player_name,
            difficulty=difficulty,
            world_state=WorldState(
                continent="克洛諾斯廢土",
                alignment=self._alignment.starting(),
                chapter=1,
            ),
        )
        self._sessions[session.session_id] = session
        self._scene_counters[session.session_id] = 1
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    def session_count(self) -> int:
        return len(self._sessions)

    def _to_image_url(self, session_id: str, scene_index: int) -> str:
        return f"/images/scenes/{session_id}_{scene_index:04d}.png"

    def _to_image_path(self, session_id: str, scene_index: int) -> str:
        return str(
            Path(settings.image_output_dir)
            / f"{session_id}_{scene_index:04d}.png"
        )

    # ── Build Messages ──────────────────────────────────

    def _build_messages(
        self,
        system_prompt: str,
        user_prompt: str,
        history: List[Dict],
    ) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
        ]

        for entry in history:
            narrative = entry.get("narrative", "")
            choice_text = entry.get("chosen_choice_text", "")
            if narrative:
                messages.append({"role": "assistant", "content": narrative})
            if choice_text:
                messages.append({"role": "user", "content": f"玩家選擇：{choice_text}"})

        messages.append({"role": "user", "content": user_prompt})
        return messages

    # ── Core Game Loop ──────────────────────────────────

    async def new_game(self, player_name: str, difficulty: str = "normal") -> ActionResponse:
        session = self.create_session(player_name, difficulty)
        image_path = self._to_image_path(session.session_id, 1)
        try:
            style = self._style_controller.resolve_style(session.world_state.continent)
            compiled = self._scene_compiler.compile(
                OPENING_SCENE_TAGS,
                style_override=style,
                continent=session.world_state.continent,
            )
            bp = self._get_bigpickle()
            await bp.initialize()
            await bp.generate(
                prompt=compiled["prompt"],
                negative_prompt=compiled["negative_prompt"],
                style=compiled["style"],
                chapter=1,
                output_path=image_path,
            )
        except Exception as exc:
            logger.warning("Opening image generation failed: %s", exc)
        return ActionResponse(
            session_id=session.session_id,
            narrative=OPENING_NARRATIVE,
            choices=OPENING_CHOICES,
            image_url=self._to_image_url(session.session_id, 1),
            world_state=session.world_state,
        )

    def _prepare_turn(self, session: Session, choice_id: str):
        """Shared setup for process_action."""
        if not session.history:
            last_choice_text = self._find_opening_choice_text(choice_id)
        else:
            last_choice_text = self._find_last_choice_text(session, choice_id)

        current_turn = len(session.history) + 1
        chapter, stage, stage_turn = chapter_stage_from_turn(current_turn)

        session.world_state.chapter = chapter
        session.world_state.continent = get_continent_for_turn(current_turn)

        final_stage = is_final_stage(current_turn)
        chapter_goal = get_chapter_goal(current_turn)
        plot_directive = get_plot_directive(current_turn)

        current_event_theme = self._roll_event_theme(stage)

        system_prompt = self._get_static_system_prompt()
        user_prompt = self._prompt_gen.build_user_prompt(
            world_state=session.world_state,
            plot_directive=plot_directive,
            chapter_goal=chapter_goal,
            recent_history=session.history,
            last_choice_text=last_choice_text,
            is_final_stage=final_stage,
            current_event_theme=current_event_theme,
        )

        messages = self._build_messages(system_prompt, user_prompt, session.history)
        return messages, current_turn, chapter, stage, final_stage

    async def process_action(
        self,
        session_id: str,
        choice_id: str,
        max_retries: int = 2,
    ) -> ActionResponse:
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")

        messages, current_turn, chapter, stage, final_stage = self._prepare_turn(
            session, choice_id
        )
        logger.warning(
            "process_action: turn=%d, chapter=%d, stage=%d, final_stage=%s",
            current_turn, chapter, stage, final_stage,
        )

        raw = None
        parsed = None
        for attempt in range(max_retries + 1):
            raw = await self._get_llm().generate(messages)
            parsed = self._parser.parse(raw)

            if parsed.options:
                for i, opt in enumerate(parsed.options):
                    if i < len(parsed.choices):
                        parsed.choices[i].text = opt
                    else:
                        parsed.choices.append(
                            Choice(id=f"c{i+1}", text=opt, alignment_delta=None)
                        )

            if final_stage:
                break

            if any(c.text for c in parsed.choices):
                break

            logger.warning(
                "Empty choices on attempt %d/%d (turn %d). Retrying...",
                attempt + 1, max_retries, current_turn,
            )

        return await self._finalize_turn(
            session, session_id, choice_id, raw, current_turn, final_stage, parsed
        )

    async def _finalize_turn(
        self,
        session: Session,
        session_id: str,
        choice_id: str,
        raw: str,
        current_turn: int,
        final_stage: bool,
        parsed: Optional[LLMOutput] = None,
    ) -> ActionResponse:
        """Parse LLM output, apply alignment, store history, generate image."""
        if parsed is None:
            parsed = self._parser.parse(raw)
        last_choice_text = self._find_last_choice_text(session, choice_id)

        merged_delta: dict = {}

        if parsed.alignment_delta:
            merged_delta.update(parsed.alignment_delta)

        choice_delta = self._find_previous_choice_delta(session, choice_id)
        if choice_delta:
            for k, v in choice_delta.items():
                if v is not None:
                    merged_delta[k] = merged_delta.get(k, 0) + v

        if merged_delta:
            difficulty_modifier = self._difficulty_multiplier(session.difficulty)
            self._alignment.apply_delta(
                session.world_state.alignment,
                merged_delta,
                difficulty_modifier,
            )

        self._scene_counters[session_id] += 1
        scene_index = self._scene_counters[session_id]

        visual_prompt = parsed.visual_prompt

        session.history.append({
            "narrative": parsed.narrative,
            "chosen_choice_id": choice_id,
            "chosen_choice_text": last_choice_text or "",
            "scene_tags": parsed.scene_tags.model_dump(),
            "choices": [c.model_dump() for c in parsed.choices],
            "visual_prompt": visual_prompt,
        })

        image_output_path = self._to_image_path(session_id, scene_index)
        try:
            bp = self._get_bigpickle()
            await bp.initialize()

            if visual_prompt:
                await bp.generate(
                    prompt=visual_prompt,
                    negative_prompt=(
                        "low quality, worst quality, blurry, distorted, deformed, "
                        "bad anatomy, watermark, text, signature, extra limbs, "
                        "ugly, sketch, cartoon, 3d render, monochrome, bad proportions, letters, words"
                    ),
                    style=self._style_controller.resolve_style(
                        session.world_state.continent,
                    ),
                    chapter=session.world_state.chapter,
                    output_path=image_output_path,
                )
            else:
                style = self._style_controller.resolve_style(
                    session.world_state.continent,
                )
                compiled = self._scene_compiler.compile(
                    parsed.scene_tags,
                    style_override=style,
                    continent=session.world_state.continent,
                )
                await bp.generate(
                    prompt=compiled["prompt"],
                    negative_prompt=compiled["negative_prompt"],
                    style=compiled["style"],
                    chapter=session.world_state.chapter,
                    output_path=image_output_path,
                )
        except Exception as exc:
            logger.error("Image generation failed: %s", exc)

        stage_info = get_stage_config(current_turn)
        logger.warning(
            "_finalize_turn: is_ending=%s, choices=%d",
            final_stage, len(parsed.choices),
        )
        return ActionResponse(
            session_id=session_id,
            narrative=parsed.narrative,
            choices=parsed.choices,
            image_url=self._to_image_url(session_id, scene_index),
            world_state=session.world_state,
            is_ending=final_stage,
            stage=stage_info["stage"],
            current_turn=current_turn,
        )

    # ── Ending System ──────────────────────────────────

    def get_ending_progress(self, session_id: str) -> dict:
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        return self._ending_service.get_ending_progress(
            session.world_state.alignment
        )

    async def resolve_ending(self, session_id: str) -> EndingResponse:
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")

        ending = self._ending_service.determine_ending(
            session.world_state.alignment
        )
        chronicle = self._chronicle_service.build_chronicle(session, ending)
        epilogue = await self._chronicle_service.generate_epilogue(
            session, ending
        )

        self._scene_counters[session_id] += 1
        scene_index = self._scene_counters[session_id]
        image_output_path = self._to_image_path(session_id, scene_index)

        try:
            style = ending.scene_tags.style
            compiled = self._scene_compiler.compile(
                ending.scene_tags,
                style_override=style,
                continent=session.world_state.continent,
            )
            bp = self._get_bigpickle()
            await bp.initialize()
            await bp.generate(
                prompt=compiled["prompt"],
                negative_prompt=compiled["negative_prompt"],
                style=compiled["style"],
                chapter=session.world_state.chapter,
                is_key_moment=True,
                output_path=image_output_path,
            )
        except Exception as exc:
            logger.error("Ending image generation failed: %s", exc)

        return EndingResponse(
            session_id=session_id,
            ending=EndingInfo(
                id=ending.id,
                title=ending.title,
                subtitle=ending.subtitle,
                moral=ending.moral,
                description=ending.description,
            ),
            chronicle=ChronicleData(**chronicle),
            epilogue=epilogue,
            image_url=self._to_image_url(session_id, scene_index),
        )

    # ── Random Event System ─────────────────────────────

    @staticmethod
    def _roll_event_theme(stage: int) -> Optional[str]:
        import random
        if stage not in TRIGGER_STAGES:
            return None
        if random.random() >= TRIGGER_PROBABILITY:
            return None
        return random.choice(EVENT_THEMES)

    # ── Helpers ─────────────────────────────────────────

    def _find_last_choice_text(
        self,
        session: Session,
        choice_id: str,
    ) -> Optional[str]:
        if not session.history:
            return None
        last_entry = session.history[-1]
        for c in last_entry.get("choices", []):
            if c.get("id") == choice_id:
                return c.get("text", "")
        return None

    def _find_previous_choice_delta(
        self,
        session: Session,
        choice_id: str,
    ) -> Optional[dict]:
        if not session.history:
            return None
        last_entry = session.history[-1]
        for c in last_entry.get("choices", []):
            if c.get("id") == choice_id:
                return c.get("alignment_delta")
        return None

    @staticmethod
    def _find_opening_choice_text(choice_id: str) -> Optional[str]:
        for c in OPENING_CHOICES:
            if c.id == choice_id:
                return c.text
        return None

    @staticmethod
    def _difficulty_multiplier(difficulty: str) -> float:
        return {"easy": 0.5, "normal": 1.0, "hard": 1.5}.get(difficulty, 1.0)

    @staticmethod
    def _current_turn(session) -> int:
        return len(session.history) + 1
