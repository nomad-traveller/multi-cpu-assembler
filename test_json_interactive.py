#!/usr/bin/env python3
"""
Interactive JSON CPU Profile Tester
Allows interactive testing of JSON CPU profiles.
"""

import json
import sys
import os
from typing import Dict, Any, List

# Add compiler directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'compiler'))

from cpu_profile_base import JSONCPUProfile
from core.diagnostics import Diagnostics

def test_addressing_mode_parsing(profile: JSONCPUProfile, test_cases: List[str]):
    """Test addressing mode parsing with various test cases."""
    print("\n🔧 Testing Addressing Mode Parsing:")
    print("-" * 40)
    
    for test_case in test_cases:
        try:
            mode, value = profile.parse_addressing_mode(test_case)
            print(f"✅ '{test_case}' -> Mode: {mode}, Value: {value}")
        except Exception as e:
            print(f"❌ '{test_case}' -> Error: {e}")

def test_opcode_lookup(profile: JSONCPUProfile, test_instructions: List[tuple]):
    """Test opcode lookup for various instructions."""
    print("\n🔍 Testing Opcode Lookup:")
    print("-" * 40)
    
    for mnemonic, mode_name in test_instructions:
        try:
            # Get mode enum value
            mode_enum = profile.get_addressing_mode_enum(mode_name)
            if mode_enum is None:
                print(f"❌ {mnemonic} {mode_name} -> Unknown addressing mode")
                continue
            
            # Create mock instruction
            from unittest.mock import MagicMock
            mock_instr = MagicMock()
            mock_instr.mnemonic = mnemonic
            mock_instr.mode = mode_enum
            
            # Get opcode details
            details = profile.get_opcode_details(mock_instr, None)
            if details:
                opcode, operand_size, cycles, flags = details
                print(f"✅ {mnemonic} {mode_name} -> Opcode: ${opcode:02X}, Size: {operand_size}, Cycles: {cycles}, Flags: {flags}")
            else:
                print(f"❌ {mnemonic} {mode_name} -> No opcode found")
        except Exception as e:
            print(f"❌ {mnemonic} {mode_name} -> Error: {e}")

def test_cpu_profile_interactive(file_path: str):
    """Interactive testing of a CPU profile."""
    print(f"🎯 Loading CPU Profile: {os.path.basename(file_path)}")
    
    try:
        diagnostics = Diagnostics()
        profile = JSONCPUProfile(diagnostics, file_path)
        
        print(f"\n📋 CPU Information:")
        print(f"   Name: {profile.cpu_info.get('name', 'Unknown')}")
        print(f"   Description: {profile.cpu_info.get('description', 'No description')}")
        print(f"   Data Width: {profile.cpu_info.get('data_width', '?')} bits")
        print(f"   Address Width: {profile.cpu_info.get('address_width', '?')} bits")
        print(f"   Endianness: {profile.cpu_info.get('endianness', '?')}")
        
        print(f"\n🔧 Available Addressing Modes:")
        for mode_name, mode_value in profile.addressing_modes.items():
            print(f"   {mode_name}: {mode_value}")
        
        print(f"\n📝 Available Mnemonics:")
        mnemonics = sorted(profile.opcodes.keys())
        for mnemonic in mnemonics:
            print(f"   {mnemonic}")
        
        print(f"\n🌿 Branch Instructions:")
        for branch in profile.branch_mnemonics:
            print(f"   {branch}")
        
        # Test 65C02 specific cases
        if profile.cpu_info.get('name') == '65C02':
            test_cases_65c02 = [
                "#$FF",      # Immediate
                "$1234",      # Absolute
                "$00",         # Zero page
                "NOP",         # Implied
                "($1234)",     # Indirect
                "($00,X)",     # Indexed X indirect
                "($00),Y",     # Indexed Y indirect
                "$1234,X",     # Absolute X indexed
                "$1234,Y",     # Absolute Y indexed
                "$00,X",        # Zero page X indexed
                "$00,Y",        # Zero page Y indexed
                "A",            # Accumulator
            ]
            
            test_instructions = [
                ("LDA", "IMMEDIATE"),
                ("LDA", "ABSOLUTE"),
                ("LDA", "ZEROPAGE"),
                ("NOP", "IMPLIED"),
                ("STA", "ABSOLUTE"),
                ("JMP", "ABSOLUTE"),
                ("BNE", "RELATIVE"),
            ]
            
            test_addressing_mode_parsing(profile, test_cases_65c02)
            test_opcode_lookup(profile, test_instructions)
        
        # Test 6800 specific cases
        elif profile.cpu_info.get('name') == '6800':
            test_cases_6800 = [
                "#$FF",      # Immediate
                "$1234",      # Extended
                "$00",         # Direct
                "NOP",         # Inherent
                "$10,X",       # Indexed
                "A",           # Accumulator A
                "B",           # Accumulator B
            ]
            
            test_instructions = [
                ("LDAA", "IMMEDIATE"),
                ("LDAA", "EXTENDED"),
                ("LDAA", "DIRECT"),
                ("NOP", "INHERENT"),
                ("STAA", "EXTENDED"),
                ("BNE", "RELATIVE"),
                ("JSR", "EXTENDED"),
            ]
            
            test_addressing_mode_parsing(profile, test_cases_6800)
            test_opcode_lookup(profile, test_instructions)
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading profile: {e}")
        return False

def interactive_menu():
    """Interactive menu for testing CPU profiles."""
    cpu_profiles_dir = os.path.join(os.path.dirname(__file__), 'compiler', 'cpu_profiles')
    
    # Find all JSON files
    json_files = []
    for file in os.listdir(cpu_profiles_dir):
        if file.endswith('.json'):
            json_files.append(os.path.join(cpu_profiles_dir, file))
    
    if not json_files:
        print("❌ No JSON CPU profile files found!")
        return
    
    print("🎯 Available CPU Profiles:")
    for i, file_path in enumerate(json_files, 1):
        print(f"   {i}. {os.path.basename(file_path)}")
    
    print(f"   {len(json_files) + 1}. Test all profiles")
    print("   0. Exit")
    
    while True:
        try:
            choice = input(f"\nSelect profile to test (0-{len(json_files) + 1}): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(json_files):
                selected_file = json_files[choice_num - 1]
                test_cpu_profile_interactive(selected_file)
            
            elif choice_num == len(json_files) + 1:
                print("\n🔄 Testing all profiles...")
                for file_path in json_files:
                    print(f"\n{'='*60}")
                    test_cpu_profile_interactive(file_path)
            
            else:
                print(f"❌ Invalid choice. Please enter 0-{len(json_files) + 1}")
                
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def main():
    """Main interactive tester."""
    if len(sys.argv) > 1:
        # Test specific file if provided
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            test_cpu_profile_interactive(file_path)
        else:
            print(f"❌ File not found: {file_path}")
    else:
        # Show interactive menu
        interactive_menu()

if __name__ == '__main__':
    main()