"""Data models for history entries."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HistoryEntry:
    """A saved post from generation history."""

    id: int
    created_at: datetime
    source_type: str
    source_url: str
    source_text: str
    template: str
    language: str
    tone: str
    post_text: str
