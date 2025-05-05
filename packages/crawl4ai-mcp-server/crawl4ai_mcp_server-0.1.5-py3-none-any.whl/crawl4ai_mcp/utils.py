"""
Utility functions for Crawl4AI MCP server.
"""

import json
import logging
import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Callable
from enum import Enum, auto

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


class CacheMode(Enum):
    DEFAULT = auto()
    BYPASS = auto()
    FORCE = auto()


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


async def retry_with_backoff(func, max_retries=3, initial_delay=1, backoff_factor=2, *args, **kwargs):
    """
    实现指数退避重试功能

    Args:
        func: 要重试的异步函数
        max_retries: 最大重试次数
        initial_delay: 初始延迟（秒）
        backoff_factor: 退避因子
        args: 传递给func的位置参数
        kwargs: 传递给func的关键字参数

    Returns:
        函数执行结果
    """
    logger = logging.getLogger("crawl4ai_mcp")
    retries = 0
    delay = initial_delay
    last_exception = None

    while True:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            retries += 1
            if retries >= max_retries:
                logger.error(f"已达到最大重试次数 {max_retries}，放弃重试")
                raise last_exception

            logger.warning(
                f"重试 {func.__name__}: {retries}/{max_retries}，延迟 {delay}秒。错误: {str(e)}")

            await asyncio.sleep(delay)
            delay *= backoff_factor


# 增强的滚动脚本
scroll_script = """
    // 更智能的页面滚动函数
    async function scrollFullPage() {
        // 初始化滚动状态
        let totalHeight = 0;
        let distance = 300;
        let scrollHeight = document.body.scrollHeight;
        let timer = 100; // 初始滚动间隔

        // 点击可能的"加载更多"按钮
        function clickLoadMoreButtons() {
            // 常见的"加载更多"按钮选择器
            const loadMoreSelectors = [
                'button[id*="load-more"], button[class*="load-more"]',
                'button[id*="loadMore"], button[class*="loadMore"]',
                'a[id*="load-more"], a[class*="load-more"]',
                'a[id*="loadMore"], a[class*="loadMore"]',
                'div[id*="load-more"], div[class*="load-more"]',
                'div[id*="loadMore"], div[class*="loadMore"]',
                'span[id*="load-more"], span[class*="load-more"]',
                'span[id*="loadMore"], span[class*="loadMore"]',
                // 包含"更多"文本的元素
                'button:contains("更多"), a:contains("更多")',
                'button:contains("加载更多"), a:contains("加载更多")',
                'button:contains("More"), a:contains("More")',
                'button:contains("Load more"), a:contains("Load more")'
            ];

            // 尝试点击各种可能的"加载更多"按钮
            loadMoreSelectors.forEach(selector => {
                try {
                    const buttons = document.querySelectorAll(selector);
                    buttons.forEach(button => {
                        if (button.offsetParent !== null && button.style.display !== 'none') {
                            console.log('Clicking load more button:', button);
                            button.click();
                        }
                    });
                } catch (err) {
                    // 忽略错误继续执行
                }
            });
        }

        // 关闭弹窗或Cookie提示
        function dismissPopups() {
            // 常见的弹窗和Cookie提示选择器
            const popupSelectors = [
                // Cookie相关
                'button[id*="cookie"], button[class*="cookie"]',
                'button[id*="Cookie"], button[class*="Cookie"]',
                'button[id*="accept"], button[class*="accept"]',
                'button[id*="consent"], button[class*="consent"]',
                // 弹窗关闭按钮
                'button[id*="close"], button[class*="close"]',
                'a[id*="close"], a[class*="close"]',
                'div[id*="close"], div[class*="close"]',
                'span[id*="close"], span[class*="close"]',
                'svg[id*="close"], svg[class*="close"]',
                // 图标按钮
                'i[class*="close"], i[class*="times"]',
                // 含有×文本的元素
                'button:contains("×"), span:contains("×")',
                // 图片关闭按钮
                'img[alt*="close"], img[src*="close"]'
            ];

            popupSelectors.forEach(selector => {
                try {
                    const buttons = document.querySelectorAll(selector);
                    buttons.forEach(button => {
                        if (button.offsetParent !== null && button.style.display !== 'none') {
                            console.log('Dismissing popup/cookie notice:', button);
                            button.click();
                        }
                    });
                } catch (err) {
                    // 忽略错误继续执行
                }
            });
        }

        // 处理懒加载图片
        function loadLazyImages() {
            // 找到所有懒加载的图片
            const lazyImages = document.querySelectorAll('img[loading="lazy"], img[data-src], img[data-srcset], img[data-original]');

            lazyImages.forEach(img => {
                // 替换src属性
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                }
                if (img.dataset.srcset) {
                    img.srcset = img.dataset.srcset;
                }
                if (img.dataset.original) {
                    img.src = img.dataset.original;
                }

                // 移除loading="lazy"
                img.removeAttribute('loading');

                // 确保图片显示
                img.style.display = 'inline';
                img.style.visibility = 'visible';
                img.style.opacity = '1';
            });
        }

        // 主滚动循环
        let lastHeight = document.body.scrollHeight;
        let scrollCount = 0;
        const maxScrolls = 30; // 最大滚动次数

        // 先尝试关闭弹窗
        dismissPopups();
        await new Promise(r => setTimeout(r, 1000));

        while (scrollCount < maxScrolls) {
            // 滚动页面
            window.scrollTo(0, document.body.scrollHeight);

            // 等待内容加载
            await new Promise(r => setTimeout(r, timer));

            // 尝试点击"加载更多"按钮
            clickLoadMoreButtons();

            // 处理懒加载图片
            loadLazyImages();

            // 再次尝试关闭可能出现的新弹窗
            if (scrollCount % 5 === 0) {
                dismissPopups();
            }

            // 检查是否已滚动到底部或内容不再加载
            const currentHeight = document.body.scrollHeight;
            if (currentHeight === lastHeight) {
                // 增加等待时间，再尝试几次
                timer = 2000;
                if (scrollCount > 10) {
                    break; // 如果已经尝试足够多次，退出循环
                }
            }

            lastHeight = currentHeight;
            scrollCount++;

            // 动态调整滚动间隔
            if (scrollCount > 5) {
                timer = 1500; // 后期增加等待时间
            }
        }

        // 最终滚动回顶部
        window.scrollTo(0, 0);

        // 返回最终的文档高度作为指标
        return document.body.scrollHeight;
    }

    // 执行完整页面滚动
    await scrollFullPage();
"""


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
        viewport_height=1080,  # 增加视口高度
        # 设置更宽松的超时时间
        browser_args=["--disable-web-security",
                      "--disable-features=IsolateOrigins,site-per-process"]
    )

    # 配置爬虫
    cache_mode = CacheMode.BYPASS if bypass_cache else CacheMode.DEFAULT

    # 使用更智能的配置
    crawler_config = CrawlerRunConfig(
        include_images=include_images,
        include_links=True,
        cache_mode=cache_mode,
        # 改为多条件等待
        wait_for=[
            "document.readyState === 'complete'",
            # 确保主要内容加载
            "document.querySelectorAll('p, h1, h2, h3, article, section, main').length > 0"
        ],
        page_timeout=45000,  # 增加到45秒
        post_load_script=scroll_script,
        max_content_length=20000000  # 20MB
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

            # 增强检测逻辑 - 不仅检查长度，还检查内容质量
            content_length = len(result.markdown)
            text_to_html_ratio = content_length / \
                (len(result.html) if hasattr(result, "html") and result.html else 1)

            # 如果内容比例过低或内容过少，可能需要重试
            if (content_length < 2000 or text_to_html_ratio < 0.1) and "." in url:
                logger.warning(
                    f"爬取到的内容可能不完整：只有{content_length}个字符，尝试使用DOM等待策略")

                # 使用DOM元素等待策略
                crawler_config.wait_for = [
                    "document.readyState === 'complete'",
                    "document.querySelectorAll('p').length > 5",  # 等待至少5个段落出现
                    "setTimeout(() => true, 8000)"  # 强制等待8秒
                ]
                crawler_config.page_timeout = 60000  # 增加到60秒

                logger.info(f"重新尝试爬取 {url} 并使用DOM等待策略")
                result = await crawler.arun(url=url, config=crawler_config)

                # 如果还是内容很少，尝试第三种策略
                if (len(result.markdown) < 2000 or len(result.markdown) / len(result.html if hasattr(result, "html") and result.html else "1") < 0.1) and result.success:
                    logger.warning(f"内容仍然不完整，尝试使用高级加载策略")

                    # 高级加载策略 - 使用更复杂的脚本
                    advanced_script = """
                        // 等待更多内容加载
                        await new Promise(r => setTimeout(r, 5000));

                        // 模拟用户交互 - 尝试点击展开按钮
                        const expandButtons = document.querySelectorAll('button[aria-expanded="false"], [data-toggle="collapse"]');
                        expandButtons.forEach(button => button.click());

                        // 等待更多内容
                        await new Promise(r => setTimeout(r, 3000));

                        // 再次滚动
                        window.scrollTo(0, 0);
                        await new Promise(r => setTimeout(r, 1000));
                        window.scrollTo(0, document.body.scrollHeight);

                        // 最终延迟
                        await new Promise(r => setTimeout(r, 5000));
                        console.log("使用高级加载策略完成");
                    """ + scroll_script

                    crawler_config.post_load_script = advanced_script
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


async def deep_crawl_webpage_impl(url: str, include_images: bool = True, cache_mode: CacheMode = CacheMode.DEFAULT) -> str:
    """
    使用多策略深度抓取网页内容的实现。

    Args:
        url: 要爬取的网页URL
        include_images: 是否在结果中包含图像
        cache_mode: 缓存模式

    Returns:
        包含抓取结果的JSON字符串
    """
    logger = logging.getLogger("crawl4ai_mcp")
    logger.info(f"深度抓取网页: {url}")

    # 配置增强的浏览器
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=2160,  # 增加视口高度
        browser_args=[
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-site-isolation-trials",
            "--disable-setuid-sandbox",
            "--no-sandbox"
        ]
    )

    # 策略1：标准策略但超长超时
    standard_config = CrawlerRunConfig(
        include_images=include_images,
        include_links=True,
        cache_mode=cache_mode,
        wait_for=[
            "document.readyState === 'complete'",
            "document.querySelectorAll('p, h1, h2, h3, article, section, main').length > 0",
            "setTimeout(() => true, 10000)"  # 强制等待10秒
        ],
        page_timeout=90000,  # 90秒超长超时
        post_load_script=scroll_script,
        max_content_length=30000000  # 30MB
    )

    # 策略2：添加用户交互模拟
    interaction_script = """
    // 用户交互模拟
    async function simulateUserInteraction() {
        // 模拟鼠标移动和点击
        function simulateMouseMovement() {
            const elements = document.querySelectorAll('a, button, input, select, textarea');
            if (elements.length > 0) {
                const randomIndex = Math.floor(Math.random() * elements.length);
                const element = elements[randomIndex];

                // 移动到元素
                element.scrollIntoView({behavior: 'smooth', block: 'center'});

                // 创建鼠标悬停事件
                const mouseoverEvent = new MouseEvent('mouseover', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                element.dispatchEvent(mouseoverEvent);
            }
        }

        // 模拟滚动
        function simulateScrolling() {
            const scrollTargets = [0.3, 0.5, 0.7, 1.0, 0.5, 0.2, 0.8, 0.4, 0.9, 0.1];
            let index = 0;

            return new Promise(resolve => {
                const interval = setInterval(() => {
                    if (index >= scrollTargets.length) {
                        clearInterval(interval);
                        resolve();
                        return;
                    }

                    const target = scrollTargets[index] * document.body.scrollHeight;
                    window.scrollTo({
                        top: target,
                        behavior: 'smooth'
                    });

                    index++;
                }, 1000);
            });
        }

        // 展开所有可折叠内容
        function expandCollapsibles() {
            // 展开按钮
            const expandButtons = document.querySelectorAll('button[aria-expanded="false"], [data-toggle="collapse"], [class*="expand"], [class*="more"], [class*="show"]');
            expandButtons.forEach(button => {
                try {
                    button.click();
                } catch (e) {}
            });

            // 展开细节
            const details = document.querySelectorAll('details:not([open])');
            details.forEach(detail => {
                try {
                    detail.setAttribute('open', 'true');
                } catch (e) {}
            });
        }

        // 移除遮盖元素
        function removeOverlays() {
            // 常见遮盖元素
            const overlaySelectors = [
                '[class*="overlay"]',
                '[class*="modal"]',
                '[class*="popup"]',
                '[class*="cookie"]',
                '[class*="banner"]',
                '[id*="overlay"]',
                '[id*="modal"]',
                '[id*="popup"]',
                '[id*="cookie"]',
                '[style*="z-index: 9"]',
                '[style*="position: fixed"]'
            ];

            overlaySelectors.forEach(selector => {
                try {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        if (el.style.zIndex > 1 ||
                            el.style.position === 'fixed' ||
                            getComputedStyle(el).position === 'fixed') {
                            el.remove();
                        }
                    });
                } catch (e) {}
            });

            // 移除body上的样式
            try {
                document.body.style.overflow = 'auto';
                document.body.style.position = 'static';
            } catch (e) {}
        }

        // 执行交互序列
        await simulateScrolling();
        removeOverlays();
        expandCollapsibles();
        simulateMouseMovement();
        await new Promise(r => setTimeout(r, 3000));
        removeOverlays();
        await simulateScrolling();

        return "用户交互模拟完成";
    }

    // 执行用户交互模拟
    await simulateUserInteraction();
    """

    interaction_config = CrawlerRunConfig(
        include_images=include_images,
        include_links=True,
        cache_mode=cache_mode,
        wait_for="document.readyState === 'complete'",
        page_timeout=120000,  # 120秒超长超时
        post_load_script=interaction_script + scroll_script,
        max_content_length=30000000  # 30MB
    )

    # 策略3：网络请求拦截
    intercept_script = """
    // 存储API响应
    window.apiResponses = [];

    // 拦截XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url) {
        this._url = url;
        return originalXHROpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function() {
        const xhr = this;
        const originalOnReadyStateChange = xhr.onreadystatechange;

        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    window.apiResponses.push({
                        url: xhr._url,
                        data: response
                    });
                } catch (e) {
                    // 非JSON响应，忽略
                }
            }

            if (originalOnReadyStateChange) {
                originalOnReadyStateChange.apply(xhr, arguments);
            }
        };

        return originalXHRSend.apply(xhr, arguments);
    };

    // 拦截Fetch API
    const originalFetch = window.fetch;
    window.fetch = async function(input, init) {
        const url = typeof input === 'string' ? input : input.url;
        const response = await originalFetch.apply(window, arguments);

        // 克隆响应以便我们可以读取内容
        const responseClone = response.clone();

        try {
            const data = await responseClone.json();
            window.apiResponses.push({
                url: url,
                data: data
            });
        } catch (e) {
            // 非JSON响应，忽略
        }

        return response;
    };
    """

    intercept_config = CrawlerRunConfig(
        include_images=include_images,
        include_links=True,
        cache_mode=cache_mode,
        wait_for="document.readyState === 'complete'",
        page_timeout=60000,  # 60秒超时
        pre_load_script=intercept_script,
        post_load_script=scroll_script,
        max_content_length=30000000  # 30MB
    )

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            # 尝试多种抓取策略
            strategies = [
                {"name": "标准增强策略", "config": standard_config},
                {"name": "用户交互策略", "config": interaction_config},
                {"name": "网络拦截策略", "config": intercept_config}
            ]

            best_result = None
            max_content_length = 0
            api_content = ""

            for strategy in strategies:
                logger.info(f"使用 {strategy['name']} 抓取 {url}")

                try:
                    result = await crawler.arun(
                        url=url,
                        config=strategy["config"]
                    )

                    if result.success:
                        content_length = len(result.markdown)
                        logger.info(
                            f"{strategy['name']} 成功，内容长度: {content_length}")

                        # 如果是网络拦截策略，尝试提取API响应
                        if strategy["name"] == "网络拦截策略":
                            try:
                                # 获取API响应
                                extract_responses_script = """
                                return window.apiResponses || [];
                                """

                                responses = await result.page.evaluate(extract_responses_script)

                                # 处理响应数据，提取内容
                                for response in responses:
                                    # 尝试从API响应中提取内容
                                    try:
                                        # 常见内容字段
                                        content_fields = [
                                            "content", "text", "body", "data", "article", "html"]
                                        for field in content_fields:
                                            if field in response["data"]:
                                                api_content += f"\n--- API响应内容 ({response['url']}) ---\n"
                                                api_content += json.dumps(
                                                    response["data"][field], ensure_ascii=False, indent=2)
                                                api_content += "\n"
                                                break
                                    except:
                                        pass
                            except Exception as e:
                                logger.error(f"提取API响应时出错: {str(e)}")

                        # 如果得到的内容更多，保存为最佳结果
                        if content_length > max_content_length:
                            max_content_length = content_length
                            best_result = result
                except Exception as e:
                    logger.error(f"{strategy['name']} 发生错误: {str(e)}")
                    continue

            # 如果所有策略都失败，尝试最基本的抓取
            if best_result is None:
                logger.warning(f"所有深度抓取策略都失败，尝试基本抓取")
                basic_config = CrawlerRunConfig(
                    include_images=include_images,
                    include_links=True,
                    cache_mode=cache_mode,
                    wait_for="document.readyState === 'complete'",
                    page_timeout=30000
                )

                result = await crawler.arun(
                    url=url,
                    config=basic_config
                )
                best_result = result

            # 构建响应
            markdown_content = best_result.markdown

            # 如果有API内容，添加到markdown末尾
            if api_content:
                markdown_content += "\n\n## API响应数据\n" + api_content

            response = {
                "success": best_result.success,
                "url": url,
                "title": best_result.metadata.get("title", ""),
                "markdown": markdown_content,
                "word_count": len(markdown_content.split()),
                "character_count": len(markdown_content),
                "crawl_time_ms": best_result.metadata.get("crawl_time_ms", 0),
                "deep_crawl": True  # 标记为深度抓取结果
            }

            # 如果包含图片，添加图片信息
            if include_images and best_result.media and "images" in best_result.media:
                response["images"] = len(best_result.media["images"])

                # 添加图片URL列表（最多10个）
                image_urls = [img.get("src", "")
                              for img in best_result.media["images"][:10]]
                if image_urls:
                    response["image_urls"] = image_urls

            return json.dumps(response, indent=2)

    except Exception as e:
        logger.error(f"深度抓取 {url} 时出错: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "deep_crawl": True
        })


async def intercept_network_requests(crawler, url, crawler_config):
    """
    拦截网络请求并提取API响应数据

    Args:
        crawler: 爬虫实例
        url: 目标URL
        crawler_config: 爬虫配置

    Returns:
        从API响应中提取的内容
    """
    # 添加网络请求拦截脚本
    intercept_script = """
    // 存储API响应
    window.apiResponses = [];

    // 拦截XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url) {
        this._url = url;
        return originalXHROpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function() {
        const xhr = this;
        const originalOnReadyStateChange = xhr.onreadystatechange;

        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    window.apiResponses.push({
                        url: xhr._url,
                        data: response
                    });
                } catch (e) {
                    // 非JSON响应，忽略
                }
            }

            if (originalOnReadyStateChange) {
                originalOnReadyStateChange.apply(xhr, arguments);
            }
        };

        return originalXHRSend.apply(xhr, arguments);
    };

    // 拦截Fetch API
    const originalFetch = window.fetch;
    window.fetch = async function(input, init) {
        const url = typeof input === 'string' ? input : input.url;
        const response = await originalFetch.apply(window, arguments);

        // 克隆响应以便我们可以读取内容
        const responseClone = response.clone();

        try {
            const data = await responseClone.json();
            window.apiResponses.push({
                url: url,
                data: data
            });
        } catch (e) {
            // 非JSON响应，忽略
        }

        return response;
    };
    """

    # 将拦截脚本添加到预加载脚本
    enhanced_config = crawler_config.copy()
    enhanced_config.pre_load_script = intercept_script

    # 运行爬虫
    result = await crawler.arun(url=url, config=enhanced_config)

    # 获取API响应
    extract_responses_script = """
    return window.apiResponses || [];
    """

    responses = await result.page.evaluate(extract_responses_script)

    # 处理响应数据，提取内容
    api_content = ""
    for response in responses:
        # 尝试从API响应中提取内容
        try:
            # 常见内容字段
            content_fields = ["content", "text",
                              "body", "data", "article", "html"]
            for field in content_fields:
                if field in response["data"]:
                    api_content += f"\n--- API响应内容 ({response['url']}) ---\n"
                    api_content += json.dumps(response["data"]
                                              [field], ensure_ascii=False, indent=2)
                    api_content += "\n"
                    break
        except:
            pass

    return result, api_content


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
        viewport_height=1080,
        browser_args=["--disable-web-security",
                      "--disable-features=IsolateOrigins,site-per-process"]
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
                page_timeout=45000,  # 增加页面超时时间
                post_load_script=scroll_script  # 使用增强的滚动脚本
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
                        "character_count": len(res.markdown),  # 添加字符计数
                        "markdown": res.markdown if len(res.markdown) < 10000 else res.markdown[:10000] + "...(内容过长，已截断)"
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
                },
                {
                    "name": "tables",
                    "selector": "table",
                    "type": "html",
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
            viewport_height=1080,
            browser_args=["--disable-web-security",
                          "--disable-features=IsolateOrigins,site-per-process"]
        )

        # 创建爬虫配置
        crawler_config = CrawlerRunConfig(
            wait_for=[
                "document.readyState === 'complete'",
                "document.querySelectorAll('p, h1, h2, h3, table, article, section, main').length > 0"
            ],
            extraction_strategy=extractor,
            page_timeout=60000,  # 增加超时时间
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
                crawler_config.page_timeout = 90000  # 增加到90秒
                crawler_config.post_load_script = interaction_script + scroll_script  # 使用交互脚本
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

    # 首先使用深度抓取获取完整内容
    try:
        deep_result_json = await deep_crawl_webpage_impl(url, include_images, CacheMode.DEFAULT)
        deep_result = json.loads(deep_result_json)

        if deep_result.get("success", False):
            # 确保文件名有.md扩展名
            if not filename.endswith('.md'):
                filename += '.md'

            # 保存为Markdown文件
            with open(filename, 'w', encoding='utf-8') as f:
                # 添加标题和元数据
                f.write(f"# {deep_result.get('title', 'Untitled')}\n\n")
                f.write(f"Source: {url}\n\n")
                f.write(
                    f"Saved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                # 写入正文
                f.write(deep_result.get("markdown", ""))

            return json.dumps({
                "success": True,
                "filename": filename,
                "title": deep_result.get("title", ""),
                "word_count": deep_result.get("word_count", 0),
                "character_count": deep_result.get("character_count", 0),
                "save_time": datetime.now().isoformat(),
                "deep_crawl": True
            }, indent=2)
        else:
            # 如果深度抓取失败，回退到标准爬取
            logger.warning(
                f"深度抓取失败，尝试标准爬取: {deep_result.get('error', '未知错误')}")
    except Exception as e:
        logger.warning(f"深度抓取失败，尝试标准爬取: {str(e)}")

    # 标准爬取方法（作为备用）
    try:
        # 配置浏览器
        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1920,
            viewport_height=1080,
            browser_args=["--disable-web-security",
                          "--disable-features=IsolateOrigins,site-per-process"]
        )

        # 配置爬虫
        crawler_config = CrawlerRunConfig(
            include_images=include_images,
            include_links=True,
            wait_for=[
                "document.readyState === 'complete'",
                "document.querySelectorAll('p, h1, h2, h3, article, section, main').length > 0"
            ],
            page_timeout=60000,  # 增加超时时间
            post_load_script=scroll_script
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

            # 确保文件名有.md扩展名
            if not filename.endswith('.md'):
                filename += '.md'

            # 保存为Markdown文件
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {result.metadata.get('title', 'Untitled')}\n\n")
                f.write(f"Source: {url}\n\n")
                f.write(
                    f"Saved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(result.markdown)

            return json.dumps({
                "success": True,
                "filename": filename,
                "title": result.metadata.get("title", ""),
                "word_count": len(result.markdown.split()),
                "character_count": len(result.markdown),
                "save_time": datetime.now().isoformat()
            }, indent=2)

    except Exception as e:
        logger.error(f"保存 {url} 为Markdown时出错: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })
