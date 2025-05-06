"""
Reporter for SSR compatibility issues
"""
import os
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Counter as CounterType
from collections import Counter
import json

from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.layout import Layout
from rich.text import Text

from inertiassrprepper.scanner.scanner import SSRIssue
from inertiassrprepper.api.claude import get_solution_from_claude
from inertiassrprepper.patterns.ssr_patterns import SSR_ISSUE_CATEGORIES
from inertiassrprepper.templates.html_report import generate_html_report
from inertiassrprepper.templates.html_simple import generate_simple_html_report

console = Console()

class SSRIssueReporter:
    """
    Reporter for SSR compatibility issues
    """
    def __init__(
        self,
        issues: List[SSRIssue],
        api_key: Optional[str] = None,
        verbose: bool = False,
    ):
        self.issues = issues
        self.api_key = api_key
        self.verbose = verbose
        
        # Group issues by file
        self.grouped_issues = self._group_issues()
        
        # Count issues by type and severity
        self.issue_counts: CounterType[str] = Counter()
        self.severity_counts: CounterType[str] = Counter()
        
        for issue in self.issues:
            self.issue_counts[issue.issue_type] += 1
            self.severity_counts[issue.severity] += 1
        
    def _group_issues(self) -> Dict[str, List[SSRIssue]]:
        """
        Group issues by file path
        """
        grouped = {}
        for issue in self.issues:
            file_path = str(issue.file_path)
            if file_path not in grouped:
                grouped[file_path] = []
            grouped[file_path].append(issue)
        return grouped
        
    def _create_summary_panel(self) -> Panel:
        """Create a summary panel with issue statistics"""
        # Create the main layout
        layout = Layout()
        layout.split_column(
            Layout(name="header"),
            Layout(name="stats", ratio=2),
            Layout(name="severity", ratio=2),
            Layout(name="types", ratio=3),
        )
        
        # Header section
        header_text = Text.from_markup(
            f"[bold green]SSR Compatibility Scan Complete[/bold green]\n"
            f"[cyan]Found [bold red]{len(self.issues)}[/bold red] potential issues in [bold yellow]{len(self.grouped_issues)}[/bold yellow] files[/cyan]"
        )
        layout["header"].update(Align.center(header_text))
        
        # Create stats table
        stats_table = Table(box=None, show_header=False, pad_edge=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Issues", str(len(self.issues)))
        stats_table.add_row("Files with Issues", str(len(self.grouped_issues)))
        stats_table.add_row("Issue Types", str(len(self.issue_counts)))
        
        layout["stats"].update(Align.center(stats_table))
        
        # Create severity table
        severity_table = Table(title="Issues by Severity", box=box.SIMPLE)
        severity_table.add_column("Severity", style="cyan")
        severity_table.add_column("Count", style="magenta")
        severity_table.add_column("Percentage", style="yellow")
        
        severity_colors = {
            'critical': 'red',
            'major': 'orange1',
            'medium': 'yellow',
            'minor': 'green',
        }
        
        # Display severities in order of importance
        severities = ['critical', 'major', 'medium', 'minor']
        for severity in severities:
            count = self.severity_counts.get(severity, 0)
            if count > 0:
                percentage = (count / len(self.issues)) * 100
                color = severity_colors.get(severity, 'white')
                severity_table.add_row(
                    f"[bold {color}]{severity.title()}[/bold {color}]",
                    str(count),
                    f"{percentage:.1f}%"
                )
                
        layout["severity"].update(Align.center(severity_table))
        
        # Create issue types table
        types_table = Table(title="Top Issue Types", box=box.SIMPLE)
        types_table.add_column("Issue Type", style="cyan")
        types_table.add_column("Count", style="magenta")
        types_table.add_column("Severity", style="yellow")
        
        # Show top 5 issue types
        for issue_type, count in self.issue_counts.most_common(5):
            # Get severity for this issue type
            severity = "minor"  # Default
            for sev, types in SSR_ISSUE_CATEGORIES.items():
                if issue_type in types:
                    severity = sev
                    break
                    
            color = severity_colors.get(severity, 'white')
            types_table.add_row(
                issue_type,
                str(count),
                f"[{color}]{severity.title()}[/{color}]"
            )
            
        layout["types"].update(Align.center(types_table))
        
        return Panel(
            layout,
            title="SSR Compatibility Scan Summary",
            border_style="green",
            padding=(1, 2),
        )
        
    def generate_report(self, output_path: Optional[Path] = None) -> None:
        """
        Generate and output report
        """
        if not self.issues:
            console.print("[bold green]No SSR compatibility issues found![/bold green]")
            return
        
        # Print summary panel
        console.print(self._create_summary_panel())
        
        # If API key is provided, get advanced solutions
        if self.api_key and self.issues:
            console.print("\n[bold blue]Getting detailed solutions from Claude...[/bold blue]")
            self._enrich_issues_with_claude()
        
        # Print detailed issues grouped by file
        console.print("\n[bold blue]Detailed Issue Report[/bold blue]")
        
        # Sort files by number of issues (descending)
        sorted_files = sorted(
            self.grouped_issues.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )
        
        for file_path, issues in sorted_files:
            # Sort issues by severity and line number
            sorted_issues = sorted(
                issues, 
                key=lambda x: (
                    # Order: critical, major, medium, minor
                    ['critical', 'major', 'medium', 'minor'].index(x.severity) 
                    if x.severity in ['critical', 'major', 'medium', 'minor'] else 999,
                    x.line_number
                )
            )
            
            # Create file panel
            file_issues_table = Table(show_header=True, box=box.SIMPLE, highlight=True)
            file_issues_table.add_column("Line", style="cyan", no_wrap=True)
            file_issues_table.add_column("Severity", style="cyan", no_wrap=True)
            file_issues_table.add_column("Issue", style="magenta")
            file_issues_table.add_column("Solution", style="green")
            
            for issue in sorted_issues:
                # Determine language for syntax highlighting
                file_ext = os.path.splitext(issue.file_path)[1].lower()
                syntax_lang = "javascript"  # Default
                
                if file_ext == ".vue":
                    syntax_lang = "vue"
                elif file_ext == ".php" or file_ext == ".blade.php":
                    syntax_lang = "php"
                elif file_ext in [".css", ".scss", ".sass", ".less"]:
                    syntax_lang = "css"
                elif file_ext in [".html", ".htm"]:
                    syntax_lang = "html"
                
                # For the issue column, we'll create a renderable object
                from rich.console import Group
                from rich.text import Text
                from rich.padding import Padding
                
                # Create syntax highlighted code snippet
                code_snippet = Syntax(
                    issue.line_content, 
                    syntax_lang,
                    theme="monokai",
                    line_numbers=True,
                    start_line=issue.line_number
                )
                
                # Create a group of renderables for the issue column
                issue_title = Text(issue.issue_type, style="bold")
                issue_message = Text(issue.message)
                issue_content = Group(
                    issue_title,
                    issue_message,
                    Padding(code_snippet, (1, 0, 0, 0))  # Add padding above the code
                )
                
                # Add row for this issue
                file_issues_table.add_row(
                    f"{issue.line_number}",
                    f"[{issue.severity_color}]{issue.severity.upper()}[/{issue.severity_color}]",
                    issue_content,
                    issue.solution or "[italic]No solution available[/italic]",
                )
            
            # Create and print panel for this file
            rel_path = os.path.relpath(file_path)
            console.print(Panel(
                file_issues_table,
                title=f"[bold cyan]{rel_path}[/bold cyan] ([bold red]{len(issues)}[/bold red] issues)",
                border_style="blue",
                expand=False,
            ))
        
        # Output to file if requested
        if output_path:
            file_ext = output_path.suffix.lower()
            
            if file_ext == '.html':
                # Generate HTML report using the original template with simplified interface
                generate_html_report(self.issues, output_path)
                console.print(f"\n[bold green]HTML report saved to [cyan]{output_path}[/cyan][/bold green]")
            elif file_ext == '.json':
                # Create JSON report
                with open(output_path, 'w', encoding='utf-8') as f:
                    json_report = {
                        "summary": {
                            "total_issues": len(self.issues),
                            "total_files": len(self.grouped_issues),
                            "issues_by_type": {k: v for k, v in self.issue_counts.items()},
                            "issues_by_severity": {k: v for k, v in self.severity_counts.items()},
                        },
                        "issues": [
                            {
                                "file_path": str(issue.file_path),
                                "relative_path": os.path.relpath(str(issue.file_path)),
                                "line_number": issue.line_number,
                                "line_content": issue.line_content,
                                "issue_type": issue.issue_type,
                                "severity": issue.severity,
                                "message": issue.message,
                                "solution": issue.solution,
                            }
                            for issue in self.issues
                        ],
                    }
                    
                    json.dump(json_report, f, indent=2)
                    console.print(f"\n[bold green]JSON report saved to [cyan]{output_path}[/cyan][/bold green]")
            else:
                # Default to JSON format with message
                output_path_json = output_path.with_suffix('.json')
                with open(output_path_json, 'w', encoding='utf-8') as f:
                    json_report = {
                        "summary": {
                            "total_issues": len(self.issues),
                            "total_files": len(self.grouped_issues),
                            "issues_by_type": {k: v for k, v in self.issue_counts.items()},
                            "issues_by_severity": {k: v for k, v in self.severity_counts.items()},
                        },
                        "issues": [
                            {
                                "file_path": str(issue.file_path),
                                "relative_path": os.path.relpath(str(issue.file_path)),
                                "line_number": issue.line_number,
                                "line_content": issue.line_content,
                                "issue_type": issue.issue_type,
                                "severity": issue.severity,
                                "message": issue.message,
                                "solution": issue.solution,
                            }
                            for issue in self.issues
                        ],
                    }
                    
                    json.dump(json_report, f, indent=2)
                    console.print(
                        f"\n[bold yellow]Note:[/bold yellow] Unrecognized file extension '{file_ext}'. "
                        f"Using JSON format instead.\n"
                        f"[bold green]JSON report saved to [cyan]{output_path_json}[/cyan][/bold green]"
                    )
    
    def _enrich_issues_with_claude(self) -> None:
        """
        Enrich issues with solutions from Claude
        """
        # Group similar issues to avoid duplicate API calls
        unique_issues = {}
        for issue in self.issues:
            key = f"{issue.issue_type}:{issue.message}"
            if key not in unique_issues:
                unique_issues[key] = issue
        
        total = len(unique_issues)
        
        # Get solution for each unique issue with progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Getting solutions from Claude... {task.completed}/{task.total}[/bold blue]"),
            transient=False,
        ) as progress:
            task = progress.add_task("Getting solutions", total=total)
            
            for key, issue in unique_issues.items():
                if self.verbose:
                    console.print(f"Getting solution for [cyan]{issue.issue_type}[/cyan] (severity: [{issue.severity_color}]{issue.severity}[/{issue.severity_color}])...")
                
                solution = get_solution_from_claude(
                    api_key=self.api_key,
                    issue_type=issue.issue_type,
                    code_snippet=issue.line_content,
                    message=issue.message,
                    severity=issue.severity,
                )
                
                # Update all similar issues with the solution
                for i in self.issues:
                    if f"{i.issue_type}:{i.message}" == key:
                        i.solution = solution
                
                progress.update(task, advance=1)
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.5)