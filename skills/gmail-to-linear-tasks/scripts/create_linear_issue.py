"""Create a Linear issue via the GraphQL API.

Usage:
    python create_linear_issue.py --team-id <TEAM_ID> --title <TITLE> --description <DESCRIPTION>
    python create_linear_issue.py --team-id <TEAM_ID> --title <TITLE> --description-file <PATH>

Environment:
    LINEAR_API_KEY — loaded from ~/.agents/.env via python-dotenv

Output (JSON):
    {
        "success": true,
        "identifier": "REI-23",
        "title": "...",
        "url": "https://linear.app/..."
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
    parser = argparse.ArgumentParser(description="Create a Linear issue")
    parser.add_argument("--team-id", required=True, help="Linear team UUID")
    parser.add_argument("--title", required=True, help="Issue title")
    parser.add_argument("--description", default="", help="Issue description (Markdown)")
    parser.add_argument("--description-file", default="", help="Path to file containing description (Markdown)")
    args = parser.parse_args()

    # Load LINEAR_API_KEY from ~/.agents/.env
    load_dotenv(dotenv_path=Path.home() / ".agents" / ".env")
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        print(json.dumps({"success": False, "error": "LINEAR_API_KEY not set"}))
        sys.exit(1)

    description = args.description
    if args.description_file:
        with open(args.description_file, "r", encoding="utf-8") as f:
            description = f.read()

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "query": "mutation($input: IssueCreateInput!) { issueCreate(input: $input) { success issue { id identifier title url } } }",
        "variables": {
            "input": {
                "teamId": args.team_id,
                "title": args.title,
                "description": description,
            }
        },
    }

    r = requests.post("https://api.linear.app/graphql", headers=headers, json=payload)
    result = r.json()

    issue_data = result.get("data", {}).get("issueCreate", {})
    if issue_data.get("success"):
        issue = issue_data["issue"]
        output = {
            "success": True,
            "id": issue["id"],
            "identifier": issue["identifier"],
            "title": issue["title"],
            "url": issue["url"],
        }
    else:
        errors = result.get("errors", [])
        output = {
            "success": False,
            "error": errors[0]["message"] if errors else "Unknown error",
            "raw": result,
        }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
