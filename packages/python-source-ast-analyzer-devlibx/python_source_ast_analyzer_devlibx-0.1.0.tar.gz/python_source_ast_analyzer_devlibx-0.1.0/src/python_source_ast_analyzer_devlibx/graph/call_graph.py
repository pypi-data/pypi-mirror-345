"""
Call Graph module for Python Source AST Analyzer.

This module contains the CallGraph class for representing and querying call relationships.
"""

from typing import Dict, List, Optional, Set, Tuple, Any

from ..parser.parser import MethodDefinition, MethodCall


class CallGraph:
    """
    Represents a call graph of methods.
    
    This class provides functionality to build and query a call graph of methods.
    """
    
    def __init__(self):
        """
        Initialize the call graph.
        """
        # Maps method unique IDs to method definitions
        self.methods: Dict[str, MethodDefinition] = {}
        
        # Maps method unique IDs to sets of method unique IDs that they call
        self.outbound_calls: Dict[str, Set[str]] = {}
        
        # Maps method unique IDs to sets of method unique IDs that call them
        self.inbound_calls: Dict[str, Set[str]] = {}
        
        # Maps callee names to sets of method unique IDs
        self.callee_name_to_methods: Dict[str, Set[str]] = {}
        
    def add_method(self, method: MethodDefinition) -> None:
        """
        Add a method to the call graph.
        
        Args:
            method: The method to add.
        """
        self.methods[method.unique_id] = method
        
        # Initialize call sets if they don't exist
        if method.unique_id not in self.outbound_calls:
            self.outbound_calls[method.unique_id] = set()
            
        if method.unique_id not in self.inbound_calls:
            self.inbound_calls[method.unique_id] = set()
            
        # Add to callee name mapping
        if method.simple_id not in self.callee_name_to_methods:
            self.callee_name_to_methods[method.simple_id] = set()
        self.callee_name_to_methods[method.simple_id].add(method.unique_id)
        
    def add_call(self, call: MethodCall) -> None:
        """
        Add a method call to the call graph.
        
        Args:
            call: The method call to add.
        """
        caller_id = call.caller_id
        
        # Add caller if it doesn't exist
        if caller_id not in self.methods:
            self.add_method(call.caller)
            
        # Find potential callees
        callee_name = call.callee_name
        callee_ids = self.callee_name_to_methods.get(callee_name, set())
        
        # If no direct match, try to match by the method name part
        if not callee_ids and "." in callee_name:
            # Extract the method name from the full name (e.g., "module.submodule.method" -> "method")
            method_name = callee_name.split(".")[-1]
            
            # Look for methods with this name
            for key, ids in self.callee_name_to_methods.items():
                if key == method_name or key.endswith("." + method_name):
                    callee_ids.update(ids)
        
        # If no callees found, this might be a call to an external library
        # or a method that hasn't been defined yet
        if not callee_ids:
            return
            
        # Add call relationships
        for callee_id in callee_ids:
            # Prevent self-calls (cycles)
            if callee_id != caller_id:
                self.outbound_calls[caller_id].add(callee_id)
                self.inbound_calls[callee_id].add(caller_id)
            
    def get_outbound_calls(self, method_id: str, depth: int = 1, visited: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Get all methods called by a specific method.
        
        Args:
            method_id: The unique ID of the method.
            depth: The depth of the call graph to traverse.
            visited: Set of already visited method IDs to prevent cycles.
            
        Returns:
            A dictionary representing the outbound call graph.
        """
        if method_id not in self.methods:
            return {}
            
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
            
        # Check if we've already visited this method
        if method_id in visited:
            return {}

        # Add current method to visited set
        visited.add(method_id)

        method = self.methods[method_id]
        result = {
            "method": method.to_dict(),
            "calls": []
        }
        
        if depth <= 0:
            return result
            
        for callee_id in self.outbound_calls.get(method_id, set()):
            if callee_id in self.methods and callee_id != method_id:  # Skip self-calls
                callee_result = self.get_outbound_calls(callee_id, depth - 1, visited.copy())
                if callee_result:  # Only add non-empty results
                    result["calls"].append(callee_result)
                
        return result
        
    def get_inbound_calls(self, method_id: str, depth: int = 1, visited: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Get all methods that call a specific method.
        
        Args:
            method_id: The unique ID of the method.
            depth: The depth of the call graph to traverse.
            visited: Set of already visited method IDs to prevent cycles.
            
        Returns:
            A dictionary representing the inbound call graph.
        """
        if method_id not in self.methods:
            return {}
            
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
            
        # Check if we've already visited this method
        if method_id in visited:
            return {}
            
        # Add current method to visited set
        visited.add(method_id)
            
        method = self.methods[method_id]
        result = {
            "method": method.to_dict(),
            "called_by": []
        }
        
        if depth <= 0:
            return result
            
        for caller_id in self.inbound_calls.get(method_id, set()):
            if caller_id in self.methods and caller_id != method_id:  # Skip self-calls
                caller_result = self.get_inbound_calls(caller_id, depth - 1, visited.copy())
                if caller_result:  # Only add non-empty results
                    result["called_by"].append(caller_result)
                
        return result
        
    def get_flat_outbound_calls(self, method_id: str, depth: int = 1) -> List[Dict]:
        """
        Get all methods called by a specific method in a flat list.
        
        Args:
            method_id: The unique ID of the method.
            depth: The depth of the call graph to traverse.
            
        Returns:
            A list of method dictionaries.
        """
        if method_id not in self.methods:
            return []
            
        result = []
        visited = set()
        
        def traverse(current_id: str, current_depth: int) -> None:
            if current_depth <= 0 or current_id in visited:
                return
                
            visited.add(current_id)
            
            for callee_id in self.outbound_calls.get(current_id, set()):
                if callee_id in self.methods and callee_id != current_id:  # Skip self-calls
                    result.append(self.methods[callee_id].to_dict())
                    traverse(callee_id, current_depth - 1)
                    
        traverse(method_id, depth)
        return result
        
    def get_flat_inbound_calls(self, method_id: str, depth: int = 1) -> List[Dict]:
        """
        Get all methods that call a specific method in a flat list.
        
        Args:
            method_id: The unique ID of the method.
            depth: The depth of the call graph to traverse.
            
        Returns:
            A list of method dictionaries.
        """
        if method_id not in self.methods:
            return []
            
        result = []
        visited = set()
        
        def traverse(current_id: str, current_depth: int) -> None:
            if current_depth <= 0 or current_id in visited:
                return
                
            visited.add(current_id)
            
            for caller_id in self.inbound_calls.get(current_id, set()):
                if caller_id in self.methods and caller_id != current_id:  # Skip self-calls
                    result.append(self.methods[caller_id].to_dict())
                    traverse(caller_id, current_depth - 1)
                    
        traverse(method_id, depth)
        return result
        
    def get_all_methods(self) -> List[Dict]:
        """
        Get all methods in the call graph.
        
        Returns:
            A list of method dictionaries.
        """
        return [method.to_dict() for method in self.methods.values()]
        
    def get_method_by_id(self, method_id: str) -> Optional[MethodDefinition]:
        """
        Get a method by its unique ID.
        
        Args:
            method_id: The unique ID of the method.
            
        Returns:
            The method definition, or None if not found.
        """
        return self.methods.get(method_id)
        
    def get_methods_by_name(self, name: str) -> List[MethodDefinition]:
        """
        Get methods by name.
        
        Args:
            name: The name of the method.
            
        Returns:
            A list of method definitions.
        """
        return [method for method in self.methods.values() if method.name == name]
        
    def get_methods_by_class(self, class_name: str) -> List[MethodDefinition]:
        """
        Get methods by class name.
        
        Args:
            class_name: The name of the class.
            
        Returns:
            A list of method definitions.
        """
        return [method for method in self.methods.values() if method.class_name == class_name]
        
    def get_methods_by_file(self, file_path: str) -> List[MethodDefinition]:
        """
        Get methods by file path.
        
        Args:
            file_path: The path of the file.
            
        Returns:
            A list of method definitions.
        """
        return [method for method in self.methods.values() if method.file_path == file_path]
