# Agent Guidelines for This Repository

## Build/Lint/Test Commands

### Testing
- Run all tests: `source compiler/.venv/bin/activate && python -m unittest discover tests/`
- Run specific test file: `source compiler/.venv/bin/activate && python -m unittest tests.test_json_cpu_profiles`
- Run single test method: `source compiler/.venv/bin/activate && python -m unittest tests.test_json_cpu_profiles.TestConfigCPUProfile.test_load_65c02_profile`
- Validate CPU profiles: `source compiler/.venv/bin/activate && python validate_json_profiles.py --all`
- Interactive testing: `source compiler/.venv/bin/activate && python test_json_interactive.py`
- Test validation engine: Create test files with specific addressing patterns to trigger validation rules

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

## Validation Engine Development

### Generic Validation Rules
The assembler uses a generic validation engine that executes rules defined in YAML files. When adding new validation:

- **Use Generic Rule Types**: Prefer existing rule types (`error_if_mode_is`, `warning_if_mode_is`, etc.)
- **No CPU-Specific Code**: Validation logic should be in YAML, not Python
- **Backward Compatibility**: Legacy validation format is still supported
- **Message Templates**: Use `{mnemonic}`, `{mode}`, `{value}` placeholders in messages

### Supported Validation Rule Types
- `error_if_mode_is` - Error if instruction uses specific addressing modes
- `error_if_mode_is_not` - Error if instruction doesn't use specific addressing modes
- `warning_if_mode_is` - Warning if instruction uses specific addressing modes  
- `warning_if_mode_is_not` - Warning if instruction doesn't use specific addressing modes
- `error_if_operand_out_of_range` - Error if operand value is outside valid range
- `warning_if_operand_out_of_range` - Warning if operand value is outside optimal range
- `error_if_register_used` / `warning_if_register_used` - Register-specific validation

### Adding New Validation Rule Types
If new validation types are needed:
1. Add rule type to `_execute_validation_rule()` in `cpu_profile_base.py`
2. Handle rule parameters and message formatting
3. Update documentation in README.md and TESTING.md
4. Add test cases to verify new rule type

### Validation Rule Examples
```yaml
# Error for accumulator-only instructions using immediate addressing
- type: "error_if_mode_is"
  mnemonics: ["ASL", "LSR", "ROL", "ROR"]
  modes: ["IMMEDIATE"]
  message: "Instruction {mnemonic} cannot use IMMEDIATE addressing with accumulator."

# Warning for optimization opportunities
- type: "warning_if_mode_is"
  mnemonics: ["LDA", "STA"]
  modes: ["ABSOLUTE"]
  message: "Instruction {mnemonic} uses absolute addressing. Consider using zero-page addressing for values under $0100."

# Range validation with exceptions
- type: "error_if_operand_out_of_range"
  min_value: 0
  max_value: 255
  message: "Immediate value ${value:04X} is too large for 8-bit immediate."
  exceptions: ["LDX", "STX"]  # 16-bit instructions
```