# KPIReport Changelog

## v1.1.0 — 2026-04-02
**Field normalization, data validation, WeekBrief support**
- Added field name normalization on read: `cumulative_deleted` → `cumulative_removed`, `deleted` → `removed` — catches silent schema drift across prompt versions
- Added data validation rules with explicit failure conditions: `actions_taken` > `total_processed`, `cumulative_removed` decreasing between runs, `run_time_min` of 0 or > 120, contradictory inbox_remaining vs inbox_pct_cleared
- Added DATA NOTES section to dashboard output listing all flagged or skipped records with reason
- Added WeekBrief parsing: scans for WEEKBRIEF KPI lines alongside INBOXTRIAGE; computes separate stats block for each agent
- Added OVERALL summary block: combined time saved and total assignments staged across all agents
- `total_removed` computation changed to use highest `cumulative_removed` found across all records — more reliable than summing per-run fields when resets have occurred

## v1.0.0 — 2026-03-27
**Initial prompt**
- Scans `Agent-Stats` Gmail label and parses all INBOXTRIAGE KPI lines
- Computes aggregate InboxTriage stats: total runs, avg/best run time, total removed, drafted, kill time rate, inbox remaining, run time trend
- Sends plain-text dashboard email to self; applies Agent-Stats label
