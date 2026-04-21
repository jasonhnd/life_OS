#!/bin/bash
# Tests for scripts/setup-hooks.sh
# ─────────────────────────────────────────────────────────────────────────────
# The production install path (register_hook in scripts/setup-hooks.sh)
# requires jq per spec §10 pre-flight check — we do NOT relax that.
#
# But the *tests themselves* only need to read JSON fields back out to
# assert on state, which is a read-only operation. To remove the hard
# jq dependency from CI and developer boxes that don't have it, the
# tests use jq when present and fall back to a tiny inline Python
# json.load() helper otherwise.
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SETUP="$REPO_ROOT/scripts/setup-hooks.sh"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/_test_lib.sh"
TEST_NAME="setup-hooks.sh"

[ ! -f "$SETUP" ] && { echo "❌ FATAL: $SETUP missing"; exit 1; }

# ─── Pick a JSON reader: jq if present, else a python3 shim ────────────────
# We need:
#   _read_json <file> <jq-expression>  -> prints the scalar result
# The python shim implements a very small subset that covers this file only:
#   .theme                                    -> string
#   [paths | length] custom aggregates below
# To avoid a parser in bash, we replace the two jq calls with pure-python
# equivalents below, and use jq only when actually installed.

if command -v jq >/dev/null 2>&1; then
  JSON_BACKEND="jq"
else
  # Find a real python interpreter. On Windows Git Bash, `python3` is often
  # a Microsoft Store stub (exits non-zero without running). Probe each
  # candidate with a trivial command and pick the first that works.
  PYTHON_BIN=""
  for candidate in python3 python py "$REPO_ROOT/.venv/Scripts/python.exe" "$REPO_ROOT/.venv/bin/python"; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" -c "import json,sys" >/dev/null 2>&1; then
        PYTHON_BIN="$candidate"
        break
      fi
    fi
  done
  if [ -z "$PYTHON_BIN" ]; then
    echo "❌ FATAL: neither jq nor a working python found — cannot run tests"
    exit 1
  fi
  JSON_BACKEND="python:$PYTHON_BIN"
fi

# count_lifeos_hooks <file> — number of hook entries whose id starts with "life-os-"
count_lifeos_hooks() {
  local file="$1"
  if [ "$JSON_BACKEND" = "jq" ]; then
    jq '[.hooks | to_entries[] | .value[] | select(.id | tostring | startswith("life-os-"))] | length' "$file"
  else
    "${JSON_BACKEND#python:}" - "$file" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
count = 0
for entries in (data.get("hooks") or {}).values():
    for entry in entries:
        hook_id = str(entry.get("id", ""))
        if hook_id.startswith("life-os-"):
            count += 1
print(count)
PY
  fi
}

# count_id <file> <id> — number of hook entries whose id == <id>
count_id() {
  local file="$1"
  local needle="$2"
  if [ "$JSON_BACKEND" = "jq" ]; then
    jq --arg id "$needle" '[.hooks | to_entries[] | .value[] | select(.id == $id)] | length' "$file"
  else
    "${JSON_BACKEND#python:}" - "$file" "$needle" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
needle = sys.argv[2]
count = 0
for entries in (data.get("hooks") or {}).values():
    for entry in entries:
        if entry.get("id") == needle:
            count += 1
print(count)
PY
  fi
}

# read_top_key <file> <key> — prints data[key] as a bare string (jq -r equivalent)
read_top_key() {
  local file="$1"
  local key="$2"
  if [ "$JSON_BACKEND" = "jq" ]; then
    jq -r --arg k "$key" '.[$k]' "$file"
  else
    "${JSON_BACKEND#python:}" - "$file" "$key" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
val = data.get(sys.argv[2])
print("" if val is None else val)
PY
  fi
}

echo "── JSON backend: $JSON_BACKEND ──"

# ─── T1: --uninstall on missing settings.json → no error ───────────────────
echo "T1: --uninstall on missing settings.json"
tmphome=$(mktemp -d)
(HOME="$tmphome" bash "$SETUP" --uninstall) >/dev/null 2>&1
ec=$?
assert_exit "$ec" 0 "graceful no-op"
rm -rf "$tmphome"

# ─── T2: --uninstall removes all life-os-* ids ─────────────────────────────
echo ""
echo "T2: --uninstall removes life-os-* entries"
tmphome=$(mktemp -d)
mkdir -p "$tmphome/.claude"
cat > "$tmphome/.claude/settings.json" <<'EOF'
{
  "hooks": {
    "UserPromptSubmit": [
      {"matcher":"*","hooks":[{"type":"command","command":"bash a.sh"}],"id":"life-os-pre-prompt-guard"},
      {"matcher":"*","hooks":[{"type":"command","command":"bash other.sh"}],"id":"other-hook"}
    ],
    "PreToolUse": [
      {"matcher":"Write","hooks":[{"type":"command","command":"bash b.sh"}],"id":"life-os-pre-write-scan"}
    ]
  },
  "theme": "light"
}
EOF
# The production uninstall path itself still needs jq (spec §10). If jq is
# missing, skip T2 and T3 (which exercise scripts/setup-hooks.sh directly)
# but keep T1 (which doesn't touch jq). T2/T3 are not deleted — they stay
# as jq-only guards on the production script.
if command -v jq >/dev/null 2>&1; then
  (HOME="$tmphome" bash "$SETUP" --uninstall) >/dev/null 2>&1
  count_lifeos=$(count_lifeos_hooks "$tmphome/.claude/settings.json")
  count_other=$(count_id "$tmphome/.claude/settings.json" "other-hook")
  theme=$(read_top_key "$tmphome/.claude/settings.json" "theme")
  assert_eq "$count_lifeos" "0" "all life-os-* removed"
  assert_eq "$count_other" "1" "other-hook preserved"
  assert_eq "$theme" "light" "unrelated keys preserved"
else
  echo "  ⏭️  T2 skipped (jq required to invoke setup-hooks.sh; spec §10)"
fi
rm -rf "$tmphome"

# ─── T3: Pre-flight fails on invalid settings JSON ─────────────────────────
echo ""
echo "T3: invalid settings.json → exit 1"
if command -v jq >/dev/null 2>&1; then
  tmphome=$(mktemp -d)
  mkdir -p "$tmphome/.claude"
  echo "{invalid json" > "$tmphome/.claude/settings.json"
  (HOME="$tmphome" bash "$SETUP") >/dev/null 2>&1
  ec=$?
  assert_exit "$ec" 1 "exits on bad JSON"
  rm -rf "$tmphome"
else
  echo "  ⏭️  T3 skipped (jq required to invoke setup-hooks.sh; spec §10)"
fi

# ─── T4: JSON reader shim works on nested arrays ───────────────────────────
# Exercises the count_lifeos_hooks / count_id / read_top_key helpers
# themselves so the test harness fails loudly if the Python shim breaks.
echo ""
echo "T4: JSON reader shim smoke"
tmpfile=$(mktemp)
cat > "$tmpfile" <<'EOF'
{
  "hooks": {
    "UserPromptSubmit": [
      {"id": "life-os-a"},
      {"id": "life-os-b"},
      {"id": "keeper"}
    ]
  },
  "theme": "dark"
}
EOF
assert_eq "$(count_lifeos_hooks "$tmpfile")" "2" "shim counts life-os-* entries"
assert_eq "$(count_id "$tmpfile" "keeper")" "1" "shim counts exact id match"
assert_eq "$(read_top_key "$tmpfile" "theme")" "dark" "shim reads top-level string"
rm -f "$tmpfile"

test_summary
