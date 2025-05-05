"""
Python Source AST Analyzer - DevLibX

A tool for analyzing Python source code using the Abstract Syntax Tree (AST) module
to generate call graphs of methods.

This package provides functionality to:
1. Parse Python source code files using Python's built-in AST module
2. Identify and extract method definitions and method calls
3. Build a directed graph representing the call relationships between methods
4. Query the graph for outbound and inbound calls
5. Output results in various formats (JSON, DOT, Text)
6. Run as an HTTP server to provide a REST API
"""

from .parser.parser import Parser, MethodDefinition, MethodCall
from .graph.graph_builder import GraphBuilder
from .graph.call_graph import CallGraph
from .query.query_engine import QueryEngine
from .output.formatters import JSONFormatter, DOTFormatter, TextFormatter
from .server.server import create_app, run_server

__version__ = "0.1.0"

__all__ = [
    "Parser",
    "MethodDefinition",
    "MethodCall",
    "GraphBuilder",
    "CallGraph",
    "QueryEngine",
    "JSONFormatter",
    "DOTFormatter",
    "TextFormatter",
    "create_app",
    "run_server",
]
