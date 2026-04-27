"""Life OS · spec_compliance_report (v1.8.0).

Scans lifeos spec files for "automation promises" (周期性 / 每天 / 每周 / 每月
/ scheduled / cron 等关键词), then scans _meta/eval-history/ for actual
execution evidence. Outputs a compliance report comparing promised vs actual.

Run via:
    python -m tools.spec_compliance_report --root .

Output: _meta/eval-history/spec-compliance-{YYYY-MM-DD}.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ─── Promise detection ────────────────────────────────────────────────────────

PROMISE_PATTERNS = [
    # English
    (r"\bdaily\b", "daily"),
    (r"\bweekly\b", "weekly"),
    (r"\bmonthly\b", "monthly"),
    (r"\bauto[-\s]?trigger", "auto"),
    (r"\bbackground\b", "auto"),
    (r"\bscheduled\b", "scheduled"),
    (r"\bperiodic", "periodic"),
    (r"every[\s_]+(\d+\s*)?(hour|day|week|month)", "periodic"),
    # 中文
    (r"每天", "daily"),
    (r"每周", "weekly"),
    (r"每月", "monthly"),
    (r"周期性", "periodic"),
    (r"自动触发", "auto"),
    (r"自动跑", "auto"),
    (r"后台", "auto"),
    # 日本語
    (r"毎日", "daily"),
    (r"毎週", "weekly"),
    (r"毎月", "monthly"),
    (r"自動的", "auto"),
]

PROMISE_RE = [(re.compile(pat, re.IGNORECASE), tag) for pat, tag in PROMISE_PATTERNS]


@dataclass
class Promise:
    spec_file: str
    line_no: int
    line_text: str
    tag: str
    expected_freq: str = "?"


@dataclass
class Evidence:
    name: str
    runs: list[datetime] = field(default_factory=list)
    successes: int = 0
    failures: int = 0


def scan_specs(root: Path) -> list[Promise]:
    """Scan spec files for automation promises."""
    promises: list[Promise] = []
    spec_dirs = [
        root / "pro" / "agents",
        root / "pro",
        root / "references",
    ]
    for sd in spec_dirs:
        if not sd.is_dir():
            continue
        for md in sd.rglob("*.md"):
            try:
                lines = md.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in enumerate(lines, 1):
                for pat, tag in PROMISE_RE:
                    if pat.search(line):
                        rel = str(md.relative_to(root))
                        promises.append(
                            Promise(
                                spec_file=rel,
                                line_no=i,
                                line_text=line.strip()[:200],
                                tag=tag,
                                expected_freq=tag,
                            )
                        )
                        break
    return promises


def scan_evidence(root: Path) -> dict[str, Evidence]:
    """Scan _meta/eval-history/cron-runs/ + _meta/runtime/ for actual runs."""
    evidence: dict[str, Evidence] = defaultdict(lambda: Evidence(name=""))

    cron_runs_dir = root / "_meta" / "eval-history" / "cron-runs"
    if cron_runs_dir.is_dir():
        for log in cron_runs_dir.rglob("*"):
            if not log.is_file():
                continue
            name = log.stem.split("-")[0]
            ev = evidence[name]
            ev.name = name
            try:
                ts = datetime.fromtimestamp(log.stat().st_mtime, tz=timezone.utc)
                ev.runs.append(ts)
            except OSError:
                continue
            if "FAIL" in log.name.upper():
                ev.failures += 1
            else:
                ev.successes += 1

    runtime_dir = root / "_meta" / "runtime"
    if runtime_dir.is_dir():
        for sid_dir in runtime_dir.iterdir():
            if not sid_dir.is_dir():
                continue
            for trail in sid_dir.glob("*.json"):
                name = trail.stem
                ev = evidence[name]
                ev.name = name
                try:
                    data = json.loads(trail.read_text(encoding="utf-8"))
                    ts_str = data.get("ended_at") or data.get("started_at")
                    if ts_str:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        ev.runs.append(ts)
                    if data.get("degraded"):
                        ev.failures += 1
                    else:
                        ev.successes += 1
                except (OSError, json.JSONDecodeError, ValueError):
                    continue

    return dict(evidence)


def expected_runs_in_window(freq: str, window_days: int) -> float:
    """How many times should this fire in the given window?"""
    if freq == "daily":
        return float(window_days)
    if freq == "weekly":
        return window_days / 7.0
    if freq == "monthly":
        return window_days / 30.0
    if freq in ("auto", "periodic", "scheduled"):
        return window_days * 10.0
    return float(window_days)


def compliance_index(
    promises: list[Promise], evidence: dict[str, Evidence], window_days: int = 30
) -> tuple[float, list[dict]]:
    """Compute compliance index for each promise."""
    rows = []
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=window_days)

    by_file: dict[str, list[Promise]] = defaultdict(list)
    for p in promises:
        by_file[p.spec_file].append(p)

    total_score = 0.0
    total_weight = 0.0

    for spec_file, plist in sorted(by_file.items()):
        tags = {p.tag for p in plist}
        if "monthly" in tags:
            freq = "monthly"
        elif "weekly" in tags:
            freq = "weekly"
        elif "daily" in tags:
            freq = "daily"
        elif "scheduled" in tags or "periodic" in tags:
            freq = "periodic"
        elif "auto" in tags:
            freq = "auto"
        else:
            freq = "?"

        expected = expected_runs_in_window(freq, window_days)

        agent_name = Path(spec_file).stem
        actual_runs = 0
        for ev_name, ev in evidence.items():
            if ev_name.startswith(agent_name) or agent_name.startswith(ev_name):
                actual_runs += sum(1 for ts in ev.runs if ts >= cutoff)

        ratio = min(actual_runs / expected, 1.0) if expected > 0 else 0.0
        weight = 1.0
        total_score += ratio * weight
        total_weight += weight

        status = "OK" if ratio >= 0.8 else ("WARN" if ratio >= 0.3 else "FAIL")

        rows.append(
            {
                "spec_file": spec_file,
                "freq": freq,
                "promises": len(plist),
                "expected": round(expected, 1),
                "actual": actual_runs,
                "ratio_pct": round(ratio * 100, 0),
                "status": status,
            }
        )

    overall = (total_score / total_weight * 100) if total_weight > 0 else 0.0
    return overall, rows


def render_report(
    overall_index: float,
    rows: list[dict],
    promises: list[Promise],
    window_days: int,
    out_path: Path,
) -> None:
    """Render markdown report."""
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = []
    lines.append(f"# Spec Compliance Report · {today}")
    lines.append("")
    lines.append(f"Window: last {window_days} days")
    lines.append(f"Overall compliance index: **{overall_index:.0f}%**")
    lines.append("")
    lines.append("## Per-spec status")
    lines.append("")
    lines.append("| Spec file | Freq | Promises | Expected | Actual | % | Status |")
    lines.append("|-----------|------|----------|----------|--------|---|--------|")
    for r in sorted(rows, key=lambda x: x["ratio_pct"]):
        lines.append(
            f"| `{r['spec_file']}` | {r['freq']} | {r['promises']} | "
            f"{r['expected']} | {r['actual']} | {r['ratio_pct']:.0f}% | {r['status']} |"
        )
    lines.append("")
    lines.append("## Promises detail (top 20)")
    lines.append("")
    seen = set()
    count = 0
    for p in promises:
        key = (p.spec_file, p.tag)
        if key in seen:
            continue
        seen.add(key)
        count += 1
        if count > 20:
            break
        lines.append(f"- `{p.spec_file}:{p.line_no}` ({p.tag}): {p.line_text}")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "Compliance index is heuristic — it counts promise mentions in spec vs "
        "execution evidence in `_meta/eval-history/cron-runs/` and "
        "`_meta/runtime/<sid>/*.json`. False positives expected; use as a trend "
        "indicator not exact metric."
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Life OS spec compliance report")
    parser.add_argument("--root", default=".", help="Repo root")
    parser.add_argument("--window", type=int, default=30, help="Lookback days")
    parser.add_argument(
        "--output",
        default=None,
        help="Output file (default: _meta/eval-history/spec-compliance-{date}.md)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print JSON to stdout in addition to file"
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / "SKILL.md").is_file():
        print(
            f"Error: {root} does not look like a Life OS root (no SKILL.md)",
            file=sys.stderr,
        )
        return 2

    promises = scan_specs(root)
    evidence = scan_evidence(root)
    overall, rows = compliance_index(promises, evidence, args.window)

    if args.output:
        out = Path(args.output)
    else:
        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        out = root / "_meta" / "eval-history" / f"spec-compliance-{today}.md"

    render_report(overall, rows, promises, args.window, out)

    print(f"Spec compliance: {overall:.0f}% (window={args.window}d)")
    print(f"Report: {out}")
    print(f"Promises scanned: {len(promises)}, evidence sources: {len(evidence)}")

    if args.json:
        print(json.dumps({"overall_index": overall, "rows": rows}, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
