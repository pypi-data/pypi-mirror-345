#!/usr/bin/env python
"""
Test script to verify the improved meta-learning and file filtering.
This script tests:
1. The quiet meta-learning option
2. Package-lock.json and other common files being filtered correctly
"""
import os
import sys
import tempfile
from pathlib import Path

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Levox modules
try:
    from levox.meta_learning import MetaLearningEngine
    from levox.advanced_scanner import AdvancedScanner
    from levox.scanner import GDPRIssue
except ImportError as e:
    print(f"Error importing Levox modules: {e}")
    sys.exit(1)

def create_test_files():
    """Create test files including package-lock.json and some code files with potential issues."""
    temp_dir = tempfile.mkdtemp(prefix="levox_test_")
    print(f"Created test directory: {temp_dir}")
    
    # Create a simple package-lock.json file that would trigger false positives
    with open(os.path.join(temp_dir, "package-lock.json"), "w") as f:
        f.write("""
{
  "name": "test-package",
  "version": "1.0.0",
  "lockfileVersion": 1,
  "requires": true,
  "dependencies": {
    "axios": {
      "version": "0.21.1",
      "resolved": "https://registry.npmjs.org/axios/-/axios-0.21.1.tgz",
      "integrity": "sha512-dKQiRHxGD9PPRIUNIWvZhPTPpl1rf/OxTYKsqKUDjBwYylTvV7SjSHJb9ratfyzM6wCdLCOYLzs73qpg5c4iGA==",
      "requires": {
        "follow-redirects": "^1.10.0"
      }
    },
    "email-validator": {
      "version": "2.0.4",
      "resolved": "https://registry.npmjs.org/email-validator/-/email-validator-2.0.4.tgz",
      "integrity": "sha512-gYCOXVKzJLTu10Jn7/ocjLhcpLzTAubXeYajBNkWiGKhDst4jVMq4nA45HvWUCNi4QKr6FUr9PaNoEuGu2zIcg=="
    },
    "user-data": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/user-data/-/user-data-1.0.0.tgz",
      "integrity": "sha512-example123456789"
    }
  }
}
        """)
    
    # Create a simple Python file with GDPR issues
    with open(os.path.join(temp_dir, "app.py"), "w") as f:
        f.write("""
# This file should be scanned and issues found
import requests
import json

# PII data collection - should be detected
def register_user(request):
    name = request.form.get('name')
    email = request.form.get('email')
    address = request.form.get('address')
    phone = request.form.get('phone')
    
    # Store user data - should be detected
    user_data = {
        'name': name,
        'email': email,
        'address': address,
        'phone': phone,
        'created_at': '2023-01-01'
    }
    
    # Send data to external API - data transfer, should be detected
    response = requests.post('https://api.example.com/users', json=user_data)
    
    if response.status_code == 200:
        return 'User registered'
    else:
        return 'Error registering user'

# No encryption for sensitive data - should be detected
def store_user_password(user_id, password):
    # BAD: Storing password without hashing
    with open(f'users/{user_id}/password.txt', 'w') as f:
        f.write(password)
        
# Application entry point
if __name__ == "__main__":
    print("Server running on port 5000")
        """)
    
    return temp_dir

def test_improved_meta_learning():
    """Test the improved meta-learning system with quiet mode."""
    print("\n== Testing Improved Meta-Learning Functionality ==")
    
    # Create test directory with files
    test_dir = create_test_files()
    
    try:
        # Initialize the meta-learning engine with quiet mode
        ml_engine = MetaLearningEngine(quiet=True)
        print("Meta-learning engine initialized in quiet mode (no extra output)")
        
        # Run a scan with the advanced scanner
        print("\nRunning scan with advanced scanner (should ignore package-lock.json)...")
        scanner = AdvancedScanner(
            test_dir,
            config={
                "use_enhanced_patterns": True,
                "context_sensitivity": True,
                "allowlist_filtering": True,
                "code_analysis": True,
                "use_meta_learning": True,
                "quiet": True  # Enable quiet mode
            }
        )
        
        issues = scanner.scan_directory()
        print(f"Scan found {len(issues)} issues")
        
        # Check that no issues were found in package-lock.json
        package_lock_issues = [i for i in issues if "package-lock.json" in i.file_path]
        py_issues = [i for i in issues if i.file_path.endswith('.py')]
        
        print(f"Issues in package-lock.json: {len(package_lock_issues)} (should be 0)")
        print(f"Issues in app.py: {len(py_issues)} (should be > 0)")
        
        # Verify success
        success = len(package_lock_issues) == 0 and len(py_issues) > 0
        print(f"\nTest {'PASSED' if success else 'FAILED'}")
        
        return success
    finally:
        # Cleanup test directory
        try:
            import shutil
            shutil.rmtree(test_dir)
            print(f"Cleaned up test directory: {test_dir}")
        except Exception as e:
            print(f"Error cleaning up: {e}")

if __name__ == "__main__":
    print("Levox Improved Meta-Learning Test")
    print("=================================")
    
    test_improved_meta_learning() 