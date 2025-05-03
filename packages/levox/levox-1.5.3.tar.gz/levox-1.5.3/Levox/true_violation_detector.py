#!/usr/bin/env python
"""
True Violation Detector for Levox

Enhanced detector that finds real GDPR violations while avoiding false positives.
Specifically addresses severity mismanagement, article misalignment, and blind spots.
"""
import os
import re
import json
import ast
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set

try:
    from levox.scanner import GDPRIssue
    from levox.meta_learning import MetaLearningEngine
    LEVOX_AVAILABLE = True
except ImportError:
    LEVOX_AVAILABLE = False
    print("Warning: Levox modules not available. Running in standalone mode.")
    
# Technical whitelist for known false positives
GDPR_WHITELIST = [  
    'UserPreferences', 'ChangeTracker',  
    'SymbolTracker', 'AmpersandToken'  
]

# JavaScript/TypeScript patterns for AST-like analysis when full parsing is unavailable
JS_PATTERNS = {
    'local_storage_set': re.compile(r'localStorage\.(set(Item)?|put)\s*\(\s*[\'"](\w+)[\'"]'),
    'cookie_set': re.compile(r'(document\.cookie\s*=|setCookie\()'),
    'data_collection': re.compile(r'(collect|gather|fetch)(User|Personal|Customer|Client)Data'),
    'age_verification': re.compile(r'(verify|check|confirm|validate)(Age|Adult|Parent|Guardian)'),
    'data_deletion': re.compile(r'(delete|remove|erase)(User|Personal|Account|Data|Profile)'),
    'consent_banner': re.compile(r'(consent|cookie|gdpr|privacy)(Banner|Notice|Dialog|Modal|Popup)'),
    'tracking_function': re.compile(r'(track|monitor|log)(User|Visit|Activity|Behavior|Analytics)'),
}

# GDPR articles and their core requirements
GDPR_ARTICLES = {
    '6': 'Lawfulness of processing',
    '7': 'Conditions for consent',
    '8': 'Conditions applicable to child\'s consent',
    '9': 'Processing of special categories of personal data',
    '12': 'Transparent information, communication',
    '15': 'Right of access by the data subject',
    '17': 'Right to erasure (right to be forgotten)',
    '25': 'Data protection by design and by default',
    '32': 'Security of processing',
    '35': 'Data protection impact assessment',
}

class TrueViolationDetector:
    """Enhanced detector for finding real GDPR violations with minimal false positives."""
    
    def __init__(self, rules_file: Optional[str] = None):
        """
        Initialize the detector with custom rules.
        
        Args:
            rules_file: Optional path to custom rules JSON file
        """
        self.rules = self._load_rules(rules_file or "improved_rules.json")
        self.issues = []
        self.file_cache = {}
        self.scanned_files = 0
        self.scanned_lines = 0
        self.excluded_patterns = self._compile_excluded_patterns()
        self.whitelist = set(self._get_default_whitelist())
        self.whitelist.update(self.rules.get("false_positive_tokens", []))
        
    def _get_default_whitelist(self) -> Set[str]:
        """Get default whitelist of tokens that should not trigger violations."""
        return {
            # Type system and compiler related
            'TypeChecker', 'CompilerOptions', 'InterfaceType', 'TypeReference',
            'TokenFactory', 'SyntaxKind', 'NodeFlags', 'SymbolFlags',
            # Test related
            'MockTracker', 'TestUser', 'FakeData', 'DummyConsent',
            # Common variable names that don't indicate PII
            'index', 'count', 'total', 'length', 'size', 'key', 'value',
            # Security implementations
            'hashPassword', 'encryptData', 'validateToken', 'verifySignature'
        }
        
    def _load_rules(self, rules_file: str) -> Dict[str, Any]:
        """Load rules from JSON file or use default rules."""
        try:
            if os.path.exists(rules_file):
                with open(rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load rules file {rules_file}: {e}")
            
        # Default rules if file not available
        return {
            "severity_adjustments": {"rules": []},
            "article_mappings": {"corrections": []},
            "detection_improvements": {"new_rules": []},
            "false_positive_tokens": [],
            "severity_criteria": {
                "high": [],
                "medium": [],
                "low": []
            }
        }
        
    def _compile_excluded_patterns(self) -> List[re.Pattern]:
        """Compile patterns for false positives to exclude."""
        patterns = [
            # Code constructs
            re.compile(r'(import|require)\s+.*'),
            re.compile(r'export\s+(default\s+)?(class|interface|type|enum)\s+'),
            re.compile(r'(class|interface|type|enum)\s+\w+'),
            # Test fixtures
            re.compile(r'(test|spec|fixture|mock|stub|fake|dummy)'),
            # Hashing functions
            re.compile(r'(hash|encrypt|decrypt|sign|verify|salt)'),
            # Variable declarations without functionality
            re.compile(r'(const|let|var)\s+\w+\s*=\s*[\'"][^\'"]*[\'"]'),
            # Type declarations
            re.compile(r'(interface|type)\s+\w+Preferences'),
        ]
        return patterns
        
    def is_false_positive(self, line: str, context: str = "") -> bool:
        """
        Determine if the line is a likely false positive.
        
        Args:
            line: Source code line to check
            context: Additional context (surrounding lines)
            
        Returns:
            True if likely a false positive, False otherwise
        """
        # Check against whitelist
        for item in self.whitelist:
            if item in line:
                return True

        for pattern in self.excluded_patterns:
            if pattern.search(line):
                return True
                
        # Check for type definitions and declarations
        if re.search(r'(interface|type|class)\s+\w+', line) and not re.search(r'new\s+\w+', line):
            # It's a declaration, not instantiation
            return True
            
        # Check for security implementation vs security issue
        if re.search(r'(security|secure|protect|hash)', line):
            # If this is implementing security, not violating it
            if not re.search(r'(bypass|skip|ignore|disable)', line):
                return True
                
        return False
        
    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan a single file for GDPR violations.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            List of detected issues
        """
        file_issues = []
        
        try:
            # Skip binary or large files
            if self._should_skip_file(file_path):
                return []
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            self.file_cache[file_path] = content.splitlines()
            self.scanned_files += 1
            self.scanned_lines += len(self.file_cache[file_path])
            
            # Determine file type
            file_type = self._get_file_type(file_path)
            
            # Scan for violations based on file type
            if file_type in ('js', 'ts', 'jsx', 'tsx'):
                file_issues.extend(self._scan_javascript_file(file_path, content))
            elif file_type == 'py':
                file_issues.extend(self._scan_python_file(file_path, content))
            else:
                file_issues.extend(self._scan_generic_file(file_path, content))
                
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
            
        # Apply severity adjustments from rules
        self._apply_severity_adjustments(file_issues)
        
        return file_issues
        
    def _apply_severity_adjustments(self, issues: List[Dict[str, Any]]) -> None:
        """Apply severity adjustments based on rules."""
        for rule in self.rules.get("severity_adjustments", {}).get("rules", []):
            pattern = rule.get("match_pattern", "")
            if not pattern:
                continue
                
            compiled_pattern = re.compile(pattern)
            
            for issue in issues:
                line_content = issue.get("line_content", "")
                if compiled_pattern.search(line_content):
                    if rule.get("action") == "ignore":
                        # Mark for removal
                        issue["_remove"] = True
                    elif rule.get("action") == "adjust":
                        # Adjust severity
                        issue["severity"] = rule.get("new_severity", issue.get("severity"))
                        issue["issue_type"] = rule.get("new_issue_type", issue.get("issue_type"))

                # Also check if line contains whitelisted terms
                for item in self.whitelist:
                    if item in line_content:
                        issue["_remove"] = True
                        break
                        
        # Remove issues marked for removal
        for i in range(len(issues) - 1, -1, -1):
            if issues[i].get("_remove", False):
                issues.pop(i)
    
    def _should_skip_file(self, file_path: str) -> bool:
        """Determine if a file should be skipped."""
        # Skip large files
        try:
            if os.path.getsize(file_path) > 5 * 1024 * 1024:  # 5MB
                return True
        except:
            return True  # Skip if can't get file size
            
        # Skip binary files
        _, ext = os.path.splitext(file_path)
        if ext.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.ttf', '.bin'):
            return True
            
        # Skip node_modules, dist, etc.
        skip_dirs = ['node_modules', 'dist', 'build', '.git', '__pycache__']
        for skip_dir in skip_dirs:
            if skip_dir in Path(file_path).parts:
                return True
                
        return False
    
    def _get_file_type(self, file_path: str) -> str:
        """Get the file type based on extension."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in ('.js', '.jsx', '.mjs'):
            return 'js'
        elif ext in ('.ts', '.tsx'):
            return 'ts'
        elif ext == '.py':
            return 'py'
        elif ext in ('.html', '.htm'):
            return 'html'
        elif ext in ('.css', '.scss', '.sass', '.less'):
            return 'css'
        elif ext in ('.json', '.yaml', '.yml'):
            return 'config'
        else:
            return 'other'
            
    def _scan_javascript_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Scan JavaScript/TypeScript file for violations with improved accuracy."""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Skip comments and empty lines
            if line.strip().startswith('//') or not line.strip():
                continue
                
            # Skip if line matches whitelist patterns
            if self.is_false_positive(line):
                continue
                
            # Check for cookie consent without opt-out
            cookie_match = re.search(r'(?i)(cookie|consent|gdpr)', line)
            if cookie_match:
                # Check for opt-out options in surrounding context
                has_optout = self._check_context(lines, i, 
                                             re.compile(r'(?i)(opt.?out|reject|decline|deny|refuse)'), 
                                             radius=10)
                if not has_optout:
                    issues.append(self._create_issue(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line,
                        issue_type="consent_without_optout",
                        severity="high",
                        description="Cookie consent mechanism without clear opt-out option",
                        articles=["7.3", "7.4"],
                        context=self._get_context(lines, i, radius=2)
                    ))
            
            # Check for child data without age verification
            child_data_match = re.search(r'(?i)(child|minor|underage|young)', line)
            if child_data_match:
                # Look for age verification in broader context
                has_verification = self._check_context(lines, i,
                                                   re.compile(r'(?i)(verify|check|validate).*(age|parent|guardian)'),
                                                   radius=20)
                if not has_verification:
                    issues.append(self._create_issue(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line,
                        issue_type="child_data_without_verification",
                        severity="high",
                        description="Processing of child's data without age verification",
                        articles=["8.1", "8.2"],
                        context=self._get_context(lines, i, radius=2)
                    ))
            
            # Check for tracking without consent
            tracking_match = re.search(r'(?i)(track|monitor|analytic).*user', line)
            if tracking_match:
                has_consent = self._check_context(lines, i,
                                              re.compile(r'(?i)(consent|permission|authorize)'),
                                              radius=15)
                if not has_consent:
                    issues.append(self._create_issue(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line,
                        issue_type="tracking_without_consent",
                        severity="high",
                        description="User tracking without explicit consent",
                        articles=["7.1"],
                        context=self._get_context(lines, i, radius=2)
                    ))
                    
        return issues
    
    def _scan_python_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Scan Python file for violations using AST analysis."""
        issues = []
        
        try:
            tree = ast.parse(content)
            visitor = GDPRVisitor(file_path)
            visitor.visit(tree)
            issues.extend(visitor.issues)
        except SyntaxError:
            # Fallback to line-by-line analysis if AST parsing fails
            return self._scan_generic_file(file_path, content)
            
        return issues
    
    def _scan_generic_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Scan any file using generic patterns."""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Skip if it's a false positive
            if self.is_false_positive(line):
                continue
                
            # Check for potential PII markers
            if re.search(r'(personal|sensitive|private).*data', line, re.IGNORECASE):
                issues.append({
                    "file_path": file_path,
                    "line_number": line_num,
                    "line_content": line,
                    "issue_type": "potential_pii",
                    "severity": "medium",
                    "description": "Potential reference to personal data",
                    "articles": ["5", "6"],
                    "context": self._get_context(lines, i, radius=2)
                })
                
            # Add additional GDPR-specific detection rules
            self._check_custom_detection_rules(file_path, line, line_num, issues, content=content)
                
        return issues
    
    def _check_custom_detection_rules(self, file_path: str, line: str, line_num: int, 
                                       issues: List[Dict[str, Any]], content: str = "") -> None:
        """Apply custom detection rules from the rule file."""
        for rule in self.rules.get("detection_improvements", {}).get("new_rules", []):
            pattern = rule.get("pattern", "")
            if not pattern:
                continue
                
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            
            if compiled_pattern.search(line):
                # Check for negative pattern (condition that makes this not a violation)
                negative_pattern = rule.get("negative_pattern")
                if negative_pattern and re.search(negative_pattern, content, re.IGNORECASE):
                    continue
                    
                # Check if context is required
                if rule.get("context_required", False):
                    # Add as a potential issue - needs human review
                    severity = "low"
                else:
                    severity = rule.get("severity", "medium")
                    
                issues.append({
                    "file_path": file_path,
                    "line_number": line_num,
                    "line_content": line,
                    "issue_type": rule.get("issue_type", "gdpr_issue"),
                    "severity": severity,
                    "description": rule.get("description", "Potential GDPR issue"),
                    "articles": rule.get("articles", []),
                    "context": self._get_context(content.splitlines() if content else [], line_num - 1, radius=2)
                })
    
    def _check_context(self, lines: List[str], current_line: int, pattern: re.Pattern, 
                      radius: int = 10) -> bool:
        """Check surrounding context for a pattern with improved accuracy."""
        start = max(0, current_line - radius)
        end = min(len(lines), current_line + radius + 1)
        
        context = '\n'.join(lines[start:end])
        return bool(pattern.search(context))
    
    def _get_context(self, lines: List[str], current_line: int, radius: int = 2) -> str:
        """Get surrounding context lines for an issue."""
        start = max(0, current_line - radius)
        end = min(len(lines), current_line + radius + 1)
        return '\n'.join(lines[start:end])
    
    def _create_issue(self, **kwargs) -> Dict[str, Any]:
        """Create a standardized issue dictionary."""
        return {
            "file_path": kwargs.get("file_path"),
            "line_number": kwargs.get("line_number"),
            "line_content": kwargs.get("line_content"),
            "issue_type": kwargs.get("issue_type"),
            "severity": kwargs.get("severity"),
            "description": kwargs.get("description"),
            "articles": kwargs.get("articles", []),
            "context": kwargs.get("context", ""),
            "confidence": kwargs.get("confidence", 0.8)
        }
    
    def scan_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Scan a directory recursively for GDPR violations.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of issues found
        """
        issues = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_issues = self.scan_file(file_path)
                issues.extend(file_issues)
                
        self.issues = issues
        return issues
    
    def generate_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a report of the issues found.
        
        Args:
            output_file: Optional file to write report to
            
        Returns:
            Dictionary with report data
        """
        # Group issues by type
        issues_by_type = {}
        for issue in self.issues:
            issue_type = issue.get("issue_type", "unknown")
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
            
        # Group issues by severity
        issues_by_severity = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        for issue in self.issues:
            severity = issue.get("severity", "low")
            issues_by_severity[severity].append(issue)
            
        # Build report
        report = {
            "summary": {
                "total_issues": len(self.issues),
                "high_severity": len(issues_by_severity["high"]),
                "medium_severity": len(issues_by_severity["medium"]),
                "low_severity": len(issues_by_severity["low"]),
                "files_scanned": self.scanned_files,
                "lines_scanned": self.scanned_lines,
                "issues_by_type": {k: len(v) for k, v in issues_by_type.items()}
            },
            "issues_by_severity": issues_by_severity,
            "issues_by_type": issues_by_type,
            "all_issues": self.issues
        }
        
        # Write report to file if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2)
                print(f"Report written to {output_file}")
            except Exception as e:
                print(f"Error writing report: {e}")
                
        return report
    
    def print_summary(self) -> None:
        """Print a summary of the issues found."""
        if not self.issues:
            print("No GDPR violations found!")
            return
            
        # Group by severity
        high = [i for i in self.issues if i.get("severity") == "high"]
        medium = [i for i in self.issues if i.get("severity") == "medium"]
        low = [i for i in self.issues if i.get("severity") == "low"]
        
        print(f"\nFound {len(self.issues)} GDPR violations:")
        print(f"  HIGH: {len(high)}")
        print(f"  MEDIUM: {len(medium)}")
        print(f"  LOW: {len(low)}")
        
        # Group by issue type
        issues_by_type = {}
        for issue in self.issues:
            issue_type = issue.get("issue_type", "unknown")
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
            
        print("\nIssues by type:")
        for issue_type, issues in sorted(issues_by_type.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {issue_type}: {len(issues)}")
            
        print("\nTop 5 high severity issues:")
        for i, issue in enumerate(high[:5]):
            print(f"  {i+1}. {issue.get('description')} [{issue.get('file_path')}:{issue.get('line_number')}]")
            print(f"     Articles: {', '.join(issue.get('articles', []))}")
            print(f"     {issue.get('line_content', '').strip()}")
            print()


class GDPRVisitor(ast.NodeVisitor):
    """AST visitor to find GDPR violations in Python code."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []
        self.class_context = None
        self.function_context = None
        self.in_data_handling = False
        
    def visit_ClassDef(self, node):
        """Visit a class definition."""
        old_context = self.class_context
        self.class_context = node.name
        
        # Look for data model classes
        if any(base.id == 'Model' for base in node.bases if isinstance(base, ast.Name)):
            # Check for delete method
            has_delete = any(method.name in ('delete', 'remove', 'erase') 
                           for method in node.body if isinstance(method, ast.FunctionDef))
            
            if not has_delete and self._contains_personal_data(node):
                self.issues.append({
                    "file_path": self.file_path,
                    "line_number": node.lineno,
                    "line_content": f"class {node.name}(...)",
                    "issue_type": "missing_data_deletion",
                    "severity": "high",
                    "description": "Data model without deletion method",
                    "articles": ["17.1", "17.2"]
                })
        
        # Continue with class body
        for child in node.body:
            self.visit(child)
            
        self.class_context = old_context
    
    def visit_FunctionDef(self, node):
        """Visit a function definition."""
        old_context = self.function_context
        self.function_context = node.name
        
        # Check for data handling functions
        if any(data_term in node.name.lower() for data_term in 
              ('user', 'profile', 'account', 'personal', 'data', 'store', 'save')):
            self.in_data_handling = True
            
            # Check for age verification in functions that might handle child data
            if 'child' in node.name.lower() or 'kid' in node.name.lower() or 'minor' in node.name.lower():
                has_verification = self._has_age_verification(node)
                if not has_verification:
                    self.issues.append({
                        "file_path": self.file_path,
                        "line_number": node.lineno,
                        "line_content": f"def {node.name}(...)",
                        "issue_type": "missing_age_verification",
                        "severity": "high",
                        "description": "Child data handling without age verification",
                        "articles": ["8.1", "8.2"]
                    })
        
        # Continue with function body
        for child in node.body:
            self.visit(child)
            
        self.function_context = old_context
        self.in_data_handling = False
    
    def visit_Call(self, node):
        """Visit a function call."""
        # Check for localStorage-like operations
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ('set', 'setItem', 'put', 'store', 'save'):
                # This is a storage operation
                if len(node.args) >= 1:
                    arg = node.args[0]
                    if isinstance(arg, ast.Str) and ('child' in arg.s.lower() or 'kid' in arg.s.lower()):
                        # Check if we're in a context with age verification
                        has_verification = self.in_data_handling and self._has_age_verification_nearby(node)
                        if not has_verification:
                            self.issues.append({
                                "file_path": self.file_path,
                                "line_number": node.lineno,
                                "line_content": f"{node.func.attr}({arg.s}, ...)",
                                "issue_type": "missing_age_verification",
                                "severity": "high",
                                "description": "Child data storage without age verification",
                                "articles": ["8.1", "8.2"]
                            })
        
        # Continue with call arguments
        for child in ast.iter_child_nodes(node):
            self.visit(child)
    
    def _contains_personal_data(self, node) -> bool:
        """Check if a class likely contains personal data."""
        personal_fields = ('name', 'email', 'phone', 'address', 'location', 'birthdate', 
                          'ssn', 'passport', 'user', 'profile', 'person')
        
        for child in node.body:
            if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                if child.target.id.lower() in personal_fields:
                    return True
            elif isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name) and target.id.lower() in personal_fields:
                        return True
                    
        return False
    
    def _has_age_verification(self, node) -> bool:
        """Check if a function has age verification."""
        age_verification_patterns = ('verify', 'check', 'confirm', 'validate', 'age', 'adult', 'parent', 'guardian')
        
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and any(pattern in child.id.lower() for pattern in age_verification_patterns):
                return True
            elif isinstance(child, ast.Attribute) and any(pattern in child.attr.lower() for pattern in age_verification_patterns):
                return True
                
        return False
    
    def _has_age_verification_nearby(self, node) -> bool:
        """Check if there's age verification near this node (simplified)."""
        # This is a simplification since we don't have easy access to surrounding context in the AST
        # A real implementation would need to look up in the parent function
        return False


def main():
    """Command-line interface for the true violation detector."""
    parser = argparse.ArgumentParser(description="Detect true GDPR violations in code")
    
    parser.add_argument('directory', help="Directory to scan")
    parser.add_argument('--rules', '-r', dest='rules_file', default="improved_rules.json",
                        help="Path to rules JSON file")
    parser.add_argument('--output', '-o', dest='output_file',
                        help="Path to output JSON report file")
    parser.add_argument('--compare', '-c', dest='compare_file',
                        help="Compare results with a standard Levox scan results file")
    
    args = parser.parse_args()
    
    # Initialize and run detector
    detector = TrueViolationDetector(args.rules_file)
    issues = detector.scan_directory(args.directory)
    
    # Generate report
    detector.generate_report(args.output_file)
    
    # Print summary
    detector.print_summary()
    
    # Compare with standard Levox results if requested
    if args.compare_file:
        try:
            with open(args.compare_file, 'r', encoding='utf-8') as f:
                levox_issues = json.load(f)
                
            # Get list of issues
            if isinstance(levox_issues, dict) and 'issues' in levox_issues:
                levox_issues = levox_issues['issues']
                
            print("\n=== Comparison with Levox Scan ===")
            print(f"Levox issues: {len(levox_issues)}")
            print(f"True violations: {len(issues)}")
            print(f"Reduction: {len(levox_issues) - len(issues)} issues ({(len(levox_issues) - len(issues)) / len(levox_issues) * 100:.1f}%)")
            
            # Find issues detected by true detector but missed by Levox
            true_files = {f"{issue['file_path']}:{issue['line_number']}" for issue in issues}
            levox_files = {f"{issue['file_path']}:{issue['line_number']}" for issue in levox_issues}
            
            missed_by_levox = true_files - levox_files
            if missed_by_levox:
                print("\nIssues missed by Levox scan:")
                for i, file_line in enumerate(list(missed_by_levox)[:5]):
                    file_path, line_num = file_line.rsplit(":", 1)
                    matching_issues = [i for i in issues if i['file_path'] == file_path and str(i['line_number']) == line_num]
                    if matching_issues:
                        issue = matching_issues[0]
                        print(f"  {i+1}. {issue.get('description')} [{file_path}:{line_num}]")
                        print(f"     Articles: {', '.join(issue.get('articles', []))}")
                
                if len(missed_by_levox) > 5:
                    print(f"  ... and {len(missed_by_levox) - 5} more")
            
        except Exception as e:
            print(f"Error comparing with Levox results: {e}")
    

if __name__ == "__main__":
    main() 