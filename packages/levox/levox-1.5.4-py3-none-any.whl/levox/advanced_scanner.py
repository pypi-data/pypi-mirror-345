"""
Advanced scanner module for detecting GDPR and PII issues with reduced false positives.
"""
import os
import re
import json
import ast
import difflib
import itertools
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union, Callable
from functools import lru_cache

from levox.scanner import Scanner, GDPRIssue, PATTERNS, EU_ADEQUATE_COUNTRIES

# Try to import meta-learning module - graceful fallback if not available
try:
    from levox.meta_learning import MetaLearningEngine
    META_LEARNING_AVAILABLE = True
except ImportError:
    META_LEARNING_AVAILABLE = False

# Enhanced patterns for better accuracy
ENHANCED_PATTERNS = {
    "data_transfer": [
        # More specific API patterns that indicate data transfer
        r"(?i)\.post\(\s*['\"]https?://(?!localhost)(?!127\.0\.0\.1)(?!0\.0\.0\.0)[^'\"]+['\"]",  # POST to non-localhost URLs
        r"(?i)\.put\(\s*['\"]https?://(?!localhost)(?!127\.0\.0\.1)(?!0\.0\.0\.0)[^'\"]+['\"]",   # PUT to non-localhost URLs
        r"(?i)\.send\(\s*['\"]https?://(?!localhost)(?!127\.0\.0\.1)(?!0\.0\.0\.0)[^'\"]+['\"]",  # SEND to non-localhost URLs
        r"(?i)upload\(\s*['\"]https?://(?!localhost)(?!127\.0\.0\.1)(?!0\.0\.0\.0)[^'\"]+['\"]",  # UPLOAD to non-localhost URLs
        
        # Analytics-specific patterns (more precise)
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)google\.?analytics\.send",
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)fbq\(['\"]track",
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)mixpanel\.track",
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)segment\.track",
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)amplitude\.track",
        
        # More context-specific data transfer patterns
        r"(?i)transmit(?:ted|ting)?\s+(?:user|personal|customer)\s+data",
        r"(?i)send(?:ing)?\s+(?:user|personal|customer)\s+data\s+to\s+(?:external|third[- ]party)",
        r"(?i)upload(?:ing)?\s+(?:user|personal|customer)\s+data\s+to\s+(?:cloud|server|api)",
    ],
    "pii_collection": [
        # More contextual PII patterns to reduce false positives
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)(?<!placeholder)user\.email|email[\s]*=|get_email|send_email",       # Email in user context
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)(?<!placeholder)user\.address|address[\s]*=|shipping_address|billing_address",  # Address in user context
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)(?<!placeholder)user\.phone|phone[\s]*=|mobile[\s]*=|telephone[\s]*=",  # Phone in user context
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)(?<!placeholder)user\.ssn|ssn[\s]*=|social_security",                # SSN in user context
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)(?<!placeholder)user\.passport|passport[\s]*=|passport_number",      # Passport in user context
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)(?<!placeholder)credit_card|card_number|cvv|ccv",                    # Credit card info
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)(?<!placeholder)date_of_birth|birth_date|dob[\s]*=",                 # Birth date
        
        # Additional patterns for collection context
        r"(?i)collect(?:ing|s|ed)?\s+(?:personal|user|customer)\s+(?:data|information)",
        r"(?i)store(?:s|d)?\s+(?:personal|user|customer)\s+(?:data|information)",
        r"(?i)save(?:s|d)?\s+(?:personal|user|customer)\s+(?:data|information)",
    ],
    "consent_issues": [
        # More contextual consent patterns
        r"(?i)set_cookie\((?!.*consent)(?!.*opt[-_]in)(?!.*permission)",                          # Setting cookie without consent
        r"(?i)create_cookie\((?!.*consent)(?!.*opt[-_]in)(?!.*permission)",                       # Creating cookie without consent
        r"(?i)track_user\((?!.*consent)(?!.*opt[-_]in)(?!.*permission)",                          # Tracking without consent
        r"(?i)track_event\((?!.*consent)(?!.*opt[-_]in)(?!.*permission)",                         # Event tracking without consent
        r"(?i)analytics\.track\((?!.*consent)(?!.*opt[-_]in)(?!.*permission)",                    # Analytics tracking without consent
        
        # Additional patterns to detect lack of consent mechanisms
        r"(?i)document\.cookie\s*=(?!.*consent)(?!.*opt[-_]in)(?!.*permission)",                  # Setting cookies directly
        r"(?i)localStorage\.set(?!.*consent)(?!.*opt[-_]in)(?!.*permission)",                     # Local storage without consent
    ],
    "third_party_integration": [
        # More specific third-party integration patterns
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)stripe\.customers\.create",                          # Stripe customer creation
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)stripe\.charges\.create",                            # Stripe payment
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)aws\.s3\.upload|s3_client\.put_object",              # AWS S3 uploads
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)google\.maps\.api|googleapis\.com/maps",             # Google Maps API
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)firebase\.database\.ref|firebase\.auth",             # Firebase database/auth
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)facebook\.api|graph\.facebook\.com",                 # Facebook API
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)twitter\.api|api\.twitter\.com",                     # Twitter API
        
        # Integration with explicit PII mentions
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)third[- ]party.{0,50}(?:personal|user|customer)\s+(?:data|information)",
        r"(?i)(?<!mock)(?<!test)(?<!fake)(?<!example)service.{0,50}(?:personal|user|customer)\s+(?:data|information)",
    ],
    "data_deletion": [
        # More precise data deletion patterns
        r"(?i)def\s+delete_user|function\s+deleteUser",            # User deletion function
        r"(?i)def\s+remove_account|function\s+removeAccount",      # Account removal function
        r"(?i)def\s+erase_user_data|function\s+eraseUserData",     # Data erasure function
        r"(?i)def\s+gdpr_delete|function\s+gdprDelete",            # GDPR deletion function
        r"(?i)def\s+handle_right_to_erasure|function\s+handleRightToErasure",  # Right to erasure
        
        # Additional patterns for data deletion context
        r"(?i)implement(?:s|ed|ing)?\s+(?:data|user)\s+deletion",
        r"(?i)data\s+erasure\s+request",
        r"(?i)right\s+to\s+be\s+forgotten",
    ],
    "pii_storage": [
        # Patterns for detecting PII storage without proper safeguards
        r"(?i)store(?:d|s)?\s+(?:personal|user|customer)\s+(?:data|information)",
        r"(?i)save(?:d|s)?\s+(?:personal|user|customer)\s+(?:data|information)",
        r"(?i)database\.(?:insert|create|update).*(?:user|email|address|phone|passport|ssn|credit)",
        r"(?i)(?:plain|clear)text\s+(?:password|credential)",
    ],
    "security_measures": [
        # Patterns for detecting missing security measures
        r"(?i)password(?!.*hash)(?!.*encrypt)(?!.*bcrypt)(?!.*scrypt)(?!.*pbkdf2)",
        r"(?i)credential(?!.*protect)(?!.*secure)(?!.*encrypt)",
        r"(?i)auth(?:entication)?(?!.*token)(?!.*secure)(?!.*session)",
        r"(?i)transmit(?!.*https)(?!.*ssl)(?!.*tls)(?!.*secure)",
    ],
}

# Context rules to reduce false positives
CONTEXT_RULES = {
    "pii_collection": {
        "required_nearby": ["user", "customer", "profile", "account", "personal", "getData", "save", "store", "collect", "client", "member", "subscriber"],
        "excluded_if_nearby": ["example", "test", "mock", "fake", "sample", "stub", "fixture", "const", "documentation", "placeholder", "dummy", "demo"],
        "high_confidence_terms": ["privacy", "gdpr", "personal_data", "sensitive", "pii", "identifiable", "personal", "customer_info"],
    },
    "data_transfer": {
        "required_nearby": ["send", "transmit", "upload", "post", "put", "request", "fetch", "api", "endpoint", "transfer", "export", "share"],
        "excluded_if_nearby": ["example", "test", "mock", "localhost", "127.0.0.1", "0.0.0.0", "stub", "fixture", "dummy", "demo", "placeholder"],
        "high_confidence_terms": ["api", "external", "third-party", "transfer", "endpoint", "cross-border", "international", "remote"],
    },
    "consent_issues": {
        "required_nearby": ["cookie", "track", "collect", "analytics", "monitor", "user", "profile", "preference", "data"],
        "excluded_if_nearby": ["consent", "permission", "opt-in", "gdpr_compliance", "hasConsent", "checkConsent", "userConsent", "consentManager", "consentGiven"],
        "high_confidence_terms": ["consent", "permission", "track", "monitor", "gdpr", "opt-in", "cookie_banner", "accept_cookies"],
    },
    "third_party_integration": {
        "required_nearby": ["api", "service", "client", "connect", "integration", "provider", "partner", "external", "vendor"],
        "excluded_if_nearby": ["test", "mock", "local", "development", "stub", "demo", "example", "local_test", "local_dev"],
        "high_confidence_terms": ["api_key", "token", "provider", "service", "integration", "platform", "subscription", "account_id"],
    },
    "data_deletion": {
        "required_nearby": ["delete", "remove", "erase", "purge", "user", "account", "data", "destroy", "clear", "wipe"],
        "excluded_if_nearby": ["test", "example", "temporary", "cache", "temp", "debug", "simulation", "mock_data"],
        "high_confidence_terms": ["right_to_erasure", "gdpr", "forget", "removal", "delete_account", "remove_data", "data_deletion_policy"],
    },
    "data_retention": {
        "required_nearby": ["store", "keep", "retain", "archive", "period", "time", "duration", "days", "months", "years"],
        "excluded_if_nearby": ["test", "example", "mock", "temporary", "demo", "cache", "debug", "log_retention"],
        "high_confidence_terms": ["policy", "compliance", "duration", "period", "retention_period", "data_lifecycle", "storage_policy"],
    },
    "data_minimization": {
        "required_nearby": ["collect", "data", "minimize", "necessary", "required", "essential", "needed", "mandatory", "fields"],
        "excluded_if_nearby": ["test", "example", "debug", "log", "mock", "demo", "simulation", "placeholder_data"],
        "high_confidence_terms": ["gdpr", "compliance", "minimize", "only_necessary", "minimization", "data_minimization", "essential_only"],
    },
    "security_measures": {
        "required_nearby": ["secure", "protect", "encrypt", "hash", "auth", "password", "login", "token", "sensitive"],
        "excluded_if_nearby": ["test", "example", "mock", "debug", "dummy", "demo", "simulation", "test_credentials"],
        "high_confidence_terms": ["security", "protection", "encryption", "hashing", "bcrypt", "scrypt", "pbkdf2", "salt", "https"],
    },
    "data_breach": {
        "required_nearby": ["breach", "incident", "leak", "violation", "report", "compromise", "unauthorized", "access", "disclosure"],
        "excluded_if_nearby": ["test", "example", "mock", "simulation", "training", "drill", "scenario", "exercise"],
        "high_confidence_terms": ["notification", "authority", "detect", "report", "incident_response", "data_breach_procedure", "notification_requirement"],
    },
    "automated_decision_making": {
        "required_nearby": ["algorithm", "automate", "decision", "profile", "score", "prediction", "classification", "assessment"],
        "excluded_if_nearby": ["test", "example", "mock", "debug", "simulation", "training", "experiment", "prototype"],
        "high_confidence_terms": ["decision_making", "automated", "profiling", "scoring", "algorithmic", "ai_decision", "automated_processing"],
    },
    "cross_border_transfers": {
        "required_nearby": ["transfer", "international", "country", "jurisdiction", "abroad", "overseas", "global", "foreign", "offshore"],
        "excluded_if_nearby": ["test", "example", "mock", "simulation", "scenario", "training", "exercise", "dummy_transfer"],
        "high_confidence_terms": ["scc", "standard_contractual_clauses", "adequacy", "shield", "binding_corporate_rules", "transfer_impact", "schrems"],
    },
    "pii_storage": {
        "required_nearby": ["store", "save", "persist", "database", "record", "table", "collection", "repository", "backup"],
        "excluded_if_nearby": ["test", "example", "mock", "temporary", "cache", "demo", "simulation", "placeholder"],
        "high_confidence_terms": ["encryption", "secure_storage", "data_protection", "at_rest", "encrypted_storage", "secure_database"],
    },
    "pii_search_function": {
        "required_nearby": ["search", "query", "find", "lookup", "filter", "retrieve", "get_user", "fetch_by"],
        "excluded_if_nearby": ["test", "example", "mock", "dummy", "demo", "simulation", "placeholder", "sample_search"],
        "high_confidence_terms": ["email_search", "find_by_personal", "user_lookup", "customer_search", "search_by_identifier"],
    },
}

# Additional file patterns to skip for GDPR scanning
ALLOWLISTS = {
    "files": [
        # Build artifacts
        r".*\.min\.js$",
        r".*\.min\.css$",
        r".*\.bundle\.js$",
        
        # Config files unlikely to contain PII
        r"package-lock\.json$",
        r"yarn\.lock$",
        r"Dockerfile$",
        r"\.gitignore$",
        r"\.gitattributes$",
        r"\.dockerignore$",
        r"\.babelrc$",
        r"tsconfig\.json$",
        r"tslint\.json$",
        r"\.eslintrc(\.json)?$",
        r"webpack\.config\.js$",
        r"jest\.config\.js$",
        
        # Non-code files
        r".*\.md$",
        r".*\.svg$",
        r".*\.png$",
        r".*\.jpg$",
        r".*\.jpeg$",
        r".*\.gif$",
        r".*\.ico$",
        r".*\.woff2?$",
        r".*\.ttf$",
        r".*\.eot$",
        r".*\.otf$",
    ],
    "domains": [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "example.com",
        "test.com",
        "yourcompany.com",
        "dummy.com",
        "placeholder.com",
        "testing.com",
    ],
    "directories": [
        "test",
        "tests",
        "testing",
        "spec",
        "specs",
        "mocks",
        "examples",
        "samples",
        "fixtures",
        "stubs",
        "demo",
        "docs",
        "node_modules",
        "venv",
        "env",
        "virtualenv",
        "__pycache__",
        "dist",
        "build",
    ],
    "code_indicators": [
        "console.log",
        "print",
        "debug",
        "TODO",
        "FIXME",
        "logger.debug",
        "assert",
        "if __name__ == '__main__'",
    ],
}

# More comprehensive list of EU-adequate countries
EXTENDED_EU_ADEQUATE_COUNTRIES = EU_ADEQUATE_COUNTRIES.union({
    'switzerland', 'norway', 'iceland', 'liechtenstein',  # EEA
    'south korea', 'korea', 'republic of korea',          # Recently received adequacy
    'singapore',                                          # Partial adequacy
    'uk', 'united kingdom', 'great britain', 'england',   # UK adequacy
})

# Define binary file extensions to skip
BINARY_EXTENSIONS = {
    '.pyc', '.pyo', '.so', '.dll', '.exe', '.bin',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.tar', '.gz', '.tgz',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.wav', '.flac',
    '.woff', '.woff2', '.ttf', '.eot', '.otf'
}

class AdvancedScanner(Scanner):
    def __init__(self, target_dir: str, exclude_dirs: List[str] = None, 
                 config: Dict[str, Any] = None):
        """Initialize the advanced scanner with configuration options."""
        super().__init__(target_dir, exclude_dirs)
        
        # Default configuration
        self.config = {
            "use_enhanced_patterns": True,
            "context_sensitivity": True,
            "allowlist_filtering": True,
            "code_analysis": True,
            "false_positive_threshold": 0.7,  # Higher means more sensitive (more issues reported)
            "min_confidence": 0.5,            # Minimum confidence to report an issue
            "max_context_lines": 5,           # Lines of context to analyze around each potential issue
            "use_meta_learning": META_LEARNING_AVAILABLE,  # Use meta-learning if available
            "quiet": False,                   # Whether to suppress verbose output
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
            
        # Storage for potential issues before false positive filtering
        self.potential_issues: List[Tuple[GDPRIssue, float]] = []
        
        # Initialize meta-learning engine if available and enabled
        self.meta_learning = None
        if self.config["use_meta_learning"] and META_LEARNING_AVAILABLE:
            try:
                self.meta_learning = MetaLearningEngine(quiet=self.config["quiet"])
                if not self.config["quiet"]:
                    print("Meta-learning enabled")
            except Exception as e:
                if not self.config["quiet"]:
                    print(f"Failed to initialize meta-learning engine: {e}")
                self.meta_learning = None
    
    def _get_context_lines(self, lines: List[str], line_index: int, n_lines: int = 5) -> List[str]:
        """Get n lines of context before and after the given line."""
        start = max(0, line_index - n_lines)
        end = min(len(lines), line_index + n_lines + 1)
        return lines[start:end]
    
    def _is_in_allowlist(self, file_path: Path, content: str) -> bool:
        """Check if the file or content should be allowlisted."""
        if not self.config["allowlist_filtering"]:
            return False
            
        # Special case for specific directories we want to analyze anyway
        # This is useful for testing on example directories
        special_analyze_dirs = ["examples"]
        for part in file_path.parts:
            if part in special_analyze_dirs:
                return False
            
        # Check file name allowlist
        file_name = file_path.name
        if any(file_name.startswith(prefix) for prefix in ALLOWLISTS["files"]):
            return True
            
        # Check directory allowlist 
        for part in file_path.parts:
            if part in ALLOWLISTS["directories"]:
                return True
                
        # Check domain allowlist in content
        for domain in ALLOWLISTS["domains"]:
            if domain in content.lower():
                return True
                
        return False
    
    def _analyze_context(self, issue_type: str, context_lines: List[str], line_index: int) -> float:
        """
        Analyze the context around a potential issue to determine confidence.
        
        Args:
            issue_type: Type of the potential GDPR issue
            context_lines: Lines of code around the potential issue
            line_index: Index of the potential issue line within context_lines
            
        Returns:
            Confidence score between 0 and 1
        """
        if issue_type not in CONTEXT_RULES:
            return 0.5  # Default medium confidence
        
        # Get context rules for this issue type
        rules = CONTEXT_RULES[issue_type]
        required_terms = rules.get("required_nearby", [])
        excluded_terms = rules.get("excluded_if_nearby", [])
        high_confidence_terms = rules.get("high_confidence_terms", [])
        
        # Join context lines into a single text for better analysis
        context_text = " ".join(context_lines).lower()
        
        # Check for required nearby terms
        required_count = 0
        has_required = False

        for term in required_terms:
            if term.lower() in context_text:
                required_count += 1
                has_required = True
        
        # Check for excluded terms
        excluded_count = 0
        is_excluded = False
        for term in excluded_terms:
            if term.lower() in context_text:
                excluded_count += 1
                is_excluded = True
        
        # Check for high confidence terms
        high_confidence_count = 0
        for term in high_confidence_terms:
            if term.lower() in context_text:
                high_confidence_count += 1
        
        # Calculate base confidence
        if has_required and not is_excluded:
            # More required terms = higher confidence
            base_confidence = 0.7 + (min(required_count, 3) * 0.1)  
        elif has_required and is_excluded:
            # More exclusion terms = lower confidence
            base_confidence = 0.5 - (min(excluded_count, 3) * 0.15)  
        elif not has_required and not is_excluded:
            base_confidence = 0.4
        else:
            # No required terms but has exclusion terms = very low confidence
            base_confidence = 0.2 - (min(excluded_count, 2) * 0.1)
            
        # Boost confidence based on high confidence terms
        confidence_boost = min(high_confidence_count * 0.15, 0.3)  # Up to 0.3 boost
        
        # Check if the context includes comments related to GDPR
        gdpr_comment_boost = 0.0
        for line in context_lines:
            if re.search(r'(?i)(?:#|//|/\*|\*|<!--|-->).*(?:gdpr|compliance|privacy|data\s+protection)', line):
                gdpr_comment_boost = 0.25
                break
        
        # Check for code indicators that might be false positives
        code_indicator_penalty = 0.0
        for indicator in ALLOWLISTS.get("code_indicators", []):
            if indicator.lower() in context_text:
                code_indicator_penalty = 0.25
                break
                
        # Additional check for test/example code contexts which are likely false positives
        test_context_penalty = 0.0
        test_indicators = ["test", "example", "mock", "stub", "fixture", "dummy"]
        test_indicator_count = sum(1 for indicator in test_indicators if indicator in context_text)
        if test_indicator_count >= 2:  # If multiple test indicators are present
            test_context_penalty = 0.3
        
        # Check specificity of pattern match (longer matches = higher confidence)
        specificity_boost = 0.0
        # Get the actual line with the issue
        if 0 <= line_index < len(context_lines):
            issue_line = context_lines[line_index]
            for term in high_confidence_terms + required_terms:
                if len(term) > 5 and term in issue_line.lower():
                    specificity_boost = 0.15
                break
        
        # Final confidence calculation with adjustments for false positive/negative reduction
        confidence = base_confidence + confidence_boost + gdpr_comment_boost + specificity_boost - code_indicator_penalty - test_context_penalty
        
        # Ensure confidence is between 0 and 1
        return max(0.1, min(1.0, confidence))
    
    def _analyze_code(self, file_path: Path, line_number: int, issue_type: str) -> float:
        """Perform static code analysis to improve detection accuracy."""
        if not self.config["code_analysis"]:
            return 0.5  # Neutral confidence if code analysis is disabled
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                code = f.read()
                
            # Check for imports of privacy or security related libraries (indicates awareness)
            security_imports = [
                r'(?i)import\s+.*\b(?:crypto|security|privacy|gdpr|compliance)',
                r'(?i)from\s+.*\b(?:crypto|security|privacy|gdpr|compliance)',
                r'(?i)require\s*\(\s*[\'"].*(?:crypto|security|privacy|gdpr|compliance)',
                r'(?i)import\s+.*\b(?:bcrypt|scrypt|argon2|aes|rsa|tls|ssl)',
                r'(?i)from\s+.*\b(?:bcrypt|scrypt|argon2|aes|rsa|tls|ssl)',
            ]
            
            import_score = 0.0
            for pattern in security_imports:
                if re.search(pattern, code):
                    import_score = 0.1
                    break
            
            # For Python files, we can use the ast module for more accurate analysis
            ast_score = 0.0
            if file_path.suffix.lower() == '.py':
                try:
                    tree = ast.parse(code)
                    
                    # Count privacy-related identifiers in the code
                    privacy_terms = ['gdpr', 'privacy', 'personal_data', 'consent', 'user_data', 
                                   'sensitive', 'compliance', 'encrypt', 'hash', 'secure']
                    privacy_count = sum(1 for node in ast.walk(tree) 
                                     if isinstance(node, ast.Name) and
                                     any(term in node.id.lower() for term in privacy_terms))
                    
                    # Calculate score based on privacy terms found
                    if privacy_count > 0:
                        ast_score = min(0.2, privacy_count * 0.05)
                        
                    # Check for annotations or docstrings related to GDPR
                    doc_score = 0.0
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.docstring:
                            if re.search(r'(?i)(?:gdpr|compliance|privacy|data protection)', node.docstring):
                                doc_score = 0.15
                                break
                    
                    # Add function analysis - check if the issue is within a function with privacy-related name
                    func_score = 0.0
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Check if our line is within this function
                            if node.lineno <= line_number <= (node.end_lineno or node.lineno + 20):
                                if any(term in node.name.lower() for term in privacy_terms):
                                    func_score = 0.15
                                    break
                except SyntaxError:
                    # If we can't parse the code, fall back to simpler analysis
                    pass
            
            # For all file types, check for privacy-related comments
            privacy_comments = ['gdpr', 'privacy', 'personal data', 'consent', 'compliance', 'data protection']
            comment_indicators = ['#', '//', '/*', '*', '<!--', '-->']
            
            # Count lines with privacy-related comments
            comment_lines = [line for line in code.split('\n') 
                          if any(ind in line for ind in comment_indicators) and
                          any(term in line.lower() for term in privacy_comments)]
            
            comment_score = 0.0
            if comment_lines:
                # If there are privacy-related comments, this increases confidence
                comment_score = min(0.2, len(comment_lines) * 0.03)
            
            # Check if file might be a test or example file based on filename
            filename_score = 0.0
            filename = file_path.name.lower()
            if any(term in filename for term in ['test', 'example', 'sample', 'mock', 'stub', 'fixture']):
                filename_score = -0.2  # Penalty for test/example files
            
            # Calculate final score
            final_score = 0.5 + import_score + ast_score + doc_score + func_score + comment_score + filename_score
            
            # Ensure score is between 0 and 1
            return max(0.0, min(1.0, final_score))
        except Exception as e:
            # If anything goes wrong, return default confidence
            return 0.5
    
    def scan_file(self, file_path: Path) -> List[GDPRIssue]:
        """Scan a single file with enhanced false positive detection."""
        # Skip if in allowlist
        if self._is_in_allowlist(file_path, ""):
            return []
            
        # Use cache if available
        cached_results = self._get_from_cache(file_path)
        if cached_results is not None:
            return cached_results
            
        issues = []
        
        try:
            # Get file content
            content, lines = self._read_file_optimized(file_path)
            if not content or not lines:
                return []
                
            # Check if this file is in an allowlist
            if self._is_in_allowlist(file_path, content):
                self._save_to_cache(file_path, [])
                return []
                
            # Check content patterns with meta-learning
            if self.meta_learning and self.config["use_meta_learning"]:
                try:
                    if self.meta_learning.check_content_patterns(content):
                        if not self.config["quiet"]:
                            print(f"Meta-learning: Content pattern match, ignoring file {file_path}")
                        self._save_to_cache(file_path, [])
                        return []
                except Exception as e:
                    if not self.config["quiet"]:
                        print(f"Error in meta-learning content check: {e}")
                
            # Get file extension
            file_extension = file_path.suffix.lower()
            
            # Fast pre-filtering
            should_scan = False
            # More comprehensive pre-filter keywords to reduce false negatives
            pre_filter_keywords = [
                "email", "name", "password", "address", "phone", "ip", "user", "customer", 
                "credit", "personal", "data", "gdpr", "privacy", "consent", "track", "collect",
                "transfer", "api", "store", "save", "delete", "erase", "retention"
            ]
            
            for keyword in pre_filter_keywords:
                if keyword in content.lower():
                    should_scan = True
                    break
                    
            if not should_scan:
                self._save_to_cache(file_path, [])
                return []
                
            # Get all patterns to check
            if self.config["use_enhanced_patterns"]:
                # Combine base patterns with enhanced patterns
                all_patterns = {}
                for issue_type, patterns in PATTERNS.items():
                    all_patterns[issue_type] = patterns.copy()
                    
                # Add enhanced patterns
                for issue_type, patterns in ENHANCED_PATTERNS.items():
                    if issue_type in all_patterns:
                        all_patterns[issue_type].extend(patterns)
                    else:
                        all_patterns[issue_type] = patterns
            else:
                all_patterns = PATTERNS
                        
            # Scan line by line
            for line_number, line in enumerate(lines, 1):
                # Skip empty lines and comment-only lines
                if not line.strip() or line.strip().startswith(('#', '//', '/*', '*', '*/')):
                    continue
                
                for issue_type, patterns in all_patterns.items():
                    # Skip data_deletion as in the parent class - we'll check separately
                    if issue_type == "data_deletion":
                        continue
                        
                    for pattern in patterns:
                        if re.search(pattern, line):
                            # Get context around this line
                            context_lines = self._get_context_lines(
                                lines, line_number - 1, 
                                self.config["max_context_lines"]
                            )
                            
                            # Calculate confidence based on context analysis
                            context_confidence = self._analyze_context(
                                issue_type, context_lines, line_number - 1
                            )
                            
                            # Perform code analysis if applicable
                            code_confidence = self._analyze_code(
                                file_path, line_number, issue_type
                            )
                            
                            # Combine confidences (weighted average)
                            # Context analysis has higher weight
                            combined_confidence = (context_confidence * 0.7) + (code_confidence * 0.3)
                            
                            # Apply meta-learning adjustments if available
                            if self.meta_learning:
                                # Create issue data for confidence adjustment
                                issue_data = {
                                    'issue_type': issue_type,
                                    'file_path': str(file_path),
                                    'line_number': line_number,
                                    'line_content': line.strip(),
                                    'context': '\n'.join(context_lines),
                                    'confidence': combined_confidence,
                                }
                                
                                # Get adjusted confidence
                                combined_confidence = self.meta_learning.adjust_confidence(issue_data)
                            
                            # Only add issues that meet the minimum confidence threshold
                            if combined_confidence >= self.config["min_confidence"]:
                                severity = self._determine_severity(issue_type, line)
                                
                                # Lower severity if confidence is not very high
                                if combined_confidence < 0.8 and severity == "high":
                                    severity = "medium"
                                elif combined_confidence < 0.75 and severity == "medium":
                                    severity = "low"
                                
                                # Create GDPR issue
                                issue = GDPRIssue(
                                    issue_type=issue_type,
                                    file_path=str(file_path),
                                    line_number=line_number,
                                    line_content=line.strip(),
                                    severity=severity
                                )
                                
                                # Add confidence as an attribute
                                issue.confidence = combined_confidence
                                
                                # Store issue with confidence for later filtering
                                self.potential_issues.append((issue, combined_confidence))
                                
                                # If confidence is very high, add directly to results
                                if combined_confidence > 0.8:
                                    issues.append(issue)
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
            
        return issues
    
    def scan_directory(self) -> List[GDPRIssue]:
        """Scan the directory with advanced false positive filtering."""
        self.issues = []
        self.potential_issues = []
        
        # Count files for statistics
        total_files = 0
        scanned_files = 0
        
        for root, dirs, files in os.walk(self.target_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs and d not in ALLOWLISTS.get("directories", [])]
            
            # Skip directories with common patterns for test/doc/example dirs (additional check)
            dirs[:] = [d for d in dirs if not any(pattern in d.lower() for pattern in ["test", "doc", "example", "sample", "mock"])]
            
            for file in files:
                total_files += 1
                file_path = Path(root) / file
                if self.should_scan_file(file_path):
                    scanned_files += 1
                    file_issues = self.scan_file(file_path)
                    self.issues.extend(file_issues)
        
        # Process potential issues that didn't get added directly
        self._process_potential_issues()
        
        # Post-processing checks
        self._check_for_missing_deletion()
        self._check_for_cross_references()
        
        # Eliminate duplicate issues (same file, type and near same line)
        self.issues = self._deduplicate_advanced(self.issues)
        
        # Record scan results in meta-learning if enabled
        if self.meta_learning:
            try:
                # Convert issues to dictionaries for meta-learning
                issue_dicts = [issue.to_dict() for issue in self.issues]
                self.meta_learning.record_scan_results(issue_dicts)
            except Exception as e:
                if not self.config["quiet"]:
                    print(f"Error recording scan results in meta-learning: {e}")
        
        # Print stats
        if not self.config["quiet"]:
            print(f"Scanned {scanned_files} of {total_files} files")
            print(f"Found {len(self.potential_issues)} potential GDPR issues")
            print(f"After filtering, reporting {len(self.issues)} issues")
            
            # Print meta-learning status only if enabled
            if self.meta_learning:
                try:
                    ml_stats = self.meta_learning.get_learning_stats()
                    if ml_stats['feedback_count'] > 0:
                        print(f"Meta-learning active: {ml_stats['feedback_count']} records")
                except Exception:
                    pass
        
        return self.issues
    
    def _process_potential_issues(self):
        """Process potential issues using false positive filtering techniques."""
        # Sort by confidence (highest first)
        self.potential_issues.sort(key=lambda x: x[1], reverse=True)
        
        # Apply false positive threshold to filter out low-confidence issues
        threshold = self.config["false_positive_threshold"]
        
        # Group potential issues by file
        issues_by_file = {}
        for issue, confidence in self.potential_issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append((issue, confidence))
            
        # Process each file's issues
        for file_path, file_issues in issues_by_file.items():
            # Group closely located issues (might be duplicates)
            grouped_issues = self._group_nearby_issues(file_issues)
            
            # Add the highest confidence issue from each group
            for group in grouped_issues:
                # Find highest confidence issue in group
                best_issue, best_conf = max(group, key=lambda x: x[1])
                
                # Only add if it meets our threshold and isn't already added
                if best_conf >= threshold and not any(i.file_path == best_issue.file_path and 
                                                 i.line_number == best_issue.line_number and
                                                 i.issue_type == best_issue.issue_type 
                                                 for i in self.issues):
                    self.issues.append(best_issue)
    
    def _group_nearby_issues(self, file_issues: List[Tuple[GDPRIssue, float]], 
                           max_distance: int = 5) -> List[List[Tuple[GDPRIssue, float]]]:
        """Group issues that are close to each other in the file."""
        # Sort by line number
        sorted_issues = sorted(file_issues, key=lambda x: x[0].line_number)
        
        # Group issues that are within max_distance lines of each other
        groups = []
        current_group = []
        last_line = -float('inf')
        
        for issue, conf in sorted_issues:
            if not current_group or issue.line_number - last_line <= max_distance:
                current_group.append((issue, conf))
            else:
                groups.append(current_group)
                current_group = [(issue, conf)]
            last_line = issue.line_number
            
        if current_group:
            groups.append(current_group)
            
        return groups
    
    def _check_for_cross_references(self):
        """Check for relationships between different issues."""
        # Group issues by file
        issues_by_file = {}
        for issue in self.issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
            
        # Look for files with both PII collection and data transfer
        # This is a higher risk scenario
        for file_path, file_issues in issues_by_file.items():
            has_pii = any(issue.issue_type == "pii_collection" for issue in file_issues)
            has_transfer = any(issue.issue_type == "data_transfer" for issue in file_issues)
            
            if has_pii and has_transfer:
                # Increase severity for these issues
                for issue in file_issues:
                    if issue.issue_type in ["pii_collection", "data_transfer"]:
                        issue.severity = "high"
    
    def _determine_severity(self, issue_type: str, content: str) -> str:
        """Enhanced severity determination with more nuanced analysis."""
        # Start with the basic severity from the parent class
        basic_severity = super()._determine_severity(issue_type, content)
        
        # Advanced severity determination for PII collection
        if issue_type == "pii_collection":
            # Check for sensitive data indicators
            sensitive_terms = ['password', 'health', 'medical', 'biometric', 'genetic', 
                              'racial', 'ethnic', 'political', 'religious', 'sexual', 
                              'criminal', 'financial', 'government_id']
            
            if any(term in content.lower() for term in sensitive_terms):
                return "high"  # Always high for sensitive data categories
        
        # Advanced severity for data transfers
        if issue_type == "data_transfer":
            # Extract potential country information (enhanced)
            countries = self._extract_countries_advanced(content)
            
            # If transferring to non-EU country without safeguards
            non_eu_countries = [c for c in countries if c.lower() not in EXTENDED_EU_ADEQUATE_COUNTRIES]
            if non_eu_countries and not any(term in content.lower() for term in 
                                           ['scc', 'standard_contractual_clause', 'adequacy_decision', 
                                            'binding_corporate_rules', 'bcr']):
                return "high"
        
        # Consent issues severity depends on the context
        if issue_type == "consent_issues":
            # Especially severe for tracking children
            if any(term in content.lower() for term in ['child', 'kid', 'minor', 'teen', 'young']):
                return "high"
        
        return basic_severity
    
    @lru_cache(maxsize=128)
    def _extract_countries_advanced(self, text: str) -> List[str]:
        """Enhanced country extraction with better accuracy."""
        from levox.scanner import extract_countries
        
        # Start with basic extraction
        countries = extract_countries(text)
        
        # Add additional country detection methods
        # Extract potential country codes
        country_codes = re.findall(r'\b([A-Z]{2})\b', text)
        
        # Extract domain endings that might indicate countries
        domains = re.findall(r'\.([a-z]{2,6})(?:\/|\s|$|\?|\))', text.lower())
        
        # Common country domain mappings
        country_domains = {
            'us': 'us', 'uk': 'uk', 'fr': 'france', 'de': 'germany', 'cn': 'china',
            'ca': 'canada', 'jp': 'japan', 'au': 'australia', 'ru': 'russia',
            'it': 'italy', 'es': 'spain', 'br': 'brazil', 'in': 'india'
        }
        
        # Add countries from domain endings
        for domain in domains:
            if domain in country_domains:
                countries.append(country_domains[domain])
        
        return list(set(countries))  # Remove duplicates 
    
    def _deduplicate_advanced(self, issues: List[GDPRIssue]) -> List[GDPRIssue]:
        """Advanced deduplication that considers issue type and proximity."""
        if not issues:
            return []
            
        # Sort by file path, issue type, and line number
        sorted_issues = sorted(issues, key=lambda x: (x.file_path, x.issue_type, x.line_number))
        
        # Use a sliding window approach to identify duplicates
        unique_issues = []
        prev_issue = None
        
        for issue in sorted_issues:
            # First issue or different file/type
            if prev_issue is None or issue.file_path != prev_issue.file_path or issue.issue_type != prev_issue.issue_type:
                unique_issues.append(issue)
                prev_issue = issue
                continue
                
            # Check if this issue is close to the previous one
            if abs(issue.line_number - prev_issue.line_number) <= 5:
                # Keep the one with higher confidence if available
                curr_confidence = getattr(issue, 'confidence', 0.5)
                prev_confidence = getattr(prev_issue, 'confidence', 0.5)
                
                if curr_confidence > prev_confidence:
                    # Replace the previous issue with this one
                    unique_issues[-1] = issue
                    prev_issue = issue
            else:
                unique_issues.append(issue)
                prev_issue = issue
                
        return unique_issues 

    def should_scan_file(self, file_path: Path) -> bool:
        """
        Determine whether a file should be scanned based on its extension and path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be scanned, False otherwise
        """
        # Convert to string for pattern matching
        file_path_str = str(file_path)
        
        # Check if the file has a known binary extension
        if file_path.suffix.lower() in BINARY_EXTENSIONS:
            return False
            
        # Check if the file matches any patterns in the allowlist
        for pattern in ALLOWLISTS.get("files", []):
            if re.search(pattern, file_path_str, re.IGNORECASE):
                return False
                
        # Explicitly check for package-lock.json and other common config files
        filename = file_path.name.lower()
        if filename in [
            'package-lock.json', 
            'yarn.lock', 
            '.gitignore', 
            '.dockerignore',
            'tsconfig.json',
            'tslint.json',
            '.eslintrc',
            '.eslintrc.json',
            'webpack.config.js',
            'jest.config.js',
            'readme.md'
        ]:
            return False
        
        # Use meta-learning to check if file should be ignored
        if self.meta_learning and self.config["use_meta_learning"]:
            try:
                if self.meta_learning.should_ignore_file(file_path_str):
                    if not self.config["quiet"]:
                        print(f"Meta-learning: Ignoring file {file_path}")
                    return False
            except Exception as e:
                if not self.config["quiet"]:
                    print(f"Error in meta-learning file check: {e}")
        
        # Call the parent class method for additional checks
        return super().should_scan_file(file_path) 