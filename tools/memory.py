#!/usr/bin/env python3
# Forked from NousResearch/hermes-agent (MIT License) commit 59b56d445c34e1d4bf797f5345b802c7b5986c72
# Adapted for Life OS v1.7.2
"""Persistent curated memory for Life OS.

This module keeps the useful Hermes memory-tool properties:

- bounded, file-backed memory
- injection/exfiltration scanning before persistent writes
- file-lock + atomic temp-file replacement for concurrent safety

Life OS adapts the storage model:

- writable operational memory lives at ``_meta/MEMORY.md``
- user identity/personhood belongs to the existing ``SOUL.md`` file
- this module never creates or writes ``USER.md``

The primary active-write API is ``emit_memory_entry(key, value, source)``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:  # pragma: no cover - exercised on non-Unix platforms
    fcntl = None  # type: ignore[assignment]

try:
    import msvcrt
except ImportError:  # pragma: no cover - exercised on non-Windows platforms
    msvcrt = None  # type: ignore[assignment]


MEMORY_RELATIVE_PATH = Path("_meta") / "MEMORY.md"
SOUL_RELATIVE_PATH = Path("SOUL.md")
DEFAULT_MEMORY_CHAR_LIMIT = 12_000

_ENTRY_START = "<!-- BEGIN_MEMORY_ENTRY"
_ENTRY_END = "<!-- END_MEMORY_ENTRY -->"
_ENTRY_PATTERN = re.compile(
    rf"{re.escape(_ENTRY_START)}\n"
    r"key:\s*(?P<key>.*?)\n"
    r"source:\s*(?P<source>.*?)\n"
    r"updated_at:\s*(?P<updated_at>.*?)\n"
    r"-->\n"
    r"(?P<value>.*?)\n"
    rf"{re.escape(_ENTRY_END)}",
    re.DOTALL,
)

_MEMORY_THREAT_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"ignore\s+(previous|all|above|prior)\s+instructions", "prompt_injection"),
    (r"you\s+are\s+now\s+", "role_hijack"),
    (r"do\s+not\s+tell\s+the\s+user", "deception_hide"),
    (r"system\s+prompt\s+override", "sys_prompt_override"),
    (r"disregard\s+(your|all|any)\s+(instructions|rules|guidelines)", "disregard_rules"),
    (
        r"act\s+as\s+(if|though)\s+you\s+(have\s+no|don't\s+have)\s+"
        r"(restrictions|limits|rules)",
        "bypass_restrictions",
    ),
    (r"curl\s+[^\n]*\$\{?\w*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|API)", "exfil_curl"),
    (r"wget\s+[^\n]*\$\{?\w*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|API)", "exfil_wget"),
    (r"cat\s+[^\n]*(\.env|credentials|\.netrc|\.pgpass|\.npmrc|\.pypirc)", "read_secrets"),
    (r"authorized_keys", "ssh_backdoor"),
    (r"\$HOME/\.ssh|\~/\.ssh", "ssh_access"),
    (r"\.life-os\.toml|LIFE_OS_.*(TOKEN|SECRET|PASSWORD|KEY)", "life_os_secret_access"),
)

_INVISIBLE_CHARS = (
    "\u200b",
    "\u200c",
    "\u200d",
    "\u2060",
    "\ufeff",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
)


@dataclass(frozen=True)
class MemoryEntry:
    """One keyed Life OS operational-memory entry."""

    key: str
    value: str
    source: str
    updated_at: str


def resolve_root(root: Path | str | None = None) -> Path:
    """Resolve the Life OS/second-brain root for repo-relative paths.

    Precedence: explicit root > LIFE_OS_ROOT > current working directory.
    This mirrors the existing tools' repo-relative behavior and avoids any
    Hermes home-directory dependency.
    """

    if root is not None:
        return Path(root).expanduser().resolve()

    env_root = os.environ.get("LIFE_OS_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    return Path.cwd().resolve()


def get_memory_path(root: Path | str | None = None) -> Path:
    """Return the repo-relative ``_meta/MEMORY.md`` path."""

    return resolve_root(root) / MEMORY_RELATIVE_PATH


def get_soul_path(root: Path | str | None = None) -> Path:
    """Return the repo-relative ``SOUL.md`` path."""

    return resolve_root(root) / SOUL_RELATIVE_PATH


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _scan_memory_content(content: str) -> str | None:
    """Return an error string if content looks unsafe for prompt injection."""

    for char in _INVISIBLE_CHARS:
        if char in content:
            return (
                "Blocked: content contains invisible unicode character "
                f"U+{ord(char):04X}."
            )

    for marker in (_ENTRY_START, _ENTRY_END, "<!--"):
        if marker in content:
            return f"Blocked: content contains reserved memory marker {marker!r}."

    for pattern, pattern_id in _MEMORY_THREAT_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return (
                f"Blocked: content matches threat pattern {pattern_id!r}. "
                "Memory entries are injected into future context and must not "
                "contain injection or exfiltration payloads."
            )

    return None


def _validate_field(name: str, value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{name} cannot be empty.")
    if "\n" in cleaned or "\r" in cleaned:
        raise ValueError(f"{name} must be a single line.")
    scan_error = _scan_memory_content(cleaned)
    if scan_error:
        raise ValueError(scan_error)
    return cleaned


def _validate_value(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("value cannot be empty.")
    scan_error = _scan_memory_content(cleaned)
    if scan_error:
        raise ValueError(scan_error)
    return cleaned


@contextmanager
def _file_lock(path: Path) -> Iterator[None]:
    """Acquire an exclusive lock using a sidecar .lock file when available."""

    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    if fcntl is None and msvcrt is None:
        yield
        return

    if msvcrt is not None and (not lock_path.exists() or lock_path.stat().st_size == 0):
        lock_path.write_text(" ", encoding="utf-8")

    with lock_path.open("r+" if msvcrt is not None else "a+", encoding="utf-8") as lock_file:
        try:
            if fcntl is not None:
                fcntl.flock(lock_file, fcntl.LOCK_EX)
            elif msvcrt is not None:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock_file, fcntl.LOCK_UN)
            elif msvcrt is not None:
                with suppress(OSError):
                    lock_file.seek(0)
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)


def _atomic_write(path: Path, text: str) -> None:
    """Write text with temp-file-then-rename semantics."""

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), prefix=".memory_", suffix=".tmp")
    tmp_file = Path(tmp_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        tmp_file.replace(path)
    except BaseException:
        with suppress(OSError):
            tmp_file.unlink()
        raise


class MemoryStore:
    """Repo-relative ``_meta/MEMORY.md`` store plus read-only ``SOUL.md`` reference."""

    def __init__(
        self,
        root: Path | str | None = None,
        memory_char_limit: int = DEFAULT_MEMORY_CHAR_LIMIT,
    ) -> None:
        self.root = resolve_root(root)
        self.memory_path = self.root / MEMORY_RELATIVE_PATH
        self.soul_path = self.root / SOUL_RELATIVE_PATH
        self.memory_char_limit = memory_char_limit
        self.memory_entries: list[MemoryEntry] = []
        self._system_prompt_snapshot: dict[str, str] = {"memory": "", "soul": ""}

    def load_from_disk(self) -> None:
        """Load memory and capture frozen prompt snapshots."""

        self.memory_entries = self._read_entries()
        self._system_prompt_snapshot = {
            "memory": self._render_memory_block(self.memory_entries),
            "soul": self._render_soul_block(),
        }

    def list_entries(self) -> list[MemoryEntry]:
        """Return current memory entries from disk."""

        self.memory_entries = self._read_entries()
        return list(self.memory_entries)

    def read_soul(self) -> str:
        """Read ``SOUL.md`` if present. This method never creates or writes it."""

        if not self.soul_path.exists():
            return ""
        return self.soul_path.read_text(encoding="utf-8")

    def upsert(self, key: str, value: str, source: str) -> dict[str, Any]:
        """Create or replace one keyed entry in ``_meta/MEMORY.md``."""

        clean_key = _validate_field("key", key)
        clean_value = _validate_value(value)
        clean_source = _validate_field("source", source)
        next_entry = MemoryEntry(
            key=clean_key,
            value=clean_value,
            source=clean_source,
            updated_at=_utc_now(),
        )

        with _file_lock(self.memory_path):
            entries = [entry for entry in self._read_entries() if entry.key != clean_key]
            entries.append(next_entry)
            self._enforce_char_limit(entries)
            self._write_entries(entries)
            self.memory_entries = entries

        return self._success_response("Entry emitted.", next_entry)

    def remove(self, key: str) -> dict[str, Any]:
        """Remove one keyed memory entry."""

        clean_key = _validate_field("key", key)
        with _file_lock(self.memory_path):
            entries = self._read_entries()
            kept = [entry for entry in entries if entry.key != clean_key]
            if len(kept) == len(entries):
                return {
                    "success": False,
                    "error": f"No memory entry matched key {clean_key!r}.",
                    "path": str(self.memory_path),
                }
            self._write_entries(kept)
            self.memory_entries = kept

        return {
            "success": True,
            "message": "Entry removed.",
            "key": clean_key,
            "path": str(self.memory_path),
            "entry_count": len(kept),
        }

    def format_for_system_prompt(self, target: str = "memory") -> str | None:
        """Return a frozen snapshot block captured by ``load_from_disk()``."""

        if not self._system_prompt_snapshot["memory"] and not self._system_prompt_snapshot["soul"]:
            self.load_from_disk()

        if target not in ("memory", "soul"):
            raise ValueError("target must be 'memory' or 'soul'.")

        block = self._system_prompt_snapshot[target]
        return block or None

    def _read_entries(self) -> list[MemoryEntry]:
        if not self.memory_path.exists():
            return []

        raw = self.memory_path.read_text(encoding="utf-8")
        entries: list[MemoryEntry] = []
        for match in _ENTRY_PATTERN.finditer(raw):
            try:
                entry = MemoryEntry(
                    key=_validate_field("key", match.group("key")),
                    source=_validate_field("source", match.group("source")),
                    updated_at=_validate_field("updated_at", match.group("updated_at")),
                    value=_validate_value(match.group("value")),
                )
            except ValueError:
                continue
            entries.append(entry)

        return _dedupe_by_key(entries)

    def _write_entries(self, entries: list[MemoryEntry]) -> None:
        content = _render_memory_file(entries)
        _atomic_write(self.memory_path, content)

    def _enforce_char_limit(self, entries: list[MemoryEntry]) -> None:
        content = _render_entries_only(entries)
        current = len(content)
        if current > self.memory_char_limit:
            raise ValueError(
                f"Memory would be {current:,}/{self.memory_char_limit:,} chars. "
                "Shorten this entry or remove older entries first."
            )

    def _render_memory_block(self, entries: list[MemoryEntry]) -> str:
        if not entries:
            return ""
        content = _render_entries_only(entries)
        current = len(content)
        pct = min(100, int((current / self.memory_char_limit) * 100))
        return (
            f"MEMORY (_meta/MEMORY.md) [{pct}% - "
            f"{current:,}/{self.memory_char_limit:,} chars]\n\n{content}"
        )

    def _render_soul_block(self) -> str:
        soul = self.read_soul().strip()
        if not soul:
            return ""
        return "SOUL (read-only identity layer from SOUL.md)\n\n" + soul

    def _success_response(self, message: str, entry: MemoryEntry) -> dict[str, Any]:
        entries = self.memory_entries
        content = _render_entries_only(entries)
        current = len(content)
        pct = min(100, int((current / self.memory_char_limit) * 100))
        return {
            "success": True,
            "message": message,
            "entry": asdict(entry),
            "path": str(self.memory_path),
            "usage": f"{pct}% - {current:,}/{self.memory_char_limit:,} chars",
            "entry_count": len(entries),
        }


def _dedupe_by_key(entries: list[MemoryEntry]) -> list[MemoryEntry]:
    """Keep the last entry for each key while preserving final order."""

    by_key: dict[str, MemoryEntry] = {}
    for entry in entries:
        by_key[entry.key] = entry
    return list(by_key.values())


def _render_entries_only(entries: list[MemoryEntry]) -> str:
    return "\n\n".join(_render_entry(entry) for entry in entries)


def _render_memory_file(entries: list[MemoryEntry]) -> str:
    header = (
        "# Life OS MEMORY\n\n"
        "Persistent operational memory for Life OS agents.\n\n"
        "User identity and long-lived personal dimensions belong in `SOUL.md`; "
        "this file stores compact repo-local notes. Edit by hand only if each "
        "entry block remains well-formed.\n"
    )
    body = _render_entries_only(entries)
    if not body:
        return header
    return f"{header}\n{body}\n"


def _render_entry(entry: MemoryEntry) -> str:
    return (
        f"{_ENTRY_START}\n"
        f"key: {entry.key}\n"
        f"source: {entry.source}\n"
        f"updated_at: {entry.updated_at}\n"
        "-->\n"
        f"{entry.value}\n"
        f"{_ENTRY_END}"
    )


def emit_memory_entry(key: str, value: str, source: str) -> dict[str, Any]:
    """Active write function for agents.

    Writes or replaces ``key`` in ``_meta/MEMORY.md`` under the resolved root
    and returns a JSON-serializable result dictionary.
    """

    return MemoryStore().upsert(key=key, value=value, source=source)


def memory_tool(
    action: str,
    target: str = "memory",
    key: str | None = None,
    content: str | None = None,
    source: str = "memory_tool",
    store: MemoryStore | None = None,
) -> str:
    """Small JSON-returning compatibility wrapper for tool-style callers."""

    if store is None:
        store = MemoryStore()

    try:
        if target == "soul":
            if action != "read":
                result: dict[str, Any] = {
                    "success": False,
                    "error": "SOUL.md is read-only from tools.memory; use action='read'.",
                    "path": str(store.soul_path),
                }
            else:
                result = {
                    "success": True,
                    "target": "soul",
                    "path": str(store.soul_path),
                    "exists": store.soul_path.exists(),
                    "content": store.read_soul(),
                }
        elif target == "memory":
            if action in ("add", "replace", "upsert", "emit"):
                if key is None or content is None:
                    raise ValueError("key and content are required for memory writes.")
                result = store.upsert(key=key, value=content, source=source)
            elif action == "remove":
                if key is None:
                    raise ValueError("key is required for remove.")
                result = store.remove(key)
            elif action == "read":
                result = {
                    "success": True,
                    "target": "memory",
                    "path": str(store.memory_path),
                    "entries": [asdict(entry) for entry in store.list_entries()],
                }
            else:
                raise ValueError("Unknown action. Use add, replace, upsert, emit, remove, or read.")
        else:
            raise ValueError("target must be 'memory' or 'soul'.")
    except ValueError as exc:
        result = {"success": False, "error": str(exc)}

    return json.dumps(result, ensure_ascii=False)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read/write Life OS _meta/MEMORY.md and read SOUL.md.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Life OS root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON for commands that support it.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    emit_parser = subparsers.add_parser("emit", help="Write or replace a memory entry.")
    _add_json_flag(emit_parser)
    emit_parser.add_argument("key")
    emit_parser.add_argument("value")
    emit_parser.add_argument("--source", default="cli")

    read_parser = subparsers.add_parser("read", help="Read memory entries or SOUL.md.")
    _add_json_flag(read_parser)
    read_parser.add_argument("--target", choices=("memory", "soul"), default="memory")

    remove_parser = subparsers.add_parser("remove", help="Remove a memory entry by key.")
    _add_json_flag(remove_parser)
    remove_parser.add_argument("key")

    path_parser = subparsers.add_parser(
        "path",
        help="Print the resolved MEMORY.md and SOUL.md paths.",
    )
    _add_json_flag(path_parser)

    return parser


def _add_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Emit machine-readable JSON.",
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    store = MemoryStore(root=args.root)

    try:
        if args.command == "emit":
            result = store.upsert(args.key, args.value, args.source)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"Memory entry emitted: {result['entry']['key']} -> {result['path']}")
            return 0

        if args.command == "read":
            if args.target == "soul":
                content = store.read_soul()
                result = {
                    "target": "soul",
                    "path": str(store.soul_path),
                    "exists": store.soul_path.exists(),
                    "content": content,
                }
                print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else content)
            else:
                entries = store.list_entries()
                result = {
                    "target": "memory",
                    "path": str(store.memory_path),
                    "entries": [asdict(entry) for entry in entries],
                }
                if args.json:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    print(_render_entries_only(entries))
            return 0

        if args.command == "remove":
            result = store.remove(args.key)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(result.get("message", result.get("error", "")))
            return 0 if result.get("success") else 1

        if args.command == "path":
            result = {"memory": str(store.memory_path), "soul": str(store.soul_path)}
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"memory: {store.memory_path}")
                print(f"soul: {store.soul_path}")
            return 0

    except (OSError, ValueError) as exc:
        print(f"memory.py: {exc}", file=sys.stderr)
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
