"""Autonomous dispatcher – periodic inbox check and classification."""

import typer

app = typer.Typer(help="Autonomous agent operations")


@app.command()
def run(
    interval: int = typer.Option(300, help="Check interval in seconds"),
) -> None:
    """Run the autonomous mail agent loop."""
    typer.echo(f"TODO: start agent loop with {interval}s interval")
