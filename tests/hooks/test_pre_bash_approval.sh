#!/bin/bash
# Tests for scripts/hooks/pre-bash-approval.sh (Round-3 audit coverage)
# ─────────────────────────────────────────────────────────────────────────────
# Hook contract:
#   Event:   PreToolUse
#   Matcher: Bash
#   Reads:   {tool_input.command} from stdin
#   Behavior:
#     - Safe command → exit 0 silently
#     - Hardline pattern (e.g. rm -rf /) → exit 2, stderr blocks
#     - approval.py crashes (bridge error) → exit 2 fail-CLOSED
#     - Bridge JSON parse fails → exit 2 fail-CLOSED
#     - approval.py source not found → exit 2 fail-CLOSED (Round-3 fix)
#     - LIFEOS_YOLO_MODE=1 → exit 0 even if approval.py missing
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK="$REPO_ROOT/scripts/hooks/pre-bash-approval.sh"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/_test_lib.sh"
TEST_NAME="pre-bash-approval.sh"

[ ! -f "$HOOK" ] && { echo "FATAL: $HOOK missing"; exit 1; }

# Build a Bash tool_input JSON
mkinput() {
  local cmd="$1"
  local escaped="${cmd//\"/\\\"}"
  printf '{"tool_name":"Bash","tool_input":{"command":"%s"}}' "$escaped"
}

echo "-- $HOOK --"
echo ""

# T1: safe command (echo) → exit 0
echo "T1: safe command 'echo hello' → exit 0"
out_t1="$(mkinput 'echo hello' | bash "$HOOK" 2>&1)"
rc_t1=$?
assert_exit "$rc_t1" "0" "safe command exits 0"

# T2: hardline command (rm -rf /) → exit 2 with reason
echo ""
echo "T2: hardline 'rm -rf /' → exit 2 (block)"
out_t2="$(mkinput 'rm -rf /' | bash "$HOOK" 2>&1)"
rc_t2=$?
assert_exit "$rc_t2" "2" "hardline blocks with exit 2"
if echo "$out_t2" | grep -qiE "blocked|hardline|guard"; then
  TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
  echo "  PASS stderr mentions block/hardline/guard"
else
  TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
  echo "  FAIL stderr did not mention block/guard reason"
  echo "       stderr: $out_t2"
fi

# T3: empty input → exit 0 silent (no command to check)
echo ""
echo "T3: empty input → exit 0 silent"
rc_t3=0
echo "" | bash "$HOOK" >/dev/null 2>&1 || rc_t3=$?
assert_exit "$rc_t3" "0" "empty input exits 0"

# T4: malformed JSON → exit 0 (no command extracted, pass through)
echo ""
echo "T4: malformed JSON → exit 0"
rc_t4=0
echo "not json at all" | bash "$HOOK" >/dev/null 2>&1 || rc_t4=$?
assert_exit "$rc_t4" "0" "malformed json exits 0 (silent passthrough)"

# T5: approval.py source missing → exit 2 fail-CLOSED (Round-3 audit fix)
echo ""
echo "T5: approval.py source missing → exit 2 fail-CLOSED"
TMPDIR_T5="$(mktemp -d 2>/dev/null || mktemp -d -t 'lifeos-t5')"
mkdir -p "$TMPDIR_T5/empty-home" "$TMPDIR_T5/fake/scripts/hooks"
cp "$HOOK" "$TMPDIR_T5/fake/scripts/hooks/pre-bash-approval.sh"
chmod +x "$TMPDIR_T5/fake/scripts/hooks/pre-bash-approval.sh"
out_t5="$(printf '%s' "$(mkinput 'echo hello')" | HOME="$TMPDIR_T5/empty-home" bash "$TMPDIR_T5/fake/scripts/hooks/pre-bash-approval.sh" 2>&1)"
rc_t5=$?
assert_exit "$rc_t5" "2" "missing approval.py exits 2 (fail-CLOSED)"
if echo "$out_t5" | grep -qE "approval.py|找不到|not found|fail-CLOSED"; then
  TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
  echo "  PASS stderr explains approval.py is missing"
else
  TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
  echo "  FAIL stderr did not explain missing approval.py"
  echo "       stderr: $out_t5"
fi
rm -rf "$TMPDIR_T5" 2>/dev/null || true

# T6: LIFEOS_YOLO_MODE=1 with missing source → exit 0 (explicit bypass)
echo ""
echo "T6: LIFEOS_YOLO_MODE=1 with missing source → exit 0"
TMPDIR_T6="$(mktemp -d 2>/dev/null || mktemp -d -t 'lifeos-t6')"
mkdir -p "$TMPDIR_T6/empty-home" "$TMPDIR_T6/fake/scripts/hooks"
cp "$HOOK" "$TMPDIR_T6/fake/scripts/hooks/pre-bash-approval.sh"
chmod +x "$TMPDIR_T6/fake/scripts/hooks/pre-bash-approval.sh"
out_t6="$(printf '%s' "$(mkinput 'echo hello')" | HOME="$TMPDIR_T6/empty-home" LIFEOS_YOLO_MODE=1 bash "$TMPDIR_T6/fake/scripts/hooks/pre-bash-approval.sh" 2>&1)"
rc_t6=$?
assert_exit "$rc_t6" "0" "YOLO_MODE bypass exits 0"
if echo "$out_t6" | grep -qE "YOLO|skipping guard"; then
  TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
  echo "  PASS stderr acknowledges YOLO bypass"
else
  TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
  echo "  FAIL stderr did not acknowledge YOLO bypass"
  echo "       stderr: $out_t6"
fi
rm -rf "$TMPDIR_T6" 2>/dev/null || true

echo ""
echo "-- ${TEST_NAME}: ${TEST_PASS_COUNT} passed, ${TEST_FAIL_COUNT} failed --"
[ "$TEST_FAIL_COUNT" -eq 0 ] || exit 1
