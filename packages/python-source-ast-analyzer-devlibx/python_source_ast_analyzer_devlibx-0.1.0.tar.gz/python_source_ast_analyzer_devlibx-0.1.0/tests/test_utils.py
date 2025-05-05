"""
Tests for utility functions.

This module contains tests for the utility functions in the utils module.
"""

import os
import unittest
from src.python_source_ast_analyzer_devlibx.utils import get_relative_path, generate_method_id


class TestUtils(unittest.TestCase):
    """
    Tests for utility functions.
    """
    
    def test_get_relative_path_with_app_prefix(self):
        """
        Test get_relative_path with a file in the app directory.
        """
        # Test with a file in the app directory
        file_path = "/tmp/project_backend_main/app/api/routes.py"
        project_root = "/tmp/project_backend_main"
        
        # The result should include the app prefix
        expected = "app/api/routes.py"
        result = get_relative_path(file_path, project_root)
        
        self.assertEqual(result, expected)
        
    def test_get_relative_path_auto_detect_project_root(self):
        """
        Test get_relative_path with auto-detection of project root.
        """
        # Test with a file in the app directory, without specifying project root
        file_path = "/tmp/project_backend_main/app/api/routes.py"
        
        # The function should detect that 'app' is a common project structure indicator
        # and use /tmp/project_backend_main as the project root
        expected = "app/api/routes.py"
        result = get_relative_path(file_path)
        
        self.assertEqual(result, expected)
        
    def test_get_relative_path_respect_provided_root(self):
        """
        Test get_relative_path respects the provided project root.
        """
        # Test with a custom project root that doesn't match common patterns
        file_path = "/custom/path/to/project/some/module/file.py"
        project_root = "/custom/path/to/project"
        
        # The function should use the provided project root directly
        expected = "some/module/file.py"
        result = get_relative_path(file_path, project_root)
        
        self.assertEqual(result, expected)
        
    def test_get_relative_path_with_src_prefix(self):
        """
        Test get_relative_path with a file in the src directory.
        """
        # Test with a file in the src directory
        file_path = "/tmp/project/src/module/file.py"
        project_root = "/tmp/project"
        
        # The result should include the src prefix
        expected = "src/module/file.py"
        result = get_relative_path(file_path, project_root)
        
        self.assertEqual(result, expected)
        
    def test_get_relative_path_no_common_prefix(self):
        """
        Test get_relative_path with a file not in a common project structure.
        """
        # Test with a file not in a common project structure
        file_path = "/tmp/project/module/file.py"
        project_root = "/tmp/project"
        
        # The result should be the relative path from the project root
        expected = "module/file.py"
        result = get_relative_path(file_path, project_root)
        
        self.assertEqual(result, expected)
        
    def test_get_relative_path_outside_project_root(self):
        """
        Test get_relative_path with a file outside the project root.
        """
        # Test with a file outside the project root
        file_path = "/tmp/other/file.py"
        project_root = "/tmp/project"
        
        # The result should be just the file name
        expected = "file.py"
        result = get_relative_path(file_path, project_root)
        
        self.assertEqual(result, expected)
        
    def test_generate_method_id_with_file_line(self):
        """
        Test generate_method_id with file path and line number.
        """
        # Test with file path and line number
        file_path = "/tmp/project_backend_main/app/api/routes.py"
        name = "add_highlight"
        line_number = 439
        
        # The result should include the relative path, method name, and line number
        expected = "app/api/routes.py#add_highlight#439"
        result = generate_method_id(file_path, name, line_number)
        
        self.assertEqual(result, expected)
        
    def test_generate_method_id_with_class_name(self):
        """
        Test generate_method_id with class name.
        """
        # Test with class name
        file_path = "/tmp/project_backend_main/app/api/routes.py"
        name = "add_highlight"
        line_number = 439
        class_name = "HighlightService"
        
        # The result should include the relative path, class name, method name, and line number
        expected = "app/api/routes.py#HighlightService.add_highlight#439"
        result = generate_method_id(file_path, name, line_number, class_name)
        
        self.assertEqual(result, expected)
        
    def test_generate_method_id_without_file_line(self):
        """
        Test generate_method_id without file path and line number.
        """
        # Test without file path and line number
        file_path = "/tmp/project_backend_main/app/api/routes.py"
        name = "add_highlight"
        line_number = 439
        
        # The result should be just the method name
        expected = "add_highlight"
        result = generate_method_id(file_path, name, line_number, with_file_line=False)
        
        self.assertEqual(result, expected)
        
    def test_generate_method_id_with_class_name_without_file_line(self):
        """
        Test generate_method_id with class name but without file path and line number.
        """
        # Test with class name but without file path and line number
        file_path = "/tmp/project_backend_main/app/api/routes.py"
        name = "add_highlight"
        line_number = 439
        class_name = "HighlightService"
        
        # The result should include the class name and method name
        expected = "HighlightService.add_highlight"
        result = generate_method_id(file_path, name, line_number, class_name, with_file_line=False)
        
        self.assertEqual(result, expected)
        
    def test_generate_method_id_without_class_name(self):
        """
        Test generate_method_id without class name.
        """
        # Test without class name
        file_path = "/tmp/project_backend_main/app/api/routes.py"
        name = "add_highlight"
        line_number = 439
        class_name = "HighlightService"
        
        # The result should include the relative path, method name, and line number
        expected = "app/api/routes.py#add_highlight#439"
        result = generate_method_id(file_path, name, line_number, class_name, with_class_name=False)
        
        self.assertEqual(result, expected)
        
    def test_generate_method_id_with_custom_project_root(self):
        """
        Test generate_method_id with a custom project root.
        """
        # Test with a custom project root
        file_path = "/custom/path/to/project/some/module/file.py"
        name = "process_data"
        line_number = 123
        project_root = "/custom/path/to/project"
        
        # The result should use the relative path from the provided project root
        expected = "some/module/file.py#process_data#123"
        result = generate_method_id(file_path, name, line_number, project_root=project_root)
        
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
