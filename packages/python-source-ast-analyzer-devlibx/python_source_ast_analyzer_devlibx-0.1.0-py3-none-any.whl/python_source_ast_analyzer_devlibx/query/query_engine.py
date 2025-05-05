"""
Query Engine module for Python Source AST Analyzer.

This module contains the QueryEngine class for querying call graphs.
"""

from typing import Dict, List, Optional, Set, Tuple, Any

from ..graph.call_graph import CallGraph
from ..parser.parser import MethodDefinition


class QueryEngine:
    """
    Query engine for call graphs.
    
    This class provides functionality to query call graphs for specific information.
    """
    
    def __init__(self, call_graph: CallGraph):
        """
        Initialize the query engine.
        
        Args:
            call_graph: The call graph to query.
        """
        self.call_graph = call_graph
        
    def get_outbound_calls(self, method_id: str, depth: int = 1, flat: bool = False) -> Dict[str, Any]:
        """
        Get all methods called by a specific method.
        
        Args:
            method_id: The unique ID of the method.
            depth: The depth of the call graph to traverse.
            flat: Whether to return a flat list of methods or a nested call graph.
            
        Returns:
            A dictionary representing the outbound call graph or a list of methods.
        """
        if flat:
            return self.call_graph.get_flat_outbound_calls(method_id, depth)
        return self.call_graph.get_outbound_calls(method_id, depth)
        
    def get_inbound_calls(self, method_id: str, depth: int = 1, flat: bool = False) -> Dict[str, Any]:
        """
        Get all methods that call a specific method.
        
        Args:
            method_id: The unique ID of the method.
            depth: The depth of the call graph to traverse.
            flat: Whether to return a flat list of methods or a nested call graph.
            
        Returns:
            A dictionary representing the inbound call graph or a list of methods.
        """
        if flat:
            return self.call_graph.get_flat_inbound_calls(method_id, depth)
        return self.call_graph.get_inbound_calls(method_id, depth)
        
    def find_methods_by_name(self, name: str) -> List[MethodDefinition]:
        """
        Find methods by name.
        
        Args:
            name: The name of the method.
            
        Returns:
            A list of method definitions.
        """
        return self.call_graph.get_methods_by_name(name)
        
    def find_methods_by_class(self, class_name: str) -> List[MethodDefinition]:
        """
        Find methods by class name.
        
        Args:
            class_name: The name of the class.
            
        Returns:
            A list of method definitions.
        """
        return self.call_graph.get_methods_by_class(class_name)
        
    def find_methods_by_file(self, file_path: str) -> List[MethodDefinition]:
        """
        Find methods by file path.
        
        Args:
            file_path: The path of the file.
            
        Returns:
            A list of method definitions.
        """
        return self.call_graph.get_methods_by_file(file_path)
        
    def find_methods_by_decorator(self, decorator_name: str) -> List[MethodDefinition]:
        """
        Find methods by decorator name.
        
        Args:
            decorator_name: The name of the decorator.
            
        Returns:
            A list of method definitions.
        """
        result = []
        for method in self.call_graph.get_all_methods():
            method_def = self.call_graph.get_method_by_id(method["unique_id"])
            if method_def and any(decorator_name in decorator for decorator in method_def.decorators):
                result.append(method_def)
        return result
        
    def find_route_handlers(self) -> List[MethodDefinition]:
        """
        Find route handler methods (Flask or FastAPI).
        
        Returns:
            A list of method definitions.
        """
        # Common route decorators in Flask and FastAPI
        route_decorators = [
            "route", "get", "post", "put", "delete", "patch", "options", "head",
            "app.route", "app.get", "app.post", "app.put", "app.delete", "app.patch", "app.options", "app.head",
            "blueprint.route", "blueprint.get", "blueprint.post", "blueprint.put", "blueprint.delete", "blueprint.patch",
            "APIRouter.route", "APIRouter.get", "APIRouter.post", "APIRouter.put", "APIRouter.delete", "APIRouter.patch",
        ]
        
        result = []
        for method in self.call_graph.get_all_methods():
            method_def = self.call_graph.get_method_by_id(method["unique_id"])
            if method_def:
                for decorator in method_def.decorators:
                    if any(route_decorator in decorator for route_decorator in route_decorators):
                        result.append(method_def)
                        break
        return result
        
    def get_all_methods(self) -> List[Dict]:
        """
        Get all methods in the call graph.
        
        Returns:
            A list of method dictionaries.
        """
        return self.call_graph.get_all_methods()
