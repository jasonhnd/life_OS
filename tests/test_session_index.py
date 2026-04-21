"""Tests for tools.lib.cortex.session_index — SessionSummary IO + INDEX compile."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from tools.lib.cortex.session_index import (
    compile_index,
    compile_index_line,
    rebuild_index,
    session_summary_to_markdown,
    truncate_subject,
    write_session_summary,
)
from tools.lib.second_brain import (
    ActionItem,
    SessionSummary,
    parse_frontmatter,
)

# ─── Helpers ────────────────────────────────────────────────────────────────


def _make_summary(
    session_id: str = "claude-20260421-1430",
    date_val: date = date(2026, 4, 21),
    score: float = 8.5,
    project: str = "life-os",
    subject: str = "test subject",
    keywords: list[str] | None = None,
) -> SessionSummary:
    """Make a SessionSummary with sensible defaults."""
    return SessionSummary(
        session_id=session_id,
        date=date_val,
        started_at=datetime.combine(date_val, datetime.min.time()).replace(hour=14),
        ended_at=datetime.combine(date_val, datetime.min.time()).replace(
            hour=14, minute=30
        ),
        duration_minutes=30,
        platform="claude",
        theme="zh-classical",
        project=project,
        workflow="full_deliberation",
        subject=subject,
        overall_score=score,
        veto_count=0,
        council_triggered=False,
        compliance_violations=0,
        body="body",
        keywords=keywords or ["k1", "k2", "k3"],
    )


# ─── truncate_subject ───────────────────────────────────────────────────────


class TestTruncateSubject:
    def test_short_subject_unchanged(self):
        assert truncate_subject("short") == "short"

    def test_exactly_max_length_unchanged(self):
        s = "a" * 80
        assert truncate_subject(s) == s

    def test_long_subject_truncated_with_ellipsis(self):
        s = "a" * 100
        result = truncate_subject(s, max_len=80)
        assert len(result) == 81  # 80 chars + ellipsis
        assert result.endswith("…")

    def test_unicode_truncation(self):
        s = "三" * 90
        result = truncate_subject(s, max_len=50)
        assert result.endswith("…")


# ─── SessionSummary IO ───────────────────────────────────────────────────────


class TestSessionSummaryIO:
    def test_write_creates_file_in_outbox_subdir(self, tmp_path: Path):
        s = _make_summary()
        outbox = tmp_path / "outbox"
        path = write_session_summary(s, outbox)
        assert path.exists()
        assert "sessions" in path.parts
        assert path.name == f"{s.session_id}.md"

    def test_round_trip_preserves_required_fields(self, tmp_path: Path):
        s = _make_summary(score=7.2, keywords=["a", "b"])
        outbox = tmp_path / "outbox"
        path = write_session_summary(s, outbox)
        parsed = parse_frontmatter(path.read_text())
        assert parsed.frontmatter["session_id"] == s.session_id
        assert parsed.frontmatter["overall_score"] == 7.2
        assert parsed.frontmatter["keywords"] == ["a", "b"]
        assert parsed.frontmatter["project"] == "life-os"

    def test_optional_empty_lists_omitted(self, tmp_path: Path):
        s = _make_summary()
        s.domains_activated = []  # empty
        path = write_session_summary(s, tmp_path)
        parsed = parse_frontmatter(path.read_text())
        # Empty optional lists should not appear in frontmatter
        assert "domains_activated" not in parsed.frontmatter

    def test_action_items_serialised(self, tmp_path: Path):
        s = _make_summary()
        s.action_items = [
            ActionItem("Do X", deadline=date(2026, 5, 1), status="pending"),
            ActionItem("Do Y", status="completed"),
        ]
        path = write_session_summary(s, tmp_path)
        parsed = parse_frontmatter(path.read_text())
        assert len(parsed.frontmatter["action_items"]) == 2
        assert parsed.frontmatter["action_items"][0]["text"] == "Do X"
        assert parsed.frontmatter["action_items"][0]["deadline"] == "2026-05-01"


# ─── compile_index_line ──────────────────────────────────────────────────────


class TestCompileIndexLine:
    def test_well_formed_frontmatter(self):
        s = _make_summary(score=8.7, keywords=["cortex", "phase-1"])
        path = Path("/tmp/test.md")
        path_text = session_summary_to_markdown(s)
        parsed = parse_frontmatter(path_text)
        line = compile_index_line(parsed)
        assert line is not None
        assert s.session_id in line
        assert "life-os" in line
        assert "8.7/10" in line
        assert "cortex, phase-1" in line

    def test_null_score_renders_as_na(self):
        s = _make_summary()
        text = session_summary_to_markdown(s)
        # Manually mutate the rendered frontmatter to simulate null score
        text = text.replace("overall_score: 8.5", "overall_score: null")
        parsed = parse_frontmatter(text)
        line = compile_index_line(parsed)
        assert line is not None
        assert "n/a/10" in line

    def test_missing_required_field_returns_none(self):
        from tools.lib.second_brain import ParsedMarkdown

        parsed = ParsedMarkdown(frontmatter={"session_id": "x"}, body="")  # no date
        assert compile_index_line(parsed) is None


# ─── compile_index ───────────────────────────────────────────────────────────


class TestCompileIndex:
    def test_empty_dir(self, tmp_path: Path):
        sessions = tmp_path / "sessions"
        sessions.mkdir()
        content = compile_index(sessions)
        assert "no sessions indexed yet" in content

    def test_nonexistent_dir(self, tmp_path: Path):
        content = compile_index(tmp_path / "nonexistent")
        assert "no sessions indexed yet" in content

    def test_groups_by_month_desc(self, tmp_path: Path):
        sessions = tmp_path / "_meta" / "sessions"
        sessions.mkdir(parents=True)
        # Apr session
        s1 = _make_summary(
            session_id="claude-20260421-1430", date_val=date(2026, 4, 21)
        )
        (sessions / f"{s1.session_id}.md").write_text(session_summary_to_markdown(s1))
        # Mar session
        s2 = _make_summary(
            session_id="claude-20260315-0900", date_val=date(2026, 3, 15)
        )
        (sessions / f"{s2.session_id}.md").write_text(session_summary_to_markdown(s2))

        content = compile_index(sessions)
        assert "## 2026-04" in content
        assert "## 2026-03" in content
        # April section comes before March (most recent first)
        assert content.index("## 2026-04") < content.index("## 2026-03")

    def test_within_month_sorted_date_desc(self, tmp_path: Path):
        sessions = tmp_path / "_meta" / "sessions"
        sessions.mkdir(parents=True)
        s1 = _make_summary(
            session_id="claude-20260421-1430", date_val=date(2026, 4, 21)
        )
        s2 = _make_summary(
            session_id="claude-20260420-0900", date_val=date(2026, 4, 20)
        )
        (sessions / f"{s1.session_id}.md").write_text(session_summary_to_markdown(s1))
        (sessions / f"{s2.session_id}.md").write_text(session_summary_to_markdown(s2))
        content = compile_index(sessions)
        assert content.index("claude-20260421-1430") < content.index(
            "claude-20260420-0900"
        )

    def test_idempotence(self, tmp_path: Path):
        sessions = tmp_path / "_meta" / "sessions"
        sessions.mkdir(parents=True)
        s = _make_summary()
        (sessions / f"{s.session_id}.md").write_text(session_summary_to_markdown(s))
        first = compile_index(sessions)
        second = compile_index(sessions)
        assert first == second

    def test_excludes_index_md(self, tmp_path: Path):
        sessions = tmp_path / "_meta" / "sessions"
        sessions.mkdir(parents=True)
        s = _make_summary()
        (sessions / f"{s.session_id}.md").write_text(session_summary_to_markdown(s))
        # Pre-existing INDEX.md should be ignored when re-compiling
        (sessions / "INDEX.md").write_text("# Old Index\n\nstale content\n")
        content = compile_index(sessions)
        assert "stale content" not in content


# ─── rebuild_index ──────────────────────────────────────────────────────────


class TestRebuildIndex:
    def test_returns_path_and_count(self, tmp_path: Path):
        sessions = tmp_path / "_meta" / "sessions"
        sessions.mkdir(parents=True)
        s = _make_summary()
        (sessions / f"{s.session_id}.md").write_text(session_summary_to_markdown(s))
        path, count = rebuild_index(tmp_path)
        assert path == sessions / "INDEX.md"
        assert path.exists()
        assert count == 1
