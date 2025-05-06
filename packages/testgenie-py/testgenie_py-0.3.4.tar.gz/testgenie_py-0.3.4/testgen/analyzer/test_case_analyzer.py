import ast
from abc import ABC, abstractmethod
from typing import List, Dict

from testgen.models.test_case import TestCase
from testgen.models.analysis_context import AnalysisContext
from testgen.models.function_metadata import FunctionMetadata
from testgen.service.logging_service import get_logger

class TestCaseAnalyzerStrategy(ABC):
    def __init__(self, analysis_context: AnalysisContext = None):
        self._analysis_context = analysis_context
        self.logger = get_logger()

    @abstractmethod
    def collect_test_cases(self, function_metadata: FunctionMetadata) -> List[TestCase]:
        pass

    def get_function_metadata(self, func_name: str) -> FunctionMetadata | None:
        if self._analysis_context and self._analysis_context.function_data:
            for func_metadata in self._analysis_context.function_data:
                if func_metadata.function_name == func_name:
                    return func_metadata
        return None

    def get_function_metadata_by_node(self, func_node: ast.FunctionDef) -> FunctionMetadata:
        return self.get_function_metadata(func_node.name)

    def get_param_types(self, func_node: ast.FunctionDef) -> Dict[str, str] | None:
        func_metadata = self.get_function_metadata_by_node(func_node)
        if func_metadata:
            return func_metadata.params

        return None

    @property
    def analysis_context(self) -> AnalysisContext:
        return self._analysis_context
        
    @analysis_context.setter
    def analysis_context(self, context: AnalysisContext):
        self._analysis_context = context
        

    

    

