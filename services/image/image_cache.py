import hashlib
import json
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Tuple


class ImageCache:
    def __init__(self, cache_dir: str, capacity: int = 64):
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._capacity = capacity
        self._lru: OrderedDict[str, str] = OrderedDict()

    def _make_key(self, prompt: str, style: str, cfg: float) -> str:
        raw = json.dumps({"p": prompt, "s": style, "c": cfg}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, prompt: str, style: str, cfg: float) -> Optional[str]:
        key = self._make_key(prompt, style, cfg)
        if key in self._lru:
            self._lru.move_to_end(key)
            path = self._lru[key]
            if Path(path).exists():
                return path
            del self._lru[key]
        return None

    def put(self, prompt: str, style: str, cfg: float, image_path: str) -> str:
        key = self._make_key(prompt, style, cfg)
        self._lru[key] = image_path
        self._lru.move_to_end(key)

        while len(self._lru) > self._capacity:
            self._lru.popitem(last=False)

        return image_path

    @property
    def size(self) -> int:
        return len(self._lru)
