"""Source type auto-detection from user input."""

import re

from linkedin_post_generator.fetcher.github_fetcher import parse_github_url
from linkedin_post_generator.fetcher.models import SourceType

_URL_RE = re.compile(r"https?://", re.IGNORECASE)


def detect_source_type(user_input: str) -> SourceType:
    """Detect the type of content source from user input.

    Detection order:
        1. GitHub URL (github.com/<owner>/<repo>)
        2. Generic URL (http:// or https://)
        3. Free-text note (everything else)

    Args:
        user_input: Raw string from the user (URL or free text).

    Returns:
        SourceType enum value.
    """
    stripped = user_input.strip()
    if parse_github_url(stripped) is not None:
        return SourceType.GITHUB
    if _URL_RE.search(stripped):
        return SourceType.URL
    return SourceType.TEXT
