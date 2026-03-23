"""Tests for post output — display, clipboard, file save, actions."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pyperclip

from linkedin_post_generator.output.actions import (
    ACTION_COPY,
    ACTION_EXIT,
    ACTION_REFINE,
    ACTION_SAVE,
    post_action_menu,
)
from linkedin_post_generator.output.clipboard import copy_to_clipboard
from linkedin_post_generator.output.display import display_post
from linkedin_post_generator.output.file_save import save_to_file


class TestDisplayPost:
    """Rich panel display of generated posts."""

    def test_does_not_raise(self) -> None:
        """Smoke test — display should not crash."""
        display_post(
            text="Hello LinkedIn!",
            template_label="Discovery",
            language="PL",
        )

    def test_auto_calculates_counts(self) -> None:
        """When counts are None, they're auto-calculated."""
        # Just verify it doesn't crash with auto-calculation
        display_post(
            text="Two words",
            template_label="TIL",
            language="EN",
            char_count=None,
            word_count=None,
        )

    def test_explicit_counts(self) -> None:
        """Explicit counts are used when provided."""
        display_post(
            text="Test post",
            template_label="Opinion",
            language="PL",
            char_count=42,
            word_count=7,
        )


class TestCopyToClipboard:
    """Clipboard copy with error handling."""

    @patch("linkedin_post_generator.output.clipboard.pyperclip")
    def test_successful_copy(self, mock_clip: MagicMock) -> None:
        result = copy_to_clipboard("Hello LinkedIn!")
        assert result is True
        mock_clip.copy.assert_called_once_with("Hello LinkedIn!")

    @patch("linkedin_post_generator.output.clipboard.pyperclip")
    def test_clipboard_error_returns_false(self, mock_clip: MagicMock) -> None:
        mock_clip.copy.side_effect = pyperclip.PyperclipException("No clipboard")
        mock_clip.PyperclipException = pyperclip.PyperclipException
        result = copy_to_clipboard("Hello")
        assert result is False


class TestSaveToFile:
    """File save — plain text only, in posts/ subdirectory."""

    def test_creates_file_in_posts_subdir(self, tmp_path: Path) -> None:
        path = save_to_file(
            text="My LinkedIn post",
            source_title="Test source",
            template_name="discovery",
            language="pl",
            directory=tmp_path,
        )
        assert path.exists()
        assert path.suffix == ".txt"
        assert path.parent.name == "posts"

    def test_file_contains_only_post_text(self, tmp_path: Path) -> None:
        path = save_to_file(
            text="My LinkedIn post content",
            source_title="Source",
            template_name="til",
            language="en",
            directory=tmp_path,
        )
        content = path.read_text(encoding="utf-8")
        assert content == "My LinkedIn post content"

    def test_no_metadata_in_file(self, tmp_path: Path) -> None:
        path = save_to_file(
            text="Post text",
            source_title="GitHub: cool/repo",
            template_name="discovery",
            language="pl",
            directory=tmp_path,
        )
        content = path.read_text(encoding="utf-8")
        assert "Source:" not in content
        assert "Template:" not in content

    def test_filename_has_timestamp(self, tmp_path: Path) -> None:
        path = save_to_file(
            text="Post",
            source_title="s",
            template_name="t",
            language="en",
            directory=tmp_path,
        )
        assert path.name.startswith("linkedin-post-")
        assert path.name.endswith(".txt")


class TestPostActionMenu:
    """Action menu dispatch."""

    @patch("linkedin_post_generator.output.actions.inquirer")
    @patch("linkedin_post_generator.output.actions.copy_to_clipboard")
    def test_copy_loops_back(self, mock_copy: MagicMock, mock_inq: MagicMock) -> None:
        """Copy action loops, then Exit breaks."""
        prompt = MagicMock()
        prompt.execute.side_effect = [ACTION_COPY, ACTION_EXIT]
        mock_inq.select.return_value = prompt

        result = post_action_menu("text", "src", "tmpl", "pl")
        assert result == ACTION_EXIT
        mock_copy.assert_called_once_with("text")

    @patch("linkedin_post_generator.output.actions.inquirer")
    @patch("linkedin_post_generator.output.actions.save_to_file")
    def test_save_loops_back(self, mock_save: MagicMock, mock_inq: MagicMock) -> None:
        """Save action loops, then Exit breaks."""
        prompt = MagicMock()
        prompt.execute.side_effect = [ACTION_SAVE, ACTION_EXIT]
        mock_inq.select.return_value = prompt

        result = post_action_menu("text", "src", "tmpl", "en")
        assert result == ACTION_EXIT
        mock_save.assert_called_once()

    @patch("linkedin_post_generator.output.actions.inquirer")
    def test_refine_returns_immediately(self, mock_inq: MagicMock) -> None:
        prompt = MagicMock()
        prompt.execute.return_value = ACTION_REFINE
        mock_inq.select.return_value = prompt

        result = post_action_menu("text", "src", "tmpl", "pl")
        assert result == ACTION_REFINE

    @patch("linkedin_post_generator.output.actions.inquirer")
    def test_exit_returns_immediately(self, mock_inq: MagicMock) -> None:
        prompt = MagicMock()
        prompt.execute.return_value = ACTION_EXIT
        mock_inq.select.return_value = prompt

        result = post_action_menu("text", "src", "tmpl", "pl")
        assert result == ACTION_EXIT
