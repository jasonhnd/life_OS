#!/bin/bash
# Life OS · pre-read-allowlist.sh (v1.7 Sprint 1)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   PreToolUse
# Matcher: Read
# Exit:    0 = pass | 2 = block (CLASS_E)
# Timeout: 3s (pure path matching — should be sub-millisecond)
#
# Purpose
#   Prevent Read on credential files and other high-sensitivity paths.
#   Even a well-meaning LLM can be prompt-injected into reading ~/.ssh/
#   or /etc/passwd.
#
# Policy
#   - Resolve file_path to absolute (relative → joined with cwd)
#   - Allowlist wins: inside $cwd, Life OS skill dirs → pass
#   - Denylist match → exit 2 + CLASS_E row
#   - Otherwise → pass (we trust LLM outside obvious danger)
#
# Contract: references/hooks-spec.md §5.5
# ─────────────────────────────────────────────────────────────────────────────

set -u

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$HOOK_DIR/_lib.sh"

INPUT="$(cat 2>/dev/null || echo "")"
[ -z "$INPUT" ] && exit 0

TOOL_NAME="$(lib_json_field "$INPUT" tool_name)"
if [ "$TOOL_NAME" != "Read" ]; then
  # Hook declared matcher Read; if invoked on a different tool, be safe.
  exit 0
fi

# Extract file_path (nested field)
FILE_PATH=""
if command -v jq >/dev/null 2>&1; then
  FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")"
fi
if [ -z "$FILE_PATH" ]; then
  FILE_PATH="$(printf '%s' "$INPUT" \
    | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' \
    | head -1 \
    | sed 's/^"file_path"[[:space:]]*:[[:space:]]*"\(.*\)"$/\1/')"
fi

[ -z "$FILE_PATH" ] && exit 0

# ─── Resolve to absolute ───────────────────────────────────────────────────
# Expand ~ manually; realpath may not exist on MSYS / Alpine.
resolved="$FILE_PATH"
case "$resolved" in
  "~/"*) resolved="${HOME}/${resolved#~/}" ;;
  "~") resolved="$HOME" ;;
esac

# Relative path: join with cwd.
case "$resolved" in
  /*|[A-Za-z]:*|[A-Za-z]:/*)
    : # already absolute (Unix / Windows drive letter)
    ;;
  *)
    resolved="$PWD/$resolved"
    ;;
esac

# Normalize .. and . segments (lightweight — relies on sed for speed).
norm="$resolved"
while [ "$norm" != "${norm%/./*}" ]; do
  norm="$(printf '%s' "$norm" | sed 's|/\./|/|g')"
done
# Resolve a/b/.. -> a — one pass; for nested just loop.
prev=""
while [ "$prev" != "$norm" ]; do
  prev="$norm"
  norm="$(printf '%s' "$norm" | sed -E 's|/[^/]+/\.\./|/|g')"
done
resolved="$norm"

# ─── Allowlist (overrides anything — safety valve) ─────────────────────────
ALLOW=0
case "$resolved" in
  "$PWD"/*|"$PWD")                         ALLOW=1 ;;
  "$HOME/.claude/skills/life_OS"/*)        ALLOW=1 ;;
  "$HOME/.claude/scripts"/*)               ALLOW=1 ;;
  "$HOME/.cache/lifeos"/*)                 ALLOW=1 ;;
esac

# ─── Denylist ──────────────────────────────────────────────────────────────
DENY_MATCH=""
check_deny() {
  local pat="$1"; local label="$2"
  case "$resolved" in
    $pat) DENY_MATCH="$label"; return 0 ;;
  esac
  return 1
}

if [ $ALLOW -eq 0 ]; then
  check_deny "$HOME/.ssh/*"          "ssh-keys" \
    || check_deny "$HOME/.aws/*"       "aws-credentials" \
    || check_deny "$HOME/.gcp/*"       "gcp-credentials" \
    || check_deny "$HOME/.azure/*"     "azure-credentials" \
    || check_deny "$HOME/.docker/config.json" "docker-config" \
    || check_deny "$HOME/.kube/config" "kube-config" \
    || check_deny "$HOME/.npmrc"       "npmrc" \
    || check_deny "$HOME/.pypirc"      "pypirc" \
    || check_deny "/etc/passwd"        "etc-passwd" \
    || check_deny "/etc/shadow"        "etc-shadow" \
    || check_deny "/etc/sudoers*"      "etc-sudoers" \
    || true

  # Patterns that can appear anywhere (id_rsa, id_ed25519, .env*):
  if [ -z "$DENY_MATCH" ]; then
    case "$resolved" in
      */id_rsa|*/id_rsa.*)        DENY_MATCH="private-key-rsa" ;;
      */id_ed25519|*/id_ed25519.*) DENY_MATCH="private-key-ed25519" ;;
      */.env|*/.env.*)            DENY_MATCH="env-file" ;;
    esac
  fi
fi

# ─── Clean → pass ─────────────────────────────────────────────────────────
if [ -z "$DENY_MATCH" ]; then
  exit 0
fi

# ─── Violation → log + block ──────────────────────────────────────────────
lib_log_violation "CLASS_E" "high" "unknown" \
  "category=$DENY_MATCH path_seg=$(basename "$resolved")" \
  "pre-read-allowlist"

cat >&1 <<EOF
<system-reminder>
🚫 HARD RULE VIOLATION (CLASS_E) · pre-read-allowlist blocked Read.

Path (category: $DENY_MATCH): $resolved

Reads of credential / secret paths are blocked even when no trigger word
is active. This is a defense-in-depth policy. If you need to read this
file, ask the user to copy the relevant content into a trusted location
inside the repo first.

Logged as CLASS_E (high severity).
Spec: references/hooks-spec.md §5.5
</system-reminder>
EOF

cat >&2 <<EOF
Blocked by life-os-pre-read-allowlist: $DENY_MATCH → $resolved
EOF

exit 2
