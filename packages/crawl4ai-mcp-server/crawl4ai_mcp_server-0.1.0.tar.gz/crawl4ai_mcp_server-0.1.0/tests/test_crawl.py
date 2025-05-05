"""
Tests for crawl functionality.
"""

import json
import unittest
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from crawl4ai_mcp.utils import crawl_webpage_impl


class TestCrawlWebpage:
    """Test cases for crawl_webpage functionality."""

    @pytest.mark.asyncio
    async def test_crawl_webpage_success(self):
        """Test successful webpage crawl."""
        # Mock crawler response
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.metadata = {"title": "Test Page"}
        mock_result.markdown = "# Test Page\n\nThis is a test page content."
        mock_result.media = {"images": ["img1.jpg", "img2.jpg"]}

        # Create mock for AsyncWebCrawler context manager
        mock_crawler = AsyncMock()
        mock_crawler.__aenter__.return_value.arun = AsyncMock(
            return_value=mock_result)

        # Patch the AsyncWebCrawler class
        with patch('crawl4ai_mcp.utils.AsyncWebCrawler', return_value=mock_crawler):
            result = await crawl_webpage_impl("https://example.com", True, False)

            # Parse the JSON result
            result_data = json.loads(result)

            # Verify the result
            assert result_data["success"] is True
            assert result_data["url"] == "https://example.com"
            assert result_data["title"] == "Test Page"
            assert result_data["markdown"] == "# Test Page\n\nThis is a test page content."
            assert result_data["word_count"] == 7
            assert result_data["images"] == 2

    @pytest.mark.asyncio
    async def test_crawl_webpage_failure(self):
        """Test failed webpage crawl."""
        # Mock crawler response for failure
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error_message = "Failed to load page"

        # Create mock for AsyncWebCrawler context manager
        mock_crawler = AsyncMock()
        mock_crawler.__aenter__.return_value.arun = AsyncMock(
            return_value=mock_result)

        # Patch the AsyncWebCrawler class
        with patch('crawl4ai_mcp.utils.AsyncWebCrawler', return_value=mock_crawler):
            result = await crawl_webpage_impl("https://example.com")

            # Parse the JSON result
            result_data = json.loads(result)

            # Verify the result
            assert result_data["success"] is False
            assert result_data["error"] == "Failed to load page"

    @pytest.mark.asyncio
    async def test_crawl_webpage_exception(self):
        """Test exception during webpage crawl."""
        # Create mock for AsyncWebCrawler that raises an exception
        mock_crawler = AsyncMock()
        mock_crawler.__aenter__.return_value.arun = AsyncMock(
            side_effect=Exception("Test error"))

        # Patch the AsyncWebCrawler class
        with patch('crawl4ai_mcp.utils.AsyncWebCrawler', return_value=mock_crawler):
            result = await crawl_webpage_impl("https://example.com")

            # Parse the JSON result
            result_data = json.loads(result)

            # Verify the result
            assert result_data["success"] is False
            assert result_data["error"] == "Test error"
