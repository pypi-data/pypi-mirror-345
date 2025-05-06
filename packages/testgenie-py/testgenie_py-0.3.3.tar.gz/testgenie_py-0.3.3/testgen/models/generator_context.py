from types import ModuleType
from typing import List

from testgen.models.test_case import TestCase


class GeneratorContext:
    def __init__(self, filepath: str, filename: str, class_name:str | None, module: ModuleType, output_path: str, test_cases: List[TestCase]):
        self._filepath: str = filepath
        self._filename: str = filename
        self._class_name: str = class_name
        self._module: ModuleType = module
        self._output_path: str = output_path
        self._test_cases: List[TestCase] = test_cases
    
    @property
    def filepath(self) -> str:
        return self._filepath
    
    @filepath.setter
    def filepath(self, value: str) -> None:
        self._filepath = value
    
    @property
    def filename(self) -> str:
        return self._filename
    
    @filename.setter
    def filename(self, value: str) -> None:
        self._filename = value
    
    @property
    def class_name(self) -> str | None:
        return self._class_name
    
    @class_name.setter
    def class_name(self, value: str | None) -> None:
        self._class_name = value
    
    @property
    def module(self) -> ModuleType:
        return self._module
    
    @module.setter
    def module(self, value: ModuleType) -> None:
        self._module = value
    
    @property
    def output_path(self) -> str:
        return self._output_path
    
    @output_path.setter
    def output_path(self, value: str) -> None:
        self._output_path = value
    
    @property
    def test_cases(self) -> List[TestCase]:
        return self._test_cases
    
    @test_cases.setter
    def test_cases(self, value: List[TestCase]) -> None:
        self._test_cases = value

