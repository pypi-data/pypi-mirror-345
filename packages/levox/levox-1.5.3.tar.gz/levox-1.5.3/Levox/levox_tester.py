#!/usr/bin/env python
"""
Levox True Violation Detector Tester

A simple script to demonstrate the true violation detector
by creating and scanning a test file with known issues.
"""
import os
import json
import tempfile
import argparse
from pathlib import Path

# Import the detector if available, otherwise proceed without it
try:
    from true_violation_detector import TrueViolationDetector
    DETECTOR_AVAILABLE = True
except ImportError:
    DETECTOR_AVAILABLE = False
    print("Warning: true_violation_detector.py not found or importable.")


# Sample files with various GDPR issues to test detection
SAMPLE_FILES = {
    "mixed_file.js": """
// File with mixed true and false positive GDPR issues

// False positive: Just a class definition, no actual GDPR issue
export class ChangeTracker {
    constructor() {
        this.changes = [];
    }
    
    trackChange(change) {
        this.changes.push(change);
    }
}

// False positive: Security implementation, not a vulnerability
function generateDjb2Hash(str) {
    let hash = 5381;
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) + hash) + str.charCodeAt(i);
    }
    return hash;
}

// False positive: Type definition, not an actual issue
interface UserPreferences {
    notifications: boolean;
    marketing: boolean;
    tracking: boolean;
}

// Real issue: No opt-out in cookie consent
function setCookieBanner() {
    const banner = document.createElement('div');
    banner.innerHTML = `
        <h2>Cookie Notice</h2>
        <p>We use cookies to enhance your experience.</p>
        <button>Accept</button>
    `;
    // Missing reject/opt-out button
    document.body.appendChild(banner);
}

// Real issue: Child data without age verification
function saveChildProfile(childName, age, interests) {
    // No age verification or parental consent
    localStorage.setItem('child_profile', JSON.stringify({
        name: childName,
        age: age,
        interests: interests
    }));
}

// Real issue: User data without deletion mechanism
class UserAccount {
    constructor(username, email) {
        this.username = username;
        this.email = email;
    }
    
    saveProfile() {
        localStorage.setItem('user_profile', JSON.stringify(this));
    }
    
    // Missing deletion method
}
""",

    "model.py": """
# Python model with GDPR issues

from database import db

class UserModel:
    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone
    
    def save(self):
        db.save(self)
    
    # Missing delete method for GDPR compliance

def store_child_data(name, age, parent_email):
    # No age verification or parental consent verification
    child_data = {
        "name": name,
        "age": age,
        "parent_email": parent_email
    }
    db.child_collection.insert(child_data)
"""
}

def create_test_files(directory):
    """Create test files in the given directory."""
    for filename, content in SAMPLE_FILES.items():
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created test file: {file_path}")
    
    # Create improved_rules.json if it doesn't exist
    rules_path = os.path.join(directory, "improved_rules.json")
    if not os.path.exists(rules_path):
        with open(rules_path, 'w', encoding='utf-8') as f:
            json.dump({
                "severity_adjustments": {
                    "rules": [
                        {
                            "match_pattern": "generateDjb2Hash|createHash|hashFunction",
                            "match_type": "function",
                            "current_issue_type": "security_measures",
                            "current_severity": "medium",
                            "action": "ignore",
                            "reason": "Hashing functions are security implementations, not vulnerabilities"
                        },
                        {
                            "match_pattern": "Tracker$|Tracker\\(",
                            "match_type": "class",
                            "current_issue_type": "consent_issues",
                            "current_severity": "high",
                            "action": "ignore",
                            "reason": "Compiler internals for type checking"
                        }
                    ]
                },
                "detection_improvements": {
                    "new_rules": [
                        {
                            "name": "cookie_banner_without_optout",
                            "pattern": "cookie(Banner|Consent|Notice).*(!opt-out|!reject|acceptOnly|accept-only)",
                            "issue_type": "consent_issues",
                            "severity": "high",
                            "articles": ["7.3", "7.4"],
                            "description": "Cookie consent without clear opt-out option"
                        }
                    ]
                }
            }, f, indent=2)
        print(f"Created improved rules file: {rules_path}")
    
    return directory

def run_detector(directory):
    """Run the true violation detector on the test files."""
    if not DETECTOR_AVAILABLE:
        print("Error: Cannot run detector. Make sure true_violation_detector.py is in the current directory.")
        return
    
    detector = TrueViolationDetector()
    issues = detector.scan_directory(directory)
    
    # Display results
    print("\n--- Scan Results ---")
    detector.print_summary()
    
    # Save report
    report_path = os.path.join(directory, "true_violations.json")
    detector.generate_report(report_path)
    print(f"\nReport saved to: {report_path}")

def main():
    """Main function for the tester."""
    parser = argparse.ArgumentParser(description="Test the Levox true violation detector")
    parser.add_argument('--dir', help="Directory to create test files in (default: temporary directory)")
    args = parser.parse_args()
    
    if args.dir:
        test_dir = args.dir
        os.makedirs(test_dir, exist_ok=True)
    else:
        # Create a temporary directory
        test_dir = tempfile.mkdtemp(prefix="levox_test_")
    
    # Create test files
    create_test_files(test_dir)
    
    # Run the detector if available
    if DETECTOR_AVAILABLE:
        run_detector(test_dir)
    else:
        print("\nTo run the detector:")
        print(f"1. Copy true_violation_detector.py to the current directory")
        print(f"2. Run: python true_violation_detector.py {test_dir}")

if __name__ == "__main__":
    main() 