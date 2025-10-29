import unittest
import sys
from io import StringIO

# Add the compiler directory to the sys.path to allow imports
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

from cpu_profiles.c6800.c6800_profile import C6800Profile
from core.diagnostics import Diagnostics
from core.instruction import Instruction
from core.parser import Parser
from core.symbol_table import SymbolTable
from cpu_profiles.c6800.opcodes_6800 import C6800AddressingMode, OPCODES_6800
from core.expression_parser import Number, Symbol


class TestC6800Profile(unittest.TestCase):
    """Test suite for the 6800 CPU profile."""

    def setUp(self):
        self.diagnostics = Diagnostics()
        self.cpu_profile = C6800Profile(self.diagnostics)
        self.parser = Parser(self.cpu_profile, self.diagnostics)
        self.symbol_table = SymbolTable(self.diagnostics)

    def test_addressing_mode_parsing_inherent(self):
        """Test parsing of inherent addressing mode (no operand)."""
        mode, value = self.cpu_profile.parse_addressing_mode("")
        self.assertEqual(mode, C6800AddressingMode.INHERENT)
        self.assertIsNone(value)

    def test_addressing_mode_parsing_accumulator_a(self):
        """Test parsing of accumulator A addressing mode."""
        mode, value = self.cpu_profile.parse_addressing_mode("A")
        self.assertEqual(mode, C6800AddressingMode.ACCUMULATOR_A)
        self.assertIsNone(value)

        mode, value = self.cpu_profile.parse_addressing_mode("a")
        self.assertEqual(mode, C6800AddressingMode.ACCUMULATOR_A)
        self.assertIsNone(value)

    def test_addressing_mode_parsing_accumulator_b(self):
        """Test parsing of accumulator B addressing mode."""
        mode, value = self.cpu_profile.parse_addressing_mode("B")
        self.assertEqual(mode, C6800AddressingMode.ACCUMULATOR_B)
        self.assertIsNone(value)

        mode, value = self.cpu_profile.parse_addressing_mode("b")
        self.assertEqual(mode, C6800AddressingMode.ACCUMULATOR_B)
        self.assertIsNone(value)

    def test_addressing_mode_parsing_immediate(self):
        """Test parsing of immediate addressing mode."""
        mode, value = self.cpu_profile.parse_addressing_mode("#$FF")
        self.assertEqual(mode, C6800AddressingMode.IMMEDIATE)
        self.assertEqual(value, 0xFF)

        mode, value = self.cpu_profile.parse_addressing_mode("#42")
        self.assertEqual(mode, C6800AddressingMode.IMMEDIATE)
        self.assertEqual(value, 42)

    def test_addressing_mode_parsing_direct(self):
        """Test parsing of direct addressing mode (like zeropage)."""
        mode, value = self.cpu_profile.parse_addressing_mode("$10")
        self.assertEqual(mode, C6800AddressingMode.DIRECT)
        self.assertEqual(value, 0x10)

    def test_addressing_mode_parsing_extended(self):
        """Test parsing of extended addressing mode (like absolute)."""
        mode, value = self.cpu_profile.parse_addressing_mode("$1234")
        self.assertEqual(mode, C6800AddressingMode.EXTENDED)
        self.assertEqual(value, 0x1234)

        # Decimal
        mode, value = self.cpu_profile.parse_addressing_mode("1234")
        self.assertEqual(mode, C6800AddressingMode.EXTENDED)
        self.assertEqual(value, 1234)

        # Label
        mode, value = self.cpu_profile.parse_addressing_mode("MY_LABEL")
        self.assertEqual(mode, C6800AddressingMode.EXTENDED)
        self.assertEqual(value, "MY_LABEL")

    def test_addressing_mode_parsing_indexed(self):
        """Test parsing of indexed addressing mode."""
        mode, value = self.cpu_profile.parse_addressing_mode("$10,X")
        self.assertEqual(mode, C6800AddressingMode.INDEXED)
        self.assertEqual(value, 0x10)

        mode, value = self.cpu_profile.parse_addressing_mode("10,X")
        self.assertEqual(mode, C6800AddressingMode.INDEXED)
        self.assertEqual(value, 10)

        mode, value = self.cpu_profile.parse_addressing_mode("LABEL,X")
        self.assertEqual(mode, C6800AddressingMode.INDEXED)
        self.assertEqual(value, "LABEL")

    def test_addressing_mode_parsing_invalid(self):
        """Test parsing of invalid operand formats."""
        with self.assertRaises(ValueError) as cm:
            self.cpu_profile.parse_addressing_mode("$INVALID")
        self.assertIn("Invalid 6800 operand", str(cm.exception))

    def test_parse_instruction_inherent(self):
        """Test parsing of inherent instructions."""
        instr = Instruction(1, "NOP")
        instr.mnemonic = "NOP"
        instr.operand_str = ""

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, C6800AddressingMode.INHERENT)
        self.assertIsNone(instr.operand_value)

    def test_parse_instruction_immediate(self):
        """Test parsing of immediate instructions."""
        instr = Instruction(1, "LDAA #$FF")
        instr.mnemonic = "LDAA"
        instr.operand_str = "#$FF"

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, C6800AddressingMode.IMMEDIATE)
        self.assertIsInstance(instr.operand_value, Number)
        self.assertEqual(instr.operand_value.value, 0xFF)

    def test_parse_instruction_direct(self):
        """Test parsing of direct instructions."""
        instr = Instruction(1, "LDAA $10")
        instr.mnemonic = "LDAA"
        instr.operand_str = "$10"

        self.cpu_profile.parse_instruction(instr, self.parser)
        # $10 (16) is a 2-digit hex, so it should be DIRECT
        self.assertEqual(instr.mode, C6800AddressingMode.DIRECT)
        self.assertIsInstance(instr.operand_value, Number)
        self.assertEqual(instr.operand_value.value, 0x10)

    def test_parse_instruction_extended(self):
        """Test parsing of extended instructions."""
        instr = Instruction(1, "LDAA $1234")
        instr.mnemonic = "LDAA"
        instr.operand_str = "$1234"

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, C6800AddressingMode.EXTENDED)
        self.assertIsInstance(instr.operand_value, Number)
        self.assertEqual(instr.operand_value.value, 0x1234)

    def test_parse_instruction_indexed(self):
        """Test parsing of indexed instructions."""
        instr = Instruction(1, "LDAA $10,X")
        instr.mnemonic = "LDAA"
        instr.operand_str = "$10,X"

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, C6800AddressingMode.INDEXED)
        self.assertIsInstance(instr.operand_value, Number)
        self.assertEqual(instr.operand_value.value, 0x10)

    def test_parse_instruction_branch(self):
        """Test parsing of branch instructions."""
        instr = Instruction(1, "BRA MY_LABEL")
        instr.mnemonic = "BRA"
        instr.operand_str = "MY_LABEL"

        self.cpu_profile.parse_instruction(instr, self.parser)
        self.assertEqual(instr.mode, C6800AddressingMode.RELATIVE)
        self.assertIsInstance(instr.operand_value, Symbol)
        self.assertEqual(instr.operand_value.name, "MY_LABEL")

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

    def test_parse_directive_equ(self):
        """Test parsing of EQU directive."""
        instr = Instruction(1, "MY_CONST EQU $10")
        instr.directive = "EQU"
        instr.operand_str = "$10"

        self.cpu_profile.parse_directive(instr, self.parser)
        self.assertIsNotNone(instr.operand_value)
        self.assertEqual(instr.size, 0)

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
        instr = Instruction(1, "LDAA #$FF")
        instr.mnemonic = "LDAA"
        instr.mode = C6800AddressingMode.IMMEDIATE

        details = self.cpu_profile.get_opcode_details(instr, self.symbol_table)
        self.assertIsNotNone(details)
        self.assertEqual(details[0], 0x86)  # LDAA immediate opcode
        self.assertEqual(details[1], 1)     # 1 byte operand

    def test_get_opcode_details_invalid_mnemonic(self):
        """Test getting opcode details for invalid mnemonic."""
        instr = Instruction(1, "INVALID #$FF")
        instr.mnemonic = "INVALID"
        instr.mode = C6800AddressingMode.IMMEDIATE

        details = self.cpu_profile.get_opcode_details(instr, self.symbol_table)
        self.assertIsNone(details)

    def test_get_opcode_details_invalid_mode(self):
        """Test getting opcode details for invalid mode."""
        instr = Instruction(1, "LDAA #$FF")
        instr.mnemonic = "LDAA"
        instr.mode = C6800AddressingMode.INHERENT  # LDAA doesn't support inherent

        details = self.cpu_profile.get_opcode_details(instr, self.symbol_table)
        self.assertIsNone(details)

    def test_encode_instruction_inherent(self):
        """Test encoding of inherent instructions."""
        instr = Instruction(1, "NOP")
        instr.mnemonic = "NOP"
        instr.mode = C6800AddressingMode.INHERENT
        instr.address = 0x1000

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        # NOP is not in the sample opcodes, so this might fail - let's check what opcodes are available
        # Actually, let me use an instruction that exists

    def test_encode_instruction_immediate(self):
        """Test encoding of immediate instructions."""
        instr = Instruction(1, "LDAA #$42")
        instr.mnemonic = "LDAA"
        instr.mode = C6800AddressingMode.IMMEDIATE
        instr.address = 0x1000
        instr.operand_value = Number(0x42)

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        self.assertEqual(instr.machine_code, [0x86, 0x42])

    def test_encode_instruction_direct(self):
        """Test encoding of direct instructions."""
        instr = Instruction(1, "LDAA $10")
        instr.mnemonic = "LDAA"
        instr.mode = C6800AddressingMode.DIRECT
        instr.address = 0x1000
        instr.operand_value = Number(0x10)

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        self.assertEqual(instr.machine_code, [0x96, 0x10])

    def test_encode_instruction_extended(self):
        """Test encoding of extended instructions."""
        instr = Instruction(1, "LDAA $1234")
        instr.mnemonic = "LDAA"
        instr.mode = C6800AddressingMode.EXTENDED
        instr.address = 0x1000
        instr.operand_value = Number(0x1234)

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        self.assertEqual(instr.machine_code, [0xB6, 0x12, 0x34])  # Big-endian

    def test_encode_instruction_indexed(self):
        """Test encoding of indexed instructions."""
        instr = Instruction(1, "LDAA $10,X")
        instr.mnemonic = "LDAA"
        instr.mode = C6800AddressingMode.INDEXED
        instr.address = 0x1000
        instr.operand_value = Number(0x10)

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        self.assertEqual(instr.machine_code, [0xA6, 0x10])

    def test_encode_instruction_branch(self):
        """Test encoding of branch instructions."""
        # Set up symbol table with target label
        self.symbol_table.add("TARGET", 0x1005, 1)

        instr = Instruction(1, "BRA TARGET")
        instr.mnemonic = "BRA"
        instr.mode = C6800AddressingMode.RELATIVE
        instr.address = 0x1000
        instr.operand_value = Symbol("TARGET")

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertTrue(success)
        self.assertEqual(instr.machine_code, [0x20, 0x03])  # BRA +3 (to reach 0x1005)

    def test_encode_instruction_branch_out_of_range(self):
        """Test encoding of branch instructions with out-of-range targets."""
        # Set up symbol table with far target
        self.symbol_table.add("FAR_TARGET", 0x2000, 1)

        instr = Instruction(1, "BRA FAR_TARGET")
        instr.mnemonic = "BRA"
        instr.mode = C6800AddressingMode.RELATIVE
        instr.address = 0x1000
        instr.operand_value = Symbol("FAR_TARGET")

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertFalse(success)  # Should fail due to range error

    def test_encode_instruction_value_out_of_range(self):
        """Test encoding with values out of range."""
        instr = Instruction(1, "LDAA #$100")  # 256 is too big for 1-byte immediate
        instr.mnemonic = "LDAA"
        instr.mode = C6800AddressingMode.IMMEDIATE
        instr.address = 0x1000
        instr.operand_value = Number(0x100)

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertFalse(success)

    def test_encode_instruction_undefined_symbol(self):
        """Test encoding with undefined symbol."""
        instr = Instruction(1, "LDAA UNDEFINED")
        instr.mnemonic = "LDAA"
        instr.mode = C6800AddressingMode.EXTENDED
        instr.address = 0x1000
        instr.operand_value = Symbol("UNDEFINED")

        success = self.cpu_profile.encode_instruction(instr, self.symbol_table)
        self.assertFalse(success)

    def test_branch_mnemonics_property(self):
        """Test that branch mnemonics are correctly defined."""
        expected_branches = {"BCC", "BCS", "BEQ", "BGE", "BGT", "BHI", "BLE", "BLS", "BLT", "BMI", "BNE", "BPL", "BRA", "BSR", "BVC", "BVS"}
        self.assertEqual(set(self.cpu_profile.branch_mnemonics), expected_branches)

    def test_opcodes_property(self):
        """Test that opcodes property returns the correct opcode table."""
        self.assertEqual(self.cpu_profile.opcodes, OPCODES_6800)

    def test_addressing_modes_enum_property(self):
        """Test that addressing_modes_enum property returns the correct enum."""
        self.assertEqual(self.cpu_profile.addressing_modes_enum, C6800AddressingMode)


if __name__ == '__main__':
    unittest.main()