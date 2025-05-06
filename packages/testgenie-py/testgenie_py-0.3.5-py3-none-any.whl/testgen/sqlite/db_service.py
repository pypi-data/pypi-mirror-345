import os
import sqlite3
import json
import time
import ast
from datetime import datetime
from typing import List, Tuple

from testgen.models.test_case import TestCase
from testgen.sqlite.db import create_database

class DBService:
    def __init__(self, db_name="testgen.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        """Establish connection to the database."""
        if not os.path.exists(self.db_name):
            create_database(self.db_name)
        
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def insert_test_suite(self, name: str) -> int:
        """Insert a test suite and return its ID."""
        self.cursor.execute(
            "INSERT INTO TestSuite (name, creation_date) VALUES (?, ?)",
            (name, datetime.now())
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_source_file(self, path: str, lines_of_code: int) -> int:
        """Insert a source file and return its ID."""
        # Check if file already exists
        self.cursor.execute("SELECT id FROM SourceFile WHERE path = ?", (path,))
        existing = self.cursor.fetchone()
        if existing:
            return existing[0]
        
        self.cursor.execute(
            "INSERT INTO SourceFile (path, lines_of_code, last_modified) VALUES (?, ?, ?)",
            (path, lines_of_code, datetime.now())
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_function(self, name: str, start_line: int, end_line: int, source_file_id: int) -> int:
        """Insert a function and return its ID."""
        num_lines = end_line - start_line + 1
        
        # Check if function already exists for this source file
        self.cursor.execute(
            "SELECT id FROM Function WHERE name = ? AND source_file_id = ?", 
            (name, source_file_id)
        )
        existing = self.cursor.fetchone()
        if existing:
            return existing[0]
            
        self.cursor.execute(
            "INSERT INTO Function (name, start_line, end_line, num_lines, source_file_id) VALUES (?, ?, ?, ?, ?)",
            (name, start_line, end_line, num_lines, source_file_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_test_case(self, test_case: TestCase, test_suite_id: int, function_id: int, test_method_type: int) -> int:
        """Insert a test case and return its ID."""
        # Convert inputs and expected output to JSON strings
        inputs_json = json.dumps(test_case.inputs)
        expected_json = json.dumps(test_case.expected)
        
        self.cursor.execute(
            "INSERT INTO TestCase (name, expected_output, input, test_function, last_run_time, test_method_type, test_suite_id, function_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                f"test_{test_case.func_name}",
                expected_json,
                inputs_json,
                test_case.func_name,
                datetime.now(),
                test_method_type,
                test_suite_id,
                function_id
            )
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_test_result(self, test_case_id: int, status: bool, error: str = None) -> int:
        """Insert a test result and return its ID."""
        self.cursor.execute(
            "INSERT INTO TestResult (test_case_id, status, error, execution_time) VALUES (?, ?, ?, ?)",
            (test_case_id, status, error, datetime.now())
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_coverage_data(self, file_name: str, executed_lines: str, missed_lines: str,
                           branch_coverage: float, source_file_id: int) -> int:
        """Insert coverage data and return its ID."""
        self.cursor.execute(
            "INSERT INTO CoverageData (file_name, executed_lines, missed_lines, branch_coverage, source_file_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (file_name, executed_lines, missed_lines, branch_coverage, source_file_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def save_test_generation_data(self, file_path: str, test_cases: List[TestCase], 
                                test_method_type: int, class_name: str = None) -> Tuple[int, List[int]]:
        """
        Save all data related to a test generation run.
        Returns the test suite ID and a list of test case IDs.
        """
        # Count lines in the source file
        with open(file_path, 'r') as f:
            lines_of_code = len(f.readlines())
        
        # Create test suite
        strategy_names = {1: "AST", 2: "Fuzz", 3: "Random", 4: "Reinforcement"}
        suite_name = f"{strategy_names.get(test_method_type, 'Unknown')}_Suite_{int(time.time())}"
        test_suite_id = self.insert_test_suite(suite_name)
        
        # Insert source file
        source_file_id = self.insert_source_file(file_path, lines_of_code)
        
        # Process functions and test cases
        test_case_ids = []
        function_ids = {}  # Cache function IDs to avoid redundant queries
        
        for test_case in test_cases:
            # Extract function name from test case
            func_name = test_case.func_name
            
            # If function not already processed
            if func_name not in function_ids:
                # Get function line numbers
                start_line, end_line = self._get_function_line_numbers(file_path, func_name)
                function_id = self.insert_function(func_name, start_line, end_line, source_file_id)
                function_ids[func_name] = function_id
            
            # Insert test case
            test_case_id = self.insert_test_case(
                test_case, 
                test_suite_id, 
                function_ids[func_name], 
                test_method_type
            )
            test_case_ids.append(test_case_id)
        
        return test_suite_id, test_case_ids
    
    def _get_function_line_numbers(self, file_path: str, function_name: str) -> Tuple[int, int]:
        """
        Extract the start and end line numbers for a function in a file.
        Returns a tuple of (start_line, end_line).
        """
        try:
            # Load the file and parse it
            with open(file_path, 'r') as f:
                file_content = f.read()
                
            tree = ast.parse(file_content)
            
            # Find the function definition
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 5  # Estimate if end_lineno not available
                    return node.lineno, end_line
                    
            # Also look for class methods
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for class_node in node.body:
                        if isinstance(class_node, ast.FunctionDef) and class_node.name == function_name:
                            end_line = class_node.end_lineno if hasattr(class_node, 'end_lineno') else class_node.lineno + 5
                            return class_node.lineno, end_line
        except Exception as e:
            print(f"Error getting function line numbers: {e}")
            
        # If we reach here, the function wasn't found or there was an error
        return 0, 0
    
    def get_test_suites(self):
        """Get all test suites from the database."""
        self.cursor.execute("SELECT * FROM TestSuite ORDER BY creation_date DESC")
        return self.cursor.fetchall()
    
    def get_test_cases_by_function(self, function_name):
        """Get all test cases for a specific function."""
        self.cursor.execute(
            "SELECT tc.* FROM TestCase tc JOIN Function f ON tc.function_id = f.id WHERE f.name = ?",
            (function_name,)
        )
        return self.cursor.fetchall()
    
    def get_coverage_by_file(self, file_path):
        """Get coverage data for a specific file."""
        self.cursor.execute(
            "SELECT cd.* FROM CoverageData cd JOIN SourceFile sf ON cd.source_file_id = sf.id WHERE sf.path = ?", 
            (file_path,)
        )
        return self.cursor.fetchall()

    def get_test_file_data(self, file_path: str):
        """
        Retrieve all test cases, coverage data, and test results for a specific file.
        """
        query = """
            SELECT
                tc.id AS test_case_id,
                tc.name AS test_case_name,
                tc.test_function AS test_case_test_function,
                tc.test_method_type AS test_case_method_type,
                COALESCE(cd.missed_lines, 'None') AS coverage_data_missed_lines
            FROM SourceFile sf
            LEFT JOIN Function f ON sf.id = f.source_file_id
            LEFT JOIN TestCase tc ON f.id = tc.function_id
            LEFT JOIN TestResult tr ON tc.id = tr.test_case_id
            LEFT JOIN CoverageData cd ON sf.id = cd.source_file_id
            WHERE sf.path = ?;
        """
        self.cursor.execute(query, (file_path,))
        return self.cursor.fetchall()
