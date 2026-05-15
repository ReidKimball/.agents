# GA4 Reporting Analyst — Agent Skill

An AI agent skill that connects to the Google Analytics 4 Data API and delivers plain-English analysis for five common reporting questions.

Built for use with [Windsurf](https://codeium.com/windsurf) (Cascade) and compatible with any agent framework that reads `SKILL.md` files.

## What It Does

Ask a question in natural language — the skill queries the GA4 API, interprets the data, and returns a readable summary.

**Supported report types:**

1. **Monthly Traffic** — month-by-month visitor trends
2. **Acquisition Channels** — where visitors come from and which channels bring the best engagement
3. **Top Traffic Pages** — which pages get the most traffic
4. **Page Engagement** — which pages hold attention vs. lose it
5. **Meaningful Actions** — whether visitors are completing important actions (purchases, signups, downloads, etc.)

All reports support **comparison date ranges** (year-over-year, period-over-period) out of the box.

## How It Works

```
User asks a question
    → Skill identifies the report type
    → Calls the GA4 Data API via code/ga4_client.py
    → Returns plain-English analysis with actionable takeaways
    → Optionally saves a Markdown report
```

The skill adapts interpretation to business context. A nonprofit gets analysis focused on donations and newsletter signups. An e-commerce site gets analysis focused on purchases and product-page behavior. Context files in `references/contexts/` make this automatic.

## Installation

### Prerequisites

- **Python 3.11+** installed on your machine
- **A Google Cloud service account** with access to the GA4 Data API
- **Viewer access** on the GA4 property for that service account

### Step 1 — Copy the skill folder

Place the `ga4-reporting-analyst/` folder in your agent skills directory.

This is typically `~/.agents/skills/` or `C:\Users\<YOUR_USERNAME>\.agents\skills`

### Step 2 — Set up credentials

Create (or edit) the file `~/.agents/.env` and add these two lines:

```
GA4_PROPERTY_ID=123456789
GOOGLE_APPLICATION_CREDENTIALS=your-service-account-key.json
```

- `GA4_PROPERTY_ID` — your GA4 property ID (found in GA4 under Admin → Property Settings)
- `GOOGLE_APPLICATION_CREDENTIALS` — path to your service account JSON key file. Relative paths resolve against `~/.agents/`, so you can place the key file there.

> **Security note:** Never commit the `.env` file or the JSON key file to a public repository.

### Step 3 — First run (automatic)

The skill is self-bootstrapping. On first invocation, it will:

1. Detect that `.venv/` does not exist
2. Create a Python virtual environment
3. Install dependencies from `requirements.txt`

No manual `pip install` needed. Just invoke the skill and it handles setup.

### Step 4 — Create your business context (optional)

The skill works without a context file, but analysis is better with one. On first use, the skill will ask about your business and create a context file in `references/contexts/`.

You can also create one manually using the template at `references/business-context-template.md`.

## Folder Structure

```
ga4-reporting-analyst/
├── SKILL.md                          # Skill instructions (read by the agent)
├── README.md                         # This file
├── requirements.txt                  # Python dependencies
├── .env.example                      # Template for required environment variables
├── .gitignore                        # Excludes .venv/ and __pycache__/
├── agents/
│   └── openai.yaml                   # Agent interface config
├── code/
│   └── ga4_client.py                 # GA4 Data API client (5 query functions)
├── references/
│   ├── business-context-template.md  # Template for new business contexts
│   └── contexts/                     # Business-specific context files
│       └── pawsome-threads-ga4.md    # Example context (fictional dog clothing company)
└── reports/                          # Generated Markdown reports (gitignored content)
```

## Design Decisions

- **API-first, not CSV.** The skill queries GA4 directly — no manual exports, no screenshots, no copy-paste.
- **Self-bootstrapping.** First run creates the venv and installs dependencies automatically.
- **Credential separation.** Secrets live in `~/.agents/.env`, not in the skill folder. Safe to share or commit the skill.
- **Business context files.** The skill adapts its interpretation lens based on a simple Markdown file describing the business. This makes the same skill useful for nonprofits, e-commerce, SaaS, and publishers.
- **Comparison built in.** Every report function supports optional comparison date ranges for year-over-year or period-over-period analysis.

## Example Usage

```
User: "Where did our traffic come from in March?"
Agent: queries acquisition_channels("2026-03-01", "2026-03-31")
     → returns a table of channels ranked by total users and engagement rate
     → highlights which channels bring volume vs. quality
     → recommends where to invest or pull back
```

## License

MIT
