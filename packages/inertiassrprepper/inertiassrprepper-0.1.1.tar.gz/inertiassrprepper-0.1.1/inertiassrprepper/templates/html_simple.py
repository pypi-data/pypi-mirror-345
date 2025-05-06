"""
Simple HTML template for the report with minimal JavaScript
"""
import os
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

from jinja2 import Template

from inertiassrprepper.scanner.scanner import SSRIssue

SIMPLE_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSR Compatibility Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: #1e1e2e;
            color: #cdd6f4;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.5;
        }
        
        h1, h2, h3, h4 {
            color: #89b4fa;
        }
        
        header {
            text-align: center;
            margin-bottom: 2rem;
            background-color: rgba(137, 180, 250, 0.1);
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid rgba(137, 180, 250, 0.2);
        }
        
        .summary {
            background-color: rgba(137, 180, 250, 0.1);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(137, 180, 250, 0.2);
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
        
        .file-section {
            margin-bottom: 1.5rem;
            border: 1px solid rgba(137, 180, 250, 0.2);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .file-header {
            background-color: rgba(137, 180, 250, 0.1);
            padding: 1rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .file-issues {
            display: none;
            padding: 1rem;
            background-color: rgba(0, 0, 0, 0.2);
        }
        
        .issue {
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem 0;
        }
        
        .issue:last-child {
            border-bottom: none;
        }
        
        .issue-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        
        .issue-type {
            font-weight: bold;
        }
        
        .critical { color: #f38ba8; }
        .major { color: #fab387; }
        .medium { color: #f9e2af; }
        .minor { color: #a6e3a1; }
        
        .issue-severity {
            font-size: 0.8rem;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            text-transform: uppercase;
            font-weight: bold;
        }
        
        .issue-severity.critical { background-color: rgba(243, 139, 168, 0.2); }
        .issue-severity.major { background-color: rgba(250, 179, 135, 0.2); }
        .issue-severity.medium { background-color: rgba(249, 226, 175, 0.2); }
        .issue-severity.minor { background-color: rgba(166, 227, 161, 0.2); }
        
        .issue-location {
            font-family: monospace;
            font-size: 0.9rem;
            color: #89dceb;
            margin-bottom: 0.5rem;
        }
        
        .issue-message {
            margin-bottom: 1rem;
            border-left: 3px solid #89dceb;
            padding-left: 0.75rem;
        }
        
        .code-snippet {
            background-color: rgba(0, 0, 0, 0.3);
            border-radius: 4px;
            padding: 0.75rem;
            margin-bottom: 1rem;
            overflow-x: auto;
            font-family: monospace;
            font-size: 0.85rem;
            line-height: 1.4;
        }
        
        .solution {
            background-color: rgba(166, 227, 161, 0.1);
            border-left: 3px solid #a6e3a1;
            padding: 0.75rem;
            border-radius: 0 4px 4px 0;
        }
        
        .solution h4 {
            color: #a6e3a1;
            margin-bottom: 0.5rem;
        }
        
        .badge {
            background-color: #f38ba8;
            color: #1e1e2e;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        
        th {
            text-align: left;
            padding: 0.75rem;
            background-color: rgba(0, 0, 0, 0.3);
        }
        
        td {
            padding: 0.75rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        footer {
            margin-top: 3rem;
            text-align: center;
            padding: 1rem;
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 6px;
        }
    </style>
</head>
<body>
    <header>
        <h1>SSR Compatibility Report</h1>
        <p>Generated on {{ timestamp }}</p>
        <p>This report highlights potential SSR compatibility issues in your Laravel + Inertia.js + Vue 3 application.</p>
    </header>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="stats">
            <div class="stat-card">
                <h3>{{ total_issues }}</h3>
                <p>Total Issues</p>
            </div>
            <div class="stat-card">
                <h3>{{ total_files }}</h3>
                <p>Files With Issues</p>
            </div>
            <div class="stat-card">
                <h3>{{ issue_types|length }}</h3>
                <p>Issue Types</p>
            </div>
            <div class="stat-card">
                <h3 class="critical">{{ severity_counts.critical or 0 }}</h3>
                <p>Critical Issues</p>
            </div>
        </div>
        
        <h3>Issues by Severity</h3>
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
                {% for severity in ['critical', 'major', 'medium', 'minor'] %}
                {% if severity_counts.get(severity, 0) > 0 %}
                <tr>
                    <td class="{{ severity }}">{{ severity|title }}</td>
                    <td>{{ severity_counts.get(severity, 0) }}</td>
                    <td>{{ ((severity_counts.get(severity, 0) / total_issues) * 100)|round(1) }}%</td>
                </tr>
                {% endif %}
                {% endfor %}
            </tbody>
        </table>
        
        <h3>Top Issue Types</h3>
        <table>
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
    
    <div class="issues">
        <h2>Detailed Issues ({{ total_issues }} total)</h2>
        
        {% for file_path, issues in files %}
        <div class="file-section" id="file-{{ loop.index }}">
            <div class="file-header" onclick="toggleFile('file-{{ loop.index }}')">
                <h3>{{ file_path }}</h3>
                <div class="badge">{{ issues|length }} issues</div>
            </div>
            <div class="file-issues" id="issues-file-{{ loop.index }}">
                {% for issue in issues %}
                <div class="issue">
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
    </footer>
    
    <script>
        // Simple toggle function with no dependencies
        function toggleFile(fileId) {
            const issuesElement = document.getElementById('issues-' + fileId);
            if (issuesElement) {
                if (issuesElement.style.display === 'block') {
                    issuesElement.style.display = 'none';
                } else {
                    issuesElement.style.display = 'block';
                }
            }
        }
        
        // Initialize by showing critical issues
        document.addEventListener('DOMContentLoaded', function() {
            {% for file_path, issues in files %}
            {% set hasCritical = false %}
            {% for issue in issues %}
            {% if issue.severity == 'critical' %}
            {% set hasCritical = true %}
            {% endif %}
            {% endfor %}
            {% if hasCritical %}
            document.getElementById('issues-file-{{ loop.index }}').style.display = 'block';
            {% endif %}
            {% endfor %}
            
            // If no critical issues, show the first file
            {% set hasAnyCritical = false %}
            {% for file_path, issues in files %}
            {% for issue in issues %}
            {% if issue.severity == 'critical' %}
            {% set hasAnyCritical = true %}
            {% endif %}
            {% endfor %}
            {% endfor %}
            
            {% if not hasAnyCritical and files|length > 0 %}
            document.getElementById('issues-file-1').style.display = 'block';
            {% endif %}
        });
    </script>
</body>
</html>
"""

def generate_simple_html_report(issues: List[SSRIssue], output_path: Path) -> None:
    """Generate a simple HTML report from the issues"""
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
    template = Template(SIMPLE_HTML_TEMPLATE)
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