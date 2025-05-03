"""
Scanner module for detecting GDPR and PII issues in code.
"""
import os
import re
import json
import ast
import tokenize
import mmap
import time
import hashlib
import pickle
import itertools
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Generator
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import lru_cache, partial
import datetime
import threading
import queue

from levox.gdpr_articles import get_articles_for_issue_type, format_article_reference, get_severity_for_issue_type

# Global cache for file scanning results
SCAN_CACHE = {}
# Global regex pattern cache
COMPILED_PATTERNS = {}
# Global file hash cache
FILE_HASH_CACHE = {}
# Thread-local storage for memory optimization
THREAD_LOCAL = threading.local()

# Performance configuration
MAX_CHUNK_SIZE = 5000  # Maximum chunk size for reading large files
ENABLE_CACHING = True  # Enable result caching
SCAN_BATCH_SIZE = 100  # Number of files to scan in a batch
FILE_READ_CHUNK_SIZE = 1024 * 1024  # 1MB chunks for reading large files

# GDPR compliance patterns
PATTERNS = {
    "data_transfer": [
        r"(?i)https?://(?!localhost)[^/\s]+",  # URLs (excluding localhost)
        r"(?i)api\.(?!localhost)[^/\s]+",      # API endpoints
        r"(?i)upload(ing)?\s+to\s+[^/\s]+",    # Uploading data
        r"(?i)send(ing)?\s+to\s+[^/\s]+",      # Sending data
        r"(?i)transfer(ing)?\s+to\s+[^/\s]+",  # Transferring data
        r"(?i)axios\.(post|put)\(",            # Axios HTTP requests
        r"(?i)fetch\(['\"]https?://",          # Fetch API calls
        r"(?i)\.ajax\({.*url",                 # jQuery AJAX
        r"(?i)new\s+XMLHttpRequest\(\)",       # XHR requests
        r"(?i)\.(upload|send|transmit)Data",   # Various send methods
        r"(?i)cloud\.upload",                  # Cloud storage uploads
    ],
    "pii_collection": [
        r"(?i)email",                      # Email
        r"(?i)address",                    # Physical address
        r"(?i)phone",                      # Phone number
        r"(?i)ssn",                        # Social Security Number
        r"(?i)social security",            # Social Security
        r"(?i)passport",                   # Passport
        r"(?i)driver'?s? licen[cs]e",      # Driver's license
        r"(?i)credit.?card",               # Credit card
        r"(?i)dob|date of birth|birth.?date", # Date of birth
        r"(?i)national.?id",               # National ID
        r"(?i)tax.?id",                    # Tax ID
        r"(?i)first.?name",                # First name
        r"(?i)last.?name",                 # Last name
        r"(?i)full.?name",                 # Full name
        r"(?i)zipcode|zip.?code|postal.?code", # Postal code
        r"(?i)geo.?location",              # Geolocation data
        r"(?i)gps.?data",                  # GPS data
        r"(?i)ip.?address",                # IP address
        r"(?i)biometric",                  # Biometric data
        r"(?i)health.?data",               # Health data
        r"(?i)medical.?(record|data)",     # Medical records
        r"(?i)gender|race|ethnicity",      # Special categories
        r"(?i)political|religious",        # Special categories
    ],
    "consent_issues": [
        r"(?i)set.?cookie",                # Setting cookies
        r"(?i)track(ing)?",                # Tracking
        r"(?i)analytic[s]?",               # Analytics
        r"(?i)monitor(ing)?",              # Monitoring
        r"(?i)log(ing)?.?user",            # User logging
        r"(?i)document\.cookie",           # Browser cookies
        r"(?i)localStorage\.",             # Local storage
        r"(?i)sessionStorage\.",           # Session storage
        r"(?i)navigator\.(geolocation|userAgent)", # Browser data
        r"(?i)pixel\.track",               # Tracking pixels
        r"(?i)(google|facebook|meta|twitter)\.?analytics", # Third-party analytics
        r"(?i)profiling",                  # User profiling
        r"(?i)user.?preference",           # User preferences
        r"(?i)opt.?(in|out)",              # Opt-in/out functions without proper check
    ],
    "third_party_integration": [
        r"(?i)facebook|fb\s+api",          # Facebook
        r"(?i)google analytics",           # Google Analytics
        r"(?i)stripe\.",                   # Stripe
        r"(?i)paypal\.",                   # PayPal
        r"(?i)aws\.|amazon",               # AWS
        r"(?i)azure\.|microsoft",          # Azure
        r"(?i)gcp\.|google cloud",         # GCP
        r"(?i)firebase\.",                 # Firebase
        r"(?i)zendesk\.",                  # Zendesk
        r"(?i)salesforce\.",               # Salesforce
        r"(?i)mailchimp\.",                # Mailchimp
        r"(?i)sendgrid\.",                 # SendGrid
        r"(?i)twilio\.",                   # Twilio
        r"(?i)hubspot\.",                  # HubSpot
        r"(?i)intercom\.",                 # Intercom
        r"(?i)amplitude\.",                # Amplitude
        r"(?i)mixpanel\.",                 # Mixpanel
        r"(?i)segment\.",                  # Segment
        r"(?i)optimizely\.",               # Optimizely
        r"(?i)hotjar\.",                   # Hotjar
    ],
    "data_deletion": [
        r"(?i)delete account",             # Delete account
        r"(?i)remove.+data",               # Remove data
        r"(?i)erase.+data",                # Erase data
        r"(?i)forget.+me",                 # Forget me
        r"(?i)right.?to.?erasure",         # Right to erasure
        r"(?i)right.?to.?be.?forgotten",   # Right to be forgotten
        r"(?i)data.?deletion.?request",    # Data deletion request
        r"(?i)purge.?user",                # Purge user data
        r"(?i)destroy.?record",            # Destroy records
        r"(?i)wipe.?(account|data)",       # Wipe account or data
    ],
    "data_retention": [
        r"(?i)retain.+data.+(\d+.days|\d+.months|\d+.years)", # Data retention with time period
        r"(?i)storage.?period",            # Storage period
        r"(?i)archive.?data",              # Archiving data
        r"(?i)data.?retention.?policy",    # Data retention policy
        r"(?i)keep.+data.+for",            # Keep data for...
        r"(?i)store.+data.+(\d+|\w+)",     # Store data for period
    ],
    "data_minimization": [
        r"(?i)collect.+only.+necessary",   # Collect only necessary data
        r"(?i)minimal.?data",              # Minimal data collection
        r"(?i)data.?minimization",         # Data minimization principle
        r"(?i)reduce.?data.?collection",   # Reduce data collection
        r"(?i)limit.?collection",          # Limit collection
    ],
    "security_measures": [
        r"(?i)encrypt",                    # Encryption
        r"(?i)hash",                       # Hashing
        r"(?i)salt",                       # Salting
        r"(?i)bcrypt|scrypt|argon2",       # Strong hashing algorithms
        r"(?i)aes|rsa|ecc",                # Encryption algorithms
        r"(?i)hmac",                       # HMAC
        r"(?i)2fa|mfa|two.?factor",        # Two-factor authentication
        r"(?i)access.?control",            # Access control
        r"(?i)authentication",             # Authentication
        r"(?i)authorization",              # Authorization
        r"(?i)rate.?limit",                # Rate limiting
        r"(?i)firewall",                   # Firewall
        r"(?i)intrusion.?detection",       # Intrusion detection
        r"(?i)ssl|tls",                    # SSL/TLS
        r"(?i)https",                      # HTTPS
    ],
    "data_breach": [
        r"(?i)breach.?notification",       # Breach notification
        r"(?i)data.?leak",                 # Data leak
        r"(?i)security.?incident",         # Security incident
        r"(?i)unauthorized.?access",       # Unauthorized access
        r"(?i)compromise.?data",           # Compromised data
        r"(?i)detect.?breach",             # Breach detection
        r"(?i)report.?incident",           # Reporting incidents
    ],
    "automated_decision_making": [
        r"(?i)automated.?decision",        # Automated decision making
        r"(?i)algorithm.?decision",        # Algorithmic decisions
        r"(?i)profiling.?user",            # User profiling
        r"(?i)automatic.?process",         # Automatic processing
        r"(?i)scoring.?system",            # Scoring systems
        r"(?i)credit.?score",              # Credit scoring
        r"(?i)risk.?assessment",           # Risk assessment
    ],
    "cross_border_transfers": [
        r"(?i)international.?transfer",    # International transfers
        r"(?i)cross.?border",              # Cross-border data
        r"(?i)standard.?contractual.?clauses", # SCCs
        r"(?i)binding.?corporate.?rules",  # BCRs
        r"(?i)privacy.?shield",            # Privacy Shield
        r"(?i)adequacy.?decision",         # Adequacy decision
        r"(?i)transfer.?impact.?assessment", # TIAs
    ]
}

# List of known EU-adequate countries for GDPR compliance
EU_ADEQUATE_COUNTRIES = {
    'austria', 'belgium', 'bulgaria', 'croatia', 'cyprus', 'czech republic', 
    'denmark', 'estonia', 'finland', 'france', 'germany', 'greece', 'hungary', 
    'ireland', 'italy', 'latvia', 'lithuania', 'luxembourg', 'malta', 'netherlands', 
    'poland', 'portugal', 'romania', 'slovakia', 'slovenia', 'spain', 'sweden',
    # Countries with adequacy decisions
    'andorra', 'argentina', 'canada', 'faroe islands', 'guernsey', 'israel', 
    'isle of man', 'japan', 'jersey', 'new zealand', 'switzerland', 'uruguay', 'uk'
}

# List of file extensions to scan
SCANNABLE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.php', '.java', '.rb', '.go', '.cs', 
    '.cpp', '.c', '.h', '.html', '.htm', '.css', '.json', '.yaml', '.yml'
}

# List of file extensions to treat as documentation
DOCUMENTATION_EXTENSIONS = {
    '.md', '.txt', '.rst', '.adoc', '.markdown', '.mdx', '.wiki',
    '.doc', '.docx', '.pdf', '.rtf'
}

# List of common documentation and resource directories to ignore
DOCUMENTATION_DIRS = {
    'docs', 'documentation', 'readme', 'changelog', 'license', 'examples',
    'samples', 'tutorials', 'guides', 'help', 'manual', 'references'
}

# Project resource directories that typically contain non-code or generated code
RESOURCE_DIRS = {
    'assets', 'static', 'public', 'resources', 'dist', 'build', 'out',
    'target', 'bin', 'obj', 'lib', 'vendor', 'third-party', 'node_modules',
    'bower_components', 'jspm_packages', 'packages', 'migrations', '__pycache__',
    '.git', '.svn', '.hg', '.vscode', '.idea', '.vs'
}

# Compiled regex patterns for better performance
PII_PATTERN = re.compile(r'(name|email|address|phone|birth|ssn|social_security|passport|license|gender|age|zip|postal|location|ip|geo|latitude|longitude|credit_card|card|cvv|expiry|payment|bank|account|iban|swift|financial|tax|invoice|password|token|api_key|auth|credential|health|medical|biometric|facial|fingerprint|genetic|diagnosis|patient|healthcare)', re.IGNORECASE)
DB_STORE_PATTERN = re.compile(r'(save|store|insert|create|add|update|upsert|write|put|persist|cache|upload|record|log|commit|push|post|set|register)', re.IGNORECASE)
CONSENT_PATTERN = re.compile(r'(consent|agree|accept|permission|approve|authorize|confirm)', re.IGNORECASE)
DATA_TRANSFER_PATTERN = re.compile(r'(transfer|send|transmit|export|share|upload|api\.post|requests\.post|fetch|axios)', re.IGNORECASE)
THIRD_PARTY_PATTERN = re.compile(r'(api|webhook|oauth|facebook|google|twitter|aws|azure|service|external|vendor|provider|partner|third.party|integration)', re.IGNORECASE)

# Common mock/fake data patterns that shouldn't be flagged
MOCK_DATA_PATTERNS = [
    r'test_email@example\.com',
    r'test@test\.com',
    r'john\.doe@example\.com',
    r'123-?4567-?8901-?2345',  # Fake credit card
    r'555-\d{3}-\d{4}',        # Fake phone number
    r'123-\d{2}-\d{4}',        # Fake SSN
    r'mock', r'fake', r'dummy', r'sample', r'test',
    r'example\.com', r'test\.com', r'localhost',
    r'127\.0\.0\.1', r'0\.0\.0\.0',
    r'John Doe', r'Jane Doe', r'xxxx'
]

# Context patterns that indicate this is development/test code
DEV_TEST_CONTEXT = [
    r'(unit|integration|e2e) test',
    r'fixture', r'mock data', r'fake data',
    r'test (data|code|function|class|suite)',
    r'sample (data|code)',
    r'TODO', r'FIXME', r'DEBUG',
    r'to be removed', r'will be replaced',
    r'not for production', r'development.only',
    r'test environment', r'sandbox'
]

MOCK_DATA_PATTERN = re.compile('|'.join(MOCK_DATA_PATTERNS), re.IGNORECASE)
DEV_TEST_CONTEXT_PATTERN = re.compile('|'.join(DEV_TEST_CONTEXT), re.IGNORECASE)

class GDPRIssue:
    """Represents a potential GDPR compliance issue in code.
    
    This class captures information about a potential GDPR issue found during code analysis,
    including the file path, line number, type of issue, description, and suggested remediation.
    It also includes references to relevant GDPR articles for addressing each type of issue.
    
    Issue types include:
    - data_transfer: Issues related to cross-border data transfers
    - pii_collection: Issues related to collecting personal identifiable information
    - consent_issues: Issues related to obtaining proper consent
    - data_retention: Issues related to how long data is stored
    - data_minimization: Issues related to collecting more data than necessary
    - user_rights: Issues related to user access, deletion, and portability rights
    - special_categories: Issues related to sensitive data like health, religion, etc.
    - children_data: Issues related to collecting data from minors
    - pii_search_function: Issues related to searching or querying by PII fields
    """

    def __init__(
            self,
            file_path: str,
            line_number: int,
            issue_type: str,
            description: str = None,
            remediation: str = None,
            articles: List[str] = None,
            line_content: str = None,  # For backward compatibility
            severity: str = "medium",  # For backward compatibility
            confidence: float = 1.0,   # For backward compatibility
            **kwargs                   # Accept any other kwargs for flexibility
    ):
        """Initialize a new GDPR issue.

        Args:
            file_path: Path to the file containing the issue
            line_number: Line number where the issue was found
            issue_type: Type of GDPR issue (e.g., "data_transfer", "pii_collection", "pii_search_function")
            description: Description of the issue
            remediation: Suggested fix or mitigation
            articles: List of relevant GDPR article numbers
            line_content: Content of the line where the issue was found (backward compatibility)
            severity: Severity of the issue (backward compatibility)
            confidence: Confidence level for the detection (backward compatibility) 
            **kwargs: Additional parameters for future compatibility
        """
        self.file_path = file_path
        self.line_number = line_number
        self.issue_type = issue_type
        self.description = description or f"Potential {issue_type.replace('_', ' ')} issue detected"
        self.remediation = remediation or ""
        self.articles = articles or get_articles_for_issue_type(issue_type)
        self.line_content = line_content or ""
        self.severity = severity
        self.confidence = confidence
        
    def format_violation(self) -> str:
        """Format this issue as a readable violation report."""
        output = []
        output.append(f"Issue: {self.description}")
        output.append(f"Location: {self.file_path}:{self.line_number}")
        output.append(f"Type: {self.issue_type}")
        output.append(f"Severity: {self.severity}")
        
        if self.line_content:
            output.append(f"Code: {self.line_content}")
            
        if self.remediation:
            output.append(f"\nRemediation suggestion:\n{self.remediation}")
            
        if self.articles:
            article_refs = [format_article_reference(article) for article in self.articles]
            output.append("\nRelevant GDPR Articles:")
            for ref in article_refs:
                output.append(f"- {ref}")
                
        return "\n".join(output)
        
    def to_dict(self) -> dict:
        """Convert this issue to a dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "issue_type": self.issue_type,
            "description": self.description,
            "remediation": self.remediation,
            "articles": self.articles,
            "line_content": self.line_content,
            "severity": self.severity,
            "confidence": self.confidence
        }

class Scanner:
    def __init__(self, target_dir: str, exclude_dirs: List[str] = None):
        """Initialize scanner with target directory."""
        self.target_dir = Path(target_dir)
        self.exclude_dirs = exclude_dirs or list(RESOURCE_DIRS)
        self.issues: List[GDPRIssue] = []
        
        # Determine optimal worker counts based on system configuration
        cpu_count = multiprocessing.cpu_count()
        self.process_workers = min(cpu_count, 16)  # Cap at 16 for memory reasons
        self.thread_workers = min(cpu_count * 2, 32)  # More threads than CPU cores for I/O bound tasks
        
        # Initialize thread pool and process pool executors
        self.thread_pool = ThreadPoolExecutor(max_workers=self.thread_workers)
        
        # Use process-safe shared data structures
        self.manager = multiprocessing.Manager()
        self.shared_issues = self.manager.list()
        self.file_queue = self.manager.Queue()
        self.result_queue = self.manager.Queue()
        
        # For cache management
        self.cache_dir = Path(os.path.expanduser("~/.levox/cache"))
        if not self.cache_dir.exists() and ENABLE_CACHING:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Precompile all regex patterns
        self._precompile_patterns()
        
    def _precompile_patterns(self):
        """Precompile all regex patterns for better performance."""
        global COMPILED_PATTERNS
        
        if COMPILED_PATTERNS:
            return  # Already compiled
            
        for issue_type, patterns in PATTERNS.items():
            COMPILED_PATTERNS[issue_type] = [re.compile(pattern, re.MULTILINE) for pattern in patterns]
        
        # Other patterns
        COMPILED_PATTERNS['mock_data'] = re.compile('|'.join(MOCK_DATA_PATTERNS), re.IGNORECASE)
        COMPILED_PATTERNS['dev_test_context'] = re.compile('|'.join(DEV_TEST_CONTEXT), re.IGNORECASE)
    
    def _fast_file_hash(self, file_path: Path) -> str:
        """Get a fast hash of file content for caching."""
        # Ensure file_path is a Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        if str(file_path) in FILE_HASH_CACHE:
            return FILE_HASH_CACHE[str(file_path)]
            
        try:
            stat = file_path.stat()
            # Use modification time and size as a quick approximation
            quick_hash = f"{stat.st_mtime}_{stat.st_size}"
            FILE_HASH_CACHE[str(file_path)] = quick_hash
            return quick_hash
        except (OSError, IOError):
            # Generate a random hash if stat fails
            return hashlib.md5(str(file_path).encode()).hexdigest()
    
    def _get_cache_key(self, file_path: Path) -> str:
        """Get a cache key for a file."""
        file_hash = self._fast_file_hash(file_path)
        return f"{file_path}_{file_hash}"
    
    def _get_from_cache(self, file_path: Path) -> Optional[List[GDPRIssue]]:
        """Try to get scan results from cache."""
        if not ENABLE_CACHING:
            return None
            
        # Ensure file_path is a Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        cache_key = self._get_cache_key(file_path)
        
        # Check in-memory cache first
        if cache_key in SCAN_CACHE:
            return SCAN_CACHE[cache_key]
            
        # Check disk cache
        cache_file = self.cache_dir / f"{hashlib.md5(cache_key.encode()).hexdigest()}.cache"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                pass
                
        return None
    
    def _save_to_cache(self, file_path: Path, issues: List[GDPRIssue]):
        """Save scan results to cache."""
        if not ENABLE_CACHING:
            return
            
        cache_key = self._get_cache_key(file_path)
        
        # Save to in-memory cache
        SCAN_CACHE[cache_key] = issues
        
        # Save to disk cache
        try:
            cache_file = self.cache_dir / f"{hashlib.md5(cache_key.encode()).hexdigest()}.cache"
            with open(cache_file, 'wb') as f:
                pickle.dump(issues, f)
        except Exception:
            pass
    
    def should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned."""
        # Optimize with early returns for common exclusions
        file_suffix = file_path.suffix.lower()
        
        # Fast path: Skip documentation files
        if file_suffix in DOCUMENTATION_EXTENSIONS:
            return False
        
        # Fast path: Skip non-source files by extension
        if file_suffix not in SCANNABLE_EXTENSIONS:
            return False
            
        # Fast path: Quick check for excluded directory names
        file_path_str = str(file_path).lower()
        for excluded in RESOURCE_DIRS:
            if f"/{excluded}/" in file_path_str.replace("\\", "/") or f"\\{excluded}\\" in file_path_str:
                return False
            
        # Skip files in documentation directories
        parent_dirs = {p.lower() for p in file_path.parts}
        if any(doc_dir in parent_dirs for doc_dir in DOCUMENTATION_DIRS):
            return False
            
        # Skip minified files (likely to be third-party libraries)
        if ".min." in file_path.name:
            return False
            
        # Skip generated files
        generated_indicators = ['generated', 'auto-generated', 'autogenerated', '.g.']
        if any(indicator in file_path.name.lower() for indicator in generated_indicators):
            return False
            
        # Skip files larger than 10MB (unlikely to be source code)
        try:
            if file_path.stat().st_size > 10_000_000:  # 10MB
                return False
        except (OSError, IOError):
            return False
            
        # Only scan text files
        try:
            with open(file_path, 'rb') as f:
                # Try to decode as utf-8 to confirm it's a text file
                content = f.read(1024)  # Read just the beginning
                try:
                    content.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    return False
        except (OSError, IOError):
            return False
            
        return True

    def _read_file_optimized(self, file_path: Path) -> Tuple[str, List[str]]:
        """Optimized file reading with memory mapping for large files."""
        # Check if we have this file content in thread-local storage
        if hasattr(THREAD_LOCAL, 'current_file') and THREAD_LOCAL.current_file == file_path:
            return THREAD_LOCAL.current_content, THREAD_LOCAL.current_lines
            
        try:
            file_size = file_path.stat().st_size
            
            # For small files, use regular file read
            if file_size < FILE_READ_CHUNK_SIZE:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    lines = content.splitlines()
            else:
                # For large files, use memory mapping
                with open(file_path, 'r+b') as f:
                    mm = mmap.mmap(f.fileno(), 0)
                    try:
                        content = mm.read().decode('utf-8', errors='replace')
                        lines = content.splitlines()
                    finally:
                        mm.close()
            
            # Store in thread-local storage for potential reuse
            THREAD_LOCAL.current_file = file_path
            THREAD_LOCAL.current_content = content
            THREAD_LOCAL.current_lines = lines
            
            return content, lines
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return "", []

    def scan_file(self, file_path: Path) -> List[GDPRIssue]:
        """Scan a single file for GDPR and PII issues."""
        # Ensure file_path is a Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        # Check cache first
        cached_results = self._get_from_cache(file_path)
        if cached_results is not None:
            return cached_results
            
        issues = []
        
        try:
            # Use optimized file reading
            content, lines = self._read_file_optimized(file_path)
            if not content:
                return []
                
            # Determine file extension to identify comment syntax
            file_extension = file_path.suffix.lower()
            
            # Fast pre-filtering - skip files that don't contain any PII keywords
            should_scan = False
            for keyword in ["email", "name", "password", "address", "phone", "ip", "user", "customer", "credit"]:
                if keyword in content.lower():
                    should_scan = True
                    break
                    
            if not should_scan:
                # Save empty result to cache
                self._save_to_cache(file_path, [])
                return []
            
            # For Python files, use AST-based parsing to exclude comments and docstrings
            if file_extension == '.py':
                issues.extend(self._scan_python_file_with_ast(file_path, content, lines))
            else:
                # For other file types, use line-by-line scanning with comment detection
                issues.extend(self._scan_file_by_line(file_path, content, lines, file_extension))
            
            # Save to cache
            self._save_to_cache(file_path, issues)
                
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
            
        return issues
        
    def _scan_file_by_line(self, file_path: Path, content: str, lines: List[str], file_extension: str) -> List[GDPRIssue]:
        """Scan file line by line for issues."""
        issues = []
        
        # Simple optimization - skip files that are clearly tests
        if "test" in str(file_path).lower() and any(test_term in content.lower() for test_term in self.TEST_INDICATORS):
            return []
            
        # Process lines in chunks for better memory usage
        for chunk_start in range(0, len(lines), MAX_CHUNK_SIZE):
            chunk_end = min(chunk_start + MAX_CHUNK_SIZE, len(lines))
            chunk = lines[chunk_start:chunk_end]
            
            for i, line in enumerate(chunk, chunk_start + 1):
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Skip comment lines based on file type
                if self._is_comment_line(line, file_extension):
                    continue
                
                # Use compiled patterns for faster matching
                for issue_type, compiled_patterns in COMPILED_PATTERNS.items():
                    if issue_type in ['mock_data', 'dev_test_context']:
                        continue
                        
                    for pattern in compiled_patterns:
                        if pattern.search(line):
                            # Special case for data deletion - we want to find MISSING deletion routines
                            if issue_type == "data_deletion":
                                # Skip this as a positive finding - we'll detect missing deletion later
                                continue
                            
                            severity = self._determine_severity(issue_type, line)
                            issues.append(GDPRIssue(
                                file_path=str(file_path),
                                line_number=i,
                                issue_type=issue_type,
                                description=f"Potential {issue_type.replace('_', ' ')} issue detected",
                                remediation=self._get_remediation_for_pattern_match(issue_type, line),
                                articles=get_articles_for_issue_type(issue_type)
                            ))
                            # Once we find an issue with this line, move to the next line
                            break
        
        return issues
        
    def _is_comment_line(self, line: str, file_extension: str) -> bool:
        """Check if line is a comment (optimized with caching)."""
        line = line.strip()
        
        # Skip empty lines
        if not line:
            return True
            
        # Use compiled patterns for faster matching
        if COMPILED_PATTERNS['mock_data'].search(line):
            return True
            
        if COMPILED_PATTERNS['dev_test_context'].search(line):
            return True
            
        # Check for documentation and markdown patterns (like README.md sections)
        if any(marker in line for marker in ['#', '##', '###', '####', '```', '---', '____', '====', '****', '>>>>']):
            if file_extension in DOCUMENTATION_EXTENSIONS:
                return True
                
        # Standard comment detection for various languages
        if file_extension in ['.py', '.pyw']:
            return line.startswith('#')
        elif file_extension in ['.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cs', '.php']:
            return line.startswith('//') or line.startswith('/*') or line.endswith('*/') or '/*' in line
        elif file_extension in ['.html', '.xml', '.svg']:
            return line.startswith('<!--') or line.endswith('-->') or ('<!--' in line and '-->' in line)
        elif file_extension in ['.rb']:
            return line.startswith('#')
        elif file_extension in ['.sql']:
            return line.startswith('--') or line.startswith('/*') or line.endswith('*/')
        elif file_extension in ['.yaml', '.yml']:
            return line.startswith('#')
        elif file_extension in ['.md', '.markdown', '.mdx']:
            return True  # Markdown files are documentation, not code
            
        return False
        
    def _determine_severity(self, issue_type: str, content: str) -> str:
        """Determine the severity of an issue based on type and content."""
        # PII collection is high risk under GDPR (based on CNIL fine patterns)
        if issue_type == "pii_collection":
            # Special categories of data are always high severity
            if any(term in content.lower() for term in ['passport', 'ssn', 'credit', 'card', 
                                                       'health', 'biometric', 'racial', 'ethnic',
                                                       'religious', 'political', 'genetic']):
                return "high"
            # Personal data is high severity as well due to GDPR enforcement patterns
            elif any(term in content.lower() for term in ['email', 'phone', 'address', 'name']):
                return "high"
            # Other PII is medium severity
            return "medium"
        
        # Data transfer without safeguards is high severity
        if issue_type == "data_transfer":
            # Check for non-EU countries in the content
            for country in extract_countries(content):
                if country.lower() not in EU_ADEQUATE_COUNTRIES:
                    return "high"
            return "medium"
            
        # Consent issues are high severity under GDPR (especially with tracking)
        if issue_type == "consent_issues":
            # Tracking without consent is always high severity
            if any(term in content.lower() for term in ['track', 'analytic', 'cookie']):
                return "high"
            return "medium"
            
        # Third-party integrations without DPAs are high risk
        if issue_type == "third_party_integration":
            # Cloud services handling personal data
            if any(term in content.lower() for term in ['google', 'facebook', 'amazon', 'microsoft',
                                                       'analytics', 'tracking', 'marketing']):
                return "high"
            return "medium"
            
        # Missing data deletion is always high severity (Art. 17)
        if issue_type == "missing_data_deletion" or issue_type == "data_deletion":
            return "high"
            
        # Default to medium severity
        return "medium"
        
    def _worker_process_file_batch(self, file_batch: List[Path]) -> List[GDPRIssue]:
        """Process a batch of files in a worker process."""
        all_issues = []
        for file_path in file_batch:
            try:
                file_issues = self.scan_file(file_path)
                all_issues.extend(file_issues)
            except Exception as e:
                print(f"Error scanning file {file_path}: {e}")
        return all_issues
    
    def scan_directory(self) -> List[GDPRIssue]:
        """Scan directory for GDPR compliance issues with optimized parallel processing."""
        start_time = time.time()
        print(f"Scanning directory: {self.target_dir}")
        
        # Begin file collection in a separate thread
        with self.thread_pool as executor:
            file_collector = executor.submit(self._collect_files)
            
            # Process files in parallel using multiple strategies
            self._parallel_process_files(file_collector.result())
        
        # Convert shared list to regular list
        self.issues = [issue for issue in self.shared_issues]
        
        # Post-processing steps are now much faster due to the reduced number of issues
        # Check for missing deletion methods in scanned files
        self._check_for_missing_deletion()
        
        # Deduplicate issues
        self.issues = self._deduplicate_issues(self.issues)
        
        # Performance stats
        end_time = time.time()
        elapsed = end_time - start_time
        if elapsed > 0:
            file_count = len(file_collector.result())
            files_per_second = file_count / elapsed
            print(f"Performance: {files_per_second:.1f} files/sec ({file_count} files in {elapsed:.2f} seconds)")
        
        return self.issues
    
    def _collect_files(self) -> List[Path]:
        """Collect all files to scan in a separate thread."""
        files_to_scan = []
        for root, dirs, files in os.walk(self.target_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if self.should_scan_file(file_path):
                    files_to_scan.append(file_path)
        
        print(f"Found {len(files_to_scan)} files to scan")
        return files_to_scan
    
    def _parallel_process_files(self, files_to_scan: List[Path]):
        """Process files using multi-level parallelism."""
        if not files_to_scan:
            return
            
        total_files = len(files_to_scan)
        processed = 0
        
        # Create batches for process-level parallelism
        batches = [files_to_scan[i:i+SCAN_BATCH_SIZE] for i in range(0, len(files_to_scan), SCAN_BATCH_SIZE)]
        
        # Process batches in parallel
        with ProcessPoolExecutor(max_workers=self.process_workers) as process_executor:
            # Use multi-level parallelism with threads for I/O bound tasks
            futures = [process_executor.submit(self._worker_process_file_batch, batch) for batch in batches]
            
            for future in as_completed(futures):
                try:
                    batch_issues = future.result()
                    for issue in batch_issues:
                        self.shared_issues.append(issue)
                    
                    # Update progress
                    processed += SCAN_BATCH_SIZE
                    processed = min(processed, total_files)
                    # Status update every 5% of files
                    if processed % max(1, total_files // 20) == 0 or processed == total_files:
                        progress = (processed / total_files) * 100
                        print(f"Progress: {progress:.1f}% ({processed}/{total_files} files)")
                        
                except Exception as e:
                    print(f"Error processing batch: {e}")
    
    def _check_for_missing_deletion(self):
        """Check if data deletion functions are present when PII is collected."""
        # Get all files with PII collection
        pii_files = set(issue.file_path for issue in self.issues 
                       if issue.issue_type == "pii_collection")
        
        # Get all files with data deletion functions
        deletion_files = set()
        for root, dirs, files in os.walk(self.target_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if self.should_scan_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                            for pattern in PATTERNS["data_deletion"]:
                                if re.search(pattern, content):
                                    deletion_files.add(str(file_path))
                    except Exception:
                        pass
        
        # For each file with PII but no corresponding deletion functions
        for pii_file in pii_files:
            if pii_file not in deletion_files:
                # Find the appropriate location to add deletion method
                line_number, class_name = self._find_class_for_deletion_method(pii_file)
                
                # Create a sample deletion method based on the filename and class
                sample_method = self._generate_deletion_method_example(pii_file, class_name)
                
                self.issues.append(GDPRIssue(
                    issue_type="missing_data_deletion",
                    file_path=pii_file,
                    line_number=line_number,  # Use the found line number instead of 0
                    line_content=f"File contains PII but lacks right-to-erasure implementation",
                    severity="high"
                ))
                # Add the sample method to the issue's remediation field for better guidance
                self.issues[-1].remediation = sample_method
    
    def _find_class_for_deletion_method(self, file_path: str) -> Tuple[int, str]:
        """Find the appropriate class to add a deletion method to."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                lines = content.splitlines()
                
            # For Python files, use AST to find classes
            if file_path.endswith('.py'):
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = node.name
                            # Return the line after the class definition
                            return node.lineno, class_name
                except SyntaxError:
                    pass
            
            # For other files or if AST parsing fails, look for class-like patterns
            for i, line in enumerate(lines):
                # Look for class definitions
                if re.search(r'class\s+\w+', line):
                    class_match = re.search(r'class\s+(\w+)', line)
                    if class_match:
                        return i + 1, class_match.group(1)
                # For JavaScript/TypeScript files
                elif re.search(r'(export\s+)?(class|interface)\s+\w+', line):
                    class_match = re.search(r'(class|interface)\s+(\w+)', line)
                    if class_match:
                        return i + 1, class_match.group(2)
                        
            # If no class is found, return the end of the file as the position
            return len(lines), os.path.basename(file_path).split('.')[0].capitalize()
                
        except Exception as e:
            print(f"Error finding class for deletion method: {e}")
            return 1, os.path.basename(file_path).split('.')[0].capitalize()
    
    def _generate_deletion_method_example(self, file_path: str, class_name: str) -> str:
        """Generate an example deletion method based on the filename and class."""
        base_name = os.path.basename(file_path).split('.')[0]
        entity_name = base_name.replace('_', ' ').title().replace(' ', '')
        
        if file_path.endswith('.py'):
            return f"""
def delete_{base_name}(self, id):
    \"\"\"
    Permanently delete {base_name} data to comply with GDPR Article 17 (Right to Erasure).
    
    Args:
        id: The unique identifier of the {base_name} to delete
        
    Returns:
        bool: True if deletion was successful
    \"\"\"
    try:
        {entity_name}.objects.filter(id=id).delete()
        # Also delete any related personal data
        return True
    except Exception as e:
        logger.error(f"Error deleting {base_name}: {{e}}")
        return False
"""
        elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            return f"""
/**
 * Permanently delete {base_name} data to comply with GDPR Article 17 (Right to Erasure)
 * 
 * @param {base_name}Id The unique identifier of the {base_name} to delete
 * @returns Promise<boolean> True if deletion was successful
 */
async delete{entity_name}({base_name}Id) {{
  try {{
    await {entity_name}Model.findByIdAndDelete({base_name}Id);
    // Also delete any related personal data
    return true;
  }} catch (error) {{
    console.error(`Error deleting {base_name}:`, error);
    return false;
  }}
}}
"""
        else:
            return f"""
// Add a method to permanently delete {base_name} data to comply with GDPR Article 17 (Right to Erasure)
// Example implementation:
//
// public boolean delete{entity_name}(String id) {{
//     try {{
//         // Delete the {base_name} record
//         // Also delete any related personal data
//         return true;
//     }} catch (Exception e) {{
//         logger.error("Error deleting {base_name}: " + e.getMessage());
//         return false;
//     }}
// }}
"""
    
    def _deduplicate_issues(self, issues: List[GDPRIssue]) -> List[GDPRIssue]:
        """Deduplicate issues to avoid repetitive findings.
        Group issues that are in the same file, same issue type, and within proximity of each other."""
        if not issues:
            return []
            
        # Sort issues by file path, issue type, and line number
        sorted_issues = sorted(issues, key=lambda x: (x.file_path, x.issue_type, x.line_number))
        
        # Group issues by file and issue type
        grouped_issues = {}
        for issue in sorted_issues:
            key = (issue.file_path, issue.issue_type)
            if key not in grouped_issues:
                grouped_issues[key] = []
            grouped_issues[key].append(issue)
        
        # Process each group to merge nearby issues
        deduplicated = []
        for (file_path, issue_type), group in grouped_issues.items():
            # Sort by line number
            group.sort(key=lambda x: x.line_number)
            
            # Identify blocks of nearby lines (within 5 lines of each other)
            blocks = []
            current_block = [group[0]]
            
            for i in range(1, len(group)):
                current_issue = group[i]
                prev_issue = current_block[-1]
                
                # If lines are close to each other (within 5 lines)
                if current_issue.line_number - prev_issue.line_number <= 5:
                    current_block.append(current_issue)
                else:
                    blocks.append(current_block)
                    current_block = [current_issue]
            
            # Add the last block
            if current_block:
                blocks.append(current_block)
            
            # For each block, create a merged issue
            for block in blocks:
                # Skip if the block is empty
                if not block:
                    continue
                    
                # If the block has only one issue, keep it as is
                if len(block) == 1:
                    deduplicated.append(block[0])
                    continue
                    
                # Create a new consolidated issue for multiple related findings
                first_issue = block[0]
                last_issue = block[-1]
                
                # Create a merged line content if issues span multiple lines
                line_range = f"Lines {first_issue.line_number}-{last_issue.line_number}"
                
                # Collect unique content from the related issues
                unique_contents = set()
                for issue in block:
                    unique_contents.add(issue.line_content.strip())
                
                # Create a merged content with multiple lines if needed (limit to 3 examples)
                content_examples = list(unique_contents)[:3]
                merged_content = "\n".join(content_examples)
                
                # Create a merged issue with line range information
                merged_issue = GDPRIssue(
                    issue_type=first_issue.issue_type,
                    file_path=first_issue.file_path,
                    line_number=first_issue.line_number,
                    line_content=merged_content,
                    severity=first_issue.severity,
                    articles=first_issue.articles
                )
                
                # Add context information about the line range
                merged_issue.context = {
                    "is_merged": True,
                    "line_range": line_range,
                    "line_count": len(block),
                    "line_start": first_issue.line_number,
                    "line_end": last_issue.line_number
                }
                
                deduplicated.append(merged_issue)
        
        return deduplicated
    
    def export_report(self, output_file: str) -> None:
        """Export the scanning results to a JSON file."""
        report = {
            "scan_time": os.path.basename(self.target_dir),
            "total_issues": len(self.issues),
            "issues_by_severity": {
                "high": sum(1 for issue in self.issues if issue.severity == "high"),
                "medium": sum(1 for issue in self.issues if issue.severity == "medium"),
                "low": sum(1 for issue in self.issues if issue.severity == "low"),
            },
            "issues": [issue.to_dict() for issue in self.issues]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

    def _scan_python_file_with_ast(self, file_path: Path, content: str, lines: List[str]) -> List[GDPRIssue]:
        """Scan Python file using AST to properly exclude comments and docstrings."""
        issues = []
        
        try:
            # Parse Python code into AST
            tree = ast.parse(content)
            
            # Find docstrings to exclude them
            docstring_finder = DocstringFinder()
            docstring_finder.visit(tree)
            docstring_lines = docstring_finder.docstring_lines
            
            # Create a visitor to find potential GDPR issues
            visitor = GDPRCodeVisitor(str(file_path), lines, docstring_lines)
            visitor.visit(tree)
            
            # Add the issues found by the visitor
            issues.extend(visitor.issues)
            
        except Exception as e:
            print(f"Error in AST parsing for {file_path}: {e}")
            # If AST parsing fails, fall back to line-by-line scanning
            return self._scan_file_by_line(file_path, content, lines, ".py")
            
        return issues

    def _get_remediation_for_pattern_match(self, issue_type: str, line: str) -> str:
        """Generate a remediation suggestion for pattern-matched issues."""
        if issue_type == "data_transfer":
            return """## Data Transfer Recommendations:
            
1. **Verify adequacy decisions**: If transferring to countries outside the EU, check if they have an adequacy decision.
2. **Implement appropriate safeguards**: Use Standard Contractual Clauses (SCCs) or Binding Corporate Rules (BCRs).
3. **Document transfer impact assessments**: Evaluate and document the risks of each data transfer.
4. **Obtain explicit consent**: For specific transfers, ensure you have explicit consent.

```python
# Example implementation
def transfer_data(data, destination):
    # Check if destination has adequacy decision or appropriate safeguards
    if not is_adequate_destination(destination) and not has_appropriate_safeguards(destination):
        logging.warning(f"Transfer to {destination} lacks adequate protections")
        raise ComplianceError("Cannot transfer data without appropriate safeguards")
    
    # Log the transfer for accountability
    transfer_log.record(data_type, destination, datetime.now())
    
    # Proceed with transfer using encrypted channel
    return secure_transfer(data, destination)
```"""
            
        elif issue_type == "pii_collection":
            return """## PII Collection Recommendations:
            
1. **Obtain appropriate lawful basis**: Ensure you have a valid basis under Article 6 GDPR.
2. **Minimize data collection**: Only collect the data you actually need.
3. **Document purpose**: Clearly state why you're collecting each piece of information.
4. **Implement consent management**: Track and honor consent for each field.

```python
# Example implementation
def collect_user_data(form_data):
    # Define minimum required fields
    required_fields = ['email', 'name']
    
    # Validate lawful basis for each field
    for field, value in form_data.items():
        if not has_lawful_basis(field, user_consent):
            raise ValidationError(f"No lawful basis to collect {field}")
    
    # Store with purpose documentation
    user_data = {
        field: value for field, value in form_data.items() 
        if field in required_fields or has_explicit_consent(field)
    }
    
    # Add metadata
    user_data['_collection_purpose'] = 'account_creation'
    user_data['_legal_basis'] = 'consent'
    user_data['_consent_timestamp'] = datetime.now()
    
    return store_user_data(user_data)
```"""
            
        elif issue_type == "consent_issues":
            return """## Consent Management Recommendations:
            
1. **Make consent specific and granular**: Separate consent for different processing activities.
2. **Document consent**: Keep records of how and when consent was obtained.
3. **Make it easy to withdraw consent**: Provide simple mechanisms to opt out.
4. **No pre-ticked boxes**: Consent must be active, not passive.

```python
# Example implementation
def handle_consent_preferences(user_id, consent_settings):
    # Store granular consent preferences
    for purpose, is_granted in consent_settings.items():
        # Ensure it's an active choice, not a default
        if 'was_explicitly_chosen' not in consent_settings:
            raise ValidationError(f"Consent for {purpose} must be actively chosen")
        
        consent_store.set_preference(
            user_id=user_id,
            purpose=purpose,
            is_granted=is_granted,
            timestamp=datetime.now(),
            source="user_preferences_page"
        )
    
    # Update user record
    user = User.get(user_id)
    user.consent_last_updated = datetime.now()
    user.save()
    
    return get_current_consent_status(user_id)
```"""
        
        else:
            return f"""## Recommendation for {issue_type.replace('_', ' ')}:

Carefully review this code to ensure it follows GDPR best practices. Refer to the associated GDPR articles for specific compliance requirements."""
            
    def _contains_hardcoded_pii(self, line: str) -> bool:
        """Check if a string literal contains hardcoded PII like emails or phone numbers."""
        # These are higher precision patterns to avoid false positives
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        credit_card_pattern = r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}'
        ssn_pattern = r'\d{3}[-\s]?\d{2}[-\s]?\d{4}'
        
        # Skip if it's mock data or in a test context
        if MOCK_DATA_PATTERN.search(line) or DEV_TEST_CONTEXT_PATTERN.search(line):
            return False
            
        # Skip common documentation examples
        if "example" in line.lower() or "test" in line.lower() or "sample" in line.lower():
            if re.search(email_pattern, line) or re.search(phone_pattern, line):
                # This looks like an example, not real PII
                return False
                
        return (re.search(email_pattern, line) is not None or
                re.search(phone_pattern, line) is not None or
                re.search(credit_card_pattern, line) is not None or
                re.search(ssn_pattern, line) is not None)


class GDPRCodeVisitor(ast.NodeVisitor):
    """AST Visitor for identifying potential GDPR compliance issues in Python code."""

    # Personal Identifiable Information field terms - expanded
    PII_TERMS = [
        # Basic identifiers
        "name", "email", "address", "phone", "birth", "ssn", "social_security",
        "passport", "license", "gender", "age", "zip", "postal", "location",
        "ip_address", "ip", "geo", "latitude", "longitude", 
        
        # Financial data
        "credit_card", "card_number", "cvv", "expiry", "payment", "bank_account",
        "account_number", "iban", "swift", "financial", "tax", "invoice", "payment_info",
        
        # Authentication
        "password", "pwd", "passwd", "secret", "token", "api_key", "auth", "credential",
        
        # Health and biometric
        "health", "medical", "biometric", "facial", "fingerprint", "genetic", 
        "diagnosis", "patient", "healthcare", "prescription", "treatment",
        
        # Demographic and sensitive
        "religion", "political", "sexual", "ethnic", "racial", "nationality",
        "citizen", "immigrant", "origin", "income", "salary", "marital", "family",
        
        # ID numbers
        "id_number", "identifier", "uuid", "unique", "driverlicense", "passport_number",
        "tax_id", "vat", "social_number",
        
        # Common PII aliases
        "user", "customer", "client", "person", "individual", "member", "contact",
        "profile", "account", "subscriber"
    ]

    # Terms that are commonly used for variables but don't actually indicate PII
    # when used in certain contexts - helps reduce false positives
    COMMON_VARIABLE_TERMS = [
        # Common variable/parameter names that shouldn't trigger alone
        "user_id", "id", "customer_id", "client_id", "account_id", "member_id",
        "name_field", "username", "user_name", "login", "handle",
        "user_type", "user_role", "user_level", "user_status", "user_group",
        "user_agent", "user_input", "user_option", "user_value", "user_data",
        "account_type", "account_status", "account_level", "account_group",
        "customer_type", "customer_segment", "customer_tier", "customer_group",
        # UI-related terms
        "profile_page", "user_panel", "account_view", "account_panel",
        # Common framework/library terms
        "user_model", "user_controller", "user_service", "user_repository",
        "account_model", "account_controller", "account_service",
        "profile_component", "profile_view", "profile_template",
        # Numeric or coded identifiers
        "user_no", "user_ref", "user_uuid", "uuid"
    ]

    # Exclude these patterns from being flagged as PII
    EXCLUDE_PATTERNS = [
        r"test_user",
        r"sample_user",
        r"example_user",
        r"dummy_user",
        r"mock_user",
        r"fake_user",
        r"dev_user",
        r"local_user",
        r"test_account",
        r"debug_account"
    ]

    # Data storage and database operation terms
    DB_STORAGE_TERMS = [
        "save", "store", "insert", "create", "add", "update", "upsert", 
        "write", "put", "persist", "cache", "upload", "record", "log",
        "commit", "push", "post", "set", "register", "archive", "backup"
    ]

    # Data processing operation terms
    DATA_PROCESSING_TERMS = [
        "process", "analyze", "compute", "calculate", "handle", "manage", "transform",
        "parse", "filter", "normalize", "validate", "format", "manipulate", "convert",
        "aggregate", "classify", "identify", "verify", "check", "match", "track"
    ]
    
    # Security-related terms that might indicate security measures
    SECURITY_TERMS = [
        "encrypt", "hash", "secure", "protect", "ssl", "tls", "https", 
        "certificate", "verify", "validate", "authenticate", "authorization",
        "salt", "sign", "signature", "cipher", "checksum", "integrity", "trust",
        "access_control", "firewall", "vpn", "private", "public_key", "private_key", 
        "security", "sha", "md5", "bcrypt", "scrypt", "argon"
    ]
    
    # Test environment indicators
    TEST_INDICATORS = [
        "test", "mock", "fake", "dummy", "sample", "example", "dev", 
        "local", "sandbox", "development", "fixture", "stub", "demo",
        "simulation", "_test", "test_", "testing", "unittest", "pytest",
        "spec", "assert", "integration", "bench", "performance"
    ]
    
    # Compliance and privacy keywords
    COMPLIANCE_TERMS = [
        "gdpr", "ccpa", "hipaa", "compliance", "consent", "opt_in", "opt_out",
        "privacy", "policy", "legal", "regulation", "right_to", "erasure", "forgotten",
        "dpa", "data_processing", "agreement", "controller", "processor", "dpo",
        "impact_assessment", "dpia", "lawful", "subject_access", "retention"
    ]

    def __init__(self, file_path: str, lines=None, non_code_lines=None):
        """Initialize the visitor with file info."""
        self.file_path = file_path
        self.issues = []
        self.lines = lines or []
        self.non_code_lines = non_code_lines or set()
        self.current_class = None
        self.current_function = None
        self.pii_fields = set()
        
    def _is_test_file(self, file_path: str) -> bool:
        """Check if the file is likely a test file."""
        file_path_lower = file_path.lower()
        return any(pattern in file_path_lower for pattern in ["test_", "_test", "tests/", "/tests/", "mock_", "_mock"])
        
    def visit_FunctionDef(self, node):
        """Visit a function definition to check for GDPR issues."""
        old_function = self.current_function
        self.current_function = node.name
        
        # Skip docstrings and test functions
        if (self._is_in_docstring(node) or
            node.name.startswith(('test_', 'mock_', 'fake_', 'dummy_', 'sample_', 'example_')) or
            node.name.endswith(('_test', '_fixture', '_mock', '_fake', '_sample', '_example')) or
            self._is_test_file(self.file_path) or
            any(term in node.name.lower() for term in self.TEST_INDICATORS)):
            self.generic_visit(node)
            self.current_function = old_function
            return
            
        # Check for explicit test-related decorators
        if hasattr(node, 'decorator_list') and node.decorator_list:
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and any(test_term in decorator.id.lower() 
                                                          for test_term in ['test', 'mock', 'fixture']):
                    self.generic_visit(node)
                    self.current_function = old_function
                    return
            
        # Check PII search functions
        if self._is_search_function(node.name):
            self._check_pii_search_function(node)
            
        # Check data storage functions
        elif any(term in node.name.lower() for term in self.DB_STORAGE_TERMS):
            self._check_data_storage_function(node)
            
        # Check data processing functions
        elif any(term in node.name.lower() for term in self.DATA_PROCESSING_TERMS):
            self._check_data_processing_function(node)
            
        # Check security implementations in security-related functions
        elif any(term in node.name.lower() for term in self.SECURITY_TERMS):
            self._check_security_implementation(node)
            
        # Check compliance functions
        elif any(term in node.name.lower() for term in self.COMPLIANCE_TERMS):
            self._check_compliance_implementation(node)
            
        # Check for PII arguments regardless of function type
        self._check_pii_in_arguments(node)
            
        self.generic_visit(node)
        self.current_function = old_function
        
    def _is_in_docstring(self, node) -> bool:
        """Check if code is within a docstring example."""
        docstring = ast.get_docstring(node)
        if not docstring:
            return False
        
        # Check for common doctest indicators
        return ">>>" in docstring or "..." in docstring
    
    def _check_pii_in_arguments(self, node):
        """Check if a function has PII in its arguments without proper protection."""
        pii_args = []
        
        # Check arguments for PII fields
        for arg in node.args.args:
            if hasattr(arg, 'arg'):
                arg_name = arg.arg.lower()
                # Skip if it's a common variable that shouldn't trigger when used alone
                if arg_name in map(str.lower, self.COMMON_VARIABLE_TERMS):
                    continue
                    
                # Skip if it matches exclude patterns
                if any(re.search(pattern, arg_name, re.IGNORECASE) for pattern in self.EXCLUDE_PATTERNS):
                    continue
                    
                # Check for PII terms
                if any(term in arg_name for term in self.PII_TERMS):
                    pii_args.append(arg.arg)
                
        if not pii_args:
            return
            
        # Check function body for validation/protection of these arguments
        validation_patterns = ['validate', 'verify', 'check', 'consent', 'authorize', 
                             'permission', 'encrypt', 'hash', 'sanitize', 'anonymize',
                             'auth', 'permission', 'allowed', 'legal_basis', 'mask',
                             'minimum', 'required', 'ensure', 'protected']
        
        # Get the function body as text
        if not self.lines:
            return
            
        try:
            body_start = node.body[0].lineno - 1
            body_end = node.body[-1].end_lineno
            body_text = "\n".join(self.lines[body_start:body_end])
            
            # Check if any validation pattern exists in the body
            if any(pattern in body_text.lower() for pattern in validation_patterns):
                return  # Validation might be present
                
            # Create GDPR issue for unprotected PII arguments
            issue = GDPRIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="pii_processing",
                description=f"Function '{node.name}' accepts personal data ({', '.join(pii_args)}) without apparent validation",
                remediation=f"""
Implement validation and protection for personal data parameters:

```python
def {node.name}({', '.join(node.args.args)}):
    # Validate authorization to access this data
    if not current_user.has_permission('process_{pii_args[0]}'):
        raise PermissionError(f"Unauthorized to process {pii_args[0]}")
    
    # Verify consent for this specific purpose
    purpose = 'function_specific_purpose'
    if not has_valid_consent_for(user_id, purpose):
        return error_response("No valid consent for this operation")
    
    # Log the access for accountability
    log_pii_access('{pii_args[0]}', current_user.id, purpose)
    
    # Process with minimized scope
    # ... your function logic ...
```

Ensure you:
1. Validate authorization before processing
2. Check for appropriate consent
3. Log access for accountability
4. Document the purpose of data processing
                """,
                articles=["5", "6", "25"]  # Articles for lawfulness and data protection by design
            )
            
            self.issues.append(issue)
            
        except (AttributeError, IndexError):
            # Skip if we can't analyze the body properly
            pass
        
    def _is_search_function(self, func_name: str) -> bool:
        """
        Determine if a function is likely searching for data based on its name.
        
        Args:
            func_name: Name of the function
            
        Returns:
            True if the function appears to be a search function, False otherwise
        """
        search_indicators = [
            "search", "find", "lookup", "query", "fetch", "retrieve",
            "select", "filter", "locate", "seek", "scan", "browse", "match",
            "lookup", "examine", "read", "get_by", "find_by"
        ]
        
        # Avoid flagging getter functions that aren't really searches
        if func_name.lower() == 'get' or func_name.lower() == 'get_data':
            return False
            
        # Avoid flagging common utility functions
        if any(func_name.lower() == term for term in ["get_config", "get_settings", "get_options"]):
            return False
            
        func_name_lower = func_name.lower()
        return any(indicator in func_name_lower for indicator in search_indicators)
    
    def _check_pii_search_function(self, node):
        """Check a function that might be searching for PII."""
        # Skip if already verified as test code
        if any(term in self.current_function.lower() for term in self.TEST_INDICATORS):
            return
            
        # Skip if in documentation or examples directories
        if self._is_in_docs_or_examples_directory():
            return
            
        # Skip if this looks like a utility or helper function
        if any(term in self.current_function.lower() for term in ['util', 'helper', 'format', 'display', 'render']):
            return
        
        # Check arguments for PII fields
        pii_visitor = PIIVisitor(self.PII_TERMS)
        pii_visitor.visit(node)
        
        # Check for PII in function body
        pii_fields_body = []
        for field in pii_visitor.pii_fields:
            # Skip common generic terms that don't necessarily indicate PII
            if field.lower() in map(str.lower, self.COMMON_VARIABLE_TERMS):
                continue
                
            # Skip test/mock data patterns
            if any(pattern in field.lower() for pattern in ['test', 'mock', 'dummy', 'sample', 'example']):
                continue
                
            if any(term in field.lower() for term in self.PII_TERMS):
                pii_fields_body.append(field)
                
        # Only create issues if we found potential PII fields
        pii_fields = pii_fields_body
        if not pii_fields:
            return
            
        # Look for authorization or consent checks
        has_authorization = False
        has_consent_check = False
        has_logging = False
        
        for child_node in ast.walk(node):
            if isinstance(child_node, ast.Call):
                func_name = ""
                if isinstance(child_node.func, ast.Name):
                    func_name = child_node.func.id
                elif isinstance(child_node.func, ast.Attribute):
                    func_name = child_node.func.attr
                    
                auth_terms = ["authorize", "permission", "access_control", "authenticate", "auth"]
                consent_terms = ["consent", "opt_in", "permission", "agreed", "acceptance"]
                logging_terms = ["log", "audit", "record", "track"]
                
                if any(term in func_name.lower() for term in auth_terms):
                    has_authorization = True
                if any(term in func_name.lower() for term in consent_terms):
                    has_consent_check = True
                if any(term in func_name.lower() for term in logging_terms):
                    has_logging = True
        
        # If all checks pass, no need to create an issue
        if has_authorization and has_consent_check and has_logging:
            return
                
        # Create GDPR issue for PII search
        missing_elements = []
        if not has_authorization:
            missing_elements.append("authorization checks")
        if not has_consent_check:
            missing_elements.append("consent verification")
        if not has_logging:
            missing_elements.append("access logging")
                
        issue = GDPRIssue(
            file_path=self.file_path,
            line_number=node.lineno,
            issue_type="pii_search_function",
            description=f"Function '{node.name}' searches for personal data ({', '.join(pii_fields)}) without {' and '.join(missing_elements)}",
            remediation=f"""
Implement proper access controls and consent verification before searching for personal data:

```python
def {node.name}(...):
    # Verify authorization and consent
    if not has_authorization(current_user, 'search_{pii_fields[0]}'):
        raise AccessDeniedError("Insufficient permissions to search this data")
        
    # Verify legal basis for processing
    legal_basis = get_legal_basis_for_processing('{pii_fields[0]}')
    if not legal_basis:
        log_unauthorized_attempt(current_user, '{pii_fields[0]}')
        raise ComplianceError("No legal basis for processing this data")
    
    # Log access for auditing
    log_data_access(user_id=current_user.id, 
                    data_type='{pii_fields[0]}',
                    purpose='search',
                    timestamp=datetime.now())
    
    # Implement data minimization for search results
    results = perform_search(...)
    return minimize_pii_in_results(results, authorized_fields_for_user(current_user))
```

Additionally:
1. Use non-PII identifiers when possible instead of direct PII fields
2. Document the purpose and legal basis for each search operation
3. Implement proper error handling that doesn't leak sensitive information
                """,
            articles=["5", "6", "25", "32"]  # Article 5 for lawfulness, 6 for legal basis, 25 for protection by design, 32 for security
        )
        
        # Add confidence score based on PII field quality
        confidence = min(0.5 + (len(pii_fields) * 0.1), 0.9)
        setattr(issue, 'confidence', confidence)
        
        self.issues.append(issue)
    
    def _check_compliance_implementation(self, node):
        """Check compliance functions for completeness."""
        compliance_function_patterns = {
            "consent": ["withdraw", "revoke", "timestamp", "purpose", "explicit"],
            "erasure": ["delete", "remove", "purge", "anonymize", "cascade"],
            "data_portability": ["export", "format", "machine_readable", "transfer"],
            "access_request": ["download", "provide", "retrieve", "copy"]
        }
        
        # Function source text
        try:
            if not self.lines:
                return
                
            start_line = node.lineno - 1
            end_line = node.end_lineno
            function_text = "\n".join(self.lines[start_line:end_line])
            
            # Check if function name matches compliance function but lacks implementation
            for compliance_type, required_terms in compliance_function_patterns.items():
                if compliance_type in node.name.lower():
                    missing_terms = [term for term in required_terms if term not in function_text.lower()]
                    
                    if len(missing_terms) > len(required_terms) / 2:  # More than half of required terms missing
                        # Pre-process the string joins to avoid f-string with backslash issues
                        missing_terms_implementation = "# " + "\n    # ".join([f"Implement {term}" for term in missing_terms])
                        
                        issue = GDPRIssue(
                            file_path=self.file_path,
                            line_number=node.lineno,
                            issue_type="compliance_implementation",
                            description=f"Function '{node.name}' appears to be a {compliance_type.replace('_', ' ')} function but may be incomplete",
                            remediation=f"""
Enhance your {compliance_type.replace('_', ' ')} implementation to include: {', '.join(missing_terms)}

```python
def {node.name}(...):
    # Document the purpose
    purpose = "Handling {compliance_type.replace('_', ' ')} request"
    
    # Verify user identity
    if not verify_identity(user_id, provided_credentials):
        return error_response("Identity verification failed")
    
    # Log the request for accountability
    log_compliance_request(user_id, '{compliance_type}', datetime.now())
    
    # Implement the actual functionality with required elements
    {missing_terms_implementation}
    
    # Provide confirmation to the user
    return success_response("Your {compliance_type.replace('_', ' ')} request has been processed")
```
                            """,
                            articles=self._get_relevant_articles_for_compliance(compliance_type)
                        )
                        
                        # Higher confidence since the function name directly matches compliance function
                        setattr(issue, 'confidence', 0.85)
                        self.issues.append(issue)
                        
        except (AttributeError, IndexError):
            pass
    
    def _get_relevant_articles_for_compliance(self, compliance_type: str) -> List[str]:
        """Get relevant GDPR articles for a compliance function type."""
        article_mapping = {
            "consent": ["7", "8"],            # Conditions for consent
            "erasure": ["17", "19"],          # Right to erasure & notification
            "data_portability": ["20"],       # Right to data portability
            "access_request": ["15", "12"],   # Right of access & transparency
            "rectification": ["16", "19"],    # Right to rectification
            "restriction": ["18", "19"],      # Right to restriction of processing
            "breach": ["33", "34"],           # Breach notification
            "objection": ["21"]               # Right to object
        }
        
        return article_mapping.get(compliance_type, ["5", "12"])  # Default to basic principles
            
    def _check_security_implementation(self, node):
        """Check security implementations in a function that handles security-related concerns."""
        # Similar implementation as before...
        # ... existing code ...
        
    def _check_data_storage_function(self, node):
        """Check a function that might be storing PII."""
        # Similar implementation as before...
        # ... existing code ...
        
    def _check_data_processing_function(self, node):
        """Check a function that might be processing PII."""
        # Similar implementation as before...
        # ... existing code ...
        
    def visit_ClassDef(self, node):
        """Visit a class definition to check for GDPR issues."""
        # Skip test classes
        if (node.name.startswith('Test') or 
            node.name.endswith('Test') or 
            self._is_test_file(self.file_path) or
            any(term in node.name for term in self.TEST_INDICATORS)):
            return
            
        # Check if class is a model/entity that might contain PII
        self._check_model_class(node)
        
        # Continue normal visit
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def _check_model_class(self, node):
        """Check if a class is a model or entity that might store PII."""
        model_indicators = ['model', 'entity', 'record', 'table', 'document', 'schema']
        is_model = False
        
        # Skip test/mock models
        if any(term in node.name.lower() for term in ['test', 'mock', 'fake', 'dummy', 'example', 'sample']):
            return
            
        # Skip if in documentation or examples directories
        if self._is_in_docs_or_examples_directory():
            return
        
        # Check class name and bases for model indicators
        if any(indicator in node.name.lower() for indicator in model_indicators):
            is_model = True
        
        for base in node.bases:
            if isinstance(base, ast.Name) and any(indicator in base.id.lower() for indicator in model_indicators):
                is_model = True
                
        if not is_model:
            return
            
        # Look for PII fields in class attributes
        pii_fields = []
        
        for child in node.body:
            # Look for field definitions
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id
                        # Skip common generic terms that don't necessarily indicate PII
                        if field_name.lower() in map(str.lower, self.COMMON_VARIABLE_TERMS):
                            continue
                            
                        # Skip test/mock data patterns
                        if any(pattern in field_name.lower() for pattern in ['test', 'mock', 'dummy', 'sample', 'example']):
                            continue
                            
                        if any(term in field_name.lower() for term in self.PII_TERMS):
                            pii_fields.append(field_name)
                            
        if not pii_fields:
            return
            
        # Check for data protection annotations/methods
        has_retention_policy = False
        has_field_protection = False
        
        # Check for privacy-enhancing methods or annotations
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and any(term in child.name.lower() for term in 
                                                     ['anonymize', 'delete', 'remove', 'encrypt', 'protect', 'clean']):
                has_field_protection = True
                
            if hasattr(child, 'decorator_list') and child.decorator_list:
                for decorator in child.decorator_list:
                    if isinstance(decorator, ast.Name) and any(term in decorator.id.lower() for term in 
                                                          ['retention', 'encrypt', 'protect', 'sensitive']):
                        has_retention_policy = True
                        
        if has_retention_policy and has_field_protection:
            return  # Both protections in place
            
        # Create an issue for model class with PII
        missing_protections = []
        if not has_retention_policy:
            missing_protections.append("data retention policy")
        if not has_field_protection:
            missing_protections.append("field-level protection")
            
        # Pre-process the string joins to avoid f-string with backslash issues
        newline_join_fields_1 = "# " + "\n        # ".join([f"self.{field} = generate_anonymous_value()" for field in pii_fields])
        newline_join_fields_2 = "\n            ".join([f"'{field}': self.{field}," for field in pii_fields])
            
        issue = GDPRIssue(
            file_path=self.file_path,
            line_number=node.lineno,
            issue_type="pii_storage",
            description=f"Class '{node.name}' appears to be a data model containing PII ({', '.join(pii_fields)}) without {' or '.join(missing_protections)}",
            remediation=f"""
Enhance data model with proper PII protection:

```python
class {node.name}:
    # Add retention metadata
    _retention_period = timedelta(days=365)  # How long to keep this data
    _data_purpose = "Specific business purpose"  # Why you collect this data
    
    # For sensitive PII fields, add encryption or pseudonymization
    @property
    def {pii_fields[0]}(self):
        # Return decrypted version only when authorized
        if not current_user.has_permission('view_{pii_fields[0]}'):
            return None  # Or masked version
        return decrypt(self._encrypted_{pii_fields[0]})
        
    @{pii_fields[0]}.setter
    def {pii_fields[0]}(self, value):
        # Store encrypted version
        self._encrypted_{pii_fields[0]} = encrypt(value)
        
    # Add data deletion methods
    def anonymize(self):
        # Replace PII with anonymous values
        {newline_join_fields_1}
        self.anonymized_at = datetime.now()
        
    # Add data export for portability
    def export_data(self):
        return {{
            {newline_join_fields_2}
            "exported_at": datetime.now().isoformat()
        }}
```

Additionally:
1. Document the legal basis for storing each PII field
2. Implement data minimization - store only what's necessary
3. Add audit logging for data access and modifications
            """,
            articles=["5", "25", "32", "89"]  # Lawfulness, protection by design, security, storage limitation
        )
        
        setattr(issue, 'confidence', 0.8)
        self.issues.append(issue)
            
    def visit_Assign(self, node):
        """Visit assignments to check for potential PII storage."""
        if self._is_test_file(self.file_path) or self._is_in_docstring(node) or self._is_in_docs_or_examples_directory():
            self.generic_visit(node)
            return
            
        # Check if assignment is storing PII without protection
        target_name = ""
        
        # Get the target variable name
        if isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
        elif isinstance(node.targets[0], ast.Attribute):
            target_name = node.targets[0].attr
            
        # Skip common non-PII variables even if they contain PII terms
        if target_name.lower() in map(str.lower, self.COMMON_VARIABLE_TERMS):
            self.generic_visit(node)
            return
            
        # Skip test/mock data patterns
        if any(pattern in target_name.lower() for pattern in ['test', 'mock', 'dummy', 'sample', 'example']):
            self.generic_visit(node)
            return
        
        # Check if target or value contains PII term
        if any(term in target_name.lower() for term in self.PII_TERMS):
            # Check if value is a raw string literal (hardcoded PII)
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                # Skip if the string is a test/example email or obviously fake data
                string_value = str(node.value.value).lower()
                if (("test" in string_value or "example" in string_value or "sample" in string_value or 
                     "fake" in string_value or "dummy" in string_value) or
                    any(mock_pattern.lower() in string_value for mock_pattern in MOCK_DATA_PATTERNS)):
                    self.generic_visit(node)
                    return
                    
                # This is a hardcoded PII assignment
                issue = GDPRIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    issue_type="hardcoded_pii",
                    description=f"Hardcoded PII value assigned to '{target_name}'",
                    remediation="""
Avoid hardcoding personal data in your code:

```python
# Instead of:
# email = "user@example.com"  # Hardcoded PII

# Better approach:
email = get_email_from_secure_source()  # From environment, config, or database

# Or for testing:
if is_test_environment():
    email = "test@example.com"  # Clearly test data
else:
    email = get_user_email_securely()
```

If this is test data, mark it clearly as such or use data factories.
                    """,
                    articles=["5", "25"]  # Lawfulness and protection by design
                )
                
                setattr(issue, 'confidence', 0.75)
                self.issues.append(issue)
                
        self.generic_visit(node)

class PIIVisitor(ast.NodeVisitor):
    """AST visitor that identifies PII fields in code."""
    
    def __init__(self, pii_terms, exclude_terms=None):
        self.pii_terms = pii_terms
        self.pii_fields = []
        self.exclude_terms = exclude_terms or ["test", "mock", "example", "sample", "dummy", "fake"]
        
    def is_pii(self, name):
        """Check if a name contains PII terms."""
        if not name or not isinstance(name, str):
            return False
            
        # Skip common test/mock patterns
        if any(exclude in name.lower() for exclude in self.exclude_terms):
            return False
            
        return any(term in name.lower() for term in self.pii_terms)
    
    def add_pii_field(self, field_name):
        """Add a field to the PII fields list if it's not already there."""
        if field_name and self.is_pii(field_name) and field_name not in self.pii_fields:
            self.pii_fields.append(field_name)
            
    def visit_Name(self, node):
        """Check variable names for PII terms."""
        self.add_pii_field(node.id)
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        """Check assignment targets for PII terms."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.add_pii_field(target.id)
            elif isinstance(target, ast.Attribute):
                self.add_pii_field(target.attr)
                
        # Also check the value for PII references
        self.visit(node.value)
        
    def visit_Call(self, node):
        """Check function calls and their arguments for PII terms."""
        # Check function name if it's an attribute
        if isinstance(node.func, ast.Attribute):
            self.add_pii_field(node.func.attr)
            
        # Check function call arguments
        for arg in node.args:
            if isinstance(arg, ast.Name):
                self.add_pii_field(arg.id)
            elif isinstance(arg, ast.Attribute):
                self.add_pii_field(arg.attr)
                
        # Check keyword arguments
        for keyword in node.keywords:
            self.add_pii_field(keyword.arg)
            if isinstance(keyword.value, ast.Name):
                self.add_pii_field(keyword.value.id)
                
        # Continue visiting function call parts
        self.generic_visit(node)
        
    def visit_Attribute(self, node):
        """Check object attributes for PII terms."""
        self.add_pii_field(node.attr)
        # Also check the value object
        self.visit(node.value)
        
    def visit_arg(self, node):
        """Check function parameters for PII terms."""
        self.add_pii_field(node.arg)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        """Check function names and arguments for PII references."""
        self.add_pii_field(node.name)
        
        # Check function parameters
        for arg in node.args.args:
            if hasattr(arg, 'arg'):
                self.add_pii_field(arg.arg)
                
        # Visit function body
        self.generic_visit(node)
        
    def visit_Subscript(self, node):
        """Check dictionary/list access for PII terms."""
        if isinstance(node.slice, ast.Index):
            # For Python 3.8 and earlier
            if hasattr(node.slice, 'value') and isinstance(node.slice.value, ast.Constant):
                self.add_pii_field(node.slice.value.value)
            elif hasattr(node.slice, 'value') and isinstance(node.slice.value, ast.Str):
                self.add_pii_field(node.slice.value.s)
        elif isinstance(node.slice, ast.Constant):
            # For Python 3.9+
            if isinstance(node.slice.value, str):
                self.add_pii_field(node.slice.value)
                
        # Also visit the value being subscripted
        self.visit(node.value)

class DocstringFinder(ast.NodeVisitor):
    """AST visitor that finds all docstrings in a Python file."""
    def __init__(self):
        self.docstring_lines = set()
        
    def visit_Module(self, node):
        self._check_docstring(node)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        self._check_docstring(node)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        self._check_docstring(node)
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        self._check_docstring(node)
        self.generic_visit(node)
        
    def visit_Expr(self, node):
        """Check for standalone string literals that might be used as comments."""
        if isinstance(node.value, ast.Str):
            # Add the line where this string literal appears
            start_line = node.lineno
            # Count lines in the string
            num_lines = node.value.s.count('\n') + 1
            for i in range(start_line, start_line + num_lines):
                self.docstring_lines.add(i)
        self.generic_visit(node)
        
    def _check_docstring(self, node):
        """Check if the node has a docstring and record its line numbers."""
        docstring = ast.get_docstring(node)
        if docstring:
            if hasattr(node, 'body') and len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                start_line = node.body[0].lineno
                # Count lines in the docstring (including triple quotes)
                num_lines = docstring.count('\n') + 2
                for i in range(start_line, start_line + num_lines):
                    self.docstring_lines.add(i)

def extract_countries(text: str) -> List[str]:
    """Extract country names from a text string."""
    # This is a simplified version - in a real implementation, 
    # we'd use NER or a more sophisticated approach
    common_countries = [
        'usa', 'us', 'united states', 'america',
        'uk', 'united kingdom', 'england',
        'canada', 'australia', 'china', 'russia',
        'india', 'japan', 'brazil', 'germany',
        'france', 'italy', 'spain'
    ]
    
    found_countries = []
    for country in common_countries:
        if re.search(r'\b' + re.escape(country) + r'\b', text.lower()):
            found_countries.append(country)
            
    return found_countries 

    def _is_in_docs_or_examples_directory(self) -> bool:
        """Check if the file is in a documentation or examples directory."""
        normalized_path = self.file_path.lower()
        for doc_dir in ['docs', 'doc', 'documentation', 'examples', 'samples', 'test', 'tests']:
            if f'/{doc_dir}/' in normalized_path.replace('\\', '/'):
                return True
        return False