import logging
import os
import sys
from datetime import datetime

# Import colorama for cross-platform color support
try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=False)  # Initialize colorama
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

# Color definitions - will use colorama if available, otherwise ANSI escape codes
if HAS_COLORAMA:
    COLORS = {
        'RESET': Style.RESET_ALL,
        'GREEN': Fore.GREEN,  # Info
        'YELLOW': Fore.YELLOW,  # Warning
        'RED': Fore.RED,  # Error
        'VIOLET': Fore.MAGENTA,  # Debug (using MAGENTA as closest to violet)
        'BOLD': Style.BRIGHT,
        'UNDERLINE': '\033[4m'  # Colorama doesn't have underline, fallback to ANSI
    }
else:
    # Fallback to ANSI color codes for terminal output
    COLORS = {
        'RESET': '\033[0m',
        'GREEN': '\033[32m',  # Info
        'YELLOW': '\033[33m',  # Warning
        'RED': '\033[31m',  # Error
        'VIOLET': '\033[35m',  # Debug
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages based on level."""
    
    FORMATS = {
        logging.DEBUG: COLORS['VIOLET'] + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + COLORS['RESET'],
        logging.INFO: COLORS['GREEN'] + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + COLORS['RESET'],
        logging.WARNING: COLORS['YELLOW'] + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + COLORS['RESET'],
        logging.ERROR: COLORS['RED'] + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + COLORS['RESET'],
        logging.CRITICAL: COLORS['BOLD'] + COLORS['RED'] + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + COLORS['RESET'],
    }
    
    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def setup_logger(name, enable_file_logging=False, log_file=None):
    """Set up and configure a logger with colored console output and optional file logging.
    
    Args:
        name (str): Name of the logger
        enable_file_logging (bool): Whether to enable logging to a file
        log_file (str, optional): Path to the log file. If None, a default path is used
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:  
        logger.removeHandler(handler)
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Default console level is INFO
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # File handler if enabled
    if enable_file_logging:
        if log_file is None:
            # Default log file in logs directory
            logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = os.path.join(logs_dir, f'pixi_{timestamp}.log')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                       datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
    
    return logger


def get_logger(name):
    """Get an existing logger or create a new one if it doesn't exist.
    
    Args:
        name (str): Name of the logger
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
