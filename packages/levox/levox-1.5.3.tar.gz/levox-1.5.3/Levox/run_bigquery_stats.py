#!/usr/bin/env python
"""
BigQuery Download Statistics Runner for Levox

Run custom BigQuery queries to analyze PyPI download statistics.
"""
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

try:
    from google.cloud import bigquery
    import pandas as pd
except ImportError:
    print("Error: Required packages not found")
    print("Please install: pip install google-cloud-bigquery pandas pandas-gbq")
    sys.exit(1)

def run_query(query: str, project_id: str = None) -> List[Dict[str, Any]]:
    """
    Run a BigQuery query and return results.
    
    Args:
        query: SQL query to execute
        project_id: Google Cloud project ID (optional)
        
    Returns:
        List of dictionaries with query results
    """
    try:
        client = bigquery.Client(project=project_id)
        query_job = client.query(query)
        results = list(query_job.result())
        
        # Convert to list of dictionaries
        return [dict(row.items()) for row in results]
        
    except Exception as e:
        print(f"Error executing query: {e}")
        return []

def run_predefined_query(name: str, package: str = "levox", days: int = 30) -> List[Dict[str, Any]]:
    """
    Run a predefined query by name.
    
    Args:
        name: Name of predefined query
        package: PyPI package name
        days: Number of days to analyze
        
    Returns:
        List of dictionaries with query results
    """
    queries = {
        "daily": f"""
            SELECT
              COUNT(*) as downloads,
              DATE(timestamp) as date
            FROM
              `bigquery-public-data.pypi.file_downloads`
            WHERE
              file.project = '{package}'
              AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
            GROUP BY
              date
            ORDER BY
              date DESC
        """,
        
        "python": f"""
            SELECT
              REGEXP_EXTRACT(details.python, r'[0-9]+\.[0-9]+') AS python_version,
              COUNT(*) AS downloads
            FROM `bigquery-public-data.pypi.file_downloads`
            WHERE
              file.project = '{package}'
              AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
              AND details.python IS NOT NULL
            GROUP BY python_version
            ORDER BY downloads DESC
            LIMIT 15
        """,
        
        "countries": f"""
            SELECT
              country_code,
              COUNT(*) as downloads
            FROM
              `bigquery-public-data.pypi.file_downloads`
            WHERE
              file.project = '{package}'
              AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
              AND country_code IS NOT NULL
            GROUP BY
              country_code
            ORDER BY
              downloads DESC
            LIMIT 20
        """,
        
        "systems": f"""
            SELECT
              details.system as system,
              COUNT(*) as downloads
            FROM
              `bigquery-public-data.pypi.file_downloads`
            WHERE
              file.project = '{package}'
              AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
              AND details.system IS NOT NULL
            GROUP BY
              system
            ORDER BY
              downloads DESC
            LIMIT 15
        """,
        
        "installers": f"""
            SELECT
              details.installer.name as installer,
              COUNT(*) as downloads
            FROM
              `bigquery-public-data.pypi.file_downloads`
            WHERE
              file.project = '{package}'
              AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
              AND details.installer.name IS NOT NULL
            GROUP BY
              installer
            ORDER BY
              downloads DESC
            LIMIT 15
        """,
        
        "versions": f"""
            SELECT
              file.version,
              COUNT(*) as downloads
            FROM
              `bigquery-public-data.pypi.file_downloads`
            WHERE
              file.project = '{package}'
              AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
            GROUP BY
              file.version
            ORDER BY
              downloads DESC
            LIMIT 20
        """,
        
        "total": f"""
            SELECT
              COUNT(*) as total_downloads
            FROM
              `bigquery-public-data.pypi.file_downloads`
            WHERE
              file.project = '{package}'
        """
    }
    
    if name not in queries:
        print(f"Error: Predefined query '{name}' not found")
        print(f"Available queries: {', '.join(queries.keys())}")
        return []
    
    return run_query(queries[name])

def display_results(results: List[Dict[str, Any]], format_type: str = "text"):
    """
    Display query results in the specified format.
    
    Args:
        results: Query results to display
        format_type: Output format (text, csv, json)
    """
    if not results:
        print("No results found")
        return
    
    if format_type == "json":
        import json
        print(json.dumps(results, indent=2, default=str))
        return
        
    if format_type == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        print(output.getvalue())
        return
    
    # Default text output
    # Get column widths
    col_widths = {}
    for result in results:
        for key, value in result.items():
            col_widths[key] = max(
                col_widths.get(key, len(str(key))),
                len(str(value))
            )
    
    # Print header
    header = " | ".join(f"{col:{col_widths[col]}}" for col in results[0].keys())
    print(header)
    print("-" * len(header))
    
    # Print rows
    for result in results:
        row = " | ".join(f"{str(val):{col_widths[key]}}" for key, val in result.items())
        print(row)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run BigQuery queries for PyPI download statistics")
    
    # Add arguments
    parser.add_argument("query", nargs="?", help="Predefined query name or path to SQL file")
    parser.add_argument("--package", "-p", default="levox", help="PyPI package name")
    parser.add_argument("--days", "-d", type=int, default=30, help="Number of days to analyze")
    parser.add_argument("--format", "-f", choices=["text", "csv", "json"], default="text", help="Output format")
    parser.add_argument("--list", "-l", action="store_true", help="List available predefined queries")
    parser.add_argument("--project", help="Google Cloud project ID")
    
    args = parser.parse_args()
    
    # List available queries
    if args.list:
        print("Available predefined queries:")
        print("  daily     - Daily download counts")
        print("  python    - Downloads by Python version")
        print("  countries - Downloads by country")
        print("  systems   - Downloads by operating system")
        print("  installers - Downloads by installer")
        print("  versions  - Downloads by package version")
        print("  total     - Total download count")
        return
    
    # Check if query is specified
    if not args.query:
        print("Error: No query specified")
        print("Run with --list to see available queries or specify a query name or SQL file")
        return
    
    # Run query
    results = None
    
    # Check if query is a file
    query_path = Path(args.query)
    if query_path.exists() and query_path.is_file():
        # Read query from file
        try:
            with open(query_path, 'r') as f:
                query = f.read()
            print(f"Running query from file: {query_path}")
            results = run_query(query, args.project)
        except Exception as e:
            print(f"Error reading query file: {e}")
            return
    else:
        # Run predefined query
        print(f"Running predefined query: {args.query}")
        print(f"Package: {args.package}, Days: {args.days}")
        results = run_predefined_query(args.query, args.package, args.days)
    
    # Display results
    if results:
        display_results(results, args.format)
        print(f"\nQuery returned {len(results)} results")

if __name__ == "__main__":
    main() 