#!/bin/bash
# Tests for scripts/hooks/post-response-verify.sh (spec §5.2)
# ─────────────────────────────────────────────────────────────────────────────
# Hook contract:
#   Event: PostToolUse
#   Matcher: Task|Bash|Write|Edit
#   Reads: {tool_name, tool_input, recent_user_message, session_id, cwd}
#   Behavior: If recent_user_message contains a trigger word AND tool_name
#             is NOT Task(expected_subagent), log CLASS_A + exit 2.
#             Otherwise exit 0.
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK="$REPO_ROOT/scripts/hooks/post-response-verify.sh"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/_test_lib.sh"
TEST_NAME="post-response-verify.sh"

if [ ! -f "$HOOK" ]; then
  echo "❌ FATAL: $HOOK missing"
  exit 1
fi

# ─── T1: Start trigger + correct Task(retrospective) → pass ─────────────────
echo "T1: '上朝' followed by Task(retrospective) → exit 0 (compliant)"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Task","tool_input":{"subagent_type":"retrospective","description":"Start Session"},"recent_user_message":"上朝","session_id":"p1","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "compliant launch passes"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 0 "no violation logged"
rm -rf "$cwd"

# ─── T2: Start trigger + wrong tool (Bash) → exit 2 + CLASS_A row ───────────
echo ""
echo "T2: '上朝' followed by Bash reading _meta → exit 2 + CLASS_A"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Bash","tool_input":{"command":"cat _meta/sessions/INDEX.md"},"recent_user_message":"上朝","session_id":"p2","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 2 "exit 2 on violation"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 1 "one violation row"
assert_contains "$out" "CLASS_A" "output mentions CLASS_A"
rm -rf "$cwd"

# ─── T3: Adjourn trigger + wrong subagent (Task retrospective) → CLASS_A ───
echo ""
echo "T3: '退朝' but Task(retrospective) instead of archiver → CLASS_A"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Task","tool_input":{"subagent_type":"retrospective"},"recent_user_message":"退朝","session_id":"p3","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 2 "wrong subagent blocked"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 1 "violation logged"
rm -rf "$cwd"

# ─── T4: Adjourn trigger + correct Task(archiver) → pass ────────────────────
echo ""
echo "T4: '退朝' + Task(archiver) → compliant"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Task","tool_input":{"subagent_type":"archiver"},"recent_user_message":"退朝","session_id":"p4","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "archiver launch OK"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 0 "no violation"
rm -rf "$cwd"

# ─── T5: No trigger word → always pass ──────────────────────────────────────
echo ""
echo "T5: 'show me the weather' + Bash → exit 0 (no trigger = no enforcement)"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Bash","tool_input":{"command":"echo hi"},"recent_user_message":"show me the weather","session_id":"p5","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "no trigger = pass"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 0 "no violation when no trigger"
rm -rf "$cwd"

# ─── T6: Review trigger + Task(retrospective) → pass ────────────────────────
echo ""
echo "T6: '复盘' + Task(retrospective) → compliant"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Task","tool_input":{"subagent_type":"retrospective"},"recent_user_message":"复盘","session_id":"p6","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "review/retrospective OK"
rm -rf "$cwd"

# ─── T7: Shell-injection in recent_user_message doesn't execute ────────────
echo ""
echo "T7: injection attempt in recent_user_message"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Task","tool_input":{"subagent_type":"retrospective"},"recent_user_message":"上朝 $(touch /tmp/lifeos-hook-pwned)","session_id":"p7","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
[ -e /tmp/lifeos-hook-pwned ] && { echo "  ❌ FAIL: injection executed"; exit 1; }
assert_exit "$ec" 0 "correct subagent + injection-safe"
rm -rf "$cwd"

# ─── T8: Missing fields → never crash, exit 0 ───────────────────────────────
echo ""
echo "T8: empty input → exit 0"
out=$(echo "{}" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "empty JSON passes"

test_summary
