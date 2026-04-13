#!/bin/bash
# Life OS Version Check — runs at Claude Code SessionStart
# Checks once per day, compares local vs remote SKILL.md version
# Output is shown to the LLM at session start

set -euo pipefail

SKILL_PATH="$HOME/.claude/skills/life_OS/SKILL.md"
CACHE_DIR="/tmp/lifeos"
CACHE_FILE="$CACHE_DIR/version-check-$(date +%Y%m%d)"

# Only check once per day
if [ -f "$CACHE_FILE" ]; then
  cat "$CACHE_FILE"
  exit 0
fi

mkdir -p "$CACHE_DIR"

# Get local version
if [ ! -f "$SKILL_PATH" ]; then
  echo "[Life OS] Skill not found at $SKILL_PATH"
  exit 0
fi

LOCAL=$(head -5 "$SKILL_PATH" | grep '^version:' | sed 's/.*"\(.*\)".*/\1/')
if [ -z "$LOCAL" ]; then
  echo "[Life OS] Could not read local version"
  exit 0
fi

# Get remote version (3 second timeout, fail silently)
REMOTE=$(curl -sf --max-time 3 "https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md" 2>/dev/null | head -5 | grep '^version:' | sed 's/.*"\(.*\)".*/\1/' || echo "")

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
