# cpu_profiles.py - CPU Profile Abstract Base Class
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING
import json
import os
import re
from enum import Enum

if TYPE_CHECKING:
    from core.parser import Parser


class JSONCPUProfile:
    """JSON-based CPU Profile that loads configuration from JSON files."""
    
    def __init__(self, diagnostics, json_file_path: str):
        self.diagnostics = diagnostics
        self._load_profile(json_file_path)
    
    def _load_profile(self, json_file_path: str):
        """Load CPU profile from JSON file."""
        try:
            with open(json_file_path, 'r') as f:
                self._profile_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"CPU profile file not found: {json_file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in CPU profile {json_file_path}: {e}")
    
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
        return self.addressing_modes.get(mode_name)
    
    def parse_addressing_mode(self, operand_str: str) -> tuple[Any, Any]:
        """Parse addressing mode using JSON patterns."""
        operand_str = operand_str.strip().upper()
        if not operand_str:
            return (self.get_addressing_mode_enum("IMPLIED"), None)
        
        for pattern_info in self.addressing_mode_patterns:
            pattern = pattern_info["pattern"]
            mode_name = pattern_info["mode"]
            group_idx = pattern_info.get("group_index")
            flags = pattern_info.get("flags", [])
            
            # Compile regex with flags
            regex_flags = 0
            if "IGNORECASE" in flags:
                regex_flags |= re.IGNORECASE
            
            compiled_pattern = re.compile(pattern, regex_flags)
            match = compiled_pattern.match(operand_str)
            if match:
                mode = self.get_addressing_mode_enum(mode_name)
                value = None
                
                if group_idx is not None:
                    val_str = match.group(group_idx)
                    if val_str.startswith('$'):
                        value = int(val_str[1:], 16)
                    elif val_str.isdigit():
                        value = int(val_str)
                    else:
                        value = val_str
                
                return (mode, value)
        
        return (None, None)
    
    def parse_instruction(self, instruction, parser: 'Parser') -> None:
        """Parse CPU instruction using JSON configuration."""
        operand_str = instruction.operand_str
        
        if not operand_str:
            instruction.mode = self.get_addressing_mode_enum("IMPLIED")
            return

        expression_str = operand_str
        if operand_str.startswith('#'):
            expression_str = operand_str[1:]

        mode, _ = self.parse_addressing_mode(operand_str)
        if mode:
            instruction.mode = mode
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
        mode_name = None
        for name, value in self.addressing_modes.items():
            if value == mode:
                mode_name = name
                break
        
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
        mode_name = None
        for name, value in self.addressing_modes.items():
            if value == mode:
                mode_name = name
                break
        
        if mode_name and mode_name in self.opcodes[mnemonic]:
            return self.opcodes[mnemonic][mode_name]
        
        return None
    
    def validate_instruction(self, instruction) -> bool:
        """Validate instruction using JSON rules."""
        mnemonic = instruction.mnemonic.upper() if instruction.mnemonic else ""
        mode = instruction.mode
        operand_value = instruction.operand_value
        
        # Convert mode enum to string for lookup
        mode_name = None
        for name, value in self.addressing_modes.items():
            if value == mode:
                mode_name = name
                break
        
        if not mode_name:
            return True
        
        # Check accumulator-only instructions
        accumulator_only = self.validation_rules.get("accumulator_only", {})
        if mnemonic in accumulator_only and mode_name in accumulator_only[mnemonic]:
            self.diagnostics.error(instruction.line_num,
                f"Instruction '{mnemonic}' does not support {mode_name.lower()} addressing mode. Use accumulator mode (A) instead.")
            return False
        
        # Check branch instructions
        branch_relative = self.validation_rules.get("branch_relative_only", {})
        if mnemonic in branch_relative and mode_name in branch_relative[mnemonic]:
            self.diagnostics.error(instruction.line_num,
                f"Branch instruction '{mnemonic}' cannot use {mode_name.lower()} addressing. Branches are always relative.")
            return False
        
        # Check register warnings
        register_warnings = self.validation_rules.get("register_warnings", {})
        if mnemonic in register_warnings and operand_value in register_warnings[mnemonic]:
            self.diagnostics.warning(instruction.line_num,
                f"Instruction '{mnemonic}' uses {operand_value} register, but operand suggests {register_warnings[mnemonic][0]} register usage.")
        
        # Check optimization hints
        optimization = self.validation_rules.get("optimization_hints", {})
        
        # Zero page optimization
        if "zeropage_optimization" in optimization:
            zp_opt = optimization["zeropage_optimization"]
            if (mnemonic in zp_opt["mnemonics"] and 
                mode_name == "ABSOLUTE" and 
                isinstance(operand_value, int) and 
                operand_value <= zp_opt["threshold"]):
                self.diagnostics.warning(instruction.line_num,
                    zp_opt["message"].format(value=operand_value))
        
        # Immediate range check
        if "immediate_range_check" in optimization:
            imm_check = optimization["immediate_range_check"]
            if (mode_name == "IMMEDIATE" and 
                isinstance(operand_value, int) and 
                operand_value > imm_check["max_value"]):
                self.diagnostics.error(instruction.line_num,
                    imm_check["message"].format(value=operand_value))
                return False
        
        # JMP indirect warning
        if "jmp_indirect_warning" in optimization:
            jmp_warn = optimization["jmp_indirect_warning"]
            if (mnemonic == "JMP" and 
                mode_name == "INDIRECT" and 
                isinstance(operand_value, int) and 
                eval(jmp_warn["condition"].replace("value", str(operand_value)))):
                self.diagnostics.warning(instruction.line_num,
                    jmp_warn["message"].format(value=operand_value))
        
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
                    if mode == self.get_addressing_mode_enum("RELATIVE"):
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


class CPUProfile(JSONCPUProfile):
    """Backward compatibility class."""
    
    def __init__(self, diagnostics, json_file_path: str | None = None):
        if json_file_path:
            super().__init__(diagnostics, json_file_path)
        else:
            self.diagnostics = diagnostics
