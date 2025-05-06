import ast
import os
from typing import Dict, List, Set
import coverage

from testgen.service.logging_service import get_logger
import testgen.util.coverage_utils
from testgen.models.test_case import TestCase
import pygraphviz as pgv

class CoverageVisualizer:
    def __init__(self):
        self.service = None
        self.cov = coverage.Coverage(branch=True)
        self.covered_lines: Dict[str, Set[int]] = {}
        self.logger = get_logger()

    def set_service(self, service):
        self.service = service

    def get_covered_lines(self, file_path: str, class_name: str | None, func_def: ast.FunctionDef, test_cases: List[TestCase]):
        if func_def.name not in self.covered_lines:
            self.covered_lines[func_def.name] = set()

        for test_case in [tc for tc in test_cases if tc.func_name == func_def.name]:
            analysis = testgen.util.coverage_utils.get_coverage_analysis(file_path, class_name, func_def.name, test_case.inputs)
            covered = testgen.util.coverage_utils.get_list_of_covered_statements(analysis)
            if covered:
                self.covered_lines[func_def.name].update(covered)

        if func_def.name in self.covered_lines:
            self.logger.debug(f"Covered lines for {func_def.name}: {self.covered_lines[func_def.name]}")
        else:
            self.logger.debug(f"No coverage data found for {func_def.name}")

    def generate_colored_cfg(self, function_name, output_path):
        """Generate colored CFG for a function showing test coverage"""
        source_file = self.service.file_path

        # Get absolute path
        abs_source_file = os.path.abspath(source_file)

        # Verify file exists
        if not os.path.exists(abs_source_file):
            print(f"ERROR: File does not exist: {abs_source_file}")
            return None

        # Read source code safely
        try:
            with open(abs_source_file, 'r') as f:
                source_code = f.read()
        except Exception as e:
            print(f"Error reading source file: {e}")
            return None

        try:
            tree = ast.parse(source_code)
            ast_functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            self.logger.debug(f"Functions found by AST: {ast_functions}")

            return self._create_basic_cfg(source_code, function_name, output_path)

        except Exception as e:
            print(f"Error in CFG generation: {e}")
            import traceback
            traceback.print_exc()
            return self._create_basic_cfg(source_code, function_name, output_path)

    def _create_basic_cfg(self, source_code, function_name, output_path):
        """Create a better CFG visualization showing actual branches"""
        # Parse the code to find the function
        tree = ast.parse(source_code)

        # Find the requested function
        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                func_node = node
                break

        if not func_node:
            raise ValueError(f"Function {function_name} not found in AST")

        # Create a directed graph
        graph = pgv.AGraph(directed=True)

        next_id = 0

        entry_id = next_id
        next_id += 1
        graph.add_node(entry_id, label=f"def {function_name}()", style="filled", fillcolor="#ddffdd")

        def process_node(ast_node, parent_id):
            nonlocal next_id

            if isinstance(ast_node, ast.If):
                # Create if condition node
                if_id = next_id
                next_id += 1
                line_num = ast_node.lineno
                line_text = source_code.split('\n')[line_num - 1].strip()
                covered = line_num in self.covered_lines[function_name]
                color = "#ddffdd" if covered else "#ffdddd"
                graph.add_node(if_id, label=line_text, style="filled", fillcolor=color)
                graph.add_edge(parent_id, if_id)

                if ast_node.body:
                    next_id += 1
                    graph.add_edge(if_id, next_id, label="True")
                    # Process true branch
                    true_id = process_block(ast_node.body, if_id, "True")
                else:
                    true_id = if_id

                if ast_node.orelse:
                    next_id += 1
                    graph.add_edge(if_id, next_id, label="False")
                    # Process false branch
                    false_id = process_block(ast_node.orelse, if_id, "False")
                else:
                    false_id = if_id

                return next_id - 1

            elif isinstance(ast_node, ast.Return):
                return_id = next_id
                next_id += 1
                line_num = ast_node.lineno
                line_text = source_code.split('\n')[line_num - 1].strip()
                covered = line_num in self.covered_lines[function_name]
                color = "#ddffdd" if covered else "#ffdddd"
                graph.add_node(return_id, label=line_text, style="filled", fillcolor=color)
                graph.add_edge(parent_id, return_id)
                return return_id

            return parent_id

        def process_block(nodes, parent_id, branch_label=""):
            if not nodes:
                return parent_id

            current_id = parent_id
            for node in nodes:
                current_id = process_node(node, current_id)

            return current_id

        # Process the function body
        process_block(func_node.body, entry_id)

        # Save the graph
        graph.layout(prog='dot')
        graph.draw(output_path)
        print(f"Enhanced basic CFG drawn to {output_path}")

        return output_path