import os
from .diagnostics import Diagnostics

class Emitter:
    """
    Handles the output of the assembly process, including printing listings
    and writing the final binary file.
    """
    def __init__(self, diagnostics: 'Diagnostics'):
        self.diagnostics = diagnostics

    def print_pass_listing(self, title, program):
        """Prints a detailed listing of the program state after a pass."""
        self.diagnostics.info(f"--- {title} ---")
        header = f"{'Address':<8} {'Size':<5} {'Bytes':<20} {'Original Source'}"
        self.diagnostics.info(header)
        self.diagnostics.info("-" * (len(header) + 20))

        for instr in program.instructions:
            addr_str = f"{instr.address:04X}" if instr.address is not None else "----"
            size_str = str(instr.size)
            bytes_str = " ".join(f"{b:02X}" for b in instr.machine_code) if instr.machine_code is not None else ""

            self.diagnostics.info(f"{addr_str:<8} {size_str:<5} {bytes_str:<20} {instr.original_text}")
        self.diagnostics.info("") # Add a blank line for spacing

    def write_binary(self, program, output_file, profile):
        """Writes the assembled machine code to a binary file."""
        min_addr = float('inf')
        max_addr = float('-inf')
        for instr in program.instructions:
            if instr.address is not None and instr.size > 0:
                min_addr = min(min_addr, instr.address)
                max_addr = max(max_addr, instr.address + instr.size - 1)

        if min_addr != float('inf'):
            # Convert to integers for calculation
            min_addr_int = int(min_addr)
            max_addr_int = int(max_addr)
            mem_size = max_addr_int - min_addr_int + 1
            # Get fill byte from profile, default to 0x00 if not specified
            fill_byte_str = profile.cpu_info.get("fill_byte", "0x00")
            try:
                fill_byte = int(fill_byte_str, 0)
            except ValueError:
                fill_byte = 0x00  # Default to 0x00 on error
            data = bytearray([fill_byte] * mem_size)  # Use the profile's fill byte
            for instr in program.instructions:
                if instr.machine_code and instr.address is not None:
                    offset = instr.address - min_addr_int
                    # Ensure offset is within bounds of data array
                    if offset >= 0 and (offset + len(instr.machine_code)) <= len(data):
                        data[offset:offset + len(instr.machine_code)] = instr.machine_code
                    else:
                        self.diagnostics.warning(instr.line_num, f"Instruction at ${instr.address:04X} ({instr.original_text}) falls outside calculated memory image range. Skipping.")
            try:
                # Ensure to output directory exists
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                with open(output_file, 'wb') as f:
                    f.write(data)
                self.diagnostics.info(f"Machine code written to {output_file} ({mem_size} bytes, from ${min_addr_int:04X} to ${max_addr_int:04X})")
            except IOError as e:
                self.diagnostics.error(None, f"Error writing binary to '{output_file}': {e}")
                return False
        else:
            self.diagnostics.info("No machine code generated to write.")
        return True