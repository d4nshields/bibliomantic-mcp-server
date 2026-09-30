"""Bibliomantic MCP server package."""

from importlib.metadata import PackageNotFoundError, version as _version

from mcp.types import LATEST_PROTOCOL_VERSION as MCP_LATEST_PROTOCOL_VERSION

try:
    MCP_SDK_VERSION = _version("mcp")
except PackageNotFoundError:  # running from a bare checkout without an install
    MCP_SDK_VERSION = "unknown"

__all__ = ["MCP_SDK_VERSION", "MCP_LATEST_PROTOCOL_VERSION"]
