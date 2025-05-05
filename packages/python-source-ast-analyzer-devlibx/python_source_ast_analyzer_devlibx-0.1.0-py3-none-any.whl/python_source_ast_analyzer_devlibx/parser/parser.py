"""
Parser module for Python Source AST Analyzer.

This module contains the Parser class and related data structures for parsing
Python source code and extracting method definitions and calls.
"""

import ast
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union

from .ast_visitor import ASTVisitor
from ..utils import generate_method_id


@dataclass
class MethodDefinition:
    """
    Represents a method definition in Python source code.
    """
    name: str
    module: str
    file_path: str
    class_name: Optional[str]
    line_number: int
    is_async: bool = False
    decorators: List[str] = None
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []
    
    @property
    def unique_id(self) -> str:
        """
        Get a unique identifier for this method.
        
        Returns:
            A unique identifier string.
        """
        return generate_method_id(
            file_path=self.file_path,
            name=self.name,
            line_number=self.line_number,
            class_name=self.class_name,
            with_class_name=True,
            with_file_line=True
        )
    
    @property
    def simple_id(self) -> str:
        """
        Get a simplified identifier for this method.
        
        Returns:
            A simplified identifier string.
        """
        return generate_method_id(
            file_path=self.file_path,
            name=self.name,
            line_number=self.line_number,
            class_name=self.class_name,
            with_class_name=True,
            with_file_line=False
        )
    
    def to_dict(self) -> Dict:
        """
        Convert the method definition to a dictionary.
        
        Returns:
            A dictionary representation of the method definition.
        """
        return {
            "name": self.name,
            "module": self.module,
            "file_path": self.file_path,
            "class_name": self.class_name,
            "line_number": self.line_number,
            "is_async": self.is_async,
            "decorators": self.decorators,
            "unique_id": self.unique_id,
            "simple_id": self.simple_id,
        }


@dataclass
class MethodCall:
    """
    Represents a method call in Python source code.
    """
    caller: MethodDefinition
    callee_name: str
    line_number: int
    
    @property
    def caller_id(self) -> str:
        """
        Get the unique identifier of the caller.
        
        Returns:
            The unique identifier of the caller.
        """
        return self.caller.unique_id
    
    def to_dict(self) -> Dict:
        """
        Convert the method call to a dictionary.
        
        Returns:
            A dictionary representation of the method call.
        """
        return {
            "caller": self.caller.to_dict(),
            "callee_name": self.callee_name,
            "line_number": self.line_number,
            "caller_id": self.caller_id,
        }


class Parser:
    """
    Parser for Python source code.
    
    This class is responsible for parsing Python source code and extracting
    method definitions and calls.
    """
    
    def __init__(self):
        """
        Initialize the parser.
        """
        self.method_definitions: Dict[str, MethodDefinition] = {}
        self.method_calls: List[MethodCall] = []
        
    def parse_file(self, file_path: str, module_name: Optional[str] = None) -> Tuple[List[MethodDefinition], List[MethodCall]]:
        """
        Parse a Python source code file.
        
        Args:
            file_path: The path to the Python source code file.
            module_name: The name of the module being parsed.
            
        Returns:
            A tuple containing the method definitions and method calls.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            SyntaxError: If the file contains invalid Python syntax.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if module_name is None:
            # Extract module name from file path
            module_name = os.path.basename(file_path)
            if module_name.endswith(".py"):
                module_name = module_name[:-3]
                
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
            
        return self.parse_source(source_code, file_path, module_name)
        
    def parse_source(self, source_code: str, file_path: str = "<unknown>", module_name: str = "<unknown>") -> Tuple[List[MethodDefinition], List[MethodCall]]:
        """
        Parse Python source code.
        
        Args:
            source_code: The Python source code to parse.
            file_path: The path to the Python source code file.
            module_name: The name of the module being parsed.
            
        Returns:
            A tuple containing the method definitions and method calls.
            
        Raises:
            SyntaxError: If the source code contains invalid Python syntax.
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {file_path}: {e}")
            
        visitor = ASTVisitor(module_name=module_name, file_path=file_path)
        visitor.visit(tree)
        
        # Convert to MethodDefinition and MethodCall objects
        method_defs = []
        for method_def_dict in visitor.method_definitions:
            method_def = MethodDefinition(
                name=method_def_dict["name"],
                module=method_def_dict["module"],
                file_path=method_def_dict["file_path"],
                class_name=method_def_dict["class_name"],
                line_number=method_def_dict["line_number"],
                is_async=method_def_dict["is_async"],
                decorators=method_def_dict["decorators"],
            )
            method_defs.append(method_def)
            self.method_definitions[method_def.unique_id] = method_def
            
        method_calls = []
        for method_call_dict in visitor.method_calls:
            caller_dict = method_call_dict["caller"]
            caller = MethodDefinition(
                name=caller_dict["name"],
                module=caller_dict["module"],
                file_path=caller_dict["file_path"],
                class_name=caller_dict["class_name"],
                line_number=caller_dict["line_number"],
                is_async=caller_dict.get("is_async", False),
                decorators=caller_dict.get("decorators", []),
            )
            method_call = MethodCall(
                caller=caller,
                callee_name=method_call_dict["callee_name"],
                line_number=method_call_dict["line_number"],
            )
            method_calls.append(method_call)
            self.method_calls.append(method_call)
            
        return method_defs, method_calls
        
    def parse_directory(self, directory_path: str, recursive: bool = True) -> Tuple[List[MethodDefinition], List[MethodCall]]:
        """
        Parse all Python source code files in a directory.
        
        Args:
            directory_path: The path to the directory.
            recursive: Whether to recursively parse subdirectories.
            
        Returns:
            A tuple containing the method definitions and method calls.
            
        Raises:
            FileNotFoundError: If the directory does not exist.
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"Not a directory: {directory_path}")
            
        method_defs = []
        method_calls = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        defs, calls = self.parse_file(file_path)
                        method_defs.extend(defs)
                        method_calls.extend(calls)
                    except (SyntaxError, UnicodeDecodeError) as e:
                        print(f"Error parsing {file_path}: {e}")
                        
            if not recursive:
                break
                
        return method_defs, method_calls
        
    def get_method_definitions(self) -> List[MethodDefinition]:
        """
        Get all method definitions.
        
        Returns:
            A list of method definitions.
        """
        return list(self.method_definitions.values())
        
    def get_method_calls(self) -> List[MethodCall]:
        """
        Get all method calls.
        
        Returns:
            A list of method calls.
        """
        return self.method_calls
