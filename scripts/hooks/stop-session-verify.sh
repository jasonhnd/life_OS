#!/bin/bash
# Life OS · stop-session-verify.sh (v1.7 Sprint 1)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   Stop
# Matcher: *
# Exit:    0 ALWAYS (session is ending — we cannot block)
# Timeout: 10s (transcript parse may be slow on long sessions)
#
# Purpose
#   On session end, verify: if an adjourn trigger fired during the session,
#   did archiver complete all 4 phases with non-placeholder values?
#   If not → CLASS_C (incomplete flow) or placeholder-specific variant.
#
# Solves
#   Archiver half-completion — Phase 1 archives, something times out,
#   Phase 3 DREAM gets skipped, user thinks session closed cleanly but
#   journal/outbox is inconsistent.
#
# Contract: references/hooks-spec.md §5.4
# ─────────────────────────────────────────────────────────────────────────────

set -u

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$HOOK_DIR/_lib.sh"

INPUT="$(cat 2>/dev/null || echo "")"
[ -z "$INPUT" ] && exit 0

TRANSCRIPT_PATH="$(lib_json_field "$INPUT" transcript_path)"

# No transcript path → nothing to verify.
if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
  exit 0
fi

# ─── Detect adjourn trigger anywhere in transcript ─────────────────────────
# (We use a simpler regex here — trigger search, not first-line detection.
#  Transcripts can be long; we only care IF it fired, not WHERE.)
ADJOURN_RE='(退朝|散会|结束|終わり|お疲れ|閣議終了|adjourn|close[[:space:]]session|dismiss)'
if ! grep -qiE "$ADJOURN_RE" "$TRANSCRIPT_PATH"; then
  exit 0
fi

# ─── Adjourn fired — verify 4 archiver phase markers ──────────────────────
# Each phase should appear at least once. Placeholder detection: "TBD" or
# "{...}" within the phase line.
MISSING=""
PLACEHOLDER=""

check_phase() {
  local n="$1"; local label="$2"
  # Match "Phase N" or "Phase N:" (case-insensitive, possibly prefixed)
  local line
  line="$(grep -iE "[Pp]hase[[:space:]]+$n[[:space:]:,.-]" "$TRANSCRIPT_PATH" | head -1 || echo "")"
  if [ -z "$line" ]; then
    MISSING="${MISSING}${n} "
    return
  fi
  # Placeholder check
  case "$line" in
    *TBD*|*tbd*|*"{...}"*|*placeholder*)
      PLACEHOLDER="${PLACEHOLDER}${n} "
      ;;
  esac
}

check_phase 1 "Archive"
check_phase 2 "Knowledge Extraction"
check_phase 3 "DREAM"
check_phase 4 "Sync"

# ─── Clean → exit silently ─────────────────────────────────────────────────
if [ -z "$MISSING" ] && [ -z "$PLACEHOLDER" ]; then
  exit 0
fi

# ─── Violation → log CLASS_C (exit 0 — session already ending) ────────────
DETAIL=""
if [ -n "$MISSING" ]; then
  DETAIL="missing_phases=${MISSING% } "
fi
if [ -n "$PLACEHOLDER" ]; then
  DETAIL="${DETAIL}placeholder_phases=${PLACEHOLDER% }"
fi

lib_log_violation "CLASS_C" "high" "archiver" "$DETAIL" "stop-session-verify"

# Emit to stderr — Stop hook stdout isn't guaranteed-injected.
cat >&2 <<EOF
Life OS stop-session-verify: adjourn detected but archiver flow incomplete.
Detail: $DETAIL
Logged to compliance path as CLASS_C. See references/hooks-spec.md §5.4.
EOF

exit 0
