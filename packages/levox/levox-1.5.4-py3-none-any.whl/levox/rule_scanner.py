"""
Rule-based GDPR compliance scanner using Semgrep patterns.

This module provides a fast, pattern-based scanning approach for detecting
potential GDPR compliance issues in code.
"""
import os
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

from levox.scanner import Scanner, GDPRIssue
from levox.gdpr_articles import get_articles_for_issue_type

# Default GDPR rules in Semgrep pattern format
GDPR_RULES = {
    "pii_collection": [
        {
            "id": "levox-pii-collection-email",
            "pattern": "$X.email",
            "message": "Collection of email addresses requires proper consent",
            "severity": "medium"
        },
        {
            "id": "levox-pii-collection-personal-data",
            "patterns": [
                "$X.name", "$X.full_name", "$X.first_name", "$X.last_name",
                "$X.address", "$X.postal", "$X.zip", "$X.phone", "$X.birthdate",
                "$X.ssn", "$X.social_security", "$X.passport", "$X.driver_license"
            ],
            "message": "Collection of personal data requires proper legal basis",
            "severity": "high"
        },
        {
            "id": "levox-pii-special-categories",
            "patterns": [
                "$X.gender", "$X.race", "$X.ethnicity", "$X.religion",
                "$X.politics", "$X.health", "$X.medical", "$X.biometric",
                "$X.genetic", "$X.sexual_orientation"
            ],
            "message": "Special categories of data require explicit consent",
            "severity": "high"
        }
    ],
    "data_transfer": [
        {
            "id": "levox-data-transfer-api",
            "patterns": [
                "axios.post($URL, $DATA)",
                "fetch($URL, $OPTIONS)",
                "$.ajax($OPTIONS)",
                "request.post($URL, $DATA)"
            ],
            "message": "Data transfer to external API may require GDPR safeguards",
            "severity": "medium"
        },
        {
            "id": "levox-data-transfer-third-party",
            "patterns": [
                "firebase.$X($DATA)", 
                "analytics.$X($DATA)",
                "amplitude.$X($DATA)",
                "mixpanel.$X($DATA)",
                "segment.$X($DATA)",
                "gtag($EVENT, $DATA)",
                "fbq($EVENT, $DATA)"
            ],
            "message": "Transfer to third-party service requires data processing agreement",
            "severity": "high"
        }
    ],
    "consent_issues": [
        {
            "id": "levox-consent-cookies",
            "patterns": [
                "document.cookie = $X",
                "setCookie($NAME, $VALUE)",
                "localStorage.setItem($KEY, $VALUE)",
                "sessionStorage.setItem($KEY, $VALUE)"
            ],
            "message": "Setting cookies or storage without consent validation",
            "severity": "high"
        }
    ],
    "security_measures": [
        {
            "id": "levox-security-plaintext",
            "patterns": [
                "password = $X",
                "$VAR = \"password\"",
                "$VAR = \"api_key\"",
                "$VAR = \"secret\""
            ],
            "message": "Potential plaintext storage of sensitive data",
            "severity": "high"
        },
        {
            "id": "levox-security-http",
            "pattern": "http://",
            "message": "Use of insecure HTTP protocol for data transfer",
            "severity": "medium"
        }
    ],
    "data_minimization": [
        {
            "id": "levox-data-minimization-select-all",
            "patterns": [
                "SELECT * FROM $TABLE",
                "find({})",
                "findAll()",
                "db.$TABLE.find({})"
            ],
            "message": "Fetching all fields violates data minimization principle",
            "severity": "medium"
        }
    ]
}

class RuleScanner:
    """
    Rule-based scanner for GDPR compliance issues using Semgrep patterns.
    """
    
    def __init__(self, target_dir: str, exclude_dirs: List[str] = None,
                 custom_rules: Dict[str, List[Dict[str, Any]]] = None):
        """
        Initialize the rule-based scanner.
        
        Args:
            target_dir: The directory to scan
            exclude_dirs: Directories to exclude from scanning
            custom_rules: Custom Semgrep rules to use in addition to default rules
        """
        self.target_dir = Path(target_dir)
        self.exclude_dirs = exclude_dirs or ['node_modules', 'venv', '.git', '__pycache__', 'dist', 'build']
        self.custom_rules = custom_rules or {}
        
        # Merge custom rules with default rules
        self.rules = GDPR_RULES.copy()
        for rule_type, rules in self.custom_rules.items():
            if rule_type in self.rules:
                self.rules[rule_type].extend(rules)
            else:
                self.rules[rule_type] = rules
                
        # Initialize fallback scanner
        self.fallback_scanner = Scanner(target_dir, exclude_dirs)
        
    def scan(self) -> List[GDPRIssue]:
        """
        Scan the target directory for GDPR compliance issues.
        
        Returns:
            List of GDPRIssue objects
        """
        # Try to use Semgrep for scanning
        try:
            issues = self._scan_with_semgrep()
            
            # If Semgrep doesn't find anything, fall back to pattern-based scanning
            if not issues:
                print("Semgrep didn't find issues, falling back to pattern-based scanner.")
                issues = self.fallback_scanner.scan_directory()
                
            return issues
        except Exception as e:
            print(f"Error using Semgrep: {e}. Falling back to pattern-based scanner.")
            return self.fallback_scanner.scan_directory()
    
    def _scan_with_semgrep(self) -> List[GDPRIssue]:
        """
        Scan using Semgrep with GDPR rules.
        
        Returns:
            List of GDPRIssue objects
        """
        issues = []
        
        # Create a temporary file with the rules
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            # Convert rules to Semgrep YAML format
            semgrep_rules = {
                "rules": []
            }
            
            # Add each rule type
            for rule_type, rules in self.rules.items():
                for rule in rules:
                    semgrep_rule = {
                        "id": rule["id"],
                        "message": rule["message"],
                        "severity": rule["severity"],
                        "metadata": {
                            "issue_type": rule_type
                        },
                        "languages": ["python", "javascript", "typescript", "java", "go"]
                    }
                    
                    # Add pattern or patterns
                    if "pattern" in rule:
                        semgrep_rule["pattern"] = rule["pattern"]
                    elif "patterns" in rule:
                        semgrep_rule["patterns"] = rule["patterns"]
                        
                    semgrep_rules["rules"].append(semgrep_rule)
            
            # Write the rules to the temporary file
            json.dump(semgrep_rules, f)
            rules_file = f.name
        
        try:
            # Run Semgrep with the rules
            cmd = [
                "semgrep",
                "--config", rules_file,
                "--json",
                "--exclude", ",".join(self.exclude_dirs),
                str(self.target_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse the results
            if result.returncode == 0:
                findings = json.loads(result.stdout)
                
                for finding in findings.get("results", []):
                    # Extract information from the finding
                    rule_id = finding.get("check_id", "")
                    path = finding.get("path", "")
                    line = finding.get("start", {}).get("line", 1)
                    message = finding.get("extra", {}).get("message", "")
                    severity = finding.get("extra", {}).get("severity", "medium")
                    
                    # Get the issue type from the rule metadata
                    issue_type = finding.get("extra", {}).get("metadata", {}).get("issue_type", "unspecified")
                    
                    # Get the code snippet
                    lines = finding.get("extra", {}).get("lines", "")
                    
                    # Create a GDPRIssue object
                    issue = GDPRIssue(
                        file_path=path,
                        line_number=line,
                        issue_type=issue_type,
                        description=message,
                        remediation=self._generate_remediation(issue_type, lines),
                        severity=severity,
                        line_content=lines,
                        articles=get_articles_for_issue_type(issue_type)
                    )
                    
                    issues.append(issue)
            
            # Clean up the temporary file
            os.unlink(rules_file)
            
            return issues
            
        except Exception as e:
            print(f"Error running Semgrep: {e}")
            # Clean up the temporary file
            try:
                os.unlink(rules_file)
            except:
                pass
            
            # Re-raise to trigger the fallback
            raise
    
    def _generate_remediation(self, issue_type: str, code_snippet: str) -> str:
        """
        Generate a remediation suggestion for a GDPR issue.
        
        Args:
            issue_type: The type of GDPR issue
            code_snippet: The code snippet that triggered the issue
            
        Returns:
            A remediation suggestion
        """
        if issue_type == "pii_collection":
            return """## GDPR-compliant data collection:

```python
# Ensure you have a legal basis before collecting PII
if user_has_consented('data_collection') or has_legitimate_interest():
    # Document the purpose of collection
    user_data = {
        'name': name,
        'email': email,
        # Only collect what you actually need
    }
    
    # Store with appropriate safeguards
    store_with_encryption(user_data)
else:
    # Handle case where no legal basis exists
    log_consent_rejection()
    redirect_to_consent_page()
```"""

        elif issue_type == "data_transfer":
            # Check for specific destinations to provide targeted advice
            us_transfer = any(term in code_snippet.lower() for term in ["us", "united states", "america", "aws", "amazon"])
            uk_transfer = any(term in code_snippet.lower() for term in ["uk", "united kingdom", "britain"])
            china_transfer = any(term in code_snippet.lower() for term in ["china", "chinese", "cn"])
            
            if us_transfer:
                return """## GDPR-compliant US data transfer:

```python
# US transfers require specific safeguards after the invalidation of Privacy Shield
def transfer_data_to_us(data, purpose):
    # 1. Implement Standard Contractual Clauses (SCCs)
    if not verify_sccs_in_place('us_recipient'):
        raise GDPRException("Cannot transfer data without SCCs in place")
        
    # 2. Perform Transfer Impact Assessment (TIA)
    tia_result = perform_transfer_impact_assessment('us_recipient')
    if not tia_result.is_acceptable:
        log.error(f"TIA identified unacceptable risks: {tia_result.risks}")
        raise GDPRException("Transfer Impact Assessment failed")
    
    # 3. Implement supplementary measures
    encrypted_data = apply_end_to_end_encryption(data)
    
    # 4. Document the transfer
    document_transfer(
        destination="US",
        legal_basis="SCCs with supplementary measures",
        tia_reference=tia_result.reference_id
    )
    
    # 5. Proceed with transfer
    return api_client.send_to_us(encrypted_data)
```"""
            elif china_transfer:
                return """## GDPR-compliant China data transfer:

```python
# China transfers require robust safeguards as it lacks adequacy decision
def transfer_data_to_china(data, purpose):
    # 1. Implement Standard Contractual Clauses (SCCs)
    if not verify_sccs_in_place('china_recipient'):
        raise GDPRException("Cannot transfer data without SCCs in place")
        
    # 2. Perform Transfer Impact Assessment (TIA) with focus on government access
    tia_result = perform_transfer_impact_assessment('china_recipient', 
                                                   high_risk_country=True)
    if not tia_result.is_acceptable:
        log.error(f"TIA identified unacceptable risks: {tia_result.risks}")
        raise GDPRException("Transfer Impact Assessment failed")
    
    # 3. Implement strong supplementary measures
    pseudonymized_data = pseudonymize_data(data)
    encrypted_data = apply_strong_encryption(pseudonymized_data)
    
    # 4. Obtain explicit consent for this specific transfer
    if not user_has_explicit_consent_for_transfer(data_subject_id, 'china'):
        raise GDPRException("Explicit consent required for China transfer")
    
    # 5. Document the transfer
    document_transfer(
        destination="China",
        legal_basis="SCCs with supplementary measures and explicit consent",
        tia_reference=tia_result.reference_id
    )
    
    # 6. Proceed with transfer
    return api_client.send_to_china(encrypted_data)
```"""
            elif uk_transfer:
                return """## GDPR-compliant UK data transfer:

```python
# UK has a positive adequacy decision from the EU
def transfer_data_to_uk(data, purpose):
    # 1. Document transfer under adequacy decision
    document_transfer(
        destination="UK",
        legal_basis="Adequacy decision",
        adequacy_decision_reference="C/2021/4800"
    )
    
    # 2. Still implement appropriate security measures
    secured_data = apply_transport_security(data)
    
    # 3. Proceed with transfer
    return api_client.send_to_uk(secured_data)
```"""
            else:
                # Generic data transfer remediation
                return """## GDPR-compliant data transfer:

```python
# Check if transfer is to adequate country or has appropriate safeguards
def transfer_data_international(data, destination):
    # 1. Check if destination has an adequacy decision
    if is_adequate_destination(destination):
        legal_basis = "Adequacy decision"
    else:
        # 2. Implement Standard Contractual Clauses (SCCs)
        if not verify_sccs_in_place(destination):
            raise GDPRException("Cannot transfer data without appropriate safeguards")
            
        # 3. Perform Transfer Impact Assessment (TIA) for non-adequate countries
        tia_result = perform_transfer_impact_assessment(destination)
        if not tia_result.is_acceptable:
            log.error(f"TIA identified unacceptable risks: {tia_result.risks}")
            raise GDPRException("Transfer Impact Assessment failed")
            
        legal_basis = "SCCs with supplementary measures"
    
    # 4. Implement security measures regardless of destination
    secured_data = apply_transport_security(data)
    
    # 5. Document the transfer
    document_transfer(
        destination=destination,
        legal_basis=legal_basis
    )
    
    # 6. Proceed with transfer
    return api_client.send_to_destination(destination, secured_data)
```"""

        elif issue_type == "consent_issues":
            return """## GDPR-compliant consent handling:

```python
# Check for specific, informed consent before setting cookies
if user_has_consented('cookies', purpose='analytics'):
    # Set cookies with appropriate expiration
    set_cookie('analytics_id', generate_id(), 
               expiry=30, # days
               secure=True,
               http_only=True)
    
    # Provide means to withdraw consent
    show_cookie_settings_link()
else:
    # Don't set cookies, use alternative approach or show consent banner
    show_consent_banner(required_for=['cookies'])
```"""

        elif issue_type == "security_measures":
            return """## GDPR-compliant security implementation:

```python
# Never store sensitive data in plaintext
from cryptography.fernet import Fernet

# Generate or retrieve key from secure storage
key = get_encryption_key_from_secure_storage()
cipher = Fernet(key)

# Encrypt sensitive data before storage
encrypted_password = cipher.encrypt(password.encode())

# Store the encrypted value
user.encrypted_password = encrypted_password

# Ensure all API communication uses HTTPS
api_url = api_url.replace('http://', 'https://')
```"""

        elif issue_type == "data_minimization":
            return """## GDPR-compliant data minimization:

```python
# Instead of SELECT * or fetching all fields
# Specify only the fields you actually need
user_data = db.users.find(
    {'user_id': user_id},
    projection={
        'name': 1,
        'email': 1,
        'preferences': 1,
        # Exclude unnecessary fields
        'password': 0,
        'detailed_history': 0,
        'analytics_data': 0
    }
)

# Document why these fields are necessary
FIELD_PURPOSES = {
    'name': 'Necessary for account identification',
    'email': 'Required for account communication',
    'preferences': 'Necessary to provide requested service'
}
```"""
        
        else:
            return f"""## GDPR compliance recommendation:

Review this code for compliance with GDPR principles:
- Lawfulness, fairness and transparency
- Purpose limitation
- Data minimization
- Accuracy
- Storage limitation
- Integrity and confidentiality
- Accountability

Consider documenting the legal basis for data processing and implementing appropriate safeguards.""" 