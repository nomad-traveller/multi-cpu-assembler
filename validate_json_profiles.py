#!/usr/bin/env python3
"""
Simple JSON CPU Profile Validator
Validates CPU profile JSON files with basic structure checks.
"""

import json
import sys
import os
from typing import Dict, List, Any

def validate_cpu_profile(file_path: str) -> Dict[str, Any]:
    """Validate a CPU profile JSON file and return results."""
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'analysis': {}
    }
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result['errors'].append(f"JSON syntax error: {e}")
        return result
    except FileNotFoundError:
        result['errors'].append("File not found")
        return result
    except Exception as e:
        result['errors'].append(f"Unexpected error: {e}")
        return result
    
    # Basic structure validation
    required_sections = ['cpu_info', 'addressing_modes', 'addressing_mode_patterns', 'opcodes', 'branch_mnemonics']
    
    for section in required_sections:
        if section not in data:
            result['errors'].append(f"Missing required section: {section}")
    
    # Validate cpu_info section
    if 'cpu_info' in data:
        cpu_info = data['cpu_info']
        required_cpu_fields = ['name', 'description', 'data_width', 'address_width', 'endianness']
        
        for field in required_cpu_fields:
            if field not in cpu_info:
                result['errors'].append(f"Missing cpu_info field: {field}")
        
        # Validate specific fields
        if 'endianness' in cpu_info and cpu_info['endianness'] not in ['little', 'big']:
            result['errors'].append(f"Invalid endianness: {cpu_info['endianness']}")
        
        if 'data_width' in cpu_info:
            dw = cpu_info['data_width']
            if not isinstance(dw, int) or dw < 1 or dw > 64:
                result['errors'].append(f"Invalid data_width: {dw}")
        
        if 'address_width' in cpu_info:
            aw = cpu_info['address_width']
            if not isinstance(aw, int) or aw < 1 or aw > 64:
                result['errors'].append(f"Invalid address_width: {aw}")
    
    # Validate addressing_modes
    if 'addressing_modes' in data:
        addressing_modes = data['addressing_modes']
        if not isinstance(addressing_modes, dict):
            result['errors'].append("addressing_modes must be a dictionary")
        else:
            for mode_name, mode_value in addressing_modes.items():
                if not isinstance(mode_value, int) or mode_value < 0:
                    result['errors'].append(f"Invalid addressing mode value for {mode_name}: {mode_value}")
    
    # Validate addressing_mode_patterns
    if 'addressing_mode_patterns' in data:
        patterns = data['addressing_mode_patterns']
        if not isinstance(patterns, list):
            result['errors'].append("addressing_mode_patterns must be a list")
        else:
            for i, pattern in enumerate(patterns):
                if not isinstance(pattern, dict):
                    result['errors'].append(f"Pattern {i} must be a dictionary")
                    continue
                
                required_pattern_fields = ['pattern', 'mode']
                for field in required_pattern_fields:
                    if field not in pattern:
                        result['errors'].append(f"Pattern {i} missing field: {field}")
                
                if 'pattern' in pattern and not isinstance(pattern['pattern'], str):
                    result['errors'].append(f"Pattern {i} pattern must be a string")
                
                if 'mode' in pattern and not isinstance(pattern['mode'], str):
                    result['errors'].append(f"Pattern {i} mode must be a string")
                
                if 'group_index' in pattern:
                    gi = pattern['group_index']
                    if gi is not None and not isinstance(gi, int):
                        result['errors'].append(f"Pattern {i} group_index must be null or integer")
    
    # Validate opcodes
    if 'opcodes' in data:
        opcodes = data['opcodes']
        if not isinstance(opcodes, dict):
            result['errors'].append("opcodes must be a dictionary")
        else:
            for mnemonic, modes in opcodes.items():
                if not isinstance(modes, dict):
                    result['errors'].append(f"Opcodes for {mnemonic} must be a dictionary")
                    continue
                
                for mode_name, opcode_data in modes.items():
                    if not isinstance(opcode_data, list):
                        result['errors'].append(f"Opcode data for {mnemonic}.{mode_name} must be a list")
                        continue
                    
                    if len(opcode_data) < 3:
                        result['errors'].append(f"Opcode data for {mnemonic}.{mode_name} must have at least 3 elements")
                    
                    # Check opcode value (first element)
                    if len(opcode_data) > 0:
                        opcode_val = opcode_data[0]
                        if not isinstance(opcode_val, int) or opcode_val < 0 or opcode_val > 255:
                            result['errors'].append(f"Invalid opcode value for {mnemonic}.{mode_name}: {opcode_val}")
                    
                    # Check operand size (second element)
                    if len(opcode_data) > 1:
                        operand_size = opcode_data[1]
                        if not isinstance(operand_size, int) or operand_size < 0 or operand_size > 4:
                            result['errors'].append(f"Invalid operand size for {mnemonic}.{mode_name}: {operand_size}")
    
    # Validate branch_mnemonics
    if 'branch_mnemonics' in data:
        branch_mnemonics = data['branch_mnemonics']
        if not isinstance(branch_mnemonics, list):
            result['errors'].append("branch_mnemonics must be a list")
        else:
            for i, mnemonic in enumerate(branch_mnemonics):
                if not isinstance(mnemonic, str):
                    result['errors'].append(f"Branch mnemonic {i} must be a string")
    
    # Analyze the profile if no errors
    if not result['errors']:
        result['valid'] = True
        result['analysis'] = analyze_profile(data)
    
    return result

def analyze_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a valid CPU profile and return statistics."""
    analysis = {
        'cpu_name': data.get('cpu_info', {}).get('name', 'Unknown'),
        'data_width': data.get('cpu_info', {}).get('data_width', 0),
        'address_width': data.get('cpu_info', {}).get('address_width', 0),
        'endianness': data.get('cpu_info', {}).get('endianness', 'unknown'),
        'addressing_modes_count': len(data.get('addressing_modes', {})),
        'mnemonic_count': len(data.get('opcodes', {})),
        'total_opcodes': 0,
        'branch_count': len(data.get('branch_mnemonics', [])),
        'pattern_count': len(data.get('addressing_mode_patterns', [])),
        'has_directives': 'directives' in data,
        'has_validation_rules': 'validation_rules' in data
    }
    
    # Count total opcodes
    for mnemonic, modes in data.get('opcodes', {}).items():
        analysis['total_opcodes'] += len(modes)
    
    return analysis

def print_validation_result(file_path: str, result: Dict[str, Any]):
    """Print validation result in a formatted way."""
    filename = os.path.basename(file_path)
    
    if result['valid']:
        print(f"✅ {filename}: VALID")
        analysis = result['analysis']
        print(f"   📋 CPU: {analysis['cpu_name']} ({analysis['data_width']}-bit, {analysis['address_width']}-bit, {analysis['endianness']} endian)")
        print(f"   🔧 Addressing Modes: {analysis['addressing_modes_count']}")
        print(f"   📝 Mnemonics: {analysis['mnemonic_count']}")
        print(f"   🔢 Total Opcodes: {analysis['total_opcodes']}")
        print(f"   🌿 Branch Instructions: {analysis['branch_count']}")
        print(f"   🎯 Addressing Patterns: {analysis['pattern_count']}")
        print(f"   📜 Has Directives: {'Yes' if analysis['has_directives'] else 'No'}")
        print(f"   ⚖️  Has Validation Rules: {'Yes' if analysis['has_validation_rules'] else 'No'}")
    else:
        print(f"❌ {filename}: INVALID")
        for error in result['errors']:
            print(f"   🔴 {error}")
    
    if result['warnings']:
        for warning in result['warnings']:
            print(f"   🟡 {warning}")

def main():
    """Main validation script."""
    if len(sys.argv) < 2:
        print("Usage: python validate_json_profiles.py <json_file> [json_file2 ...]")
        print("   Or: python validate_json_profiles.py --all (validates all JSON files in cpu_profiles/)")
        sys.exit(1)
    
    files_to_validate = []
    
    if sys.argv[1] == "--all":
        # Validate all JSON files in cpu_profiles directory
        cpu_profiles_dir = os.path.join(os.path.dirname(__file__), 'compiler', 'cpu_profiles')
        for file in os.listdir(cpu_profiles_dir):
            if file.endswith('.json'):
                files_to_validate.append(os.path.join(cpu_profiles_dir, file))
    else:
        # Validate specified files
        files_to_validate = sys.argv[1:]
    
    print("🔍 JSON CPU Profile Validation")
    print("=" * 60)
    
    all_valid = True
    
    for file_path in files_to_validate:
        result = validate_cpu_profile(file_path)
        print_validation_result(file_path, result)
        print()
        
        if not result['valid']:
            all_valid = False
    
    print("=" * 60)
    if all_valid:
        print("✅ All JSON files are valid!")
        sys.exit(0)
    else:
        print("❌ Some JSON files have errors!")
        sys.exit(1)

if __name__ == '__main__':
    main()