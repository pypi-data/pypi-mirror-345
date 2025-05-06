import ast

class BranchCondition:
    def __init__(self, condition_ast, line_number, variables):
        self._condition_ast = condition_ast
        self._line_number = line_number
        self._variables = variables
        self._z3_expr = None
        
    @property
    def condition_ast(self):
        """Get the AST node representing the condition"""
        return self._condition_ast
    
    @condition_ast.setter
    def condition_ast(self, value):
        """Set the AST node representing the condition"""
        self._condition_ast = value
    
    @property
    def line_number(self):
        """Get the line number where this condition appears"""
        return self._line_number
    
    @line_number.setter
    def line_number(self, value):
        """Set the line number where this condition appears"""
        self._line_number = value
    
    @property
    def variables(self):
        """Get the variables used in this condition"""
        return self._variables
    
    @variables.setter
    def variables(self, value):
        """Set the variables used in this condition"""
        self._variables = value
    
    @property
    def z3_expr(self):
        """Get the Z3 expression for this condition"""
        return self._z3_expr
    
    @z3_expr.setter
    def z3_expr(self, value):
        """Set the Z3 expression for this condition"""
        self._z3_expr = value
    
    def __str__(self):
        """Return a string representation of this branch condition"""
        condition_text = ast.unparse(self.condition_ast) if self.condition_ast else "None"
        vars_text = ", ".join(sorted(self.variables)) if self.variables else "None"
        z3_text = str(self.z3_expr) if self.z3_expr else "None"
        
        return (f"BranchCondition(line={self.line_number}, "
                f"condition='{condition_text}', "
                f"variables=[{vars_text}], "
                f"z3_expr={z3_text})")
    
    def __repr__(self):
        """Return a string representation for debugging"""
        return self.__str__()
    
    def to_dict(self):
        """Convert this branch condition to a dictionary"""
        return {
            'line_number': self.line_number,
            'condition': ast.unparse(self.condition_ast) if self.condition_ast else None,
            'variables': sorted(list(self.variables)) if self.variables else [],
            'z3_expr': str(self.z3_expr) if self.z3_expr else None
        }