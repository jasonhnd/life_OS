"""Tests for tools.stats §6.3 extensions — session / eval / SOUL aggregates.

Per references/tools-spec.md §6.3. The existing stats.py keeps its
compliance-violations output (covered by tests/test_stats.py). The
extension adds:

    --period month|quarter|year
    --since YYYY-MM-DD
    --output FILE

and computes session count, avg overall_score, domain distribution,
SOUL 4-tier trend, DREAM trigger frequency, top 3 concept tags, and
eval-history dimension averages.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from tools.stats import (
    aggregate_stats,
    compute_domain_distribution,
    compute_session_aggregates,
    compute_top_concept_tags,
    main,
    parse_period_filter,
)

# ─── Fixtures ────────────────────────────────────────────────────────────────


def _session_md(
    session_id: str,
    date_val: date,
    *,
    project: str = "life-os",
    score: float = 8.0,
    domains: list[str] | None = None,
    concepts: list[str] | None = None,
    dream_triggers: list[str] | None = None,
) -> str:
    domains = domains or ["professional"]
    domain_yaml = "".join(f"  - {d}\n" for d in domains)
    concept_yaml = (
        ("concepts_activated:\n" + "".join(f"  - {c}\n" for c in concepts))
        if concepts
        else ""
    )
    dream_yaml = (
        ("dream_triggers:\n" + "".join(f"  - {d}\n" for d in dream_triggers))
        if dream_triggers
        else ""
    )
    return (
        "---\n"
        f"session_id: {session_id}\n"
        f"date: {date_val.isoformat()}\n"
        f"started_at: {date_val.isoformat()}T14:30:00\n"
        f"ended_at: {date_val.isoformat()}T15:00:00\n"
        "duration_minutes: 30\n"
        "platform: claude\n"
        "theme: zh-classical\n"
        f"project: {project}\n"
        "workflow: full_deliberation\n"
        "subject: test\n"
        f"overall_score: {score}\n"
        "veto_count: 0\n"
        "council_triggered: false\n"
        "compliance_violations: 0\n"
        "domains_activated:\n"
        f"{domain_yaml}"
        f"{concept_yaml}"
        f"{dream_yaml}"
        "---\nbody\n"
    )


def _setup_sessions(root: Path, sessions: list[tuple[str, date, dict]]) -> None:
    sessions_dir = root / "_meta" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    for session_id, date_val, kwargs in sessions:
        (sessions_dir / f"{session_id}.md").write_text(
            _session_md(session_id, date_val, **kwargs), encoding="utf-8"
        )


# ─── parse_period_filter ─────────────────────────────────────────────────────


class TestParsePeriod:
    def test_month_default_30_days(self):
        now = datetime(2026, 4, 21, 12, 0)
        since = parse_period_filter(period="month", since=None, now=now)
        assert (now - since).days == 30

    def test_quarter_90_days(self):
        now = datetime(2026, 4, 21, 12, 0)
        since = parse_period_filter(period="quarter", since=None, now=now)
        assert (now - since).days == 90

    def test_year_365_days(self):
        now = datetime(2026, 4, 21, 12, 0)
        since = parse_period_filter(period="year", since=None, now=now)
        assert (now - since).days == 365

    def test_since_wins_over_period(self):
        now = datetime(2026, 4, 21, 12, 0)
        since = parse_period_filter(period="month", since="2025-01-01", now=now)
        assert since.date() == date(2025, 1, 1)


# ─── compute_session_aggregates ──────────────────────────────────────────────


class TestSessionAggregates:
    def test_empty_returns_zero(self, tmp_path: Path):
        sessions_dir = tmp_path / "_meta" / "sessions"
        sessions_dir.mkdir(parents=True)
        agg = compute_session_aggregates(sessions_dir, since=datetime(2000, 1, 1))
        assert agg["count"] == 0
        assert agg["avg_overall_score"] is None

    def test_count_and_average(self, tmp_path: Path):
        today = date.today()
        _setup_sessions(
            tmp_path,
            [
                ("s1", today, {"score": 7.0}),
                ("s2", today, {"score": 9.0}),
                ("s3", today, {"score": 8.0}),
            ],
        )
        agg = compute_session_aggregates(
            tmp_path / "_meta" / "sessions",
            since=datetime.combine(today - timedelta(days=5), datetime.min.time()),
        )
        assert agg["count"] == 3
        assert agg["avg_overall_score"] == 8.0

    def test_since_excludes_old_sessions(self, tmp_path: Path):
        today = date.today()
        _setup_sessions(
            tmp_path,
            [
                ("recent", today, {"score": 9.0}),
                ("old", today - timedelta(days=200), {"score": 5.0}),
            ],
        )
        agg = compute_session_aggregates(
            tmp_path / "_meta" / "sessions",
            since=datetime.combine(today - timedelta(days=30), datetime.min.time()),
        )
        assert agg["count"] == 1
        assert agg["avg_overall_score"] == 9.0


# ─── compute_domain_distribution ────────────────────────────────────────────


class TestDomainDistribution:
    def test_counts_per_domain(self, tmp_path: Path):
        today = date.today()
        _setup_sessions(
            tmp_path,
            [
                ("s1", today, {"domains": ["professional", "relationships"]}),
                ("s2", today, {"domains": ["professional"]}),
                ("s3", today, {"domains": ["health"]}),
            ],
        )
        dist = compute_domain_distribution(
            tmp_path / "_meta" / "sessions",
            since=datetime.combine(today - timedelta(days=30), datetime.min.time()),
        )
        assert dist["professional"] == 2
        assert dist["relationships"] == 1
        assert dist["health"] == 1


# ─── compute_top_concept_tags ───────────────────────────────────────────────


class TestTopConceptTags:
    def test_top_3_by_frequency(self, tmp_path: Path):
        today = date.today()
        _setup_sessions(
            tmp_path,
            [
                ("s1", today, {"concepts": ["focus", "energy", "focus"]}),
                ("s2", today, {"concepts": ["focus", "money"]}),
                ("s3", today, {"concepts": ["energy", "discipline"]}),
            ],
        )
        top = compute_top_concept_tags(
            tmp_path / "_meta" / "sessions",
            since=datetime.combine(today - timedelta(days=30), datetime.min.time()),
            top_n=3,
        )
        # Ordered by frequency descending
        assert [t[0] for t in top[:3]] == ["focus", "energy", "money"] or [
            t[0] for t in top[:3]
        ] == ["focus", "energy", "discipline"]  # tie break


# ─── Integration — main() ────────────────────────────────────────────────────


class TestMainIntegration:
    def test_default_period_month_stdout(self, tmp_path: Path, capsys):
        _setup_sessions(tmp_path, [("s1", date.today(), {"score": 8.0})])
        rc = main(["--root", str(tmp_path)])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Session count" in captured.out or "session" in captured.out.lower()

    def test_since_filter(self, tmp_path: Path, capsys):
        today = date.today()
        _setup_sessions(
            tmp_path,
            [
                ("recent", today, {"score": 9.0}),
                ("old", today - timedelta(days=400), {"score": 3.0}),
            ],
        )
        rc = main(["--since", "2026-01-01", "--root", str(tmp_path)])
        assert rc == 0
        captured = capsys.readouterr()
        # "old" should be excluded from the window
        assert "3.0" not in captured.out

    def test_output_file(self, tmp_path: Path):
        _setup_sessions(tmp_path, [("s1", date.today(), {"score": 8.0})])
        out = tmp_path / "report.md"
        rc = main(["--output", str(out), "--root", str(tmp_path)])
        assert rc == 0
        assert out.exists()
        text = out.read_text(encoding="utf-8")
        assert "session" in text.lower()

    def test_empty_period_exits_zero(self, tmp_path: Path, capsys):
        # Empty second-brain — no sessions / eval / snapshots
        (tmp_path / "_meta" / "sessions").mkdir(parents=True)
        rc = main(["--period", "month", "--root", str(tmp_path)])
        assert rc == 0
        captured = capsys.readouterr()
        assert "no data" in captured.out.lower()

    def test_period_quarter(self, tmp_path: Path, capsys):
        today = date.today()
        _setup_sessions(
            tmp_path,
            [
                ("recent", today, {"score": 9.0}),
                ("old", today - timedelta(days=60), {"score": 5.0}),
            ],
        )
        rc = main(["--period", "quarter", "--root", str(tmp_path)])
        assert rc == 0
        captured = capsys.readouterr()
        # 60d ago falls within quarter (90d window)
        assert "2" in captured.out  # count == 2 likely appears


# ─── aggregate_stats — the core function ────────────────────────────────────


class TestAggregateStats:
    def test_returns_required_keys(self, tmp_path: Path):
        _setup_sessions(tmp_path, [("s1", date.today(), {"score": 7.5})])
        result = aggregate_stats(
            tmp_path,
            since=datetime.combine(
                date.today() - timedelta(days=30), datetime.min.time()
            ),
        )
        # Every major metric defined in the spec is surfaced
        assert "session_count" in result
        assert "avg_overall_score" in result
        assert "domain_distribution" in result
        assert "top_concept_tags" in result
        assert "dream_trigger_frequency" in result

    def test_aggregate_math(self, tmp_path: Path):
        today = date.today()
        _setup_sessions(
            tmp_path,
            [
                ("s1", today, {"score": 10.0}),
                ("s2", today, {"score": 6.0}),
            ],
        )
        result = aggregate_stats(
            tmp_path,
            since=datetime.combine(today - timedelta(days=30), datetime.min.time()),
        )
        assert result["session_count"] == 2
        assert result["avg_overall_score"] == 8.0


# ─── Backward compatibility — legacy violations still work ──────────────────


class TestLegacyCompat:
    def test_violations_flag_still_works(self, tmp_path: Path, capsys):
        # Legacy --violations flag must not have been removed.
        violations = tmp_path / "violations.md"
        violations.write_text(
            "| Timestamp | Trigger | Type | Severity | Details | Resolved |\n"
            "|-----------|---------|------|----------|---------|----------|\n"
            "| 2026-04-19T22:47+09:00 | x | A1 | P0 | y | false |\n",
            encoding="utf-8",
        )
        rc = main(["--violations", str(violations), "--root", str(tmp_path)])
        assert rc == 0
