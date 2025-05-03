#!/usr/bin/env python
"""
Levox Benchmark Runner

This script allows running benchmarks for the Levox GDPR compliance tool.
It tests the scanner against various codebases to evaluate performance.
"""
import os
import sys
import argparse
from typing import List, Dict, Any

try:
    from levox.benchmark import run_benchmarks, get_benchmark_results, DEFAULT_BENCHMARKS
except ImportError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    try:
        from levox.benchmark import run_benchmarks, get_benchmark_results, DEFAULT_BENCHMARKS
    except ImportError:
        print("Error: Could not import benchmark module. Make sure Levox is installed correctly.")
        sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run GDPR compliance benchmarks for Levox")
    
    parser.add_argument("--run", action="store_true", help="Run all benchmarks")
    parser.add_argument("--show", action="store_true", help="Show latest benchmark results")
    parser.add_argument("--list", action="store_true", help="List available benchmarks")
    parser.add_argument("--name", type=str, help="Run a specific benchmark by name")
    
    return parser.parse_args()

def list_benchmarks():
    """List all available benchmarks."""
    print("Available benchmarks:")
    for i, benchmark in enumerate(DEFAULT_BENCHMARKS, 1):
        name = benchmark.get("name", "Unknown")
        desc = benchmark.get("description", "No description")
        language = benchmark.get("language", "Unknown")
        print(f"{i}. {name} ({language}) - {desc}")

def format_benchmark_results(result):
    """Format benchmark results for display."""
    if not result:
        print("No benchmark results available.")
        return
        
    print(f"\nBenchmark: {result.get('name')}")
    print(f"Repository: {result.get('repository', 'N/A')}")
    print(f"Files scanned: {result.get('files_scanned', 0):,}")
    print(f"Lines of code: {result.get('lines_scanned', 0):,}")
    print(f"Scan time: {result.get('scan_time', 0):.2f} seconds")
    print(f"Performance: {result.get('files_per_second', 0):.2f} files/second")
    print(f"Speed: {result.get('lines_per_second', 0):.2f} lines/second")
    print(f"Issues found: {result.get('issues_found', 0):,}")
    
    # Print issues by severity
    issues_by_severity = result.get('issues_by_severity', {})
    if issues_by_severity:
        print("\nIssues by severity:")
        for severity, count in issues_by_severity.items():
            print(f"  {severity.upper()}: {count}")
    
    # Print top issues by type
    top_issues = result.get('top_issues', [])
    if top_issues:
        print("\nTop issue types:")
        for issue in top_issues:
            print(f"  {issue.get('type')}: {issue.get('count')}")
            
    # Show timestamp of benchmark
    timestamp = result.get('timestamp')
    if timestamp:
        print(f"\nBenchmark run at: {timestamp}")

def run_specific_benchmark(name: str) -> bool:
    """Run a specific benchmark by name."""
    # Find the benchmark by name
    benchmark = None
    for config in DEFAULT_BENCHMARKS:
        if config.get("name", "").lower() == name.lower():
            benchmark = config
            break
            
    if not benchmark:
        print(f"Benchmark '{name}' not found. Run with --list to see available benchmarks.")
        return False
        
    print(f"Running benchmark: {benchmark.get('name')}")
    results = run_benchmarks([benchmark])
    
    if results:
        # Get the result for the specified benchmark
        benchmark_key = benchmark.get("name", "").lower().replace(" ", "_")
        if benchmark_key in results:
            format_benchmark_results(results[benchmark_key])
            return True
            
    print("Benchmark failed or returned no results.")
    return False

def main():
    """Main function for the benchmark runner."""
    args = parse_arguments()
    
    if args.list:
        list_benchmarks()
        return 0
        
    if args.name:
        run_specific_benchmark(args.name)
        return 0
        
    if args.run:
        print("Running all benchmarks...")
        run_benchmarks()
        latest = get_benchmark_results()
        format_benchmark_results(latest)
        return 0
        
    if args.show or not (args.run or args.list or args.name):
        # Default to showing latest results
        latest = get_benchmark_results()
        format_benchmark_results(latest)
        return 0
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 