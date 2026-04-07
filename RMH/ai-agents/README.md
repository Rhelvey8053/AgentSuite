# ai-agents

A personal agent suite built inside Claude in Chrome. Structured prompts saved as browser shortcuts that run autonomously against Gmail and Canvas LMS — no APIs, no infrastructure, no code.

Built and iterated over 12 days in Spring 2026 as a personal experiment in agentic AI productivity.

---

## What this is

Three agents, one feedback loop:

| Agent | Trigger | What it does |
|-------|---------|--------------|
| **InboxTriage** | Daily 9 AM | Classifies, labels, and prunes Gmail inbox using a two-tier retention system |
| **WeekBrief** | Weekly | Reads Canvas LMS agenda, stages AI-assisted assignments with ready-to-fire prompts |
| **KPIReport** | On demand | Parses all Agent-Stats emails and produces a performance dashboard |

The agents self-report via structured KPI emails after every run. KPIReport reads those emails and surfaces trends. The loop: **agent runs → STATS email → KPIReport audits → prompt patched → next run**.

---

## Results (Mar 26 – Apr 6, 2026)

| Metric | Value |
|--------|-------|
| InboxTriage runs | 10 |
| Emails eliminated | 422 |
| Inbox baseline | 874 |
| Agent runtime | ~441 min (7.4 hrs) |
| WeekBrief runs | 5 |
| Hours of coursework managed | ~23h |
| Combined time saved | ~1,822 min (30.4 hrs) |
| Prompt versions shipped | 16 |
| Bugs detected and fixed | 5 |

These numbers were audited and corrected by Claude Code — see [Process & Trials](docs/process-and-trials.md) for the full story including the data quality issues discovered during the audit.

---

## Architecture

```
Gmail Inbox / Canvas LMS
        ↓
  Claude in Chrome
  (prompt shortcuts)
        ↓
  Agent runs autonomously
        ↓
  Self-sends KPI email → Agent-Stats label
        ↓
  KPIReport parses all STATS emails
        ↓
  Dashboard + trend analysis
        ↓
  Prompt patched → next version
```

No external APIs. No webhooks. No hosted infrastructure.
The browser is the runtime. The prompt is the logic. Gmail is the database.

---

## Agent overview

### InboxTriage
Runs daily. Performs a full inbox audit in five steps:
1. Batch junk cleanup via targeted Gmail searches
2. Classify and label all unread email (HIGH / MED / LOW)
3. Audit read email backlog
4. Flag unanswered sent threads
5. Draft replies for real humans only

Uses a two-tier retention system per category label — some emails are kept permanently (tax docs, lease agreements), others deleted after 7, 14, 30, or 90 days depending on type.

→ [Prompt template](agents/inbox-triage/prompt-template.md) | [Changelog](agents/inbox-triage/CHANGELOG.md)

### WeekBrief
Runs weekly. Reads the Canvas LMS agenda and:
1. Deduplicates against the prior week's brief (carried assignments)
2. Deep-reads new assignments for requirements, rubric, and file links
3. Classifies as AI-assisted, collaborative, or independent
4. Generates ready-to-fire prompts for AI-assisted tasks
5. Sends Week Brief + Task Staging emails, logs KPIs

→ [Prompt template](agents/week-brief/prompt-template.md) | [Changelog](agents/week-brief/CHANGELOG.md)

### KPIReport
Runs on demand. Scans all Agent-Stats emails, normalizes field names across schema versions, validates data, computes aggregate stats, and sends a plain-text dashboard. Includes data quality flagging for known bug patterns.

→ [Prompt template](agents/kpi-report/prompt-template.md)

---

## Setup

See [Setup Guide](docs/setup-guide.md) for full installation instructions.

**Quick start:**
1. Install Claude in Chrome
2. Open Settings → Shortcuts → New Shortcut
3. Paste the prompt template for the agent you want
4. Fill in all `[YOUR_*]` placeholders
5. Set your schedule or run manually

**Required Gmail labels** (create before first run):
```
Reviewed
Agent-Stats
[YOUR_PREFIX]/Finance
[YOUR_PREFIX]/Tax-Legal
[YOUR_PREFIX]/Employer
[YOUR_PREFIX]/Housing
[YOUR_PREFIX]/Travel
[YOUR_PREFIX]/School
[YOUR_PREFIX]/Orders
[YOUR_PREFIX]/Agent-Reports
[YOUR_PREFIX]/Newsletters
[YOUR_PREFIX]/Family
[YOUR_PREFIX]/Security-Alerts
```

---

## Prompt engineering notes

Every version in the changelogs corresponds to a real failure in production. Nothing was added speculatively — each feature exists because a run broke without it.

Key patterns that emerged:
- **Never use Escape to close compose windows** — it discards drafts silently. Always use the minimize button.
- **Labeling via toolbar is unreliable** — category-specific search → select all → three-dot menu is the only consistent method.
- **Counter initialization matters** — without explicit `= 0` at run start, counters carry phantom values from prior context.
- **Field name consistency** — one mismatched field name (`cumulative_deleted` vs `cumulative_removed`) caused a silent chain error across 9 of 10 runs.

See [Process & Trials](docs/process-and-trials.md) for the full engineering narrative.

---

## Roadmap

- [ ] v2.9 — Smarter step budgeting based on inbox size at run start
- [ ] v3.0 — Remote activation via scheduled email trigger (no browser required)
- [ ] v3.1 — Cross-agent memory (InboxTriage surfaces relevant emails to WeekBrief)
- [ ] v4.0 — API migration — same logic, headless execution

---

## What's not in this repo

Personal prompt versions (with real email, labels, sender lists) are gitignored.
Only scrubbed templates with `[YOUR_*]` placeholders are included.

---

## License

MIT. Use freely, iterate openly.
