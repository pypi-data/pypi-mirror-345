from types import ModuleType
from typing import List

from testgen.models.function_metadata import FunctionMetadata


class AnalysisContext:
    def __init__(self, filepath: str, filename: str, class_name: str, module: ModuleType, function_data: List[FunctionMetadata] = None):
        self._filepath: str = filepath
        self._filename: str = filename
        self._class_name: str = class_name
        self._module: ModuleType = module
        self._function_data: List[FunctionMetadata] = function_data

    @property
    def filepath(self) -> str:
        return self._filepath

    @filepath.setter
    def filepath(self, value: str):
        self._filepath = value

    @property
    def filename(self) -> str:
        return self._filename
    
    @filename.setter
    def filename(self, value: str):
        self._filename = value
    
    @property
    def class_name(self) -> str:
        return self._class_name
    
    @class_name.setter
    def class_name(self, value: str):
        self._class_name = value
    
    @property
    def module(self) -> ModuleType:
        return self._module
    
    @module.setter
    def module(self, value: ModuleType):
        self._module = value
    
    @property
    def function_data(self) -> List[FunctionMetadata]:
        return self._function_data
    
    @function_data.setter
    def function_data(self, value: List[FunctionMetadata]):
        self._function_data = value



