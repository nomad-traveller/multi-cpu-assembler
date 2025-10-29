# cpu_profiles.py - CPU Profile Abstract Base Class
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from core.parser import Parser

class CPUProfile(ABC):
    @property
    @abstractmethod
    def opcodes(self) -> dict[str, dict[Any, list[Any]]]:
        ...

    @property
    @abstractmethod
    def branch_mnemonics(self) -> set[str]:
        ...

    @property
    @abstractmethod
    def addressing_modes_enum(self) -> type[Any]:
        ...

    @abstractmethod
    def parse_addressing_mode(self, operand_str: str) -> tuple[Any, Any]:
        ...

    @abstractmethod
    def parse_instruction(self, instruction, parser: 'Parser') -> None:
        """Parses a CPU instruction, setting its mode and operand value."""
        ...

    @abstractmethod
    def parse_directive(self, instruction, parser: 'Parser') -> None:
        """Parses an assembler directive, setting its operand value and size."""
        ...

    @abstractmethod
    def get_opcode_details(self, instruction, symbol_table) -> list[Any] | None:
        ...

    @abstractmethod
    def encode_instruction(self, instruction, symbol_table) -> bool:
        ...

# Import concrete CPU profile implementations (moved to avoid circular imports)
# These are imported conditionally in main.py and test files
