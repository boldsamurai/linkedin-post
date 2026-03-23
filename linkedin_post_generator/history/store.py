"""SQLite-backed history store for generated posts."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from linkedin_post_generator.config.paths import history_db_path
from linkedin_post_generator.history.models import HistoryEntry

_CREATE_TABLE = """\
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_url TEXT,
    source_text TEXT NOT NULL,
    template TEXT NOT NULL,
    language TEXT NOT NULL,
    tone TEXT NOT NULL,
    post_text TEXT NOT NULL
)
"""


class HistoryStore:
    """SQLite store for post generation history."""

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or history_db_path()
        self._ensure_table()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self) -> None:
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE)

    def save(
        self,
        source_type: str,
        source_url: str,
        source_text: str,
        template: str,
        language: str,
        tone: str,
        post_text: str,
    ) -> int:
        """Save a generated post to history.

        Returns:
            The ID of the new history entry.
        """
        now = datetime.now(tz=UTC).isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO posts "
                "(created_at, source_type, source_url, source_text, "
                "template, language, tone, post_text) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    now,
                    source_type,
                    source_url or None,
                    source_text,
                    template,
                    language,
                    tone,
                    post_text,
                ),
            )
            return cursor.lastrowid  # type: ignore[return-value]

    def get(self, post_id: int) -> HistoryEntry | None:
        """Get a single post by ID.

        Returns:
            HistoryEntry or None if not found.
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM posts WHERE id = ?", (post_id,)
            ).fetchone()
        if row is None:
            return None
        return _row_to_entry(row)

    def list_recent(self, limit: int = 20, offset: int = 0) -> list[HistoryEntry]:
        """List recent posts, most recent first.

        Args:
            limit: Maximum number of entries.
            offset: Skip this many entries (for pagination).

        Returns:
            List of HistoryEntry.
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM posts ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [_row_to_entry(r) for r in rows]

    def search(self, query: str) -> list[HistoryEntry]:
        """Search posts by content (source URL, source text, post text).

        Args:
            query: Search term (SQL LIKE pattern applied).

        Returns:
            Matching entries, most recent first.
        """
        pattern = f"%{query}%"
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM posts WHERE "
                "source_url LIKE ? OR source_text LIKE ? OR post_text LIKE ? "
                "ORDER BY id DESC",
                (pattern, pattern, pattern),
            ).fetchall()
        return [_row_to_entry(r) for r in rows]

    def delete(self, post_id: int) -> bool:
        """Delete a post by ID.

        Returns:
            True if deleted, False if not found.
        """
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            return cursor.rowcount > 0

    def find_by_url(self, url: str) -> HistoryEntry | None:
        """Find the most recent post with the given source URL.

        Args:
            url: Source URL to check for duplicates.

        Returns:
            Most recent matching HistoryEntry, or None.
        """
        if not url:
            return None
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM posts WHERE source_url = ? ORDER BY id DESC LIMIT 1",
                (url,),
            ).fetchone()
        if row is None:
            return None
        return _row_to_entry(row)


def _row_to_entry(row: sqlite3.Row) -> HistoryEntry:
    """Convert a database row to a HistoryEntry."""
    return HistoryEntry(
        id=row["id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        source_type=row["source_type"],
        source_url=row["source_url"] or "",
        source_text=row["source_text"],
        template=row["template"],
        language=row["language"],
        tone=row["tone"],
        post_text=row["post_text"],
    )


def get_store() -> HistoryStore:
    """Get a HistoryStore with the default DB path."""
    return HistoryStore()
