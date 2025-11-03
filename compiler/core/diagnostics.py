"""
A dedicated module for handling all diagnostic output, including errors,
warnings, and informational messages.
"""
import logging

class Diagnostics:
    """Manages and displays diagnostic messages for the assembler."""
    def __init__(self, logger=None):
        self._error_count = 0
        self._warning_count = 0
        # Use provided logger or a null logger to avoid conditional checks
        self.logger = logger or logging.getLogger('null')

    def error(self, line_num, message):
        """Reports a compilation error to the console and the logger."""
        self._error_count += 1
        full_message = f"Error on line {line_num}: {message}" if line_num else f"Error: {message}"
        print(full_message)
        self.logger.error(full_message)

    def warning(self, line_num, message):
        """Reports a compilation warning to the console and the logger."""
        self._warning_count += 1
        full_message = f"Warning on line {line_num}: {message}" if line_num else f"Warning: {message}"
        print(full_message)
        self.logger.warning(full_message)

    def info(self, message):
        """Prints a general informational message to the console and the logger."""
        print(message)
        self.logger.info(message)

    def has_errors(self):
        """Returns True if any errors have been reported."""
        return self._error_count > 0

    def print_summary(self):
        """Prints a summary of the compilation results."""
        self.info("\n--- Assembly Summary ---")
        if self._error_count > 0:
            self.info(f"Assembly failed with {self._error_count} error(s) and {self._warning_count} warning(s).")
        else:
            self.info(f"Assembly successful with {self._warning_count} warning(s).")