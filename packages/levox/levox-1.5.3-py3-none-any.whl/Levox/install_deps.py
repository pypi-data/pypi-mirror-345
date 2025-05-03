#!/usr/bin/env python
"""
Levox Dependency Installer

This script helps install the right dependencies for Levox based on your system.
It will install the core dependencies and optionally the advanced dependencies
if your system supports them.
"""
import sys
import subprocess
import platform
import os

def print_header():
    """Print the installer header."""
    print("\n" + "=" * 60)
    print("Levox Dependency Installer")
    print("=" * 60)
    print("This script will install the required dependencies for Levox.")
    print("System info:", platform.platform())
    print("Python version:", sys.version.split('\n')[0])
    print("=" * 60 + "\n")

def install_dependencies(include_advanced=False):
    """Install dependencies using pip."""
    print("Installing core dependencies...")
    
    # Core dependencies - these are required
    core_deps = [
        "prompt_toolkit>=3.0.0",
        "ollama>=0.1.0",
        "regex>=2023.0.0",
        "pyyaml>=6.0.0", 
        "rich>=13.0.0",
        "tqdm>=4.65.0",
        "watchdog>=3.0.0",
        "matplotlib>=3.5.0",
        "numpy>=1.20.0",
        "weasyprint>=53.0",
        "apscheduler>=3.9.0",
        "requests>=2.27.0"
    ]
    
    # Advanced dependencies - optional but enable better features
    advanced_deps = [
        "scikit-learn>=1.0.0",
        "joblib>=1.1.0",
        "pandas>=1.3.0",
        "nltk>=3.6.0",
        "scipy>=1.7.0"
    ]
    
    # Install core dependencies
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + core_deps)
        print("Core dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing core dependencies: {e}")
        return False
    
    # Install advanced dependencies if requested
    if include_advanced:
        print("\nInstalling advanced dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + advanced_deps)
            print("Advanced dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing advanced dependencies: {e}")
            print("Levox will still work, but with reduced functionality.")
    
    return True

def main():
    """Main function."""
    print_header()
    
    # Ask user if they want to install advanced dependencies
    response = input("Install advanced dependencies for better meta-learning? (y/n) [y]: ").lower() or 'y'
    include_advanced = response in ('y', 'yes')
    
    if include_advanced:
        print("\nAdvanced dependencies will be installed if compatible with your system.")
    else:
        print("\nOnly core dependencies will be installed.")
    
    # Confirm installation
    confirm = input("\nProceed with installation? (y/n) [y]: ").lower() or 'y'
    if confirm not in ('y', 'yes'):
        print("Installation canceled.")
        return
    
    # Install dependencies
    success = install_dependencies(include_advanced)
    
    # Print final message
    if success:
        print("\nDependencies installed successfully!")
        print("You can now run Levox by executing: python main.py")
    else:
        print("\nError installing dependencies. Please check the error messages above.")

if __name__ == "__main__":
    main() 