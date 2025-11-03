#!/usr/bin/env python3

import unittest
import sys
import os
from unittest.mock import patch
from io import StringIO

# Add the tests directory to the path to import modules
sys.path.insert(0, os.path.dirname(__file__))

from main import CPUProfileFactory, main
from diagnostics import Diagnostics
from assembler import Assembler
from symbol_table import SymbolTable
from program import Program
from parser import Parser


class TestEndToEnd65C02(unittest.TestCase):
    """End-to-end tests for 65C02 assembly with JSON profile"""

    def setUp(self):
        """Set up test fixtures"""
        self.diagnostics = Diagnostics()
        self.factory = CPUProfileFactory()

    def test_simple_65c02_assembly(self):
        """Test assembling a simple 65C02 program"""
        # Create a simple assembly program
        assembly_code = """
        .ORG $8000
        LDA #$FF
        STA $0200
        NOP
        BRK
        """
        
        # Write to a temporary file
        test_file = "/tmp/test_65c02.s"
        with open(test_file, "w") as f:
            f.write(assembly_code)
        
        try:
            # Create assembler with 65C02 profile
            profile = self.factory.create_profile("65c02", self.diagnostics)
            symbol_table = SymbolTable(self.diagnostics)
            parser = Parser(profile, self.diagnostics)
            program = Program(symbol_table)
            assembler = Assembler(profile, symbol_table, self.diagnostics)
            
            # Parse the file
            parser.parse_source_file(test_file, program)
            
            # Assemble the program
            success = assembler.assemble(program, 0x8000)
            
            # Check that assembly succeeded
            self.assertTrue(success, "Assembly should succeed")
            self.assertFalse(self.diagnostics.has_errors(), f"Should have no errors, but got: {self.diagnostics._error_count}")
            
            # Check that we got some machine code
            self.assertIsNotNone(program)
            
            # Collect machine code from all instructions
            machine_code = []
            for instr in program.instructions:
                if instr.machine_code:
                    machine_code.extend(instr.machine_code)
            
            self.assertGreater(len(machine_code), 0, "Should generate machine code")
            
            # Check specific instructions
            # LDA #$FF should be A9 FF
            # STA $0200 should be 8D 00 02  
            # NOP should be EA
            # BRK should be 00
            expected_bytes = [0xA9, 0xFF, 0x8D, 0x00, 0x02, 0xEA, 0x00]
            
            # Check that the expected bytes are present (might have padding)
            for i, expected_byte in enumerate(expected_bytes):
                if i < len(machine_code):
                    self.assertEqual(machine_code[i], expected_byte, 
                                   f"Byte {i} should be {expected_byte:02X}, got {machine_code[i]:02X}")
        
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_65c02_addressing_modes(self):
        """Test various 65C02 addressing modes"""
        assembly_code = """
        .ORG $0000
        
        ; Immediate addressing
        LDA #$42
        
        ; Absolute addressing  
        STA $1234
        
        ; Zero page addressing
        LDX $00
        
        ; Implied addressing
        NOP
        """
        
        test_file = "/tmp/test_65c02_modes.s"
        with open(test_file, "w") as f:
            f.write(assembly_code)
        
        try:
            profile = self.factory.create_profile("65c02", self.diagnostics)
            symbol_table = SymbolTable(self.diagnostics)
            parser = Parser(profile, self.diagnostics)
            program = Program(symbol_table)
            assembler = Assembler(profile, symbol_table, self.diagnostics)
            
            # Parse the file
            parser.parse_source_file(test_file, program)
            
            # Assemble the program
            success = assembler.assemble(program, 0x0000)
            
            self.assertTrue(success, "Assembly with different addressing modes should succeed")
            self.assertFalse(self.diagnostics.has_errors(), f"Should have no errors: {self.diagnostics._error_count}")
        
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_65c02_with_labels(self):
        """Test 65C02 assembly with labels and symbols"""
        assembly_code = """
        .ORG $8000
        
        START:  LDA #$01
                STA $0200
                LDX #$08
        
        LOOP:   DEX
                BNE LOOP
                BRK
        """
        
        test_file = "/tmp/test_65c02_labels.s"
        with open(test_file, "w") as f:
            f.write(assembly_code)
        
        try:
            profile = self.factory.create_profile("65c02", self.diagnostics)
            symbol_table = SymbolTable(self.diagnostics)
            parser = Parser(profile, self.diagnostics)
            program = Program(symbol_table)
            assembler = Assembler(profile, symbol_table, self.diagnostics)
            
            # Parse the file
            parser.parse_source_file(test_file, program)
            
            # Assemble the program
            success = assembler.assemble(program, 0x0000)
            
            self.assertTrue(success, "Assembly with labels should succeed")
            self.assertFalse(self.diagnostics.has_errors(), f"Should have no errors: {self.diagnostics._error_count}")
            
            # Check that symbols were resolved
            self.assertIsNotNone(program.symbol_table)
            
            # Should have START and LOOP symbols
            symbols = program.symbol_table._symbols
            self.assertIn("START", symbols)
            self.assertIn("LOOP", symbols)
        
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_cli_integration_65c02(self):
        """Test CLI integration with 65C02"""
        assembly_code = ".ORG $0000\nLDA #$FF\nNOP\nBRK\n"
        test_file = "/tmp/test_cli_65c02.s"
        output_file = "/tmp/test_cli_65c02.bin"
        
        with open(test_file, "w") as f:
            f.write(assembly_code)
        
        try:
            # Mock sys.argv for CLI testing
            test_args = ["main.py", test_file, "-o", output_file, "--cpu", "65c02"]
            
            with patch.object(sys, 'argv', test_args):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    try:
                        main()
                    except SystemExit:
                        pass  # main() calls sys.exit()
            
            # Check that output file was created
            self.assertTrue(os.path.exists(output_file), "Output binary file should be created")
            
            # Check that binary has expected content
            with open(output_file, "rb") as f:
                binary_data = f.read()
            
            # Should contain: A9 FF EA 00 (LDA #$FF, NOP, BRK)
            expected = [0xA9, 0xFF, 0xEA, 0x00]
            actual = list(binary_data)
            
            self.assertEqual(len(actual), len(expected), f"Binary length mismatch: expected {len(expected)}, got {len(actual)}")
            for i, (exp, act) in enumerate(zip(expected, actual)):
                self.assertEqual(act, exp, f"Byte {i} mismatch: expected {exp:02X}, got {act:02X}")
        
        finally:
            for f in [test_file, output_file]:
                if os.path.exists(f):
                    os.remove(f)

    def test_65c02_error_handling(self):
        """Test error handling with invalid 65C02 code"""
        assembly_code = """
        .ORG $0000
        LDA #$1234  ; Immediate value too large for 8-bit
        INVALID_OPCODE ; Invalid instruction
        """
        
        test_file = "/tmp/test_65c02_errors.s"
        with open(test_file, "w") as f:
            f.write(assembly_code)
        
        try:
            profile = self.factory.create_profile("65c02", self.diagnostics)
            symbol_table = SymbolTable(self.diagnostics)
            parser = Parser(profile, self.diagnostics)
            program = Program(symbol_table)
            assembler = Assembler(profile, symbol_table, self.diagnostics)
            
            # Parse the file
            parser.parse_source_file(test_file, program)
            
            # Assemble the program
            success = assembler.assemble(program, 0x0000)
            
            # Assembly should fail due to errors
            self.assertFalse(success, "Assembly with errors should fail")
            self.assertTrue(self.diagnostics.has_errors(), "Should have errors reported")
        
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


if __name__ == '__main__':
    unittest.main()