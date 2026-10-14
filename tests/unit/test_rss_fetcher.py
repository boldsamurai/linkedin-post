"""Tests for RSS/Atom feed fetching."""

from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from linkedin_post_generator.fetcher import (
    FeedFetchResult,
    FetchError,
    fetch_feed_entries,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "feeds"
RSS_URL = "https://python.example.com/rss.xml"
ATOM_URL = "https://devops.example.org/atom.xml"
BROKEN_URL = "https://broken.example.net/feed"


def _read_fixture(name: str) -> bytes:
    return (FIXTURES_DIR / name).read_bytes()


def test_fetch_feed_entries_parses_rss2(httpx_mock):
    httpx_mock.add_response(url=RSS_URL, content=_read_fixture("rss2.xml"))

    result = fetch_feed_entries([RSS_URL])

    assert isinstance(result, FeedFetchResult)
    assert [e.url for e in result.entries] == [
        "https://python.example.com/uv",
        "https://python.example.com/asyncio",
        "https://python.example.com/undated",
    ], "Expected newest first, undated last, linkless item skipped"
    newest = result.entries[0]
    assert newest.title == "Newest post about uv"
    assert newest.feed_title == "Python Weekly Notes"
    assert newest.published == datetime(2026, 10, 12, 8, 0, tzinfo=UTC)
    assert result.entries[-1].published is None
    assert result.failed_feeds == []


def test_fetch_feed_entries_parses_atom(httpx_mock):
    httpx_mock.add_response(url=ATOM_URL, content=_read_fixture("atom.xml"))

    result = fetch_feed_entries([ATOM_URL])

    assert [e.title for e in result.entries] == [
        "Kubernetes upgrade lessons",
        "Terraform state tips",
    ]
    assert result.entries[0].feed_title == "DevOps Diary"
    # published wins over updated, converted to UTC
    assert result.entries[1].published == datetime(2026, 10, 1, 7, 30, tzinfo=UTC)


def test_fetch_feed_entries_merges_feeds_newest_first(httpx_mock):
    httpx_mock.add_response(url=RSS_URL, content=_read_fixture("rss2.xml"))
    httpx_mock.add_response(url=ATOM_URL, content=_read_fixture("atom.xml"))

    result = fetch_feed_entries([RSS_URL, ATOM_URL])

    assert [e.url for e in result.entries[:3]] == [
        "https://python.example.com/uv",
        "https://devops.example.org/k8s-upgrade",
        "https://python.example.com/asyncio",
    ]


def test_fetch_feed_entries_limits_per_feed(httpx_mock):
    httpx_mock.add_response(url=RSS_URL, content=_read_fixture("rss2.xml"))

    result = fetch_feed_entries([RSS_URL], limit_per_feed=1)

    assert [e.url for e in result.entries] == ["https://python.example.com/uv"]


def test_fetch_feed_entries_one_server_error_one_ok(httpx_mock):
    httpx_mock.add_response(url=BROKEN_URL, status_code=500)
    httpx_mock.add_response(url=ATOM_URL, content=_read_fixture("atom.xml"))

    result = fetch_feed_entries([BROKEN_URL, ATOM_URL])

    assert result.failed_feeds == [BROKEN_URL]
    assert len(result.entries) == 2


def test_fetch_feed_entries_malformed_xml_marks_feed_failed(httpx_mock):
    httpx_mock.add_response(url=BROKEN_URL, content=_read_fixture("malformed.xml"))
    httpx_mock.add_response(url=RSS_URL, content=_read_fixture("rss2.xml"))

    result = fetch_feed_entries([BROKEN_URL, RSS_URL])

    assert result.failed_feeds == [BROKEN_URL]
    assert len(result.entries) == 3


def test_fetch_feed_entries_html_page_marks_feed_failed(httpx_mock):
    httpx_mock.add_response(
        url=BROKEN_URL, html="<html><body><p>Not a feed</p></body></html>"
    )
    httpx_mock.add_response(url=RSS_URL, content=_read_fixture("rss2.xml"))

    result = fetch_feed_entries([BROKEN_URL, RSS_URL])

    assert result.failed_feeds == [BROKEN_URL]


def test_fetch_feed_entries_valid_empty_feed_is_not_failure(httpx_mock):
    empty_rss = (
        b'<?xml version="1.0"?><rss version="2.0">'
        b"<channel><title>Quiet</title></channel></rss>"
    )
    httpx_mock.add_response(url=RSS_URL, content=empty_rss)

    result = fetch_feed_entries([RSS_URL])

    assert result == FeedFetchResult(entries=[], failed_feeds=[])


def test_fetch_feed_entries_connection_error_marks_feed_failed(httpx_mock):
    httpx_mock.add_exception(httpx.ConnectError("refused"), url=BROKEN_URL)
    httpx_mock.add_response(url=RSS_URL, content=_read_fixture("rss2.xml"))

    result = fetch_feed_entries([BROKEN_URL, RSS_URL])

    assert result.failed_feeds == [BROKEN_URL]
    assert len(result.entries) == 3, "The healthy feed should still return entries"


def test_fetch_feed_entries_broken_feed_with_linkless_entries_fails(httpx_mock):
    broken = b'<rss version="2.0"><channel><item><title>Fragment</title><item>'
    httpx_mock.add_response(url=BROKEN_URL, content=broken)
    httpx_mock.add_response(url=RSS_URL, content=_read_fixture("rss2.xml"))

    result = fetch_feed_entries([BROKEN_URL, RSS_URL])

    assert result.failed_feeds == [BROKEN_URL]


def test_fetch_feed_entries_untitled_entry_falls_back_to_link(httpx_mock):
    rss = (
        b'<?xml version="1.0"?><rss version="2.0"><channel><title>T</title>'
        b"<item><link>https://python.example.com/no-title</link></item>"
        b"</channel></rss>"
    )
    httpx_mock.add_response(url=RSS_URL, content=rss)

    result = fetch_feed_entries([RSS_URL])

    assert result.entries[0].title == "https://python.example.com/no-title"


def test_fetch_feed_entries_raises_when_all_fail(httpx_mock):
    httpx_mock.add_response(url=BROKEN_URL, status_code=500)
    httpx_mock.add_response(url=RSS_URL, content=_read_fixture("malformed.xml"))

    with pytest.raises(FetchError, match="All feeds failed"):
        fetch_feed_entries([BROKEN_URL, RSS_URL])


def test_fetch_feed_entries_empty_list_returns_empty_result():
    assert fetch_feed_entries([]) == FeedFetchResult(entries=[], failed_feeds=[])


def test_fetch_feed_entries_skips_non_http_links(httpx_mock):
    rss = (
        b'<?xml version="1.0"?><rss version="2.0"><channel><title>T</title>'
        b"<item><title>Local</title><link>file:///etc/passwd</link></item>"
        b"<item><title>Mail</title><link>mailto:someone@example.com</link></item>"
        b"<item><title>Bad</title><link>http://[</link></item>"
        b"<item><title>Web</title><link>https://python.example.com/web</link></item>"
        b"</channel></rss>"
    )
    httpx_mock.add_response(url=RSS_URL, content=rss)

    result = fetch_feed_entries([RSS_URL])

    assert [e.url for e in result.entries] == ["https://python.example.com/web"]
