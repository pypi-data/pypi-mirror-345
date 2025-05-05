"""
Test module for the GraphBuilder class.

This module tests the GraphBuilder's ability to build call graphs from Python source code.
"""

import os
import unittest
from typing import Dict, List, Set

from python_source_ast_analyzer_devlibx.graph.graph_builder import GraphBuilder
from python_source_ast_analyzer_devlibx.graph.call_graph import CallGraph


class TestGraphBuilder(unittest.TestCase):
    """
    Test case for the GraphBuilder class.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        self.graph_builder = GraphBuilder()
        
        # Path to the sample Flask application
        self.sample_file_path = os.path.join(os.path.dirname(__file__), "sample_flask_app", "sample_flask_app.py")
        
        # Read the sample file content
        with open(self.sample_file_path, "r", encoding="utf-8") as f:
            self.sample_code = f.read()
        
    def test_build_from_file(self):
        """
        Test the build_from_file method with the sample Flask application.
        """
        # Build the call graph from the sample file
        call_graph = self.graph_builder.build_from_file(self.sample_file_path)
        
        # Verify that the call graph is not None
        self.assertIsNotNone(call_graph, "Expected a non-None call graph")
        
        # Verify that the call graph is a CallGraph instance
        self.assertIsInstance(call_graph, CallGraph, "Expected a CallGraph instance")
        
        # Get all methods from the call graph
        methods = call_graph.get_all_methods()
        
        # Verify that we have the expected number of methods
        # The sample file has:
        # - 5 regular functions (process_data, validate_data, get_data, initialize_app, enhance_result)
        # - 1 async function (process_request)
        # - 2 methods in DataUtility class (clean_data, format_response)
        # - 3 methods in ConfigManager class (__init__, get_config, update_config)
        # Total: 11 method definitions
        self.assertEqual(len(methods), 11, "Expected 11 methods in the call graph")
        
        # Verify that we found the route handlers
        route_handlers = [m for m in methods if any("app.route" in d for d in m.get("decorators", []))]
        self.assertEqual(len(route_handlers), 2, "Expected 2 route handlers")
        
        # Verify the route handler names
        route_handler_names = {m.get("name") for m in route_handlers}
        self.assertSetEqual(route_handler_names, {"get_data", "process_request"}, 
                           "Expected route handlers named 'get_data' and 'process_request'")
        
        # Verify that we found the async functions
        async_functions = [m for m in methods if m.get("is_async", False)]
        self.assertEqual(len(async_functions), 2, "Expected 2 async functions")
        
        # Verify the async function names
        async_function_names = {m.get("name") for m in async_functions}
        self.assertSetEqual(async_function_names, {"process_request", "enhance_result"}, 
                           "Expected async functions named 'process_request' and 'enhance_result'")
        
        # Verify that we found the class methods
        class_methods = [m for m in methods if m.get("class_name") is not None]
        self.assertEqual(len(class_methods), 5, "Expected 5 class methods")
        
        # Verify the class names
        class_names = {m.get("class_name") for m in class_methods}
        self.assertSetEqual(class_names, {"DataUtility", "ConfigManager"}, 
                           "Expected classes named 'DataUtility' and 'ConfigManager'")
        
        # Test outbound calls for a specific method
        # Find the get_data method
        get_data_method = next((m for m in methods if m.get("name") == "get_data"), None)
        self.assertIsNotNone(get_data_method, "Expected to find 'get_data' method")
        
        # Get outbound calls for get_data
        outbound_calls = call_graph.get_outbound_calls(get_data_method.get("unique_id"), depth=1)
        
        # Verify that outbound_calls is not None
        self.assertIsNotNone(outbound_calls, "Expected non-None outbound calls")
        
        # Verify that outbound_calls has the correct structure
        self.assertIn("method", outbound_calls, "Expected 'method' key in outbound calls")
        self.assertIn("calls", outbound_calls, "Expected 'calls' key in outbound calls")
        
        # Verify that get_data has outbound calls
        self.assertGreater(len(outbound_calls.get("calls", [])), 0, 
                          "Expected at least one outbound call from 'get_data'")
        
        # Test inbound calls for a specific method
        # Find the process_data method
        process_data_method = next((m for m in methods if m.get("name") == "process_data"), None)
        self.assertIsNotNone(process_data_method, "Expected to find 'process_data' method")
        
        # Get inbound calls for process_data
        inbound_calls = call_graph.get_inbound_calls(process_data_method.get("unique_id"), depth=1)
        
        # Verify that inbound_calls is not None
        self.assertIsNotNone(inbound_calls, "Expected non-None inbound calls")
        
        # Verify that inbound_calls has the correct structure
        self.assertIn("method", inbound_calls, "Expected 'method' key in inbound calls")
        self.assertIn("called_by", inbound_calls, "Expected 'called_by' key in inbound calls")
        
        # Verify that process_data has inbound calls
        self.assertGreater(len(inbound_calls.get("called_by", [])), 0, 
                          "Expected at least one inbound call to 'process_data'")
        
        # Test flat outbound calls
        flat_outbound_calls = call_graph.get_flat_outbound_calls(get_data_method.get("unique_id"), depth=2)
        
        # Verify that flat_outbound_calls is not None
        self.assertIsNotNone(flat_outbound_calls, "Expected non-None flat outbound calls")
        
        # Verify that flat_outbound_calls is a list
        self.assertIsInstance(flat_outbound_calls, list, "Expected flat outbound calls to be a list")
        
        # Verify that flat_outbound_calls has at least one item
        self.assertGreater(len(flat_outbound_calls), 0, 
                          "Expected at least one item in flat outbound calls")
        
        # Test method lookup by name
        process_data_methods = call_graph.get_methods_by_name("process_data")
        
        # Verify that process_data_methods is not None
        self.assertIsNotNone(process_data_methods, "Expected non-None methods by name")
        
        # Verify that process_data_methods is a list
        self.assertIsInstance(process_data_methods, list, "Expected methods by name to be a list")
        
        # Verify that process_data_methods has exactly one item
        self.assertEqual(len(process_data_methods), 1, 
                        "Expected exactly one method named 'process_data'")
        
        # Verify that the method has the correct name
        self.assertEqual(process_data_methods[0].name, "process_data", 
                        "Expected method name to be 'process_data'")
        
        # Test method lookup by class
        data_utility_methods = call_graph.get_methods_by_class("DataUtility")
        
        # Verify that data_utility_methods is not None
        self.assertIsNotNone(data_utility_methods, "Expected non-None methods by class")
        
        # Verify that data_utility_methods is a list
        self.assertIsInstance(data_utility_methods, list, "Expected methods by class to be a list")
        
        # Verify that data_utility_methods has exactly two items
        self.assertEqual(len(data_utility_methods), 2, 
                        "Expected exactly two methods in class 'DataUtility'")
        
        # Verify that the methods have the correct class name
        for method in data_utility_methods:
            self.assertEqual(method.class_name, "DataUtility", 
                           "Expected class name to be 'DataUtility'")
        
        # Test method lookup by file
        file_methods = call_graph.get_methods_by_file(self.sample_file_path)
        
        # Verify that file_methods is not None
        self.assertIsNotNone(file_methods, "Expected non-None methods by file")
        
        # Verify that file_methods is a list
        self.assertIsInstance(file_methods, list, "Expected methods by file to be a list")
        
        # Verify that file_methods has the expected number of items
        self.assertEqual(len(file_methods), 11, 
                        f"Expected 11 methods in file '{self.sample_file_path}'")
        
        # Verify that the methods have the correct file path
        for method in file_methods:
            self.assertEqual(method.file_path, self.sample_file_path, 
                           f"Expected file path to be '{self.sample_file_path}'")


    def test_build_from_source(self):
        """
        Test the build_from_source method with the sample Flask application.
        """
        # Build the call graph from the sample source code
        call_graph = self.graph_builder.build_from_source(
            self.sample_code, 
            self.sample_file_path, 
            "sample_flask_app"
        )
        
        # Verify that the call graph is not None
        self.assertIsNotNone(call_graph, "Expected a non-None call graph")
        
        # Verify that the call graph is a CallGraph instance
        self.assertIsInstance(call_graph, CallGraph, "Expected a CallGraph instance")
        
        # Get all methods from the call graph
        methods = call_graph.get_all_methods()
        
        # Verify that we have the expected number of methods
        self.assertEqual(len(methods), 11, "Expected 11 methods in the call graph")
        
        # Verify that we found the route handlers
        route_handlers = [m for m in methods if any("app.route" in d for d in m.get("decorators", []))]
        self.assertEqual(len(route_handlers), 2, "Expected 2 route handlers")
        
        # Verify that we found the async functions
        async_functions = [m for m in methods if m.get("is_async", False)]
        self.assertEqual(len(async_functions), 2, "Expected 2 async functions")
        
        # Verify that we found the class methods
        class_methods = [m for m in methods if m.get("class_name") is not None]
        self.assertEqual(len(class_methods), 5, "Expected 5 class methods")
        
        # Verify that the module name is correctly set
        for method in methods:
            self.assertEqual(method.get("module"), "sample_flask_app", 
                           "Expected module name to be 'sample_flask_app'")
            
        # Verify that the file path is correctly set
        for method in methods:
            self.assertEqual(method.get("file_path"), self.sample_file_path, 
                           f"Expected file path to be '{self.sample_file_path}'")
            
        # Test specific method calls
        # Find the get_data method
        get_data_method = next((m for m in methods if m.get("name") == "get_data"), None)
        self.assertIsNotNone(get_data_method, "Expected to find 'get_data' method")
        
        # Get outbound calls for get_data
        outbound_calls = call_graph.get_outbound_calls(get_data_method.get("unique_id"), depth=1)
        
        # Verify that get_data has outbound calls
        self.assertGreater(len(outbound_calls.get("calls", [])), 0, 
                          "Expected at least one outbound call from 'get_data'")
        
        # Compare with the results from build_from_file
        file_call_graph = self.graph_builder.build_from_file(self.sample_file_path)
        file_methods = file_call_graph.get_all_methods()
        
        # Verify that both methods produce the same number of methods
        self.assertEqual(len(methods), len(file_methods), 
                        "Expected the same number of methods from both build methods")
        
        # Verify that both methods produce the same method names
        source_method_names = {m.get("name") for m in methods}
        file_method_names = {m.get("name") for m in file_methods}
        self.assertSetEqual(source_method_names, file_method_names, 
                          "Expected the same method names from both build methods")
                          
    def test_get_call_graph(self):
        """
        Test the get_call_graph method.
        """
        # Build a call graph
        built_call_graph = self.graph_builder.build_from_file(self.sample_file_path)
        
        # Get the call graph using get_call_graph
        retrieved_call_graph = self.graph_builder.get_call_graph()
        
        # Verify that the retrieved call graph is not None
        self.assertIsNotNone(retrieved_call_graph, "Expected a non-None call graph")
        
        # Verify that the retrieved call graph is a CallGraph instance
        self.assertIsInstance(retrieved_call_graph, CallGraph, "Expected a CallGraph instance")
        
        # Verify that the retrieved call graph is the same object as the built call graph
        self.assertIs(retrieved_call_graph, built_call_graph, 
                     "Expected get_call_graph to return the same object as build_from_file")
        
        # Get all methods from both call graphs
        built_methods = built_call_graph.get_all_methods()
        retrieved_methods = retrieved_call_graph.get_all_methods()
        
        # Verify that both call graphs have the same number of methods
        self.assertEqual(len(built_methods), len(retrieved_methods), 
                        "Expected the same number of methods in both call graphs")
        
        # Verify that both call graphs have the same method names
        built_method_names = {m.get("name") for m in built_methods}
        retrieved_method_names = {m.get("name") for m in retrieved_methods}
        self.assertSetEqual(built_method_names, retrieved_method_names, 
                          "Expected the same method names in both call graphs")
                          
    def test_build_from_directory(self):
        """
        Test the build_from_directory method with the sample Flask application directory.
        """
        # Get the directory containing the sample Flask application
        sample_dir = os.path.dirname(self.sample_file_path)
        
        # Build the call graph from the directory
        call_graph = self.graph_builder.build_from_directory(sample_dir)
        
        # Verify that the call graph is not None
        self.assertIsNotNone(call_graph, "Expected a non-None call graph")
        
        # Verify that the call graph is a CallGraph instance
        self.assertIsInstance(call_graph, CallGraph, "Expected a CallGraph instance")
        
        # Get all methods from the call graph
        methods = call_graph.get_all_methods()
        
        # Verify that we have methods
        self.assertGreater(len(methods), 0, "Expected at least one method in the call graph")
        
        # Verify that we found the sample Flask application methods
        # Find the get_data method from the sample Flask application
        get_data_method = next((m for m in methods if m.get("name") == "get_data"), None)
        self.assertIsNotNone(get_data_method, "Expected to find 'get_data' method")
        
        # Verify that the file path is correct
        self.assertEqual(get_data_method.get("file_path"), self.sample_file_path, 
                        f"Expected file path to be '{self.sample_file_path}'")
        
        # Compare with the results from build_from_file
        file_call_graph = self.graph_builder.build_from_file(self.sample_file_path)
        file_methods = file_call_graph.get_all_methods()
        
        # Get the method names from the directory call graph that are from the sample file
        dir_sample_methods = [m for m in methods if m.get("file_path") == self.sample_file_path]
        dir_sample_method_names = {m.get("name") for m in dir_sample_methods}
        
        # Get the method names from the file call graph
        file_method_names = {m.get("name") for m in file_methods}
        
        # Verify that the directory call graph contains all the methods from the file call graph
        self.assertSetEqual(dir_sample_method_names, file_method_names, 
                          "Expected the directory call graph to contain all methods from the file call graph")
        
        # Test with recursive=False
        non_recursive_call_graph = self.graph_builder.build_from_directory(sample_dir, recursive=False)
        
        # Verify that the call graph is not None
        self.assertIsNotNone(non_recursive_call_graph, "Expected a non-None call graph")
        
        # Get all methods from the call graph
        non_recursive_methods = non_recursive_call_graph.get_all_methods()
        
        # Verify that we have methods
        self.assertGreater(len(non_recursive_methods), 0, 
                          "Expected at least one method in the non-recursive call graph")
                          
    def test_error_handling(self):
        """
        Test error handling in the GraphBuilder class.
        """
        # Test FileNotFoundError for build_from_file
        non_existent_file = os.path.join(os.path.dirname(__file__), "non_existent_file.py")
        with self.assertRaises(FileNotFoundError):
            self.graph_builder.build_from_file(non_existent_file)
            
        # Test FileNotFoundError for build_from_directory
        non_existent_dir = os.path.join(os.path.dirname(__file__), "non_existent_dir")
        with self.assertRaises(FileNotFoundError):
            self.graph_builder.build_from_directory(non_existent_dir)
            
        # Test NotADirectoryError for build_from_directory
        with self.assertRaises(NotADirectoryError):
            self.graph_builder.build_from_directory(self.sample_file_path)
            
        # Test SyntaxError for build_from_source
        invalid_python = "def invalid_function(:"  # Missing closing parenthesis
        with self.assertRaises(SyntaxError):
            self.graph_builder.build_from_source(invalid_python)
            
    def test_custom_parser(self):
        """
        Test the GraphBuilder with a custom parser.
        """
        # Create a mock parser
        class MockParser:
            def __init__(self):
                self.parse_file_called = False
                self.parse_directory_called = False
                self.parse_source_called = False
                
            def parse_file(self, file_path, module_name=None):
                self.parse_file_called = True
                self.file_path = file_path
                self.module_name = module_name
                return [], []
                
            def parse_directory(self, directory_path, recursive=True):
                self.parse_directory_called = True
                self.directory_path = directory_path
                self.recursive = recursive
                return [], []
                
            def parse_source(self, source_code, file_path="<unknown>", module_name="<unknown>"):
                self.parse_source_called = True
                self.source_code = source_code
                self.file_path = file_path
                self.module_name = module_name
                return [], []
        
        # Create a mock parser
        mock_parser = MockParser()
        
        # Create a GraphBuilder with the mock parser
        graph_builder = GraphBuilder(parser=mock_parser)
        
        # Verify that the GraphBuilder uses the mock parser
        self.assertIs(graph_builder.parser, mock_parser, 
                     "Expected GraphBuilder to use the provided parser")
        
        # Test build_from_file with the mock parser
        graph_builder.build_from_file(self.sample_file_path)
        
        # Verify that the mock parser's parse_file method was called
        self.assertTrue(mock_parser.parse_file_called, 
                       "Expected mock parser's parse_file method to be called")
        
        # Verify that the mock parser was called with the correct arguments
        self.assertEqual(mock_parser.file_path, self.sample_file_path, 
                        "Expected mock parser to be called with the correct file path")
        
        # Test build_from_directory with the mock parser
        sample_dir = os.path.dirname(self.sample_file_path)
        graph_builder.build_from_directory(sample_dir, recursive=False)
        
        # Verify that the mock parser's parse_directory method was called
        self.assertTrue(mock_parser.parse_directory_called, 
                       "Expected mock parser's parse_directory method to be called")
        
        # Verify that the mock parser was called with the correct arguments
        self.assertEqual(mock_parser.directory_path, sample_dir, 
                        "Expected mock parser to be called with the correct directory path")
        self.assertEqual(mock_parser.recursive, False, 
                        "Expected mock parser to be called with recursive=False")
        
        # Test build_from_source with the mock parser
        graph_builder.build_from_source(self.sample_code, self.sample_file_path, "sample_flask_app")
        
        # Verify that the mock parser's parse_source method was called
        self.assertTrue(mock_parser.parse_source_called, 
                       "Expected mock parser's parse_source method to be called")
        
        # Verify that the mock parser was called with the correct arguments
        self.assertEqual(mock_parser.source_code, self.sample_code, 
                        "Expected mock parser to be called with the correct source code")
        self.assertEqual(mock_parser.file_path, self.sample_file_path, 
                        "Expected mock parser to be called with the correct file path")
        self.assertEqual(mock_parser.module_name, "sample_flask_app", 
                        "Expected mock parser to be called with the correct module name")


if __name__ == "__main__":
    unittest.main()
