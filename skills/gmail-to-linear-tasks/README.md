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

- Uses the `gws` CLI to read Gmail (authenticated via Google Workspace)
- Python helper scripts handle email parsing, base64 decoding, and Linear GraphQL calls
- All credentials loaded from `~/.agents/.env` at runtime — nothing hardcoded in scripts
- The agent classifies each email using criteria defined in `SKILL.md` (task requests, info/links provided, etc.)

## Portability

This skill was built for a specific machine and workflow. Paths, team keys, and conventions are tailored to my personal setup.

It is **not** designed to work out of the box on another machine. However, the architecture is straightforward and can be customized manually:

- Update hardcoded paths in `SKILL.md` to match your environment
- Replace the Linear team key (`REI`) with your own
- Ensure `gws` CLI is installed and authenticated
- Set `LINEAR_API_KEY` in `~/.agents/.env`

## Prerequisites

- `gws` CLI on `$PATH` and authenticated (`gws auth login`)
- Google Workspace Skills documentation: https://github.com/googleworkspace/cli/blob/main/docs/skills.md
- `LINEAR_API_KEY` environment variable set in `~/.agents/.env`
- Python 3.10+ with `requests` and `python-dotenv`

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
    ├── parse_email.py              # Parse Gmail JSON → headers + decoded body
    ├── get_linear_team.py          # Query Linear for team UUID by key
    └── create_linear_issue.py      # Create Linear issue via GraphQL
```

## Design Decisions

- **Helper scripts over inline code.** PowerShell mangles GraphQL `$input` variables. Python scripts avoid shell escaping nightmares entirely.
- **Narrow scope.** Read + create + label. No replies, no archiving, no side effects beyond what's explicitly documented.
- **Self-improving.** The `gotchas/GOTCHAS.md` file captures errors and failure patterns during execution, creating a feedback loop that improves the skill over time.
- **Credential separation.** Secrets live in `~/.agents/.env`, not in the skill folder.

## License

MIT
