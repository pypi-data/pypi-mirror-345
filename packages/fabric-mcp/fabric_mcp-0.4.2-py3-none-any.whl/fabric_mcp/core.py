"""Core MCP server implementation using the Model Context Protocol."""

import logging
from asyncio.exceptions import CancelledError

from anyio import WouldBlock
from fastmcp import FastMCP

from . import __version__


class FabricMCP(FastMCP):
    """Base class for the Model Context Protocol server."""

    def __init__(self, log_level: str = "INFO"):
        """Initialize the MCP server with a model."""
        super().__init__(f"Fabric MCP v{__version__}", log_level=log_level)
        self.mcp = self
        self.logger = logging.getLogger(__name__)

        @self.tool()
        def fabric_list_patterns() -> list[str]:
            """Return a list of available fabric patterns."""
            # This is a placeholder for the actual implementation
            return ["pattern1", "pattern2", "pattern3"]

        @self.tool()
        def fabric_pattern_details(pattern_name: str) -> dict:
            """Return the details of a specific fabric pattern."""
            # This is a placeholder for the actual implementation
            return {"name": pattern_name, "details": "Pattern details here"}

        @self.tool()
        def fabric_run_pattern(pattern_name: str, *args, **kwargs) -> dict:
            """Run a specific fabric pattern with the given arguments."""
            # This is a placeholder for the actual implementation
            return {
                "name": pattern_name,
                "result": "Pattern result here",
                "args": args,
                "kwargs": kwargs,
            }

    def stdio(self):
        """Run the MCP server."""
        try:
            self.mcp.run()
        except (KeyboardInterrupt, CancelledError, WouldBlock):
            # Handle graceful shutdown
            self.logger.info("Server stopped by user.")
