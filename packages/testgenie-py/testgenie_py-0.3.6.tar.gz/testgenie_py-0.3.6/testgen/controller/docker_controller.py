import os
import sys
from argparse import Namespace
import docker
from docker import DockerClient, client
from docker import errors
from docker.models.containers import Container
import importlib.resources as pkg_resources
import tempfile
import shutil

from testgen.service.logging_service import get_logger
from testgen.service.service import Service

AST_STRAT = 1
FUZZ_STRAT = 2
RANDOM_STRAT = 3

UNITTEST_FORMAT = 1
PYTEST_FORMAT = 2
DOCTEST_FORMAT = 3

class DockerController:
    def __init__(self):
        self.service = Service()
        self.debug_mode = False
        self.args = None
        self.logger = get_logger()

    def run_in_docker(self, project_root: str, docker_client: DockerClient, args: Namespace) -> bool:
        self.args = args
        self.debug_mode = True if args.debug else False
    
        os.environ["RUNNING_IN_DOCKER"] = "1"

        # Check if Docker image exists, build it if not
        image_name = "testgen-runner"
        self.get_image(docker_client, image_name, project_root)
        if not self.args.safe:
            self.logger.info("Docker image not found. Running locally...")
            return False

        src_path = os.path.abspath(args.file_path)
        dest_path = os.path.join(project_root, os.path.basename(src_path))
        try:
            shutil.copy(src_path, dest_path)
            print(f"Copied file from {src_path} to {dest_path}")
            self.logger.debug(f"Copied file from {src_path} to {dest_path}")
        except Exception as e:
            print(f"Failed to copy file: {e}")
            self.logger.error(f"Failed to copy file: {e}")
            sys.exit(1)

        docker_args = [os.path.basename(args.file_path)] + [arg for arg in sys.argv[2:] if arg != "--safe"]
        docker_args[0] = f"/controller/{docker_args[0]}"

        # Run the container with the same arguments
        try:
            self.debug(f"project_root: {project_root}")
            container = self.run_container(docker_client, image_name, docker_args, project_root)

            self.clean_up(dest_path)

            # Stream the logs to the console
            logs_output = self.get_logs(container)
            self.debug(logs_output)

        except Exception as e:
            print(f"Error running container: {e}")
            sys.exit(1)

        # Create the target directory if it doesn't exist
        if args.output is None:
            target_path = os.path.join(os.getcwd(), 'tests')
        else:
            target_path = args.output
        os.makedirs(target_path, exist_ok=True)

        self.debug(f"SERVICE target path after logs: {target_path}")

        test_cases = self.service.parse_test_cases_from_logs(logs_output)

        print(f"Extracted {len(test_cases)} test cases from container.")

        file_path = os.path.abspath(args.file_path)
        self.debug(f"Filepath in CLI CONTROLLER: {file_path}")
        self.service.set_file_path(file_path)

        if args.test_format == "pytest":
            self.service.set_test_generator_format(PYTEST_FORMAT)
        elif args.test_format == "doctest":
            self.service.set_test_generator_format(DOCTEST_FORMAT)
        else:
            self.service.set_test_generator_format(UNITTEST_FORMAT)

        test_file = self.service.generate_test_file(test_cases, target_path)
        print(f"Unit tests saved to: {test_file}")

        if not args.generate_only:
            print("Running coverage...")
            self.service.run_coverage(test_file)
            
        # Add explicit return True here
        return True


    def get_image(self, docker_client: DockerClient, image_name: str, project_root: str):
        try:
            docker_client.images.get(image_name)
            print(f"Using existing {image_name} Docker image")
        except docker.errors.ImageNotFound:
            print(f"Building {image_name} Docker image...")

            # Look for Dockerfile in the project root
            dockerfile_path = self.get_dockerfile_path()
            if not os.path.exists(dockerfile_path):
                print(f"Dockerfile not found at {dockerfile_path}")
                sys.exit(1)

            self.debug(f"Using Dockerfile at: {dockerfile_path}")

            if not self.build_docker_image(docker_client, image_name, dockerfile_path, project_root):
                print("Failed to build Docker image. Continuing without safe mode.")
                self.args.safe = False

    @staticmethod
    def get_logs(container) -> str:
        # Stream the logs to the console
        logs = container.logs(stream=True)
        logs_output = ""
        for log in logs:
            log_line = log.decode()
            logs_output += log_line
            print(log_line, end="")
        return logs_output

    @staticmethod
    def run_container(docker_client: DockerClient, image_name: str, docker_args: list, project_root: str) -> Container:
        # Create Docker-specific environment variables
        docker_env = {
            "RUNNING_IN_DOCKER": "1",
            "PYTHONPATH": "/controller"
        }
        
        # Join arguments with proper escaping
        args_str = ' '.join(f'"{arg}"' for arg in docker_args)
        
        print(f"Docker args: {docker_args}")
        print(f"Project root: {project_root}")
        
        return docker_client.containers.run(
                image=image_name,
                command=["testgenie"] + docker_args,
                volumes={
                os.path.abspath(project_root): {
                "bind": "/controller",
                "mode": "rw"
                    }
                },
                working_dir="/controller",
                environment=docker_env,
                detach=True,
                remove=True,
                stdout=True,
                stderr=True
            )

    def build_docker_image(self, docker_client, image_name, dockerfile_path, project_root):
        try:
            print(f"Starting Docker build for image: {image_name}")
            dockerfile_rel_path = os.path.relpath(dockerfile_path, project_root)
            docker_dir = os.path.dirname(dockerfile_path)

            dockerfile_rel_path = os.path.relpath(dockerfile_path, project_root)
            self.debug(f"Project root {project_root}")
            self.debug(f"Docker directory: {docker_dir}")
            self.debug(f"Docker rel path: {dockerfile_rel_path}")

            build_progress = docker_client.api.build(
                path=docker_dir,          # now it knows what docker_dir is
                dockerfile=dockerfile_path,
                tag=image_name,
                rm=True,
                decode=True
            )

            for chunk in build_progress:
                self.debug(f"CHUNK: {chunk}")
                if 'stream' in chunk:
                    for line in chunk['stream'].splitlines():
                        if line.strip():
                            print(f"Docker: {line.strip()}")
                elif 'error' in chunk:
                    self.debug(f"Docker build error: {chunk['error']}")
                    return False
            print(f"Docker image built successfully: {image_name}")
            return True

        except docker.errors.BuildError as e:
            print(f"Docker build error: {e}")
        except docker.errors.APIError as e:
            print(f"Docker API error: {e}")
        except Exception as e:
            print(f"Unexpected error during Docker build: {str(e)}")
            return False

    def get_dockerfile_path(self) -> str:
        # First, try local development path
        local_dockerfile = os.path.join(os.path.dirname(__file__), "docker", "Dockerfile")
        if os.path.exists(local_dockerfile):
            self.debug(f"Found local Dockerfile at: {local_dockerfile}")
            return local_dockerfile

        # If not found locally, try inside installed package
        try:
            dockerfile_resource = pkg_resources.files('testgen').joinpath('docker/Dockerfile')
            if dockerfile_resource.is_file():
                self.debug(f"Found package-installed Dockerfile at: {dockerfile_resource}")
                return str(dockerfile_resource)
        except Exception as e:
            print(f"Error locating Dockerfile in package resources: {e}")

        print("Dockerfile not found in local project or package.")
        sys.exit(1)

    def clean_up(self, dest_path: str) -> None:
        # Remove copied file from project root
        try:
            if os.path.exists(dest_path):
                os.remove(dest_path)
                print(f"Deleted file from {dest_path}")
                self.logger.debug(f"Deleted file from {dest_path}")
        except Exception as e:
            print(f"Failed to delete file: {e}")
            self.logger.error(f"Failed to delete file: {e}")

    @staticmethod
    def is_inside_docker() -> bool:
        """Check if the current process is running inside a Docker container."""
        return os.environ.get("RUNNING_IN_DOCKER") in ("1", "true", "True")

    def debug(self, message: str):
        """Log debug message"""
        if self.debug_mode:
            self.logger.debug(message)