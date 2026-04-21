#!/usr/bin/env python3
"""Unified CLI dispatcher - `life-os-tool {command} [args]`.

Routes subcommands to the appropriate tools/*.py module. Per
references/tools-spec.md §2 single-binary entry point.

Available commands:
    stats                 - escalation ladder analytics for violations.md
    rebuild-session-index - recompile _meta/sessions/INDEX.md
    rebuild-concept-index - recompile _meta/concepts/INDEX.md + SYNAPSES-INDEX.md
    backup                - rotate snapshots + archive old violations
    list                  - list all available commands

Usage:
    uv run life-os-tool {command} [args]
    python3 -m tools.cli {command} [args]

Each subcommand forwards remaining args to its module's argparse.
"""

from __future__ import annotations

import contextlib
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 on stdout/stderr so descriptions containing emoji / arrows / CJK
# characters do not crash on Windows JP locale (cp932 default encoder).
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        with contextlib.suppress(OSError, ValueError):
            _stream.reconfigure(encoding="utf-8")


# Map CLI command -> Python module path
_COMMANDS: dict[str, tuple[str, str]] = {
    # v1.6.x legacy tools (still supported)
    "stats": ("tools.stats", "Usage + quality statistics + compliance escalation ladder"),
    "rebuild-session-index": (
        "tools.rebuild_session_index",
        "Recompile _meta/sessions/INDEX.md (legacy; prefer `reindex --sessions`)",
    ),
    "rebuild-concept-index": (
        "tools.rebuild_concept_index",
        "Recompile _meta/concepts/INDEX.md + SYNAPSES-INDEX.md (legacy; prefer `reindex --concepts`)",
    ),
    "backup": ("tools.backup", "Rotate snapshots + archive old violations"),
    "extract": (
        "tools.extract",
        "Concept candidate extraction from text (frequency + slug helpers)",
    ),
    "seed-concepts": (
        "tools.seed_concepts",
        "Bootstrap concept graph from existing second-brain content",
    ),
    # v1.7 core maintenance (S3)
    "reindex": (
        "tools.reindex",
        "Unified compile of sessions + concepts INDEX.md (replaces rebuild-*-index)",
    ),
    "reconcile": (
        "tools.reconcile",
        "Integrity check: orphan files / broken wikilinks / missing frontmatter / schema",
    ),
    # v1.7 user-invoked tools (S4)
    "search": (
        "tools.search",
        "Cross-session grep + metadata ranking (no semantic search; see hippocampus)",
    ),
    "daily-briefing": (
        "tools.daily_briefing",
        "Today's briefing: SOUL core / DREAM 30d / active projects / inbox / eval history",
    ),
    "research": (
        "tools.research",
        "Web fetch → inbox/ with markdownify + robots.txt respect (no LLM summary)",
    ),
    # v1.7 export + sync (S5)
    "export": (
        "tools.export",
        "Format conversion: pdf (pandoc) / html / json / anki (.apkg)",
    ),
    "sync-notion": (
        "tools.sync_notion",
        "Notion fallback sync when archiver Phase 4 MCP failed",
    ),
    "embed": (
        "tools.embed",
        "Placeholder (out of scope for v1.7 per user decision #3) - prints notice + exit 0",
    ),
    # v1.7 one-time tools (S6)
    "migrate": (
        "tools.migrate",
        "One-time v1.6.2a → v1.7 schema backfill (3-month window)",
    ),
    "seed": (
        "tools.seed",
        "New-user bootstrap: create empty-but-valid second-brain + git init",
    ),
}


def _print_usage(stream=None) -> None:
    # Resolve sys.stdout at call time, not definition time, so pytest capsys
    # (which patches sys.stdout) captures the output correctly.
    if stream is None:
        stream = sys.stdout
    print("Usage: life-os-tool <command> [args]", file=stream)
    print("", file=stream)
    print("Available commands:", file=stream)
    for cmd, (_module, desc) in sorted(_COMMANDS.items()):
        print(f"  {cmd:<28} {desc}", file=stream)
    print(f"  {'list':<28} List all available commands (this help)", file=stream)
    print("", file=stream)
    print("Examples:", file=stream)
    print("  life-os-tool stats", file=stream)
    print("  life-os-tool rebuild-session-index --root ~/second-brain", file=stream)
    print("  life-os-tool backup --dry-run", file=stream)


def main() -> int:
    if len(sys.argv) < 2:
        _print_usage()
        return 0

    command = sys.argv[1]

    if command in ("-h", "--help", "help", "list"):
        _print_usage()
        return 0

    if command not in _COMMANDS:
        print(f"❌ Unknown command: {command}", file=sys.stderr)
        print("", file=sys.stderr)
        _print_usage(stream=sys.stderr)
        return 2

    module_path, _desc = _COMMANDS[command]
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        print(f"❌ Failed to load command '{command}': {exc}", file=sys.stderr)
        return 2

    if not hasattr(module, "main"):
        print(
            f"❌ Module '{module_path}' has no main() function (broken tool?)",
            file=sys.stderr,
        )
        return 2

    # Forward remaining args to the subcommand by mutating sys.argv.
    # Each subcommand uses argparse, which reads sys.argv[1:].
    original_argv = sys.argv
    sys.argv = [command] + sys.argv[2:]
    try:
        result = module.main()
    finally:
        sys.argv = original_argv
    return int(result) if result is not None else 0


if __name__ == "__main__":
    sys.exit(main())
