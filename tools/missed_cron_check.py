"""Life OS · missed_cron_check (v1.8.0).

Run via launchd RunAtLoad on Mac wake / boot. Detects which cron jobs missed
their schedule (because computer was asleep / powered off) and triggers
recovery for any critical missed jobs.

Run via:
    python -m tools.missed_cron_check --root .

Output: stdout summary; appends to _meta/inbox/notifications.md if missed jobs.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

JOBS = {
    "reindex": {"freq_hours": 24, "critical": False, "grace_hours": 6},
    "daily-briefing": {"freq_hours": 24, "critical": True, "grace_hours": 2},
    "backup": {"freq_hours": 24 * 7, "critical": False, "grace_hours": 24},
    "spec-compliance": {"freq_hours": 24 * 7, "critical": False, "grace_hours": 12},
    "wiki-decay": {"freq_hours": 24 * 30, "critical": False, "grace_hours": 24},
    "archiver-recovery": {"freq_hours": 24, "critical": True, "grace_hours": 4},
    "auditor-mode-2": {"freq_hours": 24 * 7, "critical": False, "grace_hours": 24},
    "advisor-monthly": {"freq_hours": 24 * 30, "critical": False, "grace_hours": 24},
    "eval-history-monthly": {
        "freq_hours": 24 * 30,
        "critical": False,
        "grace_hours": 24,
    },
    "strategic-consistency": {
        "freq_hours": 24 * 30,
        "critical": False,
        "grace_hours": 24,
    },
}


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


def last_run_time(log_dirs: list[Path], job: str) -> datetime | None:
    latest: datetime | None = None
    for ld in log_dirs:
        for log in ld.rglob("*"):
            if not log.is_file():
                continue
            if not log.stem.startswith(job):
                continue
            try:
                ts = datetime.fromtimestamp(log.stat().st_mtime, tz=timezone.utc)
            except OSError:
                continue
            if latest is None or ts > latest:
                latest = ts
    return latest


def find_missed(
    log_dirs: list[Path],
) -> list[tuple[str, dict, datetime | None]]:
    missed: list[tuple[str, dict, datetime | None]] = []
    now = datetime.now(tz=timezone.utc)
    for name, meta in JOBS.items():
        last = last_run_time(log_dirs, name)
        if last is None:
            missed.append((name, meta, None))
            continue
        gap = now - last
        threshold = timedelta(hours=meta["freq_hours"] + meta["grace_hours"])
        if gap > threshold:
            missed.append((name, meta, last))
    return missed


def trigger_recovery(repo_root: Path, job: str) -> tuple[bool, str]:
    script = repo_root / "scripts" / "run-cron-now.sh"
    if not script.is_file():
        return False, f"run-cron-now.sh not found at {script}"
    try:
        result = subprocess.run(
            ["bash", str(script), job],
            check=False,
            capture_output=True,
            text=True,
            timeout=600,
        )
        ok = result.returncode == 0
        msg = (result.stdout or "")[-500:] + (
            ("\nSTDERR: " + result.stderr[-300:]) if result.stderr else ""
        )
        return ok, msg
    except subprocess.TimeoutExpired:
        return False, "Recovery timed out after 10 minutes"
    except (OSError, subprocess.SubprocessError) as e:
        return False, f"Recovery error: {e}"


def append_notification(repo_root: Path, line: str) -> None:
    inbox_dir = repo_root / "_meta" / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    notif = inbox_dir / "notifications.md"
    with notif.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Life OS missed cron check")
    parser.add_argument("--root", default=".", help="Repo root")
    parser.add_argument(
        "--no-recover",
        action="store_true",
        help="Detect only, do not trigger recovery for critical jobs",
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce stdout output")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / "SKILL.md").is_file():
        print(
            f"Error: {root} does not look like a Life OS root (no SKILL.md)",
            file=sys.stderr,
        )
        return 2

    log_dirs = get_log_dirs()
    if not log_dirs:
        if not args.quiet:
            print("No log directories yet — run setup-cron.sh first.")
        return 0

    missed = find_missed(log_dirs)
    if not missed:
        if not args.quiet:
            print("All cron jobs on schedule. No catch-up needed.")
        return 0

    now_iso = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    print(f"Missed jobs ({len(missed)}):")
    for name, meta, last in missed:
        last_str = last.isoformat() if last else "never"
        crit = "CRITICAL" if meta["critical"] else "non-critical"
        print(f"  - {name} ({crit}, freq {meta['freq_hours']}h, last={last_str})")

    recovery_summary: list[str] = []
    if not args.no_recover:
        for name, meta, _ in missed:
            if not meta["critical"]:
                continue
            print(f"Triggering recovery for {name}...")
            ok, msg = trigger_recovery(root, name)
            status = "OK" if ok else "FAIL"
            recovery_summary.append(f"  - {name}: {status}")
            if not ok:
                print(f"    Error: {msg[:200]}")

    notif_line = f"[{now_iso}] launchd missed-cron-check: {len(missed)} missed"
    if recovery_summary:
        notif_line += " · recovery=" + ",".join(
            [n.split(":")[0].strip().lstrip("- ") for n in recovery_summary]
        )
    notif_line += " (see tools.missed_cron_check)"
    append_notification(root, notif_line)

    return 0


if __name__ == "__main__":
    sys.exit(main())
