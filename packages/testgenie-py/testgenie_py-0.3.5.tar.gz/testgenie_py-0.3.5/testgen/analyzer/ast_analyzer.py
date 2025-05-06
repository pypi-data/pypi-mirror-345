import ast
from typing import List

import testgen.util.file_utils
from testgen.models.test_case import TestCase
from testgen.analyzer.test_case_analyzer import TestCaseAnalyzerStrategy
from abc import ABC
from testgen.models.function_metadata import FunctionMetadata

class ASTAnalyzer(TestCaseAnalyzerStrategy, ABC):
    def __init__(self, analysis_context=None):
        super().__init__(analysis_context)

    def collect_test_cases(self, function_metadata: FunctionMetadata) -> List[TestCase]:
        """Collect test cases by analyzing AST conditions and return statements"""

        if function_metadata and function_metadata.params:
            param_names = list(function_metadata.params.keys())
        else:
            param_names = [arg.arg for arg in function_metadata.func_def.args.args
                           if arg.arg != 'self']

        test_cases: List[TestCase] = self.get_conditions_recursively(
            function_metadata,
            function_metadata.function_name,
            function_metadata.func_def.body,
            param_names)
        return test_cases

    def get_conditions_recursively(self, function_metadata: FunctionMetadata, func_name: str, func_node_body: list, param_names, test_cases=None, conditions=None) -> List[TestCase]:
        if conditions is None:
            conditions = []

        if test_cases is None:
            test_cases = []

        for node in func_node_body:
            if isinstance(node, ast.If):
                condition_str = self.parse_condition(node.test)
                self.logger.debug(f"Condition found in function: {condition_str}")
                self.get_conditions_recursively(function_metadata, func_name, node.body, param_names, test_cases, conditions + [condition_str])
                if node.orelse:
                    self.get_conditions_recursively(function_metadata, func_name, node.orelse, param_names, test_cases, conditions)

            elif isinstance(node, ast.Return):
                inputs = self.generate_inputs_from_conditions(conditions, param_names)
                
                input_exists = False
                for existing_test in test_cases:
                    if existing_test.func_name == func_name and existing_test.inputs == inputs:
                        input_exists = True
                        break
                    
                if not input_exists:
                    try:
                        generated_file = function_metadata.filename
                        module = testgen.util.file_utils.load_module(generated_file)
                        
                        if function_metadata.class_name:
                            cls = getattr(module, function_metadata.class_name)
                            instance = cls()
                            func = getattr(instance, func_name)
                            output = func(*inputs)
                        else:
                            func = getattr(module, func_name)
                            output = func(*inputs)
                        
                    except Exception as e:
                        print(f"Error executing function: {e}")
                        output = self._try_to_determine_output(node)
                    
                    test_case = TestCase(func_name, inputs, output)
                    test_cases.append(test_case)

        return test_cases

    def _try_to_determine_output(self, return_node):
        """Try different strategies to determine the output value"""
        try:
            # Try direct evaluation
            return ast.literal_eval(return_node.value)
        except (ValueError, SyntaxError):
            # Check for constants
            if isinstance(return_node.value, ast.Constant):
                return return_node.value.value
            # Check for name values
            elif isinstance(return_node.value, ast.Name):
                if return_node.value.id == 'True':
                    return True
                elif return_node.value.id == 'False':
                    return False
            # Default fallback
            return None

    @staticmethod
    def parse_condition(condition_node):
        """Parse an AST condition node into a string representation."""
        try:
            if isinstance(condition_node, ast.Compare):
                left = condition_node.left.id if isinstance(condition_node.left, ast.Name) else str(condition_node.left)
                op = type(condition_node.ops[0]).__name__
                right = condition_node.comparators[0].value if isinstance(condition_node.comparators[0], ast.Constant) else str(condition_node.comparators[0])
                return f"{left} {op} {right}"
            elif isinstance(condition_node, ast.BoolOp):
                # Use a simple representation for boolean operations
                return f"BoolOp({type(condition_node.op).__name__})"
            elif isinstance(condition_node, ast.UnaryOp):
                # Use a simple representation for unary operations
                return f"UnaryOp({type(condition_node.op).__name__})"
            elif isinstance(condition_node, ast.Name):
                return condition_node.id
            elif isinstance(condition_node, ast.Constant):
                return str(condition_node.value)
            
            return ast.dump(condition_node)
        except Exception as e:
            print(f"Error parsing condition: {e}")
            return "UnknownCondition"

    @staticmethod
    def generate_inputs_from_conditions(conditions, param_names):
        inputs = []

        # Create parameter values with more variety based on condition path
        param_values = {}

        # If no meaningful conditions were found, create varied inputs
        if not any(param in cond for cond in conditions for param in param_names):
            for i, param in enumerate(param_names):
                # Alternate True/False to create diverse test cases
                param_values[param] = (i % 2 == 0)
        else:
            # Start with all False
            param_values = {param: False for param in param_names}

            # Process each condition to extract parameter values
            for cond in conditions:
                for param in param_names:
                    if param in cond:
                        if "Eq True" in cond or "== True" in cond:
                            param_values[param] = True
                        elif "Eq False" in cond or "== False" in cond:
                            param_values[param] = False
                        elif f"Not({param})" in cond:
                            param_values[param] = False

        # Build the input tuple
        for param in param_names:
            inputs.append(param_values[param])

        return tuple(inputs)