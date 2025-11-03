#!/usr/bin/env python3
"""
Convert JSON5 CPU profiles to YAML format.
Migrates from JSON5 to more readable YAML format.
"""

import json5
import yaml
import sys
import os

def convert_json5_to_yaml(json5_file, yaml_file):
    """Convert JSON5 CPU profile to YAML format."""
    try:
        # Load JSON5 file
        with open(json5_file, 'r') as f:
            data = json5.load(f)
        
        # Convert to YAML with enhanced formatting
        with open(yaml_file, 'w') as f:
            f.write(f"# {os.path.basename(yaml_file)}\n")
            f.write(f"# Multi-CPU Assembler CPU Profile - YAML Format\n")
            f.write(f"# Generated from {os.path.basename(json5_file)}\n\n")
            
            # Use YAML dump with custom formatting
            yaml.dump(data, f, 
                     default_flow_style=False,
                     sort_keys=False,
                     indent=2,
                     width=120,
                     allow_unicode=True)
            
        print(f"✅ Converted {json5_file} -> {yaml_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error converting {json5_file}: {e}")
        return False

def main():
    """Main conversion function."""
    if len(sys.argv) < 2:
        print("Usage: python convert_to_yaml.py <json5_file> [json5_file2...]")
        return
    
    input_files = sys.argv[1:]
    
    for input_file in input_files:
        if not os.path.exists(input_file):
            print(f"❌ File not found: {input_file}")
            continue
            
        # Create YAML filename
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.yaml"
        
        # Convert file
        if convert_json5_to_yaml(input_file, output_file):
            print(f"   📝 Enhanced readability with YAML format")
            print(f"   🔧 Better comments and structure")

if __name__ == '__main__':
    main()