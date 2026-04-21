#!/usr/bin/env python3
"""Concept candidate extraction CLI.

Reads text (from file or stdin), counts noun-phrase candidates, applies
the >=2 mention frequency filter, and prints the candidates with their
proposed slug forms.

Used by archiver Phase 2 Step A as a deterministic helper before the
LLM judgment step (categorisation, identity check, person/value filter).

Usage:
    uv run tools/extract.py [--input FILE] [--min-count N] [--top N] [--json]
    cat session.md | python3 tools/extract.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.cortex.extraction import (  # noqa: E402
    count_candidate_frequencies,
    filter_by_min_frequency,
    slug_from_name,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract concept candidates from text (frequency + slug)."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input file (default: read from stdin)",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=2,
        help="Minimum mention count (default: 2 per archiver Phase 2 Step A.1)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Show top N candidates (default: 20)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable text",
    )
    args = parser.parse_args()

    if args.input:
        if not args.input.exists():
            print(f"❌ Input file not found: {args.input}", file=sys.stderr)
            return 2
        text = args.input.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("❌ No input text provided", file=sys.stderr)
        return 2

    counts = count_candidate_frequencies(text)
    filtered = filter_by_min_frequency(counts, min_count=args.min_count)
    top_candidates = filtered.most_common(args.top)

    if args.json:
        result = {
            "total_unique_candidates": len(counts),
            "after_frequency_filter": len(filtered),
            "min_count": args.min_count,
            "top_n": args.top,
            "candidates": [
                {
                    "phrase": phrase,
                    "count": count,
                    "slug": slug_from_name(phrase),
                }
                for phrase, count in top_candidates
            ],
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"📊 Concept candidate extraction")
        print(f"   Total unique candidates: {len(counts)}")
        print(f"   After ≥{args.min_count}-mention filter: {len(filtered)}")
        print(f"   Top {args.top}:")
        print()
        if not top_candidates:
            print("   (no candidates met the frequency threshold)")
        else:
            for phrase, count in top_candidates:
                print(f"   {count:3d}×  {phrase}")
                print(f"        → slug: {slug_from_name(phrase)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
