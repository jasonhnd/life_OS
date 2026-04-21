"""Tests for tools.search — grep + metadata-ranked cross-session search.

Contract: references/tools-spec.md §6.8.

Ranking formula (deterministic, no LLM):
    base_score = 4 * subject_hits
               + 2 * (domain + keyword) hits
               + 1 * min(body_paragraph_hits, 5)
    recency_mult = 1.5 if days_since <= recency_boost_days else 1.0
    final_score = base_score * recency_mult

Tie-break: newer session first.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from tools.search import main, rank_sessions

# ─── Fixture helpers ────────────────────────────────────────────────────────


_FM_TEMPLATE = """\
---
session_id: {session_id}
date: {date}
started_at: {started_at}
ended_at: {ended_at}
duration_minutes: 30
platform: claude
theme: zh-classical
project: {project}
workflow: full_deliberation
subject: {subject}
overall_score: {score}
veto_count: 0
council_triggered: false
compliance_violations: 0
domains_activated: {domains}
keywords: {keywords}
---
{body}
"""


def _yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(f'"{item}"' for item in items) + "]"


def _write_session(
    sessions_dir: Path,
    session_id: str,
    date_val: date,
    subject: str,
    domains: list[str] | None = None,
    keywords: list[str] | None = None,
    body: str = "body content here\n\nsecond paragraph\n",
    project: str = "life-os",
    score: float = 8.0,
) -> Path:
    """Write one session .md file matching session-index-spec format."""
    started = datetime.combine(date_val, datetime.min.time()).replace(hour=14)
    ended = started.replace(hour=14, minute=30)
    content = _FM_TEMPLATE.format(
        session_id=session_id,
        date=date_val.isoformat(),
        started_at=started.isoformat(),
        ended_at=ended.isoformat(),
        project=project,
        subject=subject,
        score=score,
        domains=_yaml_list(domains or []),
        keywords=_yaml_list(keywords or []),
        body=body,
    )
    path = sessions_dir / f"{session_id}.md"
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def brain_root(tmp_path: Path) -> Path:
    """A tmp second-brain root with an empty _meta/sessions/."""
    root = tmp_path / "brain"
    (root / "_meta" / "sessions").mkdir(parents=True)
    return root


# ─── rank_sessions() — pure function ─────────────────────────────────────────


class TestRankScoring:
    def test_empty_dir_returns_empty_list(self, brain_root: Path):
        results = rank_sessions(brain_root, "anything", today=date(2026, 4, 21))
        assert results == []

    def test_subject_hit_outweighs_body_hit(self, brain_root: Path):
        """Subject hit (4x) must outweigh a pure body hit (1x)."""
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="quit job deliberation",
            body="unrelated body\n",
        )
        _write_session(
            sessions,
            "claude-20260419-0900",
            today - timedelta(days=200),
            subject="unrelated",
            body="quit appears in body\n\nquit again\n",
        )
        results = rank_sessions(brain_root, "quit", today=today)
        assert len(results) == 2
        assert results[0].session_id == "claude-20260420-0900"
        assert results[0].score > results[1].score

    def test_domain_and_keyword_hits_weighted_2x(self, brain_root: Path):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="unrelated subject",
            keywords=["career"],
            body="no match here\n",
        )
        results = rank_sessions(brain_root, "career", today=today)
        assert len(results) == 1
        # keyword hit only: base=2, recency_mult=1.0 -> 2.0
        assert results[0].score == pytest.approx(2.0)

    def test_body_paragraph_hits_capped_at_five(self, brain_root: Path):
        """Body hits contribute at most 5 to base_score (capped)."""
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        body = "\n\n".join(["career matters"] * 10)
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="unrelated",
            body=body,
        )
        results = rank_sessions(brain_root, "career", today=today)
        # base = 0 (subject) + 0 (keyword) + 1 * min(10, 5) = 5, recency=1.0 => 5.0
        assert results[0].score == pytest.approx(5.0)

    def test_body_hits_count_at_most_once_per_paragraph(self, brain_root: Path):
        """A paragraph with the term 3 times counts as 1 paragraph hit."""
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        body = "career career career\n\nother stuff\n"
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="unrelated",
            body=body,
        )
        results = rank_sessions(brain_root, "career", today=today)
        # 1 paragraph hit (not 3), base=1, recency=1.0
        assert results[0].score == pytest.approx(1.0)

    def test_recency_boost_applied_within_window(self, brain_root: Path):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        # Recent session (within default 90 days)
        _write_session(
            sessions,
            "claude-20260401-0900",
            today - timedelta(days=20),
            subject="career thoughts",
        )
        # Old session
        _write_session(
            sessions,
            "claude-20250101-0900",
            today - timedelta(days=365),
            subject="career thoughts",
        )
        results = rank_sessions(brain_root, "career", today=today)
        # recent: 4 * 1.5 = 6.0; old: 4 * 1.0 = 4.0
        assert results[0].session_id == "claude-20260401-0900"
        assert results[0].score == pytest.approx(6.0)
        assert results[1].score == pytest.approx(4.0)

    def test_recency_boost_honours_config(self, brain_root: Path):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        # 120 days ago — outside default 90, inside config 150
        _write_session(
            sessions,
            "claude-20251222-0900",
            today - timedelta(days=120),
            subject="career",
        )
        results = rank_sessions(
            brain_root, "career", today=today, recency_boost_days=150
        )
        assert results[0].score == pytest.approx(6.0)  # 4 * 1.5

        results_default = rank_sessions(
            brain_root, "career", today=today, recency_boost_days=90
        )
        assert results_default[0].score == pytest.approx(4.0)  # 4 * 1.0

    def test_tie_break_newer_first(self, brain_root: Path):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        # Same score — both 200 days old (no recency), same subject
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="career",
        )
        _write_session(
            sessions,
            "claude-20260419-0900",
            today - timedelta(days=201),
            subject="career",
        )
        results = rank_sessions(brain_root, "career", today=today)
        assert results[0].session_id == "claude-20260420-0900"
        assert results[1].session_id == "claude-20260419-0900"

    def test_multi_term_or(self, brain_root: Path):
        """Multiple query terms: a session matches if ANY term matches."""
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="career change",
        )
        _write_session(
            sessions,
            "claude-20260419-0900",
            today - timedelta(days=200),
            subject="health habits",
        )
        results = rank_sessions(brain_root, "career health", today=today)
        assert len(results) == 2  # both match at least one term
        # Both get 4 (one subject hit each), tie-break by newer
        assert results[0].session_id == "claude-20260420-0900"

    def test_case_insensitive(self, brain_root: Path):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="CAREER topic",
        )
        results = rank_sessions(brain_root, "career", today=today)
        assert len(results) == 1
        assert results[0].score == pytest.approx(4.0)

    def test_no_match_returns_empty(self, brain_root: Path):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="nothing relevant",
            body="truly unrelated\n",
        )
        results = rank_sessions(brain_root, "xyzunmatchable", today=today)
        assert results == []

    def test_ignores_index_md(self, brain_root: Path):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="career",
        )
        (sessions / "INDEX.md").write_text(
            "# Session Index\n\ncareer career career\n", encoding="utf-8"
        )
        results = rank_sessions(brain_root, "career", today=today)
        assert len(results) == 1  # INDEX.md not counted


# ─── CLI entry point ─────────────────────────────────────────────────────────


class TestCLI:
    def test_no_matches_exits_zero_with_message(
        self, brain_root: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(brain_root)
        rc = main(["xyzunmatchable"])
        captured = capsys.readouterr()
        assert rc == 0
        assert "no matches" in captured.out.lower()

    def test_top_n_limits_output(
        self,
        brain_root: Path,
        capsys: pytest.CaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        for i in range(10):
            _write_session(
                sessions,
                f"claude-2026042{i % 10}-0900",
                today - timedelta(days=200 + i),
                subject="career topic",
            )
        monkeypatch.chdir(brain_root)
        rc = main(["career", "--top", "2"])
        captured = capsys.readouterr()
        assert rc == 0
        output_lines = [
            line for line in captured.out.splitlines() if line.strip()
        ]
        assert len(output_lines) == 2

    def test_default_top_five(
        self,
        brain_root: Path,
        capsys: pytest.CaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        for i in range(8):
            _write_session(
                sessions,
                f"claude-2026042{i % 10}-0900",
                today - timedelta(days=200 + i),
                subject="career topic",
            )
        monkeypatch.chdir(brain_root)
        rc = main(["career"])
        captured = capsys.readouterr()
        assert rc == 0
        output_lines = [
            line for line in captured.out.splitlines() if line.strip()
        ]
        assert len(output_lines) == 5  # default N

    def test_rank_line_format(
        self,
        brain_root: Path,
        capsys: pytest.CaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="career change decision",
        )
        monkeypatch.chdir(brain_root)
        rc = main(["career"])
        captured = capsys.readouterr()
        assert rc == 0
        line = captured.out.strip()
        # Format: {rank}. {path}  (score={score:.1f})  {snippet up to 80ch}
        assert line.startswith("1.")
        assert "claude-20260420-0900.md" in line
        assert "score=" in line


class TestSnippetFromSubject:
    def test_snippet_prefers_subject(
        self,
        brain_root: Path,
        capsys: pytest.CaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ):
        sessions = brain_root / "_meta" / "sessions"
        today = date(2026, 4, 21)
        _write_session(
            sessions,
            "claude-20260420-0900",
            today - timedelta(days=200),
            subject="career change — leaving fintech for AI research",
            body="body here\n",
        )
        monkeypatch.chdir(brain_root)
        rc = main(["career"])
        captured = capsys.readouterr()
        assert rc == 0
        assert "career change" in captured.out
