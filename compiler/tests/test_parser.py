import unittest
from unittest.mock import MagicMock

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

from core.parser import Parser
from cpu_profile_base import CPUProfile
from cpu_profiles.c6502.opcodes_65C02 import AddressingMode
from core.diagnostics import Diagnostics
from core.instruction import Instruction

class MockCPUProfile(CPUProfile):
    """
    A concrete, predictable mock CPU profile for testing the parser.
    Instead of using MagicMock, this provides stable behavior.
    """
    def __init__(self, diagnostics):
        self.diagnostics = diagnostics

    def parse_instruction(self, instruction, parser): # Corrected line
        if not instruction.operand_str:
            instruction.mode = AddressingMode.IMPLIED
        elif instruction.operand_str.startswith('#'):
            instruction.mode = AddressingMode.IMMEDIATE
        else:
            instruction.mode = AddressingMode.ABSOLUTE

    def parse_directive(self, instruction, parser):
        """Simulates parsing a directive."""
        # This logic is simple for the test; a real profile is more complex.
        if instruction.operand_str:
            instruction.operand_value = parser.parse_operand_list(instruction.operand_str)

    # Implement abstract methods with dummy implementations
    @property
    def opcodes(self): return {}
    @property
    def branch_mnemonics(self): return set()
    @property
    def addressing_modes_enum(self): return AddressingMode
    def parse_addressing_mode(self, operand_str): pass
    def get_opcode_details(self, instruction, symbol_table): pass
    def encode_instruction(self, instruction, symbol_table): pass


class TestParser(unittest.TestCase):
    """
    A robust, data-driven test suite for the Parser class.
    It tests the public behavior (input string -> Instruction object)
    rather than the internal implementation details.
    """

    def setUp(self):
        """Set up a new Parser instance for each test."""
        self.diagnostics = MagicMock(spec=Diagnostics)
        self.diagnostics.logger = MagicMock()
        self.cpu_profile = MockCPUProfile(self.diagnostics)
        self.parser = Parser(self.cpu_profile, self.diagnostics)

    def test_parser_with_various_inputs(self):
        """
        Tests the parser against a comprehensive list of assembly code lines.
        This data-driven approach makes it easy to add new test cases.
        """
        test_cases = {
            # Test Case Name: (input_line, expected_properties_dict)
            "Implied Instruction": ("  NOP  ; do nothing", {"mnemonic": "NOP", "operand_str": None, "mode": AddressingMode.IMPLIED}),
            "Immediate Instruction": ("LDA #$10", {"mnemonic": "LDA", "operand_str": "#$10", "mode": AddressingMode.IMMEDIATE}),
            "Label Only": ("MY_LABEL:", {"label": "MY_LABEL", "mnemonic": None, "directive": None}),
            "Label with Instruction": ("LOOP: LDA #$FF", {"label": "LOOP", "mnemonic": "LDA", "operand_str": "#$FF"}),
            "EQU Directive": ("MY_CONST EQU 100", {"label": "MY_CONST", "directive": "EQU", "operand_str": "100"}),
            ".ORG Directive": (".ORG $C000", {"directive": ".ORG", "operand_str": "$C000"}),
            "Label with .BYTE Directive": ("DATA: .BYTE $10, $20", {"label": "DATA", "directive": ".BYTE", "operand_str": "$10, $20"}),
            "Absolute Instruction": ("JMP START", {"mnemonic": "JMP", "operand_str": "START", "mode": AddressingMode.ABSOLUTE}),
        }

        for name, (line, expected) in test_cases.items():
            with self.subTest(name=name):
                # --- Act ---
                instr = self.parser.parse_line(line, 1)

                # --- Assert ---
                self.assertIsNotNone(instr, f"Parser returned None for a valid line: '{line}'")
                
                for prop, expected_value in expected.items():
                    actual_value = getattr(instr, prop)
                    self.assertEqual(actual_value, expected_value,
                                     f"Property '{prop}' failed for test '{name}'. Expected: {expected_value}, Got: {actual_value}")

    def test_parser_handles_invalid_and_empty_lines(self):
        """
        Tests that the parser correctly returns None for invalid or empty lines.
        """
        test_cases = {
            "Empty Line": "",
            "Whitespace Only": "    \t ",
            "Comment Only": "; this is a comment",
            "Whitespace and Comment": "  ; another comment",
        }

        for name, line in test_cases.items():
            with self.subTest(name=name):
                instr = self.parser.parse_line(line, 1)
                self.assertIsNone(instr, f"Parser should return None for line: '{line}'")

    def test_parser_reports_errors(self):
        """
        Tests that the parser correctly identifies syntax errors and reports them.
        """
        test_cases = {
            # Test Case Name: (input_line, expected_error_message_part)
            "Invalid EQU Syntax": ("MY_LABEL: MY_CONST EQU 100", "Cannot have a colon-terminated label and an EQU"),
        }

        for name, (line, error_part) in test_cases.items():
            with self.subTest(name=name):
                # Reset the mock for each subtest
                self.diagnostics.reset_mock()

                # --- Act ---
                instr = self.parser.parse_line(line, 1)

                # --- Assert ---
                self.assertIsNone(instr, f"Parser should have failed for line: '{line}'")
                self.diagnostics.error.assert_called_once()
                # Check that the error message contains the expected text
                call_args, _ = self.diagnostics.error.call_args
                self.assertIn(error_part, call_args[1])


if __name__ == '__main__':
    unittest.main()