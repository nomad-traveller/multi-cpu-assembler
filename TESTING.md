# Testing Guide

This document provides comprehensive testing documentation for the Multi-CPU Assembler, including JSON5/YAML CPU profile validation, unit testing, and interactive testing tools.

## Overview

The assembler includes a complete testing suite designed to validate both the core functionality and the JSON5/YAML-based CPU profiles. All tests can be run independently of the main assembler.

## Test Suite Structure

```
tests/
├── test_json_cpu_profiles.py     # Profile functionality (10 tests)
├── test_end_to_end_65c02.py      # 65C02 assembly workflow (5 tests)
└── test_end_to_end_6800.py       # 6800 assembly workflow (5 tests)

Profile Testing Tools:
├── validate_json_profiles.py     # Automated profile validator (JSON5/YAML)
├── test_json_interactive.py      # Interactive profile tester
├── convert_to_yaml.py           # JSON5 to YAML conversion tool
└── JSON_TESTING_SUMMARY.md       # Complete testing documentation
```

## Quick Testing Commands

### Run All Tests
```bash
# Activate virtual environment
. compiler/.venv/bin/activate

# Run complete test suite
python -m unittest discover -s tests -p "test_*.py"

# Expected: Ran 20 tests, OK
```

### Validate CPU Profiles (JSON5/YAML)
```bash
# Validate all profiles (both JSON5 and YAML)
python validate_json_profiles.py --all

# Validate specific profile
python validate_json_profiles.py compiler/cpu_profiles/65c02.json
python validate_json_profiles.py compiler/cpu_profiles/65c02.yaml

# Expected output:
# ✅ 65c02.json: VALID
# ✅ 65c02.yaml: VALID
# ✅ 6800.json: VALID
# ✅ 6800.yaml: VALID
# ✅ All profile files are valid!
```

### Interactive Testing
```bash
# Interactive menu for testing profiles (supports both formats)
python test_json_interactive.py

# Test specific profile directly
python test_json_interactive.py compiler/cpu_profiles/65c02.json
python test_json_interactive.py compiler/cpu_profiles/65c02.yaml
```

## CPU Profile Testing (JSON5/YAML)

### Automated Validation (`validate_json_profiles.py`)

This tool performs comprehensive validation of CPU profiles in both JSON5 and YAML formats:

**Features:**
- JSON5/YAML syntax validation
- Required sections checking
- Data type validation
- Cross-reference validation
- Detailed analysis reporting
- Automatic format detection

**Validation Criteria:**
- ✅ JSON5/YAML syntax is valid
- ✅ Required sections exist (cpu_info, addressing_modes, opcodes, etc.)
- ✅ CPU information is complete
- ✅ Addressing modes are properly defined
- ✅ Opcodes reference valid addressing modes
- ✅ Mnemonics are properly formatted
- ✅ Addressing patterns are valid regex
- ✅ Directives are properly defined

**Example Output:**
```
🔍 CPU Profile Validation (JSON/YAML)
============================================================
✅ 65c02.json: VALID
   📋 CPU: 65C02 (8-bit, 16-bit, little endian)
   🔧 Addressing Modes: 14
   📝 Mnemonics: 64
   🔢 Total Opcodes: 178
   🌿 Branch Instructions: 9
   🎯 Addressing Patterns: 15
   📜 Has Directives: Yes
   ⚖️  Has Validation Rules: Yes

✅ 65c02.yaml: VALID
   📋 CPU: 65C02 (8-bit, 16-bit, little endian)
   🔧 Addressing Modes: 14
   📝 Mnemonics: 64
   🔢 Total Opcodes: 178
   🌿 Branch Instructions: 9
   🎯 Addressing Patterns: 15
   📜 Has Directives: Yes
   ⚖️  Has Validation Rules: Yes
```

### Interactive Testing (`test_json_interactive.py`)

This tool provides interactive testing of CPU profile functionality:

**Features:**
- CPU information display
- Addressing mode enumeration
- Mnemonic listing
- Real-time addressing mode parsing tests
- Opcode lookup testing
- CPU-specific test cases

**Interactive Menu:**
```
🎯 Available CPU Profiles:
   1. 65c02.json
   2. 65c02.yaml
   3. 6800.json
   4. 6800.yaml
   5. Test all profiles
   0. Exit

Select profile to test (0-5):
```

**Testing Capabilities:**

1. **Addressing Mode Parsing Tests:**
   ```python
   test_cases = [
       "#$FF",      # Immediate
       "$1234",      # Absolute
       "$00",         # Zero page
       "NOP",         # Implied
       "($1234)",     # Indirect
       "($00,X)",     # Indexed X indirect
   ]
   ```

2. **Opcode Lookup Tests:**
   ```python
   test_instructions = [
       ("LDA", "IMMEDIATE"),
       ("JMP", "ABSOLUTE"),
       ("BNE", "RELATIVE"),
   ]
   ```

**Example Output:**
```
🔧 Testing Addressing Mode Parsing:
----------------------------------------
✅ '#$FF' -> Mode: 2, Value: 255
✅ '$1234' -> Mode: 6, Value: 4660
✅ 'NOP' -> Mode: 0, Value: NOP

🔍 Testing Opcode Lookup:
----------------------------------------
✅ LDA IMMEDIATE -> Opcode: $A9, Size: 1, Cycles: {'base': 2}, Flags: NZ
✅ JMP ABSOLUTE -> Opcode: $4C, Size: 2, Cycles: {'base': 3}, Flags: 
```

## Unit Testing

### Test Categories

#### 1. CPU Profile Tests (`test_json_cpu_profiles.py`)
**10 tests covering:**
- ConfigCPUProfile class functionality (JSON5/YAML)
- CPUProfileFactory testing
- Error handling and validation
- Addressing mode parsing
- Opcode lookup functionality

**Key Test Methods:**
```python
def test_load_65c02_profile(self)
def test_load_6800_profile(self)
def test_invalid_json_file(self)
def test_addressing_mode_parsing(self)
def test_opcode_lookup(self)
def test_cpu_info_extraction(self)
def test_branch_instructions(self)
def test_directives(self)
def test_validation_rules(self)
def test_factory_invalid_cpu(self)
```

#### 2. End-to-End 65C02 Tests (`test_end_to_end_65c02.py`)
**5 tests covering:**
- Complete 65C02 assembly workflow
- CLI integration testing
- Real assembly file processing
- Error handling validation

**Test Files:**
- Simple instruction assembly
- Symbol resolution testing
- Directive processing
- Error case handling

#### 3. End-to-End 6800 Tests (`test_end_to_end_6800.py`)
**5 tests covering:**
- Complete 6800 assembly workflow
- CLI integration testing
- Real assembly file processing
- Error handling validation

### Running Individual Tests

```bash
# Run specific test file
. compiler/.venv/bin/activate && python -m unittest tests.test_json_cpu_profiles

# Run specific test method
. compiler/.venv/bin/activate && python -m unittest tests.test_json_cpu_profiles.TestConfigCPUProfile.test_load_65c02_profile

# Run with verbose output
. compiler/.venv/bin/activate && python -m unittest discover -s tests -p "test_*.py" -v
```

## Test Data and Examples

### Sample Assembly Files for Testing

**65C02 Test File (`examples/mcu65c02.s`):**
```assembly
; 65C02 test program
.ORG $8000

START:  LDA #$48        ; Load immediate
        STA $0200       ; Store absolute
        LDX #$00        ; Load X register
        INX             ; Increment X
        BNE LOOP        ; Branch if not equal
LOOP:   JMP START       ; Jump to start
        RTS             ; Return from subroutine

.END
```

**6800 Test File (`examples/mcu6800.s`):**
```assembly
; 6800 test program
.ORG $8000

START:  LDAA #$48       ; Load accumulator A immediate
        STAA $0080      ; Store accumulator A direct
        LDX #$0000      ; Load index register extended
        INX             ; Increment index register
        BNE LOOP        ; Branch if not equal
LOOP:   JMP START       ; Jump to start
        RTS             ; Return from subroutine

.END
```

## Expected Test Results

### Current Test Suite Status
- **Total Tests**: 20
- **Pass Rate**: 100% (20/20)
- **Coverage**: JSON profiles, assembly workflow, CLI integration

### JSON Profile Validation Results
- **65C02 Profile**: ✅ VALID (178 opcodes, 14 addressing modes, 64 mnemonics)
- **6800 Profile**: ✅ VALID (61 opcodes, 8 addressing modes, 27 mnemonics)

### Test Output Examples

**Successful Test Run:**
```
..........
----------------------------------------------------------------------
Ran 10 tests in 0.012s

OK

.....
----------------------------------------------------------------------
Ran 5 tests in 0.008s

OK

.....
----------------------------------------------------------------------
Ran 5 tests in 0.007s

OK
```

**JSON Validation Output:**
```
✅ 65c02.json: VALID
   📋 CPU: 65C02 (8-bit, 16-bit, little endian)
   🔧 Addressing Modes: 14
   📝 Mnemonics: 64
   🔢 Total Opcodes: 178
```

## Troubleshooting

### Common Test Issues

1. **Import Errors:**
   ```bash
   # Ensure virtual environment is activated
   . compiler/.venv/bin/activate
   
   # Install required dependencies
   pip install sly
   ```

2. **Path Issues:**
   ```bash
   # Run from project root directory
   pwd  # Should be /home/user/myproject
   ```

3. **Profile Validation Failures:**
   ```bash
   # Check JSON5 syntax
   python -c "import json5; print(json5.load(open('compiler/cpu_profiles/65c02.json')))"
   
   # Check YAML syntax
   python -c "import yaml; print(yaml.safe_load(open('compiler/cpu_profiles/65c02.yaml')))"
   
   # Run detailed validation
   python validate_json_profiles.py compiler/cpu_profiles/65c02.json
   python validate_json_profiles.py compiler/cpu_profiles/65c02.yaml
   ```

### Debug Mode

For detailed test output, run with increased verbosity:

```bash
. compiler/.venv/bin/activate && python -m unittest discover -s tests -p "test_*.py" -v
```

## Contributing to Tests

### Adding New Tests

1. **Unit Tests**: Add to appropriate test file in `tests/`
2. **JSON Profile Tests**: Add to `test_json_cpu_profiles.py`
3. **End-to-End Tests**: Add to CPU-specific test files

### Test Naming Conventions

- Test classes: `TestClassName`
- Test methods: `test_functionality_description`
- Descriptive names that explain what is being tested

### Test Structure

```python
import unittest
from unittest.mock import patch, MagicMock

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_specific_functionality(self):
        """Test specific functionality with clear description."""
        # Arrange
        # Act
        # Assert
        pass
    
    def tearDown(self):
        """Clean up after tests."""
        pass
```

## Continuous Integration

The test suite is designed for CI/CD integration:

```bash
# CI-friendly test command
. compiler/.venv/bin/activate && python -m unittest discover -s tests -p "test_*.py" && python validate_json_profiles.py --all
```

This command runs all unit tests and validates CPU profiles (both JSON5 and YAML), providing comprehensive validation.

## Performance Testing

For performance benchmarking:

```bash
# Time the test suite
time . compiler/.venv/bin/activate && python -m unittest discover -s tests -p "test_*.py"

# Profile JSON validation
python -m cProfile validate_json_profiles.py --all
```

## Conclusion

The testing suite provides comprehensive coverage of the assembler's functionality, with special emphasis on the JSON5/YAML-based CPU profile system. All tools are designed for independent operation and can be used without running the main assembler.

**Status**: ✅ All tests passing, JSON validation complete