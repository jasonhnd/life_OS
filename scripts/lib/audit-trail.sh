#!/usr/bin/env bash
# Life OS · Audit Trail shared library (v1.7.1 R11)
# Provides JSON runtime evidence files for subagents and ROUTER prefetch steps.

audit_trail_timestamp() {
  date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z'
}

audit_json_string() {
  local value="${1:-}"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\r'/}"
  value="${value//$'\n'/\\n}"
  printf '"%s"' "$value"
}

audit_trail_slug() {
  local value="${1:-unknown}"
  value="$(printf '%s' "$value" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9._-]+/-/g; s/^-+//; s/-+$//g' 2>/dev/null || true)"
  if [[ -z "$value" ]]; then
    value="unknown"
  fi
  printf '%s\n' "$value"
}

audit_trail_root() {
  local root="${LIFEOS_AUDIT_ROOT:-${LIFEOS_SECOND_BRAIN_PATH:-${LIFEOS_SECOND_BRAIN:-${SECOND_BRAIN_PATH:-${SECOND_BRAIN:-}}}}}"
  if [[ -z "$root" ]]; then
    root="$(pwd -P 2>/dev/null || pwd)"
  fi
  printf '%s\n' "$root"
}

audit_trail_session_id() {
  local sid="${LIFEOS_SESSION_ID:-${AUDIT_TRAIL_SESSION_ID:-${LIFEOS_AUDIT_SESSION_ID:-}}}"
  if [[ -z "$sid" ]]; then
    sid="$(date -u '+%Y%m%dT%H%M%S' 2>/dev/null || date '+%Y%m%dT%H%M%S')"
  fi
  sid="$(printf '%s' "$sid" | sed -E 's/[^A-Za-z0-9._-]+/-/g; s/^-+//; s/-+$//g' 2>/dev/null || true)"
  if [[ -z "$sid" ]]; then
    sid="$(date -u '+%Y%m%dT%H%M%S' 2>/dev/null || date '+%Y%m%dT%H%M%S')"
  fi
  AUDIT_TRAIL_SESSION_ID="$sid"
  printf '%s\n' "$AUDIT_TRAIL_SESSION_ID"
}

audit_trail_dir() {
  local root
  local sid
  local dir

  sid="$(audit_trail_session_id)"
  root="$(audit_trail_root)"
  dir="$root/_meta/runtime/$sid"
  mkdir -p "$dir" || return 1
  printf '%s\n' "$dir"
}

# emit_trail_entry <subagent> <step> <json_payload>
emit_trail_entry() {
  local subagent="$1"
  local step="$2"
  local payload="$3"
  local dir
  local file

  dir="$(audit_trail_dir)" || return 1
  file="$dir/$(audit_trail_slug "$subagent")-$(audit_trail_slug "$step").json"
  printf '%s\n' "$payload" >"$file" || return 1
  echo "[TRAIL: ${subagent}/${step} -> ${file}]"
}

# emit_trail_marker <subagent> <step> <step_name> <input_summary> <output_summary>
emit_trail_marker() {
  local subagent="$1"
  local step="$2"
  local step_name="$3"
  local input_summary="$4"
  local output_summary="$5"
  local now
  local payload
  local trigger_count

  now="$(audit_trail_timestamp)"
  trigger_count="${LIFEOS_TRIGGER_COUNT_IN_SESSION:-${TRIGGER_COUNT_IN_SESSION:-1}}"
  if ! [[ "$trigger_count" =~ ^[0-9]+$ ]]; then
    trigger_count=1
  fi
  payload=$(
    cat <<JSON
{
  "subagent": $(audit_json_string "$subagent"),
  "step_or_phase": $(audit_json_string "$step"),
  "step_name": $(audit_json_string "$step_name"),
  "started_at": $(audit_json_string "$now"),
  "ended_at": $(audit_json_string "$now"),
  "input_summary": $(audit_json_string "$input_summary"),
  "tool_calls": [],
  "llm_reasoning": "(Bash pre-fetch, no LLM)",
  "output_summary": $(audit_json_string "$output_summary"),
  "tokens": {"input": 0, "output": 0},
  "fresh_invocation": true,
  "trigger_count_in_session": ${trigger_count},
  "audit_trail_version": "v1.7.1-r11"
}
JSON
  )
  emit_trail_entry "$subagent" "$step" "$payload"
}
