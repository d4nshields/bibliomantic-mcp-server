#!/usr/bin/env python3
"""
Bibliomantic MCP Server

A Model Context Protocol server that integrates I Ching divination with AI responses,
exploring the bibliomantic approach described in Philip K. Dick's "The Man in the High Castle".

This is the main entry point for the server when installed as a package.
"""

from bibliomantic_fastmcp_ethical import mcp

def main():
    """Main entry point for the bibliomantic server."""
    mcp.run()

if __name__ == "__main__":
    main()
