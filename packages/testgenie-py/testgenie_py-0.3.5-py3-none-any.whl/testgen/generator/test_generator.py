from abc import ABC, abstractmethod
from testgen.models.generator_context import GeneratorContext

class TestGenerator(ABC):
    def __init__(self, generator_context: GeneratorContext):
        self._generator_context = generator_context

    @property
    def generator_context(self) -> GeneratorContext:
        return self._generator_context

    @generator_context.setter
    def generator_context(self, value: GeneratorContext):
        self._generator_context = value

    @abstractmethod
    def generate_test_header(self):
        pass

    @abstractmethod
    def generate_test_function(self, unique_func_name, func_name, cases):
        pass

    @abstractmethod
    def save_file(self):
        pass