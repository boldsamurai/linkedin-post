"""Custom exceptions for the templates module."""

from pathlib import Path


class TemplateError(Exception):
    """Raised when a custom template file cannot be loaded."""

    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"Invalid template file {path}: {reason}")
