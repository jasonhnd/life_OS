#!/usr/bin/env bash
# Remove Life OS agent wrappers created for Claude Code native Task() discovery.

set -euo pipefail

AGENTS_DIR="$HOME/.claude/agents"
REMOVED=0

for f in "$AGENTS_DIR"/lifeos-*.md; do
  [ -f "$f" ] || continue
  rm -v "$f"
  REMOVED=$((REMOVED + 1))
done

echo "Removed $REMOVED lifeos-* wrappers"
