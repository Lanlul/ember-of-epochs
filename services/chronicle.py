import logging
from typing import Dict, List, Any, Optional

from ..models.session import Session
from ..models.world import Alignment
from ..models.action import LLMOutput
from .llm import PromptGenerator, StructParser, create_provider
from .llm.provider import LLMProvider
from .ending import Ending, EndingService

logger = logging.getLogger(__name__)


class ChronicleService:
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
    ):
        self._llm = llm_provider
        self._prompt_gen = PromptGenerator()
        self._parser = StructParser()
        self._ending_service = EndingService()

    def _get_llm(self) -> LLMProvider:
        if self._llm is None:
            self._llm = create_provider()
        return self._llm

    def build_chronicle(
        self,
        session: Session,
        ending: Ending,
    ) -> Dict[str, Any]:
        key_decisions = self._extract_key_decisions(session.history)
        journey_summary = self._summarize_journey(session)

        return {
            "player_name": session.player_name,
            "ending": {
                "id": ending.id,
                "title": ending.title,
                "subtitle": ending.subtitle,
                "moral": ending.moral,
                "description": ending.description,
            },
            "journey": journey_summary,
            "key_decisions": key_decisions,
            "final_alignment": session.world_state.alignment.model_dump(),
        }

    async def generate_epilogue(
        self,
        session: Session,
        ending: Ending,
    ) -> str:
        system_prompt = (
            "你是一位擅長撰寫史詩結局的作家。"
            "根據玩家旅程與結局類型，生成一篇約 200 字的繁體中文終章敘事。"
            "請使用詩意的語言，為玩家的旅程畫下句點。"
        )

        user_prompt = (
            f"玩家名稱：{session.player_name}\n"
            f"結局：{ending.title} — {ending.subtitle}\n"
            f"核心訊息：{ending.moral}\n"
            f"旅程回顧：\n"
        )
        for entry in session.history[-5:]:
            tags = entry.get("scene_tags", {})
            if isinstance(tags, dict):
                user_prompt += f"- {entry.get('narrative', '')[:80]}...\n"

        user_prompt += "\n請生成終章敘事。"

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            return await self._get_llm().generate(messages)
        except Exception as exc:
            logger.warning("Epilogue generation failed: %s", exc)
            return ending.description

    def _extract_key_decisions(
        self,
        history: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        decisions = []
        for i, entry in enumerate(history):
            narrative = entry.get("narrative", "")
            if any(kw in narrative for kw in ["選擇", "決定", "抉擇", "關鍵"]):
                decisions.append({
                    "chapter": i + 1,
                    "decision": narrative[:60],
                })
        if not decisions and history:
            decisions.append({
                "chapter": 1,
                "decision": history[0].get("narrative", "")[:60],
            })
        return decisions

    def _summarize_journey(self, session: Session) -> Dict[str, Any]:
        align = session.world_state.alignment
        return {
            "total_actions": len(session.history),
            "continent": session.world_state.continent,
            "chapter": session.world_state.chapter,
            "alignment_summary": self._alignment_to_text(align),
        }

    @staticmethod
    def _alignment_to_text(alignment: Alignment) -> str:
        parts = []
        if alignment.order > 60:
            parts.append("崇尚秩序")
        elif alignment.chaos > 60:
            parts.append("擁抱混沌")

        if alignment.technology > 60:
            parts.append("信賴科技")
        elif alignment.nature > 60:
            parts.append("親近自然")

        if not parts:
            parts.append("維持均衡")

        return "、".join(parts)
