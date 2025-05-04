"""Test core functionality of fabric-mcp"""

import subprocess
import sys

from fabric_mcp import __version__

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
