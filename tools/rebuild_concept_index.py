#!/usr/bin/env python3
"""Rebuild ``_meta/concepts/INDEX.md`` and ``SYNAPSES-INDEX.md`` from concept files.

Use cases:
- Fallback when retrospective Mode 0's INDEX compilation step is unavailable
- Manual recompile after editing concept frontmatter
- Recovery after corruption of INDEX.md or SYNAPSES-INDEX.md

Usage:
    uv run tools/rebuild_concept_index.py [--root PATH] [--dry-run] [--no-synapses]
    python3 tools/rebuild_concept_index.py [--root PATH] [--dry-run] [--no-synapses]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lib.cortex.concept import (  # noqa: E402
    compile_concept_index,
    compile_synapses_index,
    rebuild_concept_index,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recompile _meta/concepts/INDEX.md (and SYNAPSES-INDEX.md) from concept files. "
            "Idempotent — safe to run repeatedly."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Path to second-brain root (default: cwd)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print preview, do not modify files",
    )
    parser.add_argument(
        "--no-synapses",
        action="store_true",
        help="Skip SYNAPSES-INDEX.md compilation (only INDEX.md)",
    )
    args = parser.parse_args()

    concepts_root = args.root / "_meta" / "concepts"
    if not concepts_root.exists():
        print(f"❌ Concepts directory not found: {concepts_root}", file=sys.stderr)
        return 2

    if args.dry_run:
        idx_content = compile_concept_index(concepts_root)
        print("--- INDEX.md preview ---")
        print(idx_content)
        if not args.no_synapses:
            syn_content = compile_synapses_index(concepts_root)
            print("--- SYNAPSES-INDEX.md preview ---")
            print(syn_content)
        print("--- (dry-run, no files written) ---")
        return 0

    idx_target, idx_count = rebuild_concept_index(args.root)
    print(f"✅ Wrote {idx_target} ({idx_count} concepts indexed)")

    if not args.no_synapses:
        syn_content = compile_synapses_index(concepts_root)
        syn_target = concepts_root / "SYNAPSES-INDEX.md"
        syn_tmp = syn_target.with_suffix(".md.tmp")
        syn_tmp.write_text(syn_content, encoding="utf-8")
        syn_tmp.replace(syn_target)
        edge_count = sum(
            1
            for line in syn_content.splitlines()
            if "weight=" in line
        )
        print(f"✅ Wrote {syn_target} ({edge_count} synapse edges)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
