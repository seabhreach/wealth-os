"""Logging configuration for Wealth OS."""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the process-wide logging defaults for the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
