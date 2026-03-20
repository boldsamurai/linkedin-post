"""GitHub repository fetching via REST API."""

import os
import re

import httpx

from linkedin_post_generator import __version__
from linkedin_post_generator.fetcher.exceptions import (
    FetchError,
    FetchTimeoutError,
)
from linkedin_post_generator.fetcher.models import FetchedContent, GitHubRepo

USER_AGENT = f"linkedin-post-generator/{__version__}"
CONNECT_TIMEOUT = 15.0
READ_TIMEOUT = 30.0
MAX_README_LENGTH = 10_000

_GITHUB_URL_RE = re.compile(
    r"(?:https?://)?github\.com/(?P<owner>[^/]+)/(?P<repo>[^/#?]+)"
)

API_BASE = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"


def parse_github_url(url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from a GitHub URL.

    Returns:
        Tuple of (owner, repo) or None if not a GitHub URL.
    """
    match = _GITHUB_URL_RE.match(url)
    if not match:
        return None
    repo = match.group("repo")
    # Strip .git suffix if present
    if repo.endswith(".git"):
        repo = repo[:-4]
    return match.group("owner"), repo


def fetch_github_repo(url: str) -> FetchedContent:
    """Fetch GitHub repo metadata and README, return as FetchedContent.

    Args:
        url: GitHub repository URL.

    Returns:
        FetchedContent with repo summary as title and metadata + README as text.

    Raises:
        FetchError: If the URL is not a valid GitHub repo URL or API fails.
        FetchTimeoutError: If the request times out.
    """
    parsed = parse_github_url(url)
    if not parsed:
        raise FetchError(url, "Not a valid GitHub repository URL")

    owner, repo_name = parsed
    repo = _fetch_repo_data(owner, repo_name, url)

    base = f"{repo.owner}/{repo.name}"
    title = f"{base}: {repo.description}" if repo.description else base

    text_parts = [
        f"Repository: {repo.owner}/{repo.name}",
        f"Description: {repo.description}" if repo.description else None,
        f"Stars: {repo.stars:,}",
        f"Language: {repo.language}" if repo.language else None,
        f"Topics: {', '.join(repo.topics)}" if repo.topics else None,
        "",
        "--- README ---",
        repo.readme_text if repo.readme_text else "(no README available)",
    ]
    text = "\n".join(part for part in text_parts if part is not None)

    return FetchedContent(title=title, text=text, url=url)


def _fetch_repo_data(owner: str, repo_name: str, url: str) -> GitHubRepo:
    """Fetch metadata and README from GitHub API."""
    client = _build_client()

    metadata = _fetch_metadata(client, owner, repo_name, url)
    readme = _fetch_readme(client, owner, repo_name)

    return GitHubRepo(
        owner=owner,
        name=repo_name,
        description=metadata.get("description") or "",
        stars=metadata.get("stargazers_count", 0),
        language=metadata.get("language") or "",
        topics=metadata.get("topics") or [],
        readme_text=readme,
        url=url,
    )


def _build_client() -> httpx.Client:
    """Build httpx client with auth headers if GITHUB_TOKEN is set."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return httpx.Client(
        headers=headers,
        timeout=httpx.Timeout(READ_TIMEOUT, connect=CONNECT_TIMEOUT),
        follow_redirects=True,
    )


def _fetch_metadata(client: httpx.Client, owner: str, repo_name: str, url: str) -> dict:
    """Fetch repository metadata from GitHub API."""
    api_url = f"{API_BASE}/repos/{owner}/{repo_name}"
    try:
        response = client.get(api_url)
    except httpx.TimeoutException as exc:
        raise FetchTimeoutError(url) from exc
    except httpx.HTTPError as exc:
        raise FetchError(url, f"GitHub API error: {exc}") from exc

    if response.status_code == 404:
        raise FetchError(url, "Repository not found")
    if response.status_code >= 400:
        raise FetchError(url, f"GitHub API HTTP {response.status_code}")

    return response.json()


def _fetch_readme(client: httpx.Client, owner: str, repo_name: str) -> str:
    """Fetch README content, with fallback to raw.githubusercontent.com."""
    # Try API first
    readme = _fetch_readme_via_api(client, owner, repo_name)
    if readme is not None:
        return readme

    # Fallback to raw URL
    return _fetch_readme_via_raw(client, owner, repo_name)


def _fetch_readme_via_api(
    client: httpx.Client, owner: str, repo_name: str
) -> str | None:
    """Fetch README via GitHub API. Returns None on failure."""
    api_url = f"{API_BASE}/repos/{owner}/{repo_name}/readme"
    try:
        response = client.get(
            api_url,
            headers={"Accept": "application/vnd.github.raw"},
        )
        if response.status_code == 200:
            return _truncate_readme(response.text)
    except httpx.HTTPError:
        pass
    return None


def _fetch_readme_via_raw(client: httpx.Client, owner: str, repo_name: str) -> str:
    """Fetch README from raw.githubusercontent.com as fallback."""
    raw_url = f"{RAW_BASE}/{owner}/{repo_name}/HEAD/README.md"
    try:
        response = client.get(raw_url)
        if response.status_code == 200:
            return _truncate_readme(response.text)
    except httpx.HTTPError:
        pass
    return ""


def _truncate_readme(text: str) -> str:
    """Truncate README if it exceeds MAX_README_LENGTH."""
    if len(text) <= MAX_README_LENGTH:
        return text
    return text[:MAX_README_LENGTH] + "\n\n[... README truncated]"
