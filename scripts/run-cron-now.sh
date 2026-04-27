#!/bin/bash
# Life OS · run-cron-now.sh (v1.8.0)
# ─────────────────────────────────────────────────────────────────────────────
# Manually trigger any installed Life OS cron job immediately, without waiting
# for its schedule. Used from inside Claude Code session (typically /monitor)
# or interactively from a Terminal.
#
# Usage:
#   bash scripts/run-cron-now.sh <job-name>
#   bash scripts/run-cron-now.sh --list
#
# Job names (v1.8.0):
#   reindex                 (daily 03:00)
#   daily-briefing          (daily 08:00)
#   backup                  (weekly Sun 02:00)
#   spec-compliance         (weekly Sun 22:00)
#   wiki-decay              (monthly 15th 02:00)
#   archiver-recovery       (daily 23:30)
#   auditor-mode-2          (weekly Sun 21:00)
#   advisor-monthly         (monthly 1st 06:00)
#   eval-history-monthly    (monthly 1st 07:00)
#   strategic-consistency   (monthly 1st 08:00)
#
# Behavior:
#   - python-tool jobs (reindex/daily-briefing/backup/spec-compliance/wiki-decay)
#     run via `python -m tools.<name>`
#   - claude-prompt jobs (rest) run via `claude -p "$(cat scripts/prompts/<name>.md)"`
#   - Output is written to the same log path the scheduled job uses, AND echoed
#     to current terminal so the caller can see it.
# ─────────────────────────────────────────────────────────────────────────────

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"  # lifeos skill source (has tools/, scripts/prompts/)
PROMPTS_DIR="$SCRIPT_DIR/prompts"

# v1.8.0 fix (R-1.8.0-003): the data root is the CALLER's cwd (their second-brain
# repo with _meta/), NOT the skill source dir. Without this, --root . pointed at
# the skill dir and every job scanned 0 sessions.
DATA_ROOT="${LIFEOS_DATA_ROOT:-$PWD}"
if [ ! -d "$DATA_ROOT/_meta" ]; then
  echo "Error: $DATA_ROOT does not look like a Life OS data repo (no _meta/)." >&2
  echo "       cd into your second-brain repo first, or set LIFEOS_DATA_ROOT." >&2
  exit 2
fi

# Log dir matches setup-cron.sh
case "$(uname -s 2>/dev/null)" in
  Darwin) LOG_DIR="${HOME}/Library/Logs/LifeOS/hermes-local" ;;
  *)      LOG_DIR="${XDG_STATE_HOME:-${HOME}/.local/state}/lifeos/hermes-local" ;;
esac
mkdir -p "$LOG_DIR"

# v1.8.0 fix (R-1.8.0-002): macOS ships bash 3.2.57 which has no `declare -A`.
# Use a case-based lookup function instead of an associative array. Format
# returned: "<kind>:<cmd>" where kind = python | prompt.
job_spec() {
  case "$1" in
    reindex)               echo "python:reindex" ;;
    daily-briefing)        echo "python:daily_briefing" ;;
    backup)                echo "python:backup" ;;
    spec-compliance)       echo "python:spec_compliance_report" ;;
    wiki-decay)            echo "python:wiki_decay" ;;
    archiver-recovery)     echo "prompt:archiver-recovery" ;;
    auditor-mode-2)        echo "prompt:auditor-mode-2" ;;
    advisor-monthly)       echo "prompt:advisor-monthly" ;;
    eval-history-monthly)  echo "prompt:eval-history-monthly" ;;
    strategic-consistency) echo "prompt:strategic-consistency" ;;
    *)                     echo "" ;;
  esac
}

JOB_NAMES="reindex daily-briefing backup spec-compliance wiki-decay archiver-recovery auditor-mode-2 advisor-monthly eval-history-monthly strategic-consistency"

list_jobs() {
  echo "Life OS cron jobs (v1.8.0):"
  for name in $JOB_NAMES; do
    spec="$(job_spec "$name")"
    kind="${spec%%:*}"
    cmd="${spec##*:}"
    case "$kind" in
      python) echo "  $name       → python -m tools.$cmd" ;;
      prompt) echo "  $name       → claude -p \"\$(cat scripts/prompts/$cmd.md)\"" ;;
    esac
  done
}

case "${1:-}" in
  ""|--help|-h|help) cat <<EOF
Usage: bash scripts/run-cron-now.sh <job-name>
       bash scripts/run-cron-now.sh --list

Data root resolution (v1.8.0+):
  Defaults to the current working directory (must contain _meta/).
  Override with LIFEOS_DATA_ROOT=/path/to/second-brain.
EOF
    exit 0 ;;
  --list|list) list_jobs; exit 0 ;;
esac

JOB_NAME="$1"
SPEC="$(job_spec "$JOB_NAME")"
if [ -z "$SPEC" ]; then
  echo "Unknown job: $JOB_NAME" >&2
  echo "Run with --list to see available jobs." >&2
  exit 2
fi

KIND="${SPEC%%:*}"
CMD="${SPEC##*:}"
TS="$(date +%Y%m%dT%H%M%S)"
LOG_FILE="$LOG_DIR/${JOB_NAME}-now-${TS}.log"

echo "🚀 Running cron job '$JOB_NAME' now (manual trigger)"
echo "   Data root: $DATA_ROOT"
echo "   Log:       $LOG_FILE"
echo "   ────────────────────────────────────────────"

case "$KIND" in
  python)
    # cd into SCRIPT_ROOT so `python -m tools.X` resolves; pass --root explicitly
    # to the user's second-brain so the tool reads/writes there.
    cd "$SCRIPT_ROOT" || { echo "Cannot cd to $SCRIPT_ROOT" >&2; exit 1; }
    if command -v uv >/dev/null 2>&1; then
      uv run python -m "tools.$CMD" --root "$DATA_ROOT" 2>&1 | tee "$LOG_FILE"
    else
      python3 -m "tools.$CMD" --root "$DATA_ROOT" 2>&1 | tee "$LOG_FILE"
    fi
    EXIT_CODE="${PIPESTATUS[0]}"
    ;;
  prompt)
    PROMPT_FILE="$PROMPTS_DIR/$CMD.md"
    if [ ! -f "$PROMPT_FILE" ]; then
      echo "Prompt file not found: $PROMPT_FILE" >&2
      exit 1
    fi
    if ! command -v claude >/dev/null 2>&1; then
      echo "claude CLI not found. Install Claude Code or run from a session." >&2
      exit 1
    fi
    # Run claude -p with cwd = DATA_ROOT so the spawned session reads the
    # correct second-brain.
    cd "$DATA_ROOT" || { echo "Cannot cd to $DATA_ROOT" >&2; exit 1; }
    claude -p "$(cat "$PROMPT_FILE")" 2>&1 | tee "$LOG_FILE"
    EXIT_CODE="${PIPESTATUS[0]}"
    ;;
esac

echo "   ────────────────────────────────────────────"
if [ "$EXIT_CODE" -eq 0 ]; then
  echo "OK '$JOB_NAME' completed successfully"
else
  echo "FAIL '$JOB_NAME' exited with code $EXIT_CODE"
fi
exit "$EXIT_CODE"
