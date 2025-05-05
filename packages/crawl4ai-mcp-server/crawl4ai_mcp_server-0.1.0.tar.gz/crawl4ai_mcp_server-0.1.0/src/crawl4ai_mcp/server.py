"""
Main server implementation for Crawl4AI MCP Server.
"""

import json
import logging
import os
import sys
import asyncio
from typing import Dict, Any, List, Optional, Union

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    ErrorData,
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    INVALID_PARAMS
)
from mcp.shared.exceptions import McpError
from pydantic import BaseModel, Field

from crawl4ai_mcp.utils import (
    setup_logging,
    crawl_webpage_impl,
    crawl_website_impl,
    extract_structured_data_impl,
    save_as_markdown_impl,
    check_virtual_env
)

# 设置日志记录器
logger = setup_logging("crawl4ai_mcp")

# 模型定义
class CrawlWebpageParams(BaseModel):
    """Parameters for crawling a single webpage."""
    url: str = Field(description="要爬取的网页URL")
    include_images: bool = Field(default=True, description="是否在结果中包含图像")
    bypass_cache: bool = Field(default=False, description="是否绕过缓存")

class CrawlWebsiteParams(BaseModel):
    """Parameters for crawling a website."""
    url: str = Field(description="爬取起始URL")
    max_depth: int = Field(default=1, description="最大爬取深度")
    max_pages: int = Field(default=5, description="最大爬取页面数量")
    include_images: bool = Field(default=True, description="是否在结果中包含图像")

class ExtractStructuredDataParams(BaseModel):
    """Parameters for extracting structured data from a webpage."""
    url: str = Field(description="要提取数据的网页URL")
    schema: Optional[Dict[str, Any]] = Field(default=None, description="定义提取的schema")
    css_selector: str = Field(default="body", description="用于定位特定页面部分的CSS选择器")

class SaveAsMarkdownParams(BaseModel):
    """Parameters for saving a webpage as markdown."""
    url: str = Field(description="要爬取的网页URL")
    filename: str = Field(description="保存Markdown的文件名")
    include_images: bool = Field(default=True, description="是否包含图像")

async def serve():
    """Run the Crawl4AI MCP server."""
    server = Server("Crawl4AI")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools in this server."""
        return [
            Tool(
                name="crawl_webpage",
                description="爬取单个网页并返回其内容为markdown格式。",
                inputSchema=CrawlWebpageParams.model_json_schema(),
            ),
            Tool(
                name="crawl_website",
                description="从给定URL开始爬取网站，最多爬取指定深度和页面数量。",
                inputSchema=CrawlWebsiteParams.model_json_schema(),
            ),
            Tool(
                name="extract_structured_data",
                description="使用CSS选择器从网页中提取结构化数据。",
                inputSchema=ExtractStructuredDataParams.model_json_schema(),
            ),
            Tool(
                name="save_as_markdown",
                description="爬取网页并将内容保存为Markdown文件。",
                inputSchema=SaveAsMarkdownParams.model_json_schema(),
            )
        ]

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """List available prompts in this server."""
        return [
            Prompt(
                name="crawl",
                description="爬取网页并获取其内容",
                arguments=[
                    PromptArgument(
                        name="url", description="要爬取的网页URL", required=True
                    )
                ],
            ),
            Prompt(
                name="save_page",
                description="爬取网页并保存为Markdown文件",
                arguments=[
                    PromptArgument(
                        name="url", description="要爬取的网页URL", required=True
                    ),
                    PromptArgument(
                        name="filename", description="保存的文件名", required=True
                    )
                ],
            )
        ]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        """Handle prompt requests."""
        if name == "crawl":
            if not arguments or "url" not in arguments:
                raise McpError(ErrorData(code=INVALID_PARAMS, message="URL is required"))

            url = arguments["url"]
            try:
                result = await crawl_webpage_impl(url, True, False)
                result_data = json.loads(result)
                if not result_data.get("success", False):
                    return GetPromptResult(
                        description=f"Failed to crawl {url}",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(type="text", text=result_data.get("error", "Unknown error")),
                            )
                        ],
                    )

                return GetPromptResult(
                    description=f"Contents of {url}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(type="text", text=result_data.get("markdown", "No content"))
                        )
                    ],
                )
            except Exception as e:
                return GetPromptResult(
                    description=f"Failed to crawl {url}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(type="text", text=str(e)),
                        )
                    ],
                )
        elif name == "save_page":
            if not arguments or "url" not in arguments or "filename" not in arguments:
                raise McpError(ErrorData(code=INVALID_PARAMS, message="URL and filename are required"))

            url = arguments["url"]
            filename = arguments["filename"]
            try:
                result = await save_as_markdown_impl(url, filename, True)
                result_data = json.loads(result)
                if not result_data.get("success", False):
                    return GetPromptResult(
                        description=f"Failed to save {url}",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(type="text", text=result_data.get("error", "Unknown error")),
                            )
                        ],
                    )

                return GetPromptResult(
                    description=f"Page saved as {filename}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"Successfully saved {url} as {filename} with {result_data.get('word_count', 0)} words."
                            )
                        )
                    ],
                )
            except Exception as e:
                return GetPromptResult(
                    description=f"Failed to save {url}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(type="text", text=str(e)),
                        )
                    ],
                )

        raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Unknown prompt: {name}"))

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        logger.info(f"工具调用: {name} {arguments}")

        if name == "crawl_webpage":
            try:
                params = CrawlWebpageParams(**arguments)
                result = await crawl_webpage_impl(
                    params.url, params.include_images, params.bypass_cache
                )
                return [TextContent(type="text", text=result)]
            except Exception as e:
                logger.error(f"爬取网页时出错: {str(e)}")
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

        elif name == "crawl_website":
            try:
                params = CrawlWebsiteParams(**arguments)
                result = await crawl_website_impl(
                    params.url, params.max_depth, params.max_pages, params.include_images
                )
                return [TextContent(type="text", text=result)]
            except Exception as e:
                logger.error(f"爬取网站时出错: {str(e)}")
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

        elif name == "extract_structured_data":
            try:
                params = ExtractStructuredDataParams(**arguments)
                result = await extract_structured_data_impl(
                    params.url, params.schema, params.css_selector
                )
                return [TextContent(type="text", text=result)]
            except Exception as e:
                logger.error(f"提取结构化数据时出错: {str(e)}")
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

        elif name == "save_as_markdown":
            try:
                params = SaveAsMarkdownParams(**arguments)
                result = await save_as_markdown_impl(
                    params.url, params.filename, params.include_images
                )
                return [TextContent(type="text", text=result)]
            except Exception as e:
                logger.error(f"保存为Markdown时出错: {str(e)}")
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

        else:
            logger.error(f"未知工具: {name}")
            raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Unknown tool: {name}"))

    # 将工具信息打印到日志
    logger.info("MCP服务器启动，可用工具: crawl_webpage, crawl_website, extract_structured_data, save_as_markdown")

    # 创建服务器选项
    options = server.create_initialization_options()

    # 使用标准的stdio服务器运行
    logger.info("使用标准stdio服务器运行MCP服务")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


def main():
    """Command-line entry point for the server."""
    logger.info("启动Crawl4AI MCP服务器...")
    check_virtual_env()

    try:
        # 使用asyncio.run运行服务器
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在关闭服务器...")
    except Exception as e:
        logger.error(f"启动MCP服务器时出现未处理异常: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

    logger.info("Crawl4AI MCP服务器已关闭")


if __name__ == "__main__":
    main()