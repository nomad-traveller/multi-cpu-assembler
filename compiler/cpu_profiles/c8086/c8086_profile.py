# c8086_profile.py - Intel 8086 CPU Profile Implementation
import re
from typing import Any, TYPE_CHECKING
from .opcodes_8086 import OPCODES_8086, AddressingMode, Register, SPECIAL_OPCODES
from .opcodes_8086 import MOD_MEMORY_NO_DISP, MOD_MEMORY_DISP8, MOD_MEMORY_DISP16, MOD_REGISTER
from .opcodes_8086 import REG_AL, REG_CL, REG_DL, REG_BL, REG_AH, REG_CH, REG_DH, REG_BH
from .opcodes_8086 import REG_AX, REG_CX, REG_DX, REG_BX, REG_SP, REG_BP, REG_SI, REG_DI
from .opcodes_8086 import EA_BX_SI, EA_BX_DI, EA_BP_SI, EA_BP_DI, EA_SI, EA_DI, EA_BP, EA_BX
from core.expression_evaluator import evaluate_expression
from core.diagnostics import Diagnostics
from .. import CPUProfile

if TYPE_CHECKING:
    from core.parser import Parser


class C8086Profile(CPUProfile):
    """The CPU Profile for the Intel 8086 processor."""

    def __init__(self, diagnostics: Diagnostics):
        self._opcodes = OPCODES_8086
        # 8086 doesn't have traditional branch mnemonics like 8-bit CPUs
        # JMP and CALL are handled as regular instructions
        self._branch_mnemonics = set()
        self._addressing_modes_enum = AddressingMode
        self.diagnostics = diagnostics

        # Register name mappings
        self._byte_registers = {
            'AL': REG_AL, 'CL': REG_CL, 'DL': REG_DL, 'BL': REG_BL,
            'AH': REG_AH, 'CH': REG_CH, 'DH': REG_DH, 'BH': REG_BH
        }
        self._word_registers = {
            'AX': REG_AX, 'CX': REG_CX, 'DX': REG_DX, 'BX': REG_BX,
            'SP': REG_SP, 'BP': REG_BP, 'SI': REG_SI, 'DI': REG_DI
        }

    @property
    def opcodes(self):
        return self._opcodes

    @property
    def branch_mnemonics(self):
        return self._branch_mnemonics

    @property
    def addressing_modes_enum(self):
        return self._addressing_modes_enum

    # 8086 addressing mode patterns - simplified for initial implementation
    _8086_MODE_PATTERNS = [
        # Registers (must come first)
        (re.compile(r'^(AL|CL|DL|BL|AH|CH|DH|BH)$', re.IGNORECASE), AddressingMode.REGISTER),
        (re.compile(r'^(AX|CX|DX|BX|SP|BP|SI|DI)$', re.IGNORECASE), AddressingMode.REGISTER),

        # Immediate values
        (re.compile(r'^#'), AddressingMode.IMMEDIATE),

        # Memory references - simplified patterns
        (re.compile(r'^\[.*\]$'), AddressingMode.MEMORY),
    ]

    def parse_addressing_mode(self, operand_str):
        """Parse 8086 addressing mode from operand string."""
        operand_str = operand_str.strip().upper()
        if not operand_str:
            return (AddressingMode.IMPLIED, None)

        for pattern, mode in self._8086_MODE_PATTERNS:
            if pattern.match(operand_str):
                if mode == AddressingMode.REGISTER:
                    # Extract register value
                    reg_name = operand_str
                    if reg_name in self._byte_registers:
                        return (mode, self._byte_registers[reg_name])
                    elif reg_name in self._word_registers:
                        return (mode, self._word_registers[reg_name])
                elif mode == AddressingMode.IMMEDIATE:
                    # Remove # prefix and parse value
                    value_str = operand_str[1:]
                    try:
                        if value_str.startswith('0X') or value_str.startswith('$'):
                            value = int(value_str.replace('$', ''), 16)
                        else:
                            value = int(value_str)
                        return (mode, value)
                    except ValueError:
                        return (mode, value_str)  # Symbol/label
                elif mode == AddressingMode.MEMORY:
                    # Simplified memory parsing - just return the bracketed content
                    mem_expr = operand_str[1:-1]  # Remove brackets
                    return (mode, mem_expr)

        # If no pattern matches, assume it's a symbol/label
        return (AddressingMode.IMMEDIATE, operand_str)

    def parse_directive(self, instruction, parser: 'Parser'):
        """Parses 8086 assembler directives."""
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
        """Parses an 8086 CPU instruction."""
        operand_str = instruction.operand_str
        mnemonic = instruction.mnemonic.upper()

        if not operand_str:
            instruction.mode = AddressingMode.IMPLIED
            return

        # Split operands (8086 can have 0, 1, or 2 operands)
        operands = [op.strip() for op in operand_str.split(',')]
        if len(operands) > 2:
            raise ValueError(f"Too many operands for {mnemonic}")

        # Parse first operand
        if len(operands) >= 1:
            mode1, value1 = self.parse_addressing_mode(operands[0])
            instruction.mode = mode1
            instruction.operand_value = parser.parse_operand_list(str(value1))[0] if value1 is not None else None

        # For now, we only handle single-operand instructions
        # Two-operand instructions would need more complex parsing

    def get_opcode_details(self, instruction, symbol_table):
        """Get opcode details for 8086 instruction."""
        mnemonic = instruction.mnemonic.upper()
        mode = instruction.mode

        if mnemonic not in self.opcodes:
            return None
        if mode not in self.opcodes[mnemonic]:
            return None

        return self.opcodes[mnemonic][mode]

    def _encode_modrm(self, mod, reg, rm):
        """Encode Mod-Reg-R/M byte."""
        return (mod << 6) | (reg << 3) | rm

    def _get_register_code(self, reg_value, is_word=True):
        """Get register code for Mod-Reg-R/M."""
        if is_word:
            return reg_value  # Already in correct format
        else:
            return reg_value  # Byte registers use same encoding

    def encode_instruction(self, instruction, symbol_table):
        """Encode 8086 instruction to machine code."""
        mnemonic = instruction.mnemonic.upper()
        mode = instruction.mode

        # Get opcode details
        details = self.get_opcode_details(instruction, symbol_table)
        if details is None:
            self.diagnostics.error(instruction.line_num, f"Invalid instruction: {mnemonic} {mode}")
            return False

        opcode, operand_size, requires_modrm, direction_bit = details

        try:
            machine_code = [opcode]

            # Handle different instruction types
            if mnemonic == "MOV" and mode == AddressingMode.REGISTER:
                # MOV reg, reg - requires Mod-Reg-R/M
                # For now, assume register-to-register move
                # This is simplified - real implementation would need operand parsing
                modrm = self._encode_modrm(MOD_REGISTER, REG_AX, REG_BX)  # Example: MOV AX, BX
                machine_code.append(modrm)

            elif mnemonic == "MOV" and mode == AddressingMode.IMMEDIATE:
                # MOV reg, imm
                if isinstance(instruction.operand_value, int):
                    reg_code = instruction.operand_value  # This should be the register code
                    imm_value = instruction.operand_value  # This should be the immediate value
                    # Simplified: assume MOV AL, imm8 or MOV AX, imm16
                    if imm_value <= 0xFF:
                        machine_code = [0xB0 + reg_code, imm_value]  # MOV reg8, imm8
                    else:
                        machine_code = [0xB8 + reg_code, imm_value & 0xFF, (imm_value >> 8) & 0xFF]  # MOV reg16, imm16

            elif mode == AddressingMode.IMPLIED:
                # No additional bytes needed
                pass

            elif mnemonic == "ADD" and mode == AddressingMode.IMMEDIATE:
                # ADD reg/mem, imm
                # Simplified implementation
                if isinstance(instruction.operand_value, int) and instruction.operand_value <= 0xFF:
                    machine_code = [0x80, 0xC0, instruction.operand_value]  # ADD AL, imm8 (example)

            elif mnemonic == "JMP" and mode == AddressingMode.IMMEDIATE:
                # JMP rel16
                val = instruction.operand_value
                if hasattr(val, 'value'):  # Number object
                    val = val.value
                elif hasattr(val, 'name'):  # Symbol object
                    symbol_name = val.name
                    val = symbol_table.resolve(symbol_name)
                    if val is None:
                        raise ValueError(f"Undefined symbol '{symbol_name}'")

                if isinstance(val, int):
                    offset = val - (instruction.address + 3)  # JMP is 3 bytes
                    if -32768 <= offset <= 32767:
                        machine_code = [0xE9, offset & 0xFF, (offset >> 8) & 0xFF]
                    else:
                        raise ValueError(f"JMP offset out of range: {offset}")

            elif mnemonic == "INT" and mode == AddressingMode.IMMEDIATE:
                # INT imm8
                val = instruction.operand_value
                if hasattr(val, 'value'):  # Number object
                    val = val.value
                if isinstance(val, int) and 0 <= val <= 0xFF:
                    machine_code.append(val)
                else:
                    raise ValueError("INT requires 8-bit immediate value")

            # Store the machine code
            instruction.machine_code = machine_code
            return True

        except ValueError as e:
            self.diagnostics.error(instruction.line_num, str(e))
            return False

    def validate_instruction(self, instruction) -> bool:
        """
        Validates 8086 instructions for common assembly mistakes.
        """
        mnemonic = instruction.mnemonic.upper() if instruction.mnemonic else ""
        mode = instruction.mode
        operand_value = instruction.operand_value

        # Check for segment register usage in invalid contexts
        segment_regs = ["CS", "DS", "ES", "SS"]
        if mnemonic in ("MOV", "ADD", "SUB", "CMP") and operand_value in segment_regs:
            if mode == AddressingMode.IMMEDIATE:
                self.diagnostics.error(instruction.line_num,
                    f"Cannot use segment register '{operand_value}' with immediate value in '{mnemonic}' instruction.")
                return False

        # Check for invalid register combinations
        if mnemonic == "MOV" and mode == AddressingMode.REGISTER:
            # This would need more complex validation for register-to-register moves
            # For now, just check for obvious mistakes
            pass

        # Check for potential optimization opportunities
        if mode == AddressingMode.IMMEDIATE and isinstance(operand_value, int):
            if operand_value == 0 and mnemonic in ("ADD", "SUB", "OR", "XOR"):
                self.diagnostics.warning(instruction.line_num,
                    f"Using '{mnemonic}' with immediate value 0. Consider using shorter 'MOV' instruction or removing the operation.")

        # Check for invalid operand sizes
        if mnemonic in ("MOV", "ADD", "SUB") and mode == AddressingMode.IMMEDIATE:
            if isinstance(operand_value, int) and operand_value > 0xFFFF:
                self.diagnostics.error(instruction.line_num,
                    f"Immediate value ${operand_value:08X} is too large for 16-bit instruction '{mnemonic}'.")
                return False

        return True