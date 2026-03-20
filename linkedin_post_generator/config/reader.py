"""TOML config reader with fallback chain: local > global > defaults."""

import tomllib
from pathlib import Path

from linkedin_post_generator.config.model import AppConfig
from linkedin_post_generator.config.paths import global_config_path, local_config_path


def _read_toml(path: Path) -> dict:
    """Read and parse a TOML file, returning an empty dict on failure."""
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return {}


def load_config() -> AppConfig:
    """Load config with fallback chain: local > global > built-in defaults.

    Merge strategy: local overrides only the fields it defines,
    rest comes from global, then from built-in defaults.
    """
    global_data = _read_toml(global_config_path())

    local_path = local_config_path()
    local_data = _read_toml(local_path) if local_path else {}

    merged = {**global_data, **local_data}
    return AppConfig(**merged)


def config_exists() -> bool:
    """Check if any config file exists (global or local)."""
    return global_config_path().is_file() or local_config_path() is not None
