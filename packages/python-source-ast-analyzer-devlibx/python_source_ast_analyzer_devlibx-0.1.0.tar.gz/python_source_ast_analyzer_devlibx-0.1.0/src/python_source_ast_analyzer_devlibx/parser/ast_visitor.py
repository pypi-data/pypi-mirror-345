"""
AST Visitor for Python Source AST Analyzer.

This module implements a visitor for traversing Python AST nodes and extracting
method definitions and calls.
"""

import ast
from typing import Dict, List, Optional, Set, Tuple


class ASTVisitor(ast.NodeVisitor):
    """
    AST visitor that traverses Python AST nodes to extract method definitions and calls.
    
    This visitor implements the visitor pattern for AST traversal and collects
    information about method definitions and calls.
    """
    
    def __init__(self, module_name: str = "<unknown>", file_path: str = "<unknown>"):
        """
        Initialize the AST visitor.
        
        Args:
            module_name: The name of the module being parsed.
            file_path: The path of the file being parsed.
        """
        self.module_name = module_name
        self.file_path = file_path
        self.current_class: Optional[str] = None
        self.current_function: Optional[Dict] = None
        self.function_stack: List[Dict] = []
        
        # Store method definitions and calls
        self.method_definitions: List[Dict] = []
        self.method_calls: List[Dict] = []
        
        # Track imported names
        self.imports: Dict[str, str] = {}
        self.from_imports: Dict[str, Dict[str, str]] = {}
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Visit a class definition node.
        
        Args:
            node: The AST node representing a class definition.
        """
        old_class = self.current_class
        self.current_class = node.name
        
        # Visit all child nodes
        self.generic_visit(node)
        
        # Restore the previous class context
        self.current_class = old_class
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Visit a function definition node.
        
        Args:
            node: The AST node representing a function definition.
        """
        self._process_function_def(node)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """
        Visit an async function definition node.
        
        Args:
            node: The AST node representing an async function definition.
        """
        self._process_function_def(node, is_async=True)
        
    def _process_function_def(self, node: ast.FunctionDef, is_async: bool = False) -> None:
        """
        Process a function definition node.
        
        Args:
            node: The AST node representing a function definition.
            is_async: Whether the function is async.
        """
        # Create a function definition record
        function_def = {
            "name": node.name,
            "module": self.module_name,
            "file_path": self.file_path,
            "class_name": self.current_class,
            "line_number": node.lineno,
            "is_async": is_async,
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
        }
        
        # Add to method definitions
        self.method_definitions.append(function_def)
        
        # Update current function context
        old_function = self.current_function
        self.current_function = function_def
        self.function_stack.append(function_def)
        
        # Visit all child nodes
        self.generic_visit(node)
        
        # Restore the previous function context
        self.function_stack.pop()
        self.current_function = old_function if self.function_stack else None
        
    def _get_decorator_name(self, node: ast.expr) -> str:
        """
        Get the name of a decorator.
        
        Args:
            node: The AST node representing a decorator.
            
        Returns:
            The name of the decorator.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_decorator_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return str(ast.dump(node))
        
    def visit_Call(self, node: ast.Call) -> None:
        """
        Visit a function call node.
        
        Args:
            node: The AST node representing a function call.
        """
        if self.current_function is None:
            # Skip calls outside of functions
            self.generic_visit(node)
            return
            
        # Get the name of the called function
        callee_name = self._get_call_name(node)
        
        if callee_name:
            # Create a method call record
            method_call = {
                "caller": self.current_function,
                "callee_name": callee_name,
                "line_number": node.lineno,
            }
            
            # Add to method calls
            self.method_calls.append(method_call)
            
        # Visit all child nodes
        self.generic_visit(node)
        
    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        """
        Get the name of a function call.
        
        Args:
            node: The AST node representing a function call.
            
        Returns:
            The name of the called function, or None if it cannot be determined.
        """
        func = node.func
        
        if isinstance(func, ast.Name):
            # Simple function call: func()
            # Check if this is an imported name
            resolved_name = self._resolve_imported_name(func.id)
            if resolved_name:
                return resolved_name
                
            return func.id
        elif isinstance(func, ast.Attribute):
            # Method call: obj.method()
            if isinstance(func.value, ast.Name):
                # Simple attribute: obj.method()
                obj_name = func.value.id
                
                # Check if the object is an imported module
                resolved_obj = self._resolve_imported_name(obj_name)
                if resolved_obj:
                    return f"{resolved_obj}.{func.attr}"
                    
                return f"{obj_name}.{func.attr}"
            else:
                # Complex attribute: obj.attr.method()
                complex_attr = self._get_complex_attribute(func.value)
                return f"{complex_attr}.{func.attr}"
        
        return None
        
    def _get_complex_attribute(self, node: ast.expr) -> str:
        """
        Get the name of a complex attribute.
        
        Args:
            node: The AST node representing a complex attribute.
            
        Returns:
            The name of the complex attribute.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_complex_attribute(node.value)}.{node.attr}"
        
        return str(ast.dump(node))
        
    def visit_Import(self, node: ast.Import) -> None:
        """
        Visit an import node.
        
        Args:
            node: The AST node representing an import statement.
        """
        for name in node.names:
            asname = name.asname or name.name
            self.imports[asname] = name.name
            
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Visit an import from node.
        
        Args:
            node: The AST node representing an import from statement.
        """
        if node.module not in self.from_imports:
            self.from_imports[node.module] = {}
            
        for name in node.names:
            asname = name.asname or name.name
            self.from_imports[node.module][asname] = name.name
                
        self.generic_visit(node)
        
    def _resolve_imported_name(self, name: str) -> Optional[str]:
        """
        Resolve an imported name to its full module path.
        
        Args:
            name: The name to resolve.
            
        Returns:
            The full module path, or None if not found.
        """
        # Check direct imports
        if name in self.imports:
            return self.imports[name]
            
        # Check from imports
        for module, imports in self.from_imports.items():
            if name in imports:
                return f"{module}.{imports[name]}"
                
        return None
