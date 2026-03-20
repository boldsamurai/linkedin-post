"""Tests for source type auto-detection."""

from linkedin_post_generator.fetcher.detector import detect_source_type
from linkedin_post_generator.fetcher.models import SourceType


class TestDetectGitHub:
    """GitHub URL detection."""

    def test_github_https_url(self) -> None:
        result = detect_source_type("https://github.com/pallets/flask")
        assert result == SourceType.GITHUB

    def test_github_http_url(self) -> None:
        result = detect_source_type("http://github.com/pallets/flask")
        assert result == SourceType.GITHUB

    def test_github_url_without_scheme(self) -> None:
        result = detect_source_type("github.com/pallets/flask")
        assert result == SourceType.GITHUB

    def test_github_url_with_path(self) -> None:
        result = detect_source_type("https://github.com/pallets/flask/tree/main/src")
        assert result == SourceType.GITHUB

    def test_github_url_with_git_suffix(self) -> None:
        result = detect_source_type("https://github.com/pallets/flask.git")
        assert result == SourceType.GITHUB

    def test_github_url_with_whitespace(self) -> None:
        result = detect_source_type("  https://github.com/pallets/flask  ")
        assert result == SourceType.GITHUB


class TestDetectURL:
    """Generic URL detection."""

    def test_https_article_url(self) -> None:
        result = detect_source_type("https://blog.example.com/my-article")
        assert result == SourceType.URL

    def test_http_url(self) -> None:
        result = detect_source_type("http://example.com/page")
        assert result == SourceType.URL

    def test_url_with_query_params(self) -> None:
        result = detect_source_type("https://example.com/page?id=123&lang=pl")
        assert result == SourceType.URL

    def test_url_with_whitespace(self) -> None:
        result = detect_source_type("  https://example.com/page  ")
        assert result == SourceType.URL


class TestDetectText:
    """Free-text note detection."""

    def test_plain_text(self) -> None:
        result = detect_source_type("Today I learned about Python decorators")
        assert result == SourceType.TEXT

    def test_empty_string(self) -> None:
        result = detect_source_type("")
        assert result == SourceType.TEXT

    def test_whitespace_only(self) -> None:
        result = detect_source_type("   ")
        assert result == SourceType.TEXT

    def test_text_mentioning_github(self) -> None:
        """Text that mentions github but is not a URL should be TEXT."""
        result = detect_source_type("Check out the github project for details")
        assert result == SourceType.TEXT

    def test_text_with_url_fragment(self) -> None:
        """Partial URL without scheme should be TEXT (not github.com)."""
        result = detect_source_type("visit example.com for more info")
        assert result == SourceType.TEXT

    def test_multiline_text(self) -> None:
        result = detect_source_type("Line one\nLine two\nLine three")
        assert result == SourceType.TEXT
