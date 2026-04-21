"""Tests for tools.backup — snapshot rotation + violations archival."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tools.backup import (
    _quarter_for,
    resolve_violations_paths,
    rotate_snapshots,
    rotate_violations,
)
from tools.lib.cortex.snapshot import write_snapshot
from tools.lib.second_brain import SnapshotDimension, SoulSnapshot


def _make_snapshot(
    snapshot_id: str,
    captured_at: datetime,
) -> SoulSnapshot:
    return SoulSnapshot(
        snapshot_id=snapshot_id,
        captured_at=captured_at,
        session_id="test-session",
        previous_snapshot=None,
        dimensions=[SnapshotDimension("autonomy", 0.85, 5, 1, "core")],
    )


# ─── _quarter_for ────────────────────────────────────────────────────────────


class TestQuarterFor:
    @pytest.mark.parametrize(
        "month,expected_q",
        [(1, 1), (2, 1), (3, 1), (4, 2), (6, 2), (7, 3), (9, 3), (10, 4), (12, 4)],
    )
    def test_month_to_quarter(self, month: int, expected_q: int):
        result = _quarter_for(datetime(2026, month, 15))
        assert result == f"2026-Q{expected_q}"


# ─── rotate_snapshots ───────────────────────────────────────────────────────


class TestRotateSnapshots:
    def test_recent_snapshots_untouched(self, tmp_path: Path):
        recent = _make_snapshot("2026-04-21-1430", datetime.now() - timedelta(days=2))
        write_snapshot(recent, tmp_path)
        archived, deleted = rotate_snapshots(tmp_path)
        assert archived == []
        assert deleted == []
        assert (tmp_path / "2026-04-21-1430.md").exists()

    def test_30d_to_90d_archived(self, tmp_path: Path):
        old = _make_snapshot("2026-03-15-0000", datetime.now() - timedelta(days=35))
        path = write_snapshot(old, tmp_path)
        archived, deleted = rotate_snapshots(tmp_path)
        assert len(archived) == 1
        assert deleted == []
        # File moved to _archive
        assert not path.exists()
        assert (tmp_path / "_archive" / "2026-03-15-0000.md").exists()

    def test_over_90d_deleted(self, tmp_path: Path):
        very_old = _make_snapshot(
            "2026-01-12-0000", datetime.now() - timedelta(days=100)
        )
        path = write_snapshot(very_old, tmp_path)
        archived, deleted = rotate_snapshots(tmp_path)
        assert len(deleted) == 1
        assert not path.exists()

    def test_dry_run_no_changes(self, tmp_path: Path):
        old = _make_snapshot("2026-03-15-0000", datetime.now() - timedelta(days=35))
        path = write_snapshot(old, tmp_path)
        archived, deleted = rotate_snapshots(tmp_path, dry_run=True)
        assert len(archived) == 1
        assert path.exists()  # Not actually moved
        assert not (tmp_path / "_archive" / "2026-03-15-0000.md").exists()


# ─── rotate_violations ──────────────────────────────────────────────────────


class TestRotateViolations:
    def test_no_archival_when_all_recent(self, tmp_path: Path):
        v_path = tmp_path / "violations.md"
        recent_dt = (datetime.now().astimezone() - timedelta(days=10)).isoformat()
        v_path.write_text(
            f"| {recent_dt} | trigger | A1 | P0 | recent | false |\n",
            encoding="utf-8",
        )
        result = rotate_violations(v_path, tmp_path / "archive")
        assert result["archived_count"] == 0
        assert result["active_remaining"] == 1

    def test_old_rows_archived(self, tmp_path: Path):
        v_path = tmp_path / "violations.md"
        archive_root = tmp_path / "archive"
        old_dt = (datetime.now().astimezone() - timedelta(days=100)).isoformat()
        recent_dt = (datetime.now().astimezone() - timedelta(days=10)).isoformat()
        v_path.write_text(
            f"| {old_dt} | trigger | A1 | P0 | old | true |\n"
            f"| {recent_dt} | trigger | B | P0 | new | false |\n",
            encoding="utf-8",
        )
        result = rotate_violations(v_path, archive_root)
        assert result["archived_count"] == 1
        assert result["active_remaining"] == 1
        assert len(result["archive_files"]) == 1

    def test_dry_run_no_changes(self, tmp_path: Path):
        v_path = tmp_path / "violations.md"
        archive_root = tmp_path / "archive"
        old_dt = (datetime.now().astimezone() - timedelta(days=100)).isoformat()
        original_content = f"| {old_dt} | trigger | A1 | P0 | old | true |\n"
        v_path.write_text(original_content, encoding="utf-8")
        result = rotate_violations(v_path, archive_root, dry_run=True)
        assert result["archived_count"] == 1
        # File not modified
        assert v_path.read_text() == original_content
        # Archive not created
        assert not archive_root.exists()


# ─── resolve_violations_paths ───────────────────────────────────────────────


class TestResolvePaths:
    def test_dev_repo(self, tmp_path: Path):
        (tmp_path / "pro" / "compliance").mkdir(parents=True)
        v = tmp_path / "pro" / "compliance" / "violations.md"
        v.write_text("# log\n", encoding="utf-8")
        v_path, a_path = resolve_violations_paths(tmp_path)
        assert v_path == v
        assert a_path == tmp_path / "pro" / "compliance" / "archive"

    def test_user_repo(self, tmp_path: Path):
        (tmp_path / "_meta" / "compliance").mkdir(parents=True)
        v = tmp_path / "_meta" / "compliance" / "violations.md"
        v.write_text("# log\n", encoding="utf-8")
        v_path, a_path = resolve_violations_paths(tmp_path)
        assert v_path == v

    def test_neither(self, tmp_path: Path):
        v_path, a_path = resolve_violations_paths(tmp_path)
        assert v_path is None
        assert a_path is None
