"""Logging configuration for the application."""

import logging
import sys
from typing import Any

from app.config import settings


def setup_logging() -> None:
    """Configure logging for the application."""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    # Format: timestamp | level | logger | message | extras
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    logger.addHandler(console_handler)

    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.debug else logging.WARNING
    )
    logging.getLogger("alembic").setLevel(logging.INFO)

    logger.info(f"Logging configured - Debug mode: {settings.debug}")


class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter for adding context to log messages."""

    def process(self, msg: str, kwargs: Any) -> tuple[str, Any]:
        """Add extra context to log messages.

        Args:
            msg: Log message
            kwargs: Keyword arguments

        Returns:
            Tuple of message and kwargs with extra context
        """
        # Add request ID if available
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        return msg, kwargs
