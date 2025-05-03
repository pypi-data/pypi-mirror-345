"""Logging configuration for the ZMP Markdown Translator service.

This module provides a centralized logging setup for consistent log formatting
across the application.
"""

import logging


def setup_logging():
    """Configure application-wide logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format=("%(asctime)s [%(levelname)s] " "%(name)s: %(message)s"),
    )
