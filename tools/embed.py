#!/usr/bin/env python3
"""embed.py — not implemented. Semantic embeddings are out of scope for v1.7
(user decision #3: markdown-first, LLM-judgment-only).

For retrieval inside a session: use the hippocampus subagent
(references/hippocampus-spec.md).
For batch search: use search.py (metadata + grep ranking).

Invoking this tool prints this notice and exits 0.
"""

from __future__ import annotations

import sys

_NOTICE = (
    "embed.py -- not implemented. Semantic embeddings are out of scope "
    "for v1.7 (user decision #3: markdown-first, LLM-judgment-only).\n"
    "\n"
    "For retrieval inside a session: use the hippocampus subagent "
    "(references/hippocampus-spec.md).\n"
    "For batch search: use search.py (metadata + grep ranking).\n"
)


def main(argv: list[str] | None = None) -> int:
    """Print the unimplemented notice and exit 0.

    ``argv`` is accepted but ignored; the tool has no flags. Default-None
    signature matches the other v1.7 tools so ``tools/cli.py`` can dispatch
    uniformly.
    """
    del argv  # explicitly unused
    print(_NOTICE)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
