"""
Meta-learning module for Levox GDPR compliance scanner.

This module implements learning from user feedback to reduce
false positives and false negatives in GDPR compliance scanning.
"""
import os
import json
import pickle
import datetime
import re
import hashlib
import math
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional, Union
import numpy as np
from collections import defaultdict, Counter
import difflib
import logging

# Version information
VERSION = "1.5.2"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("meta_learning")

# Check if scikit-learn is available for advanced features
SKLEARN_AVAILABLE = False
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except (ImportError, ValueError):
    # Simple fallback for TF-IDF when sklearn is not available
    class SimpleTfidfVectorizer:
        """Simple implementation of TF-IDF for when sklearn is not available"""
        def __init__(self, max_features=1000, stop_words=None):
            self.max_features = max_features
            self.stop_words = stop_words or []
            self.vocabulary_ = {}
            self.idf_ = {}
            
        def fit_transform(self, texts):
            """Simple implementation of fit_transform"""
            # Create vocabulary
            word_counts = defaultdict(int)
            for text in texts:
                for word in self._tokenize(text):
                    if word not in self.stop_words:
                        word_counts[word] += 1
            
            # Take top max_features words
            sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            self.vocabulary_ = {word: idx for idx, (word, _) in 
                              enumerate(sorted_words[:self.max_features])}
            
            # Calculate document frequency
            doc_freq = defaultdict(int)
            for text in texts:
                words = set(self._tokenize(text))  # Count each word only once per document
                for word in words:
                    if word in self.vocabulary_:
                        doc_freq[word] += 1
            
            # Calculate IDF
            n_docs = len(texts)
            self.idf_ = {word: np.log(n_docs / (1 + doc_freq.get(word, 0))) + 1.0 
                        for word in self.vocabulary_}
            
            # Transform texts to TF-IDF vectors
            vectors = []
            for text in texts:
                vector = np.zeros(len(self.vocabulary_))
                words = self._tokenize(text)
                for word in words:
                    if word in self.vocabulary_:
                        idx = self.vocabulary_[word]
                        tf = words.count(word) / len(words) if len(words) > 0 else 0
                        vector[idx] = tf * self.idf_.get(word, 0)
                vectors.append(vector)
            
            return np.array(vectors)
            
        def transform(self, texts):
            """Transform new texts using existing vocabulary"""
            vectors = []
            for text in texts:
                vector = np.zeros(len(self.vocabulary_))
                words = self._tokenize(text)
                for word in words:
                    if word in self.vocabulary_:
                        idx = self.vocabulary_[word]
                        tf = words.count(word) / len(words) if len(words) > 0 else 0
                        vector[idx] = tf * self.idf_.get(word, 0)
                vectors.append(vector)
            
            return np.array(vectors)
            
        def _tokenize(self, text):
            """Simple tokenization"""
            if not text:
                return []
            
            # Remove punctuation and split
            for char in ',.(){}[]=/\\\'":;+*':
                text = text.replace(char, ' ')
            
            # Return lowercase tokens, excluding stop words
            return [token.lower() for token in text.split() 
                   if token and token.lower() not in self.stop_words]
    
    def simple_cosine_similarity(a, b):
        """Simple implementation of cosine similarity"""
        if a.shape[0] == 0 or b.shape[0] == 0:
            return np.array([])
            
        # Compute similarity for each pair
        result = np.zeros((a.shape[0], b.shape[0]))
        for i in range(a.shape[0]):
            for j in range(b.shape[0]):
                dot_product = np.dot(a[i], b[j])
                norm_a = np.linalg.norm(a[i])
                norm_b = np.linalg.norm(b[j])
                
                if norm_a > 0 and norm_b > 0:
                    result[i, j] = dot_product / (norm_a * norm_b)
                else:
                    result[i, j] = 0.0
                    
        return result

# Type definitions for clarity
ScanResult = Dict[str, Any]  # Complete scan result
IssueFeatures = Dict[str, Any]  # Features extracted from an issue
FeedbackType = str  # "false_positive", "false_negative", "true_positive"
ConfidenceAdjustment = float  # Adjustment to confidence scores

# Optional imports for telemetry
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class MetaLearningEngine:
    """
    Meta-learning engine that adapts GDPR issue detection based on feedback.
    """
    def __init__(self, data_dir: str = None, quiet: bool = False, enable_telemetry: bool = False):
        """
        Initialize the meta-learning engine.
        
        Args:
            data_dir: Directory to store learning data
            quiet: If True, suppress output messages
            enable_telemetry: If True, share anonymized statistics (opt-in only)
        """
        # Set up storage location for learning data
        self.data_dir = data_dir or os.path.join(os.path.expanduser("~"), ".levox", "meta_learning")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Paths for storing feedback and model data
        self.feedback_path = os.path.join(self.data_dir, "feedback_data.json")
        self.model_path = os.path.join(self.data_dir, "meta_model.pkl")
        self.allowlist_path = os.path.join(self.data_dir, "auto_allowlist.json")
        self.telemetry_consent_path = os.path.join(self.data_dir, "telemetry_consent.json")
        
        # Initialize data structures
        self.feedback_data: List[Dict[str, Any]] = []
        self.issue_patterns: Dict[str, Dict[str, Any]] = {}
        self.context_adjustments: Dict[str, Dict[str, float]] = {}
        self.token_weights: Dict[str, Dict[str, float]] = {}
        self.file_pattern_scores: Dict[str, float] = {}
        self.auto_allowlist: Dict[str, List[str]] = {
            "files": [],
            "patterns": [],
            "extensions": []
        }
        
        # TF-IDF vectorizer for semantic similarity
        self.vectorizer = None
        self.similarity_matrix = None
        self.vectorized_texts = None
        self.corpus_metadata = []
        
        # Verbosity control
        self.quiet = quiet
        
        # Telemetry settings (off by default, requires explicit consent)
        self.enable_telemetry = enable_telemetry
        self.telemetry_consent = self._load_telemetry_consent()
        if enable_telemetry and not self.telemetry_consent.get('consent_given', False):
            self.enable_telemetry = False
            if not quiet:
                print("Telemetry disabled: user consent not given. Use set_telemetry_consent() to enable.")
        
        # Load existing data if available
        self._load_data()
        
    def _load_data(self):
        """Load existing feedback and model data if available."""
        try:
            if os.path.exists(self.feedback_path):
                with open(self.feedback_path, 'r') as f:
                    self.feedback_data = json.load(f)
                if not self.quiet:
                    print(f"Loaded {len(self.feedback_data)} feedback records")
        except Exception as e:
            if not self.quiet:
                print(f"Error loading feedback data: {e}")
            self.feedback_data = []
            
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.issue_patterns = model_data.get('issue_patterns', {})
                    self.context_adjustments = model_data.get('context_adjustments', {})
                    self.token_weights = model_data.get('token_weights', {})
                    self.file_pattern_scores = model_data.get('file_pattern_scores', {})
        except Exception as e:
            if not self.quiet:
                print(f"Error loading model data: {e}")
            # Initialize with empty data structures
            self.issue_patterns = {}
            self.context_adjustments = {}
            self.token_weights = {}
            self.file_pattern_scores = {}
            
        # Load auto-allowlist if available
        try:
            if os.path.exists(self.allowlist_path):
                with open(self.allowlist_path, 'r') as f:
                    self.auto_allowlist = json.load(f)
        except Exception as e:
            if not self.quiet:
                print(f"Error loading auto-allowlist: {e}")
            # Use the default empty allowlist
            pass
            
    def _save_data(self):
        """Save feedback and model data to disk."""
        try:
            with open(self.feedback_path, 'w') as f:
                json.dump(self.feedback_data, f)
                
            model_data = {
                'issue_patterns': self.issue_patterns,
                'context_adjustments': self.context_adjustments,
                'token_weights': self.token_weights,
                'file_pattern_scores': self.file_pattern_scores,
                'updated_at': datetime.datetime.now().isoformat()
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
                
            # Save auto-allowlist separately
            with open(self.allowlist_path, 'w') as f:
                json.dump(self.auto_allowlist, f)
                
        except Exception as e:
            if not self.quiet:
                print(f"Error saving meta-learning data: {e}")
            
    def record_feedback(self, issue_data: Dict[str, Any], feedback_type: str):
        """
        Record user feedback about a detected GDPR issue.
        
        Args:
            issue_data: Data about the issue (should include file_path, line_number, issue_type, line_content)
            feedback_type: Type of feedback ('false_positive', 'false_negative', 'true_positive')
        """
        if feedback_type not in ['false_positive', 'false_negative', 'true_positive']:
            raise ValueError(f"Invalid feedback_type: {feedback_type}")
            
        # Extract essential data from the issue
        feedback_record = {
            'file_path': issue_data.get('file_path', ''),
            'line_number': issue_data.get('line_number', 0),
            'issue_type': issue_data.get('issue_type', ''),
            'line_content': issue_data.get('line_content', ''),
            'context': issue_data.get('context', ''),
            'confidence': issue_data.get('confidence', 0.5),
            'severity': issue_data.get('severity', 'medium'),
            'feedback_type': feedback_type,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Add feedback to records
        self.feedback_data.append(feedback_record)
        
        # Save updated data
        self._save_data()
        
        # If it's a false positive, update allowlists immediately
        if feedback_type == 'false_positive':
            self._update_allowlists_for_false_positive(feedback_record)
        
        # Update models immediately if we have enough data
        if len(self.feedback_data) % 10 == 0:  # Update after every 10 feedback items
            self.update_models()
            
        return True
        
    def record_scan_results(self, scan_results: List[Dict[str, Any]], user_corrections: List[Dict[str, Any]] = None):
        """
        Record the results of a complete scan, with optional user corrections.
        
        Args:
            scan_results: List of detected issues from a scan
            user_corrections: List of user corrections to the scan results
        """
        timestamp = datetime.datetime.now().isoformat()
        
        # Record all issues as presumed true positives initially
        for issue in scan_results:
            # Create a basic record for each issue
            record = {
                'file_path': issue.get('file_path', ''),
                'line_number': issue.get('line_number', 0),
                'issue_type': issue.get('issue_type', ''),
                'line_content': issue.get('line_content', ''),
                'confidence': issue.get('confidence', 0.5),
                'severity': issue.get('severity', 'medium'),
                'feedback_type': 'scan_result',  # Default - hasn't been verified
                'timestamp': timestamp
            }
            self.feedback_data.append(record)
            
        # Process user corrections if provided
        if user_corrections:
            for correction in user_corrections:
                feedback_type = correction.get('feedback_type')
                issue_data = correction.get('issue_data', {})
                
                if feedback_type and issue_data:
                    self.record_feedback(issue_data, feedback_type)
        
        # Save all data
        self._save_data()
        
        return True
        
    def extract_features(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract learning features from an issue.
        
        Args:
            issue_data: Data about the GDPR issue
            
        Returns:
            Dictionary of features for learning
        """
        line_content = issue_data.get('line_content', '')
        context = issue_data.get('context', '')
        issue_type = issue_data.get('issue_type', '')
        
        # Basic token features
        tokens = self._tokenize(line_content)
        context_tokens = self._tokenize(context) if context else []
        
        # File path features
        file_path = issue_data.get('file_path', '')
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower() if filename else ''
        is_test = any(kw in filename.lower() for kw in ['test', 'mock', 'example', 'fixture'])
        
        # Contextual features
        has_comment = '//' in line_content or '#' in line_content or '/*' in line_content
        is_url = 'http' in line_content or 'www.' in line_content
        
        # Pattern-based features
        pattern_matches = {}
        
        features = {
            'tokens': tokens,
            'token_count': len(tokens),
            'context_tokens': context_tokens,
            'file_ext': file_ext,
            'is_test_file': is_test,
            'has_comment': has_comment,
            'is_url': is_url,
            'issue_type': issue_type,
            'pattern_matches': pattern_matches
        }
        
        return features
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization of text."""
        if not text:
            return []
            
        # Remove common punctuation and split
        for char in ',.(){}[]=/\\\'":;+*':
            text = text.replace(char, ' ')
            
        # Return lowercase tokens
        return [token.lower() for token in text.split() if token]
    
    def update_models(self):
        """Update the meta-learning models based on collected feedback."""
        if not self.feedback_data or len(self.feedback_data) < 5:
            if not self.quiet:
                print("Not enough feedback data to update models")
            return False
            
        if not self.quiet:
            print(f"Updating meta-learning models with {len(self.feedback_data)} feedback records")
        
        # Analyze feedback data to identify patterns
        self._analyze_issue_patterns()
        self._analyze_context_patterns()
        self._analyze_token_weights()
        self._analyze_file_patterns()
        self._build_semantic_similarity_model()
        self._update_auto_allowlist()
        
        # Save updated models
        self._save_data()
        
        # Send telemetry if enabled
        if self.enable_telemetry:
            telemetry_data = {
                'issue_patterns': self.issue_patterns,
                'auto_allowlist': self.auto_allowlist
            }
            self._send_telemetry(telemetry_data)
        
        return True
    
    def _analyze_issue_patterns(self):
        """Analyze patterns in issue detection and feedback."""
        # Group feedback by issue type
        feedback_by_type = defaultdict(list)
        for record in self.feedback_data:
            issue_type = record.get('issue_type')
            if issue_type:
                feedback_by_type[issue_type].append(record)
                
        # For each issue type, analyze false positives and negatives
        for issue_type, records in feedback_by_type.items():
            false_positives = [r for r in records if r.get('feedback_type') == 'false_positive']
            false_negatives = [r for r in records if r.get('feedback_type') == 'false_negative']
            true_positives = [r for r in records if r.get('feedback_type') == 'true_positive']
            
            # Calculate false positive rate if we have enough data
            if len(false_positives) + len(true_positives) > 0:
                fp_rate = len(false_positives) / (len(false_positives) + len(true_positives))
            else:
                fp_rate = 0.0
                
            # Store pattern information
            self.issue_patterns[issue_type] = {
                'false_positive_rate': fp_rate,
                'false_positive_count': len(false_positives),
                'false_negative_count': len(false_negatives),
                'true_positive_count': len(true_positives),
                'total_records': len(records)
            }
    
    def _analyze_context_patterns(self):
        """Analyze context patterns in issues with feedback."""
        # Initialize context adjustments for each issue type
        for issue_type in set(r.get('issue_type', '') for r in self.feedback_data):
            if issue_type and issue_type not in self.context_adjustments:
                self.context_adjustments[issue_type] = {}
                
        # Analyze contexts that lead to false positives
        for record in self.feedback_data:
            feedback_type = record.get('feedback_type')
            issue_type = record.get('issue_type')
            
            if not (feedback_type and issue_type):
                continue
                
            # Extract context features
            file_path = record.get('file_path', '')
            filename = os.path.basename(file_path).lower()
            
            # Context adjustments based on filename patterns
            for pattern in ['test', 'mock', 'example', 'fixture', 'demo']:
                if pattern in filename:
                    context_key = f"filename_contains_{pattern}"
                    if context_key not in self.context_adjustments[issue_type]:
                        self.context_adjustments[issue_type][context_key] = 0.0
                        
                    # Adjust based on feedback type
                    if feedback_type == 'false_positive':
                        # If false positive, penalize this context
                        self.context_adjustments[issue_type][context_key] -= 0.05
                    elif feedback_type == 'true_positive':
                        # If true positive, reduce penalty
                        self.context_adjustments[issue_type][context_key] += 0.02
    
    def _analyze_token_weights(self):
        """Analyze tokens associated with different feedback types."""
        # Initialize token weights for each issue type
        for issue_type in set(r.get('issue_type', '') for r in self.feedback_data):
            if issue_type and issue_type not in self.token_weights:
                self.token_weights[issue_type] = {}
                
        # Count token occurrences for different feedback types
        token_counters = {
            'false_positive': defaultdict(Counter),
            'false_negative': defaultdict(Counter),
            'true_positive': defaultdict(Counter)
        }
        
        for record in self.feedback_data:
            feedback_type = record.get('feedback_type')
            issue_type = record.get('issue_type')
            
            if not (feedback_type in token_counters and issue_type):
                continue
                
            # Get tokens from line content
            tokens = self._tokenize(record.get('line_content', ''))
            
            # Count each token for this feedback type and issue type
            for token in tokens:
                token_counters[feedback_type][issue_type][token] += 1
        
        # Calculate token weights based on relative frequencies
        for issue_type in self.token_weights:
            # Get token counters for this issue type
            fp_counter = token_counters['false_positive'][issue_type]
            tp_counter = token_counters['true_positive'][issue_type]
            fn_counter = token_counters['false_negative'][issue_type]
            
            # Collect all tokens
            all_tokens = set()
            for counter in [fp_counter, tp_counter, fn_counter]:
                all_tokens.update(counter.keys())
                
            # Calculate weights for each token
            for token in all_tokens:
                fp_count = fp_counter[token]
                tp_count = tp_counter[token]
                fn_count = fn_counter[token]
                
                total = fp_count + tp_count + fn_count
                if total == 0:
                    continue
                    
                # Weight formula: higher values for tokens associated with true positives
                # Lower values for tokens associated with false positives
                weight = 0.0
                if tp_count > 0:
                    weight += 0.5 * (tp_count / total)
                if fp_count > 0:
                    weight -= 0.3 * (fp_count / total)
                if fn_count > 0:
                    weight -= 0.2 * (fn_count / total)
                    
                self.token_weights[issue_type][token] = weight
    
    def _analyze_file_patterns(self):
        """
        Analyze file patterns that lead to false positives or negatives.
        This helps identify which file types or naming patterns are more likely
        to produce false results.
        """
        # Group feedback by file extension and path patterns
        file_pattern_counts = defaultdict(lambda: {'fp': 0, 'tp': 0, 'fn': 0})
        
        for record in self.feedback_data:
            feedback_type = record.get('feedback_type')
            if feedback_type not in ['false_positive', 'false_negative', 'true_positive']:
                continue
                
            file_path = record.get('file_path', '')
            if not file_path:
                continue
                
            # Extract file extension
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            if ext:
                key = f"extension:{ext}"
                if feedback_type == 'false_positive':
                    file_pattern_counts[key]['fp'] += 1
                elif feedback_type == 'true_positive':
                    file_pattern_counts[key]['tp'] += 1
                elif feedback_type == 'false_negative':
                    file_pattern_counts[key]['fn'] += 1
            
            # Extract directory patterns
            parts = Path(file_path).parts
            for part in parts:
                part_lower = part.lower()
                for pattern in ['test', 'example', 'demo', 'sample', 'fixture', 'mock', 'config', 'vendor', 'dist']:
                    if pattern in part_lower:
                        key = f"dir_pattern:{pattern}"
                        if feedback_type == 'false_positive':
                            file_pattern_counts[key]['fp'] += 1
                        elif feedback_type == 'true_positive':
                            file_pattern_counts[key]['tp'] += 1
                        elif feedback_type == 'false_negative':
                            file_pattern_counts[key]['fn'] += 1
            
            # Extract filename patterns
            filename = os.path.basename(file_path).lower()
            for pattern in ['test', 'example', 'demo', 'sample', 'fixture', 'mock', 'config', 'readme']:
                if pattern in filename:
                    key = f"filename_pattern:{pattern}"
                    if feedback_type == 'false_positive':
                        file_pattern_counts[key]['fp'] += 1
                    elif feedback_type == 'true_positive':
                        file_pattern_counts[key]['tp'] += 1
                    elif feedback_type == 'false_negative':
                        file_pattern_counts[key]['fn'] += 1
        
        # Calculate scores for each pattern
        # A positive score means the pattern is associated with true positives
        # A negative score means the pattern is associated with false positives
        for pattern, counts in file_pattern_counts.items():
            total = counts['fp'] + counts['tp'] + counts['fn']
            if total >= 3:  # Only consider patterns with enough data
                score = 0.0
                if counts['tp'] > 0:
                    score += 0.6 * (counts['tp'] / total)
                if counts['fp'] > 0:
                    score -= 0.8 * (counts['fp'] / total)
                if counts['fn'] > 0:
                    score -= 0.2 * (counts['fn'] / total)
                
                self.file_pattern_scores[pattern] = score
    
    def _build_semantic_similarity_model(self):
        """
        Build a semantic similarity model to detect similar issues.
        This helps identify false positives that are semantically similar
        to previously identified false positives.
        """
        try:
            # Get enough data for meaningful similarity analysis
            true_positives = [r for r in self.feedback_data if r.get('feedback_type') == 'true_positive']
            false_positives = [r for r in self.feedback_data if r.get('feedback_type') == 'false_positive']
            
            if len(true_positives) < 5 or len(false_positives) < 5:
                return  # Not enough data
                
            # Prepare text corpus for vectorization
            corpus = []
            corpus_metadata = []
            
            for record in true_positives + false_positives:
                line_content = record.get('line_content', '')
                context = record.get('context', '')
                
                if not line_content:
                    continue
                    
                # Combine line and context for better semantic understanding
                text = line_content
                if context:
                    text = text + " " + context
                    
                corpus.append(text)
                corpus_metadata.append({
                    'issue_type': record.get('issue_type', ''),
                    'feedback_type': record.get('feedback_type', ''),
                    'file_path': record.get('file_path', ''),
                    'line_number': record.get('line_number', 0)
                })
            
            if not corpus:
                return
                
            # Create TF-IDF vectorizer based on availability
            if SKLEARN_AVAILABLE:
                self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            else:
                self.vectorizer = SimpleTfidfVectorizer(max_features=1000, stop_words='english')
                
            self.vectorized_texts = self.vectorizer.fit_transform(corpus)
            
            # Store metadata for later reference
            self.corpus_metadata = corpus_metadata
            
        except Exception as e:
            if not self.quiet:
                print(f"Error building semantic similarity model: {e}")
            self.vectorizer = None
            self.vectorized_texts = None
    
    def _update_auto_allowlist(self):
        """
        Update auto-allowlist based on feedback patterns.
        Files or patterns consistently marked as false positives
        will be added to the allowlist.
        """
        # Count false positives by file path and extension
        file_fp_counts = defaultdict(int)
        ext_fp_counts = defaultdict(int)
        pattern_fp_counts = defaultdict(int)
        
        for record in self.feedback_data:
            if record.get('feedback_type') != 'false_positive':
                continue
                
            file_path = record.get('file_path', '')
            if not file_path:
                continue
                
            # Count by file path
            file_fp_counts[file_path] += 1
            
            # Count by extension
            _, ext = os.path.splitext(file_path)
            if ext:
                ext_fp_counts[ext.lower()] += 1
                
            # Count common patterns in line content
            line_content = record.get('line_content', '')
            if line_content:
                # Look for common patterns like URLs, IP addresses, etc.
                if re.search(r'https?://[\w\.-]+', line_content):
                    pattern_fp_counts['url'] += 1
                if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', line_content):
                    pattern_fp_counts['ip_address'] += 1
                if re.search(r'localhost|127\.0\.0\.1', line_content):
                    pattern_fp_counts['localhost'] += 1
        
        # Update allowlist with files that have multiple false positives
        for file_path, count in file_fp_counts.items():
            if count >= 3 and file_path not in self.auto_allowlist['files']:
                self.auto_allowlist['files'].append(file_path)
                
        # Update allowlist with extensions that have high false positive rates
        for ext, count in ext_fp_counts.items():
            if count >= 5 and ext not in self.auto_allowlist['extensions']:
                self.auto_allowlist['extensions'].append(ext)
                
        # Update allowlist with patterns that frequently lead to false positives
        for pattern, count in pattern_fp_counts.items():
            if count >= 3 and pattern not in self.auto_allowlist['patterns']:
                pattern_regex = ''
                if pattern == 'url':
                    pattern_regex = r'https?://[\w\.-]+'
                elif pattern == 'ip_address':
                    pattern_regex = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
                elif pattern == 'localhost':
                    pattern_regex = r'localhost|127\.0\.0\.1'
                    
                if pattern_regex and pattern_regex not in self.auto_allowlist['patterns']:
                    self.auto_allowlist['patterns'].append(pattern_regex)
    
    def _update_allowlists_for_false_positive(self, feedback_record: Dict[str, Any]):
        """
        Update allowlists immediately when a false positive is recorded.
        This allows for faster adaptation.
        
        Args:
            feedback_record: The feedback record for a false positive
        """
        file_path = feedback_record.get('file_path', '')
        if not file_path:
            return
            
        # Check if we already have multiple false positives for this file
        fp_count = sum(1 for r in self.feedback_data if r.get('file_path') == file_path and 
                      r.get('feedback_type') == 'false_positive')
        
        if fp_count >= 3 and file_path not in self.auto_allowlist['files']:
            self.auto_allowlist['files'].append(file_path)
            self._save_data()  # Save immediately to update the allowlist
    
    def check_semantic_similarity(self, issue_data: Dict[str, Any]) -> Tuple[float, str]:
        """
        Check if an issue is semantically similar to previous issues.
        
        Args:
            issue_data: Data about the GDPR issue
            
        Returns:
            Tuple of (similarity_score, feedback_type of most similar issue)
        """
        if not self.vectorizer or not self.vectorized_texts:
            return (0.0, '')
            
        try:
            line_content = issue_data.get('line_content', '')
            context = issue_data.get('context', '')
            
            if not line_content:
                return (0.0, '')
                
            # Combine line and context for better semantic understanding
            text = line_content
            if context:
                text = text + " " + context
                
            # Vectorize the text
            text_vector = self.vectorizer.transform([text])
            
            # Calculate similarity with all previous issues
            if SKLEARN_AVAILABLE:
                similarities = cosine_similarity(text_vector, self.vectorized_texts).flatten()
            else:
                similarities = simple_cosine_similarity(text_vector, self.vectorized_texts).flatten()
            
            # Find the most similar issue
            if len(similarities) > 0:
                max_idx = np.argmax(similarities)
                max_similarity = similarities[max_idx]
                
                # Get feedback type of the most similar issue
                similar_feedback_type = self.corpus_metadata[max_idx]['feedback_type']
                
                return (max_similarity, similar_feedback_type)
                
        except Exception as e:
            if not self.quiet:
                print(f"Error calculating semantic similarity: {e}")
                
        return (0.0, '')
    
    def should_ignore_file(self, file_path: str) -> bool:
        """
        Check if a file should be ignored based on learned patterns.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be ignored, False otherwise
        """
        if not file_path:
            return False
            
        # Check if file is in the auto-allowlist
        if file_path in self.auto_allowlist['files']:
            return True
            
        # Check if file extension is in the auto-allowlist
        _, ext = os.path.splitext(file_path)
        if ext and ext.lower() in self.auto_allowlist['extensions']:
            return True
            
        # Check file pattern scores
        file_score = 0.0
        
        # Check extension score
        if ext:
            ext_key = f"extension:{ext.lower()}"
            if ext_key in self.file_pattern_scores:
                file_score += self.file_pattern_scores[ext_key]
        
        # Check directory pattern scores
        parts = Path(file_path).parts
        for part in parts:
            part_lower = part.lower()
            for pattern in ['test', 'example', 'demo', 'sample', 'fixture', 'mock', 'config', 'vendor', 'dist']:
                if pattern in part_lower:
                    key = f"dir_pattern:{pattern}"
                    if key in self.file_pattern_scores:
                        file_score += self.file_pattern_scores[key]
        
        # Check filename pattern scores
        filename = os.path.basename(file_path).lower()
        for pattern in ['test', 'example', 'demo', 'sample', 'fixture', 'mock', 'config', 'readme']:
            if pattern in filename:
                key = f"filename_pattern:{pattern}"
                if key in self.file_pattern_scores:
                    file_score += self.file_pattern_scores[key]
        
        # If file has a very negative score, ignore it
        return file_score < -0.7
    
    def check_content_patterns(self, content: str) -> bool:
        """
        Check if content matches any known false positive patterns.
        
        Args:
            content: Content to check
            
        Returns:
            True if the content matches a known false positive pattern
        """
        if not content:
            return False
            
        # Check against pattern allowlist
        for pattern in self.auto_allowlist['patterns']:
            if re.search(pattern, content):
                return True
                
        return False
    
    def adjust_confidence(self, issue_data: Dict[str, Any]) -> float:
        """
        Adjust the confidence score for an issue based on meta-learning.
        
        Args:
            issue_data: Data about the GDPR issue
            
        Returns:
            Adjusted confidence score
        """
        base_confidence = issue_data.get('confidence', 0.5)
        issue_type = issue_data.get('issue_type', '')
        
        if not issue_type or issue_type not in self.issue_patterns:
            return base_confidence
            
        # Extract features
        features = self.extract_features(issue_data)
        
        # Apply token-based adjustments
        token_adjustment = 0.0
        token_count = 0
        
        if issue_type in self.token_weights:
            for token in features.get('tokens', []):
                if token in self.token_weights[issue_type]:
                    token_adjustment += self.token_weights[issue_type][token]
                    token_count += 1
                    
            if token_count > 0:
                token_adjustment /= token_count  # Average adjustment
        
        # Apply context-based adjustments
        context_adjustment = 0.0
        context_count = 0
        
        if issue_type in self.context_adjustments:
            # Check filename patterns
            file_path = issue_data.get('file_path', '')
            filename = os.path.basename(file_path).lower()
            
            for pattern, adjustment in self.context_adjustments[issue_type].items():
                if pattern.startswith('filename_contains_'):
                    check_pattern = pattern.replace('filename_contains_', '')
                    if check_pattern in filename:
                        context_adjustment += adjustment
                        context_count += 1
                        
            if context_count > 0:
                context_adjustment /= context_count  # Average adjustment
        
        # Apply semantic similarity adjustment
        similarity_adjustment = 0.0
        similarity_score, similar_feedback_type = self.check_semantic_similarity(issue_data)
        
        if similarity_score > 0.7:  # Only apply if there's a strong similarity
            if similar_feedback_type == 'false_positive':
                similarity_adjustment = -0.3 * similarity_score  # Reduce confidence if similar to false positives
            elif similar_feedback_type == 'true_positive':
                similarity_adjustment = 0.2 * similarity_score  # Increase confidence if similar to true positives
        
        # Apply file pattern score adjustments
        file_pattern_adjustment = 0.0
        file_path = issue_data.get('file_path', '')
        
        if file_path:
            # Check extension score
            _, ext = os.path.splitext(file_path)
            if ext:
                ext_key = f"extension:{ext.lower()}"
                if ext_key in self.file_pattern_scores:
                    file_pattern_adjustment += self.file_pattern_scores[ext_key] * 0.1
            
            # Check directory and filename pattern scores
            path_score = 0.0
            score_count = 0
            
            # Directory patterns
            parts = Path(file_path).parts
            for part in parts:
                part_lower = part.lower()
                for pattern in ['test', 'example', 'demo', 'sample', 'fixture', 'mock', 'config', 'vendor', 'dist']:
                    if pattern in part_lower:
                        key = f"dir_pattern:{pattern}"
                        if key in self.file_pattern_scores:
                            path_score += self.file_pattern_scores[key]
                            score_count += 1
            
            # Filename patterns
            filename = os.path.basename(file_path).lower()
            for pattern in ['test', 'example', 'demo', 'sample', 'fixture', 'mock', 'config', 'readme']:
                if pattern in filename:
                    key = f"filename_pattern:{pattern}"
                    if key in self.file_pattern_scores:
                        path_score += self.file_pattern_scores[key]
                        score_count += 1
            
            if score_count > 0:
                path_score /= score_count
                file_pattern_adjustment += path_score * 0.15
        
        # Calculate overall confidence adjustment
        total_adjustment = (token_adjustment * 0.4 + 
                           context_adjustment * 0.2 + 
                           similarity_adjustment * 0.25 + 
                           file_pattern_adjustment * 0.15)
        
        # Apply adjustment with limits to prevent extreme changes
        adjusted_confidence = base_confidence + total_adjustment
        
        # Ensure confidence is between 0 and 1
        return max(0.1, min(0.99, adjusted_confidence))
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the current learning state."""
        stats = {
            'feedback_count': len(self.feedback_data),
            'issue_types': list(self.issue_patterns.keys()),
            'false_positive_counts': {
                issue_type: data.get('false_positive_count', 0)
                for issue_type, data in self.issue_patterns.items()
            },
            'false_negative_counts': {
                issue_type: data.get('false_negative_count', 0)
                for issue_type, data in self.issue_patterns.items()
            },
            'context_patterns': len(self.context_adjustments),
            'token_patterns': sum(len(weights) for weights in self.token_weights.values()),
            'auto_allowlist_files': len(self.auto_allowlist['files']),
            'auto_allowlist_patterns': len(self.auto_allowlist['patterns']),
            'auto_allowlist_extensions': len(self.auto_allowlist['extensions']),
            'has_similarity_model': self.vectorizer is not None
        }
        
        return stats
        
    def get_auto_allowlist(self) -> Dict[str, List[str]]:
        """Get the automatically generated allowlist."""
        return self.auto_allowlist 

    def _load_telemetry_consent(self) -> Dict[str, Any]:
        """Load telemetry consent settings."""
        if os.path.exists(self.telemetry_consent_path):
            try:
                with open(self.telemetry_consent_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {'consent_given': False, 'timestamp': None}
        return {'consent_given': False, 'timestamp': None}
    
    def _save_telemetry_consent(self):
        """Save telemetry consent settings."""
        try:
            with open(self.telemetry_consent_path, 'w') as f:
                json.dump(self.telemetry_consent, f, indent=2)
        except Exception as e:
            if not self.quiet:
                print(f"Error saving telemetry consent: {e}")
    
    def set_telemetry_consent(self, consent: bool) -> bool:
        """
        Set user consent for telemetry data sharing.
        
        Args:
            consent: True to enable telemetry, False to disable
            
        Returns:
            Success status
        """
        self.telemetry_consent = {
            'consent_given': consent,
            'timestamp': datetime.datetime.now().isoformat(),
            'version': VERSION  # Ensure VERSION is defined at module level
        }
        
        self.enable_telemetry = consent
        self._save_telemetry_consent()
        
        if not self.quiet:
            if consent:
                print("Telemetry enabled. Thank you for helping improve Levox!")
                print("Only anonymized meta-learning statistics will be shared.")
            else:
                print("Telemetry disabled. No data will be shared.")
                
        return True
    
    def _send_telemetry(self, data: Dict[str, Any]) -> bool:
        """
        Send anonymized telemetry data to central server.
        
        Args:
            data: Data to send (will be anonymized)
            
        Returns:
            Success status
        """
        if not self.enable_telemetry or not self.telemetry_consent.get('consent_given', False):
            return False
            
        if not REQUESTS_AVAILABLE:
            return False
            
        # Anonymize the data
        anonymized_data = self._anonymize_telemetry_data(data)
        
        try:
            # Send to server (replace with your actual endpoint)
            response = requests.post(
                "https://api.levox.io/telemetry",
                json=anonymized_data,
                timeout=5  # Don't block for too long
            )
            return response.status_code == 200
        except Exception:
            # Fail silently - telemetry should never break functionality
            return False
    
    def _anonymize_telemetry_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove any identifiable information from telemetry data.
        
        Args:
            data: Raw telemetry data
            
        Returns:
            Anonymized data
        """
        # Create a copy to avoid modifying the original
        anon_data = {}
        
        # Include only statistical information, never file paths or content
        if 'issue_patterns' in data:
            anon_data['issue_patterns'] = {}
            for issue_type, pattern_data in data['issue_patterns'].items():
                anon_data['issue_patterns'][issue_type] = {
                    'false_positive_rate': pattern_data.get('false_positive_rate', 0),
                    'false_positive_count': pattern_data.get('false_positive_count', 0),
                    'false_negative_count': pattern_data.get('false_negative_count', 0),
                    'true_positive_count': pattern_data.get('true_positive_count', 0),
                    'total_records': pattern_data.get('total_records', 0)
                }
        
        # Include counts of file extensions but not specific files
        if 'auto_allowlist' in data:
            anon_data['auto_allowlist'] = {
                'files_count': len(data['auto_allowlist'].get('files', [])),
                'patterns_count': len(data['auto_allowlist'].get('patterns', [])),
                'extensions': data['auto_allowlist'].get('extensions', [])  # Extensions are safe to share
            }
        
        # Include overall stats
        anon_data['stats'] = {
            'feedback_count': len(self.feedback_data),
            'token_pattern_count': sum(len(weights) for weights in self.token_weights.values()),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        return anon_data 