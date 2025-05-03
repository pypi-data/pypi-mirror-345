"""
Data Flow Analyzer for GDPR Compliance

This module implements data flow analysis with Zero Knowledge proofs to track
how data moves through applications while ensuring sensitive data remains protected.
"""

import os
import re
import ast
import hashlib
import json
import networkx as nx
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union, Optional, Any
import logging

# Define data source categories
DATA_SOURCES = {
    'user_input': [
        r'request\.form', r'request\.get_json\(\)', r'request\.args',
        r'input\(', r'getattr\(request', r'request\[', r'request\.data',
        r'input\s*\(', r'prompt\s*\(', r'document\.getElementById',
        r'\.value', r'\.innerHTML', r'\.innerText'
    ],
    'database_read': [
        r'\.query', r'\.find', r'\.findOne', r'\.get', r'\.select',
        r'\.execute\(', r'cursor\.execute', r'Model\.objects',
        r'\.find_by_', r'\.where\(', r'\.filter\('
    ],
    'file_read': [
        r'open\s*\(.*,\s*[\'"]r[\'"]', r'read\(\)', r'readlines\(\)',
        r'fs\.read', r'FileReader', r'readFile', r'readFileSync'
    ],
    'api_response': [
        r'requests\.get', r'urllib\.request', r'http\.get', r'axios\.get',
        r'fetch\(', r'\.json\(\)', r'response\.data', r'\.content'
    ]
}

# Define data sink categories
DATA_SINKS = {
    'database_write': [
        r'\.save\(', r'\.insert', r'\.update', r'\.create', r'\.add\(',
        r'\.commit\(', r'execute\(', r'cursor\.execute'
    ],
    'api_request': [
        r'requests\.post', r'requests\.put', r'axios\.post', r'http\.post',
        r'fetch\(.*method.*post', r'\.send\(', r'\.request\('
    ],
    'file_write': [
        r'open\s*\(.*,\s*[\'"]w[\'"]', r'\.write\(', r'fs\.write',
        r'writeFile', r'writeFileSync'
    ],
    'logging': [
        r'logger\.', r'logging\.', r'console\.log', r'print\('
    ],
    'cookie_storage': [
        r'document\.cookie', r'cookies\.set', r'set_cookie', r'\.set_cookie\('
    ],
    'local_storage': [
        r'localStorage\.', r'sessionStorage\.', r'$.storage'
    ]
}

# Define data transformation operations
DATA_TRANSFORMATIONS = {
    'encryption': [
        r'encrypt', r'cipher', r'AES', r'RSA', r'Crypto', r'createCipher',
        r'pbkdf2', r'bcrypt'
    ],
    'hashing': [
        r'hash', r'sha\d+', r'md5', r'hashlib', r'createHash', r'digest',
        r'hmac', r'pbkdf2'
    ],
    'anonymization': [
        r'anonymize', r'pseudonymize', r'mask', r'tokenize', r'scramble'
    ],
    'data_minimization': [
        r'filter', r'select', r'projection', r'exclude', r'omit',
        r'\.values\(', r'only\('
    ]
}

# Sensitive data patterns
SENSITIVE_DATA_PATTERNS = [
    r'password', r'passwd', r'secret', r'key', r'token', r'auth',
    r'social_security', r'ssn', r'national_id', r'passport',
    r'credit_card', r'card_number', r'cvv', r'email', r'address',
    r'phone', r'dob', r'birth_date', r'gender', r'salary', r'income'
]

class DataNode:
    """
    A node in the data flow graph representing a data point with its characteristics.
    Implements Zero Knowledge proof concepts to protect sensitive data.
    """
    
    def __init__(self, 
                 node_id: str, 
                 node_type: str, 
                 file_path: str, 
                 line_number: int,
                 variable_name: str = None,
                 content_hash: str = None,
                 data_category: str = None,
                 is_sensitive: bool = False):
        self.id = node_id
        self.type = node_type  # source, sink, transformation
        self.file_path = file_path
        self.line_number = line_number
        self.variable_name = variable_name
        self.content_hash = content_hash  # For Zero Knowledge verification
        self.data_category = data_category
        self.is_sensitive = is_sensitive
        self.transformations = []
    
    def secure_hash(self, content: str) -> str:
        """
        Create a secure hash of content (for Zero Knowledge proofs)
        """
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_content(self, content: str) -> bool:
        """
        Verify content matches the stored hash without revealing the content
        (Zero Knowledge verification)
        """
        if not self.content_hash:
            return False
        return self.secure_hash(content) == self.content_hash
    
    def to_dict(self) -> Dict:
        """
        Convert the node to a dictionary representation
        """
        return {
            'id': self.id,
            'type': self.type,
            'file': self.file_path,
            'line': self.line_number,
            'variable': self.variable_name,
            'category': self.data_category,
            'is_sensitive': self.is_sensitive,
            'transformations': self.transformations
        }
    
    def __str__(self) -> str:
        return f"{self.type} ({self.data_category}): {self.variable_name} at {self.file_path}:{self.line_number}"

class DataFlowGraph:
    """
    A directed graph representing data flows in the application.
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes = {}  # id -> DataNode
    
    def add_node(self, node: DataNode) -> None:
        """
        Add a node to the graph
        """
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **node.to_dict())
    
    def add_edge(self, source_id: str, target_id: str, edge_type: str = "data_flow") -> None:
        """
        Add an edge between two nodes
        """
        if source_id in self.nodes and target_id in self.nodes:
            self.graph.add_edge(source_id, target_id, type=edge_type)
    
    def get_node(self, node_id: str) -> Optional[DataNode]:
        """
        Get a node by its ID
        """
        return self.nodes.get(node_id)
    
    def get_paths(self, source_id: str, sink_id: str) -> List[List[str]]:
        """
        Get all paths from source to sink
        """
        try:
            return list(nx.all_simple_paths(self.graph, source_id, sink_id))
        except nx.NetworkXNoPath:
            return []
    
    def get_sources_for_sink(self, sink_id: str) -> List[DataNode]:
        """
        Get all source nodes that flow into a sink
        """
        sources = []
        for node_id in self.nodes:
            if self.nodes[node_id].type == "source":
                if nx.has_path(self.graph, node_id, sink_id):
                    sources.append(self.nodes[node_id])
        return sources
    
    def find_unprotected_flows(self) -> List[Dict]:
        """
        Find flows where sensitive data goes to a sink without proper transformation
        """
        issues = []
        
        for node_id, node in self.nodes.items():
            if node.type == "sink":
                # Get all sources that flow into this sink
                sources = self.get_sources_for_sink(node_id)
                
                for source in sources:
                    if source.is_sensitive:
                        # Get all paths from this source to the sink
                        paths = self.get_paths(source.id, node_id)
                        
                        for path in paths:
                            # Check if any path contains proper transformations
                            has_protection = False
                            for path_node_id in path:
                                path_node = self.nodes[path_node_id]
                                if path_node.type == "transformation" and any(
                                    t in ["encryption", "hashing", "anonymization"] 
                                    for t in path_node.transformations
                                ):
                                    has_protection = True
                                    break
                            
                            if not has_protection:
                                issue = {
                                    "issue_type": "unprotected_sensitive_data_flow",
                                    "source": source.to_dict(),
                                    "sink": node.to_dict(),
                                    "description": f"Sensitive data from {source.variable_name} flows to {node.data_category} without proper protection",
                                    "severity": "high",
                                    "remediation": f"Apply encryption, hashing, or anonymization to {source.variable_name} before sending to {node.data_category}"
                                }
                                issues.append(issue)
        
        return issues
    
    def export_to_json(self, output_file: str) -> None:
        """
        Export the graph to a JSON file for visualization
        """
        data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [{"source": u, "target": v, "type": d["type"]} 
                      for u, v, d in self.graph.edges(data=True)]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

class DataFlowAnalyzer:
    """
    Analyzes code for data flows and potential GDPR compliance issues.
    """
    
    def __init__(self):
        self.graph = DataFlowGraph()
        self.variables = {}  # variable_name -> node_id
        self.next_node_id = 0
    
    def _get_next_node_id(self) -> str:
        """Get the next unique node ID"""
        node_id = f"node_{self.next_node_id}"
        self.next_node_id += 1
        return node_id
    
    def analyze_directory(self, directory_path: str) -> DataFlowGraph:
        """
        Analyze all files in a directory recursively
        """
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                    file_path = os.path.join(root, file)
                    self.analyze_file(file_path)
        
        return self.graph
    
    def analyze_file(self, file_path: str) -> None:
        """
        Analyze a single file for data flows
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Reset the variables dictionary for this file
        self.variables = {}
        
        if file_path.endswith('.py'):
            self._analyze_python_file(file_path, content)
        else:
            self._analyze_with_regex(file_path, content)
    
    def _analyze_python_file(self, file_path: str, content: str) -> None:
        """
        Analyze a Python file using AST for better accuracy
        """
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                # Find variable assignments
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Check if the right side contains a source
                            source_type = self._check_node_for_source(node.value, content)
                            if source_type:
                                line_number = node.lineno
                                var_name = target.id
                                
                                # Create a source node
                                node_id = self._get_next_node_id()
                                data_node = DataNode(
                                    node_id=node_id,
                                    node_type="source",
                                    file_path=file_path,
                                    line_number=line_number,
                                    variable_name=var_name,
                                    data_category=source_type,
                                    is_sensitive=self._is_sensitive_variable(var_name)
                                )
                                self.graph.add_node(data_node)
                                self.variables[var_name] = node_id
                
                # Find function calls that could be sinks
                elif isinstance(node, ast.Call):
                    # Check if it's a sink
                    sink_type = self._check_node_for_sink(node, content)
                    if sink_type:
                        line_number = node.lineno
                        
                        # Create a sink node
                        node_id = self._get_next_node_id()
                        sink_node = DataNode(
                            node_id=node_id,
                            node_type="sink",
                            file_path=file_path,
                            line_number=line_number,
                            data_category=sink_type
                        )
                        self.graph.add_node(sink_node)
                        
                        # Find data flowing into this sink
                        for arg in node.args:
                            if isinstance(arg, ast.Name) and arg.id in self.variables:
                                source_id = self.variables[arg.id]
                                self.graph.add_edge(source_id, node_id)
                        
                        # Also check keyword arguments
                        for keyword in node.keywords:
                            if isinstance(keyword.value, ast.Name) and keyword.value.id in self.variables:
                                source_id = self.variables[keyword.value.id]
                                self.graph.add_edge(source_id, node_id)
                
                # Check for transformation operations
                elif isinstance(node, ast.Call):
                    transformation_type = self._check_node_for_transformation(node, content)
                    if transformation_type:
                        line_number = node.lineno
                        
                        # Create a transformation node
                        node_id = self._get_next_node_id()
                        transform_node = DataNode(
                            node_id=node_id,
                            node_type="transformation",
                            file_path=file_path,
                            line_number=line_number,
                            data_category=transformation_type
                        )
                        transform_node.transformations.append(transformation_type)
                        self.graph.add_node(transform_node)
                        
                        # Find data flowing into this transformation
                        for arg in node.args:
                            if isinstance(arg, ast.Name) and arg.id in self.variables:
                                source_id = self.variables[arg.id]
                                self.graph.add_edge(source_id, node_id)
                                
                                # If this is an assignment, update the variable to point to transformed data
                                parent = self._get_parent_assignment(tree, node)
                                if parent and isinstance(parent, ast.Assign):
                                    for target in parent.targets:
                                        if isinstance(target, ast.Name):
                                            self.variables[target.id] = node_id
                
        except SyntaxError:
            # Fallback to regex-based analysis if AST parsing fails
            self._analyze_with_regex(file_path, content)
    
    def _get_parent_assignment(self, tree, target_node):
        """Find the parent assignment node for a given node"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for child in ast.walk(node.value):
                    if child == target_node:
                        return node
        return None
    
    def _check_node_for_source(self, node, content):
        """Check if an AST node represents a data source"""
        node_str = ast.unparse(node) if hasattr(ast, 'unparse') else content[node.lineno-1]
        
        for source_type, patterns in DATA_SOURCES.items():
            for pattern in patterns:
                if re.search(pattern, node_str):
                    return source_type
        return None
    
    def _check_node_for_sink(self, node, content):
        """Check if an AST node represents a data sink"""
        node_str = ast.unparse(node) if hasattr(ast, 'unparse') else content[node.lineno-1]
        
        for sink_type, patterns in DATA_SINKS.items():
            for pattern in patterns:
                if re.search(pattern, node_str):
                    return sink_type
        return None
    
    def _check_node_for_transformation(self, node, content):
        """Check if an AST node represents a data transformation"""
        node_str = ast.unparse(node) if hasattr(ast, 'unparse') else content[node.lineno-1]
        
        for transform_type, patterns in DATA_TRANSFORMATIONS.items():
            for pattern in patterns:
                if re.search(pattern, node_str):
                    return transform_type
        return None
    
    def _analyze_with_regex(self, file_path: str, content: str) -> None:
        """
        Analyze a file using regex patterns when AST analysis is not available
        """
        lines = content.split('\n')
        
        # Find sources
        for i, line in enumerate(lines):
            line_number = i + 1
            
            for source_type, patterns in DATA_SOURCES.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        # Extract variable name (simplified approach)
                        var_match = re.search(r'(\w+)\s*=', line)
                        var_name = var_match.group(1) if var_match else f"unknown_var_{i}"
                        
                        # Create a source node
                        node_id = self._get_next_node_id()
                        data_node = DataNode(
                            node_id=node_id,
                            node_type="source",
                            file_path=file_path,
                            line_number=line_number,
                            variable_name=var_name,
                            data_category=source_type,
                            is_sensitive=self._is_sensitive_variable(var_name)
                        )
                        self.graph.add_node(data_node)
                        self.variables[var_name] = node_id
            
            # Find sinks
            for sink_type, patterns in DATA_SINKS.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        # Create a sink node
                        node_id = self._get_next_node_id()
                        sink_node = DataNode(
                            node_id=node_id,
                            node_type="sink",
                            file_path=file_path,
                            line_number=line_number,
                            data_category=sink_type
                        )
                        self.graph.add_node(sink_node)
                        
                        # Find variables used in this line
                        for var_name in self.variables:
                            if re.search(r'\b' + re.escape(var_name) + r'\b', line):
                                source_id = self.variables[var_name]
                                self.graph.add_edge(source_id, node_id)
            
            # Find transformations
            for transform_type, patterns in DATA_TRANSFORMATIONS.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        # Create a transformation node
                        node_id = self._get_next_node_id()
                        transform_node = DataNode(
                            node_id=node_id,
                            node_type="transformation",
                            file_path=file_path,
                            line_number=line_number,
                            data_category=transform_type
                        )
                        transform_node.transformations.append(transform_type)
                        self.graph.add_node(transform_node)
                        
                        # Find variables used in this line
                        for var_name in self.variables:
                            if re.search(r'\b' + re.escape(var_name) + r'\b', line):
                                source_id = self.variables[var_name]
                                self.graph.add_edge(source_id, node_id)
                                
                                # If this is an assignment, update the variable
                                var_match = re.search(r'(\w+)\s*=', line)
                                if var_match:
                                    new_var = var_match.group(1)
                                    self.variables[new_var] = node_id
    
    def _is_sensitive_variable(self, variable_name: str) -> bool:
        """
        Check if a variable name suggests it contains sensitive data
        """
        for pattern in SENSITIVE_DATA_PATTERNS:
            if re.search(pattern, variable_name.lower()):
                return True
        return False

def analyze_data_flows(directory_path: str, export_path: str = None) -> List[Dict]:
    """
    Analyze data flows in a directory and identify potential GDPR compliance issues.
    
    Args:
        directory_path: Path to the directory to analyze
        export_path: Optional path to export the data flow graph as JSON
        
    Returns:
        List of potential GDPR compliance issues related to data flows
    """
    analyzer = DataFlowAnalyzer()
    graph = analyzer.analyze_directory(directory_path)
    
    # Find potential issues
    issues = graph.find_unprotected_flows()
    
    # Export graph if requested
    if export_path:
        graph.export_to_json(export_path)
    
    return issues 