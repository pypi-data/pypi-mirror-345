#!/usr/bin/env python
"""
Debug script to test scanner operation
"""
import os
from levox.scanner import Scanner, GDPRIssue
try:
    from levox.advanced_scanner import AdvancedScanner
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False

print("==== GDPR Scanner Debug Test ====")
print(f"Advanced scanner available: {ADVANCED_AVAILABLE}")

# Check if examples directory exists
if not os.path.exists("examples"):
    print("Error: examples directory not found")
    exit(1)

# Run basic scanner first
print("\n== Running Basic Scanner ==")
basic_scanner = Scanner("examples")
basic_issues = basic_scanner.scan_directory()
print(f"Basic scanner found {len(basic_issues)} issues")

if not basic_issues:
    print("No issues found with basic scanner, please check example files")
else:
    print(f"Issues by severity:")
    high = [i for i in basic_issues if i.severity == "high"]
    medium = [i for i in basic_issues if i.severity == "medium"]
    low = [i for i in basic_issues if i.severity == "low"]
    print(f"HIGH: {len(high)} | MEDIUM: {len(medium)} | LOW: {len(low)}")

if ADVANCED_AVAILABLE:
    # Run advanced scanner
    print("\n== Running Advanced Scanner ==")
    advanced_scanner = AdvancedScanner(
        "examples", 
        config={
            "use_enhanced_patterns": True,
            "context_sensitivity": True,
            "allowlist_filtering": False,  # Disable allowlist filtering for testing
            "code_analysis": True,
            "false_positive_threshold": 0.5,  # Very lenient for debugging
            "min_confidence": 0.3,           # Very lenient for debugging 
            "max_context_lines": 10,
        }
    )
    advanced_issues = advanced_scanner.scan_directory()
    
    print(f"Advanced scanner found {len(advanced_issues)} issues")
    
    # Show all issues with confidence
    print("\nIssues with confidence scores:")
    for issue in advanced_issues:
        confidence = getattr(issue, 'confidence', 'N/A')
        print(f"{issue.issue_type} ({issue.severity}) - {os.path.basename(issue.file_path)}:{issue.line_number} - Confidence: {confidence}")
    
    # Filter for high confidence issues
    high_confidence = [i for i in advanced_issues if getattr(i, 'confidence', 0) > 0.8]
    print(f"\nHigh confidence issues: {len(high_confidence)}")
    
    # Display a few high confidence issues in detail
    if high_confidence:
        print("\nSample high confidence issues:")
        for issue in high_confidence[:3]:  # Show up to 3 examples
            print("\n" + issue.format_violation())

print("\n== Test Complete ==") 