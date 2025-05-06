"""
HTML Report Template for SSR compatibility issues
"""
import os
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

from jinja2 import Template

from inertiassrprepper.scanner.scanner import SSRIssue

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSR Compatibility Report</title>
    <style>
        :root {
            --color-bg: #1e1e2e;
            --color-fg: #cdd6f4;
            --color-sidebar: #181825;
            --color-primary: #89b4fa;
            --color-secondary: #f38ba8;
            --color-accent: #a6e3a1;
            --color-warning: #f9e2af;
            --color-error: #f38ba8;
            --color-info: #89dceb;
            --color-success: #a6e3a1;
            
            --color-critical: #f38ba8;
            --color-major: #fab387;
            --color-medium: #f9e2af;
            --color-minor: #a6e3a1;
            
            --font-mono: 'SF Mono', 'Consolas', 'Monaco', 'Menlo', monospace;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            background-color: var(--color-bg);
            color: var(--color-fg);
            font-family: var(--font-sans);
            line-height: 1.5;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        header {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 2rem;
            text-align: center;
            background-color: rgba(137, 180, 250, 0.1);
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid rgba(137, 180, 250, 0.2);
        }
        
        header h1 {
            color: var(--color-primary);
            margin-bottom: 0.5rem;
        }
        
        header .timestamp {
            color: var(--color-info);
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        .logo {
            font-family: var(--font-mono);
            font-size: 0.85rem;
            line-height: 1.2;
            margin-bottom: 1.5rem;
            white-space: pre;
            color: var(--color-primary);
            text-align: center;
        }
        
        .summary {
            background-color: rgba(137, 180, 250, 0.1);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(137, 180, 250, 0.2);
        }
        
        .summary h2 {
            color: var(--color-primary);
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--color-primary);
            padding-bottom: 0.5rem;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .stat-card {
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 6px;
            padding: 1rem;
            text-align: center;
        }
        
        .stat-card .value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .stat-card .label {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .severity-stats, .type-stats {
            margin-top: 1.5rem;
        }
        
        .severity-stats h3, .type-stats h3 {
            color: var(--color-secondary);
            margin-bottom: 0.5rem;
        }
        
        .severity-table, .type-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.5rem;
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 6px;
            overflow: hidden;
        }
        
        th {
            text-align: left;
            padding: 0.75rem 1rem;
            background-color: rgba(0, 0, 0, 0.3);
            color: var(--color-primary);
        }
        
        td {
            padding: 0.75rem 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .critical {
            color: var(--color-critical);
        }
        
        .major {
            color: var(--color-major);
        }
        
        .medium {
            color: var(--color-medium);
        }
        
        .minor {
            color: var(--color-minor);
        }
        
        .percentage-bar {
            height: 8px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.25rem;
        }
        
        .percentage-fill {
            height: 100%;
            border-radius: 4px;
        }
        
        .tools {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .search-box {
            flex: 1;
            min-width: 250px;
        }
        
        .search-input {
            width: 100%;
            padding: 0.75rem;
            background-color: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: var(--color-fg);
            font-family: var(--font-sans);
            font-size: 1rem;
        }
        
        .search-input:focus {
            outline: none;
            border-color: var(--color-primary);
        }
        
        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: center;
        }
        
        .filters-label {
            font-size: 0.9rem;
            color: var(--color-info);
        }
        
        .filter-button {
            background-color: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            padding: 0.5rem 0.75rem;
            color: var(--color-fg);
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .filter-button:hover {
            background-color: rgba(137, 180, 250, 0.1);
        }
        
        .filter-button.active {
            background-color: var(--color-primary);
            color: var(--color-bg);
        }
        
        .issues {
            margin-top: 2rem;
        }
        
        .issues h2 {
            color: var(--color-primary);
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--color-primary);
            padding-bottom: 0.5rem;
        }
        
        .file-issues {
            margin-bottom: 1rem;
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid rgba(137, 180, 250, 0.2);
        }
        
        .file-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: rgba(137, 180, 250, 0.1);
            padding: 0.75rem 1rem;
            cursor: pointer;
        }
        
        .file-header h3 {
            color: var(--color-info);
            font-family: var(--font-mono);
            font-size: 0.9rem;
            margin: 0;
        }
        
        .file-header .badge {
            background-color: var(--color-secondary);
            color: var(--color-bg);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .file-issues-content {
            background-color: rgba(0, 0, 0, 0.2);
        }
        
        .issue {
            padding: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .issue:last-child {
            border-bottom: none;
        }
        
        .issue-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            align-items: center;
        }
        
        .issue-type {
            font-weight: bold;
            margin-right: 1rem;
        }
        
        .issue-severity {
            font-size: 0.8rem;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            text-transform: uppercase;
            font-weight: bold;
        }
        
        .issue-severity.critical {
            background-color: rgba(243, 139, 168, 0.2);
        }
        
        .issue-severity.major {
            background-color: rgba(250, 179, 135, 0.2);
        }
        
        .issue-severity.medium {
            background-color: rgba(249, 226, 175, 0.2);
        }
        
        .issue-severity.minor {
            background-color: rgba(166, 227, 161, 0.2);
        }
        
        .issue-location {
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: var(--color-info);
            margin-bottom: 0.5rem;
            padding: 0.25rem 0;
        }
        
        .issue-message {
            margin-bottom: 1rem;
            border-left: 3px solid var(--color-info);
            padding-left: 0.75rem;
        }
        
        .code-snippet {
            background-color: rgba(0, 0, 0, 0.3);
            border-radius: 4px;
            padding: 0.75rem;
            margin-bottom: 1rem;
            overflow-x: auto;
            font-family: var(--font-mono);
            font-size: 0.85rem;
            line-height: 1.4;
            color: #f8f8f2;
        }
        
        .solution {
            background-color: rgba(166, 227, 161, 0.1);
            border-left: 3px solid var(--color-accent);
            padding: 0.75rem;
            border-radius: 0 4px 4px 0;
        }
        
        .solution h4 {
            color: var(--color-accent);
            margin-bottom: 0.5rem;
        }
        
        footer {
            margin-top: 3rem;
            text-align: center;
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.9rem;
            padding: 1rem;
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 6px;
        }
        
        /* Toggle functionality */
        .file-issues-content {
            display: block; /* Always show issues content */
        }
        
        /* Toggle styles removed */
        
        /* Code highlighting */
        .code-keyword {
            color: #ff79c6;
        }
        
        .code-string {
            color: #f1fa8c;
        }
        
        .code-number {
            color: #bd93f9;
        }
        
        .code-comment {
            color: #6272a4;
        }
        
        .code-function {
            color: #50fa7b;
        }
        
        .highlight-line {
            background-color: rgba(255, 121, 198, 0.1);
            display: block;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            .stats {
                grid-template-columns: 1fr;
            }
            
            .issue-header {
                flex-direction: column;
                gap: 0.5rem;
                align-items: flex-start;
            }
            
            .tools {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">
 _____               _   _        _____ _____ _____   _____                                
|_   _|             | | (_)      /  ___/  ___|  __ \\ |  __ \\                               
  | | _ __   ___ _ __| |_ _  __ _\\ `--.\\  `--.| |  \\/ | |  \\/_  __ ___ _ __  _ __   ___ _ __ 
  | || '_ \\ / _ \\ '__| __| |/ _` |`--. \\`--. \\ | __  | | __| '__/ _ \\ '_ \\| '_ \\ / _ \\ '__|
 _| || | | |  __/ |  | |_| | (_| /\\__/ /\\__/ / |_\\ \\ | |_\\ \\ | |  __/ |_) | |_) |  __/ |   
 \\___/_| |_|\\___|_|   \\__|_|\\__,_\\____/\\____/ \\____/  \\____/_|  \\___|  __/| .__/ \\___|_|   
                                                                      | |   | |              
                                                                      |_|   |_|              
        </div>
        <h1>SSR Compatibility Report</h1>
        <div class="timestamp">Generated on {{ timestamp }}</div>
        <p>This report highlights potential SSR compatibility issues in your Laravel + Inertia.js + Vue 3 application.</p>
    </header>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="value">{{ total_issues }}</div>
                <div class="label">Total Issues</div>
            </div>
            <div class="stat-card">
                <div class="value">{{ total_files }}</div>
                <div class="label">Files With Issues</div>
            </div>
            <div class="stat-card">
                <div class="value">{{ issue_types|length }}</div>
                <div class="label">Issue Types</div>
            </div>
            <div class="stat-card">
                <div class="value {{ critical_class }}">{{ severity_counts.critical or 0 }}</div>
                <div class="label critical">Critical Issues</div>
            </div>
        </div>
        
        <div class="severity-stats">
            <h3>Issues by Severity</h3>
            <table class="severity-table">
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Count</th>
                        <th>Percentage</th>
                        <th width="30%">Distribution</th>
                    </tr>
                </thead>
                <tbody>
                    {% for severity in ['critical', 'major', 'medium', 'minor'] %}
                    {% if severity_counts.get(severity, 0) > 0 %}
                    <tr>
                        <td class="{{ severity }}">{{ severity|title }}</td>
                        <td>{{ severity_counts.get(severity, 0) }}</td>
                        <td>{{ ((severity_counts.get(severity, 0) / total_issues) * 100)|round(1) }}%</td>
                        <td>
                            <div class="percentage-bar">
                                <div 
                                    class="percentage-fill {{ severity }}" 
                                    style="width: {{ ((severity_counts.get(severity, 0) / total_issues) * 100)|round }}%; background-color: var(--color-{{ severity }});">
                                </div>
                            </div>
                        </td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="type-stats">
            <h3>Top Issue Types</h3>
            <table class="type-table">
                <thead>
                    <tr>
                        <th>Issue Type</th>
                        <th>Count</th>
                        <th>Severity</th>
                    </tr>
                </thead>
                <tbody>
                    {% for issue_type, count in issue_counts|dictsort(by='value')|reverse %}
                    {% if loop.index <= 5 %}
                    <tr>
                        <td>{{ issue_type }}</td>
                        <td>{{ count }}</td>
                        <td class="{{ issue_severities[issue_type] }}">{{ issue_severities[issue_type]|title }}</td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Filters removed for simplicity -->
    
    <div class="issues">
        <h2>Detailed Issues ({{ total_issues }} total)</h2>
        
        {% for file_path, issues in files %}
        <div class="file-issues" data-severity="{{ issues|map(attribute='severity')|join(' ') }}">
            <div class="file-header">
                <h3>{{ file_path }}</h3>
                <div class="badge">{{ issues|length }} issues</div>
            </div>
            <div class="file-issues-content">
                {% for issue in issues %}
                <div class="issue" data-severity="{{ issue.severity }}">
                    <div class="issue-header">
                        <div class="issue-type">{{ issue.issue_type }}</div>
                        <div class="issue-severity {{ issue.severity }}">{{ issue.severity }}</div>
                    </div>
                    <div class="issue-location">Line {{ issue.line_number }}</div>
                    <div class="issue-message">{{ issue.message }}</div>
                    <div class="code-snippet">{{ issue.line_content }}</div>
                    {% if issue.solution %}
                    <div class="solution">
                        <h4>Solution</h4>
                        <p>{{ issue.solution }}</p>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <footer>
        <p>Generated by InertiaSSRPrepper - CLI tool for identifying SSR compatibility issues</p>
        <p class="timestamp">Report generated on {{ timestamp }}</p>
    </footer>
    
    <script type="text/javascript">
        // Initialize when the DOM is fully loaded
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM fully loaded');
            
            // Add syntax highlighting to code snippets
            const codeSnippets = document.querySelectorAll('.code-snippet');
            codeSnippets.forEach(function(snippet) {
                let content = snippet.textContent || '';
                
                // Simple syntax highlighting for JavaScript/Vue
                content = content
                    // Keywords
                    .replace(/\b(const|let|var|function|return|if|else|for|while|import|export|from|default|class|extends|try|catch|finally|throw|async|await|new)\b/g, '<span class="code-keyword">$1</span>')
                    // Strings
                    .replace(/(['"`])((?:\\\1|.)*?)\1/g, '<span class="code-string">$1$2$1</span>')
                    // Numbers
                    .replace(/\b([0-9]+)\b/g, '<span class="code-number">$1</span>')
                    // Comments
                    .replace(/(\/\/.*)/g, '<span class="code-comment">$1</span>')
                    // Functions
                    .replace(/\b([a-zA-Z_$][a-zA-Z0-9_$]*)\(/g, '<span class="code-function">$1</span>(');
                
                // Set innerHTML for syntax highlighting
                snippet.innerHTML = content;
            });
        });
    </script>
</body>
</html>
"""

def generate_html_report(issues: List[SSRIssue], output_path: Path) -> None:
    """Generate an HTML report from the issues"""
    # Group issues by file
    grouped_issues = {}
    for issue in issues:
        file_path = str(issue.file_path)
        if file_path not in grouped_issues:
            grouped_issues[file_path] = []
        grouped_issues[file_path].append(issue)
    
    # Sort files by issues count (descending)
    sorted_files = sorted(
        grouped_issues.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    # For each file, sort issues by severity and line number
    files_with_sorted_issues = []
    for file_path, file_issues in sorted_files:
        sorted_issues = sorted(
            file_issues,
            key=lambda x: (
                ['critical', 'major', 'medium', 'minor'].index(x.severity)
                if x.severity in ['critical', 'major', 'medium', 'minor'] else 999,
                x.line_number
            )
        )
        
        rel_path = os.path.relpath(file_path)
        files_with_sorted_issues.append((rel_path, sorted_issues))
    
    # Count issues by type and severity
    issue_counts = {}
    severity_counts = {'critical': 0, 'major': 0, 'medium': 0, 'minor': 0}
    issue_severities = {}
    
    for issue in issues:
        # Count by type
        if issue.issue_type not in issue_counts:
            issue_counts[issue.issue_type] = 0
        issue_counts[issue.issue_type] += 1
        
        # Count by severity
        severity_counts[issue.severity] += 1
        
        # Map issue types to severities
        issue_severities[issue.issue_type] = issue.severity
    
    # Determine if we have critical issues (for styling)
    critical_class = "critical" if severity_counts['critical'] > 0 else ""
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Render template
    template = Template(HTML_TEMPLATE)
    html_content = template.render(
        timestamp=timestamp,
        total_issues=len(issues),
        total_files=len(grouped_issues),
        issue_types=set(issue.issue_type for issue in issues),
        severity_counts=severity_counts,
        issue_counts=issue_counts,
        issue_severities=issue_severities,
        files=files_with_sorted_issues,
        critical_class=critical_class,
    )
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)