"""
GDPR Articles module for Levox compliance scanner.

This module provides access to GDPR article information and helpers
to associate specific GDPR articles with detected compliance issues.
"""
from typing import Dict, List, Optional


# Dictionary mapping GDPR articles to their titles and summaries
GDPR_ARTICLES = {
    "5": {
        "title": "Principles relating to processing of personal data",
        "summary": "Personal data shall be processed lawfully, fairly, with transparency, for legitimate purposes, with data minimization, accuracy, storage limitation, and with integrity and confidentiality."
    },
    "6": {
        "title": "Lawfulness of processing",
        "summary": "Processing is lawful only with consent, contractual necessity, legal obligation, vital interests, public interest, or legitimate interests."
    },
    "7": {
        "title": "Conditions for consent",
        "summary": "Consent must be freely given, specific, informed, unambiguous, demonstrable, easy to withdraw, and in clear and plain language."
    },
    "8": {
        "title": "Conditions applicable to child's consent",
        "summary": "Processing of child's data requires parental consent for children under 16 years (or lower as per Member State law, but not below 13 years)."
    },
    "9": {
        "title": "Processing of special categories of personal data",
        "summary": "Processing of sensitive data (race, religion, health, etc.) is prohibited unless specific conditions apply."
    },
    "12": {
        "title": "Transparent information, communication and modalities",
        "summary": "Controllers must provide information in clear, plain language and facilitate exercise of data subject rights."
    },
    "13": {
        "title": "Information to be provided where personal data are collected",
        "summary": "When collecting data directly, controllers must provide specific information including identity, purpose, and data subject rights."
    },
    "14": {
        "title": "Information to be provided where personal data have not been obtained from the data subject",
        "summary": "When data is not obtained directly, controllers must provide information on source and categories of data."
    },
    "15": {
        "title": "Right of access by the data subject",
        "summary": "Data subjects have the right to obtain confirmation of processing and access to their personal data."
    },
    "16": {
        "title": "Right to rectification",
        "summary": "Data subjects have the right to rectify inaccurate personal data without undue delay."
    },
    "17": {
        "title": "Right to erasure ('right to be forgotten')",
        "summary": "Data subjects have the right to erasure of personal data under certain conditions."
    },
    "18": {
        "title": "Right to restriction of processing",
        "summary": "Data subjects can restrict processing in specific circumstances."
    },
    "19": {
        "title": "Notification obligation regarding rectification or erasure",
        "summary": "Controllers must communicate changes to recipients of the data."
    },
    "20": {
        "title": "Right to data portability",
        "summary": "Data subjects can receive their data in a structured, commonly used, machine-readable format."
    },
    "21": {
        "title": "Right to object",
        "summary": "Data subjects can object to processing based on legitimate interests, public interest, or profiling."
    },
    "22": {
        "title": "Automated individual decision-making, including profiling",
        "summary": "Data subjects have the right not to be subject to automated decision-making with legal effects."
    },
    "25": {
        "title": "Data protection by design and by default",
        "summary": "Controllers must implement appropriate technical and organizational measures for data protection principles."
    },
    "28": {
        "title": "Processor",
        "summary": "Controllers must use processors that provide sufficient guarantees of GDPR compliance."
    },
    "30": {
        "title": "Records of processing activities",
        "summary": "Controllers and processors must maintain records of processing activities."
    },
    "32": {
        "title": "Security of processing",
        "summary": "Controllers and processors must implement appropriate security measures."
    },
    "33": {
        "title": "Notification of a personal data breach",
        "summary": "Controllers must notify authorities of data breaches within 72 hours."
    },
    "34": {
        "title": "Communication of a personal data breach to the data subject",
        "summary": "Controllers must communicate high-risk breaches to affected data subjects."
    },
    "35": {
        "title": "Data protection impact assessment",
        "summary": "Controllers must conduct impact assessments for high-risk processing."
    },
    "44": {
        "title": "General principle for transfers",
        "summary": "Transfers to third countries require adequate protection or specific safeguards."
    },
    "45": {
        "title": "Transfers on the basis of an adequacy decision",
        "summary": "Transfers allowed to countries with Commission adequacy decisions."
    },
    "46": {
        "title": "Transfers subject to appropriate safeguards",
        "summary": "Transfers allowed with appropriate safeguards like standard contractual clauses."
    },
    "47": {
        "title": "Binding corporate rules",
        "summary": "Corporate groups can use binding corporate rules for international transfers."
    },
    "48": {
        "title": "Transfers not authorized by Union law",
        "summary": "Foreign court judgments requiring transfers only recognized if based on international agreement."
    },
    "49": {
        "title": "Derogations for specific situations",
        "summary": "Transfers allowed in specific situations like explicit consent or contract necessity."
    }
}


# Mapping of issue types to GDPR article numbers
ISSUE_TYPE_TO_ARTICLES = {
    "data_transfer": ["44", "45", "46", "47", "48", "49"],
    "pii_collection": ["5", "6", "7"],
    "pii_search_function": ["5", "6", "25", "32"],
    "pii_search": ["5", "6", "25", "32"],
    "consent_issues": ["7", "8"],
    "data_breach": ["33", "34"],
    "dpia_needed": ["35", "36"],
    "third_party_integration": ["28", "29"],
    "data_deletion": ["17", "19"],
    "data_retention": ["5", "17", "89"],
    "automated_decision": ["22"],
    "children_data": ["8"],
    "sensitive_data": ["9", "10"],
    "data_subject_rights": ["12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"],
    "documentation": ["5", "24", "30"],
    # New issue types
    "pii_storage": ["5", "6", "25", "32", "89"],
    "pii_processing": ["5", "6", "25"],
    "data_minimization": ["5", "25", "89"],
    "security_measures": ["5", "32", "34"],
    "cross_border_transfers": ["44", "45", "46", "47", "48", "49"],
    "user_rights": ["12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]
}

# Map issue types to severity levels based on CNIL/EDPB guidelines
ISSUE_TYPE_TO_SEVERITY = {
    "data_transfer": "high",
    "pii_collection": "high",
    "pii_search_function": "medium",
    "pii_search": "medium",
    "consent_issues": "high",
    "data_breach": "critical",
    "dpia_needed": "high",
    "third_party_integration": "high",
    "data_deletion": "high",
    "data_retention": "medium",
    "automated_decision": "high",
    "children_data": "critical",
    "sensitive_data": "critical",
    "data_subject_rights": "high",
    "documentation": "medium",
    "pii_storage": "high",
    "pii_processing": "medium",
    "data_minimization": "medium",
    "security_measures": "high",
    "cross_border_transfers": "high",
    "user_rights": "high"
}


def get_articles_for_issue_type(issue_type: str) -> List[str]:
    """
    Get the list of GDPR article numbers relevant to a specific issue type.
    
    Args:
        issue_type: The type of GDPR issue
        
    Returns:
        List of article numbers as strings
    """
    return ISSUE_TYPE_TO_ARTICLES.get(issue_type, [])


def get_severity_for_issue_type(issue_type: str) -> str:
    """
    Get the default severity for a specific issue type based on GDPR risk levels.
    
    Args:
        issue_type: The type of GDPR issue
        
    Returns:
        Severity level as string ('low', 'medium', 'high', or 'critical')
    """
    return ISSUE_TYPE_TO_SEVERITY.get(issue_type, "medium")


def get_article_info(article_number: str) -> Optional[Dict]:
    """
    Get information about a specific GDPR article.
    
    Args:
        article_number: The GDPR article number as a string
        
    Returns:
        Dictionary with article information or None if not found
    """
    return GDPR_ARTICLES.get(article_number)


def format_article_reference(article_number: str) -> str:
    """
    Format a GDPR article reference with title.
    
    Args:
        article_number: The GDPR article number as a string
        
    Returns:
        Formatted reference string like "Article 5 - Principles relating to processing"
    """
    article_info = get_article_info(article_number)
    if not article_info:
        return f"Article {article_number}"
    
    return f"Article {article_number} - {article_info['title']}" 