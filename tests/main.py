# main.py (YAML-based template version)
import argparse
import re
import os

# Import JSON profiles dynamically - no custom classes needed
from emitter import Emitter # Keep for type hinting if needed
from expression_evaluator import evaluate_expression
from diagnostics import Diagnostics
from symbol_table import SymbolTable
from program import Program
from parser import Parser
from instruction import Instruction
from assembler import Assembler
import logging

# --- CPU Profile Template System ---
# This system allows dynamic loading of CPU profiles from JSON files
# and provides a template-based architecture for different CPU types

class CPUProfileFactory:
    """Factory for creating CPU profiles from YAML files."""
    
    def __init__(self):
        self.profiles_dir = os.path.join(os.path.dirname(__file__), "..", "compiler", "cpu_profiles")
        self._profile_cache = {}
        self._load_available_profiles()
    
    def _load_available_profiles(self):
        """Scan for available CPU profiles."""
        if not os.path.exists(self.profiles_dir):
            return
        
        # Get all YAML files
        files = os.listdir(self.profiles_dir)
        
        for file in files:
            cpu_name = None
            if file.endswith('.yaml'):
                cpu_name = file[:-5]
            elif file.endswith('.yml'):
                cpu_name = file[:-4]
            
            if cpu_name:
                self._profile_cache[cpu_name] = {
                    'file': os.path.join(self.profiles_dir, file)
                }
    
    def get_available_cpus(self) -> list[str]:
        """Get list of available CPU profiles."""
        return list(self._profile_cache.keys())
    
    def create_profile(self, cpu_name: str, diagnostics: Diagnostics):
        """Create a CPU profile instance."""
        cpu_name = cpu_name.lower()
        
        if cpu_name not in self._profile_cache:
            raise ValueError(f"CPU profile '{cpu_name}' not found. Available: {self.get_available_cpus()}")
        
        # Load profile using generic ConfigCPUProfile
        profile_info = self._profile_cache[cpu_name]
        profile_file = profile_info['file']
        
        from cpu_profile_base import ConfigCPUProfile
        return ConfigCPUProfile(diagnostics, profile_file)

# Initialize the profile factory
profile_factory = CPUProfileFactory()
SUPPORTED_CPUS = {cpu: cpu for cpu in profile_factory.get_available_cpus()}

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
    try:
        profile = profile_factory.create_profile(args.cpu, diagnostics)
    except ValueError as e:
        diagnostics.error(None, str(e))
        return False
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
        emitter.write_binary(program, output_file, profile)
        diagnostics.print_summary()
        return True
    else:
        diagnostics.print_summary()
        return False

if __name__ == "__main__":
    # Run the assembler and exit with an appropriate status code
    if not main():
        exit(1)
