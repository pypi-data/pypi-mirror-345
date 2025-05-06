# /api/watcher_service.py
import sys
import os
import subprocess
import json
import atexit
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

WATCHER_PROCESSES: Dict[str, subprocess.Popen] = {}
RUN_WATCH_SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "run_watch.py"
STORAGE_BASE_DIR = Path(os.environ.get("SUBTXT_STORAGE_PATH", "./api_output")).resolve()
OUTPUT_FILE_SUFFIX = ".llms.txt" # Define here

STORAGE_BASE_DIR.mkdir(parents=True, exist_ok=True)

def _get_output_path(identifier: str) -> Path:
    """Gets the full path to the output file."""
    if not identifier or any(c in '/\\.' for c in identifier):
         raise ValueError(f"Invalid identifier for file path: '{identifier}'")
    return (STORAGE_BASE_DIR / identifier).with_suffix(OUTPUT_FILE_SUFFIX)

def start_watcher_process(identifier: str, config: Dict[str, Any]) -> Optional[int]:
    """Starts a watcher subprocess if not already running."""
    if identifier in WATCHER_PROCESSES and WATCHER_PROCESSES[identifier].poll() is None:
        print(f"Watcher Service: Process for '{identifier}' already running (PID: {WATCHER_PROCESSES[identifier].pid}).")
        return None # Indicate already running

    python_executable = sys.executable or "python"
    output_file_path = _get_output_path(identifier)
    cmd = [
        python_executable, str(RUN_WATCH_SCRIPT_PATH),
        "--url", config['url'],
        "--interval", str(config['interval_seconds']),
        "--output-file", str(output_file_path),
        "--concurrency", str(config.get('concurrency', 10))
    ]
    # Add optional list/string args carefully
    if config.get('include_paths'): cmd.extend(["--include-paths", json.dumps(config['include_paths'])])
    if config.get('exclude_paths'): cmd.extend(["--exclude-paths", json.dumps(config['exclude_paths'])])
    if config.get('replace_title'): cmd.extend(["--replace-title", json.dumps(config['replace_title'])])
    if config.get('output_title'): cmd.extend(["--output-title", config['output_title']])
    if config.get('output_description'): cmd.extend(["--output-description", config['output_description']])
    if config.get('user_agent'): cmd.extend(["--user-agent", config['user_agent']])

    try:
        process = subprocess.Popen(cmd, stdout=sys.stderr, stderr=sys.stderr)
        WATCHER_PROCESSES[identifier] = process
        print(f"Watcher Service: Started process for '{identifier}' (PID: {process.pid})")
        return process.pid
    except Exception as e:
        print(f"Watcher Service Error: Failed to start process for '{identifier}': {e}")
        return -1 # Indicate failure

def stop_watcher_process(identifier: str) -> Tuple[str, Optional[int]]:
    """Stops a watcher subprocess. Returns status and PID."""
    process = WATCHER_PROCESSES.get(identifier)
    pid = None
    if process:
        pid = process.pid
        if process.poll() is None: # Still running
            print(f"Watcher Service: Terminating process for '{identifier}' (PID: {pid})...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Watcher Service: Force killing process '{identifier}' (PID: {pid})...")
                process.kill()
                try: process.wait(timeout=1)
                except Exception: pass
            except Exception as e:
                 print(f"Watcher Service Error: During termination of {pid}: {e}")
            finally:
                 if identifier in WATCHER_PROCESSES: del WATCHER_PROCESSES[identifier]
            return "stopped", pid
        else: # Existed but already stopped
            if identifier in WATCHER_PROCESSES: del WATCHER_PROCESSES[identifier]
            return "stopped", pid
    return "not_found", None

def get_watcher_status(identifier: str) -> Tuple[str, Optional[int]]:
    """Checks the status of a watcher subprocess."""
    process = WATCHER_PROCESSES.get(identifier)
    if process:
        if process.poll() is None:
            return "running", process.pid
        else: # Process finished, remove from tracking
            if identifier in WATCHER_PROCESSES: del WATCHER_PROCESSES[identifier]
            return "stopped", process.pid
    return "not_found", None

def list_running_watchers() -> List[Dict[str, Any]]:
    """Lists identifiers and PIDs of currently running watchers."""
    running = []
    for identifier, process in list(WATCHER_PROCESSES.items()):
        if process.poll() is None:
            running.append({"identifier": identifier, "pid": process.pid, "status": "running"})
        else: # Clean up stopped processes from dict
             if identifier in WATCHER_PROCESSES: del WATCHER_PROCESSES[identifier]
    return running

def load_watcher_output(identifier: str) -> Optional[str]:
    """Loads the content of the output file for a given identifier."""
    try:
        output_path = _get_output_path(identifier)
        if output_path.is_file():
            return output_path.read_text(encoding='utf-8')
        else:
            return None # Not generated yet or identifier invalid
    except ValueError: # Invalid identifier
        return None
    except Exception as e:
        print(f"Watcher Service Error: reading output for '{identifier}': {e}")
        return None # Or raise internal error

def is_valid_identifier(identifier: str) -> bool:
    """Check if the identifier is valid."""
    return bool(identifier and isinstance(identifier, str) and identifier.strip())

def get_output_file_path(identifier: str) -> str:
    """Get the full path to the output file for a given identifier."""
    if not is_valid_identifier(identifier):
        raise ValueError(f"Invalid identifier: {identifier}")
    
    # Use the same path resolution as _get_output_path
    if not identifier or any(c in '/\\.' for c in identifier):
        raise ValueError(f"Invalid identifier for file path: '{identifier}'")
    return str((STORAGE_BASE_DIR / identifier).with_suffix(OUTPUT_FILE_SUFFIX))

def cleanup_all_processes():
    """Stop all managed processes on API exit."""
    print("Watcher Service: Cleaning up watcher processes...")
    identifiers = list(WATCHER_PROCESSES.keys())
    for identifier in identifiers:
        stop_watcher_process(identifier)
    print("Watcher Service: Cleanup finished.")

atexit.register(cleanup_all_processes)