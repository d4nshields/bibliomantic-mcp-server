#!/usr/bin/env python3
"""
Enhanced Bibliomantic MCP Server

A Model Context Protocol server that integrates enhanced I Ching divination with AI responses,
exploring the bibliomantic approach described in Philip K. Dick's "The Man in the High Castle"
with traditional Chinese I Ching elements. How much authored traditional text each hexagram
carries varies; the server info resource reports exact coverage.

This is the main entry point for the server when invoked by an MCP host such as
Claude Desktop, either via the ``bibliomantic-mcp-server`` console script or
``python -m bibliomantic_server``.

Command-line options:
    --no-ethical-disclaimers    Omit the ethical guidance note that is otherwise appended
                                to every divination, consultation and hexagram-details
                                result for the assistant to convey in context.
"""

import argparse
import logging
import sys
from typing import Optional, Sequence

from .ethics import enable_disclaimers

# Configure logging to stderr (MCP uses stdout for protocol)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

from .enhanced_bibliomantic_server import mcp  # noqa: E402  (logging must be set up first)

logger.info("Loaded Enhanced Bibliomantic MCP Server with traditional I Ching content")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bibliomantic-mcp-server",
        description="Bibliomantic I Ching MCP server (stdio transport).",
    )
    parser.add_argument(
        "--no-ethical-disclaimers",
        dest="ethical_disclaimers",
        action="store_false",
        help="omit the ethical guidance note that is appended by default to "
             "divination, consultation and hexagram-details results for the "
             "assistant to convey in context",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Main entry point for the bibliomantic server."""
    args = build_parser().parse_args(argv)

    enable_disclaimers(args.ethical_disclaimers)
    if not args.ethical_disclaimers:
        logger.info("Ethical disclaimers disabled (--no-ethical-disclaimers)")

    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
