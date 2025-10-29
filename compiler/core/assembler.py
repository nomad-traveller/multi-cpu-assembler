from cpu_profile_base import CPUProfile
from .symbol_table import SymbolTable
from .diagnostics import Diagnostics
from .program import Program
from .expression_evaluator import evaluate_expression

class Assembler:
    def __init__(self, cpu_profile: 'CPUProfile', symbol_table: 'SymbolTable', diagnostics: 'Diagnostics'):
        self.cpu_profile = cpu_profile
        self.symbol_table = symbol_table
        self.diagnostics = diagnostics

    def _first_pass(self, program: 'Program', start_address):
        current_address = start_address
        for instr in program.instructions:
            if instr.directive == "EQU":
                # For EQU, we must evaluate the expression and add the *result* to the symbol table.
                equ_value = evaluate_expression(instr.operand_value, self.symbol_table, instr.line_num)
                if equ_value is None:
                    return False # Error already reported
                if not self.symbol_table.add(instr.label, equ_value, instr.line_num):
                    return False
                instr.size = 0
                continue
            if instr.directive == ".ORG":
                # The operand_value from the parser is a token list/string.
                # We must evaluate it to get the integer address.
                org_address = evaluate_expression(instr.operand_value, self.symbol_table, instr.line_num)
                if org_address is None:
                    return False # Error already reported by evaluator
                current_address = org_address
                instr.address = current_address
                instr.size = 0

            if instr.label:
                if not self.symbol_table.add(instr.label, current_address, instr.line_num):
                    return False

            if instr.directive in (".BYTE", ".WORD"):
                instr.address = current_address
                current_address += instr.size
            elif instr.mnemonic:
                instr.address = current_address
                details = self.cpu_profile.get_opcode_details(instr, None)
                if details:
                    instr.size = 1 + details[1]
                else:
                    mode_name = instr.mode.name if instr.mode else "UNKNOWN"
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
            if instr.directive == ".BYTE":
                machine_code = []
                for v in instr.operand_value:
                    val = evaluate_expression(v, self.symbol_table, instr.line_num)
                    if val is None:
                        self.diagnostics.error(instr.line_num, f"Undefined symbol '{v}' in .BYTE directive.")
                        return False
                    if not 0 <= val < 256:
                        self.diagnostics.error(instr.line_num, f"Byte value '{val}' out of range (0-255).")
                        return False
                    machine_code.append(val & 0xFF)
                instr.machine_code = machine_code
            elif instr.directive == ".WORD":
                machine_code = []
                for v in instr.operand_value:
                    val = evaluate_expression(v, self.symbol_table, instr.line_num)
                    if val is None:
                        self.diagnostics.error(instr.line_num, f"Undefined symbol '{v}' in .WORD directive.")
                        return False
                    if not 0 <= val < 65536:
                        self.diagnostics.error(instr.line_num, f"Word value '{val}' out of range (0-65535).")
                        return False
                    machine_code.extend([val & 0xFF, (val >> 8) & 0xFF])
                instr.machine_code = machine_code
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