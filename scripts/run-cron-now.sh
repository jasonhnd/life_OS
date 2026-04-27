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
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"

# Log dir matches setup-cron.sh
case "$(uname -s 2>/dev/null)" in
  Darwin) LOG_DIR="${HOME}/Library/Logs/LifeOS/hermes-local" ;;
  *)      LOG_DIR="${XDG_STATE_HOME:-${HOME}/.local/state}/lifeos/hermes-local" ;;
esac
mkdir -p "$LOG_DIR"

# Job registry: name → kind:command
# kind = python | prompt
declare -A JOBS
JOBS[reindex]="python:reindex"
JOBS[daily-briefing]="python:daily_briefing"
JOBS[backup]="python:backup"
JOBS[spec-compliance]="python:spec_compliance_report"
JOBS[wiki-decay]="python:wiki_decay"
JOBS[archiver-recovery]="prompt:archiver-recovery"
JOBS[auditor-mode-2]="prompt:auditor-mode-2"
JOBS[advisor-monthly]="prompt:advisor-monthly"
JOBS[eval-history-monthly]="prompt:eval-history-monthly"
JOBS[strategic-consistency]="prompt:strategic-consistency"

list_jobs() {
  echo "Life OS cron jobs (v1.8.0):"
  for name in "${!JOBS[@]}"; do
    spec="${JOBS[$name]}"
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
EOF
    exit 0 ;;
  --list|list) list_jobs; exit 0 ;;
esac

JOB_NAME="$1"
if [ -z "${JOBS[$JOB_NAME]:-}" ]; then
  echo "Unknown job: $JOB_NAME" >&2
  echo "Run with --list to see available jobs." >&2
  exit 2
fi

SPEC="${JOBS[$JOB_NAME]}"
KIND="${SPEC%%:*}"
CMD="${SPEC##*:}"
TS="$(date +%Y%m%dT%H%M%S)"
LOG_FILE="$LOG_DIR/${JOB_NAME}-now-${TS}.log"

cd "$REPO_ROOT" || { echo "Cannot cd to $REPO_ROOT" >&2; exit 1; }

echo "🚀 Running cron job '$JOB_NAME' now (manual trigger)"
echo "   Log: $LOG_FILE"
echo "   ────────────────────────────────────────────"

case "$KIND" in
  python)
    if command -v uv >/dev/null 2>&1; then
      uv run python -m "tools.$CMD" --root . 2>&1 | tee "$LOG_FILE"
    else
      python3 -m "tools.$CMD" --root . 2>&1 | tee "$LOG_FILE"
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
