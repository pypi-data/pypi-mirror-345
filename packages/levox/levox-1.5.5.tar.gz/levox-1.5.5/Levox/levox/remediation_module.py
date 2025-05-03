"""
Remediation Module for GDPR compliance issues.

This module provides automated fixes for GDPR compliance issues and
generates documentation for GDPR compliance.
"""
import os
import json
import ast
from typing import Dict, List, Set, Any, Optional, Tuple
from pathlib import Path
import tempfile
from datetime import datetime
import difflib
import re
import logging
import importlib.util

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from levox.scanner import GDPRIssue
from levox.gdpr_articles import get_articles_for_issue_type, format_article_reference, get_article_info
from levox.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RemediationModule")

class AutoFixer:
    """
    Automatically applies fixes for GDPR compliance issues.
    """
    
    def __init__(self, model_name: str = "deepseek-r1:1.5b"):
        """Initialize the auto fixer."""
        self.model_name = model_name
        
    def fix_issue(self, issue: GDPRIssue, dry_run: bool = True) -> Dict[str, Any]:
        """
        Automatically fix a GDPR compliance issue.
        
        Args:
            issue: The GDPRIssue to fix
            dry_run: If True, only generate the fix but don't apply it
            
        Returns:
            Dict with fix results, including diff
        """
        if not OLLAMA_AVAILABLE:
            return {
                "success": False, 
                "message": "Ollama is not available. Install with 'pip install ollama'",
                "diff": ""
            }
            
        try:
            # Read file content
            with open(issue.file_path, 'r', encoding='utf-8', errors='replace') as f:
                original_content = f.read()
                
            # Split into lines
            lines = original_content.splitlines()
            
            # Get context around the issue
            context_start = max(0, issue.line_number - 10)
            context_end = min(len(lines), issue.line_number + 10)
            context_lines = lines[context_start:context_end]
            context = "\n".join(context_lines)
            
            # Create AI prompt
            prompt = self._create_fix_prompt(issue, context, context_start)
            
            # Get AI response
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                temperature=0.1,
                top_p=0.95,
                max_tokens=1000
            )
            
            if not response or 'response' not in response:
                return {"success": False, "message": "No response from AI model", "diff": ""}
                
            # Extract the fix
            fixed_code = self._extract_code_from_response(response['response'])
            
            if not fixed_code:
                return {"success": False, "message": "Could not extract fixed code from AI response", "diff": ""}
                
            # Create patched content
            new_lines = lines.copy()
            fixed_lines = fixed_code.splitlines()
            
            # Replace the context lines with the fixed lines
            new_lines[context_start:context_end] = fixed_lines
            patched_content = "\n".join(new_lines)
            
            # Create diff
            diff = self._create_diff(
                original_content.splitlines(), 
                patched_content.splitlines(), 
                issue.file_path
            )
            
            # Apply the fix if not dry run
            if not dry_run:
                with open(issue.file_path, 'w', encoding='utf-8') as f:
                    f.write(patched_content)
                    
            return {
                "success": True,
                "message": f"Fix {'generated' if dry_run else 'applied'} for issue in {issue.file_path}:{issue.line_number}",
                "diff": diff
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error fixing issue: {e}", "diff": ""}
    
    def _create_fix_prompt(self, issue: GDPRIssue, context: str, context_start: int) -> str:
        """
        Create a prompt for fixing a GDPR issue.
        
        Args:
            issue: The GDPRIssue to fix
            context: The code context around the issue
            context_start: The starting line number of the context
            
        Returns:
            Prompt string for AI
        """
        # Get article information
        article_info = ""
        for article in issue.articles:
            info = get_article_info(article)
            if info:
                article_info += f"Article {article}: {info['title']}\n{info['summary']}\n\n"
        
        prompt = f"""You are a GDPR compliance expert and software developer fixing code to comply with GDPR.

ISSUE DETAILS:
- File: {issue.file_path}
- Line: {issue.line_number}
- Issue Type: {issue.issue_type}
- Description: {issue.description}

GDPR ARTICLES RELEVANT TO THIS ISSUE:
{article_info}

RECOMMENDED REMEDIATION:
{issue.remediation}

CODE CONTEXT (Line {context_start+1} to {context_start+len(context.splitlines())}):
```
{context}
```

YOUR TASK:
1. Fix the code to address the GDPR compliance issue
2. Implement the recommended remediation
3. Add appropriate comments explaining the GDPR compliance measures
4. Preserve the existing functionality while making it GDPR compliant
5. Return ONLY the fixed code block (including the context above and below)

IMPORTANT:
- Make minimal changes to fix the issue while preserving functionality
- Add clear comments explaining GDPR compliance measures
- If you're unsure about something, use explicit TODO comments
- Return ONLY the fixed code with no other text

FIXED CODE:
"""
        return prompt
    
    def _extract_code_from_response(self, response: str) -> str:
        """
        Extract code from AI response.
        
        Args:
            response: The AI response text
            
        Returns:
            The extracted code
        """
        if "```" in response:
            # Extract code between triple backticks
            parts = response.split("```")
            if len(parts) > 1:
                # Check if there's a language identifier
                code = parts[1]
                if code.startswith("python") or code.startswith("py"):
                    code = code[code.find("\n")+1:]
                return code.strip()
        
        # If no code block, return the whole response
        return response.strip()
    
    def _create_diff(self, original_lines: List[str], new_lines: List[str], file_path: str) -> str:
        """
        Create a unified diff between original and new content.
        
        Args:
            original_lines: Original content lines
            new_lines: New content lines
            file_path: Path to the file
            
        Returns:
            Unified diff as string
        """
        diff = difflib.unified_diff(
            original_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        )
        return "\n".join(diff)


class DocumentationGenerator:
    """
    Generates GDPR compliance documentation.
    """
    
    def __init__(self, base_dir: str = "."):
        """Initialize the documentation generator."""
        self.base_dir = Path(base_dir)
        
    def generate_processing_record(self, issues: List[GDPRIssue], output_file: Optional[str] = None) -> str:
        """
        Generate a record of processing activities based on detected issues.
        
        Args:
            issues: List of detected GDPR issues
            output_file: Path to save the documentation (optional)
            
        Returns:
            The generated documentation as string
        """
        if not output_file:
            output_file = self.base_dir / "gdpr_processing_record.md"
            
        # Group issues by type
        issues_by_type = {}
        for issue in issues:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = []
            issues_by_type[issue.issue_type].append(issue)
            
        # Generate documentation
        doc = [
            "# Record of Processing Activities",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overview",
            "",
            "This document provides a record of processing activities as required by Article 30 of the GDPR.",
            "It is based on automated scanning of the codebase to identify personal data processing activities.",
            "",
            f"Total issues detected: {len(issues)}",
            ""
        ]
        
        # Add summary of issue types
        doc.append("## Summary of Processing Activities")
        doc.append("")
        for issue_type, type_issues in issues_by_type.items():
            doc.append(f"### {issue_type.replace('_', ' ').title()}")
            doc.append("")
            doc.append(f"Number of occurrences: {len(type_issues)}")
            doc.append("")
            
            # List relevant articles
            articles = set()
            for issue in type_issues:
                articles.update(issue.articles)
            
            if articles:
                doc.append("Relevant GDPR Articles:")
                doc.append("")
                for article in sorted(articles):
                    info = get_article_info(article)
                    if info:
                        doc.append(f"- **Article {article}**: {info['title']}")
                doc.append("")
            
            # Add example locations
            doc.append("Example locations:")
            doc.append("")
            for i, issue in enumerate(type_issues[:5]):  # Show up to 5 examples
                doc.append(f"- {issue.file_path}:{issue.line_number}")
            
            if len(type_issues) > 5:
                doc.append(f"- ... and {len(type_issues) - 5} more")
            
            doc.append("")
        
        # Add detailed inventory
        doc.append("## Detailed Data Processing Inventory")
        doc.append("")
        
        # Look for data collection issues to determine categories of data subjects and data
        collection_issues = issues_by_type.get("pii_collection", [])
        subjects = set()
        categories = set()
        
        for issue in collection_issues:
            desc = issue.description.lower()
            
            # Try to identify data subjects
            if "customer" in desc or "client" in desc:
                subjects.add("Customers/Clients")
            if "employee" in desc or "staff" in desc:
                subjects.add("Employees")
            if "user" in desc:
                subjects.add("Users")
            if "patient" in desc:
                subjects.add("Patients")
            
            # Try to identify categories of data
            if "name" in desc:
                categories.add("Names")
            if "email" in desc:
                categories.add("Email addresses")
            if "address" in desc:
                categories.add("Postal addresses")
            if "phone" in desc:
                categories.add("Phone numbers")
            if "birth" in desc or "dob" in desc:
                categories.add("Date of birth")
            if "ssn" in desc or "social security" in desc:
                categories.add("Social security numbers")
            if "passport" in desc:
                categories.add("Passport information")
            if "health" in desc or "medical" in desc:
                categories.add("Health information")
            if "financial" in desc or "payment" in desc or "credit" in desc:
                categories.add("Financial information")
        
        # If we didn't identify any, add generic ones
        if not subjects:
            subjects.add("Application users")
        if not categories:
            categories.add("Personal identifiers")
            categories.add("Contact information")
        
        # Add data subjects section
        doc.append("### Categories of Data Subjects")
        doc.append("")
        for subject in subjects:
            doc.append(f"- {subject}")
        doc.append("")
        
        # Add data categories section
        doc.append("### Categories of Personal Data")
        doc.append("")
        for category in categories:
            doc.append(f"- {category}")
        doc.append("")
        
        # Add legal basis section
        doc.append("### Legal Basis for Processing")
        doc.append("")
        doc.append("Based on the code scan, the following legal bases may be relevant:")
        doc.append("")
        
        # Look for consent issues
        if "consent_issues" in issues_by_type:
            doc.append("- **Consent (Article 6(1)(a))**: Implementation of proper consent mechanisms may be required")
        
        # Add standard legal bases as possibilities
        doc.append("- **Contract (Article 6(1)(b))**: Processing necessary for performance of a contract")
        doc.append("- **Legal Obligation (Article 6(1)(c))**: Processing necessary for compliance with legal obligations")
        doc.append("- **Legitimate Interests (Article 6(1)(f))**: Processing necessary for legitimate interests")
        doc.append("")
        doc.append("**Note**: The application owners should review and confirm the appropriate legal basis for each processing activity.")
        doc.append("")
        
        # Add data transfers section
        transfer_issues = issues_by_type.get("data_transfer", [])
        if transfer_issues:
            doc.append("### Data Transfers")
            doc.append("")
            doc.append("Potential data transfers identified:")
            doc.append("")
            
            for issue in transfer_issues[:5]:  # Show up to 5 examples
                doc.append(f"- {issue.file_path}:{issue.line_number} - {issue.description.split('.')[0]}")
            
            if len(transfer_issues) > 5:
                doc.append(f"- ... and {len(transfer_issues) - 5} more")
            
            doc.append("")
        
        # Add security measures section
        security_issues = issues_by_type.get("security_measures", [])
        doc.append("### Technical and Organizational Security Measures")
        doc.append("")
        
        if security_issues:
            doc.append("Security concerns identified that should be addressed:")
            doc.append("")
            
            for issue in security_issues[:5]:  # Show up to 5 examples
                doc.append(f"- {issue.file_path}:{issue.line_number} - {issue.description.split('.')[0]}")
            
            if len(security_issues) > 5:
                doc.append(f"- ... and {len(security_issues) - 5} more")
        else:
            doc.append("No specific security issues were identified in the scan, but the application should implement:")
            doc.append("")
            doc.append("- Encryption of personal data")
            doc.append("- Access controls")
            doc.append("- Regular security assessments")
            doc.append("- Secure data storage")
        
        doc.append("")
        
        # Add retention policies section
        retention_issues = issues_by_type.get("data_retention", [])
        doc.append("### Data Retention Policies")
        doc.append("")
        
        if retention_issues:
            doc.append("Data retention concerns identified:")
            doc.append("")
            
            for issue in retention_issues[:5]:  # Show up to 5 examples
                doc.append(f"- {issue.file_path}:{issue.line_number} - {issue.description.split('.')[0]}")
            
            if len(retention_issues) > 5:
                doc.append(f"- ... and {len(retention_issues) - 5} more")
        else:
            doc.append("No specific data retention issues were identified in the scan, but the application should implement:")
            doc.append("")
            doc.append("- Clear data retention periods")
            doc.append("- Automated data deletion processes")
            doc.append("- Documentation of retention policies")
        
        doc.append("")
        
        # Save the documentation
        documentation = "\n".join(doc)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(documentation)
        
        return documentation


class RemediationModule:
    """
    Main remediation module that coordinates fixes and documentation.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the remediation module.
        
        Args:
            config: Configuration object with remediation settings
        """
        self.config = config or Config()
        self.fix_templates = self._load_fix_templates()
        self.supported_languages = {
            "python": {
                "extensions": [".py"],
                "handlers": {
                    "consent_issues": self._fix_python_consent_issues,
                    "data_minimization": self._fix_python_data_minimization,
                    "pii_collection": self._fix_python_pii_collection,
                    "data_transfer": self._fix_python_data_transfer,
                    "data_retention": self._fix_python_data_retention,
                    "access_control": self._fix_python_access_control,
                }
            },
            "javascript": {
                "extensions": [".js", ".jsx", ".ts", ".tsx"],
                "handlers": {
                    "consent_issues": self._fix_js_consent_issues,
                    "data_minimization": self._fix_js_data_minimization,
                    "pii_collection": self._fix_js_pii_collection,
                }
            }
        }
        
        # Track application metrics
        self.metrics = {
            "total_issues_fixed": 0,
            "fixes_by_type": {},
            "successful_fixes": 0,
            "failed_fixes": 0
        }
        
        self.auto_fixer = AutoFixer(self.config.model_name)
        self.doc_generator = DocumentationGenerator(self.config.base_dir)
        
    def _load_fix_templates(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Load code fix templates from templates directory."""
        templates_path = os.path.join(os.path.dirname(__file__), "templates", "fixes")
        templates = {}
        
        if not os.path.exists(templates_path):
            logger.warning(f"Templates directory not found: {templates_path}")
            return templates
            
        for lang_file in os.listdir(templates_path):
            if lang_file.endswith('.json'):
                lang = lang_file.split('.')[0]
                try:
                    with open(os.path.join(templates_path, lang_file), 'r') as f:
                        templates[lang] = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading templates for {lang}: {str(e)}")
        
        return templates

    def suggest_fixes(self, issues: List[Dict[str, Any]], file_path: str) -> List[Dict[str, Any]]:
        """
        Generate suggested fixes for the given GDPR compliance issues.
        
        Args:
            issues: List of GDPR issues detected in the file
            file_path: Path to the file with issues
        
        Returns:
            List of issues with added remediation suggestions
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        language = self._detect_language(file_ext)
        
        if not language:
            logger.warning(f"Unsupported file type for remediation: {file_ext}")
            return issues
        
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            
        issues_with_fixes = []
        for issue in issues:
            issue_type = issue.get('issue_type', '')
            issue_with_fix = issue.copy()
            
            # Generate context-aware fix suggestions
            if issue_type in self.supported_languages[language]["handlers"]:
                handler = self.supported_languages[language]["handlers"][issue_type]
                suggested_fix = handler(issue, file_content)
                issue_with_fix["remediation_code"] = suggested_fix
                issue_with_fix["can_auto_fix"] = bool(suggested_fix)
            else:
                # Generate generic suggestion based on templates if available
                suggested_fix = self._get_template_fix(language, issue_type, issue)
                issue_with_fix["remediation_suggestion"] = suggested_fix
                issue_with_fix["can_auto_fix"] = False
            
            issues_with_fixes.append(issue_with_fix)
            
        return issues_with_fixes

    def apply_fix(self, issue: Dict[str, Any], file_path: str) -> Tuple[bool, str]:
        """
        Apply an automated fix for a GDPR issue.
        
        Args:
            issue: The issue to fix
            file_path: Path to the file to modify
        
        Returns:
            Tuple of (success_flag, message)
        """
        if not issue.get("can_auto_fix", False):
            return False, "This issue does not support automated fixing"
        
        file_ext = os.path.splitext(file_path)[1].lower()
        language = self._detect_language(file_ext)
        
        if not language:
            return False, f"Unsupported file type: {file_ext}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            line_number = issue.get("line_number", 0)
            issue_type = issue.get("issue_type", "")
            
            if not issue.get("remediation_code"):
                return False, "No remediation code available"
                
            updated_content = self._apply_code_fix(
                file_content, 
                line_number, 
                issue.get("remediation_code", ""), 
                language
            )
            
            if updated_content == file_content:
                return False, "No changes were made"
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            # Update metrics
            self.metrics["total_issues_fixed"] += 1
            self.metrics["successful_fixes"] += 1
            self.metrics["fixes_by_type"][issue_type] = self.metrics["fixes_by_type"].get(issue_type, 0) + 1
            
            relevant_articles = get_articles_for_issue_type(issue_type)
            article_refs = [format_article_reference(article) for article in relevant_articles]
            
            return True, f"Successfully fixed {issue_type} issue (complies with {', '.join(article_refs)})"
            
        except Exception as e:
            logger.error(f"Error applying fix: {str(e)}")
            self.metrics["failed_fixes"] += 1
            return False, f"Failed to apply fix: {str(e)}"

    def _detect_language(self, file_extension: str) -> Optional[str]:
        """Determine the programming language based on file extension."""
        for lang, info in self.supported_languages.items():
            if file_extension in info["extensions"]:
                return lang
        return None

    def _get_template_fix(self, language: str, issue_type: str, issue: Dict[str, Any]) -> str:
        """Get a template-based fix for the given issue type and language."""
        if language in self.fix_templates and issue_type in self.fix_templates[language]:
            template = self.fix_templates[language][issue_type]
            
            # Customize template based on issue details
            customized_template = template.get("template", "")
            for key, value in issue.items():
                if isinstance(value, str):
                    customized_template = customized_template.replace(f"{{{key}}}", value)
            
            return customized_template
        
        # Fallback to generic advice
        return self._generate_generic_advice(issue_type)
    
    def _generate_generic_advice(self, issue_type: str) -> str:
        """Generate generic remediation advice based on the issue type."""
        advice_map = {
            "consent_issues": "Implement explicit user consent mechanisms before processing data. Ensure consent is freely given, specific, informed, and unambiguous.",
            "data_minimization": "Review the data being collected and only process what is necessary for the specified purpose. Remove any excessive data collection.",
            "pii_collection": "Ensure proper safeguards for PII collection. Implement encryption, access controls, and maintain records of processing activities.",
            "data_transfer": "Implement appropriate safeguards for international data transfers, such as Standard Contractual Clauses or Privacy Shield compliance.",
            "data_retention": "Implement a data retention policy that limits storage duration to what is necessary. Add automated data deletion mechanisms.",
            "access_control": "Implement proper authentication and authorization checks before allowing access to personal data."
        }
        
        return advice_map.get(issue_type, "Review the code for GDPR compliance and implement appropriate safeguards.")

    def _apply_code_fix(self, content: str, line_number: int, fix_code: str, language: str) -> str:
        """
        Apply a code fix at the specified line number.
        
        Args:
            content: Original file content
            line_number: Line number where the issue was detected
            fix_code: Suggested fix code
            language: Programming language
            
        Returns:
            Updated file content
        """
        lines = content.split('\n')
        if line_number < 1 or line_number > len(lines):
            return content
            
        # Determine indentation of the original line
        original_line = lines[line_number - 1]
        indentation = len(original_line) - len(original_line.lstrip())
        
        # Apply indentation to the fix code
        indented_fix = '\n'.join(
            ' ' * indentation + line if i > 0 else line
            for i, line in enumerate(fix_code.split('\n'))
        )
        
        # Replace the problematic line with the fix
        lines[line_number - 1] = indented_fix
        
        return '\n'.join(lines)

    # Fix handlers for Python

    def _fix_python_consent_issues(self, issue: Dict[str, Any], file_content: str) -> str:
        """Generate a fix for Python consent issues."""
        context = issue.get("context", "")
        if "user data" in context.lower() or "personal data" in context.lower():
            return """# Check for user consent before processing data
if user_has_consented(user_id, 'data_processing'):
    # Original data processing code here
else:
    logger.warning(f"User {user_id} has not provided consent for data processing")
    return {"error": "Consent required", "status": "error"}"""
        return ""

    def _fix_python_data_minimization(self, issue: Dict[str, Any], file_content: str) -> str:
        """Generate a fix for Python data minimization issues."""
        return """# Apply data minimization by only selecting required fields
minimized_data = {
    k: v for k, v in data.items() 
    if k in required_fields
}
return minimized_data"""

    def _fix_python_pii_collection(self, issue: Dict[str, Any], file_content: str) -> str:
        """Generate a fix for Python PII collection issues."""
        return """# Ensure PII processing has legal basis and proper protections
from levox.security import encrypt_pii, log_pii_access

# Document the legal basis for processing
legal_basis = "explicit_consent"  # or "legitimate_interest", "contract", etc.

# Encrypt PII before storage
encrypted_data = encrypt_pii(pii_data)

# Log access for auditability
log_pii_access(user_id, "read", request.context)

# Limit data to only what's necessary
redacted_results = {field: value for field, value in results.items() 
                   if field in allowed_fields}"""

    def _fix_python_data_transfer(self, issue: Dict[str, Any], file_content: str) -> str:
        """Generate a fix for Python data transfer issues."""
        return """# Verify data transfer compliance before sending
from levox.gdpr import verify_transfer_compliance

destination = request.headers.get('Origin', 'unknown')
if not verify_transfer_compliance(destination):
    return {
        "error": "Data transfer to this region requires additional safeguards",
        "status": "error",
        "code": 403
    }
    
# Proceed with data transfer if compliant
# Original code here"""

    def _fix_python_data_retention(self, issue: Dict[str, Any], file_content: str) -> str:
        """Generate a fix for Python data retention issues."""
        return """# Implement data retention controls
from datetime import datetime, timedelta
from levox.data_management import should_retain_data

creation_time = data.get('created_at')
retention_period = timedelta(days=90)  # Customize based on your policy

if not should_retain_data(creation_time, retention_period):
    # Data has exceeded retention period, handle accordingly
    delete_expired_data(data_id)
    return {"status": "deleted", "reason": "retention_policy"}
    
# Continue processing if within retention period
# Original code here"""

    def _fix_python_access_control(self, issue: Dict[str, Any], file_content: str) -> str:
        """Generate a fix for Python access control issues."""
        return """# Implement proper access control
from levox.auth import verify_access_permission

def access_protected_data(user_id, data_id):
    # Verify the user has permission to access this data
    if not verify_access_permission(user_id, data_id, "read"):
        logger.warning(f"Unauthorized access attempt by {user_id} for data {data_id}")
        raise PermissionError("You do not have permission to access this data")
        
    # Proceed with data access if authorized
    data = get_data(data_id)
    return data"""

    # Fix handlers for JavaScript

    def _fix_js_consent_issues(self, issue: Dict[str, Any], file_content: str) -> str:
        """Generate a fix for JavaScript consent issues."""
        return """// Check for user consent before processing data
async function processWithConsent(userId, data) {
  const hasConsent = await consentManager.checkConsent(userId, 'data_processing');
  
  if (hasConsent) {
    // Original data processing code here
    return processData(data);
  } else {
    console.warn(`User ${userId} has not provided consent for data processing`);
    return {
      error: "Consent required",
      status: "error"
    };
  }
}"""

    def _fix_js_data_minimization(self, issue: Dict[str, Any], file_content: str) -> str:
        """Generate a fix for JavaScript data minimization issues."""
        return """// Apply data minimization by only selecting required fields
function minimizeData(data, requiredFields) {
  return Object.keys(data)
    .filter(key => requiredFields.includes(key))
    .reduce((obj, key) => {
      obj[key] = data[key];
      return obj;
    }, {});
}

const minimizedData = minimizeData(userData, requiredFields);"""

    def _fix_js_pii_collection(self, issue: Dict[str, Any], file_content: str) -> str:
        """Generate a fix for JavaScript PII collection issues."""
        return """// Ensure PII processing has legal basis and proper protections
import { encryptPII, logPIIAccess } from '../security/piiProtection';

// Document the legal basis for processing
const legalBasis = 'explicit_consent'; // or 'legitimate_interest', 'contract', etc.

// Encrypt PII before storage
const encryptedData = encryptPII(piiData);

// Log access for auditability
logPIIAccess(userId, 'read', requestContext);

// Limit data to only what's necessary
const redactedResults = Object.keys(results)
  .filter(field => allowedFields.includes(field))
  .reduce((obj, field) => {
    obj[field] = results[field];
    return obj;
  }, {});"""

    def export_metrics(self) -> Dict[str, Any]:
        """Export metrics about remediation activities."""
        return self.metrics

    def remediate_issues(self, issues: List[GDPRIssue], fix: bool = False, document: bool = True) -> Dict[str, Any]:
        """
        Remediate GDPR issues by fixing code and generating documentation.
        
        Args:
            issues: List of GDPRIssue objects to remediate
            fix: Whether to automatically apply fixes
            document: Whether to generate documentation
            
        Returns:
            Dict with remediation results
        """
        results = {
            "fixes": [],
            "documentation": None,
            "summary": {
                "total_issues": len(issues),
                "fixed_issues": 0,
                "failed_fixes": 0
            }
        }
        
        # Apply fixes
        for issue in issues:
            fix_result = self.auto_fixer.fix_issue(issue, dry_run=not fix)
            results["fixes"].append({
                "issue": {
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "issue_type": issue.issue_type,
                    "description": issue.description
                },
                "result": fix_result
            })
            
            if fix_result["success"]:
                results["summary"]["fixed_issues"] += 1
            else:
                results["summary"]["failed_fixes"] += 1
        
        # Generate documentation
        if document and issues:
            doc_path = Path(self.config.base_dir) / "gdpr_documentation"
            doc_path.mkdir(exist_ok=True)
            
            # Generate record of processing activities
            processing_record_path = doc_path / "processing_record.md"
            processing_record = self.doc_generator.generate_processing_record(
                issues, 
                str(processing_record_path)
            )
            
            results["documentation"] = {
                "processing_record_path": str(processing_record_path)
            }
        
        return results 