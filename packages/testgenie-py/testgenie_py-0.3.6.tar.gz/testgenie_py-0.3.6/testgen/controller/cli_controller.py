import argparse
import inspect
import os
import sys

import docker
from docker import DockerClient
from docker import errors
from testgen.service.logging_service import LoggingService, get_logger
from testgen.util.file_utils import adjust_file_path_for_docker, get_project_root_in_docker
from testgen.controller.docker_controller import DockerController
from testgen.service.service import Service
from testgen.presentation.cli_view import CLIView
from testgen.sqlite.db_service import DBService

AST_STRAT = 1
FUZZ_STRAT = 2
RANDOM_STRAT = 3
REINFORCE_STRAT = 4

UNITTEST_FORMAT = 1
PYTEST_FORMAT = 2
DOCTEST_FORMAT = 3

class CLIController:
    #TODO: Possibly create a view 'interface' and use dependency injection to extend other views
    def __init__(self, service: Service, view: CLIView):
        self.service = service
        self.view = view

    def run(self):

        parser = self.add_arguments()

        args = parser.parse_args()

        LoggingService.get_instance().initialize(
            debug_mode=args.debug if hasattr(args, 'debug') else False,
            log_file=args.log_file if hasattr(args, 'log_file') else None,
            console_output=True
        )

        logger = get_logger()

        if args.query:
            print(f"Querying database for file: {args.file_path}")
            self.service.query_test_file_data(args.file_path)
            return
        
        if args.coverage:
            self.service.get_coverage(args.file_path)
            return
            
        running_in_docker = os.environ.get("RUNNING_IN_DOCKER") is not None
        if running_in_docker:
            args.file_path = adjust_file_path_for_docker(args.file_path)
            self.execute_generation(args, True)
        elif args.safe and not running_in_docker:
            client = self.docker_available()
            # Skip Docker-dependent operations if client is None
            if client is None and args.safe:
                self.view.display_message("Running with --safe flag requires Docker. Continuing without safe mode.")
                args.safe = False
                self.execute_generation(args)
            else:
                docker_controller = DockerController()
                project_root = get_project_root_in_docker(args.file_path)
                successful: bool = docker_controller.run_in_docker(project_root, client, args)
                if not successful:
                    if hasattr(args, 'db') and args.db:
                        self.service.db_service = DBService(args.db)
                        self.view.display_message(f"Using database: {args.db}")
                    self.execute_generation(args)
                # Else successful, do nothing - we're done
        else:
            # Initialize database service with specified path
            if hasattr(args, 'db') and args.db:
                self.service.db_service = DBService(args.db)
                self.view.display_message(f"Using database: {args.db}")
            self.view.display_message("Running in local mode...")
            self.execute_generation(args)

    def execute_generation(self, args: argparse.Namespace, running_in_docker: bool = False):
        try:
            self.set_service_args(args)

            if running_in_docker:
                self.view.display_message("Running in Docker mode...")
                self.service.generate_test_cases()

            else:
                test_file = self.service.generate_tests(args.output)
                self.view.display_message(f"Unit tests saved to: {test_file}")
                self.view.display_message("Running coverage...")
                self.service.run_coverage(test_file)
                self.view.display_message("Tests and coverage data saved to database.")

                if args.visualize:
                    self.service.visualize_test_coverage()

        except Exception as e:
            self.view.display_error(f"An error occurred: {e}")
            # Make sure to close the DB connection on error
            if hasattr(self.service, 'db_service'):
                self.service.db_service.close()

    def set_service_args(self, args: argparse.Namespace):
        self.service.set_file_path(args.file_path)
        self.set_test_format(args)
        self.set_test_strategy(args)

    def add_arguments(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="A CLI tool for generating unit tests.")
        parser.add_argument("file_path", type=str, help="Path to the Python file.")
        parser.add_argument("--output", "-o", type=str, help="Path to output directory.")
        parser.add_argument("-q", "--query", action="store_true", help="Query the database for test cases, coverage data, and test results for a specific file")
        parser.add_argument(
            "--generate-only", "-g",
            action="store_true",
            help="Generate branched code but skip running unit tests and coverage."
        )
        parser.add_argument(
            "--test-mode",
            choices=["ast", "random", "fuzz", "reinforce"],
            default="ast",
            help="Set the test generation analysis technique"
        )
        parser.add_argument(
            "--reinforce-mode",
            choices=["train", "collect"],
            default="train",
            help="Set mode for reinforcement learning"
        )
        parser.add_argument(
            "--test-format",
            choices=["unittest", "pytest", "doctest"],
            default="unittest",
            help="Set the test generation format"
        )
        parser.add_argument(
            "--safe",
            action="store_true",
            help="Run test generation from within a docker container."
        )
        parser.add_argument(
            "--db",
            type=str,
            default="testgen.db",
            help="Path to SQLite database file (default: testgen.db)"
        )
        parser.add_argument(
            "-viz", "--visualize",
            action="store_true",
            help = "Visualize the tests with graphviz"
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging"
        )
        parser.add_argument(
            "--log-file",
            type=str,
            help="Path to log file (if not specified, logs will only go to console)"
        )
        parser.add_argument(
            "-c", "--coverage",
            action="store_true",
            help="Run coverage analysis on the generated tests"
        )
        return parser

    def set_test_format(self, args: argparse.Namespace):
        if args.test_format == "pytest":
            self.service.set_test_generator_format(PYTEST_FORMAT)
        elif args.test_format == "doctest":
            self.service.set_test_generator_format(DOCTEST_FORMAT)
        else:
            self.service.set_test_generator_format(UNITTEST_FORMAT)

    def set_test_strategy(self, args: argparse.Namespace):
        if args.test_mode == "random":
            self.view.display_message("Using Random Feedback-Directed Test Generation Strategy.")
            self.service.set_test_analysis_strategy(RANDOM_STRAT)
        elif args.test_mode == "fuzz":
            self.view.display_message("Using Fuzz Test Generation Strategy...")
            self.service.set_test_analysis_strategy(FUZZ_STRAT)
        elif args.test_mode == "reinforce":
            self.view.display_message("Using Reinforcement Learning Test Generation Strategy...")
            if args.reinforce_mode == "train":
                self.view.display_message("Training mode enabled - will update Q-table")
            else:
                self.view.display_message("Training mode disabled - will use existing Q-table")
            self.service.set_test_analysis_strategy(REINFORCE_STRAT)
            self.service.set_reinforcement_mode(args.reinforce_mode)
        else:
            self.view.display_message("Generating function code using AST analysis...")
            generated_file_path = self.service.generate_function_code()
            self.view.display_message(f"Generated code saved to: {generated_file_path}")
            if not args.generate_only:
                self.view.display_message("Using Simple AST Traversal Test Generation Strategy...")
                self.service.set_test_analysis_strategy(AST_STRAT)

    def docker_available(self) -> DockerClient | None:
        try:
            client = docker.from_env()
            client.ping()
            self.view.display_message("Docker daemon is running and connected.")
            return client
        except docker.errors.DockerException as err:
            print(f"Docker is not available: {err}")
            print(f"Make sure the Docker daemon is running, and try again.")
            choice = input("Continue without Docker (y/n)?")
            if choice.lower() == 'y':
                return None
            else:
                sys.exit(1)
