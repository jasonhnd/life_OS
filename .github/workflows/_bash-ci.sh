#!/bin/bash
# .github/workflows/_bash-ci.sh — shared CI body for test.yml jobs.
# ─────────────────────────────────────────────────────────────────────────────
# Runs the same 5 checks across ubuntu / macOS / windows runners. Kept as a
# single sourceable script so test.yml stays minimal and changes to the
# check set don't drift between the fast-path (ubuntu push) and cross-platform
# (PR macOS + windows) jobs.
#
# Exit code: 0 = all checks green, non-zero = at least one check failed.
# ─────────────────────────────────────────────────────────────────────────────

set -u
fail=0

# ─── Check 1 · bash -n syntax check on every tracked .sh ────────────────────
echo ""
echo "── Check 1 · bash -n syntax (all tracked .sh) ──"
while IFS= read -r script; do
  printf '  Checking %-60s' "$script"
  if bash -n "$script" 2>/dev/null; then
    echo "✅"
  else
    echo "❌ SYNTAX ERROR:"
    bash -n "$script"
    fail=1
  fi
done < <(git ls-files '*.sh')

# ─── Check 2 · tests/hooks/*.sh integration suite ───────────────────────────
echo ""
echo "── Check 2 · tests/hooks/*.sh integration suite ──"
chmod +x tests/hooks/*.sh 2>/dev/null || true
for s in tests/hooks/test_*.sh; do
  echo "  ─ Running $s"
  if bash "$s"; then
    :
  else
    echo "  ❌ FAILED: $s"
    fail=1
  fi
done

# ─── Check 3 · spec drift scan (STRICT) ─────────────────────────────────────
echo ""
echo "── Check 3 · scripts/check-spec-drift.sh (STRICT) ──"
chmod +x scripts/check-spec-drift.sh 2>/dev/null || true
if STRICT=1 bash scripts/check-spec-drift.sh; then
  echo "  ✅ no spec drift"
else
  echo "  ❌ spec drift detected"
  fail=1
fi

# ─── Check 4 · pre-prompt-guard regex smoke ─────────────────────────────────
echo ""
echo "── Check 4 · pre-prompt-guard regex smoke ──"
chmod +x scripts/lifeos-pre-prompt-guard.sh 2>/dev/null || true
out=$(echo '{"prompt":"上朝"}' | bash scripts/lifeos-pre-prompt-guard.sh)
if echo "$out" | grep -q "HARD RULE"; then
  echo "  ✅ '上朝' triggers HARD RULE injection"
else
  echo "  ❌ '上朝' did NOT trigger reminder"
  fail=1
fi
long=$(printf '%.0sx' {1..600})
out=$(echo "{\"prompt\":\"$long\"}" | bash scripts/lifeos-pre-prompt-guard.sh)
if echo "$out" | grep -q "HARD RULE"; then
  echo "  ❌ 600-char paste FALSELY triggered reminder"
  fail=1
else
  echo "  ✅ 600-char paste correctly does NOT trigger"
fi

# ─── Result ─────────────────────────────────────────────────────────────────
echo ""
if [ "$fail" -eq 0 ]; then
  echo "═════════════════════════════════════════════════════════════════"
  echo "✅ ALL CI CHECKS PASSED"
  echo "═════════════════════════════════════════════════════════════════"
else
  echo "═════════════════════════════════════════════════════════════════"
  echo "❌ ONE OR MORE CI CHECKS FAILED"
  echo "═════════════════════════════════════════════════════════════════"
fi
exit $fail
