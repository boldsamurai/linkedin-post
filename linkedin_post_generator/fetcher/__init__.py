"""Source fetching — extract content from URLs, GitHub repos, and free-text notes."""

from linkedin_post_generator.fetcher.detector import detect_source_type
from linkedin_post_generator.fetcher.exceptions import (
    FetchContentError,
    FetchError,
    FetchTimeoutError,
)
from linkedin_post_generator.fetcher.github_fetcher import (
    fetch_github_repo,
    parse_github_url,
)
from linkedin_post_generator.fetcher.models import (
    FetchedContent,
    GitHubRepo,
    SourceType,
)
from linkedin_post_generator.fetcher.text_input import create_note, prompt_for_note
from linkedin_post_generator.fetcher.url_fetcher import fetch_url

__all__ = [
    "FetchContentError",
    "FetchError",
    "FetchTimeoutError",
    "FetchedContent",
    "GitHubRepo",
    "SourceType",
    "create_note",
    "detect_source_type",
    "fetch_github_repo",
    "fetch_url",
    "parse_github_url",
    "prompt_for_note",
]
