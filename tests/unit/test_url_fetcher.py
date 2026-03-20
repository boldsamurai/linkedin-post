"""Tests for URL content extraction."""

from pathlib import Path

import httpx
import pytest

from linkedin_post_generator.fetcher import (
    FetchContentError,
    FetchedContent,
    FetchError,
    FetchTimeoutError,
    fetch_url,
)
from linkedin_post_generator.fetcher.url_fetcher import USER_AGENT

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "html_pages"
SAMPLE_URL = "https://example.com/blog/python-async"


def _read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


class TestFetchUrlHappyPath:
    def test_extracts_title_and_text(self, httpx_mock):
        html = _read_fixture("sample_article.html")
        httpx_mock.add_response(
            url=SAMPLE_URL,
            html=html,
        )

        result = fetch_url(SAMPLE_URL)

        assert isinstance(result, FetchedContent)
        assert "Python Async" in result.title
        assert "async/await" in result.text
        assert result.url == SAMPLE_URL

    def test_strips_html_tags(self, httpx_mock):
        html = _read_fixture("sample_article.html")
        httpx_mock.add_response(url=SAMPLE_URL, html=html)

        result = fetch_url(SAMPLE_URL)

        assert "<p>" not in result.text
        assert "<article>" not in result.text

    def test_strips_navigation_and_footer(self, httpx_mock):
        html = _read_fixture("sample_article.html")
        httpx_mock.add_response(url=SAMPLE_URL, html=html)

        result = fetch_url(SAMPLE_URL)

        # readability should extract article content, not nav/footer
        assert "Copyright" not in result.text

    def test_sends_user_agent_header(self, httpx_mock):
        html = _read_fixture("sample_article.html")
        httpx_mock.add_response(url=SAMPLE_URL, html=html)

        fetch_url(SAMPLE_URL)

        request = httpx_mock.get_request()
        assert request.headers["user-agent"] == USER_AGENT


class TestFetchUrlFollowsRedirects:
    def test_follows_redirect(self, httpx_mock):
        redirect_url = "https://example.com/old-url"
        final_url = "https://example.com/blog/python-async"
        html = _read_fixture("sample_article.html")

        httpx_mock.add_response(
            url=redirect_url,
            status_code=301,
            headers={"location": final_url},
        )
        httpx_mock.add_response(url=final_url, html=html)

        result = fetch_url(redirect_url)

        assert "Python Async" in result.title


class TestFetchUrlErrors:
    def test_timeout_raises_fetch_timeout_error(self, httpx_mock):
        httpx_mock.add_exception(httpx.ReadTimeout("timed out"))

        with pytest.raises(FetchTimeoutError, match="timed out"):
            fetch_url(SAMPLE_URL)

    def test_connect_timeout_raises_fetch_timeout_error(self, httpx_mock):
        httpx_mock.add_exception(httpx.ConnectTimeout("connect timed out"))

        with pytest.raises(FetchTimeoutError, match="timed out"):
            fetch_url(SAMPLE_URL)

    def test_404_raises_fetch_error(self, httpx_mock):
        httpx_mock.add_response(url=SAMPLE_URL, status_code=404)

        with pytest.raises(FetchError, match="HTTP 404"):
            fetch_url(SAMPLE_URL)

    def test_500_raises_fetch_error(self, httpx_mock):
        httpx_mock.add_response(url=SAMPLE_URL, status_code=500)

        with pytest.raises(FetchError, match="HTTP 500"):
            fetch_url(SAMPLE_URL)

    def test_connection_error_raises_fetch_error(self, httpx_mock):
        httpx_mock.add_exception(httpx.ConnectError("Connection refused"))

        with pytest.raises(FetchError, match="HTTP error"):
            fetch_url(SAMPLE_URL)

    def test_non_html_raises_fetch_content_error(self, httpx_mock):
        httpx_mock.add_response(
            url=SAMPLE_URL,
            content=b"%PDF-1.4 fake pdf content",
            headers={"content-type": "application/pdf"},
        )

        with pytest.raises(FetchContentError, match="not HTML"):
            fetch_url(SAMPLE_URL)

    def test_empty_html_raises_fetch_content_error(self, httpx_mock):
        httpx_mock.add_response(
            url=SAMPLE_URL,
            html="<html><head><title>Empty</title></head><body></body></html>",
        )

        with pytest.raises(FetchContentError, match="no extractable content"):
            fetch_url(SAMPLE_URL)
