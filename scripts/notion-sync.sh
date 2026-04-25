#!/usr/bin/env bash
# ROUTER calls the Notion MCP after archiver Phase 4. Then ROUTER calls this
# script to write the audit trail from observed summaries/payload strings.
# This script does not perform Notion sync, does not call MCP, and does not ask
# the user for confirmation.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P)"
SCRIPT_ROOT="$(cd "${SCRIPT_DIR}/.." 2>/dev/null && pwd -P)"
PWD_ROOT="$(pwd -P 2>/dev/null || pwd)"
AUDIT_TRAIL_AVAILABLE=0

for _audit_trail_lib in "$SCRIPT_DIR/lib/audit-trail.sh" "$SCRIPT_ROOT/scripts/lib/audit-trail.sh"; do
  if [[ -r "$_audit_trail_lib" ]]; then
    if . "$_audit_trail_lib"; then
      AUDIT_TRAIL_AVAILABLE=1
    fi
    break
  fi
done
unset _audit_trail_lib

usage() {
  cat <<'EOF'
Usage: notion-sync.sh --input SUMMARY --output SUMMARY [options]

Writes a ROUTER Notion MCP sync audit trail. It does not sync Notion itself.

Options:
  --root PATH          Second-brain/root path for _meta/runtime output.
  --session-id SID     Runtime audit session id.
  --subagent NAME      Trail actor, default: router.
  --step STEP          Trail step id, default: notion-sync.
  --step-name NAME     Trail step name, default: ROUTER Notion MCP Sync.
  --input TEXT         Input summary observed by ROUTER.
  --output TEXT        Output summary observed by ROUTER.
  --payload TEXT       Literal payload/details to store.
  --payload-file PATH  Read payload/details from a file.
EOF
}

write_notion_sync_trail() {
  local input_summary="${1:-}"
  local output_summary="${2:-}"
  local payload="${3:-}"
  local root="${4:-$PWD_ROOT}"
  local subagent="${5:-notion-sync}"
  local step="${6:-step-10a}"
  local step_name="${7:-ROUTER Notion MCP Sync}"
  local dir
  local path
  local now
  local payload_json
  local trigger_count

  if [[ "${AUDIT_TRAIL_AVAILABLE:-0}" != "1" ]]; then
    printf 'audit-trail helper unavailable\n' >&2
    return 1
  fi

  LIFEOS_AUDIT_ROOT="$root"
  dir="$(audit_trail_dir)" || return 1
  path="$dir/notion-sync.json"
  now="$(audit_trail_timestamp)"
  trigger_count="${LIFEOS_TRIGGER_COUNT_IN_SESSION:-${TRIGGER_COUNT_IN_SESSION:-1}}"
  if ! [[ "$trigger_count" =~ ^[0-9]+$ ]]; then
    trigger_count=1
  fi
  payload_json=$(
    cat <<JSON
{
  "subagent": $(audit_json_string "$subagent"),
  "step_or_phase": $(audit_json_string "$step"),
  "step_name": $(audit_json_string "$step_name"),
  "started_at": $(audit_json_string "$now"),
  "ended_at": $(audit_json_string "$now"),
  "input_summary": $(audit_json_string "$input_summary"),
  "tool_calls": [
    {"tool": "Notion MCP", "args": $(audit_json_string "$input_summary"), "result_summary": $(audit_json_string "${payload:-$output_summary}"), "exit_code": 0}
  ],
  "llm_reasoning": "(ROUTER orchestrator sync wrapper, no subagent LLM)",
  "output_summary": $(audit_json_string "$output_summary"),
  "tokens": {"input": 0, "output": 0},
  "fresh_invocation": true,
  "trigger_count_in_session": ${trigger_count},
  "audit_trail_version": "v1.7.1-r11"
}
JSON
  )
  printf '%s\n' "$payload_json" >"$path" || return 1
  printf '%s\n' "$path"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  root="$PWD_ROOT"
  requested_sid=""
  subagent="notion-sync"
  step="step-10a"
  step_name="ROUTER Notion MCP Sync"
  input_summary=""
  output_summary=""
  payload=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --root)
        if [[ $# -lt 2 ]]; then
          printf 'Missing value for --root\n' >&2
          exit 2
        fi
        root="${2:-}"
        shift 2
        ;;
      --session-id)
        if [[ $# -lt 2 ]]; then
          printf 'Missing value for --session-id\n' >&2
          exit 2
        fi
        requested_sid="${2:-}"
        shift 2
        ;;
      --subagent)
        if [[ $# -lt 2 ]]; then
          printf 'Missing value for --subagent\n' >&2
          exit 2
        fi
        subagent="${2:-}"
        shift 2
        ;;
      --step)
        if [[ $# -lt 2 ]]; then
          printf 'Missing value for --step\n' >&2
          exit 2
        fi
        step="${2:-}"
        shift 2
        ;;
      --step-name)
        if [[ $# -lt 2 ]]; then
          printf 'Missing value for --step-name\n' >&2
          exit 2
        fi
        step_name="${2:-}"
        shift 2
        ;;
      --input)
        if [[ $# -lt 2 ]]; then
          printf 'Missing value for --input\n' >&2
          exit 2
        fi
        input_summary="${2:-}"
        shift 2
        ;;
      --output)
        if [[ $# -lt 2 ]]; then
          printf 'Missing value for --output\n' >&2
          exit 2
        fi
        output_summary="${2:-}"
        shift 2
        ;;
      --payload)
        if [[ $# -lt 2 ]]; then
          printf 'Missing value for --payload\n' >&2
          exit 2
        fi
        payload="${2:-}"
        shift 2
        ;;
      --payload-file)
        if [[ $# -lt 2 ]]; then
          printf 'Missing value for --payload-file\n' >&2
          exit 2
        fi
        payload_file="${2:-}"
        if [[ -r "$payload_file" ]]; then
          payload="$(cat "$payload_file")"
        else
          printf 'Payload file not readable: %s\n' "$payload_file" >&2
          exit 2
        fi
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        printf 'Unknown argument: %s\n' "$1" >&2
        usage >&2
        exit 2
        ;;
    esac
  done

  if [[ -n "$requested_sid" ]]; then
    LIFEOS_AUDIT_SESSION_ID="$requested_sid"
  fi

  if [[ -z "$input_summary" || -z "$output_summary" ]]; then
    printf 'Missing required --input or --output summary.\n' >&2
    usage >&2
    exit 2
  fi

  trail_path="$(write_notion_sync_trail "$input_summary" "$output_summary" "$payload" "$root" "$subagent" "$step" "$step_name")" || exit 1
  printf '[NOTION SYNC TRAIL: %s]\n' "$trail_path"
fi
