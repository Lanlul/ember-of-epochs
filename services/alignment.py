from typing import Dict, Optional

from ..models.world import Alignment


OPPOSING_AXES = {
    "order": "chaos",
    "chaos": "order",
    "technology": "nature",
    "nature": "technology",
}


class AlignmentService:
    def apply_delta(
        self,
        alignment: Alignment,
        delta: Dict[str, int],
        difficulty_modifier: float = 1.0,
    ) -> Alignment:
        for axis, raw_delta in delta.items():
            if not hasattr(alignment, axis):
                continue

            adjusted = round(raw_delta * difficulty_modifier)
            current = getattr(alignment, axis)
            setattr(alignment, axis, self._clamp(current + adjusted))

            opposing = OPPOSING_AXES.get(axis)
            if opposing and raw_delta != 0:
                opposing_current = getattr(alignment, opposing)
                opposing_delta = -abs(adjusted) // 2
                setattr(
                    alignment, opposing,
                    self._clamp(opposing_current + opposing_delta),
                )

        return alignment

    def get_dominant_axis(self, alignment: Alignment) -> str:
        axes = {
            "order": alignment.order,
            "chaos": alignment.chaos,
            "technology": alignment.technology,
            "nature": alignment.nature,
        }
        return max(axes, key=axes.get)

    def get_axis_pair_dominance(self, alignment: Alignment) -> Dict[str, str]:
        moral = "order" if alignment.order >= alignment.chaos else "chaos"
        elemental = "technology" if alignment.technology >= alignment.nature else "nature"
        return {"moral": moral, "elemental": elemental}

    @staticmethod
    def _clamp(value: int) -> int:
        return max(0, min(100, value))

    @staticmethod
    def starting() -> Alignment:
        return Alignment()
