#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic tests for the Python Source AST Analyzer.
"""

import os
import sys
import unittest

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python_source_ast_analyzer_devlibx.graph.graph_builder import GraphBuilder
from python_source_ast_analyzer_devlibx.query.query_engine import QueryEngine


class TestBasic(unittest.TestCase):
    """
    Basic tests for the Python Source AST Analyzer.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        # Create a simple Python source code string for testing
        self.source_code = """
def example_function():
    helper_function()
    return "Hello, world!"

def helper_function():
    return "I'm a helper function!"

class ExampleClass:
    def __init__(self):
        self.value = "example"
        
    def example_method(self):
        return self.helper_method()
        
    def helper_method(self):
        return helper_function()
"""
        
        # Build a call graph from the source code
        self.graph_builder = GraphBuilder()
        self.call_graph = self.graph_builder.build_from_source(self.source_code, "<test>")
        
        # Create a query engine
        self.query_engine = QueryEngine(self.call_graph)
        
    def test_method_extraction(self):
        """
        Test that methods are correctly extracted from the source code.
        """
        # Get all methods
        methods = self.query_engine.get_all_methods()
        
        # Check that we have the expected number of methods
        self.assertEqual(len(methods), 5)
        
        # Check that we have the expected method names
        method_names = [method["name"] for method in methods]
        self.assertIn("example_function", method_names)
        self.assertIn("helper_function", method_names)
        self.assertIn("__init__", method_names)
        self.assertIn("example_method", method_names)
        self.assertIn("helper_method", method_names)
        
    def test_outbound_calls(self):
        """
        Test that outbound calls are correctly extracted from the source code.
        """
        # Find the example_function
        methods = self.query_engine.find_methods_by_name("example_function")
        self.assertTrue(methods)
        method_id = methods[0].unique_id
        
        # Get outbound calls
        outbound_calls = self.query_engine.get_outbound_calls(method_id, depth=1)
        
        # Check that we have the expected outbound calls
        self.assertIn("calls", outbound_calls)
        self.assertEqual(len(outbound_calls["calls"]), 1)
        self.assertEqual(outbound_calls["calls"][0]["method"]["name"], "helper_function")
        
    def test_class_methods(self):
        """
        Test that class methods are correctly extracted from the source code.
        """
        # Find methods in the ExampleClass
        methods = self.query_engine.find_methods_by_class("ExampleClass")
        self.assertEqual(len(methods), 3)
        
        # Check that we have the expected method names
        method_names = [method.name for method in methods]
        self.assertIn("__init__", method_names)
        self.assertIn("example_method", method_names)
        self.assertIn("helper_method", method_names)
        
    def test_method_calls_in_class(self):
        """
        Test that method calls in classes are correctly extracted from the source code.
        """
        # Find the example_method
        methods = self.query_engine.find_methods_by_name("example_method")
        self.assertTrue(methods)
        method_id = methods[0].unique_id
        
        # Get outbound calls
        outbound_calls = self.query_engine.get_outbound_calls(method_id, depth=1)
        
        # Check that we have the expected outbound calls
        self.assertIn("calls", outbound_calls)
        self.assertEqual(len(outbound_calls["calls"]), 1)
        self.assertEqual(outbound_calls["calls"][0]["method"]["name"], "helper_method")


if __name__ == "__main__":
    unittest.main()
