"""Rich panel display for generated posts."""

from rich.console import Console
from rich.panel import Panel

console = Console()


def display_post(
    text: str,
    template_label: str,
    language: str,
    char_count: int | None = None,
    word_count: int | None = None,
) -> None:
    """Display a generated post in a Rich panel with metadata bar.

    Args:
        text: The generated post text.
        template_label: Human-readable template name (e.g. "Discovery").
        language: Language code (e.g. "PL", "EN").
        char_count: Character count (auto-calculated if None).
        word_count: Word count (auto-calculated if None).
    """
    if char_count is None:
        char_count = len(text)
    if word_count is None:
        word_count = len(text.split())

    console.print()
    console.print(
        Panel(
            text,
            title="📝 Draft",
            border_style="green",
            padding=(1, 2),
        )
    )

    meta = (
        f"  [dim]{template_label} | {language.upper()} | "
        f"{char_count} chars | {word_count} words[/]"
    )
    console.print(meta)
