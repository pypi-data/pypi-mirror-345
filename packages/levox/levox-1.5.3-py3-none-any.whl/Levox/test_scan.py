#!/usr/bin/env python
import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from tabulate import tabulate
from levox.scanner import scan, merge_issues
from levox.data_flow_analyzer import analyze_data_flows
from levox.gdpr_articles import get_articles_for_issue_type
from levox.business import explain_issue_impact, create_business_impact_report, SEVERITY_ORDER

def parse_args():
    parser = argparse.ArgumentParser(description='Test scan for GDPR compliance issues')
    parser.add_argument('file_or_dir', nargs='*', help='Files or directories to scan')
    parser.add_argument('--min-confidence', type=float, default=0.5, help='Minimum confidence threshold')
    parser.add_argument('--output', '-o', help='Output file for detailed report')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--data-flow', action='store_true', help='Run data flow analysis')
    parser.add_argument('--export-graph', help='Export data flow graph to specified file')
    return parser.parse_args()

def get_files_to_scan(paths: List[str]) -> List[str]:
    """Get all files to scan from the provided paths."""
    files_to_scan = []
    for path in paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                        files_to_scan.append(os.path.join(root, file))
        elif os.path.isfile(path):
            files_to_scan.append(path)
    return files_to_scan

def display_issues(issues: List[Dict[str, Any]]) -> None:
    """Display a summary of issues by severity and type."""
    # Group issues by severity
    severity_counts = {}
    for issue in issues:
        severity = issue.get('severity', 'UNKNOWN').upper()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Display severity counts
    print("\n=== Issue Summary by Severity ===")
    severity_rows = []
    for severity in SEVERITY_ORDER:
        if severity in severity_counts and severity_counts[severity] > 0:
            severity_rows.append([severity, severity_counts[severity]])
    print(tabulate(severity_rows, headers=["Severity", "Count"]))
    
    # Group by issue type
    type_counts = {}
    for issue in issues:
        issue_type = issue.get('issue_type', 'UNKNOWN')
        type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
    
    # Display type counts
    print("\n=== Issue Summary by Type ===")
    type_rows = []
    for issue_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        type_rows.append([issue_type, count])
    print(tabulate(type_rows, headers=["Issue Type", "Count"]))

def display_detailed_issues(issues: List[Dict[str, Any]]) -> None:
    """Display detailed information about each issue."""
    print("\n=== Detailed Issues ===")
    
    # Group issues by severity
    issues_by_severity = {}
    for issue in issues:
        severity = issue.get('severity', 'UNKNOWN').upper()
        if severity not in issues_by_severity:
            issues_by_severity[severity] = []
        issues_by_severity[severity].append(issue)
    
    # Display issues by severity
    for severity in SEVERITY_ORDER:
        if severity in issues_by_severity:
            print(f"\n--- {severity} Severity Issues ---")
            for i, issue in enumerate(issues_by_severity[severity], 1):
                print(f"\n{i}. {issue['issue_type']}")
                if 'file' in issue:
                    print(f"   File: {issue['file']}")
                if 'line' in issue:
                    print(f"   Line: {issue['line']}")
                if 'source' in issue:
                    source = issue['source']
                    print(f"   Source: {source.get('variable', 'Unknown')} in {source.get('file', 'Unknown')}:{source.get('line', 'Unknown')}")
                if 'sink' in issue:
                    sink = issue['sink']
                    print(f"   Sink: {sink.get('category', 'Unknown')} in {sink.get('file', 'Unknown')}:{sink.get('line', 'Unknown')}")
                print(f"   Description: {issue['description']}")
                print(f"   Confidence: {issue.get('confidence', 'N/A')}")
                
                # Get related GDPR articles
                articles = get_articles_for_issue_type(issue['issue_type'])
                if articles:
                    print(f"   GDPR Articles: {', '.join(articles)}")
                
                # Get business impact explanation
                impact = explain_issue_impact(issue)
                if impact:
                    print(f"   Business Impact: {impact}")
                
                # Get remediation advice
                if 'remediation' in issue:
                    print(f"   Remediation: {issue['remediation']}")

def main():
    args = parse_args()
    
    # If no files/directories provided, scan current directory
    if not args.file_or_dir:
        args.file_or_dir = ['.']
    
    # Get all files to scan
    files_to_scan = get_files_to_scan(args.file_or_dir)
    
    if not files_to_scan:
        print("No files found to scan.")
        return 1
    
    print(f"Scanning {len(files_to_scan)} files for GDPR compliance issues...")
    
    # Run the scan
    all_issues = []
    for file_path in files_to_scan:
        file_issues = scan(file_path)
        if file_issues:
            all_issues.extend(file_issues)
    
    # Run data flow analysis if requested
    if args.data_flow:
        if len(args.file_or_dir) == 1 and os.path.isdir(args.file_or_dir[0]):
            print(f"Running data flow analysis on directory: {args.file_or_dir[0]}")
            data_flow_issues = analyze_data_flows(args.file_or_dir[0], args.export_graph)
            
            # Convert data flow issues to standard format with high confidence
            for issue in data_flow_issues:
                issue['confidence'] = 0.9
                all_issues.append(issue)
        else:
            print("Warning: Data flow analysis requires a directory parameter")
    
    # Filter by confidence threshold
    filtered_issues = [issue for issue in all_issues if issue.get('confidence', 0) >= args.min_confidence]
    
    if not filtered_issues:
        print("No issues found meeting the confidence threshold.")
        return 0
    
    # Display summary
    display_issues(filtered_issues)
    
    # Display detailed issues
    display_detailed_issues(filtered_issues)
    
    # Write to output file if specified
    if args.output:
        if args.format == 'json':
            with open(args.output, 'w') as f:
                json.dump(filtered_issues, f, indent=2)
        else:
            with open(args.output, 'w') as f:
                f.write("# GDPR Compliance Report\n\n")
                f.write(f"Total issues: {len(filtered_issues)}\n\n")
                
                # Write severity summary
                f.write("## Issues by Severity\n\n")
                severity_counts = {}
                for issue in filtered_issues:
                    severity = issue.get('severity', 'UNKNOWN').upper()
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                for severity in SEVERITY_ORDER:
                    if severity in severity_counts and severity_counts[severity] > 0:
                        f.write(f"- {severity}: {severity_counts[severity]}\n")
                
                # Write type summary
                f.write("\n## Issues by Type\n\n")
                type_counts = {}
                for issue in filtered_issues:
                    issue_type = issue.get('issue_type', 'UNKNOWN')
                    type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
                
                for issue_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"- {issue_type}: {count}\n")
                
                # Write detailed issues
                f.write("\n## Detailed Issues\n\n")
                for i, issue in enumerate(filtered_issues, 1):
                    f.write(f"### {i}. {issue['issue_type']} ({issue.get('severity', 'UNKNOWN').upper()})\n\n")
                    if 'file' in issue:
                        f.write(f"- **File**: {issue['file']}\n")
                    if 'line' in issue:
                        f.write(f"- **Line**: {issue['line']}\n")
                    if 'source' in issue:
                        source = issue['source']
                        f.write(f"- **Source**: {source.get('variable', 'Unknown')} in {source.get('file', 'Unknown')}:{source.get('line', 'Unknown')}\n")
                    if 'sink' in issue:
                        sink = issue['sink']
                        f.write(f"- **Sink**: {sink.get('category', 'Unknown')} in {sink.get('file', 'Unknown')}:{sink.get('line', 'Unknown')}\n")
                    f.write(f"- **Description**: {issue['description']}\n")
                    f.write(f"- **Confidence**: {issue.get('confidence', 'N/A')}\n")
                    
                    # Write GDPR articles
                    articles = get_articles_for_issue_type(issue['issue_type'])
                    if articles:
                        f.write(f"- **GDPR Articles**: {', '.join(articles)}\n")
                    
                    # Write business impact
                    impact = explain_issue_impact(issue)
                    if impact:
                        f.write(f"- **Business Impact**: {impact}\n")
                    
                    # Write remediation
                    if 'remediation' in issue:
                        f.write(f"- **Remediation**: {issue['remediation']}\n")
                    
                    f.write("\n")
                
                # Generate business impact report
                f.write("## Business Impact Summary\n\n")
                business_report = create_business_impact_report(filtered_issues)
                f.write(business_report)
        
        print(f"\nDetailed report saved to {args.output}")
    
    # Ask if user wants remediation advice
    print("\nWould you like to see detailed remediation advice for each issue? (y/n) ", end="")
    response = input().strip().lower()
    if response == 'y':
        print("\n=== Remediation Advice ===")
        for i, issue in enumerate(filtered_issues, 1):
            print(f"\n{i}. {issue['issue_type']} ({issue.get('severity', 'UNKNOWN').upper()})")
            if 'remediation' in issue:
                print(f"   {issue['remediation']}")
            else:
                print("   No specific remediation advice available.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 