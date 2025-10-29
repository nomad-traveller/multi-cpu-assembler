# opcodes_8086.py
# This module contains opcode data for the Intel 8086 processor.
# The 8086 uses a complex Mod-Reg-R/M encoding scheme for instructions.

from enum import Enum, auto

class AddressingMode(Enum):
    """8086 addressing modes."""
    IMPLIED = auto()           # No operands (NOP, RET, etc.)
    REGISTER = auto()          # Register operand
    IMMEDIATE = auto()         # Immediate value
    MEMORY = auto()            # Memory operand (various forms)
    REGISTER_INDIRECT = auto() # [reg]
    REGISTER_DISP8 = auto()    # [reg + disp8]
    REGISTER_DISP16 = auto()   # [reg + disp16]
    BP_DISP8 = auto()          # [BP + disp8] (special case)
    BP_DISP16 = auto()         # [BP + disp16] (special case)
    DIRECT = auto()            # [disp16] - direct memory address

class Register(Enum):
    """8086 registers."""
    AL = 0b000
    CL = 0b001
    DL = 0b010
    BL = 0b011
    AH = 0b100
    CH = 0b101
    DH = 0b110
    BH = 0b111

    AX = 0b000
    CX = 0b001
    DX = 0b010
    BX = 0b011
    SP = 0b100
    BP = 0b101
    SI = 0b110
    DI = 0b111

# 8086 opcodes - subset of common instructions
# Format: [base_opcode, operand_size, requires_modrm, direction_bit]
OPCODES_8086 = {
    # Data Movement
    "MOV": {
        AddressingMode.REGISTER: [0x88, 0, True, None],  # MOV reg, reg/mem
        AddressingMode.IMMEDIATE: [0xB0, 0, False, None], # MOV reg, imm (byte)
        AddressingMode.MEMORY: [0xA0, 0, False, None],    # MOV AL/AX, [mem]
    },

    # Arithmetic
    "ADD": {
        AddressingMode.REGISTER: [0x00, 0, True, None],   # ADD reg/mem, reg
        AddressingMode.IMMEDIATE: [0x80, 0, True, None],  # ADD reg/mem, imm
    },

    "SUB": {
        AddressingMode.REGISTER: [0x28, 0, True, None],   # SUB reg/mem, reg
        AddressingMode.IMMEDIATE: [0x80, 0, True, None],  # SUB reg/mem, imm
    },

    "CMP": {
        AddressingMode.REGISTER: [0x38, 0, True, None],   # CMP reg/mem, reg
        AddressingMode.IMMEDIATE: [0x80, 0, True, None],  # CMP reg/mem, imm
    },

    # Logic
    "AND": {
        AddressingMode.REGISTER: [0x20, 0, True, None],   # AND reg/mem, reg
        AddressingMode.IMMEDIATE: [0x80, 0, True, None],  # AND reg/mem, imm
    },

    "OR": {
        AddressingMode.REGISTER: [0x08, 0, True, None],   # OR reg/mem, reg
        AddressingMode.IMMEDIATE: [0x80, 0, True, None],  # OR reg/mem, imm
    },

    "XOR": {
        AddressingMode.REGISTER: [0x30, 0, True, None],   # XOR reg/mem, reg
        AddressingMode.IMMEDIATE: [0x80, 0, True, None],  # XOR reg/mem, imm
    },

    # Stack
    "PUSH": {
        AddressingMode.REGISTER: [0x50, 0, False, None],  # PUSH reg
    },

    "POP": {
        AddressingMode.REGISTER: [0x58, 0, False, None],  # POP reg
    },

    # Control Flow
    "JMP": {
        AddressingMode.REGISTER: [0xFF, 0, True, None],   # JMP reg/mem (near)
        AddressingMode.IMMEDIATE: [0xE9, 0, False, None], # JMP rel16 (near)
    },

    "CALL": {
        AddressingMode.REGISTER: [0xFF, 0, True, None],   # CALL reg/mem (near)
        AddressingMode.IMMEDIATE: [0xE8, 0, False, None], # CALL rel16 (near)
    },

    # String Operations
    "MOVSB": {
        AddressingMode.IMPLIED: [0xA4, 0, False, None],   # MOVSB
    },

    "MOVSW": {
        AddressingMode.IMPLIED: [0xA5, 0, False, None],   # MOVSW
    },

    # I/O
    "IN": {
        AddressingMode.IMMEDIATE: [0xE4, 0, False, None], # IN AL, imm8
    },

    "OUT": {
        AddressingMode.IMMEDIATE: [0xE6, 0, False, None], # OUT imm8, AL
    },

    # Miscellaneous
    "NOP": {
        AddressingMode.IMPLIED: [0x90, 0, False, None],   # NOP
    },

    "INT": {
        AddressingMode.IMMEDIATE: [0xCD, 0, False, None], # INT imm8
    },

    "RET": {
        AddressingMode.IMPLIED: [0xC3, 0, False, None],   # RET (near)
    },
}

# Special opcodes that need special handling
SPECIAL_OPCODES = {
    "MOV_REG_IMM": 0xB0,  # MOV reg, imm (base for all registers)
    "ADD_IMM": 0x80,      # ADD/ADC/SBB/SUB/CMP/AND/TEST/OR/XOR reg/mem, imm
    "GROUP1_EXT": 0x80,   # Extension for immediate operations
}

# Mod-Reg-R/M encoding helpers
MOD_MEMORY_NO_DISP = 0b00
MOD_MEMORY_DISP8 = 0b01
MOD_MEMORY_DISP16 = 0b10
MOD_REGISTER = 0b11

# Register encodings for Mod-Reg-R/M
REG_AL = 0b000
REG_CL = 0b001
REG_DL = 0b010
REG_BL = 0b011
REG_AH = 0b100
REG_CH = 0b101
REG_DH = 0b110
REG_BH = 0b111

REG_AX = 0b000
REG_CX = 0b001
REG_DX = 0b010
REG_BX = 0b011
REG_SP = 0b100
REG_BP = 0b101
REG_SI = 0b110
REG_DI = 0b111

# Effective address calculations for memory operands
EA_BX_SI = 0b000
EA_BX_DI = 0b001
EA_BP_SI = 0b010
EA_BP_DI = 0b011
EA_SI = 0b100
EA_DI = 0b101
EA_BP = 0b110  # Can also be direct address
EA_BX = 0b111