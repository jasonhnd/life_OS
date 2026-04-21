"""Tests for tools.lib.second_brain — dataclasses + frontmatter parser."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest

from tools.lib.second_brain import (
    ActionItem,
    Concept,
    ConceptEdge,
    ConceptProvenance,
    EvalEntry,
    Method,
    ParsedMarkdown,
    SecondBrainEntity,
    SessionSummary,
    SnapshotDimension,
    SoulSnapshot,
    WikiNote,
    dump_frontmatter,
    load_markdown,
    parse_frontmatter,
    resolve_path,
)


# ─── Frontmatter parser ──────────────────────────────────────────────────────


class TestParseFrontmatter:
    def test_simple_frontmatter(self):
        content = "---\nkey: value\nnum: 42\n---\nbody text\n"
        parsed = parse_frontmatter(content)
        assert parsed.frontmatter == {"key": "value", "num": 42}
        assert parsed.body == "body text\n"
        assert parsed.has_frontmatter

    def test_no_frontmatter(self):
        content = "just body, no frontmatter\n"
        parsed = parse_frontmatter(content)
        assert parsed.frontmatter == {}
        assert parsed.body == content
        assert not parsed.has_frontmatter

    def test_malformed_no_closing_marker(self):
        content = "---\nkey: value\n(no closing)\nbody\n"
        parsed = parse_frontmatter(content)
        # Treated as no frontmatter — full content is body
        assert parsed.frontmatter == {}
        assert parsed.body == content

    def test_invalid_yaml_raises(self):
        content = "---\nkey: : :\nvalue\n---\nbody\n"
        with pytest.raises(ValueError, match="Invalid YAML frontmatter"):
            parse_frontmatter(content, source_path=Path("/test.md"))

    def test_non_dict_frontmatter_raises(self):
        content = "---\n- list item\n- another\n---\nbody\n"
        with pytest.raises(ValueError, match="must be a dict"):
            parse_frontmatter(content)

    def test_round_trip_preserves_data(self):
        sample = {
            "session_id": "claude-20260421-1430",
            "score": 8.5,
            "keywords": ["a", "b", "c"],
        }
        body = "## Body\n\ncontent\n"
        serialised = dump_frontmatter(sample, body)
        parsed = parse_frontmatter(serialised)
        assert parsed.frontmatter == sample
        assert parsed.body == body

    def test_unicode_preserved(self):
        sample = {"subject": "三省六部 · v1.7 cortex"}
        body = "テスト内容\n"
        serialised = dump_frontmatter(sample, body)
        parsed = parse_frontmatter(serialised)
        assert parsed.frontmatter == sample
        assert parsed.body == body


class TestLoadMarkdown:
    def test_load_real_file(self, tmp_path: Path):
        target = tmp_path / "test.md"
        target.write_text("---\nkey: value\n---\nbody\n", encoding="utf-8")
        parsed = load_markdown(target)
        assert parsed.frontmatter == {"key": "value"}
        assert parsed.body == "body\n"
        assert parsed.source_path == target


# ─── SnapshotDimension tier mapping ──────────────────────────────────────────


class TestSnapshotDimension:
    @pytest.mark.parametrize(
        "confidence,expected_tier",
        [
            (1.0, "core"),
            (0.85, "core"),
            (0.7, "core"),
            (0.69, "secondary"),
            (0.5, "secondary"),
            (0.3, "secondary"),
            (0.29, "emerging"),
            (0.2, "emerging"),
            (0.19, "dormant"),
            (0.0, "dormant"),
        ],
    )
    def test_derive_tier(self, confidence: float, expected_tier: str):
        assert SnapshotDimension.derive_tier(confidence) == expected_tier


# ─── SoulSnapshot ───────────────────────────────────────────────────────────


class TestSoulSnapshot:
    def test_dormant_dimensions_filtered(self):
        snap = SoulSnapshot(
            snapshot_id="2026-04-21-1430",
            captured_at=datetime(2026, 4, 21, 14, 30),
            session_id="claude-20260421-1430",
            previous_snapshot=None,
            dimensions=[
                SnapshotDimension("core_dim", 0.85, 5, 0, "core"),
                SnapshotDimension("low_dim", 0.1, 1, 1, "dormant"),
            ],
        )
        assert len(snap.dimensions) == 1
        assert snap.dimensions[0].name == "core_dim"


# ─── resolve_path ────────────────────────────────────────────────────────────


class TestResolvePath:
    def test_session_summary_path(self):
        ss = SessionSummary(
            session_id="claude-20260421-1430",
            date=date(2026, 4, 21),
            started_at=datetime(2026, 4, 21, 14, 0),
            ended_at=datetime(2026, 4, 21, 14, 30),
            duration_minutes=30,
            platform="claude",
            theme="zh-classical",
            project="life-os",
            workflow="full_deliberation",
            subject="test",
            overall_score=8.5,
            veto_count=0,
            council_triggered=False,
            compliance_violations=0,
            body="body",
        )
        result = resolve_path(ss, Path("/tmp/sb"))
        assert result == Path("/tmp/sb/_meta/sessions/claude-20260421-1430.md")

    def test_concept_path(self):
        c = Concept(
            concept_id="test-concept",
            canonical_name="Test",
            domain="startup",
            status="confirmed",
            permanence="fact",
            activation_count=3,
            last_activated=datetime(2026, 4, 21),
            created=datetime(2026, 4, 1),
            body="body",
        )
        result = resolve_path(c, Path("/tmp/sb"))
        assert result == Path("/tmp/sb/_meta/concepts/startup/test-concept.md")
