"""
InertiaSSRPrepper - CLI tool to identify SSR compatibility issues in Laravel Inertia Vue applications
"""
import os
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich import print as rprint

from inertiassrprepper.cli.commands import scan_command
from inertiassrprepper.__version__ import __version__

# Create Typer app
app = typer.Typer(
    name="inertiassr",
    help="CLI tool to identify SSR compatibility issues in Laravel Inertia Vue applications",
    add_completion=False,
)

console = Console()

def version_callback(value: bool):
    """Show version information and exit"""
    if value:
        rprint(f"[bold cyan]InertiaSSRPrepper[/bold cyan] [green]v{__version__}[/green]")
        rprint("[dim]A modern CLI tool to identify SSR compatibility issues in Laravel Inertia Vue applications[/dim]")
        raise typer.Exit()

# Add version option to the app
@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    InertiaSSRPrepper - Find and fix SSR compatibility issues in Laravel Inertia Vue applications
    """
    pass

# Register commands
app.command(name="scan")(scan_command)

if __name__ == "__main__":
    app()