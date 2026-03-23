"""File save — write post to timestamped .txt file."""

from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console

console = Console()


def save_to_file(
    text: str,
    source_title: str,
    template_name: str,
    language: str,
    directory: Path | None = None,
) -> Path:
    """Save post text to a timestamped .txt file with metadata header.

    Args:
        text: The generated post text.
        source_title: Title/summary of the source material.
        template_name: Template used for generation.
        language: Language code (e.g. "pl", "en").
        directory: Target directory (defaults to cwd).

    Returns:
        Path to the saved file.
    """
    if directory is None:
        directory = Path.cwd()

    now = datetime.now(tz=timezone.utc)
    timestamp = now.strftime("%Y-%m-%d-%H%M%S")
    filename = f"linkedin-post-{timestamp}.txt"
    filepath = directory / filename

    header = (
        f"# LinkedIn Post Draft\n"
        f"# Date: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"# Source: {source_title}\n"
        f"# Template: {template_name}\n"
        f"# Language: {language}\n"
        f"#\n\n"
    )

    filepath.write_text(header + text, encoding="utf-8")

    console.print(f"[green]✅ Post zapisany: {filepath}[/]")
    return filepath
