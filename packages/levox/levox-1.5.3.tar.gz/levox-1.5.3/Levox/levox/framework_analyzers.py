#!/usr/bin/env python
"""
Framework-Specific Analyzers Module

This module implements specialized analyzers for popular frameworks and cloud services:
- Django, Flask, FastAPI
- React, Angular
- AWS, Azure, GCP services
- Audit trail system for GDPR compliance
"""

import ast
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import re
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
from datetime import datetime
import hashlib
import uuid
import os
from threading import Lock

class AuditLogger:
    """GDPR-compliant audit logging system"""
    
    def __init__(self, log_path: Optional[str] = None):
        self.log_path = log_path or os.path.join(os.getcwd(), 'gdpr_audit_logs')
        self.log_lock = Lock()
        os.makedirs(self.log_path, exist_ok=True)
    
    def log_data_access(self, user_id: str, data_type: str, purpose: str,
                       action: str, status: str, details: Optional[Dict] = None):
        """
        Log data access events
        
        Args:
            user_id: ID of user accessing data
            data_type: Type of data being accessed
            purpose: Purpose of access
            action: Action being performed (read/write/delete)
            status: Outcome status
            details: Additional details
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_id': str(uuid.uuid4()),
            'user_id': user_id,
            'data_type': data_type,
            'purpose': purpose,
            'action': action,
            'status': status,
            'details': details or {},
            'hash': None  # Will be set below
        }
        
        # Add hash for integrity verification
        log_entry['hash'] = self._hash_entry(log_entry)
        
        self._write_log(log_entry)
    
    def log_consent_change(self, user_id: str, consent_type: str,
                          action: str, expiry: Optional[str] = None):
        """
        Log consent-related events
        
        Args:
            user_id: ID of user
            consent_type: Type of consent
            action: Action (grant/revoke)
            expiry: Optional expiry date
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_id': str(uuid.uuid4()),
            'event_type': 'consent_change',
            'user_id': user_id,
            'consent_type': consent_type,
            'action': action,
            'expiry': expiry,
            'hash': None
        }
        
        log_entry['hash'] = self._hash_entry(log_entry)
        self._write_log(log_entry)
    
    def log_deletion_request(self, user_id: str, request_type: str,
                           status: str, affected_data: List[str]):
        """
        Log data deletion requests
        
        Args:
            user_id: ID of user
            request_type: Type of deletion request
            status: Request status
            affected_data: List of affected data types
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_id': str(uuid.uuid4()),
            'event_type': 'deletion_request',
            'user_id': user_id,
            'request_type': request_type,
            'status': status,
            'affected_data': affected_data,
            'hash': None
        }
        
        log_entry['hash'] = self._hash_entry(log_entry)
        self._write_log(log_entry)
    
    def verify_log_integrity(self, start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> List[str]:
        """
        Verify integrity of audit logs
        
        Args:
            start_date: Optional start date for verification
            end_date: Optional end date for verification
            
        Returns:
            List of event IDs with integrity issues
        """
        compromised_events = []
        
        for log_file in self._get_log_files(start_date, end_date):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        entry = json.loads(line)
                        stored_hash = entry.pop('hash', None)
                        if stored_hash:
                            calculated_hash = self._hash_entry(entry)
                            if calculated_hash != stored_hash:
                                compromised_events.append(entry['event_id'])
            except Exception as e:
                logging.error(f"Error verifying log file {log_file}: {str(e)}")
                
        return compromised_events
    
    def _write_log(self, log_entry: Dict[str, Any]):
        """Write log entry to file with thread safety"""
        try:
            # Use date-based log files
            log_date = datetime.fromisoformat(log_entry['timestamp']).strftime('%Y-%m-%d')
            log_file = os.path.join(self.log_path, f'gdpr_audit_{log_date}.log')
            
            with self.log_lock:
                with open(log_file, 'a') as f:
                    json.dump(log_entry, f)
                    f.write('\n')
                    f.flush()
                    os.fsync(f.fileno())
                    
        except Exception as e:
            logging.error(f"Error writing audit log: {str(e)}")
    
    def _hash_entry(self, entry: Dict[str, Any]) -> str:
        """Create cryptographic hash of log entry for integrity"""
        # Sort keys for consistent hashing
        serialized = json.dumps(entry, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
    
    def _get_log_files(self, start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> List[str]:
        """Get relevant log files for date range"""
        all_logs = [f for f in os.listdir(self.log_path)
                   if f.startswith('gdpr_audit_') and f.endswith('.log')]
        
        if not (start_date or end_date):
            return [os.path.join(self.log_path, f) for f in all_logs]
            
        filtered_logs = []
        for log_file in all_logs:
            try:
                log_date = datetime.strptime(log_file[11:21], '%Y-%m-%d')
                if start_date and log_date < datetime.fromisoformat(start_date):
                    continue
                if end_date and log_date > datetime.fromisoformat(end_date):
                    continue
                filtered_logs.append(os.path.join(self.log_path, log_file))
            except ValueError:
                continue
                
        return filtered_logs

@dataclass
class FrameworkContext:
    """Context information for framework analysis"""
    framework_type: str
    version: Optional[str] = None
    config_files: List[str] = None
    dependencies: Dict[str, str] = None
    routes: List[str] = None

class BaseFrameworkAnalyzer(ABC):
    """Base class for framework-specific analyzers"""
    
    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.context: Optional[FrameworkContext] = None
        
    @abstractmethod
    def analyze_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Analyze a file for framework-specific issues"""
        pass
        
    @abstractmethod
    def get_data_flow_patterns(self) -> Dict[str, List[str]]:
        """Get framework-specific data flow patterns"""
        pass
        
    def _add_issue(self, issue_type: str, message: str, file_path: str, 
                   line_number: int, severity: str = "medium", confidence: float = 0.8):
        """Add a framework-specific issue"""
        self.issues.append({
            "type": f"{self.context.framework_type}_{issue_type}",
            "message": message,
            "file": file_path,
            "line": line_number,
            "severity": severity,
            "confidence": confidence
        })

class DjangoAnalyzer(BaseFrameworkAnalyzer):
    """Analyzer for Django applications"""
    
    SENSITIVE_MODEL_FIELDS = {
        'email', 'password', 'secret', 'token', 'key', 'ssn', 'credit_card',
        'phone', 'address', 'dob', 'birth_date', 'social_security'
    }
    
    def __init__(self):
        super().__init__()
        self.models: Dict[str, Set[str]] = {}  # model_name -> fields
        self.views: Dict[str, List[str]] = {}  # view_name -> accessed_fields
        
    def analyze_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Analyze Django file for GDPR compliance issues"""
        try:
            tree = ast.parse(content)
            
            if 'models.py' in file_path:
                self._analyze_models(tree, file_path)
            elif 'views.py' in file_path:
                self._analyze_views(tree, file_path)
            elif 'forms.py' in file_path:
                self._analyze_forms(tree, file_path)
            elif 'settings.py' in file_path:
                self._analyze_settings(tree, file_path)
                
        except Exception as e:
            logging.error(f"Error analyzing Django file {file_path}: {str(e)}")
            
        return self.issues
    
    def get_data_flow_patterns(self) -> Dict[str, List[str]]:
        """Get Django-specific data flow patterns"""
        return {
            'model_save': [
                r'model\.save\(',
                r'\.objects\.create\(',
                r'\.objects\.update\('
            ],
            'form_data': [
                r'request\.POST',
                r'form\.cleaned_data',
                r'form\.data'
            ],
            'session_data': [
                r'request\.session',
                r'\.set_cookie\(',
                r'\.get_cookie\('
            ]
        }
    
    def _analyze_models(self, tree: ast.AST, file_path: str):
        """Analyze Django models for sensitive fields"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a Django model
                if any(base.id == 'Model' for base in node.bases 
                      if isinstance(base, ast.Name)):
                    model_name = node.name
                    self.models[model_name] = set()
                    
                    # Check fields
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name):
                                    field_name = target.id
                                    if field_name.lower() in self.SENSITIVE_MODEL_FIELDS:
                                        self.models[model_name].add(field_name)
                                        
                                        # Check for proper field protection
                                        if not self._has_field_protection(child.value):
                                            self._add_issue(
                                                "unprotected_sensitive_field",
                                                f"Sensitive field '{field_name}' in model '{model_name}' lacks proper protection",
                                                file_path,
                                                child.lineno,
                                                "high"
                                            )
    
    def _analyze_views(self, tree: ast.AST, file_path: str):
        """Analyze Django views for data handling"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if it's a view function
                if self._is_view_function(node):
                    view_name = node.name
                    self.views[view_name] = []
                    
                    # Check request handling
                    for child in ast.walk(node):
                        if isinstance(child, ast.Attribute):
                            if isinstance(child.value, ast.Name) and child.value.id == 'request':
                                if child.attr in {'POST', 'GET', 'FILES'}:
                                    # Check for proper input validation
                                    if not self._has_input_validation(node):
                                        self._add_issue(
                                            "missing_input_validation",
                                            f"View '{view_name}' handles user input without proper validation",
                                            file_path,
                                            node.lineno
                                        )
                                        
                        # Check model access
                        elif isinstance(child, ast.Call):
                            if self._is_model_query(child):
                                if not self._has_permission_check(node):
                                    self._add_issue(
                                        "missing_permission_check",
                                        f"View '{view_name}' accesses model data without permission checks",
                                        file_path,
                                        node.lineno
                                    )
    
    def _analyze_forms(self, tree: ast.AST, file_path: str):
        """Analyze Django forms for data handling"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a form class
                if any(base.id.endswith('Form') for base in node.bases 
                      if isinstance(base, ast.Name)):
                    form_name = node.name
                    
                    # Check for sensitive fields
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name):
                                    field_name = target.id
                                    if field_name.lower() in self.SENSITIVE_MODEL_FIELDS:
                                        # Check for proper validation
                                        if not self._has_field_validation(child.value):
                                            self._add_issue(
                                                "missing_form_validation",
                                                f"Sensitive form field '{field_name}' lacks proper validation",
                                                file_path,
                                                child.lineno
                                            )
    
    def _analyze_settings(self, tree: ast.AST, file_path: str):
        """Analyze Django settings for security configurations"""
        required_settings = {
            'SESSION_COOKIE_SECURE': True,
            'CSRF_COOKIE_SECURE': True,
            'SECURE_SSL_REDIRECT': True,
            'SECURE_HSTS_SECONDS': lambda x: x > 0,
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': True
        }
        
        settings = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        settings[target.id] = self._get_setting_value(node.value)
                        
        # Check required security settings
        for setting, required_value in required_settings.items():
            if setting not in settings:
                self._add_issue(
                    "missing_security_setting",
                    f"Required security setting '{setting}' is missing",
                    file_path,
                    1,
                    "high"
                )
            elif callable(required_value):
                if not required_value(settings[setting]):
                    self._add_issue(
                        "insecure_setting",
                        f"Security setting '{setting}' has insecure value",
                        file_path,
                        1,
                        "high"
                    )
            elif settings[setting] != required_value:
                self._add_issue(
                    "insecure_setting",
                    f"Security setting '{setting}' should be {required_value}",
                    file_path,
                    1,
                    "high"
                )
    
    def _has_field_protection(self, node: ast.AST) -> bool:
        """Check if a model field has proper protection"""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                protection_methods = {'encrypt', 'hash', 'mask'}
                return node.func.attr in protection_methods
        return False
    
    def _has_input_validation(self, node: ast.AST) -> bool:
        """Check if a view has input validation"""
        validation_patterns = {'clean', 'validate', 'form.is_valid'}
        return any(
            isinstance(child, ast.Call) and
            isinstance(child.func, ast.Attribute) and
            child.func.attr in validation_patterns
            for child in ast.walk(node)
        )
    
    def _has_permission_check(self, node: ast.AST) -> bool:
        """Check if a view has permission checks"""
        permission_patterns = {
            'has_permission', 'is_authenticated', 'permission_required',
            'login_required', 'user_passes_test'
        }
        return any(
            isinstance(child, (ast.Call, ast.Name)) and
            hasattr(child, 'id' if isinstance(child, ast.Name) else 'func') and
            any(pattern in (child.id if isinstance(child, ast.Name) else child.func.attr)
                for pattern in permission_patterns)
            for child in ast.walk(node)
        )
    
    def _is_view_function(self, node: ast.AST) -> bool:
        """Check if a function is a Django view"""
        # Check decorators
        if hasattr(node, 'decorator_list'):
            decorators = {
                d.id if isinstance(d, ast.Name)
                else (d.func.id if isinstance(d.func, ast.Name)
                     else d.func.attr if isinstance(d.func, ast.Attribute)
                     else '')
                for d in node.decorator_list
            }
            view_decorators = {'login_required', 'permission_required', 'api_view'}
            if any(d in view_decorators for d in decorators):
                return True
                
        # Check parameters
        if isinstance(node, ast.FunctionDef):
            args = node.args.args
            return any(arg.arg == 'request' for arg in args)
            
        return False
    
    def _is_model_query(self, node: ast.AST) -> bool:
        """Check if a node is a model query"""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                query_methods = {'filter', 'get', 'all', 'create', 'update'}
                return node.func.attr in query_methods
        return False
    
    def _get_setting_value(self, node: ast.AST) -> Any:
        """Get the value of a settings node"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.List):
            return [self._get_setting_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Dict):
            return {
                self._get_setting_value(k): self._get_setting_value(v)
                for k, v in zip(node.keys, node.values)
            }
        return None

class FlaskAnalyzer(BaseFrameworkAnalyzer):
    """Analyzer for Flask applications"""
    
    def analyze_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Analyze Flask file for GDPR compliance issues"""
        # Implementation for Flask-specific analysis
        pass
        
    def get_data_flow_patterns(self) -> Dict[str, List[str]]:
        """Get Flask-specific data flow patterns"""
        return {
            'route_data': [
                r'request\.form',
                r'request\.args',
                r'request\.json'
            ],
            'session_data': [
                r'session\[',
                r'session\.get'
            ]
        }

class FastAPIAnalyzer(BaseFrameworkAnalyzer):
    """Analyzer for FastAPI applications"""
    
    def analyze_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Analyze FastAPI file for GDPR compliance issues"""
        # Implementation for FastAPI-specific analysis
        pass
        
    def get_data_flow_patterns(self) -> Dict[str, List[str]]:
        """Get FastAPI-specific data flow patterns"""
        return {
            'pydantic_models': [
                r'BaseModel',
                r'Field\(',
                r'validator\('
            ],
            'route_data': [
                r'Depends\(',
                r'Body\(',
                r'Query\('
            ]
        }

class ReactAnalyzer(BaseFrameworkAnalyzer):
    """Analyzer for React applications"""
    
    def analyze_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Analyze React file for GDPR compliance issues"""
        # Implementation for React-specific analysis
        pass
        
    def get_data_flow_patterns(self) -> Dict[str, List[str]]:
        """Get React-specific data flow patterns"""
        return {
            'state_data': [
                r'useState\(',
                r'useReducer\(',
                r'this\.state'
            ],
            'form_data': [
                r'onChange=',
                r'onSubmit=',
                r'handleSubmit'
            ]
        }

class CloudServiceAnalyzer:
    """Analyzer for cloud service configurations"""
    
    def __init__(self, service_type: str):
        self.service_type = service_type
        self.issues: List[Dict[str, Any]] = []
        
    def analyze_config(self, config_path: str) -> List[Dict[str, Any]]:
        """Analyze cloud service configuration"""
        if self.service_type == 'aws':
            return self._analyze_aws_config(config_path)
        elif self.service_type == 'azure':
            return self._analyze_azure_config(config_path)
        elif self.service_type == 'gcp':
            return self._analyze_gcp_config(config_path)
        return []
        
    def _analyze_aws_config(self, config_path: str) -> List[Dict[str, Any]]:
        """Analyze AWS configuration files"""
        # Implementation for AWS config analysis
        pass
        
    def _analyze_azure_config(self, config_path: str) -> List[Dict[str, Any]]:
        """Analyze Azure configuration files"""
        # Implementation for Azure config analysis
        pass
        
    def _analyze_gcp_config(self, config_path: str) -> List[Dict[str, Any]]:
        """Analyze GCP configuration files"""
        # Implementation for GCP config analysis
        pass

def get_analyzer(framework_type: str) -> BaseFrameworkAnalyzer:
    """Get appropriate analyzer for framework type"""
    analyzers = {
        'django': DjangoAnalyzer,
        'flask': FlaskAnalyzer,
        'fastapi': FastAPIAnalyzer,
        'react': ReactAnalyzer
    }
    
    analyzer_class = analyzers.get(framework_type.lower())
    if analyzer_class:
        return analyzer_class()
    else:
        raise ValueError(f"No analyzer available for framework: {framework_type}") 