#!/usr/bin/env python
"""
False Positive Manager for Levox

A utility to help manage and reduce false positives in Levox GDPR compliance scans.
"""
import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

# Try to import Levox modules
try:
    from levox.meta_learning import MetaLearningEngine
    from levox.scanner import GDPRIssue
    META_LEARNING_AVAILABLE = True
except ImportError:
    META_LEARNING_AVAILABLE = False
    print("Warning: Meta-learning module not available. Limited functionality.")

class FalsePositiveManager:
    """Manager for handling false positives in Levox scans."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the false positive manager.
        
        Args:
            data_dir: Optional directory for meta-learning data
        """
        self.meta_learning = None
        if META_LEARNING_AVAILABLE:
            try:
                self.meta_learning = MetaLearningEngine(data_dir=data_dir)
                print(f"Meta-learning initialized successfully")
            except Exception as e:
                print(f"Error initializing meta-learning: {e}")
        
        # Store allowlists
        self.file_allowlist = set()
        self.pattern_allowlist = set()
        
        # Store code context for AST and pattern analysis
        self.code_contexts = {}
        
        # Store common false positive patterns
        self.common_false_positives = {
            "consent_issues": [
                r"UserPreferences",
                r"Settings\s+",
                r"Options\s+",
                r"Configuration\s+",
                r"Preferences\s+",
                r"interface\s+.*Preferences",
                r"type\s+.*Preferences",
                r"onChange",
                r"onSubmit",
                r"form"
            ],
            "security_measures": [
                r"Token$",
                r"AmpersandToken",
                r"HashToken",
                r"SyntaxKind",
                r"[A-Z][a-z]*Token",
                r"[A-Z][a-z]*Kind"
            ],
            "code_utility": [
                r"class\s+ChangeTracker",
                r"class\s+.*Tracker",
                r"class\s+.*Manager",
                r"class\s+.*Factory",
                r"class\s+.*Builder",
                r"class\s+.*Helper"
            ]
        }
        
    def mark_all_as_false_positives(self, issues_file: str) -> int:
        """
        Mark all issues in a JSON file as false positives for training.
        
        Args:
            issues_file: Path to JSON file containing scan issues
            
        Returns:
            Number of issues marked as false positives
        """
        if not self.meta_learning:
            print("Error: Meta-learning is not available")
            return 0
            
        try:
            with open(issues_file, 'r', encoding='utf-8') as f:
                issues_data = json.load(f)
                
            if not isinstance(issues_data, list):
                if 'issues' in issues_data and isinstance(issues_data['issues'], list):
                    issues_data = issues_data['issues']
                else:
                    print(f"Error: Invalid issues format in {issues_file}")
                    return 0
            
            marked_count = 0
            for issue in issues_data:
                try:
                    result = self.meta_learning.record_feedback(issue, 'false_positive')
                    if result:
                        marked_count += 1
                except Exception as e:
                    print(f"Error marking issue as false positive: {e}")
                    
            print(f"Marked {marked_count} issues as false positives")
            
            # Update models after feedback
            self.meta_learning.update_models()
            print("Meta-learning models updated with new feedback")
            
            return marked_count
            
        except Exception as e:
            print(f"Error processing issues file: {e}")
            return 0
            
    def create_allowlist(self, issues_file: str, output_file: str = ".levoxignore") -> bool:
        """
        Create an allowlist file based on false positive patterns.
        
        Args:
            issues_file: Path to JSON file containing scan issues
            output_file: Path to output allowlist file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(issues_file, 'r', encoding='utf-8') as f:
                issues_data = json.load(f)
                
            if not isinstance(issues_data, list):
                if 'issues' in issues_data and isinstance(issues_data['issues'], list):
                    issues_data = issues_data['issues']
                else:
                    print(f"Error: Invalid issues format in {issues_file}")
                    return False
            
            # Extract file patterns and code patterns
            for issue in issues_data:
                if 'file_path' in issue:
                    file_path = issue['file_path']
                    self._add_file_pattern(file_path)
                    
                if 'line_content' in issue:
                    line_content = issue['line_content']
                    issue_type = issue.get('issue_type', '')
                    self._add_code_pattern(line_content, issue_type)
                    
                # Store code context for analysis if available
                if 'file_path' in issue and 'line_number' in issue:
                    self._store_code_context(issue)
            
            # Analyze code contexts for common false positives
            self._analyze_code_contexts()
                    
            # Write allowlist file
            self._write_allowlist(output_file)
            print(f"Allowlist created at {output_file}")
            return True
            
        except Exception as e:
            print(f"Error creating allowlist: {e}")
            return False
            
    def _store_code_context(self, issue: Dict[str, Any]) -> None:
        """Store code context for better analysis."""
        file_path = issue.get('file_path', '')
        line_number = issue.get('line_number', 0)
        context = issue.get('context', '')
        
        if not file_path or not line_number:
            return
            
        if not context and 'line_content' in issue:
            # If no context provided, use the line content
            context = issue['line_content']
            
        if file_path not in self.code_contexts:
            self.code_contexts[file_path] = {}
            
        self.code_contexts[file_path][line_number] = {
            'context': context,
            'issue_type': issue.get('issue_type', ''),
            'line_content': issue.get('line_content', '')
        }
            
    def _analyze_code_contexts(self) -> None:
        """Analyze code contexts to identify patterns of false positives."""
        for file_path, lines in self.code_contexts.items():
            for line_number, data in lines.items():
                context = data.get('context', '')
                issue_type = data.get('issue_type', '')
                
                # Check for export patterns (classes, interfaces)
                if self._is_declaration(context):
                    self._add_declaration_patterns(context)
                    
                # Check for specific false positive categories
                if issue_type in self.common_false_positives:
                    for pattern in self.common_false_positives[issue_type]:
                        if re.search(pattern, context):
                            self.pattern_allowlist.add(pattern)
                
    def _is_declaration(self, context: str) -> bool:
        """Check if the context contains a declaration."""
        declaration_patterns = [
            r'export\s+(class|interface|type|enum)',
            r'class\s+\w+',
            r'interface\s+\w+',
            r'type\s+\w+\s*=',
            r'enum\s+\w+'
        ]
        
        for pattern in declaration_patterns:
            if re.search(pattern, context):
                return True
                
        return False
        
    def _add_declaration_patterns(self, context: str) -> None:
        """Add patterns for declarations that are likely false positives."""
        # Extract class/interface/type name
        declaration_match = re.search(r'(class|interface|type|enum)\s+(\w+)', context)
        if declaration_match:
            type_kind = declaration_match.group(1)
            type_name = declaration_match.group(2)
            
            # Add the specific type name
            self.pattern_allowlist.add(f"{type_kind}\\s+{type_name}")
            
            # Check for utility classes
            suffix_patterns = ['Service', 'Helper', 'Manager', 'Factory', 'Builder', 'Tracker', 'Util']
            for suffix in suffix_patterns:
                if type_name.endswith(suffix):
                    self.pattern_allowlist.add(f"{type_kind}\\s+.*{suffix}")
            
            # Check for preference/setting classes
            preference_patterns = ['Preferences', 'Settings', 'Options', 'Config']
            for pref in preference_patterns:
                if pref in type_name:
                    self.pattern_allowlist.add(f"{type_kind}\\s+.*{pref}")
            
    def _add_file_pattern(self, file_path: str) -> None:
        """Add a file path pattern to the allowlist."""
        # Add exact file
        self.file_allowlist.add(file_path)
        
        # Add file extension
        _, ext = os.path.splitext(file_path)
        if ext and ext.startswith('.'):
            if ext in ['.min.js', '.min.css', '.bundle.js', '.json', '.md', '.svg', '.d.ts']:
                self.file_allowlist.add(f"*{ext}")
                
        # Add directory patterns
        parts = Path(file_path).parts
        for part in parts:
            if part.lower() in ['test', 'tests', 'node_modules', 'examples', 'dist', 'build', '__tests__']:
                self.file_allowlist.add(f"*/{part}/*")
                
    def _add_code_pattern(self, line_content: str, issue_type: str = '') -> None:
        """Add a code pattern to the allowlist."""
        # Add patterns that look like imports/requires
        if 'import ' in line_content or 'require(' in line_content:
            self.pattern_allowlist.add(line_content.strip())
            
        # Add patterns that look like constants
        if ' = ' in line_content and ('//' not in line_content.split(' = ')[0]):
            parts = line_content.split(' = ')
            if len(parts) >= 2 and parts[1].strip().startswith(('"', "'", '`')):
                self.pattern_allowlist.add(parts[0].strip())
                
        # Add patterns for common false positives in the specific category
        if issue_type in self.common_false_positives:
            for pattern in self.common_false_positives[issue_type]:
                if re.search(pattern, line_content):
                    self.pattern_allowlist.add(pattern)
                
    def _write_allowlist(self, output_file: str) -> None:
        """Write patterns to allowlist file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Levox allowlist file generated to reduce false positives\n")
            f.write("ignore:\n")
            
            # Write file patterns
            for pattern in sorted(self.file_allowlist):
                f.write(f"  - file: {pattern}\n")
                
            # Write code patterns
            for pattern in sorted(self.pattern_allowlist):
                # Escape quotes in the pattern
                escaped_pattern = pattern.replace('"', '\\"')
                f.write(f'  - pattern: "{escaped_pattern}"\n')
                
    def optimize_scanner_settings(self, config_file: str = None) -> bool:
        """
        Create optimized scanner settings to reduce false positives.
        
        Args:
            config_file: Optional path to write config file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create optimized settings
            settings = {
                "scan": {
                    "exclude_dirs": [
                        "node_modules", "venv", ".git", "__pycache__",
                        "dist", "build", "test", "tests", "example", "examples",
                        "types", "typings", "__tests__"
                    ],
                    "exclude_files": [
                        ".pyc", ".jpg", ".png", ".gif", ".pdf", ".min.js", ".min.css", 
                        ".bundle.js", ".md", ".svg", ".gitignore", ".lock", ".d.ts",
                        "tsconfig.json", "*.config.js", "*.config.ts"
                    ],
                    "enhanced_patterns": True,
                    "false_positive_threshold": 0.9,  # Higher threshold for precision
                    "confidence_minimum": 0.85,       # Minimum confidence level
                    "consider_non_code": False,       # Don't analyze comments, strings
                    "ignore_test_code": True,
                    "ignore_file_patterns": [
                        ".*\\.test\\..*", ".*\\.spec\\..*", ".*-test\\..*",
                        ".*\\.min\\..*", ".*\\.bundle\\..*", ".*\\.d\\.ts$"
                    ],
                    "ignore_code_patterns": list(self.pattern_allowlist) if self.pattern_allowlist else [
                        "import\\s+.*\\s+from\\s+['\"].*['\"]",
                        "require\\(['\"].*['\"]\\)",
                        "const\\s+.*\\s*=\\s*['\"].*['\"]",
                        "let\\s+.*\\s*=\\s*['\"].*['\"]",
                        "var\\s+.*\\s*=\\s*['\"].*['\"]",
                        "UserPreferences",
                        "class\\s+ChangeTracker",
                        "AmpersandToken",
                        "HashToken" 
                    ],
                    "context_sensitivity": True,      # Enable context sensitivity
                    "semantic_analysis": True,        # Enable semantic analysis
                    "use_advanced_scanner": True,     # Use advanced scanner if available
                    "max_file_size": 2097152          # 2MB max file size
                },
                "advanced": {
                    "code_analysis": True,
                    "context_lines": 10,
                    "type_inference": True,
                    "high_precision": True,
                    "exclude_exported_types": [
                        "Preferences", "UserPreferences", "Settings", "Configuration",
                        "Options", "Tracker", "Manager", "Service", "Helper", "Util"
                    ]
                }
            }
            
            # Write config file if path provided
            if config_file:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2)
                print(f"Optimized scanner settings written to {config_file}")
                
            return True
            
        except Exception as e:
            print(f"Error optimizing scanner settings: {e}")
            return False
            
    def analyze_issue_types(self, issues_file: str) -> Dict[str, Dict[str, int]]:
        """
        Analyze issue types and false positive rates.
        
        Args:
            issues_file: Path to JSON file containing scan issues
            
        Returns:
            Dictionary with issue type analysis
        """
        try:
            with open(issues_file, 'r', encoding='utf-8') as f:
                issues_data = json.load(f)
                
            if not isinstance(issues_data, list):
                if 'issues' in issues_data and isinstance(issues_data['issues'], list):
                    issues_data = issues_data['issues']
                else:
                    print(f"Error: Invalid issues format in {issues_file}")
                    return {}
            
            # Count issues by type and analyze false positive likelihood
            issue_types = {}
            for issue in issues_data:
                issue_type = issue.get('issue_type', 'unknown')
                
                if issue_type not in issue_types:
                    issue_types[issue_type] = {
                        'count': 0,
                        'false_positive_count': 0
                    }
                
                issue_types[issue_type]['count'] += 1
                
                # Estimate if this is likely a false positive
                if self._is_likely_false_positive(issue):
                    issue_types[issue_type]['false_positive_count'] += 1
            
            # Calculate false positive rates
            for issue_type, data in issue_types.items():
                if data['count'] > 0:
                    data['false_positive_rate'] = data['false_positive_count'] / data['count']
                else:
                    data['false_positive_rate'] = 0
            
            # Print summary
            total_issues = sum(data['count'] for data in issue_types.values())
            total_false_positives = sum(data['false_positive_count'] for data in issue_types.values())
            
            print("\n=== Issue Type Analysis ===")
            print(f"Total issues: {total_issues}")
            print(f"Estimated false positives: {total_false_positives} ({total_false_positives/total_issues*100:.1f}% of all issues)")
            print("\nBreakdown by issue type:")
            
            for issue_type, data in sorted(issue_types.items(), key=lambda x: x[1]['count'], reverse=True):
                print(f"  {issue_type}: {data['count']} issues, {data['false_positive_count']} false positives ({data['false_positive_rate']*100:.1f}%)")
                
            return issue_types
                
        except Exception as e:
            print(f"Error analyzing issue types: {e}")
            return {}
    
    def _is_likely_false_positive(self, issue: Dict[str, Any]) -> bool:
        """Determine if an issue is likely a false positive."""
        issue_type = issue.get('issue_type', '')
        line_content = issue.get('line_content', '')
        file_path = issue.get('file_path', '')
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() in ['.json', '.md', '.svg', '.gitignore', '.lock', '.d.ts']:
            return True
            
        # Check patterns for common false positives
        if issue_type in self.common_false_positives:
            for pattern in self.common_false_positives[issue_type]:
                if re.search(pattern, line_content):
                    return True
                    
        # Check for class/interface/type declarations
        if self._is_declaration(line_content):
            return True
            
        # Check for imports/requires
        if 'import ' in line_content or 'require(' in line_content:
            return True
        
        return False
            
def main():
    """Main entry point for the false positive manager."""
    parser = argparse.ArgumentParser(description="Manage false positives in Levox GDPR scans")
    
    parser.add_argument('--mark-all', '-m', dest='issues_file',
                        help='Mark all issues in a JSON file as false positives')
    
    parser.add_argument('--create-allowlist', '-a', dest='allowlist_source',
                        help='Create an allowlist file from issues in a JSON file')
    
    parser.add_argument('--output', '-o', dest='output_file', default='.levoxignore',
                        help='Output file for allowlist (default: .levoxignore)')
    
    parser.add_argument('--optimize-settings', '-s', dest='settings_file',
                        help='Create optimized scanner settings to reduce false positives')
                        
    parser.add_argument('--analyze', '-n', dest='analyze_file',
                        help='Analyze issue types and false positive rates')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = FalsePositiveManager()
    
    # Process arguments
    if args.issues_file:
        manager.mark_all_as_false_positives(args.issues_file)
        
    if args.allowlist_source:
        manager.create_allowlist(args.allowlist_source, args.output_file)
        
    if args.settings_file:
        manager.optimize_scanner_settings(args.settings_file)
        
    if args.analyze_file:
        manager.analyze_issue_types(args.analyze_file)
        
    # If no actions specified, print help
    if not any([args.issues_file, args.allowlist_source, args.settings_file, args.analyze_file]):
        parser.print_help()
        
if __name__ == "__main__":
    main() 