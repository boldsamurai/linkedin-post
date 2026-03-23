"""Tests for built-in post templates — verify all 5 templates are registered."""

import pytest

from linkedin_post_generator.templates import TEMPLATES, get_template, list_templates
from linkedin_post_generator.templates.builtins import (
    ARTICLE_REACTION,
    DISCOVERY,
    OPINION,
    PROJECT_SHOWCASE,
    TIL,
)

EXPECTED_NAMES = ["discovery", "opinion", "til", "project-showcase", "article-reaction"]


class TestBuiltinRegistration:
    """All 5 templates are registered and accessible."""

    def test_all_five_registered(self) -> None:
        assert len(TEMPLATES) >= 5

    @pytest.mark.parametrize("name", EXPECTED_NAMES)
    def test_template_exists(self, name: str) -> None:
        template = get_template(name)
        assert template.name == name

    def test_list_contains_all(self) -> None:
        templates = list_templates()
        names = [t.name for t in templates]
        for name in EXPECTED_NAMES:
            assert name in names, f"Template '{name}' not in list_templates()"


class TestDiscoveryTemplate:
    """Discovery template content."""

    def test_label(self) -> None:
        assert DISCOVERY.label == "Discovery"

    def test_instructions_mention_hook(self) -> None:
        assert "Hook" in DISCOVERY.instructions

    def test_instructions_mention_value(self) -> None:
        assert "interesting" in DISCOVERY.instructions.lower()


class TestOpinionTemplate:
    """Opinion template content."""

    def test_label(self) -> None:
        assert OPINION.label == "Opinion"

    def test_instructions_mention_bold_statement(self) -> None:
        assert "Bold statement" in OPINION.instructions

    def test_instructions_mention_argumentation(self) -> None:
        assert "Argumentation" in OPINION.instructions


class TestTILTemplate:
    """TIL template content."""

    def test_label(self) -> None:
        assert TIL.label == "TIL"

    def test_instructions_mention_insight(self) -> None:
        assert "insight" in TIL.instructions.lower()

    def test_instructions_mention_short(self) -> None:
        assert "500-800" in TIL.instructions


class TestProjectShowcaseTemplate:
    """Project Showcase template content."""

    def test_label(self) -> None:
        assert PROJECT_SHOWCASE.label == "Project Showcase"

    def test_instructions_mention_problem(self) -> None:
        assert "problem" in PROJECT_SHOWCASE.instructions.lower()

    def test_instructions_mention_lessons(self) -> None:
        assert "learned" in PROJECT_SHOWCASE.instructions.lower()


class TestArticleReactionTemplate:
    """Article Reaction template content."""

    def test_label(self) -> None:
        assert ARTICLE_REACTION.label == "Article Reaction"

    def test_instructions_mention_perspective(self) -> None:
        assert "perspective" in ARTICLE_REACTION.instructions.lower()

    def test_instructions_mention_recommendation(self) -> None:
        assert "Recommendation" in ARTICLE_REACTION.instructions
