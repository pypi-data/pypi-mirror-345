import ast
from typing import List

import coverage

from testgen.models.analysis_context import AnalysisContext
from testgen.models.function_metadata import FunctionMetadata
from testgen.models.test_case import TestCase
from testgen.util.file_utils import load_and_parse_file_for_tree, load_module
from testgen.util.utils import get_function_boundaries
from testgen.util.z3_utils.constraint_extractor import extract_branch_conditions


def get_branch_coverage(file_name, func, *args) -> list:
    cov = coverage.Coverage(branch=True)
    cov.start()

    func(*args)

    cov.stop()
    cov.save()

    analysis = cov.analysis2(file_name)

    branches = analysis.arcs()
    return branches


def get_coverage_analysis(file_name, class_name: str | None, func_name, args) -> tuple:
    tree = load_and_parse_file_for_tree(file_name)
    func_node = None
    func_start = None
    func_end = None
    
    # Process tree body
    for i, node in enumerate(tree.body):
        # Handle class methods
        if isinstance(node, ast.ClassDef) and class_name is not None:
            # Search within class body with its own index
            for j, class_node in enumerate(node.body):
                if isinstance(class_node, ast.FunctionDef) and class_node.name == func_name:
                    func_node = class_node
                    func_start = class_node.lineno
                    
                    # Now correctly check if this is the last method in the class
                    if j == len(node.body) - 1:
                        # Last method in class - find maximum line in method
                        max_lines = [line.lineno for line in ast.walk(class_node) 
                                    if hasattr(line, 'lineno') and line.lineno]
                        func_end = max(max_lines) if max_lines else func_start
                    else:
                        # Not last method - use next method's line number minus 1
                        next_node = node.body[j + 1]  # Correct index now
                        if hasattr(next_node, 'lineno'):
                            func_end = next_node.lineno - 1
                        else:
                            # Fallback using max line in method
                            max_lines = [line.lineno for line in ast.walk(class_node)
                                        if hasattr(line, 'lineno') and line.lineno]
                            func_end = max(max_lines) if max_lines else func_start
                    break
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_node = node
            func_start = node.lineno

            if i == len(tree.body) - 1:
                max_lines = [line.lineno for line in ast.walk(node) if hasattr(line, 'lineno') and line.lineno]
                func_end = max(max_lines) if max_lines else func_start
            else:
                next_node = tree.body[i + 1]
                if hasattr(next_node, 'lineno'):
                    func_end = next_node.lineno - 1
                else:
                    max_lines = [line.lineno for line in ast.walk(node)
                                 if hasattr(line, 'lineno') and line.lineno]
                    func_end = max(max_lines) if max_lines else func_start
            break

    if not func_node:
        raise ValueError(f"Function {func_name} not found in {file_name}")

    # Enable branch coverage
    cov = coverage.Coverage(branch=True)
    cov.start()
    module = load_module(file_name)

    if class_name is not None:
        class_obj = getattr(module, class_name)
        instance = class_obj()
        func = getattr(instance, func_name)
    else:
        func = getattr(module, func_name)

    func(*args)

    cov.stop()
    cov.save()

    analysis = cov.analysis2(file_name)
    analysis_list = list(analysis)
    # Filter executable and missed lines to function range
    analysis_list[1] = [line for line in analysis_list[1] if func_start <= line <= func_end]
    analysis_list[3] = [line for line in analysis_list[3] if func_start <= line <= func_end]

    # Find all branching statements (if/else) in function
    branch_lines = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.If):
            # Add the 'if' line
            branch_lines.append(node.lineno)

            # Find 'else' lines by analyzing orelse block
            if node.orelse:
                for else_item in node.orelse:
                    if hasattr(else_item, 'lineno'):
                        # Add line before the first statement in else block
                        else_line = else_item.lineno - 1
                        branch_lines.append(else_line)
                        break

    # Add branch lines to executable statements if not already present
    for line in branch_lines:
        if func_start <= line <= func_end and line not in analysis_list[1]:
            analysis_list[1].append(line)
    analysis_list[1].sort()

    # Make sure func_start is in executable and not in missed
    if func_start not in analysis_list[1]:
        analysis_list[1].append(func_start)
        analysis_list[1].sort()
    if func_start in analysis_list[3]:
        analysis_list[3].remove(func_start)

    return tuple(analysis_list)


def get_coverage_percentage(analysis: tuple) -> float:
    total_statements = len(analysis[1])
    missed_statements = len(analysis[3])
    covered_statements = total_statements - missed_statements
    return (covered_statements / total_statements) * 100 if total_statements > 0 else 0


def get_list_of_missed_lines(analysis: tuple) -> list:
    return analysis[3] # analysis[3] is list of missed line numbers


def get_list_of_covered_statements(analysis: tuple) -> list:
    return [x for x in analysis[1] if x not in analysis[3]]


def get_uncovered_lines_for_func(file_name: str, class_name: str | None, func_node: ast.FunctionDef, test_cases: List[TestCase]) -> List[int]:
    # Get normal uncovered lines
    func_name = func_node.name

    function_test_cases = [tc for tc in test_cases if tc.func_name == func_name]
    if not function_test_cases:
        print(f"Warning: No test cases found for function {func_name}.")
        return []

    module = load_module(file_name)
    if class_name is not None:
        class_obj = getattr(module, class_name)
        instance = class_obj()
        func = getattr(instance, func_name)
    else:
        func = getattr(module, func_name)

    # Run coverage
    cov = coverage.Coverage(branch=True)  # Enable branch coverage
    cov.start()
    for test_case in function_test_cases:
        if test_case.func_name == func_name:
            try:
                func(*test_case.inputs)
            except Exception as e:
                print(f"Warning: Test Case {test_case.inputs} failed with error: {e}")
    cov.stop()

    analysis = cov.analysis2(file_name)

    # Extract branch conditions from the function
    branch_conditions, _ = extract_branch_conditions(func_node)
    condition_line_numbers = [bc.line_number for bc in branch_conditions]

    # Check which branch condition lines weren't exercised
    func_start, func_end = get_function_boundaries(file_name, func_name)
    missed_lines = [line for line in analysis[3] if func_start <= line <= func_end]

    # Find branch conditions that need to be tested (those near missed lines)
    uncovered_branch_lines = []
    for line in condition_line_numbers:
        # Check if the condition itself or its following line (likely the branch body) is uncovered
        if line in missed_lines or (line + 1) in missed_lines:
            uncovered_branch_lines.append(line)

    return uncovered_branch_lines

def get_all_executable_statements(analysis_context: AnalysisContext, func: FunctionMetadata, test_cases):
    import ast

    if not test_cases:
        print("Warning: No test cases available to determine executable statements")
    else:
        analysis = get_coverage_analysis(analysis_context.filepath, analysis_context.class_name, func.function_name, test_cases[0].inputs)

    executable_lines = list(analysis[1])

    with open(analysis_context.filepath, 'r') as f:
        source = f.read()

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func.func_def.name:
            for if_node in ast.walk(node):
                if isinstance(if_node, ast.If) and if_node.orelse:
                    if isinstance(if_node.orelse[0], ast.If):
                        continue
                    else_line = if_node.orelse[0].lineno - 1

                    with open(analysis_context.filepath, 'r') as f:
                        lines = f.readlines()
                        if else_line <= len(lines):
                            line_content = lines[else_line - 1].strip()
                            if line_content == "else:":
                                if else_line not in executable_lines:
                                    executable_lines.append(else_line)

    return sorted(executable_lines)