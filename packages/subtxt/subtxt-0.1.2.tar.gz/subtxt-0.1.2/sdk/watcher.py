# subtxt/watcher.py
"""Stateful watcher logic for the CLI."""

import asyncio
import time
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from .core.models import StructuredData
from .core.exceptions import WatcherError
from . import generate_structured_data_orchestrator
from .rendering import render_markdown

from datetime import datetime
from .rendering import RenderingError

STATE_FILE_SUFFIX = ".state.json"

def _load_previous_state(state_file_path: Path) -> Optional[Dict[str, Any]]:
    """Loads the last known state from the state file."""
    if not state_file_path.exists():
        return None
    try:
        with open(state_file_path, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        # Validate basic structure
        if isinstance(state_data, dict) and "pages" in state_data and "source_url" in state_data:
            print(f"Loaded previous state ({len(state_data.get('pages',[]))} pages) from {state_file_path}", file=sys.stderr)
            return state_data
        else:
            print(f"Warning: Invalid state file format found: {state_file_path}", file=sys.stderr)
            # Optionally delete or rename the bad state file here
            return None
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from state file: {state_file_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Could not read state file {state_file_path}: {e}", file=sys.stderr)
        return None


def _save_current_state(state_file_path: Path, current_data: StructuredData):
    """Saves the relevant parts of the current structured data as the new state."""
    try:
        # Store only essential data for comparison to keep state file smaller
        state_to_save = {
            "source_url": current_data.source_url,
            "generation_timestamp": current_data.generation_timestamp,
            # Convert ProcessedPageData objects to dictionaries for JSON serialization
            "pages": [page.__dict__ for page in current_data.pages]
        }
        state_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file_path, 'w', encoding='utf-8') as f:
            json.dump(state_to_save, f, indent=2)
        print(f"Saved current state ({len(current_data.pages)} pages) to {state_file_path}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error saving state file {state_file_path}: {e}", file=sys.stderr)
        raise WatcherError(f"Failed to save state: {e}") from e



def _compare_state(prev_state: Optional[Dict[str, Any]], current_data: StructuredData) -> Tuple[bool, str]:
    """
    Compares the current structured data with the previous state dict.
    Performs strict comparison on titles and descriptions for existing URLs.

    Returns:
        (bool: changes_detected, str: change_summary).
    """
    change_summary = "No significant changes detected."
    changes_detected = False # Default to no changes

    if current_data.error:
        if prev_state is None or prev_state.get("error") != current_data.error:
            change_summary = f"Error state changed or occurred: {current_data.error}"
            return True, change_summary
        else:
             change_summary = "Error state remains unchanged."
             return False, change_summary

    if prev_state is None:
        change_summary = "First run or no previous state found."
        return True, change_summary

    if prev_state.get("error"):
        change_summary = "Previous run had an error, generating fresh data."
        return True, change_summary

    # Compare the 'pages' list
    prev_pages_list = prev_state.get("pages", [])
    current_pages_list = [p.__dict__ for p in current_data.pages] # Convert current objects to dicts

    prev_pages_dict = {p['url']: p for p in prev_pages_list if 'url' in p}
    current_pages_dict = {p['url']: p for p in current_pages_list if 'url' in p}

    prev_urls = set(prev_pages_dict.keys())
    current_urls = set(current_pages_dict.keys())

    added_urls = current_urls - prev_urls
    removed_urls = prev_urls - current_urls

    if added_urls:
        change_summary = f"Detected {len(added_urls)} added URLs."
        changes_detected = True

    if removed_urls and not changes_detected: # Only report removals if no additions yet
        change_summary = f"Detected {len(removed_urls)} removed URLs."
        changes_detected = True

    # If URLs were added or removed, we already know there's a change.
    if changes_detected:
        return True, change_summary

    modified_count = 0
    modified_examples = [] # Keep track of a few examples
    for url in prev_urls.intersection(current_urls):
        prev_page = prev_pages_dict[url]
        current_page = current_pages_dict[url]
        page_modified = False

        # 1. Compare lastmod if available (optional first check)
        prev_lastmod = prev_page.get('sitemap_lastmod')
        current_lastmod = current_page.get('sitemap_lastmod')
        if prev_lastmod and current_lastmod and prev_lastmod != current_lastmod:
            # print(f"  Debug: lastmod changed for {url}", file=sys.stderr) # Optional debug
            page_modified = True

        # 2. Compare title (strict)
        if not page_modified and prev_page.get('title') != current_page.get('title'):
            # print(f"  Debug: title changed for {url}", file=sys.stderr) # Optional debug
            page_modified = True

        # 3. Compare description (strict) - Handle None vs empty string as same? For now, strict compare.
        # Treat None and empty string as potentially different states if needed.
        if not page_modified and prev_page.get('description') != current_page.get('description'):
             # print(f"  Debug: description changed for {url}", file=sys.stderr) # Optional debug
             page_modified = True

        if page_modified:
            modified_count += 1
            if len(modified_examples) < 3: # Log first few examples
                modified_examples.append(url)


    if modified_count > 0:
        change_summary = f"Detected content changes in {modified_count} existing page(s)."
        if modified_examples:
             change_summary += f" Examples: {', '.join(modified_examples)}{'...' if modified_count > 3 else ''}"
        changes_detected = True

    # Return final decision
    return changes_detected, change_summary


async def run_watch_loop(
    url: str,
    interval: int,
    output_file: str,
    generation_config: Dict[str, Any] # Pass other args like includes, excludes etc. here
) -> None:
    """The core async loop for the stateful watcher."""
    output_path = Path(output_file)
    state_file_path = output_path.with_suffix(STATE_FILE_SUFFIX)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Watcher starting...", file=sys.stderr)
    print(f"Watching: {url}", file=sys.stderr)
    print(f"Outputting to: {output_path}", file=sys.stderr)
    print(f"State file: {state_file_path}", file=sys.stderr)
    print(f"Check interval: {interval}s", file=sys.stderr)

    while True:
        start_time = time.monotonic()
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Watcher: Checking for updates...", file=sys.stderr)

        previous_state = _load_previous_state(state_file_path)
        current_structured_data: Optional[StructuredData] = None
        error_occurred = False

        try:
            # Call the core orchestrator function to get structured data
            current_structured_data = await generate_structured_data_orchestrator(
                sitemap_url=url, **generation_config
            )
            if current_structured_data.error:
                 print(f"Warning: Generation failed: {current_structured_data.error}", file=sys.stderr)
                 # Proceed to comparison to see if error state changed

        except Exception as e:
            print(f"❌ Watcher: Unhandled exception during generation: {e}", file=sys.stderr)
            error_occurred = True
            # Create a dummy structure to indicate error for state comparison/saving
            current_structured_data = StructuredData(source_url=url, main_title="Error", main_description="Generation failed", error=str(e))

        if current_structured_data is None:
            # Should ideally not happen if exceptions create error structure
             print("❌ Watcher: Failed to get current data structure. Skipping cycle.", file=sys.stderr)
             error_occurred = True

        if not error_occurred and current_structured_data:
            changes_detected, change_summary = _compare_state(previous_state, current_structured_data)
            print(f"Watcher: {change_summary}", file=sys.stderr)

            if changes_detected:
                try:
                    print(f"Watcher: Rendering and writing update to {output_path}...", file=sys.stderr)
                    current_markdown = render_markdown(current_structured_data)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(current_markdown, encoding='utf-8')
                    print(f"✅ Watcher: Successfully updated {output_path}", file=sys.stderr)
                    _save_current_state(state_file_path, current_structured_data)
                except (IOError, WatcherError, RenderingError) as e: # Catch specific errors
                    print(f"❌ Watcher: Error writing output or saving state: {e}", file=sys.stderr)
                    # Avoid saving state if write failed
                except Exception as e:
                     print(f"❌ Watcher: Unexpected error during file write/state save: {e}", file=sys.stderr)
                     # Avoid saving state if write failed

        elif current_structured_data: # Handle case where error occurred during generation
             changes_detected, change_summary = _compare_state(previous_state, current_structured_data)
             print(f"Watcher: {change_summary}", file=sys.stderr)
             if changes_detected: # If error state is new or different
                 print("Watcher: Saving new error state.", file=sys.stderr)
                 try:
                     _save_current_state(state_file_path, current_structured_data)
                 except WatcherError as e:
                     print(f"❌ Watcher: Error saving error state: {e}", file=sys.stderr)


        # --- Sleep logic ---
        elapsed_time = time.monotonic() - start_time
        sleep_duration = max(1, interval - elapsed_time) # Ensure at least 1s sleep
        print(f"Watcher: Check finished in {elapsed_time:.2f}s. Sleeping for {sleep_duration:.2f}s...", file=sys.stderr)
        try:
             await asyncio.sleep(sleep_duration)
        except asyncio.CancelledError:
             print("\nWatcher loop cancelled.", file=sys.stderr)
             break
