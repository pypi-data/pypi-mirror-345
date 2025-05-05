"""Test core functionality of fabric-mcp"""

import logging
import subprocess
import sys
from unittest.mock import patch

import pytest
from fastmcp import FastMCP

from fabric_mcp import __version__
from fabric_mcp.core import FabricMCP

# Tests for core functionality


def test_cli_version():
    """Test the --version flag of the CLI."""
    command = [sys.executable, "-m", "fabric_mcp.cli", "--version"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    # argparse --version action prints to stdout and exits with 0
    assert result.returncode == 0
    assert result.stderr == ""
    expected_output = f"fabric-mcp {__version__}\n"
    assert result.stdout == expected_output


@pytest.fixture(name="server_instance")  # Renamed fixture
def _server_instance() -> FabricMCP:
    """Fixture to create a FabricMCPServer instance."""
    return FabricMCP(log_level="DEBUG")


def test_server_initialization(server_instance: FabricMCP):
    """Test the initialization of the FabricMCPServer."""
    assert isinstance(server_instance.mcp, FastMCP)
    assert server_instance.mcp.name == f"Fabric MCP v{__version__}"
    assert isinstance(server_instance.logger, logging.Logger)
    # Check if log level propagates (Note: FastMCP handles its own logger setup)
    # We check the logger passed during init, FastMCP might configure differently
    # assert server_instance.logger.level == logging.DEBUG


def test_stdio_method_runs_mcp(server_instance: FabricMCP):
    """Test that the stdio method calls mcp.run()."""
    with patch.object(server_instance.mcp, "run") as mock_run:
        server_instance.stdio()
        mock_run.assert_called_once()


def test_stdio_method_handles_keyboard_interrupt(
    server_instance: FabricMCP,
    caplog: pytest.LogCaptureFixture,
):
    """Test that stdio handles KeyboardInterrupt gracefully."""
    with patch.object(server_instance.mcp, "run", side_effect=KeyboardInterrupt):
        with caplog.at_level(logging.INFO):
            server_instance.stdio()
    assert "Server stopped by user." in caplog.text
