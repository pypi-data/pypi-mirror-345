"""
Report generator for GDPR compliance scans.
"""
import os
import json
import difflib
from typing import Dict, List, Optional
from datetime import datetime
import html

def generate_text_report(issues: List[Dict], output_file: str = None) -> str:
    """
    Generate a text-based report for GDPR compliance issues.
    
    Args:
        issues: List of GDPR issues detected
        output_file: File to write the report to (optional)
    
    Returns:
        Text report as string
    """
    if not issues:
        report = "No GDPR compliance issues detected."
        return report
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"GDPR Compliance Scan Report\n"
    report += f"Generated on: {timestamp}\n"
    report += f"Total issues found: {len(issues)}\n\n"
    
    # Group issues by file
    issues_by_file = {}
    for issue in issues:
        file_path = issue["file_path"]
        if file_path not in issues_by_file:
            issues_by_file[file_path] = []
        issues_by_file[file_path].append(issue)
    
    # Generate report by file
    for file_path, file_issues in issues_by_file.items():
        report += f"File: {file_path}\n"
        report += f"  Issues: {len(file_issues)}\n"
        
        for i, issue in enumerate(file_issues, 1):
            report += f"  [{i}] Line {issue['line_number']}: {issue['description']}\n"
            report += f"      Type: {issue['issue_type']}\n"
            report += f"      Severity: {issue['severity']}\n"
            report += f"      Code: {issue['line_content'].strip()}\n"
            report += f"      Suggestion: {issue['suggestion']}\n"
            
            # Add GDPR article references
            if "article_references" in issue and issue["article_references"]:
                report += f"      Relevant GDPR Articles:\n"
                for ref in issue["article_references"]:
                    report += f"        - {ref}\n"
            
            report += "\n"
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
    
    return report

def generate_json_report(issues: List[Dict], output_file: str = None) -> str:
    """
    Generate a JSON report for GDPR compliance issues.
    
    Args:
        issues: List of GDPR issues detected
        output_file: File to write the report to (optional)
    
    Returns:
        JSON report as string
    """
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_issues": len(issues),
        "issues": issues
    }
    
    json_report = json.dumps(report_data, indent=2)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(json_report)
    
    return json_report

def generate_html_report(issues: List[Dict], output_file: str = None) -> str:
    """
    Generate an HTML report for GDPR compliance issues.
    
    Args:
        issues: List of GDPR issues detected
        output_file: File to write the report to (optional)
    
    Returns:
        HTML report as string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>GDPR Compliance Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .file-section {{
            margin-bottom: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }}
        .issue {{
            background-color: #fff;
            border-left: 4px solid #ccc;
            margin-bottom: 15px;
            padding: 10px 15px;
        }}
        .high {{
            border-left-color: #dc3545;
        }}
        .medium {{
            border-left-color: #ffc107;
        }}
        .low {{
            border-left-color: #17a2b8;
        }}
        .code {{
            font-family: monospace;
            background-color: #f1f1f1;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }}
        .suggestion {{
            margin-top: 10px;
            font-style: italic;
        }}
        .articles {{
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .article {{
            display: inline-block;
            background-color: #e9ecef;
            padding: 2px 6px;
            margin-right: 5px;
            margin-bottom: 5px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GDPR Compliance Scan Report</h1>
        
        <div class="summary">
            <p><strong>Generated on:</strong> {timestamp}</p>
            <p><strong>Total issues found:</strong> {len(issues)}</p>
        </div>
"""

    # Group issues by file
    issues_by_file = {}
    for issue in issues:
        file_path = issue["file_path"]
        if file_path not in issues_by_file:
            issues_by_file[file_path] = []
        issues_by_file[file_path].append(issue)
    
    if not issues:
        html += "<div class='summary'><p>No GDPR compliance issues detected.</p></div>"
    else:
        # Generate report by file
        for file_path, file_issues in issues_by_file.items():
            html += f"""
        <div class="file-section">
            <h2>File: {file_path}</h2>
            <p>Issues: {len(file_issues)}</p>
"""
            
            for issue in file_issues:
                severity_class = issue["severity"].lower()
                html += f"""
            <div class="issue {severity_class}">
                <h3>Line {issue['line_number']}: {issue['description']}</h3>
                <p><strong>Type:</strong> {issue['issue_type']}</p>
                <p><strong>Severity:</strong> {issue['severity']}</p>
                <div class="code">{issue['line_content'].strip()}</div>
                <div class="suggestion"><strong>Suggestion:</strong> {issue['suggestion']}</div>
"""
                # Add GDPR article references
                if "article_references" in issue and issue["article_references"]:
                    html += f"""
                <div class="articles">
                    <strong>Relevant GDPR Articles:</strong><br>
"""
                    for ref in issue["article_references"]:
                        html += f"""                    <span class="article">{ref}</span>
"""
                    html += "                </div>"
                
                html += """
            </div>
"""
            
            html += "        </div>"
    
    html += """
    </div>
</body>
</html>
"""
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(html)
    
    return html 

def generate_changes_report(issues: List[Dict], output_file: str = None) -> str:
    """
    Generate a report showing the changes made to fix GDPR compliance issues.
    
    Args:
        issues: List of GDPR issues that were fixed
        output_file: File to write the report to (optional)
    
    Returns:
        HTML report as string
    """
    if not issues:
        report = "No changes were made."
        return report
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create the HTML report structure
    html_report = f"""<!DOCTYPE html>
<html>
<head>
    <title>GDPR Compliance Changes Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .file-section {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }}
        .file-header {{
            background-color: #f1f1f1;
            padding: 10px 15px;
            border-bottom: 1px solid #ddd;
            font-weight: bold;
        }}
        .issue {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        .issue:last-child {{
            border-bottom: none;
        }}
        .diff {{
            font-family: monospace;
            white-space: pre-wrap;
            margin: 10px 0;
            overflow-x: auto;
        }}
        .diff-added {{
            background-color: #e6ffed;
            color: #22863a;
        }}
        .diff-removed {{
            background-color: #ffeef0;
            color: #cb2431;
        }}
        .issue-type {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 5px;
        }}
        .high {{
            background-color: #ffdddd;
            color: #d73a49;
        }}
        .medium {{
            background-color: #fff9c4;
            color: #b08800;
        }}
        .low {{
            background-color: #e6f4ea;
            color: #28a745;
        }}
        .articles {{
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .article {{
            display: inline-block;
            background-color: #e9ecef;
            padding: 2px 6px;
            margin-right: 5px;
            margin-bottom: 5px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <h1>GDPR Compliance Changes Report</h1>
    
    <div class="summary">
        <p><strong>Generated on:</strong> {timestamp}</p>
        <p><strong>Total issues fixed:</strong> {len(issues)}</p>
    </div>
"""
    
    # Group issues by file
    issues_by_file = {}
    for issue in issues:
        file_path = issue.get("file_path", "")
        if file_path not in issues_by_file:
            issues_by_file[file_path] = []
        issues_by_file[file_path].append(issue)
    
    # Process each file
    for file_path, file_issues in issues_by_file.items():
        if not os.path.exists(file_path):
            continue
        
        html_report += f'''
    <div class="file-section">
        <div class="file-header">{file_path}</div>
'''
        
        # Load the current content of the file
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                current_content = f.readlines()
        except Exception:
            current_content = []
        
        # Process each issue in the file
        for issue in file_issues:
            issue_type = issue.get("issue_type", "unknown")
            severity = issue.get("severity", "medium")
            description = issue.get("description", "")
            line_number = issue.get("line_number", 0)
            original_content = issue.get("line_content", "")
            remediation = issue.get("remediation", "")
            articles = issue.get("articles", [])
            
            html_report += f'''
        <div class="issue">
            <h3>
                <span class="issue-type {severity}">{severity.upper()}</span>
                Line {line_number}: {description}
            </h3>
            <p><strong>Issue Type:</strong> {issue_type.replace("_", " ").title()}</p>
'''
            
            # Generate a diff if we have both original and remediation content
            if original_content and remediation:
                # Format the diff
                original_lines = original_content.splitlines()
                remediation_lines = remediation.splitlines()
                
                diff = difflib.unified_diff(
                    original_lines,
                    remediation_lines,
                    lineterm='',
                    n=3  # Context lines
                )
                
                # Format the diff for HTML display
                diff_html = []
                for line in diff:
                    line_html = html.escape(line)
                    if line.startswith('+'):
                        diff_html.append(f'<div class="diff-added">{line_html}</div>')
                    elif line.startswith('-'):
                        diff_html.append(f'<div class="diff-removed">{line_html}</div>')
                    elif line.startswith('@@'):
                        diff_html.append(f'<div style="color:#555;">{line_html}</div>')
                    else:
                        diff_html.append(f'<div>{line_html}</div>')
                
                diff_content = "\n".join(diff_html)
                html_report += f'''
            <p><strong>Changes Made:</strong></p>
            <div class="diff">
{diff_content}
            </div>
'''
            
            # Add GDPR article references
            if articles:
                html_report += f'''
            <div class="articles">
                <strong>Relevant GDPR Articles:</strong><br>
'''
                for article in articles:
                    html_report += f'                <span class="article">{article}</span>\n'
                html_report += '            </div>\n'
            
            html_report += '        </div>\n'
        
        html_report += '    </div>\n'
    
    html_report += '''
</body>
</html>
'''
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
    
    return html_report 