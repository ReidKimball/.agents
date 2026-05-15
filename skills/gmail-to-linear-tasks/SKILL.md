# Gmail to Linear Tasks

## Run a self-improvement loop before executing this skill
Check the `./gotchas/GOTCHAS.md` file for any issues that are hurting the performance of this skill. Stop executing the skill and discuss with the user what you found and how you plan to improve the skill. Get approval from the user before making changes to skill files, assets, and scripts.

## Purpose

Scan today's unread Gmail Inbox messages for emails that contain actionable tasks or information/links the user previously requested. For each qualifying email, auto-create a Linear issue in the **REI** team and label the Gmail message to prevent duplicates.

This skill is intentionally narrow: it reads email, creates Linear issues, and applies a Gmail label. It does not reply, archive, delete, or modify emails in any other way.

## Required GWS Skills

Before running Gmail commands, read and follow:

- `C:\Users\Reid\.agents\skills\gws-shared\SKILL.md`
- `C:\Users\Reid\.agents\skills\gws-gmail\SKILL.md`

Use `gws schema ...` if a command shape is uncertain.

## Prerequisites

- `gws` CLI on `$PATH` and authenticated (`gws auth login`)
- `LINEAR_API_KEY` environment variable set with a personal API key that has **Create issues** permission
- Python 3.10+ with `requests` and `python-dotenv` packages installed

## Helper Scripts

The `scripts/` subfolder contains Python scripts that handle JSON parsing, base64 decoding, and Linear API calls. **Always use these scripts** instead of inline Python or PowerShell for these operations — they avoid shell escaping issues (e.g. PowerShell mangling `$input` in GraphQL queries).

| Script | Purpose |
|--------|---------|
| `scripts/get_linear_team.py` | Query Linear for a team by key, return its UUID |
| `scripts/parse_email.py` | Parse Gmail full-format JSON, extract headers + decoded body |
| `scripts/create_linear_issue.py` | Create a Linear issue via GraphQL, return identifier + URL |

All scripts load `LINEAR_API_KEY` from `~/.agents/.env` automatically via `python-dotenv`.

Script base path:
```
C:\Users\Reid\.agents\skills\gmail-to-linear-tasks\scripts
```

## Step 1 — Discover the REI Team ID

Use the helper script to query Linear for the team with key `REI`:

```powershell
$scriptDir = "C:\Users\Reid\.agents\skills\gmail-to-linear-tasks\scripts"
$teamResult = python "$scriptDir\get_linear_team.py" --key REI | ConvertFrom-Json
$teamId = $teamResult.teamId
```

If `$teamResult.success` is `$false`, report the error (including available teams) and stop. Do not guess a team ID.

## Step 2 — List Today's Unread Inbox Messages

Use a broad recent query, then filter by local date (same pattern as `gmail-reply-soon-triage`):

```powershell
$query = "in:inbox is:unread newer_than:2d -label:Linear-Issue-Created"
gws gmail users messages list --params "{\"userId\":\"me\",\"q\":\"$query\",\"maxResults\":500}" --format json
```

If the result has no `messages`, report that there are no unread Inbox messages from today and stop.

## Step 3 — Filter to Today's Local Date

For each listed message ID, fetch metadata:

```powershell
gws gmail users messages get --params "{\"userId\":\"me\",\"id\":\"MESSAGE_ID\",\"format\":\"metadata\"}" --format json
```

Convert `internalDate` to local time and skip unless the local date equals today:

```powershell
$receivedLocal = [DateTimeOffset]::FromUnixTimeMilliseconds([int64]$message.internalDate).ToLocalTime()
$receivedLocal.Date -eq (Get-Date).Date
```

Also skip any message whose `labelIds` already contains the `Linear Issue Created` label ID (belt-and-suspenders with the query filter).

## Step 4 — Read Full Message Content

For messages that pass the date filter, fetch the full body and save to a temp file, then parse with the helper script:

```powershell
gws gmail users messages get --params "{\"userId\":\"me\",\"id\":\"MESSAGE_ID\",\"format\":\"full\"}" --format json | Out-File -FilePath "$env:TEMP\gmail_msg.json" -Encoding utf8

$parsed = python "$scriptDir\parse_email.py" "$env:TEMP\gmail_msg.json" | ConvertFrom-Json
```

The script returns a JSON object with: `from`, `to`, `subject`, `date`, `threadId`, `messageId`, `body` (plain text, base64 decoded).

## Step 5 — Classify the Email

Analyze the email content. An email qualifies if it contains **at least one** of:

### Task Requests (someone asks Reid to do something)
- Direct requests: "Can you…", "Please…", "Could you…", "I need you to…"
- Action items: "Send me…", "Review…", "Update…", "Schedule…", "Follow up on…"
- Deadlines or due dates tied to an action
- Approval requests: "Sign off on…", "Approve…"

### Information / Links Provided (someone responding to Reid's earlier ask)
- URLs to documents, articles, tools, or resources
- Attachments referenced as "here's what you asked for" or similar
- Answers to questions Reid previously asked, containing reference links

### Do NOT Qualify
- Newsletters, marketing, promotions, automated notifications
- Simple acknowledgments ("Thanks!", "Got it", "Sounds good")
- Calendar invites or meeting notifications
- Receipts, shipping notices, password resets
- Messages where Reid is CC'd but not directly addressed
- Purely social/conversational messages with no action item

When unsure, **skip the message**. Err on the side of fewer false positives.

## Step 6 — Ensure the Gmail Label Exists

List labels and find `Linear Issue Created`:

```powershell
gws gmail users labels list --params '{"userId":"me"}' --format json
```

Find the label with `name` exactly equal to `Linear Issue Created` and use its `id`.

If the label does not exist, create it:

```powershell
gws gmail users labels create --params '{"userId":"me"}' --json '{"name":"Linear Issue Created","labelListVisibility":"labelShow","messageListVisibility":"show"}' --format json
```

Use the returned label `id`.

## Step 7 — Create Linear Issue

For each qualifying email, construct the issue:

### Gmail Link Format
```
https://mail.google.com/mail/u/0/#inbox/<threadId>
```

### Issue Title
Use a concise, actionable title derived from the email subject and sender:
```
[Action from <SenderFirstName>] <Subject>
```

### Issue Description (Markdown)
```markdown
## Source Email
- **From:** <sender>
- **Subject:** <subject>
- **Date:** <date>
- **Gmail Link:** <gmail_link>

## Tasks Requested
- [ ] <task 1>
- [ ] <task 2>

## Links to Review
- <url 1>
- <url 2>

## Context
<Brief summary of the email context — what was discussed, why these tasks/links are relevant>
```

Omit the "Tasks Requested" section if there are no tasks. Omit the "Links to Review" section if there are no links.

### Create the Issue

Write the constructed description to a temp file, then call the helper script:

```powershell
$descriptionMarkdown | Out-File -FilePath "$env:TEMP\linear_desc.md" -Encoding utf8

$issueResult = python "$scriptDir\create_linear_issue.py" --team-id $teamId --title $title --description-file "$env:TEMP\linear_desc.md" | ConvertFrom-Json
```

Verify `$issueResult.success` is `$true`. Capture `$issueResult.identifier` (e.g., `REI-42`) and `$issueResult.url` for the report. If `success` is `$false`, log `$issueResult.error`, skip labeling this message, and continue.

## Step 8 — Label the Gmail Message

After successfully creating the Linear issue, apply the label:

```powershell
$body = @{
  ids = @("MESSAGE_ID")
  addLabelIds = @("LINEAR_ISSUE_CREATED_LABEL_ID")
} | ConvertTo-Json -Compress

gws gmail users messages batchModify --params '{"userId":"me"}' --json $body --format json
```

Batch multiple message IDs together if processing several emails.

## Step 9 — Final Report

Keep the response short and private:

- How many today's unread Inbox messages were scanned
- How many Linear issues were created
- For each issue: the Linear issue identifier (e.g., `REI-42`), a one-line summary, and the Linear URL
- How many messages were skipped (and brief reason categories)
- Any errors

Do **not** include full email bodies or sensitive content in the report. Summarize only.

## Error Handling

- If `LINEAR_API_KEY` is not set, report the error and stop immediately.
- If the REI team is not found, report available teams and stop.
- If a single issue creation fails, log the error, skip that email (do not label it), and continue with remaining emails.
- If Gmail API calls fail, retry once, then skip and report.

## Security Rules

- **Never** output the `LINEAR_API_KEY` value.
- **Never** display full email bodies in the final report.
- Confirm `LINEAR_API_KEY` is set before making any API calls.
- All Linear API calls use `Authorization: $env:LINEAR_API_KEY` header.

## Capturing Gotchas
Any errors, mistakes, and difficulties in executing this skill to a high level of quality and user satisfaction, write what the problem was to `./gotchas/GOTCHAS.md`. These will be used to improve this skill.
