"""Tests for interactive selection steps in the generate flow."""

from unittest.mock import MagicMock, patch

from linkedin_post_generator.cli.selections import (
    select_language,
    select_length,
    select_template,
    select_tone,
)
from linkedin_post_generator.config.model import Language, Length, Tone


def _mock_inquirer_select(return_value: str):
    """Create a mock for inquirer.select().execute() chain."""
    mock_prompt = MagicMock()
    mock_prompt.execute.return_value = return_value
    return mock_prompt


class TestSelectTemplate:
    """Template selection menu."""

    @patch("linkedin_post_generator.cli.selections.inquirer")
    def test_returns_selected_template_name(self, mock_inq: MagicMock) -> None:
        mock_inq.select.return_value = _mock_inquirer_select("discovery")
        result = select_template()
        assert result == "discovery"

    @patch("linkedin_post_generator.cli.selections.inquirer")
    def test_lists_all_templates(self, mock_inq: MagicMock) -> None:
        mock_inq.select.return_value = _mock_inquirer_select("opinion")
        select_template()
        call_kwargs = mock_inq.select.call_args.kwargs
        choices = call_kwargs["choices"]
        names = [c["value"] for c in choices]
        assert "discovery" in names
        assert "opinion" in names
        assert "til" in names
        assert "project-showcase" in names
        assert "article-reaction" in names


class TestSelectLanguage:
    """Language selection with config default."""

    @patch("linkedin_post_generator.cli.selections.inquirer")
    def test_returns_selected_language(self, mock_inq: MagicMock) -> None:
        mock_inq.select.return_value = _mock_inquirer_select("en")
        result = select_language(default=Language.PL)
        assert result == Language.EN

    @patch("linkedin_post_generator.cli.selections.inquirer")
    def test_passes_config_default(self, mock_inq: MagicMock) -> None:
        mock_inq.select.return_value = _mock_inquirer_select("pl")
        select_language(default=Language.EN)
        call_kwargs = mock_inq.select.call_args.kwargs
        assert call_kwargs["default"] == "en"


class TestSelectTone:
    """Tone selection with config default."""

    @patch("linkedin_post_generator.cli.selections.inquirer")
    def test_returns_selected_tone(self, mock_inq: MagicMock) -> None:
        mock_inq.select.return_value = _mock_inquirer_select("technical")
        result = select_tone(default=Tone.PROFESSIONAL_CASUAL)
        assert result == Tone.TECHNICAL

    @patch("linkedin_post_generator.cli.selections.inquirer")
    def test_passes_config_default(self, mock_inq: MagicMock) -> None:
        mock_inq.select.return_value = _mock_inquirer_select("storytelling")
        select_tone(default=Tone.STORYTELLING)
        call_kwargs = mock_inq.select.call_args.kwargs
        assert call_kwargs["default"] == "storytelling"


class TestSelectLength:
    """Length selection with config default."""

    @patch("linkedin_post_generator.cli.selections.inquirer")
    def test_returns_selected_length(self, mock_inq: MagicMock) -> None:
        mock_inq.select.return_value = _mock_inquirer_select("long")
        result = select_length(default=Length.STANDARD)
        assert result == Length.LONG

    @patch("linkedin_post_generator.cli.selections.inquirer")
    def test_passes_config_default(self, mock_inq: MagicMock) -> None:
        mock_inq.select.return_value = _mock_inquirer_select("short")
        select_length(default=Length.SHORT)
        call_kwargs = mock_inq.select.call_args.kwargs
        assert call_kwargs["default"] == "short"
