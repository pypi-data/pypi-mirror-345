"""CLI entry point for fabric-mcp."""

import argparse
import logging
import sys

from fabric_mcp import __version__

from .core import FabricMCPServer


def main():
    "Argument parsing and entrypoint or fabric-mcp CLI."
    parser = argparse.ArgumentParser(
        prog="fabric-mcp",
        description="A Model Context Protocol server for Fabric AI.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version number and exit.",
    )
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Run the server in stdio mode (default).",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="Set the logging level (default: INFO)",
    )
    # Add other arguments and subcommands here in the future
    args = parser.parse_args()

    # Configure logging
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        # This should not happen with choices, but good practice
        print(f"Invalid log level: {args.log_level}", file=sys.stderr)
        sys.exit(1)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(module)s - %(levelname)s - %(message)s",
    )

    # If --stdio is not provided, and it's not just --version or --help, show help.
    # Allow running with just --log-level if --stdio is also present.
    if not args.stdio:
        # Show help if no arguments or only unrelated flags are provided
        if len(sys.argv) == 1 or all(
            arg in ["--version", "-h", "--help"] or arg.startswith("--log-level")
            for arg in sys.argv[1:]
        ):
            parser.print_help(sys.stderr)
            sys.exit(1)

    logger = logging.getLogger(__name__)

    # Add main logic based on args here
    if args.stdio:
        logger.info("Starting server with log level %s", args.log_level)
        fabric_mcp = FabricMCPServer(log_level=args.log_level.upper())
        fabric_mcp.stdio()
        logger.info("Server stopped.")


if __name__ == "__main__":
    main()
