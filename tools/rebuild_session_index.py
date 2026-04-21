#!/usr/bin/env python3
"""Rebuild ``_meta/sessions/INDEX.md`` from per-session markdown files.

Use cases:
- Fallback when retrospective Mode 0's INDEX compilation step did not run
- Manual recompile after editing session frontmatter directly
- Recovery after corruption of INDEX.md

Usage:
    uv run tools/rebuild_session_index.py [--root PATH] [--dry-run]
    python3 tools/rebuild_session_index.py [--root PATH] [--dry-run]

If ``--root`` is omitted, defaults to current working directory (assumes you
run from inside the second-brain).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from repo root via `python3 tools/rebuild_session_index.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.cortex.session_index import compile_index, write_index  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recompile _meta/sessions/INDEX.md from per-session markdown files. "
            "Idempotent — safe to run repeatedly."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Path to second-brain root (default: cwd)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written, do not modify files",
    )
    args = parser.parse_args()

    sessions_dir = args.root / "_meta" / "sessions"
    if not sessions_dir.exists():
        print(f"❌ Sessions directory not found: {sessions_dir}", file=sys.stderr)
        print(
            "   Is --root pointing at a Life OS second-brain?",
            file=sys.stderr,
        )
        return 2

    content = compile_index(sessions_dir)
    line_count = sum(
        1
        for line in content.splitlines()
        if " | " in line and not line.startswith("#")
    )

    if args.dry_run:
        print(f"--- INDEX.md preview ({line_count} sessions) ---")
        print(content)
        print("--- (dry-run, no files written) ---")
        return 0

    target = write_index(content, sessions_dir)
    print(f"✅ Wrote {target} ({line_count} sessions indexed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
