#!/usr/bin/env python3
"""Unified CLI dispatcher — `life-os-tool {command} [args]`.

Routes subcommands to the appropriate tools/*.py module. Per
references/tools-spec.md §2 single-binary entry point.

Available commands:
    stats                 — escalation ladder analytics for violations.md
    rebuild-session-index — recompile _meta/sessions/INDEX.md
    rebuild-concept-index — recompile _meta/concepts/INDEX.md + SYNAPSES-INDEX.md
    backup                — rotate snapshots + archive old violations
    list                  — list all available commands

Usage:
    uv run life-os-tool {command} [args]
    python3 -m tools.cli {command} [args]

Each subcommand forwards remaining args to its module's argparse.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# Map CLI command -> Python module path
_COMMANDS: dict[str, tuple[str, str]] = {
    "stats": ("tools.stats", "Compliance violations escalation ladder analytics"),
    "rebuild-session-index": (
        "tools.rebuild_session_index",
        "Recompile _meta/sessions/INDEX.md",
    ),
    "rebuild-concept-index": (
        "tools.rebuild_concept_index",
        "Recompile _meta/concepts/INDEX.md + SYNAPSES-INDEX.md",
    ),
    "backup": ("tools.backup", "Rotate snapshots + archive old violations"),
}


def _print_usage(stream=sys.stdout) -> None:
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
        _print_usage(sys.stderr)
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
