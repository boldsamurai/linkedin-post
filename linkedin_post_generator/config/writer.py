"""TOML config writer for init and config commands."""

from pathlib import Path

import tomli_w

from linkedin_post_generator.config.model import AppConfig
from linkedin_post_generator.config.paths import global_config_path


def save_config(config: AppConfig, path: Path | None = None) -> Path:
    """Save config to a TOML file.

    Args:
        config: The config model to serialize.
        path: Target path. Defaults to global config path.

    Returns:
        The path where the config was saved.
    """
    target = path or global_config_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    data = config.model_dump(mode="json")
    with target.open("wb") as f:
        tomli_w.dump(data, f)

    return target
