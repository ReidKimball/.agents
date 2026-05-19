"""Preflight environment checks for the gmail-to-linear-tasks skill.
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Enforce UTF-8 on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def check_python_version():
    ver = sys.version_info
    if ver.major < 3 or (ver.major == 3 and ver.minor < 10):
        return {"success": False, "error": f"Python 3.10+ required. Current: {sys.version}"}
    return {"success": True}

def check_python_packages():
    missing = []
    try:
        import requests
    except ImportError:
        missing.append("requests")
    try:
        import dotenv
    except ImportError:
        missing.append("python-dotenv")
        
    if missing:
        return {"success": False, "error": f"Missing python packages: {', '.join(missing)}"}
    return {"success": True}

def check_credentials():
    from dotenv import load_dotenv
    env_path = Path.home() / ".agents" / ".env"
    if not env_path.exists():
        return {"success": False, "error": f"Environment file not found at {env_path}"}
        
    load_dotenv(dotenv_path=env_path)
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        return {"success": False, "error": f"LINEAR_API_KEY not found in {env_path}"}
    return {"success": True, "api_key_preview": f"{api_key[:8]}... (length: {len(api_key)})"}

def check_gws_cli():
    # Import gws_call helper to run a basic command
    try:
        sys.path.append(str(Path(__file__).parent))
        import gws_call
    except ImportError as e:
        return {"success": False, "error": f"Failed to import gws_call.py: {str(e)}"}
        
    # Check if CLI path resolves
    try:
        exe = gws_call.get_gws_executable()
    except FileNotFoundError as e:
        return {"success": False, "error": f"GWS CLI discovery failed: {str(e)}"}
        
    # Try a simple labels listing to test GWS credentials and connection
    labels_res = gws_call.list_labels()
    if not labels_res.get("success"):
        return {
            "success": False, 
            "error": "GWS CLI execution failed. Make sure you are authenticated with 'gws auth login'", 
            "details": labels_res.get("details", labels_res.get("error"))
        }
    return {"success": True}

def check_linear_api():
    # Resolve the team REI
    try:
        from dotenv import load_dotenv
        import requests
        
        load_dotenv(dotenv_path=Path.home() / ".agents" / ".env")
        api_key = os.environ.get("LINEAR_API_KEY")
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "query": "query { teams { nodes { id name key } } }"
        }
        r = requests.post("https://api.linear.app/graphql", headers=headers, json=payload)
        if r.status_code != 200:
            return {"success": False, "error": f"Linear API returned status {r.status_code}", "details": r.text}
            
        result = r.json()
        teams = result.get("data", {}).get("teams", {}).get("nodes", [])
        match = next((t for t in teams if t["key"] == "REI"), None)
        if not match:
            available = [t["key"] for t in teams]
            return {"success": False, "error": "Team REI not found in Linear.", "available_keys": available}
        return {"success": True, "teamId": match["id"]}
    except Exception as e:
        return {"success": False, "error": f"Failed to connect to Linear API: {str(e)}"}

def main():
    steps = {
        "python_version": check_python_version(),
        "python_packages": check_python_packages(),
        "credentials": check_credentials(),
        "gws_cli": check_gws_cli(),
        "linear_api": check_linear_api()
    }
    
    all_ok = all(step.get("success") for step in steps.values())
    
    output = {
        "success": all_ok,
        "results": steps
    }
    
    print(json.dumps(output, indent=2))
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
