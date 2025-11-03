# cpu_profiles.py - CPU Profile Abstract Base Class
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING
import json
import os
import re
from enum import Enum
try:
    import json5
except ImportError:
    json5 = None

if TYPE_CHECKING:
    from core.parser import Parser


def create_addressing_mode_enum(cpu_name: str, addressing_modes: dict):
    """Create a dynamic Enum for addressing modes based on CPU profile."""
    enum_name = f"{cpu_name.upper()}AddressingMode"
    
    # Create enum members with their integer values
    enum_members = {}
    for mode_name, mode_value in addressing_modes.items():
        # Convert to valid Python enum member name
        member_name = mode_name.upper().replace(' ', '_')
        enum_members[member_name] = mode_value
    
    return Enum(enum_name, enum_members)


class JSONCPUProfile:
    """JSON-based CPU Profile that loads configuration from JSON files."""
    
    def __init__(self, diagnostics, json_file_path: str):
        self.diagnostics = diagnostics
        self._load_profile(json_file_path)
        self._create_addressing_mode_enum()
    
    def _load_profile(self, json_file_path: str):
        """Load CPU profile from JSON5 file."""
        try:
            if json5 is not None:
                with open(json_file_path, 'r') as f:
                    self._profile_data = json5.load(f)
            else:
                # Fallback to regular JSON if json5 not available
                with open(json_file_path, 'r') as f:
                    self._profile_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"CPU profile file not found: {json_file_path}")
        except Exception as e:
            raise ValueError(f"Invalid JSON5/JSON in CPU profile {json_file_path}: {e}")
    
    def _create_addressing_mode_enum(self):
        """Create dynamic Enum for addressing modes."""
        cpu_name = self.cpu_info.get("name", "CPU")
        addressing_modes = self._profile_data["addressing_modes"]
        self.AddressingMode = create_addressing_mode_enum(cpu_name, addressing_modes)
    
    @property
    def cpu_info(self) -> dict:
        return self._profile_data["cpu_info"]
    
    @property
    def opcodes(self) -> dict[str, dict[Any, list[Any]]]:
        return self._profile_data["opcodes"]
    
    @property
    def branch_mnemonics(self) -> set[str]:
        return set(self._profile_data["branch_mnemonics"])
    
    @property
    def addressing_modes(self) -> dict[str, int]:
        """Legacy property for backward compatibility."""
        return self._profile_data["addressing_modes"]
    
    @property
    def addressing_mode_patterns(self) -> list[dict]:
        return self._profile_data["addressing_mode_patterns"]
    
    @property
    def directives(self) -> dict:
        return self._profile_data.get("directives", {})
    
    @property
    def validation_rules(self) -> dict:
        return self._profile_data.get("validation_rules", {})
    
    def get_addressing_mode_enum(self, mode_name: str) -> Any:
        """Get enum value for addressing mode name."""
        # Convert mode name to enum member name
        member_name = mode_name.upper().replace(' ', '_')
        try:
            return getattr(self.AddressingMode, member_name)
        except AttributeError:
            # Fallback to dictionary for backward compatibility
            return self.addressing_modes.get(mode_name)
    
    def get_addressing_mode_name(self, mode_enum: Any) -> str | None:
        """Get addressing mode name from enum value."""
        # If it's an Enum member, get its name
        if hasattr(mode_enum, 'name'):
            return mode_enum.name.replace('_', ' ')
        
        # If it's an integer value, look up in dictionary
        if isinstance(mode_enum, int):
            for name, value in self.addressing_modes.items():
                if value == mode_enum:
                    return name
            return None
        
        # Fallback: try to convert to string
        return str(mode_enum) if mode_enum else None
    
    def parse_addressing_mode(self, operand_str: str) -> tuple[Any, Any]:
        """Parse addressing mode using JSON patterns (optimized for 8-bit CPUs)."""
        operand_str = operand_str.strip().upper()
        if not operand_str:
            return (self.get_addressing_mode_enum("INHERENT"), None)
        
        # Try each pattern until we find a match
        for pattern_info in self.addressing_mode_patterns:
            match = self._match_pattern(operand_str, pattern_info)
            if match:
                mode_name = pattern_info["mode"]
                mode = self.get_addressing_mode_enum(mode_name)
                value = self._extract_value(match, pattern_info, operand_str)
                return (mode, value)
        
        raise ValueError(f"Invalid operand: {operand_str}")
    
    def _match_pattern(self, operand_str: str, pattern_info: dict) -> re.Match | None:
        """Match operand against a single pattern."""
        pattern = pattern_info["pattern"]
        flags = pattern_info.get("flags", [])
        
        # Compile regex with appropriate flags
        regex_flags = 0
        if "IGNORECASE" in flags:
            regex_flags |= re.IGNORECASE
        
        compiled_pattern = re.compile(pattern, regex_flags)
        return compiled_pattern.match(operand_str)
    
    def _extract_value(self, match: re.Match, pattern_info: dict, original_operand: str) -> Any:
        """Extract and convert value from regex match (8-bit CPU optimized)."""
        mode_name = pattern_info["mode"]
        group_idx = pattern_info.get("group_index")
        
        # Handle accumulator modes (no value needed)
        if mode_name in ["ACCUMULATOR", "ACCUMULATOR_A", "ACCUMULATOR_B"]:
            return None
        
        # Extract value using group index if specified
        if group_idx is not None:
            val_str = match.group(group_idx)
            return self._convert_numeric_value(val_str)
        
        # For patterns without group_idx, handle based on mode
        if mode_name == "IMPLIED":
            # For implied instructions, return the full operand (e.g., "NOP")
            return original_operand
        elif mode_name in ["IMMEDIATE", "DIRECT", "EXTENDED", "INDEXED"]:
            return self._extract_from_operand(original_operand, mode_name)
        
        # Default: no value
        return None
    
    def _convert_numeric_value(self, val_str: str) -> int | str | None:
        """Convert string value to numeric if possible (8-bit CPU optimized)."""
        if not val_str:
            return None
            
        # Handle hexadecimal values
        if val_str.startswith('$'):
            try:
                return int(val_str[1:], 16)
            except ValueError:
                return val_str
        
        # Handle decimal values
        if val_str.isdigit():
            return int(val_str)
        
        # Return as string (label/symbol)
        return val_str
    
    def _convert_opcode_to_int(self, opcode_value) -> int:
        """Convert opcode value to integer (handles hex strings from JSON5)."""
        if isinstance(opcode_value, str):
            # Handle hexadecimal strings like "0x69"
            if opcode_value.startswith('0x') or opcode_value.startswith('0X'):
                return int(opcode_value, 16)
            # Handle hex strings without 0x prefix
            elif opcode_value.startswith('$'):
                return int(opcode_value[1:], 16)
            else:
                # Try to parse as hex, fallback to decimal
                try:
                    return int(opcode_value, 16)
                except ValueError:
                    return int(opcode_value)
        elif isinstance(opcode_value, int):
            return opcode_value
        else:
            raise ValueError(f"Invalid opcode format: {opcode_value}")
    
    def _extract_from_operand(self, operand_str: str, mode_name: str) -> int | str | None:
        """Extract value from operand string based on addressing mode."""
        # Remove addressing mode syntax characters
        clean_str = operand_str
        clean_str = re.sub(r'[#()]', '', clean_str)  # Remove #, (, )
        
        # For indexed addressing, extract base address
        if mode_name == "INDEXED":
            parts = clean_str.split(',')
            clean_str = parts[0] if parts else clean_str
        
        # Remove register references
        clean_str = re.sub(r'[XYAB]$', '', clean_str.strip())
        
        return self._convert_numeric_value(clean_str)
    
    def parse_instruction(self, instruction, parser: 'Parser') -> None:
        """Parse CPU instruction using JSON configuration."""
        operand_str = instruction.operand_str
        mnemonic = instruction.mnemonic
        
        if not operand_str:
            # Check if this mnemonic is an inherent instruction
            mode, _ = self.parse_addressing_mode(mnemonic)
            if mode is not None:
                instruction.mode = mode
            else:
                instruction.mode = self.get_addressing_mode_enum("IMPLIED")
            return

        expression_str = operand_str
        if operand_str.startswith('#'):
            expression_str = operand_str[1:]

        mode, extracted_value = self.parse_addressing_mode(operand_str)
        if mode:
            instruction.mode = mode
            # For indexed addressing, use the extracted value (before ",X")
            if mode == self.get_addressing_mode_enum("INDEXED") and extracted_value:
                instruction.operand_value = parser.parse_operand_list(extracted_value)[0]
            else:
                instruction.operand_value = parser.parse_operand_list(expression_str)[0]
        else:
            raise ValueError(f"Could not determine addressing mode for operand: {operand_str}")

        # Apply CPU-specific post-processing rules from JSON
        self._apply_post_processing_rules(instruction)
    
    def _apply_post_processing_rules(self, instruction):
        """Apply CPU-specific post-processing rules from JSON configuration."""
        mnemonic = instruction.mnemonic
        mode = instruction.mode
        
        # Convert mode enum to string for lookup
        mode_name = self.get_addressing_mode_name(mode)
        
        if not mode_name:
            return
        
        # Get post-processing rules from JSON
        post_processing = self._profile_data.get("post_processing", {})
        
        # Branch instruction handling
        branch_rules = post_processing.get("branch_instructions", {})
        if mnemonic in branch_rules.get("mnemonics", []):
            target_mode = branch_rules.get("force_mode")
            if target_mode:
                instruction.mode = self.get_addressing_mode_enum(target_mode)
        
        # Automatic mode conversion rules
        auto_conversion = post_processing.get("automatic_mode_conversion", [])
        for rule in auto_conversion:
            if (mode_name == rule["from_mode"] and 
                isinstance(instruction.operand_value, int) and 
                instruction.operand_value <= rule["threshold"]):
                instruction.mode = self.get_addressing_mode_enum(rule["to_mode"])
    
    def parse_directive(self, instruction, parser: 'Parser') -> None:
        """Parse assembler directive using JSON configuration."""
        mnemonic = instruction.directive
        operand_str = instruction.operand_str
        
        if mnemonic not in self.directives:
            raise ValueError(f"Unknown directive: {mnemonic}")
        
        directive_info = self.directives[mnemonic]
        operand_count = directive_info.get("operand_count", 1)
        operand_type = directive_info.get("operand_type", "expression")
        
        if operand_count == 1:
            if not operand_str:
                raise ValueError(f"Missing operand for {mnemonic}")
            instruction.operand_value = parser.parse_operand_list(operand_str)[0]
        elif operand_count == "variable":
            instruction.operand_value = parser.parse_operand_list(operand_str)
            size_multiplier = directive_info.get("size_multiplier", 1)
            instruction.size = len(instruction.operand_value) * size_multiplier
        else:
            raise ValueError(f"Unsupported operand count for {mnemonic}: {operand_count}")
    
    def get_opcode_details(self, instruction, symbol_table) -> list[Any] | None:
        """Get opcode details for instruction."""
        mnemonic = instruction.mnemonic
        mode = instruction.mode
        
        if mnemonic not in self.opcodes:
            return None
        
        # Convert mode enum to string for lookup
        mode_name = self.get_addressing_mode_name(mode)
        
        if mode_name and mode_name in self.opcodes[mnemonic]:
            opcode_details = self.opcodes[mnemonic][mode_name]
            # Convert hex string opcodes to integers
            if isinstance(opcode_details, list) and len(opcode_details) > 0:
                opcode_details[0] = self._convert_opcode_to_int(opcode_details[0])
            return opcode_details
        
        # Handle automatic mode conversion (e.g., 6800 EXTENDED to DIRECT)
        post_processing = self._profile_data.get("post_processing", {})
        auto_conversion = post_processing.get("automatic_mode_conversion", [])
        
        for rule in auto_conversion:
            if (mode_name == rule["from_mode"] and 
                mnemonic in self.opcodes):
                condition = rule.get("condition")
                if condition:
                    # Simple condition evaluation for mode conversion
                    target_mode = rule["to_mode"]
                    if target_mode in self.opcodes[mnemonic]:
                        instruction.mode = self.get_addressing_mode_enum(target_mode)
                        opcode_details = self.opcodes[mnemonic][target_mode]
                        if isinstance(opcode_details, list) and len(opcode_details) > 0:
                            opcode_details[0] = self._convert_opcode_to_int(opcode_details[0])
                        return opcode_details
                elif isinstance(instruction.operand_value, int) and instruction.operand_value <= rule["threshold"]:
                    target_mode = rule["to_mode"]
                    if target_mode in self.opcodes[mnemonic]:
                        instruction.mode = self.get_addressing_mode_enum(target_mode)
                        opcode_details = self.opcodes[mnemonic][target_mode]
                        if isinstance(opcode_details, list) and len(opcode_details) > 0:
                            opcode_details[0] = self._convert_opcode_to_int(opcode_details[0])
                        return opcode_details
        
        return None
    
    def validate_instruction(self, instruction) -> bool:
        """Validate instruction using JSON rules."""
        mnemonic = instruction.mnemonic.upper() if instruction.mnemonic else ""
        mode = instruction.mode
        operand_value = instruction.operand_value
        
        # Convert mode enum to string for lookup
        mode_name = self.get_addressing_mode_name(mode)
        
        if not mode_name:
            return True
        
        # Check accumulator-only instructions
        accumulator_only = self.validation_rules.get("accumulator_only", {})
        if mnemonic in accumulator_only and mode_name in accumulator_only[mnemonic]:
            self.diagnostics.error(instruction.line_num,
                f"Instruction '{mnemonic}' must use inherent addressing (no operands).")
            return False
        
        # Check inherent-only instructions
        inherent_only = self.validation_rules.get("inherent_only", {})
        if mnemonic in inherent_only and mode_name not in inherent_only[mnemonic]:
            self.diagnostics.error(instruction.line_num,
                f"Instruction '{mnemonic}' must use inherent addressing (no operands).")
            return False
        
        # Check branch instruction valid modes
        branch_valid_modes = self.validation_rules.get("branch_valid_modes", {})
        if mnemonic in branch_valid_modes and mode_name not in branch_valid_modes[mnemonic]:
            valid_modes = ", ".join(branch_valid_modes[mnemonic])
            self.diagnostics.error(instruction.line_num,
                f"Branch instruction '{mnemonic}' requires {valid_modes} addressing.")
            return False
        
        # Check inherent warnings
        inherent_warnings = self.validation_rules.get("inherent_warnings", {})
        if mnemonic in inherent_warnings and mode_name not in inherent_warnings[mnemonic]:
            self.diagnostics.warning(instruction.line_num,
                f"Instruction '{mnemonic}' typically uses inherent addressing. Operands may be ignored.")
        
        # Check optimization hints
        optimization = self.validation_rules.get("optimization_hints", {})
        
        # Direct page optimization (6800 equivalent of zeropage)
        if "direct_page_optimization" in optimization:
            dp_opt = optimization["direct_page_optimization"]
            if (mnemonic in dp_opt["mnemonics"] and 
                mode_name == "EXTENDED" and 
                isinstance(operand_value, int) and 
                operand_value <= dp_opt["threshold"]):
                self.diagnostics.warning(instruction.line_num,
                    dp_opt["message"].format(value=operand_value))
        
        # Immediate range check
        if "immediate_range_check" in optimization:
            imm_check = optimization["immediate_range_check"]
            if (mode_name == "IMMEDIATE" and 
                isinstance(operand_value, int) and 
                operand_value > imm_check["max_value"]):
                exceptions = imm_check.get("exceptions", [])
                if mnemonic not in exceptions:
                    self.diagnostics.error(instruction.line_num,
                        imm_check["message"].format(value=operand_value, mnemonic=mnemonic))
                    return False
        
        return True
    
    def encode_instruction(self, instruction, symbol_table) -> bool:
        """Generic instruction encoding using JSON configuration."""
        from core.expression_evaluator import evaluate_expression
        
        mnemonic = instruction.mnemonic
        mode = instruction.mode

        details = self.get_opcode_details(instruction, symbol_table)
        if details is None:
            return False
            
        opcode, operand_size, _, _ = details

        try:
            val = evaluate_expression(instruction.operand_value, symbol_table, instruction.line_num)
            if operand_size == 0:
                instruction.machine_code = [opcode]
            elif operand_size > 0:
                if val is None:
                    raise ValueError(f"Mnemonic '{mnemonic}' requires an operand but none was provided.")
                if operand_size == 1:
                    # Handle relative branches
                    relative_mode = self.get_addressing_mode_enum("RELATIVE")
                    if mode == relative_mode:
                        offset = val - (instruction.address + 2)
                        if not -128 <= offset <= 127:
                            raise ValueError(f"Branch offset out of range: {offset}")
                        instruction.machine_code = [opcode, offset & 0xFF]
                    else:
                        if not 0 <= val < 256:
                            raise ValueError(f"Value out of range for 1-byte operand: {val}")
                        instruction.machine_code = [opcode, val & 0xFF]
                elif operand_size == 2:
                    # Check endianness from CPU info
                    endianness = self.cpu_info.get("endianness", "little")
                    if endianness == "little":
                        instruction.machine_code = [opcode, val & 0xFF, (val >> 8) & 0xFF]
                    else:  # big endian
                        instruction.machine_code = [opcode, (val >> 8) & 0xFF, val & 0xFF]
                else:
                    raise ValueError(f"Unsupported operand size: {operand_size}")
        except ValueError as e:
            self.diagnostics.error(instruction.line_num, str(e))
            return False
        return True



