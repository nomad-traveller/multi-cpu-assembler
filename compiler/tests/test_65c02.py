import unittest
import sys
import os
from io import StringIO
from unittest.mock import MagicMock

# Add the compiler directory to the sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

# Import classes from your project
from cpu_profiles.c6502.c6502_profile import C6502Profile
from core.diagnostics import Diagnostics
from core.instruction import Instruction
from core.parser import Parser
from core.symbol_table import SymbolTable
from cpu_profiles.c6502.opcodes_65C02 import AddressingMode, OPCODES
from core.expression_parser import Number, Symbol


class TestC6502Profile(unittest.TestCase):
    """Test suite for the 65C02 CPU profile."""

    def setUp(self):
        self.diagnostics = Diagnostics()
        self.cpu_profile = C6502Profile(self.diagnostics)
        self.parser = Parser(self.cpu_profile, self.diagnostics)
        self.symbol_table = SymbolTable(self.diagnostics)

    def test_addressing_mode_parsing_implied(self):
        """Test parsing of implied addressing mode (no operand)."""
        mode, value = self.cpu_profile.parse_addressing_mode("")
        self.assertEqual(mode, AddressingMode.IMPLIED)
        self.assertIsNone(value)

    def test_addressing_mode_parsing_accumulator(self):
        """Test parsing of accumulator addressing mode."""
        mode, value = self.cpu_profile.parse_addressing_mode("A")
        self.assertEqual(mode, AddressingMode.ACCUMULATOR)
        self.assertIsNone(value)

        mode, value = self.cpu_profile.parse_addressing_mode("a")
        self.assertEqual(mode, AddressingMode.ACCUMULATOR)
        self.assertIsNone(value)

    def test_addressing_mode_parsing_immediate(self):
        """Test parsing of immediate addressing mode."""
        # Hex immediate
        mode, value = self.cpu_profile.parse_addressing_mode("#$FF")
        self.assertEqual(mode, AddressingMode.IMMEDIATE)
        self.assertEqual(value, 0xFF)

        # Decimal immediate
        mode, value = self.cpu_profile.parse_addressing_mode("#42")
        self.assertEqual(mode, AddressingMode.IMMEDIATE)
        self.assertEqual(value, 42)

        # Label immediate
        mode, value = self.cpu_profile.parse_addressing_mode("#MY_CONST")
        self.assertEqual(mode, AddressingMode.IMMEDIATE)
        self.assertEqual(value, "MY_CONST")

    def test_addressing_mode_parsing_zeropage(self):
        """Test parsing of zeropage addressing modes."""
        # Zero page
        mode, value = self.cpu_profile.parse_addressing_mode("$10")
        self.assertEqual(mode, AddressingMode.ZEROPAGE)
        self.assertEqual(value, 0x10)

        # Zero page X
        mode, value = self.cpu_profile.parse_addressing_mode("$10,X")
        self.assertEqual(mode, AddressingMode.ZEROPAGE_X)
        self.assertEqual(value, 0x10)

        # Zero page Y
        mode, value = self.cpu_profile.parse_addressing_mode("$10,Y")
        self.assertEqual(mode, AddressingMode.ZEROPAGE_Y)
        self.assertEqual(value, 0x10)

    def test_addressing_mode_parsing_absolute(self):
        """Test parsing of absolute addressing modes."""
        # Absolute
        mode, value = self.cpu_profile.parse_addressing_mode("$1234")
        self.assertEqual(mode, AddressingMode.ABSOLUTE)
        self.assertEqual(value, 0x1234)

        # Absolute X
        mode, value = self.cpu_profile.parse_addressing_mode("$1234,X")
        self.assertEqual(mode, AddressingMode.ABSOLUTE_X)
        self.assertEqual(value, 0x1234)

        # Absolute Y
        mode, value = self.cpu_profile.parse_addressing_mode("$1234,Y")
        self.assertEqual(mode, AddressingMode.ABSOLUTE_Y)
        self.assertEqual(value, 0x1234)

    def test_addressing_mode_parsing_indirect(self):
        """Test parsing of indirect addressing modes."""
        # Indirect (JMP)
        mode, value = self.cpu_profile.parse_addressing_mode("($1234)")
        self.assertEqual(mode, AddressingMode.INDIRECT)
        self.assertEqual(value, 0x1234)

        # Zero page indirect (65C02)
        mode, value = self.cpu_profile.parse_addressing_mode("($10)")
        self.assertEqual(mode, AddressingMode.ZEROPAGE_INDIRECT)
        self.assertEqual(value, 0x10)

        # Indirect X
        mode, value = self.cpu_profile.parse_addressing_mode("($10,X)")
        self.assertEqual(mode, AddressingMode.INDIRECT_X)
        self.assertEqual(value, 0x10)

        # Indirect Y
        mode, value = self.cpu_profile.parse_addressing_mode("($10),Y")
        self.assertEqual(mode, AddressingMode.INDIRECT_Y)
        self.assertEqual(value, 0x10)

    def test_addressing_mode_parsing_labels(self):
        """Test parsing of label operands."""
        # Label (defaults to absolute)
        mode, value = self.cpu_profile.parse_addressing_mode("MY_LABEL")
        self.assertEqual(mode, AddressingMode.ABSOLUTE)
        self.assertEqual(value, "MY_LABEL")

        # Decimal number
        mode, value = self.cpu_profile.parse_addressing_mode("1234")
        self.assertEqual(mode, AddressingMode.ABSOLUTE)
        self.assertEqual(value, 1234)

    def test_addressing_mode_parsing_invalid(self):
        """Test parsing of invalid operand formats."""
        # This should fail because it doesn't match any pattern
        mode, value = self.cpu_profile.parse_addressing_mode("$INVALID")
        self.assertIsNone(mode)
        self.assertIsNone(value)

    def test_parse_instruction_implied(self):
        """Test parsing of implied instructions."""
        instr = Instruction(1, "NOP")
        instr.mnemonic = "NOP"
        instr.operand_str = ""

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, AddressingMode.IMPLIED)
        self.assertIsNone(instr.operand_value)

    def test_parse_instruction_immediate(self):
        """Test parsing of immediate instructions."""
        instr = Instruction(1, "LDA #$FF")
        instr.mnemonic = "LDA"
        instr.operand_str = "#$FF"

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, AddressingMode.IMMEDIATE)
        self.assertIsInstance(instr.operand_value, Number)
        self.assertEqual(instr.operand_value.value, 0xFF)

    def test_parse_instruction_branch(self):
        """Test parsing of branch instructions."""
        instr = Instruction(1, "BEQ MY_LABEL")
        instr.mnemonic = "BEQ"
        instr.operand_str = "MY_LABEL"

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, AddressingMode.RELATIVE)
        self.assertIsInstance(instr.operand_value, Symbol)
        self.assertEqual(instr.operand_value.name, "MY_LABEL")

    def test_parse_instruction_zeropage_conversion(self):
        """Test automatic conversion from absolute to zeropage for small values."""
        instr = Instruction(1, "LDA $10")
        instr.mnemonic = "LDA"
        instr.operand_str = "$10"

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, AddressingMode.ZEROPAGE)

    def test_parse_directive_org(self):
        """Test parsing of .ORG directive."""
        instr = Instruction(1, ".ORG $8000")
        instr.directive = ".ORG"
        instr.operand_str = "$8000"

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
        instr = Instruction(1, "LDA #$FF")
        instr.mnemonic = "LDA"
        instr.mode = AddressingMode.IMMEDIATE

        details = self.cpu_profile.get_opcode_details(instr, self.symbol_table)
        self.assertIsNotNone(details)
        self.assertEqual(details[0], 0xA9)  # LDA immediate opcode
        self.assertEqual(details[1], 1)     # 1 byte operand

    def test_get_opcode_details_invalid_mnemonic(self):
        """Test getting opcode details for invalid mnemonic."""
        instr = Instruction(1, "INVALID #$FF")
        instr.mnemonic = "INVALID"
        instr.mode = AddressingMode.IMMEDIATE

        details = self.cpu_profile.get_opcode_details(instr, self.symbol_table)
        self.assertIsNone(details)

    def test_get_opcode_details_invalid_mode(self):
        """Test getting opcode details for invalid mode."""
        instr = Instruction(1, "LDA #$FF")
        instr.mnemonic = "LDA"
        instr.mode = AddressingMode.INDIRECT  # LDA doesn't support indirect

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
        self.assertEqual(instr.machine_code, [0xEA])

    def test_encode_instruction_immediate(self):
        """Test encoding of immediate instructions."""
        instr = Instruction(1, "LDA #$42")
        instr.mnemonic = "LDA"
        instr.mode = AddressingMode.IMMEDIATE
        instr.address = 0x1000
        instr.operand_value = Number(0x42)

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        self.assertEqual(instr.machine_code, [0xA9, 0x42])

    def test_encode_instruction_absolute(self):
        """Test encoding of absolute instructions."""
        instr = Instruction(1, "STA $1234")
        instr.mnemonic = "STA"
        instr.mode = AddressingMode.ABSOLUTE
        instr.address = 0x1000
        instr.operand_value = Number(0x1234)

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        self.assertEqual(instr.machine_code, [0x8D, 0x34, 0x12])

    def test_encode_instruction_branch(self):
        """Test encoding of branch instructions."""
        # Set up symbol table with target label
        self.symbol_table.add("TARGET", 0x1005, 1)

        instr = Instruction(1, "BEQ TARGET")
        instr.mnemonic = "BEQ"
        instr.mode = AddressingMode.RELATIVE
        instr.address = 0x1000
        instr.operand_value = Symbol("TARGET")

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        self.assertEqual(instr.machine_code, [0xF0, 0x03])  # BEQ +3 (to reach 0x1005)

    def test_encode_instruction_branch_out_of_range(self):
        """Test encoding of branch instructions with out-of-range targets."""
        # Set up symbol table with far target
        self.symbol_table.add("FAR_TARGET", 0x2000, 1)

        instr = Instruction(1, "BEQ FAR_TARGET")
        instr.mnemonic = "BEQ"
        instr.mode = AddressingMode.RELATIVE
        instr.address = 0x1000
        instr.operand_value = Symbol("FAR_TARGET")

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertFalse(success)  # Should fail due to range error

    def test_encode_instruction_value_out_of_range(self):
        """Test encoding with values out of range."""
        instr = Instruction(1, "LDA #$100")  # 256 is too big for immediate
        instr.mnemonic = "LDA"
        instr.mode = AddressingMode.IMMEDIATE
        instr.address = 0x1000
        instr.operand_value = Number(0x100)

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertFalse(success)

    def test_encode_instruction_undefined_symbol(self):
        """Test encoding with undefined symbol."""
        instr = Instruction(1, "LDA UNDEFINED")
        instr.mnemonic = "LDA"
        instr.mode = AddressingMode.ABSOLUTE
        instr.address = 0x1000
        instr.operand_value = Symbol("UNDEFINED")

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertFalse(success)

    def test_branch_mnemonics_property(self):
        """Test that branch mnemonics are correctly defined."""
        expected_branches = {"BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC", "BVS", "BRA"}
        self.assertEqual(set(self.cpu_profile.branch_mnemonics), expected_branches)

    def test_opcodes_property(self):
        """Test that opcodes property returns the correct opcode table."""
        self.assertEqual(self.cpu_profile.opcodes, OPCODES)

    def test_addressing_modes_enum_property(self):
        """Test that addressing_modes_enum property returns the correct enum."""
        self.assertEqual(self.cpu_profile.addressing_modes_enum, AddressingMode)


if __name__ == '__main__':
    unittest.main()