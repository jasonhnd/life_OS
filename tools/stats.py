#!/usr/bin/env python3
"""Compliance violation statistics + usage/quality aggregates (v1.7 §6.3).

The tool keeps its original compliance-violation output (backward
compatible with v1.6.x invocations) and adds v1.7 aggregates across
``_meta/sessions/`` (session count, avg overall_score, domain
distribution, DREAM trigger frequency, top concept tags).

Usage::

    # Legacy compliance mode (unchanged behaviour)
    uv run tools/stats.py [--violations PATH] [--json]

    # v1.7 aggregate mode
    uv run tools/stats.py [--period month|quarter|year] [--since YYYY-MM-DD]
                          [--output FILE] [--root PATH]

Default when neither ``--violations`` nor any v1.7 flag is provided:
scan the current repo for both kinds of data and report whichever is
available. Empty periods exit 0 with a ``no data`` notice (not an error).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.second_brain import load_markdown  # noqa: E402

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


def parse_violations(violations_path: Path) -> list[dict[str, Any]]:
    """Parse violations.md into a list of structured records.

    Returns list of dicts with keys: timestamp, trigger, type, severity,
    details, resolved, parsed_dt (datetime or None on parse failure).

    Skips: header row, separator, code blocks (format examples), rows whose
    type field doesn't look like a valid type code (A1/A2/A3/B/C/D/E/F).
    """
    if not violations_path.exists():
        return []
    rows: list[dict[str, Any]] = []
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


def compute_escalations(
    rows: list[dict[str, Any]], now: datetime | None = None
) -> dict[str, Any]:
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

    all_by_type: Counter[str] = Counter()
    active_30d: Counter[str] = Counter()
    active_90d: Counter[str] = Counter()
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

    escalations: list[dict[str, Any]] = []
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


# ─── v1.7 aggregates (§6.3) ─────────────────────────────────────────────────


_PERIOD_DAYS: dict[str, int] = {
    "month": 30,
    "quarter": 90,
    "year": 365,
}


def parse_period_filter(
    *,
    period: str | None,
    since: str | None,
    now: datetime | None = None,
) -> datetime:
    """Resolve the effective ``since`` datetime from CLI flags.

    Precedence: ``--since`` > ``--period`` > default (``period=month``).

    ``now`` is accepted for test determinism.
    """
    current = now or datetime.now()
    if since:
        try:
            return datetime.fromisoformat(since)
        except ValueError as exc:
            raise ValueError(f"Invalid --since value {since!r}: {exc}") from exc
    window_days = _PERIOD_DAYS.get(period or "month", 30)
    return current - timedelta(days=window_days)


@dataclass(frozen=True)
class SessionRow:
    """Lightweight view of one session summary for aggregate computations."""

    session_id: str
    date: date
    project: str
    overall_score: float | None
    domains_activated: tuple[str, ...]
    concepts_activated: tuple[str, ...]
    dream_triggers: tuple[str, ...]


def _load_session_row(path: Path) -> SessionRow | None:
    """Parse a session summary file into a SessionRow, or None on failure."""
    try:
        parsed = load_markdown(path)
    except (ValueError, OSError):
        return None
    fm = parsed.frontmatter
    if not fm:
        return None
    raw_date = fm.get("date")
    if isinstance(raw_date, date):
        date_val = raw_date
    elif isinstance(raw_date, str):
        try:
            date_val = date.fromisoformat(raw_date)
        except ValueError:
            return None
    else:
        return None

    score_raw = fm.get("overall_score")
    if isinstance(score_raw, bool):
        score: float | None = None
    elif isinstance(score_raw, (int, float)):
        score = float(score_raw)
    else:
        score = None

    def _tuple(key: str) -> tuple[str, ...]:
        v = fm.get(key) or []
        if isinstance(v, list):
            return tuple(str(x) for x in v)
        return ()

    return SessionRow(
        session_id=str(fm.get("session_id", path.stem)),
        date=date_val,
        project=str(fm.get("project", "")),
        overall_score=score,
        domains_activated=_tuple("domains_activated"),
        concepts_activated=_tuple("concepts_activated"),
        dream_triggers=_tuple("dream_triggers"),
    )


def _iter_session_rows(sessions_dir: Path, *, since: datetime) -> list[SessionRow]:
    """Yield SessionRow objects whose ``date`` is on or after ``since``."""
    if not sessions_dir.exists():
        return []
    threshold = since.date()
    results: list[SessionRow] = []
    for path in sorted(sessions_dir.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        row = _load_session_row(path)
        if row is None:
            continue
        if row.date < threshold:
            continue
        results.append(row)
    return results


def compute_session_aggregates(
    sessions_dir: Path, *, since: datetime
) -> dict[str, object]:
    """Return ``{count, avg_overall_score, by_project}``."""
    rows = _iter_session_rows(sessions_dir, since=since)
    scores = [r.overall_score for r in rows if r.overall_score is not None]
    avg = (sum(scores) / len(scores)) if scores else None
    by_project: Counter[str] = Counter(r.project for r in rows if r.project)
    return {
        "count": len(rows),
        "avg_overall_score": avg,
        "by_project": dict(by_project),
    }


def compute_domain_distribution(
    sessions_dir: Path, *, since: datetime
) -> dict[str, int]:
    """Return ``{domain: count}`` across all sessions in window."""
    rows = _iter_session_rows(sessions_dir, since=since)
    counter: Counter[str] = Counter()
    for row in rows:
        counter.update(row.domains_activated)
    return dict(counter)


def compute_top_concept_tags(
    sessions_dir: Path, *, since: datetime, top_n: int = 3
) -> list[tuple[str, int]]:
    """Return the top-N concepts (as ``(tag, count)`` tuples)."""
    rows = _iter_session_rows(sessions_dir, since=since)
    counter: Counter[str] = Counter()
    for row in rows:
        counter.update(row.concepts_activated)
    return counter.most_common(top_n)


def compute_dream_trigger_frequency(
    sessions_dir: Path, *, since: datetime
) -> dict[str, int]:
    """Return ``{trigger: count}`` for DREAM triggers in window."""
    rows = _iter_session_rows(sessions_dir, since=since)
    counter: Counter[str] = Counter()
    for row in rows:
        counter.update(row.dream_triggers)
    return dict(counter)


def compute_soul_tier_trend(
    snapshots_root: Path, *, since: datetime
) -> dict[str, int]:
    """Return ``{tier: count}`` summed across snapshots newer than ``since``.

    Tiers are ``core``, ``secondary``, ``emerging`` (per snapshot-spec.md).
    """
    if not snapshots_root.exists():
        return {}
    tier_counter: Counter[str] = Counter()
    for path in snapshots_root.rglob("*.md"):
        if path.name == "INDEX.md":
            continue
        try:
            parsed = load_markdown(path)
        except (ValueError, OSError):
            continue
        fm = parsed.frontmatter or {}
        # Filter by captured_at if present, else by filename date
        captured = fm.get("captured_at")
        captured_dt: datetime | None = None
        if isinstance(captured, datetime):
            captured_dt = captured
        elif isinstance(captured, str):
            try:
                captured_dt = datetime.fromisoformat(captured)
            except ValueError:
                captured_dt = None
        if captured_dt is not None and captured_dt < since:
            continue
        dims = fm.get("dimensions") or []
        if isinstance(dims, list):
            for dim in dims:
                if isinstance(dim, dict):
                    tier = dim.get("tier")
                    if isinstance(tier, str):
                        tier_counter[tier] += 1
    return dict(tier_counter)


def compute_eval_dimension_averages(
    eval_root: Path, *, since: datetime
) -> dict[str, float]:
    """Return ``{dimension: avg_score}`` across eval-history newer than ``since``."""
    if not eval_root.exists():
        return {}
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    threshold = since.date()
    for path in eval_root.rglob("*.md"):
        if path.name == "INDEX.md":
            continue
        try:
            parsed = load_markdown(path)
        except (ValueError, OSError):
            continue
        fm = parsed.frontmatter or {}
        raw_date = fm.get("date")
        if isinstance(raw_date, date):
            date_val = raw_date
        elif isinstance(raw_date, str):
            try:
                date_val = date.fromisoformat(raw_date)
            except ValueError:
                continue
        else:
            continue
        if date_val < threshold:
            continue
        metrics = fm.get("metrics") or {}
        if isinstance(metrics, dict):
            for dim, score in metrics.items():
                if isinstance(score, (int, float)) and not isinstance(score, bool):
                    totals[dim] = totals.get(dim, 0.0) + float(score)
                    counts[dim] = counts.get(dim, 0) + 1
    return {dim: totals[dim] / counts[dim] for dim in totals if counts[dim] > 0}


def aggregate_stats(root: Path, *, since: datetime) -> dict[str, object]:
    """Compute all v1.7 aggregates for the given second-brain root and window."""
    sessions_dir = root / "_meta" / "sessions"
    snapshots_root = root / "_meta" / "snapshots"
    eval_root = root / "_meta" / "eval-history"

    session_agg = compute_session_aggregates(sessions_dir, since=since)
    return {
        "since": since.isoformat(),
        "session_count": session_agg["count"],
        "avg_overall_score": session_agg["avg_overall_score"],
        "by_project": session_agg["by_project"],
        "domain_distribution": compute_domain_distribution(
            sessions_dir, since=since
        ),
        "top_concept_tags": compute_top_concept_tags(sessions_dir, since=since),
        "dream_trigger_frequency": compute_dream_trigger_frequency(
            sessions_dir, since=since
        ),
        "soul_tier_trend": compute_soul_tier_trend(snapshots_root, since=since),
        "eval_dimension_averages": compute_eval_dimension_averages(
            eval_root, since=since
        ),
    }


def render_aggregate_report(result: dict[str, object]) -> str:
    """Render aggregate_stats() output as markdown."""
    lines: list[str] = [
        "# Life OS Stats",
        "",
        f"_Since: {result['since']}_",
        "",
        f"- Session count: {result['session_count']}",
    ]
    avg = result["avg_overall_score"]
    lines.append(
        f"- Avg overall_score: {avg:.2f}"
        if isinstance(avg, (int, float))
        else "- Avg overall_score: n/a"
    )

    def section(title: str, mapping: dict[str, object]) -> None:
        lines.append("")
        lines.append(f"## {title}")
        lines.append("")
        if not mapping:
            lines.append("_(none)_")
            return
        for key, val in sorted(mapping.items()):
            lines.append(f"- {key}: {val}")

    section("Domain distribution", result["domain_distribution"])  # type: ignore[arg-type]
    section("DREAM trigger frequency", result["dream_trigger_frequency"])  # type: ignore[arg-type]
    section("SOUL tier trend", result["soul_tier_trend"])  # type: ignore[arg-type]

    lines.append("")
    lines.append("## Top concept tags")
    lines.append("")
    tags = result["top_concept_tags"]
    if isinstance(tags, list) and tags:
        for tag, count in tags:
            lines.append(f"- {tag}: {count}")
    else:
        lines.append("_(none)_")

    eval_avgs = result["eval_dimension_averages"]
    lines.append("")
    lines.append("## Eval dimension averages")
    lines.append("")
    if isinstance(eval_avgs, dict) and eval_avgs:
        for dim, avg_score in sorted(eval_avgs.items()):
            lines.append(f"- {dim}: {avg_score:.2f}")
    else:
        lines.append("_(none)_")

    return "\n".join(lines).rstrip() + "\n"


# ─── CLI ────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stats",
        description=(
            "Report compliance-violation escalations and/or Life OS usage + "
            "quality aggregates."
        ),
    )
    parser.add_argument(
        "--violations",
        type=Path,
        default=None,
        help=(
            "Path to violations.md (legacy compliance mode — auto-detected if "
            "omitted). Presence of this flag selects legacy output."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable text (legacy mode only).",
    )
    parser.add_argument(
        "--period",
        choices=sorted(_PERIOD_DAYS.keys()),
        default=None,
        help="Aggregate window (default: month when neither --period nor --since given).",
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Explicit start date (YYYY-MM-DD). Wins over --period.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write the aggregate report to FILE instead of stdout.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Second-brain root (default: cwd).",
    )
    return parser


def _run_legacy_compliance(
    explicit_path: Path | None, as_json: bool
) -> int:
    """Execute the pre-v1.7 compliance output path."""
    path = explicit_path or resolve_violations_path(Path.cwd())
    if path is None or not path.exists():
        print(
            "❌ violations.md not found. Specify --violations PATH.",
            file=sys.stderr,
        )
        return 2

    rows = parse_violations(path)
    stats = compute_escalations(rows)

    if as_json:
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


def _run_aggregate(args: argparse.Namespace) -> int:
    """Execute the v1.7 aggregate report path."""
    root = args.root or Path.cwd()
    try:
        since = parse_period_filter(period=args.period, since=args.since)
    except ValueError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    result = aggregate_stats(root, since=since)

    if result["session_count"] == 0 and not result["eval_dimension_averages"]:
        message = f"no data in window since {since.date().isoformat()}\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(message, encoding="utf-8")
        else:
            print(message, end="")
        return 0

    report = render_aggregate_report(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point — returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Legacy compliance mode is selected when --violations is passed
    # explicitly. Every v1.7 flag (--period/--since/--output/--root) or
    # the default no-argument invocation falls into the aggregate path.
    if args.violations is not None:
        return _run_legacy_compliance(args.violations, args.json)
    if args.period is None and args.since is None and args.output is None \
            and args.root is None and not args.json:
        # No flags at all — keep the pre-v1.7 default: try auto-detecting
        # violations.md first; if found, use legacy output; otherwise fall
        # through to the aggregate report.
        auto_path = resolve_violations_path(Path.cwd())
        if auto_path is not None:
            return _run_legacy_compliance(auto_path, as_json=False)
    return _run_aggregate(args)


if __name__ == "__main__":
    sys.exit(main())
