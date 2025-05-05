"""
Tests for MCP server functionality.
"""

import json
import unittest
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from mcp.types import TextContent

from crawl4ai_mcp.server import (
    CrawlWebpageParams,
    CrawlWebsiteParams,
    ExtractStructuredDataParams,
    SaveAsMarkdownParams,
)


class TestServer:
    """Test cases for server functionality."""

    def test_crawl_webpage_params(self):
        """Test CrawlWebpageParams model."""
        # Test default values
        params = CrawlWebpageParams(url="https://example.com")
        assert params.url == "https://example.com"
        assert params.include_images is True
        assert params.bypass_cache is False

        # Test custom values
        params = CrawlWebpageParams(
            url="https://example.com",
            include_images=False,
            bypass_cache=True
        )
        assert params.url == "https://example.com"
        assert params.include_images is False
        assert params.bypass_cache is True

        # Test model validation
        try:
            params = CrawlWebpageParams()
            assert False, "Should have raised a validation error for missing url"
        except Exception:
            pass

    def test_crawl_website_params(self):
        """Test CrawlWebsiteParams model."""
        # Test default values
        params = CrawlWebsiteParams(url="https://example.com")
        assert params.url == "https://example.com"
        assert params.max_depth == 1
        assert params.max_pages == 5
        assert params.include_images is True

        # Test custom values
        params = CrawlWebsiteParams(
            url="https://example.com",
            max_depth=3,
            max_pages=10,
            include_images=False
        )
        assert params.url == "https://example.com"
        assert params.max_depth == 3
        assert params.max_pages == 10
        assert params.include_images is False

    def test_extract_structured_data_params(self):
        """Test ExtractStructuredDataParams model."""
        # Test default values
        params = ExtractStructuredDataParams(url="https://example.com")
        assert params.url == "https://example.com"
        assert params.schema is None
        assert params.css_selector == "body"

        # Test custom values
        schema = {
            "name": "TestSchema",
            "fields": [{"name": "title", "selector": "h1"}]
        }
        params = ExtractStructuredDataParams(
            url="https://example.com",
            schema=schema,
            css_selector="div.content"
        )
        assert params.url == "https://example.com"
        assert params.schema == schema
        assert params.css_selector == "div.content"

    def test_save_as_markdown_params(self):
        """Test SaveAsMarkdownParams model."""
        # Test default values
        params = SaveAsMarkdownParams(
            url="https://example.com", filename="output.md")
        assert params.url == "https://example.com"
        assert params.filename == "output.md"
        assert params.include_images is True

        # Test custom values
        params = SaveAsMarkdownParams(
            url="https://example.com",
            filename="output.md",
            include_images=False
        )
        assert params.url == "https://example.com"
        assert params.filename == "output.md"
        assert params.include_images is False

        # Test model validation
        try:
            params = SaveAsMarkdownParams(url="https://example.com")
            assert False, "Should have raised a validation error for missing filename"
        except Exception:
            pass

        try:
            params = SaveAsMarkdownParams(filename="output.md")
            assert False, "Should have raised a validation error for missing url"
        except Exception:
            pass


@pytest.mark.asyncio
async def test_call_tool_crawl_webpage():
    """Test call_tool with crawl_webpage."""
    from crawl4ai_mcp.server import call_tool

    # Create a successful crawl result
    crawl_result = json.dumps({
        "success": True,
        "url": "https://example.com",
        "title": "Example Page",
        "markdown": "# Example Page\n\nContent here.",
        "word_count": 3
    })

    # Patch the implementation function
    with patch('crawl4ai_mcp.server.crawl_webpage_impl',
               new=AsyncMock(return_value=crawl_result)) as mock_impl:
        # Call the tool
        result = await call_tool(
            "crawl_webpage",
            {"url": "https://example.com", "include_images": True}
        )

        # Verify the implementation was called with correct parameters
        mock_impl.assert_called_once_with("https://example.com", True, False)

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert result[0].text == crawl_result
