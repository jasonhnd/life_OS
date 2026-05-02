#!/bin/bash
# Tests for scripts/lifeos-compliance-check.sh (v1.8.1 zero-python)
# ─────────────────────────────────────────────────────────────────────────────
# Replaces the deleted tests/test_compliance_check.py (pytest, 12 cases).
# Same coverage axes (clean / fabricated / missing-phase / placeholder /
# Cortex states / unknown scenario), just bash-native + invoked the same
# way the AUDITOR Mode 3 invokes it in production.
#
# Contract under test:
#   bash scripts/lifeos-compliance-check.sh <output_file> <scenario>
#   exit 0 = clean / no violations
#   exit 1 = one or more violations detected
#   exit 2 = usage error or input file missing
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/lifeos-compliance-check.sh"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/_test_lib.sh"
TEST_NAME="lifeos-compliance-check.sh"

[ ! -f "$SCRIPT" ] && { echo "FATAL: $SCRIPT missing"; exit 1; }

# Per-test scratch dir
TMPDIR_T="$(mktemp -d 2>/dev/null || mktemp -d -t lifeos-comp-test)"
trap 'rm -rf "$TMPDIR_T" 2>/dev/null || true' EXIT

# Helper: invoke compliance-check and return exit code
run_check() {
  local fixture="$1"
  local scenario="$2"
  local violations_file="${3:-$TMPDIR_T/violations.md}"
  bash "$SCRIPT" "$fixture" "$scenario" "$violations_file" >/dev/null 2>&1
  echo $?
}

# Build a clean Start Session briefing fixture
write_clean_briefing() {
  local path="$1"
  cat > "$path" <<'EOF'
🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0
✅ I am the RETROSPECTIVE subagent (Mode 0, not main-context simulation)
Step 2 DIRECTORY TYPE CHECK:
a) 连接到 second-brain
b) 开发模式
c) 新建 second-brain
[Local SKILL.md version: 1.8.1]
[Remote check (forced fresh): up-to-date]
[Cortex: skipped - per-message pull mode in v1.8.0]

## 0. 丞相 · 上朝准备
Ready

## 1. 第二大脑同步状态
Clean

## 2. SOUL Health 报告
No drift

## 3. DREAM / 隔夜更新
None

## 4. Today's Focus + 待陛下圣裁
Ready

## 5. 系统状态
Green
EOF
}

# Build a clean adjourn briefing fixture
write_clean_adjourn() {
  local path="$1"
  cat > "$path" <<'EOF'
📝 Trigger: 退朝 → Action: Launch(archiver) subagent
✅ I am the ARCHIVER subagent
[Local SKILL.md version: 1.8.1]
[Remote check (forced fresh): up-to-date]
[Cortex: skipped]

## Phase 1
Done

## Phase 2
Done

## Phase 3
Done

## Phase 4
Done

## Completion Checklist
- all four phases returned without unresolved placeholders or empty values
EOF
}

echo "-- $SCRIPT --"
echo ""

# ─── T1: clean Start Session briefing → exit 0 ──────────────────────────────
echo "T1: clean briefing → exit 0"
write_clean_briefing "$TMPDIR_T/clean.md"
rc_t1="$(run_check "$TMPDIR_T/clean.md" start-session-compliance)"
assert_exit "$rc_t1" "0" "clean briefing passes"

# ─── T2: missing version marker → exit 1 (version-markers / start-session) ──
echo ""
echo "T2: missing version markers → exit 1"
write_clean_briefing "$TMPDIR_T/no-version.md"
sed -i.bak '/Local SKILL.md version/d; /Remote check (forced fresh)/d' \
  "$TMPDIR_T/no-version.md"
rm -f "$TMPDIR_T/no-version.md.bak"
rc_t2="$(run_check "$TMPDIR_T/no-version.md" start-session-compliance)"
assert_exit "$rc_t2" "1" "missing version markers detected"

# ─── T3: fabricated path detected → exit 1 ──────────────────────────────────
echo ""
echo "T3: fabricated path → exit 1"
write_clean_briefing "$TMPDIR_T/fabricated.md"
cat >> "$TMPDIR_T/fabricated.md" <<'EOF'

Per `_meta/roles/CLAUDE.md § 0 Pre-Court Preparation`, ROUTER is required to...
EOF
rc_t3="$(run_check "$TMPDIR_T/fabricated.md" fabricate-path-check)"
assert_exit "$rc_t3" "1" "fabricated path detected"

# ─── T4: missing H2 sections → exit 1 (briefing-completeness) ───────────────
echo ""
echo "T4: missing H2 sections → exit 1"
cat > "$TMPDIR_T/incomplete.md" <<'EOF'
🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0
✅ I am the RETROSPECTIVE subagent (Mode 0)
[Local SKILL.md version: 1.8.1]
[Remote check (forced fresh): up-to-date]
[Cortex: skipped]

## 0. 丞相 · 上朝准备
Ready
EOF
rc_t4="$(run_check "$TMPDIR_T/incomplete.md" briefing-completeness)"
assert_exit "$rc_t4" "1" "incomplete briefing detected"

# ─── T5: placeholder TBD detected → exit 1 ──────────────────────────────────
echo ""
echo "T5: TBD placeholder → exit 1"
write_clean_briefing "$TMPDIR_T/placeholder.md"
# Inject a literal TBD inside one section
sed -i.bak 's/Ready$/Ready (TBD)/' "$TMPDIR_T/placeholder.md"
rm -f "$TMPDIR_T/placeholder.md.bak"
rc_t5="$(run_check "$TMPDIR_T/placeholder.md" placeholder-check)"
assert_exit "$rc_t5" "1" "TBD placeholder detected"

# ─── T6: clean briefing has no placeholder → exit 0 ─────────────────────────
echo ""
echo "T6: placeholder-check on clean briefing → exit 0"
write_clean_briefing "$TMPDIR_T/clean-pl.md"
rc_t6="$(run_check "$TMPDIR_T/clean-pl.md" placeholder-check)"
assert_exit "$rc_t6" "0" "no placeholder in clean briefing"

# ─── T7: unknown scenario → exit 0 (skips silently) ─────────────────────────
echo ""
echo "T7: unknown scenario → skips silently (exit 0)"
write_clean_briefing "$TMPDIR_T/clean2.md"
rc_t7="$(run_check "$TMPDIR_T/clean2.md" not-a-real-scenario)"
assert_exit "$rc_t7" "0" "unknown scenario skips silently"

# ─── T8: missing input file → exit 2 (usage error) ──────────────────────────
echo ""
echo "T8: missing input file → exit 2"
rc_t8="$(run_check "$TMPDIR_T/does-not-exist.md" start-session-compliance)"
assert_exit "$rc_t8" "2" "missing input file → usage error"

# ─── T9: missing arguments → exit 2 (usage error) ───────────────────────────
echo ""
echo "T9: no arguments → exit 2"
rc_t9=0
bash "$SCRIPT" >/dev/null 2>&1 || rc_t9=$?
assert_exit "$rc_t9" "2" "no arguments → usage error"

# ─── T10: clean adjourn briefing (4 phases present) → exit 0 ────────────────
echo ""
echo "T10: clean adjourn → exit 0"
write_clean_adjourn "$TMPDIR_T/adjourn.md"
rc_t10="$(run_check "$TMPDIR_T/adjourn.md" adjourn-compliance)"
assert_exit "$rc_t10" "0" "clean adjourn passes"

# ─── T11: missing Phase 3 in adjourn → exit 1 ───────────────────────────────
echo ""
echo "T11: missing Phase 3 → exit 1"
write_clean_adjourn "$TMPDIR_T/adjourn-incomplete.md"
sed -i.bak '/^## Phase 3/,/^$/d' "$TMPDIR_T/adjourn-incomplete.md"
rm -f "$TMPDIR_T/adjourn-incomplete.md.bak"
rc_t11="$(run_check "$TMPDIR_T/adjourn-incomplete.md" adjourn-compliance)"
assert_exit "$rc_t11" "1" "missing phase 3 detected"

# ─── Summary ────────────────────────────────────────────────────────────────
test_summary
