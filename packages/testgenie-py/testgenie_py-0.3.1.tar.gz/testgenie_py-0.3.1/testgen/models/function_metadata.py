import ast
from types import ModuleType


class FunctionMetadata:
    def __init__(self, filename: str, module: ModuleType, class_name: str, function_name: str, func_def: ast.FunctionDef, params: dict):
        self._filename: str = filename
        self._module: ModuleType = module
        self._class_name: str = class_name
        self._function_name: str = function_name
        self._func_def: ast.FunctionDef = func_def
        self._params: dict = params
    
    @property
    def filename(self) -> str:
        return self._filename
    
    @filename.setter
    def filename(self, filename: str):
        self._filename = filename
    
    @property
    def module(self) -> ModuleType:
        return self._module
    
    @module.setter
    def module(self, module: ModuleType):
        self._module = module

    @property
    def class_name(self) -> str:
        return self._class_name
    
    @class_name.setter
    def class_name(self, class_name: str):
        self._class_name = class_name
    
    @property
    def function_name(self) -> str:
        return self._function_name
    
    @function_name.setter
    def function_name(self, func_name: str):
        self._function_name = func_name
    
    @property
    def func_def(self) -> ast.FunctionDef:
        return self._func_def
    
    @func_def.setter
    def func_def(self, func_def: ast.FunctionDef):
        self._func_def = func_def
    
    @property
    def params(self) -> dict:
        return self._params
    
    @params.setter
    def params(self, params: dict):
        self._params = params

