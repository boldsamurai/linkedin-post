"""History command — history management with subcommands."""

import typer

history_app = typer.Typer(
    help="History management (list, show, search, delete).",
    no_args_is_help=True,
)


@history_app.command(name="list")
def history_list() -> None:
    """List recent posts."""
    typer.echo("History list — not implemented yet.")


@history_app.command()
def show(post_id: int = typer.Argument(help="Post ID to display")) -> None:
    """Show a specific post by ID."""
    typer.echo(f"History show #{post_id} — not implemented yet.")


@history_app.command()
def search(
    query: str = typer.Argument(help="Search query"),
) -> None:
    """Search posts by content."""
    typer.echo(f"History search '{query}' — not implemented yet.")


@history_app.command()
def delete(
    post_id: int = typer.Argument(help="Post ID to delete"),
) -> None:
    """Delete a post from history."""
    typer.echo(f"History delete #{post_id} — not implemented yet.")
