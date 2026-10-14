"""RSS/Atom feed fetching: download with httpx, parse with feedparser."""

import calendar
from datetime import UTC, datetime

import feedparser

from linkedin_post_generator.fetcher.exceptions import FetchError
from linkedin_post_generator.fetcher.models import FeedEntry, FeedFetchResult
from linkedin_post_generator.fetcher.url_fetcher import _fetch_response

DEFAULT_LIMIT_PER_FEED = 10

_OLDEST = datetime.min.replace(tzinfo=UTC)


def fetch_feed_entries(
    feed_urls: list[str], limit_per_feed: int = DEFAULT_LIMIT_PER_FEED
) -> FeedFetchResult:
    """Fetch several feeds and merge their newest entries.

    A feed that fails to download or parse is reported in ``failed_feeds``
    instead of aborting the whole fetch.

    Args:
        feed_urls: RSS or Atom feed URLs.
        limit_per_feed: Maximum number of newest entries taken from each feed.

    Returns:
        FeedFetchResult with entries sorted newest first (undated entries last)
        and the URLs of feeds that failed.

    Raises:
        FetchError: If every feed failed.
    """
    entries: list[FeedEntry] = []
    failed_feeds: list[str] = []

    for url in feed_urls:
        try:
            entries.extend(_fetch_single_feed(url, limit_per_feed))
        except FetchError:
            failed_feeds.append(url)

    if feed_urls and len(failed_feeds) == len(feed_urls):
        raise FetchError(", ".join(failed_feeds), "All feeds failed")

    return FeedFetchResult(
        entries=sorted(entries, key=_sort_key, reverse=True),
        failed_feeds=failed_feeds,
    )


def _fetch_single_feed(url: str, limit: int) -> list[FeedEntry]:
    """Download and parse one feed, returning its newest entries."""
    # Raw bytes, not text: feedparser detects the encoding from the XML prolog.
    parsed = feedparser.parse(_fetch_response(url).content)
    feed_title = parsed.feed.get("title", "").strip() or url
    entries = [
        FeedEntry(
            title=entry.get("title", "").strip() or entry.link,
            url=entry.link,
            published=_published_at(entry),
            feed_title=feed_title,
        )
        for entry in parsed.entries
        if entry.get("link")
    ]
    # Judge by the entries we keep: a lenient parse of broken XML can yield
    # link-less fragments. An empty ``version`` means no RSS/Atom format was
    # recognised, e.g. the URL returned an HTML page instead of a feed.
    if not entries and (parsed.bozo or not parsed.version):
        raise FetchError(url, f"Invalid feed ({parsed.get('bozo_exception')})")
    return sorted(entries, key=_sort_key, reverse=True)[:limit]


def _published_at(entry: feedparser.FeedParserDict) -> datetime | None:
    """Convert feedparser's UTC struct_time to an aware datetime."""
    parsed_time = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed_time is None:
        return None
    return datetime.fromtimestamp(calendar.timegm(parsed_time), tz=UTC)


def _sort_key(entry: FeedEntry) -> datetime:
    """Sort key placing undated entries after every dated one."""
    return entry.published or _OLDEST
