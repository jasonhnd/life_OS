#!/usr/bin/env python3
"""Cross-session grep + metadata-ranked search — v1.7 Sprint 4.

Contract: references/tools-spec.md §6.8.

Deterministic ranking (no LLM):

    base_score = 4.0 * subject_hits
               + 2.0 * (domains_hits + keywords_hits)
               + 1.0 * min(body_paragraph_hits, 5)

    recency_mult = 1.5 if days_since <= recency_boost_days else 1.0
    final_score  = base_score * recency_mult

Tie-break by newer session first. Empty result prints "no matches" and
exits 0 (per spec — empty results are valid).

Usage::

    uv run tools/search.py "query" [--top N]

Implementation notes:
- No dependency on INDEX.md — we read per-session .md files directly so
  the tool works when INDEX.md is stale or missing. Reading 1,000 small
  markdown files is well under the 3-second budget (<30 MB of I/O).
- Multi-word query is OR-matched: a session scores positive if any term
  hits any surface. This matches user expectation for a quick search
  tool; semantic ranking is the hippocampus subagent's job.
- Matching is case-insensitive, plain substring (no regex), consistent
  with grep-style recall over quality.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.config import ConfigError, load_config  # noqa: E402
from tools.lib.second_brain import load_markdown  # noqa: E402

# ─── Constants ──────────────────────────────────────────────────────────────

_DEFAULT_TOP_N = 5
_SNIPPET_MAX_LEN = 80
_BODY_PARAGRAPH_HIT_CAP = 5
_RECENCY_MULT_BOOST = 1.5
_RECENCY_MULT_FLAT = 1.0
_W_SUBJECT = 4.0
_W_META = 2.0  # domains + keywords
_W_BODY = 1.0

# Paragraphs = blocks separated by one-or-more blank lines.
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")


# ─── Data types ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SearchResult:
    """One ranked search hit."""

    session_id: str
    path: Path
    score: float
    snippet: str
    session_date: date


# ─── Scoring primitives ─────────────────────────────────────────────────────


def _term_hits_in_text(text: str, term: str) -> int:
    """Count case-insensitive occurrences of ``term`` in ``text``."""
    if not term:
        return 0
    return text.lower().count(term.lower())


def _term_hits_in_list(items: list[object], term: str) -> int:
    """Count how many list elements contain ``term`` (case-insensitive)."""
    lowered = term.lower()
    hits = 0
    for item in items:
        if lowered in str(item).lower():
            hits += 1
    return hits


def _count_paragraph_hits(body: str, terms: list[str]) -> int:
    """Count paragraphs containing AT LEAST one query term (each paragraph
    counts at most once even if it contains several terms multiple times).

    Per spec §6.8: "hits_in_body_paragraphs counts at most once per paragraph".
    """
    if not body.strip() or not terms:
        return 0
    paragraphs = _PARAGRAPH_SPLIT_RE.split(body)
    lowered_terms = [t.lower() for t in terms if t]
    count = 0
    for para in paragraphs:
        lower_para = para.lower()
        if any(t in lower_para for t in lowered_terms):
            count += 1
    return count


def _parse_session_date(fm: dict[str, object]) -> date | None:
    """Extract a date from frontmatter 'date' field, tolerating str/date."""
    value = fm.get("date")
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _split_terms(query: str) -> list[str]:
    """Split query into non-empty terms (whitespace-separated)."""
    return [t for t in query.split() if t]


# ─── Ranking ────────────────────────────────────────────────────────────────


def _score_session(
    parsed_fm: dict[str, object],
    body: str,
    terms: list[str],
    today: date,
    recency_boost_days: int,
    session_date: date | None,
) -> float:
    """Compute the final score for one session against the query terms."""
    subject = str(parsed_fm.get("subject", ""))
    domains_raw = parsed_fm.get("domains_activated") or []
    keywords_raw = parsed_fm.get("keywords") or []
    domains: list[object] = list(domains_raw) if isinstance(domains_raw, list) else []
    keywords: list[object] = (
        list(keywords_raw) if isinstance(keywords_raw, list) else []
    )

    subject_hits = sum(_term_hits_in_text(subject, t) for t in terms)
    domain_hits = sum(_term_hits_in_list(domains, t) for t in terms)
    keyword_hits = sum(_term_hits_in_list(keywords, t) for t in terms)
    body_hits_raw = _count_paragraph_hits(body, terms)
    body_hits = min(body_hits_raw, _BODY_PARAGRAPH_HIT_CAP)

    base = (
        _W_SUBJECT * subject_hits
        + _W_META * (domain_hits + keyword_hits)
        + _W_BODY * body_hits
    )

    if session_date is None:
        mult = _RECENCY_MULT_FLAT
    else:
        days_since = (today - session_date).days
        mult = (
            _RECENCY_MULT_BOOST
            if 0 <= days_since <= recency_boost_days
            else _RECENCY_MULT_FLAT
        )

    return base * mult


def _build_snippet(subject: str, body: str) -> str:
    """Return up to 80 chars of flavor text — subject if set, else body head."""
    text = subject.strip() if subject.strip() else body.strip().split("\n", 1)[0]
    text = text.replace("\n", " ").strip()
    if len(text) <= _SNIPPET_MAX_LEN:
        return text
    return text[:_SNIPPET_MAX_LEN].rstrip() + "…"


def rank_sessions(
    second_brain_root: Path,
    query: str,
    *,
    today: date | None = None,
    recency_boost_days: int = 90,
) -> list[SearchResult]:
    """Rank every session under ``_meta/sessions/`` against the query.

    Returns a list of :class:`SearchResult` sorted by score desc, ties
    broken by newer ``session_date`` first. Sessions with zero score are
    excluded (they're irrelevant, not ambiguous).
    """
    sessions_dir = second_brain_root / "_meta" / "sessions"
    if not sessions_dir.exists():
        return []

    terms = _split_terms(query)
    if not terms:
        return []

    today = today or date.today()
    results: list[SearchResult] = []

    for path in sessions_dir.glob("*.md"):
        if path.name == "INDEX.md":
            continue
        try:
            parsed = load_markdown(path)
        except (ValueError, OSError):
            continue
        fm = parsed.frontmatter or {}
        if not fm:
            continue

        session_date = _parse_session_date(fm)
        score = _score_session(
            fm,
            parsed.body,
            terms,
            today,
            recency_boost_days,
            session_date,
        )
        if score <= 0.0:
            continue

        session_id = str(fm.get("session_id", path.stem))
        snippet = _build_snippet(str(fm.get("subject", "")), parsed.body)
        results.append(
            SearchResult(
                session_id=session_id,
                path=path,
                score=score,
                snippet=snippet,
                session_date=session_date or date.min,
            )
        )

    # Sort: score desc; tie-break by date desc (newer first); stable secondary
    # tie-break on session_id desc so same-date sessions still order deterministically.
    results.sort(
        key=lambda r: (r.score, r.session_date, r.session_id),
        reverse=True,
    )
    return results


# ─── CLI ────────────────────────────────────────────────────────────────────


def _format_line(rank: int, result: SearchResult) -> str:
    return f"{rank}. {result.path}  (score={result.score:.1f})  {result.snippet}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="search",
        description=(
            "Grep + metadata-ranked search across Life OS session summaries "
            "(references/tools-spec.md §6.8). Deterministic, LLM-free."
        ),
    )
    parser.add_argument("query", help="Query string (whitespace OR-matched)")
    parser.add_argument(
        "--top",
        type=int,
        default=_DEFAULT_TOP_N,
        help="Max number of results to print (default: 5)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Second-brain root (default: CWD)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    root = args.root if args.root is not None else Path.cwd()

    # Config resolves recency_boost_days; falls back to default 90 when no
    # .life-os.toml is present (load_config is defensive about missing files).
    # Round-3 audit fix: catch the project's own ConfigError (semantic
    # signal for "config malformed/missing") plus FileNotFoundError (file
    # genuinely absent). Other exceptions (ImportError / AttributeError /
    # bugs in config loader) propagate so the user sees them.
    try:
        cfg = load_config(root)
        recency_boost_days = cfg.search_recency_boost_days
    except (ConfigError, FileNotFoundError) as exc:
        print(
            f"[search] config load failed ({type(exc).__name__}: {exc}); "
            "using default recency_boost_days=90",
            file=sys.stderr,
        )
        recency_boost_days = 90

    results = rank_sessions(
        root,
        args.query,
        recency_boost_days=recency_boost_days,
    )

    if not results:
        print("no matches")
        return 0

    top_n = max(1, args.top)
    for rank, res in enumerate(results[:top_n], start=1):
        print(_format_line(rank, res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
