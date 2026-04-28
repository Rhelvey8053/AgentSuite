# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A suite of three prompt-based AI agents that run inside Claude in Chrome (browser extension). No APIs, no infrastructure, no build system — the prompts are the code. Gmail is the runtime database. All output is via self-sent emails labeled `Agent-Stats`.

## Agents

| Agent | File | Version | Trigger |
|-------|------|---------|---------|
| InboxTriage | `agents/inbox-triage/prompt-template.md` | v2.8.2 | Daily 9 AM |
| WeekBrief | `agents/week-brief/prompt-template.md` | v2.1.0 | Weekly Monday |
| KPIReport | `agents/kpi-report/prompt-template.md` | v1.1.0 | On demand |

## STATS line schema

Every agent run self-reports via a pipe-separated KPI line in a self-sent email labeled `Agent-Stats`. This is the primary data artifact for the whole system.

**InboxTriage schema:**
```
INBOXTRIAGE | {date} | start_time: HH:MM | end_time: HH:MM | run_time_min: N |
kill_time_reached: yes/no | step_kill_reached: yes/no |
new_unread_since_last_run: N | total_processed: N | removed_this_run: N |
cumulative_removed: N | net_cleared: N | drafted_replies: N | steps_used: N
```
`steps_used` added in v2.8.3. Absent in pre-v2.8.3 records — treat as N/A.
Target: `steps_used / total_processed <= 4`. Prior failure mode: ~9 steps/email.

**WeekBrief schema:**
```
WEEKBRIEF | {date} | start_time: HH:MM | end_time: HH:MM | run_time_min: N |
new_assignments: N | carried_assignments: N | completed_since_last_run: N |
ai_assisted: N | collaborative: N | independent: N | recurring_skipped: N |
hours_total: N | hours_offloaded: N | offload_pct: X% | time_saved_min: N |
pages_navigated: N
```

**Field name normalization** (early runs used different names — KPIReport normalizes these):
- `cumulative_deleted` → `cumulative_removed`
- `deleted` → `removed`

## Branch and commit conventions

- Feature branch: `claude/gmail-triage-agent-4Hwgx` (active development branch)
- Prompt changes get a version bump. Patches increment the third number (v2.8.1), behavioral changes increment the second (v2.9.0), major rewrites increment the first (v3.0.0).
- Every prompt version in the changelogs corresponds to a real production failure — nothing is added speculatively.

## What lives where

- `agents/*/prompt-template.md` — public templates with `[YOUR_*]` placeholders. Personal versions (real email, sender lists, label names) are **not committed** — gitignore them.
- `agents/*/CHANGELOG.md` — per-agent version history
- `docs/process-and-trials.md` — engineering narrative: what broke, what was learned
- `docs/setup-guide.md` — install instructions and placeholder reference

## Known failure patterns (don't reintroduce)

**Escape discards drafts** — Gmail compose must be closed with the minimize button (dash icon), never Escape. Escape silently discards unsaved drafts. This caused STATS emails to go missing across multiple runs before being fixed in v2.8.1.

**Counter initialization** — all counters (`UNREAD_PROCESSED`, `READ_AUDITED`, `REMOVED_THIS_RUN`, `DRAFTED_REPLIES`) must be explicitly set to `= 0` at run start. Uninitialized counters carry phantom values from prior context. Fixed in v2.8.2.

**Cumulative field name mismatch** — if a prompt version renames a STATS field, the next run's lookback search won't find it and will silently default to 0. This compounded across 9 of 10 runs before being caught by data audit. Any field rename needs a migration note in the prompt.

**Second compose reuse** — when the agent minimizes the Report draft then presses `c` for a second STATS compose, Gmail can reopen the minimized draft instead. Fixed in v2.8.3: navigate directly to mail.google.com instead of pressing `c`.

**Step efficiency** — Runs 7 and 10 hit the 150-step kill switch. Root cause: ~9 steps/email vs a 3-step target. The agent was taking screenshots between labeling actions and running `extract_page_text` redundantly. Fixed in v2.8.3: `steps_used` field added to STATS schema — now measurable from data, not just transcripts.

## Open work

- Run numbering discrepancy between transcript ("Run 9 partial") and STATS history ("Run 7") — unresolved
- WeekBrief schema v2 fields (`carried_assignments`, `completed_since_last_run`) not reflected in setup guide
- `tests/test_kpi_parser.py` covers parsing and validation logic; run with `python tests/test_kpi_parser.py`
