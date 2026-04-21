#!/usr/bin/env python3
"""Snapshot + violations archive rotation.

Implements the archive policy from references/snapshot-spec.md +
references/compliance-spec.md:

Snapshots:
- Active: <= 30 days old → stay in _meta/snapshots/soul/
- Archived: 30-90 days → move to _meta/snapshots/soul/_archive/
- Deleted: > 90 days → remove from filesystem (git history retains)

Violations log:
- Active: rolling 90 days in pro/compliance/violations.md (or
  _meta/compliance/violations.md for user repo)
- Archived: > 90 days → moved to pro/compliance/archive/YYYY-QN.md
  (or _meta/compliance/archive/...)

Usage:
    uv run tools/backup.py [--root PATH] [--dry-run] [--snapshots-only | --violations-only]
    python3 tools/backup.py [--root PATH] [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.cortex.snapshot import (  # noqa: E402
    list_active_snapshots,
    list_archive_snapshots,
    should_archive,
    should_delete,
)


_NINETY_DAYS = timedelta(days=90)


# ─── Snapshot rotation ──────────────────────────────────────────────────────


def rotate_snapshots(
    snapshots_root: Path, dry_run: bool = False
) -> tuple[list[Path], list[Path]]:
    """Move 30-90d snapshots to _archive/, delete >90d.

    Returns (archived_paths, deleted_paths).
    """
    archive_dir = snapshots_root / "_archive"
    archived: list[Path] = []
    deleted: list[Path] = []

    if not snapshots_root.exists():
        return archived, deleted

    # Process active snapshots (top-level)
    for path in list_active_snapshots(snapshots_root):
        if should_delete(path):
            deleted.append(path)
            if not dry_run:
                path.unlink()
        elif should_archive(path):
            archived.append(path)
            if not dry_run:
                archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), str(archive_dir / path.name))

    # Also delete archived snapshots > 90d old
    for path in list_archive_snapshots(snapshots_root):
        if should_delete(path):
            deleted.append(path)
            if not dry_run:
                path.unlink()

    return archived, deleted


# ─── Violations log rotation ────────────────────────────────────────────────


_VIOLATION_ROW_RE = re.compile(
    r"^\|\s*(?P<timestamp>\d{4}-\d{2}-\d{2}\S*)\s*\|"
)


def _quarter_for(d: datetime) -> str:
    """Return YYYY-QN for the given date."""
    quarter = (d.month - 1) // 3 + 1
    return f"{d.year}-Q{quarter}"


def rotate_violations(
    violations_path: Path,
    archive_root: Path,
    dry_run: bool = False,
    now: datetime | None = None,
) -> dict:
    """Move violation rows older than 90 days to quarterly archive files.

    Returns dict with keys:
    - archived_count: rows moved
    - active_remaining: rows remaining in violations.md
    - archive_files: list of archive files created/appended
    """
    now = now or datetime.now().astimezone()
    cutoff = now - _NINETY_DAYS

    if not violations_path.exists():
        return {"archived_count": 0, "active_remaining": 0, "archive_files": []}

    lines = violations_path.read_text(encoding="utf-8").splitlines()
    keep_lines: list[str] = []
    archive_buckets: dict[str, list[str]] = {}

    in_violations_table = False
    for line in lines:
        m = _VIOLATION_ROW_RE.match(line)
        if not m:
            keep_lines.append(line)
            continue
        ts = m.group("timestamp")
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError:
            keep_lines.append(line)
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=now.tzinfo)
        if dt < cutoff:
            quarter = _quarter_for(dt)
            archive_buckets.setdefault(quarter, []).append(line)
        else:
            keep_lines.append(line)

    archive_files: list[Path] = []
    if not dry_run:
        archive_root.mkdir(parents=True, exist_ok=True)
        for quarter, rows in archive_buckets.items():
            archive_path = archive_root / f"{quarter}.md"
            archive_files.append(archive_path)
            existing = (
                archive_path.read_text(encoding="utf-8") if archive_path.exists() else ""
            )
            if not existing:
                existing = (
                    f"# Compliance Violations Archive · {quarter}\n\n"
                    "| Timestamp | Trigger | Type | Severity | Details | Resolved |\n"
                    "|-----------|---------|------|----------|---------|----------|\n"
                )
            archive_path.write_text(existing + "\n".join(rows) + "\n", encoding="utf-8")

        if archive_buckets:
            violations_path.write_text("\n".join(keep_lines) + "\n", encoding="utf-8")

    return {
        "archived_count": sum(len(rows) for rows in archive_buckets.values()),
        "active_remaining": sum(
            1 for line in keep_lines if _VIOLATION_ROW_RE.match(line)
        ),
        "archive_files": [str(p) for p in archive_files],
    }


# ─── Path resolution ────────────────────────────────────────────────────────


def resolve_violations_paths(cwd: Path) -> tuple[Path | None, Path | None]:
    """Auto-detect violations.md + archive root (dev or user repo)."""
    candidates = [
        (cwd / "pro" / "compliance" / "violations.md",
         cwd / "pro" / "compliance" / "archive"),
        (cwd / "_meta" / "compliance" / "violations.md",
         cwd / "_meta" / "compliance" / "archive"),
    ]
    for v_path, a_path in candidates:
        if v_path.exists():
            return v_path, a_path
    return None, None


# ─── CLI ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rotate snapshots (30d/90d) + archive old violations (>90d)"
    )
    parser.add_argument(
        "--root", type=Path, default=Path.cwd(),
        help="Path to second-brain root (default: cwd)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would happen, do not modify files",
    )
    parser.add_argument(
        "--snapshots-only", action="store_true",
        help="Only rotate snapshots; skip violations archival",
    )
    parser.add_argument(
        "--violations-only", action="store_true",
        help="Only archive violations; skip snapshot rotation",
    )
    args = parser.parse_args()

    if args.snapshots_only and args.violations_only:
        print("❌ Cannot use both --snapshots-only and --violations-only", file=sys.stderr)
        return 2

    do_snapshots = not args.violations_only
    do_violations = not args.snapshots_only

    print(f"🗂️  Backup rotation · root: {args.root}")
    if args.dry_run:
        print("   (dry-run mode — no files modified)")
    print()

    if do_snapshots:
        snapshots_root = args.root / "_meta" / "snapshots" / "soul"
        if snapshots_root.exists():
            archived, deleted = rotate_snapshots(snapshots_root, dry_run=args.dry_run)
            verb = "Would archive" if args.dry_run else "Archived"
            print(f"📸 SOUL snapshots: {verb} {len(archived)}, {'would delete' if args.dry_run else 'deleted'} {len(deleted)}")
            for p in archived[:5]:
                print(f"   archived: {p.name}")
            if len(archived) > 5:
                print(f"   ... and {len(archived) - 5} more")
            for p in deleted[:5]:
                print(f"   deleted: {p.name}")
            if len(deleted) > 5:
                print(f"   ... and {len(deleted) - 5} more")
        else:
            print(f"📸 SOUL snapshots: no snapshots directory at {snapshots_root}, skipping")
        print()

    if do_violations:
        v_path, a_root = resolve_violations_paths(args.root)
        if v_path is None:
            print("📋 Violations: no log file found, skipping")
        else:
            result = rotate_violations(v_path, a_root, dry_run=args.dry_run)
            verb = "Would archive" if args.dry_run else "Archived"
            print(f"📋 Violations log: {verb} {result['archived_count']} rows")
            print(f"   active remaining: {result['active_remaining']}")
            for f in result["archive_files"]:
                print(f"   archive: {f}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
