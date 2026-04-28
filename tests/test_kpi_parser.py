"""
KPI parser and validator for AgentSuite STATS emails.

Parses the pipe-separated KPI line format produced by InboxTriage and
WeekBrief, validates data integrity, and computes derived metrics —
without requiring a live Gmail session.

Run:
    python tests/test_kpi_parser.py
    python -m pytest tests/
"""

import unittest
from typing import Optional


# ---------------------------------------------------------------------------
# Field-name normalization
# Early runs used different names. KPIReport normalizes on read.
# ---------------------------------------------------------------------------

FIELD_ALIASES = {
    "cumulative_deleted": "cumulative_removed",
    "deleted": "removed",
}


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_stats_line(line: str) -> dict:
    """
    Parse a pipe-separated STATS line into a normalized flat dict.

    Expected format:
        INBOXTRIAGE | YYYY-MM-DD | key: val | key: val | ...
    """
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 2:
        raise ValueError(f"Malformed STATS line: {line!r}")
    agent = parts[0]
    if agent not in ("INBOXTRIAGE", "WEEKBRIEF"):
        raise ValueError(f"Unknown agent type: {agent!r}")
    record: dict = {"agent": agent, "date": parts[1]}
    for part in parts[2:]:
        if ":" in part:
            key, _, val = part.partition(":")
            key = FIELD_ALIASES.get(key.strip(), key.strip())
            record[key] = val.strip()
    return record


def int_field(record: dict, key: str, default: int = 0) -> int:
    """Safely coerce a record field to int."""
    try:
        return int(record.get(key, default))
    except (ValueError, TypeError):
        return default


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def validate_record(record: dict) -> list:
    """Return a list of validation error strings for a single STATS record."""
    errors = []
    total_processed = int_field(record, "total_processed")
    removed = int_field(record, "removed_this_run")
    run_time = int_field(record, "run_time_min")

    if total_processed > 0 and removed > total_processed:
        errors.append(
            f"removed_this_run ({removed}) > total_processed ({total_processed})"
        )
    if run_time == 0 or run_time > 120:
        errors.append(f"run_time_min ({run_time}) outside expected range 1-120")

    return errors


def validate_cumulative_chain(records: list) -> list:
    """
    Verify cumulative_removed is monotonically increasing across runs.
    Returns a list of reset-event dicts when a decrease is detected.

    A decrease means a run searched for cumulative_removed in the prior STATS
    email, didn't find it (due to a field rename), and silently defaulted to 0.
    """
    events = []
    prev = 0
    for i, record in enumerate(records):
        current = int_field(record, "cumulative_removed")
        if current < prev:
            events.append({
                "run": i + 1,
                "date": record.get("date", "unknown"),
                "prior": prev,
                "reported": current,
                "type": "cumulative_reset",
            })
        prev = current
    return events


def corrected_cumulative(records: list) -> int:
    """
    True cumulative = sum of all per-run removed_this_run values.

    The reported cumulative_removed field underestimates whenever a
    field-name reset occurred, because the agent carried forward from 0
    instead of from the true prior total.
    """
    return sum(int_field(r, "removed_this_run") for r in records)


# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------

def compute_net_cleared(baseline: int, current_inbox_count: int) -> int:
    """Emails cleared relative to the original inbox baseline."""
    return baseline - current_inbox_count


def compute_steps_per_email(record: dict) -> Optional[float]:
    """
    Returns steps/email ratio, or None if steps_used is absent (pre-v2.8.3).
    Target: <= 4. Observed failure mode in Runs 7 and 10: ~9 steps/email.
    """
    if "steps_used" not in record:
        return None
    steps = int_field(record, "steps_used")
    total = int_field(record, "total_processed")
    return round(steps / total, 2) if total > 0 else None


# ---------------------------------------------------------------------------
# Fixtures — representative of the 10-run production history (Mar-Apr 2026)
#
# Runs 1-3:  used field name `cumulative_deleted` (pre-rename)
# Run 4:     field rename to `cumulative_removed` caused a silent reset to 0;
#            true cumulative at that point was 98, reported was 42.
# Run 5:     kill_time_reached (60-min limit hit)
# Run 7:     step_kill_reached; audit corrected removed from 53 → 146 via
#            transcript, but raw STATS email reported 53.
# Runs 9-10: steps_used field introduced in v2.8.3
#
# True cumulative = sum of all removed_this_run = 329 (raw STATS)
# Reported cumulative at Run 10 = 231
# Gap = 98 = the amount lost when Run 4 reset to 0 instead of carrying 98
# ---------------------------------------------------------------------------

INBOX_BASELINE = 874

FIXTURE_LINES = [
    # Run 1
    "INBOXTRIAGE | 2026-03-26 | start_time: 09:02 | end_time: 09:44 | run_time_min: 42 | kill_time_reached: no | step_kill_reached: no | new_unread_since_last_run: 87 | total_processed: 30 | removed_this_run: 28 | cumulative_deleted: 28 | net_cleared: 28 | drafted_replies: 2",
    # Run 2
    "INBOXTRIAGE | 2026-03-27 | start_time: 09:01 | end_time: 09:38 | run_time_min: 37 | kill_time_reached: no | step_kill_reached: no | new_unread_since_last_run: 12 | total_processed: 38 | removed_this_run: 35 | cumulative_deleted: 63 | net_cleared: 63 | drafted_replies: 1",
    # Run 3
    "INBOXTRIAGE | 2026-03-27 | start_time: 14:10 | end_time: 15:05 | run_time_min: 55 | kill_time_reached: no | step_kill_reached: no | new_unread_since_last_run: 8 | total_processed: 67 | removed_this_run: 35 | cumulative_deleted: 98 | net_cleared: 98 | drafted_replies: 0",
    # Run 4 — silent reset: cumulative_removed=42 instead of 140 (98+42)
    "INBOXTRIAGE | 2026-03-28 | start_time: 09:05 | end_time: 09:47 | run_time_min: 42 | kill_time_reached: no | step_kill_reached: no | new_unread_since_last_run: 15 | total_processed: 29 | removed_this_run: 42 | cumulative_removed: 42 | net_cleared: 140 | drafted_replies: 1",
    # Run 5 — kill_time_reached
    "INBOXTRIAGE | 2026-03-29 | start_time: 09:03 | end_time: 10:03 | run_time_min: 60 | kill_time_reached: yes | step_kill_reached: no | new_unread_since_last_run: 22 | total_processed: 40 | removed_this_run: 48 | cumulative_removed: 90 | net_cleared: 188 | drafted_replies: 0",
    # Run 6 — read_audited=0 counter-init bug; total_processed still valid
    "INBOXTRIAGE | 2026-03-30 | start_time: 09:01 | end_time: 09:55 | run_time_min: 54 | kill_time_reached: no | step_kill_reached: no | new_unread_since_last_run: 19 | total_processed: 50 | removed_this_run: 50 | cumulative_removed: 140 | net_cleared: 238 | drafted_replies: 2",
    # Run 7 — step kill; raw STATS removed=53 (=total_processed); audit found true removed=146
    "INBOXTRIAGE | 2026-03-31 | start_time: 09:00 | end_time: 10:00 | run_time_min: 60 | kill_time_reached: yes | step_kill_reached: yes | new_unread_since_last_run: 31 | total_processed: 53 | removed_this_run: 53 | cumulative_removed: 193 | net_cleared: 291 | drafted_replies: 1",
    # Run 8
    "INBOXTRIAGE | 2026-04-01 | start_time: 09:04 | end_time: 09:51 | run_time_min: 47 | kill_time_reached: no | step_kill_reached: no | new_unread_since_last_run: 14 | total_processed: 32 | removed_this_run: 28 | cumulative_removed: 221 | net_cleared: 319 | drafted_replies: 0",
    # Run 9 (partial) — steps_used introduced in v2.8.3; 82 steps / 18 emails = 4.6/email
    "INBOXTRIAGE | 2026-04-03 | start_time: 09:02 | end_time: 09:29 | run_time_min: 27 | kill_time_reached: no | step_kill_reached: no | new_unread_since_last_run: 9 | total_processed: 18 | removed_this_run: 6 | cumulative_removed: 227 | net_cleared: 325 | drafted_replies: 0 | steps_used: 82",
    # Run 10 — step kill hit again; 67 steps / 44 emails = 1.5/email (efficient run)
    "INBOXTRIAGE | 2026-04-06 | start_time: 09:01 | end_time: 09:58 | run_time_min: 57 | kill_time_reached: no | step_kill_reached: yes | new_unread_since_last_run: 24 | total_processed: 44 | removed_this_run: 4 | cumulative_removed: 231 | net_cleared: 329 | drafted_replies: 1 | steps_used: 67",
]

# True cumulative = 28+35+35+42+48+50+53+28+6+4 = 329
# Reported at Run 10                              = 231
# Gap                                             =  98  (the Run 4 reset loss)
TRUE_CUMULATIVE = 329
REPORTED_CUMULATIVE_AT_RUN_10 = 231
RESET_LOSS = TRUE_CUMULATIVE - REPORTED_CUMULATIVE_AT_RUN_10  # = 98


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestParseStatsLine(unittest.TestCase):

    def _run1(self):
        return parse_stats_line(FIXTURE_LINES[0])

    def test_agent_and_date_parsed(self):
        r = self._run1()
        self.assertEqual(r["agent"], "INBOXTRIAGE")
        self.assertEqual(r["date"], "2026-03-26")

    def test_integer_fields_present(self):
        r = self._run1()
        self.assertEqual(r["run_time_min"], "42")
        self.assertEqual(r["total_processed"], "30")
        self.assertEqual(r["removed_this_run"], "28")

    def test_field_name_normalization_cumulative_deleted(self):
        r = self._run1()
        self.assertIn("cumulative_removed", r)
        self.assertNotIn("cumulative_deleted", r)
        self.assertEqual(r["cumulative_removed"], "28")

    def test_new_field_steps_used_parsed(self):
        r = parse_stats_line(FIXTURE_LINES[8])  # Run 9
        self.assertIn("steps_used", r)
        self.assertEqual(r["steps_used"], "82")

    def test_missing_steps_used_absent_in_old_runs(self):
        r = self._run1()
        self.assertNotIn("steps_used", r)

    def test_malformed_line_raises(self):
        with self.assertRaises(ValueError):
            parse_stats_line("not a stats line")

    def test_unknown_agent_raises(self):
        with self.assertRaises(ValueError):
            parse_stats_line("WEEKPLAN | 2026-03-26 | run_time_min: 10")

    def test_weekbrief_line_parsed(self):
        line = "WEEKBRIEF | 2026-03-28 | start_time: 08:05 | end_time: 08:47 | run_time_min: 42 | new_assignments: 6 | carried_assignments: 2 | ai_assisted: 3 | hours_offloaded: 4 | time_saved_min: 240"
        r = parse_stats_line(line)
        self.assertEqual(r["agent"], "WEEKBRIEF")
        self.assertEqual(r["new_assignments"], "6")


class TestValidateRecord(unittest.TestCase):

    def _make(self, **kwargs) -> dict:
        base = {"run_time_min": "45", "total_processed": "30", "removed_this_run": "20"}
        base.update({k: str(v) for k, v in kwargs.items()})
        return base

    def test_clean_record_no_errors(self):
        self.assertEqual(validate_record(self._make()), [])

    def test_run_time_zero_flagged(self):
        errors = validate_record(self._make(run_time_min=0))
        self.assertTrue(any("run_time_min" in e for e in errors))

    def test_run_time_over_120_flagged(self):
        errors = validate_record(self._make(run_time_min=125))
        self.assertTrue(any("run_time_min" in e for e in errors))

    def test_run_time_at_boundary_ok(self):
        self.assertEqual(validate_record(self._make(run_time_min=120)), [])
        self.assertEqual(validate_record(self._make(run_time_min=1)), [])

    def test_removed_exceeds_processed_flagged(self):
        errors = validate_record(self._make(total_processed=30, removed_this_run=31))
        self.assertTrue(any("removed_this_run" in e for e in errors))

    def test_removed_equals_processed_ok(self):
        self.assertEqual(validate_record(self._make(total_processed=30, removed_this_run=30)), [])

    def test_zero_total_processed_skips_removed_check(self):
        # A run with nothing processed shouldn't flag removed=0 as a violation
        self.assertEqual(validate_record(self._make(total_processed=0, removed_this_run=0)), [])


class TestCumulativeChain(unittest.TestCase):

    def setUp(self):
        self.records = [parse_stats_line(line) for line in FIXTURE_LINES]

    def test_reset_detected_at_run_4(self):
        events = validate_cumulative_chain(self.records)
        reset_runs = [e["run"] for e in events if e["type"] == "cumulative_reset"]
        self.assertIn(4, reset_runs, "Expected cumulative reset detected at Run 4")

    def test_exactly_one_reset_in_fixture(self):
        events = validate_cumulative_chain(self.records)
        self.assertEqual(len(events), 1)

    def test_reset_event_has_expected_values(self):
        events = validate_cumulative_chain(self.records)
        event = events[0]
        self.assertEqual(event["prior"], 98)   # cumulative_deleted from Run 3
        self.assertEqual(event["reported"], 42)  # cumulative_removed reset value

    def test_corrected_cumulative_equals_sum_of_removed(self):
        total = corrected_cumulative(self.records)
        self.assertEqual(total, TRUE_CUMULATIVE)

    def test_reported_underestimates_true(self):
        # The reported cumulative at Run 10 is less than the true sum
        reported = int_field(self.records[-1], "cumulative_removed")
        true_total = corrected_cumulative(self.records)
        self.assertLess(reported, true_total)
        self.assertEqual(true_total - reported, RESET_LOSS)

    def test_monotonic_chain_no_events(self):
        clean = [
            parse_stats_line("INBOXTRIAGE | 2026-04-10 | run_time_min: 40 | total_processed: 20 | removed_this_run: 10 | cumulative_removed: 10 | net_cleared: 10 | drafted_replies: 0"),
            parse_stats_line("INBOXTRIAGE | 2026-04-11 | run_time_min: 40 | total_processed: 20 | removed_this_run: 15 | cumulative_removed: 25 | net_cleared: 25 | drafted_replies: 0"),
            parse_stats_line("INBOXTRIAGE | 2026-04-12 | run_time_min: 40 | total_processed: 20 | removed_this_run: 5 | cumulative_removed: 30 | net_cleared: 30 | drafted_replies: 0"),
        ]
        self.assertEqual(validate_cumulative_chain(clean), [])


class TestDerivedMetrics(unittest.TestCase):

    def test_net_cleared_positive(self):
        self.assertEqual(compute_net_cleared(874, 452), 422)

    def test_net_cleared_zero(self):
        self.assertEqual(compute_net_cleared(874, 874), 0)

    def test_net_cleared_negative_when_inbox_grew(self):
        # More emails than the baseline — inbox grew
        self.assertEqual(compute_net_cleared(874, 900), -26)

    def test_steps_per_email_computed_when_present(self):
        r = parse_stats_line(FIXTURE_LINES[8])  # Run 9: 82 steps / 18 emails
        ratio = compute_steps_per_email(r)
        self.assertIsNotNone(ratio)
        self.assertAlmostEqual(ratio, 4.56, places=1)

    def test_steps_per_email_none_when_absent(self):
        r = parse_stats_line(FIXTURE_LINES[0])  # Run 1: no steps_used field
        self.assertIsNone(compute_steps_per_email(r))

    def test_steps_per_email_efficiency_threshold(self):
        # Target: <= 4 steps/email. Run 9 (4.6) is borderline; Run 10 (1.5) is efficient.
        run9 = parse_stats_line(FIXTURE_LINES[8])
        run10 = parse_stats_line(FIXTURE_LINES[9])
        self.assertGreater(compute_steps_per_email(run9), 4.0)   # borderline — worth flagging
        self.assertLessEqual(compute_steps_per_email(run10), 4.0)  # efficient

    def test_steps_per_email_zero_processed_returns_none(self):
        r = {"steps_used": "50", "total_processed": "0"}
        self.assertIsNone(compute_steps_per_email(r))


if __name__ == "__main__":
    unittest.main(verbosity=2)
