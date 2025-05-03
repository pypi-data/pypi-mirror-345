"""
Hybrid Orchestrator for GDPR compliance scanning.

This module coordinates between rule-based scanning and AI-powered
contextual analysis to provide comprehensive GDPR compliance checking.
"""
import os
import json
import logging
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from pathlib import Path
import concurrent.futures
import time

from levox.scanner import GDPRIssue, GDPRScanner
from levox.ai_context_engine import AIContextEngine
from levox.remediation_module import RemediationModule
from levox.gdpr_articles import get_articles_for_issue_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hybrid_orchestrator")

class ScanResult:
    """
    Container for scan results from different engines.
    """
    
    def __init__(self):
        """Initialize scan result container."""
        self.rule_based_issues: List[GDPRIssue] = []
        self.ai_detected_issues: List[GDPRIssue] = []
        self.consolidated_issues: List[GDPRIssue] = []
        self.scan_stats: Dict[str, Any] = {
            "rule_based_count": 0,
            "ai_detected_count": 0,
            "consolidated_count": 0,
            "false_positives": 0,
            "confidence_levels": {},
            "files_scanned": 0,
            "execution_time": {
                "rule_based": 0,
                "ai": 0,
                "total": 0
            }
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert scan results to dictionary."""
        return {
            "rule_based_issues": [issue.to_dict() for issue in self.rule_based_issues],
            "ai_detected_issues": [issue.to_dict() for issue in self.ai_detected_issues],
            "consolidated_issues": [issue.to_dict() for issue in self.consolidated_issues],
            "scan_stats": self.scan_stats
        }
        
    def save_to_file(self, file_path: str) -> None:
        """
        Save scan results to a file.
        
        Args:
            file_path: Path to save the results
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
            

class HybridOrchestrator:
    """
    Coordinates rule-based scanning and AI-based contextual analysis.
    """
    
    def __init__(
        self, 
        rule_based_scanner: Optional[GDPRScanner] = None,
        ai_context_engine: Optional[AIContextEngine] = None,
        remediation_module: Optional[RemediationModule] = None,
        parallel: bool = True,
        confidence_threshold: float = 0.7
    ):
        """
        Initialize the hybrid orchestrator.
        
        Args:
            rule_based_scanner: Scanner for rule-based detection
            ai_context_engine: Engine for AI-based detection
            remediation_module: Module for fixing issues
            parallel: Whether to run scanning in parallel
            confidence_threshold: Threshold for AI-detected issues
        """
        self.rule_based_scanner = rule_based_scanner or GDPRScanner()
        self.ai_context_engine = ai_context_engine or AIContextEngine()
        self.remediation_module = remediation_module or RemediationModule()
        self.parallel = parallel
        self.confidence_threshold = confidence_threshold
        
    def scan(
        self, 
        target_paths: Union[str, List[str]],
        exclusions: Optional[List[str]] = None,
        max_files: Optional[int] = None
    ) -> ScanResult:
        """
        Perform a hybrid scan of the target paths.
        
        Args:
            target_paths: Paths to scan
            exclusions: Patterns to exclude
            max_files: Maximum number of files to scan
            
        Returns:
            ScanResult with consolidated issues
        """
        start_time = time.time()
        result = ScanResult()
        
        # Normalize target paths
        if isinstance(target_paths, str):
            target_paths = [target_paths]
            
        # Collect files to scan
        files_to_scan = self._collect_files(target_paths, exclusions, max_files)
        result.scan_stats["files_scanned"] = len(files_to_scan)
        
        logger.info(f"Starting hybrid scan of {len(files_to_scan)} files")
        
        # Perform rule-based scan
        rule_start_time = time.time()
        rule_based_issues = self._perform_rule_based_scan(files_to_scan)
        rule_end_time = time.time()
        
        # Record rule-based issues
        result.rule_based_issues = rule_based_issues
        result.scan_stats["rule_based_count"] = len(rule_based_issues)
        result.scan_stats["execution_time"]["rule_based"] = rule_end_time - rule_start_time
        
        # Perform AI-based scan
        ai_start_time = time.time()
        ai_detected_issues = self._perform_ai_scan(files_to_scan, rule_based_issues)
        ai_end_time = time.time()
        
        # Record AI-detected issues
        result.ai_detected_issues = ai_detected_issues
        result.scan_stats["ai_detected_count"] = len(ai_detected_issues)
        result.scan_stats["execution_time"]["ai"] = ai_end_time - ai_start_time
        
        # Consolidate issues
        consolidated_issues = self._consolidate_issues(rule_based_issues, ai_detected_issues)
        result.consolidated_issues = consolidated_issues
        result.scan_stats["consolidated_count"] = len(consolidated_issues)
        
        # Calculate confidence levels distribution
        confidence_levels = {}
        for issue in ai_detected_issues:
            confidence = getattr(issue, "confidence", 0)
            level = round(confidence * 10) / 10  # Round to nearest 0.1
            confidence_levels[str(level)] = confidence_levels.get(str(level), 0) + 1
            
        result.scan_stats["confidence_levels"] = confidence_levels
        
        # Calculate total time
        end_time = time.time()
        result.scan_stats["execution_time"]["total"] = end_time - start_time
        
        logger.info(f"Hybrid scan completed: {len(consolidated_issues)} issues found")
        logger.info(f"Rule-based: {len(rule_based_issues)}, AI-detected: {len(ai_detected_issues)}")
        
        return result
    
    def _collect_files(
        self, 
        target_paths: List[str],
        exclusions: Optional[List[str]] = None,
        max_files: Optional[int] = None
    ) -> List[str]:
        """
        Collect files to scan based on target paths and exclusions.
        
        Args:
            target_paths: Paths to scan
            exclusions: Patterns to exclude
            max_files: Maximum number of files to scan
            
        Returns:
            List of file paths to scan
        """
        if not exclusions:
            exclusions = [
                "__pycache__", ".git", ".idea", ".vscode", 
                "venv", "node_modules", "build", "dist",
                ".pytest_cache", ".coverage"
            ]
            
        files_to_scan = []
        
        for target_path in target_paths:
            path = Path(target_path)
            
            if path.is_file() and path.suffix.lower() in {".py", ".js", ".ts", ".jsx", ".tsx"}:
                files_to_scan.append(str(path))
            elif path.is_dir():
                for root, dirs, files in os.walk(path):
                    # Apply directory exclusions
                    dirs[:] = [d for d in dirs if d not in exclusions]
                    
                    for file in files:
                        if Path(file).suffix.lower() in {".py", ".js", ".ts", ".jsx", ".tsx"}:
                            full_path = Path(root) / file
                            # Check if file path contains any exclusion pattern
                            if not any(excl in str(full_path) for excl in exclusions):
                                files_to_scan.append(str(full_path))
        
        # Apply max_files limit if specified
        if max_files and len(files_to_scan) > max_files:
            files_to_scan = files_to_scan[:max_files]
            
        return files_to_scan
    
    def _perform_rule_based_scan(self, files: List[str]) -> List[GDPRIssue]:
        """
        Perform rule-based scanning on files.
        
        Args:
            files: List of files to scan
            
        Returns:
            List of GDPRIssue objects from rule-based scan
        """
        logger.info(f"Starting rule-based scan of {len(files)} files")
        all_issues = []
        
        if self.parallel and len(files) > 1:
            # Parallel scanning
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_file = {
                    executor.submit(self.rule_based_scanner.scan_file, file): file 
                    for file in files
                }
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        issues = future.result()
                        all_issues.extend(issues)
                    except Exception as e:
                        logger.error(f"Error scanning file {file}: {e}")
        else:
            # Sequential scanning
            for file in files:
                try:
                    issues = self.rule_based_scanner.scan_file(file)
                    all_issues.extend(issues)
                except Exception as e:
                    logger.error(f"Error scanning file {file}: {e}")
                    
        logger.info(f"Rule-based scan completed: {len(all_issues)} issues found")
        return all_issues
    
    def _perform_ai_scan(self, files: List[str], rule_based_issues: List[GDPRIssue]) -> List[GDPRIssue]:
        """
        Perform AI-based scanning on files.
        
        Args:
            files: List of files to scan
            rule_based_issues: Issues from rule-based scan (for context)
            
        Returns:
            List of GDPRIssue objects from AI-based scan
        """
        logger.info(f"Starting AI-based scan of {len(files)} files")
        all_issues = []
        
        # Create a mapping of files to rule-based issues for context
        file_issues_map = {}
        for issue in rule_based_issues:
            if issue.file_path not in file_issues_map:
                file_issues_map[issue.file_path] = []
            file_issues_map[issue.file_path].append(issue)
        
        # Prioritize files with rule-based issues for AI scanning
        prioritized_files = list(file_issues_map.keys())
        remaining_files = [f for f in files if f not in file_issues_map]
        
        # Combine prioritized and remaining files
        ordered_files = prioritized_files + remaining_files
        
        if self.parallel and len(ordered_files) > 1:
            # Parallel scanning
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_file = {
                    executor.submit(
                        self.ai_context_engine.analyze_file, 
                        file, 
                        file_issues_map.get(file, [])
                    ): file for file in ordered_files
                }
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        issues = future.result()
                        # Filter issues by confidence threshold
                        issues = [i for i in issues if getattr(i, "confidence", 0) >= self.confidence_threshold]
                        all_issues.extend(issues)
                    except Exception as e:
                        logger.error(f"Error AI scanning file {file}: {e}")
        else:
            # Sequential scanning
            for file in ordered_files:
                try:
                    issues = self.ai_context_engine.analyze_file(file, file_issues_map.get(file, []))
                    # Filter issues by confidence threshold
                    issues = [i for i in issues if getattr(i, "confidence", 0) >= self.confidence_threshold]
                    all_issues.extend(issues)
                except Exception as e:
                    logger.error(f"Error AI scanning file {file}: {e}")
                    
        logger.info(f"AI-based scan completed: {len(all_issues)} issues found")
        return all_issues
    
    def _consolidate_issues(
        self, 
        rule_based_issues: List[GDPRIssue], 
        ai_detected_issues: List[GDPRIssue]
    ) -> List[GDPRIssue]:
        """
        Consolidate issues from rule-based and AI-based scans.
        
        Args:
            rule_based_issues: Issues from rule-based scan
            ai_detected_issues: Issues from AI-based scan
            
        Returns:
            Consolidated list of issues with duplicates resolved and similar issues grouped
        """
        # Create a dictionary to track issues by location
        consolidated = {}
        false_positives = 0
        
        # Process rule-based issues first
        for issue in rule_based_issues:
            key = f"{issue.file_path}:{issue.line_number}:{issue.issue_type}"
            consolidated[key] = issue
        
        # Process AI-detected issues
        for issue in ai_detected_issues:
            key = f"{issue.file_path}:{issue.line_number}:{issue.issue_type}"
            
            if key in consolidated:
                # Issue already exists from rule-based scan, enhance it
                existing_issue = consolidated[key]
                
                # Merge articles
                existing_issue.articles = list(set(existing_issue.articles + issue.articles))
                
                # Enhance description if AI provides more details
                if len(issue.description) > len(existing_issue.description):
                    existing_issue.description = issue.description
                    
                # Enhance remediation if AI provides more details
                if len(issue.remediation) > len(existing_issue.remediation):
                    existing_issue.remediation = issue.remediation
                    
                # Add confidence from AI
                if hasattr(issue, "confidence"):
                    existing_issue.confidence = issue.confidence
            else:
                # New issue from AI
                consolidated[key] = issue
        
        # Convert back to list
        result = list(consolidated.values())
        
        # Group similar issues
        if result and self.config.get("remediation.group_similar_issues", True):
            result = self._group_similar_issues(result)
            
        return result

    def _group_similar_issues(self, issues: List[GDPRIssue]) -> List[GDPRIssue]:
        """
        Group similar issues to reduce redundancy.
        
        Args:
            issues: List of issues to group
            
        Returns:
            List of grouped issues
        """
        # Sort issues by file path and issue type
        issues_by_file = {}
        for issue in issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = {}
                
            if issue.issue_type not in issues_by_file[issue.file_path]:
                issues_by_file[issue.file_path][issue.issue_type] = []
                
            issues_by_file[issue.file_path][issue.issue_type].append(issue)
            
        # Group issues by proximity
        grouped_issues = []
        max_distance = self.config.get("remediation.max_group_distance", 10)
        
        for file_path, issue_types in issues_by_file.items():
            for issue_type, file_issues in issue_types.items():
                # Sort issues by line number
                file_issues.sort(key=lambda x: x.line_number)
                
                # Group issues that are close to each other
                current_group = [file_issues[0]]
                
                for i in range(1, len(file_issues)):
                    current_issue = file_issues[i]
                    last_issue = current_group[-1]
                    
                    # If the current issue is close to the last issue in the group, add it to the group
                    if current_issue.line_number - last_issue.line_number <= max_distance:
                        current_group.append(current_issue)
                    else:
                        # Create a grouped issue from the current group
                        grouped_issue = self._create_grouped_issue(current_group)
                        grouped_issues.append(grouped_issue)
                        
                        # Start a new group
                        current_group = [current_issue]
                        
                # Create a grouped issue from the last group
                if current_group:
                    grouped_issue = self._create_grouped_issue(current_group)
                    grouped_issues.append(grouped_issue)
                    
        return grouped_issues
        
    def _create_grouped_issue(self, issues: List[GDPRIssue]) -> GDPRIssue:
        """
        Create a grouped issue from a list of similar issues.
        
        Args:
            issues: List of similar issues
            
        Returns:
            A new issue representing the group
        """
        if len(issues) == 1:
            return issues[0]
            
        # Use the first issue as a template
        base_issue = issues[0]
        
        # Calculate line range
        start_line = min(issue.line_number for issue in issues)
        end_line = max(issue.line_number for issue in issues)
        
        # Create a descriptive range string
        line_range = f"{start_line}-{end_line}" if start_line != end_line else str(start_line)
        
        # Merge articles from all issues
        all_articles = set()
        for issue in issues:
            all_articles.update(issue.articles)
            
        # Determine highest severity
        severity_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        highest_severity = base_issue.severity
        for issue in issues:
            if severity_levels.get(issue.severity, 0) > severity_levels.get(highest_severity, 0):
                highest_severity = issue.severity
                
        # Create grouped description
        if len(issues) > 1:
            description = f"{base_issue.issue_type.replace('_', ' ').title()} issues found in lines {line_range} ({len(issues)} instances)"
            
            # Add specific details for each instance
            details = "\n\nInstances:\n"
            for i, issue in enumerate(issues, 1):
                details += f"- Line {issue.line_number}: {issue.description}\n"
                
            description += details
        else:
            description = base_issue.description
            
        # Create remediation with consolidated advice
        remediation = f"""# {base_issue.issue_type.replace('_', ' ').title()} Issues (Lines {line_range})

Multiple instances of this issue type were detected in close proximity. A consolidated fix is recommended:

{base_issue.remediation}

Consider addressing these issues with a systematic approach rather than fixing each line individually.
"""
        
        # Create the grouped issue
        grouped_issue = GDPRIssue(
            file_path=base_issue.file_path,
            line_number=start_line,
            issue_type=base_issue.issue_type,
            description=description,
            remediation=remediation,
            severity=highest_severity,
            articles=list(all_articles)
        )
        
        # Add metadata about the group
        setattr(grouped_issue, 'grouped', True)
        setattr(grouped_issue, 'group_size', len(issues))
        setattr(grouped_issue, 'line_range', (start_line, end_line))
        
        # For confidence, use the highest confidence
        highest_confidence = max((getattr(issue, 'confidence', 0) for issue in issues), default=0)
        setattr(grouped_issue, 'confidence', highest_confidence)
        
        return grouped_issue
    
    def remediate(
        self, 
        scan_result: ScanResult,
        auto_fix: bool = False,
        generate_docs: bool = True,
        output_dir: str = "."
    ) -> Dict[str, Any]:
        """
        Remediate issues found by the scan.
        
        Args:
            scan_result: The ScanResult from a scan
            auto_fix: Whether to automatically apply fixes
            generate_docs: Whether to generate documentation
            output_dir: Directory to save documentation
            
        Returns:
            Dictionary with remediation results
        """
        logger.info(f"Starting remediation of {len(scan_result.consolidated_issues)} issues")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Remediate issues
        remediation_results = self.remediation_module.remediate_issues(
            scan_result.consolidated_issues, 
            fix=auto_fix,
            document=generate_docs
        )
        
        # Save scan report
        report_path = os.path.join(output_dir, "gdpr_scan_report.json")
        scan_result.save_to_file(report_path)
        
        logger.info(f"Remediation completed. Report saved to {report_path}")
        
        return {
            "remediation_results": remediation_results,
            "report_path": report_path
        } 