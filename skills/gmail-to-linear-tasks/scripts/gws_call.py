"""Dynamic Google Workspace CLI (gws) runner for Gmail operations.

Bypasses shell command parsing issues and handles Unicode/UTF-8 streams safely.
"""

import sys
import os
import json
import subprocess
import argparse
import shutil
from pathlib import Path

# Enforce UTF-8 on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def get_gws_executable() -> list[str]:
    """Dynamically locate the gws executable or the global node runner."""
    gws_path = shutil.which("gws")
    if gws_path:
        return [gws_path]
    
    # Fallback to standard global npm directory structure on Windows
    if sys.platform == "win32":
        local_npm = Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "@googleworkspace" / "cli" / "run.js"
        if local_npm.exists():
            return ["node", str(local_npm)]
            
    raise FileNotFoundError("Could not locate the 'gws' CLI on this system.")

def run_gws(args: list[str]) -> dict:
    """Run gws CLI with arguments, parsing output as JSON."""
    try:
        cmd = get_gws_executable() + args + ["--format", "json"]
    except FileNotFoundError as e:
        return {
            "success": False,
            "step": "locate-cli",
            "error": str(e)
        }
        
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        return {
            "success": False,
            "step": "execute-cli",
            "error": f"Exit code {res.returncode}",
            "details": res.stderr.strip() or res.stdout.strip()
        }
        
    try:
        # Check if the output is empty
        stdout_str = res.stdout.strip()
        if not stdout_str:
            return {"success": True, "data": None}
            
        # Try parsing entire stdout first (covers multi-line JSON)
        try:
            return {"success": True, "data": json.loads(stdout_str)}
        except json.JSONDecodeError:
            # Fallback to NDJSON (Newline Delimited JSON)
            lines = [line.strip() for line in stdout_str.splitlines() if line.strip()]
            if len(lines) == 1:
                return {"success": True, "data": json.loads(lines[0])}
            elif len(lines) > 1:
                return {"success": True, "data": [json.loads(line) for line in lines]}
            return {"success": True, "data": None}
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "step": "parse-json",
            "error": "Failed to parse JSON response",
            "details": f"{str(e)}\nRaw output: {res.stdout}"
        }

def list_unread(query: str, max_results: int) -> dict:
    params = {"userId": "me", "q": query, "maxResults": max_results}
    return run_gws(["gmail", "users", "messages", "list", "--params", json.dumps(params)])

def get_meta(message_id: str) -> dict:
    params = {"userId": "me", "id": message_id, "format": "metadata"}
    return run_gws(["gmail", "users", "messages", "get", "--params", json.dumps(params)])

def get_full(message_id: str) -> dict:
    params = {"userId": "me", "id": message_id, "format": "full"}
    return run_gws(["gmail", "users", "messages", "get", "--params", json.dumps(params)])

def list_labels() -> dict:
    params = {"userId": "me"}
    return run_gws(["gmail", "users", "labels", "list", "--params", json.dumps(params)])

def create_label(name: str) -> dict:
    params = {"userId": "me"}
    body = {
        "name": name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show"
    }
    return run_gws(["gmail", "users", "labels", "create", "--params", json.dumps(params), "--json", json.dumps(body)])

def label_message(label_id: str, message_ids: list[str]) -> dict:
    params = {"userId": "me"}
    body = {
        "ids": message_ids,
        "addLabelIds": [label_id]
    }
    return run_gws(["gmail", "users", "messages", "batchModify", "--params", json.dumps(params), "--json", json.dumps(body)])

def main():
    parser = argparse.ArgumentParser(description="Helper for gws Gmail CLI operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # list-unread
    parser_list = subparsers.add_parser("list-unread")
    parser_list.add_argument("--query", required=True)
    parser_list.add_argument("--max-results", type=int, default=500)
    
    # get-meta
    parser_meta = subparsers.add_parser("get-meta")
    parser_meta.add_argument("--id", required=True)
    
    # get-full
    parser_full = subparsers.add_parser("get-full")
    parser_full.add_argument("--id", required=True)
    
    # list-labels
    subparsers.add_parser("list-labels")
    
    # create-label
    parser_create = subparsers.add_parser("create-label")
    parser_create.add_argument("--name", required=True)
    
    # label-message
    parser_label = subparsers.add_parser("label-message")
    parser_label.add_argument("--label-id", required=True)
    parser_label.add_argument("--message-ids", nargs="+", required=True)
    
    args = parser.parse_args()
    
    if args.command == "list-unread":
        res = list_unread(args.query, args.max_results)
    elif args.command == "get-meta":
        res = get_meta(args.id)
    elif args.command == "get-full":
        res = get_full(args.id)
    elif args.command == "list-labels":
        res = list_labels()
    elif args.command == "create-label":
        res = create_label(args.name)
    elif args.command == "label-message":
        res = label_message(args.label_id, args.message_ids)
    else:
        res = {"success": False, "error": "Unknown command"}
        
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
