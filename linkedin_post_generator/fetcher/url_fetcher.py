"""URL content extraction using httpx and readability-lxml."""

import re

import httpx
from readability import Document

from linkedin_post_generator import __version__
from linkedin_post_generator.fetcher.exceptions import (
    FetchContentError,
    FetchError,
    FetchTimeoutError,
)
from linkedin_post_generator.fetcher.models import FetchedContent

USER_AGENT = f"linkedin-post-generator/{__version__}"
CONNECT_TIMEOUT = 15.0
READ_TIMEOUT = 30.0

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\n{3,}")


def fetch_url(url: str) -> FetchedContent:
    """Fetch a URL and extract readable article content.

    Args:
        url: The URL to fetch.

    Returns:
        FetchedContent with extracted title and clean text.

    Raises:
        FetchTimeoutError: If the request times out.
        FetchError: If the HTTP request fails (4xx/5xx).
        FetchContentError: If the response is not HTML or has no extractable content.
    """
    response = _fetch_response(url)
    _validate_content_type(url, response)
    return _extract_content(url, response.text)


def _fetch_response(url: str) -> httpx.Response:
    """Make HTTP GET request with proper headers and timeouts."""
    try:
        response = httpx.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=httpx.Timeout(READ_TIMEOUT, connect=CONNECT_TIMEOUT),
            follow_redirects=True,
        )
    except httpx.TimeoutException as exc:
        raise FetchTimeoutError(url) from exc
    except httpx.HTTPError as exc:
        raise FetchError(url, f"HTTP error: {exc}") from exc

    if response.status_code >= 400:
        raise FetchError(url, f"HTTP {response.status_code}")

    return response


def _validate_content_type(url: str, response: httpx.Response) -> None:
    """Check that the response contains HTML content."""
    content_type = response.headers.get("content-type", "")
    if "html" not in content_type.lower():
        raise FetchContentError(url, f"not HTML (got {content_type})")


def _extract_content(url: str, html: str) -> FetchedContent:
    """Extract readable content from HTML using readability-lxml."""
    doc = Document(html)
    title = doc.title().strip()
    summary_html = doc.summary()

    text = _strip_html_tags(summary_html)
    text = _WHITESPACE_RE.sub("\n\n", text).strip()

    if not text:
        raise FetchContentError(url, "no extractable content")

    return FetchedContent(title=title, text=text, url=url)


def _strip_html_tags(html: str) -> str:
    """Remove HTML tags, leaving only text content."""
    return _HTML_TAG_RE.sub("", html)
