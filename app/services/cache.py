from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import OrderedDict

from app.models import RiskFeatures, RiskResult
from app.services.config import RuleConfig


class RiskCache:
    def __init__(self, ttl_seconds: int = 30, max_size: int = 1000):
        self.ttl = ttl_seconds
        self.max_size = max_size
        self._cache: OrderedDict[str, tuple[float, RiskResult]] = OrderedDict()
        self._lock = threading.Lock()

    @classmethod
    def from_config(cls) -> RiskCache | None:
        cfg = RuleConfig.get().get_cache()
        if not cfg.get("enabled", False):
            return None
        return cls(
            ttl_seconds=cfg.get("ttl_seconds", 30),
            max_size=cfg.get("max_size", 1000),
        )

    @staticmethod
    def _make_key(features: RiskFeatures) -> str:
        raw = json.dumps(features.model_dump(), sort_keys=True, ensure_ascii=False)
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, features: RiskFeatures) -> RiskResult | None:
        key = self._make_key(features)
        with self._lock:
            if key in self._cache:
                ts, result = self._cache[key]
                if time.time() - ts < self.ttl:
                    self._cache.move_to_end(key)
                    return result
                del self._cache[key]
        return None

    def set(self, features: RiskFeatures, result: RiskResult) -> None:
        key = self._make_key(features)
        with self._lock:
            self._cache[key] = (time.time(), result)
            self._cache.move_to_end(key)
            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def info(self) -> dict:
        with self._lock:
            return {"size": len(self._cache), "max_size": self.max_size, "ttl_seconds": self.ttl}