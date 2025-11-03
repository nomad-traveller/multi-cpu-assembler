# Agent Guidelines for This Repository

## Build/Lint/Test Commands

### Testing
- Run all tests: `source compiler/.venv/bin/activate && python -m unittest discover tests/`
- Run specific test file: `source compiler/.venv/bin/activate && python -m unittest tests.test_json_cpu_profiles`
- Run single test method: `source compiler/.venv/bin/activate && python -m unittest tests.test_json_cpu_profiles.TestConfigCPUProfile.test_load_65c02_profile`
- Validate CPU profiles: `source compiler/.venv/bin/activate && python validate_json_profiles.py --all`
- Interactive testing: `source compiler/.venv/bin/activate && python test_json_interactive.py`

### Building/Running
- Main assembler: `source compiler/.venv/bin/activate && python compiler/main.py source_file.s -o output.bin --cpu 65c02`
- Available CPUs: 65c02, 6800
- Profile formats: JSON5 (.json) and YAML (.yaml/.yml) - auto-detected

### Dependencies
- Create virtual environment: `python3 -m venv compiler/.venv`
- Activate virtual environment: `source compiler/.venv/bin/activate` (or `. compiler/.venv/bin/activate`)
- Install required packages: `pip install sly PyYAML`
- The project uses a virtual environment in `compiler/.venv/`

## Code Style Guidelines

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- One import per line
- Use absolute imports within the project

### Naming Conventions
- **Classes**: PascalCase (e.g., `CPUProfile`, `C6502Profile`)
- **Functions/Methods**: snake_case (e.g., `parse_addressing_mode`, `assemble`)
- **Variables**: snake_case (e.g., `operand_str`, `symbol_table`)
- **Constants**: ALL_CAPS (e.g., `SUPPORTED_CPUS`, `OPCODES`)
- **Modules**: snake_case (e.g., `cpu_profiles.py`, `expression_parser.py`)

### Formatting
- 4 spaces for indentation
- Line length: ~100 characters (not strictly enforced)
- Blank lines between class/method definitions
- No trailing whitespace

### Types and Type Hints
- Use type hints for function parameters and return values where beneficial
- Use `Union` types for multiple possible types
- Use `Optional` for nullable types
- Example: `def parse_args() -> argparse.Namespace:`

### Error Handling
- Use custom Diagnostics class for error reporting
- Return boolean success/failure from main functions
- Print errors to stdout/stderr appropriately
- Use try/except blocks for expected exceptions

### Code Structure
- Follow object-oriented design with clear separation of concerns
- Use abstract base classes for extensible interfaces (e.g., `CPUProfile`)
- Implement dependency injection pattern
- Keep functions focused on single responsibilities
- Use composition over inheritance where appropriate

### Documentation
- Use docstrings for classes and public methods
- Include type information in docstrings where helpful
- Add inline comments for complex logic
- Keep comments concise and explanatory

### Testing
- Use unittest framework
- Test classes inherit from `unittest.TestCase`
- Use descriptive test method names (e.g., `test_duplicate_label_pass1`)
- Mock external dependencies with `unittest.mock`
- Test both success and failure cases
- Capture stdout/stderr for validation when needed