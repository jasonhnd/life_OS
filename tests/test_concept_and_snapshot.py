"""Tests for tools.lib.cortex.concept and tools.lib.cortex.snapshot."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tools.lib.cortex.concept import (
    compile_concept_index,
    compile_synapses_index,
    hebbian_update,
    read_concept,
    rebuild_concept_index,
    write_concept,
)
from tools.lib.cortex.snapshot import (
    find_latest_snapshot,
    find_previous_snapshot,
    list_active_snapshots,
    should_archive,
    should_delete,
    write_snapshot,
)
from tools.lib.second_brain import (
    Concept,
    ConceptEdge,
    ConceptProvenance,
    SnapshotDimension,
    SoulSnapshot,
)


# ─── Helpers ────────────────────────────────────────────────────────────────


def _make_concept(
    concept_id: str = "test-concept",
    domain: str = "startup",
    activation_count: int = 1,
    edges: list[ConceptEdge] | None = None,
) -> Concept:
    return Concept(
        concept_id=concept_id,
        canonical_name=concept_id.replace("-", " ").title(),
        domain=domain,
        status="confirmed",
        permanence="fact",
        activation_count=activation_count,
        last_activated=datetime(2026, 4, 21, 14, 30),
        created=datetime(2026, 3, 1),
        body="body",
        outgoing_edges=edges or [],
    )


def _make_snapshot(
    snapshot_id: str = "2026-04-21-1430",
    captured_at: datetime | None = None,
) -> SoulSnapshot:
    return SoulSnapshot(
        snapshot_id=snapshot_id,
        captured_at=captured_at or datetime(2026, 4, 21, 14, 30),
        session_id="claude-20260421-1430",
        previous_snapshot=None,
        dimensions=[SnapshotDimension("autonomy", 0.85, 5, 1, "core")],
    )


# ─── concept.py — IO ────────────────────────────────────────────────────────


class TestConceptIO:
    def test_write_creates_domain_dir(self, tmp_path: Path):
        c = _make_concept()
        path = write_concept(c, tmp_path)
        assert path.parent.name == "startup"
        assert path.name == "test-concept.md"

    def test_round_trip(self, tmp_path: Path):
        edges = [
            ConceptEdge("other", 5, datetime(2026, 4, 20), relation="implies")
        ]
        c = _make_concept(activation_count=12, edges=edges)
        path = write_concept(c, tmp_path)
        loaded = read_concept(path)
        assert loaded is not None
        assert loaded.concept_id == c.concept_id
        assert loaded.activation_count == 12
        assert len(loaded.outgoing_edges) == 1
        assert loaded.outgoing_edges[0].target == "other"
        assert loaded.outgoing_edges[0].weight == 5

    def test_read_invalid_file_returns_none(self, tmp_path: Path):
        bad = tmp_path / "bad.md"
        bad.write_text("---\nincomplete\n", encoding="utf-8")
        assert read_concept(bad) is None


# ─── concept.py — INDEX compile ─────────────────────────────────────────────


class TestConceptIndex:
    def test_groups_by_domain(self, tmp_path: Path):
        write_concept(_make_concept("c-startup", "startup"), tmp_path)
        write_concept(_make_concept("c-finance", "finance"), tmp_path)
        content = compile_concept_index(tmp_path)
        assert "## startup" in content
        assert "## finance" in content
        assert "c-startup" in content
        assert "c-finance" in content

    def test_excludes_tentative_and_archive(self, tmp_path: Path):
        # Manually drop a file under _tentative — should be ignored
        (tmp_path / "_tentative").mkdir(parents=True)
        (tmp_path / "_tentative" / "skip-me.md").write_text(
            "---\nconcept_id: skip-me\ncanonical_name: Skip\ndomain: startup\n"
            "status: tentative\npermanence: transient\nactivation_count: 1\n"
            "last_activated: 2026-04-21T00:00:00\ncreated: 2026-04-01T00:00:00\n---\n",
            encoding="utf-8",
        )
        # Add one real concept
        write_concept(_make_concept(), tmp_path)
        content = compile_concept_index(tmp_path)
        assert "skip-me" not in content
        assert "test-concept" in content

    def test_empty_dir(self, tmp_path: Path):
        content = compile_concept_index(tmp_path / "empty")
        assert "no concepts yet" in content

    def test_rebuild_returns_count(self, tmp_path: Path):
        concepts_root = tmp_path / "_meta" / "concepts"
        concepts_root.mkdir(parents=True)
        write_concept(_make_concept(), concepts_root)
        target, count = rebuild_concept_index(tmp_path)
        assert target.exists()
        assert count == 1


# ─── concept.py — SYNAPSES-INDEX ────────────────────────────────────────────


class TestSynapsesIndex:
    def test_reverse_index(self, tmp_path: Path):
        a = _make_concept("a", edges=[ConceptEdge("b", 5, datetime(2026, 4, 20))])
        b = _make_concept("b")
        write_concept(a, tmp_path)
        write_concept(b, tmp_path)
        syn = compile_synapses_index(tmp_path)
        assert "## b" in syn
        assert "a | weight=5" in syn

    def test_empty_when_no_edges(self, tmp_path: Path):
        write_concept(_make_concept(), tmp_path)
        syn = compile_synapses_index(tmp_path)
        assert "no synapse edges yet" in syn


# ─── concept.py — Hebbian ────────────────────────────────────────────────────


class TestHebbian:
    def test_increment_existing_edge(self):
        a = _make_concept(
            "a", edges=[ConceptEdge("b", 3, datetime(2026, 4, 20))]
        )
        b = _make_concept("b")
        result = hebbian_update([a, b], [("a", "b")])
        assert result[0].outgoing_edges[0].weight == 4
        assert result[0].activation_count == 2  # was 1, +1

    def test_create_new_edge(self):
        a = _make_concept("a", edges=[])
        b = _make_concept("b")
        result = hebbian_update([a, b], [("a", "b")])
        assert len(result[0].outgoing_edges) == 1
        assert result[0].outgoing_edges[0].target == "b"
        assert result[0].outgoing_edges[0].weight == 1

    def test_skip_unknown_source(self):
        a = _make_concept("a")
        result = hebbian_update([a], [("nonexistent", "a")])
        assert len(result) == 1
        # No edges added, no activation_count change
        assert result[0].activation_count == 1
        assert result[0].outgoing_edges == []


# ─── snapshot.py ─────────────────────────────────────────────────────────────


class TestSnapshot:
    def test_write_creates_file(self, tmp_path: Path):
        s = _make_snapshot()
        path = write_snapshot(s, tmp_path)
        assert path.exists()
        assert path.name == f"{s.snapshot_id}.md"

    def test_immutability_raises(self, tmp_path: Path):
        s = _make_snapshot()
        write_snapshot(s, tmp_path)
        with pytest.raises(FileExistsError):
            write_snapshot(s, tmp_path)

    def test_find_latest(self, tmp_path: Path):
        s1 = _make_snapshot(snapshot_id="2026-04-20-0900")
        s2 = _make_snapshot(snapshot_id="2026-04-21-1430")
        write_snapshot(s1, tmp_path)
        write_snapshot(s2, tmp_path)
        latest = find_latest_snapshot(tmp_path)
        assert latest is not None
        assert latest.name == "2026-04-21-1430.md"

    def test_find_previous(self, tmp_path: Path):
        s1 = _make_snapshot(snapshot_id="2026-04-20-0900")
        s2 = _make_snapshot(snapshot_id="2026-04-21-1430")
        write_snapshot(s1, tmp_path)
        write_snapshot(s2, tmp_path)
        prev = find_previous_snapshot(tmp_path)
        assert prev is not None
        assert prev.name == "2026-04-20-0900.md"

    def test_find_previous_none_when_only_one(self, tmp_path: Path):
        write_snapshot(_make_snapshot(), tmp_path)
        assert find_previous_snapshot(tmp_path) is None

    def test_should_archive_after_30_days(self, tmp_path: Path):
        old = _make_snapshot(captured_at=datetime.now() - timedelta(days=35))
        path = write_snapshot(old, tmp_path)
        assert should_archive(path) is True
        assert should_delete(path) is False

    def test_should_delete_after_90_days(self, tmp_path: Path):
        very_old = _make_snapshot(captured_at=datetime.now() - timedelta(days=100))
        path = write_snapshot(very_old, tmp_path)
        assert should_delete(path) is True

    def test_recent_snapshot_neither_archived_nor_deleted(self, tmp_path: Path):
        recent = _make_snapshot(captured_at=datetime.now() - timedelta(days=2))
        path = write_snapshot(recent, tmp_path)
        assert should_archive(path) is False
        assert should_delete(path) is False
