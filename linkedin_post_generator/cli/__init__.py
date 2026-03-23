"""CLI package — Typer app with all commands."""

import typer

from linkedin_post_generator import __version__
from linkedin_post_generator.cli.config_cmd import config
from linkedin_post_generator.cli.generate_cmd import generate_cmd
from linkedin_post_generator.cli.history_cmd import history_app
from linkedin_post_generator.cli.init_cmd import init

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
    """LinkedIn Post Generator — AI-assisted, human-refined posts."""


app.command()(init)
app.command(name="generate")(generate_cmd)
app.command()(config)
app.add_typer(history_app, name="history")
