import inspect
import ast
import time
from types import ModuleType
from typing import Dict, List

import testgen
from testgen.service.logging_service import get_logger
import testgen.util.file_utils
import testgen.util.file_utils as file_utils
import testgen.util.utils
from testgen.analyzer.ast_analyzer import ASTAnalyzer
from testgen.analyzer.fuzz_analyzer import FuzzAnalyzer
from testgen.analyzer.random_feedback_analyzer import RandomFeedbackAnalyzer
from testgen.models.test_case import TestCase
from testgen.analyzer.test_case_analyzer_context import TestCaseAnalyzerContext
from testgen.reinforcement.agent import ReinforcementAgent
from testgen.reinforcement.environment import ReinforcementEnvironment
from testgen.reinforcement.statement_coverage_state import StatementCoverageState
from testgen.models.analysis_context import AnalysisContext
from testgen.models.function_metadata import FunctionMetadata

# Constants for test strategies
AST_STRAT = 1
FUZZ_STRAT = 2
RANDOM_STRAT = 3
REINFORCE_STRAT = 4

class AnalysisService:
    def __init__(self):
        self.file_path = None
        self.class_name = None
        self.test_case_analyzer_context = TestCaseAnalyzerContext(None, None)
        self.test_strategy = 0
        self.reinforcement_mode = "train"
        self.logger = get_logger()

    def generate_test_cases(self) -> List[TestCase]:
            """Generate test cases using the current strategy."""
            if self.test_strategy == REINFORCE_STRAT:
                return self.do_reinforcement_learning(self.file_path)
            else:
                self.test_case_analyzer_context.do_logic()
                return self.test_case_analyzer_context.test_cases
    
    def create_analysis_context(self, filepath: str) -> AnalysisContext:
        """Create an analysis context for the given file."""
        self.logger.debug(f"Creating analysis context for {filepath}")
        filename = file_utils.get_filename(filepath)
        self.logger.debug(f"Filename: {filename}")
        module = file_utils.load_module(filepath)
        self.logger.debug(f"Module: {module}")
        class_name = self.get_class_name(module)
        self.logger.debug(f"Class name: {class_name}")
        function_data = self.get_function_data(filename, module, class_name)
        self.logger.debug(f"Function data: {function_data}")
        return AnalysisContext(filepath, filename, class_name, module, function_data)
    
    def get_function_data(self, filename: str, module: ModuleType, class_name: str | None) -> List[FunctionMetadata]:
        function_metadata_list: List[FunctionMetadata] = []

        # Parse the module's source code
        source_code = inspect.getsource(module)
        tree = ast.parse(source_code)

        # Find all function definitions in the module
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                function_metadata_list.append(self._create_function_metadata(filename, module, class_name, node))
            elif isinstance(node, ast.ClassDef):
                # Get the class name to check if it matches the expected class
                ast_class_name = node.name

                # If we have a specified class and it doesn't match, skip
                if self.class_name and ast_class_name != self.class_name:
                    continue

                # Process class methods
                for class_node in node.body:
                    if isinstance(class_node, ast.FunctionDef):
                        # Skip private methods (those starting with _)
                        if not class_node.name.startswith('_'):
                            function_metadata_list.append(self._create_function_metadata(filename, module, class_name, class_node))

        return function_metadata_list

    def do_reinforcement_learning(self, filepath: str, class_name: str | None, mode: str = None) -> List[TestCase]:
        mode = mode or self.reinforcement_mode
        module: ModuleType = testgen.util.file_utils.load_module(filepath)
        tree: ast.Module = testgen.util.file_utils.load_and_parse_file_for_tree(filepath)
        functions: List[ast.FunctionDef] = testgen.util.utils.get_functions(tree)
        self.class_name = class_name
        time_limit: int = 30
        all_test_cases: List[TestCase] = []

        q_table = self._load_q_table()

        for function in functions:
            print(f"\nStarting reinforcement learning for function {function.name}")
            start_time = time.time()
            function_test_cases: List[TestCase] = []
            best_coverage: float = 0.0

            # Create environment and agent once per function
            environment = ReinforcementEnvironment(filepath, function, module, self.class_name, function_test_cases, state=StatementCoverageState(None))
            environment.state = StatementCoverageState(environment)

            # Create agent with existing Q-table
            agent = ReinforcementAgent(filepath, environment, function_test_cases, q_table)

            if mode == "train":
                new_test_cases = agent.do_q_learning()
                function_test_cases.extend(new_test_cases)
            else:
                new_test_cases = agent.collect_test_cases()
                function_test_cases.extend(new_test_cases)

            print(f"\nNumber of test cases for {function.name}: {len(function_test_cases)}")

            current_coverage: float = environment.run_tests()
            print(f"Current coverage: {function.name}: {current_coverage}")

            q_table.update(agent.q_table)

            # Process and filter unique test cases
            seen = set()
            unique_test_cases: List[TestCase] = []
            for case in function_test_cases:
                # Make case tuple hashable
                case_inputs = tuple(case.inputs) if isinstance(case.inputs, list) else case.inputs
                case_key = (case.func_name, case_inputs)
                if case_key not in seen:
                    seen.add(case_key)
                    unique_test_cases.append(case)

            all_test_cases.extend(unique_test_cases)
            print(f"Final coverage for {function.name}: {best_coverage}%")
            print(f"Final test cases for {function.name}: {len(unique_test_cases)}")

        self._save_q_table(q_table)

        print("\nReinforcement Learning Complete")
        print(f"Total test cases found: {len(all_test_cases)}")
        return all_test_cases

    def _create_function_metadata(self, filename: str, module: ModuleType, class_name: str | None,
                                  func_node: ast.FunctionDef) -> FunctionMetadata:
        function_name = func_node.name

        param_types = self._get_params(func_node)

        return FunctionMetadata(filename, module, class_name, function_name, func_node, param_types)
    
    def _get_params(self, func_node: ast.FunctionDef) -> Dict[str, str]:
        # Extract parameter types
        param_types = {}
        for arg in func_node.args.args:
            param_name = arg.arg
            if param_name == 'self':
                continue

            if arg.annotation:
                param_type = ast.unparse(arg.annotation)
                param_types[param_name] = param_type
            else:
                param_types[param_name] = None
        return param_types
    
    def set_test_strategy(self, strategy: int, module_name: str, class_name: str):
        """Set the test analysis strategy."""
        self.test_strategy = strategy
        analysis_context = self.create_analysis_context(self.file_path)

        if strategy == AST_STRAT:
            analyzer = ASTAnalyzer(analysis_context)
            self.test_case_analyzer_context = TestCaseAnalyzerContext(analysis_context, analyzer)
        elif strategy == FUZZ_STRAT:
            analyzer = FuzzAnalyzer(analysis_context)
            self.test_case_analyzer_context = TestCaseAnalyzerContext(analysis_context, analyzer)
        elif strategy == RANDOM_STRAT:
            analyzer = RandomFeedbackAnalyzer(analysis_context)
            self.test_case_analyzer_context = TestCaseAnalyzerContext(analysis_context, analyzer)
        elif strategy == REINFORCE_STRAT:
            pass
        else:
            raise NotImplementedError(f"Test strategy {strategy} not implemented")
        
    def set_file_path(self, path: str):
        """Set the file path for analysis."""
        self.file_path = path

    def set_reinforcement_mode(self, mode: str):
        self.reinforcement_mode = mode

    @staticmethod
    def get_class_name(module: ModuleType) -> str | None:
        """Get class from module otherwise return None."""
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module.__name__:
                return name
        return None

    @staticmethod
    def _save_q_table(q_table):
        """Save Q-table to a global JSON file"""
        import json
        import os

        q_table_dir = "q_table"
        os.makedirs(q_table_dir, exist_ok=True)
        q_table_path = os.path.join(q_table_dir, "global_q_table.json")

        global_q_table = {}
        if os.path.exists(q_table_path):
            try:
                with open(q_table_path, 'r') as f:
                    global_q_table = json.load(f)
            except Exception as e:
                print(f"Error loading existing Q-table: {e}")

        serializable_q_table = {}
        for key, value in q_table.items():
            state, action = key
            state_str = str(state)
            serializable_q_table[f"{state_str}|{action}"] = value

        global_q_table = serializable_q_table  # Replace with latest Q-table

        try:
            with open(q_table_path, 'w') as f:
                json.dump(global_q_table, f)
            print(f"Q-table saved to {q_table_path}")
        except Exception as e:
            print(f"Error saving Q-table: {e}")

    @staticmethod
    def _load_q_table():
        """Load Q-table from the global JSON file"""
        import json
        import os
        import ast

        q_table_dir = "q_table"
        q_table_path = os.path.join(q_table_dir, "global_q_table.json")

        if not os.path.exists(q_table_path):
            print(f"No existing Q-table found at {q_table_path}")
            return {}

        try:
            with open(q_table_path, 'r') as f:
                serialized_q_table = json.load(f)

            # Convert serialized keys back to (state, action) tuples
            q_table = {}
            for key, value in serialized_q_table.items():
                state_str, action = key.split('|')
                try:
                    state = ast.literal_eval(state_str)
                    q_table[(state, action)] = value
                except (ValueError, SyntaxError):
                    print(f"Skipping invalid state: {state_str}")

            print(f"Loaded global Q-table with {len(q_table)} entries")
            return q_table
        except Exception as e:
            print(f"Error loading Q-table: {e}")
            return {}