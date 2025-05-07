"""Orchestrates the core steps of sitemap fetching, processing, and structuring."""

import sys
from typing import Optional, List
from urllib.parse import urlparse 

from sdk.core.sitemap import fetch_sitemap_data
from sdk.core.processing import process_urls_concurrently
from sdk.core.structuring import structure_processed_data
from .utils import filter_urls
from sdk.core.models import StructuredData, SitemapUrlData, ProcessedPageData # Added SitemapUrlData, ProcessedPageData
from sdk.core.exceptions import SubtxtError

def _get_url_prefix(input_url: str) -> str:
    """Determines the base prefix string to filter URLs against."""
    try:
        parsed = urlparse(input_url)
        # Basic check for scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Input URL must have scheme and domain.")

        # If the input looks like a specific file, scope to the directory containing it, if not use full path
        path = parsed.path
        if path.endswith(('.xml', '.xml.gz', '.html', '.htm')):
             # Find the last '/'
             last_slash_index = path.rfind('/')
             if last_slash_index > 0: # Keep trailing slash if not root
                 path = path[:last_slash_index + 1]
             elif last_slash_index == 0: # Path was like /sitemap.xml
                 path = '/'
             else: # Path had no slashes, scope to root
                  path = '/'
        elif not path.endswith('/'):
             path += '/' # Ensure directory-like paths end with /

        # Reconstruct the prefix
        prefix = f"{parsed.scheme}://{parsed.netloc}{path}"
        # Handle root case explicitly - ensure it ends with /
        if path == '/':
             prefix = f"{parsed.scheme}://{parsed.netloc}/"

        return prefix
    except Exception as e:
        print(f"Warning: Could not reliably determine URL prefix from '{input_url}': {e}. Scoping to domain root.", file=sys.stderr)
        # Fallback to just the domain root if parsing fails badly
        parsed = urlparse(input_url)
        return f"{parsed.scheme or 'https'}://{parsed.netloc or ''}/"


async def generate_structured_data_orchestrator(
    sitemap_url: str, # This is the user's input URL, used for scoping
    *,
    include_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    replace_title: Optional[List[str]] = None,
    output_title: Optional[str] = None,
    output_description: Optional[str] = None,
    concurrency: int = 10,
    user_agent: str = "PythonSubtxtSdk/1.0"
) -> StructuredData:
    """
    Orchestrates fetching sitemap, filtering (scope + user), processing URLs, and structuring results.
    """
    print(f"Orchestrator: Starting data generation for scope: {sitemap_url}", file=sys.stderr)
    try:
        # Determine scope prefix
        url_scope_prefix = _get_url_prefix(sitemap_url)
        print(f"Orchestrator: Applying automatic scope filter: URLs must start with '{url_scope_prefix}'", file=sys.stderr)

        # Fetch all potential URLs from sitemaps
        sitemap_url_data_list: List[SitemapUrlData] = await fetch_sitemap_data(sitemap_url, user_agent)
        if not sitemap_url_data_list:
            return StructuredData(source_url=sitemap_url, main_title="Error", main_description="No URLs found in sitemap(s).", error="No URLs found in sitemap(s).")

        # Apply automatic scope filtering
        scoped_urls_data_dicts = []
        scope_filtered_count = 0
        for item in sitemap_url_data_list:
             if item.url.startswith(url_scope_prefix):
                  # Convert back to simple dict for next filter step
                  scoped_urls_data_dicts.append({'url': item.url, 'lastmod': item.lastmod})
             else:
                  scope_filtered_count += 1
        if scope_filtered_count > 0:
            print(f"Orchestrator: Automatically filtered out {scope_filtered_count} URLs outside the scope '{url_scope_prefix}'.", file=sys.stderr)

        if not scoped_urls_data_dicts:
             return StructuredData(source_url=sitemap_url, main_title="Error", main_description=f"No URLs found within the scope '{url_scope_prefix}'.", error=f"No URLs found within the specified scope.")

        # Apply user-defined include/exclude filters
        user_filtered_urls_data = filter_urls(scoped_urls_data_dicts, include_paths, exclude_paths)
        if not user_filtered_urls_data:
             return StructuredData(source_url=sitemap_url, main_title="Error", main_description="No URLs remained after applying user include/exclude filters.", error="No URLs remained after applying user filters.")

        # Process filtered URLs
        processed_page_data_list: List[ProcessedPageData] = await process_urls_concurrently(
            user_filtered_urls_data, # Pass the list of dicts
            replace_title or [],
            concurrency,
            user_agent
        )

        # Structure results
        final_structured_data = structure_processed_data(
             processed_page_data_list,
             sitemap_url, # Pass original input URL as source reference
             output_title,
             output_description
        )

        print(f"Orchestrator: Finished data generation for {sitemap_url}", file=sys.stderr)
        return final_structured_data

    except SubtxtError as e:
        print(f"❌ Orchestrator: Error during generation: {e}", file=sys.stderr)
        return StructuredData(source_url=sitemap_url, main_title="Error", main_description=f"Generation failed: {e}", error=str(e))
    except Exception as e:
        print(f"❌ Orchestrator: Unexpected error during generation: {e}", file=sys.stderr)
        return StructuredData(source_url=sitemap_url, main_title="Error", main_description=f"Unexpected generation failure: {e}", error=f"Unexpected failure: {e}")