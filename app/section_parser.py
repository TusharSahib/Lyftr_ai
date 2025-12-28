
import logging
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString, Tag

from app.models import Section, ContentData, ContentLink, ContentImage

logger = logging.getLogger(__name__)

# Configuration
MAX_RAW_HTML_LENGTH = 2000
NOISE_SELECTORS = [
    ".cookie-banner", ".cookie-notice", "[data-cookie]",
    ".modal:not(.modal.active)", ".popup", "[role='dialog']",
    "[data-ad-slot]", ".ad-container", "iframe[src*='ads']",
    ".newsletter-popup", ".modal-backdrop",
    "[class*='advertisement']", "[class*='consent']"
]


def parse_sections_from_html(html: str, base_url: str) -> List[Section]:
    """
    Parse HTML into semantic sections
    Groups by landmarks, headings, and content blocks
    """
    soup = BeautifulSoup(html, "lxml")
    
    # Remove noise
    for selector in NOISE_SELECTORS:
        for element in soup.select(selector):
            element.decompose()
    
    # Remove scripts and styles
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    sections = []
    section_id = 0
    processed_elements = set()
    
    # Stage 1: Extract landmark-based sections
    for landmark in ["header", "nav", "main", "section", "article", "footer"]:
        for element in soup.find_all(landmark, recursive=True):
            if element not in processed_elements:
                section = _extract_section_from_element(
                    element, base_url, f"{landmark}-{section_id}"
                )
                if section and section.content.text.strip():
                    sections.append(section)
                    section_id += 1
                    processed_elements.add(element)
    
    # Stage 2: Extract heading-based sections
    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        if heading not in processed_elements:
            section = _extract_heading_section(
                heading, base_url, f"section-{section_id}"
            )
            if section and section.content.text.strip():
                sections.append(section)
                section_id += 1
                processed_elements.add(heading)
    
    # Stage 3: Extract remaining significant blocks
    for div in soup.find_all("div", class_=True):
        if div not in processed_elements:
            # Check if div looks like a section (has significant content)
            text_len = len(div.get_text(strip=True))
            if text_len > 200:  # Significant content
                section = _extract_section_from_element(
                    div, base_url, f"block-{section_id}"
                )
                if section and section.content.text.strip():
                    sections.append(section)
                    section_id += 1
                    processed_elements.add(div)
    
    # Deduplicate similar sections
    sections = _deduplicate_sections(sections)
    
    # Assign types
    for section in sections:
        section.type = _detect_section_type(section)
    
    return sections


def _extract_section_from_element(element: Tag, base_url: str, section_id: str) -> Optional[Section]:
    """Extract a section from a DOM element"""
    if not element or not element.name:
        return None
    
    # Extract heading
    heading_elem = element.find(["h1", "h2", "h3", "h4", "h5", "h6"])
    heading_text = heading_elem.get_text(strip=True) if heading_elem else ""
    
    # Extract all text
    text = element.get_text(strip=True)
    if len(text) > 10000:
        text = text[:10000]  # Truncate very long text
    
    # Extract headings
    headings = []
    for h in element.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        h_text = h.get_text(strip=True)
        if h_text:
            headings.append(h_text)
    
    # Extract links
    links = []
    for a in element.find_all("a", href=True):
        href = a.get("href", "")
        if href:
            # Make absolute URL
            href = urljoin(base_url, href)
            if href.startswith(("http://", "https://")):
                link_text = a.get_text(strip=True) or href
                links.append(ContentLink(text=link_text, href=href))
    
    # Extract images
    images = []
    for img in element.find_all("img"):
        src = img.get("src", "")
        if src:
            src = urljoin(base_url, src)
            alt = img.get("alt", "")
            images.append(ContentImage(src=src, alt=alt))
    
    # Extract lists
    lists = []
    for ul_ol in element.find_all(["ul", "ol"]):
        items = []
        for li in ul_ol.find_all("li", recursive=False):
            item_text = li.get_text(strip=True)
            if item_text:
                items.append(item_text)
        if items:
            lists.append(items)
    
    # Extract tables
    tables = []
    for table in element.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            row = []
            for td in tr.find_all(["td", "th"]):
                row.append(td.get_text(strip=True))
            if row:
                rows.append(row)
        if rows:
            tables.append(rows)
    
    # Generate label
    label = heading_text or _generate_label_from_text(text)
    if not label:
        label = element.name.title()
    
    # Get raw HTML
    raw_html = str(element)[:MAX_RAW_HTML_LENGTH]
    truncated = len(str(element)) > MAX_RAW_HTML_LENGTH
    
    return Section(
        id=section_id,
        type="unknown",  # Will be assigned later
        label=label,
        sourceUrl=base_url,
        content=ContentData(
            headings=headings,
            text=text,
            links=links,
            images=images,
            lists=lists,
            tables=tables
        ),
        rawHtml=raw_html,
        truncated=truncated
    )


def _extract_heading_section(heading: Tag, base_url: str, section_id: str) -> Optional[Section]:
    """Extract a section starting from a heading"""
    heading_text = heading.get_text(strip=True)
    
    # Collect sibling content until next heading
    content_elements = []
    current = heading.next_sibling
    
    while current:
        if isinstance(current, NavigableString):
            if str(current).strip():
                content_elements.append(current)
        elif isinstance(current, Tag):
            # Stop at next heading
            if current.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                break
            content_elements.append(current)
        
        current = current.next_sibling
        
        if len(content_elements) > 20:  # Limit elements per section
            break
    
    # Create temporary container
    container = BeautifulSoup("", "lxml").new_tag("div")
    container.append(heading)
    for elem in content_elements:
        if isinstance(elem, Tag):
            container.append(elem)
    
    return _extract_section_from_element(container, base_url, section_id)


def _generate_label_from_text(text: str, max_words: int = 7) -> str:
    """Generate human-readable label from first words of text"""
    words = text.split()[:max_words]
    label = " ".join(words)
    
    # Truncate at word boundary
    if len(label) > 60:
        label = label[:60].rsplit(" ", 1)[0]
    
    return label


def _deduplicate_sections(sections: List[Section]) -> List[Section]:
    """Remove duplicate or highly overlapping sections"""
    unique = []
    seen_text = set()
    
    for section in sections:
        # Create hash of content
        content_hash = hash(section.content.text[:200])
        
        if content_hash not in seen_text:
            unique.append(section)
            seen_text.add(content_hash)
    
    return unique


def _detect_section_type(section: Section) -> str:
    """Detect section type based on content characteristics"""
    text = section.content.text.lower()
    label = section.label.lower()
    
    # Hero/Banner
    if ("hero" in label or "banner" in label or "welcome" in label):
        if section.content.images:
            return "hero"
    
    # Navigation
    if ("nav" in label or "menu" in label):
        return "nav"
    
    # Footer
    if "footer" in label or "copyright" in label or "contact us" in label:
        return "footer"
    
    # List
    if section.content.lists and len(section.content.lists) > 1:
        return "list"
    
    # Grid (multiple columns via images or divs)
    if len(section.content.images) > 4:
        return "grid"
    
    # FAQ
    if ("faq" in label or "question" in label or "answer" in label):
        if ("q:" in text or "a:" in text or "?" in text):
            return "faq"
    
    # Pricing
    if ("pricing" in label or "plan" in label or "price" in label):
        if any(c in text for c in ["$", "€", "¥", "₹"]):
            return "pricing"
    
    # Default to section
    return "section"