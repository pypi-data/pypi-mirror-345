"""Utility functions for the fabric_mcp module."""

import logging

from rich.console import Console
from rich.logging import RichHandler


class Log:
    """Custom class to handle logging set up and log levels."""

    def __init__(self, level: str):
        """Initialize the Log class with a specific log level."""
        self._level_name = level.upper()
        self._level = Log.log_level(self._level_name)

        handler = RichHandler(
            console=Console(stderr=True),
            rich_tracebacks=True,
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(module)s  - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        self._logger = logging.getLogger("FabricMCP")
        self._logger.setLevel(self.level_name)

        self.logger.setLevel(self.level_name.upper())

        # Remove any existing handlers to avoid duplicates on reconfiguration
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        self._logger.addHandler(handler)

    @property
    def level_name(self) -> str:
        """Return the log level as a string."""
        return self._level_name

    @property
    def logger(self) -> logging.Logger:
        """Return the logger instance."""
        return self._logger

    @property
    def level(self) -> int:
        """Return the log level as an integer."""
        return self._level

    @staticmethod
    def log_level(level: str) -> int:
        """Convert a string log level to its corresponding integer value."""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        # Ensure level is uppercase for dictionary lookup
        level_upper = level.upper()
        if level_upper not in levels:
            raise ValueError(
                f"Invalid log level: {level}. Choose from {list(levels.keys())}."
            )
        return levels.get(level_upper)
