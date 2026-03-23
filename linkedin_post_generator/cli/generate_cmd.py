"""Generate command — interactive post generation flow."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from linkedin_post_generator.cli.init_cmd import init as run_init
from linkedin_post_generator.config.reader import config_exists
from linkedin_post_generator.fetcher import (
    FetchedContent,
    FetchError,
    create_note,
    detect_source_type,
    fetch_github_repo,
    fetch_url,
    prompt_for_note,
)
from linkedin_post_generator.fetcher.models import SourceType

console = Console()

_SOURCE_TYPE_LABELS: dict[SourceType, str] = {
    SourceType.GITHUB: "GitHub",
    SourceType.URL: "URL",
    SourceType.TEXT: "Notatka",
}

_SPINNER_MESSAGES: dict[SourceType, str] = {
    SourceType.GITHUB: "🔗 Pobieranie danych z GitHub...",
    SourceType.URL: "🔗 Pobieranie treści...",
}


def generate() -> None:
    """Interactive post generation flow."""
    if not config_exists():
        console.print("[cyan]Pierwsza konfiguracja — uruchamiam wizard...[/]\n")
        run_init()
        console.print()

    content = _source_input()
    if content is None:
        return

    typer.echo("Generate flow — next steps not implemented yet.")


def _source_input() -> FetchedContent | None:
    """Interactive source input step.

    Prompts user for URL or topic, detects source type,
    fetches content, and shows a preview.

    Returns:
        FetchedContent on success, None if user cancels.
    """
    while True:
        user_input = Prompt.ask("\n[cyan]O czym chcesz napisać?[/] (URL lub temat)")

        if not user_input.strip():
            console.print("[yellow]Podaj URL lub temat.[/]")
            continue

        source_type = detect_source_type(user_input)

        try:
            content = _fetch_source(user_input.strip(), source_type)
        except FetchError as exc:
            _show_error(str(exc))
            continue

        _show_source_preview(content, source_type)
        return content


def _fetch_source(user_input: str, source_type: SourceType) -> FetchedContent:
    """Fetch content based on detected source type.

    Args:
        user_input: Raw user input (URL or text).
        source_type: Detected source type.

    Returns:
        Fetched content.
    """
    if source_type == SourceType.GITHUB:
        with console.status(_SPINNER_MESSAGES[SourceType.GITHUB]):
            return fetch_github_repo(user_input)

    if source_type == SourceType.URL:
        with console.status(_SPINNER_MESSAGES[SourceType.URL]):
            return fetch_url(user_input)

    # Free text — if very short, offer multi-line input
    if len(user_input) < 20:
        console.print(f"\n📝 Temat: [bold]{user_input}[/]")
        return prompt_for_note()

    return create_note(user_input)


def _show_source_preview(content: FetchedContent, source_type: SourceType) -> None:
    """Show a preview of fetched source content."""
    label = _SOURCE_TYPE_LABELS.get(source_type, "Źródło")

    preview_text = content.text[:200]
    if len(content.text) > 200:
        preview_text += "..."

    body = f"[bold]{content.title}[/]\n\n[dim]{preview_text}[/]"
    if content.url:
        body += f"\n\n[underline blue]{content.url}[/]"

    console.print(Panel(body, title=f"📄 {label}", border_style="cyan"))


def _show_error(message: str) -> None:
    """Show a fetch error with retry instruction."""
    console.print(
        Panel(
            f"{message}\n\n[dim]Spróbuj ponownie z innym URL lub wpisz temat.[/]",
            title="❌ Error",
            border_style="red bold",
        )
    )
