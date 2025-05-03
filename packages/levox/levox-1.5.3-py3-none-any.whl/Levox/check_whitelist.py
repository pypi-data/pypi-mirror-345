#!/usr/bin/env python
"""
Whitelist Verification Tool for Levox

A simple utility to verify that the GDPR_WHITELIST is working correctly.
"""
import os
import sys
import json
from pathlib import Path

try:
    from true_violation_detector import TrueViolationDetector, GDPR_WHITELIST
    DETECTOR_AVAILABLE = True
except ImportError:
    DETECTOR_AVAILABLE = False
    print("Error: true_violation_detector.py not found in the current directory.")
    sys.exit(1)

WHITELISTED_CODE = {
    "whitelist_test.js": """
// Code that contains items from the whitelist - should be ignored
export class ChangeTracker {
    constructor() {
        this.changes = {};
    }
    
    trackChanges() {
        console.log('Tracking changes');
    }
}

// This should be ignored
interface UserPreferences {
    notifications: boolean;
    tracking: boolean;
}

// Compiler internals - should be ignored
const SymbolTracker = new TrackerFactory();
const ampersand = AmpersandToken.create();

// Security implementation - should be ignored
function generateHash(data) {
    return crypto.createHash('sha256').update(data).digest('hex');
}
""",

    "whitelist_test.ts": """
// TypeScript code with whitelist items

// This token type should be ignored
export type AmpersandToken = {
    kind: SyntaxKind.AmpersandToken;
};

// This symbol tracker class should be ignored
export class SymbolTracker implements ISymbolTracker {
    private symbols = new Map<string, Symbol>();
    
    trackSymbol(name: string, symbol: Symbol): void {
        this.symbols.set(name, symbol);
    }
}

// This user preferences interface should be ignored
export interface UserPreferences {
    theme: string;
    tracking: boolean;
    notifications: boolean;
}
"""
}

def create_test_files(directory):
    """Create test files with whitelisted items."""
    os.makedirs(directory, exist_ok=True)
    
    for filename, content in WHITELISTED_CODE.items():
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created test file: {file_path}")
    
    return directory

def test_whitelist(directory):
    """Test the whitelist functionality."""
    print(f"\nTesting whitelist functionality...")
    print(f"Hardcoded whitelist items: {sorted(GDPR_WHITELIST)}")
    
    # Create a detector
    detector = TrueViolationDetector()
    
    # Load rules from improved_rules.json if it exists
    try:
        with open("improved_rules.json", "r") as f:
            rules = json.load(f)
            fp_tokens = rules.get("false_positive_tokens", [])
            print(f"Additional false positive tokens from rules: {sorted(fp_tokens)}")
    except FileNotFoundError:
        print("Note: improved_rules.json not found. Only using hardcoded whitelist.")
    
    print(f"Combined whitelist items: {sorted(detector.whitelist)}")
    
    # Scan the test directory
    issues = detector.scan_directory(directory)
    
    # Check results
    if issues:
        print(f"\n❌ Whitelist not working correctly!")
        print(f"Found {len(issues)} issues that should have been ignored:")
        
        for i, issue in enumerate(issues, 1):
            line = issue.get("line_content", "").strip()
            file = Path(issue.get("file_path", "")).name
            print(f"  {i}. In {file}: {line}")
            
        # Find which whitelisted items were not caught
        all_content = "\n".join(WHITELISTED_CODE.values())
        missed_items = []
        
        for item in detector.whitelist:
            if item in all_content and any(item in issue.get("line_content", "") for issue in issues):
                missed_items.append(item)
                
        if missed_items:
            print(f"\nWhitelisted items that were missed: {missed_items}")
    else:
        print(f"\n✅ Whitelist working correctly!")
        print(f"All whitelisted items were ignored as expected.")
    
    print("\nNote: If whitelist isn't working, check these potential issues:")
    print("1. Make sure whitelist is applied correctly in is_false_positive()")
    print("2. Verify the case sensitivity in whitelist comparisons")
    print("3. Ensure whitelist items are also checked in _apply_severity_adjustments()")

def main():
    """Main function."""
    import tempfile
    
    # Create a temporary directory for test files
    test_dir = tempfile.mkdtemp(prefix="levox_whitelist_test_")
    print(f"Created test directory: {test_dir}")
    
    # Create test files with whitelist items
    create_test_files(test_dir)
    
    # Test the whitelist functionality
    test_whitelist(test_dir)

if __name__ == "__main__":
    main() 