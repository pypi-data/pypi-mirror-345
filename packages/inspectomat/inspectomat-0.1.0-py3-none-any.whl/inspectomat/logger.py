"""
Logging system for the cleaner package.
Provides consistent logging across all modules.
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any

# Default log levels
DEFAULT_CONSOLE_LEVEL = logging.INFO
DEFAULT_FILE_LEVEL = logging.DEBUG

# Default log format
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Default log file
DEFAULT_LOG_DIR = os.path.expanduser('~/.cleaner/logs')
DEFAULT_LOG_FILE = 'cleaner.log'

# Maximum log file size (10 MB)
MAX_LOG_SIZE = 10 * 1024 * 1024
# Number of backup log files
BACKUP_COUNT = 3

# Global logger dictionary to avoid creating multiple loggers for the same name
_loggers: Dict[str, logging.Logger] = {}

def setup_logging(
    console_level: int = DEFAULT_CONSOLE_LEVEL,
    file_level: int = DEFAULT_FILE_LEVEL,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True
) -> None:
    """
    Set up the root logger with console and file handlers.
    
    Args:
        console_level: Logging level for console output
        file_level: Logging level for file output
        log_format: Format string for log messages
        date_format: Format string for log message dates
        log_file: Path to the log file (default: ~/.cleaner/logs/cleaner.log)
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all logs, handlers will filter
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format, date_format)
    
    # Add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler if enabled
    if enable_file:
        if log_file is None:
            # Create default log directory if it doesn't exist
            os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)
            log_file = os.path.join(DEFAULT_LOG_DIR, DEFAULT_LOG_FILE)
        
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Name of the logger
        
    Returns:
        logging.Logger: Logger instance
    """
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    _loggers[name] = logger
    return logger

def set_log_level(level: int, logger_name: Optional[str] = None) -> None:
    """
    Set the log level for a specific logger or all loggers.
    
    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
        logger_name: Name of the logger to set the level for, or None for all loggers
    """
    if logger_name is None:
        # Set level for all loggers
        for logger in _loggers.values():
            logger.setLevel(level)
    elif logger_name in _loggers:
        # Set level for specific logger
        _loggers[logger_name].setLevel(level)

# Initialize logging with default settings
setup_logging()

# Create a default logger for the cleaner package
logger = get_logger('cleaner')
