"""
Levox - GDPR, PII and Data Flow Compliance Tool

A tool for scanning, fixing, and reporting GDPR compliance issues in code.
"""

__version__ = "1.5.0"
__author__ = "Levox Team"

# Import commonly used modules for easier access
try:
    from levox.scanner import Scanner, GDPRIssue
    from levox.fixer import Fixer
    from levox.cli import main as cli_main
except ImportError:
    # These may not be available during installation
    pass

# Convenience function for scanning
def scan_directory(directory_path):
    """
    Scan a directory for GDPR compliance issues.
    
    Args:
        directory_path: Path to directory to scan
        
    Returns:
        List of GDPRIssue objects
    """
    from levox.scanner import Scanner
    scanner = Scanner(directory_path)
    return scanner.scan_directory()
