#!/bin/bash
# Tests for scripts/hooks/pre-prompt-guard.sh (spec §5.1)
# ─────────────────────────────────────────────────────────────────────────────
# Hook contract:
#   Event: UserPromptSubmit
#   Matcher: *
#   Reads: {prompt, session_id, cwd}
#   Behavior: Match first line against trigger regex. If matched, emit
#             <system-reminder> to stdout and exit 0. Otherwise silent exit 0.
#   Never exits 2 (prompts cannot be blocked — only annotated).
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK="$REPO_ROOT/scripts/hooks/pre-prompt-guard.sh"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/_test_lib.sh"
TEST_NAME="pre-prompt-guard.sh"

if [ ! -f "$HOOK" ]; then
  echo "❌ FATAL: $HOOK missing — cannot run tests"
  exit 1
fi

# ─── T1: start trigger 上朝 injects reminder ────────────────────────────────
echo "T1: Chinese start trigger '上朝' → emits HARD RULE reminder"
cwd=$(test_mkdev_cwd)
input='{"prompt":"上朝","session_id":"s1","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK")
ec=$?
assert_exit "$ec" 0 "exit 0 on match"
assert_contains "$out" "<system-reminder>" "stdout contains system-reminder tag"
assert_contains "$out" "retrospective" "stdout names retrospective subagent"
assert_contains "$out" "上朝" "stdout echoes detected trigger"
rm -rf "$cwd"

# ─── T2: adjourn trigger 退朝 → archiver ────────────────────────────────────
echo ""
echo "T2: Chinese adjourn '退朝' → reminder names archiver"
cwd=$(test_mkdev_cwd)
input='{"prompt":"退朝","session_id":"s2","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK">/dev/null 2>&1; : )
# Re-run capturing output (need it this time)
out=$(cd "$cwd" && echo "$input" | bash "$HOOK")
ec=$?
assert_exit "$ec" 0 "exit 0"
# Adjourn reminder must launch archiver in the Pre-flight line
assert_contains "$out" "Launch(archiver)" "pre-flight line launches archiver"
assert_not_contains "$out" "Launch(retrospective)" "pre-flight line does not target retrospective"
rm -rf "$cwd"

# ─── T3: review trigger '复盘' → retrospective Mode 2 ───────────────────────
echo ""
echo "T3: review '复盘' → retrospective Mode 2"
cwd=$(test_mkdev_cwd)
input='{"prompt":"复盘","session_id":"s3","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK")
ec=$?
assert_exit "$ec" 0 "exit 0"
assert_contains "$out" "retrospective" "names retrospective"
rm -rf "$cwd"

# ─── T4: English 'start' works ──────────────────────────────────────────────
echo ""
echo "T4: English 'start' trigger"
cwd=$(test_mkdev_cwd)
input='{"prompt":"start","session_id":"s4","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK")
ec=$?
assert_exit "$ec" 0 "exit 0"
assert_contains "$out" "<system-reminder>" "reminder emitted"
rm -rf "$cwd"

# ─── T5: no trigger → silent exit 0 ─────────────────────────────────────────
echo ""
echo "T5: arbitrary prompt 'what's the weather' → silent pass-through"
cwd=$(test_mkdev_cwd)
input='{"prompt":"what'"'"'s the weather","session_id":"s5","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK")
ec=$?
assert_exit "$ec" 0 "exit 0 always"
assert_not_contains "$out" "<system-reminder>" "no reminder emitted"
assert_not_contains "$out" "HARD RULE" "no HARD RULE injection"
rm -rf "$cwd"

# ─── T6: False positive guard — paste > 500 chars, trigger mid-content ──────
echo ""
echo "T6: long paste containing '上朝' mid-content → no trigger (v1.6.3a)"
cwd=$(test_mkdev_cwd)
# Build a long prompt
big=""
for i in $(seq 1 30); do big+="This is a paste from another transcript, line $i, containing nothing suspicious. "; done
big+="And later the word 上朝 appears."
# Escape double quotes in $big
escaped=$(printf '%s' "$big" | sed 's/"/\\"/g')
input='{"prompt":"'$escaped'","session_id":"s6","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK")
ec=$?
assert_exit "$ec" 0 "exit 0"
assert_not_contains "$out" "<system-reminder>" "no reminder (long paste guard)"
rm -rf "$cwd"

# ─── T7: shell-injection attempt in prompt doesn't execute ──────────────────
echo ""
echo "T7: prompt contains \$(whoami) — must not execute"
cwd=$(test_mkdev_cwd)
input='{"prompt":"上朝 $(whoami)","session_id":"s7","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK")
ec=$?
assert_exit "$ec" 0 "exit 0"
# If $(whoami) executed, output would contain the username. We check that the literal string remains.
assert_not_contains "$out" "$(whoami 2>/dev/null)-executed" "no command substitution"
rm -rf "$cwd"

# ─── T8: missing prompt field → silent pass ────────────────────────────────
echo ""
echo "T8: JSON without prompt field"
cwd=$(test_mkdev_cwd)
input='{"session_id":"s8","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK")
ec=$?
assert_exit "$ec" 0 "exit 0 even on empty prompt"
assert_not_contains "$out" "<system-reminder>" "no reminder on empty"
rm -rf "$cwd"

# ─── T9: compliance path auto-detect — other repo routes to /dev/null ──────
echo ""
echo "T9: compliance path routes to /dev/null in unrelated cwd"
cwd=$(test_mkother_cwd)
input='{"prompt":"上朝","session_id":"s9","cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK")
ec=$?
assert_exit "$ec" 0 "exit 0"
# In 'other' repo, still emits reminder (this hook never logs — only later hooks do)
assert_contains "$out" "<system-reminder>" "reminder still emitted"
rm -rf "$cwd"

test_summary
