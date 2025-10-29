assembler.md
Assembler System Architecture and Extensibility
This document outlines the modular architecture of the assembler and provides a step-by-step guide on how to integrate support for new CPU architectures.

1. System Overview
The assembler is designed with a strong emphasis on modularity, separation of concerns, and dependency injection. This approach ensures that the core assembly logic is CPU-agnostic, while CPU-specific details are encapsulated within dedicated "profile" modules.

High-Level Data Flow:

main.py: Parses command-line arguments, sets up logging, and orchestrates the entire assembly process. It acts as the "Composition Root," wiring all components together.
parser.py: Reads the source file line by line, performs lexical and syntactic analysis, and converts each line into an Instruction object. It delegates expression parsing to expression_parser.py.
assembler.py: Executes the two-pass assembly process.
Pass 1: Calculates instruction addresses and populates the SymbolTable.
Pass 2: Generates machine code bytes for each instruction. It delegates CPU-specific tasks (like determining instruction size or encoding) to the active CPUProfile.
emitter.py: Handles output, including printing assembly listings and writing the final binary file.
diagnostics.py: Centralized system for reporting errors, warnings, and informational messages to both the console and a log file.
2. Key Components and Responsibilities
main.py
Role: Application entry point, command-line argument parsing, logging setup, and orchestrator.
Key Functions: parse_args(), setup_logging(), main().
Extensibility: Registers new CPUProfile implementations in the SUPPORTED_CPUS dictionary.
parser.py
Role: Converts raw assembly source lines into structured Instruction objects.
Key Classes:
Parser: Main parser class. Uses _LineParser for initial line breakdown and expression_parser for operand evaluation.
_LineParser: Internal helper for breaking a raw line into label, mnemonic, and operand string. Handles comments and EQU directive syntax.
Key Methods: parse_line(), parse_operand_list(), parse_source_file().
Dependencies: CPUProfile, Diagnostics, ExpressionLexer, ExpressionParser.
assembler.py
Role: Implements the two-pass assembly algorithm.
Key Methods: assemble(), _first_pass(), _second_pass().
Dependencies: CPUProfile, SymbolTable, Diagnostics, Program, expression_evaluator.
cpu_profiles.py
Role: Defines the abstract interface for CPU-specific behavior and provides concrete implementations for supported CPUs.
Key Classes:
CPUProfile (Abstract Base Class): Defines methods like parse_addressing_mode(), parse_directive(), parse_instruction(), get_opcode_details(), encode_instruction().
C6502Profile, C6800Profile: Concrete implementations for the 65C02 and 6800 CPUs.
Extensibility: This is the primary extension point for new CPU architectures.
opcodes_65C02.py / opcodes_6800.py (and similar)
Role: Stores CPU-specific opcode data.
Key Data Structure: OPCODES dictionary, mapping mnemonics and addressing modes to opcode bytes, operand sizes, cycle info, and flags affected.
Key Enums: AddressingMode (or C6800AddressingMode), defining the addressing modes specific to that CPU.
expression_parser.py
Role: Lexical analysis and parsing of expression strings into an Abstract Syntax Tree (AST).
Key Classes:
BinOp, UnaryOp, Number, Symbol: AST node definitions.
ExpressionLexer (Sly-based): Tokenizes expression strings.
ExpressionParser (Sly-based): Parses tokens into an AST, handling operator precedence and parentheses.
Dependencies: sly library.
expression_evaluator.py
Role: Evaluates an expression AST into a final integer value.
Key Function: evaluate_expression().
Dependencies: AST node classes from expression_parser.py.
symbol_table.py
Role: Manages the mapping of labels to their memory addresses.
Key Class: SymbolTable.
Dependencies: Diagnostics.
instruction.py
Role: Represents a single parsed line of assembly code, holding all its attributes (label, mnemonic, operand, address, machine code, etc.).
Key Class: Instruction.
Dependencies: Diagnostics.
diagnostics.py
Role: Centralized error, warning, and informational message reporting. Integrates with Python's logging module.
Key Class: Diagnostics.
Dependencies: logging.
emitter.py
Role: Outputs the assembly listing and writes the final binary file.
Key Class: Emitter.
Dependencies: Diagnostics.
3. Steps to Integrate Other CPU Architectures
To add support for a new CPU (e.g., the Z80), you would follow these steps:

Step 1: Create a New Opcode Data Module (opcodes_Z80.py)
Create a new Python file, for example, /mnt/mcu6502/opcodes_Z80.py.

Define Addressing Modes Enum: Create an Enum for the Z80's specific addressing modes.
# /mnt/mcu6502/opcodes_Z80.py
from enum import Enum, auto

class Z80AddressingMode(Enum):
    IMPLIED = auto()
    IMMEDIATE = auto()
    EXTENDED = auto() # 16-bit address
    INDEXED_IX = auto() # (IX+d)
    INDEXED_IY = auto() # (IY+d)
    RELATIVE = auto()
    # ... add all other Z80 addressing modes

2.  Populate the OPCODES Dictionary: Define the OPCODES dictionary for the Z80. The structure should be consistent: OPCODES[mnemonic][addressing_mode] = [opcode_byte(s), operand_size_in_bytes, cycle_info_dict, flags_affected_string]

opcode_byte(s): A list of bytes for multi-byte opcodes (e.g., [0xDD, 0x21] for LD IX,nn).
operand_size_in_bytes: The number of bytes the operand takes (0, 1, or 2).
cycle_info_dict: (Optional) Dictionary for cycle counts.
flags_affected_string: (Optional) String indicating affected flags.  

# /mnt/mcu6502/opcodes_Z80.py
# ... (Z80AddressingMode definition)

OPCODES_Z80 = {
    "NOP": {
        Z80AddressingMode.IMPLIED: [0x00, 0, {}, ""],
    },
    "LD": {
        Z80AddressingMode.IMMEDIATE: [0x3E, 1, {}, "NZHVPC"], # LD A,n
        Z80AddressingMode.EXTENDED: [0x21, 2, {}, "NZHVPC"], # LD HL,nn
        # ... many more LD variations
    },
    "JP": {
        Z80AddressingMode.EXTENDED: [0xC3, 2, {}, ""], # JP nn
    },
    "JR": {
        Z80AddressingMode.RELATIVE: [0x18, 1, {}, ""], # JR e
    },
    # ... add all other Z80 opcodes
}

Step 2: Implement the Z80Profile in cpu_profiles.py
Open /mnt/mcu6502/cpu_profiles.py and add a new class for the Z80.

Import necessary modules:

# /mnt/mcu6502/cpu_profiles.py
# ... existing imports
from opcodes_Z80 import OPCODES_Z80, Z80AddressingMode
# ...

2. Create the Z80Profile class: This class must inherit from CPUProfile and implement all its abstract methods.

# /mnt/mcu6502/cpu_profiles.py
# ... (existing CPUProfile, C6502Profile, C6800Profile classes)

class Z80Profile(CPUProfile):
    """The CPU Profile for the Zilog Z80 processor."""
    def __init__(self, diagnostics: Diagnostics):
        self._opcodes = OPCODES_Z80
        self._branch_mnemonics = {"JR", "JP"} # Z80 has both relative (JR) and absolute (JP) branches
        self._addressing_modes_enum = Z80AddressingMode
        self.diagnostics = diagnostics

        # Define regex patterns for Z80 addressing modes
        # This is crucial for parse_addressing_mode
        self._Z80_MODE_PATTERNS = [
            (re.compile(r"^#"), Z80AddressingMode.IMMEDIATE, None), # Immediate (e.g., LD A,n)
            (re.compile(r"^\(\$[0-9A-F]+\)$"), Z80AddressingMode.EXTENDED, 1), # (nn)
            (re.compile(r"^\$[0-9A-F]+$"), Z80AddressingMode.EXTENDED, 0), # nn (absolute address)
            (re.compile(r"^[A-Z_][A-Z0-9_]*$"), Z80AddressingMode.EXTENDED, 0), # Label (default to extended)
            # ... add patterns for (IX+d), (IY+d), etc.
        ]

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
        """Parses Z80 addressing modes from an operand string."""
        operand_str = operand_str.strip().upper()
        if not operand_str:
            return (Z80AddressingMode.IMPLIED, None)

        for pattern, mode, group_idx in self._Z80_MODE_PATTERNS:
            match = pattern.match(operand_str)
            if match:
                value = None
                if group_idx is not None:
                    val_str = match.group(group_idx) if group_idx > 0 else operand_str
                    # Strip syntax characters for expression evaluation
                    val_str = re.sub(r'[#()\$]', '', val_str)
                    value = val_str # Pass as string for expression parser
                return (mode, value)
        return (None, None) # No mode matched

    def parse_directive(self, instruction, parser: 'Parser'):
        """Parses Z80 assembler directives."""
        mnemonic = instruction.directive
        operand_str = instruction.operand_str

        if mnemonic == ".ORG":
            if not operand_str:
                raise ValueError("Missing operand for .ORG")
            instruction.operand_value = parser.parse_operand_list(operand_str)[0]
        elif mnemonic == ".BYTE":
            instruction.operand_value = parser.parse_operand_list(operand_str)
            instruction.size = len(instruction.operand_value)
        elif mnemonic == ".WORD":
            instruction.operand_value = parser.parse_operand_list(operand_str)
            instruction.size = len(instruction.operand_value) * 2
        elif mnemonic == "EQU":
            instruction.operand_value = parser.parse_operand_list(operand_str)[0]
            instruction.size = 0
        # Add any Z80-specific directives here
        else:
            raise ValueError(f"Unknown directive: {mnemonic}")

    def parse_instruction(self, instruction, parser: 'Parser'):
        """Parses a Z80 CPU instruction."""
        operand_str = instruction.operand_str
        expression_str = operand_str

        # Strip addressing mode prefixes before passing to expression parser
        if operand_str and operand_str.startswith('#'): # Immediate
            expression_str = operand_str[1:]
        elif operand_str and operand_str.startswith('(') and operand_str.endswith(')'): # Indirect
            expression_str = operand_str[1:-1]

        mode, _ = self.parse_addressing_mode(operand_str or "")
        instruction.mode = mode
        instruction.operand_value = parser.parse_operand_list(expression_str)[0] if expression_str else None

        # Post-parse fix-ups for Z80 (e.g., specific branch types, register parsing)
        # For Z80, you might need to parse registers (A, B, C, D, E, H, L, IX, IY, SP, PC)
        # This would involve more complex logic than just stripping prefixes.

    def get_opcode_details(self, instruction, symbol_table):
        """Retrieves opcode details for a Z80 instruction."""
        mnemonic = instruction.mnemonic
        mode = instruction.mode
        # Z80 often has multiple opcodes for the same mnemonic based on registers/operands.
        # This method would need to be more sophisticated for Z80.
        # For simplicity, this example assumes direct lookup.
        if mnemonic not in self.opcodes:
            return None
        if mode not in self.opcodes[mnemonic]:
            return None
        return self.opcodes[mnemonic][mode]

    def encode_instruction(self, instruction, symbol_table):
        """Encodes a Z80 instruction into machine code bytes."""
        val = evaluate_expression(instruction.operand_value, symbol_table, instruction.line_num)
        details = self.get_opcode_details(instruction, symbol_table)

        if details is None:
            raise ValueError(f"No opcode details found for {instruction.mnemonic} {instruction.mode.name}")

        opcode_bytes, operand_size, _, _ = details

        machine_code = list(opcode_bytes) # Ensure it's a mutable list

        try:
            if operand_size == 0:
                pass # Opcode only
            elif operand_size == 1:
                if instruction.mode == Z80AddressingMode.RELATIVE:
                    # Z80 relative branches are signed 8-bit offsets
                    offset = val - (instruction.address + len(opcode_bytes) + 1) # +1 for the offset byte itself
                    if not -128 <= offset <= 127:
                        raise ValueError(f"Branch offset out of range: {offset}")
                    machine_code.append(offset & 0xFF)
                else:
                    if not 0 <= val < 256:
                        raise ValueError(f"Value out of range for 1-byte operand: {val}")
                    machine_code.append(val & 0xFF)
            elif operand_size == 2:
                if not 0 <= val < 65536:
                    raise ValueError(f"Value out of range for 2-byte operand: {val}")
                # Z80 is little-endian for 16-bit operands (nn)
                machine_code.extend([val & 0xFF, (val >> 8) & 0xFF])
            else:
                raise ValueError(f"Unsupported operand size: {operand_size} for {instruction.mnemonic} {instruction.mode.name}")

        except ValueError as e:
            self.diagnostics.error(instruction.line_num, str(e))
            return False

        instruction.machine_code = machine_code
        return True

Step 3: Register the New Profile in main.py
Open /mnt/mcu6502/main.py and update the SUPPORTED_CPUS dictionary.

Import the new profile:

# /mnt/mcu6502/main.py
# ... existing imports
from cpu_profiles import C6502Profile, C6800Profile, Z80Profile # Add Z80Profile
# ...

# /mnt/mcu6502/main.py
SUPPORTED_CPUS = {
    "65c02": C6502Profile,
    "6800": C6800Profile,
    "z80": Z80Profile, # Add the new Z80 profile
}
Step 4: Test Your New CPU Profile
Create a Sample Assembly File: Create a file like /mnt/mcu6502/z80_test.s:

; Z80 Test Program
        ORG $8000
START:  LD A,#
        LD B,#A
        ADD A,B
        JR LOOP
LOOP:   NOP
        JP START


Step 4: Test Your New CPU Profile
Create a Sample Assembly File: Create a file like /mnt/mcu6502/z80_test.s:

; Z80 Test Program
        ORG $8000
START:  LD A,#
        LD B,#A
        ADD A,B
        JR LOOP
LOOP:   NOP
        JP START

Run the Assembler

python main.py --cpu z80 z80_test.s -o z80_test.bin

# /mnt/mcu6502/main.py
# ... existing imports
from cpu_profiles import C6502Profile, C6800Profile, Z80Profile # Add Z80Profile
# ...


