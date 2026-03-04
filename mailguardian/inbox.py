"""IMAP inbox module."""

from typing import Optional

import typer

app = typer.Typer(help="Inbox operations")


@app.command("list")
def list_mails(
    limit: int = typer.Option(10, help="Number of mails to show"),
    account: Optional[str] = typer.Option(None, help="Account name to use"),
) -> None:
    """List recent emails."""
    typer.echo(f"TODO: list {limit} mails" + (f" from {account}" if account else ""))


@app.command()
def show(mail_id: str = typer.Argument(..., help="Mail ID to show")) -> None:
    """Show a specific email."""
    typer.echo(f"TODO: show mail {mail_id}")


@app.command()
def scan(
    ai: bool = typer.Option(False, "--ai", help="Use AI classification"),
    account: Optional[str] = typer.Option(None, help="Account name to use"),
) -> None:
    """Scan and classify emails."""
    typer.echo("TODO: scan mails" + (" with AI" if ai else ""))
