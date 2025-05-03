#!/usr/bin/env python
"""
Machine Learning Enhanced Analysis Module

This module implements machine learning capabilities for:
- Active learning from user feedback
- Pattern detection using embeddings
- Automated rule generation
- Framework-specific pattern learning
- Secure PII handling and encryption
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import logging
from dataclasses import dataclass
from datetime import datetime
import pickle
from collections import defaultdict
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import uuid

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import DBSCAN
    import torch
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("Machine learning packages not available. Install required packages for ML features.")

@dataclass
class CodePattern:
    """Represents a learned code pattern"""
    pattern_type: str
    confidence: float
    examples: List[str]
    embeddings: Optional[np.ndarray] = None
    rules: Optional[List[Dict]] = None
    last_updated: datetime = datetime.now()

@dataclass
class PIIData:
    """Represents encrypted PII data with consent tracking"""
    data_type: str
    encrypted_value: bytes
    consent_id: str
    consent_date: datetime
    encryption_id: str
    salt: bytes

class SecurePIIHandler:
    """Handles secure PII data processing with encryption and consent tracking"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize PII handler with encryption
        
        Args:
            encryption_key: Optional master key for encryption
        """
        self.encryption_key = encryption_key or os.environ.get('PII_ENCRYPTION_KEY')
        if not self.encryption_key:
            self.encryption_key = self._generate_key()
            
        self.consent_records: Dict[str, Dict[str, Any]] = {}
        self.encryption_keys: Dict[str, Fernet] = {}
    
    def encrypt_pii(self, data: str, data_type: str, user_consent: Dict[str, Any]) -> PIIData:
        """
        Encrypt PII data with consent tracking
        
        Args:
            data: Raw PII data to encrypt
            data_type: Type of PII (e.g., 'email', 'phone')
            user_consent: Consent information
            
        Returns:
            PIIData object with encrypted data and consent info
        """
        # Generate unique encryption key for this data
        salt = os.urandom(16)
        encryption_id = str(uuid.uuid4())
        key = self._derive_key(salt)
        
        # Create Fernet cipher
        f = Fernet(base64.urlsafe_b64encode(key))
        self.encryption_keys[encryption_id] = f
        
        # Encrypt the data
        encrypted_value = f.encrypt(data.encode())
        
        # Record consent
        consent_id = str(uuid.uuid4())
        self.consent_records[consent_id] = {
            'timestamp': datetime.utcnow().isoformat(),
            'data_type': data_type,
            'purpose': user_consent.get('purpose', 'unspecified'),
            'expiry': user_consent.get('expiry'),
            'source': user_consent.get('source', 'direct'),
        }
        
        return PIIData(
            data_type=data_type,
            encrypted_value=encrypted_value,
            consent_id=consent_id,
            consent_date=datetime.utcnow(),
            encryption_id=encryption_id,
            salt=salt
        )
    
    def decrypt_pii(self, pii_data: PIIData) -> Optional[str]:
        """
        Decrypt PII data if consent is valid
        
        Args:
            pii_data: PIIData object containing encrypted data
            
        Returns:
            Decrypted data if consent is valid, None otherwise
        """
        # Check consent validity
        if not self._is_consent_valid(pii_data.consent_id):
            logging.warning(f"Invalid or expired consent for {pii_data.data_type}")
            return None
            
        try:
            # Get encryption key
            f = self.encryption_keys.get(pii_data.encryption_id)
            if not f:
                # Recreate cipher if not cached
                key = self._derive_key(pii_data.salt)
                f = Fernet(base64.urlsafe_b64encode(key))
                
            # Decrypt data
            decrypted = f.decrypt(pii_data.encrypted_value)
            return decrypted.decode()
            
        except Exception as e:
            logging.error(f"Error decrypting {pii_data.data_type}: {str(e)}")
            return None
    
    def revoke_consent(self, consent_id: str):
        """
        Revoke consent for PII data
        
        Args:
            consent_id: ID of consent to revoke
        """
        if consent_id in self.consent_records:
            self.consent_records[consent_id]['revoked'] = datetime.utcnow().isoformat()
    
    def _generate_key(self) -> str:
        """Generate a new master encryption key"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()
    
    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(self.encryption_key.encode())
    
    def _is_consent_valid(self, consent_id: str) -> bool:
        """Check if consent is valid and not expired/revoked"""
        if consent_id not in self.consent_records:
            return False
            
        consent = self.consent_records[consent_id]
        
        # Check if consent is revoked
        if consent.get('revoked'):
            return False
            
        # Check if consent is expired
        if consent.get('expiry'):
            expiry = datetime.fromisoformat(consent['expiry'])
            if datetime.utcnow() > expiry:
                return False
                
        return True

class MLAnalyzer:
    """
    Machine learning enhanced analyzer for GDPR compliance
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.patterns: Dict[str, CodePattern] = {}
        self.feedback_data: List[Dict] = []
        self.classifier = None
        self.vectorizer = None
        self.embedding_model = None
        
        if ML_AVAILABLE:
            self._initialize_ml_components(model_path)
    
    def _initialize_ml_components(self, model_path: Optional[str]):
        """Initialize ML models and components"""
        # Initialize text vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3)
        )
        
        # Initialize classifier
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            class_weight='balanced'
        )
        
        # Load pre-trained sentence transformer for code embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logging.error(f"Error loading embedding model: {str(e)}")
            self.embedding_model = None
            
        # Load existing patterns if available
        if model_path and Path(model_path).exists():
            self.load_patterns(model_path)
    
    def analyze_code(self, code: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Analyze code using learned patterns and ML models
        
        Args:
            code: Source code to analyze
            context: Additional context (e.g., framework, file type)
            
        Returns:
            List of potential issues found
        """
        if not ML_AVAILABLE:
            return []
            
        issues = []
        
        # Get code embedding
        code_embedding = self._get_code_embedding(code)
        
        # Match against known patterns
        pattern_matches = self._match_patterns(code, code_embedding)
        issues.extend(pattern_matches)
        
        # Classify using trained model
        if self.classifier and self.vectorizer:
            classification_issues = self._classify_code(code)
            issues.extend(classification_issues)
            
        # Apply framework-specific patterns if context provided
        if context and 'framework' in context:
            framework_issues = self._apply_framework_patterns(code, context['framework'])
            issues.extend(framework_issues)
            
        return issues
    
    def add_feedback(self, code: str, issue_type: str, is_violation: bool, context: Dict[str, Any] = None):
        """
        Add feedback for active learning
        
        Args:
            code: The code snippet
            issue_type: Type of issue
            is_violation: Whether it's a true violation
            context: Additional context
        """
        feedback = {
            'code': code,
            'issue_type': issue_type,
            'is_violation': is_violation,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        self.feedback_data.append(feedback)
        
        # Update models with new feedback
        if len(self.feedback_data) % 10 == 0:  # Retrain after every 10 feedback items
            self._update_models()
    
    def learn_new_pattern(self, pattern_type: str, examples: List[str], rules: Optional[List[Dict]] = None):
        """
        Learn a new pattern from examples
        
        Args:
            pattern_type: Type of pattern to learn
            examples: Example code snippets
            rules: Optional rules associated with the pattern
        """
        if not ML_AVAILABLE or not self.embedding_model:
            return
            
        # Get embeddings for examples
        embeddings = []
        for example in examples:
            embedding = self._get_code_embedding(example)
            if embedding is not None:
                embeddings.append(embedding)
                
        if not embeddings:
            return
            
        # Create pattern
        pattern = CodePattern(
            pattern_type=pattern_type,
            confidence=0.8,  # Initial confidence
            examples=examples,
            embeddings=np.mean(embeddings, axis=0),  # Use mean embedding
            rules=rules
        )
        
        self.patterns[pattern_type] = pattern
    
    def _get_code_embedding(self, code: str) -> Optional[np.ndarray]:
        """Get embedding for code snippet"""
        if not self.embedding_model:
            return None
            
        try:
            embedding = self.embedding_model.encode(code)
            return embedding
        except Exception as e:
            logging.error(f"Error getting code embedding: {str(e)}")
            return None
    
    def _match_patterns(self, code: str, code_embedding: Optional[np.ndarray]) -> List[Dict[str, Any]]:
        """Match code against known patterns"""
        issues = []
        
        if code_embedding is None:
            return issues
            
        for pattern_type, pattern in self.patterns.items():
            if pattern.embeddings is not None:
                # Calculate similarity
                similarity = self._calculate_similarity(code_embedding, pattern.embeddings)
                
                if similarity > 0.8:  # Similarity threshold
                    issues.append({
                        'type': pattern_type,
                        'confidence': float(similarity * pattern.confidence),
                        'message': f'Code matches {pattern_type} pattern',
                        'severity': 'medium'
                    })
                    
        return issues
    
    def _classify_code(self, code: str) -> List[Dict[str, Any]]:
        """Classify code using trained model"""
        issues = []
        
        try:
            # Transform code
            X = self.vectorizer.transform([code])
            
            # Get prediction and probability
            pred = self.classifier.predict(X)
            prob = self.classifier.predict_proba(X)
            
            if pred[0] == 1:  # Violation predicted
                max_prob = np.max(prob[0])
                issues.append({
                    'type': 'ml_detected_violation',
                    'confidence': float(max_prob),
                    'message': 'Potential violation detected by ML model',
                    'severity': 'medium'
                })
                
        except Exception as e:
            logging.error(f"Error in code classification: {str(e)}")
            
        return issues
    
    def _apply_framework_patterns(self, code: str, framework: str) -> List[Dict[str, Any]]:
        """Apply framework-specific patterns"""
        issues = []
        
        # Get framework-specific patterns
        framework_patterns = {k: v for k, v in self.patterns.items() 
                            if k.startswith(f"{framework}_")}
        
        code_embedding = self._get_code_embedding(code)
        if code_embedding is not None:
            for pattern_type, pattern in framework_patterns.items():
                if pattern.embeddings is not None:
                    similarity = self._calculate_similarity(code_embedding, pattern.embeddings)
                    
                    if similarity > 0.85:  # Higher threshold for framework patterns
                        issues.append({
                            'type': pattern_type,
                            'confidence': float(similarity * pattern.confidence),
                            'message': f'Code matches {framework} pattern: {pattern_type}',
                            'severity': 'medium'
                        })
                        
        return issues
    
    def _update_models(self):
        """Update ML models with new feedback data"""
        if not self.feedback_data:
            return
            
        # Prepare training data
        X_text = [item['code'] for item in self.feedback_data]
        y = [int(item['is_violation']) for item in self.feedback_data]
        
        # Update vectorizer and transform text
        X = self.vectorizer.fit_transform(X_text)
        
        # Train classifier
        self.classifier.fit(X, y)
        
        # Update pattern confidences based on feedback
        self._update_pattern_confidences()
    
    def _update_pattern_confidences(self):
        """Update pattern confidences based on feedback"""
        pattern_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for feedback in self.feedback_data:
            code_embedding = self._get_code_embedding(feedback['code'])
            if code_embedding is None:
                continue
                
            for pattern_type, pattern in self.patterns.items():
                if pattern.embeddings is not None:
                    similarity = self._calculate_similarity(code_embedding, pattern.embeddings)
                    
                    if similarity > 0.8:
                        pattern_performance[pattern_type]['total'] += 1
                        if feedback['is_violation'] == (pattern_type in feedback['issue_type']):
                            pattern_performance[pattern_type]['correct'] += 1
                            
        # Update confidences
        for pattern_type, stats in pattern_performance.items():
            if stats['total'] > 0:
                accuracy = stats['correct'] / stats['total']
                self.patterns[pattern_type].confidence = (
                    0.7 * self.patterns[pattern_type].confidence + 0.3 * accuracy
                )
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        return float(np.dot(embedding1, embedding2) / 
                    (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
    
    def save_patterns(self, path: str):
        """Save learned patterns to file"""
        data = {
            'patterns': {k: {
                'pattern_type': v.pattern_type,
                'confidence': v.confidence,
                'examples': v.examples,
                'embeddings': v.embeddings.tolist() if v.embeddings is not None else None,
                'rules': v.rules,
                'last_updated': v.last_updated.isoformat()
            } for k, v in self.patterns.items()},
            'feedback_data': self.feedback_data
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def load_patterns(self, path: str):
        """Load patterns from file"""
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                
            self.patterns = {
                k: CodePattern(
                    pattern_type=v['pattern_type'],
                    confidence=v['confidence'],
                    examples=v['examples'],
                    embeddings=np.array(v['embeddings']) if v['embeddings'] else None,
                    rules=v['rules'],
                    last_updated=datetime.fromisoformat(v['last_updated'])
                ) for k, v in data['patterns'].items()
            }
            
            self.feedback_data = data['feedback_data']
            
        except Exception as e:
            logging.error(f"Error loading patterns: {str(e)}")
            
    def cluster_violations(self, min_samples: int = 3) -> Dict[str, List[str]]:
        """
        Cluster similar violations to identify patterns
        
        Args:
            min_samples: Minimum samples for a cluster
            
        Returns:
            Dictionary mapping cluster labels to code examples
        """
        if not self.feedback_data or not self.embedding_model:
            return {}
            
        # Get embeddings for violation examples
        violation_data = [(item['code'], self._get_code_embedding(item['code']))
                         for item in self.feedback_data if item['is_violation']]
        
        if not violation_data:
            return {}
            
        codes, embeddings = zip(*[(code, emb) for code, emb in violation_data if emb is not None])
        embeddings = np.array(embeddings)
        
        # Cluster embeddings
        clusterer = DBSCAN(eps=0.3, min_samples=min_samples)
        labels = clusterer.fit_predict(embeddings)
        
        # Group examples by cluster
        clusters = defaultdict(list)
        for code, label in zip(codes, labels):
            if label >= 0:  # Ignore noise points (-1)
                clusters[f"cluster_{label}"].append(code)
                
        return dict(clusters) 