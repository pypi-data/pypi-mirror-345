"""
AI Context Engine for GDPR compliance scanning.

This module provides advanced AI-powered analysis of code to detect
potential GDPR compliance issues by understanding context and developer intent.
"""
import os
import re
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import ast
import time

from levox.scanner import GDPRIssue
from levox.gdpr_articles import get_articles_for_issue_type, get_article_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_context_engine")

# Try to import various AI providers
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_community.llms import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    try:
        # Try legacy import path as fallback
        from langchain.llms import Ollama
        OLLAMA_AVAILABLE = True
    except ImportError:
        OLLAMA_AVAILABLE = False

class AIContextEngine:
    """
    AI-powered engine for contextual analysis of code for GDPR compliance.
    """
    
    def __init__(
        self,
        provider: str = "ollama",
        model: str = "llama3",
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize the AI Context Engine.
        
        Args:
            provider: AI provider to use ('ollama', 'openai')
            model: Model name to use
            api_key: API key for the provider (if needed)
            temperature: Temperature setting for generation
            max_tokens: Maximum tokens in responses
            cache_dir: Directory to cache AI responses
        """
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key or os.environ.get(f"{provider.upper()}_API_KEY", "")
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize cache
        self.cache_dir = cache_dir
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            self.cache_file = os.path.join(self.cache_dir, "ai_responses.json")
            self.response_cache = self._load_cache()
        else:
            self.response_cache = {}
            
        # Initialize AI client
        self.client = self._initialize_client()
        
        # Compile patterns for identifying GDPR-sensitive code
        self._compile_patterns()
        
    def _initialize_client(self) -> Any:
        """Initialize the AI client based on provider."""
        if self.provider == "openai" and OPENAI_AVAILABLE:
            logger.info(f"Initializing OpenAI client with model {self.model}")
            if self.api_key:
                openai.api_key = self.api_key
            return openai.Client()
        elif self.provider == "ollama" and OLLAMA_AVAILABLE:
            logger.info(f"Initializing Ollama client with model {self.model}")
            return Ollama(model=self.model)
        else:
            if self.provider == "openai" and not OPENAI_AVAILABLE:
                logger.warning("OpenAI package not installed. Install with 'pip install openai'")
            elif self.provider == "ollama" and not OLLAMA_AVAILABLE:
                logger.warning("Langchain and Ollama not installed. Install with 'pip install langchain ollama'")
            else:
                logger.warning(f"Unsupported provider: {self.provider}")
                
            logger.warning("Falling back to template-based analysis")
            return None
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for identifying GDPR-sensitive code."""
        # PII field patterns
        self.pii_patterns = {
            # Personal identifiers
            "personal_id": re.compile(r'(?i)(ssn|social_security|passport|id_number|national_id|driver_licen[sc]e)',),
            # Contact information
            "contact": re.compile(r'(?i)(email|phone|mobile|address|zip|postal|city|state|country)'),
            # Financial information
            "financial": re.compile(r'(?i)(credit_card|card_number|cvv|expir(y|ation)|account_number|iban|bank)'),
            # Health information
            "health": re.compile(r'(?i)(health|medical|diagnosis|treatment|prescription|patient)'),
            # Biometric data
            "biometric": re.compile(r'(?i)(finger(print)?|face|facial|retina|iris|voice|gait|dna|biometric)'),
            # Location data
            "location": re.compile(r'(?i)(location|gps|coordinates|latitude|longitude|geo)'),
            # Demographic data
            "demographic": re.compile(r'(?i)(gender|age|birth|ethnicity|nationality|race|religion|political|sexuality)'),
            # General PII concepts
            "general_pii": re.compile(r'(?i)(personal|pii|gdpr|data_subject|consent|identifier|privacy)')
        }
        
        # Sensitive operations patterns
        self.operation_patterns = {
            # Data collection
            "collection": re.compile(r'(?i)(collect|gather|obtain|receive|acquire|input|upload|import|store)'),
            # Data processing
            "processing": re.compile(r'(?i)(process|analyze|compute|calculate|handle|manage|transform)'),
            # Data access
            "access": re.compile(r'(?i)(access|retrieve|get|fetch|read|query|search|find|lookup)'),
            # Data transfer
            "transfer": re.compile(r'(?i)(transfer|send|transmit|export|share|disclose|provide)'),
            # Data storage
            "storage": re.compile(r'(?i)(store|save|persist|cache|archive|backup|write)'),
            # Data deletion
            "deletion": re.compile(r'(?i)(delete|remove|erase|purge|destroy|clear|clean|forget)')
        }
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file if it exists."""
        if self.cache_dir and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading cache: {e}")
        return {}
    
    def _save_cache(self) -> None:
        """Save cache to file."""
        if self.cache_dir:
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.response_cache, f, indent=2)
            except Exception as e:
                logger.warning(f"Error saving cache: {e}")
    
    def analyze_file(
        self, 
        file_path: str, 
        existing_issues: Optional[List[GDPRIssue]] = None
    ) -> List[GDPRIssue]:
        """
        Analyze a file for potential GDPR compliance issues using AI.
        
        Args:
            file_path: Path to the file to analyze
            existing_issues: List of issues already detected by rule-based scanning
            
        Returns:
            List of GDPRIssue objects detected by AI
        """
        logger.info(f"Analyzing file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []
            
        # Extract file information
        file_info = self._extract_file_info(file_path, content)
        
        # Initial pattern-based screening
        if not self._should_analyze_further(file_info, content):
            logger.info(f"File {file_path} does not contain PII or sensitive operations, skipping AI analysis")
            return []
            
        # Prepare context including existing issues
        context = self._prepare_context(file_info, content, existing_issues)
        
        # Use AI to analyze the file
        ai_analysis = self._get_ai_analysis(context)
        
        # Parse AI response into issues
        issues = self._parse_ai_response(ai_analysis, file_path)
        
        logger.info(f"AI analysis found {len(issues)} issues in {file_path}")
        return issues
        
    def _extract_file_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Extract basic information about the file.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            
        Returns:
            Dictionary with file information
        """
        file_info = {
            "path": file_path,
            "extension": Path(file_path).suffix.lower(),
            "size": len(content),
            "line_count": content.count('\n') + 1,
            "functions": [],
            "classes": [],
            "imports": [],
            "sensitive_patterns": {
                "pii": {},
                "operations": {}
            }
        }
        
        # Extract code structure for Python files
        if file_info["extension"] == ".py":
            try:
                tree = ast.parse(content)
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            file_info["imports"].append(name.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for name in node.names:
                            file_info["imports"].append(f"{module}.{name.name}")
                
                # Extract functions and classes
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef):
                        file_info["functions"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "end_line": node.end_lineno,
                            "args": [arg.arg for arg in node.args.args]
                        })
                    elif isinstance(node, ast.ClassDef):
                        methods = []
                        for child in node.body:
                            if isinstance(child, ast.FunctionDef):
                                methods.append({
                                    "name": child.name,
                                    "line": child.lineno,
                                    "end_line": child.end_lineno,
                                    "args": [arg.arg for arg in child.args.args]
                                })
                        
                        file_info["classes"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "end_line": node.end_lineno,
                            "methods": methods
                        })
            except SyntaxError:
                logger.warning(f"Could not parse Python file: {file_path}")
        
        # Basic pattern-based scanning for sensitive content
        for category, pattern in self.pii_patterns.items():
            matches = pattern.findall(content)
            if matches:
                file_info["sensitive_patterns"]["pii"][category] = matches
                
        for operation, pattern in self.operation_patterns.items():
            matches = pattern.findall(content)
            if matches:
                file_info["sensitive_patterns"]["operations"][operation] = matches
                
        return file_info
    
    def _should_analyze_further(self, file_info: Dict[str, Any], content: str) -> bool:
        """
        Determine if the file should be analyzed further by AI.
        
        Args:
            file_info: Information about the file
            content: Content of the file
            
        Returns:
            True if the file should be analyzed further, False otherwise
        """
        # Skip if file is empty or very small
        if file_info["size"] < 50:
            return False
            
        # Skip if file doesn't have any PII or sensitive operations
        if not file_info["sensitive_patterns"]["pii"] and not file_info["sensitive_patterns"]["operations"]:
            return False
            
        # Skip if file is a test file and doesn't have many PII patterns
        if ("test" in file_info["path"] or file_info["path"].startswith("tests/")) and len(file_info["sensitive_patterns"]["pii"]) < 2:
            return False
            
        return True
        
    def _prepare_context(
        self, 
        file_info: Dict[str, Any], 
        content: str, 
        existing_issues: Optional[List[GDPRIssue]] = None
    ) -> Dict[str, Any]:
        """
        Prepare context for AI analysis.
        
        Args:
            file_info: Information about the file
            content: Content of the file
            existing_issues: Issues detected by rule-based scanning
            
        Returns:
            Dictionary with context for AI analysis
        """
        # If file is too large, extract relevant sections
        file_content = content
        if file_info["size"] > 10000:
            file_content = self._extract_relevant_sections(content, file_info)
            
        context = {
            "file_path": file_info["path"],
            "file_content": file_content,
            "file_info": file_info,
            "existing_issues": []
        }
        
        # Add existing issues
        if existing_issues:
            for issue in existing_issues:
                context["existing_issues"].append({
                    "issue_type": issue.issue_type,
                    "line_number": issue.line_number,
                    "description": issue.description,
                    "articles": issue.articles
                })
                
        return context
        
    def _extract_relevant_sections(self, content: str, file_info: Dict[str, Any]) -> str:
        """
        Extract relevant sections of large files.
        
        Args:
            content: Content of the file
            file_info: Information about the file
            
        Returns:
            String with relevant sections of the file
        """
        lines = content.split('\n')
        
        # Collect line ranges for relevant functions, classes, and their methods
        line_ranges = []
        
        # Add functions that have sensitive patterns
        for func in file_info["functions"]:
            func_content = '\n'.join(lines[func["line"]-1:func["end_line"]])
            if any(pattern.search(func_content) for pattern in self.pii_patterns.values()) or \
               any(pattern.search(func_content) for pattern in self.operation_patterns.values()):
                line_ranges.append((func["line"], func["end_line"]))
                
        # Add methods from classes that have sensitive patterns
        for cls in file_info["classes"]:
            cls_content = '\n'.join(lines[cls["line"]-1:cls["end_line"]])
            if any(pattern.search(cls_content) for pattern in self.pii_patterns.values()) or \
               any(pattern.search(cls_content) for pattern in self.operation_patterns.values()):
                for method in cls["methods"]:
                    method_content = '\n'.join(lines[method["line"]-1:method["end_line"]])
                    if any(pattern.search(method_content) for pattern in self.pii_patterns.values()) or \
                       any(pattern.search(method_content) for pattern in self.operation_patterns.values()):
                        line_ranges.append((method["line"], method["end_line"]))
                        
        # If no line ranges were identified, use the whole file
        if not line_ranges:
            return content
            
        # Merge overlapping or nearby ranges
        line_ranges.sort()
        merged_ranges = []
        current_range = line_ranges[0]
        
        for next_range in line_ranges[1:]:
            # If ranges overlap or are within 10 lines, merge them
            if next_range[0] <= current_range[1] + 10:
                current_range = (current_range[0], max(current_range[1], next_range[1]))
            else:
                merged_ranges.append(current_range)
                current_range = next_range
                
        merged_ranges.append(current_range)
        
        # Add file header (first 20 lines) to provide context
        merged_ranges.insert(0, (1, min(20, len(lines))))
        
        # Extract content from merged ranges
        extracted_lines = []
        for start, end in merged_ranges:
            # Add separator between ranges
            if extracted_lines:
                extracted_lines.append("\n# ...\n")
                
            # Add line range
            for i in range(max(0, start-1), min(len(lines), end)):
                extracted_lines.append(lines[i])
                
        return '\n'.join(extracted_lines)
    
    def _get_ai_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI analysis for a file.
        
        Args:
            context: Context for AI analysis
            
        Returns:
            Dictionary with AI analysis results
        """
        # Generate cache key
        cache_key = f"{context['file_path']}:{hash(context['file_content'])}"
        
        # Check cache
        if cache_key in self.response_cache:
            logger.info(f"Using cached AI analysis for {context['file_path']}")
            return self.response_cache[cache_key]
            
        # Prepare prompt
        prompt = self._create_prompt(context)
        
        try:
            # Use AI client to get analysis
            start_time = time.time()
            
            if self.client is None:
                # Use template-based analysis if no AI client
                analysis = self._template_based_analysis(context)
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                analysis = json.loads(response.choices[0].message.content)
            elif self.provider == "ollama":
                response = self.client(
                    prompt=f"{SYSTEM_PROMPT}\n\n{prompt}\n\nRespond with JSON only."
                )
                # Parse JSON from response
                match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
                if match:
                    analysis = json.loads(match.group(1))
                else:
                    try:
                        analysis = json.loads(response)
                    except json.JSONDecodeError:
                        analysis = {"error": "Could not parse JSON from response"}
            
            end_time = time.time()
            logger.info(f"AI analysis took {end_time - start_time:.2f} seconds")
            
            # Add to cache
            self.response_cache[cache_key] = analysis
            self._save_cache()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting AI analysis: {e}")
            return {"error": str(e), "issues": []}
    
    def _create_prompt(self, context: Dict[str, Any]) -> str:
        """
        Create prompt for AI analysis.
        
        Args:
            context: Context for AI analysis
            
        Returns:
            Prompt string
        """
        prompt = f"""
Please analyze the following code for GDPR compliance issues.

File: {context['file_path']}

{context['file_content']}

Existing issues detected by rule-based scanning:
{json.dumps(context['existing_issues'], indent=2) if context['existing_issues'] else "None"}

Focus on the following aspects:
1. Personal data processing (collection, storage, transmission)
2. User consent management
3. Data subject rights implementation
4. Data transfer mechanisms
5. Data retention policies
6. Security measures for data protection
7. Privacy by design principles

Provide your analysis in a structured JSON format with the following fields:
- "issues": a list of detected issues, each with:
  - "issue_type": the type of GDPR issue (e.g., "pii_collection", "consent_issues", "data_transfer")
  - "line_number": the line number where the issue occurs
  - "description": detailed description of the issue
  - "remediation": specific suggestion to fix the issue
  - "confidence": confidence score between 0.0 and 1.0
  - "articles": list of relevant GDPR article numbers (e.g., "5", "6", "13")
- "summary": overall assessment of the file's GDPR compliance

Do not include any explanations or text outside the JSON structure.
"""
        return prompt
    
    def _template_based_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform template-based analysis when no AI client is available.
        
        Args:
            context: Context for analysis
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Using template-based analysis")
        
        issues = []
        file_content = context["file_content"]
        file_path = context["file_path"]
        
        # Check for PII collection without consent
        pii_fields = []
        for category, pattern in self.pii_patterns.items():
            for match in pattern.finditer(file_content):
                pii_fields.append((match.group(), match.start()))
                
        for field, pos in pii_fields:
            # Find line number
            line_number = file_content[:pos].count('\n') + 1
            
            # Check if consent is mentioned nearby
            start = max(0, pos - 200)
            end = min(len(file_content), pos + 200)
            snippet = file_content[start:end]
            
            if not re.search(r'(?i)(consent|permission|authorize|gdpr|opt[_-]in)', snippet):
                issues.append({
                    "issue_type": "pii_collection",
                    "line_number": line_number,
                    "description": f"Collection of PII ({field}) without explicit consent checks",
                    "remediation": "Add explicit consent verification before processing this personal data",
                    "confidence": 0.8,
                    "articles": ["6", "7"]
                })
                
        # Check for data transfers
        transfer_patterns = [
            (r'(?i)api\.send\(.*?\)', "API data transfer without safeguards"),
            (r'(?i)export.*?(data|user)', "Data export functionality"),
            (r'(?i)(third[_-]party|external)', "References to third-party service")
        ]
        
        for pattern, desc in transfer_patterns:
            for match in re.finditer(pattern, file_content):
                line_number = file_content[:match.start()].count('\n') + 1
                issues.append({
                    "issue_type": "data_transfer",
                    "line_number": line_number,
                    "description": f"{desc} without apparent transfer safeguards",
                    "remediation": "Implement appropriate safeguards for international data transfers",
                    "confidence": 0.7,
                    "articles": ["44", "45", "46"]
                })
                
        # Check for data retention
        if re.search(r'(?i)(user|data|profile|account)', file_content) and not re.search(r'(?i)(retention|expire|timeout|ttl|delete after)', file_content):
            issues.append({
                "issue_type": "data_retention",
                "line_number": 1,
                "description": "No clear data retention policy found in code handling personal data",
                "remediation": "Implement data retention policies that limit storage of personal data",
                "confidence": 0.6,
                "articles": ["5"]
            })
            
        return {
            "issues": issues,
            "summary": f"Template-based analysis found {len(issues)} potential GDPR compliance issues."
        }
    
    def _parse_ai_response(self, ai_analysis: Dict[str, Any], file_path: str) -> List[GDPRIssue]:
        """
        Parse AI response into GDPRIssue objects.
        
        Args:
            ai_analysis: AI analysis results
            file_path: Path to the file
            
        Returns:
            List of GDPRIssue objects
        """
        issues = []
        
        if "error" in ai_analysis:
            logger.error(f"Error in AI analysis: {ai_analysis['error']}")
            return issues
            
        if "issues" not in ai_analysis:
            logger.warning(f"No issues found in AI analysis for {file_path}")
            return issues
            
        for issue_data in ai_analysis["issues"]:
            try:
                # Validate required fields
                if not all(k in issue_data for k in ["issue_type", "line_number", "description", "remediation"]):
                    logger.warning(f"Missing required fields in issue: {issue_data}")
                    continue
                    
                # Create GDPRIssue
                issue = GDPRIssue(
                    file_path=file_path,
                    line_number=issue_data["line_number"],
                    issue_type=issue_data["issue_type"],
                    description=issue_data["description"],
                    remediation=issue_data["remediation"]
                )
                
                # Add articles if provided, otherwise get default articles for issue type
                if "articles" in issue_data and issue_data["articles"]:
                    issue.articles = issue_data["articles"]
                else:
                    issue.articles = get_articles_for_issue_type(issue_data["issue_type"])
                    
                # Add confidence if provided
                if "confidence" in issue_data:
                    issue.confidence = float(issue_data["confidence"])
                else:
                    issue.confidence = 0.7
                    
                issues.append(issue)
                
            except Exception as e:
                logger.error(f"Error parsing issue: {e}")
                
        return issues


# System prompt for AI analysis
SYSTEM_PROMPT = """
You are a GDPR compliance expert specialized in code analysis. Your task is to analyze code for potential GDPR compliance issues.

Focus on:
1. Personal data processing (collection, storage, transmission)
2. User consent management
3. Data subject rights implementation
4. Data transfer mechanisms
5. Data retention policies
6. Security measures for data protection
7. Privacy by design principles

Be specific in your analysis, providing exact line numbers and concrete remediation steps.
Respond in structured JSON format only.
""" 