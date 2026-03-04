"""OAuth2 and credential management."""

import typer

app = typer.Typer(help="Authentication & account management")


@app.command()
def add() -> None:
    """Add a new mail account (interactive wizard)."""
    typer.echo("TODO: interactive account setup wizard")


@app.command("list")
def list_accounts() -> None:
    """List all configured accounts."""
    typer.echo("TODO: list configured accounts")
