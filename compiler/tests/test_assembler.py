import re
import unittest
import os
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

# Add the compiler directory to the sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

# Import classes from your project
from main import Instruction, SymbolTable, Program, Parser, Assembler, SUPPORTED_CPUS
from cpu_profiles import CPUProfile
from cpu_profiles.c6502.c6502_profile import C6502Profile
from cpu_profiles.c6800.c6800_profile import C6800Profile
from core.diagnostics import Diagnostics
from cpu_profiles.c6502.opcodes_65C02 import AddressingMode
from cpu_profiles.c6800.opcodes_6800 import C6800AddressingMode
from core.emitter import Emitter
from core.expression_parser import Number

# --- Mock CPU Profile for Generic Parser/Assembler Testing ---
class MockCPUProfile(CPUProfile):
    """A minimal CPU profile for testing generic Parser/Assembler logic."""
    def __init__(self):
        self._opcodes = {
            "LDA": {
                AddressingMode.IMMEDIATE: [0xA9, 1, {}, ""],
                AddressingMode.ABSOLUTE: [0xAD, 2, {}, ""],
            },
            "JMP": {
                AddressingMode.ABSOLUTE: [0x4C, 2, {}, ""],
                AddressingMode.RELATIVE: [0x80, 1, {}, ""],
            },
            "NOP": {
                AddressingMode.IMPLIED: [0xEA, 0, {}, ""],
            }
        }
        self._branch_mnemonics = {"JMP"} # Mock JMP as a branch for relative testing
        self._addressing_modes_enum = AddressingMode

    @property
    def opcodes(self): return self._opcodes
    @property
    def branch_mnemonics(self): return self._branch_mnemonics
    @property
    def addressing_modes_enum(self): return self._addressing_modes_enum

    def parse_addressing_mode(self, operand_str):
        operand_str = operand_str.strip().upper()
        if operand_str.startswith('#'):
            val_str = operand_str[1:]
            if val_str.startswith('$'):
                # It's a hex value
                return (AddressingMode.IMMEDIATE, int(val_str[1:], 16))
            elif val_str.isdigit():
                # It's a decimal value
                return (AddressingMode.IMMEDIATE, int(val_str))
            else:
                # It must be a symbol
                return (AddressingMode.IMMEDIATE, val_str)
        if re.match(r'^\$[0-9A-F]{4}$', operand_str):
            return (AddressingMode.ABSOLUTE, int(operand_str[1:], 16))
        if re.match(r'^[A-Z_][A-Z0-9_]*$', operand_str): # Assume labels are absolute by default
            return (AddressingMode.ABSOLUTE, operand_str)
        return (AddressingMode.IMPLIED, None) # Fallback for NOP or similar

    def parse_instruction(self, instruction, parser):
        mode, value = self.parse_addressing_mode(instruction.operand_str or "")
        instruction.mode = mode
        instruction.operand_value = value
        if instruction.mnemonic in self.branch_mnemonics:
            instruction.mode = AddressingMode.RELATIVE # Force relative for JMP in mock

    def parse_directive(self, instruction, parser):
        mnemonic = instruction.directive
        operand_str = instruction.operand_str
        if mnemonic == ".ORG":
            instruction.operand_value = parser.parse_operand_list(operand_str)[0]
        elif mnemonic == ".BYTE":
            instruction.operand_value = parser.parse_operand_list(operand_str)
            instruction.size = len(instruction.operand_value)
        elif mnemonic == ".WORD":
            instruction.operand_value = parser.parse_operand_list(operand_str)
            instruction.size = len(instruction.operand_value) * 2
        elif mnemonic == "EQU":
            instruction.operand_value = parser.parse_operand_list(operand_str)[0]
            instruction.size = 0
        else:
            raise ValueError(f"Unknown directive: {mnemonic}")

    def get_opcode_details(self, instruction, symbol_table):
        mnemonic = instruction.mnemonic
        mode = instruction.mode
        if mnemonic not in self.opcodes: return None
        if mode not in self.opcodes[mnemonic]: return None
        return self.opcodes[mnemonic][mode]

    def encode_instruction(self, instruction, symbol_table):
        value = instruction.operand_value
        if isinstance(value, str):
            val = symbol_table.resolve(value)
            if val is None: raise ValueError(f"Undefined symbol '{value}'")
        else: val = value if value is not None else 0

        details = self.get_opcode_details(instruction, symbol_table)
        opcode, operand_size, _, _ = details

        if instruction.mode == AddressingMode.IMPLIED:
            instruction.machine_code = [opcode]
        elif operand_size == 1:
            if instruction.mode == AddressingMode.RELATIVE:
                offset = val - (instruction.address + 2)
                if not -128 <= offset <= 127: raise ValueError(f"Branch offset out of range: {offset}")
                instruction.machine_code = [opcode, offset & 0xFF]
            else: instruction.machine_code = [opcode, val & 0xFF]
        elif operand_size == 2:
            instruction.machine_code = [opcode, val & 0xFF, (val >> 8) & 0xFF]
        else: instruction.machine_code = [opcode]
        return True

# --- Test Cases ---

class TestInstruction(unittest.TestCase):
    def test_validation_mnemonic_and_directive(self):
        diagnostics = Diagnostics(None)
        instr = Instruction(1, "LABEL LDA .ORG")
        instr.mnemonic = "LDA"
        instr.directive = ".ORG"
        self.assertFalse(instr.validate(diagnostics))

    def test_validation_mnemonic_missing_mode(self):
        diagnostics = Diagnostics(None)
        instr = Instruction(1, "LDA $1000")
        instr.mnemonic = "LDA"
        instr.mode = None # Simulate missing mode
        self.assertFalse(instr.validate(diagnostics))

    def test_validation_valid_instruction(self):
        diagnostics = Diagnostics(None)
        instr = Instruction(1, "LDA #$FF")
        instr.mnemonic = "LDA"
        instr.mode = AddressingMode.IMMEDIATE
        self.assertTrue(instr.validate(diagnostics))

    def test_validation_valid_directive(self):
        diagnostics = Diagnostics(None)
        instr = Instruction(1, ".ORG $C000")
        instr.directive = ".ORG"
        self.assertTrue(instr.validate(diagnostics))

class TestSymbolTable(unittest.TestCase):
    def test_add_and_resolve(self):
        diagnostics = Diagnostics(None)
        st = SymbolTable(diagnostics)
        self.assertTrue(st.add("LABEL1", 0x1000, 1))
        self.assertEqual(st.resolve("LABEL1"), 0x1000)

    def test_duplicate_label(self):
        diagnostics = Diagnostics(None)
        st = SymbolTable(diagnostics)
        st.add("LABEL1", 0x1000, 1)
        captured_output = StringIO()
        sys.stdout = captured_output
        self.assertFalse(st.add("LABEL1", 0x2000, 2))
        sys.stdout = sys.__stdout__
        self.assertIn("Duplicate label", captured_output.getvalue())

    def test_resolve_non_existent_label(self):
        diagnostics = Diagnostics(None)
        st = SymbolTable(diagnostics)
        self.assertIsNone(st.resolve("NONEXISTENT"))

class TestParser(unittest.TestCase):
    def setUp(self):
        self.cpu_profile = MockCPUProfile()
        self.diagnostics = Diagnostics(None)
        self.parser = Parser(self.cpu_profile, self.diagnostics)

    def test_empty_line(self):
        self.assertIsNone(self.parser.parse_line("", 1))

    def test_comment_only_line(self):
        self.assertIsNone(self.parser.parse_line("; This is a comment", 1))

    def test_label_only_line(self):
        instr = self.parser.parse_line("MYLABEL:", 1)
        self.assertIsNotNone(instr)
        self.assertEqual(instr.label, "MYLABEL")
        self.assertIsNone(instr.mnemonic)
        self.assertIsNone(instr.directive)

    def test_malformed_operand_list(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = self.parser.parse_operand_list("10, $GG")
        sys.stdout = sys.__stdout__
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Number)
        self.assertEqual(result[0].value, 10)
        self.assertIsNone(result[1])
        self.assertIn("In expression '$GG': Illegal character '$'", captured_output.getvalue())

    def test_directive_with_invalid_operand(self):
        # Mock the CPU profile's parse_directive to raise an error for invalid operand
        self.cpu_profile.parse_directive = MagicMock(side_effect=ValueError("Invalid directive operand"))
        
        # Suppress stdout to keep test output clean
        captured_output = StringIO()
        sys.stdout = captured_output
        instr = self.parser.parse_line(".ORG $GGGG", 1)
        sys.stdout = sys.__stdout__ # Restore stdout

        self.assertIsNone(instr) # Should return None due to validation failure
        self.assertIn("Invalid directive operand", captured_output.getvalue())

    def test_instruction_with_invalid_operand_format(self):
        # Mock the CPU profile's parse_instruction to raise an error for invalid operand
        self.cpu_profile.parse_instruction = MagicMock(side_effect=ValueError("Invalid instruction operand"))
        captured_output = StringIO()
        sys.stdout = captured_output
        instr = self.parser.parse_line("LDA (INVALID)", 1)
        sys.stdout = sys.__stdout__ # Restore stdout
        self.assertIsNone(instr) # Should return None due to validation failure
        self.assertIn("Invalid instruction operand", captured_output.getvalue())

    def test_equ_directive(self):
        instr = self.parser.parse_line("MY_CONST EQU $10", 1)
        self.assertIsNotNone(instr)
        self.assertEqual(instr.label, "MY_CONST")
        self.assertEqual(instr.directive, "EQU")
        # operand_value contains the parsed expression object
        self.assertIsNotNone(instr.operand_value)
        self.assertEqual(instr.size, 0)

class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.cpu_profile = MockCPUProfile()
        self.diagnostics = Diagnostics(None)
        self.symbol_table = SymbolTable(self.diagnostics)
        self.assembler = Assembler(self.cpu_profile, self.symbol_table, self.diagnostics)
        self.program = Program(self.symbol_table)
        self.parser = Parser(self.cpu_profile, self.diagnostics)

    def _assemble_source(self, source_lines, start_address=0x0000, capture_output=None):
        self.program = Program(self.symbol_table) # Reset program for each test
        for i, line in enumerate(source_lines):
            instr = self.parser.parse_line(line, i + 1)
            if instr:
                self.program.add_instruction(instr)
        
        # Redirect stdout if a capture object is provided, otherwise suppress it
        output_capture = capture_output if capture_output is not None else StringIO()
        original_stdout = sys.stdout
        sys.stdout = output_capture
        success = self.assembler.assemble(self.program, start_address)
        sys.stdout = original_stdout # Restore stdout
        return success

    def test_empty_program(self):
        # An empty program should still pass assembly, but generate no code
        success = self._assemble_source([])
        self.assertTrue(success)
        self.assertEqual(len(self.program.instructions), 0)
        # No need to check captured output here, as it's just progress messages

    def test_duplicate_label_pass1(self):
        source = [
            "LABEL: LDA #$FF",
            "LABEL: NOP"
        ]
        captured_output = StringIO()
        success = self._assemble_source(source, capture_output=captured_output)
        self.assertFalse(success)
        # Assert against the captured output for the specific error message
        self.assertIn("Duplicate label 'LABEL'", captured_output.getvalue())

    def test_undefined_symbol_pass2(self):
        source = [
            "LDA UNDEFINED_LABEL"
        ]
        captured_output = StringIO()
        success = self._assemble_source(source, capture_output=captured_output)
        self.assertFalse(success)
        # Assert against the captured output for the specific error message
        self.assertIn("Undefined symbol 'UNDEFINED_LABEL'", captured_output.getvalue())

    def test_branch_out_of_range(self):
        # Mock JMP to be a branch, then place target far away
        source = [
            ".ORG $0100",
            "JMP FAR_AWAY", # This JMP will be at $0100, target at $0200
            ".ORG $0200",
            "FAR_AWAY: NOP"
        ]
        captured_output = StringIO()
        success = self._assemble_source(source, capture_output=captured_output)
        self.assertFalse(success)
        # Assert against the captured output for the specific error message
        self.assertIn("Branch offset out of range", captured_output.getvalue())

    def test_byte_directive_out_of_range(self):
        source = [
            ".BYTE $100" # Value > 255
        ]
        captured_output = StringIO()
        success = self._assemble_source(source, capture_output=captured_output)
        self.assertFalse(success)
        # Assert against the captured output for the specific error message
        self.assertIn("Byte value '256' out of range (0-255)", captured_output.getvalue())

    def test_word_directive_out_of_range(self):
        source = [
            ".WORD $10000" # Value > 65535
        ]
        captured_output = StringIO()
        success = self._assemble_source(source, capture_output=captured_output)
        self.assertFalse(success)
        # Assert against the captured output for the specific error message
        self.assertIn("Word value '65536' out of range (0-65535)", captured_output.getvalue())

    def test_equ_symbol_resolution(self):
        source = [
            "MY_VAL EQU $10",
            "LDA #MY_VAL"
        ]
        success = self._assemble_source(source) # This test expects success, so no need to capture stdout for errors
        self.assertTrue(success)
        self.assertEqual(self.program.symbol_table.resolve("MY_VAL"), 0x10)
        # Find the LDA instruction and check its machine code
        lda_instr = next(i for i in self.program.instructions if i.mnemonic == "LDA")
        self.assertIsNotNone(lda_instr)
        self.assertEqual(lda_instr.machine_code, [0xA9, 0x10])

    def test_unknown_mnemonic_or_mode(self):
        source = [
            "UNKNOWN_MNEMONIC #$FF"
        ]
        captured_output = StringIO()
        success = self._assemble_source(source, capture_output=captured_output)
        self.assertFalse(success)
        # Assert against the captured output for the specific error message
        self.assertIn("Invalid mnemonic 'UNKNOWN_MNEMONIC'", captured_output.getvalue())

    def test_mnemonic_unsupported_mode(self):
        source = [
            "NOP #$FF" # NOP is implied, not immediate
        ]
        captured_output = StringIO()
        success = self._assemble_source(source, capture_output=captured_output)
        self.assertFalse(success)
        # Assert against the captured output for the specific error message
        self.assertIn("Invalid mnemonic 'NOP' or addressing mode 'IMMEDIATE'", captured_output.getvalue())


class TestEmitter(unittest.TestCase):
    def setUp(self):
        self.diagnostics = Diagnostics(None)
        self.symbol_table = SymbolTable(self.diagnostics)
        self.emitter = Emitter(self.diagnostics)
        self.program = Program(self.symbol_table)
        self.test_file = "test_output.bin"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_write_binary_empty_program(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        success = self.emitter.write_binary(self.program, self.test_file)
        sys.stdout = sys.__stdout__
        self.assertTrue(success) # No machine code generated is not an error for emitter, but it prints a message
        self.assertIn("No machine code generated to write.", captured_output.getvalue())
        self.assertFalse(os.path.exists(self.test_file))

    def test_write_binary_with_code(self):
        instr1 = Instruction(1, "LDA #$01")
        instr1.address = 0x1000
        instr1.size = 2
        instr1.machine_code = [0xA9, 0x01]
        self.program.add_instruction(instr1)

        instr2 = Instruction(2, "NOP")
        instr2.address = 0x1002
        instr2.size = 1
        instr2.machine_code = [0xEA]
        self.program.add_instruction(instr2)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        success = self.emitter.write_binary(self.program, self.test_file)
        sys.stdout = sys.__stdout__
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, 'rb') as f:
            content = f.read()
            self.assertEqual(content, b'\xA9\x01\xEA')
        self.assertIn("Machine code written to", captured_output.getvalue())

    @patch('builtins.open', side_effect=IOError("Disk full"))
    def test_write_binary_io_error(self, mock_open):
        instr1 = Instruction(1, "LDA #$01")
        instr1.address = 0x1000
        instr1.size = 2
        instr1.machine_code = [0xA9, 0x01]
        self.program.add_instruction(instr1)

        captured_output = StringIO()
        sys.stdout = captured_output
        success = self.emitter.write_binary(self.program, self.test_file)
        sys.stdout = sys.__stdout__
        self.assertFalse(success)
        self.assertIn("Error writing binary to", captured_output.getvalue())

if __name__ == '__main__':
    unittest.main()