"""Life OS · cron_health_report (v1.8.0).

Inspect Life OS cron job execution history (logs + audit trails) and report
on success rate, missed runs, recent failures.

Run via:
    python -m tools.cron_health_report --root .
    python -m tools.cron_health_report --root . --json
    python -m tools.cron_health_report --root . --week

Output: stdout (markdown table by default; JSON if --json)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

JOBS = {
    "reindex": {"freq": "daily", "schedule": "03:00"},
    "daily-briefing": {"freq": "daily", "schedule": "08:00"},
    "backup": {"freq": "weekly", "schedule": "Sun 02:00"},
    "spec-compliance": {"freq": "weekly", "schedule": "Sun 22:00"},
    "wiki-decay": {"freq": "monthly", "schedule": "15th 02:00"},
    "archiver-recovery": {"freq": "daily", "schedule": "23:30"},
    "auditor-mode-2": {"freq": "weekly", "schedule": "Sun 21:00"},
    "advisor-monthly": {"freq": "monthly", "schedule": "1st 06:00"},
    "eval-history-monthly": {"freq": "monthly", "schedule": "1st 07:00"},
    "strategic-consistency": {"freq": "monthly", "schedule": "1st 08:00"},
}


@dataclass
class JobHealth:
    name: str
    freq: str
    schedule: str
    runs_in_window: int
    successes: int
    failures: int
    last_run: str | None
    last_status: str | None
    expected_in_window: float
    health_pct: float


def get_log_dirs() -> list[Path]:
    home = Path.home()
    candidates = [
        home / "Library" / "Logs" / "LifeOS" / "hermes-local",
        home / ".local" / "state" / "lifeos" / "hermes-local",
    ]
    if "XDG_STATE_HOME" in os.environ:
        candidates.append(
            Path(os.environ["XDG_STATE_HOME"]) / "lifeos" / "hermes-local"
        )
    return [d for d in candidates if d.is_dir()]


def scan_logs(
    log_dirs: Iterable[Path], cutoff: datetime
) -> dict[str, list[tuple[datetime, bool]]]:
    runs: dict[str, list[tuple[datetime, bool]]] = {}
    for ld in log_dirs:
        for log in ld.rglob("*"):
            if not log.is_file():
                continue
            try:
                mtime = datetime.fromtimestamp(log.stat().st_mtime, tz=timezone.utc)
            except OSError:
                continue
            if mtime < cutoff:
                continue
            stem = log.stem
            for job_name in JOBS:
                if stem.startswith(job_name):
                    fail = "FAIL" in log.name.upper() or "fail" in log.name
                    runs.setdefault(job_name, []).append((mtime, not fail))
                    break
    return runs


def expected_in_window(freq: str, days: int) -> float:
    if freq == "daily":
        return float(days)
    if freq == "weekly":
        return days / 7.0
    if freq == "monthly":
        return days / 30.0
    return float(days)


def assess_health(
    runs: dict[str, list[tuple[datetime, bool]]], window_days: int
) -> list[JobHealth]:
    out: list[JobHealth] = []
    for name, meta in JOBS.items():
        job_runs = runs.get(name, [])
        sc = sum(1 for _, ok in job_runs if ok)
        fl = sum(1 for _, ok in job_runs if not ok)
        expected = expected_in_window(meta["freq"], window_days)
        actual_total = len(job_runs)
        health = (
            min(sc / expected, 1.0) * 100
            if expected > 0
            else (100.0 if actual_total == 0 else 0.0)
        )
        last_ts = max((ts for ts, _ in job_runs), default=None)
        last_status = None
        if last_ts is not None:
            for _, ok in sorted(job_runs, key=lambda x: x[0], reverse=True):
                last_status = "success" if ok else "failure"
                break
        out.append(
            JobHealth(
                name=name,
                freq=meta["freq"],
                schedule=meta["schedule"],
                runs_in_window=actual_total,
                successes=sc,
                failures=fl,
                last_run=last_ts.isoformat() if last_ts else None,
                last_status=last_status,
                expected_in_window=round(expected, 1),
                health_pct=round(health, 0),
            )
        )
    return out


def render_markdown(health: list[JobHealth], window_days: int) -> str:
    lines: list[str] = []
    lines.append(f"# Cron Health Report · last {window_days} days")
    lines.append("")
    avg = sum(h.health_pct for h in health) / len(health) if health else 0
    lines.append(f"Average health: **{avg:.0f}%**")
    lines.append("")
    lines.append(
        "| Job | Schedule | Expected | Actual | OK | Fail | Health | Last run |"
    )
    lines.append(
        "|-----|----------|----------|--------|----|------|--------|----------|"
    )
    for h in sorted(health, key=lambda x: x.health_pct):
        last = h.last_run or "never"
        if last != "never":
            last = last.split("T")[0]
        lines.append(
            f"| {h.name} | {h.schedule} | {h.expected_in_window} | "
            f"{h.runs_in_window} | {h.successes} | {h.failures} | "
            f"{h.health_pct:.0f}% | {last} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- Health = successes / expected (capped at 100%). 100% = OK; "
        "<80% means missed runs or failures."
    )
    lines.append(
        "- A job at 0% with 0 actual runs has either never been installed or "
        "its scheduler missed every window."
    )
    lines.append(
        "- To install missing jobs: `bash scripts/setup-cron.sh install`. To "
        "trigger one immediately: `bash scripts/run-cron-now.sh <job-name>`."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Life OS cron health report")
    parser.add_argument("--root", default=".", help="Repo root (for compatibility)")
    parser.add_argument("--window", type=int, default=30, help="Lookback days")
    parser.add_argument("--week", action="store_true", help="Shortcut for --window 7")
    parser.add_argument("--month", action="store_true", help="Shortcut for --window 30")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    args = parser.parse_args(argv)

    if args.week:
        window_days = 7
    elif args.month:
        window_days = 30
    else:
        window_days = args.window

    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=window_days)
    log_dirs = get_log_dirs()
    if not log_dirs:
        print("No log directories found. Run setup-cron.sh first.", file=sys.stderr)
        return 1

    runs = scan_logs(log_dirs, cutoff)
    health = assess_health(runs, window_days)

    if args.json:
        print(json.dumps([asdict(h) for h in health], indent=2))
    else:
        print(render_markdown(health, window_days))

    return 0


if __name__ == "__main__":
    sys.exit(main())
