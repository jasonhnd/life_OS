"""SOUL snapshot helpers — write SoulSnapshot, compile snapshot index.

Used by archiver Phase 2 Step 3 (snapshot dump after concept extraction).
Per references/snapshot-spec.md.

Snapshots are immutable metadata-only dumps capturing SOUL dimension state
at session close. RETROSPECTIVE Mode 0 reads the two most recent snapshots
to compute trend arrows (↗↘→) in the SOUL Health Report.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from tools.lib.second_brain import (
    SnapshotDimension,
    SoulSnapshot,
    dump_frontmatter,
    load_markdown,
)

__all__ = [
    "snapshot_to_markdown",
    "write_snapshot",
    "find_latest_snapshot",
    "find_previous_snapshot",
    "list_active_snapshots",
    "list_archive_snapshots",
    "should_archive",
    "should_delete",
]


# ─── SoulSnapshot IO ─────────────────────────────────────────────────────────


def _snapshot_to_frontmatter(snap: SoulSnapshot) -> dict[str, Any]:
    """Convert SoulSnapshot dataclass to YAML-serialisable frontmatter dict."""
    fm: dict[str, Any] = {
        "snapshot_id": snap.snapshot_id,
        "captured_at": snap.captured_at.isoformat(),
        "session_id": snap.session_id,
        "previous_snapshot": snap.previous_snapshot,
        "dimensions": [
            {
                "name": d.name,
                "confidence": round(d.confidence, 3),
                "evidence_count": d.evidence_count,
                "challenges": d.challenges,
                "tier": d.tier,
            }
            for d in snap.dimensions
        ],
    }
    return fm


def snapshot_to_markdown(snap: SoulSnapshot) -> str:
    """Serialise a SoulSnapshot to markdown (frontmatter + minimal body)."""
    body = f"# SOUL Snapshot · {snap.snapshot_id}\n\n_({len(snap.dimensions)} dimensions, dormant excluded)_\n"
    return dump_frontmatter(_snapshot_to_frontmatter(snap), body)


def write_snapshot(snap: SoulSnapshot, snapshots_root: Path) -> Path:
    """Write SoulSnapshot to ``<snapshots_root>/{snapshot_id}.md``.

    Per spec: snapshots are immutable. Caller must not call this with the
    same snapshot_id twice; if file exists, raises ``FileExistsError``.

    Returns the path written.
    """
    snapshots_root.mkdir(parents=True, exist_ok=True)
    target = snapshots_root / f"{snap.snapshot_id}.md"
    if target.exists():
        raise FileExistsError(
            f"Snapshot {target} already exists (immutable per spec). "
            f"To correct, write a new snapshot with a different timestamp."
        )
    target.write_text(snapshot_to_markdown(snap), encoding="utf-8")
    return target


# ─── Snapshot lookup (for trend computation) ────────────────────────────────


def list_active_snapshots(snapshots_root: Path) -> list[Path]:
    """Return active snapshot files (in ``snapshots_root/`` directly), sorted desc."""
    if not snapshots_root.exists():
        return []
    return sorted(
        (p for p in snapshots_root.glob("*.md") if p.is_file()),
        key=lambda p: p.name,
        reverse=True,
    )


def list_archive_snapshots(snapshots_root: Path) -> list[Path]:
    """Return archived snapshot files (in ``snapshots_root/_archive/``), sorted desc."""
    archive_dir = snapshots_root / "_archive"
    if not archive_dir.exists():
        return []
    return sorted(
        (p for p in archive_dir.glob("*.md") if p.is_file()),
        key=lambda p: p.name,
        reverse=True,
    )


def find_latest_snapshot(snapshots_root: Path) -> Path | None:
    """Return the most recent active snapshot, or None if none exist."""
    actives = list_active_snapshots(snapshots_root)
    return actives[0] if actives else None


def find_previous_snapshot(snapshots_root: Path) -> Path | None:
    """Return the second-most-recent active snapshot, or None.

    Used by RETROSPECTIVE to compute trend deltas (latest vs previous).
    """
    actives = list_active_snapshots(snapshots_root)
    return actives[1] if len(actives) >= 2 else None


# ─── Archive policy (per spec: 30d active, 90d archive, then delete) ────────


_ACTIVE_DAYS = 30
_ARCHIVE_DAYS = 90


def should_archive(snapshot_path: Path, now: datetime | None = None) -> bool:
    """Check if a snapshot should be moved from active to archive.

    Per spec: snapshots > 30 days old move to ``_archive/``.
    """
    now = now or datetime.now()
    snap = _parse_snapshot(snapshot_path)
    if snap is None:
        return False
    age = now - snap.captured_at.replace(tzinfo=None)
    return age > timedelta(days=_ACTIVE_DAYS)


def should_delete(snapshot_path: Path, now: datetime | None = None) -> bool:
    """Check if a snapshot should be deleted (>90 days old).

    Git history retains the audit trail; this is filesystem cleanup only.
    """
    now = now or datetime.now()
    snap = _parse_snapshot(snapshot_path)
    if snap is None:
        return False
    age = now - snap.captured_at.replace(tzinfo=None)
    return age > timedelta(days=_ARCHIVE_DAYS)


def _parse_snapshot(path: Path) -> SoulSnapshot | None:
    """Parse a snapshot file into SoulSnapshot dataclass. Returns None on error."""
    try:
        parsed = load_markdown(path)
    except (ValueError, OSError):
        return None
    fm = parsed.frontmatter
    try:
        captured_at = fm["captured_at"]
        if isinstance(captured_at, str):
            captured_at = datetime.fromisoformat(captured_at)
        dims = [
            SnapshotDimension(
                name=d["name"],
                confidence=float(d["confidence"]),
                evidence_count=int(d.get("evidence_count", 0)),
                challenges=int(d.get("challenges", 0)),
                tier=d.get("tier") or SnapshotDimension.derive_tier(float(d["confidence"])),
            )
            for d in (fm.get("dimensions") or [])
        ]
        return SoulSnapshot(
            snapshot_id=fm["snapshot_id"],
            captured_at=captured_at,
            session_id=fm["session_id"],
            previous_snapshot=fm.get("previous_snapshot"),
            dimensions=dims,
        )
    except (KeyError, TypeError, ValueError):
        return None
