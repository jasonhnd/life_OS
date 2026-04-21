#!/bin/bash
# Life OS Hooks · Shared Library
# ─────────────────────────────────────────────────────────────────────────────
# Common functions used by all 5 v1.7 hook scripts. Source via:
#   source "$(dirname "$0")/_lib.sh"
#
# Design:
# - Bash 4+ required (uses builtins + arrays)
# - jq preferred, bash-regex fallback when jq absent
# - Zero network, zero filesystem beyond `pwd` and compliance path
# - All hook scripts must stay < 100 ms on typical input
#
# Security invariants:
# - Never eval, never treat stdin strings as shell tokens
# - Always `jq -r` then use the value only as a string argument
# - Violations log writes go through lib_log_violation — never inline
#
# Created: 2026-04-21 (v1.7 Sprint 1)
# Contract: references/hooks-spec.md §5–§7
# ─────────────────────────────────────────────────────────────────────────────

# ─── Compliance path detection (spec §6) ────────────────────────────────────
# Dev repo  → pro/compliance/violations.md
# User repo → _meta/compliance/violations.md
# Anything else → /dev/null (skip logging entirely)
lib_detect_compliance_path() {
  local cwd="${1:-$PWD}"
  if [ -f "$cwd/pro/agents/retrospective.md" ]; then
    echo "$cwd/pro/compliance/violations.md"
  elif [ -f "$cwd/_meta/config.md" ]; then
    echo "$cwd/_meta/compliance/violations.md"
  else
    echo "/dev/null"
  fi
}

# ─── JSON field extraction ───────────────────────────────────────────────────
# lib_json_field <json> <field_path>
#   jq if available, else a deliberately-narrow bash fallback (top-level string
#   fields only — nested objects should go through jq in production).
# Returns empty string on missing or on any parse error (never fails hard).
lib_json_field() {
  local input="$1"
  local path="$2"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$input" | jq -r ".${path} // empty" 2>/dev/null || echo ""
    return
  fi
  # Bash fallback: only handles simple top-level keys like "prompt" / "tool_name".
  local key="${path##*.}"
  printf '%s' "$input" \
    | grep -oE "\"${key}\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" \
    | head -1 \
    | sed "s/^\"${key}\"[[:space:]]*:[[:space:]]*\"\\(.*\\)\"$/\\1/" \
    || echo ""
}

# ─── Nested JSON extraction (tool_input.file_path etc.) ─────────────────────
# Allows jq dot paths when jq present. Bash fallback is narrower — it assumes
# the nested value is a quoted string within the first matching object.
lib_json_nested() {
  local input="$1"
  local path="$2"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$input" | jq -r ".${path} // empty" 2>/dev/null || echo ""
    return
  fi
  # Fallback: extract "last_key" value from flat sed, best-effort only.
  local key="${path##*.}"
  printf '%s' "$input" \
    | grep -oE "\"${key}\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" \
    | head -1 \
    | sed "s/^\"${key}\"[[:space:]]*:[[:space:]]*\"\\(.*\\)\"$/\\1/" \
    || echo ""
}

# ─── Violation logger (spec §7) ──────────────────────────────────────────────
# lib_log_violation <type> <severity> <agent> <detail> <hook>
#   type:     CLASS_A | CLASS_B | CLASS_C | CLASS_D | CLASS_E
#   severity: critical | high | medium | low
#   agent:    ROUTER | archiver | retrospective | unknown
#   detail:   ONE-LINE metadata only (never raw user input, spec §13)
#   hook:     script name (pre-prompt-guard / pre-write-scan / ...)
# Appends a row to the compliance log. Silently skips when compliance
# path resolves to /dev/null (cwd isn't a dev repo or second-brain).
lib_log_violation() {
  local v_type="$1"
  local v_sev="$2"
  local v_agent="$3"
  local v_detail="$4"
  local v_hook="$5"
  local path
  path=$(lib_detect_compliance_path "$PWD")

  # No-op in unrelated repos.
  if [ "$path" = "/dev/null" ]; then
    return 0
  fi

  # Ensure directory + header file exist.
  local dir
  dir=$(dirname "$path")
  mkdir -p "$dir" 2>/dev/null || return 0
  if [ ! -f "$path" ]; then
    cat > "$path" <<'HEADER_EOF'
# Compliance Violations Log

> Rolling 90-day window. Older rows archived to `archive/{year}-Q{n}.md` by `backup.py`.

| Timestamp | Type | Severity | Agent | Detail | Hook | Resolved |
|-----------|------|----------|-------|--------|------|----------|
HEADER_EOF
  fi

  # ISO 8601 timestamp with timezone.
  local ts
  ts=$(date -Iseconds 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S%z")

  # Sanitize detail — strip pipes and newlines so the row stays valid markdown.
  local sanitized
  sanitized=$(printf '%s' "$v_detail" | tr '\n\r|' '   ' | head -c 200)

  printf '| %s | %s | %s | %s | %s | %s | open |\n' \
    "$ts" "$v_type" "$v_sev" "$v_agent" "$sanitized" "$v_hook" >> "$path"
}

# ─── Trigger word detection ──────────────────────────────────────────────────
# Returns 0 (match) or 1 (no match); stdout has the classification
# "start" / "adjourn" / "review" / "debate" / "".
lib_classify_trigger() {
  local first_line="$1"
  local start_re='^[[:space:]]*(上朝|开会|开始|はじめる|初める|開始|朝廷開始|閣議開始|朝礼|start|begin|convene|open[[:space:]]session)'
  local review_re='^[[:space:]]*(复盘|早朝|振り返り|レビュー|報告|汇报|review|report|brief[[:space:]]me|standup|morning[[:space:]]court)'
  local adjourn_re='^[[:space:]]*(退朝|散会|结束|終わり|お疲れ|閣議終了|adjourn|done|end|dismiss|close[[:space:]]session)'
  local debate_re='^[[:space:]]*(朝堂议政|讨论|討論|御前会議|debate|comitia|cabinet[[:space:]]session|board[[:space:]]discussion|plenary[[:space:]]debate)'

  if echo "$first_line" | grep -qiE "$start_re"; then
    echo "start"
    return 0
  elif echo "$first_line" | grep -qiE "$adjourn_re"; then
    echo "adjourn"
    return 0
  elif echo "$first_line" | grep -qiE "$review_re"; then
    echo "review"
    return 0
  elif echo "$first_line" | grep -qiE "$debate_re"; then
    echo "debate"
    return 0
  else
    echo ""
    return 1
  fi
}

# ─── Agent expected-by-trigger map ──────────────────────────────────────────
lib_expected_agent() {
  case "$1" in
    start|review) echo "retrospective" ;;
    adjourn)      echo "archiver" ;;
    debate)       echo "council" ;;
    *)            echo "" ;;
  esac
}
