#!/bin/bash
# Life OS Hook Setup — run ONCE after installing Life OS skill
# Adds two hooks to Claude Code:
#   1. SessionStart       → checks for skill updates daily
#                            (lifeos-version-check.sh)
#   2. UserPromptSubmit   → injects HARD RULE reminder on trigger words
#                            (lifeos-pre-prompt-guard.sh · v1.6.3 COURT-START-001
#                             fix Layer 1 of 5-layer defense)
#
# Usage:
#   bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
#
# What it does:
#   1. Pre-flight: checks all dependencies and validates existing config
#   2. Copies version-check + pre-prompt-guard scripts to ~/.claude/scripts/
#   3. Adds SessionStart + UserPromptSubmit hooks to ~/.claude/settings.json
#   4. Safe to run multiple times (idempotent — skips already-registered hooks)
#
# v1.6.3a (2026-04-21): Layer 1 install gap fix — UserPromptSubmit hook is now
# auto-registered. Previously /install-skill copied files but did NOT modify
# ~/.claude/settings.json, so default installs shipped without Layer 1 defense.

set -euo pipefail

SCRIPTS_DIR="$HOME/.claude/scripts"
SETTINGS="$HOME/.claude/settings.json"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"

VERSION_HOOK_ID="session:lifeos-version-check"
VERSION_SOURCE="$SOURCE_DIR/lifeos-version-check.sh"
VERSION_DEST="$SCRIPTS_DIR/lifeos-version-check.sh"

GUARD_HOOK_ID="lifeos:pre-prompt-guard"
GUARD_SOURCE="$SOURCE_DIR/lifeos-pre-prompt-guard.sh"
GUARD_DEST="$SCRIPTS_DIR/lifeos-pre-prompt-guard.sh"

echo "🏛️ Life OS Hook Setup"
echo ""

# ── Pre-flight checks (BEFORE touching any files) ──────────────────

# 1a. jq is required
if ! command -v jq &>/dev/null; then
  echo "❌ jq is required but not found."
  echo "   Install it first: brew install jq (macOS) / apt install jq (Linux)"
  exit 1
fi

# 1b. Source scripts must exist
if [ ! -f "$VERSION_SOURCE" ]; then
  echo "❌ Source script not found: $VERSION_SOURCE"
  exit 1
fi
if [ ! -f "$GUARD_SOURCE" ]; then
  echo "❌ Source script not found: $GUARD_SOURCE"
  echo "   (v1.6.3 Layer 1 defense requires this. Update skill: /install-skill <repo>)"
  exit 1
fi

# 1c. If settings.json already exists, it must be valid JSON
if [ -f "$SETTINGS" ]; then
  if ! jq empty "$SETTINGS" 2>/dev/null; then
    echo "❌ $SETTINGS contains invalid JSON. Please fix it manually and re-run."
    exit 1
  fi
fi

echo "✅ Pre-flight checks passed"

# ── Install scripts ──────────────────────────────────────────────────

mkdir -p "$SCRIPTS_DIR"

cp "$VERSION_SOURCE" "$VERSION_DEST"
chmod +x "$VERSION_DEST"
echo "✅ Version check script installed → $VERSION_DEST"

cp "$GUARD_SOURCE" "$GUARD_DEST"
chmod +x "$GUARD_DEST"
echo "✅ Pre-prompt guard script installed → $GUARD_DEST"

# ── Initialize settings.json if needed ──────────────────────────────

if [ ! -f "$SETTINGS" ]; then
  echo '{"hooks":{}}' > "$SETTINGS"
  echo "✅ Created minimal $SETTINGS"
fi

# ── Helper: register a hook idempotently ────────────────────────────
# Args: $1 = event name (SessionStart / UserPromptSubmit / ...)
#       $2 = hook id (string)
#       $3 = command path (full path to script)
#       $4 = description (string)
#       $5 = timeout in seconds (number)
register_hook() {
  local EVENT="$1"
  local HOOK_ID="$2"
  local COMMAND_PATH="$3"
  local DESCRIPTION="$4"
  local TIMEOUT="$5"

  # Idempotent check
  if jq -e ".hooks.${EVENT}[]? | select(.id == \"$HOOK_ID\")" "$SETTINGS" &>/dev/null 2>&1; then
    echo "✅ ${EVENT} hook \"$HOOK_ID\" already registered (skipping)"
    return
  fi

  # Ensure event array exists
  local CURRENT_TYPE
  CURRENT_TYPE=$(jq -r ".hooks.${EVENT} | type" "$SETTINGS" 2>/dev/null || echo "null")
  if [ "$CURRENT_TYPE" != "array" ]; then
    jq ".hooks = (.hooks // {}) | .hooks.${EVENT} = []" "$SETTINGS" > "${SETTINGS}.tmp" && mv "${SETTINGS}.tmp" "$SETTINGS"
  fi

  # Build hook block
  local HOOK_JSON
  HOOK_JSON=$(cat <<HOOKEOF
{
  "matcher": "*",
  "hooks": [
    {
      "type": "command",
      "command": "bash \"$COMMAND_PATH\"",
      "timeout": $TIMEOUT
    }
  ],
  "description": "$DESCRIPTION",
  "id": "$HOOK_ID"
}
HOOKEOF
)

  jq --argjson hook "$HOOK_JSON" ".hooks.${EVENT} += [\$hook]" "$SETTINGS" > "${SETTINGS}.tmp" && mv "${SETTINGS}.tmp" "$SETTINGS"
  echo "✅ ${EVENT} hook \"$HOOK_ID\" registered"
}

# ── Register hooks ──────────────────────────────────────────────────

register_hook \
  "SessionStart" \
  "$VERSION_HOOK_ID" \
  "$VERSION_DEST" \
  "Check for Life OS skill updates (daily)" \
  "5"

register_hook \
  "UserPromptSubmit" \
  "$GUARD_HOOK_ID" \
  "$GUARD_DEST" \
  "Life OS trigger-word guard · v1.6.3 COURT-START-001 fix Layer 1 · injects HARD RULE reminder when Start Session / Adjourn / Review / Debate trigger words detected" \
  "3"

echo ""
echo "🏛️ Setup complete. Life OS hooks active:"
echo "   · SessionStart      → daily skill update check"
echo "   · UserPromptSubmit  → trigger-word HARD RULE injection (Layer 1 of 5)"
echo ""
echo "   To uninstall: remove the \"$VERSION_HOOK_ID\" and \"$GUARD_HOOK_ID\""
echo "   entries from $SETTINGS"
