#!/bin/bash
# Life OS · Tool Eval Runner (R4.5)
#
# Machine-verifiable runner for tool-*.md scenarios under evals/scenarios/.
# Unlike run-eval.sh (which exercises claude -p on full routing scenarios),
# this runner invokes the underlying Python tools directly and asserts on
# exit code, stdout substrings, and created files.
#
# Each scenario's frontmatter drives the run:
#   setup_script          multiline bash; `{tmp_dir}` substituted with mktemp
#   invocation            shell command; `{tmp_dir}` substituted
#   expected_exit_code    integer
#   expected_stdout_contains    list of substrings (checked via grep -F)
#   expected_stderr_contains    list of substrings (optional)
#   expected_files        list of paths (after substitution) that must exist
#   expected_files_glob   list of glob patterns that must match >=1 file
#   env                   optional map of env vars to set per scenario
#   skip_if_missing_python_module  list of import-names; if any missing => SKIP
#   skip_if_missing_binary         list of PATH names; if any missing => SKIP
#
# Exit codes:
#   0   all scenarios passed or gracefully skipped
#   1   >=1 FAIL
#   2   harness-level error (python/yaml unavailable, etc.)

set -u

# Force utf-8 for every python subprocess to dodge cp932 on Windows.
export PYTHONIOENCODING=utf-8

EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$EVAL_DIR/.." && pwd)"
SCENARIOS_DIR="$EVAL_DIR/scenarios"

PASS=0
FAIL=0
SKIP=0
RESULTS=()

# ─── Resolve Python ─────────────────────────────────────────────────────────
# Prefer the repo-local venv (Windows / .venv layout); fall back to python3 /
# python on PATH. If none works, exit 2 (harness cannot run).

PYTHON=""
for candidate in \
    "$REPO_ROOT/.venv/Scripts/python.exe" \
    "$REPO_ROOT/.venv/Scripts/python" \
    "$REPO_ROOT/.venv/bin/python3" \
    "$REPO_ROOT/.venv/bin/python" \
    "python3" \
    "python"; do
    if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c "import yaml" >/dev/null 2>&1; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ No Python with PyYAML available. Install via: uv sync --extra dev"
    echo "   (tried .venv/Scripts/python, .venv/bin/python3, python3, python)"
    exit 2
fi

echo "=== Life OS Tool Eval Runner (R4.5) ==="
echo "Python: $PYTHON"
echo "Scenarios dir: $SCENARIOS_DIR"
echo ""

# ─── Frontmatter parser ─────────────────────────────────────────────────────
# Splits on the first TWO lines that are literally `---` (line-anchored), so
# heredoc blocks inside the YAML body (which contain their own `---`) don't
# accidentally terminate the frontmatter. Outputs shell-assignable KEY=VALUE
# lines with list/string values base64-encoded.

parse_frontmatter() {
    local file="$1"
    SCENARIO_FILE="$file" "$PYTHON" - <<'PYEOF'
import base64
import json
import os
import re
import sys
import yaml

path = os.environ["SCENARIO_FILE"]
try:
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
except OSError as exc:
    print(f"__HARNESS_ERROR__={exc}")
    sys.exit(0)

# Front-matter must begin with `---\n` and end with the first subsequent
# `\n---\n` (the marker on its own line). This avoids swallowing embedded
# `---` lines that appear inside YAML block-scalars (e.g. heredoc bodies).
if not content.startswith("---\n") and not content.startswith("---\r\n"):
    print("__NO_FRONTMATTER__=1")
    sys.exit(0)

m = re.search(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", content, re.DOTALL)
if not m:
    print("__NO_FRONTMATTER__=1")
    sys.exit(0)

try:
    fm = yaml.safe_load(m.group(1)) or {}
except yaml.YAMLError as exc:
    print(f"__HARNESS_ERROR__=yaml parse: {exc}")
    sys.exit(0)

if not isinstance(fm, dict):
    print("__NO_MACHINE_FIELDS__=1")
    sys.exit(0)

if "expected_exit_code" not in fm:
    print("__NO_MACHINE_FIELDS__=1")
    sys.exit(0)


def b64(s):
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


setup_script = fm.get("setup_script", "") or ""
invocation = fm.get("invocation", "") or ""
print(f"SETUP_B64={b64(setup_script)}")
print(f"INVOCATION_B64={b64(invocation)}")
print(f"EXPECTED_EXIT_CODE={int(fm.get('expected_exit_code', 0))}")
print(f"STDOUT_CONTAINS_JSON={b64(json.dumps(fm.get('expected_stdout_contains', []) or []))}")
print(f"STDERR_CONTAINS_JSON={b64(json.dumps(fm.get('expected_stderr_contains', []) or []))}")
print(f"EXPECTED_FILES_JSON={b64(json.dumps(fm.get('expected_files', []) or []))}")
print(f"EXPECTED_FILES_GLOB_JSON={b64(json.dumps(fm.get('expected_files_glob', []) or []))}")
print(f"SKIP_MODULES_JSON={b64(json.dumps(fm.get('skip_if_missing_python_module', []) or []))}")
print(f"SKIP_BINARIES_JSON={b64(json.dumps(fm.get('skip_if_missing_binary', []) or []))}")
print(f"ENV_JSON={b64(json.dumps(fm.get('env', {}) or {}))}")
PYEOF
}

# ─── Helpers ────────────────────────────────────────────────────────────────

b64decode() {
    echo "$1" | "$PYTHON" -c "import sys, base64; sys.stdout.write(base64.b64decode(sys.stdin.read()).decode('utf-8'))"
}

json_to_lines() {
    # Write bytes directly so Python's text-mode CRLF translation on Windows
    # doesn't bake \r into each needle (would break `grep -F` substring
    # matches on the captured stdout/stderr files).
    echo "$1" | "$PYTHON" -c "
import sys, json
s = sys.stdin.read().strip()
items = json.loads(s) if s else []
out = ''.join(f'{x}\n' for x in items)
sys.stdout.buffer.write(out.encode('utf-8'))
"
}

substitute_tmpdir() {
    local s="$1"
    TMP_DIR_FOR_SUBST="$2" "$PYTHON" -c "
import sys, os
sys.stdout.write(sys.stdin.read().replace('{tmp_dir}', os.environ['TMP_DIR_FOR_SUBST']))
" <<< "$s"
}

rewrite_python3() {
    local text="$1"
    RESOLVED_PYTHON="$PYTHON" "$PYTHON" -c "
import sys, os, re
py = os.environ['RESOLVED_PYTHON']
text = sys.stdin.read()
text = re.sub(r'(^|[\s;&|])python3(\s)', lambda m: f\"{m.group(1)}{py}{m.group(2)}\", text)
sys.stdout.write(text)
" <<< "$text"
}

check_python_module() {
    "$PYTHON" -c "import $1" >/dev/null 2>&1
}

# ─── Per-scenario runner ────────────────────────────────────────────────────

run_scenario() {
    local scenario_file="$1"
    local name
    name="$(basename "$scenario_file" .md)"

    echo "🔧 $name"

    local fm_out
    fm_out="$(parse_frontmatter "$scenario_file")"

    if echo "$fm_out" | grep -q "^__HARNESS_ERROR__="; then
        local err
        err=$(echo "$fm_out" | grep "^__HARNESS_ERROR__=" | sed 's/^__HARNESS_ERROR__=//')
        echo "   ⏭  SKIP (harness error: $err)"
        RESULTS+=("SKIP $name (harness: $err)")
        SKIP=$((SKIP + 1))
        return
    fi

    if echo "$fm_out" | grep -q "^__NO_FRONTMATTER__=1"; then
        echo "   ⏭  SKIP (no YAML frontmatter)"
        RESULTS+=("SKIP $name (no frontmatter)")
        SKIP=$((SKIP + 1))
        return
    fi

    if echo "$fm_out" | grep -q "^__NO_MACHINE_FIELDS__=1"; then
        echo "   ⏭  SKIP (no machine-eval fields — expected_exit_code missing)"
        RESULTS+=("SKIP $name (no machine fields)")
        SKIP=$((SKIP + 1))
        return
    fi

    local SETUP_B64="" INVOCATION_B64="" EXPECTED_EXIT_CODE=0
    local STDOUT_CONTAINS_JSON="" STDERR_CONTAINS_JSON=""
    local EXPECTED_FILES_JSON="" EXPECTED_FILES_GLOB_JSON=""
    local SKIP_MODULES_JSON="" SKIP_BINARIES_JSON="" ENV_JSON=""
    eval "$fm_out"

    local skip_reason=""
    while IFS= read -r mod; do
        [ -z "$mod" ] && continue
        if ! check_python_module "$mod"; then
            skip_reason="missing python module: $mod"
            break
        fi
    done < <(json_to_lines "$(b64decode "$SKIP_MODULES_JSON")")

    if [ -n "$skip_reason" ]; then
        echo "   ⏭  SKIP ($skip_reason)"
        RESULTS+=("SKIP $name ($skip_reason)")
        SKIP=$((SKIP + 1))
        return
    fi

    while IFS= read -r bin; do
        [ -z "$bin" ] && continue
        if ! command -v "$bin" >/dev/null 2>&1; then
            skip_reason="missing binary: $bin"
            break
        fi
    done < <(json_to_lines "$(b64decode "$SKIP_BINARIES_JSON")")

    if [ -n "$skip_reason" ]; then
        echo "   ⏭  SKIP ($skip_reason)"
        RESULTS+=("SKIP $name ($skip_reason)")
        SKIP=$((SKIP + 1))
        return
    fi

    local TMP_DIR
    TMP_DIR="$(mktemp -d -t lifeos-tooleval-XXXXXX 2>/dev/null || mktemp -d)"

    local SETUP_SCRIPT INVOCATION INVOCATION_EXEC
    SETUP_SCRIPT="$(substitute_tmpdir "$(b64decode "$SETUP_B64")" "$TMP_DIR")"
    INVOCATION="$(substitute_tmpdir "$(b64decode "$INVOCATION_B64")" "$TMP_DIR")"
    INVOCATION_EXEC="$(rewrite_python3 "$INVOCATION")"

    local ENV_EXPORTS=""
    ENV_EXPORTS="$(ENV_JSON_B64="$ENV_JSON" "$PYTHON" -c "
import os, sys, base64, json, shlex
data = json.loads(base64.b64decode(os.environ['ENV_JSON_B64']).decode('utf-8') or '{}')
for k, v in data.items():
    print(f'export {k}={shlex.quote(str(v))}')
")"

    # Assemble setup block. Empty ENV_EXPORTS / SETUP_SCRIPT must not inject
    # spurious semicolons.
    local setup_block="set -e"
    if [ -n "$ENV_EXPORTS" ]; then
        setup_block+=$'\n'"$ENV_EXPORTS"
    fi
    if [ -n "$SETUP_SCRIPT" ]; then
        setup_block+=$'\n'"$SETUP_SCRIPT"
    fi

    local setup_out setup_rc=0
    setup_out="$(bash -c "$setup_block" 2>&1)" || setup_rc=$?
    if [ "$setup_rc" -ne 0 ]; then
        echo "   ❌ FAIL (setup_script exit $setup_rc)"
        if [ -n "$setup_out" ]; then
            echo "$setup_out" | head -10 | sed 's/^/      /'
        fi
        RESULTS+=("FAIL $name (setup_script exit $setup_rc)")
        FAIL=$((FAIL + 1))
        rm -rf "$TMP_DIR"
        return
    fi

    # Build invocation block similarly.
    local invoke_block="set +e"
    invoke_block+=$'\n'"export PYTHONIOENCODING=utf-8"
    invoke_block+=$'\n'"export PYTHONPATH=\"$REPO_ROOT\""
    if [ -n "$ENV_EXPORTS" ]; then
        invoke_block+=$'\n'"$ENV_EXPORTS"
    fi
    invoke_block+=$'\n'"cd \"$REPO_ROOT\""
    invoke_block+=$'\n'"$INVOCATION_EXEC"

    local stdout_file stderr_file actual_rc=0
    stdout_file="$TMP_DIR/.stdout"
    stderr_file="$TMP_DIR/.stderr"

    bash -c "$invoke_block" > "$stdout_file" 2> "$stderr_file"
    actual_rc=$?

    local assertions_failed=""

    if [ "$actual_rc" -ne "$EXPECTED_EXIT_CODE" ]; then
        assertions_failed+=$'\n'"      exit code: expected $EXPECTED_EXIT_CODE, got $actual_rc"
    fi

    while IFS= read -r needle; do
        [ -z "$needle" ] && continue
        if ! grep -F -q -- "$needle" "$stdout_file"; then
            assertions_failed+=$'\n'"      stdout missing: $needle"
        fi
    done < <(json_to_lines "$(b64decode "$STDOUT_CONTAINS_JSON")")

    while IFS= read -r needle; do
        [ -z "$needle" ] && continue
        if ! grep -F -q -- "$needle" "$stderr_file"; then
            assertions_failed+=$'\n'"      stderr missing: $needle"
        fi
    done < <(json_to_lines "$(b64decode "$STDERR_CONTAINS_JSON")")

    while IFS= read -r raw_path; do
        [ -z "$raw_path" ] && continue
        local resolved_path
        resolved_path="$(substitute_tmpdir "$raw_path" "$TMP_DIR")"
        if [ ! -e "$resolved_path" ]; then
            assertions_failed+=$'\n'"      missing file: $resolved_path"
        fi
    done < <(json_to_lines "$(b64decode "$EXPECTED_FILES_JSON")")

    while IFS= read -r raw_glob; do
        [ -z "$raw_glob" ] && continue
        local resolved_glob
        resolved_glob="$(substitute_tmpdir "$raw_glob" "$TMP_DIR")"
        # shellcheck disable=SC2206,SC2086
        local matches=( $resolved_glob )
        if [ ${#matches[@]} -eq 0 ] || [ ! -e "${matches[0]}" ]; then
            assertions_failed+=$'\n'"      no files match glob: $resolved_glob"
        fi
    done < <(json_to_lines "$(b64decode "$EXPECTED_FILES_GLOB_JSON")")

    if [ -z "$assertions_failed" ]; then
        echo "   ✅ PASS (exit $actual_rc)"
        RESULTS+=("PASS $name")
        PASS=$((PASS + 1))
    else
        echo "   ❌ FAIL"
        echo "$assertions_failed" | sed '/^$/d'
        if [ -s "$stderr_file" ]; then
            echo "      stderr head:"
            head -5 "$stderr_file" | sed 's/^/         /'
        fi
        if [ -s "$stdout_file" ]; then
            echo "      stdout head:"
            head -5 "$stdout_file" | sed 's/^/         /'
        fi
        RESULTS+=("FAIL $name")
        FAIL=$((FAIL + 1))
    fi

    rm -rf "$TMP_DIR"
}

# ─── Main ───────────────────────────────────────────────────────────────────

shopt -s nullglob
SCENARIOS=("$SCENARIOS_DIR"/tool-*.md)
shopt -u nullglob

if [ ${#SCENARIOS[@]} -eq 0 ]; then
    echo "⚠️  no tool-*.md scenarios found under $SCENARIOS_DIR"
    echo ""
    echo "=== 结果汇总 ==="
    echo "通过: 0 / 失败: 0 / 跳过: 0 / 总计: 0"
    exit 0
fi

for scenario_file in "${SCENARIOS[@]}"; do
    run_scenario "$scenario_file"
done

echo ""
echo "=== 结果汇总 ==="
for r in "${RESULTS[@]}"; do
    echo "  $r"
done
echo ""
echo "通过: $PASS / 失败: $FAIL / 跳过: $SKIP / 总计: ${#SCENARIOS[@]}"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
