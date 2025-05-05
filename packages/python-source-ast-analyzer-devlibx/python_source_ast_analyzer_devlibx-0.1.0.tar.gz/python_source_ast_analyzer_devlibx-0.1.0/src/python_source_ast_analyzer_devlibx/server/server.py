"""
HTTP Server for Python Source AST Analyzer.

This module provides a Flask-based HTTP server for analyzing Python source code.
"""

import os
import json
import sys
from typing import Dict, Any, Optional, List, Union

from flask import Flask, request, jsonify, Response

# Import utils differently when run as a script vs as part of the package
if __name__ == "__main__":
    # Will be imported later after adding the parent directory to the path
    pass
else:
    from ..utils import generate_method_id

# Handle imports differently when run as a script vs as part of the package
if __name__ == "__main__":
    # Add the parent directory to the path so we can import the package
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from python_source_ast_analyzer_devlibx.graph.graph_builder import GraphBuilder
    from python_source_ast_analyzer_devlibx.query.query_engine import QueryEngine
    from python_source_ast_analyzer_devlibx.output.formatters import JSONFormatter
    from python_source_ast_analyzer_devlibx.utils import generate_method_id
else:
    from ..graph.graph_builder import GraphBuilder
    from ..query.query_engine import QueryEngine
    from ..output.formatters import JSONFormatter


def create_app() -> Flask:
    """
    Create a Flask application for the Python Source AST Analyzer.
    
    Returns:
        A Flask application.
    """
    app = Flask(__name__)
    
    @app.route("/health", methods=["GET"])
    def health_check() -> Response:
        """
        Health check endpoint.
        
        Returns:
            A JSON response indicating the server is healthy.
        """
        return jsonify({"status": "healthy"})
    
    @app.route("/v1/analyze_project", methods=["POST"])
    def analyze_project() -> Response:
        """
        Analyze a project and generate a call graph.
        
        Supports two formats:
        
        Format 1:
        {
            "project_path": "/path/to/project",
            "recursive": true,
            "output_format": "json",
            "query_type": "outbound",
            "method_name": "example_method",
            "class_name": "ExampleClass",
            "file_path": "/path/to/file.py",
            "depth": 2,
            "flat": false
        }
        
        Format 2:
        {
            "project_dir": "/path/to/project",
            "depth": 3,
            "nested": true,
            "function_with_class_names": false,
            "function_with_file_name_and_line_number": true
        }
        
        Returns:
            A JSON response with the analysis results.
        """
        data = request.json
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Check which format is being used
        if "project_dir" in data:
            # Format 2 - Nested call graph format
            project_dir = data.get("project_dir")
            if not project_dir:
                return jsonify({"error": "No project_dir provided"}), 400
                
            if not os.path.exists(project_dir):
                return jsonify({"error": f"Project directory not found: {project_dir}"}), 404
                
            depth = data.get("depth", 3)
            nested = data.get("nested", True)
            function_with_class_names = data.get("function_with_class_names", False)
            function_with_file_name_and_line_number = data.get("function_with_file_name_and_line_number", True)
            
            try:
                # Build the call graph
                graph_builder = GraphBuilder()
                
                if os.path.isdir(project_dir):
                    call_graph = graph_builder.build_from_directory(project_dir, recursive=True)
                else:
                    call_graph = graph_builder.build_from_file(project_dir)
                    
                # Create a query engine
                query_engine = QueryEngine(call_graph)
                
                # Get all methods
                methods = query_engine.get_all_methods()
                
                # Build the nested call graph
                result = {}
                
                for method in methods:
                    # Create method identifier
                    method_id = generate_method_id(
                        file_path=method.get('file_path', ''),
                        name=method.get('name', ''),
                        line_number=method.get('line_number', 0),
                        class_name=method.get('class_name'),
                        with_class_name=function_with_class_names,
                        with_file_line=function_with_file_name_and_line_number
                    )
                    log = (method_id == "api/routes.py#add_highlight#439")
                    if log: print("Method ID:", method_id, "unique_id", method.get('unique_id'))
                    
                    # Get outbound calls for this method
                    outbound_data = query_engine.get_outbound_calls(method.get('unique_id'), depth, flat=False)
                    if log: print("outbound_data:", outbound_data)
                    
                    # Process the outbound calls recursively
                    result[method_id] = _process_nested_calls(outbound_data, depth, 1, 
                                                             function_with_class_names, 
                                                             function_with_file_name_and_line_number)
                    if log: print("result[method_id]:", result[method_id])

                return jsonify(result)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            # Format 1 - Original format
            project_path = data.get("project_path")
            if not project_path:
                return jsonify({"error": "No project_path provided"}), 400
                
            if not os.path.exists(project_path):
                return jsonify({"error": f"Project path not found: {project_path}"}), 404
                
            recursive = data.get("recursive", True)
            query_type = data.get("query_type", "outbound")
            method_name = data.get("method_name")
            class_name = data.get("class_name")
            file_path = data.get("file_path")
            depth = data.get("depth", 1)
            flat = data.get("flat", False)
            
            try:
                # Build the call graph
                graph_builder = GraphBuilder()
                
                if os.path.isdir(project_path):
                    call_graph = graph_builder.build_from_directory(project_path, recursive)
                else:
                    call_graph = graph_builder.build_from_file(project_path)
                    
                # Create a query engine
                query_engine = QueryEngine(call_graph)
                
                # Create a formatter
                formatter = JSONFormatter(indent=2)
                
                # Execute the query
                result = None
                
                if method_name:
                    # Find the method
                    methods = query_engine.find_methods_by_name(method_name)
                    
                    # Filter by class name if specified
                    if class_name:
                        methods = [m for m in methods if m.class_name == class_name]
                        
                    # Filter by file path if specified
                    if file_path:
                        methods = [m for m in methods if m.file_path == file_path]
                        
                    if not methods:
                        return jsonify({"error": f"Method not found: {method_name}"}), 404
                        
                    method_id = methods[0].unique_id
                    
                    # Query the call graph
                    if query_type == "outbound":
                        # Get outbound calls
                        data = query_engine.get_outbound_calls(method_id, depth, flat)
                        result = json.loads(formatter.format_outbound_calls(data))
                    elif query_type == "inbound":
                        # Get inbound calls
                        data = query_engine.get_inbound_calls(method_id, depth, flat)
                        result = json.loads(formatter.format_inbound_calls(data))
                    else:
                        return jsonify({"error": f"Invalid query_type: {query_type}"}), 400
                else:
                    # List all methods
                    methods = query_engine.get_all_methods()
                    result = json.loads(formatter.format_methods(methods))
                    
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            
    @app.route("/v1/find_routes", methods=["POST"])
    def find_routes() -> Response:
        """
        Find route handler methods in a project.
        
        Expected JSON payload:
        {
            "project_path": "/path/to/project",
            "recursive": true
        }
        
        Returns:
            A JSON response with the route handler methods.
        """
        data = request.json
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        project_path = data.get("project_path")
        if not project_path:
            return jsonify({"error": "No project_path provided"}), 400
            
        if not os.path.exists(project_path):
            return jsonify({"error": f"Project path not found: {project_path}"}), 404
            
        recursive = data.get("recursive", True)
        
        try:
            # Build the call graph
            graph_builder = GraphBuilder()
            
            if os.path.isdir(project_path):
                call_graph = graph_builder.build_from_directory(project_path, recursive)
            else:
                call_graph = graph_builder.build_from_file(project_path)
                
            # Create a query engine
            query_engine = QueryEngine(call_graph)
            
            # Find route handlers
            routes = query_engine.find_route_handlers()
            
            # Create a formatter
            formatter = JSONFormatter(indent=2)
            
            # Format the results
            result = json.loads(formatter.format_methods([r.to_dict() for r in routes]))
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    @app.route("/v1/analyze_project_nested", methods=["POST"])
    def analyze_project_nested() -> Response:
        """
        Analyze a project and generate a nested call graph with a specific format.
        
        Expected JSON payload:
        {
            "project_dir": "/path/to/project",
            "depth": 3,
            "nested": true,
            "function_with_class_names": false,
            "function_with_file_name_and_line_number": true
        }
        
        Returns:
            A JSON response with the nested call graph.
        """
        data = request.json
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        project_dir = data.get("project_dir")
        if not project_dir:
            return jsonify({"error": "No project_dir provided"}), 400
            
        if not os.path.exists(project_dir):
            return jsonify({"error": f"Project directory not found: {project_dir}"}), 404
            
        depth = data.get("depth", 3)
        nested = data.get("nested", True)
        function_with_class_names = data.get("function_with_class_names", False)
        function_with_file_name_and_line_number = data.get("function_with_file_name_and_line_number", True)
        
        try:
            # Build the call graph
            graph_builder = GraphBuilder()
            
            if os.path.isdir(project_dir):
                call_graph = graph_builder.build_from_directory(project_dir, recursive=True)
            else:
                call_graph = graph_builder.build_from_file(project_dir)
                
            # Create a query engine
            query_engine = QueryEngine(call_graph)
            
            # Get all methods
            methods = query_engine.get_all_methods()
            
            # Build the nested call graph
            result = {}
            
            for method in methods:
                # Create method identifier
                method_id = generate_method_id(
                    file_path=method.get('file_path', ''),
                    name=method.get('name', ''),
                    line_number=method.get('line_number', 0),
                    class_name=method.get('class_name'),
                    with_class_name=function_with_class_names,
                    with_file_line=function_with_file_name_and_line_number
                )
                
                # Get outbound calls for this method
                outbound_data = query_engine.get_outbound_calls(method.get('unique_id'), depth, flat=False)
                
                # Process the outbound calls recursively
                result[method_id] = _process_nested_calls(outbound_data, depth, 1, 
                                                         function_with_class_names, 
                                                         function_with_file_name_and_line_number)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def _process_nested_calls(node, max_depth, current_depth, with_class_names, with_file_line):
        """
        Process a call graph node recursively to build a nested structure.
        
        Args:
            node: The node to process.
            max_depth: Maximum depth to traverse.
            current_depth: Current depth in the traversal.
            with_class_names: Whether to include class names in method identifiers.
            with_file_line: Whether to include file paths and line numbers in method identifiers.
            
        Returns:
            A nested dictionary representing the call graph.
        """
        if current_depth > max_depth or not node or "method" not in node:
            return {}
            
        result = {}
        
        for call in node.get("calls", []):
            if "method" not in call:
                continue
                
            method = call["method"]
            
            # Create method identifier
            method_id = generate_method_id(
                file_path=method.get('file_path', ''),
                name=method.get('name', ''),
                line_number=method.get('line_number', 0),
                class_name=method.get('class_name'),
                with_class_name=with_class_names,
                with_file_line=with_file_line
            )
                
            # Process nested calls recursively
            result[method_id] = _process_nested_calls(call, max_depth, current_depth + 1, 
                                                    with_class_names, with_file_line)
                
        return result
    
    
    @app.route("/v1/list_methods", methods=["POST"])
    def list_methods() -> Response:
        """
        List all methods in a project.
        
        Expected JSON payload:
        {
            "project_path": "/path/to/project",
            "recursive": true
        }
        
        Returns:
            A JSON response with all methods in the project.
        """
        data = request.json
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        project_path = data.get("project_path")
        if not project_path:
            return jsonify({"error": "No project_path provided"}), 400
            
        if not os.path.exists(project_path):
            return jsonify({"error": f"Project path not found: {project_path}"}), 404
            
        recursive = data.get("recursive", True)
        
        try:
            # Build the call graph
            graph_builder = GraphBuilder()
            
            if os.path.isdir(project_path):
                call_graph = graph_builder.build_from_directory(project_path, recursive)
            else:
                call_graph = graph_builder.build_from_file(project_path)
                
            # Create a query engine
            query_engine = QueryEngine(call_graph)
            
            # List all methods
            methods = query_engine.get_all_methods()
            
            # Create a formatter
            formatter = JSONFormatter(indent=2)
            
            # Format the results
            result = json.loads(formatter.format_methods(methods))
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app


def run_server(host: str = "0.0.0.0", port: int = 9093, debug: bool = False) -> None:
    """
    Run the Flask server.
    
    Args:
        host: The host to run the server on.
        port: The port to run the server on.
        debug: Whether to run the server in debug mode.
    """
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(debug=True)
