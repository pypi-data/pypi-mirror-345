# subtxt

The comprehensive tool for generating and maintaining `llms.txt` files for websites using sitemap data.

## What is subtxt?

subtxt automatically generates an `llms.txt` file for any website by processing its sitemap and creating a structured Markdown summary that includes:
- Page titles and URLs
- Optional page descriptions
- Logical categorization based on URL paths

Once generated, subtxt can continuously monitor the sitemap and update the `llms.txt` file as content changes, making it perfect for tracking website evolution over time.

## Installation

### From PyPI
```bash
pip install subtxt
```

### From source
```bash
# Clone the repository
git clone https://github.com/ananyakgarg/subtxt.git
cd subtxt

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Requirements
- Python 3.11 or higher
- Dependencies (automatically installed):
  - beautifulsoup4 >= 4.12
  - lxml >= 4.9
  - httpx >= 0.24
  - pathspec >= 0.11
  - ultimate-sitemap-parser >= 1.4
  - tqdm >= 4.60
  - fastapi >= 0.100
  - uvicorn[standard] >= 0.20
  - pydantic >= 2.0
  - sse-starlette >= 1.8.0

## Usage

subtxt offers two primary modes of operation:

### 1. Generate Command (One-time Generation)

Generate a snapshot `llms.txt` file for a website:

```bash
subtxt generate --url https://example.com --out llms.txt
```

### 2. Watch Command (Continuous Monitoring)

This is the main command for most use cases. It generates an initial `llms.txt` file and then continuously watches for changes:

```bash
subtxt watch --url https://example.com --interval 3600 --out llms.txt
```

The `watch` command maintains state between runs in a `.state.json` file, allowing it to efficiently detect changes and only update the `llms.txt` file when necessary.

## Configuration Options

### Common Options for Both Commands

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Target website URL or direct sitemap URL (required) | - |
| `-i`, `--include-path` | URL path pattern to include (can use multiple) | None |
| `-x`, `--exclude-path` | URL path pattern to exclude (can use multiple) | None |
| `-r`, `--replace-title` | Sed-style title substitution (can use multiple) | None |
| `-t`, `--title` | Override the main documentation title | Domain name |
| `-d`, `--description` | Override the main documentation description | Auto-generated |
| `-c`, `--concurrency` | Number of concurrent HTTP requests | 10 |
| `-ua`, `--user-agent` | Custom User-Agent for HTTP requests | Chrome-like user agent string |
| `--out` | Output file path | llms.txt |

### Additional Watch Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--interval` | Check interval in seconds | 21600 (6 hours) |

## Configuration File

subtxt supports configuration via `pyproject.toml` file, which allows you to set default options for all commands without having to specify them on the command line each time.

### Location

The configuration file should be named `pyproject.toml` and can be placed:
- In the current directory where you run subtxt
- In any parent directory (subtxt will search upwards)

### Format

Add a `[tool.subtxt]` section to your `pyproject.toml` file:

```toml
[tool.subtxt]
# Required URL can be set here instead of command line
url = "https://docs.example.com"
# Default output file path
output_file = "docs.txt"
# Number of concurrent HTTP requests
concurrency = 15
# Check interval for watch command (in seconds)
interval = 3600
# Custom user agent string
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
# Override main title
title = "API Documentation"
# Override description
description = "Generated documentation for Example API"
# Include paths (glob patterns)
include_paths = [
    "/api/*",
    "/guides/**"
]
# Exclude paths (glob patterns)
exclude_paths = [
    "/blog/*",
    "/news/*",
    "/deprecated/*"
]
# Title transformations (sed style)
replace_title = [
    "s/ - Example Company//g",
    "s/API Reference/API Docs/g"
]
```

### Priority

Command-line arguments always override configuration file settings. This allows you to:
1. Set common defaults in the config file
2. Override specific options when needed on the command line

### Example Usage with Config File

With the above configuration in `pyproject.toml`, you can simply run:

```bash
# No need to specify options that are in the config file
subtxt generate

# Override just the output file
subtxt generate --out custom-output.txt

# Watch command with config file defaults
subtxt watch
```

## Examples

### Basic Usage

```bash
# Generate from a website's sitemap
subtxt generate --url https://docs.example.com

# Generate with custom output file
subtxt generate --url https://docs.example.com --out custom_name.txt

# Generate using a direct sitemap URL
subtxt generate --url https://docs.example.com/sitemap.xml

# Continuously monitor a site, checking every hour
subtxt watch --url https://docs.example.com --interval 3600 --out docs_llms.txt
```

### Advanced Filtering

```bash
# Only include specific sections of a site
subtxt generate --url https://docs.example.com -i "/api/*" -i "/guides/*"

# Exclude certain paths
subtxt generate --url https://docs.example.com -x "/blog/*" -x "/deprecated/*"

# Combine includes and excludes
subtxt generate --url https://docs.example.com -i "/docs/*" -x "/docs/internal/*"
```

### Title Transformations

```bash
# Remove " - Company Name" from all page titles
subtxt generate --url https://docs.example.com -r "s/ - Company Name$//"

# Replace instances of "API" with "Application Programming Interface"
subtxt generate --url https://docs.example.com -r "s/API/Application Programming Interface/g"

# Multiple transformations can be chained
subtxt generate --url https://docs.example.com -r "s/API/REST API/g" -r "s/ - Docs$//"
```

### Customizing Output

```bash
# Set custom main title and description
subtxt generate --url https://docs.example.com -t "Developer Documentation" -d "Complete API reference and guides"

# Adjust concurrency for faster processing or to be more respectful
subtxt generate --url https://docs.example.com -c 5  # Lower concurrency
subtxt generate --url https://docs.example.com -c 20  # Higher concurrency

# Set a custom user-agent
subtxt generate --url https://docs.example.com -ua "MyCompany Docs Processor/1.0"
```

## API Integration Examples

### Next.js Integration

You can integrate subtxt with your Next.js application to generate and maintain documentation. Here are some examples:

#### 1. Generate Documentation (One-time)

```typescript
// app/api/generate-docs/route.ts
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const config = {
    url: "https://docs.example.com",
    include_paths: ["/api/*", "/guides/*"],
    exclude_paths: ["/deprecated/*"],
    replace_title: ["s/ - Company Name$//"],
    output_title: "API Documentation",
    concurrency: 10,
    user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
  }

  try {
    const response = await fetch('http://localhost:8000/generate_markdown', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    })

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const markdown = await response.text()
    
    return NextResponse.json({ markdown })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to generate documentation' },
      { status: 500 }
    )
  }
}
```

#### 2. Watch Documentation (Continuous Updates)

```typescript
// app/api/watch-docs/route.ts
import { NextResponse } from 'next/server'

// Start watching a documentation site and get SSE updates
export async function POST(request: Request) {
  const config = {
    url: "https://docs.example.com",
    identifier: "example-docs-watch",
    interval_seconds: 3600,
    include_paths: ["/api/*"],
    user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
  }

  try {
    // This will start the watcher and establish SSE connection
    const response = await fetch('http://localhost:8000/watch/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    })

    // Forward the SSE response to the client
    const { readable, writable } = new TransformStream()
    response.body?.pipeTo(writable)
    
    return new Response(readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to start documentation watch' },
      { status: 500 }
    )
  }
}

// Get latest documentation content
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const identifier = searchParams.get('identifier')

  if (!identifier) {
    return NextResponse.json(
      { error: 'Identifier is required' },
      { status: 400 }
    )
  }

  try {
    const response = await fetch(
      `http://localhost:8000/watch/output/${identifier}`,
      { method: 'GET' }
    )

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const markdown = await response.text()
    
    return NextResponse.json({ markdown })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch documentation' },
      { status: 500 }
    )
  }
}
```

#### 3. React Component Usage

```typescript
// components/Documentation.tsx
'use client'

import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

export default function Documentation({ identifier }: { identifier: string }) {
  const [markdown, setMarkdown] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    let eventSource: EventSource | null = null

    const startWatchAndListen = async () => {
      try {
        // Start the watcher and get SSE updates
        eventSource = new EventSource(`/api/watch-docs?identifier=${identifier}`)

        // Initial content fetch
        const response = await fetch(`/api/watch-docs?identifier=${identifier}`)
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        const data = await response.json()
        setMarkdown(data.markdown)

        // Listen for updates
        eventSource.onmessage = async () => {
          const response = await fetch(`/api/watch-docs?identifier=${identifier}`)
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
          const data = await response.json()
          setMarkdown(data.markdown)
        }

        eventSource.onerror = (error) => {
          console.error('SSE Error:', error)
          eventSource?.close()
          // Try to reconnect after 5 seconds
          setTimeout(startWatchAndListen, 5000)
        }
      } catch (error) {
        setError('Failed to start documentation watch')
        // Try to reconnect after 5 seconds
        setTimeout(startWatchAndListen, 5000)
      }
    }

    startWatchAndListen()

    return () => {
      if (eventSource) {
        eventSource.close()
      }
    }
  }, [identifier])

  if (error) return <div>Error: {error}</div>
  if (!markdown) return <div>Loading...</div>

  return <ReactMarkdown>{markdown}</ReactMarkdown>
}
```

#### 4. Page Implementation

```typescript
// app/docs/page.tsx
import Documentation from '@/components/Documentation'

export default function DocsPage() {
  return (
    <main className="container mx-auto p-4">
      <h1>Documentation</h1>
      <Documentation identifier="example-docs-watch" />
    </main>
  )
}
```

The above examples demonstrate:
- Setting up API routes to interact with the subtxt server
- Starting a documentation watch process
- Fetching and displaying documentation updates
- Using the Chrome-like user agent for better compatibility
- Error handling and loading states

Remember to:
1. Start the subtxt API server before making requests
2. Handle rate limiting and error cases appropriately
3. Consider caching documentation content to reduce server load
4. Use environment variables for configuration in production

## Output Format

The generated `llms.txt` file follows this format:

```markdown
# Documentation

> Generated documentation from sitemap

## Api reference

- [Chat Completions - Perplexity](https://docs.perplexity.ai/api-reference/chat-completions): Generates a model's response for the given chat conversation.

## Guides

- [API Group - Perplexity](https://docs.perplexity.ai/guides/api-organization): Learn how to use the Perplexity API Portal to manage access, usage, billing, and team collaboration.
- [Image Guide - Perplexity](https://docs.perplexity.ai/guides/image-guide): Learn how to use Sonar's image upload feature.
```

The output is organized by sections derived from the first path segment of each URL, with each page listing:
- Page title (as clickable link)
- Optional page description (if available from meta tags)

## How subtxt Works

### Technical Overview

subtxt operates through a pipeline process of sitemap retrieval, page processing, and Markdown generation:

1. **Sitemap Processing**:
   - Uses ultimate-sitemap-parser to discover and parse XML sitemaps
   - Supports both sitemap index files and direct sitemap URLs
   - Handles compressed (gzip) sitemaps automatically
   - Extracts all page URLs and last modification dates

2. **Concurrent Page Processing**:
   - Uses async HTTP requests via httpx for efficient page fetching
   - Processes multiple pages concurrently (default: 10, configurable)
   - Extracts titles from HTML `<title>` tags and meta tags
   - Extracts descriptions from meta description tags
   - Applies path filtering using pathspec (git-style patterns)
   - Performs title transformations using regex substitutions

3. **Section Organization**:
   - Groups pages by their first URL path segment
   - Automatically capitalizes and formats section names
   - Sorts sections and pages alphabetically
   - Handles special cases like language codes in paths

4. **Watch Mode Operation** (via API Server):
   - Runs as a FastAPI server with Server-Sent Events (SSE)
   - Performs initial generation from the sitemap
   - Stores state information in a local `.state.json` file
   - Periodically re-checks the sitemap at the specified interval
   - Uses last modification dates to detect changes
   - Updates the output file only when changes are detected
   - Provides real-time updates via SSE endpoint
   - Supports multiple watchers with different configurations

5. **Output Generation**:
   - Generates consistent, well-formatted Markdown
   - Maintains proper heading hierarchy
   - Includes clickable links with optional descriptions
   - Supports custom title and description overrides
   - Handles special characters and escaping

6. **Error Handling**:
   - Retries failed HTTP requests with exponential backoff
   - Validates sitemap and HTML content
   - Provides detailed error messages
   - Continues processing on per-page failures
   - Logs issues without stopping the entire process

## Website Access Notes

subtxt uses a Chrome-like user agent by default to improve compatibility with websites that may restrict bot access. While this works for most websites, some services (like OpenAI's documentation) may still return 403 Forbidden errors. In such cases, you may need to:

1. Use a different user agent string
2. Ensure you have proper authorization if required
3. Consider using the sitemap URL directly if available

## Data Types and Output Options

subtxt supports two main types of output:

### 1. Structured Data (JSON)

You can generate structured JSON data representing all the site's pages, their titles, descriptions, and categorization. This is useful for integrating with other systems or for creating custom renderers.

### 2. Markdown Format (llms.txt)

The default output is a Markdown file formatted according to common conventions for documentation sites, with sections and nicely formatted links.

## Troubleshooting

### Common Issues

1. **Sitemap not found**: Make sure the site has a sitemap.xml file or provide a direct URL
2. **Connection errors**: Check your internet connection and try again
3. **Empty output**: The site might not have a proper sitemap or use custom sitemap URLs
4. **Memory issues**: Lower the concurrency value with `-c` for large sitemaps

### Best Practices

- Start with default settings when testing a new site
- Use more targeted includes/excludes for large sites
- Be respectful of website resources by using reasonable concurrency values
- Set appropriate check intervals in watch mode (hourly, daily, etc.)

## Using as a Library

subtxt can also be imported and used programmatically:

```python
import asyncio
from subtxt import generate, watch, generate_structured_data, render_markdown

# Simple approach: Generate llms.txt content synchronously
content = generate(
    url="https://example.com",
    include_paths=["/docs/*"],
    exclude_paths=["/docs/internal/*"],
    replace_title=["s/ - Example//g"],
    output_title="API Documentation",
    concurrency=10
)

# Save to file
with open("llms.txt", "w") as f:
    f.write(content)

# Advanced approach: Get structured data and customize rendering
async def get_structured_data():
    data = await generate_structured_data(
        sitemap_url="https://example.com",
        include_paths=["/docs/*"],
        exclude_paths=["/docs/internal/*"],
    )
    
    # Use the structured data
    print(f"Found {len(data.pages)} pages across {len(data.sections)} sections")
    
    # Custom rendering or use the built-in renderer
    markdown = render_markdown(data)
    return markdown

# Watch a site using the built-in watcher
async def run_watcher():
    await watch(
        url="https://example.com",
        interval=3600,
        output_file="llms.txt",
        include_paths=["/docs/*"]
    )

# Run the watcher
asyncio.run(run_watcher())
```

## License

MIT
