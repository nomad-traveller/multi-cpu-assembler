#!/usr/bin/env python3

import unittest
import sys
import os
from unittest.mock import patch
from io import StringIO

# Add the compiler directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'compiler'))

from main import CPUProfileFactory, main
from core.diagnostics import Diagnostics
from core.assembler import Assembler
from core.symbol_table import SymbolTable
from core.program import Program
from core.parser import Parser


class TestEndToEnd6800(unittest.TestCase):
    """End-to-end tests for 6800 assembly with JSON profile"""

    def setUp(self):
        """Set up test fixtures"""
        self.diagnostics = Diagnostics()
        self.factory = CPUProfileFactory()

    def test_simple_6800_assembly(self):
        """Test assembling a simple 6800 program"""
        # Create a simple assembly program
        assembly_code = """
        .ORG $8000
        LDAA #$FF
        STAA $0200
        NOP
        CLR $0200
        """
        
        # Write to a temporary file
        test_file = "/tmp/test_6800.s"
        with open(test_file, "w") as f:
            f.write(assembly_code)
        
        try:
            # Create assembler with 6800 profile
            profile = self.factory.create_profile("6800", self.diagnostics)
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
            self.assertFalse(self.diagnostics.has_errors(), f"Should have no errors: {self.diagnostics._error_count}")
            
            # Check that we got some machine code
            self.assertIsNotNone(program)
            
            # Collect machine code from all instructions
            machine_code = []
            for instr in program.instructions:
                if instr.machine_code:
                    machine_code.extend(instr.machine_code)
            
            self.assertGreater(len(machine_code), 0, "Should generate machine code")
            
            # Check that we have reasonable machine code (exact bytes depend on 6800 opcodes)
            # Should have machine code for LDAA #$FF, STAA $0200, NOP, CLR $0200
            self.assertGreaterEqual(len(machine_code), 4, "Should generate at least 4 bytes of machine code")
        
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_6800_addressing_modes(self):
        """Test various 6800 addressing modes"""
        assembly_code = """
        .ORG $0000
        
        ; Immediate addressing
        LDAA #$42
        
        ; Extended addressing  
        STAA $1234
        
        ; Direct addressing (zero page equivalent)
        LDAB $00
        
        ; Implied addressing
        NOP
        
        ; Inherent addressing
        NOP
        """
        
        test_file = "/tmp/test_6800_modes.s"
        with open(test_file, "w") as f:
            f.write(assembly_code)
        
        try:
            profile = self.factory.create_profile("6800", self.diagnostics)
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

    def test_6800_with_labels(self):
        """Test 6800 assembly with labels and symbols"""
        assembly_code = """
        .ORG $8000
        
        START:  LDAA #$01
                STAA $0200
                LDX #$08
        
        LOOP:   DEX
                BNE LOOP
                CLR $0200
        """
        
        test_file = "/tmp/test_6800_labels.s"
        with open(test_file, "w") as f:
            f.write(assembly_code)
        
        try:
            profile = self.factory.create_profile("6800", self.diagnostics)
            symbol_table = SymbolTable(self.diagnostics)
            parser = Parser(profile, self.diagnostics)
            program = Program(symbol_table)
            assembler = Assembler(profile, symbol_table, self.diagnostics)
            
            # Parse the file
            parser.parse_source_file(test_file, program)
            
            # Assemble the program
            success = assembler.assemble(program, 0x8000)
            
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

    def test_cli_integration_6800(self):
        """Test CLI integration with 6800"""
        assembly_code = ".ORG $0000\nLDAA #$FF\nNOP\nCLR $0000\n"
        test_file = "/tmp/test_cli_6800.s"
        output_file = "/tmp/test_cli_6800.bin"
        
        with open(test_file, "w") as f:
            f.write(assembly_code)
        
        try:
            # Mock sys.argv for CLI testing
            test_args = ["main.py", test_file, "-o", output_file, "--cpu", "6800"]
            
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
            
            # Should contain machine code for LDAA #$FF, NOP, CLR $0000
            # Exact bytes depend on 6800 opcodes
            self.assertGreater(len(binary_data), 0, "Binary should contain machine code")
        
        finally:
            for f in [test_file, output_file]:
                if os.path.exists(f):
                    os.remove(f)

    def test_6800_error_handling(self):
        """Test error handling with invalid 6800 code"""
        assembly_code = """
        .ORG $0000
        LDAA #$1234  ; Immediate value too large for 8-bit
        INVALID_OPCODE ; Invalid instruction
        """
        
        test_file = "/tmp/test_6800_errors.s"
        with open(test_file, "w") as f:
            f.write(assembly_code)
        
        try:
            profile = self.factory.create_profile("6800", self.diagnostics)
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