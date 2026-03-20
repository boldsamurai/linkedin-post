"""Tests for free-text note input."""

from unittest.mock import MagicMock, patch

import pyperclip
import pytest

from linkedin_post_generator.fetcher.text_input import (
    MAX_TITLE_LENGTH,
    _extract_title,
    _get_clipboard_text,
    create_note,
    prompt_for_note,
)


class TestCreateNote:
    """Tests for create_note()."""

    def test_basic_note(self):
        result = create_note("My thoughts on Python")
        assert result.text == "My thoughts on Python"
        assert result.title == "My thoughts on Python"
        assert result.url == ""

    def test_custom_title(self):
        result = create_note("Some text here", title="Custom Title")
        assert result.title == "Custom Title"
        assert result.text == "Some text here"

    def test_multiline_title_from_first_line(self):
        text = "First line as title\nSecond line\nThird line"
        result = create_note(text)
        assert result.title == "First line as title"
        assert result.text == text

    def test_long_first_line_truncated(self):
        long_line = "A" * 100
        result = create_note(long_line)
        assert len(result.title) == MAX_TITLE_LENGTH
        assert result.title.endswith("...")

    def test_strips_whitespace(self):
        result = create_note("  hello world  \n\n")
        assert result.text == "hello world"

    def test_empty_text_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            create_note("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            create_note("   \n\n  ")


class TestExtractTitle:
    """Tests for _extract_title()."""

    def test_short_line(self):
        assert _extract_title("Short title") == "Short title"

    def test_exact_max_length(self):
        line = "A" * MAX_TITLE_LENGTH
        assert _extract_title(line) == line

    def test_over_max_length_truncated(self):
        line = "A" * (MAX_TITLE_LENGTH + 10)
        result = _extract_title(line)
        assert len(result) == MAX_TITLE_LENGTH
        assert result.endswith("...")

    def test_multiline_uses_first(self):
        assert _extract_title("First\nSecond\nThird") == "First"


class TestGetClipboardText:
    """Tests for _get_clipboard_text()."""

    @patch("linkedin_post_generator.fetcher.text_input.pyperclip.paste")
    def test_returns_clipboard_content(self, mock_paste):
        mock_paste.return_value = "clipboard text"
        assert _get_clipboard_text() == "clipboard text"

    @patch("linkedin_post_generator.fetcher.text_input.pyperclip.paste")
    def test_strips_whitespace(self, mock_paste):
        mock_paste.return_value = "  text  \n"
        assert _get_clipboard_text() == "text"

    @patch("linkedin_post_generator.fetcher.text_input.pyperclip.paste")
    def test_empty_clipboard(self, mock_paste):
        mock_paste.return_value = ""
        assert _get_clipboard_text() == ""

    @patch("linkedin_post_generator.fetcher.text_input.pyperclip.paste")
    def test_none_clipboard(self, mock_paste):
        mock_paste.return_value = None
        assert _get_clipboard_text() == ""

    @patch("linkedin_post_generator.fetcher.text_input.pyperclip.paste")
    def test_pyperclip_exception_returns_empty(self, mock_paste):
        mock_paste.side_effect = pyperclip.PyperclipException("no clipboard")
        assert _get_clipboard_text() == ""


class TestPromptForNote:
    """Tests for prompt_for_note()."""

    @patch("linkedin_post_generator.fetcher.text_input._get_clipboard_text")
    @patch("linkedin_post_generator.fetcher.text_input.Console")
    def test_manual_input(self, mock_console_cls, mock_clipboard):
        mock_clipboard.return_value = ""
        console = MagicMock()
        mock_console_cls.return_value = console
        console.input.side_effect = ["Line one", "Line two", ""]

        result = prompt_for_note()

        assert result.text == "Line one\nLine two"
        assert result.title == "Line one"

    @patch("linkedin_post_generator.fetcher.text_input._get_clipboard_text")
    @patch("linkedin_post_generator.fetcher.text_input.Console")
    def test_manual_input_eof(self, mock_console_cls, mock_clipboard):
        mock_clipboard.return_value = ""
        console = MagicMock()
        mock_console_cls.return_value = console
        console.input.side_effect = ["Only line", EOFError]

        result = prompt_for_note()

        assert result.text == "Only line"

    @patch("linkedin_post_generator.fetcher.text_input._get_clipboard_text")
    @patch("linkedin_post_generator.fetcher.text_input.Console")
    def test_empty_manual_input_raises(self, mock_console_cls, mock_clipboard):
        mock_clipboard.return_value = ""
        console = MagicMock()
        mock_console_cls.return_value = console
        console.input.side_effect = EOFError

        with pytest.raises(ValueError, match="cannot be empty"):
            prompt_for_note()

    @patch("linkedin_post_generator.fetcher.text_input.Confirm")
    @patch("linkedin_post_generator.fetcher.text_input._get_clipboard_text")
    @patch("linkedin_post_generator.fetcher.text_input.Console")
    def test_clipboard_accepted(self, mock_console_cls, mock_clipboard, mock_confirm):
        mock_clipboard.return_value = "Pasted from clipboard"
        mock_console_cls.return_value = MagicMock()
        mock_confirm.ask.return_value = True

        result = prompt_for_note()

        assert result.text == "Pasted from clipboard"

    @patch("linkedin_post_generator.fetcher.text_input.Confirm")
    @patch("linkedin_post_generator.fetcher.text_input._get_clipboard_text")
    @patch("linkedin_post_generator.fetcher.text_input.Console")
    def test_clipboard_declined_falls_to_manual(
        self, mock_console_cls, mock_clipboard, mock_confirm
    ):
        mock_clipboard.return_value = "Clipboard text"
        console = MagicMock()
        mock_console_cls.return_value = console
        mock_confirm.ask.return_value = False
        console.input.side_effect = ["Manual text", ""]

        result = prompt_for_note()

        assert result.text == "Manual text"
