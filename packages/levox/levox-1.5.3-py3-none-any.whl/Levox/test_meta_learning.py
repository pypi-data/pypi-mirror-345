#!/usr/bin/env python
"""
Test script for the meta-learning system in Levox.

This script demonstrates how to use the meta-learning system to train on feedback
and improve GDPR compliance detection over time.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from levox.meta_learning import MetaLearningEngine
    from levox.advanced_scanner import AdvancedScanner
    from levox.scanner import GDPRIssue
except ImportError as e:
    print(f"Error importing Levox modules: {e}")
    print("Make sure you're running this script from the Levox directory.")
    sys.exit(1)

def test_meta_learning_basic():
    """Basic test of meta-learning functionality."""
    print("== Testing Meta-Learning Basic Functionality ==")
    
    # Initialize the meta-learning engine
    ml_engine = MetaLearningEngine()
    
    # Get initial stats
    stats = ml_engine.get_learning_stats()
    print(f"Initial feedback records: {stats['feedback_count']}")
    
    # Create test issue data
    test_issue = {
        'file_path': 'test_data/sample.py',
        'line_number': 42,
        'line_content': 'user_email = request.form.get("email")',
        'issue_type': 'pii_collection',
        'severity': 'medium',
        'confidence': 0.7,
    }
    
    # Record as a false positive
    print("Recording test issue as false positive...")
    ml_engine.record_feedback(test_issue, 'false_positive')
    
    # Check updated stats
    stats = ml_engine.get_learning_stats()
    print(f"Updated feedback records: {stats['feedback_count']}")
    
    return True

def test_meta_learning_with_scanner(test_dir: str):
    """Test meta-learning integration with the scanner."""
    print(f"== Testing Meta-Learning with Scanner on {test_dir} ==")
    
    if not os.path.isdir(test_dir):
        print(f"Test directory not found: {test_dir}")
        return False
    
    # Initialize the meta-learning engine
    ml_engine = MetaLearningEngine()
    
    # Get initial stats
    stats = ml_engine.get_learning_stats()
    initial_count = stats['feedback_count']
    print(f"Initial feedback records: {initial_count}")
    
    # First scan - without applying feedback yet
    print("\nRunning initial scan...")
    scanner = AdvancedScanner(
        test_dir,
        config={
            "use_enhanced_patterns": True,
            "context_sensitivity": True,
            "allowlist_filtering": True,
            "code_analysis": True,
            "use_meta_learning": False,  # Disable meta-learning for baseline
            "false_positive_threshold": 0.7
        }
    )
    
    baseline_issues = scanner.scan_directory()
    print(f"Baseline scan found {len(baseline_issues)} issues")
    
    # Mark a few issues as false positives (first 2 issues if there are any)
    if len(baseline_issues) > 0:
        print("\nMarking some issues as false positives...")
        num_to_mark = min(2, len(baseline_issues))
        
        for i in range(num_to_mark):
            issue = baseline_issues[i]
            issue_data = issue.to_dict()
            
            # Add context if possible
            try:
                with open(issue.file_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                    
                line_num = issue.line_number - 1  # Convert to 0-indexed
                start = max(0, line_num - 5)
                end = min(len(lines), line_num + 6)
                context = ''.join(lines[start:end])
                issue_data['context'] = context
            except Exception:
                pass
                
            ml_engine.record_feedback(issue_data, 'false_positive')
            print(f"Marked issue as false positive: {issue.issue_type} in {issue.file_path}:{issue.line_number}")
    
    # Update models
    print("\nUpdating meta-learning models...")
    ml_engine.update_models()
    
    # Second scan - with meta-learning enabled
    print("\nRunning scan with meta-learning enabled...")
    ml_scanner = AdvancedScanner(
        test_dir,
        config={
            "use_enhanced_patterns": True,
            "context_sensitivity": True,
            "allowlist_filtering": True,
            "code_analysis": True,
            "use_meta_learning": True,  # Enable meta-learning
            "false_positive_threshold": 0.7
        }
    )
    
    ml_issues = ml_scanner.scan_directory()
    print(f"Scan with meta-learning found {len(ml_issues)} issues")
    
    # Compare results
    print("\nComparison:")
    print(f"Baseline issues: {len(baseline_issues)}")
    print(f"Meta-learning issues: {len(ml_issues)}")
    
    if len(baseline_issues) > len(ml_issues):
        print(f"Meta-learning reduced issues by {len(baseline_issues) - len(ml_issues)} ({((len(baseline_issues) - len(ml_issues)) / len(baseline_issues) * 100):.1f}%)")
    
    # Final stats
    stats = ml_engine.get_learning_stats()
    print(f"\nFinal feedback records: {stats['feedback_count']} (added {stats['feedback_count'] - initial_count})")
    
    return True

def main():
    """Main entry point for the test script."""
    print("Levox Meta-Learning Test Script")
    print("===============================")
    
    # Test basic functionality
    test_meta_learning_basic()
    
    # Test with a scanner on a real directory
    # First try the test directory if it exists
    if os.path.isdir("tests"):
        test_meta_learning_with_scanner("tests")
    elif os.path.isdir("test"):
        test_meta_learning_with_scanner("test")
    elif len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        # Use directory provided as command line argument
        test_meta_learning_with_scanner(sys.argv[1])
    else:
        # Default to current directory but with a warning
        print("\nWarning: No test directory found. Using current directory.")
        print("For better testing, provide a test directory as an argument.")
        test_meta_learning_with_scanner(".")

if __name__ == "__main__":
    main() 