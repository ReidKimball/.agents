# .agents

A collection of AI agent skills designed around one principle: **the agent should either make me think harder or do real work I don't normally do.**

## Design Philosophy

I design two types of skills:

### Skills That Push My Thinking

These are Socratic coaches and mentors. They don't write the answer for me — they ask better questions, challenge weak assumptions, and force me to articulate what I actually mean.

Examples:

- **engineering-tutor** — teaches programming fundamentals while preventing passive AI reliance.
- **api-design** - guides me through designing RESTful and GraphQL APIs following industry best practices.

The pattern: I do the thinking. The skill makes sure I'm thinking well.

### Skills That Connect to APIs and Do Real Work

These are mini software applications that live inside the agent. They authenticate with real services, query real data, and produce real outputs — not summaries of what's on screen, but actual API-driven automation.

Examples:

- **ga4-reporting-analyst** — connects to the Google Analytics 4 Data API, queries traffic data, and delivers plain-English analysis with actionable recommendations. Self-bootstrapping: creates its own Python venv on first run.
- **gmail-to-linear-tasks** — reads Gmail, parses actionable emails, and creates structured issues in Linear. End-to-end: inbox to issue tracker with no manual copy-paste.

The pattern: the skill does the tedious, repeatable work so I can focus on decisions.

## How Skills Work

Each skill is a folder with a `SKILL.md` file that tells the agent how to behave. Some skills also include:

- **`code/`** — Python modules that connect to APIs (GA4, Gmail, Linear, etc.)
- **`references/`** — business context files that adapt the skill's behavior per project
- **`reports/`** — generated deliverables (Markdown summaries, analyses)
- **`requirements.txt`** — Python dependencies, auto-installed on first run

Skills are designed to be **portable**. Copy a skill folder to another machine, set up credentials, and it works. API-connected skills use `~/.agents/.env` for secrets — nothing is hardcoded in the skill itself.

## Skill Structure

```
skills/
├── ga4-reporting-analyst/       # API-connected: queries GA4 Data API
│   ├── SKILL.md                 # Agent instructions
│   ├── code/ga4_client.py       # API client with 5 query functions
│   ├── references/contexts/     # Business-specific interpretation context
│   ├── reports/                 # Generated analysis reports
│   └── requirements.txt         # Auto-installed Python deps
│
├── critical-thought-partner/    # Thinking skill: no API, pure coaching
│   └── SKILL.md                 # Socratic coaching instructions
│
├── gmail-to-linear-tasks/       # API-connected: Gmail → Linear pipeline
│   ├── SKILL.md
│   └── scripts/                 # Email parsing + Linear issue creation
│
└── ...
```

## Why This Matters

Most people use AI agents as autocomplete — ask a question, get a paragraph. These skills are different:

- **Thinking skills** create a feedback loop that builds real competence. The agent doesn't let me be lazy.
- **API skills** replace manual workflows that eat hours. The agent reads the email, queries the data, creates the ticket, publishes the post — and I review the output.

The goal is an agent that's both a rigorous thinking partner and a capable operator.

## Getting Started

To use a skill from this repo:

1. Copy the skill folder into `~/.agents/skills/` (or `C:\Users\<YOUR_USERNAME>\.agents\skills\` on Windows)
2. If the skill has a `requirements.txt`, it will auto-install dependencies on first run
3. If the skill connects to an API, add the required credentials to `~/.agents/.env` (see `.env.example` in the skill folder)
4. Invoke the skill in your agent (e.g., Windsurf Cascade)

Each API-connected skill includes its own README with specific setup instructions.

## Author

Reid Kimball — [GitHub](https://github.com/ReidKimball)
