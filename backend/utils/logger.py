"""
Logging configuration for the multiagent system.
"""

import logging
import sys
from typing import Optional
try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    try:
        import json
        
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': self.formatTime(record),
                    'name': record.name,
                    'level': record.levelname,
                    'message': record.getMessage()
                }
                return json.dumps(log_entry)
        
        jsonlogger = type('jsonlogger', (), {'JsonFormatter': JsonFormatter})()
    except ImportError:
        jsonlogger = None

try:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
except ImportError:
    AzureLogHandler = None
import os

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Set up a logger with Azure Application Insights integration."""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create JSON formatter for structured logging
    if jsonlogger:
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
    else:
        # Fallback to standard formatter
        json_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    console_handler.setFormatter(json_formatter)
    
    # Add console handler
    logger.addHandler(console_handler)
    
    # Add Azure Application Insights handler if connection string is available
    app_insights_conn_str = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn_str and AzureLogHandler:
        try:
            azure_handler = AzureLogHandler(
                connection_string=app_insights_conn_str
            )
            azure_handler.setLevel(getattr(logging, level.upper()))
            azure_handler.setFormatter(json_formatter)
            logger.addHandler(azure_handler)
        except Exception as e:
            logger.warning(f"Failed to initialize Azure log handler: {str(e)}")
    
    return logger

class LogContext:
    """Context manager for adding context to logs."""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)

def log_function_call(func):
    """Decorator to log function calls."""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed with error: {str(e)}")
            raise
    
    return wrapper

async def log_async_function_call(func):
    """Decorator to log async function calls."""
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.info(f"Calling async {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Async function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Async function {func.__name__} failed with error: {str(e)}")
            raise
    
    return wrapper
