"""Tests for tools.lib.skills_scanner local SKILL.md inventory parsing."""

from __future__ import annotations

import os
from datetime import UTC, date, datetime
from pathlib import Path

from tools.lib.skills_scanner import (
    STATUS_CHECK_FAILED,
    STATUS_CURRENT_LOCAL,
    STATUS_STALE,
    SkillRecord,
    exit_code_for_records,
    has_data_source_errors,
    scan_skills,
    staleness_baseline,
    triggers_hint,
)


def _write_skill(skills_root: Path, skill_id: str, frontmatter: str) -> Path:
    path = skills_root / skill_id / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n# Body\n", encoding="utf-8")
    return path


def _write_raw_skill(skills_root: Path, skill_id: str, content: str) -> Path:
    path = skills_root / skill_id / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _set_mtime(path: Path, day: date) -> None:
    timestamp = datetime.combine(day, datetime.min.time(), tzinfo=UTC).timestamp()
    os.utime(path, (timestamp, timestamp))


class TestScanSkills:
    def test_empty_dir(self, tmp_path: Path) -> None:
        skills_root = tmp_path / ".claude" / "skills"
        skills_root.mkdir(parents=True)
        assert scan_skills(skills_root) == []

    def test_valid_skills(self, tmp_path: Path) -> None:
        skills_root = tmp_path / ".claude" / "skills"
        _write_skill(
            skills_root,
            "beta",
            "name: Beta Skill\n"
            "version: 2.0.0\n"
            "description: Second skill\n"
            "triggers: beta, second\n"
            "installed-at: 2026-04-20\n",
        )
        _write_skill(
            skills_root,
            "alpha",
            "name: Alpha Skill\n"
            "version: 1.0.0\n"
            "description: First skill\n"
            "triggers:\n"
            "  - start\n"
            "  - begin\n"
            "installed-at: 2026-04-21\n",
        )

        records = scan_skills(skills_root, today=date(2026, 4, 24))

        assert [record.id for record in records] == ["alpha", "beta"]
        alpha = records[0]
        assert isinstance(alpha, SkillRecord)
        assert alpha.name == "Alpha Skill"
        assert alpha.version == "1.0.0"
        assert alpha.description == "First skill"
        assert alpha.triggers == ("start", "begin")
        assert alpha.installed_at == "2026-04-21"
        assert alpha.source == "skills://alpha"
        assert alpha.status == STATUS_CURRENT_LOCAL
        assert alpha.error is None
        assert not alpha.data_source_error

    def test_missing_fields_and_local_only(self, tmp_path: Path) -> None:
        skills_root = tmp_path / ".claude" / "skills"
        path = _write_skill(
            skills_root,
            "scratchpad",
            "source: local://scratchpad\n"
            "triggers: [note, scratch, jot]\n",
        )
        _set_mtime(path, date(2026, 4, 23))

        records = scan_skills(skills_root, today=date(2026, 4, 24))

        assert len(records) == 1
        record = records[0]
        assert record.id == "scratchpad"
        assert record.name == "scratchpad"
        assert record.version == "local"
        assert record.source == "local://scratchpad"
        assert record.installed_at == "2026-04-23"
        assert record.baseline_source == "mtime"
        assert record.triggers_hint == "note, scratch, jot"
        assert record.status == STATUS_CURRENT_LOCAL
        assert not record.data_source_error

    def test_corrupt_frontmatter_does_not_stop_scan(self, tmp_path: Path) -> None:
        skills_root = tmp_path / ".claude" / "skills"
        _write_raw_skill(
            skills_root,
            "broken",
            "---\nname: : :\nversion: 1.0.0\n---\n# Broken\n",
        )
        _write_skill(
            skills_root,
            "good",
            "name: Good Skill\n"
            "version: 1.0.0\n"
            "installed-at: 2026-04-22\n",
        )

        records = scan_skills(skills_root, today=date(2026, 4, 24))

        assert [record.id for record in records] == ["broken", "good"]
        broken = records[0]
        assert broken.status == STATUS_CHECK_FAILED
        assert broken.data_source_error
        assert broken.error is not None
        assert records[1].status == STATUS_CURRENT_LOCAL
        assert has_data_source_errors(records)
        assert exit_code_for_records(records) == 3

    def test_mtime_fallback_triggers_hint_and_stale_status(self, tmp_path: Path) -> None:
        skills_root = tmp_path / ".claude" / "skills"
        path = _write_skill(
            skills_root,
            "old-capture",
            "name: Old Capture\n"
            "version: 0.9.0\n"
            "triggers:\n"
            "  - capture\n"
            "  - inbox\n"
            "  - clip\n"
            "  - archive\n",
        )
        _set_mtime(path, date(2026, 1, 1))

        records = scan_skills(skills_root, today=date(2026, 4, 24))

        record = records[0]
        assert record.installed_at == "2026-01-01"
        assert record.baseline_source == "mtime"
        assert record.baseline_at == staleness_baseline(None, record.mtime)
        assert record.triggers_hint == "capture, inbox, clip"
        assert triggers_hint(record.triggers) == "capture, inbox, clip"
        assert record.status == STATUS_STALE
        assert exit_code_for_records(records) == 2
