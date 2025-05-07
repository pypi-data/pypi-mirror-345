# subtxt/core/exceptions.py
"""Custom exception classes for the subtxt SDK."""

class SubtxtError(Exception):
    """Base class for subtxt exceptions."""
    pass

class SitemapError(SubtxtError):
    """Error related to fetching or parsing sitemaps."""
    pass

class ProcessingError(SubtxtError):
    """Error during page fetching or HTML processing."""
    pass

class RenderingError(SubtxtError):
    """Error during Markdown rendering."""
    pass

class WatcherError(SubtxtError):
    """Error specific to the watcher functionality."""
    pass