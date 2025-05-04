# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
- Build project: `make build`
- Lint code: `make lint`
- Run all tests: `make test`
- Run single test: `pytest tests/test_file.py::TestClass::test_function -v`
- Format code: `make format`
- Setup dev environment: `uv venv && uv install -e ".[dev]"`

## Code Style
- Python >=3.9 compatibility
- Black formatting with 88 character line limit
- isort with Black profile for import ordering
- Strict type annotations with mypy
- Google/NumPy style docstrings
- PascalCase for classes, snake_case for functions/variables

## Error Handling
- Use hierarchy of exceptions extending from `A2AError` base class
- Catch specific exceptions (e.g., `A2AConnectionError`) rather than generic ones
- Provide descriptive error messages

## Project Structure
- Modular organization with clients, servers, models, and utils
- Tests in `/tests` directory using pytest
- Examples demonstrating different use cases in `/examples`
- Extensive type annotations throughout