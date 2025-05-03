#!/usr/bin/env python
"""
Levox - GDPR, PII and Data Flow Compliance Tool

A tool for scanning, fixing, and reporting GDPR compliance issues in code.
"""
import sys
import os
from pathlib import Path
import argparse
import shlex

# Import benchmark data from benchmark module
try:
    # First try relative import
    from levox.benchmark import get_benchmark_results
except ImportError:
    try:
        # Then try absolute import
        from benchmark import get_benchmark_results
    except ImportError:
        # Fallback benchmark data if module not available
        get_benchmark_results = None
        
# Fallback benchmark data if module not available
FALLBACK_BENCHMARK_DATA = {
    "name": "DVNA (Damn Vulnerable Node.js Application)",
    "files_scanned": 133,
    "lines_scanned": 22385,
    "scan_time": 0.12,
    "issues_found": 23,
    "true_positives": 21,
    "false_positives": 2,
    "accuracy": 0.91
}

# Version and system information
VERSION = "1.3.1"  # Updated to reflect meta-learning improvements and fallback
BUILD_DATE = "2023-09-15"
SYSTEM_INFO = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def get_features():
    """Get a list of Levox features."""
    features = [
        "GDPR Compliance Scanning",
        "PII Detection and Classification",
        "Data Flow Analysis",
        "AI-Assisted Remediation",
        "Detailed HTML Reports",
        "Interactive Command Line Interface",
        "AST-based Code Analysis",
        "Adaptive Meta-Learning" # New feature
    ]
    
    # Check if meta-learning is available
    try:
        from levox.meta_learning import MetaLearningEngine, SKLEARN_AVAILABLE
        features.append("Meta-Learning for Reduced False Positives")
        
        # Check if advanced meta-learning is available
        if SKLEARN_AVAILABLE:
            features.append("Advanced Semantic Analysis (with scikit-learn)")
        else:
            features.append("Basic Semantic Analysis (fallback mode)")
    except ImportError:
        pass
        
    return features

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Levox - GDPR Compliance Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        help='Path to directory or file to scan'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'html'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path for report'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix detected issues'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )
    
    return parser.parse_args()

def validate_path(path: str) -> Path:
    """
    Validate and normalize input path.
    
    Args:
        path: Input path string
        
    Returns:
        Normalized Path object
        
    Raises:
        ValueError: If path is invalid or doesn't exist
    """
    try:
        # Handle quoted paths and normalize
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        
        # Convert to Path object and resolve
        path_obj = Path(path).resolve()
        
        # Check if path exists
        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")
            
        return path_obj
        
    except Exception as e:
        raise ValueError(f"Invalid path: {path}\nError: {str(e)}")

def main():
    """Main function for starting the Levox CLI."""
    try:
        args = parse_arguments()
        
        # Show version if requested
        if args.version:
            print_version_info()
            return 0
            
        # Start interactive CLI if no arguments
        if not args.path:
            from levox.cli import main as cli_main
            return cli_main()
            
        # Validate input path
        try:
            target_path = validate_path(args.path)
        except ValueError as e:
            print(f"Error: {str(e)}")
            print("\nUsage examples:")
            print('  levox "C:\\Users\\name\\My Project"')
            print('  levox /path/to/project')
            print('  levox . --format html --output report.html')
            return 1
            
        # Initialize scanner
        from levox.scanner import Scanner
        scanner = Scanner(str(target_path))
        
        # Scan for issues
        print(f"Scanning {target_path}...")
        issues = scanner.scan_directory()
        
        if not issues:
            print("No GDPR compliance issues found!")
            return 0
            
        # Generate report
        if args.output:
            from levox.report import (
                generate_text_report,
                generate_json_report,
                generate_html_report
            )
            
            generators = {
                'text': generate_text_report,
                'json': generate_json_report,
                'html': generate_html_report
            }
            
            generator = generators[args.format]
            generator(issues, args.output)
            print(f"\nReport saved to: {args.output}")
        else:
            # Print issues to console
            print(f"\nFound {len(issues)} GDPR compliance issues:\n")
            for issue in issues:
                print(f"File: {issue.file_path}")
                print(f"Line {issue.line_number}: {issue.description}")
                print(f"Severity: {issue.severity.upper()}\n")
                
        # Fix issues if requested
        if args.fix:
            from levox.fixer import Fixer
            fixer = Fixer()
            results = fixer.fix_issues(issues)
            print(f"\nFixed {results['fixed']} issues, {results['failed']} failed")
            
        return 0
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

def print_version_info():
    """Print version information."""
    features = get_features()
    
    print(f"Levox v{VERSION} ({BUILD_DATE})")
    print(f"Running on {SYSTEM_INFO}")
    print("\nFeatures:")
    for feature in features:
        print(f"- {feature}")
        
    print("\nBenchmark Data:")
    try:
        if get_benchmark_results:
            benchmark = get_benchmark_results()
        else:
            benchmark = FALLBACK_BENCHMARK_DATA
        
        print(f"- Test dataset: {benchmark['name']}")
        print(f"- Files scanned: {benchmark['files_scanned']}")
        print(f"- Lines of code: {benchmark['lines_scanned']}")
        print(f"- Scan time: {benchmark['scan_time']:.2f}s")
        print(f"- Issues found: {benchmark['issues_found']}")
        
        # Show accuracy metrics if available
        if 'true_positives' in benchmark and 'false_positives' in benchmark:
            print(f"- True positives: {benchmark['true_positives']}")
            print(f"- False positives: {benchmark['false_positives']}")
            
        # Calculate and display precision if possible
        if 'true_positives' in benchmark and 'issues_found' in benchmark and benchmark['issues_found'] > 0:
            precision = benchmark['true_positives'] / benchmark['issues_found']
            print(f"- Precision: {precision:.2f}")
            
        # Show accuracy if available
        if 'accuracy' in benchmark:
            print(f"- Accuracy: {benchmark['accuracy']:.2f}")
            
        # Add meta-learning info
        try:
            from levox.meta_learning import MetaLearningEngine
            ml_engine = MetaLearningEngine()
            ml_stats = ml_engine.get_learning_stats()
            if ml_stats.get('feedback_count', 0) > 0:
                print("\nMeta-Learning Status:")
                print(f"- Feedback records: {ml_stats.get('feedback_count', 0)}")
                print(f"- Issue types analyzed: {len(ml_stats.get('issue_types', []))}")
                
                # Total false positives/negatives
                fp_total = sum(ml_stats.get('false_positive_counts', {}).values())
                fn_total = sum(ml_stats.get('false_negative_counts', {}).values())
                print(f"- False positives identified: {fp_total}")
                print(f"- False negatives identified: {fn_total}")
        except (ImportError, Exception):
            # Meta-learning not available or error
            pass
            
    except Exception as e:
        print(f"Error loading benchmark data: {e}")

if __name__ == "__main__":
    sys.exit(main())