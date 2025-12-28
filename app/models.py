
from typing import List, Optional, Literal, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ContentLink(BaseModel):
    """Hyperlink in section"""
    text: str
    href: str


class ContentImage(BaseModel):
    """Image reference in section"""
    src: str
    alt: str


class ContentData(BaseModel):
    """Content extracted from a section"""
    headings: List[str] = Field(default_factory=list)
    text: str = ""
    links: List[ContentLink] = Field(default_factory=list)
    images: List[ContentImage] = Field(default_factory=list)
    lists: List[List[str]] = Field(default_factory=list)
    tables: List[Any] = Field(default_factory=list)


class Section(BaseModel):
    """A section of a webpage"""
    id: str  # Unique identifier (e.g., "hero-0", "section-1")
    type: Literal["hero", "nav", "section", "list", "grid", "faq", "pricing", "footer", "unknown"]
    label: str  # Human-readable label
    sourceUrl: str  # URL where this section came from
    content: ContentData
    rawHtml: str  # HTML snippet (truncated)
    truncated: bool  # Whether rawHtml was truncated


class Metadata(BaseModel):
    """Page metadata"""
    title: str = ""
    description: str = ""
    language: str = "en"
    canonical: Optional[str] = None


class Interactions(BaseModel):
    """User interactions detected during scraping"""
    clicks: List[str] = Field(default_factory=list)  # CSS selectors or descriptions
    scrolls: int = 0  # Number of scroll actions
    pages: List[str] = Field(default_factory=list)  # URLs visited


class ScraperError(BaseModel):
    """An error that occurred during scraping"""
    message: str
    phase: str  # "fetch", "render", "parse", "click", "scroll", etc.


class ScraperResult(BaseModel):
    """Complete scraping result"""
    url: str  # Exact input URL
    scrapedAt: str  # ISO8601 datetime UTC
    meta: Metadata
    sections: List[Section]
    interactions: Interactions
    errors: List[ScraperError] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "scrapedAt": "2025-12-28T23:02:00Z",
                "meta": {
                    "title": "Example Domain",
                    "description": "Example of a domain",
                    "language": "en",
                    "canonical": "https://example.com"
                },
                "sections": [
                    {
                        "id": "hero-0",
                        "type": "hero",
                        "label": "Hero Section",
                        "sourceUrl": "https://example.com",
                        "content": {
                            "headings": ["Welcome to Example"],
                            "text": "This domain is for use in examples...",
                            "links": [{"text": "More info", "href": "https://example.com/info"}],
                            "images": [{"src": "https://example.com/img.png", "alt": "Hero"}],
                            "lists": [],
                            "tables": []
                        },
                        "rawHtml": "<section>...</section>",
                        "truncated": True
                    }
                ],
                "interactions": {
                    "clicks": [],
                    "scrolls": 0,
                    "pages": ["https://example.com"]
                },
                "errors": []
            }
        }