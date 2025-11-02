# main.py (JSON-based template version)
import argparse
import re
import os
import importlib
import json

# Import JSON profiles dynamically - no custom classes needed
from core.emitter import Emitter # Keep for type hinting if needed
from core.expression_evaluator import evaluate_expression
from core.diagnostics import Diagnostics
from core.symbol_table import SymbolTable
from core.program import Program
from core.parser import Parser
from core.instruction import Instruction
from core.assembler import Assembler
import logging

# --- CPU Profile Template System ---
# This system allows dynamic loading of CPU profiles from JSON files
# and provides a template-based architecture for different CPU types

class CPUProfileFactory:
    """Factory for creating CPU profiles from JSON files and templates."""
    
    def __init__(self):
        self.profiles_dir = os.path.join(os.path.dirname(__file__), "cpu_profiles")
        self._profile_cache = {}
        self._load_available_profiles()
    
    def _load_available_profiles(self):
        """Scan for available CPU profiles."""
        if not os.path.exists(self.profiles_dir):
            return
        
        for file in os.listdir(self.profiles_dir):
            if file.endswith('.json'):
                cpu_name = file[:-5]  # Remove .json extension
                self._profile_cache[cpu_name] = {
                    'json_file': os.path.join(self.profiles_dir, file),
                    'class': None
                }
    
    def get_available_cpus(self) -> list[str]:
        """Get list of available CPU profiles."""
        return list(self._profile_cache.keys())
    
    def create_profile(self, cpu_name: str, diagnostics: Diagnostics):
        """Create a CPU profile instance."""
        cpu_name = cpu_name.lower()
        
        if cpu_name not in self._profile_cache:
            raise ValueError(f"CPU profile '{cpu_name}' not found. Available: {self.get_available_cpus()}")
        
        # No special handling needed - all profiles use generic JSONCPUProfile
        
        # Generic JSON profile loading
        profile_info = self._profile_cache[cpu_name]
        json_file = profile_info['json_file']
        
        # Try to load a custom profile class if it exists
        class_file = os.path.join(self.profiles_dir, f"json_{cpu_name}_profile.py")
        if os.path.exists(class_file):
            module_name = f"cpu_profiles.json_{cpu_name}_profile"
            class_name = f"JSON{cpu_name.upper().replace('-', '')}Profile"
            
            try:
                module = importlib.import_module(module_name)
                profile_class = getattr(module, class_name)
                return profile_class(diagnostics)
            except (ImportError, AttributeError):
                pass
        
        # Fall back to generic JSON profile
        from cpu_profile_base import JSONCPUProfile
        return JSONCPUProfile(diagnostics, json_file)

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
