"""Tests for history module — SQLite store CRUD operations."""

from pathlib import Path

import pytest

from linkedin_post_generator.history.models import HistoryEntry
from linkedin_post_generator.history.store import HistoryStore


@pytest.fixture()
def store(tmp_path: Path) -> HistoryStore:
    """Create a HistoryStore with a temporary database."""
    return HistoryStore(db_path=tmp_path / "test_history.db")


def _save_sample(store: HistoryStore, **overrides) -> int:
    """Save a sample post and return its ID."""
    defaults = {
        "source_type": "url",
        "source_url": "https://example.com/article",
        "source_text": "Article about Python decorators",
        "template": "discovery",
        "language": "pl",
        "tone": "professional-casual",
        "post_text": "Odkryłem świetne narzędzie do dekoratorów...",
    }
    defaults.update(overrides)
    return store.save(**defaults)


class TestHistoryStoreSave:
    """Save posts to history."""

    def test_save_returns_id(self, store: HistoryStore) -> None:
        post_id = _save_sample(store)
        assert isinstance(post_id, int)
        assert post_id > 0

    def test_save_increments_id(self, store: HistoryStore) -> None:
        id1 = _save_sample(store)
        id2 = _save_sample(store)
        assert id2 > id1

    def test_save_with_empty_url(self, store: HistoryStore) -> None:
        post_id = _save_sample(store, source_url="", source_type="text")
        entry = store.get(post_id)
        assert entry is not None
        assert entry.source_url == ""


class TestHistoryStoreGet:
    """Get a single post by ID."""

    def test_get_existing(self, store: HistoryStore) -> None:
        post_id = _save_sample(store)
        entry = store.get(post_id)
        assert entry is not None
        assert isinstance(entry, HistoryEntry)
        assert entry.id == post_id
        assert entry.template == "discovery"
        assert entry.language == "pl"

    def test_get_nonexistent(self, store: HistoryStore) -> None:
        assert store.get(999) is None

    def test_get_has_timestamp(self, store: HistoryStore) -> None:
        post_id = _save_sample(store)
        entry = store.get(post_id)
        assert entry is not None
        assert entry.created_at is not None


class TestHistoryStoreList:
    """List recent posts."""

    def test_list_empty(self, store: HistoryStore) -> None:
        assert store.list_recent() == []

    def test_list_returns_entries(self, store: HistoryStore) -> None:
        _save_sample(store)
        _save_sample(store, template="opinion")
        entries = store.list_recent()
        assert len(entries) == 2

    def test_list_most_recent_first(self, store: HistoryStore) -> None:
        _save_sample(store, template="first")
        _save_sample(store, template="second")
        entries = store.list_recent()
        assert entries[0].template == "second"
        assert entries[1].template == "first"

    def test_list_respects_limit(self, store: HistoryStore) -> None:
        for _ in range(5):
            _save_sample(store)
        entries = store.list_recent(limit=3)
        assert len(entries) == 3

    def test_list_respects_offset(self, store: HistoryStore) -> None:
        for i in range(5):
            _save_sample(store, template=f"t{i}")
        entries = store.list_recent(limit=2, offset=2)
        assert len(entries) == 2


class TestHistoryStoreSearch:
    """Search posts by content."""

    def test_search_by_url(self, store: HistoryStore) -> None:
        _save_sample(store, source_url="https://github.com/cool/repo")
        _save_sample(store, source_url="https://example.com/other")
        results = store.search("github.com")
        assert len(results) == 1
        assert "github.com" in results[0].source_url

    def test_search_by_post_text(self, store: HistoryStore) -> None:
        _save_sample(store, post_text="Elixir is amazing for concurrency")
        _save_sample(store, post_text="Rust is fast")
        results = store.search("Elixir")
        assert len(results) == 1

    def test_search_no_results(self, store: HistoryStore) -> None:
        _save_sample(store)
        assert store.search("nonexistent_xyz") == []

    def test_search_case_insensitive(self, store: HistoryStore) -> None:
        _save_sample(store, post_text="Python decorators")
        results = store.search("python")
        assert len(results) == 1


class TestHistoryStoreDelete:
    """Delete posts from history."""

    def test_delete_existing(self, store: HistoryStore) -> None:
        post_id = _save_sample(store)
        assert store.delete(post_id) is True
        assert store.get(post_id) is None

    def test_delete_nonexistent(self, store: HistoryStore) -> None:
        assert store.delete(999) is False


class TestHistoryStoreFindByUrl:
    """Dedup check — find existing post by URL."""

    def test_finds_existing_url(self, store: HistoryStore) -> None:
        _save_sample(store, source_url="https://example.com/dup")
        result = store.find_by_url("https://example.com/dup")
        assert result is not None
        assert result.source_url == "https://example.com/dup"

    def test_returns_none_for_unknown_url(self, store: HistoryStore) -> None:
        assert store.find_by_url("https://unknown.com") is None

    def test_returns_none_for_empty_url(self, store: HistoryStore) -> None:
        assert store.find_by_url("") is None

    def test_returns_most_recent_match(self, store: HistoryStore) -> None:
        url = "https://example.com/shared"
        _save_sample(store, source_url=url, template="first")
        _save_sample(store, source_url=url, template="second")
        result = store.find_by_url(url)
        assert result is not None
        assert result.template == "second"


class TestAutoCreateTable:
    """Table auto-creation on first use."""

    def test_creates_db_file(self, tmp_path: Path) -> None:
        db_path = tmp_path / "new.db"
        HistoryStore(db_path=db_path)
        assert db_path.exists()
