"""Configure logger for runtime."""

import logging
import os

LOGGING_ENV_VAR = "UNION_SDK_LOGGING_LEVEL"
PACKAGE_NAME = "union_runtime"


def _init_global_logger():
    """Return True if logger is configured."""
    logging_level = int(os.getenv(LOGGING_ENV_VAR, logging.INFO))

    logger = logging.getLogger(PACKAGE_NAME)

    handler = logging.StreamHandler()
    handler.setLevel(logging_level)
    formatter = logging.Formatter(fmt="[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging_level)
