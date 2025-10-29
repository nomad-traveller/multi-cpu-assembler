# c6502_profile.py - 65C02 CPU Profile Implementation
import re
from typing import Any, TYPE_CHECKING
from cpu_profiles.c6502.opcodes_65C02 import OPCODES, AddressingMode
from core.expression_evaluator import evaluate_expression
from core.diagnostics import Diagnostics
from cpu_profile_base import CPUProfile

if TYPE_CHECKING:
    from parser import Parser


class C6502Profile(CPUProfile):
    def __init__(self, diagnostics: Diagnostics):
        self._opcodes = OPCODES
        self._branch_mnemonics = {
            "BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC", "BVS", "BRA"  # 65C02 includes BRA
        }
        self._addressing_modes_enum = AddressingMode
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

    # A data-driven approach for parsing 6502 addressing modes.
    # Patterns are ordered from most specific to least specific to ensure correct matching.
    # Each tuple: (regex_pattern, AddressingMode, group_index_for_value)
    # group_index_for_value: None for implied/accumulator, 1+ for specific group.
    _6502_MODE_PATTERNS = [
        (re.compile(r"^[aA]$"), AddressingMode.ACCUMULATOR, None),
        (re.compile(r"^#(\$?[0-9A-F]+|[A-Z_][A-Z0-9_]*)$", re.IGNORECASE), AddressingMode.IMMEDIATE, 1),
        (re.compile(r"^\((\$?[0-9A-F]{1,2}),X\)$", re.IGNORECASE), AddressingMode.INDIRECT_X, 1),
        (re.compile(r"^\((\$?[0-9A-F]{1,2})\),Y$", re.IGNORECASE), AddressingMode.INDIRECT_Y, 1),
        (re.compile(r"^\((\$?[0-9A-F]{3,4})\)$", re.IGNORECASE), AddressingMode.INDIRECT, 1), # Absolute Indirect (JMP ($NNNN))
        (re.compile(r"^\((\$?[0-9A-F]{1,2})\)$", re.IGNORECASE), AddressingMode.ZEROPAGE_INDIRECT, 1), # Zero Page Indirect (65C02)
        (re.compile(r"^(\$?[0-9A-F]{3,4}),X$", re.IGNORECASE), AddressingMode.ABSOLUTE_X, 1),
        (re.compile(r"^(\$?[0-9A-F]{3,4}),Y$", re.IGNORECASE), AddressingMode.ABSOLUTE_Y, 1),
        (re.compile(r"^(\$?[0-9A-F]{1,2}),X$", re.IGNORECASE), AddressingMode.ZEROPAGE_X, 1),
        (re.compile(r"^(\$?[0-9A-F]{1,2}),Y$", re.IGNORECASE), AddressingMode.ZEROPAGE_Y, 1),
        (re.compile(r"^(\$?[0-9A-F]{3,4})$", re.IGNORECASE), AddressingMode.ABSOLUTE, 1), # Absolute
        (re.compile(r"^(\$?[0-9A-F]{1,2})$", re.IGNORECASE), AddressingMode.ZEROPAGE, 1), # Zero Page
        (re.compile(r"^([A-Z_][A-Z0-9_]*)$", re.IGNORECASE), AddressingMode.ABSOLUTE, 1), # Label (default to absolute, will be fixed to relative for branches)
        (re.compile(r"^([0-9]+)$"), AddressingMode.ABSOLUTE, 1), # Decimal (default to absolute)
    ]

    def parse_addressing_mode(self, operand_str):
        operand_str = operand_str.strip().upper()
        if not operand_str:
            return (AddressingMode.IMPLIED, None)

        for pattern, mode, group_idx in self._6502_MODE_PATTERNS:
            match = pattern.match(operand_str)
            if match:
                value = None
                if group_idx is not None:
                    val_str = match.group(group_idx)
                    if val_str.startswith('$'):
                        value = int(val_str[1:], 16)
                    elif val_str.isdigit():
                        value = int(val_str)
                    else: # It's a label
                        value = val_str
                return (mode, value)

        return (None, None) # Indicate that no mode was matched

    def parse_directive(self, instruction, parser: 'Parser'):
        """Parses 65C02 assembler directives."""
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
        else:
            raise ValueError(f"Unknown directive: {mnemonic}")

    def parse_instruction(self, instruction, parser: 'Parser'):
        """Parses a 65C02 CPU instruction."""
        operand_str = instruction.operand_str
        if not operand_str:
            instruction.mode = AddressingMode.IMPLIED
            return

        expression_str = operand_str
        if operand_str.startswith('#'):
            expression_str = operand_str[1:]

        mode, _ = self.parse_addressing_mode(operand_str) # We only need the mode from regex
        if mode:
            instruction.mode = mode
            instruction.operand_value = parser.parse_operand_list(expression_str)[0]
        else:
            # This should not happen if parse_addressing_mode is comprehensive
            raise ValueError(f"Could not determine addressing mode for operand: {operand_str}")

        # Post-parse fix-ups for 6502
        # If the mnemonic is a branch, force the mode to RELATIVE.
        if instruction.mnemonic in self.branch_mnemonics:
            # The value is a label string, which is correct for relative mode.
            instruction.mode = AddressingMode.RELATIVE

        # If an absolute mode was detected for a small value, it's actually zeropage.
        # This is a bit of a simplification; a more robust parser might handle this differently.
        if instruction.mode == AddressingMode.ABSOLUTE and isinstance(instruction.operand_value, int) and instruction.operand_value <= 0xFF:
            instruction.mode = AddressingMode.ZEROPAGE
        elif instruction.mode == AddressingMode.ABSOLUTE_X and isinstance(instruction.operand_value, int) and instruction.operand_value <= 0xFF:
            instruction.mode = AddressingMode.ZEROPAGE_X
        elif instruction.mode == AddressingMode.ABSOLUTE_Y and isinstance(instruction.operand_value, int) and instruction.operand_value <= 0xFF:
            instruction.mode = AddressingMode.ZEROPAGE_Y

    def get_opcode_details(self, instruction, symbol_table):
        mnemonic = instruction.mnemonic
        mode = instruction.mode
        if mnemonic not in self.opcodes:
            return None
        if mode not in self.opcodes[mnemonic]:
            return None
        return self.opcodes[mnemonic][mode]

    def encode_instruction(self, instruction, symbol_table):
        mnemonic = instruction.mnemonic
        mode = instruction.mode

        details = self.opcodes[mnemonic][mode]
        opcode, operand_size, _, _ = details

        try:
            # Call the static Assembler method for expression evaluation
            val = evaluate_expression(instruction.operand_value, symbol_table, instruction.line_num)
            if operand_size == 0: # Implied or Accumulator modes have 0 operand bytes
                instruction.machine_code = [opcode]
            elif operand_size > 0: # Process operand if required
                if val is None:
                    raise ValueError(f"Mnemonic '{mnemonic}' requires an operand but none was provided.")
                if operand_size == 1:
                    if mode == AddressingMode.RELATIVE:
                        offset = val - (instruction.address + 2)
                        if not -128 <= offset <= 127:
                            raise ValueError(f"Branch offset out of range: {offset}")
                        instruction.machine_code = [opcode, offset & 0xFF]
                    else:
                        if not 0 <= val < 256:
                            raise ValueError(f"Value out of range for 1-byte operand: {val}")
                        instruction.machine_code = [opcode, val & 0xFF]
                elif operand_size == 2:
                    if not 0 <= val < 65536:
                        raise ValueError(f"Value out of range for 2-byte operand: {val}")
                    instruction.machine_code = [opcode, val & 0xFF, (val >> 8) & 0xFF]
                else:
                    raise ValueError(f"Unsupported operand size: {operand_size}")
            # No else needed, as operand_size == 0 is handled.
        except ValueError as e:
            self.diagnostics.error(instruction.line_num, str(e))
            return False
        return True

    def validate_instruction(self, instruction) -> bool:
        """
        Validates 6502 instructions for common assembly mistakes.
        """
        mnemonic = instruction.mnemonic.upper() if instruction.mnemonic else ""
        mode = instruction.mode
        operand_value = instruction.operand_value

        # Check for instructions that don't support certain addressing modes
        if mnemonic in ("ASL", "LSR", "ROL", "ROR") and mode == AddressingMode.IMMEDIATE:
            self.diagnostics.error(instruction.line_num,
                f"Instruction '{mnemonic}' does not support immediate addressing mode. Use accumulator mode (A) instead.")
            return False

        # Check for branch instructions with absolute addressing (should be relative)
        if mnemonic in self.branch_mnemonics and mode in (AddressingMode.ABSOLUTE, AddressingMode.ZEROPAGE):
            self.diagnostics.error(instruction.line_num,
                f"Branch instruction '{mnemonic}' cannot use absolute addressing. Branches are always relative.")
            return False

        # Check for invalid register usage
        if mnemonic in ("LDX", "STX", "TAX", "TXA", "INX", "DEX") and operand_value == "Y":
            self.diagnostics.warning(instruction.line_num,
                f"Instruction '{mnemonic}' uses X register, but operand suggests Y register usage. Did you mean LDY/STY/TAY/TYA/INY/DEY?")

        if mnemonic in ("LDY", "STY", "TAY", "TYA", "INY", "DEY") and operand_value == "X":
            self.diagnostics.warning(instruction.line_num,
                f"Instruction '{mnemonic}' uses Y register, but operand suggests X register usage. Did you mean LDX/STX/TAX/TXA/INX/DEX?")

        # Check for potential optimization opportunities
        if mode == AddressingMode.ABSOLUTE and isinstance(operand_value, int) and operand_value <= 0xFF:
            if mnemonic in ("LDA", "LDX", "LDY", "STA", "STX", "STY", "ADC", "SBC", "CMP", "AND", "ORA", "EOR"):
                self.diagnostics.warning(instruction.line_num,
                    f"Using absolute addressing for zero-page value ${operand_value:02X}. Consider using zero-page addressing for better performance.")

        # Check for common immediate value mistakes
        if mode == AddressingMode.IMMEDIATE and isinstance(operand_value, int):
            if operand_value > 0xFF:
                self.diagnostics.error(instruction.line_num,
                    f"Immediate value ${operand_value:04X} is too large for 8-bit immediate. Maximum is $FF.")
                return False

        # Check for invalid operand combinations
        if mnemonic == "JMP" and mode == AddressingMode.INDIRECT and isinstance(operand_value, int) and (operand_value & 0xFF) == 0xFF:
            self.diagnostics.warning(instruction.line_num,
                f"JMP (${operand_value:04X}) uses page boundary crossing which may be slower on some 6502 variants.")

        return True