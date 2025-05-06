"""Functions for fetching HTML and extracting metadata from pages."""

import asyncio
import sys
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup, SoupStrainer
from tqdm.asyncio import tqdm as tqdm_async

from ..utils import clean_title, substitute_title, parse_section
from .models import ProcessedPageData

# Define strainers for faster parsing
_TITLE_STRAINER = SoupStrainer("title")
_META_STRAINER = SoupStrainer("meta", attrs={'name': ['description', 'twitter:description'], 'property': ['og:description']})
_HEAD_STRAINER = SoupStrainer("head")


async def fetch_html(url: str, client: httpx.AsyncClient, user_agent: str) -> Optional[str]:
    """Fetches HTML content from a URL asynchronously."""
    headers = {"User-Agent": user_agent}
    try:
        response = await client.get(url, headers=headers, follow_redirects=True, timeout=20.0)
        response.raise_for_status()
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            return response.text
        else:
            return None # Skip non-html
    except httpx.RequestError as exc:
        print(f"Warning: Request failed for {url}: {exc}", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"Warning: Unexpected error fetching {url}: {exc}", file=sys.stderr)
        return None


def _parse_html(html: str, strainer: Optional[SoupStrainer] = None) -> Optional[BeautifulSoup]:
    """Parses HTML using BeautifulSoup with optional strainer."""
    if not html: return None
    try:
        return BeautifulSoup(html, 'lxml', parse_only=strainer)
    except ImportError:
        try:
            return BeautifulSoup(html, 'html.parser', parse_only=strainer)
        except Exception as e:
            print(f"Warning: Failed to parse HTML snippet: {e}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Warning: Failed parsing HTML: {e}", file=sys.stderr)
        return None


def get_title(html: str) -> Optional[str]:
    """Extracts the title tag content from HTML using a strainer."""
    soup = _parse_html(html, strainer=_HEAD_STRAINER) # Strainer focuses parsing
    if not soup: return None
    try:
        title_tag = soup.find('title') # Find within the parsed head
        if title_tag and title_tag.string:
            return ' '.join(title_tag.string.strip().split())
    except Exception: pass
    return None


def get_description(html: str) -> Optional[str]:
    """Extracts the meta description content from HTML using a strainer."""
    soup = _parse_html(html, strainer=_META_STRAINER)
    if not soup: return None
    description = None
    try:
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc['content']
        if not description:
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                description = og_desc['content']
        if not description:
            twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
            if twitter_desc and twitter_desc.get('content'):
                description = twitter_desc['content']
        if description:
             return ' '.join(description.strip().split())
    except Exception: pass
    return None


async def process_single_url(
    sitemap_entry: Dict[str, Any], # Expects {'url': str, 'lastmod': Optional[str]}
    client: httpx.AsyncClient,
    replace_title_commands: List[str],
    semaphore: asyncio.Semaphore,
    pbar: tqdm_async,
    user_agent: str
) -> Optional[ProcessedPageData]:
    """
    Fetches, parses, and processes a single URL based on sitemap data.
    Returns ProcessedPageData object or None on failure.
    """
    url = sitemap_entry['url']
    sitemap_lastmod = sitemap_entry.get('lastmod')

    async with semaphore: # Limit concurrency
        short_url = urlparse(url).path[:40] + '...' if urlparse(url).path and len(urlparse(url).path) > 40 else urlparse(url).path or url
        pbar.set_description(f"Fetching {short_url}")

        html = await fetch_html(url, client, user_agent)
        if not html:
            pbar.update(1)
            return None

        pbar.set_description(f"Parsing {short_url}")

        title = get_title(html)
        if not title:
             pbar.update(1); return None

        title = substitute_title(title, replace_title_commands)
        title = clean_title(title)
        if not title:
             pbar.update(1); return None

        description = get_description(html)
        section = parse_section(url)
        pbar.update(1)

        return ProcessedPageData(
            url=url,
            title=title,
            section=section,
            description=description,
            sitemap_lastmod=sitemap_lastmod
        )

async def process_urls_concurrently(
    urls_data: List[Dict[str, Any]], # List of {'url': ..., 'lastmod': ...}
    replace_title_commands: List[str],
    concurrency: int,
    user_agent: str
) -> List[ProcessedPageData]:
    """
    Processes a list of URLs concurrently, returning processed page data.

    Args:
        urls_data: List of dictionaries from sitemap parsing.
        replace_title_commands: List of sed-style commands for title substitution.
        concurrency: Maximum number of concurrent requests.
        user_agent: User-Agent string.

    Returns:
        List of ProcessedPageData objects for successfully processed URLs.
    """
    processed_results: List[ProcessedPageData] = []
    semaphore = asyncio.Semaphore(concurrency)
    # Use a single client for connection pooling
    async with httpx.AsyncClient(headers={"User-Agent": user_agent}, verify=False) as client:
        tasks = []
        total = len(urls_data)

        with tqdm_async(total=total, desc="Processing URLs", unit="url", file=sys.stderr) as pbar:
            for item_data in urls_data:
                tasks.append(asyncio.ensure_future(
                    process_single_url(
                        item_data, client, replace_title_commands, semaphore, pbar, user_agent
                    )
                ))
            results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_count = 0
        error_count = 0
        skipped_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_count += 1
                print(f"Error processing {urls_data[i]['url']}: {result}", file=sys.stderr)
            elif isinstance(result, ProcessedPageData):
                 processed_results.append(result)
                 processed_count += 1
            else: # Result was None
                skipped_count +=1

    print(f"\nProcessed {processed_count} URLs successfully.", file=sys.stderr)
    if error_count > 0: print(f"Encountered errors processing {error_count} URLs.", file=sys.stderr)
    if skipped_count > 0: print(f"Skipped {skipped_count} URLs due to fetch errors or lack of title.", file=sys.stderr)

    return processed_results