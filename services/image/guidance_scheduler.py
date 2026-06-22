from typing import Optional


class GuidanceScheduler:
    def __init__(self, base_cfg: float = 0.0):
        self._base_cfg = base_cfg

    def schedule(self, chapter: int, is_key_moment: bool = False) -> float:
        return self._base_cfg
