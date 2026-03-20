"""Cross-platform config paths using platformdirs (XDG-compliant)."""

from pathlib import Path

from platformdirs import user_config_dir

APP_NAME = "linkedin-post"

LOCAL_CONFIG_FILENAME = "config.toml"


def config_dir() -> Path:
    """Return the global config directory, creating it if needed."""
    path = Path(user_config_dir(APP_NAME))
    path.mkdir(parents=True, exist_ok=True)
    return path


def global_config_path() -> Path:
    """Return the path to the global config file."""
    return config_dir() / LOCAL_CONFIG_FILENAME


def local_config_path() -> Path | None:
    """Return the local config path if it exists, else None."""
    path = Path.cwd() / LOCAL_CONFIG_FILENAME
    return path if path.is_file() else None


def history_db_path() -> Path:
    """Return the path to the history SQLite database."""
    return config_dir() / "history.db"
