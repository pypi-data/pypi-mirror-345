"""
Test module for the Parser class using a sample Flask application.

This module tests the Parser's ability to extract method definitions and calls
from a sample Flask application.
"""

import os
import unittest
from typing import Dict, List, Tuple

from python_source_ast_analyzer_devlibx.parser.parser import Parser, MethodDefinition, MethodCall


class TestParserWithFlaskApp(unittest.TestCase):
    """
    Test case for the Parser class using a sample Flask application.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        self.parser = Parser()
        
        # Path to the sample Flask application
        self.sample_file_path = os.path.join(os.path.dirname(__file__), "sample_flask_app", "sample_flask_app.py")
        
        # Read the sample file content
        with open(self.sample_file_path, "r", encoding="utf-8") as f:
            self.sample_code = f.read()
            
    def test_build_from_file(self):
        """
        Test the build_from_file method with the sample Flask application.
        """
        # Parse the sample file
        method_defs, method_calls = self.parser.parse_file(self.sample_file_path)
        
        # Verify that we have the expected number of method definitions
        self.assertEqual(len(method_defs), 11, "Expected 11 method definitions")
        
        # Verify that we have method calls
        self.assertGreater(len(method_calls), 0, "Expected at least one method call")
        
        # Verify that the module name was correctly extracted from the file path
        module_name = os.path.basename(self.sample_file_path)[:-3]  # Remove .py extension
        for method_def in method_defs:
            self.assertEqual(method_def.module, module_name, 
                           f"Expected module name '{module_name}' for method {method_def.name}")
        
        # Verify that we found the route handlers
        route_handlers = [m for m in method_defs if any("app.route" in d for d in m.decorators)]
        self.assertEqual(len(route_handlers), 2, "Expected 2 route handlers")
        
        # Verify that we found the async functions
        async_functions = [m for m in method_defs if m.is_async]
        self.assertEqual(len(async_functions), 2, "Expected 2 async functions")
        
        # Verify that we found the class methods
        class_methods = [m for m in method_defs if m.class_name is not None]
        self.assertEqual(len(class_methods), 5, "Expected 5 class methods")
        
        # Verify that the file path is correctly set
        for method_def in method_defs:
            self.assertEqual(method_def.file_path, self.sample_file_path, 
                           f"Expected file path '{self.sample_file_path}' for method {method_def.name}")
            
    def test_parse_source(self):
        """
        Test the parse_source method with the sample Flask application.
        """
        # Parse the sample code
        method_defs, method_calls = self.parser.parse_source(
            self.sample_code, 
            self.sample_file_path, 
            "sample_flask_app"
        )
        
        # Verify that we have the expected number of method definitions
        # The sample file has:
        # - 5 regular functions (process_data, validate_data, get_data, initialize_app, enhance_result)
        # - 1 async function (process_request)
        # - 2 methods in DataUtility class (clean_data, format_response)
        # - 3 methods in ConfigManager class (__init__, get_config, update_config)
        # Total: 11 method definitions
        self.assertEqual(len(method_defs), 11, "Expected 11 method definitions")
        
        # Verify that we have method calls
        self.assertGreater(len(method_calls), 0, "Expected at least one method call")
        
        # Verify that we found the route handlers
        route_handlers = [m for m in method_defs if any("app.route" in d for d in m.decorators)]
        self.assertEqual(len(route_handlers), 2, "Expected 2 route handlers")
        
        # Verify the route handler names
        route_handler_names = {m.name for m in route_handlers}
        self.assertSetEqual(route_handler_names, {"get_data", "process_request"}, 
                           "Expected route handlers named 'get_data' and 'process_request'")
        
        # Verify that we found the async function
        async_functions = [m for m in method_defs if m.is_async]
        self.assertEqual(len(async_functions), 2, "Expected 2 async functions")
        
        # Verify the async function names
        async_function_names = {m.name for m in async_functions}
        self.assertSetEqual(async_function_names, {"process_request", "enhance_result"}, 
                           "Expected async functions named 'process_request' and 'enhance_result'")
        
        # Verify that we found the class methods
        class_methods = [m for m in method_defs if m.class_name is not None]
        self.assertEqual(len(class_methods), 5, "Expected 5 class methods")
        
        # Verify the class names
        class_names = {m.class_name for m in class_methods}
        self.assertSetEqual(class_names, {"DataUtility", "ConfigManager"}, 
                           "Expected classes named 'DataUtility' and 'ConfigManager'")
        
        # Verify specific method calls
        # Find the get_data method
        get_data_method = next((m for m in method_defs if m.name == "get_data"), None)
        self.assertIsNotNone(get_data_method, "Expected to find 'get_data' method")
        
        # Find calls from get_data
        get_data_calls = [c for c in method_calls if c.caller_id == get_data_method.unique_id]
        self.assertGreaterEqual(len(get_data_calls), 2, 
                              "Expected at least 2 calls from 'get_data' method")
        
        # Verify that get_data calls process_data and DataUtility.format_response
        get_data_callee_names = {c.callee_name for c in get_data_calls}
        self.assertIn("process_data", get_data_callee_names, 
                     "Expected 'get_data' to call 'process_data'")
        self.assertIn("DataUtility.format_response", get_data_callee_names, 
                     "Expected 'get_data' to call 'DataUtility.format_response'")
        
    def test_method_definition_properties(self):
        """
        Test the properties of MethodDefinition objects.
        """
        # Parse the sample code
        method_defs, _ = self.parser.parse_source(
            self.sample_code, 
            self.sample_file_path, 
            "sample_flask_app"
        )
        
        # Find a regular function
        process_data = next((m for m in method_defs if m.name == "process_data"), None)
        self.assertIsNotNone(process_data, "Expected to find 'process_data' method")
        
        # Verify its properties
        self.assertEqual(process_data.module, "sample_flask_app")
        self.assertEqual(process_data.file_path, self.sample_file_path)
        self.assertIsNone(process_data.class_name)
        self.assertFalse(process_data.is_async)
        self.assertEqual(process_data.decorators, [])
        
        # Verify unique_id and simple_id
        # Get the relative path from the test directory
        test_dir = os.path.dirname(__file__)
        rel_path = os.path.relpath(self.sample_file_path, os.path.dirname(test_dir))
        self.assertEqual(process_data.unique_id, f"{rel_path}#process_data#{process_data.line_number}")
        self.assertEqual(process_data.simple_id, "process_data")
        
        # Find a class method
        clean_data = next((m for m in method_defs if m.name == "clean_data"), None)
        self.assertIsNotNone(clean_data, "Expected to find 'clean_data' method")
        
        # Verify its properties
        self.assertEqual(clean_data.module, "sample_flask_app")
        self.assertEqual(clean_data.file_path, self.sample_file_path)
        self.assertEqual(clean_data.class_name, "DataUtility")
        self.assertFalse(clean_data.is_async)
        self.assertIn("staticmethod", clean_data.decorators)
        
        # Verify unique_id and simple_id
        self.assertEqual(clean_data.unique_id, 
                        f"{rel_path}#DataUtility.clean_data#{clean_data.line_number}")
        self.assertEqual(clean_data.simple_id, "DataUtility.clean_data")
        
        # Find an async function
        process_request = next((m for m in method_defs if m.name == "process_request"), None)
        self.assertIsNotNone(process_request, "Expected to find 'process_request' method")
        
        # Verify its properties
        self.assertEqual(process_request.module, "sample_flask_app")
        self.assertEqual(process_request.file_path, self.sample_file_path)
        self.assertIsNone(process_request.class_name)
        self.assertTrue(process_request.is_async)
        self.assertTrue(any("app.route" in d for d in process_request.decorators))
        
    def test_method_call_properties(self):
        """
        Test the properties of MethodCall objects.
        """
        # Parse the sample code
        method_defs, method_calls = self.parser.parse_source(
            self.sample_code, 
            self.sample_file_path, 
            "sample_flask_app"
        )
        
        # Find the process_data method
        process_data = next((m for m in method_defs if m.name == "process_data"), None)
        self.assertIsNotNone(process_data, "Expected to find 'process_data' method")
        
        # Find calls from process_data
        process_data_calls = [c for c in method_calls if c.caller_id == process_data.unique_id]
        self.assertGreaterEqual(len(process_data_calls), 1, 
                              "Expected at least 1 call from 'process_data' method")
        
        # Get the call to validate_data
        validate_data_call = next((c for c in process_data_calls if c.callee_name == "validate_data"), None)
        self.assertIsNotNone(validate_data_call, "Expected to find call to 'validate_data'")
        
        # Verify its properties
        self.assertEqual(validate_data_call.caller_id, process_data.unique_id)
        self.assertEqual(validate_data_call.callee_name, "validate_data")
        
        # Verify to_dict method
        call_dict = validate_data_call.to_dict()
        self.assertEqual(call_dict["caller"]["name"], "process_data")
        self.assertEqual(call_dict["callee_name"], "validate_data")
        self.assertEqual(call_dict["caller_id"], process_data.unique_id)


if __name__ == "__main__":
    unittest.main()
