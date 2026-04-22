#!/usr/bin/env python3
"""Bootstrap a Cortex concept graph from an existing second-brain.

Scans wiki/ + decisions/ + journal/ files for candidate noun phrases,
applies frequency + stopword filtering, and prints proposed concept
files for the user to review before writing.

Use case: a user with ≥30 sessions of accumulated history wants to
enable Cortex but has an empty `_meta/concepts/` directory. Running
this tool surfaces likely concepts so they can:
1. Review the proposals
2. Manually create concept files (or accept all via --write flag)
3. Then enable cortex_enabled: true

Usage:
    uv run tools/seed_concepts.py [--root PATH] [--min-count N] [--top N] [--write]
    python3 tools/seed_concepts.py [--root PATH] [--min-count N] [--top N] [--write]

By default --dry-run (just prints proposals). --write actually creates
concept files at _meta/concepts/_tentative/{slug}.md (status=tentative
so they need explicit promotion).
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.cortex.concept import write_concept  # noqa: E402
from tools.lib.cortex.extraction import (  # noqa: E402
    count_candidate_frequencies,
    filter_by_min_frequency,
    slug_from_name,
)
from tools.lib.second_brain import Concept, ConceptProvenance  # noqa: E402

_SCAN_DIRS = [
    "wiki",
    "decisions",
    "_meta/decisions",
    "_meta/journal",
    "projects",  # walks recursively
]


def collect_text(second_brain_root: Path) -> str:
    """Concatenate text from all scannable files in the second-brain.

    Returns one big string (not per-file) — frequency counts span the
    whole corpus. Per-file context is lost but that's fine for bootstrap.
    """
    chunks: list[str] = []
    for rel_dir in _SCAN_DIRS:
        d = second_brain_root / rel_dir
        if not d.exists():
            continue
        for path in d.rglob("*.md"):
            try:
                chunks.append(path.read_text(encoding="utf-8"))
            except OSError:
                continue
    return "\n\n".join(chunks)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap concept candidates from existing second-brain content"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Path to second-brain root (default: cwd)",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=5,
        help="Minimum mention count (default: 5 — higher than archiver "
        "Phase 2 default 2 because we're scanning a larger corpus)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=30,
        help="Show top N candidates (default: 30)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually write concept files to _meta/concepts/_tentative/ "
        "(default: dry-run only)",
    )
    parser.add_argument(
        "--default-domain",
        default="personal",
        help="Default domain for new concepts (default: personal). "
        "User can re-categorise after.",
    )
    args = parser.parse_args()

    if not args.root.exists():
        print(f"❌ Root not found: {args.root}", file=sys.stderr)
        return 2

    print(f"🌱 Concept seeding · scanning {args.root}")
    text = collect_text(args.root)

    if not text.strip():
        print("   No content found — is this a Life OS second-brain?")
        print(f"   Expected at least one of: {_SCAN_DIRS}")
        return 0

    print(f"   Corpus: {len(text):,} chars")

    counts = count_candidate_frequencies(text)
    filtered = filter_by_min_frequency(counts, min_count=args.min_count)
    top_candidates = filtered.most_common(args.top)

    print(f"   Total unique candidates: {len(counts)}")
    print(f"   After ≥{args.min_count}-mention filter: {len(filtered)}")
    print(f"   Top {args.top}:")
    print()

    if not top_candidates:
        print("   (no candidates met threshold — try --min-count smaller)")
        return 0

    if args.write:
        concepts_root = args.root / "_meta" / "concepts" / "_tentative"
        now = datetime.now()
        written: list[Path] = []
        for phrase, count in top_candidates:
            slug = slug_from_name(phrase)
            concept = Concept(
                concept_id=slug,
                canonical_name=phrase,
                domain=args.default_domain,
                status="tentative",
                permanence="transient",
                activation_count=count,
                last_activated=now,
                created=now,
                body=(
                    f"## Definition\n\n"
                    f"_(seeded from existing second-brain content — review and "
                    f"flesh out before promoting from tentative to confirmed)_\n\n"
                    f"## Provenance\n\n"
                    f"- Initial mention count: {count}\n"
                    f"- Seeded by: tools/seed_concepts.py on "
                    f"{now.date().isoformat()}\n"
                ),
                provenance=ConceptProvenance(discovered_at=now),
            )
            path = write_concept(concept, concepts_root.parent)
            # write_concept puts it at concepts_root.parent/{domain}/{slug}.md
            # We actually want _tentative/, so move
            target = concepts_root / f"{slug}.md"
            concepts_root.mkdir(parents=True, exist_ok=True)
            path.rename(target)
            written.append(target)

        print(f"✅ Wrote {len(written)} tentative concepts to {concepts_root}/")
        print(f"   Review them, then move to {args.root}/_meta/concepts/{{domain}}/")
        print("   Run: life-os-tool rebuild-concept-index --root <root>")
        return 0

    # Dry-run preview
    for phrase, count in top_candidates:
        slug = slug_from_name(phrase)
        print(f"   {count:4d}×  {phrase}")
        print(f"         → slug: {slug}  → would write: _meta/concepts/_tentative/{slug}.md")

    print()
    print("Add --write to actually create concept files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
