# subtxt/core/models.py
"""Data models used within the subtxt SDK."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

@dataclass
class SitemapUrlData:
    """Represents data extracted directly from the sitemap for a URL."""
    url: str
    lastmod: Optional[str] = None

@dataclass
class ProcessedPageData:
    """Represents processed data for a single page after fetching and parsing."""
    url: str
    title: str
    section: str
    description: Optional[str] = None
    sitemap_lastmod: Optional[str] = None
    html: Optional[str] = None


@dataclass
class StructuredData:
    """Represents the fully structured data ready for rendering or state comparison."""
    source_url: str
    main_title: str
    main_description: str
    generation_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sections: Dict[str, List[ProcessedPageData]] = field(default_factory=dict)
    pages: List[ProcessedPageData] = field(default_factory=list)
    error: Optional[str] = None