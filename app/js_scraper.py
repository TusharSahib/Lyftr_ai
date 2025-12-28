
import asyncio
import logging
from typing import Optional, List
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from app.models import Interactions

logger = logging.getLogger(__name__)


class JSScraper:
    """Render and extract content from JS-heavy pages"""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
    
    async def render(self, url: str) -> Optional[str]:
        """Render page with Playwright and return HTML"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    viewport={"width": 1280, "height": 720}
                )
                
                page = await context.new_page()
                
                try:
                    # Navigate with timeout
                    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    
                    # Wait for content
                    try:
                        await page.wait_for_load_state("networkidle", timeout=10000)
                    except PlaywrightTimeout:
                        # Fallback: wait for selector
                        try:
                            await page.wait_for_selector("body", timeout=5000)
                        except PlaywrightTimeout:
                            # Last resort: fixed sleep
                            await page.wait_for_timeout(2000)
                    
                    # Get rendered HTML
                    content = await page.content()
                    return content
                
                finally:
                    await context.close()
                    await browser.close()
        
        except PlaywrightTimeout:
            logger.error(f"Playwright timeout rendering {url}")
            raise TimeoutError(f"JS rendering timed out for {url}")
        except Exception as e:
            logger.error(f"Error rendering {url}: {e}")
            raise
    
    async def handle_interactions(self, url: str) -> Optional[Interactions]:
        """
        Handle user interactions: tabs, load more, pagination, infinite scroll
        Returns interactions object with clicks, scrolls, and visited pages
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    viewport={"width": 1280, "height": 720}
                )
                page = await context.new_page()
                
                try:
                    visited_pages = [url]
                    clicks_performed = []
                    scroll_count = 0
                    
                    # Navigate to URL
                    await page.goto(url, wait_until="networkidle", timeout=15000)
                    await page.wait_for_timeout(1000)
                    
                    # 1. Click tabs
                    tab_selectors = [
                        "[role='tab']",
                        ".tab-button",
                        ".nav-tab",
                        "button[aria-selected='false']"
                    ]
                    
                    for selector in tab_selectors:
                        elements = await page.query_selector_all(selector)
                        for i, element in enumerate(elements[:5]):  # Max 5 tabs
                            try:
                                is_visible = await element.is_visible()
                                if is_visible:
                                    await element.click()
                                    clicks_performed.append(f"{selector}[{i}]")
                                    await page.wait_for_timeout(1500)
                            except Exception as e:
                                logger.debug(f"Tab click failed: {e}")
                    
                    # 2. Click "Load More" buttons
                    load_more_selectors = [
                        "button:has-text('Load More')",
                        "button:has-text('Show More')",
                        "button:has-text('View More')",
                        "a:has-text('Load More')",
                        "[data-action='load-more']"
                    ]
                    
                    for i in range(3):  # Max 3 load more clicks
                        clicked = False
                        for selector in load_more_selectors:
                            try:
                                elements = await page.query_selector_all(selector)
                                if elements:
                                    await elements[0].click()
                                    clicks_performed.append(selector)
                                    await page.wait_for_timeout(1500)
                                    clicked = True
                                    break
                            except Exception:
                                pass
                        if not clicked:
                            break
                    
                    # 3. Handle pagination
                    pagination_selectors = [
                        "a[rel='next']",
                        ".pagination a.next",
                        "a:has-text('Next')",
                        "a[aria-label='Next page']"
                    ]
                    
                    for i in range(3):  # Max 3 pages
                        found_next = False
                        for selector in pagination_selectors:
                            try:
                                next_link = await page.query_selector(selector)
                                if next_link:
                                    next_url = await next_link.get_attribute("href")
                                    if next_url:
                                        if not next_url.startswith("http"):
                                            from urllib.parse import urljoin
                                            next_url = urljoin(url, next_url)
                                        
                                        if next_url not in visited_pages and next_url.startswith(("http://", "https://")):
                                            await page.goto(next_url, wait_until="networkidle", timeout=10000)
                                            visited_pages.append(next_url)
                                            found_next = True
                                            await page.wait_for_timeout(500)
                                            break
                            except Exception:
                                pass
                        if not found_next:
                            break
                    
                    # 4. Infinite scroll
                    for i in range(3):  # Max 3 scrolls
                        try:
                            # Get current height
                            prev_height = await page.evaluate("document.body.scrollHeight")
                            
                            # Scroll down
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            
                            # Wait for new content
                            try:
                                await page.wait_for_load_state("networkidle", timeout=5000)
                            except:
                                await page.wait_for_timeout(2000)
                            
                            # Check new height
                            new_height = await page.evaluate("document.body.scrollHeight")
                            
                            if new_height > prev_height:
                                scroll_count += 1
                            else:
                                break  # No new content
                        except Exception as e:
                            logger.debug(f"Scroll failed: {e}")
                            break
                    
                    # Return interactions
                    return Interactions(
                        pages=visited_pages,
                        clicks=clicks_performed,
                        scrolls=scroll_count
                    )
                
                finally:
                    await context.close()
                    await browser.close()
        
        except Exception as e:
            logger.warning(f"Interaction handling failed: {e}")
            return Interactions(pages=[url])