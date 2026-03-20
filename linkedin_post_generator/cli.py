"""CLI entry point — Typer app with all commands."""

import typer

from linkedin_post_generator import __version__

app = typer.Typer(
    name="linkedin-post",
    help="Interactive CLI for AI-assisted LinkedIn post drafts.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"linkedin-post {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """LinkedIn Post Generator — AI-assisted, human-refined LinkedIn posts."""


@app.command()
def init() -> None:
    """First-run configuration wizard."""
    typer.echo("Init wizard — not implemented yet.")


@app.command()
def generate() -> None:
    """Interactive post generation flow."""
    typer.echo("Generate — not implemented yet.")


@app.command()
def config() -> None:
    """Interactive config editor."""
    typer.echo("Config editor — not implemented yet.")


@app.command()
def history() -> None:
    """History management (list, show, search, delete)."""
    typer.echo("History — not implemented yet.")
