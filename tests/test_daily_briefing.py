"""Tests for tools.daily_briefing — v1.7 Sprint 4.

Contract: references/tools-spec.md §6.5.

Aggregates:
  - SOUL core tier (confidence >= 0.7)
  - DREAM reports from last 30 days
  - Active projects (last_modified within last 14 days)
  - Inbox items (count pending)
  - Eval-history (last 3 entries)

Always exits 0. Runtime < 3s.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from tools.daily_briefing import build_briefing, main

# ─── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
def brain_root(tmp_path: Path) -> Path:
    """A minimally-valid empty second-brain root."""
    root = tmp_path / "brain"
    root.mkdir()
    # Core subdirectories — mirror the layout enforced by seed.py
    (root / "_meta" / "journal").mkdir(parents=True)
    (root / "_meta" / "eval-history").mkdir(parents=True)
    (root / "projects").mkdir()
    (root / "inbox").mkdir()
    return root


def _write_soul(
    root: Path,
    dimensions: list[tuple[str, float]],
) -> None:
    """Write SOUL.md with the given (name, confidence) dimensions."""
    parts = ["# SOUL · Test User\n", ""]
    for name, conf in dimensions:
        ev = 10
        challenges = 0
        # tier derivation
        if conf >= 0.7:
            tier = "core"
        elif conf >= 0.3:
            tier = "secondary"
        elif conf >= 0.2:
            tier = "emerging"
        else:
            tier = "dormant"
        parts.append(f"## Dimension: {name}\n")
        parts.append("")
        parts.append("```yaml")
        parts.append(f"dimension_id: {name.lower().replace(' ', '-')}")
        parts.append(f"confidence: {conf}")
        parts.append(f"evidence_count: {ev}")
        parts.append(f"challenges: {challenges}")
        parts.append(f"tier: {tier}")
        parts.append("```")
        parts.append("")
        parts.append("### What IS")
        parts.append("observed pattern")
        parts.append("")
        parts.append("---")
        parts.append("")
    (root / "SOUL.md").write_text("\n".join(parts), encoding="utf-8")


def _write_dream(root: Path, d: date) -> Path:
    path = root / "_meta" / "journal" / f"{d.isoformat()}-dream.md"
    path.write_text(
        f"# Dream Report · {d.isoformat()}\n\nInsights go here.\n",
        encoding="utf-8",
    )
    return path


def _write_project(
    root: Path,
    name: str,
    last_modified: datetime,
    status: str = "active",
) -> Path:
    proj = root / "projects" / name
    proj.mkdir(parents=True, exist_ok=True)
    content = f"""\
---
name: {name}
status: {status}
last_modified: {last_modified.isoformat()}
---
# {name}

Project description.
"""
    path = proj / "index.md"
    path.write_text(content, encoding="utf-8")
    return path


def _write_inbox(root: Path, slug: str) -> Path:
    path = root / "inbox" / f"{slug}.md"
    path.write_text("# Inbox item\n\nunprocessed content\n", encoding="utf-8")
    return path


def _write_eval(root: Path, d: date, project: str, score: float) -> Path:
    path = root / "_meta" / "eval-history" / f"{d.isoformat()}-{project}.md"
    path.write_text(
        f"""\
---
date: {d.isoformat()}
project: {project}
overall_score: {score}
---
# Eval · {d.isoformat()} · {project}
""",
        encoding="utf-8",
    )
    return path


# ─── build_briefing() — pure function ────────────────────────────────────────


class TestEmptyBrain:
    def test_all_sections_present_on_empty_brain(self, brain_root: Path):
        md = build_briefing(brain_root, today=date(2026, 4, 21))
        assert "# Today's Briefing — 2026-04-21" in md
        assert "## SOUL Core" in md
        assert "## Recent DREAMs" in md
        assert "## Active Projects" in md
        assert "## Inbox" in md
        assert "## Eval History" in md

    def test_empty_brain_mentions_empty_state(self, brain_root: Path):
        md = build_briefing(brain_root, today=date(2026, 4, 21))
        # Each section should have a meaningful empty-state hint, not a crash.
        assert "0" in md  # counters of zero somewhere


class TestSoulCoreTier:
    def test_lists_core_dimension_only(self, brain_root: Path):
        _write_soul(
            brain_root,
            [
                ("High Value", 0.9),  # core
                ("Mid Value", 0.5),  # secondary — NOT included
                ("Low Value", 0.25),  # emerging — NOT included
                ("Dormant Value", 0.1),  # dormant — NOT included
            ],
        )
        md = build_briefing(brain_root, today=date(2026, 4, 21))
        assert "High Value" in md
        assert "Mid Value" not in md
        assert "Low Value" not in md
        assert "Dormant Value" not in md

    def test_core_confidence_threshold_inclusive(self, brain_root: Path):
        _write_soul(brain_root, [("Boundary", 0.7)])
        md = build_briefing(brain_root, today=date(2026, 4, 21))
        assert "Boundary" in md

    def test_core_threshold_strict_below(self, brain_root: Path):
        _write_soul(brain_root, [("Just Below", 0.69)])
        md = build_briefing(brain_root, today=date(2026, 4, 21))
        assert "Just Below" not in md

    def test_missing_soul_renders_zero(self, brain_root: Path):
        md = build_briefing(brain_root, today=date(2026, 4, 21))
        assert "## SOUL Core" in md
        # Should not crash; empty state should not list any dimensions.


class TestDreamWindow:
    def test_includes_dream_within_30_days(self, brain_root: Path):
        today = date(2026, 4, 21)
        _write_dream(brain_root, today - timedelta(days=5))
        _write_dream(brain_root, today - timedelta(days=29))
        # outside the 30-day window (31 days ago)
        _write_dream(brain_root, today - timedelta(days=31))
        md = build_briefing(brain_root, today=today)
        # section header should show count of reports within window
        assert "last 30 days: 2 reports" in md

    def test_30_day_window_boundary_inclusive(self, brain_root: Path):
        today = date(2026, 4, 21)
        _write_dream(brain_root, today - timedelta(days=30))
        md = build_briefing(brain_root, today=today)
        assert "last 30 days: 1 reports" in md

    def test_no_dreams_empty_window(self, brain_root: Path):
        md = build_briefing(brain_root, today=date(2026, 4, 21))
        assert "last 30 days: 0 reports" in md


class TestActiveProjects:
    def test_active_within_14_days(self, brain_root: Path):
        today = date(2026, 4, 21)
        now = datetime.combine(today, datetime.min.time()).replace(hour=12)
        _write_project(brain_root, "alpha", now - timedelta(days=3))
        _write_project(brain_root, "beta", now - timedelta(days=13))
        _write_project(brain_root, "dormant", now - timedelta(days=20))
        md = build_briefing(brain_root, today=today)
        assert "Active Projects (2)" in md
        assert "alpha" in md
        assert "beta" in md
        assert "dormant" not in md

    def test_fifteenth_day_is_inactive(self, brain_root: Path):
        """Boundary: 15th day past is NOT active (strict <=14)."""
        today = date(2026, 4, 21)
        now = datetime.combine(today, datetime.min.time()).replace(hour=12)
        _write_project(brain_root, "borderline", now - timedelta(days=15))
        md = build_briefing(brain_root, today=today)
        assert "Active Projects (0)" in md
        assert "borderline" not in md

    def test_fourteenth_day_is_active(self, brain_root: Path):
        today = date(2026, 4, 21)
        now = datetime.combine(today, datetime.min.time()).replace(hour=12)
        _write_project(brain_root, "edge", now - timedelta(days=14))
        md = build_briefing(brain_root, today=today)
        assert "Active Projects (1)" in md
        assert "edge" in md

    def test_project_without_last_modified_skipped(self, brain_root: Path):
        proj = brain_root / "projects" / "no-meta"
        proj.mkdir()
        (proj / "index.md").write_text("# plain\n\nno frontmatter\n", encoding="utf-8")
        md = build_briefing(brain_root, today=date(2026, 4, 21))
        assert "Active Projects (0)" in md


class TestInbox:
    def test_counts_pending_inbox_items(self, brain_root: Path):
        _write_inbox(brain_root, "item-1")
        _write_inbox(brain_root, "item-2")
        _write_inbox(brain_root, "item-3")
        md = build_briefing(brain_root, today=date(2026, 4, 21))
        assert "Inbox (3 pending)" in md

    def test_empty_inbox_zero(self, brain_root: Path):
        md = build_briefing(brain_root, today=date(2026, 4, 21))
        assert "Inbox (0 pending)" in md


class TestEvalHistory:
    def test_shows_last_three_by_date_desc(self, brain_root: Path):
        today = date(2026, 4, 21)
        _write_eval(brain_root, today - timedelta(days=1), "alpha", 8.0)
        _write_eval(brain_root, today - timedelta(days=2), "beta", 7.5)
        _write_eval(brain_root, today - timedelta(days=3), "gamma", 9.0)
        _write_eval(brain_root, today - timedelta(days=5), "delta", 6.0)
        md = build_briefing(brain_root, today=today)
        # Most recent three only
        assert "alpha" in md
        assert "beta" in md
        assert "gamma" in md
        assert "delta" not in md
        # Ordering: alpha (most recent) appears before gamma (older)
        assert md.index("alpha") < md.index("gamma")


# ─── CLI ─────────────────────────────────────────────────────────────────────


class TestCLI:
    def test_main_exits_zero_on_empty_brain(
        self, brain_root: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(brain_root)
        rc = main([])
        captured = capsys.readouterr()
        assert rc == 0
        assert "Today's Briefing" in captured.out

    def test_main_supports_root_flag(
        self, brain_root: Path, capsys: pytest.CaptureFixture
    ):
        rc = main(["--root", str(brain_root)])
        captured = capsys.readouterr()
        assert rc == 0
        assert "Today's Briefing" in captured.out
