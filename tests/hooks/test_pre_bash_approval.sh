#!/bin/bash
# Tests for scripts/hooks/pre-bash-approval.sh (v1.8.1 zero-python)
# ─────────────────────────────────────────────────────────────────────────────
# Hook contract (v1.8.1):
#   Event:   PreToolUse
#   Matcher: Bash
#   Reads:   {tool_input.command} from stdin
#   Behavior:
#     - Safe command → exit 0 silently
#     - Hardline pattern (e.g. rm -rf /) → exit 2, stderr blocks
#     - Empty input or empty command → exit 0
#     - Malformed JSON → exit 2 fail-CLOSED
#     - LIFEOS_YOLO_MODE=1 → exit 0 even on dangerous command
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
if echo "$out_t2" | grep -qiE "拦截|guard|blocked|root filesystem"; then
  TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
  echo "  PASS stderr mentions block/拦截/guard"
else
  TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
  echo "  FAIL stderr did not mention block reason"
  echo "       stderr: $out_t2"
fi

# T3: empty input → exit 0 silent (no command to check)
echo ""
echo "T3: empty input → exit 0 silent"
rc_t3=0
echo "" | bash "$HOOK" >/dev/null 2>&1 || rc_t3=$?
assert_exit "$rc_t3" "0" "empty input exits 0"

# T4: malformed JSON → exit 2 fail-CLOSED
echo ""
echo "T4: malformed JSON → exit 2 fail-CLOSED"
rc_t4=0
out_t4="$(echo "not json at all" | bash "$HOOK" 2>&1)" || rc_t4=$?
assert_exit "$rc_t4" "2" "malformed json exits 2 (fail-CLOSED)"
if echo "$out_t4" | grep -qiE "无法解析|fail-CLOSED|parse"; then
  TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
  echo "  PASS stderr explains parse failure"
else
  TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
  echo "  FAIL stderr did not explain parse failure"
  echo "       stderr: $out_t4"
fi

# T5: LIFEOS_YOLO_MODE=1 with dangerous command → exit 0 (explicit bypass)
echo ""
echo "T5: LIFEOS_YOLO_MODE=1 with dangerous command → exit 0"
out_t5="$(mkinput 'rm -rf /home/user' | LIFEOS_YOLO_MODE=1 bash "$HOOK" 2>&1)"
rc_t5=$?
assert_exit "$rc_t5" "0" "YOLO_MODE bypasses dangerous command"

# T6: case-insensitive match (uppercase RM -RF) → exit 2
echo ""
echo "T6: case-insensitive RM -RF /etc → exit 2"
out_t6="$(mkinput 'RM -RF /etc/passwd' | bash "$HOOK" 2>&1)"
rc_t6=$?
assert_exit "$rc_t6" "2" "case-insensitive match blocks"

# T7: empty command field (valid JSON, no command) → exit 0
echo ""
echo "T7: empty command field → exit 0 silent"
rc_t7=0
mkinput '' | bash "$HOOK" >/dev/null 2>&1 || rc_t7=$?
assert_exit "$rc_t7" "0" "empty command exits 0"

echo ""
echo "-- ${TEST_NAME}: ${TEST_PASS_COUNT} passed, ${TEST_FAIL_COUNT} failed --"
[ "$TEST_FAIL_COUNT" -eq 0 ] || exit 1
