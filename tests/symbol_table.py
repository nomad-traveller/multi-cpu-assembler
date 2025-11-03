from diagnostics import Diagnostics

class SymbolTable:
    def __init__(self, diagnostics: 'Diagnostics'):
        self._symbols = {}
        self.diagnostics = diagnostics

    def add(self, label, address, line_num):
        """Adds a symbol to the table. Returns False on duplicate."""
        if label in self._symbols:
            self.diagnostics.error(line_num, f"Duplicate label '{label}'")
            return False
        self._symbols[label] = address
        return True

    def resolve(self, symbol):
        """Resolves a symbol to its address. Returns None if not found."""
        return self._symbols.get(symbol)

    def get_printable(self):
        """Returns a dictionary formatted for printing."""
        return {k: f"${v:04X}" for k, v in self._symbols.items()}