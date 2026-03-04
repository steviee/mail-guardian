"""IMAP inbox CLI commands."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mailguardian.accounts import get_account, get_password
from mailguardian.imap_client import connect, fetch_mail_detail, fetch_mail_list

app = typer.Typer(help="Inbox operations")
console = Console()


def _get_client(account_name: Optional[str] = None):
    """Helper: resolve account and connect."""
    acc = get_account(account_name)
    if not acc:
        console.print("[red]No account configured. Use 'mg auth add' first.[/red]")
        raise typer.Exit(1)

    pw = get_password(acc["name"])
    if not pw:
        console.print(f"[red]No password for '{acc['name']}'. Re-add the account.[/red]")
        raise typer.Exit(1)

    try:
        client = connect(acc["imap_host"], acc["imap_port"], acc["username"], pw)
    except Exception as e:
        console.print(f"[red]Connection failed: {e}[/red]")
        raise typer.Exit(1)

    return client, acc


@app.command("list")
def list_mails(
    limit: int = typer.Option(10, help="Number of mails to show"),
    account: Optional[str] = typer.Option(None, help="Account name to use"),
    folder: str = typer.Option("INBOX", help="Mail folder to list"),
) -> None:
    """List recent emails."""
    client, acc = _get_client(account)

    try:
        mails = fetch_mail_list(client, folder=folder, limit=limit)
    finally:
        client.logout()

    if not mails:
        console.print("[yellow]No mails found.[/yellow]")
        return

    table = Table(title=f"Inbox — {acc['name']} ({len(mails)} mails)")
    table.add_column("UID", style="dim", justify="right")
    table.add_column("Date", style="cyan", width=16)
    table.add_column("From", width=30)
    table.add_column("Subject")
    table.add_column("", width=2)  # unread marker

    for m in mails:
        date_str = m.date.strftime("%Y-%m-%d %H:%M") if m.date else ""
        marker = "[bold red]*[/bold red]" if m.is_unread else ""
        table.add_row(str(m.uid), date_str, m.sender[:30], m.subject, marker)

    console.print(table)


@app.command()
def show(
    mail_uid: int = typer.Argument(..., help="Mail UID to show"),
    account: Optional[str] = typer.Option(None, help="Account name to use"),
    folder: str = typer.Option("INBOX", help="Mail folder"),
) -> None:
    """Show a specific email by UID."""
    client, acc = _get_client(account)

    try:
        detail = fetch_mail_detail(client, mail_uid, folder=folder)
    finally:
        client.logout()

    if not detail:
        console.print(f"[red]Mail UID {mail_uid} not found.[/red]")
        raise typer.Exit(1)

    date_str = detail.date.strftime("%Y-%m-%d %H:%M:%S") if detail.date else "unknown"
    header = (
        f"[bold]{detail.subject}[/bold]\n"
        f"From: {detail.sender}\n"
        f"To:   {detail.to}\n"
        f"Date: {date_str}"
    )
    console.print(Panel(header, title=f"Mail #{detail.uid}", border_style="blue"))
    console.print()

    body = detail.body_text or "(no plain-text body)"
    console.print(body)


@app.command()
def scan(
    limit: int = typer.Option(10, help="Number of mails to scan"),
    ai: bool = typer.Option(False, "--ai", help="Use AI classification (requires Issue #3)"),
    account: Optional[str] = typer.Option(None, help="Account name to use"),
    folder: str = typer.Option("INBOX", help="Mail folder"),
) -> None:
    """Scan and classify emails."""
    if ai:
        console.print("[yellow]AI classification not yet implemented (see Issue #3).[/yellow]")
        return

    client, acc = _get_client(account)

    try:
        mails = fetch_mail_list(client, folder=folder, limit=limit)
    finally:
        client.logout()

    if not mails:
        console.print("[yellow]No mails found.[/yellow]")
        return

    table = Table(title=f"Scan — {acc['name']}")
    table.add_column("UID", style="dim", justify="right")
    table.add_column("Status")
    table.add_column("From", width=30)
    table.add_column("Subject")

    for m in mails:
        status = "[red]UNREAD[/red]" if m.is_unread else "[green]read[/green]"
        table.add_row(str(m.uid), status, m.sender[:30], m.subject)

    console.print(table)
