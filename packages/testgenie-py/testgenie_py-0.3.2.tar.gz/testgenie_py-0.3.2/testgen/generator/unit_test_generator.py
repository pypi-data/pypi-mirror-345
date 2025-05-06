from testgen.util.file_utils import get_import_info
from testgen.generator.test_generator import TestGenerator
from testgen.models.generator_context import GeneratorContext

AST_STRAT = 1
FUZZ_STRAT = 2
RANDOM_STRAT = 3

class UnitTestGenerator(TestGenerator):
    def __init__(self, generator_context: GeneratorContext):
        super().__init__(generator_context)
        self.test_code = []

    def generate_test_header(self):

        import_info = get_import_info(self._generator_context.filepath)

        self.test_code.append("import unittest\n")
        if self._generator_context.class_name == "" or self._generator_context.class_name is None:
            if import_info['is_package']:
                self.test_code.append(f"import {import_info['import_path']} as {self._generator_context.module.__name__}\n")
            else:
                self.test_code.append(f"import {import_info['import_path']} as {self._generator_context.module.__name__}\n")
        else:
            if import_info['is_package']:
                self.test_code.append(f"from {import_info['import_path']} import {self._generator_context.class_name}\n")
            else:
                self.test_code.append(f"from {import_info['import_path']} import {self._generator_context.class_name}\n")
        self.test_code.append(f"class Test{self._generator_context.class_name}(unittest.TestCase):  \n")

    def generate_test_function(self, unique_func_name, func_name, cases):
        print(f"Cases: {cases}")
        self.test_code.append(f"   def test_{unique_func_name}(self):")
        for inputs, expected in cases:
            args_str: str = self.generate_args_statement(inputs)
            expected_str: str = self.generate_expected_statement(expected)
            is_class: bool = self._generator_context.class_name != "" and self._generator_context.class_name is not None
            class_or_mod_name: str = self.generate_class_or_mod_name(is_class)
            result_statement: str = self.generate_result_statement(class_or_mod_name, func_name, inputs)
            assert_statement: str = self.generate_assert_statement()


            self.test_code.append(args_str)
            self.test_code.append(expected_str)
            self.test_code.append(result_statement)
            self.test_code.append(assert_statement)

    def save_file(self):
        with open(self._generator_context.output_path, "w") as f:
            f.write("\n".join(self.test_code))

    def generate_class_or_mod_name(self, is_class: bool) -> str:
        if is_class:
            return f"{self._generator_context.class_name}()"
        else:
            return f"{self._generator_context.module.__name__}"

    @staticmethod
    def generate_args_statement(inputs) -> str:
        input_args = ', '.join(map(repr, inputs))
        if len(inputs) == 1:
            return f"      args = {input_args}"
        else:
            return f"      args = ({input_args})"

    @staticmethod
    def generate_expected_statement(expected) -> str:
        if isinstance(expected, str):
            return f"      expected = '{expected}'"
        else:
            return f"      expected = {expected}"
        

    @staticmethod
    def generate_result_statement(class_or_mod_name, func_name, inputs) -> str:
        if len(inputs) == 1:
            return f"      result = {class_or_mod_name}.{func_name}(args)"
        else:
            return f"      result = {class_or_mod_name}.{func_name}(*args)"

    @staticmethod
    def generate_assert_statement() -> str:
        return f"      self.assertEqual(result, expected)\n"

