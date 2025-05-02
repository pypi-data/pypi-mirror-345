# Levox - GDPR Compliance Tool

A comprehensive tool for scanning, fixing, and reporting GDPR compliance issues in code.

## Features

- **GDPR Compliance Scanning**: Detect potential GDPR violations in your codebase
- **PII Detection**: Identify personally identifiable information in your code
- **Data Flow Analysis**: Track how data moves through your application
- **Automated Remediation**: Get suggestions for fixing compliance issues
- **Detailed Reporting**: Generate reports in multiple formats

## Installation

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