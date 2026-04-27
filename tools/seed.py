#!/usr/bin/env python3
"""New-user second-brain bootstrap.

Per references/tools-spec.md §6.10. Creates an empty-but-valid v1.7
second-brain layout at a target path: SOUL.md skeleton, .life-os.toml
stub, an example project, .gitignore with recommended entries, and the
full ``_meta/`` directory tree (each subdirectory seeded with a
``.gitkeep`` so git picks them up).

Also runs ``git init`` and makes an initial commit so the user can
start tracking from day one.

Usage::

    uv run tools/seed.py --path ~/second-brain

Exit codes:
- ``0`` — second-brain created successfully
- ``1`` — target path exists and is non-empty (refusing to overwrite)
  OR git invocation failed
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Allow running from repo root via ``python3 tools/seed.py``
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ─── File templates ─────────────────────────────────────────────────────────


_GITIGNORE = """# Life OS v1.7 — recommended ignore list
.DS_Store
Thumbs.db
*.tmp
*.swp
*.swo
*~
.idea/
.vscode/
.venv/
__pycache__/
*.log
# Local-only caches
.mypy_cache/
.ruff_cache/
.pytest_cache/
"""


def _life_os_toml(root_path: Path) -> str:
    """Render a minimal .life-os.toml stub.

    The ``second_brain.root`` field echoes the path the user passed
    (expanded). This is parseable by tools.lib.config.load_config.
    """
    return (
        "# Life OS v1.7 — per-user configuration.\n"
        "# All keys are optional; this file can be left empty.\n"
        "\n"
        "[second_brain]\n"
        f'root = "{root_path.as_posix()}"\n'
        "\n"
        "[tools]\n"
        "# backup_dest defaults to <root>/../second-brain-backups\n"
        "# backup_dest = \"~/second-brain-backups\"\n"
        "\n"
        "[search]\n"
        "# Boost sessions newer than this many days in search ranking.\n"
        "recency_boost_days = 90\n"
        "\n"
        "[export]\n"
        "# Default format for `life-os-tool export` when --format is omitted.\n"
        'default_format = "pdf"\n'
        "\n"
        "[reconcile]\n"
        "# Set to true to enable --fix by default (not recommended).\n"
        "auto_fix = false\n"
        "\n"
        "[notion]\n"
        "# Enable only if you want Notion sync. Store the token under the\n"
        "# named environment variable to keep it out of git.\n"
        "# token_env_var = \"LIFE_OS_NOTION_TOKEN\"\n"
        "# workspace_id  = \"\"\n"
    )


_SOUL_MD = """# SOUL · Personal Identity Layer

_(Seeded by `tools/seed.py`. Fill in each section as your second-brain matures.
Dimensions accumulate over time; they do not need to all exist on day one.)_

## Core Values
- _(What principles do you refuse to compromise on?)_

## Decision Style
- _(How do you weigh tradeoffs? Risk tolerance? Reversibility preference?)_

## Working Patterns
- _(What tempo works for you? What makes you sharp or dull?)_

## Boundaries
- _(What you say no to — as a default. Hard limits.)_

## Active Concerns
- _(What problems currently occupy the front of mind?)_

## Dimensions

_(Auto-tracked dimensions will appear here once ADVISOR starts writing
SOUL deltas. For v1.7 they are stored inline as `- name: ... confidence:`
lines under this heading. On day one, this list is intentionally empty.)_
"""


_EXAMPLE_PROJECT = """---
id: example-project
name: Example Project
status: active
created: {created}
owner: you
---

# Example Project

_(This is a seed file — rename the directory, update frontmatter, and start
working.)_

## Summary

One-paragraph description of what this project is for.

## Goals

1. _(first outcome)_
2. _(second outcome)_

## Active Decisions

_(Decision logs are written by the archiver under
`_meta/journal/YYYY-MM-DD-{{project}}.md`. This section is a human-readable
pointer to the most relevant ones.)_

## Notes

- Seeded by `tools/seed.py`. Feel free to delete or rename this project.
"""


_INBOX_NOTIFICATIONS = """# Life OS · Cron Notifications Inbox (v1.8.0)

This file is the **cron → session bridge** target. Background cron jobs
(archiver-recovery, auditor-mode-2, advisor-monthly, etc.) append one-line
notifications here. The `session-start-inbox` hook reads the tail at every
new Claude Code session start and surfaces unread items.

## Format

Each line: `[ISO8601] <emoji> <subagent>: <summary> · see <relative-path>`

Example:
```
[2026-04-28T23:30:00Z] 🌆 archiver-recovery: auto-recovered SID 2026-04-27T1602Z, see _meta/eval-history/recovery/2026-04-27-2330.md
```

## Notes

- Append-only. Do not edit historical lines.
- `session-start-inbox` reads the last 30 lines at session start.
- Older entries can be archived to `_meta/inbox/archive/YYYY-MM.md` if this
  file grows beyond a few hundred lines.
"""


# ─── Scaffolding ────────────────────────────────────────────────────────────


META_GITKEEP_DIRS = (
    "_meta/sessions",
    "_meta/concepts",
    "_meta/snapshots",
    "_meta/eval-history",
    "_meta/eval-history/cron-runs",
    "_meta/eval-history/auditor-patrol",
    "_meta/eval-history/recovery",
    "_meta/methods",
    "_meta/inbox",
    "_meta/runtime",
)

TOP_GITKEEP_DIRS = (
    "inbox",
    "wiki",
)


def _is_non_empty(target: Path) -> bool:
    """Return True when target exists and has any entries (files or dirs)."""
    if not target.exists():
        return False
    if not target.is_dir():
        # A file at the target path definitely counts as non-empty.
        return True
    return any(target.iterdir())


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_gitkeep(dir_path: Path) -> None:
    dir_path.mkdir(parents=True, exist_ok=True)
    keep = dir_path / ".gitkeep"
    keep.write_text("", encoding="utf-8")


def _seed_scaffolding(target: Path) -> None:
    """Write every non-git file required by the spec."""
    target.mkdir(parents=True, exist_ok=True)

    _write_file(target / ".gitignore", _GITIGNORE)
    _write_file(target / ".life-os.toml", _life_os_toml(target))
    _write_file(target / "SOUL.md", _SOUL_MD)
    _write_file(
        target / "projects" / "example-project" / "index.md",
        _EXAMPLE_PROJECT.format(created=datetime.now().date().isoformat()),
    )

    for d in META_GITKEEP_DIRS:
        _write_gitkeep(target / d)
    for d in TOP_GITKEEP_DIRS:
        _write_gitkeep(target / d)

    inbox_notif = target / "_meta" / "inbox" / "notifications.md"
    if not inbox_notif.exists():
        _write_file(inbox_notif, _INBOX_NOTIFICATIONS)


# ─── Git bootstrap ──────────────────────────────────────────────────────────


def _run_git(
    target: Path, args: list[str], *, logger: logging.Logger
) -> tuple[int, str, str]:
    """Run ``git -C <target> <args>``; return (exit, stdout, stderr)."""
    cmd = ["git", "-C", str(target), *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except FileNotFoundError:
        logger.error(
            "git binary not found on PATH; cannot initialise repo. "
            "Scaffolding is still in place; run `git init` yourself."
        )
        return 127, "", "git not found"
    except subprocess.TimeoutExpired:
        logger.error("git command timed out: %s", " ".join(cmd))
        return 124, "", "timeout"
    return result.returncode, result.stdout, result.stderr


def _git_bootstrap(target: Path, logger: logging.Logger) -> bool:
    """Initialise a new git repo and produce the initial commit.

    Returns True on success, False when git reported an error. If the
    ``git`` binary is missing the function returns False and logs but
    does not raise — callers can choose to treat that as non-fatal.
    """
    rc, _out, err = _run_git(target, ["init", "-q"], logger=logger)
    if rc != 0:
        logger.error("git init failed: %s", err.strip())
        return False

    # Add everything we just seeded.
    rc, _out, err = _run_git(target, ["add", "."], logger=logger)
    if rc != 0:
        logger.error("git add failed: %s", err.strip())
        return False

    # Commit. Author identity may or may not be set on the user machine;
    # supply a fallback via -c flags so the initial commit never blocks.
    rc, _out, err = _run_git(
        target,
        [
            "-c",
            "user.name=Life OS",
            "-c",
            "user.email=life-os@localhost",
            "commit",
            "-q",
            "-m",
            "Initial Life OS v1.7 second-brain",
        ],
        logger=logger,
    )
    if rc != 0:
        logger.error("git commit failed: %s", err.strip())
        return False
    return True


# ─── CLI ────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seed",
        description=(
            "Create an empty-but-valid Life OS v1.7 second-brain at the "
            "target path. Refuses to overwrite an existing non-empty "
            "directory."
        ),
    )
    parser.add_argument(
        "--path",
        required=True,
        type=Path,
        help="Target directory (will be created if missing).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Emit progress on stderr.",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help=(
            "Skip the `git init` + initial commit step (useful for "
            "environments without a git binary)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
        stream=sys.stderr,
    )
    logger = logging.getLogger("seed")

    target: Path = args.path.expanduser()

    if _is_non_empty(target):
        logger.error(
            "Refusing to seed: %s already exists and is non-empty. "
            "Remove it or pick a different path.",
            target,
        )
        return 1

    try:
        _seed_scaffolding(target)
    except OSError as exc:
        logger.error("Failed to write scaffolding: %s", exc)
        return 1

    if not args.no_git:
        ok = _git_bootstrap(target, logger)
        if not ok:
            # Scaffolding exists; user can re-run `git init` themselves.
            logger.warning(
                "Scaffolding is on disk but git bootstrap failed. "
                "Run `git init` yourself in %s once git is available.",
                target,
            )
            return 1

    logger.info("Seeded Life OS v1.7 second-brain at %s", target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
