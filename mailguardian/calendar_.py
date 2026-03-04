"""Google Calendar CLI commands (underscore to avoid stdlib collision)."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mailguardian.config import DEFAULT_LLM_MODEL

app = typer.Typer(help="Calendar operations")
console = Console()


@app.command("auth")
def auth() -> None:
    """Authenticate with Google Calendar (OAuth2 flow)."""
    from mailguardian.gcal import authenticate, CREDENTIALS_FILE

    if not CREDENTIALS_FILE.exists():
        console.print(
            f"[red]Missing credentials file:[/red] {CREDENTIALS_FILE}\n"
            "Download from Google Cloud Console → APIs & Services → Credentials\n"
            "and save as 'gcal_credentials.json' in ~/.config/mailguardian/"
        )
        raise typer.Exit(1)

    console.print("[dim]Opening browser for Google OAuth2...[/dim]")
    if authenticate():
        console.print("[green]Google Calendar authenticated successfully![/green]")
    else:
        console.print("[red]Authentication failed.[/red]")
        raise typer.Exit(1)


@app.command()
def view(
    day: str = typer.Option("today", help="Day to view (today|tomorrow|YYYY-MM-DD)"),
) -> None:
    """View calendar events for a day."""
    from mailguardian.gcal import get_events

    try:
        events = get_events(day=day)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Calendar error: {e}[/red]")
        raise typer.Exit(1)

    if not events:
        console.print(f"[yellow]No events for {day}.[/yellow]")
        return

    table = Table(title=f"Calendar — {day}")
    table.add_column("Time", style="cyan", width=14)
    table.add_column("Event")
    table.add_column("Location", style="dim")

    for ev in events:
        if ev.all_day:
            time_str = "All day"
        elif ev.start:
            end_str = ev.end.strftime("%H:%M") if ev.end else ""
            time_str = f"{ev.start.strftime('%H:%M')}–{end_str}"
        else:
            time_str = ""

        table.add_row(time_str, ev.summary, ev.location)

    console.print(table)


@app.command()
def add(
    text: str = typer.Argument(..., help="Event description in natural language"),
    model: str = typer.Option(DEFAULT_LLM_MODEL, help="LLM model for parsing"),
) -> None:
    """Add a calendar event using natural language (AI-powered)."""
    import json
    from datetime import datetime

    from mailguardian.gcal import create_event

    try:
        import litellm

        response = litellm.completion(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Today is {datetime.now().strftime('%Y-%m-%d %A')}. "
                        "Parse the user's text into a calendar event. Return JSON with:\n"
                        '- "summary": event title\n'
                        '- "start": ISO datetime string\n'
                        '- "end": ISO datetime string\n'
                        '- "location": string (optional, empty if not mentioned)\n'
                        "Return ONLY valid JSON, no markdown."
                    ),
                },
                {"role": "user", "content": text},
            ],
            max_tokens=200,
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        data = json.loads(raw)
        start = datetime.fromisoformat(data["start"])
        end = datetime.fromisoformat(data["end"])

        console.print(f"[dim]Creating event: {data['summary']}[/dim]")
        console.print(f"[dim]  {start.strftime('%Y-%m-%d %H:%M')} – {end.strftime('%H:%M')}[/dim]")

        result = create_event(
            summary=data["summary"],
            start=start,
            end=end,
            location=data.get("location", ""),
        )
        console.print(f"[green]Event created![/green] ID: {result['id']}")

    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
