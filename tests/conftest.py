"""Shared test fixtures for the LinkedIn Post Generator test suite."""

from pathlib import Path

import pytest

from linkedin_post_generator.config import paths


@pytest.fixture(autouse=True)
def custom_templates_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the custom templates directory at an empty temporary path.

    Keeps every test away from the user's real ~/.config templates.
    """
    directory = tmp_path / "custom-templates"
    monkeypatch.setattr(paths, "templates_dir", lambda: directory)
    return directory
