#!/bin/bash
# Tests for scripts/hooks/pre-read-allowlist.sh (spec §5.5)
# ─────────────────────────────────────────────────────────────────────────────
# Hook contract:
#   Event: PreToolUse
#   Matcher: Read
#   Reads: {tool_name, tool_input.file_path, cwd}
#   Behavior:
#     - Resolve file_path absolute
#     - Inside cwd OR explicit allowlist → exit 0
#     - Matches denylist → exit 2 + CLASS_E
#     - Otherwise → exit 0 (trust LLM outside denylist)
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK="$REPO_ROOT/scripts/hooks/pre-read-allowlist.sh"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/_test_lib.sh"
TEST_NAME="pre-read-allowlist.sh"

[ ! -f "$HOOK" ] && { echo "❌ FATAL: $HOOK missing"; exit 1; }

# ─── T1: Read inside cwd → pass ────────────────────────────────────────────
echo "T1: Read \$cwd/projects/foo.md → pass"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Read","tool_input":{"file_path":"'$cwd'/projects/foo.md"},"cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "cwd pass-through"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 0 "no violation"
rm -rf "$cwd"

# ─── T2: Read ~/.ssh/id_rsa → exit 2 + CLASS_E ─────────────────────────────
echo ""
echo "T2: Read ~/.ssh/id_rsa → block CLASS_E"
cwd=$(test_mkdev_cwd)
home="$HOME"
input='{"tool_name":"Read","tool_input":{"file_path":"'$home'/.ssh/id_rsa"},"cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 2 "blocked"
vc=$(test_violation_count "$cwd/pro/compliance/violations.md")
assert_eq "$vc" 1 "CLASS_E"
assert_contains "$out" "CLASS_E" "mentions CLASS_E"
rm -rf "$cwd"

# ─── T3: Read ~/.aws/credentials → block ───────────────────────────────────
echo ""
echo "T3: Read ~/.aws/credentials → block"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Read","tool_input":{"file_path":"'$HOME'/.aws/credentials"},"cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 2 "blocked"
rm -rf "$cwd"

# ─── T4: Read /etc/passwd → block ──────────────────────────────────────────
echo ""
echo "T4: Read /etc/passwd → block"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Read","tool_input":{"file_path":"/etc/passwd"},"cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 2 "blocked"
rm -rf "$cwd"

# ─── T5: Read .env OUTSIDE cwd → block (sensitive by convention) ──────────
echo ""
echo "T5: Read /tmp/outside-.env → block (outside cwd, denylist match)"
cwd=$(test_mkdev_cwd); outside=$(mktemp -d)
input='{"tool_name":"Read","tool_input":{"file_path":"'$outside'/.env"},"cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 2 "blocked (outside cwd)"
rm -rf "$cwd" "$outside"

# ─── T6: Read id_rsa anywhere → block ─────────────────────────────────────
echo ""
echo "T6: Read /tmp/id_rsa → block"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Read","tool_input":{"file_path":"/tmp/id_rsa"},"cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 2 "blocked"
rm -rf "$cwd"

# ─── T7: Read outside cwd but not denylist → pass ─────────────────────────
echo ""
echo "T7: Read /tmp/random.txt → pass (neither cwd nor denylist)"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Read","tool_input":{"file_path":"/tmp/random.txt"},"cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "pass (trust outside denylist)"
rm -rf "$cwd"

# ─── T8: relative path resolved via cwd → pass ────────────────────────────
echo ""
echo "T8: relative file_path './README.md' → pass (inside cwd)"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Read","tool_input":{"file_path":"./README.md"},"cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
assert_exit "$ec" 0 "relative pass"
rm -rf "$cwd"

# ─── T9: non-Read tool → always pass ──────────────────────────────────────
echo ""
echo "T9: Bash tool not matched → pass"
cwd=$(test_mkdev_cwd)
input='{"tool_name":"Bash","tool_input":{"command":"cat ~/.ssh/id_rsa"},"cwd":"'$cwd'"}'
out=$(cd "$cwd" && echo "$input" | bash "$HOOK" 2>&1)
ec=$?
# Note: Bash isn't in this hook's matcher; if Claude Code invokes it by error it should be no-op.
# Our hook guards only when tool_name == Read.
assert_exit "$ec" 0 "non-Read pass"
rm -rf "$cwd"

test_summary
