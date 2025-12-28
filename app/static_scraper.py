
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


class StaticScraper:
    """Fetch and parse static HTML"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    
    async def fetch(self, url: str) -> Optional[str]:
        """Fetch HTML from URL"""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True
            ) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.user_agent}
                )
                response.raise_for_status()
                return response.text
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.status_code}: {url}")
            raise
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching {url}")
            raise
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            raise