"""
This module provides core functionality for sending AI metadata to Revenium.
"""
import os
import logging

# Set up logger
logger = logging.getLogger("revenium_middleware")
log_level = os.environ.get("REVENIUM_LOG_LEVEL", "INFO").upper()
try:
    logger.setLevel(getattr(logging, log_level))
except AttributeError:
    logger.setLevel(logging.INFO)
    logger.warning(f"Invalid log level: {log_level}, defaulting to INFO")

# Configure a basic handler if none exists
if not logger.handlers and not logging.root.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

from .metering import run_async_in_thread, shutdown_event, client
