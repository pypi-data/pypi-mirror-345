#!/usr/bin/env python3
"""
Code Analyzer Tool

This script performs three main functions:
1. Lists Python files with more than 350 lines of code
2. Creates a call graph showing which function calls which other function
3. Creates an index of all functions with their file paths
"""

import os
import ast
import sys
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# Директории, которые следует исключить из анализа
EXCLUDED_DIRS = [
    '.venv', 
    'site-packages', 
    'dist-packages',
    '__pycache__',
    'node_modules',
    '.git'
]

def should_skip_dir(path):
    """Проверяет, нужно ли пропустить директорию"""
    for excluded in EXCLUDED_DIRS:
        if excluded in path:
            return True
    return False

class FunctionCallVisitor(ast.NodeVisitor):
    """AST visitor to collect function calls within each function definition"""
    
    def __init__(self):
        self.current_function = None
        self.call_graph = defaultdict(set)
        self.functions = {}  # Map function names to their full names with class if applicable
        self.current_class = None
    
    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        # Visit all children in the class
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        # Save the current function
        old_function = self.current_function
        
        # Create fully qualified function name
        if self.current_class:
            self.current_function = f"{self.current_class}.{node.name}"
        else:
            self.current_function = node.name
        
        # Map the simple name to the fully qualified name
        self.functions[node.name] = self.current_function
        
        # Visit all children in the function
        self.generic_visit(node)
        
        # Restore the parent function
        self.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node):
        # Handle async functions just like regular functions
        self.visit_FunctionDef(node)
    
    def visit_Call(self, node):
        # Check if we're inside a function
        if self.current_function:
            func_name = None
            
            # Get the name of the called function
            if isinstance(node.func, ast.Name):
                # Direct function call like "foo()"
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                # Method call like "obj.foo()"
                func_name = node.func.attr
            
            if func_name:
                # Add to the call graph
                self.call_graph[self.current_function].add(func_name)
        
        # Continue visiting children
        self.generic_visit(node)

def count_lines(file_path):
    """Count the number of non-empty, non-comment lines in a file"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # Count non-empty, non-comment lines
    count = 0
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            count += 1
    
    return count

def find_large_files(root_dir, min_lines=350):
    """Find Python files with more than min_lines lines of code"""
    large_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Пропускаем исключенные директории
        dirs[:] = [d for d in dirs if not should_skip_dir(os.path.join(root, d))]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Пропускаем файлы в исключенных директориях
                if should_skip_dir(file_path):
                    continue
                    
                line_count = count_lines(file_path)
                
                if line_count > min_lines:
                    relative_path = os.path.relpath(file_path, root_dir)
                    large_files.append((relative_path, line_count))
    
    return large_files

def create_function_index(root_dir, output_file='function_index.txt'):
    """Create an index of all functions with their file paths"""
    function_index = []
    modules_analyzed = 0
    
    # Process each Python file
    for root, dirs, files in os.walk(root_dir):
        # Пропускаем исключенные директории
        dirs[:] = [d for d in dirs if not should_skip_dir(os.path.join(root, d))]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Пропускаем файлы в исключенных директориях
                if should_skip_dir(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        module_content = f.read()
                    
                    # Parse the file
                    module = ast.parse(module_content, filename=file_path)
                    
                    # Extract the module name from the file path
                    rel_path = os.path.relpath(file_path, root_dir)
                    module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
                    
                    # Find functions and classes
                    for node in ast.walk(module):
                        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                            function_name = node.name
                            function_index.append((function_name, rel_path))
                        elif isinstance(node, ast.ClassDef):
                            class_name = node.name
                            function_index.append((f"class {class_name}", rel_path))
                            # Find methods in the class
                            for class_node in node.body:
                                if isinstance(class_node, ast.FunctionDef) or isinstance(class_node, ast.AsyncFunctionDef):
                                    method_name = class_node.name
                                    function_index.append((f"{class_name}.{method_name}", rel_path))
                    
                    modules_analyzed += 1
                    
                except (SyntaxError, UnicodeDecodeError) as e:
                    print(f"Error analyzing {file_path}: {e}")
    
    # Save function index to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Function Index (analyzed {modules_analyzed} modules)\n\n")
        
        for function_name, file_path in sorted(function_index, key=lambda x: x[0].lower()):
            f.write(f"{function_name}: {file_path}\n")
    
    print(f"Function index saved to {output_file}")
    
    return function_index

def create_call_graph(root_dir, output_file='call_graph.txt'):
    """Create a graph of function calls and save it to a file"""
    call_graph = defaultdict(set)
    modules_analyzed = 0
    
    # Process each Python file
    for root, dirs, files in os.walk(root_dir):
        # Пропускаем исключенные директории
        dirs[:] = [d for d in dirs if not should_skip_dir(os.path.join(root, d))]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Пропускаем файлы в исключенных директориях
                if should_skip_dir(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        module_content = f.read()
                    
                    # Parse the file
                    module = ast.parse(module_content, filename=file_path)
                    
                    # Extract the module name from the file path
                    rel_path = os.path.relpath(file_path, root_dir)
                    module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
                    
                    # Find function calls
                    visitor = FunctionCallVisitor()
                    visitor.visit(module)
                    
                    # Add to the global call graph with module name prefix
                    for caller, callees in visitor.call_graph.items():
                        full_caller = f"{module_name}::{caller}"
                        for callee in callees:
                            # Try to get the fully qualified name if available
                            if callee in visitor.functions:
                                full_callee = f"{module_name}::{visitor.functions[callee]}"
                            else:
                                full_callee = callee
                            
                            call_graph[full_caller].add(full_callee)
                    
                    modules_analyzed += 1
                    
                except (SyntaxError, UnicodeDecodeError) as e:
                    print(f"Error analyzing {file_path}: {e}")
    
    # Save call graph to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Function Call Graph (analyzed {modules_analyzed} modules)\n\n")
        
        for caller, callees in sorted(call_graph.items()):
            f.write(f"{caller}:\n")
            for callee in sorted(callees):
                f.write(f"  - {callee}\n")
            f.write("\n")
    
    print(f"Call graph saved to {output_file}")
    
    return call_graph

def visualize_call_graph(call_graph, output_file='call_graph.png'):
    """Create a visual representation of the call graph using NetworkX"""
    G = nx.DiGraph()
    
    # Add nodes and edges
    for caller, callees in call_graph.items():
        G.add_node(caller)
        for callee in callees:
            G.add_node(callee)
            G.add_edge(caller, callee)
    
    # Check if the graph is too large to visualize effectively
    if len(G.nodes) > 100:
        print(f"Warning: Graph is very large ({len(G.nodes)} nodes), visualization may be cluttered")
        print("Consider filtering the graph or using a specialized tool like pyan for better visualization")
    
    try:
        # Create the plot
        plt.figure(figsize=(20, 20))
        pos = nx.spring_layout(G, k=0.3, iterations=50)
        nx.draw(G, pos, with_labels=True, node_size=100, node_color="skyblue", 
                font_size=8, font_weight="bold", arrows=True, 
                connectionstyle='arc3, rad=0.1', arrowsize=10)
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Call graph visualization saved to {output_file}")
    except Exception as e:
        print(f"Error creating visualization: {e}")
        print("Text-based call graph is still available")

def main():
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = os.getcwd()  # Default to current directory
    
    print(f"Analyzing code in {root_dir} (excluding library files)")
    
    # Find large files
    print("\n=== Files with more than 350 lines ===")
    large_files = find_large_files(root_dir)
    
    if large_files:
        with open('large_files.txt', 'w', encoding='utf-8') as f:
            f.write("# Files with more than 350 lines of code\n\n")
            for file_path, line_count in sorted(large_files, key=lambda x: x[1], reverse=True):
                info = f"{file_path}: {line_count} lines"
                print(info)
                f.write(f"{info}\n")
        print(f"\nList of large files saved to large_files.txt")
    else:
        print("No files with more than 350 lines found.")
    
    # Create function index
    print("\n=== Creating function index ===")
    create_function_index(root_dir)
    
    # Create call graph
    print("\n=== Creating function call graph ===")
    call_graph = create_call_graph(root_dir)
    
    # Try to visualize the graph if matplotlib is available
    try:
        visualize_call_graph(call_graph)
    except Exception as e:
        print(f"Could not create visual graph: {e}")

if __name__ == "__main__":
    main() 