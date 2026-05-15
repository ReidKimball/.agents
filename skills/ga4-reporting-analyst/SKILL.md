---
name: ga4-reporting-analyst
description: "Connects to the GA4 API and analyzes data in plain English for one of five common reporting questions: monthly traffic, acquisition channels, top traffic pages, page engagement, or meaningful actions. Use this when a user wants help reading GA4 data, interpreting analytics, or turning GA4 data into consistent Markdown summaries."
---

# GA4 Reporting Analyst

This skill connects to the GA4 Data API and helps users answer one GA4 reporting question at a time.

Use it when the user wants help:

- understanding GA4 data without jargon
- querying GA4 data directly via the API
- analyzing GA4 data in plain English
- producing a consistent Markdown summary from GA4 data

## First-Run Setup

Before doing anything else, check whether `.venv/` exists in the skill root directory.

If `.venv/` does **not** exist:

1. Run `python -m venv .venv` from the skill root directory.
2. Run `.venv\Scripts\pip install -r requirements.txt` from the skill root directory.
3. Tell the user: "Setting up for the first time — installing dependencies."

If `.venv/` already exists, skip setup and proceed normally.

This ensures the skill is self-bootstrapping — anyone who receives a copy of the skill folder just needs Python installed on their machine.

## Core Workflow

Follow this sequence:

1. Run the First-Run Setup check above.
2. Identify which of the 5 reporting questions the user wants to answer.
3. Check for a matching business context file in `references/contexts/`.
4. If no matching context file exists, run a lightweight setup and create one.
5. Call the appropriate function from `code/ga4_client.py` with the user's date range.
6. Analyze the returned data in plain English.
7. Save a Markdown report if the user wants a deliverable.

## Opening Behavior

If the user has not specified a report type yet, explain that you can help analyze 5 GA4 report types:

1. How many people visit the site each month?
2. Where do they come from?
3. Which pages get the most traffic?
4. Which pages keep people engaged vs. lose them?
5. Are people completing meaningful actions?

Then ask which one they want to focus on and what date range they want.

If the user already gave both, skip the question and continue.

## Lightweight Setup Routine

Before giving analysis, look for a relevant context file in `references/contexts/`.

Use the business name, website domain, or GA4 property name to find a likely match.

If no match exists, gather only these 4 things:

- business or GA4 property name
- business type
- primary goals of the website
- most important website actions

Then create a new Markdown file in `references/contexts/` named after the property or domain in lowercase kebab-case.

Keep the first version short. Update it later only when new important information appears.

Use the template in `references/business-context-template.md`.

## Analysis Style

Always translate GA4 into plain English.

Use this lens whenever possible:

- More people?
- Better people?
- What should we do about it?

Avoid drowning the user in GA4 jargon. Explain metrics only when they are necessary for interpretation.

## API Connection

The skill uses `code/ga4_client.py` in the skill root directory to connect to the GA4 Data API.

It loads credentials from `~/.agents/.env` per the `.api_registry` convention:

- `GA4_PROPERTY_ID` — the GA4 property ID
- `GOOGLE_APPLICATION_CREDENTIALS` — path to the service account JSON key file (relative paths resolve against `~/.agents/`)

The venv at `.venv/` contains the required packages (listed in `requirements.txt`).

If `.venv/` is missing, the First-Run Setup section above will create it automatically.

To run a query, use the venv Python:

```
.venv\Scripts\python.exe -c "from ga4_client import monthly_traffic; import json; print(json.dumps(monthly_traffic('30daysAgo', 'today'), indent=2))"
```

## Report Types

### 1. Monthly Traffic

Use this when the user wants a month-by-month traffic trend.

Function: `monthly_traffic(start_date, end_date, compare_start_date=None, compare_end_date=None)`

API dimensions: `yearMonth`
API metrics: `totalUsers`, `newUsers`, `sessions`

Important notes:

- Prefer a date range that starts at the beginning of a month.
- Warn the user when the first or last month is partial.

Interpretation focus:

- month-by-month traffic trend
- spikes, dips, and rebounds
- caution around partial months or known anomalies

### 2. Acquisition Channels

Use this when the user wants to know where visitors come from.

Function: `acquisition_channels(start_date, end_date, compare_start_date=None, compare_end_date=None)`

API dimension: `firstUserPrimaryChannelGroup`
API metrics: `totalUsers`, `newUsers`, `activeUsers`, `userEngagementDuration`, `engagedSessions`, `engagementRate`

Interpretation focus:

- which channels are bringing more people
- which channels are bringing better people
- which channels deserve more or less attention

### 3. Top Traffic Pages

Use this when the user wants to know which pages get the most traffic.

Function: `top_traffic_pages(start_date, end_date, limit=20, compare_start_date=None, compare_end_date=None)`

API dimension: `unifiedPagePathScreen`
API metrics: `screenPageViews`, `activeUsers`, `screenPageViewsPerUser`, `userEngagementDuration`, `keyEvents`

Interpretation focus:

- highest-traffic pages
- top content hubs
- which pages are real content drivers

Treat utility, admin, draft, and system pages cautiously.

### 4. Page Engagement

Use this when the user wants to know which pages keep people engaged vs. lose them.

Function: `page_engagement(start_date, end_date, limit=20, compare_start_date=None, compare_end_date=None)`

API dimension: `unifiedPagePathScreen`
API metrics: `screenPageViews`, `activeUsers`, `screenPageViewsPerUser`, `userEngagementDuration`, `keyEvents`

Interpretation focus:

- which pages hold attention
- which pages attract traffic but shed attention quickly
- which content types appear strongest

### 5. Meaningful Actions

Use this when the user wants to know whether visitors are completing important actions.

Function: `meaningful_actions(start_date, end_date, limit=20, compare_start_date=None, compare_end_date=None)`

API dimension: `eventName`
API metrics: `eventCount`, `totalUsers`, `eventCountPerUser`

Interpretation focus:

- which events look like real business outcomes
- which events are missing, unreliable, or misconfigured
- whether actions like donations, signups, downloads, or form submissions are visible

Do not treat GA system events like `page_view`, `session_start`, `first_visit`, or `user_engagement` as business outcomes.

## Comparison Date Ranges

All 5 report functions support optional comparison date ranges via `compare_start_date` and `compare_end_date` parameters.

When provided, metric values become `[current, comparison]` lists instead of single values. For example:

- `monthly_traffic("2026-03-01", "2026-03-31", "2025-03-01", "2025-03-31")` → YoY comparison
- `acquisition_channels("7daysAgo", "today", "14daysAgo", "8daysAgo")` → week-over-week

Ask the user if they want to compare against a previous period. Common comparisons:

- **Year-over-year**: same month, previous year
- **Period-over-period**: previous equivalent period (e.g., last 7 days vs the 7 days before)

When comparison data is present, the response includes `"comparison": true` and each metric value is a `[current, comparison]` pair.

## Data Quality Rules

- Treat suspicious traffic spikes cautiously.
- If the user mentions a known anomaly for a certain date range, include that caveat in the report.
- Do not assume all tracked events are meaningful.
- Do not assume all high-traffic pages are strategically important.
- If a report contains utility pages, login pages, drafts, or redirect pages, mention that they may distort the interpretation.

## Standard Output Structure

When writing a Markdown summary, use this structure:

- title
- report context
- simple reading lens
- scope notes if needed
- key takeaways
- plain-English summary
- what this means
- metrics used for interpretation

Keep the tone practical and readable.

## Domain Context Files

When a matching context file exists in `references/contexts/`, use it to adapt interpretation.

Examples:

- nonprofits: donations, newsletter signups, resource downloads, contact intent
- ecommerce: purchases, product-page behavior, cart actions
- SaaS: signups, demo requests, pricing-page behavior
- publishers: subscriptions, article engagement, recirculation

Only read the specific matching context file. Do not bulk-load all context files.

## Files To Read

- Use `references/business-context-template.md` when creating a new context file.
- Read a matching file under `references/contexts/` if one exists for the business or property.
- Use `code/ga4_client.py` for all GA4 API queries.
- Run all queries using the venv at `.venv/Scripts/python.exe`.
