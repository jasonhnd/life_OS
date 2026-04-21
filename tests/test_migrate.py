"""Tests for tools.migrate — v1.6.2a to v1.7 one-shot schema migration.

Per references/tools-spec.md §6.7 + the four downstream spec sections:
- references/session-index-spec.md §9   (session backfill)
- references/concept-spec.md §Migration  (concept backfill)
- references/snapshot-spec.md §Migration (SOUL delta synth)
- references/method-library-spec.md §15  (method candidates)

Also pins the no-backfill invariant from eval-history-spec.md §11.

These tests exercise the CLI surface (flags, exit codes, dry-run) and
the per-target migration rules (filename conventions, activation counts,
3-month window, idempotence).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import yaml

from tools.migrate import main

# ─── Fixture helpers ─────────────────────────────────────────────────────────


def _journal_file(
    root: Path,
    *,
    name: str,
    content: str,
    mtime: datetime | None = None,
) -> Path:
    """Write a journal file under ``<root>/_meta/journal/<name>`` and optionally
    stamp its mtime so the 3-month-window check can be exercised.
    """
    journal_dir = root / "_meta" / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    path = journal_dir / name
    path.write_text(content, encoding="utf-8")
    if mtime is not None:
        ts = mtime.timestamp()
        import os

        os.utime(path, (ts, ts))
    return path


def _basic_journal_body(project: str = "passpay") -> str:
    """Minimal journal content that contains concept-like phrases,
    a SOUL Delta block, and method language keywords.
    """
    return (
        f"# Journal — {project}\n\n"
        "## Summary\n\n"
        "Today's session explored the zk-proof evidence chain in the "
        "passpay whitepaper. The zk-proof section needs tightening. "
        "We applied an iterative refinement approach. The approach was "
        "repeatable: 4 rounds of review. zk-proof was referenced again "
        "in section 4.2, and the whitepaper evidence chain is now more "
        "consistent. The evidence chain pattern proved useful.\n\n"
        "## 🔮 SOUL Delta\n\n"
        "- evidence-discipline: +0.08 (confidence=0.82)\n"
        "- quality-over-speed: +0.05 (confidence=0.71)\n"
    )


# ─── Basic CLI contract ──────────────────────────────────────────────────────


class TestCliContract:
    def test_requires_from_and_to(self, tmp_path: Path, capsys):
        # Argparse exits with code 2 when required args are missing.
        try:
            main(["--root", str(tmp_path)])
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("expected SystemExit(2) for missing args")

    def test_empty_journal_dir_exits_zero(self, tmp_path: Path):
        # Provide an empty _meta/journal so we don't touch the cwd.
        (tmp_path / "_meta" / "journal").mkdir(parents=True)
        rc = main(
            ["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)]
        )
        assert rc == 0

    def test_empty_journal_writes_bootstrap_status(self, tmp_path: Path):
        (tmp_path / "_meta" / "journal").mkdir(parents=True)
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        status_path = (
            tmp_path / "_meta" / "cortex" / "bootstrap-status.md"
        )
        assert status_path.exists()
        text = status_path.read_text(encoding="utf-8")
        assert "migrate" in text.lower() or "Migration" in text

    def test_dry_run_writes_no_files(self, tmp_path: Path):
        _journal_file(
            tmp_path,
            name="2026-04-19-passpay.md",
            content=_basic_journal_body(),
            mtime=datetime(2026, 4, 19, 12, 38),
        )
        rc = main(
            [
                "--from",
                "v1.6.2a",
                "--to",
                "v1.7",
                "--dry-run",
                "--root",
                str(tmp_path),
            ]
        )
        assert rc == 0
        # No new output directories should appear
        assert not (tmp_path / "_meta" / "sessions").exists()
        assert not (tmp_path / "_meta" / "concepts").exists()
        assert not (tmp_path / "_meta" / "snapshots").exists()
        assert not (tmp_path / "_meta" / "methods").exists()
        assert not (
            tmp_path / "_meta" / "cortex" / "bootstrap-status.md"
        ).exists()


# ─── Session migration (§9) ──────────────────────────────────────────────────


class TestSessionBackfill:
    def test_journal_files_become_session_files(self, tmp_path: Path):
        for d in range(1, 5):
            _journal_file(
                tmp_path,
                name=f"2026-04-0{d}-passpay.md",
                content=_basic_journal_body(),
                mtime=datetime(2026, 4, d, 12, 38),
            )
        rc = main(
            ["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)]
        )
        assert rc == 0
        sessions_dir = tmp_path / "_meta" / "sessions"
        session_files = sorted(
            p for p in sessions_dir.glob("*.md") if p.name != "INDEX.md"
        )
        assert len(session_files) == 4

    def test_session_id_format_claude_yyyymmdd_hhmm(self, tmp_path: Path):
        _journal_file(
            tmp_path,
            name="2026-04-19-passpay.md",
            content=_basic_journal_body(),
            mtime=datetime(2026, 4, 19, 12, 38),
        )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        sessions_dir = tmp_path / "_meta" / "sessions"
        matches = [
            p for p in sessions_dir.glob("claude-20260419-1238.md")
            if p.name != "INDEX.md"
        ]
        assert matches, (
            f"Expected claude-20260419-1238.md, got "
            f"{[p.name for p in sessions_dir.glob('*.md')]}"
        )

    def test_session_defaults_platform_claude(self, tmp_path: Path):
        _journal_file(
            tmp_path,
            name="2026-04-19-passpay.md",
            content=_basic_journal_body(),
            mtime=datetime(2026, 4, 19, 12, 38),
        )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        session_file = (
            tmp_path / "_meta" / "sessions" / "claude-20260419-1238.md"
        )
        content = session_file.read_text(encoding="utf-8")
        # Parse frontmatter
        _, fm_text, _ = content.split("---\n", 2)
        fm = yaml.safe_load(fm_text)
        assert fm["platform"] == "claude"

    def test_session_prev17_fields_null(self, tmp_path: Path):
        """Pre-v1.7 fields like overall_score, domain_scores aren't
        authoritative; they should be null/absent, not fabricated."""
        _journal_file(
            tmp_path,
            name="2026-04-19-passpay.md",
            content=_basic_journal_body(),
            mtime=datetime(2026, 4, 19, 12, 38),
        )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        session_file = (
            tmp_path / "_meta" / "sessions" / "claude-20260419-1238.md"
        )
        content = session_file.read_text(encoding="utf-8")
        _, fm_text, _ = content.split("---\n", 2)
        fm = yaml.safe_load(fm_text)
        # overall_score is either missing or explicitly None
        assert fm.get("overall_score") in (None, 0, 0.0)

    def test_index_has_one_line_per_session(self, tmp_path: Path):
        for d in range(1, 5):
            _journal_file(
                tmp_path,
                name=f"2026-04-0{d}-passpay.md",
                content=_basic_journal_body(),
                mtime=datetime(2026, 4, d, 12, 38),
            )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        index_file = tmp_path / "_meta" / "sessions" / "INDEX.md"
        assert index_file.exists()
        content = index_file.read_text(encoding="utf-8")
        # Count lines with ` | ` and not a heading
        lines = [
            line
            for line in content.splitlines()
            if " | " in line and not line.startswith("#")
        ]
        assert len(lines) == 4


# ─── Concept backfill (§Migration) ───────────────────────────────────────────


class TestConceptBackfill:
    def test_concept_activation_count_ge_3_promotes_to_confirmed(
        self, tmp_path: Path
    ):
        # Create 3 separate journal entries that each mention "zk-proof"
        for d in range(1, 4):
            _journal_file(
                tmp_path,
                name=f"2026-04-0{d}-passpay.md",
                content=_basic_journal_body(),
                mtime=datetime(2026, 4, d, 12, 38),
            )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        concepts_root = tmp_path / "_meta" / "concepts"
        # Find a confirmed concept (not under _tentative/)
        confirmed_files = [
            p
            for p in concepts_root.rglob("*.md")
            if "_tentative" not in p.parts and p.name != "INDEX.md"
            and p.name != "SYNAPSES-INDEX.md"
        ]
        assert (
            len(confirmed_files) > 0
        ), "Expected at least one confirmed concept after 3+ sessions"
        # Verify status: confirmed in at least one file
        for cf in confirmed_files:
            content = cf.read_text(encoding="utf-8")
            if "status: confirmed" in content:
                return
        raise AssertionError(
            "No concept had status: confirmed despite activation ≥ 3"
        )

    def test_concept_activation_count_ge_10_promotes_to_canonical(
        self, tmp_path: Path
    ):
        # Create 10 separate journal entries that each mention "zk-proof"
        for d in range(1, 11):
            _journal_file(
                tmp_path,
                name=f"2026-04-{d:02d}-passpay.md",
                content=_basic_journal_body(),
                mtime=datetime(2026, 4, d, 12, 38),
            )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        concepts_root = tmp_path / "_meta" / "concepts"
        canonical_hits: list[Path] = []
        for cf in concepts_root.rglob("*.md"):
            if cf.name in ("INDEX.md", "SYNAPSES-INDEX.md"):
                continue
            if "status: canonical" in cf.read_text(encoding="utf-8"):
                canonical_hits.append(cf)
        assert canonical_hits, (
            "Expected at least one canonical concept after 10 sessions"
        )


# ─── SOUL snapshot synthesis (§Migration) ────────────────────────────────────


class TestSoulSnapshotSynth:
    def test_soul_delta_block_produces_synthetic_snapshot(
        self, tmp_path: Path
    ):
        _journal_file(
            tmp_path,
            name="2026-04-19-passpay.md",
            content=_basic_journal_body(),
            mtime=datetime(2026, 4, 19, 12, 38),
        )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        soul_root = tmp_path / "_meta" / "snapshots" / "soul"
        snapshot_files = list(soul_root.glob("*.md"))
        assert snapshot_files, (
            "Expected at least one synthetic snapshot from SOUL Delta"
        )
        content = snapshot_files[0].read_text(encoding="utf-8")
        assert "provenance: synthetic" in content, (
            f"Synthetic snapshot missing provenance marker: {content[:200]}"
        )

    def test_no_soul_delta_no_snapshot(self, tmp_path: Path):
        _journal_file(
            tmp_path,
            name="2026-04-19-passpay.md",
            content="# Journal\n\nA session without any SOUL delta.\n",
            mtime=datetime(2026, 4, 19, 12, 38),
        )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        soul_root = tmp_path / "_meta" / "snapshots" / "soul"
        if soul_root.exists():
            assert not any(soul_root.glob("*.md")), (
                "Did not expect any synthetic snapshot when no SOUL Delta "
                "block is present."
            )


# ─── Method candidate extraction (§15) ───────────────────────────────────────


class TestMethodCandidateExtraction:
    def test_approach_keyword_found(self, tmp_path: Path):
        _journal_file(
            tmp_path,
            name="2026-04-19-passpay.md",
            content=_basic_journal_body(),
            mtime=datetime(2026, 4, 19, 12, 38),
        )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        methods_tentative = tmp_path / "_meta" / "methods" / "_tentative"
        assert methods_tentative.exists(), (
            "Expected _meta/methods/_tentative to be created by migration"
        )
        tentative_files = list(methods_tentative.rglob("*.md"))
        assert tentative_files, (
            "Expected at least one tentative method candidate"
        )
        # All candidates must start as tentative
        for mf in tentative_files:
            assert "status: tentative" in mf.read_text(encoding="utf-8")


# ─── 3-month window ──────────────────────────────────────────────────────────


class TestThreeMonthWindow:
    def test_journal_older_than_90_days_skipped(self, tmp_path: Path):
        # Use a cutoff anchored off "now".
        now = datetime.now()
        old = now - timedelta(days=120)
        _journal_file(
            tmp_path,
            name="ancient.md",
            content=_basic_journal_body(),
            mtime=old,
        )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        sessions_dir = tmp_path / "_meta" / "sessions"
        # Session should not be produced for 120-day-old journal.
        if sessions_dir.exists():
            session_files = [
                p for p in sessions_dir.glob("*.md") if p.name != "INDEX.md"
            ]
            assert not session_files, (
                "Journal older than 3 months should have been skipped."
            )

    def test_journal_within_window_included(self, tmp_path: Path):
        now = datetime.now()
        fresh = now - timedelta(days=10)
        _journal_file(
            tmp_path,
            name="recent.md",
            content=_basic_journal_body(),
            mtime=fresh,
        )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        sessions_dir = tmp_path / "_meta" / "sessions"
        session_files = [
            p for p in sessions_dir.glob("*.md") if p.name != "INDEX.md"
        ]
        assert session_files, (
            "Journal within window should be migrated to a session file."
        )


# ─── Eval history: explicitly NOT migrated ──────────────────────────────────


class TestEvalHistoryNotMigrated:
    def test_eval_history_dir_stays_empty(self, tmp_path: Path):
        _journal_file(
            tmp_path,
            name="2026-04-19-passpay.md",
            content=_basic_journal_body(),
            mtime=datetime(2026, 4, 19, 12, 38),
        )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        eval_dir = tmp_path / "_meta" / "eval-history"
        # Either absent or exists but with no .md files
        if eval_dir.exists():
            md_files = list(eval_dir.rglob("*.md"))
            assert not md_files, (
                "eval-history must not be backfilled per spec §11"
            )


# ─── Idempotence ─────────────────────────────────────────────────────────────


class TestIdempotence:
    def test_rerun_produces_same_index(self, tmp_path: Path):
        for d in range(1, 4):
            _journal_file(
                tmp_path,
                name=f"2026-04-0{d}-passpay.md",
                content=_basic_journal_body(),
                mtime=datetime(2026, 4, d, 12, 38),
            )
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        idx_path = tmp_path / "_meta" / "sessions" / "INDEX.md"
        first = idx_path.read_text(encoding="utf-8")
        session_count_before = len(
            [p for p in (tmp_path / "_meta" / "sessions").glob("*.md")
             if p.name != "INDEX.md"]
        )
        # Re-run migration
        main(["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)])
        second = idx_path.read_text(encoding="utf-8")
        assert first == second, (
            "Re-run of migrate should produce byte-identical INDEX."
        )
        session_count_after = len(
            [p for p in (tmp_path / "_meta" / "sessions").glob("*.md")
             if p.name != "INDEX.md"]
        )
        assert session_count_before == session_count_after


# ─── Error handling ──────────────────────────────────────────────────────────


class TestParseErrors:
    def test_bad_file_skipped_others_succeed(self, tmp_path: Path):
        _journal_file(
            tmp_path,
            name="good.md",
            content=_basic_journal_body(),
            mtime=datetime(2026, 4, 19, 12, 38),
        )
        # Write something that yaml / utf-8 simply won't tolerate.
        bad_path = tmp_path / "_meta" / "journal" / "bad.md"
        bad_path.write_bytes(b"\xff\xfe\x00\x00")
        import os

        ts = datetime(2026, 4, 18, 9, 0).timestamp()
        os.utime(bad_path, (ts, ts))
        rc = main(
            ["--from", "v1.6.2a", "--to", "v1.7", "--root", str(tmp_path)]
        )
        # Exit 1 because at least one file had a parse error; per spec the
        # error is logged but other files continue through migration.
        assert rc == 1
        sessions_dir = tmp_path / "_meta" / "sessions"
        # The good file should still have produced a session.
        session_files = [
            p for p in sessions_dir.glob("*.md") if p.name != "INDEX.md"
        ]
        assert session_files, (
            "Parse error in one file must not prevent migrating others."
        )
