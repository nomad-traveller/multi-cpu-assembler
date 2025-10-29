import unittest
import sys

# Add the compiler directory to the sys.path to allow imports
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

from cpu_profiles.c8086.c8086_profile import C8086Profile
from core.diagnostics import Diagnostics
from core.instruction import Instruction
from core.parser import Parser
from core.symbol_table import SymbolTable
from cpu_profiles.c8086.opcodes_8086 import AddressingMode, OPCODES_8086
from core.expression_parser import Number, Symbol


class TestC8086Profile(unittest.TestCase):
    """Test suite for the Intel 8086 CPU profile."""

    def setUp(self):
        self.diagnostics = Diagnostics()
        self.cpu_profile = C8086Profile(self.diagnostics)
        self.parser = Parser(self.cpu_profile, self.diagnostics)
        self.symbol_table = SymbolTable(self.diagnostics)

    def test_addressing_mode_parsing_implied(self):
        """Test parsing of implied addressing mode (no operand)."""
        mode, value = self.cpu_profile.parse_addressing_mode("")
        self.assertEqual(mode, AddressingMode.IMPLIED)
        self.assertIsNone(value)

    def test_addressing_mode_parsing_register_byte(self):
        """Test parsing of byte register operands."""
        mode, value = self.cpu_profile.parse_addressing_mode("AL")
        self.assertEqual(mode, AddressingMode.REGISTER)
        self.assertEqual(value, 0b000)  # REG_AL

        mode, value = self.cpu_profile.parse_addressing_mode("BH")
        self.assertEqual(mode, AddressingMode.REGISTER)
        self.assertEqual(value, 0b111)  # REG_BH

    def test_addressing_mode_parsing_register_word(self):
        """Test parsing of word register operands."""
        mode, value = self.cpu_profile.parse_addressing_mode("AX")
        self.assertEqual(mode, AddressingMode.REGISTER)
        self.assertEqual(value, 0b000)  # REG_AX

        mode, value = self.cpu_profile.parse_addressing_mode("SP")
        self.assertEqual(mode, AddressingMode.REGISTER)
        self.assertEqual(value, 0b100)  # REG_SP

    def test_addressing_mode_parsing_immediate_hex(self):
        """Test parsing of immediate hex values."""
        mode, value = self.cpu_profile.parse_addressing_mode("#$FF")
        self.assertEqual(mode, AddressingMode.IMMEDIATE)
        self.assertEqual(value, 0xFF)

        mode, value = self.cpu_profile.parse_addressing_mode("#$1234")
        self.assertEqual(mode, AddressingMode.IMMEDIATE)
        self.assertEqual(value, 0x1234)

    def test_addressing_mode_parsing_immediate_decimal(self):
        """Test parsing of immediate decimal values."""
        mode, value = self.cpu_profile.parse_addressing_mode("#42")
        self.assertEqual(mode, AddressingMode.IMMEDIATE)
        self.assertEqual(value, 42)

        mode, value = self.cpu_profile.parse_addressing_mode("#1234")
        self.assertEqual(mode, AddressingMode.IMMEDIATE)
        self.assertEqual(value, 1234)

    def test_addressing_mode_parsing_memory(self):
        """Test parsing of memory operands."""
        mode, value = self.cpu_profile.parse_addressing_mode("[BX]")
        self.assertEqual(mode, AddressingMode.MEMORY)
        self.assertEqual(value, "BX")

        mode, value = self.cpu_profile.parse_addressing_mode("[SI+8]")
        self.assertEqual(mode, AddressingMode.MEMORY)
        self.assertEqual(value, "SI+8")

    def test_parse_instruction_implied(self):
        """Test parsing of implied instructions."""
        instr = Instruction(1, "NOP")
        instr.mnemonic = "NOP"
        instr.operand_str = ""

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, AddressingMode.IMPLIED)
        self.assertIsNone(instr.operand_value)

    def test_parse_instruction_register(self):
        """Test parsing of register instructions."""
        instr = Instruction(1, "PUSH AX")
        instr.mnemonic = "PUSH"
        instr.operand_str = "AX"

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, AddressingMode.REGISTER)
        self.assertIsNotNone(instr.operand_value)

    def test_parse_instruction_immediate(self):
        """Test parsing of immediate instructions."""
        instr = Instruction(1, "INT #21")
        instr.mnemonic = "INT"
        instr.operand_str = "#21"

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, AddressingMode.IMMEDIATE)
        self.assertIsInstance(instr.operand_value, Number)
        self.assertEqual(instr.operand_value.value, 21)

    def test_parse_directive_org(self):
        """Test parsing of .ORG directive."""
        instr = Instruction(1, ".ORG $100")
        instr.directive = ".ORG"
        instr.operand_str = "$100"

        self.cpu_profile.parse_directive(instr, self.parser)
        self.assertIsNotNone(instr.operand_value)

    def test_parse_directive_byte(self):
        """Test parsing of .BYTE directive."""
        instr = Instruction(1, ".BYTE $01, $02, $03")
        instr.directive = ".BYTE"
        instr.operand_str = "$01, $02, $03"

        self.cpu_profile.parse_directive(instr, self.parser)
        self.assertEqual(len(instr.operand_value), 3)
        self.assertEqual(instr.size, 3)

    def test_parse_directive_word(self):
        """Test parsing of .WORD directive."""
        instr = Instruction(1, ".WORD $1234, $5678")
        instr.directive = ".WORD"
        instr.operand_str = "$1234, $5678"

        self.cpu_profile.parse_directive(instr, self.parser)
        self.assertEqual(len(instr.operand_value), 2)
        self.assertEqual(instr.size, 4)  # 2 bytes per word

    def test_parse_directive_unknown(self):
        """Test parsing of unknown directive."""
        instr = Instruction(1, ".UNKNOWN $1234")
        instr.directive = ".UNKNOWN"
        instr.operand_str = "$1234"

        with self.assertRaises(ValueError) as cm:
            self.cpu_profile.parse_directive(instr, self.parser)
        self.assertIn("Unknown directive", str(cm.exception))

    def test_get_opcode_details_valid(self):
        """Test getting opcode details for valid instructions."""
        instr = Instruction(1, "NOP")
        instr.mnemonic = "NOP"
        instr.mode = AddressingMode.IMPLIED

        details = self.cpu_profile.get_opcode_details(instr, self.symbol_table)
        self.assertIsNotNone(details)
        self.assertEqual(details[0], 0x90)  # NOP opcode
        self.assertEqual(details[1], 0)     # 0 operand bytes

    def test_get_opcode_details_invalid_mnemonic(self):
        """Test getting opcode details for invalid mnemonic."""
        instr = Instruction(1, "INVALID")
        instr.mnemonic = "INVALID"
        instr.mode = AddressingMode.IMPLIED

        details = self.cpu_profile.get_opcode_details(instr, self.symbol_table)
        self.assertIsNone(details)

    def test_get_opcode_details_invalid_mode(self):
        """Test getting opcode details for invalid mode."""
        instr = Instruction(1, "NOP #$FF")
        instr.mnemonic = "NOP"
        instr.mode = AddressingMode.IMMEDIATE  # NOP doesn't support immediate

        details = self.cpu_profile.get_opcode_details(instr, self.symbol_table)
        self.assertIsNone(details)

    def test_encode_instruction_implied(self):
        """Test encoding of implied instructions."""
        instr = Instruction(1, "NOP")
        instr.mnemonic = "NOP"
        instr.mode = AddressingMode.IMPLIED
        instr.address = 0x1000

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        self.assertEqual(instr.machine_code, [0x90])

    def test_encode_instruction_int(self):
        """Test encoding of INT instruction."""
        instr = Instruction(1, "INT #21")
        instr.mnemonic = "INT"
        instr.mode = AddressingMode.IMMEDIATE
        instr.address = 0x1000
        instr.operand_value = Number(0x21)

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        self.assertEqual(instr.machine_code, [0xCD, 0x21])

    def test_encode_instruction_jmp_immediate(self):
        """Test encoding of JMP with immediate operand."""
        # Set up symbol table with target label
        self.symbol_table.add("TARGET", 0x1005, 1)

        instr = Instruction(1, "JMP #TARGET")
        instr.mnemonic = "JMP"
        instr.mode = AddressingMode.IMMEDIATE
        instr.address = 0x1000
        instr.operand_value = Symbol("TARGET")

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        # JMP rel16: E9 + 16-bit offset
        # From 0x1000 to 0x1005 = +5, so offset should be 5 - 3 = 2
        expected_offset = 0x1005 - (0x1000 + 3)  # 3 bytes for JMP instruction
        self.assertEqual(instr.machine_code, [0xE9, expected_offset & 0xFF, (expected_offset >> 8) & 0xFF])

    def test_encode_instruction_jmp_out_of_range(self):
        """Test encoding of JMP with out-of-range target."""
        # Set up symbol table with far target
        self.symbol_table.add("FAR_TARGET", 0x20000, 1)  # Too far for 16-bit offset

        instr = Instruction(1, "JMP #FAR_TARGET")
        instr.mnemonic = "JMP"
        instr.mode = AddressingMode.IMMEDIATE
        instr.address = 0x1000
        instr.operand_value = Symbol("FAR_TARGET")

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertFalse(success)  # Should fail due to range error

    def test_encode_instruction_undefined_symbol(self):
        """Test encoding with undefined symbol."""
        instr = Instruction(1, "JMP #UNDEFINED")
        instr.mnemonic = "JMP"
        instr.mode = AddressingMode.IMMEDIATE
        instr.address = 0x1000
        instr.operand_value = Symbol("UNDEFINED")

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertFalse(success)

    def test_encode_instruction_invalid_int_value(self):
        """Test encoding of INT with invalid value."""
        instr = Instruction(1, "INT #256")  # Too big for 8-bit
        instr.mnemonic = "INT"
        instr.mode = AddressingMode.IMMEDIATE
        instr.address = 0x1000
        instr.operand_value = Number(256)

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertFalse(success)

    def test_branch_mnemonics_property(self):
        """Test that branch mnemonics are correctly defined (empty for 8086)."""
        self.assertEqual(self.cpu_profile.branch_mnemonics, set())

    def test_opcodes_property(self):
        """Test that opcodes property returns the correct opcode table."""
        self.assertEqual(self.cpu_profile.opcodes, OPCODES_8086)

    def test_addressing_modes_enum_property(self):
        """Test that addressing_modes_enum property returns the correct enum."""
        self.assertEqual(self.cpu_profile.addressing_modes_enum, AddressingMode)


if __name__ == '__main__':
    unittest.main()