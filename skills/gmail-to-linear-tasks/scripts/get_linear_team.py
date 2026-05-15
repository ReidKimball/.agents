"""Query the Linear API for a team by key and return its ID.

Usage:
    python get_linear_team.py --key REI

Environment:
    LINEAR_API_KEY — loaded from ~/.agents/.env via python-dotenv

Output (JSON):
    {
        "success": true,
        "teamId": "8c5f5b72-...",
        "name": "Reid Kimball",
        "key": "REI"
    }
"""

import sys
import os
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description="Get Linear team ID by key")
    parser.add_argument("--key", required=True, help="Team key (e.g. REI)")
    args = parser.parse_args()

    # Load LINEAR_API_KEY from ~/.agents/.env
    load_dotenv(dotenv_path=Path.home() / ".agents" / ".env")
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        print(json.dumps({"success": False, "error": "LINEAR_API_KEY not set"}))
        sys.exit(1)

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "query": "query { teams { nodes { id name key } } }"
    }

    r = requests.post("https://api.linear.app/graphql", headers=headers, json=payload)
    result = r.json()

    teams = result.get("data", {}).get("teams", {}).get("nodes", [])
    match = next((t for t in teams if t["key"] == args.key), None)

    if match:
        output = {
            "success": True,
            "teamId": match["id"],
            "name": match["name"],
            "key": match["key"],
        }
    else:
        available = [{"key": t["key"], "name": t["name"]} for t in teams]
        output = {
            "success": False,
            "error": f"Team with key '{args.key}' not found",
            "availableTeams": available,
        }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
