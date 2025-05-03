# Levox - GDPR Compliance Scanner

A powerful tool for scanning, fixing, and reporting GDPR compliance issues in your codebase.

## Features

- GDPR Compliance Scanning
- PII Detection and Classification
- Data Flow Analysis
- AI-Assisted Remediation
- Detailed HTML Reports
- Interactive Command Line Interface
- AST-based Code Analysis
- Meta-Learning for Reduced False Positives

## Installation

### Using pip (recommended)

```bash
pip install levox
```

### From source

```bash
git clone https://github.com/levox-tech/levox.git
cd levox
pip install -e .
```

## Quick Start

1. Basic scan:
```bash
levox /path/to/your/project
```

2. Scan with HTML report:
```bash
levox /path/to/your/project --format html --output report.html
```

3. Scan and fix issues:
```bash
levox /path/to/your/project --fix
```

4. Interactive mode:
```bash
levox
```

## Important Notes

- For paths with spaces, use quotes:
  ```bash
  levox "C:\Users\name\My Project"
  ```

- Use forward slashes or escaped backslashes in Windows paths:
  ```bash
  levox C:/Users/name/Project
  # or
  levox C:\\Users\\name\\Project
  ```

## Common Issues

1. "Directory not found" error:
   - Make sure the path exists
   - Use quotes for paths with spaces
   - Use correct path separators

2. Permission issues:
   - Run with appropriate permissions
   - Check file/directory access rights

3. Installation issues:
   - Make sure Python 3.7+ is installed
   - Update pip: `python -m pip install --upgrade pip`
   - Install in a virtual environment if needed

## Documentation

For detailed documentation, visit: https://levox.io/docs

## Support

- GitHub Issues: https://github.com/levox-tech/levox/issues
- Email: support@levox.io
- Documentation: https://levox.io/docs

## License

MIT License - see LICENSE file for details 