# Gmail to Linear Tasks — Agent Skill

An AI agent skill that scans today's unread Gmail inbox, identifies actionable emails (task requests or information someone sent you), and auto-creates Linear issues for each one.

## What It Does

```
Scan today's unread inbox
    → Filter for emails containing tasks or requested info/links
    → Create a Linear issue with structured description + Gmail link
    → Label the email to prevent duplicates
    → Report what was created
```

The skill is intentionally narrow: it reads email, creates issues, and applies a label. It does not reply, archive, delete, or modify emails in any other way.

## How It Works

- **Preflight Health Checks:** A startup script validates environment dependencies, Python libraries, `~/.agents/.env` keys, Node executables, and Linear API access before any email processing begins.
- **Bypassed Shell Interpreters:** Executes the Google Workspace CLI dynamically via Python's list-based subprocesses (`gws_call.py`). This prevents command argument quote-escaping and shell authentication errors.
- **Safe UTF-8 Encoding:** Configures standard console input and output streams to force UTF-8 on Windows, avoiding terminal decoding/encoding crashes on emojis or non-ASCII characters in email content.
- **Linear Issue Creation:** Uses GraphQL API calls to resolve teams and create clean markdown descriptions with links back to the source Gmail threads.
- **Gmail Label Filtering:** Applies the `Linear Issue Created` label to prevent duplicate processing in future runs.

## Portability

This skill was built for a specific machine and workflow. Paths, team keys, and conventions are tailored to my personal setup.

It is **not** designed to work out of the box on another machine. However, the architecture is straightforward and can be customized manually:

- Update hardcoded paths in `SKILL.md` to match your environment
- Replace the Linear team key (`REI`) with your own
- Ensure `gws` CLI is installed and authenticated
- Set `LINEAR_API_KEY` in `~/.agents/.env`

## Prerequisites

- `gws` CLI installed and authenticated (`gws auth login`)
- Google Workspace Skills documentation: https://github.com/googleworkspace/cli/blob/main/docs/skills.md
- `LINEAR_API_KEY` set in `~/.agents/.env`
- Python 3.10+ with `requests` and `python-dotenv` packages installed

## Folder Structure

```
gmail-to-linear-tasks/
├── SKILL.md                        # Full agent instructions (step-by-step workflow)
├── README.md                       # This file
├── agents/
│   └── openai.yaml                 # Agent interface config
├── gotchas/
│   └── GOTCHAS.md                  # Known issues captured during execution
└── scripts/
    ├── preflight.py                # Verify environment, credentials, and CLI status
    ├── gws_call.py                 # Execute Gmail commands via list-based subprocess
    ├── parse_email.py              # Parse Gmail JSON → headers + decoded body
    ├── get_linear_team.py          # Query Linear for team UUID by key
    └── create_linear_issue.py      # Create Linear issue via GraphQL
```

## Design Decisions

- **Helper scripts over inline code.** Windows PowerShell and CMD mangle quotes and JSON parameters. Using python lists bypasses shell interpreters entirely.
- **Dynamic executable resolution.** Script dynamically checks standard `APPDATA` paths and environment settings to find the npm `gws` runner.
- **UTF-8 Stream Forcing.** Standardizes stream boundaries across all helper scripts to prevent character encoding crashes.
- **Narrow scope.** Read + create + label. No replies, no archiving, no side effects beyond what's explicitly documented.
- **Self-improving.** A mandatory **Step 10** in `SKILL.md` requires agents to record execution errors in `gotchas/GOTCHAS.md` before generating the final report.
- **Credential separation.** Secrets live in `~/.agents/.env`, not in the skill folder.

## License

MIT
