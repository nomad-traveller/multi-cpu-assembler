# Testing Guide

This document provides comprehensive testing documentation for the Multi-CPU Assembler, including YAML CPU profile validation, unit testing, and interactive testing tools.

## Overview

The assembler includes a complete testing suite designed to validate both the core functionality and the JSON5/YAML-based CPU profiles. All tests can be run independently of the main assembler.

## Test Suite Structure

```
tests/
├── test_assembler.py             # Core assembler functionality (4 tests)
├── test_yaml_cpu_profiles.py     # YAML profile functionality (10 tests)
├── test_end_to_end_65c02.py      # 65C02 assembly workflow (5 tests)
└── test_end_to_end_6800.py       # 6800 assembly workflow (5 tests)
```

## Quick Testing Commands

### Run All Tests
```bash
# Activate virtual environment
. compiler/.venv/bin/activate

# Run complete test suite
python -m unittest discover -s tests -p "test_*.py"

# Expected: Ran 24 tests, OK
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

#### 1. Core Assembler Tests (`test_assembler.py`)
**4 tests covering:**
- Two-pass assembly process
- Symbol resolution and management
- Machine code generation
- Error handling for duplicate labels

#### 2. CPU Profile Tests (`test_yaml_cpu_profiles.py`)
**10 tests covering:**
- ConfigCPUProfile class functionality (YAML)
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
. compiler/.venv/bin/activate && python -m unittest tests.test_yaml_cpu_profiles

# Run specific test method
. compiler/.venv/bin/activate && python -m unittest tests.test_yaml_cpu_profiles.TestYAMLConfigCPUProfile.test_load_valid_profile

# Run with verbose output
. compiler/.venv/bin/activate && python -m unittest discover tests/ -v
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
- **Total Tests**: 24
- **Pass Rate**: 100% (24/24)
- **Coverage**: Core assembler, YAML profiles, assembly workflow, CLI integration

### YAML Profile Validation Results
- **65C02 Profile**: ✅ VALID (178 opcodes, 14 addressing modes, 64 mnemonics)
- **6800 Profile**: ✅ VALID (61 opcodes, 8 addressing modes, 27 mnemonics)

### Test Output Examples

**Successful Test Run:**
```
....
----------------------------------------------------------------------
Ran 4 tests in 0.007s

OK

..........
----------------------------------------------------------------------
Ran 10 tests in 0.055s

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

**YAML Profile Validation Output:**
```
✅ 65c02.yaml: VALID
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

## Validation Engine Testing

The generic validation engine is tested through the main test suite and can be validated independently:

### Validation Rule Types Testing

The validation engine supports these rule types (all tested in end-to-end tests):

1. **Mode-based Validation:**
   - `error_if_mode_is` - Tests accumulator-only instructions
   - `error_if_mode_is_not` - Tests inherent-only instructions  
   - `warning_if_mode_is` - Tests optimization hints
   - `warning_if_mode_is_not` - Tests typical usage patterns

2. **Operand Range Validation:**
   - `error_if_operand_out_of_range` - Tests immediate value limits
   - `warning_if_operand_out_of_range` - Tests optimization opportunities

3. **Register-specific Validation:**
   - `error_if_register_used` - Tests register conflicts
   - `warning_if_register_used` - Tests register usage warnings

### Testing Validation Rules

Create test files to trigger validation:

```bash
# Test 65C02 validation
cat > test_validation.s << 'EOF'
    .ORG $8000
    LDA $0050   ; Should warn about zero-page optimization
    RTS
EOF

python compiler/main.py test_validation.s -o output.bin --cpu 65c02
# Expected: Warning about using absolute addressing for zero-page value

# Test 6800 validation  
cat > test_validation.s << 'EOF'
    .ORG $8000
    LDAA $0050  ; Should warn about direct-page optimization
    RTS
EOF

python compiler/main.py test_validation.s -o output.bin --cpu 6800
# Expected: Warning about using extended addressing for direct-page value
```

### Validation Rule Examples

**65C02 Validation Rules:**
```yaml
validation_rules:
  - type: "warning_if_mode_is"
    mnemonics: ["LDA", "STA", "LDX", "STX"]
    modes: ["ABSOLUTE"]
    message: "Instruction {mnemonic} uses absolute addressing. Consider using zero-page addressing for values under $0100."
```

**6800 Validation Rules:**
```yaml
validation_rules:
  - type: "error_if_mode_is_not"
    mnemonics: ["ABA", "CBA", "SBA"]
    modes: ["INHERENT"]
    message: "Instruction {mnemonic} must use INHERENT addressing (no operands)."
```

### Backward Compatibility

The validation engine maintains backward compatibility with legacy validation format:

```yaml
# Legacy format (still supported)
validation_rules:
  accumulator_only:
    ASL: ["IMMEDIATE"]
  branch_valid_modes:
    BCC: ["RELATIVE", "DIRECT", "EXTENDED"]

# New generic format (recommended)
validation_rules:
  - type: "error_if_mode_is"
    mnemonics: ["ASL"]
    modes: ["IMMEDIATE"]
    message: "Instruction {mnemonic} cannot use IMMEDIATE addressing."
```

## Conclusion

The testing suite provides comprehensive coverage of the assembler's functionality, with special emphasis on YAML-based CPU profile system and generic validation engine. All tools are designed for independent operation and can be used without running the main assembler.

**Status**: ✅ All tests passing (24/24), YAML validation complete, generic validation engine operational