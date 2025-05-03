"""
Resource path management for Levox

This module provides functions to access resources (rules, examples, config files)
in both development mode and when running from a bundled executable.
"""
import os
import sys
from pathlib import Path

def is_bundled():
    """Check if the application is running as a bundled executable"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_base_dir():
    """Get the base directory for the application"""
    if is_bundled():
        # Running as a bundled executable
        return getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.executable)))
    else:
        # Running in development mode
        return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def get_resource_path(relative_path):
    """
    Get absolute path to a resource, works for development and bundled app
    
    Args:
        relative_path: Path relative to the resources directory
        
    Returns:
        Absolute path to the resource
    """
    base_dir = get_base_dir()
    
    # Try different possible locations
    possible_paths = [
        # First check if resource exists in specified resources directory in bundled app
        os.path.join(base_dir, 'resources', relative_path),
        # Then check if resource exists directly in the bundle
        os.path.join(base_dir, relative_path),
        # Finally check in the development structure
        os.path.join(base_dir, relative_path)
    ]
    
    # Return the first path that exists
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If none exist, return the first path (bundled resources) and let the
    # calling code handle the case where the file doesn't exist
    return possible_paths[0]

def get_rules_path():
    """Get the path to the rules directory"""
    return get_resource_path('rules')

def get_examples_path():
    """Get the path to the examples directory"""
    return get_resource_path('examples')

def get_config_path():
    """Get the path to the config directory or file"""
    if is_bundled():
        # In bundled app, look for config in resources
        return get_resource_path('.levoxignore')
    else:
        # In development, look in root directory
        return os.path.join(get_base_dir(), '.levoxignore')

def get_user_data_dir():
    """Get the path to the user data directory"""
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, '.levox')

def ensure_user_data_dir():
    """Ensure the user data directory exists"""
    user_data_dir = get_user_data_dir()
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir, exist_ok=True)
    return user_data_dir 