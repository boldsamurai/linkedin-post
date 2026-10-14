"""Tests for user-defined templates — directory, TOML loader, registry."""

from pathlib import Path

import pytest

import linkedin_post_generator.templates  # noqa: F401  (registers built-ins)
from linkedin_post_generator.config import paths
from linkedin_post_generator.config.model import Language, Length, Tone

# Bound before conftest's autouse fixture replaces paths.templates_dir
from linkedin_post_generator.config.paths import templates_dir
from linkedin_post_generator.templates.builder import build_prompt
from linkedin_post_generator.templates.custom_loader import load_custom_templates
from linkedin_post_generator.templates.exceptions import TemplateError
from linkedin_post_generator.templates.models import CUSTOM_BADGE
from linkedin_post_generator.templates.registry import (
    TEMPLATES,
    get_template,
    list_templates,
)

FIXTURES = Path(__file__).parent.parent / "fixtures" / "templates"


@pytest.fixture
def fake_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the app config directory at a temporary path."""
    config = tmp_path / "linkedin-post"
    monkeypatch.setattr(paths, "user_config_dir", lambda _app: str(config))
    return config


def test_templates_dir_is_inside_config_dir(fake_config_dir: Path) -> None:
    assert templates_dir() == fake_config_dir / "templates"


def test_templates_dir_not_created_on_read(fake_config_dir: Path) -> None:
    result = templates_dir()
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


def _write_template(directory: Path, name: str, label: str = "Mine") -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{name}.toml").write_text(
        f'name = "{name}"\nlabel = "{label}"\ndescription = "d"\n'
        f'instructions = "Custom instructions for {name}."\n',
        encoding="utf-8",
    )


def test_list_templates_returns_builtins_then_custom(
    custom_templates_dir: Path,
) -> None:
    _write_template(custom_templates_dir, "zeta")
    _write_template(custom_templates_dir, "alpha")
    names = [t.name for t in list_templates()]
    assert names == [*TEMPLATES, "alpha", "zeta"]


def test_list_templates_without_custom_dir_returns_builtins() -> None:
    assert list_templates() == list(TEMPLATES.values())


def test_list_templates_shows_badge_on_custom(custom_templates_dir: Path) -> None:
    _write_template(custom_templates_dir, "mine", label="My format")
    custom = [t for t in list_templates() if t.is_custom]
    assert [t.label for t in custom] == [f"{CUSTOM_BADGE} My format"]


def test_get_template_finds_custom(custom_templates_dir: Path) -> None:
    _write_template(custom_templates_dir, "mine")
    result = get_template("mine")
    assert result.is_custom is True
    assert result.instructions == "Custom instructions for mine."


def test_get_template_unknown_lists_custom_names(custom_templates_dir: Path) -> None:
    _write_template(custom_templates_dir, "mine")
    with pytest.raises(KeyError, match=r"Available: .*mine"):
        get_template("missing")


def test_get_template_builtin_ignores_broken_custom_file(
    custom_templates_dir: Path,
) -> None:
    custom_templates_dir.mkdir()
    (custom_templates_dir / "broken.toml").write_text("name = ", encoding="utf-8")
    assert get_template("discovery").name == "discovery"


def test_list_templates_raises_on_broken_custom_file(
    custom_templates_dir: Path,
) -> None:
    custom_templates_dir.mkdir()
    (custom_templates_dir / "broken.toml").write_text("name = ", encoding="utf-8")
    with pytest.raises(TemplateError, match=r"broken\.toml"):
        list_templates()


def test_build_prompt_with_custom_template(custom_templates_dir: Path) -> None:
    _write_template(custom_templates_dir, "mine")
    system, user = build_prompt(
        template_name="mine",
        source_content="Source text",
        tone=Tone.TECHNICAL,
        language=Language.EN,
        length=Length.STANDARD,
    )
    assert "Custom instructions for mine." in system
    assert "Source text" in user
