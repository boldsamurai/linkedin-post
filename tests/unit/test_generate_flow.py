"""Tests for the generate command source input flow."""

from unittest.mock import MagicMock, patch

from linkedin_post_generator.cli.generate_cmd import _fetch_source
from linkedin_post_generator.fetcher.models import FetchedContent, SourceType

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
