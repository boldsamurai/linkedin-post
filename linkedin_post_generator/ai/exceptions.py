"""Custom exceptions for the AI backend module."""


class AIError(Exception):
    """Base exception for all AI-related errors."""


class AINotAvailableError(AIError):
    """Raised when no AI backend is available (CLI not found, no API key)."""


class AITimeoutError(AIError):
    """Raised when AI generation exceeds the timeout."""

    def __init__(self, timeout: int) -> None:
        super().__init__(f"AI generation timed out after {timeout}s")
        self.timeout = timeout


class AIResponseError(AIError):
    """Raised when the AI response is invalid or contains an error."""
