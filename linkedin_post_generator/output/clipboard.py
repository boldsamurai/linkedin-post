"""Clipboard copy — plain text only, with error handling."""

import pyperclip
from rich.console import Console
from rich.text import Text

console = Console()


def copy_to_clipboard(text: str) -> bool:
    """Copy plain text to system clipboard.

    Strips any Rich markup that might have leaked into the text,
    ensuring only plain text reaches the clipboard.

    Args:
        text: The text to copy.

    Returns:
        True if successful, False on failure.
    """
    # Strip any potential Rich markup to ensure clean plain text
    clean_text = Text.from_markup(text).plain

    try:
        pyperclip.copy(clean_text)
        console.print("[green]✅ Post skopiowany do schowka[/]")
        return True
    except pyperclip.PyperclipException:
        console.print(
            "[yellow]⚠️ Nie udało się skopiować do schowka "
            "(brak mechanizmu clipboard na tym systemie)[/]"
        )
        return False
