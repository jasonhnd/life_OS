#!/bin/bash
# Life OS · pre-bash-approval.sh (v1.7.3)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   PreToolUse
# Matcher: Bash
# Exit:    0 (approve, silent) | 2 (block, stderr -> Claude visible)
# Timeout: 5s
#
# Purpose
#   Bridge Claude Code Bash invocations to tools/approval.py.
#   Closes the v1.7.2 gap where 47 dangerous-command patterns sat in
#   approval.py with 0 callers. Now every Bash command is screened.
#
# Behaviour
#   - Reads JSON from stdin (Claude Code hook protocol)
#   - Extracts tool_input.command
#   - Calls tools.approval.check_dangerous_command via inline python
#   - exit 0 silently if approved (no UI noise on safe commands)
#   - exit 2 with stderr message if blocked (Claude shows reason to user)
#
# Bypass switch
#   - export LIFEOS_YOLO_MODE=1   # one-session bypass (use sparingly)
#
# Safety design
#   - Never blocks on tool failure (silent pass) — we don't want hook bugs
#     to lock the user out of their own shell
#   - Searches for lifeos source in 3 standard locations
# ─────────────────────────────────────────────────────────────────────────────

set -u

INPUT="$(cat)"
if [ -z "$INPUT" ]; then
  exit 0
fi

# ─── Extract command from hook JSON ─────────────────────────────────────────
COMMAND=""
if command -v jq >/dev/null 2>&1; then
  COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)"
fi
if [ -z "$COMMAND" ]; then
  COMMAND="$(printf '%s' "$INPUT" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    pass
" 2>/dev/null)"
fi
if [ -z "$COMMAND" ]; then
  exit 0
fi

# ─── Locate lifeos source (where tools/approval.py lives) ───────────────────
LIFEOS_DIR=""
for candidate in \
  "$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)" \
  "$HOME/.claude/skills/life_OS" \
  "$HOME/.claude/skills/lifeos"; do
  if [ -n "$candidate" ] && [ -f "$candidate/tools/approval.py" ]; then
    LIFEOS_DIR="$candidate"
    break
  fi
done
if [ -z "$LIFEOS_DIR" ]; then
  exit 0
fi

# ─── Run approval check ─────────────────────────────────────────────────────
DECISION_JSON="$(cd "$LIFEOS_DIR" && LIFEOS_INTERACTIVE=1 python -c "
import json, sys
try:
    from tools.approval import check_dangerous_command
    result = check_dangerous_command(sys.argv[1], 'host')
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'approved': True, 'message': None, 'error': str(e)}))
" "$COMMAND" 2>/dev/null)"

if [ -z "$DECISION_JSON" ]; then
  exit 0
fi

# ─── Parse decision ─────────────────────────────────────────────────────────
APPROVED="$(printf '%s' "$DECISION_JSON" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print('true' if d.get('approved', True) else 'false')
except Exception:
    print('true')
" 2>/dev/null)"

if [ "$APPROVED" = "false" ]; then
  MESSAGE="$(printf '%s' "$DECISION_JSON" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('message') or d.get('description') or 'dangerous command pattern matched')
except Exception:
    print('dangerous command pattern matched')
" 2>/dev/null)"
  PATTERN="$(printf '%s' "$DECISION_JSON" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('pattern_key') or d.get('description') or 'unknown')
except Exception:
    print('unknown')
" 2>/dev/null)"

  cat >&2 <<EOF
🛡️ Life OS 守门人 · 危险命令拦截

  命令: $COMMAND
  匹配模式: $PATTERN

  原因: $MESSAGE

  下一步:
    a) 改命令绕开此模式（推荐）
    b) 临时关闭守门人本会话: export LIFEOS_YOLO_MODE=1
    c) 永久 allowlist 此 pattern: 编辑 tools/approval.py

  接入: 47 dangerous patterns from tools/approval.py (v1.7.3 wired)
EOF
  exit 2
fi

exit 0
