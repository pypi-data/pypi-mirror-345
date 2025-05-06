# subtxt/__main__.py
"""Command Line Interface for the subtxt SDK."""

import argparse
import asyncio
import sys
import os
import tomllib
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from . import generate, watch, __version__, SubtxtError
    from . import watcher
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from subtxt import generate, watch, __version__, SubtxtError
    from subtxt import watcher


def find_pyproject_toml(start_dir: Path = Path('.')) -> Optional[Path]:
    """Searches parent directories for pyproject.toml."""
    current_dir = start_dir.resolve()
    while True:
        pyproject_path = current_dir / "pyproject.toml"
        if pyproject_path.is_file():
            return pyproject_path
        parent_dir = current_dir.parent
        if parent_dir == current_dir:
            return None
        current_dir = parent_dir

def load_config_from_toml() -> Dict[str, Any]:
    """Loads configuration from [tool.subtxt] in pyproject.toml."""
    config = {}
    pyproject_path = find_pyproject_toml()
    if pyproject_path:
        try:
            with open(pyproject_path, "rb") as f:
                toml_data = tomllib.load(f)
            config = toml_data.get("tool", {}).get("subtxt", {})
        except Exception as e:
            print(f"Warning: Could not load or parse config from {pyproject_path}: {e}", file=sys.stderr)
    return config


def cli():
    """Parses arguments and runs the appropriate subtxt command."""
    config_defaults = load_config_from_toml()

    p = argparse.ArgumentParser(
        prog="subtxt",
        description=f"Generate or watch llms.txt files using sitemaps. Version {__version__}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    sub = p.add_subparsers(dest="cmd", required=True, help="Available commands")

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--url", default=config_defaults.get('url'), help="Homepage URL or direct sitemap.xml URL.")
    common_parser.add_argument("-i", "--include-path", dest="include_paths", action="append", default=None, help="Glob pattern for URL paths to include.")
    common_parser.add_argument("-x", "--exclude-path", dest="exclude_paths", action="append", default=None, help="Glob pattern for URL paths to exclude.")
    common_parser.add_argument("-r", "--replace-title", dest="replace_title", action="append", default=None, help="Sed-style substitution for titles (s/old/new/f).")
    common_parser.add_argument("-t", "--title", dest="output_title", default=None, help="Override the main title.")
    common_parser.add_argument("-d", "--description", dest="output_description", default=None, help="Override the main description.")
    common_parser.add_argument("-c", "--concurrency", type=int, default=config_defaults.get('concurrency', 10), help="Number of concurrent page fetch requests.")
    common_parser.add_argument("-ua", "--user-agent", default=config_defaults.get('user_agent'), help="Custom User-Agent string.")

    g = sub.add_parser("generate", help="Generate llms.txt (one-shot).", parents=[common_parser])
    g.add_argument("--out", default=config_defaults.get('output_file', 'llms.txt'), help="Output file path.")

    w = sub.add_parser("watch", help="Watch sitemap and update llms.txt.", parents=[common_parser])
    w.add_argument("--out", default=config_defaults.get('output_file', 'llms.txt'), help="Output file path.")
    w.add_argument("--interval", type=int, default=config_defaults.get('interval', 21600), help="Check interval in seconds.")

    args = p.parse_args()

    if not args.url:
         p.error("the following arguments are required: --url (or set 'url' in pyproject.toml [tool.subtxt])")

    final_config = {
        "url": args.url,
        "output_file": args.out,
        "concurrency": args.concurrency,
        "user_agent": args.user_agent,
        "output_title": args.output_title if args.output_title is not None else config_defaults.get('title'),
        "output_description": args.output_description if args.output_description is not None else config_defaults.get('description'),
        "include_paths": args.include_paths if args.include_paths is not None else config_defaults.get('include_paths', []),
        "exclude_paths": args.exclude_paths if args.exclude_paths is not None else config_defaults.get('exclude_paths', []),
        "replace_title": args.replace_title if args.replace_title is not None else config_defaults.get('replace_title', []),
    }
    if final_config['include_paths'] is None: final_config['include_paths'] = []
    if final_config['exclude_paths'] is None: final_config['exclude_paths'] = []
    if final_config['replace_title'] is None: final_config['replace_title'] = []

    if args.cmd == 'watch':
        final_config["interval"] = args.interval

    if args.cmd == "generate":
        print(f"Generating {final_config['output_file']} from sitemap at {final_config['url']}...", file=sys.stderr)
        try:
            llms_content = generate(
                url=final_config['url'],
                include_paths=final_config['include_paths'],
                exclude_paths=final_config['exclude_paths'],
                replace_title=final_config['replace_title'],
                output_title=final_config['output_title'],
                output_description=final_config['output_description'],
                concurrency=final_config['concurrency'],
                user_agent=final_config['user_agent'],
            )
            output_path = Path(final_config['output_file'])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(llms_content, encoding='utf-8')
            print(f"✅ Wrote {output_path.resolve()}", file=sys.stderr)
            if not llms_content.strip().startswith("# Error"):
                 print(llms_content)
            else:
                 print(llms_content, file=sys.stderr)
                 sys.exit(1)
        except SubtxtError as e:
             print(f"❌ Generation Error: {e}", file=sys.stderr)
             sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error during generation: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "watch":
        if final_config["interval"] <= 0:
             print("❌ Error: Watch interval must be positive.", file=sys.stderr)
             sys.exit(1)

        state_file_path = Path(final_config['output_file']).with_suffix(watcher.STATE_FILE_SUFFIX)
        print(f"Starting watcher for {final_config['url']}...", file=sys.stderr)
        print(f"(Will update '{final_config['output_file']}' and use state file '{state_file_path}')", file=sys.stderr)

        watch_args = {
            "url": final_config['url'],
            "interval": final_config['interval'],
            "output_file": final_config['output_file'],
            "include_paths": final_config['include_paths'],
            "exclude_paths": final_config['exclude_paths'],
            "replace_title": final_config['replace_title'],
            "output_title": final_config['output_title'],
            "output_description": final_config['output_description'],
            "concurrency": final_config['concurrency'],
            "user_agent": final_config['user_agent'],
        }
        try:
            asyncio.run(watch(**watch_args))
        except KeyboardInterrupt:
            print("\nWatcher stopped by user.", file=sys.stderr)
            sys.exit(0)
        except SubtxtError as e:
             print(f"❌ Watcher Error: {e}", file=sys.stderr)
             sys.exit(1)
        except Exception as e:
            print(f"❌ Critical error starting or during watch: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    """Entry point."""
    try:
        cli()
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()