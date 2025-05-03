"CLI entry point for fabric-mcp."

import argparse
import asyncio
import logging  # Import logging
import sys

from .__about__ import __version__
from .server import run_server_stdio


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
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
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
        level=numeric_level, format="%(asctime)s - %(levelname)s - %(message)s"
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

    # Add main logic based on args here
    if args.stdio:
        logging.info("Starting server with log level %s", args.log_level)  # Log level
        try:
            # Logging is now configured above
            asyncio.run(run_server_stdio())
        except KeyboardInterrupt:
            logging.info("Server stopped by user.")
            sys.exit(0)
        except Exception:
            # Log the full traceback for unexpected errors
            logging.exception("An unexpected error occurred during server execution.")
            sys.exit(1)


if __name__ == "__main__":
    main()
