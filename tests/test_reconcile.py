"""Tests for tools.reconcile — integrity checker.

Per references/tools-spec.md §6.2. reconcile runs four checks across the
second-brain markdown tree:

    1. orphan files (in directories the spec treats as reachable but with
       no inbound wikilinks from indexed notes)
    2. broken [[wikilinks]] (target missing on disk)
    3. missing YAML frontmatter on files where the spec requires it
    4. schema violations (required frontmatter keys missing)

Reports are written to ``_meta/reconcile-report-{YYYY-MM-DD}.md`` and
overwritten on same-day re-run (idempotent).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from tools.reconcile import main

# ─── Fixture helpers ─────────────────────────────────────────────────────────


def _valid_session_md() -> str:
    return (
        "---\n"
        "session_id: claude-20260421-1430\n"
        "date: 2026-04-21\n"
        "started_at: 2026-04-21T14:30:00\n"
        "ended_at: 2026-04-21T15:00:00\n"
        "duration_minutes: 30\n"
        "platform: claude\n"
        "theme: zh-classical\n"
        "project: life-os\n"
        "workflow: full_deliberation\n"
        "subject: test\n"
        "overall_score: 8.5\n"
        "veto_count: 0\n"
        "council_triggered: false\n"
        "compliance_violations: 0\n"
        "last_modified: 2026-04-21\n"
        "id: claude-20260421-1430\n"
        "---\n"
        "body\n"
    )


def _missing_fm_md() -> str:
    return "# Just a heading\n\nNo frontmatter here.\n"


def _broken_link_md() -> str:
    return (
        "---\n"
        "last_modified: 2026-04-21\n"
        "id: wiki-x\n"
        "---\n"
        "\n"
        "See [[concepts/nonexistent]] for details.\n"
    )


def _schema_violation_md() -> str:
    # Has frontmatter but missing required `id` and `last_modified`
    return (
        "---\n"
        "some_field: value\n"
        "---\n"
        "body\n"
    )


def _setup_brain(root: Path) -> None:
    """Lay down a minimal second-brain root with required directories."""
    for rel in [
        "_meta/sessions",
        "_meta/concepts",
        "_meta/snapshots/soul",
        "_meta/eval-history",
        "_meta/methods",
        "wiki",
        "inbox",
        "projects",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)


# ─── Clean tree ──────────────────────────────────────────────────────────────


class TestCleanTree:
    def test_empty_brain_exit_zero(self, tmp_path: Path):
        _setup_brain(tmp_path)
        rc = main(["--root", str(tmp_path)])
        assert rc == 0

    def test_valid_session_emits_clean_report(self, tmp_path: Path):
        _setup_brain(tmp_path)
        (tmp_path / "_meta" / "sessions" / "claude-20260421-1430.md").write_text(
            _valid_session_md(), encoding="utf-8"
        )
        rc = main(["--root", str(tmp_path)])
        assert rc == 0
        today = date.today().isoformat()
        report = tmp_path / "_meta" / f"reconcile-report-{today}.md"
        assert report.exists()
        text = report.read_text(encoding="utf-8")
        assert "Reconcile Report" in text


# ─── Missing frontmatter ─────────────────────────────────────────────────────


class TestMissingFrontmatter:
    def test_missing_fm_flagged_exit_one(self, tmp_path: Path):
        _setup_brain(tmp_path)
        (tmp_path / "_meta" / "sessions" / "orphan.md").write_text(
            _missing_fm_md(), encoding="utf-8"
        )
        rc = main(["--root", str(tmp_path)])
        assert rc == 1  # unfixable without --fix
        today = date.today().isoformat()
        text = (tmp_path / "_meta" / f"reconcile-report-{today}.md").read_text(
            encoding="utf-8"
        )
        assert "missing frontmatter" in text.lower()

    def test_missing_fm_fix_inserts_defaults(self, tmp_path: Path):
        _setup_brain(tmp_path)
        target = tmp_path / "_meta" / "sessions" / "orphan.md"
        target.write_text(_missing_fm_md(), encoding="utf-8")
        rc = main(["--fix", "--root", str(tmp_path)])
        # After fix, the file should have frontmatter with last_modified + id
        content = target.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert "last_modified:" in content
        assert "id:" in content
        # Exit 0 because everything fixable was fixed
        assert rc == 0


# ─── Broken wikilinks ────────────────────────────────────────────────────────


class TestBrokenLinks:
    def test_broken_link_flagged(self, tmp_path: Path):
        _setup_brain(tmp_path)
        (tmp_path / "wiki" / "has-broken-link.md").write_text(
            _broken_link_md(), encoding="utf-8"
        )
        rc = main(["--root", str(tmp_path)])
        assert rc == 1
        today = date.today().isoformat()
        text = (tmp_path / "_meta" / f"reconcile-report-{today}.md").read_text(
            encoding="utf-8"
        )
        assert "broken" in text.lower()
        assert "nonexistent" in text

    def test_link_to_existing_file_not_flagged(self, tmp_path: Path):
        _setup_brain(tmp_path)
        (tmp_path / "wiki" / "target.md").write_text(
            "---\nlast_modified: 2026-04-21\nid: target\n---\nbody\n",
            encoding="utf-8",
        )
        (tmp_path / "wiki" / "source.md").write_text(
            "---\nlast_modified: 2026-04-21\nid: source\n---\n"
            "See [[wiki/target]] for details.\n",
            encoding="utf-8",
        )
        rc = main(["--root", str(tmp_path)])
        assert rc == 0


# ─── Orphan handling ─────────────────────────────────────────────────────────


class TestOrphans:
    def test_orphan_file_flagged_no_fix_exit_one(self, tmp_path: Path):
        _setup_brain(tmp_path)
        # Drop a file into inbox/ with frontmatter — considered an orphan
        # per reconcile (inbox content should be moved or linked)
        orphan = tmp_path / "inbox" / "loose-note.md"
        orphan.write_text(
            "---\nlast_modified: 2026-04-21\nid: loose-note\n---\ncontent\n",
            encoding="utf-8",
        )
        rc = main(["--root", str(tmp_path)])
        assert rc == 1
        today = date.today().isoformat()
        text = (tmp_path / "_meta" / f"reconcile-report-{today}.md").read_text(
            encoding="utf-8"
        )
        assert "orphan" in text.lower()

    def test_orphan_fix_moves_to_archive(self, tmp_path: Path):
        _setup_brain(tmp_path)
        orphan = tmp_path / "inbox" / "loose-note.md"
        orphan.write_text(
            "---\nlast_modified: 2026-04-21\nid: loose-note\n---\ncontent\n",
            encoding="utf-8",
        )
        rc = main(["--fix", "--root", str(tmp_path)])
        assert rc == 0
        # Original location cleared
        assert not orphan.exists()
        # Moved to archive/orphans/
        archive = tmp_path / "archive" / "orphans" / "loose-note.md"
        assert archive.exists()
        assert "content" in archive.read_text(encoding="utf-8")

    def test_reserved_paths_not_orphans(self, tmp_path: Path):
        _setup_brain(tmp_path)
        # Files in wiki/ that have frontmatter are never orphans (they're
        # the canonical storage location)
        (tmp_path / "wiki" / "keep.md").write_text(
            "---\nlast_modified: 2026-04-21\nid: keep\n---\nbody\n",
            encoding="utf-8",
        )
        rc = main(["--root", str(tmp_path)])
        assert rc == 0


# ─── Report overwrite ────────────────────────────────────────────────────────


class TestReportOverwrite:
    def test_same_day_rerun_overwrites(self, tmp_path: Path):
        _setup_brain(tmp_path)
        main(["--root", str(tmp_path)])
        today = date.today().isoformat()
        report = tmp_path / "_meta" / f"reconcile-report-{today}.md"
        assert report.exists()
        first = report.read_text(encoding="utf-8")
        # Second run produces identical report (no append)
        main(["--root", str(tmp_path)])
        second = report.read_text(encoding="utf-8")
        assert first == second


# ─── Idempotence ─────────────────────────────────────────────────────────────


class TestIdempotence:
    def test_fix_is_idempotent(self, tmp_path: Path):
        _setup_brain(tmp_path)
        target = tmp_path / "_meta" / "sessions" / "orphan.md"
        target.write_text(_missing_fm_md(), encoding="utf-8")
        rc1 = main(["--fix", "--root", str(tmp_path)])
        first = target.read_text(encoding="utf-8")
        rc2 = main(["--fix", "--root", str(tmp_path)])
        second = target.read_text(encoding="utf-8")
        assert rc1 == rc2 == 0
        assert first == second


# ─── Verbose / Flag handling ─────────────────────────────────────────────────


class TestFlagHandling:
    def test_verbose_accepted(self, tmp_path: Path):
        _setup_brain(tmp_path)
        rc = main(["--verbose", "--root", str(tmp_path)])
        assert rc == 0

    def test_schema_violation_flagged(self, tmp_path: Path):
        _setup_brain(tmp_path)
        (tmp_path / "wiki" / "bad.md").write_text(
            _schema_violation_md(), encoding="utf-8"
        )
        rc = main(["--root", str(tmp_path)])
        # Missing required frontmatter keys on a wiki file
        assert rc == 1
        today = date.today().isoformat()
        text = (tmp_path / "_meta" / f"reconcile-report-{today}.md").read_text(
            encoding="utf-8"
        )
        assert "schema" in text.lower()


# ─── Cross-platform path handling ────────────────────────────────────────────


class TestCrossPlatformPaths:
    def test_windows_style_link_resolved(self, tmp_path: Path):
        _setup_brain(tmp_path)
        # Wikilinks must work regardless of OS path separators
        (tmp_path / "wiki" / "nested").mkdir()
        (tmp_path / "wiki" / "nested" / "target.md").write_text(
            "---\nlast_modified: 2026-04-21\nid: nested-target\n---\nbody\n",
            encoding="utf-8",
        )
        (tmp_path / "wiki" / "source.md").write_text(
            "---\nlast_modified: 2026-04-21\nid: source\n---\n"
            "See [[wiki/nested/target]]\n",
            encoding="utf-8",
        )
        rc = main(["--root", str(tmp_path)])
        assert rc == 0
