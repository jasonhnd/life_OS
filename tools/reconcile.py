#!/usr/bin/env python3
"""Integrity checker — orphans, broken wikilinks, missing frontmatter, schema.

Per references/tools-spec.md §6.2. Scans every markdown file under the
second-brain root and emits a ``_meta/reconcile-report-{YYYY-MM-DD}.md``
snapshot of the current integrity state. Same-day re-runs overwrite the
report (idempotent); historical reports live in git, not as timestamped
files.

Usage::

    uv run tools/reconcile.py [--fix] [--verbose] [--root PATH]

Default ``--root`` is the current working directory.

Checks
------

1. **Orphan files** — markdown files under ``inbox/`` with frontmatter
   (implying they've been partially processed but never linked from a
   canonical location).
2. **Broken wikilinks** — ``[[target]]`` references whose target file
   does not exist on disk.
3. **Missing frontmatter** — files under paths that require YAML
   frontmatter (``_meta/**``, ``wiki/**``) but have none.
4. **Schema violations** — files that have frontmatter but are missing
   the minimal required keys (``id``, ``last_modified``).

``--fix`` handles only obvious cases: inserts missing ``last_modified``
(today's date) and ``id`` (from filename stem) defaults, and moves
orphans from ``inbox/`` to ``archive/orphans/``. It never deletes
files; everything is re-playable.

Exit codes
----------

- ``0`` — clean tree, or all issues fixed by ``--fix``.
- ``1`` — unfixable issues remain.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml  # type: ignore[import-untyped]

# Allow running from repo root via `python3 tools/reconcile.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.second_brain import load_markdown  # noqa: E402

# ─── Constants ──────────────────────────────────────────────────────────────

# Directories that require every *.md file to carry YAML frontmatter.
_FRONTMATTER_REQUIRED_DIRS: tuple[str, ...] = ("_meta", "wiki")

# Minimal required frontmatter keys for any note-style file.
_REQUIRED_FM_KEYS: tuple[str, ...] = ("id", "last_modified")

# Directories we skip entirely when scanning (build artefacts, archives).
_SKIP_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
        "archive",
        "backup",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "i18n",
        "pro",
        "references",
        "scripts",
        "docs",
        "evals",
        "tests",
        "tools",
        "themes",
    }
)

# Wikilink regex: [[target]] — target may contain slashes, hyphens, dots,
# unicode word chars. Excludes pipe aliases (``[[target|alias]]``) by
# trimming after ``|``.
_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


# ─── Dataclass ──────────────────────────────────────────────────────────────


@dataclass
class ReconcileReport:
    """Accumulated findings from one reconcile run."""

    orphans: list[Path] = field(default_factory=list)
    broken_links: list[tuple[Path, str]] = field(default_factory=list)
    missing_frontmatter: list[Path] = field(default_factory=list)
    schema_violations: list[tuple[Path, list[str]]] = field(default_factory=list)
    fixed_frontmatter: list[Path] = field(default_factory=list)
    fixed_orphans: list[tuple[Path, Path]] = field(default_factory=list)

    def has_unfixable(self) -> bool:
        return bool(
            self.orphans
            or self.broken_links
            or self.missing_frontmatter
            or self.schema_violations
        )


# ─── Scanning ───────────────────────────────────────────────────────────────


def _iter_markdown_files(root: Path) -> list[Path]:
    """Return every *.md file under ``root`` excluding skip-listed dirs."""
    results: list[Path] = []
    if not root.is_dir():
        return results
    for path in root.rglob("*.md"):
        # Skip files inside any directory whose name is in the skip list.
        parts = set(path.relative_to(root).parts[:-1])
        if parts & _SKIP_DIR_NAMES:
            continue
        results.append(path)
    return results


def _requires_frontmatter(path: Path, root: Path) -> bool:
    """True if the file lives in a directory where frontmatter is required."""
    rel = path.relative_to(root).parts
    if not rel:
        return False
    return rel[0] in _FRONTMATTER_REQUIRED_DIRS


def _is_in_inbox(path: Path, root: Path) -> bool:
    """True if the file is under ``inbox/``."""
    rel = path.relative_to(root).parts
    return bool(rel) and rel[0] == "inbox"


def _is_report_file(path: Path, root: Path) -> bool:
    """True if this is a reconcile-report file itself (skip during scan)."""
    rel = path.relative_to(root).parts
    return (
        len(rel) == 2
        and rel[0] == "_meta"
        and rel[1].startswith("reconcile-report-")
    )


def _parse_frontmatter(path: Path) -> tuple[dict[str, object] | None, str]:
    """Return ``(frontmatter_dict_or_none, body)`` — None means no FM."""
    try:
        parsed = load_markdown(path)
    except (ValueError, OSError):
        return (None, "")
    if not parsed.has_frontmatter:
        return (None, parsed.body)
    return (parsed.frontmatter, parsed.body)


def _check_schema(fm: dict[str, object]) -> list[str]:
    """Return list of missing required keys."""
    return [key for key in _REQUIRED_FM_KEYS if key not in fm]


def _resolve_wikilink_target(root: Path, target: str) -> Path | None:
    """Resolve a ``[[target]]`` reference to an on-disk path, or None."""
    # Normalise path separators — wikilinks use forward slash by convention.
    normalised = target.strip().replace("\\", "/")
    candidate = (
        root / normalised if normalised.endswith(".md") else root / f"{normalised}.md"
    )
    if candidate.is_file():
        return candidate
    # Also try without a leading slash
    candidate_alt = root / normalised.lstrip("/")
    if candidate_alt.is_file():
        return candidate_alt
    return None


def _scan_wikilinks(body: str, root: Path, source: Path) -> list[tuple[Path, str]]:
    """Return broken ``(source, target)`` pairs for every missing wikilink."""
    broken: list[tuple[Path, str]] = []
    for match in _WIKILINK_RE.finditer(body):
        target = match.group(1).strip()
        if not target:
            continue
        if _resolve_wikilink_target(root, target) is None:
            broken.append((source, target))
    return broken


# ─── Core reconcile loop ─────────────────────────────────────────────────────


def run_reconcile(root: Path, logger: logging.Logger) -> ReconcileReport:
    """Scan ``root`` and return a fresh report (no writes)."""
    report = ReconcileReport()
    files = _iter_markdown_files(root)

    for path in files:
        if _is_report_file(path, root):
            continue
        fm, body = _parse_frontmatter(path)
        requires_fm = _requires_frontmatter(path, root)

        if fm is None:
            # No frontmatter.
            if requires_fm:
                logger.debug("missing frontmatter: %s", path)
                report.missing_frontmatter.append(path)
            continue

        # Has frontmatter — check schema.
        missing_keys = _check_schema(fm)
        if missing_keys:
            logger.debug("schema violation: %s missing %s", path, missing_keys)
            report.schema_violations.append((path, missing_keys))

        # Orphan rule: files in inbox/ with frontmatter are treated as
        # orphans by reconcile (they've been partially processed but
        # never linked into the canonical tree).
        if _is_in_inbox(path, root):
            logger.debug("orphan: %s", path)
            report.orphans.append(path)

        # Broken wikilinks.
        for source, target in _scan_wikilinks(body, root, path):
            logger.debug("broken link: %s -> [[%s]]", source, target)
            report.broken_links.append((source, target))

    return report


# ─── --fix actions ───────────────────────────────────────────────────────────


def _fix_missing_frontmatter(path: Path, logger: logging.Logger) -> None:
    """Insert minimal frontmatter (``id``, ``last_modified``) at top of file."""
    original = path.read_text(encoding="utf-8")
    fm_dict = {
        "id": path.stem,
        "last_modified": date.today().isoformat(),
    }
    fm_text = yaml.safe_dump(
        fm_dict, default_flow_style=False, sort_keys=False, allow_unicode=True
    )
    new_content = f"---\n{fm_text}---\n{original}"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(new_content, encoding="utf-8")
    tmp.replace(path)
    logger.info("Inserted frontmatter: %s", path)


def _fix_schema_violation(
    path: Path, missing_keys: list[str], logger: logging.Logger
) -> None:
    """Insert missing required keys into existing frontmatter."""
    parsed = load_markdown(path)
    fm = dict(parsed.frontmatter)
    for key in missing_keys:
        if key == "id":
            fm[key] = path.stem
        elif key == "last_modified":
            fm[key] = date.today().isoformat()
    fm_text = yaml.safe_dump(
        fm, default_flow_style=False, sort_keys=False, allow_unicode=True
    )
    new_content = f"---\n{fm_text}---\n{parsed.body}"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(new_content, encoding="utf-8")
    tmp.replace(path)
    logger.info("Filled schema keys %s: %s", missing_keys, path)


def _fix_orphan(path: Path, root: Path, logger: logging.Logger) -> Path:
    """Move orphan to ``archive/orphans/`` — never deletes."""
    archive_dir = root / "archive" / "orphans"
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / path.name
    # If a file with the same name already exists, append a suffix.
    if target.exists():
        stem = target.stem
        suffix = target.suffix
        i = 1
        while (archive_dir / f"{stem}-{i}{suffix}").exists():
            i += 1
        target = archive_dir / f"{stem}-{i}{suffix}"
    path.replace(target)
    logger.info("Moved orphan: %s -> %s", path, target)
    return target


def apply_fixes(
    report: ReconcileReport, root: Path, logger: logging.Logger
) -> ReconcileReport:
    """Mutate ``report`` in place, applying safe fixes. Returns the report."""
    # Missing frontmatter
    for path in list(report.missing_frontmatter):
        try:
            _fix_missing_frontmatter(path, logger)
            report.fixed_frontmatter.append(path)
        except OSError as exc:
            logger.warning("Could not fix %s: %s", path, exc)
            continue
        report.missing_frontmatter.remove(path)

    # Schema violations — fill in required keys
    for entry in list(report.schema_violations):
        path, missing_keys = entry
        try:
            _fix_schema_violation(path, missing_keys, logger)
            report.fixed_frontmatter.append(path)
        except (OSError, ValueError) as exc:
            logger.warning("Could not fix schema for %s: %s", path, exc)
            continue
        report.schema_violations.remove(entry)

    # Orphans — move to archive/orphans/
    for path in list(report.orphans):
        try:
            new_path = _fix_orphan(path, root, logger)
            report.fixed_orphans.append((path, new_path))
        except OSError as exc:
            logger.warning("Could not move orphan %s: %s", path, exc)
            continue
        report.orphans.remove(path)

    # Broken wikilinks are not auto-fixable (cannot guess intended target).
    return report


# ─── Report rendering ────────────────────────────────────────────────────────


def _rel(path: Path, root: Path) -> str:
    """Return a POSIX-style path relative to root (cross-platform friendly)."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def render_report(report: ReconcileReport, root: Path) -> str:
    """Render a reconcile report as markdown."""
    today = date.today().isoformat()
    lines: list[str] = [
        f"# Reconcile Report — {today}",
        "",
        "_Generated by tools/reconcile.py — snapshot of current integrity state._",
        "",
    ]

    def section(title: str, items: list[str]) -> None:
        lines.append(f"## {title}")
        lines.append("")
        if not items:
            lines.append("_(none)_")
        else:
            for item in items:
                lines.append(f"- {item}")
        lines.append("")

    section(
        "Orphan files",
        [_rel(p, root) for p in sorted(report.orphans)],
    )
    section(
        "Broken wikilinks",
        [
            f"{_rel(src, root)} -> [[{target}]]"
            for src, target in sorted(report.broken_links, key=lambda t: str(t[0]))
        ],
    )
    section(
        "Missing frontmatter",
        [_rel(p, root) for p in sorted(report.missing_frontmatter)],
    )
    section(
        "Schema violations",
        [
            f"{_rel(p, root)} (missing: {', '.join(keys)})"
            for p, keys in sorted(report.schema_violations, key=lambda t: str(t[0]))
        ],
    )

    if report.fixed_frontmatter or report.fixed_orphans:
        lines.append("## Fixed in this run")
        lines.append("")
        for path in sorted(report.fixed_frontmatter):
            lines.append(f"- frontmatter: {_rel(path, root)}")
        for src, dest in report.fixed_orphans:
            lines.append(
                f"- orphan: {_rel(src, root)} -> {_rel(dest, root)}"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_report(content: str, root: Path) -> Path:
    """Write the report atomically to ``_meta/reconcile-report-{today}.md``."""
    meta_dir = root / "_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    target = meta_dir / f"reconcile-report-{today}.md"
    tmp = target.with_suffix(".md.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)
    return target


# ─── CLI ────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reconcile",
        description=(
            "Check the second-brain tree for orphans, broken links, "
            "missing frontmatter, and schema violations. Idempotent."
        ),
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix safe issues (insert missing frontmatter, move orphans).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Path to the second-brain root (default: cwd).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Emit detailed progress on stderr.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point — returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
        stream=sys.stderr,
    )
    logger = logging.getLogger("reconcile")

    try:
        report = run_reconcile(args.root, logger)
        if args.fix:
            apply_fixes(report, args.root, logger)
        content = render_report(report, args.root)
        target = write_report(content, args.root)
        logger.info("Wrote %s", target)
    except OSError as exc:
        logger.error("I/O error during reconcile: %s", exc)
        return 1

    return 1 if report.has_unfixable() else 0


if __name__ == "__main__":
    sys.exit(main())
