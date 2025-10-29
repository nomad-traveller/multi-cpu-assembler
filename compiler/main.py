# main.py (corrected version)
import argparse
import re

from cpu_profiles.c6502.c6502_profile import C6502Profile
from cpu_profiles.c6800.c6800_profile import C6800Profile
from cpu_profiles.c8086.c8086_profile import C8086Profile
from core.emitter import Emitter # Keep for type hinting if needed
from core.expression_evaluator import evaluate_expression
from core.diagnostics import Diagnostics
from core.symbol_table import SymbolTable
from core.program import Program
from core.parser import Parser
from core.instruction import Instruction
from core.assembler import Assembler
import logging

# --- Profile Factory ---
# This dictionary maps a CPU name to its corresponding profile class.
# It makes the assembler easily extensible with new CPU profiles.
SUPPORTED_CPUS = {
    "65c02": C6502Profile,
    "6800": C6800Profile,
    "8086": C8086Profile,
    # To add support for another CPU, you would:
    # 1. Import its profile class (e.g., from cpu_profiles import C8080Profile)
    # 2. Add an entry here (e.g., "8080": C8080Profile)
}

def parse_args() -> argparse.Namespace:
    """Parses and returns command-line arguments."""
    parser = argparse.ArgumentParser(description="A multi-CPU assembler.")
    parser.add_argument("source_file", help="Assembly source file")
    parser.add_argument("-o", "--output", help="Output binary file")
    parser.add_argument("--cpu", default="65c02", choices=SUPPORTED_CPUS.keys(), help="The target CPU profile.")
    parser.add_argument("--log-file", help="Specify a file to write detailed logs to.")
    parser.add_argument("--start-address", type=lambda x: int(x, 0), default=0x0000, help="Starting address (e.g., 0x8000)")
    return parser.parse_args()

def setup_logging(log_file: str | None):
    """Configures the logging system."""
    if log_file:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=log_file,
            filemode='w'
        )
        return logging.getLogger()
    return None

def main() -> bool:
    """
    The main entry point for the assembler application.
    """
    args = parse_args()
    logger = setup_logging(args.log_file)
    diagnostics = Diagnostics(logger)

    # --- Composition Root: Instantiate and wire up all components ---
    profile_class = SUPPORTED_CPUS.get(args.cpu)
    if not profile_class:
        diagnostics.error(None, f"CPU profile '{args.cpu}' is not supported.")
        return False

    profile = profile_class(diagnostics)
    symbol_table = SymbolTable(diagnostics)
    parser = Parser(profile, diagnostics)
    program = Program(symbol_table)
    assembler = Assembler(profile, symbol_table, diagnostics)
    emitter = Emitter(diagnostics)

    # --- Execution Flow ---
    parser.parse_source_file(args.source_file, program)

    if diagnostics.has_errors():
        diagnostics.print_summary()
        return False

    if assembler.assemble(program, args.start_address):
        output_file = args.output or f"{args.source_file}.bin"
        emitter.print_pass_listing("Final Assembly Listing", program)
        emitter.write_binary(program, output_file)
        diagnostics.print_summary()
        return True
    else:
        diagnostics.print_summary()
        return False

if __name__ == "__main__":
    # Run the assembler and exit with an appropriate status code
    if not main():
        exit(1)
