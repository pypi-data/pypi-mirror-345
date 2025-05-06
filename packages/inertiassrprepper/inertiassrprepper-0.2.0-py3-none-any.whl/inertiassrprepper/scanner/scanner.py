"""
Scanner for Laravel Inertia Vue applications
"""
import os
import re
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Set, Counter as CounterType
from collections import Counter

from rich.console import Console
from rich.progress import (
    Progress, 
    TaskID, 
    TextColumn, 
    BarColumn, 
    TaskProgressColumn, 
    TimeRemainingColumn,
    SpinnerColumn,
    MofNCompleteColumn
)
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
import pathspec

from inertiassrprepper.patterns.ssr_patterns import SSR_ISSUE_PATTERNS, get_issue_severity
from inertiassrprepper.utils.file_utils import is_text_file, get_file_type

console = Console()

class SSRIssue:
    """
    Represents an SSR compatibility issue
    """
    def __init__(
        self,
        file_path: Path,
        line_number: int,
        line_content: str,
        issue_type: str,
        message: str,
        solution: Optional[str] = None,
        context_before: Optional[List[str]] = None,
        context_after: Optional[List[str]] = None,
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.line_content = line_content
        self.issue_type = issue_type
        self.message = message
        self.solution = solution
        self.context_before = context_before or []
        self.context_after = context_after or []
        self.rel_path = str(file_path).split('/')[-1]  # Only filename for display
        self.severity = get_issue_severity(issue_type)
        
    def __repr__(self) -> str:
        return f"SSRIssue({self.issue_type}, {self.rel_path}:{self.line_number}, severity={self.severity})"
        
    @property
    def severity_color(self) -> str:
        """Get color for severity level"""
        colors = {
            'critical': 'red',
            'major': 'orange1',
            'medium': 'yellow',
            'minor': 'green',
        }
        return colors.get(self.severity, 'white')

class ScanStats:
    """
    Statistics for the scanning process
    """
    def __init__(self):
        self.start_time = time.time()
        self.files_scanned = 0
        self.files_with_issues = 0
        self.total_issues = 0
        self.issues_by_type: CounterType[str] = Counter()
        self.issues_by_severity: CounterType[str] = Counter()
        self.file_types_scanned: CounterType[str] = Counter()
        self.file_types_with_issues: CounterType[str] = Counter()
        self.recent_issues: List[SSRIssue] = []  # Keep the most recent issues
    
    def add_file_scanned(self, file_path: Path) -> None:
        """Add a scanned file to stats"""
        self.files_scanned += 1
        file_type = get_file_type(file_path)
        self.file_types_scanned[file_type] += 1
    
    def add_issues(self, issues: List[SSRIssue]) -> None:
        """Add issues to stats"""
        if issues:
            self.files_with_issues += 1
            self.total_issues += len(issues)
            
            # Track file type with issues
            if issues:
                file_type = get_file_type(issues[0].file_path)
                self.file_types_with_issues[file_type] += 1
            
            for issue in issues:
                self.issues_by_type[issue.issue_type] += 1
                self.issues_by_severity[issue.severity] += 1
            
            # Keep the most recent issues for the live display
            self.recent_issues = (issues + self.recent_issues)[:5]
    
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return time.time() - self.start_time
    
    def issues_per_file(self) -> float:
        """Get average issues per file with issues"""
        if self.files_with_issues == 0:
            return 0.0
        return self.total_issues / self.files_with_issues
    
    def files_per_second(self) -> float:
        """Get files processed per second"""
        elapsed = self.elapsed_time()
        if elapsed == 0:
            return 0.0
        return self.files_scanned / elapsed
        
    def get_severity_counts(self) -> Dict[str, int]:
        """Get counts of issues by severity level in order of importance"""
        severities = ['critical', 'major', 'medium', 'minor']
        return {sev: self.issues_by_severity.get(sev, 0) for sev in severities}

class LaravelInertiaScanner:
    """
    Scanner for Laravel Inertia Vue applications
    """
    def __init__(
        self,
        root_path: Path,
        ignore_patterns: Optional[List[str]] = None,
        verbose: bool = False,
        max_files: Optional[int] = None,
    ):
        self.root_path = root_path
        self.verbose = verbose
        self.max_files = max_files
        
        # Default ignore patterns
        default_ignore = [
            # Base directories to ignore
            ".git/",
            "node_modules/",
            "vendor/",
            "public/",
            "storage/",
            "bootstrap/cache/",
            
            # Admin panel directories
            "**/nova/**",
            "**/filament/**", 
            "**/backpack/**",
            "**/orchid/**",
            "**/horizon/**",
            "**/telescope/**",
            "**/jetstream/**",
            "**/breeze/**",
            "**/spark/**",
            "**/vapor/**",
            "**/livewire/**",
            "**/enso/**",
            "**/admin/**",
            "**/dashboard/**",
            
            # Build/compiled assets
            "**.map",
            "**.min.js",
            "**.min.css",
            "**/dist/**",
            "**/.DS_Store",
            "**/__pycache__/**",
            "**/.next/**",
            "**/build/**",
            "**/compiled/**",
            
            # Database and test files
            "**/migrations/**",
            "**/database/seeders/**",
            "**/tests/**",
            "**/testing/**",
            "**/__tests__/**",
        ]
        
        # Combine with user provided patterns
        all_ignore_patterns = default_ignore + (ignore_patterns or [])
        
        # Create pathspec for ignoring files
        self.spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern, all_ignore_patterns
        )
        
        # Initialize stats
        self.stats = ScanStats()
        
    def _create_stats_table(self) -> Table:
        """Create a statistics table for the live display"""
        table = Table(title="Scan Statistics", show_header=True, box=None)
        
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        elapsed = self.stats.elapsed_time()
        elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"
        
        table.add_row("Files Scanned", str(self.stats.files_scanned))
        table.add_row("Files With Issues", str(self.stats.files_with_issues))
        table.add_row("Total Issues", str(self.stats.total_issues))
        table.add_row("Time Elapsed", elapsed_str)
        table.add_row("Files/Second", f"{self.stats.files_per_second():.1f}")
        
        # Add severity breakdown if we have issues
        if self.stats.total_issues > 0:
            table.add_row("", "")
            table.add_row("[bold]Issues by Severity[/bold]", "")
            
            severity_colors = {
                'critical': 'red',
                'major': 'orange1',
                'medium': 'yellow',
                'minor': 'green',
            }
            
            severity_counts = self.stats.get_severity_counts()
            for severity, count in severity_counts.items():
                if count > 0:
                    color = severity_colors.get(severity, 'white')
                    table.add_row(
                        f" - [bold {color}]{severity.title()}[/bold {color}]", 
                        str(count)
                    )
        
        # Add top issue types if we have issues
        if self.stats.issues_by_type:
            table.add_row("", "")
            table.add_row("[bold]Top Issue Types[/bold]", "")
            
            for issue_type, count in self.stats.issues_by_type.most_common(3):
                table.add_row(f" - {issue_type}", str(count))
        
        return table
    
    def _create_recent_issues_table(self) -> Table:
        """Create a table of recent issues for the live display"""
        if not self.stats.recent_issues:
            return None
            
        table = Table(title="Recent Issues", show_header=True, box=None)
        
        table.add_column("File", style="cyan")
        table.add_column("Line", style="magenta")
        table.add_column("Type", style="yellow")
        
        for issue in self.stats.recent_issues:
            table.add_row(
                issue.rel_path,
                str(issue.line_number),
                issue.issue_type
            )
            
        return table
        
    def scan(self) -> List[SSRIssue]:
        """
        Scan the application for SSR compatibility issues
        """
        all_issues: List[SSRIssue] = []
        scannable_files: List[Path] = []
        
        # First find all files to scan
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Finding files to scan...[/bold blue]"),
            BarColumn(),
            MofNCompleteColumn(),
            transient=False,
        ) as progress:
            find_task = progress.add_task("Finding files", total=None)
            
            for root, _, files in os.walk(self.root_path):
                root_path = Path(root)
                for file in files:
                    file_path = root_path / file
                    rel_path = file_path.relative_to(self.root_path)
                    
                    # Skip ignored files
                    if self.spec.match_file(str(rel_path)):
                        continue
                    
                    # Only scan text files
                    if is_text_file(file_path):
                        scannable_files.append(file_path)
                        
                        # Update progress description periodically
                        if len(scannable_files) % 100 == 0:
                            progress.update(find_task, description=f"Finding files ({len(scannable_files)} found)")
            
            # Apply max_files limit if specified
            if self.max_files is not None:
                scannable_files = scannable_files[:self.max_files]
                
            progress.update(find_task, description=f"Found {len(scannable_files)} files to scan", completed=True)
        
        # Now scan files with progress
        progress = Progress(
            TextColumn("[bold green]{task.description}[/bold green]"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
        )
        
        scan_task = progress.add_task("Scanning files...", total=len(scannable_files))
        
        # Create a live display with both progress and stats
        layout = Table.grid()
        layout.add_row(Panel(progress))
        
        stats_panel = Panel(self._create_stats_table(), title="Scanning Progress", border_style="blue")
        layout.add_row(stats_panel)
        
        with Live(layout, refresh_per_second=4) as live:
            for i, file_path in enumerate(scannable_files):
                rel_path = file_path.relative_to(self.root_path)
                
                # Update description periodically to show current file
                if i % 10 == 0 or self.verbose:
                    progress.update(scan_task, description=f"Scanning [cyan]{rel_path}[/cyan]")
                
                # Scan the file
                file_issues = self._scan_file(file_path)
                
                # Update stats
                self.stats.add_file_scanned(file_path)
                self.stats.add_issues(file_issues)
                
                # Add to all issues
                all_issues.extend(file_issues)
                
                # Update progress
                progress.update(scan_task, advance=1)
                
                # Update the live display with latest stats
                stats_table = self._create_stats_table()
                recent_issues_table = self._create_recent_issues_table()
                
                if recent_issues_table:
                    stats_grid = Table.grid()
                    stats_grid.add_row(stats_table)
                    stats_grid.add_row(recent_issues_table)
                    stats_panel = Panel(stats_grid, title="Scanning Progress", border_style="blue")
                else:
                    stats_panel = Panel(stats_table, title="Scanning Progress", border_style="blue")
                    
                layout = Table.grid()
                layout.add_row(Panel(progress))
                layout.add_row(stats_panel)
                
                live.update(layout)
        
        console.print(f"[bold green]Scan complete![/bold green] Found [bold red]{len(all_issues)}[/bold red] potential SSR issues in [bold yellow]{self.stats.files_with_issues}[/bold yellow] files.")
        
        return all_issues
    
    def _scan_file(self, file_path: Path) -> List[SSRIssue]:
        """
        Scan a single file for SSR compatibility issues
        """
        issues = []
        
        # Skip very large files or binary files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (UnicodeDecodeError, IOError):
            return []
        
        # Skip empty files
        if not lines:
            return []
        
        # Get file extension to determine which patterns to check
        file_ext = file_path.suffix.lower()
        
        # Keep track of lines with issues to avoid duplicates
        lines_with_issues: Set[int] = set()
        
        # Check each line for issues
        for i, line in enumerate(lines):
            line_number = i + 1
            
            # Skip if we already found an issue on this line (avoid duplicates)
            if line_number in lines_with_issues:
                continue
                
            # Apply each pattern
            for pattern in SSR_ISSUE_PATTERNS:
                # Skip patterns that don't apply to this file type
                if pattern.get('file_extensions') and file_ext not in pattern.get('file_extensions'):
                    continue
                
                # Check if this line matches the pattern
                try:
                    if re.search(pattern['pattern'], line):
                        match_found = True
                    else:
                        match_found = False
                except re.error:
                    # If regex is too complex or has errors, fall back to simpler substring search
                    simple_terms = pattern.get('simple_terms', [])
                    match_found = any(term in line for term in simple_terms) if simple_terms else False
                
                if match_found:
                    # Get context lines (up to 3 lines before and after)
                    context_before = [lines[max(0, i-3):i]]
                    context_after = [lines[i+1:min(len(lines), i+4)]]
                    
                    issues.append(SSRIssue(
                        file_path=file_path,
                        line_number=line_number,
                        line_content=line.strip(),
                        issue_type=pattern['type'],
                        message=pattern['message'],
                        solution=pattern.get('solution'),
                        context_before=context_before,
                        context_after=context_after,
                    ))
                    
                    # Mark this line as having an issue
                    lines_with_issues.add(line_number)
                    break  # Only one issue type per line to avoid duplicates
        
        return issues