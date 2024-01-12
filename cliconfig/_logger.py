# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Logging functions for cliconfig."""
import logging
import sys
from logging import Logger


def create_logger() -> Logger:
    """Create cliconfig logger."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
