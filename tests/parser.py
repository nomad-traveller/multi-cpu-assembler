import re
from collections import namedtuple

from cpu_profile_base import ConfigCPUProfile
from diagnostics import Diagnostics
from instruction import Instruction
from program import Program
from expression_parser import ExpressionLexer, ExpressionParser

ParsedLine = namedtuple('ParsedLine', ['label', 'mnemonic', 'operand_str'])

class _LineParser:
    """A helper class to handle the syntactic parsing of a single line of text."""

    def __init__(self):
        """
        Initializes the _LineParser helper class.
        """

    def parse(self, line: str, logger) -> ParsedLine | None:
        """
        Parses a raw line of text into its label, mnemonic, and operand components.
        Handles comments and the special syntax for the EQU directive.
        """
        parse_text = self._strip_comment(line, logger)
        if not parse_text:
            return None

        label, parse_text = self._extract_label(parse_text, logger)

        if not parse_text:
            return ParsedLine(label, None, None)

        # No special EQU handling needed - directives are detected by profile

        return self._extract_mnemonic_and_operand(parse_text, label, logger)

    def _strip_comment(self, line: str, logger) -> str:
        """Removes comments and trailing whitespace from a line."""
        comment_index = line.find(';')
        if comment_index != -1:
            stripped = line[:comment_index].rstrip()
            logger.debug(f"Stripped comment, result: '{stripped}'")
            return stripped
        return line.rstrip()

    def _extract_label(self, text: str, logger) -> tuple[str | None, str]:
        """Extracts a colon-terminated label from the text, if present."""
        if ':' in text:
            label_part, rest = text.split(':', 1)
            label = label_part.strip().upper()
            logger.debug(f"Extracted label: '{label}', remaining text: '{rest.strip()}'")
            return label, rest.strip()
        return None, text

    def _extract_mnemonic_and_operand(self, text: str, existing_label: str | None, logger) -> ParsedLine:
        """Extracts the mnemonic and operand."""
        # Parse as a standard mnemonic and operand.
        parts = text.strip().split(maxsplit=2)
        
        # Handle special case: LABEL DIRECTIVE VALUE (without colon)
        # This allows directives like EQU to be written as "LABEL EQU $1234"
        if existing_label is None and len(parts) >= 3:
            # This could be "LABEL DIRECTIVE VALUE" format
            potential_label = parts[0].upper()
            potential_directive = parts[1].upper()
            # Check if the second part is a known directive that supports implicit labels
            # For now, we'll handle EQU specifically, but this could be profile-driven
            if potential_directive == "EQU":
                label = potential_label
                mnemonic = potential_directive
                operand_str = parts[2]
                logger.debug(f"Parsed directive with implicit label: '{label}' = '{operand_str}'")
                return ParsedLine(label, mnemonic, operand_str)
        
        # Standard parsing: MNEMONIC [OPERAND]
        mnemonic = parts[0].upper()
        operand_str = parts[1] if len(parts) > 1 else None
        return ParsedLine(existing_label, mnemonic, operand_str)

class Parser:
    def __init__(self, cpu_profile: ConfigCPUProfile, diagnostics: 'Diagnostics'):
        """
        Initializes the Parser with a CPU profile and a diagnostics object.

        Args:
            cpu_profile (ConfigCPUProfile): The CPU profile to use for instruction and directive parsing.
        """
        self.cpu_profile = cpu_profile
        self.diagnostics = diagnostics
        self.logger = diagnostics.logger
        # Instantiate the expression lexer and parser
        self._exp_lexer = ExpressionLexer()
        self._exp_parser = ExpressionParser()
        self._line_parser = _LineParser()

    def _validate_syntax(self, instruction: Instruction):
        """Validates instruction syntax for common mistakes."""
        # Check for invalid label names
        if instruction.label:
            if not re.match(r'^[A-Z_][A-Z0-9_]*$', instruction.label, re.IGNORECASE):
                self.diagnostics.warning(instruction.line_num,
                    f"Label '{instruction.label}' contains invalid characters. Labels should start with a letter or underscore and contain only letters, digits, and underscores.")

            if len(instruction.label) > 32:
                self.diagnostics.warning(instruction.line_num,
                    f"Label '{instruction.label}' is very long ({len(instruction.label)} characters). Consider using a shorter name.")

        # Check for suspicious operand patterns
        if instruction.operand_str:
            # Check for missing spaces around operators
            if '+' in instruction.operand_str and not re.search(r'\s+\+\s+', instruction.operand_str):
                self.diagnostics.warning(instruction.line_num,
                    f"Missing spaces around '+' operator in operand '{instruction.operand_str}'. Consider adding spaces for clarity.")

            # Check for invalid hex notation
            if re.search(r'\$[0-9A-F]*[G-Z]', instruction.operand_str, re.IGNORECASE):
                self.diagnostics.warning(instruction.line_num,
                    f"Invalid hex digit in operand '{instruction.operand_str}'. Hex digits should be 0-9, A-F.")

            # Check for potential decimal in hex context
            if re.search(r'\$[0-9]+\d*[A-F]', instruction.operand_str):
                self.diagnostics.warning(instruction.line_num,
                    f"Mixed decimal and hex digits in operand '{instruction.operand_str}'. This may not be what you intended.")

    def parse_operand_list(self, operand_str):
        """
        Parses a comma-separated list of operands into a list of AST nodes.

        Args:
            operand_str (str): The string containing the comma-separated operands.
        Returns:
            list: A list of AST nodes representing the parsed operands, or an empty list if there are no operands."""
        if not operand_str:
            return []
        parts = [p.strip() for p in operand_str.split(',')]
        values = []
        for p in parts:
            try:
                ast = self._exp_parser.parse(self._exp_lexer.tokenize(p))
                values.append(ast)
            except ValueError as e:
                self.logger.debug(f"Sly expression parser failed for operand '{p}'", exc_info=True)
                self.diagnostics.error(None, f"In expression '{p}': {e}")
                values.append(None) # Append None to indicate failure
        return values

    def _parse_directive(self, instr, mnemonic, operand_str):
        """
        Handles parsing of assembler directives.

        Args:
            instr (Instruction): The Instruction object to populate.
            mnemonic (str): The directive mnemonic (e.g., ".ORG", ".BYTE").
            operand_str (str): The operand string for the directive.
        """
        instr.directive = mnemonic
        self.cpu_profile.parse_directive(instr, self)

    def _parse_instruction(self, instr, mnemonic, operand_str):
        """
        Handles parsing of CPU instructions.
        Args:
            instr (Instruction): The Instruction object to populate.
        """
        """Handles parsing of CPU instructions."""
        instr.mnemonic = mnemonic
        self.cpu_profile.parse_instruction(instr, self)

    def parse_line(self, line, line_num):
        original_text = line.rstrip()
        self.logger.debug(f"--- Parsing line {line_num}: '{original_text}' ---")
        try:
            parsed_line = self._line_parser.parse(original_text, self.logger)
        except ValueError as e:
            self.logger.debug(f"Line parser failed for line: '{original_text}'", exc_info=True)
            self.diagnostics.error(line_num, str(e))
            return None

        if not parsed_line:
            return None

        self.logger.debug(f"Line parser result: {parsed_line}")
        instr = Instruction(line_num, original_text)
        instr.label = parsed_line.label
        instr.mnemonic = parsed_line.mnemonic
        instr.operand_str = parsed_line.operand_str

        # Enhanced syntax validation
        self._validate_syntax(instr)

        if not parsed_line.mnemonic: # Label-only line
            return instr

        # Parse the instruction using the CPU profile
        try:
            if instr.mnemonic:
                if self.cpu_profile.is_directive(instr.mnemonic):
                    instr.directive = instr.mnemonic
                    instr.mnemonic = None  # Clear mnemonic for directives
                    self.cpu_profile.parse_directive(instr, self)
                else:
                    self.cpu_profile.parse_instruction(instr, self)
        except ValueError as e:
            self.diagnostics.error(line_num, str(e))
            return None

        return instr

    def parse_source_file(self, source_file_path: str, program: 'Program'):
        """
        Reads a source file, parses each line, and populates the Program object.
        """
        try:
            with open(source_file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    instr = self.parse_line(line, line_num)
                    if self.diagnostics.has_errors():
                        # Stop parsing on the first error to avoid cascade failures
                        break
                    elif instr:
                        program.add_instruction(instr)
        except FileNotFoundError:
            self.logger.debug(f"File not found exception for path: '{source_file_path}'", exc_info=True)
            self.diagnostics.error(None, f"Source file not found at '{source_file_path}'")