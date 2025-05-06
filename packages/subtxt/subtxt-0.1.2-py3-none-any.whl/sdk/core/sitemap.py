"""Functions for fetching and parsing sitemap data with improved robustness."""

import sys
import asyncio
import gzip
import urllib.robotparser
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse, urljoin

import httpx
from usp.tree import sitemap_tree_for_homepage

from .exceptions import SitemapError
from .models import SitemapUrlData

# XML fetching and parsing helpers

async def _fetch_and_parse_xml(url: str, client: httpx.AsyncClient) -> Optional[ET.Element]:
    """Fetches a URL and attempts to parse it as XML (handles .gz). Logs cleanly."""
    try:
        print(f"  Fetching XML: {url}", file=sys.stderr)
        response = await client.get(url, follow_redirects=True, timeout=30.0)

        if response.status_code == 404:
            print(f"  Info: Sitemap URL not found (404): {url}", file=sys.stderr)
            return None
        elif response.status_code >= 400:
             print(f"  Warning: HTTP {response.status_code} fetching sitemap {url}", file=sys.stderr)
             response.raise_for_status() # Raise for other client/server errors

        content_type = response.headers.get('content-type', '').lower()
        content = response.content # Get bytes

        is_gzipped = url.endswith('.gz') or content.startswith(b'\x1f\x8b')
        if is_gzipped:
            try:
                content = gzip.decompress(content)
            except gzip.BadGzipFile:
                print(f"  Info: Couldn't gunzip {url}, attempting to parse as plain XML.", file=sys.stderr)
                pass # Fall through to parsing

        if 'xml' not in content_type and 'html' in content_type:
             print(f"  Warning: URL {url} returned HTML, not XML. Skipping.", file=sys.stderr)
             return None

        # Decode explicitly to handle potential encoding issues
        try:
            xml_string = content.decode('utf-8', errors='replace')
        except Exception:
             xml_string = content.decode('iso-8859-1', errors='replace')

        return ET.fromstring(xml_string)

    except httpx.RequestError as e:
        print(f"  Warning: Request failed for sitemap {url}: {e}", file=sys.stderr)
        return None
    except ET.ParseError as e:
        print(f"  Warning: Failed to parse XML from sitemap {url}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Warning: Unexpected error fetching/parsing sitemap {url}: {e}", file=sys.stderr)
        return None


async def _parse_sitemap_element(
    root: ET.Element,
    base_url: str,
    urls_data_dict: Dict[str, SitemapUrlData],
    client: httpx.AsyncClient,
    processed_sitemaps: Set[str]
    ):
    """Parses a sitemap XML element (handles both index and urlset)."""
    namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    sitemap_links = root.findall('.//sm:sitemap/sm:loc', namespaces)
    if sitemap_links:
        tasks = []
        new_sitemaps_to_process = []
        for loc_element in sitemap_links:
            if loc_element.text:
                sub_sitemap_url = urljoin(base_url, loc_element.text.strip())
                if sub_sitemap_url not in processed_sitemaps:
                    processed_sitemaps.add(sub_sitemap_url)
                    new_sitemaps_to_process.append(sub_sitemap_url)
                    tasks.append(_fetch_and_parse_xml(sub_sitemap_url, client))

        if not tasks: return # No new sitemaps found in this index

        sub_roots = await asyncio.gather(*tasks)
        parse_tasks = []
        for sub_root, sub_url in zip(sub_roots, new_sitemaps_to_process):
             if sub_root is not None:
                  parse_tasks.append(
                       _parse_sitemap_element(sub_root, base_url, urls_data_dict, client, processed_sitemaps)
                  )
        if parse_tasks:
             await asyncio.gather(*parse_tasks)
        return # Index processing complete

    url_elements = root.findall('.//sm:url', namespaces)
    if not url_elements and not sitemap_links: # Check if it was empty or unknown
         print(f"  Warning: XML element seems empty or not a standard sitemap/index format.", file=sys.stderr)
         return

    count = 0
    for url_element in url_elements:
        loc_element = url_element.find('sm:loc', namespaces)
        if loc_element is not None and loc_element.text:
            count += 1
            url = loc_element.text.strip()
            lastmod_element = url_element.find('sm:lastmod', namespaces)
            lastmod_str = lastmod_element.text.strip() if lastmod_element is not None and lastmod_element.text else None
            if url not in urls_data_dict or (lastmod_str and not urls_data_dict[url].lastmod):
                urls_data_dict[url] = SitemapUrlData(url=url, lastmod=lastmod_str)

# Robots.txt parsing helper
async def _get_sitemap_urls_from_robots(robots_url: str, client: httpx.AsyncClient) -> List[str]:
    """Fetches robots.txt and extracts Sitemap URLs using standard and manual parsing."""
    raw_text = None
    try:
        response = await client.get(robots_url, timeout=15.0)
        if response.status_code == 200:
            raw_text = response.text
        else:
             print(f"  Info: robots.txt not found or not accessible (Status: {response.status_code})", file=sys.stderr) # Debug
             return []
    except httpx.RequestError as e:
        print(f"  Warning: Failed to fetch robots.txt from {robots_url}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  Warning: Error fetching robots.txt from {robots_url}: {e}", file=sys.stderr)
        return []

    sitemaps_found = set()

    # Try standard parser
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(raw_text.splitlines())
        if rp.sitemaps:
            sitemaps_found.update(rp.sitemaps)
            print(f"  Found sitemaps via robotparser: {rp.sitemaps}", file=sys.stderr)
    except Exception as parse_err:
        print(f"  Warning: Error using standard robotparser: {parse_err}. Trying manual parse.", file=sys.stderr)

    # Try manual parsing (robust fallback)
    try:
        for line in raw_text.splitlines():
            line = line.strip()
            if line.lower().startswith('sitemap:'):
                try:
                    url = line.split(':', 1)[1].strip()
                    if url:
                        sitemaps_found.add(url)
                except IndexError: pass # Ignore malformed lines
    except Exception as manual_parse_err:
         print(f"  Warning: Error during manual robots.txt parse: {manual_parse_err}", file=sys.stderr)


    if sitemaps_found:
        print(f"  Found {len(sitemaps_found)} unique sitemap URLs in robots.txt.", file=sys.stderr)
        return list(sitemaps_found)
    else:
        print(f"  No sitemap URLs found in {robots_url}", file=sys.stderr)
        return []

async def fetch_sitemap_data(sitemap_url: str, user_agent: str) -> List[SitemapUrlData]:
    """
    Fetches and parses sitemap(s), returning a list of SitemapUrlData objects.
    Uses USP, then falls back to robots.txt and common defaults.
    """
    print(f"Starting sitemap data fetch for: {sitemap_url}", file=sys.stderr)
    urls_data_dict: Dict[str, SitemapUrlData] = {}
    processed_sitemaps: Set[str] = set() # Track processed sitemaps during fallback

    # Determine homepage URL
    try:
        parsed_start_url = urlparse(sitemap_url)
        scheme = parsed_start_url.scheme or 'https'
        netloc = parsed_start_url.netloc
        if not netloc: raise ValueError("Invalid URL")
        homepage = f"{scheme}://{netloc}"
        robots_url = urljoin(homepage, '/robots.txt')
    except ValueError as e:
        raise SitemapError(f"Invalid starting URL provided: {sitemap_url}") from e

    # Attempt 1: Use USP 
    try:
        print("Attempting sitemap discovery via USP...", file=sys.stderr)
        tree = sitemap_tree_for_homepage(homepage)
        if tree:
            page_count = 0
            for page in tree.all_pages():
                page_count += 1
                # Handle potential AttributeError if usp internal object lacks lastmod
                try:
                    lastmod_str = page.lastmod.isoformat() if hasattr(page, 'lastmod') and page.lastmod else None
                except AttributeError:
                    lastmod_str = None # Treat as if not present
                except Exception as iso_err: # Catch potential isoformat errors too
                     print(f"  Warning: Could not format lastmod for {page.url}: {iso_err}", file=sys.stderr)
                     lastmod_str = None

                if page.url not in urls_data_dict or (lastmod_str and not urls_data_dict[page.url].lastmod):
                     urls_data_dict[page.url] = SitemapUrlData(url=page.url, lastmod=lastmod_str)

            if page_count > 0:
                print(f"Successfully extracted {len(urls_data_dict)} unique URLs via USP.", file=sys.stderr)
                return list(urls_data_dict.values()) # Success with USP!
            else:
                 print("Info: USP found sitemap structure but yielded 0 URLs. Proceeding to fallback.", file=sys.stderr)
        else:
             print("Info: USP could not find sitemap structure. Proceeding to fallback.", file=sys.stderr)
    except AttributeError as e: # Catch the specific error seen with MDN
         print(f"Info: Encountered attribute error during USP processing ({e}). Proceeding to fallback.", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Error during USP processing: {e}. Proceeding to fallback.", file=sys.stderr)

    # Attempt 2: Fallback
    print("Attempting fallback: Checking robots.txt and common sitemap locations...", file=sys.stderr)
    async with httpx.AsyncClient(headers={"User-Agent": user_agent}, timeout=30.0, follow_redirects=True) as client:

        # Get URLs from robots.txt
        sitemap_urls_to_try = await _get_sitemap_urls_from_robots(robots_url, client)

        # Add common defaults ONLY if robots.txt yielded nothing
        if not sitemap_urls_to_try:
            print("Info: No sitemaps found in robots.txt, trying common defaults.", file=sys.stderr)
            sitemap_urls_to_try.extend([
                urljoin(homepage, '/sitemap.xml'),
                urljoin(homepage, '/sitemap_index.xml'),
                urljoin(homepage, '/sitemaps/sitemap.xml') # Keep this one just in case
            ])
        else:
            print(f"Found {len(sitemap_urls_to_try)} sitemaps via robots.txt. Processing these.", file=sys.stderr)


        fetch_tasks = []
        processed_sitemaps.clear() # Reset for fallback phase
        unique_urls_to_fetch = list(set(sitemap_urls_to_try)) # De-duplicate potential URLs

        for s_url in unique_urls_to_fetch:
             if s_url not in processed_sitemaps:
                processed_sitemaps.add(s_url)
                fetch_tasks.append(_fetch_and_parse_xml(s_url, client))
             else:
                 print(f"  Info: Skipping already processed sitemap: {s_url}", file=sys.stderr)

        if not fetch_tasks:
             print("Fallback: No valid sitemap URLs found to attempt fetching.", file=sys.stderr)
        else:
             print(f"Fallback: Attempting to fetch/parse {len(fetch_tasks)} potential sitemap(s)...", file=sys.stderr)
             root_elements = await asyncio.gather(*fetch_tasks)
             parse_tasks = []
             for root_element, s_url in zip(root_elements, unique_urls_to_fetch):
                 if root_element is not None:
                     # print(f"Fallback: Parsing content from {s_url}...", file=sys.stderr) # Debug
                     parse_tasks.append(
                          _parse_sitemap_element(root_element, homepage, urls_data_dict, client, processed_sitemaps)
                     )

             if parse_tasks:
                 try:
                     await asyncio.gather(*parse_tasks)
                     print(f"Fallback processing complete. Total unique URLs found: {len(urls_data_dict)}", file=sys.stderr)
                 except Exception as e:
                     print(f"Warning: Error during fallback parsing gather: {e}", file=sys.stderr)

    if not urls_data_dict:
         raise SitemapError(f"Failed to extract any URLs using USP or fallback methods for {sitemap_url}")

    print(f"Finished sitemap data fetch. Total unique URLs: {len(urls_data_dict)}", file=sys.stderr)
    return list(urls_data_dict.values())