# opcodes_65C02.py
# This module contains the opcode data for the 65C02 processor.
# Data is based on standard 65C02 opcode tables (e.g., from 6502.org or Wikipedia).
# cycle_info_dict includes base cycles and penalties (e.g., page cross, branch taken).

from enum import Enum

class AddressingMode(Enum):
    IMPLIED = 0
    ACCUMULATOR = 1
    IMMEDIATE = 2
    ZEROPAGE = 3
    ZEROPAGE_X = 4
    ZEROPAGE_Y = 5
    ABSOLUTE = 6
    ABSOLUTE_X = 7
    ABSOLUTE_Y = 8
    INDIRECT = 9
    INDIRECT_X = 10
    INDIRECT_Y = 11
    RELATIVE = 12
    ZEROPAGE_INDIRECT = 13  # 65C02: (zp)

OPCODES = {
    "ADC": {
        AddressingMode.IMMEDIATE: [0x69, 1, {"base": 2}, "NVZC"],
        AddressingMode.ZEROPAGE: [0x65, 1, {"base": 3}, "NVZC"],
        AddressingMode.ZEROPAGE_X: [0x75, 1, {"base": 4}, "NVZC"],
        AddressingMode.ABSOLUTE: [0x6D, 2, {"base": 4}, "NVZC"],
        AddressingMode.ABSOLUTE_X: [0x7D, 2, {"base": 4, "page": 1}, "NVZC"],
        AddressingMode.ABSOLUTE_Y: [0x79, 2, {"base": 4, "page": 1}, "NVZC"],
        AddressingMode.INDIRECT_X: [0x61, 1, {"base": 6}, "NVZC"],
        AddressingMode.INDIRECT_Y: [0x71, 1, {"base": 5, "page": 1}, "NVZC"],
        AddressingMode.ZEROPAGE_INDIRECT: [0x72, 1, {"base": 5}, "NVZC"],  # 65C02
    },
    "AND": {
        AddressingMode.IMMEDIATE: [0x29, 1, {"base": 2}, "NZ"],
        AddressingMode.ZEROPAGE: [0x25, 1, {"base": 3}, "NZ"],
        AddressingMode.ZEROPAGE_X: [0x35, 1, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE: [0x2D, 2, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE_X: [0x3D, 2, {"base": 4, "page": 1}, "NZ"],
        AddressingMode.ABSOLUTE_Y: [0x39, 2, {"base": 4, "page": 1}, "NZ"],
        AddressingMode.INDIRECT_X: [0x21, 1, {"base": 6}, "NZ"],
        AddressingMode.INDIRECT_Y: [0x31, 1, {"base": 5, "page": 1}, "NZ"],
        AddressingMode.ZEROPAGE_INDIRECT: [0x32, 1, {"base": 5}, "NZ"],  # 65C02
    },
    "ASL": {
        AddressingMode.ACCUMULATOR: [0x0A, 0, {"base": 2}, "NZC"],
        AddressingMode.ZEROPAGE: [0x06, 1, {"base": 5}, "NZC"],
        AddressingMode.ZEROPAGE_X: [0x16, 1, {"base": 6}, "NZC"],
        AddressingMode.ABSOLUTE: [0x0E, 2, {"base": 6}, "NZC"],
        AddressingMode.ABSOLUTE_X: [0x1E, 2, {"base": 7}, "NZC"],
    },
    "BCC": {
        AddressingMode.RELATIVE: [0x90, 1, {"base": 2, "branch": 1, "page": 1}, ""],
    },
    "BCS": {
        AddressingMode.RELATIVE: [0xB0, 1, {"base": 2, "branch": 1, "page": 1}, ""],
    },
    "BEQ": {
        AddressingMode.RELATIVE: [0xF0, 1, {"base": 2, "branch": 1, "page": 1}, ""],
    },
    "BIT": {
        AddressingMode.IMMEDIATE: [0x89, 1, {"base": 2}, "NZ"],  # 65C02
        AddressingMode.ZEROPAGE: [0x24, 1, {"base": 3}, "NVZ"],
        AddressingMode.ABSOLUTE: [0x2C, 2, {"base": 4}, "NVZ"],
        AddressingMode.ZEROPAGE_X: [0x34, 1, {"base": 4}, "NVZ"],  # 65C02
        AddressingMode.ABSOLUTE_X: [0x3C, 2, {"base": 4, "page": 1}, "NVZ"],  # 65C02
    },
    "BMI": {
        AddressingMode.RELATIVE: [0x30, 1, {"base": 2, "branch": 1, "page": 1}, ""],
    },
    "BNE": {
        AddressingMode.RELATIVE: [0xD0, 1, {"base": 2, "branch": 1, "page": 1}, ""],
    },
    "BPL": {
        AddressingMode.RELATIVE: [0x10, 1, {"base": 2, "branch": 1, "page": 1}, ""],
    },
    "BRA": {  # 65C02
        AddressingMode.RELATIVE: [0x80, 1, {"base": 2, "branch": 1, "page": 1}, ""],
    },
    "BRK": {
        AddressingMode.IMPLIED: [0x00, 0, {"base": 7}, "B"],
    },
    "BVC": {
        AddressingMode.RELATIVE: [0x50, 1, {"base": 2, "branch": 1, "page": 1}, ""],
    },
    "BVS": {
        AddressingMode.RELATIVE: [0x70, 1, {"base": 2, "branch": 1, "page": 1}, ""],
    },
    "CLC": {
        AddressingMode.IMPLIED: [0x18, 0, {"base": 2}, "C"],
    },
    "CLD": {
        AddressingMode.IMPLIED: [0xD8, 0, {"base": 2}, "D"],
    },
    "CLI": {
        AddressingMode.IMPLIED: [0x58, 0, {"base": 2}, "I"],
    },
    "CLV": {
        AddressingMode.IMPLIED: [0xB8, 0, {"base": 2}, "V"],
    },
    "CMP": {
        AddressingMode.IMMEDIATE: [0xC9, 1, {"base": 2}, "NZC"],
        AddressingMode.ZEROPAGE: [0xC5, 1, {"base": 3}, "NZC"],
        AddressingMode.ZEROPAGE_X: [0xD5, 1, {"base": 4}, "NZC"],
        AddressingMode.ABSOLUTE: [0xCD, 2, {"base": 4}, "NZC"],
        AddressingMode.ABSOLUTE_X: [0xDD, 2, {"base": 4, "page": 1}, "NZC"],
        AddressingMode.ABSOLUTE_Y: [0xD9, 2, {"base": 4, "page": 1}, "NZC"],
        AddressingMode.INDIRECT_X: [0xC1, 1, {"base": 6}, "NZC"],
        AddressingMode.INDIRECT_Y: [0xD1, 1, {"base": 5, "page": 1}, "NZC"],
        AddressingMode.ZEROPAGE_INDIRECT: [0xD2, 1, {"base": 5}, "NZC"],  # 65C02
    },
    "CPX": {
        AddressingMode.IMMEDIATE: [0xE0, 1, {"base": 2}, "NZC"],
        AddressingMode.ZEROPAGE: [0xE4, 1, {"base": 3}, "NZC"],
        AddressingMode.ABSOLUTE: [0xEC, 2, {"base": 4}, "NZC"],
    },
    "CPY": {
        AddressingMode.IMMEDIATE: [0xC0, 1, {"base": 2}, "NZC"],
        AddressingMode.ZEROPAGE: [0xC4, 1, {"base": 3}, "NZC"],
        AddressingMode.ABSOLUTE: [0xCC, 2, {"base": 4}, "NZC"],
    },
    "DEC": {
        AddressingMode.ACCUMULATOR: [0x3A, 0, {"base": 2}, "NZ"],  # 65C02
        AddressingMode.ZEROPAGE: [0xC6, 1, {"base": 5}, "NZ"],
        AddressingMode.ZEROPAGE_X: [0xD6, 1, {"base": 6}, "NZ"],
        AddressingMode.ABSOLUTE: [0xCE, 2, {"base": 6}, "NZ"],
        AddressingMode.ABSOLUTE_X: [0xDE, 2, {"base": 7}, "NZ"],
    },
    "DEX": {
        AddressingMode.IMPLIED: [0xCA, 0, {"base": 2}, "NZ"],
    },
    "DEY": {
        AddressingMode.IMPLIED: [0x88, 0, {"base": 2}, "NZ"],
    },
    "EOR": {
        AddressingMode.IMMEDIATE: [0x49, 1, {"base": 2}, "NZ"],
        AddressingMode.ZEROPAGE: [0x45, 1, {"base": 3}, "NZ"],
        AddressingMode.ZEROPAGE_X: [0x55, 1, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE: [0x4D, 2, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE_X: [0x5D, 2, {"base": 4, "page": 1}, "NZ"],
        AddressingMode.ABSOLUTE_Y: [0x59, 2, {"base": 4, "page": 1}, "NZ"],
        AddressingMode.INDIRECT_X: [0x41, 1, {"base": 6}, "NZ"],
        AddressingMode.INDIRECT_Y: [0x51, 1, {"base": 5, "page": 1}, "NZ"],
        AddressingMode.ZEROPAGE_INDIRECT: [0x52, 1, {"base": 5}, "NZ"],  # 65C02
    },
    "INC": {
        AddressingMode.ACCUMULATOR: [0x1A, 0, {"base": 2}, "NZ"],  # 65C02
        AddressingMode.ZEROPAGE: [0xE6, 1, {"base": 5}, "NZ"],
        AddressingMode.ZEROPAGE_X: [0xF6, 1, {"base": 6}, "NZ"],
        AddressingMode.ABSOLUTE: [0xEE, 2, {"base": 6}, "NZ"],
        AddressingMode.ABSOLUTE_X: [0xFE, 2, {"base": 7}, "NZ"],
    },
    "INX": {
        AddressingMode.IMPLIED: [0xE8, 0, {"base": 2}, "NZ"],
    },
    "INY": {
        AddressingMode.IMPLIED: [0xC8, 0, {"base": 2}, "NZ"],
    },
    "JMP": {
        AddressingMode.ABSOLUTE: [0x4C, 2, {"base": 3}, ""],
        AddressingMode.INDIRECT: [0x6C, 2, {"base": 5}, ""],
        AddressingMode.ABSOLUTE_X: [0x7C, 2, {"base": 6}, ""],  # 65C02: JMP (abs,X)
    },
    "JSR": {
        AddressingMode.ABSOLUTE: [0x20, 2, {"base": 6}, ""],
    },
    "LDA": {
        AddressingMode.IMMEDIATE: [0xA9, 1, {"base": 2}, "NZ"],
        AddressingMode.ZEROPAGE: [0xA5, 1, {"base": 3}, "NZ"],
        AddressingMode.ZEROPAGE_X: [0xB5, 1, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE: [0xAD, 2, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE_X: [0xBD, 2, {"base": 4, "page": 1}, "NZ"],
        AddressingMode.ABSOLUTE_Y: [0xB9, 2, {"base": 4, "page": 1}, "NZ"],
        AddressingMode.INDIRECT_X: [0xA1, 1, {"base": 6}, "NZ"],
        AddressingMode.INDIRECT_Y: [0xB1, 1, {"base": 5, "page": 1}, "NZ"],
        AddressingMode.ZEROPAGE_INDIRECT: [0xB2, 1, {"base": 5}, "NZ"],  # 65C02
    },
    "LDX": {
        AddressingMode.IMMEDIATE: [0xA2, 1, {"base": 2}, "NZ"],
        AddressingMode.ZEROPAGE: [0xA6, 1, {"base": 3}, "NZ"],
        AddressingMode.ZEROPAGE_Y: [0xB6, 1, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE: [0xAE, 2, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE_Y: [0xBE, 2, {"base": 4, "page": 1}, "NZ"],
    },
    "LDY": {
        AddressingMode.IMMEDIATE: [0xA0, 1, {"base": 2}, "NZ"],
        AddressingMode.ZEROPAGE: [0xA4, 1, {"base": 3}, "NZ"],
        AddressingMode.ZEROPAGE_X: [0xB4, 1, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE: [0xAC, 2, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE_X: [0xBC, 2, {"base": 4, "page": 1}, "NZ"],
    },
    "LSR": {
        AddressingMode.ACCUMULATOR: [0x4A, 0, {"base": 2}, "NZC"],
        AddressingMode.ZEROPAGE: [0x46, 1, {"base": 5}, "NZC"],
        AddressingMode.ZEROPAGE_X: [0x56, 1, {"base": 6}, "NZC"],
        AddressingMode.ABSOLUTE: [0x4E, 2, {"base": 6}, "NZC"],
        AddressingMode.ABSOLUTE_X: [0x5E, 2, {"base": 7}, "NZC"],
    },
    "NOP": {
        AddressingMode.IMPLIED: [0xEA, 0, {"base": 2}, ""],
    },
    "ORA": {
        AddressingMode.IMMEDIATE: [0x09, 1, {"base": 2}, "NZ"],
        AddressingMode.ZEROPAGE: [0x05, 1, {"base": 3}, "NZ"],
        AddressingMode.ZEROPAGE_X: [0x15, 1, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE: [0x0D, 2, {"base": 4}, "NZ"],
        AddressingMode.ABSOLUTE_X: [0x1D, 2, {"base": 4, "page": 1}, "NZ"],
        AddressingMode.ABSOLUTE_Y: [0x19, 2, {"base": 4, "page": 1}, "NZ"],
        AddressingMode.INDIRECT_X: [0x01, 1, {"base": 6}, "NZ"],
        AddressingMode.INDIRECT_Y: [0x11, 1, {"base": 5, "page": 1}, "NZ"],
        AddressingMode.ZEROPAGE_INDIRECT: [0x12, 1, {"base": 5}, "NZ"],  # 65C02
    },
    "PHA": {
        AddressingMode.IMPLIED: [0x48, 0, {"base": 3}, ""],
    },
    "PHP": {
        AddressingMode.IMPLIED: [0x08, 0, {"base": 3}, ""],
    },
    "PHX": {  # 65C02
        AddressingMode.IMPLIED: [0xDA, 0, {"base": 3}, ""],
    },
    "PHY": {  # 65C02
        AddressingMode.IMPLIED: [0x5A, 0, {"base": 3}, ""],
    },
    "PLA": {
        AddressingMode.IMPLIED: [0x68, 0, {"base": 4}, "NZ"],
    },
    "PLP": {
        AddressingMode.IMPLIED: [0x28, 0, {"base": 4}, "NVZC"],  # All flags
    },
    "PLX": {  # 65C02
        AddressingMode.IMPLIED: [0xFA, 0, {"base": 4}, "NZ"],
    },
    "PLY": {  # 65C02
        AddressingMode.IMPLIED: [0x7A, 0, {"base": 4}, "NZ"],
    },
    "ROL": {
        AddressingMode.ACCUMULATOR: [0x2A, 0, {"base": 2}, "NZC"],
        AddressingMode.ZEROPAGE: [0x26, 1, {"base": 5}, "NZC"],
        AddressingMode.ZEROPAGE_X: [0x36, 1, {"base": 6}, "NZC"],
        AddressingMode.ABSOLUTE: [0x2E, 2, {"base": 6}, "NZC"],
        AddressingMode.ABSOLUTE_X: [0x3E, 2, {"base": 7}, "NZC"],
    },
    "ROR": {
        AddressingMode.ACCUMULATOR: [0x6A, 0, {"base": 2}, "NZC"],
        AddressingMode.ZEROPAGE: [0x66, 1, {"base": 5}, "NZC"],
        AddressingMode.ZEROPAGE_X: [0x76, 1, {"base": 6}, "NZC"],
        AddressingMode.ABSOLUTE: [0x6E, 2, {"base": 6}, "NZC"],
        AddressingMode.ABSOLUTE_X: [0x7E, 2, {"base": 7}, "NZC"],
    },
    "RTI": {
        AddressingMode.IMPLIED: [0x40, 0, {"base": 6}, "NVZC"],  # All flags
    },
    "RTS": {
        AddressingMode.IMPLIED: [0x60, 0, {"base": 6}, ""],
    },
    "SBC": {
        AddressingMode.IMMEDIATE: [0xE9, 1, {"base": 2}, "NVZC"],
        AddressingMode.ZEROPAGE: [0xE5, 1, {"base": 3}, "NVZC"],
        AddressingMode.ZEROPAGE_X: [0xF5, 1, {"base": 4}, "NVZC"],
        AddressingMode.ABSOLUTE: [0xED, 2, {"base": 4}, "NVZC"],
        AddressingMode.ABSOLUTE_X: [0xFD, 2, {"base": 4, "page": 1}, "NVZC"],
        AddressingMode.ABSOLUTE_Y: [0xF9, 2, {"base": 4, "page": 1}, "NVZC"],
        AddressingMode.INDIRECT_X: [0xE1, 1, {"base": 6}, "NVZC"],
        AddressingMode.INDIRECT_Y: [0xF1, 1, {"base": 5, "page": 1}, "NVZC"],
        AddressingMode.ZEROPAGE_INDIRECT: [0xF2, 1, {"base": 5}, "NVZC"],  # 65C02
    },
    "SEC": {
        AddressingMode.IMPLIED: [0x38, 0, {"base": 2}, "C"],
    },
    "SED": {
        AddressingMode.IMPLIED: [0xF8, 0, {"base": 2}, "D"],
    },
    "SEI": {
        AddressingMode.IMPLIED: [0x78, 0, {"base": 2}, "I"],
    },
    "STA": {
        AddressingMode.ZEROPAGE: [0x85, 1, {"base": 3}, ""],
        AddressingMode.ZEROPAGE_X: [0x95, 1, {"base": 4}, ""],
        AddressingMode.ABSOLUTE: [0x8D, 2, {"base": 4}, ""],
        AddressingMode.ABSOLUTE_X: [0x9D, 2, {"base": 5}, ""],
        AddressingMode.ABSOLUTE_Y: [0x99, 2, {"base": 5}, ""],
        AddressingMode.INDIRECT_X: [0x81, 1, {"base": 6}, ""],
        AddressingMode.INDIRECT_Y: [0x91, 1, {"base": 6}, ""],
        AddressingMode.ZEROPAGE_INDIRECT: [0x92, 1, {"base": 5}, ""],  # 65C02
    },
    "STX": {
        AddressingMode.ZEROPAGE: [0x86, 1, {"base": 3}, ""],
        AddressingMode.ZEROPAGE_Y: [0x96, 1, {"base": 4}, ""],
        AddressingMode.ABSOLUTE: [0x8E, 2, {"base": 4}, ""],
    },
    "STY": {
        AddressingMode.ZEROPAGE: [0x84, 1, {"base": 3}, ""],
        AddressingMode.ZEROPAGE_X: [0x94, 1, {"base": 4}, ""],
        AddressingMode.ABSOLUTE: [0x8C, 2, {"base": 4}, ""],
    },
    "STZ": {  # 65C02
        AddressingMode.ZEROPAGE: [0x64, 1, {"base": 3}, ""],
        AddressingMode.ZEROPAGE_X: [0x74, 1, {"base": 4}, ""],
        AddressingMode.ABSOLUTE: [0x9C, 2, {"base": 4}, ""],
        AddressingMode.ABSOLUTE_X: [0x9E, 2, {"base": 5}, ""],
    },
    "TAX": {
        AddressingMode.IMPLIED: [0xAA, 0, {"base": 2}, "NZ"],
    },
    "TAY": {
        AddressingMode.IMPLIED: [0xA8, 0, {"base": 2}, "NZ"],
    },
    "TRB": {  # 65C02
        AddressingMode.ZEROPAGE: [0x14, 1, {"base": 5}, "Z"],
        AddressingMode.ABSOLUTE: [0x1C, 2, {"base": 6}, "Z"],
    },
    "TSB": {  # 65C02
        AddressingMode.ZEROPAGE: [0x04, 1, {"base": 5}, "Z"],
        AddressingMode.ABSOLUTE: [0x0C, 2, {"base": 6}, "Z"],
    },
    "TSX": {
        AddressingMode.IMPLIED: [0xBA, 0, {"base": 2}, "NZ"],
    },
    "TXA": {
        AddressingMode.IMPLIED: [0x8A, 0, {"base": 2}, "NZ"],
    },
    "TXS": {
        AddressingMode.IMPLIED: [0x9A, 0, {"base": 2}, ""],
    },
    "TYA": {
        AddressingMode.IMPLIED: [0x98, 0, {"base": 2}, "NZ"],
    },
}
