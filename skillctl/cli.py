"""Typer entry point for skillctl."""

import typer

app = typer.Typer(
    name="skillctl",
    help="Inventory, share, and merge AI agent skills.",
    no_args_is_help=True,
)


@app.command()
def list():
    """List all skills found on this machine."""
    typer.echo("skillctl list — not yet implemented (Iteration 1)")


@app.command()
def show(name: str = typer.Argument(..., help="Skill name to display")):
    """Print the resolved skill frontmatter and body."""
    typer.echo(f"skillctl show {name!r} — not yet implemented (Iteration 1)")


if __name__ == "__main__":
    app()
