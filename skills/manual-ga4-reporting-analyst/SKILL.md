---
name: manual-ga4-reporting-analyst
description: Helps users manually obtain the right GA4 export and analyze it in plain English for one of five common reporting questions: monthly traffic, acquisition channels, top traffic pages, page engagement, or meaningful actions. Use this when a user wants help reading GA4, exporting the right report, interpreting CSV data, or turning GA4 exports into consistent Markdown summaries without API access.
---

# Manual GA4 Reporting Analyst

This skill helps users answer one GA4 reporting question at a time.

Use it when the user wants help:

- understanding GA4 reports without jargon
- exporting the right GA4 CSV manually
- analyzing a GA4 CSV or screenshot
- producing a consistent Markdown summary from GA4 data
- building repeatable reporting before API access exists

## Core Workflow

Follow this sequence:

1. Identify which of the 5 reporting questions the user wants to answer.
2. Check for a matching business context file in `references/contexts/`.
3. If no matching context file exists, run a lightweight setup and create one.
4. Guide the user to the correct GA4 report or Explore view.
5. Tell the user exactly which dimensions, metrics, date range, and comparison settings to use.
6. Ask for the exported CSV, or adapt to a screenshot if needed.
7. Analyze the data in plain English.
8. Save a Markdown report if the user wants a deliverable.

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

## Report Types

### 1. Monthly Traffic

Use this when the user wants a month-by-month traffic trend.

Preferred path:

- `Explore` -> `Free form`

Recommended setup:

- Rows: `Year`, `Month`
- Values: `Total users`, `New users`, `Sessions`

Important notes:

- Prefer a date range that starts at the beginning of a month.
- Warn the user when the first or last month is partial.
- `Month` alone is not enough for a year-long trend. Use `Year` and `Month` together when `Year month` is unavailable.

Interpretation focus:

- month-by-month traffic trend
- spikes, dips, and rebounds
- caution around partial months or known anomalies

### 2. Acquisition Channels

Use this when the user wants to know where visitors come from.

Preferred path:

- `Reports` -> `Acquisition` -> `User acquisition`

Recommended dimension:

- `First user primary channel group (Default Channel Group)`

Useful metrics:

- `Total users`
- `New users`
- `Returning users`
- `Average engagement time per active user`
- `Engaged sessions per active user`

Interpretation focus:

- which channels are bringing more people
- which channels are bringing better people
- which channels deserve more or less attention

### 3. Top Traffic Pages

Use this when the user wants to know which pages get the most traffic.

Preferred path:

- `Reports` -> `Engagement` -> `Pages and screens`

Recommended dimension:

- `Page path and screen class`

Useful metrics:

- `Views`
- `Active users`
- `Views per active user`
- `Average engagement time per active user`
- `Key events`

Interpretation focus:

- highest-traffic pages
- top content hubs
- which pages are real content drivers

Treat utility, admin, draft, and system pages cautiously.

### 4. Page Engagement

Use this when the user wants to know which pages keep people engaged vs. lose them.

Preferred path:

- `Reports` -> `Engagement` -> `Pages and screens`

Recommended dimension:

- `Page path and screen class`

Useful metrics:

- `Views`
- `Active users`
- `Views per active user`
- `Average engagement time per active user`
- `Key events`

Interpretation focus:

- which pages hold attention
- which pages attract traffic but shed attention quickly
- which content types appear strongest

### 5. Meaningful Actions

Use this when the user wants to know whether visitors are completing important actions.

Preferred path:

- `Admin` -> `Data display` -> `Key events` to inspect setup
- `Reports` -> `Engagement` -> `Events` to analyze outcomes

Useful metrics:

- `Event count`
- `Total users`
- `Event count per active user`

Interpretation focus:

- which events look like real business outcomes
- which events are missing, unreliable, or misconfigured
- whether actions like donations, signups, downloads, or form submissions are visible

Do not treat GA system events like `page_view`, `session_start`, `first_visit`, or `user_engagement` as business outcomes.

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