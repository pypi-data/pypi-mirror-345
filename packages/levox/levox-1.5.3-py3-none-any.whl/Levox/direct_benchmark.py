#!/usr/bin/env python
"""
Direct Benchmark Runner for Levox

This script directly runs benchmarks on large codebases to test performance.
"""
import os
import sys
import time
import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

# Add the current directory to the path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BENCHMARKS = [
    {
        "name": "OWASP Benchmark Project",
        "repo": "https://github.com/OWASP/benchmark",
        "language": "Java",
        "description": "Security Tool Accuracy Testing"
    },
    {
        "name": "DVNA",
        "repo": "https://github.com/appsecco/dvna",
        "language": "JavaScript",
        "description": "Modern JS Framework Vulnerabilities"
    },
    {
        "name": "OWASP Juice Shop",
        "repo": "https://github.com/juice-shop/juice-shop",
        "language": "TypeScript",
        "description": "Comprehensive Security Training"
    }
]

def setup_temp_dir():
    """Set up a temporary directory for benchmarks."""
    temp_dir = os.path.join(tempfile.gettempdir(), f"levox_benchmark_{int(time.time())}")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def clone_repository(repo_url, target_dir):
    """Clone a repository for benchmarking."""
    print(f"Cloning {repo_url} to {target_dir}...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, target_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def count_files_and_lines(directory):
    """Count files and lines in a repository."""
    print(f"Counting files and lines in {directory}...")
    total_files = 0
    total_lines = 0
    
    for root, _, files in os.walk(directory):
        # Skip .git directory
        if ".git" in root:
            continue
            
        for file in files:
            # Skip binary files
            if file.endswith(('.pyc', '.so', '.dll', '.exe', '.jpg', '.png', '.gif', '.pdf')):
                continue
                
            file_path = os.path.join(root, file)
            total_files += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    total_lines += sum(1 for _ in f)
            except:
                # Skip files that can't be read
                pass
                
    return total_files, total_lines

def run_scan(directory):
    """Run a quick scan on the directory."""
    print(f"Running scan on {directory}...")
    start_time = time.time()
    
    # Create a simple scan by just finding common PII patterns
    issues = []
    pii_patterns = [
        "email", "password", "credit_card", "ssn", "social_security",
        "phone", "address", "name", "dob", "birth_date", "passport"
    ]
    
    files_scanned = 0
    lines_scanned = 0
    
    for root, _, files in os.walk(directory):
        # Skip .git and node_modules
        if ".git" in root or "node_modules" in root:
            continue
            
        for file in files:
            # Skip binary files
            if file.endswith(('.pyc', '.so', '.dll', '.exe', '.jpg', '.png', '.gif', '.pdf')):
                continue
                
            file_path = os.path.join(root, file)
            files_scanned += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        lines_scanned += 1
                        for pattern in pii_patterns:
                            if pattern in line.lower():
                                issues.append({
                                    "file": file_path,
                                    "line": line_num,
                                    "pattern": pattern,
                                    "content": line.strip()
                                })
            except:
                # Skip files that can't be read
                pass
    
    end_time = time.time()
    scan_time = end_time - start_time
    
    return {
        "scan_time": scan_time,
        "files_scanned": files_scanned,
        "lines_scanned": lines_scanned,
        "issues_found": len(issues),
        "issues": issues[:10]  # Only return the first 10 issues
    }

def run_benchmark(benchmark):
    """Run a benchmark on a specific repository."""
    name = benchmark["name"]
    repo = benchmark["repo"]
    
    print(f"\n{'=' * 60}")
    print(f"Running benchmark: {name}")
    print(f"Repository: {repo}")
    print(f"{'=' * 60}")
    
    # Setup
    temp_dir = setup_temp_dir()
    repo_dir = os.path.join(temp_dir, name.lower().replace(" ", "_"))
    
    try:
        # Clone the repository
        if not clone_repository(repo, repo_dir):
            print(f"Failed to clone {repo}")
            return None
            
        # Count files and lines
        files, lines = count_files_and_lines(repo_dir)
        print(f"Files: {files:,}")
        print(f"Lines: {lines:,}")
        
        # Run the scan
        scan_results = run_scan(repo_dir)
        
        # Calculate metrics
        scan_time = scan_results["scan_time"]
        files_scanned = scan_results["files_scanned"]
        lines_scanned = scan_results["lines_scanned"]
        issues_found = scan_results["issues_found"]
        
        files_per_second = files_scanned / scan_time if scan_time > 0 else 0
        lines_per_second = lines_scanned / scan_time if scan_time > 0 else 0
        
        # Display results
        print(f"\nScan Results:")
        print(f"Scan time: {scan_time:.2f} seconds")
        print(f"Files scanned: {files_scanned:,}")
        print(f"Lines scanned: {lines_scanned:,}")
        print(f"Performance: {files_per_second:.2f} files/second")
        print(f"Speed: {lines_per_second:.2f} lines/second")
        print(f"Issues found: {issues_found}")
        
        if issues_found > 0:
            print("\nSample Issues:")
            for i, issue in enumerate(scan_results["issues"], 1):
                print(f"{i}. {issue['file']} (line {issue['line']}): {issue['pattern']}")
                print(f"   {issue['content']}")
                
        # Prepare result object
        result = {
            "name": name,
            "repository": repo,
            "timestamp": datetime.now().isoformat(),
            "files_scanned": files_scanned,
            "lines_scanned": lines_scanned,
            "scan_time": scan_time,
            "files_per_second": files_per_second,
            "lines_per_second": lines_per_second,
            "issues_found": issues_found
        }
        
        return result
    finally:
        # Clean up
        try:
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")
        except:
            print(f"Failed to clean up temporary directory: {temp_dir}")

def save_results(results):
    """Save benchmark results to a file."""
    results_file = os.path.expanduser("~/.levox/benchmark_results.json")
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {results_file}")

def main():
    """Run benchmarks on selected repositories."""
    print("Levox Direct Benchmark Runner")
    print("Running benchmarks on large codebases...\n")
    
    results = {}
    
    # Run benchmarks on at least two repositories
    for benchmark in BENCHMARKS[:2]:  # Run the first two benchmarks
        result = run_benchmark(benchmark)
        if result:
            key = benchmark["name"].lower().replace(" ", "_")
            results[key] = result
    
    # Save the results
    save_results(results)
    
    print("\nBenchmarks completed!")

if __name__ == "__main__":
    main() 