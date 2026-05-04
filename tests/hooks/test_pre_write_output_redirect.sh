#!/bin/bash
# Tests for scripts/hooks/pre-write-output-redirect.sh (v1.8.2)
# ─────────────────────────────────────────────────────────────────────────────
# Hook contract:
#   Event:   PreToolUse
#   Matcher: Write
#   Behavior:
#     - Write to .pdf/.html/.docx/etc INSIDE vault → exit 2 + redirect hint
#     - Write to .md/.json/.yaml ANYWHERE → exit 0 (text formats pass through)
#     - Write to .pdf already in $HOME/Downloads/* → exit 0 (already going there)
#     - Write to wiki/.attachments/foo.png → exit 0 (in-vault binary allowlist)
#     - Write to _meta/inbox/to-process/foo.pdf → exit 0 (inbox drop-zone)
#     - LIFEOS_OUTPUT_REDIRECT_OFF=1 → exit 0 (bypass)
#     - Empty stdin → exit 0
#     - tool_name != Write (e.g. Edit) → exit 0
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK="$REPO_ROOT/scripts/hooks/pre-write-output-redirect.sh"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/_test_lib.sh"
TEST_NAME="pre-write-output-redirect.sh"

[ ! -f "$HOOK" ] && { echo "FATAL: $HOOK missing"; exit 1; }

# Build a Write tool_input JSON
mkinput() {
  local file_path="$1"
  local content="${2:-some content}"
  # Escape backslashes and quotes (Windows paths have backslashes)
  local escaped_path="${file_path//\\/\\\\}"
  escaped_path="${escaped_path//\"/\\\"}"
  printf '{"tool_name":"Write","tool_input":{"file_path":"%s","content":"%s"}}' \
    "$escaped_path" "$content"
}

mkinput_edit() {
  local file_path="$1"
  printf '{"tool_name":"Edit","tool_input":{"file_path":"%s","old_string":"a","new_string":"b"}}' "$file_path"
}

echo "-- $HOOK --"
echo ""

# T1: Write .md file → exit 0 (text format)
echo "T1: Write .md file → exit 0"
out_t1="$(mkinput "/tmp/lifeos-test/wiki/fintech/test.md" | bash "$HOOK" 2>&1)"
rc_t1=$?
assert_exit "$rc_t1" "0" "markdown file passes"

# T2: Write .json file → exit 0 (data format)
echo ""
echo "T2: Write .json file → exit 0"
rc_t2=0
mkinput "/tmp/lifeos-test/_meta/config.json" | bash "$HOOK" >/dev/null 2>&1 || rc_t2=$?
assert_exit "$rc_t2" "0" "json file passes"

# T3: Write .pdf inside vault → exit 2 (binary, redirect)
echo ""
echo "T3: Write .pdf inside vault → exit 2 (redirect)"
out_t3="$(mkinput "/tmp/lifeos-test/wiki/report.pdf" | bash "$HOOK" 2>&1)"
rc_t3=$?
assert_exit "$rc_t3" "2" "vault .pdf blocks with exit 2"
if echo "$out_t3" | grep -qE "lifeos-export|Downloads|redirect"; then
  TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
  echo "  ✅ stderr suggests Downloads redirect"
else
  TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
  echo "  ❌ stderr did not suggest Downloads redirect"
  echo "       stderr: $out_t3"
fi

# T4: Write .html inside vault → exit 2
echo ""
echo "T4: Write .html inside vault → exit 2"
rc_t4=0
mkinput "/tmp/lifeos-test/_meta/report.html" | bash "$HOOK" >/dev/null 2>&1 || rc_t4=$?
assert_exit "$rc_t4" "2" "vault .html blocks"

# T5: Write .docx inside vault → exit 2
echo ""
echo "T5: Write .docx inside vault → exit 2"
rc_t5=0
mkinput "/tmp/lifeos-test/wiki/report.docx" | bash "$HOOK" >/dev/null 2>&1 || rc_t5=$?
assert_exit "$rc_t5" "2" "vault .docx blocks"

# T6: Write .png to wiki/.attachments/ → exit 0 (allowlist)
echo ""
echo "T6: Write .png to wiki/.attachments/ → exit 0 (in-vault attachment)"
rc_t6=0
mkinput "/tmp/lifeos-test/wiki/.attachments/diagram.png" | bash "$HOOK" >/dev/null 2>&1 || rc_t6=$?
assert_exit "$rc_t6" "0" "wiki/.attachments .png passes"

# T7: Write .pdf to _meta/inbox/to-process/ → exit 0 (inbox drop-zone)
echo ""
echo "T7: Write .pdf to _meta/inbox/to-process/ → exit 0 (inbox)"
rc_t7=0
mkinput "/tmp/lifeos-test/_meta/inbox/to-process/research.pdf" | bash "$HOOK" >/dev/null 2>&1 || rc_t7=$?
assert_exit "$rc_t7" "0" "inbox to-process .pdf passes"

# T8: Write .pdf to ~/Downloads/foo.pdf → exit 0 (already going to Downloads)
echo ""
echo "T8: Write .pdf to ~/Downloads/foo.pdf → exit 0 (already in Downloads)"
rc_t8=0
mkinput "$HOME/Downloads/lifeos-export-2026-05-04/report.pdf" | bash "$HOOK" >/dev/null 2>&1 || rc_t8=$?
assert_exit "$rc_t8" "0" "Downloads .pdf passes"

# T9: LIFEOS_OUTPUT_REDIRECT_OFF=1 + .pdf in vault → exit 0 (bypass)
echo ""
echo "T9: LIFEOS_OUTPUT_REDIRECT_OFF=1 + .pdf in vault → exit 0 (bypass)"
rc_t9=0
mkinput "/tmp/lifeos-test/wiki/forced.pdf" | LIFEOS_OUTPUT_REDIRECT_OFF=1 bash "$HOOK" >/dev/null 2>&1 || rc_t9=$?
assert_exit "$rc_t9" "0" "bypass env var works"

# T10: Empty stdin → exit 0
echo ""
echo "T10: Empty stdin → exit 0"
rc_t10=0
echo "" | bash "$HOOK" >/dev/null 2>&1 || rc_t10=$?
assert_exit "$rc_t10" "0" "empty stdin passes"

# T11: tool_name = Edit → exit 0 (only Write triggered)
echo ""
echo "T11: tool_name = Edit → exit 0 (Edit ignored)"
rc_t11=0
mkinput_edit "/tmp/lifeos-test/wiki/report.pdf" | bash "$HOOK" >/dev/null 2>&1 || rc_t11=$?
assert_exit "$rc_t11" "0" "Edit on .pdf passes (only Write triggers redirect)"

# T12: Uppercase extension .PDF → still exit 2 (case-insensitive ext detection)
echo ""
echo "T12: Uppercase .PDF in vault → exit 2 (case-insensitive)"
rc_t12=0
mkinput "/tmp/lifeos-test/wiki/Report.PDF" | bash "$HOOK" >/dev/null 2>&1 || rc_t12=$?
assert_exit "$rc_t12" "2" "uppercase .PDF detected"

# T13: Multiple binary extensions all caught
echo ""
echo "T13: Sample of binary formats → exit 2"
for ext in zip mp4 jpg svg epub xlsx; do
  rc=0
  mkinput "/tmp/lifeos-test/wiki/sample.$ext" | bash "$HOOK" >/dev/null 2>&1 || rc=$?
  if [ "$rc" = "2" ]; then
    TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
    echo "  ✅ .$ext blocks"
  else
    TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
    echo "  ❌ .$ext expected exit 2, got $rc"
  fi
done

# T14: Source code formats (.sh / .py / .js) → exit 0
echo ""
echo "T14: Source code formats → exit 0"
for ext in sh py js ts go rs; do
  rc=0
  mkinput "/tmp/lifeos-test/scripts/foo.$ext" | bash "$HOOK" >/dev/null 2>&1 || rc=$?
  if [ "$rc" = "0" ]; then
    TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
    echo "  ✅ .$ext passes"
  else
    TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
    echo "  ❌ .$ext expected exit 0, got $rc"
  fi
done

# ─── Summary ────────────────────────────────────────────────────────────────
test_summary
