"""Parse a Gmail full-format JSON message and output headers + decoded plain-text body.

Usage:
    python parse_email.py <path_to_gmail_json>

Output (JSON):
    {
        "from": "...",
        "to": "...",
        "subject": "...",
        "date": "...",
        "threadId": "...",
        "messageId": "...",
        "body": "..."
    }
"""

import sys
import json
import base64

# Ensure UTF-8 output on Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def extract_text(payload):
    """Recursively extract plain text body from Gmail payload, decoding base64."""
    mime = payload.get("mimeType", "")
    if mime == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", "replace")
    for part in payload.get("parts", []):
        result = extract_text(part)
        if result:
            return result
    return ""


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_email.py <path_to_gmail_json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        msg = json.load(f)

    headers_list = msg.get("payload", {}).get("headers", [])
    headers = {h["name"]: h["value"] for h in headers_list}

    body = extract_text(msg.get("payload", {}))

    output = {
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "threadId": msg.get("threadId", ""),
        "messageId": msg.get("id", ""),
        "body": body,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
