"""
Graph Builder module for Python Source AST Analyzer.

This module contains the GraphBuilder class for building call graphs from parsed Python code.
"""

from typing import Dict, List, Optional, Set, Tuple, Any

from ..parser.parser import Parser, MethodDefinition, MethodCall
from .call_graph import CallGraph


class GraphBuilder:
    """
    Builds a call graph from parsed Python code.
    
    This class is responsible for building a call graph from parsed Python code.
    """
    
    def __init__(self, parser: Optional[Parser] = None):
        """
        Initialize the graph builder.
        
        Args:
            parser: The parser to use for parsing Python code.
        """
        self.parser = parser or Parser()
        self.call_graph = CallGraph()
        
    def build_from_file(self, file_path: str, module_name: Optional[str] = None) -> CallGraph:
        """
        Build a call graph from a Python source code file.
        
        Args:
            file_path: The path to the Python source code file.
            module_name: The name of the module being parsed.
            
        Returns:
            The built call graph.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            SyntaxError: If the file contains invalid Python syntax.
        """
        method_defs, method_calls = self.parser.parse_file(file_path, module_name)
        
        # Add methods to the call graph
        for method_def in method_defs:
            self.call_graph.add_method(method_def)
            
        # Add calls to the call graph
        for method_call in method_calls:
            self.call_graph.add_call(method_call)
            
        return self.call_graph
        
    def build_from_directory(self, directory_path: str, recursive: bool = True) -> CallGraph:
        """
        Build a call graph from all Python source code files in a directory.
        
        Args:
            directory_path: The path to the directory.
            recursive: Whether to recursively parse subdirectories.
            
        Returns:
            The built call graph.
            
        Raises:
            FileNotFoundError: If the directory does not exist.
        """
        method_defs, method_calls = self.parser.parse_directory(directory_path, recursive)
        
        # Add methods to the call graph
        for method_def in method_defs:
            self.call_graph.add_method(method_def)
            
        # Add calls to the call graph
        for method_call in method_calls:
            self.call_graph.add_call(method_call)
            
        return self.call_graph
        
    def build_from_source(self, source_code: str, file_path: str = "<unknown>", module_name: str = "<unknown>") -> CallGraph:
        """
        Build a call graph from Python source code.
        
        Args:
            source_code: The Python source code to parse.
            file_path: The path to the Python source code file.
            module_name: The name of the module being parsed.
            
        Returns:
            The built call graph.
            
        Raises:
            SyntaxError: If the source code contains invalid Python syntax.
        """
        method_defs, method_calls = self.parser.parse_source(source_code, file_path, module_name)
        
        # Add methods to the call graph
        for method_def in method_defs:
            self.call_graph.add_method(method_def)
            
        # Add calls to the call graph
        for method_call in method_calls:
            self.call_graph.add_call(method_call)
            
        return self.call_graph
        
    def get_call_graph(self) -> CallGraph:
        """
        Get the built call graph.
        
        Returns:
            The built call graph.
        """
        return self.call_graph
