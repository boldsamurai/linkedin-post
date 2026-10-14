"""Tests for the generate command source input flow."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from linkedin_post_generator.cli import app
from linkedin_post_generator.cli.generate_cmd import (
    _fetch_source,
    _source_input,
    run_generate,
)
from linkedin_post_generator.config.model import AppConfig
from linkedin_post_generator.fetcher import FetchError
from linkedin_post_generator.fetcher.models import FetchedContent, SourceType
from linkedin_post_generator.templates import TemplateError

runner = CliRunner()

GITHUB_CONTENT = FetchedContent(
    title="owner/repo: A cool project",
    text="Repository: owner/repo\nStars: 1000\n--- README ---\nHello world",
    url="https://github.com/owner/repo",
)

URL_CONTENT = FetchedContent(
    title="An Interesting Article",
    text="Article body text about interesting things.",
    url="https://example.com/article",
)


class TestFetchSource:
    """Source fetching dispatch based on type."""

    @patch("linkedin_post_generator.cli.generate_cmd.fetch_github_repo")
    def test_github_calls_fetch_github(self, mock_fetch: MagicMock) -> None:
        mock_fetch.return_value = GITHUB_CONTENT
        result = _fetch_source("https://github.com/owner/repo", SourceType.GITHUB)
        assert result == GITHUB_CONTENT
        mock_fetch.assert_called_once_with("https://github.com/owner/repo")

    @patch("linkedin_post_generator.cli.generate_cmd.fetch_url")
    def test_url_calls_fetch_url(self, mock_fetch: MagicMock) -> None:
        mock_fetch.return_value = URL_CONTENT
        result = _fetch_source("https://example.com/article", SourceType.URL)
        assert result == URL_CONTENT
        mock_fetch.assert_called_once_with("https://example.com/article")

    @patch("linkedin_post_generator.cli.generate_cmd.create_note")
    def test_long_text_calls_create_note(self, mock_note: MagicMock) -> None:
        note = FetchedContent(
            title="Python decorators are a powerful feature",
            text="Python decorators are a powerful feature that allows...",
            url="",
        )
        mock_note.return_value = note
        result = _fetch_source(
            "Python decorators are a powerful feature that allows...",
            SourceType.TEXT,
        )
        assert result == note
        mock_note.assert_called_once()

    @patch("linkedin_post_generator.cli.generate_cmd.prompt_for_note")
    def test_short_text_prompts_for_more(self, mock_prompt: MagicMock) -> None:
        note = FetchedContent(title="Python", text="Python is great", url="")
        mock_prompt.return_value = note
        result = _fetch_source("Python", SourceType.TEXT)
        assert result == note
        mock_prompt.assert_called_once()


class TestPresetSource:
    """run_generate with a source chosen elsewhere (e.g. by suggest)."""

    @patch("linkedin_post_generator.cli.generate_cmd.Prompt")
    @patch("linkedin_post_generator.cli.generate_cmd.fetch_url")
    def test_preset_source_skips_prompt(
        self, mock_fetch: MagicMock, mock_prompt: MagicMock
    ) -> None:
        mock_fetch.return_value = URL_CONTENT

        result = _source_input("https://example.com/article")

        assert result == URL_CONTENT
        mock_fetch.assert_called_once_with("https://example.com/article")
        mock_prompt.ask.assert_not_called()

    @patch("linkedin_post_generator.cli.generate_cmd.Prompt")
    @patch("linkedin_post_generator.cli.generate_cmd.fetch_url")
    def test_preset_source_fetch_error_aborts_without_prompt(
        self, mock_fetch: MagicMock, mock_prompt: MagicMock
    ) -> None:
        mock_fetch.side_effect = FetchError("https://example.com/article", "HTTP 404")

        assert _source_input("https://example.com/article") is None
        mock_prompt.ask.assert_not_called()

    @patch("linkedin_post_generator.cli.generate_cmd._check_dedup")
    @patch("linkedin_post_generator.cli.generate_cmd.load_config")
    @patch("linkedin_post_generator.cli.generate_cmd.config_exists")
    @patch("linkedin_post_generator.cli.generate_cmd.fetch_url")
    def test_run_generate_runs_dedup_for_preset(
        self,
        mock_fetch: MagicMock,
        mock_exists: MagicMock,
        mock_load: MagicMock,
        mock_dedup: MagicMock,
    ) -> None:
        mock_exists.return_value = True
        mock_load.return_value = AppConfig()
        mock_fetch.return_value = URL_CONTENT
        mock_dedup.return_value = False  # user cancels at the dedup warning

        with patch(
            "linkedin_post_generator.cli.generate_cmd.select_template"
        ) as mock_select:
            run_generate("https://example.com/article")

        mock_dedup.assert_called_once_with("https://example.com/article")
        mock_select.assert_not_called()


class TestTemplateErrorBoundary:
    """A broken custom template is reported, never shown as a traceback."""

    @patch("linkedin_post_generator.cli.generate_cmd.select_template")
    @patch("linkedin_post_generator.cli.generate_cmd._check_dedup")
    @patch("linkedin_post_generator.cli.generate_cmd.load_config")
    @patch("linkedin_post_generator.cli.generate_cmd.config_exists")
    @patch("linkedin_post_generator.cli.generate_cmd.fetch_url")
    def test_template_error_shows_panel_without_traceback(
        self,
        mock_fetch: MagicMock,
        mock_exists: MagicMock,
        mock_load: MagicMock,
        mock_dedup: MagicMock,
        mock_select: MagicMock,
    ) -> None:
        mock_exists.return_value = True
        mock_load.return_value = AppConfig()
        mock_fetch.return_value = URL_CONTENT
        mock_dedup.return_value = True
        bad_file = Path("/home/user/.config/linkedin-post/templates/weekly.toml")
        mock_select.side_effect = TemplateError(bad_file, "missing field 'label'")

        with patch("linkedin_post_generator.cli.generate_cmd.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "https://example.com/article"
            result = runner.invoke(app, ["generate"])

        assert result.exit_code == 0, result.output
        assert "❌ Error" in result.output
        assert "weekly.toml" in result.output
        assert "missing field 'label'" in result.output
        assert "Traceback" not in result.output
