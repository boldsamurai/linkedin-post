"""Tests for user-defined templates — directory location and TOML loader."""

from pathlib import Path

import pytest

import linkedin_post_generator.templates  # noqa: F401  (registers built-ins)
from linkedin_post_generator.config import paths
from linkedin_post_generator.templates.custom_loader import load_custom_templates
from linkedin_post_generator.templates.exceptions import TemplateError
from linkedin_post_generator.templates.models import CUSTOM_BADGE

FIXTURES = Path(__file__).parent.parent / "fixtures" / "templates"


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


def test_load_custom_templates_reads_files_sorted_by_name() -> None:
    result = load_custom_templates(FIXTURES / "valid")
    assert [t.name for t in result] == ["weekly-digest", "lesson-learned"]


def test_load_custom_templates_marks_custom_and_badges_label() -> None:
    weekly = load_custom_templates(FIXTURES / "valid")[0]
    assert weekly.is_custom is True
    assert weekly.label == f"{CUSTOM_BADGE} Weekly digest"
    assert weekly.description == "Three links worth reading this week"
    assert weekly.instructions == "Summarise the source as one of three weekly picks."


def test_load_custom_templates_missing_dir_returns_empty(tmp_path: Path) -> None:
    assert load_custom_templates(tmp_path / "nope") == []


def test_load_custom_templates_raises_on_missing_field() -> None:
    with pytest.raises(TemplateError, match="missing field 'label'") as exc:
        load_custom_templates(FIXTURES / "missing_field")
    assert exc.value.path.name == "broken.toml"


def test_load_custom_templates_raises_on_bad_toml() -> None:
    with pytest.raises(TemplateError, match="invalid TOML") as exc:
        load_custom_templates(FIXTURES / "bad_toml")
    assert exc.value.path.name == "broken.toml"


def test_load_custom_templates_raises_on_non_utf8_file(tmp_path: Path) -> None:
    (tmp_path / "latin.toml").write_bytes(b'name = "caf\xe9"\n')
    with pytest.raises(TemplateError, match="not valid UTF-8") as exc:
        load_custom_templates(tmp_path)
    assert exc.value.path.name == "latin.toml"


def test_load_custom_templates_raises_on_unreadable_file(tmp_path: Path) -> None:
    (tmp_path / "folder.toml").mkdir()
    with pytest.raises(TemplateError, match="cannot read file"):
        load_custom_templates(tmp_path)


def test_load_custom_templates_raises_on_empty_field(tmp_path: Path) -> None:
    (tmp_path / "empty.toml").write_text(
        'name = "x"\nlabel = "  "\ndescription = "d"\ninstructions = "i"\n',
        encoding="utf-8",
    )
    with pytest.raises(TemplateError, match=r"field 'label'.*must not be empty"):
        load_custom_templates(tmp_path)


def test_load_custom_templates_raises_on_invalid_name() -> None:
    with pytest.raises(TemplateError, match="field 'name'"):
        load_custom_templates(FIXTURES / "bad_name")


def test_load_custom_templates_raises_on_builtin_clash() -> None:
    with pytest.raises(TemplateError, match="clashes with a built-in") as exc:
        load_custom_templates(FIXTURES / "clash_builtin")
    assert exc.value.path.name == "discovery.toml"


def test_load_custom_templates_raises_on_clash_between_files() -> None:
    with pytest.raises(TemplateError, match=r"already used by .*one\.toml") as exc:
        load_custom_templates(FIXTURES / "clash_files")
    assert exc.value.path.name == "two.toml"
