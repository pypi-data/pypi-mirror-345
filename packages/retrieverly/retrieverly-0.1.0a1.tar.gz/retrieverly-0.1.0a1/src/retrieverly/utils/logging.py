"""
Logging utilities for Retrieverly.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "retrieverly", level: Optional[int] = None) -> logging.Logger:
    """
    Set up and configure logger.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level based on parameters or environment variables
    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.INFO)
    
    # Only add handlers if none exist
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(stream=sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to handler
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger


# Create default logger
logger = setup_logger()