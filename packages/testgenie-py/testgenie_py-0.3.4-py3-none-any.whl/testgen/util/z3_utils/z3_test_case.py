import ast
from typing import List

import z3

import testgen.util.file_utils
from testgen.models.test_case import TestCase
from testgen.util.z3_utils import ast_to_z3
from testgen.util.z3_utils.constraint_extractor import extract_branch_conditions


def solve_branch_condition(file_name: str, class_name: str | None, func_node: ast.FunctionDef, uncovered_lines: List[int]) -> List[TestCase]:
    branch_conditions, param_types = extract_branch_conditions(func_node)
    uncovered_conditions = [bc for bc in branch_conditions if bc.line_number in uncovered_lines]
    test_cases = []

    for branch_condition in uncovered_conditions:
        z3_expr, z3_vars = ast_to_z3.ast_to_z3_constraint(branch_condition, param_types)
        solver = z3.Solver()
        solver.add(z3_expr)

        if solver.check() == z3.sat:
            model = solver.model()

            # Create default values for all parameters
            param_values = {}
            for param_name in param_types:
                # Skip 'self' parameter for class methods
                if param_name == 'self':
                    continue
                    
                # Set default values based on type
                if param_types[param_name] == "int":
                    param_values[param_name] = 0
                elif param_types[param_name] == "float":
                    param_values[param_name] = 0.0
                elif param_types[param_name] == "bool":
                    param_values[param_name] = False
                elif param_types[param_name] == "str":
                    param_values[param_name] = ""
                else:
                    param_values[param_name] = None

            # Update with model values where available
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
                            param_values[var_name] = model[z3_var].as_long()
                    except Exception as e:
                        print(f"Couldn't get {var_name} from model: {e}")
                        # Keep the default value we already set

            # Ensure all parameters are included in correct order
            ordered_params = []
            for arg in func_node.args.args:
                arg_name = arg.arg
                if arg_name == 'self':  # Skip self parameter
                    continue
                if arg_name in param_values:
                    ordered_params.append(param_values[arg_name])
                else:
                    # Default value handling if parameter not in solution
                    if hasattr(arg, 'annotation') and arg.annotation:
                        if isinstance(arg.annotation, ast.Name):
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
                    else:
                        ordered_params.append(None)

            func_name = func_node.name
            try:
                module = testgen.util.file_utils.load_module(file_name)
                if class_name is not None:
                    class_obj = getattr(module, class_name)
                    instance = class_obj()
                    func = getattr(instance, func_name)
                else:
                    func = getattr(module, func_name)
                result = func(*ordered_params)
                test_cases.append(TestCase(func_name, tuple(ordered_params), result))
            except Exception as e:
                print(f"Error executing function with Z3 solution for {func_name}: {e}")

    return test_cases