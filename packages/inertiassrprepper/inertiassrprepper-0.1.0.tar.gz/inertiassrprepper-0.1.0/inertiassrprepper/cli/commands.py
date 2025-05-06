"""
CLI commands for InertiaSSRPrepper
"""
import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm

from inertiassrprepper.scanner.scanner import LaravelInertiaScanner
from inertiassrprepper.reporter.reporter import SSRIssueReporter

console = Console()

def print_welcome_message() -> None:
    """Print welcome message with ASCII art"""
    welcome_text = r"""
 _____               _   _        _____ _____ _____   _____                                
|_   _|             | | (_)      /  ___/  ___|  __ \ |  __ \                               
  | | _ __   ___ _ __| |_ _  __ _\ `---.\ `---.| |  \/ | |  \/_ __ ___ _ __  _ __   ___ _ __ 
  | || '_ \ / _ \ '__| __| |/ _` |`--. \`--. \ | __  | | __| '__/ _ \ '_ \| '_ \ / _ \ '__|
 _| || | | |  __/ |  | |_| | (_| /\__/ /\__/ / |_\ \ | |_\ \ | |  __/ |_) | |_) |  __/ |   
 \___/_| |_|\___|_|   \__|_|\__,_\____/\____/ \____/  \____/_|  \___| .__/| .__/ \___|_|   
                                                                     | |   | |              
                                                                     |_|   |_|              
    """
    console.print(Panel(
        welcome_text,
        title="[bold cyan]InertiaSSRPrepper[/bold cyan]",
        subtitle="[green]Find and fix SSR compatibility issues[/green]",
        border_style="blue",
    ))

def verify_laravel_inertia_app(path: Path) -> Tuple[bool, str]:
    """
    Verify that the given path is a Laravel Inertia application
    """
    # Check for Laravel
    if not (path / "artisan").exists():
        return False, "artisan file not found. Is this a Laravel application?"
    
    # Check for Inertia
    composer_json = path / "composer.json"
    package_json = path / "package.json"
    
    has_inertia = False
    inertia_msg = ""
    
    if composer_json.exists():
        try:
            import json
            with open(composer_json, 'r') as f:
                composer_data = json.load(f)
                
            require = composer_data.get('require', {})
            if 'inertiajs/inertia-laravel' in require:
                has_inertia = True
                inertia_msg = "Found inertia-laravel in composer.json"
        except:
            pass
    
    if not has_inertia and package_json.exists():
        try:
            import json
            with open(package_json, 'r') as f:
                package_data = json.load(f)
                
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            
            if '@inertiajs/vue3' in dependencies or '@inertiajs/inertia-vue3' in dependencies or '@inertiajs/vue3' in dev_dependencies or '@inertiajs/inertia-vue3' in dev_dependencies:
                has_inertia = True
                inertia_msg = "Found @inertiajs/vue3 in package.json"
        except:
            pass
    
    return has_inertia, inertia_msg

def scan_command(
    path: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=True,
        file_okay=False,
        help="Path to Laravel Inertia application to scan",
    ),
    ignore_patterns: Optional[List[str]] = typer.Option(
        None,
        "--ignore",
        "-i",
        help="Additional glob patterns to ignore (already ignores .git, node_modules, vendor, public, storage, etc.)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path for report (defaults to stdout). Use .json or .html extension for specific formats.",
    ),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Report format: 'json' or 'html' (defaults to using file extension or json)",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        envvar="ANTHROPIC_API_KEY",
        help="Anthropic API key for Claude (can also use ANTHROPIC_API_KEY env var)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    no_verify: bool = typer.Option(
        False,
        "--no-verify",
        help="Skip verification of Laravel Inertia app",
    ),
    max_files: Optional[int] = typer.Option(
        None,
        "--max-files",
        help="Maximum number of files to scan (for testing)",
    ),
) -> None:
    """
    Scan a Laravel Inertia Vue application for SSR compatibility issues
    """
    # Print welcome message
    print_welcome_message()
    
    # Verify app is Laravel + Inertia
    if not no_verify:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Verifying application...[/bold blue]"),
            transient=True,
        ) as progress:
            task = progress.add_task("Verifying", total=None)
            is_inertia, msg = verify_laravel_inertia_app(path)
            progress.update(task, completed=True)
        
        if not is_inertia:
            console.print(f"[bold yellow]Warning:[/bold yellow] This doesn't appear to be a Laravel Inertia application.")
            console.print(f"[dim]{msg}[/dim]")
            
            if not Confirm.ask("Continue anyway?"):
                console.print("[bold red]Scan aborted.[/bold red]")
                raise typer.Exit(1)
        else:
            console.print(f"[bold green]✓[/bold green] Laravel Inertia application detected! ({msg})")
    
    console.print(f"[bold blue]Scanning[/bold blue] [green]{path}[/green] for SSR compatibility issues...")
    
    # Create scanner
    scanner = LaravelInertiaScanner(
        root_path=path,
        ignore_patterns=ignore_patterns,
        verbose=verbose,
        max_files=max_files,
    )
    
    # If format is specified but output is not, create a default output path
    if format and not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = Path(f"ssr_report_{timestamp}.{format}")
    
    # If format is specified, ensure output has correct extension
    if format and output:
        if format.lower() == 'json' and output.suffix.lower() != '.json':
            output = output.with_suffix('.json')
        elif format.lower() == 'html' and output.suffix.lower() != '.html':
            output = output.with_suffix('.html')
    
    # Scan for issues
    issues = scanner.scan()
    
    # If output is not specified but we have issues, create a default HTML report
    if not output and format is None and issues:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = Path(f"ssr_report_{timestamp}.html")
        console.print(f"[bold green]Creating HTML report:[/bold green] [cyan]{output}[/cyan]")
    
    # Check if Claude API is available
    if not api_key and "ANTHROPIC_API_KEY" not in os.environ:
        console.print(
            "[bold yellow]Note:[/bold yellow] No Claude API key provided. "
            "For enhanced solutions, provide an API key with --api-key or set ANTHROPIC_API_KEY environment variable."
        )
    
    # Create reporter
    reporter = SSRIssueReporter(
        issues=issues,
        api_key=api_key,
        verbose=verbose,
    )
    
    # Generate and output report
    if output:
        reporter.generate_report(output_path=output)
    else:
        reporter.generate_report(output_path=None)