import time
from typing import List

from testgen.analyzer.test_case_analyzer import TestCaseAnalyzerStrategy
from testgen.models.test_case import TestCase
from testgen.models.analysis_context import AnalysisContext


class TestCaseAnalyzerContext:
    def __init__(self, analysis_context: AnalysisContext, test_case_analyzer: TestCaseAnalyzerStrategy):
        self._test_case_analyzer = test_case_analyzer
        self._analysis_context = analysis_context
        self._test_cases = []
        
    # TODO: GET RID OF THIS STUPID METHOD IT IS POINTLESS
    # JUST CALL INSIDE ANALYZER_SERVICE
    def do_logic(self) -> List[TestCase]:
        """Run the analysis process"""
        self.do_strategy(20)

    def do_strategy(self, time_limit=None) -> List[TestCase]:
        """Execute the analysis strategy for all functions with an optional time limit"""
        start_time = time.time()
        for func_metadata in self._analysis_context.function_data:
            if time_limit and (time.time() - start_time) >= time_limit:
                break
            test_cases = self._test_case_analyzer.collect_test_cases(func_metadata)
            for test_case in test_cases:
                print(f"Test Case: {test_case.func_name}, {test_case.inputs}, {test_case.expected}")
            self._test_cases.extend(test_cases)

    @property
    def strategy(self) -> TestCaseAnalyzerStrategy:
        return self._test_case_analyzer

    @property
    def test_cases(self):
        return self._test_cases

    @strategy.setter
    def strategy(self, test_case_analyzer: TestCaseAnalyzerStrategy) -> None:
        self._test_case_analyzer = test_case_analyzer
        if self._analysis_context:
            self._test_case_analyzer.analysis_context = self._analysis_context

    @property
    def analysis_context(self) -> AnalysisContext:
        return self._analysis_context
    
    @analysis_context.setter
    def analysis_context(self, context: AnalysisContext) -> None:
        self._analysis_context = context
        if self._test_case_analyzer:
            self._test_case_analyzer.analysis_context = context

    


