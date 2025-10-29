# c6800_profile.py - 6800 CPU Profile Implementation
import re
from typing import Any, TYPE_CHECKING
from .opcodes_6800 import OPCODES_6800, C6800AddressingMode
from core.expression_evaluator import evaluate_expression
from core.diagnostics import Diagnostics
from .. import CPUProfile

if TYPE_CHECKING:
    from core.parser import Parser


class C6800Profile(CPUProfile):
    """The CPU Profile for the Motorola 6800 processor."""
    def __init__(self, diagnostics: Diagnostics):
        self._opcodes = OPCODES_6800
        # 6800 branch mnemonics
        self._branch_mnemonics = {"BCC", "BCS", "BEQ", "BGE", "BGT", "BHI", "BLE", "BLS", "BLT", "BMI", "BNE", "BPL", "BRA", "BSR", "BVC", "BVS"} # BSR is also relative
        self._addressing_modes_enum = C6800AddressingMode
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

    # Data-driven patterns for parsing 6800 addressing modes.
    # Order matters: more specific patterns first
    _6800_MODE_PATTERNS = [
        (re.compile(r"^[aA]$"), C6800AddressingMode.ACCUMULATOR_A, None),
        (re.compile(r"^[bB]$"), C6800AddressingMode.ACCUMULATOR_B, None),
        (re.compile(r"^#"), C6800AddressingMode.IMMEDIATE, None), # Immediate must be checked before others
        (re.compile(r",X$"), C6800AddressingMode.INDEXED, None),
        (re.compile(r"^\$[0-9A-F]{1,2}$"), C6800AddressingMode.DIRECT, 0), # Direct (1-2 hex digits)
        (re.compile(r"^[A-Z_][A-Z0-9_]*$", re.IGNORECASE), C6800AddressingMode.EXTENDED, 0), # Label
        (re.compile(r"^\$[0-9A-F]{3,4}$"), C6800AddressingMode.EXTENDED, 0), # Extended hex (3-4 digits)
        (re.compile(r"^[0-9]{1,3}$"), C6800AddressingMode.DIRECT, 0), # Direct decimal (1-3 digits)
        (re.compile(r"^[0-9]{4,5}$"), C6800AddressingMode.EXTENDED, 0), # Extended decimal (4-5 digits)
    ]

    def parse_addressing_mode(self, operand_str):
        operand_str = operand_str.strip().upper()
        if not operand_str:
            return (C6800AddressingMode.INHERENT, None)

        for pattern, mode, group_idx in self._6800_MODE_PATTERNS:
            match = pattern.search(operand_str)
            if match:
                if mode in (C6800AddressingMode.ACCUMULATOR_A, C6800AddressingMode.ACCUMULATOR_B):
                    return (mode, None)
                val_str = match.group(group_idx) if group_idx is not None else operand_str
                # Remove syntax characters
                val_str = re.sub(r'[#(),X]', '', val_str)
                # Handle hex values
                if val_str.startswith('$'):
                    val_str = val_str[1:]
                    try:
                        value = int(val_str, 16)
                    except ValueError:
                        value = val_str
                else:
                    try:
                        value = int(val_str)
                    except ValueError:
                        # It's a label
                        value = val_str.strip()
                return (mode, value)

        raise ValueError(f"Invalid 6800 operand: {operand_str}")

    def parse_directive(self, instruction, parser: 'Parser'):
        # 6800 uses the same common directives as 6502, plus EQU
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
        elif mnemonic == "EQU": # Handle EQU
            instruction.operand_value = parser.parse_operand_list(operand_str)[0]
            instruction.directive = mnemonic # Ensure directive is set
            instruction.size = 0 # EQU does not take up space
        else:
            raise ValueError(f"Unknown directive: {mnemonic}")

    def parse_instruction(self, instruction, parser: 'Parser'):
        operand_str = instruction.operand_str
        expression_str = operand_str
        if operand_str and operand_str.startswith('#'):
            expression_str = operand_str[1:]

        mode, _ = self.parse_addressing_mode(operand_str or "")
        instruction.mode = mode
        instruction.operand_value = parser.parse_operand_list(expression_str)[0] if expression_str else None
        # Post-parse fix-ups for 6800
        if instruction.mnemonic in self.branch_mnemonics and instruction.mode in (C6800AddressingMode.DIRECT, C6800AddressingMode.EXTENDED):
            instruction.mode = C6800AddressingMode.RELATIVE

    def get_opcode_details(self, instruction, symbol_table):
        mnemonic = instruction.mnemonic
        mode = instruction.mode
        if mnemonic not in self.opcodes:
            return None
        if mode not in self.opcodes[mnemonic]: # Check if the exact mode exists
            # 6800 has some instructions that can be either DIRECT or EXTENDED based on value.
            # If EXTENDED fails, try DIRECT.
            if mode == C6800AddressingMode.EXTENDED and C6800AddressingMode.DIRECT in self.opcodes[mnemonic]:
                instruction.mode = C6800AddressingMode.DIRECT
                return self.opcodes[mnemonic][instruction.mode] # Return with the new mode
            return None
        return self.opcodes[mnemonic][mode]

    def encode_instruction(self, instruction, symbol_table):
        # This is very similar to the 6502 version, but uses 6800 modes.
        details = self.get_opcode_details(instruction, symbol_table)
        if details is None:
            return False
        opcode, operand_size, _, _ = details

        try:
            val = evaluate_expression(instruction.operand_value, symbol_table, instruction.line_num)
            if operand_size == 0: # Inherent modes have 0 operand bytes
                instruction.machine_code = [opcode]
            elif operand_size > 0: # Process operand if required
                if val is None:
                    raise ValueError(f"Mnemonic '{instruction.mnemonic}' requires an operand but none was provided.")
                if operand_size == 1:
                    if instruction.mode == C6800AddressingMode.RELATIVE:
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
                    instruction.machine_code = [opcode, (val >> 8) & 0xFF, val & 0xFF] # Big-endian for 6800
                else:
                    raise ValueError(f"Unsupported operand size: {operand_size} for {instruction.mnemonic} {instruction.mode.name}")
            # No else needed, as operand_size == 0 is handled.
        except ValueError as e:
            self.diagnostics.error(instruction.line_num, str(e))
            return False
        return True

    def validate_instruction(self, instruction) -> bool:
        """
        Validates 6800 instructions for common assembly mistakes.
        """
        mnemonic = instruction.mnemonic.upper() if instruction.mnemonic else ""
        mode = instruction.mode
        operand_value = instruction.operand_value

        # Check for instructions that require specific addressing modes
        if mnemonic in ("ABA", "CBA", "SBA") and mode != C6800AddressingMode.INHERENT:
            self.diagnostics.error(instruction.line_num,
                f"Instruction '{mnemonic}' must use inherent addressing (no operands).")
            return False

        # Check for branch instructions with invalid addressing modes
        if mnemonic in self.branch_mnemonics and mode not in (C6800AddressingMode.RELATIVE, C6800AddressingMode.DIRECT, C6800AddressingMode.EXTENDED):
            self.diagnostics.error(instruction.line_num,
                f"Branch instruction '{mnemonic}' requires relative, direct, or extended addressing.")
            return False

        # Check for invalid register usage
        if mnemonic in ("TAP", "TPA", "TSX", "TXS", "RTS", "RTI") and mode != C6800AddressingMode.INHERENT:
            self.diagnostics.warning(instruction.line_num,
                f"Instruction '{mnemonic}' typically uses inherent addressing. Operands may be ignored.")

        # Check for potential optimization opportunities
        if mode == C6800AddressingMode.EXTENDED and isinstance(operand_value, int) and operand_value <= 0xFF:
            self.diagnostics.warning(instruction.line_num,
                f"Using extended addressing for direct-page value ${operand_value:02X}. Consider using direct addressing for better performance.")

        # Check for invalid immediate values
        if mode == C6800AddressingMode.IMMEDIATE and isinstance(operand_value, int):
            if operand_value > 0xFF and mnemonic not in ("LDX", "STX", "CPX", "LDS", "STS", "CPS"):
                self.diagnostics.error(instruction.line_num,
                    f"Immediate value ${operand_value:04X} is too large for 8-bit immediate in instruction '{mnemonic}'.")
                return False

        return True