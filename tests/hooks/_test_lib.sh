#!/bin/bash
# Life OS Hook Tests · Shared Assertions
# ─────────────────────────────────────────────────────────────────────────────
# Minimal TAP-ish test helpers for bash hook tests. No bats, no npm deps.
# Each test script sources this, runs cases, and exits non-zero on failure.
# ─────────────────────────────────────────────────────────────────────────────

TEST_PASS_COUNT=0
TEST_FAIL_COUNT=0
TEST_NAME="${TEST_NAME:-unknown}"

# assert_eq <actual> <expected> <label>
assert_eq() {
  local actual="$1"
  local expected="$2"
  local label="${3:-assert_eq}"
  if [ "$actual" = "$expected" ]; then
    TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
    echo "  ✅ $label"
  else
    TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
    echo "  ❌ $label"
    echo "       expected: $(printf '%q' "$expected")"
    echo "       actual:   $(printf '%q' "$actual")"
  fi
}

# assert_exit <actual_code> <expected_code> <label>
assert_exit() {
  local actual="$1"
  local expected="$2"
  local label="${3:-assert_exit}"
  if [ "$actual" = "$expected" ]; then
    TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
    echo "  ✅ $label (exit $actual)"
  else
    TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
    echo "  ❌ $label — expected exit $expected, got $actual"
  fi
}

# assert_contains <haystack> <needle> <label>
assert_contains() {
  local haystack="$1"
  local needle="$2"
  local label="${3:-assert_contains}"
  case "$haystack" in
    *"$needle"*)
      TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
      echo "  ✅ $label (contains '$needle')"
      ;;
    *)
      TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
      echo "  ❌ $label — missing '$needle'"
      echo "       haystack snippet: $(printf '%.200s' "$haystack")"
      ;;
  esac
}

# assert_not_contains <haystack> <needle> <label>
assert_not_contains() {
  local haystack="$1"
  local needle="$2"
  local label="${3:-assert_not_contains}"
  case "$haystack" in
    *"$needle"*)
      TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
      echo "  ❌ $label — found forbidden '$needle'"
      ;;
    *)
      TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
      echo "  ✅ $label (does not contain '$needle')"
      ;;
  esac
}

# Make a scratch cwd that looks like a dev repo so compliance logging activates.
test_mkdev_cwd() {
  local dir
  dir=$(mktemp -d 2>/dev/null || mktemp -d -t lifeos-hook-test)
  mkdir -p "$dir/pro/agents" "$dir/pro/compliance"
  : > "$dir/pro/agents/retrospective.md"
  : > "$dir/pro/agents/archiver.md"
  echo "$dir"
}

# Make a scratch cwd that looks like a second-brain.
test_mkuser_cwd() {
  local dir
  dir=$(mktemp -d 2>/dev/null || mktemp -d -t lifeos-hook-test)
  mkdir -p "$dir/_meta/compliance"
  : > "$dir/_meta/config.md"
  echo "$dir"
}

# Make a neutral cwd (should route compliance to /dev/null).
test_mkother_cwd() {
  local dir
  dir=$(mktemp -d 2>/dev/null || mktemp -d -t lifeos-hook-test)
  echo "$dir"
}

# Count violations in a compliance file (or 0 if missing).
test_violation_count() {
  local path="$1"
  if [ ! -f "$path" ]; then
    echo 0
    return
  fi
  # Rows with a timestamp at start
  grep -cE '^\| 2[0-9]{3}-' "$path" || echo 0
}

test_summary() {
  echo ""
  echo "── $TEST_NAME: $TEST_PASS_COUNT passed, $TEST_FAIL_COUNT failed ──"
  if [ "$TEST_FAIL_COUNT" -gt 0 ]; then
    return 1
  fi
  return 0
}
