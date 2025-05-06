from typing import List, Dict
import inspect
import ast
import astor
from testgen.tree.node import Node

class CodeGenerator:
    def __init__(self):
        pass
        
    def is_all_boolean_params(self, param_types: Dict[str, str]) -> bool:
        """Check if all parameters are boolean type."""
        if not param_types:
            return False
            
        for param_type in param_types.values():
            if param_type != 'bool':
                return False
        return True

    def get_original_function_source(self, func_obj) -> str:
        """Extract the original source code of the function."""
        try:
            # Get the source code as a string
            source = inspect.getsource(func_obj)
            return source
        except (IOError, TypeError) as e:
            print(f"Error getting source: {e}")
            return None

    def generate_code_from_tree(self, func_name: str, root: Node, params: List[str], operation, is_class_method: bool, param_types: Dict[str, str] = None) -> str:
        # If we have param types and not all are boolean, extract the original source
        if param_types and not self.is_all_boolean_params(param_types):
            original_source = self.get_original_function_source(operation)
            if original_source:
                return original_source
                
        # The existing tree-based generation for boolean params
        def traverse(node, depth, path=[], indent_level=1):
            base_indent = "    " * indent_level

            if depth == len(params):
                path = path + [node.value]
                if is_class_method:
                    result = operation(self, *path)
                else:
                    result = operation(*path)
                if isinstance(result, str):
                    return f"{base_indent}return '{result}'\n"
                else:
                    return f"{base_indent}return {result}\n"

            param = params[depth]

            if isinstance(node.value, bool):
                path = path + [node.value]

            true_branch = f"{base_indent}if {param} == True:\n"
            false_branch = f"{base_indent}else:\n"

            true_code = traverse(node.children[0], depth + 1, path, indent_level + 1)
            false_code = traverse(node.children[1], depth + 1, path, indent_level + 1)

            return f"{true_branch}{true_code}{false_branch}{false_code}"

        typed_param_list = []
        if is_class_method:
            typed_param_list.append("self")

        for param in params:
            param_type = param_types.get(param, 'bool') if param_types else 'bool'
            typed_param_list.append(f"{param}: {param_type}")

        function_code = f"def {func_name}({', '.join(typed_param_list)}):\n"
        body_code = traverse(root, 0)

        return function_code + body_code

    def generate_class(self, class_name):
        branched_class_name = f"Generated{class_name}"
        file_path = f"generated_{class_name.lower()}.py"
        class_file = open(f"{file_path}", "w")
        class_file.write(f"class {branched_class_name}:\n")
        return class_file