import logging
import os
import sys
from enum import Enum
from typing import Optional


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LoggingService:
    """Centralized logging service for testgen framework"""
    _instance = None
    _initialized = False
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance of LoggingService"""
        if cls._instance is None:
            cls._instance = LoggingService()
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger('testgen')
        self.formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.file_handler = None
        self.console_handler = None
        
    def initialize(self, 
                  debug_mode: bool = False, 
                  log_file: Optional[str] = None,
                  console_output: bool = True):
        """Initialize the logging service"""
        if LoggingService._initialized:
            return
        
        self.debug_mode = debug_mode
            
        # Set the base logging level
        level = LogLevel.DEBUG.value if debug_mode else LogLevel.INFO.value
        self.logger.setLevel(level)
        
        # Add console handler if requested
        if console_output:
            self.console_handler = logging.StreamHandler(sys.stdout)
            self.console_handler.setFormatter(self.formatter)
            self.console_handler.setLevel(level)
            self.logger.addHandler(self.console_handler)
        
        # Add file handler if path provided
        if log_file:
            # Ensure directory exists
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            self.file_handler = logging.FileHandler(log_file)
            self.file_handler.setFormatter(self.formatter)
            self.file_handler.setLevel(level)
            self.logger.addHandler(self.file_handler)
        
        # Mark as initialized
        LoggingService._initialized = True
        self.info(f"Logging initialized - Debug mode: {debug_mode}")
    
    def debug(self, message: str):
        """Log debug message"""
        if self.debug_mode:
            self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)


# Global accessor function for easy import and use
def get_logger():
    """Get the global logger instance"""
    logger = LoggingService.get_instance()
    
    # If logger hasn't been initialized yet, set up a basic configuration
    if not LoggingService._initialized:
        logger.initialize(debug_mode=False, console_output=True)
        
    return logger