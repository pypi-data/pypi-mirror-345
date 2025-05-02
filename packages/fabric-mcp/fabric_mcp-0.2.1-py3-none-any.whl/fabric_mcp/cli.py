"CLI entry point for fabric-mcp."

import argparse
import sys

from .__about__ import __version__


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
    # Add other arguments and subcommands here in the future
    _ = parser.parse_args()

    # If no arguments are given (besides --version handled by action='version'),
    # print help for now. Replace this with default behavior later.
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Add main logic based on args here
    print("Main CLI logic would go here.")


if __name__ == "__main__":
    main()
