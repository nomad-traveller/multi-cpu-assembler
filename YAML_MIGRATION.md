# YAML Migration Guide

This document describes the migration from JSON5 to YAML format for CPU profiles and the dual-format support now available in the Multi-CPU Assembler.

## Overview

The Multi-CPU Assembler now supports CPU profiles in both JSON5 and YAML formats, providing enhanced readability and maintainability while maintaining full backward compatibility.

## Benefits of YAML Format

### Enhanced Readability
- **Natural Syntax**: YAML's indentation-based structure is more intuitive for configuration files
- **Better Comments**: Superior commenting capabilities with inline and block comments
- **Cleaner Structure**: More readable representation of complex nested data

### Industry Standard
- **Widely Adopted**: YAML is the preferred format for configuration files in modern development
- **Tool Support**: Excellent tooling and editor support across all platforms
- **Human-Friendly**: Designed for human readability and easy editing

### Example Comparison

#### JSON5 Format
```json
{
  "cpu_info": {
    "name": "65C02",
    "description": "CMOS 6502 processor with additional instructions",
    "data_width": 8,
    "address_width": 16,
    "endianness": "little"
  },
  "addressing_modes": {
    "IMPLIED": 0,
    "IMMEDIATE": 2,
    "ABSOLUTE": 6
  }
}
```

#### YAML Format
```yaml
cpu_info:
  name: 65C02
  description: CMOS 6502 processor with additional instructions
  data_width: 8
  address_width: 16
  endianness: little

addressing_modes:
  IMPLIED: 0
  IMMEDIATE: 2
  ABSOLUTE: 6
```

## Migration Status

### Completed ✅
- **Dual Format Support**: Automatic detection based on file extension
- **YAML Conversion**: All existing CPU profiles converted to YAML
- **Validation Tools**: Updated to support both formats
- **Testing Tools**: Interactive testing works with both formats
- **Backward Compatibility**: JSON5 files continue to work unchanged

### Available Profiles

| CPU | JSON5 Profile | YAML Profile |
|-----|---------------|--------------|
| 65C02 | `compiler/cpu_profiles/65c02.json` | `compiler/cpu_profiles/65c02.yaml` |
| 6800 | `compiler/cpu_profiles/6800.json` | `compiler/cpu_profiles/6800.yaml` |

## Usage

### Automatic Format Detection

The assembler automatically detects the profile format based on file extension:

```bash
# Both commands work the same way
python compiler/main.py program.s --cpu 65c02  # Uses 65c02.json
python compiler/main.py program.s --cpu 65c02  # Uses 65c02.yaml if available
```

### Validation

```bash
# Validate all profiles (both formats)
python validate_json_profiles.py --all

# Validate specific format
python validate_json_profiles.py compiler/cpu_profiles/65c02.json
python validate_json_profiles.py compiler/cpu_profiles/65c02.yaml
```

### Interactive Testing

```bash
# Interactive menu shows all available profiles
python test_json_interactive.py

# Test specific profile
python test_json_interactive.py compiler/cpu_profiles/65c02.yaml
```

## Conversion Tools

### JSON5 to YAML Conversion

Use the provided conversion script:

```bash
# Convert specific file
python convert_to_yaml.py compiler/cpu_profiles/65c02.json

# Convert multiple files
python convert_to_yaml.py compiler/cpu_profiles/65c02.json compiler/cpu_profiles/6800.json
```

### Manual Conversion

For manual conversion or custom profiles:

1. **Use Online Tools**: JSON to YAML converters
2. **Use Command Line**: `python -c "import yaml; import json5; yaml.safe_dump(json5.load(open('input.json')), open('output.yaml', 'w'))"`
3. **Use IDE Plugins**: Most IDEs have JSON/YAML conversion plugins

## Format Support Details

### File Extensions

| Extension | Format | Library Used |
|-----------|--------|--------------|
| `.json` | JSON5 | `json5` library |
| `.yaml` | YAML | `PyYAML` library |
| `.yml` | YAML | `PyYAML` library |

### Loading Priority

1. **Explicit Extension**: Format determined by file extension
2. **Default Fallback**: Unknown extensions default to JSON5
3. **Error Handling**: Clear error messages for missing dependencies

### Dependencies

```bash
# Required for both formats
pip install sly json5 PyYAML
```

## Creating New Profiles

### YAML Profile Template

```yaml
# new_cpu.yaml
# Multi-CPU Assembler CPU Profile - YAML Format

cpu_info:
  name: NEW_CPU
  description: New CPU Architecture
  data_width: 8
  address_width: 16
  endianness: little  # or big

addressing_modes:
  IMPLIED: 0
  IMMEDIATE: 1
  ABSOLUTE: 2

addressing_mode_patterns:
  - pattern: ^(NOP|BRK)$
    mode: IMPLIED
    group_index: null
    flags:
    - IGNORECASE

opcodes:
  NOP:
    IMPLIED: [0x00, 0, 2, ""]  # [opcode, operand_size, cycles, flags]

branch_mnemonics:
  - BRA
  - BNE

directives:
  ORG:
    operand_count: 1
    operand_type: expression

validation_rules:
  inherent_only:
    NOP: ["IMPLIED"]
```

### JSON5 Profile Template

```json
{
  // new_cpu.json
  // Multi-CPU Assembler CPU Profile - JSON5 Format
  
  "cpu_info": {
    "name": "NEW_CPU",
    "description": "New CPU Architecture",
    "data_width": 8,
    "address_width": 16,
    "endianness": "little"
  },
  
  "addressing_modes": {
    "IMPLIED": 0,
    "IMMEDIATE": 1,
    "ABSOLUTE": 2
  },
  
  "opcodes": {
    "NOP": {
      "IMPLIED": [0x00, 0, 2, ""]
    }
  }
}
```

## Best Practices

### YAML Recommendations

1. **Use 2-space indentation** for consistency
2. **Add comments** to document complex sections
3. **Use block comments** for longer explanations
4. **Keep lines under 120 characters** for readability
5. **Use quotes** for strings with special characters

### Example with Comments

```yaml
# CPU Information Section
cpu_info:
  name: 65C02                    # CPU identifier
  description: CMOS 6502 processor with additional instructions
  data_width: 8                  # 8-bit data bus
  address_width: 16               # 16-bit address bus
  endianness: little             # Little-endian byte order

# Addressing Mode Definitions
addressing_modes:
  IMPLIED: 0                     # No operand (e.g., NOP, CLC)
  IMMEDIATE: 2                   # #value (e.g., LDA #$FF)
  ABSOLUTE: 6                    # address (e.g., JMP $1234)

# Opcode Definitions
opcodes:
  LDA:                           # Load Accumulator
    IMMEDIATE: [0xA9, 1, 2, "NZ"]    # #$value, 1 byte, 2 cycles, N,Z flags
    ABSOLUTE: [0xAD, 2, 4, "NZ"]     # address, 2 bytes, 4 cycles, N,Z flags
```

## Troubleshooting

### Common Issues

1. **PyYAML Not Installed**:
   ```bash
   pip install PyYAML
   ```

2. **Indentation Errors in YAML**:
   - Use spaces, not tabs
   - Maintain consistent indentation
   - Check for trailing spaces

3. **Format Detection Issues**:
   - Ensure correct file extensions
   - Check file permissions
   - Verify file syntax

### Validation Errors

```bash
# Detailed validation output
python validate_json_profiles.py compiler/cpu_profiles/profile.yaml -v

# Check YAML syntax specifically
python -c "import yaml; yaml.safe_load(open('profile.yaml'))"
```

## Migration Strategy

### For Existing Projects

1. **Continue Using JSON5**: No immediate changes required
2. **Gradual Migration**: Convert profiles one at a time
3. **Testing**: Validate converted profiles thoroughly
4. **Documentation**: Update team documentation

### For New Projects

1. **Use YAML**: Recommended for new profiles
2. **Template**: Start from provided YAML templates
3. **Validation**: Use validation tools during development
4. **Comments**: Leverage YAML's superior commenting

## Future Roadmap

### Planned Enhancements

- [ ] **Schema Validation**: JSON Schema for both formats
- [ ] **IDE Integration**: VS Code extensions for profile editing
- [ ] **Web Editor**: Online profile creation and validation
- [ ] **Format Conversion**: Bidirectional conversion tools
- [ ] **Profile Templates**: Starter templates for common CPUs

### Community Contributions

Contributions are welcome for:
- New CPU profiles in either format
- Conversion tool improvements
- Documentation enhancements
- Validation rule improvements

## Conclusion

The YAML migration provides enhanced readability and maintainability while preserving full backward compatibility. Users can choose the format that best suits their needs, and the automatic format detection ensures seamless operation.

**Status**: ✅ Migration complete with dual-format support
**Compatibility**: ✅ Full backward compatibility maintained
**Recommendation**: ✅ Use YAML for new profiles