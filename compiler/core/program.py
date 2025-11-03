from core.symbol_table import SymbolTable

class Program:
    def __init__(self, symbol_table: 'SymbolTable'):
        self.instructions = []
        self.symbol_table = symbol_table

    def add_instruction(self, instr):
        self.instructions.append(instr)