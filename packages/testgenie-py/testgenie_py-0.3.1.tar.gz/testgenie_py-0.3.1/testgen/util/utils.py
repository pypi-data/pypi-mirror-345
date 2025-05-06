
import ast
import string
import sys
import random
from typing import List

from atheris import FuzzedDataProvider

from testgen.util.file_utils import load_and_parse_file_for_tree


def get_func(module, func_name:str):
    return getattr(module, func_name)

def extract_parameter_types(func_node):
    """Extract parameter types from a function node."""
    param_types = {}
    for arg in func_node.args.args:
        param_name = arg.arg
        if arg.annotation:
            param_type = ast.unparse(arg.annotation)
            param_types[param_name] = param_type
        else:
            if param_name != 'self':
                param_types[param_name] = None
    return param_types

def generate_random_inputs(param_types):
    """Generate inputs for fuzzing based on parameter types."""
    inputs = {}
    for param, param_type in param_types.items():
        if param_type == "int":
            # Try using sys.maxsize for minsize and maxsize
            minsize = -sys.maxsize - 1
            maxsize = sys.maxsize
            random_integer = random.randint(minsize, maxsize)
            inputs[param] = random_integer
        elif param_type == "bool":
            random_choice = random.choice([True, False])
            inputs[param] = random_choice
        elif param_type == "float":
            random_float = random.random()
            inputs[param] = random_float
        # TODO: Random String and Random bytes; Random objects?
        elif param_type == "str":
            inputs[param] = "abc"
        #elif param_type == "bytes":
        #    inputs[param] = fdp.ConsumeBytes(10)
        else:
            inputs[param] = None
    return inputs

def generate_extreme_inputs(param_types):
    inputs = {}
    for param, param_type in param_types.items():
        if param_type == "int":
            # int is unbounded in Python, but sys.maxsize is the max value representable by a signed word
            inputs[param] = sys.maxsize
        if param_type == "bool":
            random_choice = random.choice([1, 0])
            inputs[param] = random_choice
        if param_type == "float":
            random_choice = random.choice([sys.float_info.min, sys.float_info.max])
            inputs[param] = random_choice
        if param_type == "str":
            inputs[param] = ''.join(random.choice([string.ascii_letters, string.digits, string.punctuation, string.whitespace]) for _ in range(100))

def generate_inputs_from_fuzz_data(fdp: FuzzedDataProvider, param_types):
    """Generate fuzzed inputs based on parameter types."""
    inputs = []
    for param_type in param_types.values():
        if param_type == "int":
            inputs.append(fdp.ConsumeInt(4))
        elif param_type == "bool":
            inputs.append(fdp.ConsumeBool())
        elif param_type == "float":
            inputs.append(fdp.ConsumeFloat())
        elif param_type == "str":
            inputs.append(fdp.ConsumeString(10))
        elif param_type == "bytes":
            inputs.append(fdp.ConsumeBytes(10))
        else:
            inputs.append(None)
    return tuple(inputs)

def get_functions(tree) -> List[ast.FunctionDef]:
    functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
        if isinstance(node, ast.ClassDef):
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    functions.append(class_node)
    return functions

def get_function_boundaries(file_name: str, func_name: str) -> tuple:
    tree = load_and_parse_file_for_tree(file_name)
    for i, node in enumerate(tree.body):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_start = node.lineno

            if i == len(tree.body) - 1:
                max_lines = [line.lineno for line in ast.walk(node) if hasattr(line, 'lineno') and line.lineno]
                func_end = max(max_lines) if max_lines else func_start
            else:
                next_node = tree.body[i + 1]
                if hasattr(next_node, 'lineno'):
                    func_end = next_node.lineno - 1
                else:
                    max_lines = [line.lineno for line in ast.walk(node) if hasattr(line, 'lineno') and line.lineno]
                    func_end = max(max_lines) if max_lines else func_start

            return func_start, func_end
        
    # For classes
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for i, method in enumerate(node.body):
                if isinstance(method, ast.FunctionDef) and method.name == func_name:
                    func_start = method.lineno
                    
                    # Find end of method
                    if i == len(node.body) - 1:
                        max_lines = [line.lineno for line in ast.walk(method) 
                                     if hasattr(line, 'lineno') and line.lineno]
                        func_end = max(max_lines) if max_lines else func_start
                    else:
                        next_method = node.body[i + 1]
                        if hasattr(next_method, 'lineno'):
                            func_end = next_method.lineno - 1
                        else:
                            max_lines = [line.lineno for line in ast.walk(method)
                                         if hasattr(line, 'lineno') and line.lineno]
                            func_end = max(max_lines) if max_lines else func_start
                    
                    return func_start, func_end
    
    raise ValueError(f"Function {func_name} not found in {file_name}")

    

