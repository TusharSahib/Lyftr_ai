
import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


def is_absolute_url(url: str) -> bool:
    """Check if URL is absolute"""
    return url.startswith(("http://", "https://"))


def make_absolute_url(url: str, base_url: str) -> str:
    """Convert relative URL to absolute"""
    if is_absolute_url(url):
        return url
    return urljoin(base_url, url)


def same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from same domain"""
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    return domain1 == domain2


def truncate_html(html: str, max_chars: int = 2000) -> tuple[str, bool]:
    """
    Truncate HTML while preserving structure
    Returns: (truncated_html, was_truncated)
    """
    if len(html) <= max_chars:
        return html, False
    
    # Try to break at tag boundary
    truncated = html[:max_chars]
    last_tag = truncated.rfind("</")
    
    if last_tag > max_chars * 0.8:
        truncated = html[:last_tag + 4]  # Include </
    
    truncated += " ..."
    return truncated, True


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove multiple spaces
    text = " ".join(text.split())
    # Remove control characters
    text = "".join(c for c in text if ord(c) >= 32 or c in "\n\t\r")
    return text.strip()