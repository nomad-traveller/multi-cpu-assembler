#!/usr/bin/env python3

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the compiler directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'compiler'))

from core.assembler import Assembler
from core.diagnostics import Diagnostics
from core.symbol_table import SymbolTable
from core.program import Program
from core.instruction import Instruction

class TestAssembler(unittest.TestCase):
    """Unit tests for the Assembler class"""

    def setUp(self):
        """Set up test fixtures"""
        self.diagnostics = Diagnostics()
        self.symbol_table = SymbolTable(self.diagnostics)
        self.program = Program(self.symbol_table)
        
        # Mock the CPU profile to isolate the assembler
        self.mock_profile = MagicMock()
        self.mock_profile.get_instruction_size.return_value = 2 # Assume all instructions are 2 bytes
        self.mock_profile.get_opcode_details.return_value = (0xA9, 1, 2, "")  # opcode, mode, size, flags
        # Mock encode_instruction to set machine_code on the instruction and return True
        def mock_encode_instruction(instr, symbol_table):
            instr.machine_code = [0xEA, 0xEA]  # Set machine code on the instruction
            return True
        self.mock_profile.encode_instruction.side_effect = mock_encode_instruction

        self.assembler = Assembler(self.mock_profile, self.symbol_table, self.diagnostics)

    def test_first_pass_symbol_resolution(self):
        """Test that the first pass correctly resolves symbol addresses"""
        # Create a program with a label
        instr1 = Instruction(1, "START: LDA #$01")
        instr1.label = "START"
        instr1.mnemonic = "LDA"
        instr1.operand_str = "#$01"
        instr2 = Instruction(2, "STA $0200")
        instr2.mnemonic = "STA"
        instr2.operand_str = "$0200"
        self.program.add_instruction(instr1)
        self.program.add_instruction(instr2)

        # Run the first pass
        success = self.assembler._first_pass(self.program, 0x8000)

        self.assertTrue(success, "First pass should succeed")
        self.assertFalse(self.diagnostics.has_errors(), "Should be no errors in first pass")

        # Check if the symbol 'START' was added to the symbol table with the correct address
        start_address = self.symbol_table.resolve("START")
        self.assertIsNotNone(start_address, "Symbol 'START' should be in the symbol table")
        self.assertEqual(start_address, 0x8000, "Symbol 'START' should have the correct address")

        # Check that instruction addresses are set
        self.assertEqual(self.program.instructions[0].address, 0x8000)
        self.assertEqual(self.program.instructions[1].address, 0x8002) # 0x8000 + 2 bytes

    def test_second_pass_machine_code_generation(self):
        """Test that the second pass generates machine code for each instruction"""
        # Prepare a program that has already been through the first pass
        instr1 = Instruction(1, "START: LDA #$01")
        instr1.label = "START"
        instr1.mnemonic = "LDA"
        instr1.operand_str = "#$01"
        instr1.address = 0x8000
        instr1.size = 2
        self.program.add_instruction(instr1)

        # Run the second pass
        success = self.assembler._second_pass(self.program)

        self.assertTrue(success, "Second pass should succeed")
        self.assertFalse(self.diagnostics.has_errors(), "Should be no errors in second pass")

        # Check that encode_instruction was called on the profile
        self.mock_profile.encode_instruction.assert_called_once_with(instr1, self.symbol_table)

        # Check that machine code was attached to the instruction
        self.assertIsNotNone(instr1.machine_code)
        self.assertEqual(instr1.machine_code, [0xEA, 0xEA])

    def test_assemble_full_process(self):
        """Test the full assemble() method orchestrates both passes"""
        # We can use patch to spy on the pass methods
        with patch.object(self.assembler, '_first_pass', wraps=self.assembler._first_pass) as spy_first_pass:
            with patch.object(self.assembler, '_second_pass', wraps=self.assembler._second_pass) as spy_second_pass:
                # Create a simple program
                instr = Instruction(1, "NOP")
                instr.mnemonic = "NOP"
                self.program.add_instruction(instr)

                # Run the full assembly process
                success = self.assembler.assemble(self.program, 0x0000)

                self.assertTrue(success, "Assembly should succeed")
                spy_first_pass.assert_called_once_with(self.program, 0x0000)
                spy_second_pass.assert_called_once_with(self.program)

    def test_duplicate_label_error(self):
        """Test that the first pass fails on duplicate labels"""
        instr1 = Instruction(1, "LOOP: NOP")
        instr1.label = "LOOP"
        instr1.mnemonic = "NOP"
        instr2 = Instruction(2, "LOOP: NOP")
        instr2.label = "LOOP"
        instr2.mnemonic = "NOP"
        self.program.add_instruction(instr1)
        self.program.add_instruction(instr2)

        success = self.assembler._first_pass(self.program, 0x1000)

        self.assertFalse(success, "First pass should fail with duplicate labels")
        self.assertTrue(self.diagnostics.has_errors(), "An error for duplicate label should be reported")

if __name__ == '__main__':
    unittest.main()