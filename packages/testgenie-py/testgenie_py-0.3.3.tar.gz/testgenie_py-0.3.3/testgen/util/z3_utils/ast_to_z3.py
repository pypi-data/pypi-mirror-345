import ast
from typing import Dict
import z3

class ASTToZ3(ast.NodeVisitor):
    def __init__(self, param_types: Dict[str, str]):
        self.param_types = param_types
        self.z3_vars = {}

    def create_z3_var(self, name: str, type_hint: str = None):
        if name in self.z3_vars:
            return self.z3_vars[name]
        
        if type_hint == "int" or type_hint is None:
            z3_var = z3.Int(name)
        elif type_hint == "float":
            z3_var = z3.Real(name)
        elif type_hint == "bool":
            z3_var = z3.Bool(name)
        elif type_hint == "str":
            z3_var = z3.String(name)
        else:
            z3_var = z3.Int(name)

        self.z3_vars[name] = z3_var
        return z3_var
    
    def visit_Name(self, node):
        if node.id in self.param_types:
            return self.create_z3_var(node.id, self.param_types[node.id])
        return self.create_z3_var(node.id)
    
    def visit_Constant(self, node):
        return node.value
    
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            return left / right
        elif isinstance(node.op, ast.Mod):
            return left % right
        else:
            raise NotImplementedError(f"Operation {node.op} not implemented")
        
    def visit_Compare(self, node):
        left = self.visit(node.left)

        result = None
        for i, (op, right) in enumerate(zip(node.ops, node.comparators)):
            right_val = self.visit(right)
            
            if isinstance(op, ast.Eq):
                condition = left == right_val
            elif isinstance(op, ast.NotEq):
                condition = left != right_val
            elif isinstance(op, ast.Lt):
                condition = left < right_val
            elif isinstance(op, ast.LtE):
                condition = left <= right_val
            elif isinstance(op, ast.Gt):
                condition = left > right_val
            elif isinstance(op, ast.GtE):
                condition = left >= right_val

            if result is None:
                result = condition
            else:
                result = z3.And(result, condition)

        return result
    
    def visit_BoolOp(self, node):
        values = [self.visit(value) for value in node.values]

        if isinstance(node.op, ast.And):
            return z3.And(*values)
        elif isinstance(node.op, ast.Or):
            return z3.Or(*values)
        else:
            raise NotImplementedError(f"Operation {node.op} not implemented")
        
    def convert(self, ast_node):
        return self.visit(ast_node)
    
def ast_to_z3_constraint(branch_condition, param_types):
    converter = ASTToZ3(param_types)
    z3_expr = converter.convert(branch_condition.condition_ast)
    branch_condition.z3_expr = z3_expr
    return z3_expr, converter.z3_vars
    
    