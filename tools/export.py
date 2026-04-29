#!/usr/bin/env python3
"""Format conversion CLI — markdown to pdf / html / json / anki.

Spec: references/tools-spec.md §6.9.

Reads every ``*.md`` file under ``--scope`` and emits a single
``exports/{scope-slug}-{YYYY-MM-DD}.{ext}`` file. Each format has its
own implementation; the dispatcher in :func:`run` picks one.

Usage:
    uv run tools/export.py --format {pdf|html|json|anki} --scope PATH [--output-dir PATH]

Formats:
    pdf   -- external pandoc binary (>=3.0). Exit 1 if pandoc missing.
    html  -- self-contained, inline CSS, via markdown-it-py with footnote + table plugins.
    json  -- flat array, each element {frontmatter: {...}, body: "..."}
    anki  -- .apkg via genanki, deck_name = scope-slug, per-type field mapping.

Per-type Anki field mapping (§6.9):

    concept  Front = canonical_name + aliases
             Back  = body + outgoing_edges table (top 5 by weight)
    method   Front = name
             Back  = summary + ## Steps section
    wiki     Front = title (conclusion)
             Back  = Reasoning + Applicable-When sections
    session  Front = subject
             Back  = Key Decisions + Outcome

Exit codes:
    0  success
    1  scope empty / missing; pandoc or genanki unavailable; unknown format

Runtime budget: < 30 seconds per 100 files.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.second_brain import ParsedMarkdown, load_markdown  # noqa: E402

# ─── Constants ──────────────────────────────────────────────────────────────

_SUPPORTED_FORMATS = frozenset({"pdf", "html", "json", "anki"})
_MAX_EDGES_PER_CONCEPT = 5
_DEFAULT_ANKI_MODEL_ID = 1_702_193_001  # stable int; arbitrary but fixed
_DEFAULT_ANKI_DECK_ID = 2_059_400_110

_INLINE_CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
       max-width: 760px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; }
h1, h2, h3 { color: #222; }
code { background: #f4f4f4; padding: 0.1em 0.3em; border-radius: 3px; }
pre code { display: block; padding: 0.8em; overflow-x: auto; }
table { border-collapse: collapse; margin: 1em 0; }
th, td { border: 1px solid #ccc; padding: 0.4em 0.8em; }
article { border-bottom: 1px solid #ddd; margin-bottom: 2rem; padding-bottom: 2rem; }
article:last-child { border-bottom: none; }
""".strip()


# ─── Small data types ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class AnkiNote:
    """One Anki note: (front, back, type_name) with a deterministic guid."""

    front: str
    back: str
    type_name: str  # "concept" | "method" | "wiki" | "session"
    guid: str  # deterministic per-source-file


# ─── Slug + path helpers ────────────────────────────────────────────────────


def slug_from_scope(scope: Path) -> str:
    """Derive a filesystem-safe slug from a scope path (lowercase, dashes)."""
    name = scope.name or scope.resolve().name
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-") or "scope"


def output_filename(scope: Path, fmt: str, today: date | None = None) -> str:
    """Return ``{scope-slug}-{YYYY-MM-DD}.{ext}``.

    ``today`` is overridable to keep tests deterministic.
    """
    today = today or date.today()
    return f"{slug_from_scope(scope)}-{today.isoformat()}.{fmt}"


# ─── Markdown collection ────────────────────────────────────────────────────


def collect_markdown(scope: Path) -> list[ParsedMarkdown]:
    """Return every parsed markdown document under ``scope`` (recursive)."""
    if not scope.is_dir():
        return []
    docs: list[ParsedMarkdown] = []
    for path in sorted(scope.rglob("*.md")):
        if not path.is_file():
            continue
        try:
            docs.append(load_markdown(path))
        except (OSError, ValueError) as exc:  # pragma: no cover - malformed files
            print(f"[warn] skipping {path}: {exc}", file=sys.stderr)
    return docs


# ─── JSON export ────────────────────────────────────────────────────────────


def export_json(scope: Path, out_path: Path) -> int:
    """Write ``[{frontmatter, body}, ...]`` to ``out_path``."""
    docs = collect_markdown(scope)
    if not docs:
        print("[export] empty scope: no markdown files found", file=sys.stderr)
        return 1
    payload = [
        {"frontmatter": d.frontmatter, "body": d.body}
        for d in docs
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return 0


# ─── HTML export ────────────────────────────────────────────────────────────


def _build_md_renderer() -> Any:
    """Build a markdown-it renderer with table + footnote plugins.

    Imported lazily so the test for missing markdown-it is meaningful.
    """
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark", {"breaks": False, "html": False}).enable(
        ["table"]
    )
    # Footnote plugin is separate package; prefer builtin if available.
    try:
        from mdit_py_plugins.footnote import footnote_plugin  # type: ignore[import-not-found]

        md.use(footnote_plugin)
    except ModuleNotFoundError:
        pass
    return md


def export_html(scope: Path, out_path: Path) -> int:
    """Render all docs into one self-contained HTML file (inline CSS)."""
    docs = collect_markdown(scope)
    if not docs:
        print("[export] empty scope: no markdown files found", file=sys.stderr)
        return 1
    md = _build_md_renderer()
    articles: list[str] = []
    for doc in docs:
        rendered = md.render(doc.body)
        articles.append(f"<article>{rendered}</article>")
    title = slug_from_scope(scope)
    html = (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        f"<meta charset=\"utf-8\"><title>{title}</title>\n"
        f"<style>{_INLINE_CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        + "\n".join(articles)
        + "\n</body>\n</html>\n"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return 0


# ─── PDF export (pandoc) ────────────────────────────────────────────────────


def _pandoc_available() -> bool:
    """Return True if the ``pandoc`` binary is on PATH."""
    return shutil.which("pandoc") is not None


def export_pdf(scope: Path, out_path: Path) -> int:
    """Invoke pandoc to render a concatenated markdown file to PDF.

    Returns 1 when pandoc is unavailable or exits non-zero; 0 on success.
    """
    docs = collect_markdown(scope)
    if not docs:
        print("[export] empty scope: no markdown files found", file=sys.stderr)
        return 1
    if not _pandoc_available():
        print(
            "[export] pandoc binary not found on PATH; install pandoc >= 3.0 "
            "to use --format pdf (see https://pandoc.org/installing.html)",
            file=sys.stderr,
        )
        return 1

    # Concatenate all docs with separators into a temp markdown file.
    tmp_dir = out_path.parent / ".export-tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    combined = tmp_dir / "combined.md"
    body_parts: list[str] = []
    for doc in docs:
        body_parts.append(doc.body.rstrip())
    combined.write_text("\n\n---\n\n".join(body_parts), encoding="utf-8")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # R-1.8.0-013 deep-audit fix: 60s timeout prevents pandoc hanging
    # indefinitely on malformed input or filesystem stalls. Most exports
    # complete in < 5 seconds; 60s is a generous upper bound.
    try:
        result = subprocess.run(
            ["pandoc", str(combined), "-o", str(out_path)],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except subprocess.TimeoutExpired as exc:  # pragma: no cover
        size = combined.stat().st_size if combined.exists() else "unknown"
        print(
            f"[export] pandoc timed out after {exc.timeout}s. "
            f"Input file size: {size} bytes. "
            "Try splitting the export into smaller scopes or reducing entry count.",
            file=sys.stderr,
        )
        return 1
    except (OSError, FileNotFoundError) as exc:  # pragma: no cover
        print(f"[export] pandoc invocation failed: {exc}", file=sys.stderr)
        return 1
    finally:
        # best-effort cleanup; don't hide errors if any
        try:
            combined.unlink(missing_ok=True)
            tmp_dir.rmdir()
        except OSError:  # pragma: no cover
            pass

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        print(f"[export] pandoc exit {result.returncode}: {stderr}", file=sys.stderr)
        return 1
    return 0


# ─── Anki export (per-type mapping) ─────────────────────────────────────────


def _stringify_aliases(frontmatter: dict[str, Any]) -> str:
    aliases = frontmatter.get("aliases") or []
    if not isinstance(aliases, list):
        return ""
    return ", ".join(str(a) for a in aliases)


def _edges_table(frontmatter: dict[str, Any]) -> str:
    """Render the top-N outgoing_edges as a small HTML table (max 5 by weight)."""
    edges_raw = frontmatter.get("outgoing_edges") or []
    if not isinstance(edges_raw, list):
        return ""
    edges: list[tuple[str, int]] = []
    for item in edges_raw:
        if not isinstance(item, dict):
            continue
        target = str(item.get("target", ""))
        try:
            weight = int(item.get("weight", 0))
        except (TypeError, ValueError):
            weight = 0
        if target:
            edges.append((target, weight))
    edges.sort(key=lambda e: (-e[1], e[0]))
    top = edges[:_MAX_EDGES_PER_CONCEPT]
    if not top:
        return ""
    rows = "".join(f"<tr><td>{t}</td><td>{w}</td></tr>" for t, w in top)
    return (
        "<table><thead><tr><th>target</th><th>weight</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def _section(body: str, heading: str) -> str:
    """Return the text under the ``## heading`` (case-insensitive) until the
    next ``##`` heading or EOF. Empty string if not found.
    """
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(body)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", body[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(body)
    return body[start:end].strip()


def _make_note(
    *,
    front: str,
    back: str,
    type_name: str,
    source: Path | None,
) -> AnkiNote:
    # guid is deterministic: type + source path; so re-exports don't duplicate.
    guid_basis = f"{type_name}|{source.as_posix() if source else front}"
    return AnkiNote(front=front, back=back, type_name=type_name, guid=guid_basis)


def _build_note_for_concept(doc: ParsedMarkdown) -> AnkiNote:
    fm = doc.frontmatter
    canonical = str(fm.get("canonical_name") or fm.get("concept_id") or "")
    aliases = _stringify_aliases(fm)
    front = canonical if not aliases else f"{canonical}<br><small>{aliases}</small>"
    edges_html = _edges_table(fm)
    back_parts = [doc.body.strip()]
    if edges_html:
        back_parts.append(edges_html)
    return _make_note(
        front=front,
        back="<br><br>".join(p for p in back_parts if p),
        type_name="concept",
        source=doc.source_path,
    )


def _build_note_for_method(doc: ParsedMarkdown) -> AnkiNote:
    fm = doc.frontmatter
    name = str(fm.get("name") or fm.get("canonical_name") or fm.get("method_id") or "")
    summary = str(fm.get("summary") or "").strip()
    steps = _section(doc.body, "Steps")
    back_parts = [p for p in (summary, steps) if p]
    return _make_note(
        front=name,
        back="\n\n".join(back_parts),
        type_name="method",
        source=doc.source_path,
    )


def _build_note_for_wiki(doc: ParsedMarkdown) -> AnkiNote:
    fm = doc.frontmatter
    title = str(fm.get("title") or fm.get("slug") or "")
    reasoning = _section(doc.body, "Reasoning")
    applicable = _section(doc.body, "Applicable When") or _section(
        doc.body, "Applicable-When"
    )
    back_parts = [p for p in (reasoning, applicable) if p]
    return _make_note(
        front=title,
        back="\n\n".join(back_parts),
        type_name="wiki",
        source=doc.source_path,
    )


def _build_note_for_session(doc: ParsedMarkdown) -> AnkiNote:
    fm = doc.frontmatter
    subject = str(fm.get("subject") or fm.get("session_id") or "")
    decisions = _section(doc.body, "Key Decisions")
    outcome = _section(doc.body, "Outcome")
    back_parts = [p for p in (decisions, outcome) if p]
    return _make_note(
        front=subject,
        back="\n\n".join(back_parts),
        type_name="session",
        source=doc.source_path,
    )


_NOTE_BUILDERS = {
    "concept": _build_note_for_concept,
    "method": _build_note_for_method,
    "wiki": _build_note_for_wiki,
    "session": _build_note_for_session,
    "session_summary": _build_note_for_session,
}


def build_anki_notes(scope: Path) -> list[AnkiNote]:
    """Walk ``scope`` and turn every doc with a known type into an AnkiNote.

    Unknown ``type:`` values are skipped (with a stderr warning).
    """
    notes: list[AnkiNote] = []
    for doc in collect_markdown(scope):
        type_name = str(doc.frontmatter.get("type") or "").lower()
        builder = _NOTE_BUILDERS.get(type_name)
        if builder is None:
            print(
                f"[export] skipping {doc.source_path}: unknown type {type_name!r}",
                file=sys.stderr,
            )
            continue
        notes.append(builder(doc))
    return notes


def export_anki(scope: Path, out_path: Path, *, deck_name: str) -> int:
    """Build an ``.apkg`` package from every recognised doc under ``scope``."""
    notes = build_anki_notes(scope)
    if not notes:
        print("[export] empty scope: no recognisable docs for Anki", file=sys.stderr)
        return 1

    try:
        import genanki
    except ModuleNotFoundError:
        print(
            "[export] genanki not installed; run `uv sync --extra export` "
            "(see references/tools-spec.md §6.9)",
            file=sys.stderr,
        )
        return 1

    model = genanki.Model(
        _DEFAULT_ANKI_MODEL_ID,
        "Life OS Basic",
        fields=[{"name": "Front"}, {"name": "Back"}],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Front}}",
                "afmt": "{{FrontSide}}<hr id=answer>{{Back}}",
            }
        ],
    )
    deck = genanki.Deck(_DEFAULT_ANKI_DECK_ID, deck_name)
    for note in notes:
        deck.add_note(
            genanki.Note(
                model=model,
                fields=[note.front, note.back],
                guid=genanki.guid_for(note.guid),
            )
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    genanki.Package(deck).write_to_file(str(out_path))
    return 0


# ─── Dispatcher ─────────────────────────────────────────────────────────────


def run(
    *,
    fmt: str,
    scope: Path,
    output_dir: Path,
    today: date | None = None,
) -> int:
    """High-level dispatcher used by both the CLI and programmatic callers."""
    if fmt not in _SUPPORTED_FORMATS:
        print(
            f"[export] unknown format {fmt!r}; pick one of "
            f"{sorted(_SUPPORTED_FORMATS)}",
            file=sys.stderr,
        )
        return 1
    if not scope.exists():
        print(f"[export] scope not found: {scope}", file=sys.stderr)
        return 1
    if not scope.is_dir():
        print(f"[export] scope must be a directory: {scope}", file=sys.stderr)
        return 1

    out_path = output_dir / output_filename(scope, fmt, today=today)
    if fmt == "json":
        return export_json(scope, out_path)
    if fmt == "html":
        return export_html(scope, out_path)
    if fmt == "pdf":
        return export_pdf(scope, out_path)
    if fmt == "anki":
        return export_anki(scope, out_path, deck_name=slug_from_scope(scope))
    return 1  # pragma: no cover — unreachable


# ─── CLI ────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export second-brain markdown to pdf / html / json / anki.",
    )
    parser.add_argument(
        "--format",
        required=True,
        choices=sorted(_SUPPORTED_FORMATS),
        help="Output format.",
    )
    parser.add_argument(
        "--scope",
        required=True,
        type=Path,
        help="Directory whose *.md files will be exported.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("exports"),
        help="Destination directory (default: ./exports).",
    )
    args = parser.parse_args(argv)

    return run(
        fmt=args.format,
        scope=args.scope,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    sys.exit(main())
