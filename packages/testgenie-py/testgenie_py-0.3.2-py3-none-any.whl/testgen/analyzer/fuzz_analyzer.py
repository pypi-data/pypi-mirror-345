from abc import ABC
import os
import traceback
from typing import List

from atheris.native import FuzzedDataProvider

import coverage

from testgen.models.test_case import TestCase
from testgen.analyzer.test_case_analyzer import TestCaseAnalyzerStrategy

from testgen.models.function_metadata import FunctionMetadata

class FuzzAnalyzer(TestCaseAnalyzerStrategy, ABC):

    def __init__(self, analysis_context=None):
        super().__init__(analysis_context)
        self.coverage_tracker = coverage.Coverage(branch=True)
        self.executed_branches = set()

    # TODO: Use getattr() to get function in FunctionMetadata
    def collect_test_cases(self, function_metadata: FunctionMetadata) -> List[TestCase]:
        """Collect test cases using fuzzing techniques"""
        
        # Use module from function_metadata if available
        if function_metadata and function_metadata.module:
            module = self.analysis_context.module
        else:
            raise ValueError("Module not set in function metadata. Cannot perform fuzzing without a module.")
            
        class_name = function_metadata.class_name if function_metadata.class_name else None
        try:
            if not class_name is None:
                cls = getattr(module, class_name, None)
                func = getattr(cls(), function_metadata.function_name, None) if cls else None
            else:
                func = getattr(module, function_metadata.function_name, None)
            if func:
                return self.run_fuzzing(func, function_metadata.function_name, function_metadata.params, module, 10)
        except Exception as e:
            print(f"[FUZZ ANALYZER ERROR]: {e}")
            traceback.print_exc()
            return []

    def run_fuzzing(self, func, func_name, param_types, module, iterations=10) -> List[TestCase]:
        """Run the function with fuzzed inputs and collect failing test cases."""
        print(f"Running fuzzing {func_name}")
        test_cases = []

        for _ in range(iterations):
            fdp = FuzzedDataProvider(os.urandom(1024))
            inputs = self.generate_inputs_from_fuzz_data(fdp, param_types)

            self.coverage_tracker.erase()
            self.coverage_tracker.start()

            try:
                output = func(*inputs)
                self.coverage_tracker.stop()
                covered_branches = self.get_branch_coverage(module)
                covered_branches_tuple = tuple(covered_branches)

                self.logger.debug(f"[COVERED_BRANCHES]: {covered_branches}")
                self.logger.debug(f"[EXECUTED BRANCHES]: {self.executed_branches}")

                for branch in covered_branches:
                    if branch[1] < 0:
                        if covered_branches_tuple not in self.executed_branches:
                            self.executed_branches.add(covered_branches_tuple)
                            test_cases.append(TestCase(func_name, inputs, output))

            except Exception as e:
                self.coverage_tracker.stop()
                test_cases.append(TestCase(func_name, inputs, (type(e), str(e) + " EXCEPTION")))
        self.executed_branches.clear()
        return test_cases


    # TODO: Look into FuzzDataProvider.instrumentall()
    @staticmethod
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
    
    def get_branch_coverage(self, module):
        data = self.coverage_tracker.get_data()
        try:
            return data.arcs(module.__file__)
        except Exception as e:
            print(f"[ERROR: FUZZ ANALYZER] Couldn't get arcs Exception: {e}")
            return set()