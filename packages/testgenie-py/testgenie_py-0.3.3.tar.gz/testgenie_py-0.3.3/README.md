# TestGenie

**TestGenie** is an automated unit test generation tool for Python that supports multiple test generation strategies, including static AST analysis, fuzz testing, feedback-directed random testing, and reinforcement learning.  
Built with a modular Pipe and Filter architecture, it analyzes Python source code to extract function metadata, generates meaningful test cases, and outputs executable test suites in formats like Unittest, PyTest, or Doctest.  
The system can also measure and report code coverage and safely execute tests in Docker containers.  
TestGenie aims to reduce manual testing effort, improve coverage, and explore the potential of learning-based approaches for optimizing test generation.

---

## Installation

Make sure you have **Python 3.10+** and **Poetry** installed.

Install dependencies:

```bash
poetry install
```

Activate the virtual environment:

```bash
poetry shell
```

---

## Running the CLI

To invoke the test generator, run:

```bash
poetry run python -m testgen.main <file_path> [options]
```

**Required Argument:**
- `<file_path>`: Path to the Python module you want to analyze.

---

## Command-Line Options

| Command/Flag | Description |
|:---|:---|
| `--output, -o <path>` | Path to output directory for generated test files (default: `./tests`) |
| `--generate-only, -g` | Only generate test code, skip running tests and measuring coverage |
| `--test-mode <mode>` | Set the test analysis strategy: `ast` (default), `random`, `fuzz`, or `reinforce` |
| `--test-format <format>` | Set the test output format: `unittest` (default), `pytest`, or `doctest` |
| `--safe` | Run test generation inside a Docker container for isolation and safety |
| `--query, -q` | Query the database for test cases, coverage data, and test results for a specific file |
| `--db <db_path>` | Path to SQLite database file (default: `testgen.db`) |
| `--reinforce-mode <mode>` | Set mode for reinforcement learning: `train` (default) or `collect` |
| `--visualize, -viz` | Visualize generated test coverage graphs using Graphviz |
| `--debug` | Enable debug logging output |
| `--log-file <path>` | Save logs to the specified file instead of only printing to the console |

---

## Examples

Generate and run unit tests for a Python module:

```bash
poetry run python -m testgen.main mymodule.py
```

Generate tests using fuzzing strategy and output to a custom directory:

```bash
poetry run python -m testgen.main mymodule.py --test-mode fuzz --output generated_tests/
```

Run reinforcement learning-based test generation:

```bash
poetry run python -m testgen.main mymodule.py --test-mode reinforce
```

Query previously generated test results from the database:

```bash
poetry run python -m testgen.main mymodule.py --query
```

Safely generate tests inside a Docker container:

```bash
poetry run python -m testgen.main mymodule.py --safe
```

---

## Features
- Static analysis using Python AST
- Fuzz testing using randomized input generation
- Feedback-directed random testing
- Reinforcement learning-based test case optimization
- Supports Unittest, PyTest, and Doctest formats
- Code coverage measurement and reporting
- Docker sandboxing for safe test execution
- SQLite database integration for tracking tests and results
- CLI visualization of test coverage graphs

---

## Requirements

- Python 3.10+
- Poetry
- (Optional) Docker (for safe mode execution)

---
