#!/usr/bin/env python3
"""INDEX-only SQLite FTS5 candidate search for hippocampus Wave 1.

The general `tools/session_search.py` tool can index several Life OS memory
surfaces. Hippocampus has a stricter isolation boundary: Wave 1 may receive
only `_meta/sessions/INDEX.md` summaries before it chooses session files to
read. This helper reuses the FTS5 implementation from `tools/session_search.py`
while keeping the source scope to the session index and using an in-memory
database so hippocampus remains read-only except for its audit trail.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import session_search as fts5  # noqa: E402

DEFAULT_LIMIT = 50


def _safe_limit(limit: int) -> int:
    return max(1, min(int(limit), 50))


def hippocampus_wave1_search(
    query: str,
    *,
    root: Path | None = None,
    limit: int = DEFAULT_LIMIT,
    max_snippet_chars: int = fts5.DEFAULT_MAX_SNIPPET_CHARS,
) -> dict[str, Any]:
    """Search `_meta/sessions/INDEX.md` via in-memory FTS5 and return JSON-safe data."""
    resolved_root = fts5._resolve_root(root)
    docs = fts5._iter_session_index_docs(resolved_root)
    safe_limit = _safe_limit(limit)

    with fts5._connect(":memory:", dry_run=True) as conn:
        fts5._ensure_schema(conn)
        fts5._insert_docs(conn, docs)
        conn.commit()
        results = fts5._query_rows(
            conn,
            query,
            limit=safe_limit,
            max_snippet_chars=max(120, max_snippet_chars),
        )

    return {
        "success": True,
        "query": query,
        "root": str(resolved_root),
        "db_path": ":memory:",
        "source_scope": "_meta/sessions/INDEX.md",
        "sources_indexed": len(docs),
        "count": len(results),
        "results": [asdict(result) for result in results],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hippocampus_wave1_search",
        description=(
            "INDEX-only SQLite FTS5 candidate search for hippocampus Wave 1. "
            "Wraps tools/session_search.py primitives without exposing journal content."
        ),
    )
    parser.add_argument("--query", required=True, help="Wave 1 search query.")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Life OS second-brain root (default: LIFE_OS_SECOND_BRAIN_ROOT or cwd).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Maximum candidates to return, capped at 50 (default: {DEFAULT_LIMIT}).",
    )
    parser.add_argument(
        "--max-snippet-chars",
        type=int,
        default=fts5.DEFAULT_MAX_SNIPPET_CHARS,
        help="Maximum safe INDEX excerpt length per result.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured JSON. Human-readable output is used otherwise.",
    )
    return parser


def _format_human(payload: dict[str, Any]) -> str:
    if not payload["results"]:
        return (
            f"No INDEX matches for {payload['query']!r}. "
            f"Sources indexed: {payload['sources_indexed']}."
        )

    lines = [
        f"Query: {payload['query']}",
        f"Source scope: {payload['source_scope']}",
        f"Sources indexed: {payload['sources_indexed']}",
        "",
    ]
    for result in payload["results"]:
        bits = [
            f"{result['rank']}. {result['title'] or '(untitled)'}",
            f"date={result['date'] or 'unknown'}",
            f"project={result['project'] or 'unknown'}",
            f"session={result['session_id'] or 'unknown'}",
        ]
        lines.append(" ".join(bits))
        if result["snippet"]:
            lines.append(f"   Match: {result['snippet']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        payload = hippocampus_wave1_search(
            args.query,
            root=args.root,
            limit=args.limit,
            max_snippet_chars=args.max_snippet_chars,
        )
    except sqlite3.OperationalError as exc:
        print(
            f"hippocampus_wave1_search error: SQLite FTS5 unavailable or query invalid: {exc}",
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(f"hippocampus_wave1_search error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(_format_human(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
