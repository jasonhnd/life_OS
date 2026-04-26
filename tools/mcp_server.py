#!/usr/bin/env python3
"""Lightweight MCP stdio wrapper for Life OS Python tools.

The server intentionally keeps the MCP dependency optional: importing this
module works with only the Life OS baseline dependencies installed, while
running the stdio server prints a clear setup error if ``mcp`` is missing.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import inspect
import io
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None  # type: ignore[assignment]
    _MCP_AVAILABLE = False
else:
    _MCP_AVAILABLE = True

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SERVER_NAME = "life-os-tools"


ToolResult = dict[str, Any]


TOOLS: dict[str, tuple[str, str]] = {
    "stats": ("tools.stats", "Usage, quality, and compliance statistics."),
    "migrate": ("tools.migrate", "One-time schema backfill for Life OS upgrades."),
    "reconcile": ("tools.reconcile", "Integrity checks for second-brain markdown files."),
    "search": ("tools.search", "Cross-session grep plus metadata-ranked search."),
    "daily-briefing": ("tools.daily_briefing", "Generate today's Life OS briefing."),
    "research": ("tools.research", "Fetch web research into inbox markdown."),
    "export": ("tools.export", "Export Life OS content to supported formats."),
    "sync-notion": ("tools.sync_notion", "Fallback Notion sync for archived content."),
    "embed": ("tools.embed", "Embedding placeholder command."),
    "seed": ("tools.seed", "Bootstrap a new empty second-brain."),
    "extract": ("tools.extract", "Extract concept candidates from text."),
    "backup": ("tools.backup", "Rotate snapshots and archive old compliance records."),
    "reindex": ("tools.reindex", "Rebuild unified session and concept indexes."),
    "rebuild-session-index": (
        "tools.rebuild_session_index",
        "Legacy session index rebuild command.",
    ),
    "rebuild-concept-index": (
        "tools.rebuild_concept_index",
        "Legacy concept index rebuild command.",
    ),
    "cli": ("tools.cli", "Generic life-os-tool dispatcher."),
}


def _coerce_args(args: Sequence[str] | None) -> list[str]:
    if args is None:
        return []
    return [str(arg) for arg in args]


def _coerce_exit_code(code: object) -> int:
    if code is None:
        return 0
    if isinstance(code, int):
        return code
    return 1


def _main_accepts_argv(main_func: Callable[..., Any]) -> bool:
    try:
        return bool(inspect.signature(main_func).parameters)
    except (TypeError, ValueError):
        return False


@contextlib.contextmanager
def _patched_argv(program: str, args: list[str]):
    original_argv = sys.argv
    sys.argv = [program, *args]
    try:
        yield
    finally:
        sys.argv = original_argv


def _invoke_command(command: str, args: Sequence[str] | None = None) -> ToolResult:
    """Run one Life OS tool and return captured stdout/stderr.

    The wrapper invokes tool modules in-process to avoid shell quoting issues
    and extra subprocess dependencies. Tools still receive normal argparse
    inputs via either their ``main(argv)`` parameter or temporary ``sys.argv``.
    """

    if command not in TOOLS:
        return {
            "ok": False,
            "command": command,
            "args": _coerce_args(args),
            "exit_code": 2,
            "stdout": "",
            "stderr": f"Unknown Life OS tool: {command}",
        }

    module_path, _description = TOOLS[command]
    command_args = _coerce_args(args)
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = 0

    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            module = importlib.import_module(module_path)
            main_func = getattr(module, "main", None)
            if not callable(main_func):
                raise AttributeError(f"Module {module_path!r} has no callable main()")

            program = "life-os-tool" if command == "cli" else command
            with _patched_argv(program, command_args):
                if _main_accepts_argv(main_func):
                    result = main_func(command_args)
                else:
                    result = main_func()
            exit_code = _coerce_exit_code(result)
        except SystemExit as exc:
            exit_code = _coerce_exit_code(exc.code)
        except Exception as exc:  # noqa: BLE001 - tool errors should become MCP results.
            exit_code = 1
            print(f"{type(exc).__name__}: {exc}", file=sys.stderr)

    return {
        "ok": exit_code == 0,
        "command": command,
        "args": command_args,
        "exit_code": exit_code,
        "stdout": stdout.getvalue(),
        "stderr": stderr.getvalue(),
    }


def create_server() -> Any:
    """Create and register the Life OS MCP server."""

    if not _MCP_AVAILABLE:
        print(
            "Life OS MCP server requires the optional Python package 'mcp'.\n"
            "Install it in the same Python environment used to run this server:\n"
            "  pip install mcp\n"
            "  uv pip install mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    server = FastMCP(SERVER_NAME)

    for command, (_module_path, description) in TOOLS.items():
        run_tool = _make_mcp_tool(command, description)
        server.tool(name=command, description=description)(run_tool)

    return server


def _make_mcp_tool(command: str, description: str) -> Callable[[list[str] | None], ToolResult]:
    def run_tool(args: list[str] | None = None) -> ToolResult:
        return _invoke_command(command, args)

    run_tool.__name__ = command.replace("-", "_")
    run_tool.__doc__ = (
        f"{description}\n\n"
        "Pass the same argument vector you would pass after the CLI command. "
        "For example: args=['--root', '/path/to/second-brain']."
    )
    return run_tool


def _print_tool_list() -> None:
    print("tools:")
    for command, (_module_path, description) in TOOLS.items():
        print(f"{command:<24} {description}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the Life OS MCP stdio server.",
    )
    parser.add_argument(
        "--transport",
        choices=("stdio",),
        default="stdio",
        help="MCP transport to run. Only stdio is supported by this lightweight wrapper.",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List exposed tools without importing the optional MCP package.",
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start the MCP stdio server. This is the default when --list-tools is not used.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    parsed = parser.parse_args(argv)

    if parsed.list_tools:
        _print_tool_list()
        return 0

    server = create_server()
    server.run(transport=parsed.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
