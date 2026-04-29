#!/usr/bin/env python3
"""Notion fallback sync — retry archiver Phase 4 outside a live session.

Spec: references/tools-spec.md §6.11.

Reads ``_meta/notion-sync-log.md`` for entries whose status is
``pending`` or ``failed``, then calls
:meth:`tools.lib.notion.NotionClient.upsert_page` for each. Per-page
try/except keeps one failure from blocking the rest. Result rows are
appended back to the log with timestamps and reason strings.

Usage:
    uv run tools/sync_notion.py [--retry] [--since YYYY-MM-DD]
                                [--verbose] [--notion-token TOKEN]

Token resolution (highest priority first):
    1. ``--notion-token`` CLI flag
    2. ``NOTION_TOKEN`` environment variable
    3. ``[notion] token_env_var`` in ``~/second-brain/.life-os.toml``

Exit codes:
    0  all synced successfully (includes "nothing to sync")
    1  any page failed
    2  auth failure or missing token
    3  network unreachable
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.config import load_config  # noqa: E402
from tools.lib.notion import (  # noqa: E402
    NotionAuthError,
    NotionClient,
    NotionError,
    resolve_token,
)

_LOG_RELATIVE_PATH = Path("_meta") / "notion-sync-log.md"


# ─── Log parsing + serialisation ────────────────────────────────────────────


@dataclass(frozen=True)
class SyncEntry:
    """One row from ``_meta/notion-sync-log.md``."""

    date: date
    life_os_id: str
    database_id: str
    status: str  # pending | failed | synced | ...


def parse_pending_entries(
    log_path: Path,
    *,
    since: date | None = None,
) -> list[SyncEntry]:
    """Parse ``log_path`` and return entries with status != 'synced'.

    Missing log → empty list (caller treats as clean success).
    Malformed rows are skipped with a stderr warning.
    """
    if not log_path.is_file():
        return []
    content = log_path.read_text(encoding="utf-8")
    entries: list[SyncEntry] = []
    for line in content.splitlines():
        row = line.strip()
        if not row.startswith("|"):
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        # Skip header / separator / rows with wrong column count.
        if len(cells) < 4:
            continue
        if cells[0].lower() in {"date", "---"} or cells[0].startswith("-"):
            continue
        try:
            parsed_date = date.fromisoformat(cells[0])
        except ValueError:
            continue
        life_os_id = cells[1]
        database_id = cells[2]
        status = cells[3].lower()
        if not life_os_id or not database_id:
            continue
        if status in {"synced", "ok", "done"}:
            continue
        if since is not None and parsed_date < since:
            continue
        entries.append(
            SyncEntry(
                date=parsed_date,
                life_os_id=life_os_id,
                database_id=database_id,
                status=status,
            )
        )
    return entries


def append_log_result(
    log_path: Path,
    entry: SyncEntry,
    *,
    new_status: str,
    message: str,
) -> None:
    """Append a result row to ``log_path`` with an ISO-8601 timestamp."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    existing = ""
    if log_path.is_file():
        existing = log_path.read_text(encoding="utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
    timestamp = datetime.now(UTC).isoformat(timespec="seconds")
    reason = message.replace("|", "/").replace("\n", " ").strip() or "-"
    row = (
        f"| {entry.date.isoformat()} | {entry.life_os_id} | {entry.database_id} "
        f"| {new_status} | {timestamp} | {reason} |\n"
    )
    log_path.write_text(existing + row, encoding="utf-8")


# ─── Notion client construction (hook for tests) ────────────────────────────


def _build_client(
    token: str, workspace_id: str | None
) -> NotionClient:  # pragma: no cover -- monkeypatched in tests
    return NotionClient(token=token, workspace_id=workspace_id)


def _build_properties(entry: SyncEntry) -> dict[str, Any]:
    """Derive a minimal Notion property payload from a log entry.

    The archiver spec leaves per-database property shapes to the caller;
    this tool's job is the transport retry, not schema translation. We
    stamp the life_os_id (already injected by NotionClient.upsert_page)
    and a synced_at date; the archiver writes richer properties during
    the happy-path sync.
    """
    return {
        "synced_at": {"date": {"start": datetime.now(UTC).isoformat()}},
    }


# ─── Main orchestration ─────────────────────────────────────────────────────


def _classify_failure(exc: BaseException) -> tuple[int, str]:
    """Return (exit-code-candidate, one-line reason)."""
    if isinstance(exc, NotionAuthError):
        return 2, f"auth: {exc}"
    if isinstance(exc, OSError):
        return 3, f"network: {exc}"
    if isinstance(exc, NotionError):
        return 1, str(exc)
    return 1, f"unexpected: {exc}"


def run(
    *,
    root: Path,
    cli_token: str | None,
    since: date | None,
    verbose: bool,
) -> int:
    """Retry pending Notion sync entries. Returns the CLI exit code."""
    log_path = root / _LOG_RELATIVE_PATH
    entries = parse_pending_entries(log_path, since=since)
    if not entries:
        if verbose:
            print("[sync_notion] nothing to sync")
        return 0

    config = load_config(root=root)

    try:
        token = resolve_token(cli_token=cli_token or None, config=config)
    except NotionAuthError as exc:
        print(f"[sync_notion] auth error: {exc}", file=sys.stderr)
        return 2

    client = _build_client(token=token, workspace_id=config.notion_workspace_id)

    failures = 0
    worst_exit_code = 0

    for entry in entries:
        try:
            client.upsert_page(
                database_id=entry.database_id,
                life_os_id=entry.life_os_id,
                properties=_build_properties(entry),
                body=None,
            )
        except (KeyboardInterrupt, SystemExit):
            # Re-raise interpreter-level signals — they should propagate up
            # so the user can Ctrl-C out and exit codes from sys.exit() flow
            # correctly. Previous BaseException catch swallowed both,
            # turning Ctrl-C into a "page failed" log entry. R-1.8.0-013 fix.
            raise
        except Exception as exc:  # noqa: BLE001 -- per-page isolation
            code, reason = _classify_failure(exc)
            failures += 1
            worst_exit_code = max(worst_exit_code, code)
            append_log_result(
                log_path, entry, new_status="failed", message=reason
            )
            if verbose:
                print(
                    f"[sync_notion] FAIL {entry.life_os_id}: {reason}",
                    file=sys.stderr,
                )
        else:
            append_log_result(
                log_path, entry, new_status="synced", message=""
            )
            if verbose:
                print(f"[sync_notion] OK   {entry.life_os_id}")

    if failures == 0:
        return 0
    return worst_exit_code


# ─── CLI ────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Retry Notion sync outside a live Claude Code session.",
    )
    parser.add_argument(
        "--retry",
        action="store_true",
        help=(
            "Reserved flag; this tool always retries pending/failed entries. "
            "Accepted for forward compatibility with driving scripts."
        ),
    )
    parser.add_argument(
        "--since",
        type=date.fromisoformat,
        default=None,
        help="Only retry entries dated on/after YYYY-MM-DD.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-page status lines.",
    )
    parser.add_argument(
        "--notion-token",
        dest="notion_token",
        default=None,
        help="Notion integration token (highest precedence).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help=(
            "Second-brain root (default: from config / ~/second-brain). "
            "Primarily for testing."
        ),
    )
    args = parser.parse_args(argv)

    cfg = load_config(root=args.root) if args.root is None else None
    root = args.root if args.root is not None else cfg.second_brain_root  # type: ignore[union-attr]

    return run(
        root=root,
        cli_token=args.notion_token,
        since=args.since,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    sys.exit(main())
