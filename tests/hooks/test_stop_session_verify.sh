#!/bin/bash
# Tests for scripts/hooks/stop-session-verify.sh (spec §5.4)
# ─────────────────────────────────────────────────────────────────────────────
# Hook contract:
#   Event: Stop
#   Matcher: *
#   Reads: {session_id, final_state, transcript_path}
#   Behavior:
#     - Grep transcript for adjourn trigger
#     - If not found → exit 0 silently
#     - If found → check 4 archiver phase markers in transcript
#                  missing/TBD → log CLASS_C
#     - ALWAYS exit 0 (session is already ending; we log only)
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK="$REPO_ROOT/scripts/hooks/stop-session-verify.sh"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/_test_lib.sh"
TEST_NAME="stop-session-verify.sh"

[ ! -f "$HOOK" ] && { echo "❌ FATAL: $HOOK missing"; exit 1; }

# Round-4 audit fix: stop-session-verify.sh has a 5-minute cooldown
# lockfile keyed by sha of first transcript line. Test cases share first
# lines (User: 退朝 / User: adjourn) and would otherwise hit cooldown if
# the test was run twice within 5 min. Clean any stale lockfiles before
# the suite runs so cases run isolated. Note: production hook usage is
# unaffected — these lockfiles only exist after this hook runs.
rm -f "$HOME/.cache/lifeos/stop-hook-"* 2>/dev/null || true

# Build a transcript file with N phases present (1-4 means "include Phase 1..N").
mktranscript() {
  local dir="$1"; local phases="$2"; local trigger="${3:-}"
  local path="$dir/transcript.md"
  {
    [ -n "$trigger" ] && echo "User: $trigger"
    echo "User: do some work"
    echo "Assistant: did the work"
    for n in $(seq 1 "$phases"); do
      case "$n" in
        1) echo "archiver Phase 1: Archive — decisions moved to outbox" ;;
        2) echo "archiver Phase 2: Knowledge Extraction — 3 wiki entries staged" ;;
        3) echo "archiver Phase 3: DREAM — N1/N2/N3/REM cycles complete" ;;
        4) echo "archiver Phase 4: Sync — git push + Notion sync done" ;;
      esac
    done
  } > "$path"
  echo "$path"
}

# ─── T1: No adjourn trigger in transcript → silent exit 0 ──────────────────
echo "T1: transcript without adjourn trigger → silent pass"
cwd=$(test_mkdev_cwd)
transcript=$(mktranscript "$cwd" 0 "")
input='{"session_id":"e1","final_state":"normal","transcript_path":"'$transcript'"}'
rm -f "$HOME/.cache/lifeos/stop-hook-"* 2>/dev/null || true
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "silent pass"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 0 "no violation"
rm -rf "$cwd"

# ─── T2: Adjourn present + all 4 phases complete → exit 0 no violation ────
echo ""
echo "T2: adjourn + 4 phases present → compliant"
cwd=$(test_mkdev_cwd)
transcript=$(mktranscript "$cwd" 4 "退朝")
input='{"session_id":"e2","final_state":"normal","transcript_path":"'$transcript'"}'
rm -f "$HOME/.cache/lifeos/stop-hook-"* 2>/dev/null || true
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "compliant"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 0 "no violation"
rm -rf "$cwd"

# ─── T3: Adjourn + only 2 phases → CLASS_C logged, exit 0 ─────────────────
echo ""
echo "T3: adjourn + only Phase 1+2 → CLASS_C (archiver bailed early)"
cwd=$(test_mkdev_cwd)
transcript=$(mktranscript "$cwd" 2 "退朝")
input='{"session_id":"e3","final_state":"normal","transcript_path":"'$transcript'"}'
rm -f "$HOME/.cache/lifeos/stop-hook-"* 2>/dev/null || true
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "always exit 0 (session ending)"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 1 "CLASS_C logged"
rm -rf "$cwd"

# ─── T4: Adjourn + phase with TBD placeholder → CLASS_C ───────────────────
echo ""
echo "T4: Phase 4 contains 'TBD' → CLASS_D-ish (placeholder) → CLASS_C"
cwd=$(test_mkdev_cwd)
cat > "$cwd/transcript.md" <<'EOF'
User: 退朝
Assistant: running archiver
archiver Phase 1: Archive — done
archiver Phase 2: Knowledge Extraction — done
archiver Phase 3: DREAM — done
archiver Phase 4: Sync — TBD
EOF
input='{"session_id":"e4","final_state":"normal","transcript_path":"'$cwd'/transcript.md"}'
rm -f "$HOME/.cache/lifeos/stop-hook-"* 2>/dev/null || true
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "exit 0"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 1 "CLASS_C (placeholder) logged"
rm -rf "$cwd"

# ─── T5: Missing transcript_path → exit 0 silently ─────────────────────────
echo ""
echo "T5: missing transcript file → exit 0"
cwd=$(test_mkdev_cwd)
input='{"session_id":"e5","final_state":"normal","transcript_path":"'$cwd'/does-not-exist.md"}'
rm -f "$HOME/.cache/lifeos/stop-hook-"* 2>/dev/null || true
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "exit 0 on missing transcript"
rm -rf "$cwd"

# ─── T6: English adjourn trigger 'adjourn' also detected ───────────────────
echo ""
echo "T6: English 'adjourn' in transcript → detected"
cwd=$(test_mkdev_cwd)
transcript=$(mktranscript "$cwd" 2 "adjourn")
input='{"session_id":"e6","final_state":"normal","transcript_path":"'$transcript'"}'
rm -f "$HOME/.cache/lifeos/stop-hook-"* 2>/dev/null || true
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "exit 0"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 1 "violation (incomplete phases)"
rm -rf "$cwd"

test_summary
