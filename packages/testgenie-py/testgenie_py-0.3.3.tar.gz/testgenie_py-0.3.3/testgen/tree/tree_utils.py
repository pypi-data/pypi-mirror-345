from collections import deque
from .node import *
import operator


def apply_operation(func, *args):
    if not args:
        return True  # Default to True if no arguments are given
    result = args[0]
    for arg in args[1:]:
        result = func(result, arg)
    return result


def build_binary_tree(node, level, max_level):
    if level >= max_level:
        return

    true_child = Node(True)
    false_child = Node(False)

    node.add_child(true_child)
    node.add_child(false_child)

    build_binary_tree(true_child, level + 1, max_level)
    build_binary_tree(false_child, level + 1, max_level)


def print_level_order_tree(node):
    if node is None:
        return

    queue = deque([(node, 0)])

    while queue:
        current_node, level = queue.popleft()

        print(f"Level {level}, {current_node.value} -> ", end="")

        if current_node.children:
            print(", ".join(str(child.value) for child in current_node.children))
        else:
            print("None")

        for child in current_node.children:
            queue.append((child, level + 1))


def generate_boolean_function(parameters, operation):
    def evaluate_path(path_values):
        return apply_operation(operation, *path_values)

    def traverse(index, path_values):
        """Recursively constructs the function string."""
        if index == len(parameters):
            result = evaluate_path(path_values)
            return f"return {str(result)}\n"

        param = parameters[index]

        true_branch = f"if {param} == True:\n"
        true_branch += "    " + traverse(index + 1, path_values + [True]).replace("\n", "\n    ")

        false_branch = f"else:\nif {param} == False:\n"
        false_branch += "    " + traverse(index + 1, path_values + [False]).replace("\n", "\n    ")

        return true_branch + "\n" + false_branch

    function_str = traverse(0, [])

    return f"def boolean_function({', '.join(parameters)}):\n" + "    " + function_str.replace("\n", "\n    ")


# TODO
def evaluate_path(path_values):
    return

# if __name__ == '__main__':
#    build_bin_tree(["x", "y", "z"])