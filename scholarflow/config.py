"""Global configuration management for ScholarFlow."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

CONFIG_DIR = Path.home() / ".scholarflow"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class SFConfig:
    model: str = "openai/gpt-4o"
    lang: str = "zh"
    verbosity: str = "normal"  # concise | normal | detailed
    ppt_theme: str = "academic_blue"
    beamer_theme: str = "Madrid"
    api_keys: dict = field(default_factory=dict)

    @classmethod
    def load(cls) -> "SFConfig":
        """Load config from env vars, .env file, and config file (in priority order)."""
        load_dotenv()
        cfg = cls()

        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            for k, v in data.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)

        env_map = {
            "SF_MODEL": "model",
            "SF_LANG": "lang",
            "SF_VERBOSITY": "verbosity",
            "SF_PPT_THEME": "ppt_theme",
            "SF_BEAMER_THEME": "beamer_theme",
        }
        for env_key, attr in env_map.items():
            val = os.getenv(env_key)
            if val:
                setattr(cfg, attr, val)

        for provider in ("OPENAI", "ANTHROPIC", "GEMINI", "DEEPSEEK", "MINIMAX"):
            key = os.getenv(f"{provider}_API_KEY")
            if key:
                cfg.api_keys[provider.lower()] = key

        return cfg

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "model": self.model,
            "lang": self.lang,
            "verbosity": self.verbosity,
            "ppt_theme": self.ppt_theme,
            "beamer_theme": self.beamer_theme,
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def set_value(self, key: str, value: str) -> None:
        if key == "api-key":
            provider = self._detect_provider(value)
            os.environ[f"{provider.upper()}_API_KEY"] = value
            self.api_keys[provider] = value
        elif hasattr(self, key.replace("-", "_")):
            setattr(self, key.replace("-", "_"), value)
        self.save()

    @staticmethod
    def _detect_provider(key: str) -> str:
        if key.startswith("sk-"):
            if "cp" in key[:8]:
                return "minimax"
            return "openai"
        if key.startswith("AIza"):
            return "gemini"
        return "openai"

    def get_model(self, override: Optional[str] = None) -> str:
        return override or self.model
