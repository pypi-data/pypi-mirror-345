import ast
from _ast import FunctionDef
from typing import List, Tuple
from testgen.util.z3_utils.branch_condition import BranchCondition
from testgen.util.z3_utils.variable_finder import VariableFinder

class ConstraintExtractor(ast.NodeVisitor):
    def __init__(self):
        self.branch_conditions = []
        self.current_function = None
        self.param_types = {}

    def visit_FunctionDef(self, node: FunctionDef):
        prev_function = self.current_function
        self.current_function = node.name

        for arg in node.args.args:
            if arg.arg != 'self' and arg.annotation:
                self.param_types[arg.arg] = ast.unparse(arg.annotation)
        
        self.generic_visit(node)
        self.current_function = prev_function

    def visit_If(self, node):
        variable_finder = VariableFinder()
        variable_finder.visit(node.test)
        variables = variable_finder.variables

        self.branch_conditions.append(BranchCondition(node.test, node.test.lineno, variables))

        self.generic_visit(node)

def extract_branch_conditions(func_node: ast.FunctionDef) -> Tuple[List[BranchCondition], dict]:
    extractor = ConstraintExtractor()
    extractor.visit(func_node)
    return extractor.branch_conditions, extractor.param_types
