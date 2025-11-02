# Multi-CPU Assembler

A modular, extensible assembler supporting multiple CPU architectures through JSON-based CPU profiles. Currently supports 65C02 and Motorola 6800 with easy extensibility for additional architectures.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-20%20passing-brightgreen.svg)](tests/)

## Features

- **JSON-Driven CPU Profiles**: CPU architectures defined in flexible JSON format
- **Multi-CPU Support**: Currently supports 65C02 and Motorola 6800 architectures
- **Easy Extensibility**: Add new CPUs by creating JSON profiles - no code changes needed
- **Two-Pass Assembly**: Efficient symbol resolution and error detection
- **Enhanced Error Reporting**: Detailed warnings and error messages for common assembly mistakes
- **Expression Evaluation**: Support for complex expressions with operators and symbols
- **Comprehensive Testing**: Full test suite with JSON profile validation
- **Independent Testing**: JSON profiles can be validated without running the assembler

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
pip install sly
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
- **JSON Profile**: `compiler/cpu_profiles/65c02.json`
- **Instructions**: 64 mnemonics, 178 total opcodes
- **Addressing Modes**: 14 modes (IMPLIED, IMMEDIATE, ABSOLUTE, etc.)
- **Features**: Full 65C02 instruction set with enhanced error checking

### Motorola 6800
- **JSON Profile**: `compiler/cpu_profiles/6800.json`
- **Instructions**: 27 mnemonics, 61 total opcodes
- **Addressing Modes**: 8 modes (INHERENT, IMMEDIATE, EXTENDED, etc.)
- **Features**: Complete 6800 instruction set with accumulator operations

### Adding New CPUs
New CPU architectures can be added by creating JSON profiles in `compiler/cpu_profiles/`. No code changes required! See `TESTING.md` for JSON profile validation tools.

## Architecture

The assembler follows a clean, modular architecture with JSON-driven CPU profiles:

```
main.py (Entry Point)
├── parser.py (Source parsing)
├── assembler.py (Two-pass assembly)
├── emitter.py (Output generation)
├── diagnostics.py (Error reporting)
├── cpu_profile_base.py (JSON profile loader)
└── cpu_profiles/ (JSON CPU definitions)
    ├── 65c02.json
    ├── 6800.json
    └── [new_cpu].json (add your own!)
```

### Key Components

- **Parser**: Converts assembly source into structured instructions
- **Assembler**: Performs two-pass assembly with symbol resolution
- **JSONCPUProfile**: Loads and validates JSON CPU profiles
- **CPU Profiles**: JSON files defining opcodes, addressing modes, and validation rules
- **Expression Evaluator**: Handles complex expressions and symbol resolution
- **Diagnostics**: Centralized error and warning reporting

## Development

### Adding New CPU Support

The assembler is designed for easy extension through JSON profiles. To add a new CPU:

1. **Create JSON Profile**: Add `new_cpu.json` in `compiler/cpu_profiles/`
2. **Define CPU Info**: Include name, description, data width, address width
3. **Specify Addressing Modes**: List all addressing modes with enum values
4. **Add Opcodes**: Define all instructions with their opcodes, cycles, and flags
5. **Include Validation Rules**: Specify addressing patterns and directives
6. **Validate**: Use `python validate_json_profiles.py --all` to test

**Example JSON Structure**:
```json
{
  "cpu_info": {
    "name": "NEW_CPU",
    "description": "New CPU Architecture",
    "data_width": 8,
    "address_width": 16
  },
  "addressing_modes": {
    "IMPLIED": 0,
    "IMMEDIATE": 1
  },
  "opcodes": {
    "NOP": {
      "IMPLIED": {"opcode": 0x00, "cycles": 2}
    }
  }
}
```

See `TESTING.md` for JSON validation tools and detailed instructions.

### Running Tests

```bash
# Run all tests
. compiler/.venv/bin/activate && python -m unittest discover -s tests -p "test_*.py"

# Validate JSON CPU profiles
python validate_json_profiles.py --all

# Interactive JSON testing
python test_json_interactive.py
```

See `TESTING.md` for comprehensive testing documentation.

### Building Examples

```bash
cd compiler
source .venv/bin/activate

# 65C02 example
python main.py examples/mcu65c02.s -o examples/mcu65c02.bin --cpu 65c02

# 6800 example
python main.py examples/mcu6800.s -o examples/mcu6800.bin --cpu 6800

# 8086 example
python main.py examples/hello_8086.s -o examples/hello_8086.bin --cpu 8086
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

- **Unit Tests**: 20 tests covering JSON profiles, assembly workflow, and CLI
- **JSON Validation**: Standalone tools for validating CPU profiles
- **Interactive Testing**: Real-time testing of addressing modes and opcodes
- **End-to-End Testing**: Complete assembly workflow validation

See `TESTING.md` for detailed testing documentation and usage examples.

## Roadmap

- [ ] Add Z80 CPU support (JSON profile)
- [ ] Implement macro system
- [ ] Add conditional assembly
- [ ] Support additional output formats (Intel HEX, S-record)
- [ ] IDE integration features
- [ ] Web-based interface for JSON profile creation

## Acknowledgments

- Built with [SLY](https://github.com/dabeaz/sly) for expression parsing
- Inspired by classic assemblers and modern compiler design
- Thanks to contributors and the open source community