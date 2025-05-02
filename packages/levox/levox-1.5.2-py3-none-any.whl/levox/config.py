"""
Configuration module for Levox GDPR compliance tool.
"""
from typing import Dict, List, Any, Optional
import os
import re
import json
from pathlib import Path

class Config:
    """Configuration class for Levox application settings."""
    
    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration with optional settings dictionary.
        
        Args:
            settings: Dictionary of configuration settings
        """
        self.settings = settings or {}
        
        # Default settings
        self.defaults = {
            # Scanner settings
            "scan": {
                "exclude_dirs": ["node_modules", "venv", ".git", "__pycache__"],
                "exclude_files": [".pyc", ".jpg", ".png", ".gif", ".pdf"],
                "max_file_size": 1024 * 1024,  # 1MB
                "enhanced_patterns": True,
                "false_positive_threshold": 0.8,
                "consider_non_code": False,  # Don't analyze comments, strings by default
                "ignore_test_code": True,    # Ignore test code by default
                "ignore_file_patterns": [],  # File patterns to ignore
                "ignore_code_patterns": [],  # Code patterns to ignore
            },
            
            # Remediation settings
            "remediation": {
                "auto_fix": False,
                "ai_provider": "ollama",
                "ai_model": "deepseek-r1:1.5b",
                "template_dir": "templates/fixes",
                "backup_files": True,
                "group_similar_issues": True,  # Group similar issues
                "max_group_distance": 10,      # Maximum line distance for grouping
            },
            
            # Report settings
            "report": {
                "default_format": "json",
                "include_code_snippets": True,
                "max_snippet_lines": 5,
                "group_by_file": True,
                "group_by_type": True,
            },
            
            # Environment
            "environment": {
                "is_production": True,  # Default to production environment
                "test_directories": ["test", "tests", "testing"],
                "development_indicators": ["dev", "development", "local", "sandbox"],
            }
        }
        
        # Load ignore patterns if available
        self.ignore_patterns = self._load_ignore_patterns()
        
    def _load_ignore_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load ignore patterns from .levoxignore file if it exists.
        
        Returns:
            Dictionary of ignore patterns
        """
        ignore_patterns = {
            "file": [],
            "pattern": []
        }
        
        # Check for .levoxignore file in current directory and parent directories
        current_dir = os.getcwd()
        ignore_file = None
        
        while current_dir and not ignore_file:
            candidate = os.path.join(current_dir, ".levoxignore")
            if os.path.exists(candidate):
                ignore_file = candidate
                break
                
            # Move up one directory
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                break
            current_dir = parent_dir
            
        if not ignore_file:
            return ignore_patterns
            
        try:
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                        
                    # Parse YAML-like entries
                    if line.startswith('ignore:'):
                        continue
                        
                    if line.startswith('  - file:'):
                        pattern = line[len('  - file:'):].strip()
                        ignore_patterns["file"].append({"pattern": pattern})
                        
                    elif line.startswith('  - pattern:'):
                        pattern = line[len('  - pattern:'):].strip()
                        # Remove quotes if present
                        if pattern.startswith('"') and pattern.endswith('"'):
                            pattern = pattern[1:-1]
                        ignore_patterns["pattern"].append({"pattern": pattern})
        except Exception as e:
            print(f"Error loading .levoxignore file: {e}")
            
        return ignore_patterns
    
    def should_ignore_file(self, file_path: str) -> bool:
        """
        Check if a file should be ignored based on ignore patterns.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be ignored, False otherwise
        """
        # Check exclude_files extensions
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in self.get("scan.exclude_files", []):
            return True
            
        # Check exclude_dirs
        for exclude_dir in self.get("scan.exclude_dirs", []):
            if exclude_dir in file_path:
                return True
                
        # Check ignore_file_patterns from settings
        for pattern in self.get("scan.ignore_file_patterns", []):
            if re.search(pattern, file_path):
                return True
                
        # Check file patterns from .levoxignore
        for pattern_dict in self.ignore_patterns.get("file", []):
            pattern = pattern_dict.get("pattern", "")
            if self._matches_glob_pattern(file_path, pattern):
                return True
                
        return False
    
    def should_ignore_code_pattern(self, code: str) -> bool:
        """
        Check if a code pattern should be ignored.
        
        Args:
            code: Code snippet to check
            
        Returns:
            True if the code pattern should be ignored, False otherwise
        """
        # Check ignore_code_patterns from settings
        for pattern in self.get("scan.ignore_code_patterns", []):
            if re.search(pattern, code):
                return True
                
        # Check pattern patterns from .levoxignore
        for pattern_dict in self.ignore_patterns.get("pattern", []):
            pattern = pattern_dict.get("pattern", "")
            if re.search(pattern, code):
                return True
                
        return False
    
    def _matches_glob_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if a path matches a glob pattern.
        
        Args:
            path: Path to check
            pattern: Glob pattern
            
        Returns:
            True if the path matches the pattern, False otherwise
        """
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key with optional default.
        
        Args:
            key: Configuration key (can use dot notation like 'scan.exclude_dirs')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Handle dot notation
        if '.' in key:
            section, option = key.split('.', 1)
            section_dict = self.settings.get(section, self.defaults.get(section, {}))
            return section_dict.get(option, self.defaults.get(section, {}).get(option, default))
        
        return self.settings.get(key, self.defaults.get(key, default))
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (can use dot notation)
            value: Value to set
        """
        # Handle dot notation
        if '.' in key:
            section, option = key.split('.', 1)
            if section not in self.settings:
                self.settings[section] = {}
            self.settings[section][option] = value
        else:
            self.settings[key] = value
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load configuration from a JSON file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        import json
        
        try:
            with open(file_path, 'r') as f:
                self.settings.update(json.load(f))
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save configuration to a JSON file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            True if saved successfully, False otherwise
        """
        import json
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False 