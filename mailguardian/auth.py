"""OAuth2 and credential management CLI commands."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from mailguardian.accounts import (
    PROVIDER_DEFAULTS,
    add_account,
    get_password,
    list_accounts as _list_accounts,
    remove_account,
)

app = typer.Typer(help="Authentication & account management")
console = Console()


@app.command()
def add(
    name: Optional[str] = typer.Option(None, help="Account name"),
    provider: Optional[str] = typer.Option(None, help="Provider (gmail/outlook/yahoo/generic)"),
    username: Optional[str] = typer.Option(None, help="Email / username"),
    password: Optional[str] = typer.Option(None, help="Password or app-password", hide_input=True),
    imap_host: Optional[str] = typer.Option(None, help="IMAP host (auto-filled for known providers)"),
    imap_port: int = typer.Option(993, help="IMAP port"),
    default: bool = typer.Option(False, "--default", help="Set as default account"),
) -> None:
    """Add a new mail account (interactive if options omitted)."""
    # Interactive prompts for missing values
    if not name:
        name = typer.prompt("Account name (e.g. gmail-private)")
    if not provider:
        provider = typer.prompt(
            "Provider",
            default="gmail",
            type=typer.Choice(["gmail", "outlook", "yahoo", "generic"]),
        )
    if not username:
        username = typer.prompt("Email / username")
    if not password:
        password = typer.prompt("Password (app-password recommended)", hide_input=True)

    # For generic provider, ask for host if not given
    if provider == "generic" and not imap_host:
        imap_host = typer.prompt("IMAP host")
        imap_port = typer.prompt("IMAP port", default=993, type=int)

    try:
        account = add_account(
            name=name,
            provider=provider,
            username=username,
            password=password,
            imap_host=imap_host,
            imap_port=imap_port,
            default=default,
        )
        console.print(f"[green]Account '{account['name']}' added successfully.[/green]")
        console.print(f"  Host: {account['imap_host']}:{account['imap_port']}")
        if account.get("default"):
            console.print("  [bold]Set as default account[/bold]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_cmd() -> None:
    """List all configured accounts."""
    accounts = _list_accounts()
    if not accounts:
        console.print("[yellow]No accounts configured. Use 'mg auth add' to add one.[/yellow]")
        return

    table = Table(title="Mail Accounts")
    table.add_column("Name", style="cyan")
    table.add_column("Provider")
    table.add_column("Username")
    table.add_column("IMAP Host")
    table.add_column("Default", justify="center")

    for acc in accounts:
        table.add_row(
            acc["name"],
            acc.get("provider", ""),
            acc.get("username", ""),
            f"{acc.get('imap_host', '')}:{acc.get('imap_port', 993)}",
            "*" if acc.get("default") else "",
        )

    console.print(table)


@app.command()
def remove(name: str = typer.Argument(..., help="Account name to remove")) -> None:
    """Remove a configured account."""
    if remove_account(name):
        console.print(f"[green]Account '{name}' removed.[/green]")
    else:
        console.print(f"[red]Account '{name}' not found.[/red]")
        raise typer.Exit(1)


@app.command()
def test(
    account: Optional[str] = typer.Option(None, help="Account name to test"),
) -> None:
    """Test IMAP connection for an account."""
    from mailguardian.accounts import get_account
    from mailguardian.imap_client import connect

    acc = get_account(account)
    if not acc:
        console.print("[red]No account found. Use 'mg auth add' first.[/red]")
        raise typer.Exit(1)

    pw = get_password(acc["name"])
    if not pw:
        console.print(f"[red]No password found for '{acc['name']}'. Re-add the account.[/red]")
        raise typer.Exit(1)

    try:
        client = connect(acc["imap_host"], acc["imap_port"], acc["username"], pw)
        folders = client.list_folders()
        client.logout()
        console.print(f"[green]Connection to '{acc['name']}' successful![/green]")
        console.print(f"  {len(folders)} folders found.")
    except Exception as e:
        console.print(f"[red]Connection failed: {e}[/red]")
        raise typer.Exit(1)
