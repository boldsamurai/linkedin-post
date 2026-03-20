"""Generate command — interactive post generation flow."""

import typer
from rich.console import Console

from linkedin_post_generator.cli.init_cmd import init as run_init
from linkedin_post_generator.config.reader import config_exists

console = Console()


def generate() -> None:
    """Interactive post generation flow."""
    if not config_exists():
        console.print(
            "[cyan]Pierwsza konfiguracja — uruchamiam wizard...[/]\n"
        )
        run_init()
        console.print()

    typer.echo("Generate flow — not implemented yet.")
