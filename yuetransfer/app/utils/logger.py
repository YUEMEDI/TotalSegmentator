"""
YueTransfer Logging Utility
Provides structured logging for the application
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(config):
    """Set up application logging"""
    
    # Create logs directory
    log_dir = os.path.dirname(config.LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler with rotation
            RotatingFileHandler(
                config.LOG_FILE,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            # Console handler for development
            logging.StreamHandler() if config.DEBUG else logging.NullHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('paramiko').setLevel(logging.WARNING)
    
    logger = logging.getLogger('yuetransfer')
    logger.info(f"YueTransfer logging initialized - Level: {config.LOG_LEVEL}")
    
    return logger

def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(f'yuetransfer.{name}')

class LoggerMixin:
    """Mixin class to add logging to other classes"""
    
    @property
    def logger(self):
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger 