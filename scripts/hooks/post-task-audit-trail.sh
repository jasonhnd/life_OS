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

SUBAGENT=""
if command -v jq >/dev/null 2>&1; then
  SUBAGENT="$(printf '%s' "$INPUT" | jq -r '.tool_input.subagent_type // empty' 2>/dev/null)"
fi
if [ -z "$SUBAGENT" ]; then
  SUBAGENT="$(printf '%s' "$INPUT" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('subagent_type') or '')
except Exception:
    pass
" 2>/dev/null)"
fi

case "$SUBAGENT" in
  *hippocampus*) AGENT_NAME="hippocampus" ;;
  *concept-lookup*) AGENT_NAME="concept-lookup" ;;
  *soul-check*) AGENT_NAME="soul-check" ;;
  *gwt-arbitrator*) AGENT_NAME="gwt-arbitrator" ;;
  *narrator-validator*) AGENT_NAME="narrator-validator" ;;
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
