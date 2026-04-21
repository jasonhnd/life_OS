#!/bin/bash
# Life OS · pre-write-scan.sh (v1.7 Sprint 1)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   PreToolUse
# Matcher: Write|Edit
# Exit:    0 = pass | 2 = block (CLASS_D violation)
# Timeout: 5s
#
# Purpose
#   Fast regex scan of content destined for long-term knowledge files
#   (SOUL.md, wiki/**, _meta/concepts/**, user-patterns.md). Catches
#   injection payloads, leaked secrets, and invisible-Unicode payloads
#   BEFORE they land in the second-brain.
#
# Out-of-scope writes pass through silently — this hook only guards
# knowledge files. (LLM-based privacy check for wiki/SOUL runs later
# in archiver's Phase 2.)
#
# Contract
#   references/hooks-spec.md §5.3 — 15 regex patterns + invisible Unicode
# ─────────────────────────────────────────────────────────────────────────────

set -u

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$HOOK_DIR/_lib.sh"

INPUT="$(cat)"
[ -z "$INPUT" ] && exit 0

TOOL_NAME="$(lib_json_field "$INPUT" tool_name)"
case "$TOOL_NAME" in
  Write|Edit) : ;;
  *) exit 0 ;;
esac

# ─── Extract file_path + content ───────────────────────────────────────────
FILE_PATH=""
CONTENT=""

if command -v jq >/dev/null 2>&1; then
  FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")"
  if [ "$TOOL_NAME" = "Write" ]; then
    CONTENT="$(printf '%s' "$INPUT" | jq -r '.tool_input.content // empty' 2>/dev/null || echo "")"
  else
    CONTENT="$(printf '%s' "$INPUT" | jq -r '.tool_input.new_string // empty' 2>/dev/null || echo "")"
  fi
else
  # Bash fallback — flat grep. Pull first nested "file_path" string.
  FILE_PATH="$(printf '%s' "$INPUT" \
    | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' \
    | head -1 \
    | sed 's/^"file_path"[[:space:]]*:[[:space:]]*"\(.*\)"$/\1/')"
  if [ "$TOOL_NAME" = "Write" ]; then
    CONTENT="$(printf '%s' "$INPUT" \
      | grep -oE '"content"[[:space:]]*:[[:space:]]*"[^"]*"' \
      | head -1 \
      | sed 's/^"content"[[:space:]]*:[[:space:]]*"\(.*\)"$/\1/' \
      | sed 's/\\"/"/g; s/\\n/ /g; s/\\t/ /g')"
  else
    CONTENT="$(printf '%s' "$INPUT" \
      | grep -oE '"new_string"[[:space:]]*:[[:space:]]*"[^"]*"' \
      | head -1 \
      | sed 's/^"new_string"[[:space:]]*:[[:space:]]*"\(.*\)"$/\1/' \
      | sed 's/\\"/"/g; s/\\n/ /g; s/\\t/ /g')"
  fi
fi

# Missing file_path = can't determine scope, pass through.
[ -z "$FILE_PATH" ] && exit 0
[ -z "$CONTENT" ] && exit 0

# ─── Scope check ────────────────────────────────────────────────────────────
# In scope: SOUL.md, wiki/**, _meta/concepts/**, user-patterns.md
in_scope() {
  local p="$1"
  case "$p" in
    */SOUL.md|SOUL.md) return 0 ;;
    */user-patterns.md|user-patterns.md) return 0 ;;
    */wiki/*|wiki/*) return 0 ;;
    */_meta/concepts/*|_meta/concepts/*) return 0 ;;
    *) return 1 ;;
  esac
}

if ! in_scope "$FILE_PATH"; then
  exit 0
fi

# ─── 15 regex patterns (spec §5.3) ──────────────────────────────────────────
# We run grep -Ei (case-insensitive) for patterns 1-3, 6; plain -E otherwise.
# Matches are exit-on-first-match.
MATCH_ID=""
MATCH_NAME=""

scan() {
  local id="$1"; local name="$2"; local case_flag="$3"; local re="$4"
  # Use -e to disambiguate patterns starting with '-'.
  if [ "$case_flag" = "i" ]; then
    if printf '%s' "$CONTENT" | grep -qiE -e "$re"; then
      MATCH_ID="$id"; MATCH_NAME="$name"; return 0
    fi
  else
    if printf '%s' "$CONTENT" | grep -qE -e "$re"; then
      MATCH_ID="$id"; MATCH_NAME="$name"; return 0
    fi
  fi
  return 1
}

# Ordered scan — stops at first hit.
scan 1  "prompt-injection-ignore-instructions" i 'ignore[[:space:]]+(all[[:space:]]+)?(previous|above)[[:space:]]+(instructions|rules)|disregard[[:space:]]+(all[[:space:]]+|the[[:space:]]+)?system' \
  || scan 2  "prompt-injection-reveal-system" i '(reveal|output|print|show)[[:space:]]+(your|the)[[:space:]]+(system[[:space:]]+prompt|hidden[[:space:]]+instructions|initial[[:space:]]+prompt)' \
  || scan 3  "prompt-injection-role-override" i 'you[[:space:]]+are[[:space:]]+now|from[[:space:]]+now[[:space:]]+on[[:space:]]+you[[:space:]]+are|new[[:space:]]+identity|forget[[:space:]]+you[[:space:]]+are[[:space:]]+claude' \
  || scan 4  "shell-injection-command-sub"     x '\$\([^)]{1,100}\)' \
  || scan 5  "shell-injection-backticks"       x '`[^`]{1,100}`' \
  || scan 6  "sql-injection-keywords"          i 'union[[:space:]]+select|drop[[:space:]]+table|delete[[:space:]]+from[[:space:]]+[a-z_]+[[:space:]]+where[[:space:]]+[0-9]' \
  || scan 7  "sql-injection-or-1-1"            x "('|\")[[:space:]]*[Oo][Rr][[:space:]]*('|\")?[0-9]+('|\")?[[:space:]]*=[[:space:]]*('|\")?[0-9]+" \
  || scan 8  "secret-high-entropy"             x '[A-Z0-9]{32,}' \
  || scan 9  "secret-common-prefix"            x '(sk|pk|api|secret|token)_[a-zA-Z0-9]{16,}' \
  || scan 10 "secret-aws-access-key"           x 'AKIA[0-9A-Z]{16}' \
  || scan 11 "secret-github-token"             x 'ghp_[a-zA-Z0-9]{36}' \
  || scan 12 "secret-slack-token"              x 'xox[pbar]-[0-9]{10,}-[a-zA-Z0-9]{24,}' \
  || scan 13 "secret-private-key-block"        x '-----BEGIN[[:space:]]+(RSA[[:space:]]+|DSA[[:space:]]+|EC[[:space:]]+|OPENSSH[[:space:]]+)?PRIVATE[[:space:]]+KEY-----' \
  || scan 14 "pii-credit-card"                 x '4[0-9]{12}([0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(011|5[0-9]{2})[0-9]{12}' \
  || scan 15 "pii-ssn"                         x '[0-9]{3}-[0-9]{2}-[0-9]{4}' \
  || true

# ─── Invisible Unicode scan (spec §5.3 bottom paragraph) ────────────────────
# U+200B (e2 80 8b), U+200C (e2 80 8c), U+200D (e2 80 8d),
# U+2060 (e2 81 a0), U+FEFF (ef bb bf),
# U+202A..U+202E (e2 80 aa..ae = BIDI overrides)
if [ -z "$MATCH_ID" ]; then
  hex=$(printf '%s' "$CONTENT" | od -An -tx1 2>/dev/null | tr -d ' \n')
  case "$hex" in
    *e2808b*|*e2808c*|*e2808d*|*e281a0*|*efbbbf*|*e280aa*|*e280ab*|*e280ac*|*e280ad*|*e280ae*)
      MATCH_ID="16"; MATCH_NAME="invisible-unicode" ;;
  esac
fi

# ─── Clean → pass ──────────────────────────────────────────────────────────
if [ -z "$MATCH_ID" ]; then
  exit 0
fi

# ─── Violation: log + block ────────────────────────────────────────────────
# Only record file-path category, never raw content (spec §13 PII safety).
CAT="other"
case "$FILE_PATH" in
  */SOUL.md|SOUL.md) CAT="SOUL" ;;
  */user-patterns.md|user-patterns.md) CAT="user-patterns" ;;
  */wiki/*) CAT="wiki" ;;
  */_meta/concepts/*) CAT="concepts" ;;
esac

lib_log_violation "CLASS_D" "critical" "unknown" \
  "pattern=$MATCH_ID name=$MATCH_NAME scope=$CAT tool=$TOOL_NAME" \
  "pre-write-scan"

cat >&1 <<EOF
<system-reminder>
🚫 HARD RULE VIOLATION (CLASS_D) · pre-write-scan blocked ${TOOL_NAME}.

Target: $FILE_PATH (scope: $CAT)
Detection: pattern #$MATCH_ID ($MATCH_NAME)

The ${TOOL_NAME} was blocked. Knowledge files (SOUL / wiki / concepts /
user-patterns) must not contain injection payloads, secrets, or
invisible Unicode. Logged to compliance path as CLASS_D (critical).

Fix:
- If a secret leaked into content: redact and retry
- If a prompt-injection quote: move to a non-knowledge file or sanitize
- If invisible Unicode: strip before writing

Spec: references/hooks-spec.md §5.3
</system-reminder>
EOF

cat >&2 <<EOF
Blocked by life-os-pre-write-scan: pattern #$MATCH_ID ($MATCH_NAME) in $FILE_PATH.
EOF

exit 2
