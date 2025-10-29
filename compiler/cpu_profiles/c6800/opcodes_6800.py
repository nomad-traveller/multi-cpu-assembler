# opcodes_6800.py
# This module contains a sample of opcode data for the Motorola 6800 processor.

from enum import Enum, auto

class C6800AddressingMode(Enum):
    INHERENT = auto()
    ACCUMULATOR_A = auto()
    ACCUMULATOR_B = auto()
    IMMEDIATE = auto()
    DIRECT = auto()      # Like 6502 Zero-Page
    EXTENDED = auto()    # Like 6502 Absolute
    INDEXED = auto()     # e.g., 10,X
    RELATIVE = auto()    # For branches

# Structure: [opcode, operand_size, cycle_info, flags_affected]
# This is a small subset for demonstration purposes. A full implementation
# would include all 6800 instructions.
OPCODES_6800 = {
    "LDAA": {
        C6800AddressingMode.IMMEDIATE: [0x86, 1, {}, "NZV"],
        C6800AddressingMode.DIRECT:    [0x96, 1, {}, "NZV"],
        C6800AddressingMode.EXTENDED:  [0xB6, 2, {}, "NZV"],
        C6800AddressingMode.INDEXED:   [0xA6, 1, {}, "NZV"],
    },
    "LDAB": {
        C6800AddressingMode.IMMEDIATE: [0xC6, 1, {}, "NZV"],
        C6800AddressingMode.DIRECT:    [0xD6, 1, {}, "NZV"],
        C6800AddressingMode.EXTENDED:  [0xF6, 2, {}, "NZV"],
        C6800AddressingMode.INDEXED:   [0xE6, 1, {}, "NZV"],
    },
    "STAA": {
        C6800AddressingMode.DIRECT:    [0x97, 1, {}, "NZV"],
        C6800AddressingMode.EXTENDED:  [0xB7, 2, {}, "NZV"],
        C6800AddressingMode.INDEXED:   [0xA7, 1, {}, "NZV"],
    },
    "JMP": {
        C6800AddressingMode.EXTENDED:  [0x7E, 2, {}, ""],
        C6800AddressingMode.INDEXED:   [0x6E, 1, {}, ""],
    },
    "JSR": {
        C6800AddressingMode.EXTENDED:  [0xBD, 2, {}, ""],
        C6800AddressingMode.INDEXED:   [0xAD, 1, {}, ""],
    },
    "BRA": {
        C6800AddressingMode.RELATIVE:  [0x20, 1, {}, ""],
    },
    "BNE": {
        C6800AddressingMode.RELATIVE:  [0x26, 1, {}, ""],
    },
    "LDX": {
        C6800AddressingMode.IMMEDIATE: [0xCE, 2, {}, "NZV"],
        C6800AddressingMode.DIRECT:    [0xDE, 1, {}, "NZV"],
        C6800AddressingMode.EXTENDED:  [0xFE, 2, {}, "NZV"],
        C6800AddressingMode.INDEXED:   [0xEE, 1, {}, "NZV"],
    },
    "DEX": {
        C6800AddressingMode.INHERENT:  [0x09, 0, {}, "Z"],
    },
    "CLR": {
        C6800AddressingMode.EXTENDED:  [0x7F, 2, {}, "NZVC"],
        C6800AddressingMode.INDEXED:   [0x6F, 1, {}, "NZVC"],
    },
    "INX": {
        C6800AddressingMode.INHERENT:  [0x08, 0, {}, "Z"],
    },
    "NOP": {
        C6800AddressingMode.INHERENT:  [0x01, 0, {}, ""],
    },
    "RTS": {
        C6800AddressingMode.INHERENT:  [0x39, 0, {}, ""],
    },
}