"""
Utility modules for the synthai package.
"""

import logging
import sys

# Set up logging configuration
def setup_logging(level=logging.INFO):
    """Set up logging configuration for synthai.
    
    Args:
        level: Logging level to use.
    """
    logger = logging.getLogger("synthai")
    
    if not logger.handlers:
        logger.setLevel(level)
        
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(handler)
    
    return logger

# Initialize logger with default settings
logger = setup_logging()

__all__ = ["setup_logging", "logger"]