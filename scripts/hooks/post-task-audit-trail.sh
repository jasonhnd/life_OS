#!/bin/bash
# Life OS · post-task-audit-trail.sh (v1.8.0)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   PostToolUse
# Matcher: Task
# Exit:    0 always (cannot retry the subagent — just log)
# Timeout: 3s
#
# Purpose
#   Enforce R11 audit trail HARD RULE for all subagents that promised to
#   write _meta/runtime/<sid>/<name>.json. Currently the spec says MUST but
#   the system only checks at session-end (stop-session-verify). With this
#   hook, every subagent completion is checked immediately.
#
# Bypass switch
#   - export LIFEOS_SKIP_AUDIT_GUARD=1   # cron sets this
# ─────────────────────────────────────────────────────────────────────────────

set -u

if [ "${LIFEOS_SKIP_AUDIT_GUARD:-0}" = "1" ]; then
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
# Parse failure logs a stderr warning so the issue is visible.
SUBAGENT=""
PARSE_OK=0
if command -v jq >/dev/null 2>&1; then
  if SUBAGENT="$(printf '%s' "$INPUT" | jq -er '.tool_input.subagent_type // ""' 2>/dev/null)"; then
    PARSE_OK=1
  fi
fi
if [ "$PARSE_OK" -eq 0 ]; then
  PARSED="$(printf '%s' "$INPUT" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    val = d.get('tool_input', {}).get('subagent_type') or ''
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
  echo "[post-task-audit-trail] WARNING: stdin JSON parse failed; cannot verify R11 audit trail for this launch" >&2
  exit 0
fi

# v1.8.0 pivot: Cortex subagents (hippocampus / concept-lookup / soul-check /
# gwt-arbitrator) are now pull-based — ROUTER decides when to launch, audit
# trail is no longer mandatory. narrator-validator deleted entirely.
# Only archiver and knowledge-extractor still enforce R11 audit trail because
# they touch persistent SOUL/wiki/journal state and must be reproducible.
case "$SUBAGENT" in
  *knowledge-extractor*) AGENT_NAME="knowledge-extractor" ;;
  *archiver*) AGENT_NAME="archiver" ;;
  *) exit 0 ;;
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

TRAIL_DIR="_meta/runtime/$LATEST_SID"
TRAIL_FOUND=0
for trail_pattern in "${TRAIL_DIR}/${AGENT_NAME}.json" "${TRAIL_DIR}/${AGENT_NAME}-"*.json; do
  if [ -f "$trail_pattern" ]; then
    TRAIL_FOUND=1
    break
  fi
done

if [ "$TRAIL_FOUND" = "1" ]; then
  exit 0
fi

TS="$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')"
VIOLATION_LINE="| $TS | CLASS_C | medium | $AGENT_NAME | missing_audit_trail=_meta/runtime/$LATEST_SID/$AGENT_NAME.json | post-task-audit-trail | open |"

for violations_path in "_meta/violations.md" "pro/compliance/violations.md"; do
  if [ -f "$violations_path" ]; then
    echo "$VIOLATION_LINE" >> "$violations_path" 2>/dev/null && break
  fi
done

cat >&2 <<EOF
⚠️ Life OS · post-task-audit-trail · CLASS_C violation logged

Subagent '$AGENT_NAME' did NOT write its R11 audit trail to:
  $TRAIL_DIR/$AGENT_NAME.json

R11 HARD RULE (pro/agents/$AGENT_NAME.md): every subagent invocation MUST
write its audit trail before returning. Missing trails are CLASS_C
compliance violations.

Logged to violations.md. AUDITOR Mode 3 will pick this up.
EOF

exit 0
