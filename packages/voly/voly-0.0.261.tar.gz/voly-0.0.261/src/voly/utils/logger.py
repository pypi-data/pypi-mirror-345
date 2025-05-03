"""
Logger module for the Voly package.

This module provides a centralized logger configuration and
a decorator for error catching.
"""

import os
from datetime import datetime
import sys
from functools import wraps
import asyncio
from loguru import logger

# Remove the default handler first
logger.remove()

# Handler for console output - less verbose output
logger.add(
    sys.stderr,
    level="INFO",
    backtrace=False,  # Don't show traceback
    diagnose=False  # Don't show variables
)


def setup_file_logging(logs_dir="logs/"):
    """
    Set up file-based logging. This is optional and can be called
    by the end user if they want file-based logging.

    Parameters:
    logs_dir (str): Directory to store log files
    """
    os.makedirs(logs_dir, exist_ok=True)
    logger.add(
        os.path.join(logs_dir, "voly_{time:YYYY-MM-DD}.log"),
        level="INFO",
        rotation="00:00",
        retention="7 days",
        backtrace=True,  # Keep full traceback in file
        diagnose=True  # Keep variables in file
    )
    logger.info("File logging initialized")


# Decorator for error catching (supports both sync and async functions)
def catch_exception(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__}: {str(e)}")
            raise

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__}: {str(e)}")
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
