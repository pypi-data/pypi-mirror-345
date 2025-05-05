"""
Utility functions for Python Source AST Analyzer.

This module contains utility functions used throughout the package.
"""

import os
from typing import Optional


def get_relative_path(file_path: str, project_root: Optional[str] = None) -> str:
    """
    Get the relative path from the project root.
    
    Args:
        file_path: The absolute file path.
        project_root: The project root directory. If None, it will be inferred from the file path.
        
    Returns:
        The relative path from the project root.
    """
    if not file_path:
        return ""
    
    # Normalize path separators
    file_path = os.path.normpath(file_path)
    
    # If project_root is provided, use it directly
    if project_root is None:
        # If no project_root is provided, try to infer it
        
        # Check for common patterns in the path
        path_parts = file_path.split(os.sep)
        
        # Look for common project structure indicators
        app_index = -1
        for i, part in enumerate(path_parts):
            if part in ["app", "src", "lib", "source"]:
                app_index = i
                break
        
        if app_index >= 0:
            # Use the directory containing the app/src/lib directory as the project root
            project_root = os.sep.join(path_parts[:app_index])
        else:
            # Infer project root as the parent directory of the parent directory of the file
            project_root = os.path.dirname(os.path.dirname(file_path))
    
    # Get the relative path from the project root
    if file_path.startswith(project_root):
        return os.path.relpath(file_path, project_root)
    else:
        # If the file is not in the project root, use the file name
        return os.path.basename(file_path)


def generate_method_id(file_path: str, name: str, line_number: int, 
                      class_name: Optional[str] = None, 
                      with_class_name: bool = True,
                      with_file_line: bool = True,
                      project_root: Optional[str] = None) -> str:
    """
    Generate a method identifier.
    
    Args:
        file_path: The absolute file path.
        name: The method name.
        line_number: The line number.
        class_name: The class name, if any.
        with_class_name: Whether to include the class name in the identifier.
        with_file_line: Whether to include the file path and line number in the identifier.
        project_root: The project root directory. If None, it will be inferred from the file path.
        
    Returns:
        A method identifier string.
    """
    if with_file_line:
        relative_path = get_relative_path(file_path, project_root)
        if with_class_name and class_name:
            return f"{relative_path}#{class_name}.{name}#{line_number}"
        return f"{relative_path}#{name}#{line_number}"
    elif with_class_name and class_name:
        return f"{class_name}.{name}"
    else:
        return name
