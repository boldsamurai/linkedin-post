"""Data models for fetched content."""

from dataclasses import dataclass
from enum import Enum


class SourceType(Enum):
    """Type of content source detected from user input."""

    GITHUB = "github"
    URL = "url"
    TEXT = "text"


@dataclass(frozen=True)
class FetchedContent:
    """Extracted content from a source (article, GitHub repo, note)."""

    title: str
    text: str
    url: str


@dataclass(frozen=True)
class GitHubRepo:
    """Metadata and README content from a GitHub repository."""

    owner: str
    name: str
    description: str
    stars: int
    language: str
    topics: list[str]
    readme_text: str
    url: str
