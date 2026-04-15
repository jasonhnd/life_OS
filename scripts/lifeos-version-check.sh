#!/bin/bash
# Life OS Version Check — runs at Claude Code SessionStart
# Checks once per day, compares local vs remote SKILL.md version
# Output is shown to the LLM at session start

set -euo pipefail

SKILL_PATH="$HOME/.claude/skills/life_OS/SKILL.md"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/lifeos"
CACHE_FILE="$CACHE_DIR/version-check-$(date +%Y%m%d)"

# Only check once per day
if [ -f "$CACHE_FILE" ]; then
  cat "$CACHE_FILE"
  exit 0
fi

mkdir -p "$CACHE_DIR"
chmod 700 "$CACHE_DIR"

# Get local version (scan full frontmatter, not just first N lines)
if [ ! -f "$SKILL_PATH" ]; then
  echo "[Life OS] Skill not found at $SKILL_PATH"
  exit 0
fi

LOCAL=$(grep -m1 '^version:' "$SKILL_PATH" | sed 's/.*"\(.*\)".*/\1/')
if [ -z "$LOCAL" ]; then
  echo "[Life OS] Could not read local version"
  exit 0
fi

# Get remote version (3 second timeout, fail silently)
REMOTE=$(curl -sf --max-time 3 "https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md" 2>/dev/null | grep -m1 '^version:' | sed 's/.*"\(.*\)".*/\1/' || echo "")

if [ -z "$REMOTE" ]; then
  RESULT="[Life OS] v${LOCAL} (version check skipped — network unavailable)"
  echo "$RESULT" > "$CACHE_FILE"
  echo "$RESULT"
  exit 0
fi

if [ "$LOCAL" = "$REMOTE" ]; then
  RESULT="[Life OS] v${LOCAL} ✅ (latest)"
  echo "$RESULT" > "$CACHE_FILE"
  echo "$RESULT"
else
  RESULT="[Life OS] ⬆️ Update available: v${LOCAL} → v${REMOTE}
Run: /install-skill https://github.com/jasonhnd/life_OS"
  echo "$RESULT" > "$CACHE_FILE"
  echo "$RESULT"
fi
