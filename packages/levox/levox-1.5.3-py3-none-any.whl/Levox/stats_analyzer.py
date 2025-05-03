#!/usr/bin/env python
"""
PyPI Statistics Analyzer for Levox
Fetches and analyzes download and usage statistics from PyPI.
"""
import os
import json
import datetime
from typing import Dict, List, Any, Optional, Tuple
import requests
from collections import defaultdict
from pathlib import Path

# Configure matplotlib for non-GUI environments
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot
import matplotlib.pyplot as plt

# Optional imports for BigQuery (will handle if not available)
BIGQUERY_AVAILABLE = False
try:
    from google.cloud import bigquery
    import pandas as pd
    BIGQUERY_AVAILABLE = True
except ImportError:
    pass

class LevoxStatsAnalyzer:
    """Analyzer for Levox PyPI statistics."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the stats analyzer.
        
        Args:
            cache_dir: Directory to cache downloaded stats
        """
        self.package_name = "levox"
        self.base_url = "https://pypistats.org/api/packages"  # Updated URL
        self.pypi_url = "https://pypi.org/pypi/levox/json"
        
        # Set up cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".levox" / "stats"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize BigQuery client if available
        self.bigquery_client = None
        if BIGQUERY_AVAILABLE:
            try:
                self.bigquery_client = bigquery.Client()
            except Exception as e:
                print(f"Note: BigQuery client initialization failed: {e}")
                print("To use BigQuery, set up Google Cloud credentials.")
    
    def get_total_downloads(self) -> int:
        """Get total downloads for all time."""
        try:
            # Try BigQuery first if available
            if self.bigquery_client:
                try:
                    query = f"""
                    SELECT COUNT(*) as total_downloads
                    FROM `bigquery-public-data.pypi.file_downloads`
                    WHERE file.project = '{self.package_name}'
                    """
                    query_job = self.bigquery_client.query(query)
                    results = list(query_job.result())
                    if results and len(results) > 0:
                        total = results[0]['total_downloads']
                        return total
                except Exception as e:
                    print(f"BigQuery error: {e}")
            
            # First try the overall stats
            url = f"{self.base_url}/{self.package_name}/overall"
            response = self._make_request(url)
            
            if response and isinstance(response, dict):
                if "data" in response and isinstance(response["data"], dict):
                    # Sum all download counts (last_day, last_week, last_month)
                    total = sum(v for k, v in response["data"].items())
                    if total > 0:
                        return total
            
            # If no data from overall stats, try recent downloads
            url = f"{self.base_url}/{self.package_name}/recent"
            response = self._make_request(url)
            
            if response and isinstance(response, dict):
                if "data" in response and isinstance(response["data"], list):
                    # Sum all recent downloads
                    total = sum(entry["downloads"] for entry in response["data"] 
                              if isinstance(entry, dict) and "downloads" in entry)
                    return total
                elif "error" in response:
                    print(f"API Error: {response['error']}")
                    
            # If still no data, try direct PyPI API
            response = requests.get(
                self.pypi_url,
                headers={'Accept': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if "info" in data:
                    # PyPI doesn't provide download counts directly anymore
                    # But we can check if the package exists
                    print("\nNote: Package exists on PyPI but download statistics are not available.")
                    print("PyPI no longer provides direct download counts. Using BigQuery for historical data.")
                    return 0
            
            print("\nWarning: Could not fetch download statistics. The package may not exist or the API may be unavailable.")
            return 0
            
        except Exception as e:
            print(f"Error getting total downloads: {e}")
            return 0
        
    def get_daily_downloads(self, days: int = 30) -> Dict[str, int]:
        """
        Get daily download counts for the specified number of days.
        
        Args:
            days: Number of days to fetch
            
        Returns:
            Dictionary mapping dates to download counts
        """
        try:
            # Try BigQuery first if available
            if self.bigquery_client:
                try:
                    query = f"""
                    SELECT
                      COUNT(*) as downloads,
                      DATE(timestamp) as date
                    FROM
                      `bigquery-public-data.pypi.file_downloads`
                    WHERE
                      file.project = '{self.package_name}'
                      AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                    GROUP BY
                      date
                    ORDER BY
                      date
                    """
                    query_job = self.bigquery_client.query(query)
                    results = list(query_job.result())
                    
                    if results:
                        downloads = {str(row['date']): row['downloads'] for row in results}
                        return downloads
                        
                except Exception as e:
                    print(f"BigQuery error: {e}")
            
            # Fall back to PyPI Stats API
            url = f"{self.base_url}/{self.package_name}/recent"
            response = self._make_request(url)
            
            downloads = {}
            if response and isinstance(response, dict):
                if "data" in response and isinstance(response["data"], list):
                    for entry in response["data"]:
                        if isinstance(entry, dict) and "date" in entry and "downloads" in entry:
                            downloads[entry["date"]] = entry["downloads"]
                elif "error" in response:
                    print(f"API Error: {response['error']}")
            
            # Sort by date and return the last 'days' entries
            sorted_downloads = dict(sorted(downloads.items()))
            return dict(list(sorted_downloads.items())[-days:])
        except Exception as e:
            print(f"Error getting daily downloads: {e}")
            return {}
        
    def get_python_versions(self) -> Dict[str, int]:
        """Get download counts by Python version."""
        try:
            # Try BigQuery first if available
            if self.bigquery_client:
                try:
                    query = f"""
                    SELECT
                      details.python as python_version,
                      COUNT(*) as downloads
                    FROM
                      `bigquery-public-data.pypi.file_downloads`
                    WHERE
                      file.project = '{self.package_name}'
                      AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
                      AND details.python IS NOT NULL
                    GROUP BY
                      python_version
                    ORDER BY
                      downloads DESC
                    """
                    query_job = self.bigquery_client.query(query)
                    results = list(query_job.result())
                    
                    if results:
                        versions = {}
                        for row in results:
                            python_version = row['python_version']
                            # Extract major.minor version
                            if python_version:
                                import re
                                match = re.search(r'(\d+\.\d+)', python_version)
                                if match:
                                    version = match.group(1)
                                    versions[version] = versions.get(version, 0) + row['downloads']
                                else:
                                    versions[python_version] = row['downloads']
                        return versions
                        
                except Exception as e:
                    print(f"BigQuery error: {e}")
            
            # Fall back to PyPI Stats API
            url = f"{self.base_url}/{self.package_name}/python_major"
            response = self._make_request(url)
            
            versions = {}
            if response and isinstance(response, dict):
                if "data" in response and isinstance(response["data"], list):
                    for entry in response["data"]:
                        if isinstance(entry, dict) and "python" in entry and "downloads" in entry:
                            version = entry["python"]
                            if version != "null":  # Skip null/unknown versions
                                versions[version] = entry["downloads"]
                elif "error" in response:
                    print(f"API Error: {response['error']}")
            return versions
        except Exception as e:
            print(f"Error getting Python versions: {e}")
            return {}
        
    def get_system_stats(self) -> Dict[str, int]:
        """Get download counts by operating system."""
        try:
            # Try BigQuery first if available
            if self.bigquery_client:
                try:
                    query = f"""
                    SELECT
                      details.system as system,
                      COUNT(*) as downloads
                    FROM
                      `bigquery-public-data.pypi.file_downloads`
                    WHERE
                      file.project = '{self.package_name}'
                      AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
                      AND details.system IS NOT NULL
                    GROUP BY
                      system
                    ORDER BY
                      downloads DESC
                    """
                    query_job = self.bigquery_client.query(query)
                    results = list(query_job.result())
                    
                    if results:
                        systems = {row['system']: row['downloads'] for row in results}
                        return systems
                        
                except Exception as e:
                    print(f"BigQuery error: {e}")
            
            # Fall back to PyPI Stats API
            url = f"{self.base_url}/{self.package_name}/system"
            response = self._make_request(url)
            
            systems = {}
            if response and isinstance(response, dict):
                if "data" in response and isinstance(response["data"], list):
                    for entry in response["data"]:
                        if isinstance(entry, dict) and "system" in entry and "downloads" in entry:
                            system = entry["system"]
                            if system != "null":  # Skip null/unknown systems
                                systems[system] = entry["downloads"]
                elif "error" in response:
                    print(f"API Error: {response['error']}")
            return systems
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {}
    
    def get_country_downloads(self) -> Dict[str, int]:
        """Get download counts by country."""
        try:
            if not self.bigquery_client:
                print("BigQuery client not available - country data requires BigQuery")
                return {}
                
            query = f"""
            SELECT
              country_code,
              COUNT(*) as downloads
            FROM
              `bigquery-public-data.pypi.file_downloads`
            WHERE
              file.project = '{self.package_name}'
              AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
              AND country_code IS NOT NULL
            GROUP BY
              country_code
            ORDER BY
              downloads DESC
            LIMIT 20
            """
            query_job = self.bigquery_client.query(query)
            results = list(query_job.result())
            
            if results:
                countries = {row['country_code']: row['downloads'] for row in results}
                return countries
            
            return {}
        except Exception as e:
            print(f"Error getting country downloads: {e}")
            return {}
    
    def get_installer_stats(self) -> Dict[str, int]:
        """Get download counts by installer (pip, conda, etc.)."""
        try:
            if not self.bigquery_client:
                print("BigQuery client not available - installer data requires BigQuery")
                return {}
                
            query = f"""
            SELECT
              details.installer.name as installer,
              COUNT(*) as downloads
            FROM
              `bigquery-public-data.pypi.file_downloads`
            WHERE
              file.project = '{self.package_name}'
              AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
              AND details.installer.name IS NOT NULL
            GROUP BY
              installer
            ORDER BY
              downloads DESC
            """
            query_job = self.bigquery_client.query(query)
            results = list(query_job.result())
            
            if results:
                installers = {row['installer']: row['downloads'] for row in results}
                return installers
            
            return {}
        except Exception as e:
            print(f"Error getting installer stats: {e}")
            return {}

    def _make_request(self, url: str) -> Optional[Dict]:
        """Make a cached request to the API."""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.datetime.now().timestamp() - cache_file.stat().st_mtime
            if cache_age < 3600:  # Cache valid for 1 hour
                try:
                    with cache_file.open('r') as f:
                        return json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Error reading cache file: {e}")
                except Exception as e:
                    print(f"Unexpected error reading cache: {e}")
        
        # Make request
        try:
            headers = {
                'User-Agent': 'Levox-Stats-Analyzer/1.0',
                'Accept': 'application/json'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            try:
                data = response.json()
                
                # Debug logging
                print(f"\nAPI Response for {url.split('/')[-1]}:")
                print(f"Status: {response.status_code}")
                if isinstance(data, dict):
                    if "error" in data:
                        print(f"Error: {data['error']}")
                    else:
                        print("Success!")
                
                # Cache the response
                with cache_file.open('w') as f:
                    json.dump(data, f)
                    
                return data
                
            except json.JSONDecodeError as e:
                print(f"Error parsing API response: {e}")
                print(f"Response content: {response.text[:200]}...")
                
        except requests.RequestException as e:
            print(f"Error making request to {url}: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            
        return None
        
    def _get_cache_key(self, url: str) -> str:
        """Generate a cache key from URL."""
        return url.split('/')[-2] + '_' + url.split('/')[-1]
        
    def generate_text_report(self) -> str:
        """Generate a text-based report of statistics."""
        report = []
        report.append("=== Levox PyPI Statistics Report ===\n")
        
        # Total downloads
        total = self.get_total_downloads()
        report.append(f"Total Downloads: {total:,}\n")
        
        # Daily downloads (last 7 days)
        daily = self.get_daily_downloads(days=7)
        if daily:
            report.append("Download Trends (Last 7 days):")
            for date, count in daily.items():
                report.append(f"  {date}: {count:,}")
            report.append("")
        
        # Python versions
        versions = self.get_python_versions()
        if versions:
            report.append("Python Version Distribution:")
            for version, count in sorted(versions.items()):
                report.append(f"  Python {version}: {count:,} downloads")
            report.append("")
        
        # Operating systems
        systems = self.get_system_stats()
        if systems:
            report.append("Operating System Distribution:")
            for system, count in sorted(systems.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {system}: {count:,} downloads")
            report.append("")
        
        # Countries (BigQuery only)
        if self.bigquery_client:
            countries = self.get_country_downloads()
            if countries:
                report.append("Top Countries:")
                for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
                    report.append(f"  {country}: {count:,} downloads")
                report.append("")
            
            # Installers (BigQuery only)
            installers = self.get_installer_stats()
            if installers:
                report.append("Installer Distribution:")
                for installer, count in sorted(installers.items(), key=lambda x: x[1], reverse=True):
                    report.append(f"  {installer}: {count:,} downloads")
                report.append("")
        
        return "\n".join(report)
    
    def run_bigquery(self, query: str) -> List[Dict]:
        """
        Run a custom BigQuery query.
        
        Args:
            query: SQL query to execute
            
        Returns:
            List of dictionaries with query results
        """
        if not self.bigquery_client:
            print("BigQuery client not available. Install google-cloud-bigquery and set up credentials.")
            return []
            
        try:
            query_job = self.bigquery_client.query(query)
            results = list(query_job.result())
            
            # Convert to list of dictionaries
            return [dict(row.items()) for row in results]
            
        except Exception as e:
            print(f"Error executing BigQuery: {e}")
            return []

def main():
    """Main entry point."""
    try:
        print("Generating Levox statistics report...")
        analyzer = LevoxStatsAnalyzer()
        
        # Check if BigQuery is available
        if not BIGQUERY_AVAILABLE:
            print("\nNote: BigQuery functionality not available. Install google-cloud-bigquery for full statistics.")
            print("Run: pip install google-cloud-bigquery pandas pandas-gbq")
        elif analyzer.bigquery_client is None:
            print("\nNote: BigQuery client not configured. Set up Google Cloud credentials for full statistics.")
            print("See: https://cloud.google.com/docs/authentication/getting-started")
        
        # Generate and print text report
        report = analyzer.generate_text_report()
        print("\n" + report)
        
        # Example of running custom query if BigQuery is available
        if analyzer.bigquery_client:
            print("\n=== Sample BigQuery Queries ===")
            print("\nDownloads by Python version:")
            query = """
            SELECT
              REGEXP_EXTRACT(details.python, r'[0-9]+\.[0-9]+') AS python_version,
              COUNT(*) AS downloads
            FROM `bigquery-public-data.pypi.file_downloads`
            WHERE
              file.project = 'levox'
              AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
              AND details.python IS NOT NULL
            GROUP BY python_version
            ORDER BY downloads DESC
            LIMIT 10
            """
            results = analyzer.run_bigquery(query)
            for row in results:
                print(f"  Python {row['python_version']}: {row['downloads']:,} downloads")
        
    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    main() 