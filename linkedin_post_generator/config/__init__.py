"""Config module — Pydantic model, TOML reader/writer, fallback chain."""

from linkedin_post_generator.config.model import (
    AIBackend,
    AppConfig,
    Language,
    Length,
    Tone,
)
from linkedin_post_generator.config.paths import config_dir, global_config_path
from linkedin_post_generator.config.reader import load_config
from linkedin_post_generator.config.writer import save_config

__all__ = [
    "AIBackend",
    "AppConfig",
    "Language",
    "Length",
    "Tone",
    "config_dir",
    "global_config_path",
    "load_config",
    "save_config",
]
