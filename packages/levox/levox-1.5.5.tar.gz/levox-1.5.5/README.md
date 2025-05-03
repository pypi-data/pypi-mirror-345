# Levox - GDPR Compliance Assistant

A powerful tool for scanning, fixing, and reporting GDPR compliance issues in code.

## Installation

```bash
pip install levox
```

## Quick Start

After installation, you can run Levox in two ways:

1. As a command line tool:
```bash
levox
```

2. In your Python code:
```python
from levox import main
main()
```

## Troubleshooting

### Command Not Found

If you get a "command not found" error when trying to run `levox`, it might be because Python's Scripts directory is not in your PATH. Here's how to fix it:

#### Windows
1. Open Command Prompt or PowerShell
2. Add Python Scripts to PATH:
```bash
set PATH=%PATH%;C:\Users\<username>\AppData\Local\Programs\Python\Python3x\Scripts
```
Or permanently add it through System Properties > Environment Variables

#### Unix/Linux/Mac
1. Open terminal
2. Add Python bin to PATH:
```bash
export PATH=$PATH:$(python3 -m site --user-base)/bin
```
Add this line to your `~/.bashrc` or `~/.zshrc` to make it permanent

### Verifying Installation

To verify that Levox is properly installed:
```bash
pip show levox
```

This should show the package details including version and installation location.

## Features

- **GDPR Compliance Scanning**: Detect potential GDPR violations in your codebase
- **PII Detection**: Identify personally identifiable information in your code
- **Data Flow Analysis**: Track how data moves through your application
- **Automated Remediation**: Get suggestions for fixing compliance issues
- **Detailed Reporting**: Generate reports in multiple formats

## Configuration

Install the package using pip:

```bash
pip install levox
```

## Usage

### Command Line Interface

```bash
# Scan a directory for GDPR compliance issues
levox scan [directory]

# Fix GDPR compliance issues in a directory
levox fix [directory]

# Show benchmarks and information
levox about

# Run benchmarks
levox benchmark --run
```

### As a Library

```python
from levox.scanner import Scanner
from levox.fixer import Fixer

# Scan a directory
scanner = Scanner("path/to/your/code")
issues = scanner.scan_directory()

# Get suggestions for fixing issues
fixer = Fixer()
for issue in issues:
    fix = fixer.generate_fix(issue)
    print(fix)
```

## Configuration

Levox can be configured using a `levox_config.json` file in your project directory or in the user's home directory (`~/.levox/config.json`).

Example configuration:

```json
{
  "exclude": [
    "**/test/**",
    "**/node_modules/**",
    "**/__pycache__/**"
  ],
  "severity_threshold": "medium"
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 