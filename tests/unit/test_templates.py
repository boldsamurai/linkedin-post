"""Tests for post template system — models, registry, and builder."""

import pytest

from linkedin_post_generator.config.model import Language, Length, Tone
from linkedin_post_generator.templates.builder import build_prompt
from linkedin_post_generator.templates.models import PostTemplate
from linkedin_post_generator.templates.registry import (
    TEMPLATES,
    get_template,
    list_templates,
    register,
)


@pytest.fixture(autouse=True)
def _clean_registry():
    """Reset the template registry before each test."""
    saved = dict(TEMPLATES)
    TEMPLATES.clear()
    yield
    TEMPLATES.clear()
    TEMPLATES.update(saved)


SAMPLE_TEMPLATE = PostTemplate(
    name="test",
    label="Test Template",
    description="A template for testing",
    instructions="Write a test post. Focus on clarity.",
)


class TestPostTemplate:
    """PostTemplate dataclass behavior."""

    def test_fields(self) -> None:
        t = SAMPLE_TEMPLATE
        assert t.name == "test"
        assert t.label == "Test Template"
        assert t.description == "A template for testing"
        assert t.instructions == "Write a test post. Focus on clarity."

    def test_frozen(self) -> None:
        with pytest.raises(AttributeError):
            SAMPLE_TEMPLATE.name = "modified"  # type: ignore[misc]


class TestRegistry:
    """Template registry — register, get, list."""

    def test_register_adds_template(self) -> None:
        register(SAMPLE_TEMPLATE)
        assert "test" in TEMPLATES

    def test_register_returns_template(self) -> None:
        result = register(SAMPLE_TEMPLATE)
        assert result is SAMPLE_TEMPLATE

    def test_get_template_returns_registered(self) -> None:
        register(SAMPLE_TEMPLATE)
        result = get_template("test")
        assert result is SAMPLE_TEMPLATE

    def test_get_template_unknown_raises(self) -> None:
        with pytest.raises(KeyError, match="Unknown template 'nonexistent'"):
            get_template("nonexistent")

    def test_get_template_shows_available(self) -> None:
        register(SAMPLE_TEMPLATE)
        other = PostTemplate(
            name="other", label="Other", description="d", instructions="i"
        )
        register(other)
        with pytest.raises(KeyError, match="Available: other, test"):
            get_template("missing")

    def test_list_templates_empty(self) -> None:
        assert list_templates() == []

    def test_list_templates_returns_all(self) -> None:
        register(SAMPLE_TEMPLATE)
        other = PostTemplate(
            name="other", label="Other", description="d", instructions="i"
        )
        register(other)
        result = list_templates()
        assert len(result) == 2
        assert SAMPLE_TEMPLATE in result
        assert other in result


class TestBuildPrompt:
    """Prompt builder combines template + config."""

    def test_returns_system_and_user_message(self) -> None:
        register(SAMPLE_TEMPLATE)
        system, user = build_prompt(
            template_name="test",
            source_content="Python is great",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert isinstance(system, str)
        assert isinstance(user, str)

    def test_system_contains_template_instructions(self) -> None:
        register(SAMPLE_TEMPLATE)
        system, _ = build_prompt(
            template_name="test",
            source_content="content",
            tone=Tone.TECHNICAL,
            language=Language.PL,
            length=Length.SHORT,
        )
        assert "Write a test post" in system

    def test_system_contains_tone(self) -> None:
        register(SAMPLE_TEMPLATE)
        system, _ = build_prompt(
            template_name="test",
            source_content="content",
            tone=Tone.STORYTELLING,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert "Narrative structure" in system

    def test_system_contains_language(self) -> None:
        register(SAMPLE_TEMPLATE)
        system, _ = build_prompt(
            template_name="test",
            source_content="content",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.PL,
            length=Length.STANDARD,
        )
        assert "post MUST be in Polish" in system

    def test_user_message_contains_source(self) -> None:
        register(SAMPLE_TEMPLATE)
        _, user = build_prompt(
            template_name="test",
            source_content="Amazing Python library",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert "Amazing Python library" in user

    def test_passes_hashtags(self) -> None:
        register(SAMPLE_TEMPLATE)
        system, _ = build_prompt(
            template_name="test",
            source_content="content",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
            hashtags=["#Python", "#AI"],
        )
        assert "#Python" in system
        assert "#AI" in system

    def test_unknown_template_raises(self) -> None:
        with pytest.raises(KeyError, match="Unknown template"):
            build_prompt(
                template_name="nonexistent",
                source_content="content",
                tone=Tone.PROFESSIONAL_CASUAL,
                language=Language.EN,
                length=Length.STANDARD,
            )
