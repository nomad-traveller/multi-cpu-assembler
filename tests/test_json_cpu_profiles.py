#!/usr/bin/env python3

import unittest
import json
import os
import sys
from unittest.mock import patch, mock_open, MagicMock

# Add the compiler directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'compiler'))

from cpu_profile_base import ConfigCPUProfile
from main import CPUProfileFactory
from core.diagnostics import Diagnostics


class TestConfigCPUProfile(unittest.TestCase):
    """Test cases for ConfigCPUProfile class"""

    def setUp(self):
        """Set up test fixtures"""
        self.diagnostics = Diagnostics()
        
        # Create a minimal valid JSON profile structure based on the actual format
        self.valid_profile_data = {
            "cpu_info": {
                "name": "65C02",
                "description": "WDC 65C02 microprocessor",
                "endianness": "little"
            },
            "opcodes": {
                "LDA": {
                    "IMMEDIATE": [0xA9, 1, 2, "Load accumulator with immediate value"],
                    "ABSOLUTE": [0xAD, 2, 4, "Load accumulator from absolute address"]
                },
                "STA": {
                    "ABSOLUTE": [0x8D, 2, 4, "Store accumulator to absolute address"]
                },
                "NOP": {
                    "IMPLIED": [0xEA, 0, 2, "No operation"]
                }
            },
            "branch_mnemonics": ["BRA", "BCC", "BCS"],
            "addressing_modes": {
                "IMPLIED": 0,
                "IMMEDIATE": 1,
                "ABSOLUTE": 2,
                "RELATIVE": 3
            },
            "addressing_mode_patterns": [
                {
                    "pattern": "^#(\\$?[0-9A-F]+|[A-Z_][A-Z0-9_]*)$",
                    "mode": "IMMEDIATE",
                    "group_index": 1,
                    "flags": ["IGNORECASE"]
                },
                {
                    "pattern": "^(\\$?[0-9A-F]+)$",
                    "mode": "ABSOLUTE",
                    "group_index": 1,
                    "flags": ["IGNORECASE"]
                },
                {
                    "pattern": "^(BRK|CLC|CLD|CLI|CLV|DEX|DEY|INX|INY|NOP|PHA|PHP|RTI|RTS|SEC|SED|SEI|TAX|TAY|TSX|TXA|TXS|TYA)$",
                    "mode": "IMPLIED",
                    "group_index": None,
                    "flags": ["IGNORECASE"]
                }
            ],
            "directives": {
                "ORG": {"operand_count": 1, "operand_type": "expression"},
                "DB": {"operand_count": "variable", "operand_type": "expression", "size_multiplier": 1}
            },
            "validation_rules": {
                "inherent_only": {
                    "NOP": ["IMPLIED"]
                }
            }
        }

    def test_load_valid_profile(self):
        """Test loading a valid JSON profile"""
        with patch("builtins.open", mock_open(read_data=json.dumps(self.valid_profile_data))):
            profile = ConfigCPUProfile(self.diagnostics, "test_profile.json")
            
        self.assertEqual(profile.cpu_info["name"], "65C02")
        self.assertEqual(profile.cpu_info["description"], "WDC 65C02 microprocessor")
        self.assertEqual(profile.cpu_info["endianness"], "little")

    def test_get_addressing_modes(self):
        """Test getting addressing mode information"""
        with patch("builtins.open", mock_open(read_data=json.dumps(self.valid_profile_data))):
            profile = ConfigCPUProfile(self.diagnostics, "test_profile.json")
            
        modes = profile.get_addressing_mode_enum("IMMEDIATE")
        self.assertEqual(modes.value, 1)  # Enum value
        self.assertEqual(modes.name, "IMMEDIATE")  # Enum name
        modes = profile.get_addressing_mode_enum("IMPLIED")
        self.assertEqual(modes.value, 0)  # Enum value
        self.assertEqual(modes.name, "IMPLIED")  # Enum name

    def test_get_opcode_details(self):
        """Test getting opcode information"""
        with patch("builtins.open", mock_open(read_data=json.dumps(self.valid_profile_data))):
            profile = ConfigCPUProfile(self.diagnostics, "test_profile.json")
            
        # Create a mock instruction
        mock_instruction = MagicMock()
        mock_instruction.mnemonic = "LDA"
        mock_instruction.mode = 1  # IMMEDIATE
        
        details = profile.get_opcode_details(mock_instruction, None)
        self.assertIsNotNone(details)
        self.assertEqual(details[0], 0xA9)  # opcode
        self.assertEqual(details[1], 1)    # operand size

    def test_parse_addressing_mode(self):
        """Test parsing addressing modes"""
        with patch("builtins.open", mock_open(read_data=json.dumps(self.valid_profile_data))):
            profile = ConfigCPUProfile(self.diagnostics, "test_profile.json")
            
        # Test immediate mode
        mode, value = profile.parse_addressing_mode("#$FF")
        self.assertEqual(mode.value, 1)  # IMMEDIATE enum value
        self.assertEqual(mode.name, "IMMEDIATE")  # Enum name
        self.assertEqual(value, 255)  # Should be converted to int
        
        # Test absolute mode
        mode, value = profile.parse_addressing_mode("$1234")
        self.assertEqual(mode.value, 2)  # ABSOLUTE enum value
        self.assertEqual(mode.name, "ABSOLUTE")  # Enum name
        self.assertEqual(value, 0x1234)
        
        # Test implied mode
        mode, value = profile.parse_addressing_mode("NOP")
        self.assertEqual(mode.value, 0)  # IMPLIED enum value
        self.assertEqual(mode.name, "IMPLIED")  # Enum name
        # For implied mode with group_index=None, value is the full operand
        self.assertEqual(value, "NOP")

    def test_file_not_found(self):
        """Test handling of missing profile file"""
        with self.assertRaises(FileNotFoundError):
            ConfigCPUProfile(self.diagnostics, "nonexistent_file.json")

    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        with patch("builtins.open", mock_open(read_data="invalid json content")):
            with self.assertRaises(ValueError):
                ConfigCPUProfile(self.diagnostics, "invalid.json")


class TestCPUProfileFactory(unittest.TestCase):
    """Test cases for CPUProfileFactory class"""

    def setUp(self):
        """Set up test fixtures"""
        self.diagnostics = Diagnostics()

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_get_available_cpus(self, mock_listdir, mock_exists):
        """Test getting list of available CPUs"""
        mock_exists.return_value = True
        mock_listdir.return_value = ["65c02.json", "6800.json", "README.md"]
        
        factory = CPUProfileFactory()
        cpus = factory.get_available_cpus()
        
        self.assertEqual(len(cpus), 2)
        self.assertIn("65c02", cpus)
        self.assertIn("6800", cpus)

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', mock_open(read_data=json.dumps({
        "cpu_info": {"name": "65C02", "description": "Test CPU", "data_width": 8, "address_width": 16},
        "addressing_modes": {"IMPLIED": 0, "IMMEDIATE": 1},
        "opcodes": {"NOP": {"IMPLIED": [0xEA, 0, {"base": 2}, ""]}},
        "branch_mnemonics": [],
        "addressing_mode_patterns": [],
        "directives": {},
        "validation_rules": {}
    })))
    def test_create_profile_success(self, mock_listdir, mock_exists):
        """Test successful profile creation"""
        mock_exists.return_value = True
        mock_listdir.return_value = ["65c02.json"]
        
        factory = CPUProfileFactory()
        profile = factory.create_profile("65c02", self.diagnostics)
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.cpu_info["name"], "65C02")

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_create_profile_file_not_found(self, mock_listdir, mock_exists):
        """Test profile creation when file doesn't exist"""
        mock_exists.return_value = True
        mock_listdir.return_value = ["65c02.json"]
        
        factory = CPUProfileFactory()
        
        # Mock the file open to raise FileNotFoundError
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with self.assertRaises(FileNotFoundError):
                factory.create_profile("65c02", self.diagnostics)

    @patch('os.path.exists')
    def test_create_profile_cpu_not_available(self, mock_exists):
        """Test profile creation when CPU is not available"""
        mock_exists.return_value = True
        
        factory = CPUProfileFactory()
        
        with self.assertRaises(ValueError):
            factory.create_profile("nonexistent", self.diagnostics)


if __name__ == '__main__':
    unittest.main()