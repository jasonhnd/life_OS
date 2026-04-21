"""End-to-end integration tests for the Cortex Phase 1 retrieval pipeline.

Simulates the full archiver → retrospective → hippocampus chain using
synthetic fixtures:

    archiver Phase 2 writes _meta/outbox/{id}/sessions/{id}.md
    outbox merge moves to _meta/sessions/{id}.md
    retrospective compiles _meta/sessions/INDEX.md
    (hippocampus would then scan INDEX — we verify the data shape)

Plus the concept layer:
    archiver writes _meta/concepts/{domain}/{id}.md (with edges)
    Hebbian update increments edge weights
    retrospective compiles _meta/concepts/INDEX.md + SYNAPSES-INDEX.md

Plus snapshot lifecycle:
    archiver writes immutable snapshots
    archive policy (>30d → _archive, >90d → delete) enforced
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from tools.lib.cortex import (
    compile_concept_index,
    compile_index,
    compile_synapses_index,
    find_latest_snapshot,
    find_previous_snapshot,
    hebbian_update,
    rebuild_concept_index,
    rebuild_index,
    should_archive,
    should_delete,
    write_concept,
    write_session_summary,
    write_snapshot,
)
from tools.lib.cortex.session_index import session_summary_to_markdown
from tools.lib.second_brain import (
    Concept,
    ConceptEdge,
    ConceptProvenance,
    SessionSummary,
    SnapshotDimension,
    SoulSnapshot,
    parse_frontmatter,
)


# ─── Fixture builders ──────────────────────────────────────────────────────


def _build_session(
    session_id: str,
    date_val: date,
    project: str,
    subject: str,
    score: float,
    concepts_activated: list[str] | None = None,
    keywords: list[str] | None = None,
) -> SessionSummary:
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
        body=f"## Subject\n{subject}\n",
        concepts_activated=concepts_activated or [],
        keywords=keywords or [],
    )


def _build_concept(
    concept_id: str,
    domain: str,
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
        last_activated=datetime(2026, 4, 21),
        created=datetime(2026, 3, 1),
        body=f"## Definition\n{concept_id}\n",
        outgoing_edges=edges or [],
    )


# ─── Full session write→compile→read flow ──────────────────────────────────


class TestSessionFlow:
    def test_archiver_to_retrospective_pipeline(self, tmp_path: Path):
        """Simulate: archiver writes session, outbox merge, retrospective compiles INDEX."""
        # Simulated second-brain root
        sb = tmp_path / "second-brain"
        outbox = sb / "_meta" / "outbox"
        sessions = sb / "_meta" / "sessions"

        # archiver Phase 2 writes 3 session summaries to outbox
        sessions_data = [
            _build_session(
                "claude-20260421-1430",
                date(2026, 4, 21),
                "passpay",
                "Compliance architecture review",
                8.7,
                concepts_activated=["passpay-architecture", "compliance-jp"],
                keywords=["compliance", "architecture"],
            ),
            _build_session(
                "claude-20260420-0900",
                date(2026, 4, 20),
                "life-os",
                "v1.7 Cortex implementation kick-off",
                9.2,
                concepts_activated=["cortex", "hippocampus"],
                keywords=["cortex", "phase-1"],
            ),
            _build_session(
                "claude-20260315-1500",
                date(2026, 3, 15),
                "globo-gold",
                "Initial gold business case",
                6.5,
                keywords=["gold", "business-case"],
            ),
        ]
        for s in sessions_data:
            write_session_summary(s, outbox)

        # Outbox merge: move from outbox to canonical sessions/
        sessions.mkdir(parents=True, exist_ok=True)
        for s in sessions_data:
            src = outbox / s.session_id / "sessions" / f"{s.session_id}.md"
            dst = sessions / f"{s.session_id}.md"
            src.rename(dst)

        # retrospective Mode 0: compile INDEX
        index_path, count = rebuild_index(sb)
        assert index_path.exists()
        assert count == 3

        # Verify INDEX content
        content = index_path.read_text()
        assert "## 2026-04" in content
        assert "## 2026-03" in content
        assert "claude-20260421-1430" in content
        assert "8.7/10" in content
        # April section before March
        assert content.index("## 2026-04") < content.index("## 2026-03")
        # Within April: 21st before 20th (date desc)
        assert content.index("claude-20260421-1430") < content.index(
            "claude-20260420-0900"
        )

    def test_round_trip_preserves_concepts_activated(self, tmp_path: Path):
        """Verify hippocampus can read session frontmatter for concept references."""
        s = _build_session(
            "claude-20260421-1430",
            date(2026, 4, 21),
            "test",
            "test subject",
            8.0,
            concepts_activated=["concept-a", "concept-b"],
        )
        path = write_session_summary(s, tmp_path)
        # Move to canonical (simulating outbox merge)
        canonical = tmp_path / "claude-20260421-1430.md"
        path.rename(canonical)

        # hippocampus would Read the file and parse frontmatter
        parsed = parse_frontmatter(canonical.read_text())
        assert parsed.frontmatter["concepts_activated"] == ["concept-a", "concept-b"]


# ─── Concept layer end-to-end ──────────────────────────────────────────────


class TestConceptFlow:
    def test_archiver_writes_concepts_then_compiles_indexes(self, tmp_path: Path):
        """Simulate: archiver Phase 2 writes concepts → retrospective compiles INDEX + SYNAPSES."""
        sb = tmp_path / "second-brain"
        concepts_root = sb / "_meta" / "concepts"

        # 3 concepts with edges
        c1 = _build_concept(
            "passpay-arch",
            "startup",
            activation_count=10,
            edges=[ConceptEdge("compliance-jp", 5, datetime(2026, 4, 20))],
        )
        c2 = _build_concept(
            "compliance-jp",
            "legal",
            activation_count=4,
            edges=[ConceptEdge("passpay-arch", 5, datetime(2026, 4, 20))],
        )
        c3 = _build_concept("cortex", "technical", activation_count=15)

        for c in (c1, c2, c3):
            write_concept(c, concepts_root)

        # Compile INDEX
        idx_path, count = rebuild_concept_index(sb)
        assert idx_path.exists()
        assert count == 3

        idx_content = idx_path.read_text()
        assert "## startup" in idx_content
        assert "## legal" in idx_content
        assert "## technical" in idx_content
        # All 3 concept IDs present
        assert "passpay-arch" in idx_content
        assert "compliance-jp" in idx_content
        assert "cortex" in idx_content

        # SYNAPSES-INDEX
        syn = compile_synapses_index(concepts_root)
        # passpay-arch → compliance-jp edge means compliance-jp section should
        # have passpay-arch listed as source
        assert "## compliance-jp" in syn
        assert "passpay-arch | weight=5" in syn

    def test_hebbian_update_increments_edges(self, tmp_path: Path):
        """Simulate: archiver Hebbian step increments co-activation."""
        c1 = _build_concept(
            "a", "startup", activation_count=5, edges=[ConceptEdge("b", 3, datetime(2026, 4, 20))]
        )
        c2 = _build_concept("b", "startup", activation_count=2)

        # Co-activate (a, b) twice
        updated = hebbian_update([c1, c2], [("a", "b"), ("a", "b")])
        assert updated[0].outgoing_edges[0].weight == 5  # 3 + 2 increments
        assert updated[0].activation_count == 7  # 5 + 2

    def test_concept_promotion_paths(self, tmp_path: Path):
        """Verify status enum values are valid (tentative/confirmed/canonical)."""
        for status in ("tentative", "confirmed", "canonical"):
            c = _build_concept("test", "startup")
            c.status = status
            path = write_concept(c, tmp_path)
            content = path.read_text()
            assert f"status: {status}" in content


# ─── Snapshot lifecycle ────────────────────────────────────────────────────


class TestSnapshotLifecycle:
    def test_write_then_lookup_chain(self, tmp_path: Path):
        """Simulate multiple sessions writing snapshots; retrospective looks up trend."""
        snaps = tmp_path / "_meta" / "snapshots" / "soul"

        # Write 3 snapshots over time
        for i, day in enumerate([18, 19, 20]):
            captured = datetime(2026, 4, day, 14, 30)
            snap = SoulSnapshot(
                snapshot_id=f"2026-04-{day}-1430",
                captured_at=captured,
                session_id=f"claude-2026042{day}-1430",
                previous_snapshot=f"2026-04-{day-1}-1430" if i > 0 else None,
                dimensions=[
                    SnapshotDimension("autonomy", 0.7 + i * 0.05, 5 + i, 0, "core")
                ],
            )
            write_snapshot(snap, snaps)

        # retrospective Mode 0 lookup
        latest = find_latest_snapshot(snaps)
        assert latest.name == "2026-04-20-1430.md"

        prev = find_previous_snapshot(snaps)
        assert prev.name == "2026-04-19-1430.md"

        # Trend computation would compare these two

    def test_archive_then_delete_lifecycle(self, tmp_path: Path):
        """Simulate snapshots aging through 30d → archive → 90d → delete."""
        snaps = tmp_path / "_meta" / "snapshots" / "soul"

        # Recent snapshot (5 days old): keep
        recent = SoulSnapshot(
            snapshot_id="recent-001",
            captured_at=datetime.now() - timedelta(days=5),
            session_id="recent",
            previous_snapshot=None,
            dimensions=[SnapshotDimension("test", 0.85, 3, 0, "core")],
        )
        recent_path = write_snapshot(recent, snaps)
        assert not should_archive(recent_path)
        assert not should_delete(recent_path)

        # Mid-age snapshot (40 days): should archive
        mid = SoulSnapshot(
            snapshot_id="mid-001",
            captured_at=datetime.now() - timedelta(days=40),
            session_id="mid",
            previous_snapshot=None,
            dimensions=[SnapshotDimension("test", 0.85, 3, 0, "core")],
        )
        mid_path = write_snapshot(mid, snaps)
        assert should_archive(mid_path)
        assert not should_delete(mid_path)

        # Very old snapshot (100 days): should delete
        old = SoulSnapshot(
            snapshot_id="old-001",
            captured_at=datetime.now() - timedelta(days=100),
            session_id="old",
            previous_snapshot=None,
            dimensions=[SnapshotDimension("test", 0.85, 3, 0, "core")],
        )
        old_path = write_snapshot(old, snaps)
        assert should_delete(old_path)
