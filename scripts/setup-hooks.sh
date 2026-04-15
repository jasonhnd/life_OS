#!/bin/bash
# Life OS Hook Setup — run ONCE after installing Life OS skill
# Adds a SessionStart hook to Claude Code that checks for updates daily
#
# Usage:
#   bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
#
# What it does:
#   1. Pre-flight: checks all dependencies and validates existing config
#   2. Copies version-check script to ~/.claude/scripts/
#   3. Adds SessionStart hook to ~/.claude/settings.json
#   4. Safe to run multiple times (idempotent)

set -euo pipefail

SCRIPTS_DIR="$HOME/.claude/scripts"
SETTINGS="$HOME/.claude/settings.json"
HOOK_ID="session:lifeos-version-check"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_SCRIPT="$SCRIPTS_DIR/lifeos-version-check.sh"

echo "🏛️ Life OS Hook Setup"
echo ""

# ── Pre-flight checks (BEFORE touching any files) ──────────────────

# 1a. jq is required
if ! command -v jq &>/dev/null; then
  echo "❌ jq is required but not found."
  echo "   Install it first: brew install jq (macOS) / apt install jq (Linux)"
  echo ""
  echo "   Or manually add this to $SETTINGS under \"hooks\".\"SessionStart\":"
  echo ""
  echo '  {'
  echo '    "matcher": "*",'
  echo '    "hooks": [{"type": "command", "command": "bash \"'"$HOME/.claude/scripts/lifeos-version-check.sh"'\"", "timeout": 5}],'
  echo '    "description": "Check for Life OS skill updates (daily)",'
  echo '    "id": "'"$HOOK_ID"'"'
  echo '  }'
  echo ""
  exit 1
fi

# 1b. Source script must exist
if [ ! -f "$SOURCE_DIR/lifeos-version-check.sh" ]; then
  echo "❌ Source script not found: $SOURCE_DIR/lifeos-version-check.sh"
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

# ── Install ─────────────────────────────────────────────────────────

# 2. Copy version check script
mkdir -p "$SCRIPTS_DIR"
cp "$SOURCE_DIR/lifeos-version-check.sh" "$DEST_SCRIPT"
chmod +x "$DEST_SCRIPT"
echo "✅ Version check script installed → $DEST_SCRIPT"

# 3. Add to settings.json
# Create minimal settings.json if it doesn't exist
if [ ! -f "$SETTINGS" ]; then
  echo '{"hooks":{"SessionStart":[]}}' > "$SETTINGS"
  echo "✅ Created minimal $SETTINGS"
fi

# Check if hook already exists
if jq -e ".hooks.SessionStart[]? | select(.id == \"$HOOK_ID\")" "$SETTINGS" &>/dev/null 2>&1; then
  echo "✅ Hook already exists in settings.json (skipping)"
  echo ""
  echo "🏛️ Setup complete. Life OS will check for updates at every session start."
  exit 0
fi

# Ensure .hooks.SessionStart is an array (initialize if missing or wrong type)
CURRENT_TYPE=$(jq -r '.hooks.SessionStart | type' "$SETTINGS" 2>/dev/null || echo "null")
if [ "$CURRENT_TYPE" != "array" ]; then
  jq '.hooks = (.hooks // {}) | .hooks.SessionStart = []' "$SETTINGS" > "${SETTINGS}.tmp" && mv "${SETTINGS}.tmp" "$SETTINGS"
fi

# Add hook via temp file (atomic write)
HOOK_JSON=$(cat <<HOOKEOF
{
  "matcher": "*",
  "hooks": [
    {
      "type": "command",
      "command": "bash \"$DEST_SCRIPT\"",
      "timeout": 5
    }
  ],
  "description": "Check for Life OS skill updates (daily)",
  "id": "$HOOK_ID"
}
HOOKEOF
)

jq --argjson hook "$HOOK_JSON" '.hooks.SessionStart += [$hook]' "$SETTINGS" > "${SETTINGS}.tmp" && mv "${SETTINGS}.tmp" "$SETTINGS"
echo "✅ SessionStart hook added to settings.json"

echo ""
echo "🏛️ Setup complete. Life OS will check for updates at every session start."
echo "   To uninstall: remove the \"$HOOK_ID\" entry from $SETTINGS"
