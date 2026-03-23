"""Clipboard copy — plain text only, with error handling."""

import pyperclip
from rich.console import Console

console = Console()


def copy_to_clipboard(text: str) -> bool:
    """Copy plain text to system clipboard.

    Args:
        text: The text to copy (plain, no formatting).

    Returns:
        True if successful, False on failure.
    """
    try:
        pyperclip.copy(text)
        console.print("[green]✅ Post skopiowany do schowka[/]")
        return True
    except pyperclip.PyperclipException:
        console.print(
            "[yellow]⚠️ Nie udało się skopiować do schowka "
            "(brak mechanizmu clipboard na tym systemie)[/]"
        )
        return False
