import doctest
import importlib
import inspect
import json
import os
import re
import sqlite3
import sys
import time
import subprocess

import coverage
import testgen.util.coverage_utils as coverage_utils
from types import ModuleType
from typing import List

import testgen
import testgen.util.file_utils as file_utils

from testgen.models.test_case import TestCase
from testgen.service.analysis_service import AnalysisService
from testgen.service.generator_service import GeneratorService
from testgen.sqlite.db_service import DBService
from testgen.models.analysis_context import AnalysisContext
from testgen.service.logging_service import get_logger


# Constants for test strategies
AST_STRAT = 1
FUZZ_STRAT = 2
RANDOM_STRAT = 3
REINFORCE_STRAT = 4

# Constants for test formats
UNITTEST_FORMAT = 1
PYTEST_FORMAT = 2
DOCTEST_FORMAT = 3

class Service:
    def __init__(self):
        self.test_strategy: int = 0
        self.test_format: int = 0
        self.file_path = None
        self.generated_file_path = None
        self.class_name = None
        self.test_cases = []
        self.logger = get_logger()
        self.reinforcement_mode = "train"
        
        # Initialize specialized services
        self.analysis_service = AnalysisService()
        self.generator_service = GeneratorService(None, None, None)
        # Only initialize DB service if not running in Docker
        if os.environ.get("RUNNING_IN_DOCKER") is None:
            self.db_service = DBService()
        else:
            # Create a dummy DB service that doesn't do anything
            self.db_service = None

    def generate_test_cases(self) -> List[TestCase] | None:
        module = file_utils.load_module(self.file_path)
        class_name = self.analysis_service.get_class_name(module)

        if self.test_strategy == AST_STRAT:
            self.generated_file_path = self.generate_function_code()
            Service.wait_for_file(self.generated_file_path)
            self.analysis_service.set_file_path(self.generated_file_path)
            module = file_utils.load_module(self.generated_file_path)
            class_name = self.analysis_service.get_class_name(module)
            self.analysis_service.set_test_strategy(self.test_strategy, module.__name__, self.class_name)

        else:
            self.analysis_service.set_test_strategy(self.test_strategy, module.__name__, self.class_name)

        test_cases: List[TestCase] = []
        if self.test_strategy == REINFORCE_STRAT:
            test_cases = self.analysis_service.do_reinforcement_learning(self.file_path, class_name, self.reinforcement_mode)
        else:
            test_cases = self.analysis_service.generate_test_cases()

        if os.environ.get("RUNNING_IN_DOCKER") is not None:
            self.logger.debug(f"Serializing test cases {test_cases}")
            self.serialize_test_cases(test_cases)
            return None  # Exit early in analysis-only mode
        
        return test_cases

    def generate_tests(self, output_path=None):
        module = file_utils.load_module(self.file_path)
        class_name = self.analysis_service.get_class_name(module)

        test_cases = self.generate_test_cases()
        
        # Only process if we have test cases
        if test_cases is None:
            return None
            
        self.test_cases = test_cases

        # Only save to DB if not running in Docker
        if os.environ.get("RUNNING_IN_DOCKER") is None:
            file_path_to_use = self.generated_file_path if self.test_strategy == AST_STRAT else self.file_path
            self.db_service.save_test_generation_data(
                file_path_to_use,
                test_cases,
                self.test_strategy,
                class_name
            )

        test_file = self.generate_test_file(test_cases, output_path, module, class_name)

        # Ensure the test file is ready
        Service.wait_for_file(test_file)
        return test_file

    def generate_test_file(self, test_cases: List[TestCase], output_path: str | None = None,
                           module: ModuleType | None = None, class_name: str | None = None) -> str:
        if module is None:
            module = file_utils.load_module(self.file_path)
            class_name = self.analysis_service.get_class_name(module)

        if self.test_strategy == AST_STRAT:
            self.generator_service = GeneratorService(self.generated_file_path, output_path, self.test_format)
            self.generator_service.set_test_format(self.test_format)
            module = file_utils.load_module(self.generated_file_path)
        else:
            # Create the correct instance of the generator service
            self.generator_service = GeneratorService(self.file_path, output_path, self.test_format)
            self.generator_service.set_test_format(self.test_format)

        test_file = self.generator_service.generate_test_file(
            module,
            class_name,
            test_cases,
            output_path
        )

        print(f"Generated test file: {test_file}")

        # Ensure the test file is ready
        Service.wait_for_file(test_file)
        return test_file

    def generate_function_code(self):
        """Generate function code for a given class or module."""
        module = file_utils.load_module(self.file_path)
        class_name = self.analysis_service.get_class_name(module)
        functions = self.inspect_class(class_name)
        return self.generator_service.generate_function_code(self.file_path, class_name, functions)
    
    def run_coverage(self, test_file):
        """Run coverage analysis on the generated tests."""
        Service.wait_for_file(test_file)
        file_path_to_use = self.generated_file_path if self.test_strategy == AST_STRAT else self.file_path
        self.logger.debug(f"File path to use for coverage: {file_path_to_use}")
        coverage_output = ""
        
        try:
            if self.test_format == UNITTEST_FORMAT:
                 subprocess.run(["python", "-m", "coverage", "run", "--source=.", "-m", "unittest", test_file], check=True)
                 result = subprocess.run(
                     ["python", "-m", "coverage", "report", file_path_to_use], 
                     check=True, 
                     capture_output=True, 
                     text=True
                 )
                 coverage_output = result.stdout
                 print(coverage_output)
            elif self.test_format == PYTEST_FORMAT:
                self.execute_and_store_pytest(test_file)
            elif self.test_format == DOCTEST_FORMAT:
                self.execute_and_store_doctest(test_file)
            else:
                raise ValueError("Unsupported test format for test results.")

            #Run coverage analysis
            subprocess.run(["python", "-m", "coverage", "run", "--source=.", test_file], check=True)
            result = subprocess.run(["python", "-m", "coverage", "report", file_path_to_use], check=True, capture_output=True, text=True)
            self._save_coverage_data(coverage_output, file_path_to_use)
            coverage_output = result.stdout

            self._save_coverage_data(coverage_output, file_path_to_use)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running coverage subprocess: {e}")

    def _save_coverage_data(self, coverage_output, file_path):
        """Parse coverage output and save to database."""
        # Skip if running in Docker or DB service is None
        if os.environ.get("RUNNING_IN_DOCKER") is not None or self.db_service is None:
            self.logger.debug("Skipping database operations in Docker container")
            return
        
        try:
            lines = coverage_output.strip().split('\n')
            if not lines:
                raise ValueError("No coverage data found in the output.")
            else:
                for line in lines:
                    if file_path in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            file_name = os.path.basename(file_path)
                            try:
                                total_lines = int(parts[-3])
                                missed_lines = int(parts[-2])
                                executed_lines = total_lines - missed_lines
                                coverage_str = parts[-1].strip('%')
                                branch_coverage = float(coverage_str) / 100
                                
                                source_file_id = self._get_source_file_id(file_path)
                                
                                self.db_service.insert_coverage_data(
                                    file_name, 
                                    executed_lines, 
                                    missed_lines, 
                                    branch_coverage, 
                                    source_file_id
                                )
                                break
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing coverage data: {e}")
        except Exception as e:
            print(f"Error saving coverage data: {e}")
            
    def _get_source_file_id(self, file_path):
        """Helper to get source file ID from DB."""
        conn = sqlite3.connect(self.db_service.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM SourceFile WHERE path = ?", (file_path,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return row[0]
        else:
            with open(file_path, 'r') as f:
                lines_of_code = len(f.readlines())
            return self.db_service.insert_source_file(file_path, lines_of_code)

    def serialize_test_cases(self, test_cases):
        """Serialize input arguments ot JSON-compatible format"""
        print("##TEST_CASES_BEGIN##")
        serialized = []
        for tc in test_cases:
            case_data = {
                "func_name": tc.func_name,
                "inputs": self.serialize_value(tc.inputs),
                "expected": self.serialize_value(tc.expected)
            }
            serialized.append(case_data)
        print(json.dumps(serialized))
        print("##TEST_CASES_END##")

    def serialize_value(self, value):
        """Serialize a single value to a JSON-compatible format"""
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        elif isinstance(value, (list, tuple)):
            return [self.serialize_value(v) for v in value]
        else:
            return str(value)

    @staticmethod
    def parse_test_cases_from_logs(logs_output):
        """Extract and parse test cases from container logs"""
        pattern = r"##TEST_CASES_BEGIN##\n(.*?)\n##TEST_CASES_END##"
        match = re.search(pattern, logs_output, re.DOTALL)

        if not match:
            raise ValueError("Could not find test cases in the container logs")

        test_cases_json = match.group(1).strip()
        test_cases_data = json.loads(test_cases_json)

        test_cases: List[TestCase] = []
        for tc_data in test_cases_data:
            test_case = TestCase(
                func_name=tc_data["func_name"],
                inputs=tc_data["inputs"],
                expected=tc_data["expected"]
            )
            test_cases.append(test_case)

        return test_cases

    def set_file_path(self, path: str):
        """Set the file path for analysis and validate it."""
        print(f"Setting file path: {path}")
        if os.path.isfile(path) and path.endswith(".py"):
            self.file_path = path
            self.analysis_service.set_file_path(path)
        else:
            raise ValueError("Invalid file path! Please provide a valid Python file path.")

    def set_class_name(self, class_name: str):
        """Set the class name to analyze."""
        self.class_name = class_name

    def set_test_generator_format(self, test_format: int):
        """Set the test generator format."""
        self.test_format = test_format
        self.generator_service.set_test_format(test_format)

    def set_test_analysis_strategy(self, strategy: int):
        """Set the test analysis strategy."""
        self.test_strategy = strategy
        module = file_utils.load_module(self.file_path)
        self.analysis_service.set_test_strategy(strategy, module.__name__, self.class_name)
    
    def get_analysis_context(self, filepath: str) -> AnalysisContext:
        """Create an analysis context for the given file."""
        return self.analysis_service.create_analysis_context(filepath)

    def get_coverage(self, file_path: str):
        """
        Use the coverage library to calculate and print the coverage for the specified Python file.
        Dynamically determine the source directory based on the file being tested.
        """
        # Dynamically determine the source directory
        source_dir = os.path.dirname(file_path)
        cov = coverage.Coverage(source=[source_dir])  # Use the directory of the file as the source
        cov.start()

        try:
            # Dynamically import and execute the specified file
            file_name = os.path.basename(file_path)
            module_name = file_name.rstrip(".py")
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        except Exception as e:
            print(f"Error while executing the file: {e}")
            return

        finally:
            cov.stop()
            cov.save()

        # Report the coverage
        print(f"Coverage report for {file_path}:")
        cov.report(file=sys.stdout)

    @staticmethod
    def wait_for_file(file_path, retries=5, delay=1):
        """Wait for the generated file to appear."""
        while retries > 0 and not os.path.exists(file_path):
            time.sleep(delay)
            retries -= 1
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found after waiting.")

    def get_full_import_path(self) -> str:
        """Get the full import path for the current file."""
        package_root = self.find_package_root()
        if not package_root:
            raise ImportError(f"Could not determine the package root for {self.file_path}.")

        module_path = os.path.abspath(self.file_path)
        rel_path = os.path.relpath(module_path, package_root)
        package_path = rel_path.replace(os.sep, ".")
        
        if package_path.endswith(".py"):
            package_path = package_path[:-3]

        package_name = os.path.basename(package_root)
        if not package_path.startswith(package_name + "."):
            package_path = package_name + "." + package_path

        return package_path

    def find_package_root(self):
        """Find the package root directory."""
        current_dir = os.path.abspath(os.path.dirname(self.file_path))
        last_valid = None

        while current_dir:
            if "__init__.py" in os.listdir(current_dir):
                last_valid = current_dir
            else:
                break

            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                break
            current_dir = parent_dir

        return last_valid

    def inspect_class(self, class_name):
        """Inspect a class or module and return its functions."""
        module = file_utils.load_module(self.file_path)

        # Handle module-level functions when class_name is None
        if not class_name:
            # Get module-level functions
            functions = inspect.getmembers(module, inspect.isfunction)
            return functions

        # Handle class functions
        cls = getattr(module, class_name, None)
        if cls is None:
            raise ValueError(f"Class '{class_name}' not found in module '{module.__name__}'.")

        functions = inspect.getmembers(cls, inspect.isfunction)
        return functions

    def resolve_module_path(self, module_name):
        """Resolve a module name to its file path by checking multiple locations."""
        direct_path = f"/controller/{module_name}.py"
        if os.path.exists(direct_path):
            self.logger.debug(f"Found module at {direct_path}")
            return direct_path

        testgen_path = f"/controller/testgen/{module_name}.py"
        if os.path.exists(testgen_path):
            self.logger.debug(f"Found module at {testgen_path}")
            return testgen_path

        if '.' in module_name:
            parts = module_name.split('.')
            potential_path = os.path.join('/controller', *parts) + '.py'
            if os.path.exists(potential_path):
                self.logger.debug(f"Found module at {potential_path}")
                return potential_path

        self.logger.debug(f"Could not find module: {module_name}")
        return None

    def visualize_test_coverage(self):
        from testgen.service.cfg_service import CFGService
        cfg_service = CFGService()
        cfg_service.initialize_visualizer(self)

        return cfg_service.visualize_test_coverage(
            file_path=self.file_path,
            test_cases=self.test_cases,
        )

    def set_reinforcement_mode(self, mode: str):
        self.reinforcement_mode = mode
        if hasattr(self ,'analysis_service'):
            self.analysis_service.set_reinforcement_mode(mode)

    def _get_test_case_id(self, test_case_name: str) -> int:
        """
        Retrieve the test case ID from the database based on the test case name.
        Insert the test case if it does not exist.
        """
        if self.db_service is None:
            raise RuntimeError("Database service is not initialized.")

        # Query the database for the test case ID
        self.db_service.cursor.execute(
            "SELECT id FROM TestCase WHERE name = ?",
            (test_case_name,)
        )
        result = self.db_service.cursor.fetchone()

        if result:
            return result[0]  # Return the test case ID
        else:
            # Insert the test case into the database
            self.db_service.cursor.execute(
                "INSERT INTO TestCase (name) VALUES (?)",
                (test_case_name,)
            )
            self.db_service.conn.commit()
            return self.db_service.cursor.lastrowid

    def execute_and_store_pytest(self, test_file):
        import pytest
        from _pytest.reports import TestReport

        class PytestResultPlugin:
            def __init__(self, db_service, get_test_case_id):
                self.db_service = db_service
                self.get_test_case_id = get_test_case_id

            def pytest_runtest_logreport(self, report: TestReport):
                if report.when == "call":
                    test_case_id = self.get_test_case_id(report.nodeid)
                    status = report.outcome == "passed"
                    error_message = report.longreprtext if report.outcome == "failed" else None
                    self.db_service.insert_test_result(test_case_id, status, error_message)

        pytest.main([test_file], plugins=[PytestResultPlugin(self.db_service, self._get_test_case_id)])

        pytest.main([test_file])

    def execute_and_store_unittest(self, file_path_to_use, test_file):
        import unittest
        loader = unittest.TestLoader()
        self.logger.debug(f"Discovering tests in: {os.path.dirname(file_path_to_use)} with pattern: {os.path.basename(test_file)}")
        test_module = os.path.relpath(test_file,
                                      start=os.getcwd())  # Get relative path from the current working directory
        test_module = test_module.replace("/", ".").replace("\\", ".").rstrip(".py")  # Convert to module name
        if test_module.startswith("."):
            test_module = test_module[1:]  # Remove leading dot if present
        self.logger.debug(f"Test module: {test_module}")
        suite = loader.loadTestsFromName(test_module)
        runner = unittest.TextTestRunner()
        result = runner.run(suite)

        for test_case, traceback in result.failures + result.errors:
            test_case_id = self._get_test_case_id(str(test_case))
            self.db_service.insert_test_result(test_case_id, status=False, error=traceback)

        successful_tests = set(str(test) for test in suite) - set(
            str(test) for test, _ in result.failures + result.errors)
        for test_case in successful_tests:
            test_case_id = self._get_test_case_id(str(test_case))
            self.db_service.insert_test_result(test_case_id, status=True, error=None)

    def execute_and_store_doctest(self, test_file):
        module_name = os.path.splitext(os.path.basename(test_file))[0]
        spec = importlib.util.spec_from_file_location(module_name, test_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Now run doctests on the loaded module
        result = doctest.testmod(module)

        test_case_id = self._get_test_case_id(test_file)
        status = result.failed == 0
        error_message = f"{result.failed} of {result.attempted} tests failed" if result.failed > 0 else None
        self.db_service.insert_test_result(test_case_id, status, error_message)

    def query_test_file_data(self, test_file_name: str):
        if self.db_service is None:
            raise RuntimeError("Database service is not initialized.")

        results = self.db_service.get_test_file_data(test_file_name)
        if not results:
            self.logger.debug(f"No data found for file: {test_file_name}")
            return

        from tabulate import tabulate
        rows = [dict(row) for row in results]

        print(f"Results for file: {test_file_name}")
        print(tabulate(rows, headers="keys", tablefmt="grid"))

    def select_all_from_db(self) -> None:
        rows = self.db_service.get_test_suites()
        for row in rows:
            print(repr(dict(row)))
