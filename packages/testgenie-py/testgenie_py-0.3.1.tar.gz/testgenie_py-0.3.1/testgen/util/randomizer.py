import ast
import random
import string
from types import ModuleType
from typing import List

import testgen.util.coverage_utils
import testgen.util.file_utils
import testgen.util.utils as utils
# import testgen.util.z3_test_case
try:
    from testgen.util.z3_utils.z3_test_case import solve_branch_condition
except ImportError:
    print("ERROR IMPORTING Z3 TEST CASE")
    solve_branch_condition = None
from testgen.models.test_case import TestCase

def make_random_move(file_name: str, class_name: str | None, func_node: ast.FunctionDef, test_cases: List[TestCase]) -> List[TestCase]:
    random_choice = random.randint(1, 4)
    func_name = func_node.name
    # new random test case
    if random_choice == 1:
        test_cases.append(new_random_test_case(file_name, class_name, func_node))
    # combine test cases
    if random_choice == 2:
        test_cases.append(combine_cases(test_cases))
    # delete test case
    if random_choice == 3:
        test_cases = remove_case(test_cases)

    if random_choice == 4:
        # TODO: Not sure what to use for test case args/inputs i.e. test_cases[0].inputs is WRONG
        function_test_cases = [tc for tc in test_cases if tc.func_name == func_name]

        if function_test_cases:
            uncovered_lines = testgen.util.coverage_utils.get_uncovered_lines_for_func(file_name, class_name, func_name)

        if len(uncovered_lines) > 0:
            z3_test_cases = solve_branch_condition(file_name, func_node, uncovered_lines)
            test_cases.extend(z3_test_cases)

    return test_cases

def new_random_test_case(file_name: str, class_name: str | None, func_node: ast.FunctionDef) -> TestCase:
    func_name = func_node.name
    param_types: dict = utils.extract_parameter_types(func_node)

    if class_name is not None and 'self' in param_types:
        del param_types['self']

    inputs: dict = utils.generate_random_inputs(param_types)
    args = list(inputs.values())

    module = testgen.util.file_utils.load_module(file_name)

    try:
        if class_name is not None:
            class_obj = getattr(module, class_name)
            instance = class_obj()
            func = getattr(instance, func_name)
        else:
            func = getattr(module, func_name)

        output = func(*args)

        return TestCase(func_name, tuple(args), output)
    except Exception as e:
        print(f"Error generating test case for {func_name}: {e}")
        raise

def combine_cases(module: ModuleType, test_cases: List[TestCase]) -> TestCase:
    """Combine two test cases by mixing their inputs and calculating the new expected output."""
    if not test_cases:
        raise ValueError("Cannot combine cases with empty test case list")
    
    random_index1 = random.randint(0, len(test_cases) - 1)
    test_case1 = test_cases[random_index1]
    
    test_cases_of_the_same_function = [tc for tc in test_cases if tc.func_name == test_case1.func_name]
    if len(test_cases_of_the_same_function) <= 1:
        return test_case1  # Not enough cases to combine
    
    filtered_cases = [tc for tc in test_cases_of_the_same_function if tc != test_case1]
    if not filtered_cases:
        random_index2 = random.randint(0, len(test_cases_of_the_same_function) - 1)
        test_case2 = test_cases_of_the_same_function[random_index2]
    else:
        test_case2 = random.choice(filtered_cases)
    
    mixed_inputs = mix_inputs(test_case1, test_case2)
    
    try:
        
        func = getattr(module, test_case1.func_name)
        
        new_expected = func(*mixed_inputs)
        
        return TestCase(test_case1.func_name, mixed_inputs, new_expected)
    
    except Exception as e:
        print(f"Error calculating expected output for combined test case: {e}")
        return test_case1 if random.choice([True, False]) else test_case2

def remove_case(test_cases: List[TestCase]) -> List[TestCase]:
    random_index = random.randint(0, len(test_cases) - 1)
    del test_cases[random_index]
    return test_cases

def mix_inputs(test_case1: TestCase, test_case2: TestCase) -> tuple:
    len1 = len(test_case1.inputs)
    len2 = len(test_case2.inputs)

    if len1 != len2:
        raise ValueError("Test cases must have the same number of inputs")

    half = len1 // 2

    new_inputs = test_case1.inputs[:half] + test_case2.inputs[half:]

    return new_inputs

def get_z3_test_cases(file_name: str, class_name: str | None, func_node: ast.FunctionDef, test_cases: List[TestCase]) -> List[TestCase]:
    func_name = func_node.name
    
    # Filter test cases for this specific function
    function_test_cases = [tc for tc in test_cases if tc.func_name == func_name]
    
    if not function_test_cases:
        initial_case = new_random_test_case(file_name, class_name, func_node)
        test_cases.append(initial_case)
        function_test_cases = [initial_case]
    
    try:
        # Get uncovered lines
        uncovered_lines = testgen.util.coverage_utils.get_uncovered_lines_for_func(file_name, class_name, func_node, function_test_cases)

        if uncovered_lines:
            if solve_branch_condition:
                # Call the Z3 solver with uncovered lines
                z3_cases = solve_branch_condition(file_name, class_name, func_node, uncovered_lines)
                if z3_cases:
                    test_cases.extend(z3_cases)
                else:
                    print("Z3 couldn't solve branch conditions")
            else:
                print("Z3 solver not available (solve_branch_condition is None)")
        else:
            print("No uncovered lines found for Z3 to solve")
    except Exception as e:
        print(f"Error in Z3 test generation: {e}")
        import traceback
        traceback.print_exc()
    
    return test_cases