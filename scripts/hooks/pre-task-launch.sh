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

SUBAGENT=""
if command -v jq >/dev/null 2>&1; then
  SUBAGENT="$(printf '%s' "$INPUT" | jq -r '.tool_input.subagent_type // .tool_input.description // empty' 2>/dev/null)"
fi
if [ -z "$SUBAGENT" ]; then
  SUBAGENT="$(printf '%s' "$INPUT" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', {})
    print(ti.get('subagent_type') or ti.get('description') or '')
except Exception:
    pass
" 2>/dev/null)"
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
