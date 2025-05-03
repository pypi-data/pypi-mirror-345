"""
Fixer module for providing GDPR compliance remediation using Ollama LLM.
"""
import os
import re
from typing import Dict, List, Optional
from pathlib import Path

# Import locally to allow running without Ollama if just scanning
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from levox.scanner import GDPRIssue

REMEDIATION_PROMPTS = {
    "data_transfer": """
You are a GDPR compliance expert. The following code might transfer personal data outside the EU:

```
{code}
```

Please suggest a GDPR-compliant way to fix this code to ensure:
1. The data transfer includes appropriate safeguards (SCCs)
2. The user is informed about the data transfer
3. The code documents the GDPR compliance measures

Provide only the fixed code without explanations. Wrap your code in ```python tags.
""",
    "third_party_integration": """
You are a GDPR compliance expert. The following code uses a third-party service that processes personal data:

```
{code}
```

Please suggest a GDPR-compliant way to fix this code to ensure:
1. The code checks if a Data Processing Agreement (DPA) is in place
2. The data shared with the third party is minimized
3. The purpose of processing is clearly documented

Provide only the fixed code without explanations. Wrap your code in ```python tags.
""",
    "pii_collection": """
You are a GDPR compliance expert. The following code collects personal data:

```
{code}
```

Please suggest a GDPR-compliant way to fix this code to ensure:
1. The code only collects necessary data (data minimization)
2. The purpose of collection is documented
3. The data is properly protected and access-controlled

Provide only the fixed Python code without explanations. Wrap your code in ```python tags.
""",
    "consent_issues": """
You are a GDPR compliance expert. The following code may process personal data without proper consent:

```
{code}
```

Please suggest a GDPR-compliant way to fix this code to ensure:
1. Explicit consent is obtained before processing
2. The consent is specific and informed
3. The user can withdraw consent easily

Provide only the fixed Python code without explanations. Wrap your code in ```python tags.
""",
    "missing_data_deletion": """
You are a GDPR compliance expert. The following code processes personal data but lacks functions for data deletion (right to erasure):

```
{code}
```

Please suggest how to implement a data deletion function for this code that:
1. Allows complete erasure of user data
2. Documents the deletion process
3. Provides confirmation of deletion

Provide only the implementation code without explanations. Wrap your code in ```python tags.
"""
}

class Fixer:
    def __init__(self, model_name: str = "deepseek-r1:1.5b"):
        """Initialize the fixer with the specified LLM model."""
        self.model_name = model_name
        if not OLLAMA_AVAILABLE:
            print("Warning: Ollama is not available. Install with 'pip install ollama'")
    
    def check_model_availability(self) -> bool:
        """Check if the specified model is available in Ollama."""
        if not OLLAMA_AVAILABLE:
            return False
            
        try:
            models = ollama.list()
            
            # Handle ListResponse object (newer Ollama versions)
            if hasattr(models, 'models'):
                for model in models.models:
                    if hasattr(model, 'model') and model.model == self.model_name:
                        return True
                return False
                
            # Handle dict response (older Ollama versions)
            elif isinstance(models, dict):
                if 'models' in models:
                    # Format: {'models': [{'name': 'model_name'}, ...]}
                    for model in models.get('models', []):
                        if isinstance(model, dict) and (
                            model.get('name') == self.model_name or 
                            model.get('model') == self.model_name
                        ):
                            return True
                else:
                    # Alternative format: {'name': 'model', ...}
                    return self.model_name in models.keys()
            
            return False
        except Exception as e:
            print(f"Error checking model availability: {e}")
            return False
    
    def _get_code_context(self, file_path: str, line_number: int, context_lines: int = 10) -> str:
        """Get the code context around the issue."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                
            start_line = max(0, line_number - context_lines - 1)
            end_line = min(len(lines), line_number + context_lines)
            
            return ''.join(lines[start_line:end_line])
        except Exception as e:
            print(f"Error getting code context: {e}")
            return ""
    
    def generate_fix(self, issue: GDPRIssue) -> Optional[str]:
        """Generate a fix for the given issue using the LLM."""
        if not OLLAMA_AVAILABLE:
            return "Ollama is not available. Install with 'pip install ollama'"
            
        # Get code context
        context = self._get_code_context(issue.file_path, issue.line_number)
        if not context:
            return None
            
        # Get the appropriate prompt template
        prompt_template = REMEDIATION_PROMPTS.get(issue.issue_type)
        if not prompt_template:
            return None
            
        # Format the prompt with the code context
        prompt = prompt_template.format(code=context)
        
        try:
            # Generate the fix using Ollama
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt
            )
            
            # Handle different response formats
            if hasattr(response, 'response'):
                # New Ollama API (response is an object)
                fix = response.response.strip()
            elif isinstance(response, dict) and 'response' in response:
                # Old Ollama API (response is a dict)
                fix = response['response'].strip()
            else:
                print(f"Unexpected response format: {type(response)}")
                return None
            
            # Remove <think>...</think> sections (deepseek model specific)
            fix = re.sub(r'<think>[\s\S]*?</think>', '', fix)
                
            # Extract Python code blocks if they exist
            python_code_blocks = re.findall(r'```python\n([\s\S]*?)\n```', fix)
            if python_code_blocks:
                # Use the first Python code block
                fix = python_code_blocks[0].strip()
            else:
                # Remove any generic markdown code blocks
                fix = re.sub(r'```\w*\n', '', fix)
                fix = re.sub(r'\n```$', '', fix)
            
            # Clean up any remaining explanation text and remove backticks
            fix = re.sub(r'```', '', fix)
            
            return fix.strip()
                
        except Exception as e:
            print(f"Error generating fix: {e}")
            return f"Failed to generate fix: {str(e)}"
    
    def apply_fix(self, issue: GDPRIssue, fix: str) -> bool:
        """Apply the generated fix to the file."""
        if not fix:
            return False
            
        try:
            with open(issue.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Simple replacement - in a real implementation, we would need a more 
            # sophisticated approach to correctly apply the fix
            if issue.issue_type == "missing_data_deletion":
                # For missing deletion functions, we append the fix to the end of the file
                with open(issue.file_path, 'a', encoding='utf-8') as f:
                    f.write("\n\n# Added for GDPR compliance - Right to Erasure (Article 17)\n")
                    f.write(fix)
            else:
                # For better fix application, detect Python blocks and proper indentation
                if "```python" in fix or "<think>" in fix:
                    # This is raw LLM output with markdown/thinking, extract just the code
                    # Get rid of thinking tags
                    fix = re.sub(r'<think>[\s\S]*?</think>', '', fix)
                    
                    # Find Python code blocks
                    code_blocks = re.findall(r'```python\n([\s\S]*?)\n```', fix)
                    if code_blocks:
                        fix = code_blocks[0].strip()
                    else:
                        # Just clean up markdown
                        fix = re.sub(r'```\w*\n', '', fix)
                        fix = re.sub(r'\n```', '', fix)
                        fix = re.sub(r'```', '', fix)
                
                # For other issues, we replace the problematic line
                if 0 <= issue.line_number - 1 < len(lines):
                    lines[issue.line_number - 1] = fix + "\n"
                    
                    with open(issue.file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
            
            return True
        except Exception as e:
            print(f"Error applying fix: {e}")
            return False
    
    def fix_issues(self, issues: List[GDPRIssue]) -> Dict[str, int]:
        """Fix all the given issues and return statistics."""
        results = {
            "total": len(issues),
            "fixed": 0,
            "failed": 0,
            "skipped": 0
        }
        
        if not OLLAMA_AVAILABLE:
            print("Ollama is not available. Skipping fixes.")
            results["skipped"] = results["total"]
            return results
        
        # Initialize progress tracking
        print(f"Preparing to fix {len(issues)} GDPR compliance issues...")
            
        for i, issue in enumerate(issues):
            print(f"[{i+1}/{len(issues)}] Processing issue: {issue}")
            print(f"  ↪ Analyzing codebase context...")
            
            # Generate fix
            print(f"  ↪ Generating GDPR-compliant solution...")
            fix = self.generate_fix(issue)
            if not fix:
                print(f"  ✗ Failed to generate fix")
                results["failed"] += 1
                continue
            
            # Apply fix    
            print(f"  ↪ Applying code modifications...")
            success = self.apply_fix(issue, fix)
            if success:
                print(f"  ✓ Successfully implemented fix")
                results["fixed"] += 1
                issue.remediation = fix
            else:
                print(f"  ✗ Failed to apply fix")
                results["failed"] += 1
        
        return results 