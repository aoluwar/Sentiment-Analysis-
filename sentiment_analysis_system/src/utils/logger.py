import logging
import os
import sys
from logging.handlers import RotatingFileHandler
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from config.settings import LOGGING_CONFIG

def setup_logger(name=None):
    """Set up logger with consistent formatting and handlers
    
    Args:
        name: Logger name (optional)
        
    Returns:
        Configured logger instance
    """
    # Get logger
    logger = logging.getLogger(name)
    
    # Skip if logger is already configured
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, LOGGING_CONFIG.get("level", "INFO"))
    logger.setLevel(log_level)
    
    # Create formatters
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_format)
    console_handler.setLevel(log_level)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Create file handler if enabled
    if LOGGING_CONFIG.get("file_logging_enabled", False):
        # Create logs directory if it doesn't exist
        log_dir = LOGGING_CONFIG.get("log_dir", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate log file name
        log_file = os.path.join(
            log_dir,
            f"{name or 'sentiment_analysis'}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # Create file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOGGING_CONFIG.get("max_file_size_bytes", 10485760),  # 10 MB
            backupCount=LOGGING_CONFIG.get("backup_count", 5)
        )
        file_handler.setFormatter(file_format)
        file_handler.setLevel(log_level)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
    
    return logger