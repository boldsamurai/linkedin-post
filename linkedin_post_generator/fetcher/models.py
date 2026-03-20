"""Data models for fetched content."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FetchedContent:
    """Extracted content from a source (article, GitHub repo, note)."""

    title: str
    text: str
    url: str
