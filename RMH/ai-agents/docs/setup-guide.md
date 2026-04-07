# Setup Guide

This guide walks through installing any agent from this suite into Claude in Chrome.

---

## Prerequisites

- Google Chrome
- Claude in Chrome extension installed and signed in
- A Gmail account
- For WeekBrief: access to a Canvas LMS instance

---

## Step 1 — Create Gmail labels

Before running any agent, create the following labels in Gmail.
Go to Gmail → Settings → Labels → Create new label.

Choose a short prefix for your labels (e.g. your first name).
All labels below use `[PREFIX]` — replace with your chosen prefix.

**Required for InboxTriage:**
```
Reviewed
Agent-Stats
[PREFIX]/Finance
[PREFIX]/Tax-Legal
[PREFIX]/Employer
[PREFIX]/Housing
[PREFIX]/Travel
[PREFIX]/School
[PREFIX]/Orders
[PREFIX]/Agent-Reports
[PREFIX]/Newsletters
[PREFIX]/Family
[PREFIX]/Security-Alerts
```

**Required for KPIReport:**
```
Agent-Stats  (same label as above — shared across agents)
```

Labels must exist before the first run. The agent will not create them automatically.

---

## Step 2 — Install the shortcut

1. Open Chrome with Claude in Chrome active
2. Click the Claude in Chrome extension icon
3. Go to **Settings → Shortcuts → New Shortcut**
4. Give it a name (e.g. `InboxTriage`, `WeekBrief`, `KPIReport`)
5. Paste the full prompt template into the shortcut editor
6. Set permission mode to **Follow Claude's Plan**
7. Set a schedule if you want it to run automatically, or leave unscheduled to run manually

---

## Step 3 — Fill in placeholders

Each template contains placeholders in `[YOUR_*]` format. Replace all of them before saving.

| Placeholder | What to put |
|-------------|-------------|
| `[YOUR_NAME]` | Your first name (used in email signatures) |
| `[YOUR_EMAIL]` | Your Gmail address |
| `[YOUR_TIMEZONE]` | IANA timezone e.g. `America/New_York` |
| `[YOUR_PREFIX]` | Your label prefix e.g. `Reed` → `Reed/Finance` |
| `[YOUR_EMPLOYER]` | Your employer's email domain e.g. `company.com` |
| `[YOUR_UNIVERSITY]` | Your university's email domain e.g. `university.edu` |
| `[YOUR_BANK]` | Your bank's email domain e.g. `chase.com` |

**Important:** the prefix you use in `[YOUR_PREFIX]` must exactly match the labels you created in Step 1. Case-sensitive.

---

## Step 4 — Customize sender lists

Each agent includes sender-based classification and deletion rules. The templates include generic examples — replace them with senders that actually appear in your inbox.

In InboxTriage, the main areas to customize:

**Category label mappings** — add your actual financial institutions, employer domain, university domain, housing company, etc.

**Step 1 junk cleanup searches** — add sender domains you consistently want removed. These run as batch deletions before individual email processing.

---

## Step 5 — First run

For InboxTriage:
- Open Gmail in the active Chrome tab
- Run the shortcut manually (click the shortcut name in the extension)
- Watch the pre-flight check output — it will confirm Gmail is visible and note the start time
- First run will establish your inbox baseline and initialize the STATS history

For WeekBrief:
- Navigate to your Canvas calendar agenda view before running
- URL format: `https://[your-institution].instructure.com/calendar#view_name=agenda`
- Run the shortcut

For KPIReport:
- Run after you have at least 2-3 STATS emails in your Agent-Stats label
- It will parse all historical records and produce a dashboard

---

## Recommended schedule

| Agent | Suggested schedule |
|-------|--------------------|
| InboxTriage | Daily, 9:00 AM |
| WeekBrief | Monday morning, before your week starts |
| KPIReport | Weekly or after a batch of runs |

---

## Known limitations

- **Session required** — Claude in Chrome must be actively running in Chrome. It does not run headlessly.
- **Tab must be visible** — the agent needs the correct tab (Gmail or Canvas) to be the active tab when it runs.
- **150-step kill switch** — all agents stop at 150 steps to prevent runaway execution. Large inboxes may not fully process in one run — this is expected.
- **60-minute kill switch** — agents also stop after 60 minutes elapsed.
- **STATS emails** — always use the minimize button (dash icon) to close compose windows, never Escape. Escape discards the draft silently.

---

## Troubleshooting

**Agent says "wrong tab"**
Navigate to Gmail (or Canvas for WeekBrief) and make it the active tab before running.

**Labels not applying correctly**
Do not use the toolbar label icon. The only reliable method: navigate to a sender-filtered search → select all → three-dot menu → Label as → type label name → click it.

**cumulative_removed not found warning**
This means the prior STATS email used an older field name. The agent will search back through history to find a valid value. This is expected behavior on the first run after upgrading from an older prompt version.

**STATS email not saved**
Check your Drafts folder. If the draft is there but unsent, open it, apply the Agent-Stats label, and send manually. This is caused by using Escape instead of the minimize button during a prior run.
