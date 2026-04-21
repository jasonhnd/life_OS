#!/bin/bash
# Tests for scripts/setup-hooks.sh
# ─────────────────────────────────────────────────────────────────────────────
# These tests require jq. If jq is unavailable, they skip gracefully.
# The production install path (register_hook) requires jq per spec §10
# pre-flight check.
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SETUP="$REPO_ROOT/scripts/setup-hooks.sh"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/_test_lib.sh"
TEST_NAME="setup-hooks.sh"

[ ! -f "$SETUP" ] && { echo "❌ FATAL: $SETUP missing"; exit 1; }

if ! command -v jq >/dev/null 2>&1; then
  echo "⏭️  jq not installed — skipping setup-hooks tests (production install requires jq per spec §10)"
  echo "── $TEST_NAME: 0 passed, 0 failed (SKIPPED: no jq) ──"
  exit 0
fi

# ─── T1: --uninstall on missing settings.json → no error ───────────────────
echo "T1: --uninstall on missing settings.json"
tmphome=$(mktemp -d)
(HOME="$tmphome" bash "$SETUP" --uninstall) >/dev/null 2>&1
ec=$?
assert_exit "$ec" 0 "graceful no-op"
rm -rf "$tmphome"

# ─── T2: --uninstall removes all life-os-* ids ─────────────────────────────
echo ""
echo "T2: --uninstall removes life-os-* entries"
tmphome=$(mktemp -d)
mkdir -p "$tmphome/.claude"
cat > "$tmphome/.claude/settings.json" <<'EOF'
{
  "hooks": {
    "UserPromptSubmit": [
      {"matcher":"*","hooks":[{"type":"command","command":"bash a.sh"}],"id":"life-os-pre-prompt-guard"},
      {"matcher":"*","hooks":[{"type":"command","command":"bash other.sh"}],"id":"other-hook"}
    ],
    "PreToolUse": [
      {"matcher":"Write","hooks":[{"type":"command","command":"bash b.sh"}],"id":"life-os-pre-write-scan"}
    ]
  },
  "theme": "light"
}
EOF
(HOME="$tmphome" bash "$SETUP" --uninstall) >/dev/null 2>&1
# Expect: life-os-pre-prompt-guard removed, other-hook kept, life-os-pre-write-scan removed.
count_lifeos=$(jq '[.hooks | to_entries[] | .value[] | select(.id | tostring | startswith("life-os-"))] | length' "$tmphome/.claude/settings.json")
count_other=$(jq '[.hooks | to_entries[] | .value[] | select(.id == "other-hook")] | length' "$tmphome/.claude/settings.json")
theme=$(jq -r '.theme' "$tmphome/.claude/settings.json")
assert_eq "$count_lifeos" "0" "all life-os-* removed"
assert_eq "$count_other" "1" "other-hook preserved"
assert_eq "$theme" "light" "unrelated keys preserved"
rm -rf "$tmphome"

# ─── T3: Pre-flight fails on invalid settings JSON ─────────────────────────
echo ""
echo "T3: invalid settings.json → exit 1"
tmphome=$(mktemp -d)
mkdir -p "$tmphome/.claude"
echo "{invalid json" > "$tmphome/.claude/settings.json"
(HOME="$tmphome" bash "$SETUP") >/dev/null 2>&1
ec=$?
assert_exit "$ec" 1 "exits on bad JSON"
rm -rf "$tmphome"

test_summary
