"""Functions for rendering structured data into Markdown."""

import sys
from .core.models import StructuredData
from .core.exceptions import RenderingError

def render_markdown(structured_data: StructuredData) -> str:
    """
    Renders the StructuredData object into llms.txt Markdown format.

    Args:
        structured_data: The StructuredData object to render.

    Returns:
        The Markdown string.

    Raises:
        RenderingError: If the input data is invalid.
    """
    if structured_data.error:
        print(f"Rendering error state: {structured_data.error}", file=sys.stderr)
        return f"# Error\n\n{structured_data.error}"
    if not structured_data.main_title:
        raise RenderingError("Invalid structured data provided for rendering: Missing main title.")

    print(f"Rendering Markdown from structured data...", file=sys.stderr)
    output_lines = []
    output_lines.append(f"# {structured_data.main_title}")
    output_lines.append("")
    output_lines.append(f"> {structured_data.main_description}")
    output_lines.append("")

    sections = structured_data.sections
    for section_name in sections:
        output_lines.append(f"## {section_name}")
        output_lines.append("")
        for item in sections[section_name]:
            desc_part = f": {item.description}" if item.description else ""
            # Basic Markdown escaping for title
            safe_title = item.title.replace('[', '\\[').replace(']', '\\]')
            output_lines.append(f"- [{safe_title}]({item.url}){desc_part}")
        output_lines.append("") # Add newline after each section's list

    return "\n".join(output_lines)