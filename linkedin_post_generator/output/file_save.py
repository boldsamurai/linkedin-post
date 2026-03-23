"""File save — write post to timestamped .txt file."""

from datetime import UTC, datetime
from pathlib import Path

from rich.console import Console

console = Console()

POSTS_DIR = "posts"


def save_to_file(
    text: str,
    source_title: str,
    template_name: str,
    language: str,
    directory: Path | None = None,
) -> Path:
    """Save post text to a timestamped .txt file in the posts/ subdirectory.

    Args:
        text: The generated post text (plain text only).
        source_title: Unused, kept for API compatibility.
        template_name: Unused, kept for API compatibility.
        language: Unused, kept for API compatibility.
        directory: Base directory (defaults to cwd). Posts go into posts/ subdir.

    Returns:
        Path to the saved file.
    """
    if directory is None:
        directory = Path.cwd()

    posts_dir = directory / POSTS_DIR
    posts_dir.mkdir(exist_ok=True)

    now = datetime.now(tz=UTC)
    timestamp = now.strftime("%Y-%m-%d-%H%M%S")
    filename = f"linkedin-post-{timestamp}.txt"
    filepath = posts_dir / filename

    filepath.write_text(text, encoding="utf-8")

    console.print(f"[green]✅ Post zapisany: {filepath}[/]")
    return filepath
