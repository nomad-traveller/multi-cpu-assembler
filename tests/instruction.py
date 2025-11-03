from typing import Optional, List, Any
from diagnostics import Diagnostics

class Instruction:
    def __init__(self, line_num: int, original_text: str = ""):
        self.line_num: int = line_num
        self.original_text: str = original_text
        self.label: Optional[str] = None
        self.mnemonic: Optional[str] = None
        self.operand_str: Optional[str] = None
        self.mode: Optional[Any] = None  # AddressingMode enum
        self.operand_value: Optional[Any] = None  # Can be int, str, or AST node
        self.directive: Optional[str] = None
        self.address: Optional[int] = None
        self.size: int = 0
        self.machine_code: Optional[List[int]] = None

    def to_dict(self):
        """Serializes the instruction's state to a dictionary for debugging."""
        return {
            "line_num": self.line_num,
            "original_text": self.original_text,
            "label": self.label,
            "mnemonic": self.mnemonic,
            "operand_str": self.operand_str,
            "mode": self.mode.name if self.mode else None,
            "operand_value": self.operand_value,
            "directive": self.directive,
            "address": self.address,
            "size": self.size,
            "machine_code": self.machine_code,
        }

    def validate(self, diagnostics: 'Diagnostics'):
        """Checks for logical consistency in the parsed instruction. Returns True if valid."""
        if self.mnemonic and self.directive:
            diagnostics.error(self.line_num, f"Instruction has both mnemonic '{self.mnemonic}' and directive '{self.directive}'.")
            return False
        if self.mnemonic and self.mode is None:
            diagnostics.error(self.line_num, f"Mnemonic '{self.mnemonic}' is missing a valid addressing mode.")
            return False
        return True