"""Custom exceptions for the fetcher module."""


class FetchError(Exception):
    """Base exception for all fetch-related errors."""

    def __init__(self, url: str, message: str) -> None:
        self.url = url
        super().__init__(f"{message}: {url}")


class FetchTimeoutError(FetchError):
    """Raised when a fetch request times out."""

    def __init__(self, url: str) -> None:
        super().__init__(url, "Request timed out")


class FetchContentError(FetchError):
    """Raised when fetched content cannot be processed (e.g. non-HTML, empty body)."""

    def __init__(self, url: str, reason: str) -> None:
        super().__init__(url, f"Content error ({reason})")
