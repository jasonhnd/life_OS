#!/bin/bash
# Life OS pre-prompt guard wrapper.
#
# This variant adds explicit paste-indicator handling for compliance Class F.
# It never logs A1/A2/A3 directly from paste-like prompts. Real trigger prompts
# are delegated to the existing pre-prompt-guard.sh when present.

set -u

INPUT="$(cat)"
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"

json_field() {
  local key="$1"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$INPUT" | jq -r ".${key} // empty" 2>/dev/null || true
  elif command -v python3 >/dev/null 2>&1; then
    FIELD="$key" python3 -c 'import json, os, sys; print(json.load(sys.stdin).get(os.environ["FIELD"], ""))' 2>/dev/null <<<"$INPUT" || true
  elif command -v python >/dev/null 2>&1; then
    FIELD="$key" python -c 'import json, os, sys; print(json.load(sys.stdin).get(os.environ["FIELD"], ""))' 2>/dev/null <<<"$INPUT" || true
  else
    printf '%s' "$INPUT" | sed -n "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
  fi
}

compliance_log_path() {
  if [ -f "./pro/agents/retrospective.md" ]; then
    printf '%s\n' "./pro/compliance/violations.md"
  elif [ -f "./_meta/config.md" ]; then
    printf '%s\n' "./_meta/compliance/violations.md"
  fi
}

emit_activity() {
  # Append only, and only when a coordinator explicitly provided a sink. This
  # keeps Subagent C hook-activity work free to own its path and schema.
  if [ -n "${LIFEOS_HOOK_ACTIVITY_LOG:-}" ]; then
    mkdir -p "$(dirname "$LIFEOS_HOOK_ACTIVITY_LOG")" 2>/dev/null || true
    printf '%s\t%s\t%s\n' "$(date -Iseconds 2>/dev/null || date)" "lifeos-pre-prompt-guard" "$1" >>"$LIFEOS_HOOK_ACTIVITY_LOG" 2>/dev/null || true
  fi
}

append_false_positive() {
  local trigger="$1"
  local reason="$2"
  local log_path
  log_path="$(compliance_log_path)"
  [ -n "$log_path" ] || return 0
  mkdir -p "$(dirname "$log_path")" 2>/dev/null || true
  if [ ! -f "$log_path" ]; then
    {
      echo "# Life OS Compliance Violations Log"
      echo ""
      echo "| Timestamp | Trigger | Type | Severity | Details | Resolved |"
      echo "|-----------|---------|------|----------|---------|----------|"
    } >"$log_path" 2>/dev/null || return 0
  fi
  printf '| %s | %s | F | P2 | Paste-indicator/non-trigger context detected by pre-prompt guard; no A1/A2/A3 emitted. reason=%s | false |\n' \
    "$(date -Iseconds 2>/dev/null || date)" \
    "${trigger:-unknown}" \
    "$reason" >>"$log_path" 2>/dev/null || true
}

PROMPT="$(json_field prompt)"
if [ -z "$PROMPT" ]; then
  emit_activity "no_prompt"
  printf '%s\n' "$INPUT"
  exit 0
fi

FIRST_LINE="$(printf '%s\n' "$PROMPT" | sed -n '/[^[:space:]]/{p;q;}')"
PROMPT_LEN=${#PROMPT}
FIRST_LINE_LEN=${#FIRST_LINE}

TRIGGER_RE='(^|[^[:alpha:]])(start|begin|convene|open session|adjourn|done|end|dismiss|close session|review|report|brief me|standup|morning court|debate|cabinet session|board discussion)([^[:alpha:]]|$)'

if printf '%s\n' "$PROMPT" | grep -qiE "$TRIGGER_RE"; then
  PASTE_REASON=""
  if [ "$PROMPT_LEN" -gt 500 ]; then
    PASTE_REASON="prompt_length_gt_500"
  elif [ "$FIRST_LINE_LEN" -gt 100 ]; then
    PASTE_REASON="first_line_length_gt_100"
  elif ! printf '%s\n' "$FIRST_LINE" | grep -qiE "$TRIGGER_RE"; then
    PASTE_REASON="trigger_not_on_first_nonempty_line"
  elif printf '%s\n' "$PROMPT" | grep -qiE '```|^>|transcript|pasted|paste|below|following log|quoted'; then
    PASTE_REASON="quote_or_transcript_indicator"
  fi

  if [ -n "$PASTE_REASON" ]; then
    TRIGGER="$(printf '%s\n' "$PROMPT" | grep -ioE "$TRIGGER_RE" | head -1 | sed 's/^[^[:alnum:]]*//;s/[^[:alnum:] ].*$//')"
    append_false_positive "$TRIGGER" "$PASTE_REASON"
    emit_activity "class_f:$PASTE_REASON"
    printf '%s\n' "$INPUT"
    exit 0
  fi
fi

emit_activity "delegate"
if [ -f "$HOOK_DIR/pre-prompt-guard.sh" ]; then
  bash "$HOOK_DIR/pre-prompt-guard.sh" <<<"$INPUT" || printf '%s\n' "$INPUT"
else
  printf '%s\n' "$INPUT"
fi

exit 0
