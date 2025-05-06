import ast
import importlib.util
import os
import sys
from _ast import Module
from importlib import util
from types import ModuleType
from typing import Dict

def get_import_info(filepath: str) -> Dict[str, str]:
    if not os.path.exists(filepath) or not filepath.endswith('.py'):
        raise ValueError(f"Invalid Python file: {filepath}")
    
    # Get the directory and filename
    file_dir = os.path.dirname(os.path.abspath(filepath))
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    
    # Check if this is part of a package (has __init__.py)
    is_package = os.path.exists(os.path.join(file_dir, '__init__.py'))
    
    # Find the project root by looking for setup.py or a .git directory
    project_root = find_project_root(file_dir)
    
    # Build the import path based on the file's location relative to the project root
    if project_root:
        rel_path = os.path.relpath(file_dir, project_root)
        if rel_path == '.':
            # File is directly in the project root
            import_path = module_name
            package_name = ''
        else:
            # File is in a subdirectory
            path_parts = rel_path.replace('\\', '/').split('/')
            # Filter out any empty parts
            path_parts = [part for part in path_parts if part]
            
            if path_parts:
                package_name = path_parts[0]
                # Construct the full import path
                import_path = '.'.join(path_parts) + '.' + module_name
            else:
                package_name = ''
                import_path = module_name
    else:
        # Fallback if we can't find a project root
        package_name = ''
        import_path = module_name
    
    info = {
        'module_name': module_name,
        'package_name': package_name,
        'import_path': import_path,
        'is_package': is_package,
        'project_root': project_root,
        'file_dir': file_dir
    }
    
    #print(f"INFO: {info}")
    
    return info

def find_project_root(start_dir: str) -> str | None:
    current_dir = start_dir
    
    # Walk up the directory tree
    while current_dir:
        # Check for common project root indicators
        if (os.path.exists(os.path.join(current_dir, 'setup.py')) or
            os.path.exists(os.path.join(current_dir, '.git')) or
            os.path.exists(os.path.join(current_dir, 'pyproject.toml'))):
            return current_dir
            
        if os.path.exists(os.path.join(current_dir, '__main__.py')):
            return current_dir
        
        # Check for 'testgen' directory which is your project name
        if os.path.basename(current_dir) == 'testgen':
            parent_dir = os.path.dirname(current_dir)
            return parent_dir
            
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached the root
            break
        current_dir = parent_dir
    
    return None


def load_module(file_path: str) -> ModuleType:
    # Load a Python module from a file path.
    if file_path is None:
        raise ValueError("File path not set! Use set_file_path() to specify the path of the file")

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_filename(filepath: str) -> str:
    """Get filename from filepath."""
    return os.path.basename(filepath)


def load_and_parse_file_for_tree(file) -> Module:
    with open(file) as f:
        code = f.read()
    tree = ast.parse(code)
    return tree

def adjust_file_path_for_docker(file_path: str) -> str:
    """Adjust the file path to be valid inside the Docker container."""
    print(f"Docker - adjusting path: {file_path}")

    # If already absolute to /controller, return as-is
    if file_path.startswith("/controller/"):
        print(f"Docker - already adjusted: {file_path}")
        return file_path

    # If relative, make absolute
    adjusted_path = f"/controller/{file_path.lstrip('/')}"
    print(f"Docker - adjusted to: {adjusted_path}")
    return adjusted_path


"""def adjust_file_path_for_docker(file_path) -> str:
        #Adjust file path for Docker environment to handle subdirectories and relative paths.
        print(f"Docker - adjusting path: {file_path}")
        
        # Try direct path first (maybe it's correct already)
        if os.path.isfile(file_path):
            print(f"Docker - found file at direct path: {file_path}")
            return file_path
            
        # Try relative to /controller (root of mount)
        controller_path = os.path.join('/controller', file_path)
        if os.path.isfile(controller_path):
            print(f"Docker - found file at: {controller_path}")
            return controller_path
        
        # Try /controller/testgen/code_to_test path - this is where the file actually is
        testgen_path = os.path.join('/controller/testgen', file_path)
        if os.path.isfile(testgen_path):
            print(f"Docker - found file at: {testgen_path}")
            return testgen_path
        
        # If it's just a filename, search in common locations
        if os.path.basename(file_path) == file_path:
            for search_dir in ['/controller', '/controller/code_to_test', '/controller/testgen/code_to_test', '/controller/testgen']:
                test_path = os.path.join(search_dir, file_path)
                if os.path.isfile(test_path):
                    print(f"Docker - found file at: {test_path}")
                    return test_path
        
        # Debug output to help diagnose issues
        print("Docker - available files in /controller:")
        os.system("find /controller -name '*.py' | grep boolean")
        
        # Return original path if we couldn't find a better match
        print(f"Docker - couldn't find file, returning original: {file_path}")
        return file_path"""



def get_project_root_in_docker(script_path) -> str:
    # Don't use sys.argv[0] as it points to the virtualenv
    # Instead, find the actual project root
    if os.path.exists('/mnt/c/Users/cjsei/thesis/dev/testgen'):
        # Hard-coded path for now
        project_root = '/mnt/c/Users/cjsei/thesis/dev/testgen'
    else:
        # Try to find project root by looking for pyproject.toml or similar
        current_dir = os.path.dirname(os.path.abspath(script_path))
        while current_dir != '/':
            if os.path.exists(os.path.join(current_dir, 'pyproject.toml')) or \
               os.path.exists(os.path.join(current_dir, 'setup.py')):
                project_root = current_dir
                break
            current_dir = os.path.dirname(current_dir)
        else:
            # Fallback - use parent of script dir
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(script_path)))
    
    print(f"Project root directory: {project_root}")
    return project_root