"""
Command-line interface for Python Source AST Analyzer.

This module provides a command-line interface for the Python Source AST Analyzer.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Any

from .graph.graph_builder import GraphBuilder
from .query.query_engine import QueryEngine
from .output.formatters import JSONFormatter, DOTFormatter, TextFormatter
from .server.server import run_server as run_http_server


def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Python Source AST Analyzer - Analyze Python source code and generate call graphs."
    )
    
    # Mode options
    mode_group = parser.add_argument_group("Mode Options")
    mode_group.add_argument(
        "--server",
        action="store_true",
        help="Run as an HTTP server."
    )
    mode_group.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to run the HTTP server on. Default: 0.0.0.0"
    )
    mode_group.add_argument(
        "--port",
        type=int,
        default=9093,
        help="Port to run the HTTP server on. Default: 9093"
    )
    mode_group.add_argument(
        "--debug",
        action="store_true",
        help="Run the HTTP server in debug mode."
    )
    
    # Input options
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument(
        "-f", "--file", 
        help="Path to a Python source code file to analyze."
    )
    input_group.add_argument(
        "-d", "--directory", 
        help="Path to a directory containing Python source code files to analyze."
    )
    input_group.add_argument(
        "--recursive", 
        action="store_true", 
        help="Recursively analyze subdirectories."
    )
    
    # Query options
    query_group = parser.add_argument_group("Query Options")
    query_group.add_argument(
        "--method", 
        help="Name of the method to query."
    )
    query_group.add_argument(
        "--class", 
        dest="class_name", 
        help="Name of the class containing the method to query."
    )
    query_group.add_argument(
        "--file-path", 
        help="Path of the file containing the method to query."
    )
    query_group.add_argument(
        "--outbound", 
        action="store_true", 
        help="Query outbound calls (methods called by the specified method)."
    )
    query_group.add_argument(
        "--inbound", 
        action="store_true", 
        help="Query inbound calls (methods that call the specified method)."
    )
    query_group.add_argument(
        "--depth", 
        type=int, 
        default=1, 
        help="Depth of the call graph to traverse."
    )
    query_group.add_argument(
        "--flat", 
        action="store_true", 
        help="Return a flat list of methods instead of a nested call graph."
    )
    query_group.add_argument(
        "--list-methods", 
        action="store_true", 
        help="List all methods in the analyzed code."
    )
    query_group.add_argument(
        "--find-routes", 
        action="store_true", 
        help="Find route handler methods (Flask or FastAPI)."
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--format", 
        choices=["json", "dot", "text"], 
        default="text", 
        help="Output format."
    )
    output_group.add_argument(
        "--output", 
        help="Path to the output file. If not specified, output is printed to stdout."
    )
    
    return parser.parse_args()


def get_formatter(format_name: str):
    """
    Get a formatter for the specified format.
    
    Args:
        format_name: The name of the format.
        
    Returns:
        The formatter.
    """
    if format_name == "json":
        return JSONFormatter()
    elif format_name == "dot":
        return DOTFormatter()
    else:
        return TextFormatter()


def find_method_by_name(query_engine: QueryEngine, method_name: str, class_name: Optional[str] = None, file_path: Optional[str] = None) -> Optional[str]:
    """
    Find a method by name.
    
    Args:
        query_engine: The query engine to use.
        method_name: The name of the method to find.
        class_name: The name of the class containing the method.
        file_path: The path of the file containing the method.
        
    Returns:
        The unique ID of the method, or None if not found.
    """
    # Find methods by name
    methods = query_engine.find_methods_by_name(method_name)
    
    # Filter by class name if specified
    if class_name:
        methods = [m for m in methods if m.class_name == class_name]
        
    # Filter by file path if specified
    if file_path:
        methods = [m for m in methods if m.file_path == file_path]
        
    # Return the first match if any
    if methods:
        return methods[0].unique_id
    return None


def main():
    """
    Main entry point for the command-line interface.
    """
    args = parse_args()
    
    # Check if we should run as a server
    if args.server:
        print(f"Starting HTTP server on {args.host}:{args.port}...")
        run_http_server(host=args.host, port=args.port, debug=args.debug)
        return
    
    # Check if we have input
    if not args.file and not args.directory:
        print("Error: No input specified. Use --file or --directory.", file=sys.stderr)
        sys.exit(1)
    
    # Build the call graph
    graph_builder = GraphBuilder()
    
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        try:
            graph_builder.build_from_file(args.file)
        except SyntaxError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.directory:
        if not os.path.exists(args.directory):
            print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
            sys.exit(1)
        try:
            graph_builder.build_from_directory(args.directory, args.recursive)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        
    # Get the call graph
    call_graph = graph_builder.get_call_graph()
    
    # Create a query engine
    query_engine = QueryEngine(call_graph)
    
    # Get the formatter
    formatter = get_formatter(args.format)
    
    # Execute the query
    result = None
    
    if args.list_methods:
        # List all methods
        methods = query_engine.get_all_methods()
        result = formatter.format_methods(methods)
    elif args.find_routes:
        # Find route handlers
        routes = query_engine.find_route_handlers()
        result = formatter.format_methods([r.to_dict() for r in routes])
    elif args.method:
        # Find the method
        method_id = find_method_by_name(query_engine, args.method, args.class_name, args.file_path)
        
        if not method_id:
            print(f"Error: Method not found: {args.method}", file=sys.stderr)
            sys.exit(1)
            
        # Query the call graph
        if args.outbound:
            # Get outbound calls
            data = query_engine.get_outbound_calls(method_id, args.depth, args.flat)
            result = formatter.format_outbound_calls(data)
        elif args.inbound:
            # Get inbound calls
            data = query_engine.get_inbound_calls(method_id, args.depth, args.flat)
            result = formatter.format_inbound_calls(data)
        else:
            print("Error: No query specified. Use --outbound or --inbound.", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: No query specified. Use --method, --list-methods, or --find-routes.", file=sys.stderr)
        sys.exit(1)
        
    # Output the result
    if args.output:
        formatter.write_to_file(result, args.output)
    else:
        print(result)


if __name__ == "__main__":
    main()
