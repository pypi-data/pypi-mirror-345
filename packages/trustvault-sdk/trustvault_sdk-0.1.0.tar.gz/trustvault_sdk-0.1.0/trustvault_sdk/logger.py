"""Logger setup for TrustVault SDK"""

import logging
import sys
import json

def get_logger():
    """Return a singleton logger for TrustVault SDK"""
    logger = logging.getLogger("trustvault")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def safe_log(record):
    """Safely log a record, catching and logging any logging errors"""
    logger = get_logger()
    try:
        logger.info(json.dumps(record, default=str))
    except Exception:
        logger.exception("TrustVault SDK error during logging")