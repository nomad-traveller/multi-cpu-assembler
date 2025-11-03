#!/usr/bin/env python3
"""
Convert JSON CPU profiles to use hexadecimal opcodes and JSON5 format.
"""

import json
import json5
import sys
import os

def convert_decimal_to_hex_in_opcodes(data):
    """Convert decimal opcodes to hexadecimal in the JSON data."""
    if "opcodes" in data:
        for mnemonic, modes in data["opcodes"].items():
            for mode_name, opcode_info in modes.items():
                if isinstance(opcode_info, list) and len(opcode_info) >= 1:
                    # Convert the first element (opcode) from decimal to hex
                    opcode_value = opcode_info[0]
                    if isinstance(opcode_value, int):
                        opcode_info[0] = hex(opcode_value)
    
    return data

def convert_json_file(input_file, output_file):
    """Convert a JSON file to use hexadecimal opcodes and JSON5 format."""
    try:
        # Read the JSON file
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Convert decimal opcodes to hexadecimal
        data = convert_decimal_to_hex_in_opcodes(data)
        
        # Write as JSON5 with comments
        with open(output_file, 'w') as f:
            # Add JSON5 header comment
            f.write("// Multi-CPU Assembler Profile - JSON5 Format\n")
            f.write("// Opcodes are in hexadecimal format\n")
            f.write("// Generated from decimal format\n\n")
            
            # Write the data as JSON5 (allows comments and trailing commas)
            json5.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Converted {input_file} -> {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error converting {input_file}: {e}")
        return False

def main():
    """Main conversion function."""
    if len(sys.argv) < 2:
        print("Usage: python convert_to_hex_opcodes.py <json_file> [json_file2...]")
        return
    
    input_files = sys.argv[1:]
    
    for input_file in input_files:
        if not os.path.exists(input_file):
            print(f"❌ File not found: {input_file}")
            continue
            
        # Create output filename (same name, same location)
        output_file = input_file  # Overwrite original file
        
        # Convert the file
        if convert_json_file(input_file, output_file):
            print(f"   📝 Converted decimal opcodes to hexadecimal")
            print(f"   🔧 Updated to JSON5 format with comments")

if __name__ == '__main__':
    main()