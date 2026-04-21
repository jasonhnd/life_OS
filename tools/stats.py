#!/usr/bin/env python3
"""Compliance violation statistics — escalation ladder enforcement.

Reads violations.md (dual-repo: dev `pro/compliance/violations.md` or
user `_meta/compliance/violations.md`), aggregates by type and time window,
and reports which escalation thresholds have been crossed.

Per references/compliance-spec.md §Escalation Ladder:
- >=3 same type in 30 days → hook reminder strictness upgrades
- >=5 same type in 30 days → briefing prepends "🚨 Compliance Watch"
- >=10 same type in 90 days → AUDITOR runs Compliance Patrol every Start Session

Usage:
    uv run tools/stats.py [--violations PATH] [--json]
    python3 tools/stats.py [--violations PATH] [--json]

Auto-detects path:
    1. ./pro/compliance/violations.md (dev repo)
    2. ./_meta/compliance/violations.md (user repo)
    3. otherwise --violations required
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ─── Parse violations.md table ──────────────────────────────────────────────

# Table row format (per compliance-spec.md §Entry Format):
#   | Timestamp | Trigger | Type | Severity | Details | Resolved |
_ROW_RE = re.compile(
    r"^\|\s*(?P<timestamp>[^|]+?)\s*\|"
    r"\s*(?P<trigger>[^|]*?)\s*\|"
    r"\s*(?P<type>[^|]+?)\s*\|"
    r"\s*(?P<severity>[^|]+?)\s*\|"
    r"\s*(?P<details>[^|]*?)\s*\|"
    r"\s*(?P<resolved>[^|]+?)\s*\|"
    r"\s*$"
)

# Skip the header rows
_HEADER_TIMESTAMP = "timestamp"
_HEADER_SEPARATOR_FRAGMENT = "---"


def parse_violations(violations_path: Path) -> list[dict]:
    """Parse violations.md into a list of structured records.

    Returns list of dicts with keys: timestamp, trigger, type, severity,
    details, resolved, parsed_dt (datetime or None on parse failure).

    Skips: header row, separator, code blocks (format examples), rows whose
    type field doesn't look like a valid type code (A1/A2/A3/B/C/D/E/F).
    """
    if not violations_path.exists():
        return []
    rows: list[dict] = []
    in_code_block = False
    for line in violations_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        m = _ROW_RE.match(line)
        if not m:
            continue
        d = m.groupdict()
        # Skip header row + separator
        ts = d["timestamp"].strip()
        if ts.lower().startswith(_HEADER_TIMESTAMP):
            continue
        if _HEADER_SEPARATOR_FRAGMENT in ts:
            continue
        # Sanity: type code should be 1-3 chars (A1/A2/A3/B/C/D/E/F)
        type_field = d["type"].strip()
        if not type_field or len(type_field) > 3:
            continue
        d["parsed_dt"] = _parse_iso_timestamp(ts)
        rows.append(d)
    return rows


def _parse_iso_timestamp(ts: str) -> datetime | None:
    """Parse an ISO 8601 timestamp string, tolerate offset variants."""
    ts = ts.strip()
    # Common forms in spec examples:
    #   2026-04-19T22:47+09:00
    #   2026-04-21T13:42+09:00
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        # Try replacing space-separated form
        try:
            return datetime.fromisoformat(ts.replace(" ", "T"))
        except ValueError:
            return None


# ─── Escalation thresholds ──────────────────────────────────────────────────


_THRESHOLDS = [
    (3, 30, "hook_strictness_up", "Hook reminder strictness upgrades"),
    (5, 30, "briefing_compliance_watch", "Retrospective briefing prepends 🚨 Compliance Watch"),
    (10, 90, "auditor_every_start_session", "AUDITOR Compliance Patrol runs at every Start Session"),
]


def compute_escalations(rows: list[dict], now: datetime | None = None) -> dict:
    """Compute escalation state per violation type.

    Returns dict with keys:
    - by_type: Counter of all violations by type (lifetime)
    - active_30d: Counter by type, last 30 days
    - active_90d: Counter by type, last 90 days
    - escalations_active: list of {type, threshold, action} dicts
    - unresolved_count: count of rows with Resolved in (false, partial)
    """
    now = now or datetime.now().astimezone()
    cutoff_30 = now - timedelta(days=30)
    cutoff_90 = now - timedelta(days=90)

    all_by_type: Counter = Counter()
    active_30d: Counter = Counter()
    active_90d: Counter = Counter()
    unresolved = 0

    for r in rows:
        # Type may have multiple variants; canonicalise
        t = r["type"].strip().split()[0] if r["type"] else "?"
        all_by_type[t] += 1
        if r["resolved"].strip().lower() in ("false", "partial"):
            unresolved += 1
        dt = r["parsed_dt"]
        if dt is None:
            continue
        # Make timezone-aware for comparison if needed
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=now.tzinfo)
        if dt >= cutoff_30:
            active_30d[t] += 1
        if dt >= cutoff_90:
            active_90d[t] += 1

    escalations: list[dict] = []
    for threshold_count, window_days, action, description in _THRESHOLDS:
        counter = active_30d if window_days == 30 else active_90d
        for vtype, count in counter.items():
            if count >= threshold_count:
                escalations.append(
                    {
                        "type": vtype,
                        "threshold_count": threshold_count,
                        "window_days": window_days,
                        "actual_count": count,
                        "action": action,
                        "description": description,
                    }
                )

    return {
        "by_type_lifetime": dict(all_by_type),
        "active_30d": dict(active_30d),
        "active_90d": dict(active_90d),
        "unresolved_count": unresolved,
        "escalations_active": escalations,
        "computed_at": now.isoformat(),
    }


# ─── Path resolution + CLI ──────────────────────────────────────────────────


def resolve_violations_path(cwd: Path) -> Path | None:
    """Auto-detect violations.md path (dev repo or user repo)."""
    candidates = [
        cwd / "pro" / "compliance" / "violations.md",
        cwd / "_meta" / "compliance" / "violations.md",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute escalation ladder state from violations.md"
    )
    parser.add_argument(
        "--violations",
        type=Path,
        default=None,
        help="Path to violations.md (auto-detected if omitted)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable text",
    )
    args = parser.parse_args()

    path = args.violations or resolve_violations_path(Path.cwd())
    if path is None or not path.exists():
        print(
            "❌ violations.md not found. Specify --violations PATH.",
            file=sys.stderr,
        )
        return 2

    rows = parse_violations(path)
    stats = compute_escalations(rows)

    if args.json:
        print(json.dumps(stats, indent=2))
        return 0

    # Human-readable output
    print(f"📊 Compliance Stats · {path}")
    print(f"   Computed at: {stats['computed_at']}")
    print()
    print(f"Total violations (lifetime): {sum(stats['by_type_lifetime'].values())}")
    print(f"Unresolved (false / partial): {stats['unresolved_count']}")
    print()
    print("By type (lifetime):")
    for t, c in sorted(stats["by_type_lifetime"].items()):
        print(f"  {t}: {c}")
    print()
    print("Active in last 30 days:")
    if stats["active_30d"]:
        for t, c in sorted(stats["active_30d"].items()):
            print(f"  {t}: {c}")
    else:
        print("  (none)")
    print()
    print("Active in last 90 days:")
    if stats["active_90d"]:
        for t, c in sorted(stats["active_90d"].items()):
            print(f"  {t}: {c}")
    else:
        print("  (none)")
    print()
    if stats["escalations_active"]:
        print("🚨 Escalations active:")
        for esc in stats["escalations_active"]:
            print(
                f"  · Type {esc['type']}: {esc['actual_count']} in last "
                f"{esc['window_days']}d (threshold {esc['threshold_count']}) "
                f"→ {esc['description']}"
            )
    else:
        print("✅ No escalations active.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
