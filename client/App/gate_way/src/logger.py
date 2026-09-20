"""Logger module for handling application-wide logging configuration."""

import logging
import os
from datetime import datetime
from typing import Optional

# Logging constants
LOG_FORMAT       = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT  = "%Y%m%d_%H%M%S"
DEFAULT_LOG_NAME = "Gateway"

_logger: Optional[logging.Logger] = None

def setup_logger(name: str = DEFAULT_LOG_NAME, create_file: bool = False) -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        name: The name of the module requesting the logger.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    global _logger
    
    if _logger is not None:
        return logging.getLogger(name)
        
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
        ],
    )

    if create_file:
        if not os.path.exists(f"{name}_logs"):
            os.makedirs(f"{name}_logs")

        log_file: str = os.path.join(
            f"{name}_logs", f"{name}_{datetime.now().strftime(LOG_DATE_FORMAT)}.log"
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.getLogger().addHandler(file_handler)

    _logger = logging.getLogger(name)
    _logger.info("Logger setup complete")
    
    return _logger 