#!/bin/bash
# Life OS · post-response-verify.sh (v1.7 Sprint 1)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   PostToolUse
# Matcher: Task|Bash|Write|Edit
# Exit:    0 = pass | 2 = block (CLASS_A violation)
# Timeout: 5s
#
# Purpose
#   After any tool call, verify: if the recent user message contains a trigger
#   word (上朝/start, 退朝/adjourn, 复盘/review), the tool that just ran MUST
#   be Task() targeting the correct subagent. Otherwise the ROUTER is running
#   subagent logic in main context → log CLASS_A + block so Claude Code
#   retries correctly.
#
# Solves
#   ROUTER claiming "let me launch retrospective" but then running Bash/Read
#   directly against _meta/*, journal/, or wiki/ instead of via subagent.
#
# Contract: references/hooks-spec.md §5.2
# ─────────────────────────────────────────────────────────────────────────────

set -u

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$HOOK_DIR/_lib.sh"

ACTIVITY_DIR="$HOME/.cache/lifeos"
ACTIVITY_LOG="$ACTIVITY_DIR/hook-activity-$(date +%F).log"
ACTIVITY_TOOL="unknown"
ACTIVITY_VERDICT="pass"
emit_activity() {
  local line="🪝 post-response-verify: tool=${ACTIVITY_TOOL} verdict=${ACTIVITY_VERDICT}"
  mkdir -p "$ACTIVITY_DIR" 2>/dev/null || true
  printf '%s\n' "$line"
  printf '%s %s\n' "$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')" "$line" >> "$ACTIVITY_LOG" 2>/dev/null || true
}
trap emit_activity EXIT

INPUT="$(cat)"
if [ -z "$INPUT" ]; then
  exit 0
fi

TOOL_NAME="$(lib_json_field "$INPUT" tool_name)"
ACTIVITY_TOOL="${TOOL_NAME:-unknown}"
RECENT_MSG="$(lib_json_field "$INPUT" recent_user_message)"

# No recent message = no trigger context = nothing to verify.
if [ -z "$RECENT_MSG" ]; then
  exit 0
fi

# Trigger on first line only (mirrors pre-prompt-guard false-positive policy)
FIRST_LINE="$(printf '%s' "$RECENT_MSG" | sed -n '/[^[:space:]]/{p;q;}')"
[ ${#FIRST_LINE} -gt 100 ] && exit 0

CLASS="$(lib_classify_trigger "$FIRST_LINE")"
if [ -z "$CLASS" ]; then
  exit 0
fi

EXPECTED_AGENT="$(lib_expected_agent "$CLASS")"

# Extract subagent type from Task tool_input (best-effort)
SUBAGENT=""
if [ "$TOOL_NAME" = "Task" ]; then
  # Try nested jq path first
  if command -v jq >/dev/null 2>&1; then
    SUBAGENT="$(printf '%s' "$INPUT" | jq -r '.tool_input.subagent_type // .tool_input.agent // empty' 2>/dev/null || echo "")"
  fi
  # Bash fallback — grep for subagent_type within tool_input
  if [ -z "$SUBAGENT" ]; then
    SUBAGENT="$(printf '%s' "$INPUT" \
      | grep -oE '"subagent_type"[[:space:]]*:[[:space:]]*"[^"]*"' \
      | head -1 \
      | sed 's/^"subagent_type"[[:space:]]*:[[:space:]]*"\(.*\)"$/\1/')"
  fi
fi

# ─── Compliance logic ──────────────────────────────────────────────────────
# Compliant: tool_name == Task AND subagent == expected
# Violation otherwise (Bash/Write/Edit after trigger, or Task-wrong-subagent).
if [ "$TOOL_NAME" = "Task" ] && [ "$SUBAGENT" = "$EXPECTED_AGENT" ]; then
  ACTIVITY_VERDICT="pass"
  exit 0
fi

# ─── Violation: log CLASS_A + block ────────────────────────────────────────
DETAIL="trigger=$CLASS expected=Task($EXPECTED_AGENT) got=${TOOL_NAME}"
if [ -n "$SUBAGENT" ]; then
  DETAIL="$DETAIL(subagent_type=$SUBAGENT)"
fi

lib_log_violation "CLASS_A" "critical" "ROUTER" "$DETAIL" "post-response-verify"
ACTIVITY_VERDICT="block"

cat >&1 <<EOF
<system-reminder>
🚫 HARD RULE VIOLATION (CLASS_A) · post-response-verify blocked tool.

Recent user message contained trigger: "$CLASS" (word: "$FIRST_LINE")
Required: Task($EXPECTED_AGENT) as the FIRST tool call.
Observed: $TOOL_NAME${SUBAGENT:+ (subagent_type=$SUBAGENT)}

This tool call was blocked. Logged to compliance path as CLASS_A (critical).

Fix: Retry with Task($EXPECTED_AGENT). Do not execute subagent steps in main context.
Precedent: COURT-START-001 (2026-04-19).
</system-reminder>
EOF

cat >&2 <<EOF
Blocked by life-os-post-response-verify: recent trigger "$CLASS" requires Task($EXPECTED_AGENT); observed $TOOL_NAME.
EOF

exit 2
