"""Free-text note input — wraps user text into FetchedContent."""

import pyperclip
from rich.console import Console
from rich.prompt import Confirm

from linkedin_post_generator.fetcher.models import FetchedContent

MAX_TITLE_LENGTH = 80


def create_note(text: str, title: str | None = None) -> FetchedContent:
    """Create FetchedContent from free-text input.

    Args:
        text: The note text.
        title: Optional title. If not provided, auto-extracted from first line.

    Returns:
        FetchedContent with the note text.

    Raises:
        ValueError: If text is empty or whitespace-only.
    """
    text = text.strip()
    if not text:
        raise ValueError("Note text cannot be empty")

    if title is None:
        title = _extract_title(text)

    return FetchedContent(title=title, text=text, url="")


def prompt_for_note() -> FetchedContent:
    """Interactive prompt for multi-line note input with clipboard support.

    Checks clipboard first and offers to use its content.
    Falls back to manual multi-line input (terminated by empty line or Ctrl+D).

    Returns:
        FetchedContent with the entered or pasted text.

    Raises:
        ValueError: If no text was entered.
    """
    console = Console()

    clipboard_text = _get_clipboard_text()
    if clipboard_text:
        char_count = len(clipboard_text)
        console.print(f"\n📋 Znaleziono tekst w schowku ({char_count} znaków):")
        preview = clipboard_text[:200] + ("..." if char_count > 200 else "")
        console.print(f"[dim]{preview}[/dim]\n")
        if Confirm.ask("Użyć tekstu ze schowka?", default=True):
            return create_note(clipboard_text)

    console.print("\n✏️  Wpisz tekst (zakończ pustą linią):\n")
    lines: list[str] = []
    while True:
        try:
            line = console.input()
        except EOFError:
            break
        if not line and lines:
            break
        if line:
            lines.append(line)

    text = "\n".join(lines)
    return create_note(text)


def _extract_title(text: str) -> str:
    """Extract a title from the first line of text."""
    first_line = text.split("\n", maxsplit=1)[0].strip()
    if len(first_line) <= MAX_TITLE_LENGTH:
        return first_line
    return first_line[: MAX_TITLE_LENGTH - 3] + "..."


def _get_clipboard_text() -> str:
    """Safely get text from clipboard. Returns empty string on failure."""
    try:
        text = pyperclip.paste()
        return text.strip() if text else ""
    except pyperclip.PyperclipException:
        return ""
