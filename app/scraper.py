
import asyncio
import logging
from datetime import datetime
from typing import Optional, List
from urllib.parse import urljoin, urlparse

from app.models import ScraperResult, Metadata, Interactions, ScraperError, Section, ContentData
from app.static_scraper import StaticScraper
from app.js_scraper import JSScraper
from app.section_parser import parse_sections_from_html

logger = logging.getLogger(__name__)

# Configuration
STATIC_CONTENT_MIN_LENGTH = 500
STATIC_HEADING_REQUIRED = True
JS_RENDER_THRESHOLD = 500


class WebScraper:
    """Main orchestrator for web scraping"""
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        self.static_scraper = StaticScraper(timeout=10)
        self.js_scraper = JSScraper(timeout=15)
        self.errors: List[ScraperError] = []
    
    async def scrape(self, url: str) -> ScraperResult:
        """
        Scrape a URL using intelligent static-first, JS-fallback strategy
        
        Returns: ScraperResult with all required fields per schema
        """
        self.errors = []
        visited_urls = {url}
        all_html_content = ""
        
        try:
            # Stage 1: Try static scraping
            logger.info(f"[STATIC] Starting static scrape of {url}")
            static_html = await self._fetch_static(url)
            
            if static_html:
                all_html_content = static_html
                quality_score = self._assess_content_quality(static_html)
                logger.info(f"[STATIC] Content quality score: {quality_score}")
                
                # If static content is insufficient, trigger JS rendering
                if quality_score < JS_RENDER_THRESHOLD:
                    logger.info(f"[JS] Static content insufficient, triggering JS rendering")
                    try:
                        js_html = await self._fetch_with_js(url)
                        if js_html and len(js_html) > len(static_html):
                            all_html_content = js_html
                            self.errors.append(ScraperError(
                                message="Static content insufficient, used JS rendering",
                                phase="fallback"
                            ))
                    except Exception as e:
                        logger.error(f"[JS] JS rendering failed: {e}")
                        self.errors.append(ScraperError(
                            message=f"JS rendering failed: {str(e)}",
                            phase="render"
                        ))
            else:
                # No static content, must use JS
                logger.info(f"[JS] No static content, using JS rendering")
                try:
                    all_html_content = await self._fetch_with_js(url)
                except Exception as e:
                    logger.error(f"[JS] JS rendering failed: {e}")
                    self.errors.append(ScraperError(
                        message=f"JS rendering failed: {str(e)}",
                        phase="render"
                    ))
            
            # Stage 2: Parse HTML into sections
            logger.info(f"[PARSE] Parsing sections from HTML ({len(all_html_content)} chars)")
            sections = parse_sections_from_html(all_html_content, url)
            
            # Stage 3: Extract metadata
            logger.info(f"[META] Extracting metadata")
            meta = self._extract_metadata(all_html_content, url)
            
            # Stage 4: Handle interactions (tabs, load more, pagination)
            logger.info(f"[INTERACTIONS] Detecting interactions")
            interactions = await self._handle_interactions(url)
            visited_urls.update(interactions.pages)
            
            # Stage 5: Build result
            result = ScraperResult(
                url=url,
                scrapedAt=datetime.utcnow().isoformat() + "Z",
                meta=meta,
                sections=sections if sections else [self._create_empty_section(url)],
                interactions=interactions,
                errors=self.errors
            )
            
            logger.info(f"[SUCCESS] Scrape complete: {len(sections)} sections, {len(interactions.pages)} pages")
            return result
        
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error: {e}", exc_info=True)
            self.errors.append(ScraperError(message=str(e), phase="unknown"))
            
            # Return minimal valid result
            return ScraperResult(
                url=url,
                scrapedAt=datetime.utcnow().isoformat() + "Z",
                meta=Metadata(language="en"),
                sections=[],
                interactions=Interactions(pages=[url]),
                errors=self.errors
            )
    
    async def _fetch_static(self, url: str) -> Optional[str]:
        """Fetch and return static HTML"""
        try:
            html = await asyncio.wait_for(
                self.static_scraper.fetch(url),
                timeout=10
            )
            return html
        except asyncio.TimeoutError:
            self.errors.append(ScraperError(
                message="Static fetch timed out",
                phase="fetch"
            ))
            return None
        except Exception as e:
            self.errors.append(ScraperError(
                message=f"Static fetch failed: {str(e)}",
                phase="fetch"
            ))
            return None
    
    async def _fetch_with_js(self, url: str) -> Optional[str]:
        """Fetch and return JS-rendered HTML"""
        try:
            html = await asyncio.wait_for(
                self.js_scraper.render(url),
                timeout=15
            )
            return html
        except asyncio.TimeoutError:
            self.errors.append(ScraperError(
                message="JS rendering timed out",
                phase="render"
            ))
            return None
        except Exception as e:
            self.errors.append(ScraperError(
                message=f"JS rendering failed: {str(e)}",
                phase="render"
            ))
            return None
    
    def _assess_content_quality(self, html: str) -> int:
        """
        Score HTML content quality to determine if JS rendering is needed
        Higher score = better content
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, "lxml")
        
        # Remove script/style
        for tag in soup(["script", "style"]):
            tag.decompose()
        
        # Count text
        text = soup.get_text(strip=True)
        text_length = len(text)
        
        # Check for main element
        has_main = bool(soup.find(["main", "article"]))
        
        # Check for heading
        has_heading = bool(soup.find(["h1", "h2", "h3"]))
        
        # Score
        score = text_length
        if has_main:
            score += 300
        if has_heading:
            score += 200
        
        return score
    
    async def _handle_interactions(self, url: str) -> Interactions:
        """
        Detect and handle user interactions:
        - Tab clicks
        - Load more buttons
        - Pagination
        - Infinite scroll
        
        Returns interactions object with clicks, scrolls, pages
        """
        interactions = Interactions(pages=[url], clicks=[], scrolls=0)
        
        try:
            # Use JS scraper to handle interactions
            result = await asyncio.wait_for(
                self.js_scraper.handle_interactions(url),
                timeout=20
            )
            
            if result:
                interactions = result
        except Exception as e:
            logger.warning(f"Interaction handling failed: {e}")
            # Return minimal interactions object
            interactions = Interactions(pages=[url])
        
        return interactions
    
    def _extract_metadata(self, html: str, url: str) -> Metadata:
        """Extract page metadata"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, "lxml")
        
        # Title
        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)
        if not title:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = og_title.get("content", "")
        
        # Description
        description = ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag:
            description = desc_tag.get("content", "")
        if not description:
            og_desc = soup.find("meta", property="og:description")
            if og_desc:
                description = og_desc.get("content", "")
        
        # Language
        language = "en"
        html_tag = soup.find("html")
        if html_tag:
            language = html_tag.get("lang", "en").split("-")[0]
        
        # Canonical
        canonical = None
        canonical_tag = soup.find("link", attrs={"rel": "canonical"})
        if canonical_tag:
            canonical = canonical_tag.get("href")
        
        return Metadata(
            title=title,
            description=description,
            language=language,
            canonical=canonical
        )
    
    def _create_empty_section(self, url: str) -> Section:
        """Create a placeholder section when no content found"""
        return Section(
            id="empty-0",
            type="unknown",
            label="No Content Found",
            sourceUrl=url,
            content=ContentData(text="Unable to extract content from this page"),
            rawHtml="",
            truncated=False
        )