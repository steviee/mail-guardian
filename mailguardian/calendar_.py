"""Google Calendar integration (underscore to avoid stdlib collision)."""

import typer

app = typer.Typer(help="Calendar operations")


@app.command()
def view(
    day: str = typer.Option("today", help="Day to view (today|tomorrow)"),
) -> None:
    """View calendar events."""
    typer.echo(f"TODO: view calendar for {day}")


@app.command()
def add(text: str = typer.Argument(..., help="Event description in natural language")) -> None:
    """Add a calendar event using natural language."""
    typer.echo(f"TODO: create event from '{text}'")
