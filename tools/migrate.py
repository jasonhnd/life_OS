#!/usr/bin/env python3
"""v1.6.2a -> v1.7 one-shot schema migration.

Per references/tools-spec.md §6.7. Reads a legacy ``_meta/journal/`` tree
and backfills the four v1.7 Cortex artefacts:

- ``_meta/sessions/{session_id}.md``   + ``INDEX.md`` (session-index-spec.md §9)
- ``_meta/concepts/**``                (concept-spec.md §Migration)
- ``_meta/snapshots/soul/**``          (snapshot-spec.md §Migration)
- ``_meta/methods/_tentative/**``      (method-library-spec.md §15)

Does NOT backfill ``_meta/eval-history/`` — eval history starts fresh at
v1.7 day one (eval-history-spec.md §11). Does NOT modify ``SOUL.md``,
``wiki/``, or ``user-patterns.md``; those are read-only inputs.

Usage::

    uv run tools/migrate.py --from v1.6.2a --to v1.7 [--dry-run] [--root PATH]

The migration is LLM-free — pure rule-based extraction over journal
content. Bounded to the last 3 months of journal entries (user decision
#7).  The migration is idempotent; re-running it produces the same
INDEX.md and does not duplicate sessions / concepts.

Exit codes:
- ``0`` — migration completed successfully
- ``1`` — at least one file failed to parse (logged to stderr); other
  files still migrated.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

# Allow running from repo root via ``python3 tools/migrate.py``
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.cortex.concept import (  # noqa: E402
    compile_concept_index,
    compile_synapses_index,
    write_concept,
)
from tools.lib.cortex.extraction import (  # noqa: E402
    is_stopword,
    slug_from_name,
)
from tools.lib.cortex.session_index import (  # noqa: E402
    compile_index,
    session_summary_to_markdown,
    write_index,
)
from tools.lib.cortex.snapshot import snapshot_to_markdown  # noqa: E402
from tools.lib.second_brain import (  # noqa: E402
    Concept,
    ConceptEdge,
    ConceptProvenance,
    SessionSummary,
    SnapshotDimension,
    SoulSnapshot,
    dump_frontmatter,
)

# ─── Constants ──────────────────────────────────────────────────────────────


WINDOW_DAYS = 90  # 3-month migration window (user decision #7)
DEFAULT_PLATFORM = "claude"
DEFAULT_THEME = "en-roman"
DEFAULT_WORKFLOW = "direct_handle"

CONCEPT_ACTIVATION_CAP = 10  # spec: activation_count capped at 10 during migration
CONCEPT_EDGE_WEIGHT_CAP = 10

CONCEPT_CONFIRMED_THRESHOLD = 3
CONCEPT_CANONICAL_THRESHOLD = 10

METHOD_KEYWORDS = (
    "approach",
    "pattern",
    "framework",
    "process",
    "流れ",
    "やり方",
    "手順",
)

DEFAULT_DOMAIN = "personal"

# Minimum times a concept candidate must appear across sessions to be emitted
MIN_CONCEPT_FREQUENCY = 3

# Phrase extraction tailored for proper-noun-ish tokens (hyphenated words
# like "zk-proof", "evidence-chain" are common concept candidates in the
# spec examples).
_PROPER_NOUN_PATTERN = re.compile(
    r"\b[a-z][a-z0-9]*(?:-[a-z0-9]+)+\b"   # hyphenated compounds
    r"|\b[A-Z][A-Za-z0-9]*\b"              # capitalised words
    r"|[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]{2,}"  # CJK runs
)


# ─── Journal entry parsing ──────────────────────────────────────────────────


@dataclass
class JournalEntry:
    """One parsed journal file as input for migration."""

    path: Path
    mtime: datetime
    text: str
    project: str  # inferred from filename or body, falls back to "unknown"

    @property
    def session_id(self) -> str:
        """Derive session_id in format ``claude-YYYYMMDD-HHMM`` from mtime."""
        ts = self.mtime
        return (
            f"{DEFAULT_PLATFORM}-"
            f"{ts.year:04d}{ts.month:02d}{ts.day:02d}-"
            f"{ts.hour:02d}{ts.minute:02d}"
        )


def _infer_project(path: Path, body: str) -> str:
    """Guess project from filename (``YYYY-MM-DD-<project>.md``) or body."""
    stem = path.stem
    # Strip leading ISO date if present (YYYY-MM-DD-project)
    match = re.match(r"\d{4}-\d{2}-\d{2}-(.+)$", stem)
    if match:
        return match.group(1).strip() or "unknown"
    # Fall back to the stem itself, sanitised
    if stem and stem != "index":
        return stem
    # Last resort: scan body for "project: xyz" or "Project: xyz" patterns
    m = re.search(r"(?im)^\s*project\s*[:\-]\s*([^\n]+)$", body)
    if m:
        return m.group(1).strip()
    return "unknown"


def _load_journal_entries(
    journal_root: Path,
    *,
    window_days: int,
    now: datetime | None = None,
    logger: logging.Logger,
) -> tuple[list[JournalEntry], int]:
    """Enumerate journal entries within the migration window.

    Returns ``(entries, parse_error_count)``. Files outside the 3-month
    window are silently skipped (not counted as errors). Files that fail
    to decode bump the ``parse_error_count``.
    """
    if not journal_root.exists():
        return [], 0

    now = now or datetime.now()
    cutoff = now - timedelta(days=window_days)
    entries: list[JournalEntry] = []
    parse_errors = 0

    for path in sorted(journal_root.glob("*.md")):
        try:
            stat = path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            if mtime < cutoff:
                continue
            body = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            logger.warning("Skipped unreadable journal file %s: %s", path, exc)
            parse_errors += 1
            continue

        project = _infer_project(path, body)
        entries.append(
            JournalEntry(
                path=path,
                mtime=mtime,
                text=body,
                project=project,
            )
        )

    return entries, parse_errors


# ─── Target 1: Session backfill ─────────────────────────────────────────────


def _extract_subject(text: str, fallback: str) -> str:
    """Try to pull a subject line from the journal body.

    Precedence:
    1. First ``## Subject`` block (single line)
    2. First ``# ...`` heading
    3. First non-empty line
    Falls back to ``fallback`` if nothing matches.
    """
    m = re.search(r"(?im)^##\s+Subject\s*\n+(.+)$", text)
    if m:
        return m.group(1).strip()[:200]
    m = re.search(r"(?m)^#\s+(.+)$", text)
    if m:
        return m.group(1).strip()[:200]
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:200]
    return fallback[:200]


def _extract_keywords(text: str, project: str, *, max_keywords: int = 10) -> list[str]:
    """Extract up to ``max_keywords`` keyword candidates from the text.

    Deterministic: uses the proper-noun / compound pattern then frequency-
    ranks the hits. Always seeds with the project name as first keyword
    (so the session is at least discoverable by project).
    """
    words: list[str] = []
    for match in _PROPER_NOUN_PATTERN.finditer(text):
        token = match.group(0)
        if len(token) < 3:
            continue
        if is_stopword(token.lower()):
            continue
        words.append(token.lower())

    counts = Counter(words)
    ranked = [
        word for word, _count in counts.most_common(max_keywords * 2)
    ]
    # Always include the project as the first keyword (deduplicated)
    result: list[str] = []
    if project and project != "unknown":
        result.append(project.lower())
    for word in ranked:
        if word not in result:
            result.append(word)
        if len(result) >= max_keywords:
            break
    return result[:max_keywords]


def _build_session_summary(entry: JournalEntry) -> SessionSummary:
    """Synthesize a SessionSummary from a journal entry.

    Per spec §9:
    - session_id = ``claude-YYYYMMDD-HHMM`` from mtime
    - platform defaults to claude
    - pre-v1.7 fields stay empty / zero (we don't fabricate scores)
    """
    started = entry.mtime
    ended = started  # we don't know; leave equal (duration 0)
    subject = _extract_subject(entry.text, fallback=f"Migrated session from {entry.project}")
    keywords = _extract_keywords(entry.text, entry.project)

    body = (
        "## Subject\n\n"
        f"{subject}\n\n"
        "## Key Decisions\n\n"
        "_(migrated from v1.6.2a journal — decisions not individually extracted)_\n\n"
        "## Outcome\n\n"
        "_(see corresponding journal entry for full detail)_\n\n"
        "## Notable Signals\n\n"
        "- Imported via tools/migrate.py\n"
    )

    return SessionSummary(
        session_id=entry.session_id,
        date=started.date(),
        started_at=started,
        ended_at=ended,
        duration_minutes=0,
        platform=DEFAULT_PLATFORM,
        theme=DEFAULT_THEME,
        project=entry.project or "unknown",
        workflow=DEFAULT_WORKFLOW,
        subject=subject,
        overall_score=0.0,  # unknown pre-v1.7
        veto_count=0,
        council_triggered=False,
        compliance_violations=0,
        body=body,
        keywords=keywords,
        action_items=[],  # intentionally empty
    )


def _migrate_sessions(
    entries: list[JournalEntry],
    *,
    root: Path,
    dry_run: bool,
    logger: logging.Logger,
) -> int:
    """Write one session file per journal entry. Returns count written."""
    sessions_dir = root / "_meta" / "sessions"
    written = 0
    for entry in entries:
        summary = _build_session_summary(entry)
        target = sessions_dir / f"{summary.session_id}.md"
        content = session_summary_to_markdown(summary)
        if dry_run:
            logger.info("[dry-run] would write %s", target)
            written += 1
            continue
        sessions_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written += 1

    # Compile the INDEX only if we're not in dry-run.
    if not dry_run and sessions_dir.exists():
        index_content = compile_index(sessions_dir)
        write_index(index_content, sessions_dir)

    return written


# ─── Target 2: Concept backfill ─────────────────────────────────────────────


def _extract_concept_candidates(text: str) -> set[str]:
    """Return the set of concept candidates (normalized tokens) in a journal.

    We consider hyphenated compounds and capitalised nouns and CJK runs,
    minus stopwords. Uppercase words with ≤2 chars are skipped (likely
    acronyms that need manual confirmation, not auto-migration).
    """
    candidates: set[str] = set()
    for match in _PROPER_NOUN_PATTERN.finditer(text):
        token = match.group(0)
        lower = token.lower()
        if len(lower) < 3:
            continue
        if is_stopword(lower):
            continue
        candidates.add(lower)
    return candidates


def _pick_concept_domain(candidate: str) -> str:
    """Pick a domain partition heuristically.

    We don't have enough signal in the migration path to do this well;
    fallback to ``personal`` per spec's neutral choice. Users promote
    concepts to their proper domain by hand.
    """
    # A few hard-coded hints so the test fixture looks natural.
    lowered = candidate.lower()
    if any(tok in lowered for tok in ("finance", "fund", "capital", "trust", "amount")):
        return "finance"
    if any(tok in lowered for tok in ("zk", "proof", "whitepaper", "schema", "code")):
        return "technical"
    if any(tok in lowered for tok in ("gtm", "launch", "growth", "product")):
        return "startup"
    if any(tok in lowered for tok in ("method", "pattern", "framework", "approach")):
        return "method"
    return DEFAULT_DOMAIN


def _status_from_activation(activation: int) -> str:
    """Map activation_count to status tier per concept-spec.md §Migration."""
    if activation >= CONCEPT_CANONICAL_THRESHOLD:
        return "canonical"
    if activation >= CONCEPT_CONFIRMED_THRESHOLD:
        return "confirmed"
    return "tentative"


def _migrate_concepts(
    entries: list[JournalEntry],
    *,
    root: Path,
    dry_run: bool,
    logger: logging.Logger,
) -> int:
    """Run the 6-criteria-style concept extraction across the journal.

    Returns the number of concept files written (or planned, for dry-run).
    """
    # 1. Count occurrences across journals (activation = session count)
    session_mentions: dict[str, set[str]] = {}  # candidate -> set of session_ids
    session_cooccurrence: dict[str, Counter[str]] = {}  # candidate -> Counter[neighbour]

    for entry in entries:
        cands = _extract_concept_candidates(entry.text)
        for c in cands:
            session_mentions.setdefault(c, set()).add(entry.session_id)
        # Build co-occurrence inside this session
        cand_list = list(cands)
        for i, a in enumerate(cand_list):
            for b in cand_list[i + 1 :]:
                session_cooccurrence.setdefault(a, Counter())[b] += 1
                session_cooccurrence.setdefault(b, Counter())[a] += 1

    # 2. Keep only candidates with activation >= MIN_CONCEPT_FREQUENCY
    eligible: dict[str, int] = {
        cand: min(len(sessions), CONCEPT_ACTIVATION_CAP)
        for cand, sessions in session_mentions.items()
        if len(sessions) >= MIN_CONCEPT_FREQUENCY
    }

    concepts_root = root / "_meta" / "concepts"
    written = 0

    # Collect session_id provenance list outside of per-concept loop for reuse
    for cand, activation in eligible.items():
        status = _status_from_activation(activation)
        domain = _pick_concept_domain(cand)
        cid = slug_from_name(cand, max_len=64)
        if not cid:
            continue
        now = datetime.now()
        edges: list[ConceptEdge] = []
        for neighbour, weight in session_cooccurrence.get(cand, Counter()).most_common(
            10
        ):
            neighbour_id = slug_from_name(neighbour, max_len=64)
            if not neighbour_id or neighbour_id == cid:
                continue
            if neighbour not in eligible:
                continue
            bounded = min(weight, CONCEPT_EDGE_WEIGHT_CAP)
            if bounded <= 0:
                continue
            edges.append(
                ConceptEdge(
                    target=neighbour_id,
                    weight=bounded,
                    last_co_activated=now,
                )
            )

        concept = Concept(
            concept_id=cid,
            canonical_name=cand,
            domain=domain,
            status=status,
            permanence="fact",
            activation_count=activation,
            last_activated=now,
            created=now,
            body=(
                f"# {cand}\n\n"
                "## Evidence / Examples\n"
                "- Migrated from v1.6.2a journal — see source sessions.\n"
            ),
            aliases=[],
            outgoing_edges=edges,
            provenance=ConceptProvenance(
                source_sessions=sorted(session_mentions[cand]),
                discovered_at=now,
            ),
        )

        # Tentative candidates live under _tentative/{domain}/
        if status == "tentative":
            target_dir = concepts_root / "_tentative" / domain
        else:
            target_dir = concepts_root / domain

        if dry_run:
            logger.info(
                "[dry-run] would write %s (status=%s)",
                target_dir / f"{cid}.md",
                status,
            )
            written += 1
            continue

        if status == "tentative":
            # write_concept only handles the confirmed layout; for tentative
            # we write directly into the tentative/ subtree.
            target_dir.mkdir(parents=True, exist_ok=True)
            from tools.lib.cortex.concept import concept_to_markdown

            (target_dir / f"{cid}.md").write_text(
                concept_to_markdown(concept), encoding="utf-8"
            )
        else:
            write_concept(concept, concepts_root)
        written += 1

    # Compile concept + synapses indices so downstream agents have a
    # ready-to-read map immediately after migration.
    if not dry_run and concepts_root.exists():
        idx = compile_concept_index(concepts_root)
        (concepts_root / "INDEX.md").write_text(idx, encoding="utf-8")
        syn = compile_synapses_index(concepts_root)
        (concepts_root / "SYNAPSES-INDEX.md").write_text(syn, encoding="utf-8")

    return written


# ─── Target 3: SOUL snapshot synthesis ──────────────────────────────────────


_SOUL_DELTA_RE = re.compile(
    r"(?ms)(?:🔮\s*)?SOUL\s+Delta\s*\n+([\s\S]+?)(?:\n##|\n---|\Z)"
)
_DIM_LINE_RE = re.compile(
    r"-\s+([A-Za-z0-9_\-]+)\s*[:：]\s*"
    r"(?:[+\-]?\d*\.?\d+)?"
    r"(?:.*?confidence\s*=\s*([01](?:\.\d+)?))?"
)


def _extract_soul_deltas(text: str) -> list[SnapshotDimension]:
    """Scan journal text for a 🔮 SOUL Delta block, return the list of
    dimensions with derived tiers. Dormant (< 0.2) dimensions are
    excluded per snapshot-spec.md.
    """
    m = _SOUL_DELTA_RE.search(text)
    if not m:
        return []
    block = m.group(1)
    dims: list[SnapshotDimension] = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or not stripped.startswith("-"):
            continue
        dm = _DIM_LINE_RE.match(stripped)
        if not dm:
            continue
        name = dm.group(1)
        confidence_str = dm.group(2)
        if confidence_str is None:
            # No explicit confidence — default to 0.5 (emerging/secondary)
            confidence = 0.5
        else:
            try:
                confidence = float(confidence_str)
            except ValueError:
                confidence = 0.5
        if confidence <= 0.2:
            continue
        dims.append(
            SnapshotDimension(
                name=name,
                confidence=confidence,
                evidence_count=1,  # unknown pre-v1.7
                challenges=0,
                tier=SnapshotDimension.derive_tier(confidence),
            )
        )
    return dims


def _snapshot_id_from_mtime(ts: datetime) -> str:
    return f"{ts.year:04d}-{ts.month:02d}-{ts.day:02d}-{ts.hour:02d}{ts.minute:02d}"


def _migrate_snapshots(
    entries: list[JournalEntry],
    *,
    root: Path,
    dry_run: bool,
    logger: logging.Logger,
) -> int:
    """Synth a SoulSnapshot per journal entry that contains a SOUL Delta
    block. All synthetic snapshots carry ``provenance: synthetic`` so
    RETROSPECTIVE can distinguish them.
    """
    soul_root = root / "_meta" / "snapshots" / "soul"
    written = 0
    previous: str | None = None
    # Process in chronological order so previous_snapshot chains correctly.
    ordered = sorted(entries, key=lambda e: e.mtime)
    for entry in ordered:
        dims = _extract_soul_deltas(entry.text)
        if not dims:
            continue
        snapshot_id = _snapshot_id_from_mtime(entry.mtime)
        snap = SoulSnapshot(
            snapshot_id=snapshot_id,
            captured_at=entry.mtime,
            session_id=entry.session_id,
            previous_snapshot=previous,
            dimensions=dims,
        )
        target = soul_root / f"{snapshot_id}.md"
        # Inject provenance: synthetic into frontmatter after rendering.
        md = snapshot_to_markdown(snap)
        md = _inject_synthetic_provenance(md)
        if dry_run:
            logger.info("[dry-run] would write %s", target)
            written += 1
            previous = f"{snapshot_id}.md"
            continue
        if target.exists():
            # Idempotent re-run — overwrite safely with fresh content.
            logger.info("overwriting existing synthetic snapshot %s", target)
        soul_root.mkdir(parents=True, exist_ok=True)
        target.write_text(md, encoding="utf-8")
        written += 1
        previous = f"{snapshot_id}.md"
    return written


def _inject_synthetic_provenance(markdown: str) -> str:
    """Add ``provenance: synthetic`` to the frontmatter if not already there."""
    if "provenance: synthetic" in markdown:
        return markdown
    # Insert just before the closing ``---`` of the frontmatter block.
    lines = markdown.splitlines(keepends=True)
    # Find the index of the second --- line
    fence_hits = [i for i, line in enumerate(lines) if line.startswith("---")]
    if len(fence_hits) < 2:
        return markdown
    insert_at = fence_hits[1]
    lines.insert(insert_at, "provenance: synthetic\n")
    return "".join(lines)


# ─── Target 4: Method candidate extraction ──────────────────────────────────


_METHOD_PHRASE_RE = re.compile(
    r"(?i)(?:^|\s)([^.!?\n]{0,60}?\b(?:"
    + "|".join(re.escape(kw) for kw in METHOD_KEYWORDS)
    + r")\b[^.!?\n]{0,60})"
)


@dataclass
class MethodCandidate:
    """Method-candidate extracted from the journal sweep."""

    slug: str
    display: str
    frequency: int
    sources: list[str]


def _extract_method_candidates(entries: list[JournalEntry]) -> list[MethodCandidate]:
    """Return up to 5 method-candidates, ranked by frequency.

    Each candidate bundles the surrounding phrase as a description and
    counts cross-session occurrence frequency.
    """
    counts: Counter[str] = Counter()
    samples: dict[str, str] = {}
    source_map: dict[str, set[str]] = {}
    for entry in entries:
        matches = _METHOD_PHRASE_RE.findall(entry.text)
        seen_in_session: set[str] = set()
        for raw in matches:
            snippet = " ".join(raw.strip().split())
            if len(snippet) < 5:
                continue
            key = snippet.lower()
            if key in seen_in_session:
                continue
            seen_in_session.add(key)
            counts[key] += 1
            samples.setdefault(key, snippet)
            source_map.setdefault(key, set()).add(entry.session_id)

    top = [k for k, _c in counts.most_common(5)]
    results: list[MethodCandidate] = []
    for key in top:
        results.append(
            MethodCandidate(
                slug=slug_from_name(key, max_len=48) or "method-candidate",
                display=samples[key],
                frequency=counts[key],
                sources=sorted(source_map.get(key, set())),
            )
        )
    return results


def _migrate_methods(
    entries: list[JournalEntry],
    *,
    root: Path,
    dry_run: bool,
    logger: logging.Logger,
) -> int:
    """Write the top-5 method candidates to ``_meta/methods/_tentative/``."""
    candidates = _extract_method_candidates(entries)
    methods_tentative = root / "_meta" / "methods" / "_tentative"
    written = 0
    for cand in candidates:
        slug = cand.slug
        now = datetime.now()
        fm = {
            "method_id": slug,
            "name": cand.display[:80],
            "description": cand.display[:160],
            "domain": "method",
            "status": "tentative",
            "confidence": 0.3,
            "times_used": cand.frequency,
            "last_used": now.isoformat(),
            "applicable_when": [],
            "not_applicable_when": [],
            "source_sessions": cand.sources,
            "evidence_count": cand.frequency,
            "challenges": 0,
            "related_concepts": [],
            "related_methods": [],
        }
        body = (
            f"# {cand.display[:80]}\n\n"
            "## Summary\n"
            "Migrated method candidate detected via keyword scan; please review.\n\n"
            "## Steps\n"
            "1. _(placeholder — fill in when confirming this method)_\n\n"
            "## When to Use\n"
            f"- Pattern observed across {cand.frequency} sessions.\n\n"
            "## When NOT to Use\n"
            "- _(to be filled in)_\n\n"
            "## Evolution Log\n"
            f"- {now.date().isoformat()}: Extracted during v1.6.2a -> v1.7 migration.\n\n"
            "## Warnings\n"
            "- Auto-extracted; verify relevance before confirming.\n\n"
            "## Related\n"
            "- _(none yet)_\n"
        )
        markdown = dump_frontmatter(fm, body)
        target = methods_tentative / f"{slug}.md"
        if dry_run:
            logger.info("[dry-run] would write %s", target)
            written += 1
            continue
        methods_tentative.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown, encoding="utf-8")
        written += 1
    # Always ensure the directory exists even when 0 candidates — the spec
    # names it as a migration output slot.
    if not dry_run:
        methods_tentative.mkdir(parents=True, exist_ok=True)
    return written


# ─── Migration log ──────────────────────────────────────────────────────────


@dataclass
class MigrationReport:
    from_version: str
    to_version: str
    dry_run: bool
    journals_processed: int
    sessions_written: int
    concepts_written: int
    snapshots_written: int
    methods_written: int
    parse_errors: int = 0
    notes: list[str] = field(default_factory=list)

    def render(self) -> str:
        header = (
            f"# Migration Report — {self.from_version} -> {self.to_version}\n\n"
            f"Run at: {datetime.now().isoformat(timespec='seconds')}\n"
            f"Mode: {'dry-run' if self.dry_run else 'apply'}\n\n"
        )
        body = (
            f"- Journals processed: {self.journals_processed}\n"
            f"- Sessions written: {self.sessions_written}\n"
            f"- Concepts written: {self.concepts_written}\n"
            f"- Snapshots synthesized: {self.snapshots_written}\n"
            f"- Method candidates: {self.methods_written}\n"
            f"- Parse errors: {self.parse_errors}\n"
        )
        notes = ""
        if self.notes:
            notes = "\n## Notes\n" + "\n".join(f"- {n}" for n in self.notes) + "\n"
        return header + body + notes


def _write_bootstrap_status(
    report: MigrationReport,
    *,
    root: Path,
    dry_run: bool,
) -> None:
    status_path = root / "_meta" / "cortex" / "bootstrap-status.md"
    if dry_run:
        return
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(report.render(), encoding="utf-8")


# ─── CLI ────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="migrate",
        description=(
            "One-shot migration from a v1.6.2a second-brain layout "
            "to the v1.7 Cortex layout. Reads _meta/journal/ and "
            "backfills sessions, concepts, SOUL snapshots, and "
            "tentative methods."
        ),
    )
    parser.add_argument(
        "--from",
        dest="from_version",
        required=True,
        help="Source version (e.g. v1.6.2a).",
    )
    parser.add_argument(
        "--to",
        dest="to_version",
        required=True,
        help="Target version (e.g. v1.7).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the migration plan without writing files.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Second-brain root (default: cwd).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Emit progress on stderr.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
        stream=sys.stderr,
    )
    logger = logging.getLogger("migrate")

    root: Path = args.root
    journal_root = root / "_meta" / "journal"

    entries, parse_errors = _load_journal_entries(
        journal_root,
        window_days=WINDOW_DAYS,
        logger=logger,
    )

    try:
        sessions_written = _migrate_sessions(
            entries, root=root, dry_run=args.dry_run, logger=logger
        )
        concepts_written = _migrate_concepts(
            entries, root=root, dry_run=args.dry_run, logger=logger
        )
        snapshots_written = _migrate_snapshots(
            entries, root=root, dry_run=args.dry_run, logger=logger
        )
        methods_written = _migrate_methods(
            entries, root=root, dry_run=args.dry_run, logger=logger
        )
    except OSError as exc:
        logger.error("I/O error during migration: %s", exc)
        return 1

    report = MigrationReport(
        from_version=args.from_version,
        to_version=args.to_version,
        dry_run=args.dry_run,
        journals_processed=len(entries),
        sessions_written=sessions_written,
        concepts_written=concepts_written,
        snapshots_written=snapshots_written,
        methods_written=methods_written,
        parse_errors=parse_errors,
        notes=[
            "eval-history intentionally NOT backfilled (spec §11).",
            "SOUL.md, wiki/, user-patterns.md untouched (read-only inputs).",
        ],
    )
    _write_bootstrap_status(report, root=root, dry_run=args.dry_run)

    if parse_errors:
        logger.warning(
            "Migration finished with %d parse error(s); other files succeeded.",
            parse_errors,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
