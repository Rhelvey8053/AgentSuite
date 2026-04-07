# WeekBrief Changelog

## v2.1.0 — 2026-03-29
**Deduplication, carry-forward, schema v2**
- Added Step 1b deduplication check against prior Week Brief email
- Carried assignments tracked separately from new — no re-staging, no double-counting
- Added [~] marker in assignment table for carried items
- New KPI fields: `carried_assignments`, `completed_since_last_run`, `recurring_skipped`
- Added "Completed since last run" section to Step 8 output

## v2.0.0 — 2026-03-27
**KPI logging, task staging email split**
- Separated Week Brief and Task Staging into two distinct emails
- Added Step 7 KPI logging with Agent-Stats label
- Added pipe-separated STATS line format matching InboxTriage schema
- Added `hours_offloaded`, `offload_pct`, `time_saved_min` fields

## v1.1.0 — 2026-03-26
**Deep read gating, token efficiency**
- Added known recurring assignment list — skip deep read for patterns
- Added 6-assignment cap on deep reads per run (closest to due date first)
- Token efficiency rules: no screenshots between steps, extract_page_text limits

## v1.0.0 — 2026-03-26
**Initial prompt**
- Canvas agenda read, assignment classification (✦ / ⬡ / ⚠)
- Ready-to-fire prompt generation for AI-assisted tasks
- Single combined email output
