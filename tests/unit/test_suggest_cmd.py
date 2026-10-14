"""Tests for the suggest command (CliRunner, feeds and AI flow mocked)."""

import sqlite3
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from linkedin_post_generator.cli import app
from linkedin_post_generator.cli.suggest_cmd import _entry_label
from linkedin_post_generator.config.model import AppConfig
from linkedin_post_generator.fetcher import FeedEntry, FeedFetchResult, FetchError
from linkedin_post_generator.history import HistoryStore

runner = CliRunner()

MODULE = "linkedin_post_generator.cli.suggest_cmd"
FEED_URL = "https://python.example.com/rss.xml"
BROKEN_FEED = "https://broken.example.net/feed"
NEW_ENTRY = FeedEntry(
    title="Newest post about uv",
    url="https://python.example.com/uv",
    published=datetime(2026, 10, 12, 8, 0, tzinfo=UTC),
    feed_title="Python Weekly Notes",
)
USED_ENTRY = FeedEntry(
    title="Older post about asyncio",
    url="https://python.example.com/asyncio",
    published=None,
    feed_title="Python Weekly Notes",
)


@pytest.fixture
def history_store(tmp_path, monkeypatch) -> HistoryStore:
    store = HistoryStore(db_path=tmp_path / "history.db")
    monkeypatch.setattr(f"{MODULE}.get_store", lambda: store)
    return store


@pytest.fixture
def feeds_config(monkeypatch) -> None:
    monkeypatch.setattr(
        f"{MODULE}.load_config", lambda: AppConfig(feeds=[FEED_URL, BROKEN_FEED])
    )


def _mock_menu(mock_inq: MagicMock, value: str) -> None:
    mock_inq.select.return_value.execute.return_value = value


def test_suggest_without_feeds_shows_config_hint(monkeypatch):
    monkeypatch.setattr(f"{MODULE}.load_config", lambda: AppConfig())

    with patch(f"{MODULE}.fetch_feed_entries") as mock_fetch:
        result = runner.invoke(app, ["suggest"])

    assert result.exit_code == 0, result.output
    assert "Brak skonfigurowanych feedów" in result.output
    assert "feeds = [" in result.output
    mock_fetch.assert_not_called()


@pytest.mark.usefixtures("feeds_config")
@patch(f"{MODULE}.run_generate")
@patch(f"{MODULE}.inquirer")
@patch(f"{MODULE}.fetch_feed_entries")
def test_suggest_selection_passes_url_to_generate(
    mock_fetch, mock_inq, mock_generate, history_store
):
    history_store.save(
        source_type="url",
        source_url=USED_ENTRY.url,
        source_text="text",
        template="discovery",
        language="pl",
        tone="technical",
        post_text="post",
    )
    mock_fetch.return_value = FeedFetchResult(
        entries=[NEW_ENTRY, USED_ENTRY], failed_feeds=[BROKEN_FEED]
    )
    _mock_menu(mock_inq, NEW_ENTRY.url)

    result = runner.invoke(app, ["suggest"])

    assert result.exit_code == 0, result.output
    mock_generate.assert_called_once_with(NEW_ENTRY.url)
    assert f"⚠️ Nie udało się pobrać feedu: {BROKEN_FEED}" in result.output
    names = [c["name"] for c in mock_inq.select.call_args.kwargs["choices"]]
    assert names[0] == "Newest post about uv — Python Weekly Notes · 2026-10-12"
    assert names[1].endswith("✓ użyty"), f"Used entry not marked: {names[1]}"
    assert names[-1] == "Anuluj"


@pytest.mark.usefixtures("feeds_config", "history_store")
@patch(f"{MODULE}.run_generate")
@patch(f"{MODULE}.inquirer")
@patch(f"{MODULE}.fetch_feed_entries")
def test_suggest_cancel_exits_cleanly(mock_fetch, mock_inq, mock_generate):
    mock_fetch.return_value = FeedFetchResult(entries=[NEW_ENTRY], failed_feeds=[])
    _mock_menu(mock_inq, "")

    result = runner.invoke(app, ["suggest"])

    assert result.exit_code == 0, result.output
    mock_generate.assert_not_called()


@pytest.mark.usefixtures("feeds_config")
@patch(f"{MODULE}.run_generate")
@patch(f"{MODULE}.fetch_feed_entries")
def test_suggest_all_feeds_failed_shows_error_panel(mock_fetch, mock_generate):
    mock_fetch.side_effect = FetchError(BROKEN_FEED, "All feeds failed")

    result = runner.invoke(app, ["suggest"])

    assert result.exit_code == 0, result.output
    assert "❌ Error" in result.output
    assert "Traceback" not in result.output
    mock_generate.assert_not_called()


@pytest.mark.usefixtures("feeds_config")
@patch(f"{MODULE}.inquirer")
@patch(f"{MODULE}.fetch_feed_entries")
def test_suggest_no_entries_skips_menu(mock_fetch, mock_inq):
    mock_fetch.return_value = FeedFetchResult(entries=[], failed_feeds=[BROKEN_FEED])

    result = runner.invoke(app, ["suggest"])

    assert result.exit_code == 0, result.output
    assert "Feedy nie zawierają żadnych wpisów" in result.output
    mock_inq.select.assert_not_called()


@pytest.mark.usefixtures("feeds_config")
@patch(f"{MODULE}.run_generate")
@patch(f"{MODULE}.inquirer")
@patch(f"{MODULE}.fetch_feed_entries")
def test_suggest_broken_history_still_shows_menu(
    mock_fetch, mock_inq, mock_generate, monkeypatch
):
    def _broken_store():
        raise sqlite3.OperationalError("unable to open database file")

    monkeypatch.setattr(f"{MODULE}.get_store", _broken_store)
    mock_fetch.return_value = FeedFetchResult(entries=[NEW_ENTRY], failed_feeds=[])
    _mock_menu(mock_inq, NEW_ENTRY.url)

    result = runner.invoke(app, ["suggest"])

    assert result.exit_code == 0, result.output
    names = [c["name"] for c in mock_inq.select.call_args.kwargs["choices"]]
    assert not any("✓ użyty" in name for name in names)
    mock_generate.assert_called_once_with(NEW_ENTRY.url)


def test_entry_label_collapses_multiline_title():
    entry = FeedEntry(
        title="Line one\n  line\x1b[31m two",
        url="https://python.example.com/multi",
        published=None,
        feed_title="Feed\nName",
    )

    assert _entry_label(entry, is_used=False) == (
        "Line one line [31m two — Feed Name · bez daty"
    )
