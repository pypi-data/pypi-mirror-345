"""
Crawl4AI MCP Server - A Model Context Protocol server for web crawling
using the Crawl4ai library.
"""

__version__ = "0.1.0"

from crawl4ai_mcp.server import serve, main

__all__ = ["serve", "main"]