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

    # 配置浏览器 - 增加窗口大小以显示更多内容
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,  # 增加视口宽度
        viewport_height=1080  # 增加视口高度
    )

    # 配置爬虫
    cache_mode = CacheMode.BYPASS if bypass_cache else CacheMode.DEFAULT

    # 自动滚动脚本 - 确保加载懒加载内容
    scroll_script = """
        // 自动滚动到页面底部
        function scrollToBottom() {
            window.scrollTo(0, document.body.scrollHeight);
            return document.body.scrollHeight;
        }

        // 多次滚动，确保加载所有内容
        let lastHeight = 0;
        let newHeight = scrollToBottom();

        // 继续滚动直到高度不再变化或达到最大滚动次数
        let count = 0;
        while (lastHeight !== newHeight && count < 10) {
            lastHeight = newHeight;
            // 等待更多内容加载
            await new Promise(r => setTimeout(r, 1000));
            newHeight = scrollToBottom();
            count++;
        }
    """

    crawler_config = CrawlerRunConfig(
        include_images=include_images,
        include_links=True,
        cache_mode=cache_mode,
        wait_for="document.readyState === 'complete'",
        page_timeout=30000,  # 增加到30秒
        post_load_script=scroll_script,  # 添加滚动脚本
        max_content_length=10000000  # 10MB，如果库支持的话
    )

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            # 第一次尝试爬取
            result = await crawler.arun(
                url=url,
                config=crawler_config
            )

            # 检查结果是否成功
            if not result.success:
                return json.dumps({
                    "success": False,
                    "error": result.error_message
                })

            # 检查内容是否可能不完整
            content_length = len(result.markdown)
            if content_length < 1000 and "." in url:  # 如果内容很少，可能不完整，但排除非网页URL
                logger.warning(f"爬取到的内容可能不完整：只有{content_length}个字符，尝试增加等待时间")

                # 尝试增加等待时间再次爬取
                crawler_config.page_timeout = 60000  # 增加到60秒
                crawler_config.wait_for = [
                    # 强制等待额外5秒
                    "document.readyState === 'complete'", "setTimeout(() => true, 5000)"]
                logger.info(f"重新尝试爬取 {url} 并增加超时时间")
                result = await crawler.arun(url=url, config=crawler_config)

                # 如果还是内容很少，尝试使用不同的等待策略
                if len(result.markdown) < 1000 and result.success:
                    logger.warning(
                        f"内容仍然很少({len(result.markdown)}字符)，尝试使用延迟策略")
                    crawler_config.post_load_script = """
                        // 等待更多内容加载
                        await new Promise(r => setTimeout(r, 10000));
                        console.log("Waited 10 seconds for more content to load");
                    """ + scroll_script
                    result = await crawler.arun(url=url, config=crawler_config)

            # 构建响应
            response = {
                "success": True,
                "url": url,
                "title": result.metadata.get("title", ""),
                "markdown": result.markdown,
                "word_count": len(result.markdown.split()),
                "character_count": len(result.markdown),  # 添加字符计数
                # 如果可用，添加爬取时间
                "crawl_time_ms": result.metadata.get("crawl_time_ms", 0)
            }

            # 如果包含图片，添加图片信息
            if include_images and result.media and "images" in result.media:
                response["images"] = len(result.media["images"])

                # 添加图片URL列表（最多10个）
                image_urls = [img.get("src", "")
                              for img in result.media["images"][:10]]
                if image_urls:
                    response["image_urls"] = image_urls

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

    # 配置浏览器 - 增加窗口大小
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=1080
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
                max_urls=max_pages,
                page_timeout=30000  # 增加页面超时时间
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
                        "word_count": len(res.markdown.split()),
                        "character_count": len(res.markdown)  # 添加字符计数
                    }
                    pages.append(page_info)

            return json.dumps({
                "success": True,
                "start_url": url,
                "pages_crawled": len(pages),
                # 总词数
                "total_words": sum(page.get("word_count", 0) for page in pages),
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
                },
                {
                    "name": "links",
                    "selector": "a",
                    "type": "attribute",
                    "attribute": "href",
                    "multiple": True
                }
            ]
        }

    try:
        # 创建提取策略
        extractor = JsonCssExtractionStrategy(schema)

        # 配置浏览器
        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1920,
            viewport_height=1080
        )

        # 自动滚动脚本 - 确保加载懒加载内容
        scroll_script = """
            // 自动滚动到页面底部
            function scrollToBottom() {
                window.scrollTo(0, document.body.scrollHeight);
                return document.body.scrollHeight;
            }

            // 多次滚动，确保加载所有内容
            let lastHeight = 0;
            let newHeight = scrollToBottom();

            // 继续滚动直到高度不再变化
            let count = 0;
            while (lastHeight !== newHeight && count < 10) {
                lastHeight = newHeight;
                // 等待更多内容加载
                await new Promise(r => setTimeout(r, 1000));
                newHeight = scrollToBottom();
                count++;
            }
        """

        # 创建爬虫配置
        crawler_config = CrawlerRunConfig(
            wait_for="document.readyState === 'complete'",
            extraction_strategy=extractor,
            page_timeout=30000,  # 增加超时时间
            post_load_script=scroll_script  # 添加滚动脚本
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

            # 检查是否提取到数据
            if not result.extracted_data:
                logger.warning(f"未能从 {url} 提取到数据，尝试增加等待时间")
                crawler_config.page_timeout = 60000  # 增加到60秒
                result = await crawler.arun(url=url, config=crawler_config)

            return json.dumps({
                "success": True,
                "url": url,
                "data": result.extracted_data,
                # 如果可用，添加提取时间
                "extraction_time_ms": result.metadata.get("extraction_time_ms", 0)
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
        headless=True,
        viewport_width=1920,
        viewport_height=1080
    )

    # 自动滚动脚本
    scroll_script = """
        // 自动滚动到页面底部
        function scrollToBottom() {
            window.scrollTo(0, document.body.scrollHeight);
            return document.body.scrollHeight;
        }

        // 多次滚动，确保加载所有内容
        let lastHeight = 0;
        let newHeight = scrollToBottom();

        // 继续滚动直到高度不再变化
        let count = 0;
        while (lastHeight !== newHeight && count < 10) {
            lastHeight = newHeight;
            // 等待更多内容加载
            await new Promise(r => setTimeout(r, 1000));
            newHeight = scrollToBottom();
            count++;
        }
    """

    # 配置爬虫
    crawler_config = CrawlerRunConfig(
        include_images=include_images,
        include_links=True,
        wait_for="document.readyState === 'complete'",
        page_timeout=30000,  # 增加超时时间
        post_load_script=scroll_script  # 添加滚动脚本
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

            # 检查内容是否可能不完整
            content_length = len(result.markdown)
            if content_length < 1000:  # 如果内容很少，可能不完整
                logger.warning(f"爬取到的内容可能不完整：只有{content_length}个字符")

                # 尝试增加等待时间再次爬取
                crawler_config.page_timeout = 60000  # 增加到60秒
                logger.info(f"重新尝试爬取 {url} 并增加超时时间")
                result = await crawler.arun(url=url, config=crawler_config)

            # 确保文件名有.md扩展名
            if not filename.endswith('.md'):
                filename += '.md'

            # 保存为Markdown文件
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {result.metadata.get('title', 'Untitled')}\n\n")
                f.write(f"Source: {url}\n\n")
                f.write(
                    f"Saved at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(result.markdown)

            return json.dumps({
                "success": True,
                "filename": filename,
                "title": result.metadata.get("title", ""),
                "word_count": len(result.markdown.split()),
                "character_count": len(result.markdown),  # 添加字符计数
                "save_time": datetime.datetime.now().isoformat()  # 添加保存时间
            }, indent=2)

    except Exception as e:
        logger.error(f"保存 {url} 为Markdown时出错: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })
