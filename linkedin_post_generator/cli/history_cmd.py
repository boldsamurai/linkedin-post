"""History command — history management with subcommands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from linkedin_post_generator.history import HistoryEntry, get_store

history_app = typer.Typer(
    help="History management (list, show, search, delete).",
    no_args_is_help=True,
)

console = Console()

MAX_SOURCE_DISPLAY = 50


def _truncate(text: str, max_len: int = MAX_SOURCE_DISPLAY) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _source_display(entry: HistoryEntry) -> str:
    if entry.source_url:
        return _truncate(entry.source_url)
    return _truncate(entry.source_text.split("\n", maxsplit=1)[0])


def _build_table(entries: list[HistoryEntry], title: str = "Historia") -> Table:
    table = Table(title=title, border_style="cyan")
    table.add_column("ID", style="bold", width=5)
    table.add_column("Data", width=12)
    table.add_column("Źródło", max_width=50)
    table.add_column("Szablon", width=18)
    table.add_column("Język", width=6)

    for e in entries:
        table.add_row(
            str(e.id),
            e.created_at.strftime("%Y-%m-%d"),
            _source_display(e),
            e.template,
            e.language.upper(),
        )
    return table


def _show_entry_panel(entry: HistoryEntry) -> None:
    console.print()
    console.print(
        Panel(entry.post_text, title="📝 Post", border_style="green", padding=(1, 2))
    )
    meta = (
        f"  [dim]ID: {entry.id} | {entry.template} | "
        f"{entry.language.upper()} | {entry.tone} | "
        f"{entry.created_at.strftime('%Y-%m-%d %H:%M')}[/]"
    )
    console.print(meta)
    if entry.source_url:
        console.print(f"  [dim]Źródło: [underline blue]{entry.source_url}[/][/]")


@history_app.command(name="list")
def history_list() -> None:
    """List recent posts."""
    store = get_store()
    entries = store.list_recent(limit=20)

    if not entries:
        console.print("[dim]Brak postów w historii.[/]")
        return

    console.print(_build_table(entries))


@history_app.command()
def show(post_id: int = typer.Argument(help="Post ID to display")) -> None:
    """Show a specific post by ID."""
    store = get_store()
    entry = store.get(post_id)

    if entry is None:
        console.print(f"[red]Post #{post_id} nie znaleziony.[/]")
        raise typer.Exit(1)

    _show_entry_panel(entry)


@history_app.command()
def search(query: str = typer.Argument(help="Search query")) -> None:
    """Search posts by content."""
    store = get_store()
    entries = store.search(query)

    if not entries:
        console.print(f"[dim]Brak wyników dla '{query}'.[/]")
        return

    console.print(_build_table(entries, title=f"Wyniki: '{query}'"))


@history_app.command()
def delete(post_id: int = typer.Argument(help="Post ID to delete")) -> None:
    """Delete a post from history."""
    store = get_store()
    entry = store.get(post_id)

    if entry is None:
        console.print(f"[red]Post #{post_id} nie znaleziony.[/]")
        raise typer.Exit(1)

    preview = _truncate(entry.post_text, 100)
    console.print(f"\n[dim]{preview}[/]\n")

    if not Confirm.ask(f"Usunąć post #{post_id}?", default=False):
        console.print("[dim]Anulowano.[/]")
        return

    store.delete(post_id)
    console.print(f"[green]✅ Post #{post_id} usunięty.[/]")
