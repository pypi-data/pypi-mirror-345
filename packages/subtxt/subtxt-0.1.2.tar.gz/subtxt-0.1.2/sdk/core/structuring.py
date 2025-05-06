"""Functions for structuring processed page data."""

from typing import List, Dict, Optional
from datetime import datetime, timezone

from .models import ProcessedPageData, StructuredData
from ..utils import capitalize_string
from urllib.parse import urlparse

def structure_processed_data(
    processed_data: List[ProcessedPageData],
    source_url: str,
    output_title: Optional[str],
    output_description: Optional[str]
) -> StructuredData:
    """
    Organizes processed page data into the final StructuredData object.

    Args:
        processed_data: List of successfully processed ProcessedPageData objects.
        source_url: The original URL used for sitemap discovery.
        output_title: Optional override for the main title.
        output_description: Optional override for the main description.

    Returns:
        A StructuredData object.
    """
    sections: Dict[str, List[ProcessedPageData]] = {}
    root_page_data: Optional[ProcessedPageData] = None

    # Sort processed data by URL for consistent flat list in state
    sorted_processed_data = sorted(processed_data, key=lambda x: x.url)

    # Find root page and populate sections
    for result in sorted_processed_data:
        if result.section == 'ROOT':
            if root_page_data is None: # Take the first root page found
                root_page_data = result
        else:
            # Capitalize section name for display later
            section_name_display = capitalize_string(result.section.replace('-', ' ').replace('_', ' '))
            sections.setdefault(section_name_display, []).append(result)

    # Determine final title and description
    final_title = output_title or (root_page_data.title if root_page_data else "Documentation")
    default_desc = f"Generated documentation from sitemap for {urlparse(source_url).netloc or source_url}"
    final_description = output_description or (root_page_data.description if root_page_data and root_page_data.description else default_desc)

    # Sort sections by name and items within sections by title
    structured_sections: Dict[str, List[ProcessedPageData]] = {}
    for section_name in sorted(sections.keys()):
        # Items within the section are already ProcessedPageData objects
        sorted_items = sorted(sections[section_name], key=lambda item: item.title)
        structured_sections[section_name] = sorted_items

    return StructuredData(
        source_url=source_url,
        main_title=final_title,
        main_description=final_description,
        sections=structured_sections,
        pages=sorted_processed_data, # Store the flat, sorted list
        generation_timestamp=datetime.now(timezone.utc).isoformat()
    )
