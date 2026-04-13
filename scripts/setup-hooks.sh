#!/bin/bash
# Life OS Hook Setup — run ONCE after installing Life OS skill
# Adds a SessionStart hook to Claude Code that checks for updates daily
#
# Usage:
#   bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
#
# What it does:
#   1. Copies version-check script to ~/.claude/scripts/
#   2. Adds SessionStart hook to ~/.claude/settings.json
#   3. Safe to run multiple times (idempotent)

set -euo pipefail

SCRIPTS_DIR="$HOME/.claude/scripts"
SETTINGS="$HOME/.claude/settings.json"
HOOK_ID="session:lifeos-version-check"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_SCRIPT="$SCRIPTS_DIR/lifeos-version-check.sh"

echo "🏛️ Life OS Hook Setup"
echo ""

# Step 1: Copy version check script
mkdir -p "$SCRIPTS_DIR"
cp "$SOURCE_DIR/lifeos-version-check.sh" "$DEST_SCRIPT"
chmod +x "$DEST_SCRIPT"
echo "✅ Version check script installed → $DEST_SCRIPT"

# Step 2: Add to settings.json
if [ ! -f "$SETTINGS" ]; then
  echo "⚠️  $SETTINGS not found. Creating minimal settings..."
  echo '{"hooks":{"SessionStart":[]}}' > "$SETTINGS"
fi

# Check if jq is available
if ! command -v jq &>/dev/null; then
  echo ""
  echo "⚠️  jq not found. Please install jq and re-run, or manually add this to $SETTINGS:"
  echo ""
  echo '  "SessionStart": [{'
  echo '    "matcher": "*",'
  echo '    "hooks": [{"type": "command", "command": "bash \"'"$DEST_SCRIPT"'\"", "timeout": 5}],'
  echo '    "description": "Check for Life OS skill updates (daily)",'
  echo '    "id": "'"$HOOK_ID"'"'
  echo '  }]'
  echo ""
  exit 1
fi

# Check if hook already exists
if jq -e ".hooks.SessionStart[]? | select(.id == \"$HOOK_ID\")" "$SETTINGS" &>/dev/null 2>&1; then
  echo "✅ Hook already exists in settings.json (skipping)"
  echo ""
  echo "🏛️ Setup complete. Life OS will check for updates at every session start."
  exit 0
fi

# Ensure SessionStart array exists
if ! jq -e '.hooks.SessionStart' "$SETTINGS" &>/dev/null 2>&1; then
  jq '.hooks = (.hooks // {}) | .hooks.SessionStart = []' "$SETTINGS" > "${SETTINGS}.tmp" && mv "${SETTINGS}.tmp" "$SETTINGS"
fi

# Add hook
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
