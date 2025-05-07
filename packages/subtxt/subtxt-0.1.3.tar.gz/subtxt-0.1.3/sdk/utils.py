"""Utility functions for string manipulation, parsing, etc."""

import re
from urllib.parse import urlparse, ParseResult
from typing import Tuple, Optional, List, Dict, Any
import sys
import pathspec

def capitalize_string(s: str) -> str:
    """Capitalizes the first letter of a string, leaves rest as is."""
    if not s:
        return ''
    return s[0].upper() + s[1:]

def clean_title(title: Optional[str]) -> str:
    """Removes leading '|', other unwanted chars, and excessive whitespace."""
    if not title:
        return ''
    cleaned = re.sub(r'^\s*\|?\s*|\s*\|?\s*$', '', title).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def parse_substitution_command(command: str) -> Tuple[re.Pattern, str]:
    """Parses a sed-style substitution command s/pattern/replacement/flags."""
    match = re.match(r'^s/(.+?)/(.*?)/([gimsuy]*)$', command)
    if match:
        pattern_str, replacement, flags_str = match.groups()
        flags = 0
        if 'i' in flags_str: flags |= re.IGNORECASE
        if 'm' in flags_str: flags |= re.MULTILINE
        if 's' in flags_str: flags |= re.DOTALL
        try:
            pattern_str = pattern_str.replace('\\/', '/')
            replacement = replacement.replace('\\/', '/')
            pattern = re.compile(pattern_str, flags)
            return pattern, replacement
        except re.error as e:
            raise ValueError(f"Invalid regex pattern in command '{command}': {e}")
    else:
        raise ValueError(f"Invalid substitution command format: '{command}'. Expected s/pattern/replacement/flags")

def substitute_title(title: Optional[str], commands: List[str]) -> Optional[str]:
    """Applies a list of substitution commands to a title."""
    if not title or not commands:
        return title
    current_title = title
    for command in commands:
        if command and command.startswith('s/'):
            try:
                pattern, replacement = parse_substitution_command(command)
                current_title = pattern.sub(replacement, current_title)
            except ValueError as e:
                print(f"Warning: Skipping invalid substitution command: {e}", file=sys.stderr)
                continue
    return current_title

def parse_section(uri: str) -> str:
    """Extracts the first path segment as the section, or 'ROOT'."""
    try:
        parsed_url: ParseResult = urlparse(uri)
        segments = [segment for segment in parsed_url.path.split('/') if segment]
        return segments[0] if segments else 'ROOT'
    except Exception:
        return 'ROOT'

def filter_urls(
    urls_data: List[Dict[str, Any]], # Expects list of dicts like {'url': ..., 'lastmod': ...}
    include_paths: Optional[List[str]],
    exclude_paths: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
    """
    Filters a list of URL data dictionaries based on include/exclude pathspecs.

    Args:
        urls_data: List of dictionaries, each must contain at least 'url'.
        include_paths: List of glob patterns to include.
        exclude_paths: List of glob patterns to exclude.

    Returns:
        A filtered list of the input dictionaries.
    """
    if not include_paths and not exclude_paths:
        return urls_data # No filtering needed

    spec_include = pathspec.PathSpec.from_lines('gitwildmatch', include_paths) if include_paths else None
    spec_exclude = pathspec.PathSpec.from_lines('gitwildmatch', exclude_paths) if exclude_paths else None

    filtered_list = []
    skipped_count = 0
    for item in urls_data:
        url = item.get('url')
        if not url:
            skipped_count += 1
            continue # Skip items without a URL

        try:
            parsed = urlparse(url)
            url_match_path = parsed.path if parsed.path and parsed.path.startswith('/') else '/' + (parsed.path or '')
            if not url_match_path or url_match_path == '/': url_match_path = '/'
            if parsed.query: url_match_path += "?" + parsed.query

            # Apply Exclude Rules first
            if spec_exclude and spec_exclude.match_file(url_match_path):
                skipped_count += 1
                continue
            # Apply Include Rules (if any are defined)
            if spec_include and not spec_include.match_file(url_match_path):
                 skipped_count += 1
                 continue

            filtered_list.append(item) # Keep the original dict

        except Exception as e:
             print(f"Warning: Could not parse URL '{url}' for filtering, skipping. Error: {e}", file=sys.stderr)
             skipped_count += 1
             continue

    if skipped_count > 0:
         print(f"Filtered out {skipped_count} URLs based on include/exclude rules.", file=sys.stderr)
    print(f"Proceeding with {len(filtered_list)} URLs after filtering.", file=sys.stderr)
    return filtered_list
