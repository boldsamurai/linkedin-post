"""Config command — interactive config editor (re-runs init with current defaults)."""

from rich.console import Console
from rich.table import Table

from linkedin_post_generator.cli.init_cmd import init
from linkedin_post_generator.config.reader import load_config

console = Console()


def config() -> None:
    """Interactive config editor."""
    cfg = load_config()

    # Show current settings
    table = Table(title="Aktualne ustawienia", show_header=False, border_style="cyan")
    table.add_column("Pole", style="cyan")
    table.add_column("Wartość")
    table.add_row("Język", cfg.language.value)
    table.add_row("Ton", cfg.tone.value)
    table.add_row("Długość", cfg.length.value)
    table.add_row("Hashtagi", " ".join(cfg.hashtags) if cfg.hashtags else "(brak)")
    table.add_row("Backend AI", cfg.ai_backend.value)

    console.print()
    console.print(table)
    console.print("\n[dim]Uruchamiam wizard — nowe wartości zastąpią aktualne.[/]\n")

    init()
