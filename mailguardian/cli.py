"""Main CLI application with Typer subcommands."""

import typer

from mailguardian import __version__
from mailguardian.auth import app as auth_app
from mailguardian.inbox import app as inbox_app
from mailguardian.calendar_ import app as calendar_app
from mailguardian.agent import app as agent_app

app = typer.Typer(
    name="mg",
    help="MailGuardian – Agent-native CLI for email triage and calendar management",
    no_args_is_help=True,
)

app.add_typer(auth_app, name="auth")
app.add_typer(inbox_app, name="inbox")
app.add_typer(calendar_app, name="calendar")
app.add_typer(agent_app, name="agent")


@app.command()
def version() -> None:
    """Show MailGuardian version."""
    typer.echo(f"MailGuardian v{__version__}")
