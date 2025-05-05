"""
Utility functions for Crawl4AI MCP server.
"""

import json
import logging
import os
import sys
from typing import Dict, Any, Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


def setup_logging(logger_name: str) -> logging.Logger:
    """
    设置基本日志配置

    Args:
        logger_name: 日志记录器名称

    Returns:
        配置好的日志记录器
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(stream=sys.stderr)]
    )
    return logging.getLogger(logger_name)


def check_virtual_env():
    """检查是否在虚拟环境中运行"""
    logger = logging.getLogger("crawl4ai_mcp")

    venv_path = os.environ.get("VIRTUAL_ENV")
    if venv_path:
        logger.info(f"检测到虚拟环境: {venv_path}")
    else:
        logger.warning("未检测到虚拟环境。建议在虚拟环境中运行以避免依赖问题。")
        logger.warning("若在macOS上遇到'externally-managed-environment'错误，请使用虚拟环境。")

    # 获取实例ID（如果由MCP管理器提供）
    instance_id = os.environ.get("MCP_INSTANCE_ID", "未知实例")
    logger.info(f"MCP实例ID: {instance_id}")


async def crawl_webpage_impl(url: str, include_images: bool = True, bypass_cache: bool = False) -> str:
    """
    爬取单个网页并返回其内容为markdown格式的实现。

    Args:
        url: 要爬取的网页URL
        include_images: 是否在结果中包含图像
        bypass_cache: 是否绕过缓存

    Returns:
        包含爬取结果的JSON字符串
    """
    logger = logging.getLogger("crawl4ai_mcp")
    logger.info(f"爬取网页: {url}")

    # 配置浏览器
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1280,
        viewport_height=900
    )

    # 配置爬虫
    cache_mode = CacheMode.BYPASS if bypass_cache else CacheMode.DEFAULT

    crawler_config = CrawlerRunConfig(
        include_images=include_images,
        include_links=True,
        cache_mode=cache_mode,
        wait_for="document.readyState === 'complete'",
        page_timeout=5000  # 5秒超时，单位毫秒
    )

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=crawler_config
            )

            if not result.success:
                return json.dumps({
                    "success": False,
                    "error": result.error_message
                })

            # 构建响应
            response = {
                "success": True,
                "url": url,
                "title": result.metadata.get("title", ""),
                "markdown": result.markdown,
                "word_count": len(result.markdown.split())
            }

            # 如果包含图片，添加图片信息
            if include_images and result.media and "images" in result.media:
                response["images"] = len(result.media["images"])

            return json.dumps(response, indent=2)

    except Exception as e:
        logger.error(f"爬取 {url} 时出错: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def crawl_website_impl(url: str, max_depth: int = 1, max_pages: int = 5, include_images: bool = True) -> str:
    """
    从给定URL开始爬取网站，最多爬取指定深度和页面数量的实现。

    Args:
        url: 爬取起始URL
        max_depth: 最大爬取深度
        max_pages: 最大爬取页面数量
        include_images: 是否在结果中包含图像

    Returns:
        包含爬取结果的JSON字符串
    """
    logger = logging.getLogger("crawl4ai_mcp")
    logger.info(f"爬取网站: {url} (深度: {max_depth}, 最大页面数: {max_pages})")

    # 配置浏览器
    browser_config = BrowserConfig(
        headless=True
    )

    try:
        # 使用深度爬取模式
        from crawl4ai.deep_crawling import DeepCrawlStrategy, BFSLinkExtractor

        async with AsyncWebCrawler(config=browser_config) as crawler:
            # 创建深度爬取策略
            deep_crawler = DeepCrawlStrategy(
                crawler=crawler,
                link_extractor=BFSLinkExtractor(),
                max_depth=max_depth,
                max_urls=max_pages
            )

            # 执行深度爬取
            results = await deep_crawler.arun(start_url=url)

            # 处理结果
            pages = []
            for res in results:
                if res.success:
                    page_info = {
                        "url": res.url,
                        "title": res.metadata.get("title", ""),
                        "word_count": len(res.markdown.split())
                    }
                    pages.append(page_info)

            return json.dumps({
                "success": True,
                "start_url": url,
                "pages_crawled": len(pages),
                "pages": pages
            }, indent=2)

    except Exception as e:
        logger.error(f"深度爬取 {url} 时出错: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def extract_structured_data_impl(url: str, schema: Optional[Dict] = None, css_selector: str = "body") -> str:
    """
    使用CSS选择器从网页中提取结构化数据的实现。

    Args:
        url: 要提取数据的网页URL
        schema: 定义提取的schema
        css_selector: 用于定位特定页面部分的CSS选择器

    Returns:
        包含提取数据的JSON字符串
    """
    logger = logging.getLogger("crawl4ai_mcp")
    logger.info(f"从 {url} 提取结构化数据")

    if not schema:
        # 使用默认schema
        schema = {
            "name": "BasicPageInfo",
            "baseSelector": css_selector,
            "fields": [
                {
                    "name": "headings",
                    "selector": "h1, h2, h3",
                    "type": "text",
                    "multiple": True
                },
                {
                    "name": "paragraphs",
                    "selector": "p",
                    "type": "text",
                    "multiple": True
                },
                {
                    "name": "images",
                    "selector": "img",
                    "type": "attribute",
                    "attribute": "src",
                    "multiple": True
                }
            ]
        }

    try:
        # 创建提取策略
        extractor = JsonCssExtractionStrategy(schema)

        # 配置浏览器
        browser_config = BrowserConfig(
            headless=True
        )

        # 创建爬虫配置
        crawler_config = CrawlerRunConfig(
            wait_for="document.readyState === 'complete'",
            extraction_strategy=extractor
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=crawler_config
            )

            if not result.success:
                return json.dumps({
                    "success": False,
                    "error": result.error_message
                })

            return json.dumps({
                "success": True,
                "url": url,
                "data": result.extracted_data
            }, indent=2)

    except Exception as e:
        logger.error(f"从 {url} 提取数据时出错: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def save_as_markdown_impl(url: str, filename: str, include_images: bool = True) -> str:
    """
    爬取网页并将内容保存为Markdown文件的实现。

    Args:
        url: 要爬取的网页URL
        filename: 保存Markdown的文件名
        include_images: 是否包含图像

    Returns:
        操作结果的JSON字符串
    """
    logger = logging.getLogger("crawl4ai_mcp")
    logger.info(f"爬取 {url} 并保存为 {filename}")

    # 配置浏览器
    browser_config = BrowserConfig(
        headless=True
    )

    # 配置爬虫
    crawler_config = CrawlerRunConfig(
        include_images=include_images,
        include_links=True,
        wait_for="document.readyState === 'complete'"
    )

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=crawler_config
            )

            if not result.success:
                return json.dumps({
                    "success": False,
                    "error": result.error_message
                })

            # 确保文件名有.md扩展名
            if not filename.endswith('.md'):
                filename += '.md'

            # 保存为Markdown文件
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {result.metadata.get('title', 'Untitled')}\n\n")
                f.write(f"Source: {url}\n\n")
                f.write(result.markdown)

            return json.dumps({
                "success": True,
                "filename": filename,
                "title": result.metadata.get("title", ""),
                "word_count": len(result.markdown.split())
            }, indent=2)

    except Exception as e:
        logger.error(f"保存 {url} 为Markdown时出错: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })