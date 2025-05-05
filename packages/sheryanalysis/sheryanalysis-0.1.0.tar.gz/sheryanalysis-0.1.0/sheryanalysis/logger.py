"""
Logger module for sheryanalysis.
Provides logging functionality with different verbosity levels.
"""
import logging
import sys
from typing import Optional, Union, Literal

# Define log levels
LOG_LEVELS = {
    0: logging.WARNING,  # Minimal output
    1: logging.INFO,     # Normal output
    2: logging.DEBUG     # Verbose output
}

class SheryLogger:
    """
    Custom logger for sheryanalysis with configurable verbosity.
    
    Attributes:
        logger: The logging.Logger instance
        verbosity: The verbosity level (0=minimal, 1=normal, 2=verbose)
    """
    
    def __init__(self, verbosity: int = 1):
        """
        Initialize the logger with specified verbosity.
        
        Args:
            verbosity: Verbosity level (0=minimal, 1=normal, 2=verbose)
        """
        self.logger = logging.getLogger("sheryanalysis")
        self.verbosity = verbosity
        
        # Configure logger
        self._configure_logger()
    
    def _configure_logger(self) -> None:
        """Configure the logger with appropriate handlers and formatters."""
        # Clear any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
            
        # Set log level based on verbosity
        log_level = LOG_LEVELS.get(self.verbosity, logging.INFO)
        self.logger.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Create formatter
        if self.verbosity >= 2:
            # Detailed format for verbose mode
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        else:
            # Simple format for normal/minimal mode
            formatter = logging.Formatter('%(message)s')
            
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def set_verbosity(self, verbosity: int) -> None:
        """
        Change the verbosity level.
        
        Args:
            verbosity: New verbosity level (0=minimal, 1=normal, 2=verbose)
        """
        self.verbosity = verbosity
        self._configure_logger()
    
    def debug(self, msg: str) -> None:
        """Log a debug message."""
        self.logger.debug(msg)
    
    def info(self, msg: str) -> None:
        """Log an info message."""
        self.logger.info(msg)
    
    def warning(self, msg: str) -> None:
        """Log a warning message."""
        self.logger.warning(msg)
    
    def error(self, msg: str) -> None:
        """Log an error message."""
        self.logger.error(msg)
    
    def critical(self, msg: str) -> None:
        """Log a critical message."""
        self.logger.critical(msg)

# Create a default logger instance
default_logger = SheryLogger()

def get_logger(verbosity: Optional[int] = None) -> SheryLogger:
    """
    Get the default logger or create a new one with specified verbosity.
    
    Args:
        verbosity: Optional verbosity level (0=minimal, 1=normal, 2=verbose)
        
    Returns:
        SheryLogger: The logger instance
    """
    if verbosity is not None:
        default_logger.set_verbosity(verbosity)
    return default_logger
