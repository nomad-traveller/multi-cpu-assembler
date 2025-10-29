# Multi-CPU Assembler

A modular, extensible assembler supporting multiple CPU architectures including 65C02, 6800, and 8086. Built with Python for educational and development purposes.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- **Multi-CPU Support**: Currently supports 65C02, Motorola 6800, and Intel 8086 architectures
- **Modular Architecture**: Easy to extend with new CPU profiles
- **Two-Pass Assembly**: Efficient symbol resolution and error detection
- **Enhanced Error Reporting**: Detailed warnings and error messages for common assembly mistakes
- **Expression Evaluation**: Support for complex expressions with operators and symbols
- **Multiple Output Formats**: Raw binary output with plans for additional formats
- **Comprehensive Testing**: Full test suite with CPU-specific validation

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
- Full 65C02 instruction set
- All addressing modes
- Enhanced error checking for common 6502 mistakes

### Motorola 6800
- Complete 6800 instruction set
- Accumulator and index register operations
- Page zero optimization hints

### Intel 8086
- 16-bit instruction set
- Segment register handling
- Memory and register operations

## Architecture

The assembler follows a clean, modular architecture:

```
main.py (Entry Point)
├── parser.py (Source parsing)
├── assembler.py (Two-pass assembly)
├── emitter.py (Output generation)
├── diagnostics.py (Error reporting)
└── cpu_profiles/ (CPU-specific logic)
    ├── c6502/
    ├── c6800/
    └── c8086/
```

### Key Components

- **Parser**: Converts assembly source into structured instructions
- **Assembler**: Performs two-pass assembly with symbol resolution
- **CPU Profiles**: Encapsulate CPU-specific behavior (opcodes, addressing modes, validation)
- **Expression Evaluator**: Handles complex expressions and symbol resolution
- **Diagnostics**: Centralized error and warning reporting

## Development

### Adding New CPU Support

The assembler is designed for easy extension. To add a new CPU:

1. Create opcode definitions in `compiler/cpu_profiles/newcpu/opcodes_newcpu.py`
2. Implement CPU profile class in `compiler/cpu_profiles/newcpu/newcpu_profile.py`
3. Register the profile in `compiler/main.py`
4. Add tests in `compiler/tests/test_newcpu.py`

See `compiler/assembler.md` for detailed instructions.

### Running Tests

```bash
cd compiler
source .venv/bin/activate
python -m unittest discover tests/
```

### Building Examples

```bash
# 65C02 example
python compiler/main.py examples/mcu65c02.s -o examples/mcu65c02.bin --cpu 65c02

# 6800 example
python compiler/main.py examples/mcu6800.s -o examples/mcu6800.bin --cpu 6800

# 8086 example
python compiler/main.py examples/hello_8086.s -o examples/hello_8086.bin --cpu 8086
```

## Command Line Options

```
usage: main.py [-h] [--cpu {65c02,6800,8086}] [--start-address START_ADDRESS]
               [--output OUTPUT] [--log-file LOG_FILE]
               source_file

Multi-CPU Assembler

positional arguments:
  source_file           Assembly source file to assemble

optional arguments:
  -h, --help            show this help message and exit
  --cpu {65c02,6800,8086}
                        Target CPU architecture
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

## Roadmap

- [ ] Add Z80 CPU support
- [ ] Implement macro system
- [ ] Add conditional assembly
- [ ] Support additional output formats
- [ ] IDE integration features
- [ ] Web-based interface

## Acknowledgments

- Built with [SLY](https://github.com/dabeaz/sly) for expression parsing
- Inspired by classic assemblers and modern compiler design
- Thanks to contributors and the open source community