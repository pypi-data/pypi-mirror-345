import inspect
from typing import Optional, List, Set, Tuple

import astor
from testgen.generator.test_generator import TestGenerator
from testgen.models.generator_context import GeneratorContext

class DocTestGenerator(TestGenerator):
    def __init__(self, generator_context: GeneratorContext):
        super().__init__(generator_context)

    def generate_test_header(self):
        pass
    
    def generate_test_function(self, unique_func_name, func_name, cases) -> None:
        """Generate a test function with doctests."""
        doctest_examples = []

        for inputs, expected in cases:
            input_args = ', '.join(map(repr, inputs))

            if self._generator_context.class_name:
                test_call = f"{self._generator_context.class_name}().{func_name}({input_args})"
            else:
                test_call = f"{func_name}({input_args})"

            result_str = repr(expected)
            # Format with >>> and proper spacing
            doctest = f">>> {test_call}\n{result_str}"
            doctest_examples.append(doctest)

        # Inject the doctests into the original function's docstring
        self._inject_docstring(func_name, doctest_examples)
        
    def save_file(self):
            """Save the generated test content to a file."""
            return self._generator_context.filepath
        
    def _inject_docstring(self, func_name, doctest_examples):
        """Inject doctest examples into the function's docstring."""
        module_path = self._generator_context.filepath
        
        # Read the source file
        with open(module_path, 'r') as f:
            lines = f.readlines()

        func_line_num, func_indent = self._get_func_line_num_and_indent(lines, func_name)
        
        if func_line_num == -1:
            print(f"Function {func_name} not found in {module_path}")
            return
        
        has_docstring, docstring_end = self._get_docstring_end(func_line_num, lines)

        all_examples, seen_examples = self._collect_existing_docstrings(func_line_num, lines, has_docstring, docstring_end)
        
        
        all_examples, seen_examples = self._add_new_docstrings(doctest_examples, all_examples, seen_examples)
        
        docstring_lines = self._create_docstrings(func_indent, all_examples)
        
        # Modify the source code
        if has_docstring:
            # Replace existing docstring
            lines = lines[:func_line_num + 1] + [line + '\n' for line in docstring_lines] + lines[docstring_end + 1:]
        else:
            # Insert new docstring after function definition
            lines = lines[:func_line_num + 1] + [line + '\n' for line in docstring_lines] + lines[func_line_num + 1:]
        
        # Write back to the file
        with open(module_path, 'w') as f:
            f.writelines(lines)

    def _extract_doctest_examples(self, docstring_lines: List[str]) -> List[Tuple[str, str]]:
        examples = []
        current_call = None
        current_result_lines = []
        
        # Process docstring line by line
        for line in docstring_lines:
            stripped_line = line.strip()
            
            # Check if this is a test call line (starts with >>>)
            if stripped_line.startswith('>>>'):
                # If we were already collecting a test, save it
                if current_call is not None:
                    result = '\n'.join([line.strip() for line in current_result_lines if line.strip()])
                    examples.append((current_call, result))
                    current_result_lines = []
                
                # Extract the call part (everything after >>>)
                current_call = stripped_line[3:].strip()
            
            # Otherwise, if we have a current call, add to the result
            elif current_call is not None:
                current_result_lines.append(stripped_line)
        
        # Don't forget the last example if there is one
        if current_call is not None and current_result_lines:
            result = '\n'.join([line.strip() for line in current_result_lines if line.strip()])
            examples.append((current_call, result))
        
        return examples
    
    
    def _is_class_method(self, function_name: str) -> bool:
        """Check if a function is a method of a class in the module."""
        for name, obj in inspect.getmembers(self._generator_context.module):
            if inspect.isclass(obj) and hasattr(obj, function_name):
                return True
        return False
    
    def _get_class_name(self, method_name: str) -> Optional[str]:
        """Get the name of the class that contains the method."""
        for name, obj in inspect.getmembers(self._generator_context.module):
            if inspect.isclass(obj) and hasattr(obj, method_name):
                return name
        return None
    
    def _get_func_line_num_and_indent(self, lines: List[str], func_name: str) -> Tuple[int, str]:
        func_line_num = -1
        func_indent = ""
        
        for i, line in enumerate(lines):
            line_stripped = line.lstrip()
            if line_stripped.startswith('def '):
                # Extract function name
                potential_name = line_stripped[4:].split('(')[0].strip()
                if potential_name == func_name:
                    func_line_num = i
                    # Calculate indentation by counting spaces before 'def'
                    func_indent = line[:len(line) - len(line_stripped)]
                    break
        return (func_line_num, func_indent)
    
    def _get_docstring_end(self, func_line_num: int, lines: List[str]) -> Tuple[bool, int]:
        has_docstring = False
        docstring_end = -1
        
        if func_line_num + 1 < len(lines) and '"""' in lines[func_line_num + 1]:
            has_docstring = True
            # Find the end of the docstring
            for i in range(func_line_num + 2, len(lines)):
                if '"""' in lines[i]:
                    docstring_end = i
                    break
        return (has_docstring, docstring_end)
    
    def _create_docstrings(self, func_indent: int, all_examples: List[str]) -> List[str]:
        # Create the new docstring with all examples
        docstring_lines = []
        docstring_lines.append(func_indent + '    """')
        
        # Add all examples with consistent indentation
        for i, example in enumerate(all_examples):
            # Split example into lines
            example_lines = example.split('\n')
            
            # Add each line with proper indentation
            for j, line in enumerate(example_lines):
                docstring_lines.append(func_indent + '    ' + line)
            
            # Add blank line between examples (not after the last one)
            if i < len(all_examples) - 1:
                docstring_lines.append('')
        
        # Close the docstring
        docstring_lines.append(func_indent + '    """')
        return docstring_lines
        
    def _collect_existing_docstrings(self, func_line_num: int, lines: List[str], has_docstring: bool, docstring_end: int) -> Tuple[List[str], Set[str]]:
        # Collect all examples (existing)
        all_examples = []
        seen_examples = set()
        
        if has_docstring and docstring_end > 0:
            # Extract existing examples from docstring
            existing_examples = self._extract_doctest_examples(lines[func_line_num + 2:docstring_end])
            
            for call, result in existing_examples:
                # Create normalized example
                example = f">>> {call}\n{result}"
                
                if example not in seen_examples:
                    all_examples.append(example)
                    seen_examples.add(example)

        return (all_examples, seen_examples)

    def _add_new_docstrings(self, doctest_examples: List[str], all_examples: List[str], seen_examples: Set[str]) -> Tuple[List[str], Set[str]]:
         # Add new examples
        for example in doctest_examples:
            # Normalize the example format
            parts = example.split('\n', 1)
            if len(parts) == 2:
                call_line, result = parts
                call = call_line[4:].strip()  # Remove >>> prefix and whitespace
                result = result.strip()
                
                # Create normalized example
                normalized_example = f">>> {call}\n{result}"
                
                if normalized_example not in seen_examples:
                    all_examples.append(normalized_example)
                    seen_examples.add(normalized_example)

        return (all_examples, seen_examples)