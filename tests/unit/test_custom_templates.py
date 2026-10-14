"""Tests for user-defined templates — templates directory location."""

from pathlib import Path

import pytest

from linkedin_post_generator.config import paths


@pytest.fixture
def fake_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the app config directory at a temporary path."""
    config = tmp_path / "linkedin-post"
    monkeypatch.setattr(paths, "user_config_dir", lambda _app: str(config))
    return config


def test_templates_dir_is_inside_config_dir(fake_config_dir: Path) -> None:
    assert paths.templates_dir() == fake_config_dir / "templates"


def test_templates_dir_not_created_on_read(fake_config_dir: Path) -> None:
    result = paths.templates_dir()
    assert not result.exists(), "templates_dir() must not create the directory"
    assert not fake_config_dir.exists(), "templates_dir() must not create config dir"
