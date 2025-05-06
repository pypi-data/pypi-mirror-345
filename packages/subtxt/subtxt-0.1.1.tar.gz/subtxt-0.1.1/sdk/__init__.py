# subtxt/__init__.py
"""
Public API for subtxt SDK.

Provides core functions for generating website structure data and rendering
it to llms.txt format, a convenience function for generating llms.txt, and a CLI watcher entry point.
"""
from __future__ import annotations

import asyncio
import sys
from typing import Optional, List

# Import core SDK components
from .core.models import StructuredData, ProcessedPageData, SitemapUrlData
from .core.exceptions import SubtxtError, SitemapError, ProcessingError, RenderingError, WatcherError
from .orchestration import generate_structured_data_orchestrator
from .rendering import render_markdown

# Import stateful watcher logic
from .watcher import run_watch_loop

__all__ = [
    "generate_structured_data", # Async: returns structured data dict/object
    "render_markdown",         # Sync: renders structured data to markdown string
    "generate",                # Sync: runs generate_structured_data + render_markdown
    "watch",                   # Async: starts the stateful watcher loop

    # Models & Exceptions
    "StructuredData",
    "ProcessedPageData",
    "SitemapUrlData",
    "SubtxtError",
    "SitemapError",
    "ProcessingError",
    "RenderingError",
    "WatcherError",
]
__version__ = "0.1.0"

# Core SDK Functions

async def generate_structured_data(
    sitemap_url: str,
    *,
    include_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    replace_title: Optional[List[str]] = None,
    output_title: Optional[str] = None,
    output_description: Optional[str] = None,
    concurrency: int = 10,
    user_agent: Optional[str] = None,
) -> StructuredData:
    """
    Generates a structured data representation of a website from its sitemap.

    This is the primary async function for programmatic use.

    Args:
        sitemap_url: Homepage URL or direct sitemap.xml URL.
        include_paths: Glob patterns for URLs to include.
        exclude_paths: Glob patterns for URLs to exclude.
        replace_title: Sed-style commands for title substitution.
        output_title: Override the main documentation title.
        output_description: Override the main documentation description.
        concurrency: Number of concurrent page fetch requests.
        user_agent: Custom User-Agent string.

    Returns:
        A StructuredData object containing the site structure, page details,
        and potentially an error message.
    """
    ua = user_agent or f"PythonSubtxtSdk/{__version__}"
    return await generate_structured_data_orchestrator(
        sitemap_url=sitemap_url,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        replace_title=replace_title,
        output_title=output_title,
        output_description=output_description,
        concurrency=concurrency,
        user_agent=ua,
    )


# Convenience Sync Wrapper

def generate(
    url: str,
    *,
    include_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    replace_title: Optional[List[str]] = None,
    output_title: Optional[str] = None,
    output_description: Optional[str] = None,
    concurrency: int = 10,
    user_agent: Optional[str] = None,
) -> str:
    """
    Generates llms.txt Markdown content (synchronous wrapper).

    Fetches sitemap, processes pages, structures data, and renders Markdown.
    Convenient for simple scripts or CLI usage where blocking is acceptable.

    Args:
        url: Homepage URL or direct sitemap.xml URL.
        (See generate_structured_data for other args)

    Returns:
        The generated Markdown content as a string.
    """
    try:
        loop = asyncio.get_event_loop_policy().get_event_loop()
        if loop.is_running():
            print("Warning: Running generate() within an existing event loop.", file=sys.stderr)
            future = asyncio.ensure_future(generate_structured_data(url=url, include_paths=include_paths, exclude_paths=exclude_paths, replace_title=replace_title, output_title=output_title, output_description=output_description, concurrency=concurrency, user_agent=user_agent))
            while not future.done():
                 loop.run_until_complete(asyncio.sleep(0.01))
            structured_data = future.result()
        else:
             structured_data = loop.run_until_complete(
                 generate_structured_data(
                     sitemap_url=url,
                     include_paths=include_paths,
                     exclude_paths=exclude_paths,
                     replace_title=replace_title,
                     output_title=output_title,
                     output_description=output_description,
                     concurrency=concurrency,
                     user_agent=user_agent,
                 )
             )
    except RuntimeError as e:
         # Fallback for certain environments where get_event_loop fails in a running loop
         if "cannot run loop while another loop is running" in str(e):
              print("RuntimeError detecting running loop, trying asyncio.run().", file=sys.stderr)
              # This will raise its own RuntimeError if nested loops aren't allowed
              structured_data = asyncio.run(generate_structured_data(
                     sitemap_url=url,
                     include_paths=include_paths,
                     exclude_paths=exclude_paths,
                     replace_title=replace_title,
                     output_title=output_title,
                     output_description=output_description,
                     concurrency=concurrency,
                     user_agent=user_agent,
                 ))
         else:
              raise # Re-raise other RuntimeErrors
    except Exception as e:
        # Handle potential errors during async execution if needed
        print(f"Error running async generation: {e}", file=sys.stderr)
        return f"# Error\n\nGeneration failed: {e}"

    return render_markdown(structured_data)

# Stateful Watcher (CLI Entry)

async def watch(
    url: str,
    interval: int,
    output_file: str,
    *,
    include_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    replace_title: Optional[List[str]] = None,
    output_title: Optional[str] = None,
    output_description: Optional[str] = None,
    concurrency: int = 10,
    user_agent: Optional[str] = None,
    ) -> None:
    """
    Starts the continuous stateful watcher using the sitemap method.

    Manages state in a local file (<output_file>.state.json).
    Intended for CLI use; not suitable for serverless environments.

    Args:
        url: Homepage URL or direct sitemap.xml URL to watch.
        interval: Check interval in seconds.
        output_file: Path to the llms.txt file to update.
        (See generate_structured_data for other args)
    """
    ua = user_agent or f"PythonSubtxtSdk/{__version__} (Watcher)"
    # Prepare the config dict for the watcher loop
    generation_config = {
        "include_paths": include_paths,
        "exclude_paths": exclude_paths,
        "replace_title": replace_title,
        "output_title": output_title,
        "output_description": output_description,
        "concurrency": concurrency,
        "user_agent": ua,
    }
    await run_watch_loop(
        url=url,
        interval=interval,
        output_file=output_file,
        generation_config=generation_config,
    )