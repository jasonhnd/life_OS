"""Tests for tools.stats — compliance violation parser + escalation ladder."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.stats import (
    _parse_iso_timestamp,
    compute_escalations,
    parse_violations,
    resolve_violations_path,
)


# ─── parse_violations ───────────────────────────────────────────────────────


class TestParseViolations:
    def test_empty_file(self, tmp_path: Path):
        path = tmp_path / "violations.md"
        path.write_text("# Empty\n", encoding="utf-8")
        rows = parse_violations(path)
        assert rows == []

    def test_skips_header_and_separator(self, tmp_path: Path):
        path = tmp_path / "violations.md"
        path.write_text(
            "| Timestamp | Trigger | Type | Severity | Details | Resolved |\n"
            "|-----------|---------|------|----------|---------|----------|\n"
            "| 2026-04-19T22:47+09:00 | 上朝 | A1 | P0 | Real violation | partial |\n",
            encoding="utf-8",
        )
        rows = parse_violations(path)
        assert len(rows) == 1
        assert rows[0]["type"] == "A1"
        assert rows[0]["resolved"] == "partial"

    def test_skips_code_block_examples(self, tmp_path: Path):
        path = tmp_path / "violations.md"
        path.write_text(
            "```\n"
            "| Timestamp | Trigger | Type | Severity | Details | Resolved |\n"
            "```\n"
            "## Violations\n\n"
            "| 2026-04-19T22:47+09:00 | 上朝 | A1 | P0 | Real | partial |\n",
            encoding="utf-8",
        )
        rows = parse_violations(path)
        assert len(rows) == 1
        assert rows[0]["type"] == "A1"

    def test_rejects_long_type_field(self, tmp_path: Path):
        # A row whose "type" column contains a long word — likely format example
        path = tmp_path / "violations.md"
        path.write_text(
            "| 2026-04-19T22:47+09:00 | 上朝 | This is too long | P0 | x | false |\n",
            encoding="utf-8",
        )
        rows = parse_violations(path)
        assert rows == []

    def test_real_violation_parsed(self, tmp_path: Path):
        path = tmp_path / "violations.md"
        path.write_text(
            "| 2026-04-19T22:47+09:00 | 上朝 | A1 | P0 | sim violation | partial (v1.6.3) |\n"
            "| 2026-04-21T13:42+09:00 | 上朝 | F | P2 | paste hook fire | true |\n",
            encoding="utf-8",
        )
        rows = parse_violations(path)
        assert len(rows) == 2
        assert rows[0]["parsed_dt"] is not None
        assert rows[1]["type"] == "F"


# ─── _parse_iso_timestamp ───────────────────────────────────────────────────


class TestParseTimestamp:
    def test_iso_with_offset(self):
        dt = _parse_iso_timestamp("2026-04-19T22:47+09:00")
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 4
        assert dt.day == 19

    def test_invalid_returns_none(self):
        assert _parse_iso_timestamp("not a date") is None


# ─── compute_escalations ────────────────────────────────────────────────────


def _row(type_code: str, days_ago: int, resolved: str = "false") -> dict:
    """Construct a violation row dict for tests."""
    dt = datetime.now().astimezone() - timedelta(days=days_ago)
    return {
        "timestamp": dt.isoformat(),
        "trigger": "test",
        "type": type_code,
        "severity": "P0",
        "details": "test",
        "resolved": resolved,
        "parsed_dt": dt,
    }


class TestComputeEscalations:
    def test_empty(self):
        result = compute_escalations([])
        assert result["unresolved_count"] == 0
        assert result["by_type_lifetime"] == {}
        assert result["escalations_active"] == []

    def test_lifetime_count(self):
        rows = [_row("A1", 5), _row("A1", 10), _row("B", 15)]
        result = compute_escalations(rows)
        assert result["by_type_lifetime"] == {"A1": 2, "B": 1}

    def test_30d_window(self):
        rows = [
            _row("A1", 5),
            _row("A1", 25),
            _row("A1", 60),  # outside 30d
        ]
        result = compute_escalations(rows)
        assert result["active_30d"]["A1"] == 2
        assert result["active_90d"]["A1"] == 3

    def test_unresolved_count(self):
        rows = [
            _row("A1", 5, resolved="false"),
            _row("A1", 10, resolved="partial"),
            _row("B", 15, resolved="true"),
        ]
        result = compute_escalations(rows)
        assert result["unresolved_count"] == 2

    def test_threshold_3_in_30d_triggers_escalation(self):
        rows = [_row("A1", 1), _row("A1", 5), _row("A1", 10)]
        result = compute_escalations(rows)
        active = [e for e in result["escalations_active"] if e["type"] == "A1"]
        assert len(active) >= 1
        # The first threshold (>=3 in 30d) should be triggered
        assert any(e["threshold_count"] == 3 for e in active)

    def test_threshold_5_in_30d_triggers_briefing_warning(self):
        rows = [_row("B", i) for i in range(1, 6)]
        result = compute_escalations(rows)
        active = [e for e in result["escalations_active"] if e["type"] == "B"]
        # Both >=3 AND >=5 thresholds should fire
        thresholds = {e["threshold_count"] for e in active}
        assert 3 in thresholds
        assert 5 in thresholds

    def test_no_escalation_when_below_threshold(self):
        rows = [_row("A1", 5), _row("A1", 10)]  # only 2
        result = compute_escalations(rows)
        assert result["escalations_active"] == []


# ─── resolve_violations_path ────────────────────────────────────────────────


class TestResolveViolationsPath:
    def test_dev_repo(self, tmp_path: Path):
        (tmp_path / "pro" / "compliance").mkdir(parents=True)
        target = tmp_path / "pro" / "compliance" / "violations.md"
        target.write_text("# log\n", encoding="utf-8")
        assert resolve_violations_path(tmp_path) == target

    def test_user_repo(self, tmp_path: Path):
        (tmp_path / "_meta" / "compliance").mkdir(parents=True)
        target = tmp_path / "_meta" / "compliance" / "violations.md"
        target.write_text("# log\n", encoding="utf-8")
        assert resolve_violations_path(tmp_path) == target

    def test_dev_takes_precedence(self, tmp_path: Path):
        (tmp_path / "pro" / "compliance").mkdir(parents=True)
        (tmp_path / "_meta" / "compliance").mkdir(parents=True)
        dev = tmp_path / "pro" / "compliance" / "violations.md"
        user = tmp_path / "_meta" / "compliance" / "violations.md"
        dev.write_text("dev\n", encoding="utf-8")
        user.write_text("user\n", encoding="utf-8")
        assert resolve_violations_path(tmp_path) == dev

    def test_neither_returns_none(self, tmp_path: Path):
        assert resolve_violations_path(tmp_path) is None
