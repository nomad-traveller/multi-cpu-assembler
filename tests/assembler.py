from cpu_profile_base import ConfigCPUProfile
from symbol_table import SymbolTable
from diagnostics import Diagnostics
from program import Program
from expression_evaluator import evaluate_expression

class Assembler:
    def __init__(self, cpu_profile: ConfigCPUProfile, symbol_table: 'SymbolTable', diagnostics: 'Diagnostics'):
        self.cpu_profile = cpu_profile
        self.symbol_table = symbol_table
        self.diagnostics = diagnostics

    def _first_pass(self, program: 'Program', start_address):
        current_address = start_address
        for instr in program.instructions:
            if instr.directive:
                # Get directive info from profile
                directive_info = self.cpu_profile.get_directive_info(instr.directive)
                if not directive_info:
                    self.diagnostics.error(instr.line_num, f"Unknown directive '{instr.directive}'")
                    return False

                directive_type = directive_info.get("type")

                if directive_type == "symbol_equate":  # e.g., EQU
                    if not instr.label:
                        self.diagnostics.error(instr.line_num, f"Directive '{instr.directive}' requires a label.")
                        return False
                    equ_value = evaluate_expression(instr.operand_value, self.symbol_table, instr.line_num, current_address)
                    if equ_value is None:
                        return False
                    if not self.symbol_table.add(instr.label, equ_value, instr.line_num):
                        return False
                    instr.size = 0
                    # Don't add label to symbol table again (already handled by EQU)
                    
                elif directive_type == "origin_set":  # e.g., .ORG
                    org_address = evaluate_expression(instr.operand_value, self.symbol_table, instr.line_num, current_address)
                    if org_address is None:
                        return False
                    current_address = org_address
                    instr.address = current_address
                    instr.size = 0
                    # Add label if present (labels after .ORG point to new address)
                    if instr.label:
                        if not self.symbol_table.add(instr.label, current_address, instr.line_num):
                            return False
                            
                elif directive_type == "data_define":  # e.g., .BYTE, .WORD
                    instr.address = current_address
                    size_multiplier = directive_info.get("size_multiplier", 1)
                    # Size is calculated based on number of operands
                    instr.size = len(instr.operand_value) * size_multiplier
                    current_address += instr.size
                    # Add label if present (labels before data directives point to data)
                    if instr.label:
                        if not self.symbol_table.add(instr.label, instr.address, instr.line_num):
                            return False
                            
                elif directive_type == "storage_define":  # e.g., .DS
                    instr.address = current_address
                    # Size is the value of the operand (number of bytes to reserve)
                    storage_size = evaluate_expression(instr.operand_value, self.symbol_table, instr.line_num, current_address)
                    if storage_size is None:
                        return False
                    instr.size = storage_size
                    current_address += instr.size
                    # Add label if present (labels before storage directives point to storage)
                    if instr.label:
                        if not self.symbol_table.add(instr.label, instr.address, instr.line_num):
                            return False
                            
                else:
                    # Unknown directive type - try legacy profile handling
                    try:
                        current_address = self.cpu_profile.handle_directive_pass1(instr, self.symbol_table, current_address)
                        # For legacy compatibility, check if this is a symbol_equate type
                        if directive_type != "symbol_equate" and instr.label:
                            if not self.symbol_table.add(instr.label, current_address, instr.line_num):
                                return False
                    except ValueError as e:
                        self.diagnostics.error(instr.line_num, str(e))
                        return False
                continue

            if instr.label:
                if not self.symbol_table.add(instr.label, current_address, instr.line_num):
                    return False

            if instr.mnemonic:
                instr.address = current_address
                details = self.cpu_profile.get_opcode_details(instr, None)
                if details:
                    instr.size = 1 + details[1]
                else:
                    if hasattr(instr.mode, 'name'):
                        mode_name = instr.mode.name
                    else:
                        # For JSON profiles, mode is an integer
                        mode_name = f"MODE_{instr.mode}" if instr.mode is not None else "UNKNOWN"
                    self.diagnostics.error(instr.line_num, f"Invalid mnemonic '{instr.mnemonic}' or addressing mode '{mode_name}'.")
                    instr.size = 0
                    return False
                current_address += instr.size
            else:
                instr.size = 0
        self.diagnostics.info(f"Pass 1 complete. Symbol table: {self.symbol_table.get_printable()}")
        return True

    def _second_pass(self, program: 'Program'):
        for instr in program.instructions:
            if instr.directive:
                # Let the profile handle its own directive logic
                if not self.cpu_profile.handle_directive_pass2(instr, self.symbol_table):
                    return False
            elif instr.mnemonic:
                try:
                    if not self.cpu_profile.encode_instruction(instr, self.symbol_table):
                        return False
                except ValueError as e:
                    self.diagnostics.logger.debug(f"Exception during instruction encoding on line {instr.line_num}", exc_info=True)
                    self.diagnostics.error(instr.line_num, f"Error encoding {instr.mnemonic}: {e}")
                    return False
        self.diagnostics.info("Pass 2 complete.")
        return True

    def _validation_pass(self, program: 'Program'):
        """Validates instructions for common assembly mistakes."""
        for instr in program.instructions:
            if instr.mnemonic and not self.cpu_profile.validate_instruction(instr):
                return False
        return True

    def assemble(self, program: 'Program', start_address=0x0000):
        if not self._first_pass(program, start_address):
            return False
        if not self._validation_pass(program):
            return False
        if not self._second_pass(program):
            return False
        return True