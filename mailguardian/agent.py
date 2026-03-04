"""Autonomous dispatcher – periodic inbox check and classification."""

from __future__ import annotations

import signal
import sys
import time
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from mailguardian.accounts import get_account, get_password, list_accounts
from mailguardian.config import load_settings
from mailguardian.imap_client import connect, fetch_mail_detail, fetch_mail_list
from mailguardian.llm import classify_mail
from mailguardian.playbooks import Playbook, create_default_playbooks, load_playbooks

app = typer.Typer(help="Autonomous agent operations")
console = Console()

_running = True


def _handle_signal(signum, frame):
    global _running
    _running = False
    console.print("\n[yellow]Shutting down agent...[/yellow]")


def _execute_action(playbook: Playbook, classification: dict, mail_subject: str) -> None:
    """Execute a playbook action."""
    msg = playbook.action.params.get("message", "").format(
        subject=mail_subject,
        category=classification.get("category", ""),
        priority=classification.get("priority", ""),
    )

    if playbook.action.type == "log":
        console.print(f"  [dim][{playbook.name}][/dim] {msg}")
    elif playbook.action.type == "flag":
        console.print(f"  [yellow][{playbook.name}][/yellow] {msg}")
    elif playbook.action.type == "notify":
        console.print(f"  [bold cyan][{playbook.name}][/bold cyan] {msg}")
    else:
        console.print(f"  [dim][{playbook.name}] Unknown action: {playbook.action.type}[/dim]")


def _run_cycle(
    account_name: Optional[str],
    model: str,
    limit: int,
    playbooks: list[Playbook],
) -> int:
    """Run one check cycle. Returns number of mails processed."""
    acc = get_account(account_name)
    if not acc:
        console.print("[red]No account configured.[/red]")
        return 0

    pw = get_password(acc["name"])
    if not pw:
        console.print(f"[red]No password for '{acc['name']}'.[/red]")
        return 0

    try:
        client = connect(acc["imap_host"], acc["imap_port"], acc["username"], pw)
    except Exception as e:
        console.print(f"[red]Connection failed: {e}[/red]")
        return 0

    try:
        mails = fetch_mail_list(client, limit=limit)
        if not mails:
            return 0

        # Only process unread mails
        unread = [m for m in mails if m.is_unread]
        if not unread:
            return 0

        console.print(f"[cyan]Found {len(unread)} unread mail(s)[/cyan]")

        for m in unread:
            detail = fetch_mail_detail(client, m.uid)
            body = detail.body_text if detail else ""
            classification = classify_mail(m.subject, body, model=model)

            cat = classification.get("category", "other")
            pri = classification.get("priority", "medium")
            action = classification.get("action_required", False)
            summary = classification.get("summary", "")

            status = f"[{cat}] pri={pri}"
            if action:
                status += " [red]ACTION[/red]"
            console.print(f"  #{m.uid} {m.subject[:50]} → {status}")
            if summary:
                console.print(f"    [dim]{summary}[/dim]")

            # Check playbooks
            for pb in playbooks:
                if pb.matches(classification):
                    _execute_action(pb, classification, m.subject)

        return len(unread)
    finally:
        client.logout()


@app.command()
def run(
    interval: int = typer.Option(None, help="Check interval in seconds"),
    account: Optional[str] = typer.Option(None, help="Account to monitor"),
    model: Optional[str] = typer.Option(None, help="LLM model for classification"),
    limit: int = typer.Option(20, help="Max mails per cycle"),
    once: bool = typer.Option(False, "--once", help="Run one cycle and exit"),
) -> None:
    """Run the autonomous mail agent loop."""
    global _running

    settings = load_settings()
    model = model or settings.get("llm_model", "gpt-4o-mini")
    interval = interval or settings.get("check_interval", 300)

    # Ensure playbooks exist
    create_default_playbooks()
    playbooks = load_playbooks()

    console.print(f"[bold green]MailGuardian Agent[/bold green]")
    console.print(f"  Model:    {model}")
    console.print(f"  Interval: {interval}s")
    console.print(f"  Playbooks: {len(playbooks)} loaded")
    if account:
        console.print(f"  Account: {account}")
    console.print()

    if once:
        processed = _run_cycle(account, model, limit, playbooks)
        console.print(f"\n[green]Processed {processed} mail(s).[/green]")
        return

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    console.print("[dim]Press Ctrl+C to stop.[/dim]\n")

    while _running:
        timestamp = time.strftime("%H:%M:%S")
        console.print(f"[dim]── {timestamp} ──[/dim]")
        _run_cycle(account, model, limit, playbooks)

        # Sleep in small increments so we can respond to signals
        for _ in range(interval):
            if not _running:
                break
            time.sleep(1)

    console.print("[green]Agent stopped.[/green]")


@app.command("playbooks")
def list_playbooks() -> None:
    """List all configured playbooks."""
    create_default_playbooks()
    playbooks = load_playbooks()

    if not playbooks:
        console.print("[yellow]No playbooks found.[/yellow]")
        return

    table = Table(title="Playbooks")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Match")
    table.add_column("Action")

    for pb in playbooks:
        match_str = ", ".join(f"{k}={v}" for k, v in pb.match.items())
        table.add_row(pb.name, pb.description, match_str, pb.action.type)

    console.print(table)


@app.command("status")
def status() -> None:
    """Show agent configuration and readiness."""
    settings = load_settings()
    playbooks = load_playbooks()
    accounts = list_accounts()

    console.print("[bold]MailGuardian Agent Status[/bold]\n")
    console.print(f"  Accounts:  {len(accounts)} configured")
    console.print(f"  Playbooks: {len(playbooks)} loaded")
    console.print(f"  LLM Model: {settings.get('llm_model', 'gpt-4o-mini')}")
    console.print(f"  Interval:  {settings.get('check_interval', 300)}s")

    if not accounts:
        console.print("\n[yellow]No accounts configured. Run 'mg auth add' first.[/yellow]")
    else:
        console.print("\n[green]Ready to run. Use 'mg agent run' to start.[/green]")
