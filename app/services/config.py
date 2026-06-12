from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("risk_config")

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "rules_config.yaml"
_config_override_path = os.getenv("RISK_CONFIG_PATH", "")


class RuleConfig:
    _instance: RuleConfig | None = None
    _lock = threading.Lock()

    def __init__(self):
        self._data: dict[str, Any] = {}
        self._load()

    @classmethod
    def get(cls) -> RuleConfig:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _load(self):
        path = Path(_config_override_path) if _config_override_path else DEFAULT_CONFIG_PATH
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._data = yaml.safe_load(f) or {}
            logger.info("配置已加载: %s", path)
        except FileNotFoundError:
            logger.warning("配置文件不存在 %s，使用默认值", path)
            self._data = {}
        except Exception as e:
            logger.error("加载配置失败: %s", e)
            self._data = {}

    def reload(self):
        with self._lock:
            self._load()

    def get_rule(self, rule_name: str) -> dict[str, Any]:
        return self._data.get("rules", {}).get(rule_name, {})

    def get_engine(self) -> dict[str, Any]:
        return self._data.get("engine", {})

    def get_cache(self) -> dict[str, Any]:
        return self._data.get("cache", {})

    def get_log(self) -> dict[str, Any]:
        return self._data.get("log", {})

    def get_rate_limit(self) -> dict[str, Any]:
        return self._data.get("rate_limit", {})


def get_rule_config(rule_name: str) -> dict[str, Any]:
    return RuleConfig.get().get_rule(rule_name)


def get_engine_config() -> dict[str, Any]:
    return RuleConfig.get().get_engine()