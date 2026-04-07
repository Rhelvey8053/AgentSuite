# InboxTriage Changelog

## v2.8.2 — 2026-04-06
**Counter init, step budget, cumulative reset warning, actions_taken definition**
- Added explicit counter initialization block (`= 0`) for all four counters at run start — fixes `read_audited: 0` bug from Run 6
- Added step budget guidance: budget 3 steps/email, check at step 100, skip Step 3 if unable to finish
- Added `cumulative_removed` not-found warning — agent now searches back through history rather than defaulting to 0
- Strict `actions_taken` definition: removed + drafted + flagged only — never label applications or navigation

## v2.8.1 — 2026-04-06 (patch)
**STATS draft compose fix**
- Changed STATS email compose close instruction from Escape to minimize button (dash icon)
- Escape was silently discarding drafts before autosave — root cause of missing STATS emails in Runs 8, 9, 10

## v2.8.0 — 2026-04-02
**Two-tier retention rules, Newsletters label**
- Added two-tier retention system per category: KEEP PERMANENTLY vs DELETE AFTER N DAYS
- Added [YOUR_PREFIX]/Newsletters as a dedicated label with 14-day deletion rule
- Retention rules cover Finance, School, Security-Alerts, Housing, Travel, Orders, Family, Agent-Reports

## v2.7.0 — 2026-04-02
**Public template release**
- Replaced all personal values with [YOUR_*] placeholders
- Added installation instructions and placeholder reference
- Scrubbed sender lists to generic examples

## v2.6.1 — 2026-04-01 (patch)
**Tab navigation fix, hyphen not em dash**
- Fixed Tab navigation between compose fields (To → Subject → Body)
- Replaced em dashes in subject line instructions with hyphens — em dashes were causing subject field rendering issues

## v2.6.0 — 2026-04-01
**Category label system**
- Added [YOUR_PREFIX]/ label hierarchy with 11 categories
- Added category label reference section with sender-to-category mappings
- Labeling method standardized: search by sender → select all → three-dot menu → Label as

## v2.5.0 — 2026-03-29
**Step kill switch, compose click navigation**
- Added 150-step kill switch with go-to-FINAL-STEP instruction
- Added explicit click navigation for compose fields (find tool, Tab between fields)
- Added Ctrl+A then Delete to clear compose body before typing

## v2.4.1 — 2026-03-27 (patch)
**Language softening**
- Changed "delete permanently" to "move to trash" throughout
- Changed "send" to "submit" for report emails

## v2.4.0 — 2026-03-27
**KPI field standardization, cumulative carry-forward**
- Standardized all KPI field names to final schema
- Added cumulative_removed carry-forward logic from prior STATS email
- Added ORIGINAL_INBOX_SIZE tracking

## v2.3.0 — 2026-03-27
**Batch deletion, labeling sequence fix**
- Moved Step 1 junk cleanup before unread processing (was after)
- Added OR-operator batch deletion for LOW-classified emails
- Added explicit logging per search and per deleted email

## v2.2.0 — 2026-03-27
**Plain text output**
- Switched report email from HTML to plain text
- Run 1 output was HTML-formatted and unreadable in Gmail plain text view

## v2.1.0 — 2026-03-26
**KPI logging**
- Added STATS email compose step
- Added Agent-Stats label application
- Added pipe-separated KPI line format

## v2.0.0 — 2026-03-26
**Kill time, read audit cutoff**
- Added 1-hour kill time from RUN_START_TIME
- Added 45-minute cutoff for Step 3 (read email backlog)
- Added RUN_START_TIME capture in pre-flight

## v1.2.0 — 2026-03-26
**Pre-flight check, draft failure handling**
- Added pre-flight check confirming Gmail is active tab
- Added error logging and continue behavior for step failures
- Added explicit draft-save verification

## v1.1.0 — 2026-03-26
**Reviewed label memory, full inbox read audit**
- Added `label:Reviewed` exclusion to prevent re-processing
- Added Step 3 (read email backlog) for emails processed in prior runs
- Added PRIOR_RUN_MEMORY search against Agent-Stats

## v1.0.0 — 2026-03-26
**Initial prompt**
- Basic inbox triage: classify, label, draft replies
- HTML output format (later replaced)
- No step limits, no kill time, no KPI logging
