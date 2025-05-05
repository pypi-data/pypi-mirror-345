"""
Formatters module for Python Source AST Analyzer.

This module contains formatters for outputting call graph data in various formats.
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, TextIO, Optional, Set


class BaseFormatter(ABC):
    """
    Base class for formatters.
    
    This abstract class defines the interface for formatters.
    """
    
    @abstractmethod
    def format_outbound_calls(self, data: Dict[str, Any]) -> str:
        """
        Format outbound calls data.
        
        Args:
            data: The outbound calls data to format.
            
        Returns:
            The formatted data as a string.
        """
        pass
        
    @abstractmethod
    def format_inbound_calls(self, data: Dict[str, Any]) -> str:
        """
        Format inbound calls data.
        
        Args:
            data: The inbound calls data to format.
            
        Returns:
            The formatted data as a string.
        """
        pass
        
    @abstractmethod
    def format_methods(self, methods: List[Dict]) -> str:
        """
        Format methods data.
        
        Args:
            methods: The methods data to format.
            
        Returns:
            The formatted data as a string.
        """
        pass
        
    def write_to_file(self, data: str, file_path: str) -> None:
        """
        Write formatted data to a file.
        
        Args:
            data: The formatted data to write.
            file_path: The path of the file to write to.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)


class JSONFormatter(BaseFormatter):
    """
    JSON formatter for call graph data.
    
    This formatter outputs call graph data in JSON format.
    """
    
    def __init__(self, indent: int = 2):
        """
        Initialize the JSON formatter.
        
        Args:
            indent: The indentation level for the JSON output.
        """
        self.indent = indent
        
    def format_outbound_calls(self, data: Dict[str, Any]) -> str:
        """
        Format outbound calls data as JSON.
        
        Args:
            data: The outbound calls data to format.
            
        Returns:
            The formatted data as a JSON string.
        """
        return json.dumps(data, indent=self.indent)
        
    def format_inbound_calls(self, data: Dict[str, Any]) -> str:
        """
        Format inbound calls data as JSON.
        
        Args:
            data: The inbound calls data to format.
            
        Returns:
            The formatted data as a JSON string.
        """
        return json.dumps(data, indent=self.indent)
        
    def format_methods(self, methods: List[Dict]) -> str:
        """
        Format methods data as JSON.
        
        Args:
            methods: The methods data to format.
            
        Returns:
            The formatted data as a JSON string.
        """
        return json.dumps(methods, indent=self.indent)


class DOTFormatter(BaseFormatter):
    """
    DOT formatter for call graph data.
    
    This formatter outputs call graph data in DOT format for use with Graphviz.
    """
    
    def __init__(self, graph_name: str = "CallGraph"):
        """
        Initialize the DOT formatter.
        
        Args:
            graph_name: The name of the graph.
        """
        self.graph_name = graph_name
        
    def format_outbound_calls(self, data: Dict[str, Any]) -> str:
        """
        Format outbound calls data as DOT.
        
        Args:
            data: The outbound calls data to format.
            
        Returns:
            The formatted data as a DOT string.
        """
        result = [f"digraph {self.graph_name} {{"]
        result.append("  node [shape=box, style=filled, fillcolor=lightblue];")
        result.append("  edge [color=black];")
        
        # Process the call graph recursively
        self._process_outbound_node(data, result, set())
        
        result.append("}")
        return "\n".join(result)
        
    def _process_outbound_node(self, node: Dict[str, Any], result: List[str], visited: Set[str]) -> None:
        """
        Process an outbound call graph node recursively.
        
        Args:
            node: The node to process.
            result: The list of DOT lines to append to.
            visited: The set of visited node IDs.
        """
        if not node or "method" not in node:
            return
            
        method = node["method"]
        node_id = method["unique_id"]
        
        # Skip if already visited
        if node_id in visited:
            return
            
        visited.add(node_id)
        
        # Add node
        label = method["name"]
        if method["class_name"]:
            label = f"{method['class_name']}.{label}"
        result.append(f'  "{node_id}" [label="{label}"];')
        
        # Process calls
        for call in node.get("calls", []):
            if "method" in call:
                callee_id = call["method"]["unique_id"]
                result.append(f'  "{node_id}" -> "{callee_id}";')
                self._process_outbound_node(call, result, visited)
                
    def format_inbound_calls(self, data: Dict[str, Any]) -> str:
        """
        Format inbound calls data as DOT.
        
        Args:
            data: The inbound calls data to format.
            
        Returns:
            The formatted data as a DOT string.
        """
        result = [f"digraph {self.graph_name} {{"]
        result.append("  node [shape=box, style=filled, fillcolor=lightblue];")
        result.append("  edge [color=black];")
        
        # Process the call graph recursively
        self._process_inbound_node(data, result, set())
        
        result.append("}")
        return "\n".join(result)
        
    def _process_inbound_node(self, node: Dict[str, Any], result: List[str], visited: Set[str]) -> None:
        """
        Process an inbound call graph node recursively.
        
        Args:
            node: The node to process.
            result: The list of DOT lines to append to.
            visited: The set of visited node IDs.
        """
        if not node or "method" not in node:
            return
            
        method = node["method"]
        node_id = method["unique_id"]
        
        # Skip if already visited
        if node_id in visited:
            return
            
        visited.add(node_id)
        
        # Add node
        label = method["name"]
        if method["class_name"]:
            label = f"{method['class_name']}.{label}"
        result.append(f'  "{node_id}" [label="{label}"];')
        
        # Process called_by
        for caller in node.get("called_by", []):
            if "method" in caller:
                caller_id = caller["method"]["unique_id"]
                result.append(f'  "{caller_id}" -> "{node_id}";')
                self._process_inbound_node(caller, result, visited)
                
    def format_methods(self, methods: List[Dict]) -> str:
        """
        Format methods data as DOT.
        
        Args:
            methods: The methods data to format.
            
        Returns:
            The formatted data as a DOT string.
        """
        result = [f"digraph {self.graph_name} {{"]
        result.append("  node [shape=box, style=filled, fillcolor=lightblue];")
        
        # Add nodes for all methods
        for method in methods:
            node_id = method["unique_id"]
            label = method["name"]
            if method["class_name"]:
                label = f"{method['class_name']}.{label}"
            result.append(f'  "{node_id}" [label="{label}"];')
            
        result.append("}")
        return "\n".join(result)


class TextFormatter(BaseFormatter):
    """
    Text formatter for call graph data.
    
    This formatter outputs call graph data in a human-readable text format.
    """
    
    def format_outbound_calls(self, data: Dict[str, Any]) -> str:
        """
        Format outbound calls data as text.
        
        Args:
            data: The outbound calls data to format.
            
        Returns:
            The formatted data as a text string.
        """
        result = []
        self._format_outbound_node(data, result, 0)
        return "\n".join(result)
        
    def _format_outbound_node(self, node: Dict[str, Any], result: List[str], depth: int) -> None:
        """
        Format an outbound call graph node recursively.
        
        Args:
            node: The node to format.
            result: The list of text lines to append to.
            depth: The current depth in the call graph.
        """
        if not node or "method" not in node:
            return
            
        method = node["method"]
        indent = "  " * depth
        
        # Add method
        name = method["name"]
        if method["class_name"]:
            name = f"{method['class_name']}.{name}"
        result.append(f"{indent}{name} ({method['file_path']}:{method['line_number']})")
        
        # Process calls
        for call in node.get("calls", []):
            self._format_outbound_node(call, result, depth + 1)
            
    def format_inbound_calls(self, data: Dict[str, Any]) -> str:
        """
        Format inbound calls data as text.
        
        Args:
            data: The inbound calls data to format.
            
        Returns:
            The formatted data as a text string.
        """
        result = []
        self._format_inbound_node(data, result, 0)
        return "\n".join(result)
        
    def _format_inbound_node(self, node: Dict[str, Any], result: List[str], depth: int) -> None:
        """
        Format an inbound call graph node recursively.
        
        Args:
            node: The node to format.
            result: The list of text lines to append to.
            depth: The current depth in the call graph.
        """
        if not node or "method" not in node:
            return
            
        method = node["method"]
        indent = "  " * depth
        
        # Add method
        name = method["name"]
        if method["class_name"]:
            name = f"{method['class_name']}.{name}"
        result.append(f"{indent}{name} ({method['file_path']}:{method['line_number']})")
        
        # Process called_by
        for caller in node.get("called_by", []):
            self._format_inbound_node(caller, result, depth + 1)
            
    def format_methods(self, methods: List[Dict]) -> str:
        """
        Format methods data as text.
        
        Args:
            methods: The methods data to format.
            
        Returns:
            The formatted data as a text string.
        """
        result = []
        
        for method in methods:
            name = method["name"]
            if method["class_name"]:
                name = f"{method['class_name']}.{name}"
            result.append(f"{name} ({method['file_path']}:{method['line_number']})")
            
        return "\n".join(result)
