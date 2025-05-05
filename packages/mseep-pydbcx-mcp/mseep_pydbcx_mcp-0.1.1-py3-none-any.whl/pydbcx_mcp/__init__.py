import argparse
import logging
import os

from .server import mcp


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="PYDBCX MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        help="Transport mode: stdio for command line, sse for server (default: stdio)",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    logging.info(f"Starting PYDBCX MCP Server with {args.transport} transport")
    try:
        mcp.run(transport=args.transport)
    except KeyboardInterrupt:
        logging.info("Server shutdown requested by user")
    except Exception as e:
        logging.error(f"Error running MCP server: {e}", exc_info=True)
        return 1

    logging.info("PYDBCX MCP Server stopped")
    return 0

# Optionally expose other important items at package level
__all__ = ["main", "server"]