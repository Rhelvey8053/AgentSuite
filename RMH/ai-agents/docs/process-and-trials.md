# Process & Trials

This document is the engineering narrative behind the agent suite — what broke, what was learned, and how the prompts evolved. Every version number in the changelogs corresponds to a real failure in production.

---

## How this started

The goal was simple: stop manually triaging email and stop forgetting Canvas deadlines. The hypothesis was that a well-structured prompt, saved as a browser shortcut, could do both autonomously.

The first version of InboxTriage was written in a single session. It ran. It did something. The output was an HTML-formatted email that was unreadable in Gmail's plain text view. That was Run 1.

From there, every run exposed something new. The changelog is the real story.

---

## The iteration loop

Each run produced a STATS email with pipe-separated KPIs. Those emails accumulated in the Agent-Stats Gmail label. Over time, that label became a log — a structured record of every run, every metric, every failure mode.

When enough runs had accumulated, Claude Code was used to audit the full history. That audit found things the agent itself hadn't caught.

---

## Key failures and what they taught

### The Escape bug (Runs 1–7, fixed in v2.8.1)

The prompt originally told the agent to press Escape to close compose windows after saving drafts. Escape discards unsaved drafts in Gmail. The agent was saving the draft, then immediately discarding it with Escape before autosave could complete.

The fix was one word: minimize instead of Escape. The minimize button (dash icon) closes the compose window without discarding. A single behavioral change eliminated the most consistent failure in the suite.

**Lesson:** In browser automation via natural language, the exact action matters more than the intent. "Close the window" is ambiguous. "Click the minimize button" is not.

---

### The cumulative reset chain (Runs 1–10, fixed in v2.8.2)

The most subtle bug in the project. Runs 1–3 used a field name `cumulative_deleted` in their STATS emails. Starting with Run 4, the prompt was updated to use `cumulative_removed`. When Run 4 searched the prior STATS email for `cumulative_removed`, it didn't find it and silently defaulted to 0.

This propagated through every subsequent run. The agent was always carrying forward from 0 instead of from the true cumulative. By Run 10, the reported cumulative was 324 — the true corrected value was 422, an undercount of 98.

The fix had two parts:
1. Explicit warning when `cumulative_removed` is not found — do not default to 0, search back through history
2. Standardized field names across all prompt versions

Claude Code found this by parsing all 10 STATS emails in sequence and noticing that the cumulative values were not additive. The cumulative column should always be monotonically increasing. It wasn't.

**Lesson:** Self-reported metrics are only as reliable as the schema they use. One field name change without a migration plan creates a silent data corruption chain. The fix is the same as in software: validate on read, not just on write.

---

### The actions_taken overcounting bug (Run 3, fixed in v2.8.2)

Run 3 reported `actions_taken: 365` against a total of roughly 67 emails processed. The prompt at that time defined `actions_taken` vaguely — the agent included label applications, page loads, and navigation events in the count.

The fix was a strict definition: `actions_taken = emails removed + drafts saved + emails flagged for review only`. Navigation and labeling are not actions — they are overhead.

**Lesson:** In agentic systems, every metric needs an explicit formula. "Actions taken" is not self-defining. Ambiguous metrics produce garbage data.

---

### The read_audited zero bug (Run 6, fixed in v2.8.2)

Run 6 reported `read_audited: 0` despite touching 105 emails in Step 3. The counter variable was being referenced but never initialized at run start. The agent was incrementing a variable that didn't exist, which in the prompt context meant it was never tracked.

The fix was an explicit counter initialization block at the top of the pre-flight check:
```
UNREAD_PROCESSED = 0
READ_AUDITED = 0
REMOVED_THIS_RUN = 0
DRAFTED_REPLIES = 0
```

**Lesson:** Initialize everything explicitly. Assume nothing about prior state.

---

### Step efficiency (Runs 7 and 10, addressed in v2.8.2)

Run 7 and Run 10 both hit the 150-step kill switch. Analysis of Run 10's transcript showed an average of 9 steps per email against a target of 3. The agent was taking screenshots between labeling actions, running extract_page_text redundantly, and navigating back to the inbox between each email instead of batching.

v2.8.2 added explicit step budget guidance: budget 3 steps per email, check remaining count at step 100, skip Step 3 if unable to finish at that rate.

**Lesson:** Kill switches are necessary but not sufficient. A prompt that hits the kill switch every run is not a prompt that works — it's a prompt that fails gracefully. The goal is to not need the kill switch.

---

## The Claude Code audit

After 10 InboxTriage runs and 5 WeekBrief runs, Claude Code was used to do a full audit of the Agent-Stats label. The audit:

- Parsed all STATS emails and reconstructed the corrected cumulative chain
- Found the 2 WeekBrief runs missing from the manual count (CLAUDE.md had 3, audit found 5)
- Identified the Run 7 removed count as wrong (CLAUDE.md showed 53 — that was `total_processed`, actual `removed` was 146)
- Produced the corrected dataset used in this repo's metrics

The audit itself is an example of the meta-loop working: the agents generate data, the data is audited, the audit finds errors, the errors get patched into the next prompt version.

---

## WeekBrief evolution

WeekBrief had a quieter development path than InboxTriage — fewer runs, less data, but a meaningful schema evolution.

Runs 1–3 used the original schema. By Run 4, the prompt had been updated to v2 with three new fields: `carried_assignments`, `completed_since_last_run`, and `recurring_skipped`. These fields exist because Run 3 surfaced a real problem — the agent was re-staging assignments it had already staged the prior week, generating duplicate task prompts.

The deduplication logic in Step 1b of WeekBrief (checking new assignments against the prior Week Brief email) was the fix. It also changed how KPIs are counted: carried assignments are tracked separately from new ones, so the numbers stay honest.

---

## What 16 prompt versions in 12 days looks like

| Version | What triggered it |
|---------|------------------|
| v1.0.0 | First run — needed a starting point |
| v1.1.0 | Run 1 showed labels weren't being remembered across batches |
| v1.2.0 | Pre-flight check added after running on wrong tab |
| v2.0.0 | Runs taking 55+ min — needed hard kill time |
| v2.1.0 | No structured output — added KPI line |
| v2.2.0 | HTML email unreadable — switched to plain text |
| v2.3.0 | Labeling order wrong — batch deletions moved before labeling |
| v2.4.0 | KPI fields inconsistent — standardized schema |
| v2.4.1 | Language too aggressive ("delete permanently") — softened |
| v2.5.0 | No step limit — added 150-step kill switch |
| v2.6.0 | No category system — added Reed/ label hierarchy |
| v2.6.1 | Tab and dash navigation bugs — patched |
| v2.7.0 | Ready for public — scrubbed and templatized |
| v2.8.0 | Retention rules too blunt — added two-tier system |
| v2.8.1 | STATS draft discarded by Escape — fixed to minimize |
| v2.8.2 | Counter init, step budget, cumulative reset warning |

None of these were planned. All of them were responses to something that broke.

---

## What's still open

- **Run numbering discrepancy** — the transcript calls one run "Run 9 (partial)" but the STATS history calls it Run 7. Needs resolution before the next audit.
- **v2.8.2 step efficiency unconfirmed** — the guidance was added but the next clean run hasn't happened yet. The target is 3–4 steps/email vs the current 9.
- **WeekBrief schema v2 not reflected in CLAUDE.md** — the `carried_assignments` and `completed_since_last_run` fields exist in the prompt but weren't documented in the project notes until the audit.
- **Inbox trajectory** — 874 baseline, net trajectory positive but new inbound keeps arriving. The goal is net reduction, not just removal rate.
