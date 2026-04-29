#!/bin/bash
# Life OS · pre-task-launch.sh (v1.8.0)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   PreToolUse
# Matcher: Task
# Exit:    0 (allow) | 2 (block + stderr to user)
# Timeout: 3s
#
# Purpose
#   Enforce v1.7.3 archiver carve-out invariant: ROUTER MUST launch
#   knowledge-extractor BEFORE launching archiver. Without this hook, the
#   spec is just a HARD RULE in markdown that LLM may forget. With it, the
#   machine refuses to launch archiver until knowledge-extractor ran.
#
# Bypass switch
#   - export LIFEOS_SKIP_KE_GUARD=1   # one-session bypass (use in cron)
# ─────────────────────────────────────────────────────────────────────────────

set -u

if [ "${LIFEOS_SKIP_KE_GUARD:-0}" = "1" ]; then
  exit 0
fi

if [ ! -d "_meta/runtime" ]; then
  exit 0
fi

INPUT="$(cat)"
if [ -z "$INPUT" ]; then
  exit 0
fi

# Round-5 audit fix: distinguish parse-failure from empty-subagent.
# Parse failure logs a stderr warning so the issue is visible (this hook's
# role is to enforce the knowledge-extractor → archiver carve-out, not
# general security; we don't block the launch but we surface the failure).
SUBAGENT=""
PARSE_OK=0
if command -v jq >/dev/null 2>&1; then
  if SUBAGENT="$(printf '%s' "$INPUT" | jq -er '.tool_input.subagent_type // .tool_input.description // ""' 2>/dev/null)"; then
    PARSE_OK=1
  fi
fi
if [ "$PARSE_OK" -eq 0 ]; then
  PARSED="$(printf '%s' "$INPUT" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', {})
    val = ti.get('subagent_type') or ti.get('description') or ''
    print('OK\x1f' + (val if isinstance(val, str) else ''))
except Exception:
    sys.exit(1)
" 2>/dev/null)"
  if [ -n "$PARSED" ]; then
    PARSE_OK=1
    SUBAGENT="${PARSED#OK?}"
    [ "$SUBAGENT" = "$PARSED" ] && SUBAGENT=""
  fi
fi

if [ "$PARSE_OK" -eq 0 ]; then
  # Round-6 audit fix: also write a compliance violation so the parse
  # failure surfaces in pro/compliance/violations.md rather than only
  # transient stderr. Source: scripts/hooks/_lib.sh lib_log_violation.
  echo "[pre-task-launch] WARNING: stdin JSON parse failed; cannot enforce knowledge-extractor carve-out for this launch" >&2
  if command -v lib_log_violation >/dev/null 2>&1 || \
     grep -q "lib_log_violation" "$(dirname "$0")/_lib.sh" 2>/dev/null; then
    # shellcheck source=/dev/null
    source "$(dirname "$0")/_lib.sh" 2>/dev/null || true
    if command -v lib_log_violation >/dev/null 2>&1; then
      lib_log_violation "CLASS_C" "low" "router" "stdin-json-parse-failed" "pre-task-launch" 2>/dev/null || true
    fi
  fi
  exit 0
fi

case "$SUBAGENT" in
  *archiver*|*ARCHIVER*) ;;
  *) exit 0 ;;
esac

case "$SUBAGENT" in
  *knowledge-extractor*|*KNOWLEDGE-EXTRACTOR*) exit 0 ;;
esac

LATEST_SID=""
for sid_dir in $(ls -dt _meta/runtime/*/ 2>/dev/null | head -3); do
  if [ -d "$sid_dir" ]; then
    LATEST_SID="$(basename "$sid_dir")"
    break
  fi
done

if [ -z "$LATEST_SID" ]; then
  exit 0
fi

KE_TRAIL="_meta/runtime/$LATEST_SID/knowledge-extractor.json"
if [ -f "$KE_TRAIL" ]; then
  exit 0
fi

cat >&2 <<EOF
🚧 Life OS · pre-task-launch hook · v1.7.3 carve-out enforcement (v1.8.0)

You are trying to launch \`archiver\` (subagent_type=$SUBAGENT) but
knowledge-extractor has not run yet for this session ($LATEST_SID).

v1.7.3 carve-out HARD RULE (pro/CLAUDE.md Step 10): ROUTER MUST launch
knowledge-extractor BEFORE archiver. knowledge-extractor does Phase 2
(7 sub-step extraction) and writes _meta/runtime/$LATEST_SID/extraction/*.md
which archiver Phase 2 reads back to produce the user-facing summary.

To proceed:
  1. Launch knowledge-extractor first (pro/agents/knowledge-extractor.md)
  2. Wait for its YAML output
  3. Then launch archiver

If you're sure you want to skip (e.g., archiver fallback path due to host
not supporting Task nesting), set: export LIFEOS_SKIP_KE_GUARD=1

Spec: pro/CLAUDE.md Step 10 (v1.8.0 launch sequence template)
EOF
exit 2
