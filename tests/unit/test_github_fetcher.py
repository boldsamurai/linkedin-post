"""Tests for GitHub repository fetching."""

import json
from pathlib import Path

import httpx
import pytest

from linkedin_post_generator.fetcher import (
    FetchError,
    FetchTimeoutError,
    fetch_github_repo,
)
from linkedin_post_generator.fetcher.github_fetcher import (
    API_BASE,
    RAW_BASE,
    USER_AGENT,
    parse_github_url,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "api_responses"
REPO_URL = "https://github.com/tiangolo/fastapi"
SAMPLE_README = "# FastAPI\n\nFastAPI is a modern web framework for Python."


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def _mock_github_success(httpx_mock, *, readme_text: str = SAMPLE_README):
    """Register mocks for successful GitHub API calls."""
    metadata = _load_fixture("github_repo.json")

    httpx_mock.add_response(
        url=f"{API_BASE}/repos/tiangolo/fastapi",
        json=metadata,
    )
    httpx_mock.add_response(
        url=f"{API_BASE}/repos/tiangolo/fastapi/readme",
        text=readme_text,
    )


class TestParseGitHubUrl:
    def test_standard_url(self):
        assert parse_github_url("https://github.com/tiangolo/fastapi") == (
            "tiangolo",
            "fastapi",
        )

    def test_url_with_trailing_slash(self):
        assert parse_github_url("https://github.com/tiangolo/fastapi/") == (
            "tiangolo",
            "fastapi",
        )

    def test_url_with_subpath(self):
        result = parse_github_url("https://github.com/tiangolo/fastapi/tree/main/docs")
        assert result == ("tiangolo", "fastapi")

    def test_url_with_git_suffix(self):
        assert parse_github_url("https://github.com/tiangolo/fastapi.git") == (
            "tiangolo",
            "fastapi",
        )

    def test_url_without_scheme(self):
        assert parse_github_url("github.com/tiangolo/fastapi") == (
            "tiangolo",
            "fastapi",
        )

    def test_non_github_url(self):
        assert parse_github_url("https://gitlab.com/user/repo") is None

    def test_incomplete_github_url(self):
        assert parse_github_url("https://github.com/tiangolo") is None

    def test_plain_text(self):
        assert parse_github_url("not a url at all") is None


class TestFetchGitHubRepoHappyPath:
    def test_returns_fetched_content(self, httpx_mock):
        _mock_github_success(httpx_mock)

        result = fetch_github_repo(REPO_URL)

        assert "tiangolo/fastapi" in result.title
        assert "FastAPI framework" in result.title
        assert result.url == REPO_URL

    def test_text_contains_metadata(self, httpx_mock):
        _mock_github_success(httpx_mock)

        result = fetch_github_repo(REPO_URL)

        assert "Stars: 78,500" in result.text
        assert "Language: Python" in result.text
        assert "Topics: python, api, web, async, fastapi" in result.text

    def test_text_contains_readme(self, httpx_mock):
        _mock_github_success(httpx_mock)

        result = fetch_github_repo(REPO_URL)

        assert "--- README ---" in result.text
        assert "FastAPI is a modern web framework" in result.text

    def test_sends_user_agent(self, httpx_mock):
        _mock_github_success(httpx_mock)

        fetch_github_repo(REPO_URL)

        requests = httpx_mock.get_requests()
        for req in requests:
            assert req.headers["user-agent"] == USER_AGENT


class TestFetchGitHubRepoAuth:
    def test_sends_github_token_when_set(self, httpx_mock, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test123")
        _mock_github_success(httpx_mock)

        fetch_github_repo(REPO_URL)

        request = httpx_mock.get_requests()[0]
        assert request.headers["authorization"] == "Bearer ghp_test123"

    def test_no_auth_header_without_token(self, httpx_mock, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        _mock_github_success(httpx_mock)

        fetch_github_repo(REPO_URL)

        request = httpx_mock.get_requests()[0]
        assert "authorization" not in request.headers


class TestFetchGitHubRepoReadmeFallback:
    def test_falls_back_to_raw_url(self, httpx_mock):
        metadata = _load_fixture("github_repo.json")

        httpx_mock.add_response(
            url=f"{API_BASE}/repos/tiangolo/fastapi",
            json=metadata,
        )
        # API readme returns 404
        httpx_mock.add_response(
            url=f"{API_BASE}/repos/tiangolo/fastapi/readme",
            status_code=404,
        )
        # Raw fallback succeeds
        httpx_mock.add_response(
            url=f"{RAW_BASE}/tiangolo/fastapi/HEAD/README.md",
            text=SAMPLE_README,
        )

        result = fetch_github_repo(REPO_URL)

        assert "FastAPI is a modern web framework" in result.text

    def test_empty_readme_when_both_fail(self, httpx_mock):
        metadata = _load_fixture("github_repo.json")

        httpx_mock.add_response(
            url=f"{API_BASE}/repos/tiangolo/fastapi",
            json=metadata,
        )
        httpx_mock.add_response(
            url=f"{API_BASE}/repos/tiangolo/fastapi/readme",
            status_code=404,
        )
        httpx_mock.add_response(
            url=f"{RAW_BASE}/tiangolo/fastapi/HEAD/README.md",
            status_code=404,
        )

        result = fetch_github_repo(REPO_URL)

        assert "(no README available)" in result.text


class TestFetchGitHubRepoErrors:
    def test_invalid_url_raises_fetch_error(self):
        with pytest.raises(FetchError, match="Not a valid GitHub"):
            fetch_github_repo("https://gitlab.com/user/repo")

    def test_repo_not_found_raises_fetch_error(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{API_BASE}/repos/tiangolo/fastapi",
            status_code=404,
        )

        with pytest.raises(FetchError, match="not found"):
            fetch_github_repo(REPO_URL)

    def test_api_error_raises_fetch_error(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{API_BASE}/repos/tiangolo/fastapi",
            status_code=403,
        )

        with pytest.raises(FetchError, match="HTTP 403"):
            fetch_github_repo(REPO_URL)

    def test_timeout_raises_fetch_timeout_error(self, httpx_mock):
        httpx_mock.add_exception(httpx.ReadTimeout("timed out"))

        with pytest.raises(FetchTimeoutError, match="timed out"):
            fetch_github_repo(REPO_URL)


class TestReadmeTruncation:
    def test_long_readme_is_truncated(self, httpx_mock):
        long_readme = "x" * 15_000
        _mock_github_success(httpx_mock, readme_text=long_readme)

        result = fetch_github_repo(REPO_URL)

        assert "[... README truncated]" in result.text
