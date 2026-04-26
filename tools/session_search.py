#!/usr/bin/env python3
# Forked from NousResearch/hermes-agent (MIT License) commit 59b56d445c34e1d4bf797f5345b802c7b5986c72
# Adapted for Life OS v1.7.2
"""SQLite FTS5 session search for Life OS local memory.

Usage:
    python tools/session_search.py --query "X"

This tool intentionally does not assume Hermes runtime objects, Gemini, or any
external LLM summarizer. It indexes Life OS markdown surfaces into a local
SQLite FTS5 cache and returns deterministic metadata plus extractive snippets.

Sources:
    _meta/sessions/INDEX.md
    _meta/journal/*.md

Cache:
    _meta/cache/session-search.db
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        with contextlib.suppress(OSError, ValueError):
            _stream.reconfigure(encoding="utf-8")

DEFAULT_DB_RELATIVE = Path("_meta") / "cache" / "session-search.db"
SESSION_INDEX_RELATIVE = Path("_meta") / "sessions" / "INDEX.md"
JOURNAL_RELATIVE = Path("_meta") / "journal"
FTS_TABLE = "session_docs"
DEFAULT_LIMIT = 5
DEFAULT_MAX_SNIPPET_CHARS = 900
DEFAULT_SUMMARY_NOTICE = (
    "Life OS degraded recall: no external LLM summarizer is configured, "
    "so this result uses deterministic SQLite FTS5 metadata and excerpts."
)

_SESSION_INDEX_LINE_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+\|\s+"
    r"(?P<project>.*?)\s+\|\s+"
    r"(?P<subject>.*?)\s+\|\s+"
    r"(?P<score>.*?)\s+\|\s+"
    r"\[(?P<keywords>.*?)\]\s+\|\s+"
    r"(?P<session_id>\S+)\s*$"
)
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<frontmatter>.*?)\n---\s*\n", re.DOTALL)
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<title>.+?)\s*$", re.MULTILINE)
_DATE_IN_NAME_RE = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})")
_FTS_OPERATOR_RE = re.compile(r"\b(?:AND|OR|NOT|NEAR)\b", re.IGNORECASE)
_TOKEN_RE = re.compile(r"[\w./:@+-]+", re.UNICODE)


@dataclass(frozen=True)
class SourceDoc:
    """One Life OS memory surface indexed into SQLite FTS5."""

    source_key: str
    source_type: str
    source_path: str
    date: str
    project: str
    session_id: str
    title: str
    content: str


@dataclass(frozen=True)
class SearchResult:
    """One FTS5 search result with deterministic Life OS recall text."""

    rank: int
    source_type: str
    source_path: str
    title: str
    date: str
    project: str
    session_id: str
    score: float
    snippet: str
    summary: str


def _resolve_root(root: Path | None) -> Path:
    """Resolve the second-brain root, honoring the existing Life OS env var."""
    if root is not None:
        return root.expanduser().resolve()
    env_root = os.environ.get("LIFE_OS_SECOND_BRAIN_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path.cwd().resolve()


def _summary_notice() -> str:
    """Return configurable degraded-summary text for non-LLM recall."""
    return os.environ.get("LIFE_OS_SESSION_SEARCH_SUMMARY_TEXT", DEFAULT_SUMMARY_NOTICE)


def _relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")


def _strip_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse simple top-level frontmatter fields without adding PyYAML here."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    frontmatter: dict[str, str] = {}
    for raw_line in match.group("frontmatter").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and value and not value.startswith("["):
            frontmatter[key] = value

    return frontmatter, text[match.end() :]


def _title_from_markdown(body: str, fallback: str) -> str:
    match = _HEADING_RE.search(body)
    if match:
        return match.group("title").strip()
    first_nonempty = next((line.strip() for line in body.splitlines() if line.strip()), "")
    return first_nonempty[:120] if first_nonempty else fallback


def _date_from_path(path: Path) -> str:
    match = _DATE_IN_NAME_RE.search(path.name)
    if match:
        return match.group("date")
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()
    except OSError:
        return ""


def _iter_session_index_docs(root: Path) -> list[SourceDoc]:
    path = root / SESSION_INDEX_RELATIVE
    if not path.is_file():
        return []

    docs: list[SourceDoc] = []
    for line_no, raw_line in enumerate(_read_text(path).splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or " | " not in line:
            continue

        match = _SESSION_INDEX_LINE_RE.match(line)
        if match:
            data = match.groupdict()
            session_id = data["session_id"]
            title = data["subject"]
            content = "\n".join(
                [
                    f"date: {data['date']}",
                    f"project: {data['project']}",
                    f"subject: {data['subject']}",
                    f"score: {data['score']}",
                    f"keywords: {data['keywords']}",
                    f"session_id: {session_id}",
                    line,
                ]
            )
            docs.append(
                SourceDoc(
                    source_key=f"session-index:{session_id}",
                    source_type="session_index",
                    source_path=_relative_to_root(path, root),
                    date=data["date"],
                    project=data["project"],
                    session_id=session_id,
                    title=title,
                    content=content,
                )
            )
            continue

        docs.append(
            SourceDoc(
                source_key=f"session-index-line:{line_no}",
                source_type="session_index",
                source_path=_relative_to_root(path, root),
                date="",
                project="",
                session_id="",
                title=line[:120],
                content=line,
            )
        )

    return docs


def _iter_journal_docs(root: Path) -> list[SourceDoc]:
    journal_dir = root / JOURNAL_RELATIVE
    if not journal_dir.is_dir():
        return []

    docs: list[SourceDoc] = []
    for path in sorted(journal_dir.glob("*.md")):
        if not path.is_file():
            continue
        try:
            raw_text = _read_text(path)
        except OSError:
            continue
        frontmatter, body = _strip_frontmatter(raw_text)
        title = (
            frontmatter.get("subject")
            or frontmatter.get("title")
            or _title_from_markdown(body, path.stem)
        )
        date = (
            frontmatter.get("date")
            or frontmatter.get("started_at", "")[:10]
            or _date_from_path(path)
        )
        docs.append(
            SourceDoc(
                source_key=f"journal:{path.name}",
                source_type="journal",
                source_path=_relative_to_root(path, root),
                date=date,
                project=frontmatter.get("project", ""),
                session_id=frontmatter.get("session_id", ""),
                title=title,
                content=raw_text,
            )
        )

    return docs


def collect_sources(root: Path) -> list[SourceDoc]:
    """Collect all configured Life OS search sources."""
    return [*_iter_session_index_docs(root), *_iter_journal_docs(root)]


def _connect(db_path: Path | str, *, dry_run: bool = False) -> sqlite3.Connection:
    if dry_run:
        conn = sqlite3.connect(":memory:")
    else:
        resolved = Path(db_path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(resolved)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create a fresh FTS5 table for the current source scan."""
    conn.execute(f"DROP TABLE IF EXISTS {FTS_TABLE}")
    conn.execute(
        f"""
        CREATE VIRTUAL TABLE {FTS_TABLE} USING fts5(
            source_key UNINDEXED,
            source_type UNINDEXED,
            source_path UNINDEXED,
            date UNINDEXED,
            project UNINDEXED,
            session_id UNINDEXED,
            title,
            content,
            tokenize='unicode61'
        )
        """
    )


def _insert_docs(conn: sqlite3.Connection, docs: list[SourceDoc]) -> None:
    conn.executemany(
        f"""
        INSERT INTO {FTS_TABLE}
            (source_key, source_type, source_path, date, project, session_id, title, content)
        VALUES
            (:source_key, :source_type, :source_path, :date, :project, :session_id, :title, :content)
        """,
        [asdict(doc) for doc in docs],
    )


def rebuild_cache(root: Path, db_path: Path | str, *, dry_run: bool = False) -> int:
    """Rebuild the SQLite FTS5 cache from Life OS markdown sources."""
    docs = collect_sources(root)
    with _connect(db_path, dry_run=dry_run) as conn:
        _ensure_schema(conn)
        _insert_docs(conn, docs)
        conn.commit()
    return len(docs)


def _quote_fts_term(term: str) -> str:
    escaped = term.replace('"', '""')
    return f'"{escaped}"'


def _build_match_query(query: str) -> str:
    """Use FTS5 syntax when explicit; otherwise broad OR terms for recall."""
    stripped = query.strip()
    if not stripped:
        return ""
    if any(ch in stripped for ch in '"()*') or _FTS_OPERATOR_RE.search(stripped):
        return stripped
    terms = _TOKEN_RE.findall(stripped)
    if not terms:
        return _quote_fts_term(stripped)
    return " OR ".join(_quote_fts_term(term) for term in terms)


def _truncate_around_matches(full_text: str, query: str, max_chars: int) -> str:
    """Return a deterministic excerpt centered near query matches."""
    if len(full_text) <= max_chars:
        return full_text.strip()

    text_lower = full_text.lower()
    terms = [term.lower() for term in _TOKEN_RE.findall(query) if term.strip()]
    positions: list[int] = []
    for term in terms:
        positions.extend(match.start() for match in re.finditer(re.escape(term), text_lower))

    if not positions:
        excerpt = full_text[:max_chars].strip()
        return f"{excerpt}\n...[later content truncated]..."

    positions.sort()
    center = positions[0]
    start = max(0, center - max_chars // 3)
    end = min(len(full_text), start + max_chars)
    if end - start < max_chars:
        start = max(0, end - max_chars)

    prefix = "...[earlier content truncated]...\n" if start > 0 else ""
    suffix = "\n...[later content truncated]..." if end < len(full_text) else ""
    return f"{prefix}{full_text[start:end].strip()}{suffix}"


def _clean_snippet(snippet: str) -> str:
    return re.sub(r"\s+", " ", snippet).strip()


def _build_summary(row: sqlite3.Row, query: str, *, max_chars: int) -> str:
    notice = _summary_notice()
    excerpt = _truncate_around_matches(str(row["content"] or ""), query, max_chars)
    title = str(row["title"] or "(untitled)")
    source_path = str(row["source_path"] or "")
    source_type = str(row["source_type"] or "unknown")
    session_id = str(row["session_id"] or "")
    metadata_bits = [f"source={source_type}", f"path={source_path}", f"title={title}"]
    if session_id:
        metadata_bits.append(f"session_id={session_id}")
    return f"{notice}\nMetadata: {', '.join(metadata_bits)}\nExcerpt:\n{excerpt}"


def _query_rows(
    conn: sqlite3.Connection,
    query: str,
    *,
    limit: int,
    max_snippet_chars: int,
) -> list[SearchResult]:
    match_query = _build_match_query(query)
    if not match_query:
        return []

    sql = f"""
        SELECT
            source_type,
            source_path,
            date,
            project,
            session_id,
            title,
            content,
            snippet({FTS_TABLE}, 7, '[', ']', '...', 24) AS snippet,
            bm25({FTS_TABLE}) AS score
        FROM {FTS_TABLE}
        WHERE {FTS_TABLE} MATCH ?
        ORDER BY score
        LIMIT ?
    """

    try:
        rows = conn.execute(sql, (match_query, limit)).fetchall()
    except sqlite3.OperationalError:
        fallback = " OR ".join(
            _quote_fts_term(term) for term in _TOKEN_RE.findall(query.strip())
        )
        if not fallback or fallback == match_query:
            raise
        rows = conn.execute(sql, (fallback, limit)).fetchall()

    results: list[SearchResult] = []
    for rank, row in enumerate(rows, start=1):
        results.append(
            SearchResult(
                rank=rank,
                source_type=str(row["source_type"] or ""),
                source_path=str(row["source_path"] or ""),
                title=str(row["title"] or ""),
                date=str(row["date"] or ""),
                project=str(row["project"] or ""),
                session_id=str(row["session_id"] or ""),
                score=float(row["score"] or 0.0),
                snippet=_clean_snippet(str(row["snippet"] or "")),
                summary=_build_summary(row, query, max_chars=max_snippet_chars),
            )
        )
    return results


def session_search(
    query: str,
    *,
    root: Path | None = None,
    limit: int = DEFAULT_LIMIT,
    db_path: Path | None = None,
    rebuild: bool = True,
    dry_run: bool = False,
    max_snippet_chars: int = DEFAULT_MAX_SNIPPET_CHARS,
) -> dict[str, Any]:
    """Search Life OS sessions/journals via SQLite FTS5 and return structured results."""
    resolved_root = _resolve_root(root)
    resolved_db_path = db_path or (resolved_root / DEFAULT_DB_RELATIVE)
    try:
        safe_limit = int(limit)
    except (TypeError, ValueError):
        safe_limit = DEFAULT_LIMIT
    safe_limit = max(1, min(safe_limit, 50))

    indexed_count: int | None = None
    if dry_run:
        docs = collect_sources(resolved_root)
        indexed_count = len(docs)
        with _connect(resolved_db_path, dry_run=True) as conn:
            _ensure_schema(conn)
            _insert_docs(conn, docs)
            conn.commit()
            results = _query_rows(
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
            "sources_indexed": indexed_count,
            "count": len(results),
            "results": [asdict(result) for result in results],
        }

    if rebuild:
        indexed_count = rebuild_cache(resolved_root, resolved_db_path, dry_run=dry_run)

    with _connect(resolved_db_path, dry_run=False) as conn:
        results = _query_rows(
            conn,
            query,
            limit=safe_limit,
            max_snippet_chars=max(120, max_snippet_chars),
        )

    return {
        "success": True,
        "query": query,
        "root": str(resolved_root),
        "db_path": ":memory:" if dry_run else str(resolved_db_path),
        "sources_indexed": indexed_count,
        "count": len(results),
        "results": [asdict(result) for result in results],
    }


def _format_human(payload: dict[str, Any]) -> str:
    results = payload["results"]
    if not results:
        indexed = payload.get("sources_indexed")
        suffix = f" Sources indexed: {indexed}." if indexed is not None else ""
        return f"No matches for {payload['query']!r}.{suffix}"

    lines = [
        f"Query: {payload['query']}",
        f"Sources indexed: {payload.get('sources_indexed')}",
        "",
    ]
    for result in results:
        heading_bits = [
            f"{result['rank']}. {result['title'] or '(untitled)'}",
            f"[{result['source_type']}]",
        ]
        if result["date"]:
            heading_bits.append(result["date"])
        if result["project"]:
            heading_bits.append(f"project={result['project']}")
        if result["session_id"]:
            heading_bits.append(f"session={result['session_id']}")
        lines.append(" ".join(heading_bits))
        lines.append(f"   Path: {result['source_path']}")
        if result["snippet"]:
            lines.append(f"   Match: {result['snippet']}")
        lines.append("   Summary:")
        for summary_line in str(result["summary"]).splitlines():
            lines.append(f"   {summary_line}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="session_search",
        description=(
            "SQLite FTS5 search over Life OS _meta/sessions/INDEX.md and "
            "_meta/journal/*.md. No Hermes/Gemini runtime required."
        ),
    )
    parser.add_argument(
        "--query",
        required=True,
        help='Search query, for example: python tools/session_search.py --query "X"',
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Life OS second-brain root (default: LIFE_OS_SECOND_BRAIN_ROOT or cwd)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Maximum results to return (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help=f"SQLite cache path (default: {DEFAULT_DB_RELATIVE.as_posix()})",
    )
    parser.add_argument(
        "--no-rebuild",
        action="store_true",
        help="Reuse the existing cache instead of rebuilding before query",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use an in-memory FTS5 cache; do not write _meta/cache/session-search.db",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured JSON instead of human-readable text",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        payload = session_search(
            args.query,
            root=args.root,
            limit=args.limit,
            db_path=args.db,
            rebuild=not args.no_rebuild,
            dry_run=args.dry_run,
        )
    except sqlite3.OperationalError as exc:
        print(
            f"session_search error: SQLite FTS5 unavailable or query invalid: {exc}",
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(f"session_search error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(_format_human(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
