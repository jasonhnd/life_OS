"""Session index helpers — SessionSummary IO + INDEX.md compilation.

Used by:
- archiver Phase 2 step ``write_session_summary()`` — produces per-session file
- retrospective Mode 0 step ``rebuild_index()`` — compiles INDEX.md
- tools/rebuild_session_index.py CLI — manual recompile

Per ``references/session-index-spec.md`` §5 (Write Flow) and §4 (INDEX format).
Idempotent: ``compile_index`` produces byte-identical output for identical input.
"""

from __future__ import annotations

from datetime import date as DateType  # noqa: N812 — intentional alias to avoid shadowing
from datetime import datetime
from pathlib import Path
from typing import Any

from tools.lib.second_brain import (
    ParsedMarkdown,
    SessionSummary,
    dump_frontmatter,
    load_markdown,
)

__all__ = [
    "session_summary_to_markdown",
    "write_session_summary",
    "compile_index_line",
    "compile_index",
    "write_index",
    "rebuild_index",
    "truncate_subject",
]


# ─── SessionSummary IO ───────────────────────────────────────────────────────


_SUBJECT_TRUNCATE_LEN = 80


def truncate_subject(subject: str, max_len: int = _SUBJECT_TRUNCATE_LEN) -> str:
    """Truncate subject to ``max_len`` chars, append ellipsis if truncated."""
    if len(subject) <= max_len:
        return subject
    return subject[:max_len].rstrip() + "…"


def _summary_to_frontmatter(summary: SessionSummary) -> dict[str, Any]:
    """Convert SessionSummary dataclass to a YAML-serializable frontmatter dict."""
    fm: dict[str, Any] = {
        "session_id": summary.session_id,
        "date": summary.date.isoformat(),
        "started_at": summary.started_at.isoformat(),
        "ended_at": summary.ended_at.isoformat(),
        "duration_minutes": summary.duration_minutes,
        "platform": summary.platform,
        "theme": summary.theme,
        "project": summary.project,
        "workflow": summary.workflow,
        "subject": summary.subject,
        "overall_score": summary.overall_score,
        "veto_count": summary.veto_count,
        "council_triggered": summary.council_triggered,
        "compliance_violations": summary.compliance_violations,
    }
    # Optional list/dict fields — only include if non-empty (keeps frontmatter terse)
    optional_lists = (
        ("domains_activated", summary.domains_activated),
        ("soul_dimensions_touched", summary.soul_dimensions_touched),
        ("wiki_written", summary.wiki_written),
        ("methods_used", summary.methods_used),
        ("methods_discovered", summary.methods_discovered),
        ("concepts_activated", summary.concepts_activated),
        ("concepts_discovered", summary.concepts_discovered),
        ("dream_triggers", summary.dream_triggers),
        ("keywords", summary.keywords),
    )
    for key, val in optional_lists:
        if val:
            fm[key] = val
    if summary.domain_scores:
        fm["domain_scores"] = summary.domain_scores
    if summary.action_items:
        fm["action_items"] = [
            {
                "text": ai.text,
                **({"deadline": ai.deadline.isoformat()} if ai.deadline else {}),
                "status": ai.status,
            }
            for ai in summary.action_items
        ]
    return fm


def session_summary_to_markdown(summary: SessionSummary) -> str:
    """Serialise a SessionSummary to markdown (frontmatter + body).

    Body content is the caller's responsibility (archiver Phase 2 produces the
    four standard sections: Subject, Key Decisions, Outcome, Notable Signals).
    This helper just wraps frontmatter around the body string.
    """
    return dump_frontmatter(_summary_to_frontmatter(summary), summary.body)


def write_session_summary(summary: SessionSummary, outbox_root: Path) -> Path:
    """Write SessionSummary to ``<outbox_root>/{session_id}/sessions/{session_id}.md``.

    Per spec §5: archiver writes to outbox first; retrospective Mode 0
    outbox-merge step moves it to the canonical
    ``_meta/sessions/{session_id}.md`` location.

    Returns the path written.
    """
    outbox_dir = outbox_root / summary.session_id / "sessions"
    outbox_dir.mkdir(parents=True, exist_ok=True)
    target = outbox_dir / f"{summary.session_id}.md"
    target.write_text(session_summary_to_markdown(summary), encoding="utf-8")
    return target


# ─── INDEX.md compilation ────────────────────────────────────────────────────


def compile_index_line(parsed: ParsedMarkdown) -> str | None:
    """Format one INDEX.md line from a parsed session summary.

    Per spec §4 line format:
        ``{date} | {project} | {subject-truncated} | {score}/10 | [{kw-top3}] | {session_id}``

    Returns ``None`` if frontmatter lacks required fields (caller logs + skips).
    """
    fm = parsed.frontmatter
    try:
        date_field = fm["date"]
        project = fm.get("project", "<unknown>")
        subject = truncate_subject(str(fm.get("subject", "")))
        score = fm.get("overall_score")
        score_str = f"{score:.1f}" if isinstance(score, (int, float)) else "n/a"
        keywords_full = fm.get("keywords") or []
        keywords_top3 = ", ".join(str(k) for k in keywords_full[:3])
        session_id = fm["session_id"]
    except (KeyError, TypeError):
        return None

    return f"{date_field} | {project} | {subject} | {score_str}/10 | [{keywords_top3}] | {session_id}"


def _date_value(parsed: ParsedMarkdown) -> str:
    """Extract date string from frontmatter for sorting (always ISO-comparable)."""
    d = parsed.frontmatter.get("date")
    if isinstance(d, DateType):
        return d.isoformat()
    return str(d) if d else ""


def _started_at_value(parsed: ParsedMarkdown) -> str:
    """Extract started_at string from frontmatter for tie-breaking same-day sessions."""
    s = parsed.frontmatter.get("started_at")
    if isinstance(s, datetime):
        return s.isoformat()
    return str(s) if s else ""


def _month_key(parsed: ParsedMarkdown) -> str:
    """Extract YYYY-MM from date for ## heading grouping."""
    date_str = _date_value(parsed)
    return date_str[:7] if len(date_str) >= 7 else "unknown"


def compile_index(sessions_dir: Path) -> str:
    """Scan ``sessions_dir/*.md`` (excluding INDEX.md), return INDEX.md content.

    Per spec §5 (INDEX compilation):
    - Sort by date desc, secondary sort by started_at desc (same-day ties)
    - Group by YYYY-MM (## heading), most recent month first
    - Skip files with malformed YAML (degrades gracefully)

    Idempotent: identical input produces byte-identical output.
    Returns the empty-state string if ``sessions_dir`` does not exist.
    """
    if not sessions_dir.exists():
        return _empty_index()

    parsed_list: list[ParsedMarkdown] = []
    for path in sorted(sessions_dir.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        try:
            parsed = load_markdown(path)
        except (ValueError, OSError):
            continue
        if not parsed.frontmatter:
            continue
        parsed_list.append(parsed)

    # Sort by date desc, then started_at desc
    parsed_list.sort(
        key=lambda p: (_date_value(p), _started_at_value(p)),
        reverse=True,
    )

    # Group by YYYY-MM, preserving descending order within each group
    groups: dict[str, list[str]] = {}
    for parsed in parsed_list:
        line = compile_index_line(parsed)
        if line is None:
            continue
        key = _month_key(parsed)
        groups.setdefault(key, []).append(line)

    if not groups:
        return _empty_index()

    out_lines = ["# Session Index", ""]
    for month in sorted(groups.keys(), reverse=True):
        if month == "unknown":
            out_lines.append("## Unknown date")
        else:
            out_lines.append(f"## {month}")
        out_lines.append("")
        out_lines.extend(groups[month])
        out_lines.append("")

    return "\n".join(out_lines).rstrip() + "\n"


def _empty_index() -> str:
    """Minimal INDEX.md content for an empty or first-session state."""
    return "# Session Index\n\n_(no sessions indexed yet)_\n"


def write_index(content: str, sessions_dir: Path) -> Path:
    """Write INDEX.md content to ``sessions_dir/INDEX.md`` atomically (tmp + rename)."""
    sessions_dir.mkdir(parents=True, exist_ok=True)
    target = sessions_dir / "INDEX.md"
    tmp = target.with_suffix(".md.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)
    return target


def rebuild_index(second_brain_root: Path) -> tuple[Path, int]:
    """Recompile INDEX.md from all session files in ``<root>/_meta/sessions/``.

    Returns ``(path_written, session_count)`` where session_count is the number
    of indexed sessions (lines containing ``|``, excluding headings).
    """
    sessions_dir = second_brain_root / "_meta" / "sessions"
    content = compile_index(sessions_dir)
    target = write_index(content, sessions_dir)
    line_count = sum(
        1
        for line in content.splitlines()
        if " | " in line and not line.startswith("#")
    )
    return target, line_count
