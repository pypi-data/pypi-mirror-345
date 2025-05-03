#!/usr/bin/env python
"""
Main entry point for the Levox GDPR compliance tool.
"""
import sys
from levox.cli import main as cli_main

def main():
    """Main entry point."""
    return cli_main()

if __name__ == "__main__":
    sys.exit(main())
