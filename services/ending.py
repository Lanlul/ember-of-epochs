import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from ..models.world import Alignment, SceneTags

logger = logging.getLogger(__name__)

ENDING_THRESHOLD = 65
BALANCE_THRESHOLD = 55


@dataclass
class Ending:
    id: str
    title: str
    subtitle: str
    description: str
    scene_tags: SceneTags
    moral: str
    alignment_required: Optional[Dict[str, Tuple[int, int]]] = None


ENDINGS: List[Ending] = [
    Ending(
        id="mechanical_epoch",
        title="機械紀元",
        subtitle="秩序與科技的終極統一",
        description=(
            "你選擇以古紀元的科技力量重建世界。巨大的機械構造體取代了破碎的大陸，"
            "人類在嚴密的秩序下獲得安穩——但代價是再也沒有人記得風的聲音。"
        ),
        moral="秩序帶來安定，也帶來牢籠。",
        scene_tags=SceneTags(
            setting="由巨大齒輪與機械結構構成的新大陸，天空被金屬穹頂覆蓋",
            mood="莊嚴而冰冷",
            lighting="機械運轉的橙紅色光芒從地面裂縫滲出",
            color_palette=["銅褐", "鐵灰", "火焰橙", "黑曜"],
            style="steampunk",
            focus="massive_clockwork_city",
            character_state="平靜但失去溫度",
        ),
    ),
    Ending(
        id="jade_epoch",
        title="翡翠紀元",
        subtitle="秩序與自然的和諧共生",
        description=(
            "你引導古老的生體科技與自然法則融合。翡翠密境的意識擴散到每一塊大陸，"
            "植物與動物獲得了前所未有的智慧。世界變得寧靜而美麗——"
            "但這份和諧建立在嚴格的自然律法之上。"
        ),
        moral="真正的自由，來自於遵循自然的規則。",
        scene_tags=SceneTags(
            setting="被巨大翡翠色植物覆蓋的浮空大陸，生物發光孢子漂浮在空氣中",
            mood="寧靜而神聖",
            lighting="柔和的生物螢光從植物內部散發",
            color_palette=["翡翠綠", "藤紫", "琥珀", "螢光藍"],
            style="biomagical",
            focus="living_tree_city",
            character_state="安詳而敬畏",
        ),
    ),
    Ending(
        id="ashen_epoch",
        title="灰燼紀元",
        subtitle="混沌與科技的失控狂潮",
        description=(
            "古紀元的科技在沒有束縛的情況下爆發式進化。機械生命體獲得了自我意識，"
            "開始改造世界以適應自己的存在。人類成為新世界中的少數族群——"
            "但這是一個充滿無限可能性的時代。"
        ),
        moral="創造力與毀滅，往往是同一枚硬幣的兩面。",
        scene_tags=SceneTags(
            setting="由自我演化機械構成的動態城市，建築物不斷變形重組",
            mood="躁動而充滿活力",
            lighting="霓虹與電弧的光芒交錯閃爍",
            color_palette=["霓虹紫", "電光藍", "鏽蝕橙", "金屬銀"],
            style="surreal",
            focus="evolving_mechanical_organism",
            character_state="興奮而徬徨",
        ),
    ),
    Ending(
        id="primal_epoch",
        title="野性紀元",
        subtitle="混沌與自然的原始回歸",
        description=(
            "你讓世界回歸最原始的狀態。大陸重新扎根於大地，海洋覆蓋了傷痕，"
            "古老的魔法在空氣中重新流動。人類遺忘了科技，與野獸和精靈共存——"
            "世界獲得了第二次機會。"
        ),
        moral="有時候，遺忘才是真正的治癒。",
        scene_tags=SceneTags(
            setting="原始森林與巨大生物共存的荒野，瀑布從浮空大陸邊緣傾瀉而下",
            mood="狂野而自由",
            lighting="溫暖的陽光穿透濃密樹冠",
            color_palette=["翠綠", "大地棕", "天空藍", "夕陽金"],
            style="frost_epic",
            focus="primitive_wilderness",
            character_state="原始而純粹",
        ),
    ),
    Ending(
        id="eternal_cycle",
        title="輪迴紀元",
        subtitle="均衡中的永恆循環",
        description=(
            "你選擇了不選擇。四股力量在你的引導下達成了微妙的平衡，"
            "世界既沒有被改造也沒有回歸原始——它只是繼續存在。"
            "但你深知，這份平衡不會永遠持續。大凋零的循環，"
            "或許本身就是世界的本質。而你，將在下一個紀元再次醒來。"
        ),
        moral="世界不需要救世主，它只需要見證者。",
        scene_tags=SceneTags(
            setting="五塊大陸在星空中緩慢旋轉，形成一個完美的環",
            mood="超然而神秘",
            lighting="星光與極光交織，永恆的暮色",
            color_palette=["星塵銀", "深淵紫", "極光綠", "虛空黑"],
            style="surreal",
            focus="floating_continents_in_orbit",
            character_state="平靜而了然",
        ),
    ),
]


ENDINGS_BY_ID: Dict[str, Ending] = {e.id: e for e in ENDINGS}


class EndingService:
    def determine_ending(self, alignment: Alignment) -> Ending:
        moral, elemental = self._get_dominant_pairs(alignment)

        if moral == "order" and elemental == "technology":
            idx = 0
        elif moral == "order" and elemental == "nature":
            idx = 1
        elif moral == "chaos" and elemental == "technology":
            idx = 2
        elif moral == "chaos" and elemental == "nature":
            idx = 3
        else:
            idx = 4

        return ENDINGS[idx]

    def is_ending_triggered(self, alignment: Alignment, min_actions: int = 5) -> bool:
        if min_actions < 5:
            return False
        return self._get_max_axis(alignment) >= ENDING_THRESHOLD

    def _get_dominant_pairs(self, alignment: Alignment) -> Tuple[str, str]:
        moral = "order" if alignment.order >= alignment.chaos else "chaos"
        elemental = "technology" if alignment.technology >= alignment.nature else "nature"

        moral_val = getattr(alignment, moral)
        opposing_moral = getattr(alignment, "chaos" if moral == "order" else "order")
        elem_val = getattr(alignment, elemental)
        opposing_elem = getattr(alignment, "nature" if elemental == "technology" else "technology")

        if abs(moral_val - opposing_moral) <= 10 and abs(elem_val - opposing_elem) <= 10:
            return ("neutral", "neutral")

        return (moral, elemental)

    def _get_max_axis(self, alignment: Alignment) -> int:
        return max(
            alignment.order, alignment.chaos,
            alignment.technology, alignment.nature,
        )

    def get_ending_progress(self, alignment: Alignment) -> Dict[str, float]:
        moral, elemental = self._get_dominant_pairs(alignment)
        return {
            "dominant_moral": moral,
            "dominant_elemental": elemental,
            "max_axis_value": self._get_max_axis(alignment),
            "threshold": ENDING_THRESHOLD,
            "progress_pct": round(
                min(100, self._get_max_axis(alignment) / ENDING_THRESHOLD * 100)
            ),
        }
