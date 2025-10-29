# Contributing to Multi-CPU Assembler

Thank you for your interest in contributing to the Multi-CPU Assembler! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Initial Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/multi-cpu-assembler.git
   cd multi-cpu-assembler
   ```

2. **Set up Virtual Environment**
   ```bash
   python3 -m venv compiler/.venv
   source compiler/.venv/bin/activate  # On Windows: compiler\.venv\Scripts\activate
   pip install sly
   ```

3. **Verify Setup**
   ```bash
   cd compiler
   python -m unittest tests.test_parser
   ```

### Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Tests**
   ```bash
   cd compiler
   python -m unittest discover tests/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python Style

This project follows PEP 8 with some specific guidelines:

- **Line Length**: 100 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Naming**:
  - Classes: `PascalCase`
  - Functions/Methods: `snake_case`
  - Variables: `snake_case`
  - Constants: `ALL_CAPS`
  - Modules: `snake_case`

### Code Structure

- **Imports**: Grouped as standard library, third-party, local
- **Docstrings**: Use triple quotes for all public functions/classes
- **Type Hints**: Include type hints for function parameters and return values
- **Error Handling**: Use custom exceptions and proper error messages

### Example Code Style

```python
"""
Module docstring describing the purpose.
"""

from typing import Optional, List
import os
import sys

from core.diagnostics import Diagnostics

class ExampleClass:
    """Class docstring."""

    def __init__(self, diagnostics: Diagnostics) -> None:
        """Initialize the class.

        Args:
            diagnostics: Diagnostics instance for error reporting
        """
        self.diagnostics = diagnostics
        self._private_var = 0

    def public_method(self, value: int) -> Optional[str]:
        """Process a value and return result.

        Args:
            value: Input value to process

        Returns:
            Processed result or None if invalid
        """
        if value < 0:
            self.diagnostics.error(1, "Value must be non-negative")
            return None

        return f"Processed: {value}"

    def _private_method(self) -> None:
        """Internal helper method."""
        pass
```

## Adding New CPU Support

The assembler is designed for easy CPU extension. Follow these steps:

### 1. Create CPU Profile Structure

```bash
mkdir -p compiler/cpu_profiles/newcpu
touch compiler/cpu_profiles/newcpu/__init__.py
touch compiler/cpu_profiles/newcpu/newcpu_profile.py
touch compiler/cpu_profiles/newcpu/opcodes_newcpu.py
```

### 2. Define Opcodes (opcodes_newcpu.py)

```python
from enum import Enum, auto

class NewCPUAddressingMode(Enum):
    IMMEDIATE = auto()
    ABSOLUTE = auto()
    RELATIVE = auto()
    # Add more modes as needed

OPCODES = {
    "LDA": {
        NewCPUAddressingMode.IMMEDIATE: [0xA9, 1, {}, ""],
        NewCPUAddressingMode.ABSOLUTE: [0xAD, 2, {}, ""],
    },
    "JMP": {
        NewCPUAddressingMode.ABSOLUTE: [0x4C, 2, {}, ""],
    },
    # Add all opcodes
}
```

### 3. Implement CPU Profile (newcpu_profile.py)

```python
import re
from typing import Any, TYPE_CHECKING

from cpu_profiles.newcpu.opcodes_newcpu import OPCODES, NewCPUAddressingMode
from core.expression_evaluator import evaluate_expression
from core.diagnostics import Diagnostics
from cpu_profiles import CPUProfile

if TYPE_CHECKING:
    from core.parser import Parser

class NewCPUProfile(CPUProfile):
    """CPU profile for NewCPU processor."""

    def __init__(self, diagnostics: Diagnostics):
        self._opcodes = OPCODES
        self._branch_mnemonics = {"JMP", "BEQ"}  # Branch instructions
        self._addressing_modes_enum = NewCPUAddressingMode
        self.diagnostics = diagnostics

    @property
    def opcodes(self):
        return self._opcodes

    @property
    def branch_mnemonics(self):
        return self._branch_mnemonics

    @property
    def addressing_modes_enum(self):
        return self._addressing_modes_enum

    def parse_addressing_mode(self, operand_str: str):
        """Parse addressing modes from operand string."""
        # Implementation here
        pass

    def parse_directive(self, instruction, parser: 'Parser'):
        """Parse assembler directives."""
        # Implementation here
        pass

    def parse_instruction(self, instruction, parser: 'Parser'):
        """Parse CPU instructions."""
        # Implementation here
        pass

    def get_opcode_details(self, instruction, symbol_table):
        """Get opcode details for instruction."""
        # Implementation here
        pass

    def encode_instruction(self, instruction, symbol_table):
        """Encode instruction to machine code."""
        # Implementation here
        pass

    def validate_instruction(self, instruction) -> bool:
        """Validate instruction for common mistakes."""
        # Implementation here
        return True
```

### 4. Register the Profile

Update `compiler/main.py`:

```python
from cpu_profiles.newcpu.newcpu_profile import NewCPUProfile

SUPPORTED_CPUS = {
    "65c02": C6502Profile,
    "6800": C6800Profile,
    "8086": C8086Profile,
    "newcpu": NewCPUProfile,  # Add new CPU
}
```

### 5. Add Tests

Create `compiler/tests/test_newcpu.py`:

```python
import unittest
from cpu_profiles.newcpu.newcpu_profile import NewCPUProfile
from core.diagnostics import Diagnostics

class TestNewCPU(unittest.TestCase):
    def setUp(self):
        self.diagnostics = Diagnostics()
        self.profile = NewCPUProfile(self.diagnostics)

    def test_basic_instruction(self):
        # Test basic instruction parsing
        pass

    # Add more tests
```

## Testing Guidelines

### Unit Tests

- **Coverage**: Aim for high test coverage, especially for CPU profiles
- **Isolation**: Mock external dependencies
- **Naming**: `test_method_name` or `test_condition_expected_result`
- **Assertions**: Use descriptive assertion messages

### Integration Tests

- Test end-to-end assembly of sample programs
- Verify output binary correctness
- Test error conditions and diagnostics

### Running Tests

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_parser

# Run specific test method
python -m unittest tests.test_parser.TestParser.test_parse_line
```

## Documentation

### Code Documentation

- **Docstrings**: Required for all public methods and classes
- **Comments**: Explain complex logic, not obvious code
- **Type Hints**: Include for all function parameters and returns

### User Documentation

- Update README.md for new features
- Add examples in `examples/` directory
- Update `assembler.md` for architectural changes

## Commit Guidelines

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

Examples:
```
feat: add Z80 CPU support
fix: correct branch offset calculation
docs: update installation instructions
```

### Pull Request Process

1. **Create PR**: Use descriptive title and detailed description
2. **Code Review**: Address reviewer feedback
3. **Tests**: Ensure all tests pass
4. **Merge**: Squash merge with descriptive commit message

## Issue Reporting

### Bug Reports

When reporting bugs, include:
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment** (OS, Python version)
- **Sample code** that demonstrates the issue

### Feature Requests

For new features, provide:
- **Use case** and motivation
- **Proposed implementation** (if applicable)
- **Alternatives considered**

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors:

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Report unacceptable behavior to maintainers

## Getting Help

- **Documentation**: Check `assembler.md` for architecture details
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Discord/Slack**: Join our community chat (if available)

Thank you for contributing to the Multi-CPU Assembler! 🎉