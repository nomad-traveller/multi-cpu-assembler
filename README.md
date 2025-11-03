# Multi-CPU Assembler

A modular, extensible assembler supporting multiple CPU architectures through YAML-based CPU profiles. Currently supports 65C02 and Motorola 6800 with easy extensibility for additional architectures.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-24%20passing-brightgreen.svg)](tests/)

## Features

- **YAML Format Support**: CPU architectures defined in YAML format
- **Multi-CPU Support**: Currently supports 65C02 and Motorola 6800 architectures
- **Easy Extensibility**: Add new CPUs by creating YAML profiles - no code changes needed
- **Two-Pass Assembly**: Efficient symbol resolution and error detection
- **Enhanced Error Reporting**: Detailed warnings and error messages for common assembly mistakes
- **Generic Validation Engine**: Rule-based validation system that's fully CPU-agnostic
- **Expression Evaluation**: Support for complex expressions with operators and symbols
- **Comprehensive Testing**: Full test suite with profile validation
- **Independent Testing**: CPU profiles can be validated without running the assembler

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/multi-cpu-assembler.git
cd multi-cpu-assembler
```

2. Set up the virtual environment:
```bash
python3 -m venv compiler/.venv
source compiler/.venv/bin/activate  # On Windows: compiler\.venv\Scripts\activate
pip install sly PyYAML
```

### Basic Usage

Assemble a source file:
```bash
python compiler/main.py source_file.s -o output.bin --cpu 65c02
```

Example assembly file (`hello_65c02.s`):
```assembly
; Simple 65C02 program
.ORG $8000

START:  LDA #$48        ; 'H'
        JSR $FFD2       ; Print character
        LDA #$45        ; 'E'
        JSR $FFD2
        LDA #$4C        ; 'L'
        JSR $FFD2
        LDA #$4C        ; 'L'
        JSR $FFD2
        LDA #$4F        ; 'O'
        JSR $FFD2
        RTS

.END
```

## Supported CPUs

### 65C02 (Enhanced 6502)
- **Profiles**: `compiler/cpu_profiles/65c02.yaml` (YAML)
- **Instructions**: 64 mnemonics, 178 total opcodes
- **Addressing Modes**: 14 modes (IMPLIED, IMMEDIATE, ABSOLUTE, etc.)
- **Features**: Full 65C02 instruction set with enhanced error checking

### Motorola 6800
- **Profiles**: `compiler/cpu_profiles/6800.yaml` (YAML)
- **Instructions**: 27 mnemonics, 61 total opcodes
- **Addressing Modes**: 8 modes (INHERENT, IMMEDIATE, EXTENDED, etc.)
- **Features**: Complete 6800 instruction set with accumulator operations

### Adding New CPUs
New CPU architectures can be added by creating YAML profiles in `compiler/cpu_profiles/`. No code changes required! See `TESTING.md` for profile validation tools.

## Architecture

The assembler follows a clean, modular architecture with YAML-driven CPU profiles:

```
Project Root/
├── compiler/
│   ├── main.py (Entry Point)
│   ├── cpu_profile_base.py (YAML profile loader)
│   ├── core/ (Core assembler components)
│   │   ├── parser.py (Source parsing)
│   │   ├── assembler.py (Two-pass assembly)
│   │   ├── emitter.py (Output generation)
│   │   ├── diagnostics.py (Error reporting)
│   │   ├── expression_evaluator.py (Expression evaluation)
│   │   ├── expression_parser.py (Expression parsing)
│   │   ├── instruction.py (Instruction representation)
│   │   ├── program.py (Program representation)
│   │   └── symbol_table.py (Symbol management)
│   └── cpu_profiles/ (CPU definitions)
│       ├── 65c02.yaml (65C02 CPU definition)
│       ├── 6800.yaml (6800 CPU definition)
│       └── [new_cpu].yaml (Add your own CPU!)
├── tests/ (Test suite)
│   ├── test_assembler.py (Core assembler tests)
│   ├── test_yaml_cpu_profiles.py (Profile tests)
│   ├── test_end_to_end_65c02.py (65C02 integration tests)
│   ├── test_end_to_end_6800.py (6800 integration tests)
│   └── test_*.s (Test assembly files)
├── examples/ (Example programs)
│   ├── mcu65c02.s (65C02 LED blink example)
│   └── mcu6800.s (6800 PIA example)
└── docs/ (Documentation)
    ├── README.md (Main documentation)
    ├── TESTING.md (Testing guide)
    ├── CONTRIBUTING.md (Contribution guidelines)
    └── YAML_MIGRATION.md (Migration guide)
```

### Key Components

#### Core Components (`compiler/core/`)
- **Parser**: Converts assembly source into structured instructions with proper syntax validation
- **Assembler**: Performs two-pass assembly with symbol resolution and error handling
- **Emitter**: Generates binary output and assembly listings with address information
- **Diagnostics**: Centralized error and warning reporting with detailed messages
- **Expression Evaluator**: Handles complex expressions, symbol resolution, and mathematical operations
- **Expression Parser**: SLY-based parser for assembly expressions with operator precedence
- **Instruction**: Represents assembly instructions with metadata and machine code
- **Program**: Manages instruction sequences and assembly state
- **Symbol Table**: Handles label definitions, symbol resolution, and EQU directives

#### CPU Profile System (`compiler/`)
- **ConfigCPUProfile**: Loads and validates YAML CPU profiles with automatic format detection
- **CPUProfileFactory**: Simple factory that creates ConfigCPUProfile instances from YAML files
- **CPU Profiles**: YAML files defining opcodes, addressing modes, directives, and validation rules

#### Generic Validation Engine
- **Rule-based System**: Validates instructions without CPU-specific code
- **Multiple Rule Types**: Mode validation, range checking, register-specific rules
- **Template-driven**: All validation logic defined in YAML, not Python code
- **Backward Compatible**: Supports legacy validation format alongside new generic rules

#### Testing Framework (`tests/`)
- **Unit Tests**: Core component testing with mocking and isolation
- **Integration Tests**: End-to-end assembly workflow validation
- **Profile Tests**: YAML CPU profile validation and functionality testing
- **Test Data**: Comprehensive assembly files for various scenarios

## Project Structure

```
multi-cpu-assembler/
├── compiler/                          # Main assembler package
│   ├── main.py                        # CLI entry point and application bootstrap
│   ├── cpu_profile_base.py            # YAML profile loader and factory
│   ├── core/                          # Core assembler components
│   │   ├── assembler.py               # Two-pass assembly engine
│   │   ├── parser.py                  # Assembly source parser
│   │   ├── emitter.py                 # Binary output generator
│   │   ├── diagnostics.py             # Error reporting system
│   │   ├── expression_evaluator.py     # Expression evaluation engine
│   │   ├── expression_parser.py        # SLY-based expression parser
│   │   ├── instruction.py             # Instruction representation
│   │   ├── program.py                # Program state management
│   │   └── symbol_table.py           # Symbol resolution and labels
│   ├── cpu_profiles/                 # CPU architecture definitions
│   │   ├── 65c02.yaml               # 65C02 CPU profile (178 opcodes)
│   │   ├── 6800.yaml                # 6800 CPU profile (61 opcodes)
│   │   └── [new_cpu].yaml           # Add your own CPU here!
│   └── .venv/                       # Python virtual environment
├── tests/                            # Comprehensive test suite
│   ├── test_assembler.py              # Core assembler unit tests (4 tests)
│   ├── test_yaml_cpu_profiles.py      # YAML profile tests (10 tests)
│   ├── test_end_to_end_65c02.py     # 65C02 integration tests (5 tests)
│   ├── test_end_to_end_6800.py      # 6800 integration tests (5 tests)
│   ├── test_comprehensive_65c02.s     # Comprehensive 65C02 test file
│   ├── test_comprehensive_6800.s      # Comprehensive 6800 test file
│   ├── test_simple_65c02.s           # Simple 65C02 test file
│   └── test_simple.s                 # Generic test file
├── examples/                         # Example assembly programs
│   ├── mcu65c02.s                  # 65C02 LED blink program
│   ├── mcu65c02.bin                # Compiled 65C02 binary
│   ├── mcu6800.s                   # 6800 PIA control program
│   └── mcu6800.bin                # Compiled 6800 binary
├── .github/                          # GitHub configuration
│   ├── ISSUE_TEMPLATE/                # Issue templates
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md       # PR template
├── docs/                             # Project documentation
│   ├── README.md                     # Main documentation (this file)
│   ├── TESTING.md                    # Testing procedures and guidelines
│   ├── CONTRIBUTING.md                # Contribution guidelines
│   ├── AGENTS.md                    # Development agent guidelines
│   ├── YAML_MIGRATION.md             # Profile format migration guide
│   └── GITHUB_ISSUES.md             # Issue tracking templates
├── LICENSE                           # MIT License
├── .gitignore                        # Git ignore rules
└── setup_github.sh                   # GitHub setup script
```

### Directory Purposes

- **`compiler/`**: Main package containing the assembler implementation
- **`compiler/core/`**: Core assembly components with clear separation of concerns
- **`compiler/cpu_profiles/`**: YAML-based CPU architecture definitions
- **`tests/`**: Complete test suite with unit and integration tests
- **`examples/`**: Working assembly programs demonstrating CPU features
- **`.github/`**: GitHub templates and automation configuration
- **`docs/`**: Comprehensive documentation for users and contributors

### Generic Validation Engine

The assembler features a powerful, CPU-agnostic validation engine that uses rule-based validation defined entirely in YAML files. This means:

- **No Hard-coded Logic**: The Python code contains no CPU-specific validation logic
- **Extensible Rules**: Add new validation types without modifying Python code
- **Flexible Conditions**: Support for complex validation scenarios with exceptions
- **Backward Compatible**: Legacy validation format still supported

**Supported Validation Rule Types:**
- `error_if_mode_is` - Error if instruction uses specific addressing modes
- `error_if_mode_is_not` - Error if instruction doesn't use specific addressing modes  
- `warning_if_mode_is` - Warning if instruction uses specific addressing modes
- `warning_if_mode_is_not` - Warning if instruction doesn't use specific addressing modes
- `error_if_operand_out_of_range` - Error if operand value is outside valid range
- `warning_if_operand_out_of_range` - Warning if operand value is outside optimal range
- `error_if_register_used` / `warning_if_register_used` - Register-specific validation

**Example Validation Rule:**
```yaml
validation_rules:
  - type: "warning_if_mode_is"
    mnemonics: ["LDA", "STA", "LDX", "STX"]
    modes: ["ABSOLUTE"]
    message: "Instruction {mnemonic} uses absolute addressing. Consider using zero-page addressing for values under $0100."
```

## Development

### Adding New CPU Support

The assembler is designed for easy extension through YAML profiles. To add a new CPU:

1. **Create Profile**: Add `new_cpu.yaml` in `compiler/cpu_profiles/`
2. **Define CPU Info**: Include name, description, data width, address width, endianness
3. **Specify Addressing Modes**: List all addressing modes with enum values
4. **Add Opcodes**: Define all instructions with their opcodes, cycles, and flags
5. **Define Directives**: Specify assembler directives (EQU, .ORG, .BYTE, etc.)
6. **Add Validation Rules**: Use generic rule-based validation system
7. **Validate**: Use `python -m unittest tests.test_yaml_cpu_profiles` to test

The simplified CPUProfileFactory automatically detects and loads any YAML profile files without requiring custom Python code.

**Example YAML Structure**:
```yaml
cpu_info:
  name: 'NEW_CPU'
  description: New CPU Architecture
  data_width: 8
  address_width: 16
  endianness: little
  fill_byte: "0x00"

addressing_modes:
  IMPLIED: 0
  IMMEDIATE: 1

opcodes:
  NOP:
    IMPLIED: [0x00, 0, 2, ""]

directives:
  EQU:
    type: "symbol_define"
  .ORG:
    type: "origin_set"

validation_rules:
  - type: "error_if_mode_is_not"
    mnemonics: ["NOP"]
    modes: ["IMPLIED"]
    message: "Instruction {mnemonic} must use inherent addressing (no operands)."
```

See `TESTING.md` for profile validation tools and detailed instructions.

### Running Tests

```bash
# Run all tests
. compiler/.venv/bin/activate && python -m unittest discover tests/

# Run specific test file
. compiler/.venv/bin/activate && python -m unittest tests.test_yaml_cpu_profiles

# Run tests with verbose output
. compiler/.venv/bin/activate && python -m unittest discover tests/ -v
```

See `TESTING.md` for comprehensive testing documentation.

### Building Examples

```bash
. compiler/.venv/bin/activate

# 65C02 example
python compiler/main.py examples/mcu65c02.s -o examples/mcu65c02.bin --cpu 65c02

# 6800 example
python compiler/main.py examples/mcu6800.s -o examples/mcu6800.bin --cpu 6800
```

## Command Line Options

```
usage: main.py [-h] [--cpu {65c02,6800}] [--start-address START_ADDRESS]
               [--output OUTPUT] [--log-file LOG_FILE]
               source_file

Multi-CPU Assembler

positional arguments:
  source_file           Assembly source file to assemble

optional arguments:
  -h, --help            show this help message and exit
  --cpu {65c02,6800}    Target CPU architecture
  --start-address START_ADDRESS
                        Starting address (default: 0x0000)
  --output OUTPUT       Output binary file
  --log-file LOG_FILE   Log file for detailed output
```

## Error Reporting

The assembler provides detailed error messages and warnings:

```
Warning on line 5: Label 'INVALID-LABEL' contains invalid characters. Labels should start with a letter or underscore and contain only letters, digits, and underscores.
Warning on line 8: Missing spaces around '+' operator in operand '#$10+$20'. Consider adding spaces for clarity.
Error on line 8: Could not determine addressing mode for operand: #$10+$20
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- **New CPU Profiles**: Add support for additional processors
- **Output Formats**: Intel HEX, Motorola S-record, ELF
- **Macro System**: Assembly macro support
- **Conditional Assembly**: IF/ELSE/ENDIF directives
- **Performance**: Optimization and benchmarking
- **Documentation**: Improve docs and examples

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Testing and Validation

This project includes comprehensive testing tools:

- **Unit Tests**: 24 tests covering YAML profiles, assembly workflow, and CLI
- **Profile Validation**: Standalone tools for validating CPU profiles
- **Interactive Testing**: Real-time testing of addressing modes and opcodes
- **End-to-End Testing**: Complete assembly workflow validation
- **Test Coverage**: 100% test pass rate with comprehensive error handling validation


See `TESTING.md` for detailed testing documentation and usage examples.

## Roadmap

- [ ] Add Z80 CPU support (YAML profile)
- [ ] Implement macro system
- [ ] Add conditional assembly
- [ ] Support additional output formats (Intel HEX, S-record)
- [ ] IDE integration features
- [ ] Web-based interface for CPU profile creation
- [ ] Profile editor with real-time validation

## Acknowledgments

- Built with [SLY](https://github.com/dabeaz/sly) for expression parsing
- Inspired by classic assemblers and modern compiler design
- Thanks to contributors and the open source community