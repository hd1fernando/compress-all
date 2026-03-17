# AGENTS.md - Developer Guidelines for All Compressor

This file provides guidelines for AI agents working on this codebase.

## Project Overview

- **Type**: Python CLI tool for compressing/decompressing files using Brotli
- **Entry point**: `src/main.py`
- **Version**: 0.1.0
- **Dependencies**: brotli, pytest

---

## Commands

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_integration.py -v

# Run a single test (most common for debugging)
pytest tests/test_integration.py::TestCompress::test_compress_creates_br_files -v

# Run tests matching a pattern
pytest tests/ -v -k "compress"
```

### Running the Application

```bash
# From source (with venv activated)
python src/main.py <directory> [options]

# After installation
compress-all <directory> [options]
```

### Installing Dependencies

```bash
# Create venv and install
python -m venv venv
source venv/bin/activate
pip install brotli pytest
```

---

## Code Style Guidelines

### Imports

Order imports as follows (separated by blank lines):

1. Standard library imports
2. Third-party imports
3. Local/application imports

```python
# Standard library
import argparse
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Tuple

# Third-party
import brotli
```

### Type Hints

- Use the `typing` module for type hints: `Optional`, `List`, `Tuple`, `Dict`, etc.
- Always specify return types for functions
- Use `Optional[X]` instead of `X | None`

```python
def get_optimal_workers() -> int:
    ...

def compress_file(file_path: str, remove_original: bool = False) -> str:
    ...
```

### Naming Conventions

- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private functions**: prefix with `_`

```python
def get_directory_size(directory: str, exclude: Optional[List[str]] = None) -> int:
    ...

class TestCompress:
    ...

MAX_WORKERS = 4
```

### Formatting

- Use 4 spaces for indentation (no tabs)
- Maximum line length: ~100 characters (soft limit)
- Single blank line between top-level definitions
- Use spaces around operators: `size_before > 0`
- No spaces inside function calls: `os.path.join(a, b)`

### Functions

- Use early returns for error conditions
- Log errors with appropriate level (error, warning, info)

```python
def process_directory(
    directory: str,
    compress: bool = True,
    remove_original: bool = False,
    exclude: Optional[List[str]] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    if logger is None:
        logger = logging.getLogger(__name__)
    
    if not os.path.isdir(directory):
        logger.error(f"'{directory}' is not a valid directory.")
        return
    ...
```

### Error Handling

- Use try/except blocks with specific exception types when possible
- Catch exceptions at the appropriate level
- Log errors with context about what failed

```python
try:
    if compress:
        output = compress_file(full_path, remove_original)
    else:
        output = decompress_file(full_path, remove_original)
    return (file, None)
except Exception as e:
    return (file, str(e))
```

### Logging

- Use the `logging` module
- Configure in `main()` with `logging.basicConfig()`
- Use appropriate log levels: DEBUG (verbose), INFO (normal), ERROR (failures)

```python
logger = logging.getLogger(__name__)
logger.info(f"Compressing: {file}")
logger.error(f"Error compressing {file}: {error}")
```

### CLI Arguments (argparse)

- Use `argparse` for CLI
- Define arguments with both short (`-c`) and long (`--compress`) forms
- Set appropriate defaults and help text

```python
parser = argparse.ArgumentParser(
    description="Compress or decompress files in a directory using Brotli"
)
parser.add_argument(
    "-c", "--compress",
    action="store_true",
    default=True,
    help="Compress files (default)"
)
```

### Comments

- Avoid comments unless absolutely necessary
- Let code be self-documenting with clear names
- No TODO comments unless tracking real pending work

### Testing

- Use pytest with fixtures
- Use class-based test organization (`TestCompress`, `TestDecompress`, etc.)
- Test both positive and negative cases
- Test edge cases (empty directories, already compressed files, etc.)

```python
@pytest.fixture
def temp_dir():
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)

class TestCompress:
    def test_compress_creates_br_files(self, temp_dir, files_in_temp_dir):
        result = run_program(temp_dir, "-c")
        assert result.returncode == 0
```

---

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   └── main.py          # Main CLI entry point
├── tests/
│   └── test_integration.py
├── install.sh           # Installation script
├── uninstall.sh         # Uninstallation script
└── README.md           # User documentation
```

---

## Key Patterns

### File Processing with ThreadPoolExecutor

```python
def process_single(full_path: str, file: str) -> Tuple[str, Optional[str]]:
    try:
        if compress:
            output = compress_file(full_path, remove_original)
        else:
            output = decompress_file(full_path, remove_original)
        return (file, None)
    except Exception as e:
        return (file, str(e))

with ThreadPoolExecutor(max_workers=workers) as executor:
    futures = {executor.submit(process_single, fp, f): f for fp, f in files_to_process}
    
    for future in as_completed(futures):
        file, error = future.result()
        if error:
            logger.error(f"Error: {error}")
```

### Path Handling

- Always use `os.path` for path operations
- Normalize paths with `os.path.normpath()`
- Use `os.path.join()` for combining paths

---

## Git Commit Conventions

This project uses **Smart Commits** convention for commit messages:

- Start with a verb in imperative mood: `Add`, `Fix`, `Update`, `Remove`, `Refactor`
- Keep the first line under 72 characters
- Use scope when applicable: `feat(core):`, `fix(cli):`, `docs(readme):`
- Reference issues when applicable: `Fix #123`, `Closes #456`

```bash
# Examples
git commit -m "Add --dry-run option for preview"
git commit -m "Fix exclude handling for nested directories"
git commit -m "Update README with new examples"
```

---

## Notes

- This is a Python 3 project (shebang: `#!/usr/bin/env python3`)
- The tool uses Brotli compression (.br extension)
- Parallel processing is handled via ThreadPoolExecutor
- The venv in this project already has dependencies installed
