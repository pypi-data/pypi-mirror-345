# CLAUDE.md - Guide for Working with bioread

## Build & Test Commands
```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test file
pytest test/test_reader.py

# Run specific test function
pytest -xvs test/test_reader.py::test_function_name

# Build package
python -m build
```

## Code Style Guidelines for Python
- **Imports**: stdlib first, third-party (numpy, pytest) second, project modules third
- **Formatting**: black
- **Naming**: `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- **Error handling**: Catch exceptions, often collect in `read_errors` list, use context managers for resources
- **Documentation**: NumPy-style docstrings, explain complex logic with comments

## Code Style Guidelines for R
- **Style**: Follow Tidyverse style

## Project Structure
- `bioread/`: Core library for reading BIOPAC AcqKnowledge files
- `bioread/runners/`: CLI tools for file conversion and information display
- `bioread/writers/`: Output formats (text, MATLAB, etc.)
- `test/`: Test suite with fixtures in `conftest.py` using pytest
- `
