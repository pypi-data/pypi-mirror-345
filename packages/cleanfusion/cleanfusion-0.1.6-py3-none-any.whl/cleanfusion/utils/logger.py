"""
Logger module for consistent logging across the library.
"""

import logging
import os
import sys
from datetime import datetime

class Logger:
    """
    A centralized logger for the cleanfusion library.
    
    Features:
    - Console and file logging
    - Configurable log levels
    - Formatted log messages with timestamps
    - Singleton pattern to ensure consistent logging across modules
    """
    
    _instance = None
    
    def __new__(cls, log_level=logging.INFO, log_file=None):
        """
        Create a singleton logger instance.
        
        Parameters
        ----------
        log_level : int, default=logging.INFO
            The logging level to use.
        log_file : str, default=None
            Path to the log file. If None, logs only to console.
        
        Returns
        -------
        Logger
            The singleton logger instance.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(log_level, log_file)
        return cls._instance
    
    def _initialize(self, log_level, log_file):
        """Initialize the logger with handlers and formatters."""
        self.logger = logging.getLogger('cleanfusion')
        self.logger.setLevel(log_level)
        self.logger.handlers = []  # Clear any existing handlers
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Create file handler if log_file is provided
        if log_file:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def set_level(self, level):
        """
        Set the logging level.
        
        Parameters
        ----------
        level : int
            The logging level to set.
        """
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)
    
    def add_file_handler(self, log_file):
        """
        Add a file handler to the logger.
        
        Parameters
        ----------
        log_file : str
            Path to the log file.
        """
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message):
        """Log an error message."""
        self.logger.error(message)
    
    def critical(self, message):
        """Log a critical message."""
        self.logger.critical(message)
    
    def exception(self, message):
        """Log an exception message with traceback."""
        self.logger.exception(message)
