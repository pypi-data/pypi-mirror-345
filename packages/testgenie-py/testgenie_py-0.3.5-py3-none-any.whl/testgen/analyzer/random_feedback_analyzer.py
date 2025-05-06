import ast
import importlib
import random
import time
import traceback
from typing import List, Dict, Set
import z3

import testgen.util.randomizer
import testgen.util.utils as utils
import testgen.util.coverage_utils as coverage_utils
from testgen.analyzer.contracts.contract import Contract
from testgen.analyzer.contracts.no_exception_contract import NoExceptionContract
from testgen.analyzer.contracts.nonnull_contract import NonNullContract
from testgen.models.test_case import TestCase
from testgen.analyzer.test_case_analyzer import TestCaseAnalyzerStrategy
from abc import ABC

from testgen.models.function_metadata import FunctionMetadata
from testgen.util.z3_utils.constraint_extractor import extract_branch_conditions
from testgen.util.z3_utils.ast_to_z3 import ast_to_z3_constraint


# Citation in which this method and algorithm were taken from:
# C. Pacheco, S. K. Lahiri, M. D. Ernst and T. Ball, "Feedback-Directed Random Test Generation," 29th International
# Conference on Software Engineering (ICSE'07), Minneapolis, MN, USA, 2007, pp. 75-84, doi: 10.1109/ICSE.2007.37.
# keywords: {System testing;Contracts;Object oriented modeling;Law;Legal factors;Open source software;Software
# testing;Feedback;Filters;Error correction codes},

class RandomFeedbackAnalyzer(TestCaseAnalyzerStrategy, ABC):
    def __init__(self, analysis_context=None):
        super().__init__(analysis_context)
        self.test_cases = []
        self.covered_lines: Dict[str, Set[int]] = {}
        self.covered_functions: Set[str] = set()

    def collect_test_cases(self, function_metadata: FunctionMetadata, time_limit: int = 5) -> List[TestCase]:
        self.test_cases = []
        start_time = time.time()
        
        while (time.time() - start_time) < time_limit:
            
            try:
                param_values = self.generate_random_inputs(function_metadata.params)
                module = self.analysis_context.module
                func_name = function_metadata.function_name
                
                if self._analysis_context.class_name:
                    cls = getattr(module, self._analysis_context.class_name)
                    obj = cls()
                    function = getattr(obj, func_name)
                else:
                    function = getattr(module, func_name)
                
                import inspect
                sig = inspect.signature(function)
                param_names = [p.name for p in sig.parameters.values() if p.name != 'self']
                
                ordered_args = []
                for name in param_names:
                    if name in param_values:
                        ordered_args.append(param_values[name])
                    else:
                        ordered_args.append(None)
                
                result = function(*ordered_args)
                test_case = TestCase(func_name, tuple(ordered_args), result)

                if not self.is_duplicate_test_case(test_case):
                    self.test_cases.append(test_case)
                
                    covered = self.covered(function_metadata)
                    if covered:
                        break
                else:
                    # Optionally log duplicate detection
                    self.logger.debug(f"Skipping duplicate test case: {func_name}{test_case.inputs}")
                            
            except Exception as e:
                print(f"Error testing {function_metadata.function_name}: {e}")

        return self.test_cases
    
    def is_duplicate_test_case(self, new_test_case: TestCase) -> bool:
        for existing_test_case in self.test_cases:
            if (existing_test_case.func_name == new_test_case.func_name and
                existing_test_case.inputs == new_test_case.inputs):
                return True
        return False

    def covered(self, func: FunctionMetadata) -> bool:
        if func.function_name not in self.covered_lines:
            self.covered_lines[func.function_name] = set()

        for test_case in [tc for tc in self.test_cases if tc.func_name == func.function_name]:
            analysis = coverage_utils.get_coverage_analysis(self._analysis_context.filepath, self._analysis_context.class_name,
                                                                         func.function_name, test_case.inputs)
            covered = coverage_utils.get_list_of_covered_statements(analysis)
            self.covered_lines[func.function_name].update(covered)
            self.logger.debug(f"Covered lines for {func.function_name}: {self.covered_lines[func.function_name]}")

        executable_statements = set(self.get_all_executable_statements(func))
        self.logger.debug(f"Executable statements for {func.function_name}: {executable_statements}")

        return self.covered_lines[func.function_name] == executable_statements

    def execute_sequence(self, sequence, contracts: List[Contract]):
        """Execute a sequence and check contract violations"""
        func_name, args_dict = sequence
        args = tuple(args_dict.values())  # Convert dict values to tuple

        try:
            # Use module from analysis context if available
            module = self.analysis_context.module

            if self._analysis_context.class_name:
                cls = getattr(module, self._analysis_context.class_name, None)
                if cls is None:
                    raise AttributeError(f"Class '{self._analysis_context.class_name}' not found")
                obj = cls()  # Instantiate the class
                func = getattr(obj, func_name, None)

                import inspect
                sig = inspect.signature(func)
                param_names = [p.name for p in sig.parameters.values() if p.name != 'self']
            else:
                func = getattr(module, func_name, None)

                import inspect
                sig = inspect.signature(func)
                param_names = [p.name for p in sig.parameters.values()]

            # Create ordered arguments based on function signature
            ordered_args = []
            for name in param_names:
                if name in args_dict:
                    ordered_args.append(args_dict[name])

            # Check preconditions
            for contract in contracts:
                if not contract.check_preconditions(tuple(ordered_args)):
                    print(f"Preconditions failed for {func_name} with {tuple(ordered_args)}")
                    return None, True

            # Execute function with properly ordered arguments
            output = func(*ordered_args)
            exception = None

        except Exception as e:
            print(f"EXCEPTION IN RANDOM FEEDBACK: {e}")
            print(traceback.format_exc())
            output = None
            exception = e

        # Check postconditions
        for contract in contracts:
            if not contract.check_postconditions(tuple(ordered_args), output, exception):
                print(f"Postcondition failed for {func_name} with {tuple(ordered_args)}")
                return output, True

        return output, False
    

    # TODO: Currently only getting random vals of primitives, extend to sequences
    def random_seqs_and_vals(self, param_types, non_error_seqs=None):
        return self.generate_random_inputs(param_types)

    @staticmethod
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

    @staticmethod
    def generate_random_inputs(param_types):
        """Generate inputs for fuzzing based on parameter types."""
        inputs = {}
        for param, param_type in param_types.items():
            if param_type == "int":
                random_integer = random.randint(-500, 500)  # Wider range for better edge cases
                inputs[param] = random_integer
            elif param_type == "bool":
                random_choice = random.choice([True, False])
                inputs[param] = random_choice
            elif param_type == "float":
                random_float = random.uniform(-500.0, 500.0)  # Wider range for better edge cases
                inputs[param] = random_float
            elif param_type == "str":
                # Generate diverse strings instead of always "abc"
                string_type = random.choice([
                    "empty", "short", "medium", "long", "special", "numeric", "whitespace"
                ])
                
                if string_type == "empty":
                    inputs[param] = ""
                elif string_type == "short":
                    inputs[param] = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(1, 3)))
                elif string_type == "medium":
                    inputs[param] = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(4, 10)))
                elif string_type == "long":
                    inputs[param] = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(11, 30)))
                elif string_type == "special":
                    inputs[param] = ''.join(random.choices('!@#$%^&*()_+-=[]{}|;:,./<>?', k=random.randint(1, 8)))
                elif string_type == "numeric":
                    inputs[param] = ''.join(random.choices('0123456789', k=random.randint(1, 10)))
                else:  # whitespace
                    inputs[param] = ' ' * random.randint(1, 5)
            else:
                # For unknown types, try a default value
                inputs[param] = None
                
        return inputs
    
    # Algorithm described in above article
    # Classes is the classes for which we want to generate sequences
    # Contracts express invariant properties that hold both at entry and exit from a call
        # Contract takes as input the current state of the system (runtime values created in the sequence so far, and any exception thrown by the last call), and returns satisfied or violated
        # Output is the runtime values and boolean flag violated
    # Filters determine which values of a sequence are extensible and should be used as inputs
    def generate_sequences(self, function_metadata: List[FunctionMetadata], classes=None, contracts: List[Contract] = None, filters=None, time_limit=20):
        contracts = [NonNullContract(), NoExceptionContract()]
        error_seqs = [] # execution violates a contract
        non_error_seqs = [] # execution does not violate a contract

        functions = self._analysis_context.function_data
        start_time = time.time()
        while(time.time() - start_time) >= time_limit:
            # Get random function
            func = random.choice(functions)
            param_types: dict = func.params
            vals: dict = self.random_seqs_and_vals(param_types)
            new_seq = (func.function_name, vals)
            if new_seq in error_seqs or new_seq in non_error_seqs:
                continue
            outs_violated: tuple = self.execute_sequence(new_seq, contracts)
            violated: bool = outs_violated[1]
            # Create tuple of sequence ((func name, args), output)
            new_seq_out = (new_seq, outs_violated[0])
            if violated:
                error_seqs.append(new_seq_out)
            else:
                # Question: Should I use the failed contract to be the assertion in unit test??
                non_error_seqs.append(new_seq_out)
        return error_seqs, non_error_seqs

    def generate_sequences_new(self, contracts: List[Contract] = None, filters=None, time_limit=20):
        contracts = [NonNullContract(), NoExceptionContract()]
        error_seqs = []  # execution violates a contract
        non_error_seqs = []  # execution does not violate a contract

        functions = self._analysis_context.function_data.copy()
        start_time = time.time()

        while (time.time() - start_time) < time_limit:
            # Get random function
            func = random.choice(functions)
            param_types: dict = func.params
            vals: dict = self.random_seqs_and_vals(param_types)
            new_seq = (func.function_name, vals)

            if new_seq in [seq[0] for seq in error_seqs] or new_seq in [seq[0] for seq in non_error_seqs]:
                continue

            outs_violated: tuple = self.execute_sequence(new_seq, contracts)
            violated: bool = outs_violated[1]

            # Create tuple of sequence ((func name, args), output)
            new_seq_out = (new_seq, outs_violated[0])

            if violated:
                error_seqs.append(new_seq_out)

            else:
                non_error_seqs.append(new_seq_out)

            test_case = TestCase(new_seq_out[0][0], tuple(new_seq_out[0][1].values()), new_seq_out[1])
            self.test_cases.append(test_case)
            fully_covered = self.covered(func)
            if fully_covered:
                print(f"Function {func.function_name} is fully covered")
                functions.remove(func)

            if not functions:
                self.test_cases.sort(key=lambda tc: tc.func_name)
                print("All functions covered")
                break

        self.test_cases.sort(key=lambda tc: tc.func_name)
        return error_seqs, non_error_seqs
    
    def get_all_executable_statements(self, func: FunctionMetadata):
        import ast

        test_cases = [tc for tc in self.test_cases if tc.func_name == func.function_name]

        if not test_cases:
            print("Warning: No test cases available to determine executable statements")
            from testgen.util.randomizer import new_random_test_case
            temp_case = new_random_test_case(self._analysis_context.filepath, func.func_def)
            analysis = coverage_utils.get_coverage_analysis(self._analysis_context.filepath, self._analysis_context.class_name, func.function_name,
                                                                         temp_case.inputs)
        else:
            analysis = coverage_utils.get_coverage_analysis(self._analysis_context.filepath, self._analysis_context.class_name, func.function_name, test_cases[0].inputs)

        executable_lines = list(analysis[1])

        with open(self._analysis_context.filepath, 'r') as f:
            source = f.read()

        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func.func_def.name:
                for if_node in ast.walk(node):
                    if isinstance(if_node, ast.If) and if_node.orelse:
                        if isinstance(if_node.orelse[0], ast.If):
                            continue
                        else_line = if_node.orelse[0].lineno - 1

                        with open(self._analysis_context.filepath, 'r') as f:
                            lines = f.readlines()
                            if else_line <= len(lines):
                                line_content = lines[else_line - 1].strip()
                                if line_content == "else:":
                                    if else_line not in executable_lines:
                                        executable_lines.append(else_line)

        return sorted(executable_lines)

    """
    def collect_test_cases_with_z3(self, function_metadata: FunctionMetadata) -> List[TestCase]:
        test_cases = []
        
        z3_test_cases = self.generate_z3_test_cases(function_metadata)
        if z3_test_cases:
            test_cases.extend(z3_test_cases)
        
        if not test_cases:
            test_cases = self.generate_sequences_new()[1]
        
        self.test_cases = test_cases
        return test_cases

    def generate_z3_test_cases(self, function_metadata: FunctionMetadata) -> List[TestCase]:
        test_cases = []
        
        branch_conditions, param_types = extract_branch_conditions(function_metadata.func_def)
        
        if not branch_conditions:
            random_inputs = self.generate_random_inputs(function_metadata.params)
            try:
                module = self.analysis_context.module
                func_name = function_metadata.function_name
                
                if self._analysis_context.class_name:
                    cls = getattr(module, self._analysis_context.class_name)
                    obj = cls()
                    func = getattr(obj, func_name)
                    ordered_args = self._order_arguments(func, random_inputs)
                    output = func(*ordered_args)
                else:
                    func = getattr(module, func_name)
                    ordered_args = self._order_arguments(func, random_inputs)
                    output = func(*ordered_args)
                
                test_cases.append(TestCase(func_name, tuple(ordered_args), output))
            except Exception as e:
                print(f"Error executing function with random inputs: {e}")
            
            return test_cases
        
        for branch_condition in branch_conditions:
            try:
                z3_expr, z3_vars = ast_to_z3_constraint(branch_condition, function_metadata.params)
                
                solver = z3.Solver()
                solver.add(z3_expr)
                
                neg_solver = z3.Solver()
                neg_solver.add(z3.Not(z3_expr))
                
                for current_solver in [solver, neg_solver]:
                    if current_solver.check() == z3.sat:
                        model = current_solver.model()
                        
                        param_values = self._extract_z3_solution(model, z3_vars, function_metadata.params)
                        
                        ordered_params = self._order_parameters(function_metadata.func_def, param_values)
                        
                        try:
                            module = self.analysis_context.module
                            func_name = function_metadata.function_name
                            
                            if self._analysis_context.class_name:
                                cls = getattr(module, self._analysis_context.class_name)
                                obj = cls()
                                func = getattr(obj, func_name)
                            else:
                                func = getattr(module, func_name)
                                
                            result = func(*ordered_params)
                            test_cases.append(TestCase(func_name, tuple(ordered_params), result))
                        except Exception as e:
                            print(f"Error executing function with Z3 solution: {e}")
                            self._add_random_test_case(function_metadata, test_cases)
                    else:
                        self._add_random_test_case(function_metadata, test_cases)
                        
            except Exception as e:
                print(f"Error processing branch condition with Z3: {e}")
                self._add_random_test_case(function_metadata, test_cases)
        
        return test_cases
    
    def _extract_z3_solution(self, model, z3_vars, param_types):
        param_values = {}
        
        for var_name, z3_var in z3_vars.items():
            if var_name in param_types:
                try:
                    model_value = model.evaluate(z3_var)
                    
                    if param_types[var_name] == "int":
                        param_values[var_name] = model_value.as_long()
                    elif param_types[var_name] == "float":
                        param_values[var_name] = float(model_value.as_decimal(10))
                    elif param_types[var_name] == "bool":
                        param_values[var_name] = z3.is_true(model_value)
                    elif param_types[var_name] == "str":
                        str_val = str(model_value)
                        if str_val.startswith('"') and str_val.endswith('"'):
                            str_val = str_val[1:-1]
                        param_values[var_name] = str_val
                    else:
                        # Default to int for unrecognized types
                        param_values[var_name] = model_value.as_long()
                except Exception as e:
                    print(f"Couldn't get {var_name} from model: {e}")
                    # Use default values for parameters not in the model
                    if param_types[var_name] == "int":
                        param_values[var_name] = 0
                    elif param_types[var_name] == "float":
                        param_values[var_name] = 0.0
                    elif param_types[var_name] == "bool":
                        param_values[var_name] = False
                    elif param_types[var_name] == "str":
                        param_values[var_name] = ""
                    else:
                        param_values[var_name] = None
        
        return param_values
    
    def _order_parameters(self, func_node, param_values):
        ordered_params = []
        
        for arg in func_node.args.args:
            arg_name = arg.arg
            if arg_name == 'self':  # Skip self parameter
                continue
            if arg_name in param_values:
                ordered_params.append(param_values[arg_name])
            else:
                # Default value handling if parameter not in solution
                if arg.annotation and hasattr(arg.annotation, 'id'):
                    if arg.annotation.id == 'int':
                        ordered_params.append(0)
                    elif arg.annotation.id == 'float':
                        ordered_params.append(0.0)
                    elif arg.annotation.id == 'bool':
                        ordered_params.append(False)
                    elif arg.annotation.id == 'str':
                        ordered_params.append('')
                    else:
                        ordered_params.append(None)
                else:
                    ordered_params.append(None)
        
        return ordered_params
    
    def _order_arguments(self, func, args_dict):
        import inspect
        sig = inspect.signature(func)
        param_names = [p.name for p in sig.parameters.values() if p.name != 'self']
        
        ordered_args = []
        for name in param_names:
            if name in args_dict:
                ordered_args.append(args_dict[name])
            else:
                ordered_args.append(None)  # Default to None if missing
        
        return ordered_args
    
    def _add_random_test_case(self, function_metadata, test_cases):
        random_inputs = self.generate_random_inputs(function_metadata.params)
        try:
            module = self.analysis_context.module
            func_name = function_metadata.function_name
            
            if self._analysis_context.class_name:
                cls = getattr(module, self._analysis_context.class_name)
                obj = cls()
                func = getattr(obj, func_name)
            else:
                func = getattr(module, func_name)
            
            ordered_args = self._order_arguments(func, random_inputs)
            
            output = func(*ordered_args)
            test_cases.append(TestCase(func_name, tuple(ordered_args), output))
        except Exception as e:
            print(f"Error executing function with random inputs: {e}")
    """