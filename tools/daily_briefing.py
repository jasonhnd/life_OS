#!/usr/bin/env python3
"""Today's Briefing — v1.7 Sprint 4 (references/tools-spec.md §6.5).

Pure data aggregation. Writes a five-section markdown snapshot to stdout:

    # Today's Briefing — {YYYY-MM-DD}
    ## SOUL Core
    ## Recent DREAMs (last 30 days: N reports)
    ## Active Projects (N)
    ## Inbox (N pending)
    ## Eval History (last 3)

Always exits 0 (even if the brain is empty). Runtime budget: < 3 seconds.

No LLM, no network. Retrospective subagent decides what to foreground.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # type: ignore[import-untyped]  # noqa: E402

from tools.lib.second_brain import load_markdown  # noqa: E402

# ─── Constants ──────────────────────────────────────────────────────────────

_SOUL_CORE_THRESHOLD = 0.7
_DREAM_WINDOW_DAYS = 30
_PROJECT_ACTIVE_DAYS = 14
_EVAL_LAST_N = 3

# Dimension header marker inside SOUL.md — per SOUL-template.md
_SOUL_DIMENSION_HEADER_RE = re.compile(r"^##\s+Dimension:\s*(.+)$", re.MULTILINE)
# YAML code block fence inside each dimension block
_YAML_BLOCK_RE = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)
# dream file name: YYYY-MM-DD-dream.md
_DREAM_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-dream\.md$")
# eval-history filename: YYYY-MM-DD-{project}.md
_EVAL_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")


# ─── Data types ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SoulDimension:
    name: str
    confidence: float


@dataclass(frozen=True)
class ActiveProject:
    name: str
    last_modified: datetime


@dataclass(frozen=True)
class EvalSnapshot:
    entry_date: date
    project: str
    score: float | None


# ─── SOUL parsing ───────────────────────────────────────────────────────────


def _parse_soul(root: Path) -> list[SoulDimension]:
    """Parse SOUL.md into a list of dimensions. Missing file → empty list."""
    path = root / "SOUL.md"
    if not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []

    # Split by dimension header; the regex captures the name so we use split+iter
    dimensions: list[SoulDimension] = []
    # Find indexes of dimension header matches
    matches = list(_SOUL_DIMENSION_HEADER_RE.finditer(text))
    for idx, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[start:end]
        yaml_match = _YAML_BLOCK_RE.search(block)
        if not yaml_match:
            continue
        try:
            data = yaml.safe_load(yaml_match.group(1)) or {}
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        conf = data.get("confidence")
        if not isinstance(conf, (int, float)):
            continue
        dimensions.append(SoulDimension(name=name, confidence=float(conf)))
    return dimensions


def _soul_core(dimensions: list[SoulDimension]) -> list[SoulDimension]:
    return [d for d in dimensions if d.confidence >= _SOUL_CORE_THRESHOLD]


# ─── DREAM parsing ──────────────────────────────────────────────────────────


def _parse_dream_date(name: str) -> date | None:
    m = _DREAM_FILE_RE.match(name)
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1))
    except ValueError:
        return None


def _count_recent_dreams(root: Path, today: date) -> int:
    journal = root / "_meta" / "journal"
    if not journal.is_dir():
        return 0
    count = 0
    for path in journal.iterdir():
        if not path.is_file():
            continue
        d = _parse_dream_date(path.name)
        if d is None:
            continue
        if (today - d).days <= _DREAM_WINDOW_DAYS and d <= today:
            count += 1
    return count


# ─── Project parsing ────────────────────────────────────────────────────────


def _coerce_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            try:
                return datetime.combine(date.fromisoformat(value), datetime.min.time())
            except ValueError:
                return None
    return None


def _iter_active_projects(root: Path, today: date) -> list[ActiveProject]:
    projects_dir = root / "projects"
    if not projects_dir.is_dir():
        return []

    # Active window: last_modified date within the past `_PROJECT_ACTIVE_DAYS`
    # (inclusive). Comparing at day granularity keeps boundaries predictable
    # regardless of HH:MM:SS in the stored timestamp.
    active: list[ActiveProject] = []
    for project_dir in sorted(projects_dir.iterdir()):
        if not project_dir.is_dir():
            continue
        index = project_dir / "index.md"
        if not index.is_file():
            continue
        try:
            parsed = load_markdown(index)
        except (ValueError, OSError):
            continue
        fm = parsed.frontmatter or {}
        last_mod = _coerce_datetime(fm.get("last_modified"))
        if last_mod is None:
            continue
        days_since = (today - last_mod.date()).days
        if days_since < 0 or days_since > _PROJECT_ACTIVE_DAYS:
            continue
        active.append(
            ActiveProject(
                name=str(fm.get("name", project_dir.name)),
                last_modified=last_mod,
            )
        )
    # Sort by last_modified desc for display stability.
    active.sort(key=lambda p: p.last_modified, reverse=True)
    return active


# ─── Inbox ──────────────────────────────────────────────────────────────────


def _count_inbox(root: Path) -> int:
    inbox = root / "inbox"
    if not inbox.is_dir():
        return 0
    return sum(1 for p in inbox.iterdir() if p.is_file() and p.suffix == ".md")


# ─── Eval history ───────────────────────────────────────────────────────────


def _iter_recent_evals(root: Path, limit: int = _EVAL_LAST_N) -> list[EvalSnapshot]:
    eval_dir = root / "_meta" / "eval-history"
    if not eval_dir.is_dir():
        return []
    snapshots: list[EvalSnapshot] = []
    for path in eval_dir.iterdir():
        if not path.is_file() or path.suffix != ".md":
            continue
        m = _EVAL_FILE_RE.match(path.name)
        if not m:
            continue
        try:
            entry_date = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        project = m.group(2)
        try:
            parsed = load_markdown(path)
        except (ValueError, OSError):
            continue
        fm = parsed.frontmatter or {}
        score_raw = fm.get("overall_score")
        score = float(score_raw) if isinstance(score_raw, (int, float)) else None
        snapshots.append(
            EvalSnapshot(entry_date=entry_date, project=project, score=score)
        )
    snapshots.sort(key=lambda e: (e.entry_date, e.project), reverse=True)
    return snapshots[:limit]


# ─── Formatting ─────────────────────────────────────────────────────────────


def _format_soul_section(core: list[SoulDimension]) -> str:
    lines = ["## SOUL Core", ""]
    if not core:
        lines.append("_(0 core dimensions)_")
    else:
        # Sort descending by confidence so the strongest identity signals lead.
        for dim in sorted(core, key=lambda d: d.confidence, reverse=True):
            lines.append(f"- **{dim.name}** (confidence {dim.confidence:.2f})")
    return "\n".join(lines)


def _format_dreams_section(count: int) -> str:
    return (
        f"## Recent DREAMs (last 30 days: {count} reports)\n\n"
        + (
            "_(none within window)_"
            if count == 0
            else f"{count} dream report(s) available in `_meta/journal/`."
        )
    )


def _format_projects_section(active: list[ActiveProject]) -> str:
    lines = [f"## Active Projects ({len(active)})", ""]
    if not active:
        lines.append("_(no projects modified in the last 14 days)_")
    else:
        for proj in active:
            lines.append(
                f"- **{proj.name}** — last modified "
                f"{proj.last_modified.date().isoformat()}"
            )
    return "\n".join(lines)


def _format_inbox_section(count: int) -> str:
    return (
        f"## Inbox ({count} pending)\n\n"
        + ("_(empty)_" if count == 0 else f"{count} item(s) in `inbox/` awaiting triage.")
    )


def _format_evals_section(evals: list[EvalSnapshot]) -> str:
    lines = [f"## Eval History (last {_EVAL_LAST_N})", ""]
    if not evals:
        lines.append("_(no eval entries yet)_")
    else:
        for snap in evals:
            score_str = f"{snap.score:.1f}" if snap.score is not None else "n/a"
            lines.append(
                f"- {snap.entry_date.isoformat()} · **{snap.project}** — "
                f"score {score_str}"
            )
    return "\n".join(lines)


# ─── Top-level entry ────────────────────────────────────────────────────────


def build_briefing(root: Path, *, today: date | None = None) -> str:
    """Assemble the full briefing markdown for ``root``.

    Always returns a non-empty string; never raises on missing brain files.
    """
    today = today or date.today()
    soul_core = _soul_core(_parse_soul(root))
    dream_count = _count_recent_dreams(root, today)
    active = _iter_active_projects(root, today)
    inbox_n = _count_inbox(root)
    evals = _iter_recent_evals(root)

    sections = [
        f"# Today's Briefing — {today.isoformat()}",
        "",
        _format_soul_section(soul_core),
        "",
        _format_dreams_section(dream_count),
        "",
        _format_projects_section(active),
        "",
        _format_inbox_section(inbox_n),
        "",
        _format_evals_section(evals),
        "",
    ]
    return "\n".join(sections)


# ─── CLI ────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="daily_briefing",
        description=(
            "Generate today's briefing — SOUL core + DREAM + active projects + inbox "
            "+ eval-history (references/tools-spec.md §6.5)."
        ),
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
    print(build_briefing(root), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
