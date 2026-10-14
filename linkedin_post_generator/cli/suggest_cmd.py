"""Suggest command — pick a recent feed entry and generate a post from it."""

import sqlite3

from InquirerPy import inquirer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel

from linkedin_post_generator.cli.generate_cmd import run_generate
from linkedin_post_generator.config.paths import global_config_path
from linkedin_post_generator.config.reader import load_config
from linkedin_post_generator.fetcher import FeedEntry, FetchError, fetch_feed_entries
from linkedin_post_generator.history import get_store

console = Console()

_CANCEL = ""
_FEEDS_EXAMPLE = 'feeds = ["https://example.com/rss.xml"]'


def suggest() -> None:
    """Pick a recent entry from your RSS/Atom feeds and draft a post about it."""
    cfg = load_config()
    if not cfg.feeds:
        _show_no_feeds_hint()
        return

    try:
        with console.status("🔗 Pobieranie feedów..."):
            result = fetch_feed_entries(cfg.feeds)
    except FetchError as exc:
        _show_error(str(exc))
        return

    for url in result.failed_feeds:
        console.print(f"[yellow]⚠️ Nie udało się pobrać feedu: {escape(url)}[/]")

    if not result.entries:
        console.print("[yellow]⚠️ Feedy nie zawierają żadnych wpisów.[/]")
        return

    url = _select_entry(result.entries)
    if url == _CANCEL:
        return

    run_generate(url)


def _select_entry(entries: list[FeedEntry]) -> str:
    """Show the entry menu; returns the picked URL or ``_CANCEL``."""
    used_urls = _find_used_urls(entries)
    choices = [
        {"name": _entry_label(entry, entry.url in used_urls), "value": entry.url}
        for entry in entries
    ]
    choices.append({"name": "Anuluj", "value": _CANCEL})

    return inquirer.select(message="Wybierz wpis:", choices=choices).execute()


def _entry_label(entry: FeedEntry, is_used: bool) -> str:
    """Menu label: "title — feed · date", marked when already used."""
    date = entry.published.strftime("%Y-%m-%d") if entry.published else "bez daty"
    label = f"{_one_line(entry.title)} — {_one_line(entry.feed_title)} · {date}"
    return f"{label}  ✓ użyty" if is_used else label


def _one_line(text: str) -> str:
    """Collapse whitespace and drop control characters from untrusted feed text.

    The menu needs one line per entry; a newline in a hostile title could
    otherwise fake an extra menu row.
    """
    printable = "".join(ch if ch.isprintable() else " " for ch in text)
    return " ".join(printable.split())


def _find_used_urls(entries: list[FeedEntry]) -> set[str]:
    """URLs that already have a post in history; empty when history is unavailable."""
    try:
        store = get_store()
        return {entry.url for entry in entries if store.find_by_url(entry.url)}
    except sqlite3.Error:
        # History only decorates the menu; a broken DB must not block suggestions.
        return set()


def _show_no_feeds_hint() -> None:
    """Explain how to configure feeds."""
    console.print(
        "[yellow]⚠️ Brak skonfigurowanych feedów.[/]\n"
        f"Dodaj do [cyan]{escape(str(global_config_path()))}[/]:\n\n"
        f"  {escape(_FEEDS_EXAMPLE)}"
    )


def _show_error(message: str) -> None:
    """Show a feed fetch failure with a fix instruction."""
    console.print(
        Panel(
            f"{escape(message)}\n\n[dim]Sprawdź adresy w `feeds` w config.toml "
            "i połączenie z internetem.[/]",
            title="❌ Error",
            border_style="red bold",
        )
    )
