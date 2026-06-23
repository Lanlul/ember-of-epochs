from typing import List, Dict, Any, Optional
from ...models.world import WorldState
from ..prompts.system_prompt import WORLD_LORE, OUTPUT_FORMAT, WRITING_DIVERSITY
from ..script_config import FINAL_STAGE_WARNING


def build_static_system_prompt() -> str:
    """Fully static system prompt — identical every call for KV cache reuse."""
    lines = [
        "【世界觀】",
        WORLD_LORE,
        "",
        WRITING_DIVERSITY,
        "",
        "【輸出格式要求】",
        "請嚴格按照以下格式輸出，不要加入任何其他文字：",
        "",
        OUTPUT_FORMAT,
    ]
    return "\n".join(lines)


EVENT_INJECTION = """【本回合突發變數主題】{}
【情境融合絕對指令】請分析主角目前所在的具體位置與當下正在執行的動作，將上述的突發變數主題合理地具象化。
若主題為「環境與空間危機」且主角在室內，請設計停電、崩塌或毒氣；若在室外則設計氣候突變。
若主題為「不速之客的介入」，請根據當前場景安排合理的角色出場。
若主題為「關鍵資源或裝備的損壞與匱乏」，請根據主角當前持有的裝備設定具體的故障或消耗。
若主題為「主角身體或心理的突發狀況」，請根據當前壓力與環境設計合理的生理或心理反應。
若主題為「意外發現的隱藏資訊」，請根據當前場景中的元素設計一條線索或遺留物。
絕對不能寫出破壞當下物理邏輯的事件。請讓這個意外順著前文自然發生，打破主角原本的計畫。你生成的三個選項中必須包含針對此意外的應對。"""


def build_user_prompt(
    world_state: WorldState,
    plot_directive: str,
    chapter_goal: str,
    recent_history: Optional[List[Dict[str, Any]]] = None,
    last_choice_text: Optional[str] = None,
    is_final_stage: bool = False,
    current_event_theme: Optional[str] = None,
) -> str:
    lines: List[str] = []

    lines.append("【當前章節目標 — 最高優先級】")
    lines.append(chapter_goal)
    lines.append("")

    lines.append("目前狀態：")
    lines.append(f"大陸：{world_state.continent} | 第 {world_state.chapter} 章")
    lines.append(f"傾向：秩序{world_state.alignment.order} 混沌{world_state.alignment.chaos} 科技{world_state.alignment.technology} 自然{world_state.alignment.nature}")
    lines.append("")

    if last_choice_text:
        lines.append(f"玩家選擇：{last_choice_text}")

    if recent_history:
        lines.append("\n最近發展：")
        for entry in recent_history[-3:]:
            narrative = entry.get("narrative", "")
            if narrative:
                lines.append(f"- {narrative[:100]}")

    lines.append(f"\n【當前劇情指令】{plot_directive}")

    if current_event_theme:
        lines.append("")
        lines.append(EVENT_INJECTION.format(current_event_theme))

    lines.append("")
    lines.append(WRITING_DIVERSITY)

    lines.append("")
    lines.append(
        "【劇情推進絕對規則】禁止重複或改寫前一段故事中的場景設定、環境描述與事件。"
        "你寫的 narrative 必須根據玩家的選擇明確推進到全新場景或情節發展，"
        "禁止停留在相同或相似的地點與情境。"
    )

    if is_final_stage:
        lines.append(f"\n{FINAL_STAGE_WARNING}")
        lines.append("\n請生成結局故事與繪圖提示詞。choices 陣列請留空（遊戲結束）。")
    else:
        lines.append("\n請生成下一段故事與繪圖提示詞。")

    return "\n".join(lines)


def build_ending_prompt(
    world_state: WorldState,
    full_history: List[Dict[str, Any]],
) -> str:
    lines: List[str] = [
        "生成結局。",
        f"最終傾向：秩序{world_state.alignment.order} 混沌{world_state.alignment.chaos} 科技{world_state.alignment.technology} 自然{world_state.alignment.nature}",
    ]
    for entry in full_history[-3:]:
        lines.append(entry.get("narrative", "")[:80])

    lines.append("\n請生成結局敘事（300字）、title/subtitle/moral/description、scene_tags。choices為空陣列。")
    return "\n".join(lines)


class PromptGenerator:
    def build_static_system_prompt(self) -> str:
        return build_static_system_prompt()

    def build_user_prompt(
        self,
        world_state: WorldState,
        plot_directive: str,
        chapter_goal: str,
        recent_history: Optional[List[Dict[str, Any]]] = None,
        last_choice_text: Optional[str] = None,
        is_final_stage: bool = False,
        current_event_theme: Optional[str] = None,
    ) -> str:
        return build_user_prompt(
            world_state,
            plot_directive,
            chapter_goal,
            recent_history,
            last_choice_text,
            is_final_stage,
            current_event_theme,
        )

    def build_ending_prompt(self, world_state: WorldState, full_history: List[Dict[str, Any]]) -> str:
        return build_ending_prompt(world_state, full_history)
