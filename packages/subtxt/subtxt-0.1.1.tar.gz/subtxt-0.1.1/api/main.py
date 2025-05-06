# /api/main.py
import sys
import os
from fastapi import FastAPI, HTTPException, Body, Query, status
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from .request_models import WatchStartRequest, WatchActionRequest, GenerateConfigRequest
from .response_models import WatchStartResponse, WatchStatusResponse, ListWatchersResponse, StructuredDataResponse, WatchUpdateEvent
from . import watcher_service
from sse_starlette.sse import EventSourceResponse
from datetime import datetime
import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import sdk
    from sdk import SubtxtError
    from sdk.core.models import StructuredData
except ImportError as e:
    print(f"API Error: Failed to import subtxt SDK from '{project_root}': {e}", file=sys.stderr)
    print("Ensure the subtxt package is installed correctly (e.g., pip install -e .)", file=sys.stderr)
    sys.exit(1)
except Exception as e:
     print(f"API Error: Unexpected error during SDK import: {e}", file=sys.stderr)
     sys.exit(1)

app = FastAPI(
    title="Subtxt Generation API",
    description="Generates structured website data (`llms.txt` format) from sitemaps.",
    version=getattr(sdk, '__version__', '0.1.1'),
)

# Add CORS middleware to allow SSE connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(
    "/generate_structured",
    response_model=StructuredDataResponse,
    summary="Generate Structured Data (JSON)"
)
async def generate_structured_endpoint(config: GenerateConfigRequest = Body(...)):
    """Generates structured website data suitable for machine processing."""
    print(f"API: Received structured request for {config.url}")
    try:
        sdk_result: StructuredData = await sdk.generate_structured_data(
            sitemap_url=config.url,
            include_paths=config.include_paths,
            exclude_paths=config.exclude_paths,
            replace_title=config.replace_title,
            output_title=config.output_title,
            output_description=config.output_description,
            concurrency=config.concurrency,
            user_agent=config.user_agent,
        )

        response_dict = {
            "source_url": sdk_result.source_url,
            "main_title": sdk_result.main_title,
            "main_description": sdk_result.main_description,
            "generation_timestamp": sdk_result.generation_timestamp,
            "sections": {name: [page.__dict__ for page in pages] for name, pages in sdk_result.sections.items()},
            "pages": [page.__dict__ for page in sdk_result.pages],
            "error": sdk_result.error
        }

        if sdk_result.error:
            print(f"API: Generation failed for {config.url}: {sdk_result.error}")
        else:
            print(f"API: Successfully generated structured data for {config.url}")

        return StructuredDataResponse(**response_dict)

    except SubtxtError as e:
        print(f"API: SDK Error for {config.url}: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"SDK Error: {e}")
    except Exception as e:
        print(f"API: Unexpected Error for {config.url}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@app.post(
    "/generate_markdown",
    response_class=PlainTextResponse,
    summary="Generate llms.txt Markdown"
)
async def generate_markdown_endpoint(config: GenerateConfigRequest = Body(...)):
    """Generates llms.txt Markdown content."""
    print(f"API: Received markdown request for {config.url}")
    try:
        structured_data: StructuredData = await sdk.generate_structured_data(
            sitemap_url=config.url,
            include_paths=config.include_paths,
            exclude_paths=config.exclude_paths,
            replace_title=config.replace_title,
            output_title=config.output_title,
            output_description=config.output_description,
            concurrency=config.concurrency,
            user_agent=config.user_agent,
        )
        markdown_output = sdk.render_markdown(structured_data)
        print(f"API: Successfully generated markdown for {config.url}")
        return PlainTextResponse(content=markdown_output)

    except SubtxtError as e:
         print(f"API: SDK Error generating markdown for {config.url}: {e}")
         error_markdown = f"# Error\n\nSDK Error: {e}"
         return PlainTextResponse(content=error_markdown, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        print(f"API: Unexpected Error generating markdown for {config.url}: {e}")
        error_markdown = f"# Error\n\nInternal Server Error."
        return PlainTextResponse(content=error_markdown, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/watch/start", status_code=status.HTTP_202_ACCEPTED, response_model=WatchStartResponse)
async def start_watch_endpoint(request: WatchStartRequest = Body(...)):
    """Starts a background subprocess to watch a URL and sets up SSE."""
    try:
        # Pass relevant config details to the service function
        start_config = request.model_dump()
        pid = watcher_service.start_watcher_process(request.identifier, start_config)

        if pid is None: # Indicates already running
             raise HTTPException(status.HTTP_409_CONFLICT, f"Watcher already running for identifier: {request.identifier}")
        elif pid == -1: # Indicates failure to start
             raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to start watcher process for identifier: {request.identifier}")
        else:
            # Set up event stream for this identifier
            async def event_stream():
                last_check = None
                while True:
                    try:
                        output_file = watcher_service.get_output_file_path(request.identifier)
                        if not os.path.exists(output_file):
                            await asyncio.sleep(1)
                            continue

                        current_mtime = os.path.getmtime(output_file)
                        if last_check is None or current_mtime > last_check:
                            last_check = current_mtime
                            event = WatchUpdateEvent(
                                identifier=request.identifier,
                                timestamp=datetime.fromtimestamp(current_mtime).isoformat()
                            )
                            yield {
                                "event": "update",
                                "data": event.model_dump_json()
                            }
                        
                        await asyncio.sleep(1)

                    except Exception as e:
                        print(f"SSE Error for {request.identifier}: {e}")
                        error_event = WatchUpdateEvent(
                            event="error",
                            identifier=request.identifier,
                            timestamp=datetime.now().isoformat(),
                            error=str(e)
                        )
                        yield {
                            "event": "error",
                            "data": error_event.model_dump_json()
                        }
                        await asyncio.sleep(5)

            return EventSourceResponse(
                event_stream(),
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )

    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"API Error: Unexpected error in /watch/start: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error starting watcher.")

@app.post("/watch/stop", response_model=WatchStatusResponse)
async def stop_watch_endpoint(request: WatchActionRequest = Body(...)):
    """Stops a running background watcher subprocess."""
    try:
        status_msg, pid = watcher_service.stop_watcher_process(request.identifier)
        if status_msg == "not_found":
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No watcher found for identifier: {request.identifier}")
        return WatchStatusResponse(identifier=request.identifier, status=status_msg, pid=pid)
    except ValueError as e: # Invalid identifier
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"API Error: Unexpected error in /watch/stop: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error stopping watcher.")

@app.get("/watch/status", response_model=ListWatchersResponse)
async def list_watchers_endpoint():
    """Lists currently managed running watcher processes."""
    try:
        watchers = watcher_service.list_running_watchers()
        return ListWatchersResponse(watchers=watchers)
    except Exception as e:
        print(f"API Error: Unexpected error in /watch/status: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error listing watchers.")

@app.get("/watch/output/{identifier}", response_class=PlainTextResponse)
async def get_watch_output_endpoint(identifier: str):
    """Retrieves the latest generated llms.txt for a watched identifier."""
    try:
        markdown_content = watcher_service.load_watcher_output(identifier)
        if markdown_content is None:
             # Could be not found or error reading
             raise HTTPException(status.HTTP_404_NOT_FOUND, f"Output not found for identifier: {identifier}. Watcher might not have run successfully yet or identifier is invalid.")
        return PlainTextResponse(content=markdown_content)
    except ValueError as e: # Invalid identifier
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"API Error: Unexpected error in /watch/output: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error retrieving output.")

@app.get("/watch/events/{identifier}")
async def watch_events_endpoint(identifier: str):
    """SSE endpoint for real-time llms.txt updates."""
    try:
        # Initial check
        if not watcher_service.is_valid_identifier(identifier):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid identifier")

        async def event_generator():
            last_check = None
            while True:
                try:
                    output_file = watcher_service.get_output_file_path(identifier)
                    if not os.path.exists(output_file):
                        # File doesn't exist yet, wait and continue
                        await asyncio.sleep(1)
                        continue

                    current_mtime = os.path.getmtime(output_file)
                    if last_check is None or current_mtime > last_check:
                        # File is new or has been modified
                        last_check = current_mtime
                        event = WatchUpdateEvent(
                            identifier=identifier,
                            timestamp=datetime.fromtimestamp(current_mtime).isoformat()
                        )
                        yield {
                            "event": "update",
                            "data": event.model_dump_json()
                        }
                    
                    # Check every second
                    await asyncio.sleep(1)

                except Exception as e:
                    print(f"SSE Error for {identifier}: {e}")
                    error_event = WatchUpdateEvent(
                        event="error",
                        identifier=identifier,
                        timestamp=datetime.now().isoformat(),
                        error=str(e)
                    )
                    yield {
                        "event": "error",
                        "data": error_event.model_dump_json()
                    }
                    # On error, wait a bit longer before retrying
                    await asyncio.sleep(5)

        return EventSourceResponse(event_generator())

    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"SSE Setup Error: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error setting up event stream")

@app.get("/", include_in_schema=False)
async def read_root():
    return {"message": "Subtxt API is running", "version": getattr(sdk, '__version__', 'unknown')}

if __name__ == "__main__":
    import uvicorn
    print("Starting Subtxt API server on http://localhost:8000 ...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, app_dir=os.path.dirname(__file__))