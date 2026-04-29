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

ACTIVITY_DIR="$HOME/.cache/lifeos"
ACTIVITY_LOG="$ACTIVITY_DIR/hook-activity-$(date +%F).log"
ACTIVITY_MISSING="skipped"
emit_activity() {
  local line="🪝 stop-session-verify: missing_phases=${ACTIVITY_MISSING}"
  mkdir -p "$ACTIVITY_DIR" 2>/dev/null || true
  printf '%s\n' "$line"
  printf '%s %s\n' "$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')" "$line" >> "$ACTIVITY_LOG" 2>/dev/null || true
}
trap emit_activity EXIT

INPUT="$(cat 2>/dev/null || echo "")"
[ -z "$INPUT" ] && exit 0

TRANSCRIPT_PATH="$(lib_json_field "$INPUT" transcript_path)"

# No transcript path → nothing to verify.
if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
  exit 0
fi

# ─── Detect adjourn trigger in transcript tail only (v1.7.1 R9) ─────────
# Root-cause fix: full-text grep treated dev-session spec discussion
# mentions of "adjourn"/"退朝"/"dismiss" as actual archiver runs.
# Now only check the last 50 lines — if user actually said the trigger
# word to end the session, it will be near the tail.
ADJOURN_RE='(退朝|散会|结束|終わり|お疲れ|閣議終了|adjourn|close[[:space:]]session|dismiss)'
TAIL_50="$(tail -n 50 "$TRANSCRIPT_PATH" 2>/dev/null || cat "$TRANSCRIPT_PATH")"
if ! printf '%s' "$TAIL_50" | grep -qiE "$ADJOURN_RE"; then
  ACTIVITY_MISSING="none"
  exit 0
fi

# Deduplicate repeated Stop events for the same session transcript. Claude can
# invoke Stop hooks more than once; use the transcript first line as a stable
# session signature and only re-run after a 5-minute cooldown.
FIRST_TRANSCRIPT_LINE="$(sed -n '1p' "$TRANSCRIPT_PATH" 2>/dev/null || echo "")"
if command -v sha256sum >/dev/null 2>&1; then
  SESSION_HASH="$(printf '%s' "$FIRST_TRANSCRIPT_LINE" | sha256sum | awk '{print $1}')"
elif command -v shasum >/dev/null 2>&1; then
  SESSION_HASH="$(printf '%s' "$FIRST_TRANSCRIPT_LINE" | shasum -a 256 | awk '{print $1}')"
else
  SESSION_HASH="$(printf '%s' "$FIRST_TRANSCRIPT_LINE" | cksum | awk '{print $1 "-" $2}')"
fi
LOCKFILE="$ACTIVITY_DIR/stop-hook-${SESSION_HASH}"
mkdir -p "$ACTIVITY_DIR" 2>/dev/null || true
if [ -f "$LOCKFILE" ]; then
  NOW_TS="$(date +%s 2>/dev/null || echo 0)"
  LOCK_TS="$(date -r "$LOCKFILE" +%s 2>/dev/null || stat -c %Y "$LOCKFILE" 2>/dev/null || echo 0)"
  if [ "$NOW_TS" -gt 0 ] && [ "$LOCK_TS" -gt 0 ] && [ $((NOW_TS - LOCK_TS)) -lt 300 ]; then
    ACTIVITY_MISSING="cooldown"
    exit 0
  fi
fi
: > "$LOCKFILE" 2>/dev/null || true

TRANSCRIPT_TAIL="$(tail -n 800 "$TRANSCRIPT_PATH" 2>/dev/null || cat "$TRANSCRIPT_PATH")"
# Round-4 audit fix: previously this awk set `start` on every match, so
# ARCHIVER_TAIL ended up containing only the LAST `archiver` line —
# throwing away the Phase 1-3 lines that came BEFORE it. That made
# `check_phase` mis-report Phase 1/2/3 as missing in transcripts where
# all 4 phases were actually present (T2 false positive in
# tests/hooks/test_stop_session_verify.sh) and made T3/T4 share T2's
# lockfile via cooldown so they couldn't even run. Now `start` locks at
# the FIRST archiver mention, capturing the full archiver section.
ARCHIVER_TAIL="$(printf '%s\n' "$TRANSCRIPT_TAIL" | awk '
  { lines[NR] = $0 }
  /archiver|ARCHIVER|Archiver/ && start == 0 { start = NR }
  END {
    if (start == 0) {
      start = NR - 199
      if (start < 1) start = 1
    }
    for (i = start; i <= NR; i++) print lines[i]
  }
')"

# ─── Adjourn fired — verify 4 archiver phase markers ──────────────────────
# Each phase should appear at least once. Placeholder detection: "TBD" or
# "{...}" within the phase line.
MISSING=""
PLACEHOLDER=""

check_phase() {
  local n="$1"; local label="$2"
  # Match only the latest archiver tail output, with common separators after N.
  local line
  line="$(printf '%s\n' "$ARCHIVER_TAIL" | grep -iE "[Pp]hase[[:space:]]+$n([[:space:]:,.·—–-]|$)" | tail -1 || echo "")"
  if [ -z "$line" ]; then
    MISSING="${MISSING}${n} "
    return
  fi
  # Placeholder check (v1.7.3.2: also detect unfilled LLM_FILL placeholders)
  case "$line" in
    *TBD*|*tbd*|*"{...}"*|*placeholder*|*"<!-- LLM_FILL"*|*"LLM_FILL:"*)
      PLACEHOLDER="${PLACEHOLDER}${n} "
      return
      ;;
  esac
  # v1.7.3.2: also scan the section body (next ~30 lines after phase header)
  # for unfilled LLM_FILL placeholders. If any are present in this phase's
  # section, mark as placeholder-incomplete.
  local body
  body="$(printf '%s\n' "$ARCHIVER_TAIL" \
    | awk -v phase_re="[Pp]hase[[:space:]]+$n([[:space:]:,.·—–-]|$)" '
        $0 ~ phase_re { matched = NR }
        matched && NR > matched && NR <= matched + 30 { print }
      ')"
  if printf '%s' "$body" | grep -qE 'LLM_FILL:|<!--[[:space:]]*LLM_FILL'; then
    PLACEHOLDER="${PLACEHOLDER}${n} "
  fi
}

check_phase 1 "Archive"
check_phase 2 "Knowledge Extraction"
check_phase 3 "DREAM"
check_phase 4 "Sync"

# ─── Clean → exit silently ─────────────────────────────────────────────────
if [ -z "$MISSING" ] && [ -z "$PLACEHOLDER" ]; then
  ACTIVITY_MISSING="none"
  exit 0
fi

# ─── Violation → log CLASS_C (exit 0 — session already ending) ────────────
DETAIL=""
if [ -n "$MISSING" ]; then
  DETAIL="missing_phases=${MISSING% } "
  ACTIVITY_MISSING="${MISSING% }"
fi
if [ -n "$PLACEHOLDER" ]; then
  DETAIL="${DETAIL}placeholder_phases=${PLACEHOLDER% }"
  if [ -z "$MISSING" ]; then
    ACTIVITY_MISSING="none"
  fi
fi

lib_log_violation "CLASS_C" "high" "archiver" "$DETAIL" "stop-session-verify"

# Emit to stderr — Stop hook stdout isn't guaranteed-injected.
cat >&2 <<EOF
Life OS stop-session-verify: adjourn detected but archiver flow incomplete.
Detail: $DETAIL
Logged to compliance path as CLASS_C. See references/hooks-spec.md §5.4.
EOF

exit 0
