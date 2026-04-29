#!/bin/bash
# Life OS Hook Setup — run ONCE after installing Life OS skill
# ─────────────────────────────────────────────────────────────────────────────
# Registers the following hooks in ~/.claude/settings.json:
#   1. SessionStart       → scripts/lifeos-version-check.sh  (daily update check)
#   2. UserPromptSubmit   → scripts/hooks/pre-prompt-guard.sh       (HARD RULE reminder)
#   3. PreToolUse(Write|Edit)  → scripts/hooks/pre-write-scan.sh     (CLASS_D block)
#   4. PreToolUse(Read)   → scripts/hooks/pre-read-allowlist.sh      (CLASS_E block)
#   5. PostToolUse(Task|Bash|Write|Edit) → scripts/hooks/post-response-verify.sh (CLASS_A block)
#   6. Stop(*)            → scripts/hooks/stop-session-verify.sh     (CLASS_C log)
#
# Usage:
#   bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh            # install
#   bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh --uninstall # remove all life-os-* hooks
#
# Behavior:
#   - Idempotent: running twice is a no-op
#   - Atomic: writes to settings.json.tmp + mv
#   - Pre-flight: checks jq, validates existing JSON, confirms source scripts
#   - Preserves the v1.6.2 lifeos-pre-prompt-guard (legacy id) when present —
#     v1.7's pre-prompt-guard.sh uses a different filename and id.
#
# v1.7 Sprint 1 (2026-04-21): extends v1.6.2's single-hook installer to all 5
# v1.7 shell hooks defined in references/hooks-spec.md §5.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPTS_DIR="$HOME/.claude/scripts"
HOOKS_SUBDIR="$SCRIPTS_DIR/hooks"
SETTINGS="$HOME/.claude/settings.json"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"

# ─── Legacy v1.6.2 hooks (kept untouched for back-compat) ────────────────────
VERSION_HOOK_ID="session:lifeos-version-check"
VERSION_SOURCE="$SOURCE_DIR/lifeos-version-check.sh"
VERSION_DEST="$SCRIPTS_DIR/lifeos-version-check.sh"

LEGACY_GUARD_HOOK_ID="lifeos:pre-prompt-guard"
LEGACY_GUARD_SOURCE="$SOURCE_DIR/lifeos-pre-prompt-guard.sh"
LEGACY_GUARD_DEST="$SCRIPTS_DIR/lifeos-pre-prompt-guard.sh"

# ─── v1.7 Sprint 1 hooks ────────────────────────────────────────────────────
HOOK_PRE_PROMPT_ID="life-os-pre-prompt-guard"
HOOK_POST_RESPONSE_ID="life-os-post-response-verify"
HOOK_PRE_WRITE_ID="life-os-pre-write-scan"
HOOK_STOP_ID="life-os-stop-session-verify"
HOOK_PRE_READ_ID="life-os-pre-read-allowlist"
HOOK_PRE_BASH_APPROVAL_ID="life-os-pre-bash-approval"

# v1.8.0 hook IDs
HOOK_SESSION_START_INBOX_ID="life-os-session-start-inbox"
HOOK_PRE_TASK_LAUNCH_ID="life-os-pre-task-launch"
HOOK_POST_TASK_AUDIT_TRAIL_ID="life-os-post-task-audit-trail"

# Source paths inside the skill package
V17_LIB_SOURCE="$SOURCE_DIR/hooks/_lib.sh"
V17_PRE_PROMPT_SOURCE="$SOURCE_DIR/hooks/pre-prompt-guard.sh"
V17_POST_RESPONSE_SOURCE="$SOURCE_DIR/hooks/post-response-verify.sh"
V17_PRE_WRITE_SOURCE="$SOURCE_DIR/hooks/pre-write-scan.sh"
V17_STOP_SOURCE="$SOURCE_DIR/hooks/stop-session-verify.sh"
V17_PRE_READ_SOURCE="$SOURCE_DIR/hooks/pre-read-allowlist.sh"
V17_PRE_BASH_APPROVAL_SOURCE="$SOURCE_DIR/hooks/pre-bash-approval.sh"

# v1.8.0 hook source paths
V18_SESSION_START_INBOX_SOURCE="$SOURCE_DIR/hooks/session-start-inbox.sh"
V18_PRE_TASK_LAUNCH_SOURCE="$SOURCE_DIR/hooks/pre-task-launch.sh"
V18_POST_TASK_AUDIT_TRAIL_SOURCE="$SOURCE_DIR/hooks/post-task-audit-trail.sh"

# Dest paths inside ~/.claude/scripts/hooks
V17_LIB_DEST="$HOOKS_SUBDIR/_lib.sh"
V17_PRE_PROMPT_DEST="$HOOKS_SUBDIR/pre-prompt-guard.sh"
V17_POST_RESPONSE_DEST="$HOOKS_SUBDIR/post-response-verify.sh"
V17_PRE_WRITE_DEST="$HOOKS_SUBDIR/pre-write-scan.sh"
V17_STOP_DEST="$HOOKS_SUBDIR/stop-session-verify.sh"
V17_PRE_READ_DEST="$HOOKS_SUBDIR/pre-read-allowlist.sh"
V17_PRE_BASH_APPROVAL_DEST="$HOOKS_SUBDIR/pre-bash-approval.sh"

# v1.8.0 hook dest paths
V18_SESSION_START_INBOX_DEST="$HOOKS_SUBDIR/session-start-inbox.sh"
V18_PRE_TASK_LAUNCH_DEST="$HOOKS_SUBDIR/pre-task-launch.sh"
V18_POST_TASK_AUDIT_TRAIL_DEST="$HOOKS_SUBDIR/post-task-audit-trail.sh"

# ─── Uninstall mode ─────────────────────────────────────────────────────────
uninstall_all() {
  local unregister_script="$SOURCE_DIR/unregister-claude-agents.sh"
  if [ -f "$unregister_script" ]; then
    echo "Removing Life OS native subagent wrappers..."
    bash "$unregister_script"
  fi

  if [ ! -f "$SETTINGS" ]; then
    echo "ℹ️ $SETTINGS not found — nothing to uninstall"
    exit 0
  fi
  if ! command -v jq &>/dev/null; then
    echo "❌ jq required for uninstall — install then retry"
    exit 1
  fi
  if ! jq empty "$SETTINGS" 2>/dev/null; then
    echo "❌ $SETTINGS is invalid JSON; refusing to touch"
    exit 1
  fi

  # Remove any hook with id prefix "life-os-" from every event array.
  # Also drop the legacy "lifeos:" prefixed id (v1.6.3 guard).
  local tmp="${SETTINGS}.tmp"
  jq '
    .hooks |= (
      if . == null then {} else . end
      | to_entries
      | map(.value = (
          if (.value | type) == "array" then
            [.value[] | select(.id | tostring | (startswith("life-os-") | not) and (. != "lifeos:pre-prompt-guard") and (. != "session:lifeos-version-check"))]
          else .value end
        ))
      | from_entries
    )
  ' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
  echo "✅ Removed all life-os-* + legacy lifeos: hooks from $SETTINGS"
  exit 0
}

if [ "${1:-}" = "--uninstall" ]; then
  uninstall_all
fi

# ─── Pre-flight ─────────────────────────────────────────────────────────────
echo "🏛️ Life OS Hook Setup (v1.7 Sprint 1)"
echo ""

if ! command -v jq &>/dev/null; then
  echo "❌ jq is required but not found."
  echo "   Install: brew install jq (macOS) / apt install jq (Linux) / choco install jq (Win)"
  exit 1
fi

# Check every source script exists
for src in \
  "$VERSION_SOURCE" "$LEGACY_GUARD_SOURCE" \
  "$V17_LIB_SOURCE" "$V17_PRE_PROMPT_SOURCE" "$V17_POST_RESPONSE_SOURCE" \
  "$V17_PRE_WRITE_SOURCE" "$V17_STOP_SOURCE" "$V17_PRE_READ_SOURCE"; do
  if [ ! -f "$src" ]; then
    echo "❌ Source script not found: $src"
    echo "   Your install may be from an older Life OS version. Re-run: /install-skill"
    exit 1
  fi
done

if [ -f "$SETTINGS" ] && ! jq empty "$SETTINGS" 2>/dev/null; then
  echo "❌ $SETTINGS contains invalid JSON. Fix manually, then re-run."
  exit 1
fi

echo "✅ Pre-flight checks passed"

# ─── Copy scripts to ~/.claude ──────────────────────────────────────────────
mkdir -p "$SCRIPTS_DIR" "$HOOKS_SUBDIR"

copy_exec() {
  local src="$1"; local dst="$2"
  cp "$src" "$dst"
  chmod +x "$dst"
  echo "  ✅ $(basename "$dst")"
}

echo ""
echo "📁 Installing scripts → $SCRIPTS_DIR"
copy_exec "$VERSION_SOURCE"       "$VERSION_DEST"
copy_exec "$LEGACY_GUARD_SOURCE"  "$LEGACY_GUARD_DEST"

echo ""
echo "📁 Installing v1.7 hooks → $HOOKS_SUBDIR"
# _lib.sh is sourced, not executed directly — still make it readable.
cp "$V17_LIB_SOURCE" "$V17_LIB_DEST"
chmod +r "$V17_LIB_DEST"
echo "  ✅ $(basename "$V17_LIB_DEST")"
copy_exec "$V17_PRE_PROMPT_SOURCE"    "$V17_PRE_PROMPT_DEST"
copy_exec "$V17_POST_RESPONSE_SOURCE" "$V17_POST_RESPONSE_DEST"
copy_exec "$V17_PRE_WRITE_SOURCE"     "$V17_PRE_WRITE_DEST"
copy_exec "$V17_STOP_SOURCE"          "$V17_STOP_DEST"
copy_exec "$V17_PRE_READ_SOURCE"      "$V17_PRE_READ_DEST"
copy_exec "$V17_PRE_BASH_APPROVAL_SOURCE" "$V17_PRE_BASH_APPROVAL_DEST"
copy_exec "$V18_SESSION_START_INBOX_SOURCE" "$V18_SESSION_START_INBOX_DEST"
copy_exec "$V18_PRE_TASK_LAUNCH_SOURCE" "$V18_PRE_TASK_LAUNCH_DEST"
copy_exec "$V18_POST_TASK_AUDIT_TRAIL_SOURCE" "$V18_POST_TASK_AUDIT_TRAIL_DEST"

# ─── Copy v1.7.3 slash commands → ~/.claude/commands ────────────────────────
COMMANDS_DEST="$HOME/.claude/commands"
COMMANDS_SOURCE="$SOURCE_DIR/commands"
mkdir -p "$COMMANDS_DEST"
echo ""
echo "📁 Installing v1.7.3 slash commands → $COMMANDS_DEST"
if [ -d "$COMMANDS_SOURCE" ]; then
  for cmd in "$COMMANDS_SOURCE"/*.md; do
    if [ -f "$cmd" ]; then
      cp "$cmd" "$COMMANDS_DEST/"
      echo "  ✅ /$(basename "$cmd" .md)"
    fi
  done
else
  echo "  ⚠️ $COMMANDS_SOURCE not found — skipping (older Life OS install layout)"
fi

# ─── Initialize settings.json if needed ─────────────────────────────────────
if [ ! -f "$SETTINGS" ]; then
  echo '{"hooks":{}}' > "$SETTINGS"
  echo ""
  echo "✅ Created minimal $SETTINGS"
fi

# ─── Helper: atomic hook registration ───────────────────────────────────────
register_hook() {
  local EVENT="$1"
  local HOOK_ID="$2"
  local MATCHER="$3"
  local COMMAND_PATH="$4"
  local TIMEOUT="$5"
  local DESCRIPTION="$6"

  # Idempotent — check by id within event array.
  if jq -e ".hooks.${EVENT}[]? | select(.id == \"$HOOK_ID\")" "$SETTINGS" >/dev/null 2>&1; then
    echo "  ✅ ${EVENT}/${HOOK_ID} already registered"
    return 0
  fi

  # Ensure event array exists.
  local current_type
  current_type=$(jq -r ".hooks.${EVENT} | type" "$SETTINGS" 2>/dev/null || echo "null")
  if [ "$current_type" != "array" ]; then
    local tmp="${SETTINGS}.tmp"
    jq ".hooks = (.hooks // {}) | .hooks.${EVENT} = []" "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
  fi

  # Build JSON block, escape appropriately.
  local hook_json
  hook_json=$(jq -n \
    --arg matcher "$MATCHER" \
    --arg cmd "bash \"$COMMAND_PATH\"" \
    --argjson timeout "$TIMEOUT" \
    --arg id "$HOOK_ID" \
    --arg desc "$DESCRIPTION" \
    '{matcher: $matcher, hooks: [{type: "command", command: $cmd, timeout: $timeout}], id: $id, description: $desc}')

  local tmp="${SETTINGS}.tmp"
  jq --argjson hook "$hook_json" ".hooks.${EVENT} += [\$hook]" "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
  echo "  ✅ ${EVENT}/${HOOK_ID} registered (matcher: $MATCHER, timeout: ${TIMEOUT}s)"
}

# ─── Register legacy v1.6.x hooks ───────────────────────────────────────────
echo ""
echo "🔗 Registering hooks in $SETTINGS"

register_hook "SessionStart" "$VERSION_HOOK_ID" "*" \
  "$VERSION_DEST" 5 \
  "Life OS daily update check (v1.6.2)"

# Legacy pre-prompt-guard stays registered for users who installed v1.6.3 before
# this v1.7 rewrite. It's a no-op duplicate of the new one — leaving it in
# avoids churn on next install.
register_hook "UserPromptSubmit" "$LEGACY_GUARD_HOOK_ID" "*" \
  "$LEGACY_GUARD_DEST" 3 \
  "Life OS legacy pre-prompt-guard (v1.6.3, kept for back-compat)"

# ─── Register v1.7 hooks ────────────────────────────────────────────────────
register_hook "UserPromptSubmit" "$HOOK_PRE_PROMPT_ID" "*" \
  "$V17_PRE_PROMPT_DEST" 5 \
  "v1.7 · Trigger-word HARD RULE reminder. Fires Start/Review/Adjourn/Debate."

register_hook "PreToolUse" "$HOOK_PRE_WRITE_ID" "Write|Edit" \
  "$V17_PRE_WRITE_DEST" 5 \
  "v1.7 · Scan Writes to SOUL/wiki/concepts/user-patterns for injection + secrets"

register_hook "PreToolUse" "$HOOK_PRE_READ_ID" "Read" \
  "$V17_PRE_READ_DEST" 3 \
  "v1.7 · Block Reads on credential denylist (~/.ssh, ~/.aws, /etc/passwd, .env, ...)"

register_hook "PreToolUse" "$HOOK_PRE_BASH_APPROVAL_ID" "Bash" \
  "$V17_PRE_BASH_APPROVAL_DEST" 5 \
  "v1.7.3 · Approval guard wrapping tools/approval.py (47 dangerous patterns + hardline + optional tirith if installed)"

# ─── Register v1.8.0 hooks ──────────────────────────────────────────────────
register_hook "SessionStart" "$HOOK_SESSION_START_INBOX_ID" "*" \
  "$V18_SESSION_START_INBOX_DEST" 5 \
  "v1.8.0 · Inject _meta/inbox/notifications.md + maintenance task overdue status + review queue summary as system-reminder at session start (cron removed in R-1.8.0-011; all maintenance is user-invoked)"

register_hook "PreToolUse" "$HOOK_PRE_TASK_LAUNCH_ID" "Task" \
  "$V18_PRE_TASK_LAUNCH_DEST" 3 \
  "v1.8.0 · Enforce knowledge-extractor before archiver (v1.7.3 carve-out HARD RULE machine-strict)"

register_hook "PostToolUse" "$HOOK_POST_TASK_AUDIT_TRAIL_ID" "Task" \
  "$V18_POST_TASK_AUDIT_TRAIL_DEST" 3 \
  "v1.8.0 · Verify R11 audit trail written by Cortex/archiver/knowledge-extractor subagents (immediate check, not session-end)"

register_hook "PostToolUse" "$HOOK_POST_RESPONSE_ID" "Task|Bash|Write|Edit" \
  "$V17_POST_RESPONSE_DEST" 5 \
  "v1.7 · Verify trigger-word → correct Task(subagent) first call"

register_hook "Stop" "$HOOK_STOP_ID" "*" \
  "$V17_STOP_DEST" 10 \
  "v1.7 · On adjourn, verify all 4 archiver phases logged"

REGISTER_SCRIPT="$SOURCE_DIR/register-claude-agents.sh"
if [ -f "$REGISTER_SCRIPT" ]; then
  echo ""
  echo "📋 Registering life_OS agents as Claude Code subagents..."
  bash "$REGISTER_SCRIPT"
fi

write_install_sha() {
  local source_root
  source_root="$(cd "$SOURCE_DIR/.." && pwd)"
  local skill_file="$source_root/SKILL.md"

  if [ ! -f "$skill_file" ]; then
    echo "SKILL.md not found at $skill_file; skipping install_sha write"
    return 0
  fi

  if ! git -C "$source_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "$source_root is not a git worktree; skipping install_sha write"
    return 0
  fi

  local commit_sha
  if ! commit_sha="$(git -C "$source_root" rev-parse HEAD 2>/dev/null)"; then
    echo "Could not read git HEAD from $source_root; skipping install_sha write"
    return 0
  fi
  local install_date
  install_date="$(date -I 2>/dev/null || date '+%Y-%m-%d')"

  local -a sed_inplace
  if sed --version >/dev/null 2>&1; then
    sed_inplace=(sed -i -E)
  else
    sed_inplace=(sed -i '' -E)
  fi

  if grep -q '^commit_sha:' "$skill_file"; then
    "${sed_inplace[@]}" "s|^commit_sha:.*|commit_sha: \"$commit_sha\"|" "$skill_file"
  elif grep -q '^version:' "$skill_file"; then
    "${sed_inplace[@]}" "/^version:/a\\
commit_sha: \"$commit_sha\"
" "$skill_file"
  else
    echo "No version: line found in $skill_file; skipping install_sha write"
    return 0
  fi

  if grep -q '^install_date:' "$skill_file"; then
    "${sed_inplace[@]}" "s|^install_date:.*|install_date: \"$install_date\"|" "$skill_file"
  elif grep -q '^commit_sha:' "$skill_file"; then
    "${sed_inplace[@]}" "/^commit_sha:/a\\
install_date: \"$install_date\"
" "$skill_file"
  fi

  echo "Recorded install commit_sha=${commit_sha:0:7} install_date=$install_date in $skill_file"
}

write_install_sha

echo ""
echo "🏛️ Setup complete. Life OS v1.8.0 hooks active:"
echo "   · SessionStart      $VERSION_HOOK_ID"
echo "   · UserPromptSubmit  $LEGACY_GUARD_HOOK_ID (legacy)"
echo "   · UserPromptSubmit  $HOOK_PRE_PROMPT_ID"
echo "   · PreToolUse(Write|Edit)  $HOOK_PRE_WRITE_ID"
echo "   · PreToolUse(Read)  $HOOK_PRE_READ_ID"
echo "   · PostToolUse(Task|Bash|Write|Edit)  $HOOK_POST_RESPONSE_ID"
echo "   · Stop              $HOOK_STOP_ID"
echo ""
echo "   To uninstall: bash $(basename "$0") --uninstall"
