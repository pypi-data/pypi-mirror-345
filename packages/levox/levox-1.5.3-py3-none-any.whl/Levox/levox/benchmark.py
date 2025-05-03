#!/usr/bin/env python
"""
Levox Benchmarking Module

This module provides functionality to benchmark Levox's performance
against various codebases, including vulnerable and compliance-heavy ones.
"""
import os
import sys
import time
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Default benchmarks configuration
DEFAULT_BENCHMARKS = [
    {
        "name": "OWASP Benchmark Project",
        "repo": "https://github.com/OWASP-Benchmark/BenchmarkJava",
        "language": "Java",
        "description": "Security Tool Accuracy Testing",
        "scan_args": ["--rules", "security,gdpr"],
        "exclude_dirs": ["target", ".git"],
        "tags": ["security", "java", "web"]
    },
    {
        "name": "DVNA (Damn Vulnerable Node.js Application)",
        "repo": "https://github.com/ayush-sharma/dvna",
        "language": "JavaScript",
        "description": "Modern JS Framework Vulnerabilities",
        "scan_args": ["--rules", "javascript,gdpr"],
        "exclude_dirs": ["node_modules", ".git"],
        "tags": ["security", "javascript", "web"]
    },
    {
        "name": "OWASP Juice Shop",
        "repo": "https://github.com/juice-shop/juice-shop",
        "language": "TypeScript",
        "description": "Comprehensive Security Training",
        "scan_args": ["--rules", "all", "--output", "json"],
        "exclude_dirs": ["node_modules", ".git", "dist"],
        "tags": ["security", "typescript", "web"]
    },
    {
        "name": "Linux Kernel (sample)",
        "repo": "git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        "depth": 1,
        "subdirs": ["kernel", "fs"],  # Only scan specific subdirectories
        "language": "C",
        "description": "Linux Kernel Core Components",
        "scan_args": ["--rules", "c", "--max-workers", "8"],
        "exclude_dirs": ["Documentation", "tools", "scripts"],
        "tags": ["c", "system", "large-scale"]
    }
]

class BenchmarkResult:
    """Class to store and manage benchmark results."""
    
    def __init__(self, name: str, repository: str = None):
        """Initialize benchmark result with name and optional repository."""
        self.name = name
        self.repository = repository
        self.start_time = None
        self.end_time = None
        self.files_scanned = 0
        self.lines_scanned = 0
        self.scan_time = 0
        self.issues_found = 0
        self.issues_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        self.top_issues = []
        
    def start(self):
        """Mark the start time of the benchmark."""
        self.start_time = time.time()
        
    def finish(self):
        """Mark the end time and calculate scan time."""
        self.end_time = time.time()
        self.scan_time = self.end_time - self.start_time
        
    def get_files_per_second(self) -> float:
        """Calculate files processed per second."""
        if self.scan_time > 0:
            return self.files_scanned / self.scan_time
        return 0
        
    def get_lines_per_second(self) -> float:
        """Calculate lines processed per second."""
        if self.scan_time > 0:
            return self.lines_scanned / self.scan_time
        return 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the benchmark result to a dictionary."""
        files_per_second = self.get_files_per_second()
        lines_per_second = self.get_lines_per_second()
        
        return {
            "name": self.name,
            "repository": self.repository,
            "files_scanned": self.files_scanned,
            "lines_scanned": self.lines_scanned,
            "scan_time": round(self.scan_time, 2),
            "issues_found": self.issues_found,
            "issues_by_severity": self.issues_by_severity,
            "top_issues": self.top_issues[:5],  # Top 5 issues by count
            "files_per_second": round(files_per_second, 2),
            "lines_per_second": round(lines_per_second, 2),
            "timestamp": datetime.now().isoformat()
        }
        
class Benchmark:
    """Main benchmarking class for Levox."""
    
    def __init__(self, work_dir: str = None, results_file: str = None):
        """Initialize the benchmark with working directory and results file."""
        self.work_dir = work_dir or os.path.join(tempfile.gettempdir(), "levox_benchmarks")
        self.results_file = results_file or os.path.expanduser("~/.levox/benchmark_results.json")
        self.ensure_directories()
        
    def ensure_directories(self):
        """Ensure required directories exist."""
        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.results_file), exist_ok=True)
        
    def clone_repository(self, repo_url: str, target_dir: str, depth: int = None) -> bool:
        """Clone a Git repository for benchmarking."""
        try:
            cmd = ["git", "clone"]
            if depth:
                cmd.extend(["--depth", str(depth)])
            cmd.extend([repo_url, target_dir])
            
            process = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository {repo_url}: {e}")
            print(f"Error details: {e.stderr}")
            return False
        except Exception as e:
            print(f"Unexpected error cloning repository {repo_url}: {e}")
            return False
            
    def count_files_and_lines(self, directory: str, exclude_dirs: List[str] = None) -> Tuple[int, int]:
        """Count the number of files and lines in a directory."""
        exclude_dirs = exclude_dirs or []
        total_files = 0
        total_lines = 0
        
        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # Skip binary files and other non-text files
                if file.endswith(('.pyc', '.so', '.dll', '.exe', '.jpg', '.png', '.gif', '.pdf')):
                    continue
                
                file_path = os.path.join(root, file)
                total_files += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += sum(1 for _ in f)
                except Exception:
                    # Skip files that can't be read as text
                    pass
                    
        return total_files, total_lines
        
    def run_scan(self, directory: str, scan_args: List[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Run a Levox scan on the directory and return the results."""
        scan_args = scan_args or []
        results_file = os.path.join(tempfile.gettempdir(), f"levox_scan_{int(time.time())}.json")
        
        # Use a direct import of the scanner for better performance in benchmarks
        # This avoids the CLI overhead and directly uses the scanner classes
        try:
            from levox.scanner import Scanner
            from .config import Config
            
            # Setup configuration
            config = Config()
            for i in range(0, len(scan_args), 2):
                if i + 1 < len(scan_args):
                    config.set(scan_args[i].lstrip('-'), scan_args[i+1])
            
            # Run scan
            scanner = Scanner(directory)
            start_time = time.time()
            issues = scanner.scan_directory()
            end_time = time.time()
            
            # Convert issues to dictionary format
            issues_dict = [issue.to_dict() for issue in issues]
            scan_results = {
                "issues": issues_dict,
                "scan_time": end_time - start_time,
                "directory": directory,
                "config": config.settings
            }
            
            # Save results to file
            with open(results_file, 'w') as f:
                json.dump(scan_results, f)
                
            return True, scan_results
        except ImportError:
            # Fall back to CLI if direct import fails
            print("Using CLI fallback for scanning")
            cmd = [sys.executable, "-m", "levox.cli", "scan", directory, "--output", results_file, "--format", "json"]
            cmd.extend(scan_args)
            
            try:
                process = subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Parse the results file
                if os.path.exists(results_file):
                    with open(results_file, 'r') as f:
                        scan_results = json.load(f)
                    os.remove(results_file)
                    return True, scan_results
                return False, {}
                
            except subprocess.CalledProcessError as e:
                print(f"Error running scan on {directory}: {e}")
                print(f"Error details: {e.stderr}")
                return False, {}
            except Exception as e:
                print(f"Unexpected error running scan on {directory}: {e}")
                return False, {}
            
    def process_scan_results(self, result: BenchmarkResult, scan_results: Dict[str, Any]):
        """Process scan results and update the benchmark result."""
        # Count issues by severity
        issues_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        issues_by_type = {}
        
        issues = scan_results.get("issues", [])
        for issue in issues:
            severity = issue.get("severity", "medium").lower()
            issue_type = issue.get("issue_type", "unknown")
            
            if severity in issues_by_severity:
                issues_by_severity[severity] += 1
                
            if issue_type in issues_by_type:
                issues_by_type[issue_type] += 1
            else:
                issues_by_type[issue_type] = 1
                
        # Update the benchmark result
        result.issues_found = len(issues)
        result.issues_by_severity = issues_by_severity
        
        # Get top issues by count
        top_issues = []
        for issue_type, count in sorted(issues_by_type.items(), key=lambda x: x[1], reverse=True):
            top_issues.append({"type": issue_type, "count": count})
        result.top_issues = top_issues[:5]  # Top 5 issues
        
    def run_benchmark(self, benchmark_config: Dict[str, Any]) -> Optional[BenchmarkResult]:
        """Run a benchmark based on the provided configuration."""
        name = benchmark_config.get("name", "Unknown")
        repo_url = benchmark_config.get("repo")
        exclude_dirs = benchmark_config.get("exclude_dirs", [])
        scan_args = benchmark_config.get("scan_args", [])
        depth = benchmark_config.get("depth")
        subdirs = benchmark_config.get("subdirs", [])
        
        if not repo_url:
            print(f"Missing repository URL for benchmark {name}")
            return None
            
        # Create a unique directory for this benchmark
        bench_dir = os.path.join(self.work_dir, name.lower().replace(" ", "_"))
        if os.path.exists(bench_dir):
            shutil.rmtree(bench_dir)
        os.makedirs(bench_dir)
        
        # Initialize the benchmark result
        result = BenchmarkResult(name, repo_url)
        
        # Clone the repository
        print(f"Cloning repository {repo_url} for benchmark {name}...")
        if not self.clone_repository(repo_url, bench_dir, depth):
            return None
            
        # Determine which directory to scan
        scan_dir = bench_dir
        if subdirs:
            # If subdirs are specified, only count and scan those
            subdir_paths = [os.path.join(bench_dir, subdir) for subdir in subdirs]
            valid_subdirs = [path for path in subdir_paths if os.path.exists(path)]
            if valid_subdirs:
                # Count files and lines in each subdir
                total_files = 0
                total_lines = 0
                for subdir in valid_subdirs:
                    files, lines = self.count_files_and_lines(subdir, exclude_dirs)
                    total_files += files
                    total_lines += lines
                result.files_scanned = total_files
                result.lines_scanned = total_lines
                
                # For scanning, we'll use the first valid subdir or specific args
                scan_dir = valid_subdirs[0]
                scan_args.extend([subdir for subdir in valid_subdirs[1:]])
            else:
                print(f"No valid subdirectories found for benchmark {name}")
                return None
        else:
            # Count all files and lines in the repo
            files, lines = self.count_files_and_lines(bench_dir, exclude_dirs)
            result.files_scanned = files
            result.lines_scanned = lines
        
        # Run the scan
        print(f"Running Levox scan on {scan_dir}...")
        result.start()
        success, scan_results = self.run_scan(scan_dir, scan_args)
        result.finish()
        
        if success:
            self.process_scan_results(result, scan_results)
            print(f"Benchmark {name} completed successfully")
            print(f"  Files: {result.files_scanned}")
            print(f"  Lines: {result.lines_scanned}")
            print(f"  Time: {result.scan_time:.2f} seconds")
            print(f"  Speed: {result.get_files_per_second():.2f} files/second")
            print(f"  Issues: {result.issues_found}")
            return result
        else:
            print(f"Benchmark {name} failed")
            return None
        
    def run_all_benchmarks(self, configs: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run all benchmarks and return the results."""
        configs = configs or DEFAULT_BENCHMARKS
        results = {}
        
        for config in configs:
            name = config.get("name", "Unknown")
            print(f"\nRunning benchmark: {name}")
            result = self.run_benchmark(config)
            if result:
                results[name.lower().replace(" ", "_")] = result.to_dict()
                
        # Save the results
        self.save_results(results)
        return results
                
    def save_results(self, results: Dict[str, Any]):
        """Save benchmark results to a JSON file."""
        try:
            with open(self.results_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Benchmark results saved to {self.results_file}")
        except Exception as e:
            print(f"Error saving benchmark results: {e}")
            
    def load_results(self) -> Dict[str, Any]:
        """Load benchmark results from the JSON file."""
        try:
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading benchmark results: {e}")
            return {}
            
    def get_latest_benchmark(self) -> Optional[Dict[str, Any]]:
        """Get the most recent benchmark result."""
        results = self.load_results()
        if not results:
            return None
            
        # Find the benchmark with the most recent timestamp
        latest = None
        latest_time = None
        
        for name, result in results.items():
            timestamp = result.get("timestamp")
            if timestamp:
                result_time = datetime.fromisoformat(timestamp)
                if not latest_time or result_time > latest_time:
                    latest_time = result_time
                    latest = result
                    
        return latest
        
    def clean_work_directory(self):
        """Clean up the working directory."""
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
            print(f"Cleaned up working directory: {self.work_dir}")
            
def run_benchmarks(configs: List[Dict[str, Any]] = None):
    """Run benchmarks with the given configurations."""
    benchmark = Benchmark()
    try:
        results = benchmark.run_all_benchmarks(configs)
        return results
    finally:
        benchmark.clean_work_directory()
        
def get_benchmark_results() -> Dict[str, Any]:
    """Get the most recent benchmark results."""
    benchmark = Benchmark()
    latest = benchmark.get_latest_benchmark()
    if latest:
        return latest
    return {
        "name": "No benchmarks available",
        "files_scanned": 0,
        "lines_scanned": 0,
        "scan_time": 0,
        "issues_found": 0
    }
        
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        print("Running Levox benchmarks...")
        run_benchmarks()
    else:
        print("Use --run to execute benchmarks")
        latest = get_benchmark_results()
        if latest:
            print("\nLatest benchmark results:")
            print(f"Name: {latest.get('name')}")
            print(f"Files: {latest.get('files_scanned')}")
            print(f"Lines: {latest.get('lines_scanned')}")
            print(f"Time: {latest.get('scan_time')} seconds")
            print(f"Speed: {latest.get('files_per_second')} files/second")
            print(f"Issues: {latest.get('issues_found')}") 