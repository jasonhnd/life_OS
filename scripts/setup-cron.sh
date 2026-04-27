#!/usr/bin/env bash
# Install local Hermes-style scheduled jobs for Life OS.
#
# Jobs:
#   - reindex:        daily at 03:00
#   - daily_briefing: daily at 08:00
#   - backup:         weekly on Sunday at 02:00
#
# The script is intentionally idempotent:
#   - macOS launchd writes only com.lifeos.hermes-local.* plists.
#   - Linux/WSL crontab replaces only the marked Life OS block.
#   - If the scheduler is unavailable, setup instructions are printed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"  # lifeos skill source — has tools/, scripts/prompts/
# v1.8.0 fix (R-1.8.0-003): the data root is the user's second-brain repo
# (where _meta/ + SOUL.md + wiki/ live), NOT the skill source. Default to the
# caller's $PWD; override with LIFEOS_DATA_ROOT=/path/to/second-brain.
DATA_ROOT="${LIFEOS_DATA_ROOT:-$PWD}"
LAUNCHD_DIR="${HOME}/Library/LaunchAgents"
LAUNCHD_LOG_DIR="${HOME}/Library/Logs/LifeOS/hermes-local"
CRON_LOG_DIR="${XDG_STATE_HOME:-${HOME}/.local/state}/lifeos/hermes-local"
CRON_MARKER_BEGIN="# BEGIN Life OS Hermes Local scheduled jobs"
CRON_MARKER_END="# END Life OS Hermes Local scheduled jobs"

MODE="${1:-install}"

usage() {
  cat <<EOF
Usage: bash scripts/setup-cron.sh [install|--print|--help]

Installs local Hermes-style Life OS scheduled jobs:
  reindex         daily 03:00
  daily_briefing daily 08:00
  backup         weekly Sunday 02:00

Behavior:
  macOS:     install/update launchd LaunchAgent plists.
  Linux/WSL: install/update a marked crontab block.
  Other:     print scheduler setup instructions.

Safety:
  Idempotent and non-destructive. Only Life OS-owned launchd plists or the
  marked crontab block are changed.
EOF
}

die() {
  echo "Error: $*" >&2
  exit 1
}

shell_quote() {
  # Single-quote a string for safe shell snippets.
  printf "'%s'" "$(printf "%s" "$1" | sed "s/'/'\\\\''/g")"
}

xml_escape() {
  printf "%s" "$1" | sed -e "s/&/\\&amp;/g" -e "s/</\\&lt;/g" -e "s/>/\\&gt;/g"
}

cron_escape_percent() {
  # In crontab commands, unescaped percent signs are converted to newlines.
  printf "%s" "$1" | sed "s/%/\\\\%/g"
}

repo_command() {
  local tool_command="$1"
  local repo_q data_q
  repo_q="$(shell_quote "$REPO_ROOT")"
  data_q="$(shell_quote "$DATA_ROOT")"
  printf "export PATH=\"\$HOME/.local/bin:\$HOME/.claude/local:\$HOME/.bun/bin:\$HOME/.npm-global/bin:\$HOME/.volta/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${PATH:-}\"; "
  printf "cd %s && " "$repo_q"
  printf "if command -v uv >/dev/null 2>&1; then "
  printf "uv run python tools/cli.py %s --root %s; " "$tool_command" "$data_q"
  printf "else "
  printf "python3 tools/cli.py %s --root %s; " "$tool_command" "$data_q"
  printf "fi"
}

# v1.8.0: build a python module command (for new tools NOT under tools/cli.py
# subcommand registry). Used by spec-compliance / wiki-decay / cron-health /
# missed-cron-check.
repo_command_pymod() {
  local module="$1"  # e.g., "tools.spec_compliance_report"
  local repo_q data_q
  repo_q="$(shell_quote "$REPO_ROOT")"
  data_q="$(shell_quote "$DATA_ROOT")"
  printf "export PATH=\"\$HOME/.local/bin:\$HOME/.claude/local:\$HOME/.bun/bin:\$HOME/.npm-global/bin:\$HOME/.volta/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${PATH:-}\"; "
  printf "cd %s && " "$repo_q"
  printf "if command -v uv >/dev/null 2>&1; then "
  printf "uv run python -m %s --root %s; " "$module" "$data_q"
  printf "else "
  printf "python3 -m %s --root %s; " "$module" "$data_q"
  printf "fi"
}

# v1.8.0: build a `claude -p` prompt-based command. Used by archiver-recovery
# / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency.
# v1.8.0 fix (R-1.8.0-003): cd into DATA_ROOT (not REPO_ROOT) so the spawned
# claude session sees the user's second-brain data; prompt path stays absolute.
# v1.8.0 fix (R-1.8.0-006): pass --dangerously-skip-permissions because cron
# runs unattended — without it, every Write tool call blocks on a permission
# prompt nobody answers, the session times out, and the analysis is lost.
# Safety boundary is enforced by cd "$DATA_ROOT" (cannot escape) + the prompt
# files being version-controlled in scripts/prompts/.
repo_command_prompt() {
  local prompt_name="$1"  # e.g., "archiver-recovery"
  local data_q
  local prompt_path_q
  data_q="$(shell_quote "$DATA_ROOT")"
  prompt_path_q="$(shell_quote "$REPO_ROOT/scripts/prompts/${prompt_name}.md")"
  printf "export PATH=\"\$HOME/.local/bin:\$HOME/.claude/local:\$HOME/.bun/bin:\$HOME/.npm-global/bin:\$HOME/.volta/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${PATH:-}\"; "
  printf "cd %s && " "$data_q"
  printf "if command -v claude >/dev/null 2>&1; then "
  printf "claude --dangerously-skip-permissions -p \"\$(cat %s)\"; " "$prompt_path_q"
  printf "else "
  printf 'echo "claude CLI not found - skipping %s"; ' "$prompt_name"
  printf "fi"
}

cron_job_command() {
  local tool_command="$1"
  local log_dir="$2"
  local log_file="$3"
  local log_dir_q
  local log_q

  log_dir_q="$(cron_escape_percent "$(shell_quote "$log_dir")")"
  log_q="$(cron_escape_percent "$(shell_quote "$log_file")")"

  printf "mkdir -p %s && { %s; } >> %s 2>&1" \
    "$log_dir_q" \
    "$(cron_escape_percent "$(repo_command "$tool_command")")" \
    "$log_q"
}

# v1.8.0: cron command wrapping a python module (no tools/cli.py subcommand).
cron_job_pymod() {
  local module="$1"
  local log_dir="$2"
  local log_file="$3"
  local log_dir_q
  local log_q

  log_dir_q="$(cron_escape_percent "$(shell_quote "$log_dir")")"
  log_q="$(cron_escape_percent "$(shell_quote "$log_file")")"

  printf "mkdir -p %s && { %s; } >> %s 2>&1" \
    "$log_dir_q" \
    "$(cron_escape_percent "$(repo_command_pymod "$module")")" \
    "$log_q"
}

# v1.8.0: cron command wrapping a `claude -p` prompt invocation.
cron_job_prompt() {
  local prompt_name="$1"
  local log_dir="$2"
  local log_file="$3"
  local log_dir_q
  local log_q

  log_dir_q="$(cron_escape_percent "$(shell_quote "$log_dir")")"
  log_q="$(cron_escape_percent "$(shell_quote "$log_file")")"

  printf "mkdir -p %s && { %s; } >> %s 2>&1" \
    "$log_dir_q" \
    "$(cron_escape_percent "$(repo_command_prompt "$prompt_name")")" \
    "$log_q"
}

require_data_root() {
  if [ ! -d "$DATA_ROOT/_meta" ]; then
    cat >&2 <<EOF
Error: $DATA_ROOT does not look like a Life OS data repo (no _meta/).

The cron jobs need to read/write your second-brain data, not the skill source.
Either:
  cd /path/to/your/second-brain && bash $0 $MODE
or:
  LIFEOS_DATA_ROOT=/path/to/your/second-brain bash $0 $MODE
EOF
    exit 2
  fi
}

ensure_repo() {
  [ -f "$REPO_ROOT/tools/cli.py" ] || die "tools/cli.py not found under $REPO_ROOT"
  [ -f "$REPO_ROOT/tools/reindex.py" ] || die "tools/reindex.py not found under $REPO_ROOT"
  [ -f "$REPO_ROOT/tools/daily_briefing.py" ] || die "tools/daily_briefing.py not found under $REPO_ROOT"
  [ -f "$REPO_ROOT/tools/backup.py" ] || die "tools/backup.py not found under $REPO_ROOT"
  # v1.8.0 new tools (warn if missing rather than die — older installs may upgrade incrementally)
  for v18_tool in spec_compliance_report wiki_decay cron_health_report missed_cron_check; do
    [ -f "$REPO_ROOT/tools/${v18_tool}.py" ] || echo "warning: tools/${v18_tool}.py not found (v1.8.0 expected)"
  done
  for v18_prompt in archiver-recovery auditor-mode-2 advisor-monthly eval-history-monthly strategic-consistency; do
    [ -f "$REPO_ROOT/scripts/prompts/${v18_prompt}.md" ] || echo "warning: scripts/prompts/${v18_prompt}.md not found (v1.8.0 expected)"
  done
}

# v1.8.0 — bootstrap second-brain dirs the cron prompts and hooks expect.
# Idempotent: only creates files that don't exist. Required for repos seeded
# before this fix (which lacked _meta/inbox + cron-runs/auditor-patrol/recovery
# subdirs in seed.py). Skipped when DATA_ROOT is not a Life OS data repo
# (no _meta/) — typically the dev/source repo.
bootstrap_repo_dirs() {
  if [ ! -d "$DATA_ROOT/_meta" ]; then
    return 0
  fi

  local d
  for d in \
    "_meta/inbox" \
    "_meta/runtime" \
    "_meta/eval-history/cron-runs" \
    "_meta/eval-history/auditor-patrol" \
    "_meta/eval-history/recovery"; do
    mkdir -p "$DATA_ROOT/$d"
    [ -f "$DATA_ROOT/$d/.gitkeep" ] || : > "$DATA_ROOT/$d/.gitkeep"
  done

  local notif="$DATA_ROOT/_meta/inbox/notifications.md"
  if [ ! -f "$notif" ]; then
    cat > "$notif" <<'NOTIF'
# Life OS · Cron Notifications Inbox (v1.8.0)

This file is the cron → session bridge target. Background cron jobs append
one-line notifications here; `session-start-inbox` reads the tail at every
new session start and surfaces unread items.

Format: `[ISO8601] <emoji> <subagent>: <summary> · see <relative-path>`
NOTIF
  fi
}

detect_platform() {
  local uname_s
  uname_s="$(uname -s 2>/dev/null || true)"
  case "$uname_s" in
    Darwin)
      echo "macos"
      ;;
    Linux)
      if [ -r /proc/version ] && grep -qiE "microsoft|wsl" /proc/version; then
        echo "wsl"
      else
        echo "linux"
      fi
      ;;
    *)
      echo "other"
      ;;
  esac
}

print_crontab_block() {
  local log_dir="$1"
  local reindex_log="${log_dir}/reindex.log"
  local briefing_log="${log_dir}/daily_briefing.log"
  local backup_log="${log_dir}/backup.log"
  local spec_compliance_log="${log_dir}/spec_compliance.log"
  local wiki_decay_log="${log_dir}/wiki_decay.log"
  local archiver_recovery_log="${log_dir}/archiver_recovery.log"
  local auditor_mode_2_log="${log_dir}/auditor_mode_2.log"
  local advisor_monthly_log="${log_dir}/advisor_monthly.log"
  local eval_history_monthly_log="${log_dir}/eval_history_monthly.log"
  local strategic_consistency_log="${log_dir}/strategic_consistency.log"
  local missed_cron_log="${log_dir}/missed_cron_check.log"

  cat <<EOF
$CRON_MARKER_BEGIN
SHELL=/bin/bash
# v1.7.x base jobs (python-based via tools/cli.py)
0 3 * * * $(cron_job_command "reindex" "$log_dir" "$reindex_log")
0 8 * * * $(cron_job_command "daily-briefing" "$log_dir" "$briefing_log")
0 2 * * 0 $(cron_job_command "backup" "$log_dir" "$backup_log")
# v1.8.0 python-module jobs
0 22 * * 0 $(cron_job_pymod "tools.spec_compliance_report" "$log_dir" "$spec_compliance_log")
0 2 15 * * $(cron_job_pymod "tools.wiki_decay" "$log_dir" "$wiki_decay_log")
# v1.8.0 prompt-based jobs (claude -p)
30 23 * * * $(cron_job_prompt "archiver-recovery" "$log_dir" "$archiver_recovery_log")
0 21 * * 0 $(cron_job_prompt "auditor-mode-2" "$log_dir" "$auditor_mode_2_log")
0 6 1 * * $(cron_job_prompt "advisor-monthly" "$log_dir" "$advisor_monthly_log")
0 7 1 * * $(cron_job_prompt "eval-history-monthly" "$log_dir" "$eval_history_monthly_log")
0 8 1 * * $(cron_job_prompt "strategic-consistency" "$log_dir" "$strategic_consistency_log")
# v1.8.0 boot recovery (cron @reboot equivalent — best-effort on Linux/WSL)
@reboot $(cron_job_pymod "tools.missed_cron_check" "$log_dir" "$missed_cron_log")
$CRON_MARKER_END
EOF
}

print_launchd_plist() {
  local label="$1"
  local hour="$2"
  local minute="$3"
  local weekday="$4"
  local tool_command="$5"
  local log_file="$6"
  local command_xml
  local label_xml
  local log_file_xml
  local repo_root_xml
  local weekday_xml=""

  command_xml="$(xml_escape "$(repo_command "$tool_command")")"
  label_xml="$(xml_escape "$label")"
  log_file_xml="$(xml_escape "$log_file")"
  repo_root_xml="$(xml_escape "$DATA_ROOT")"

  if [ -n "$weekday" ]; then
    weekday_xml="    <key>Weekday</key>
    <integer>${weekday}</integer>"
  fi

  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${label_xml}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>${command_xml}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${hour}</integer>
    <key>Minute</key>
    <integer>${minute}</integer>
${weekday_xml}
  </dict>
  <key>StandardOutPath</key>
  <string>${log_file_xml}</string>
  <key>StandardErrorPath</key>
  <string>${log_file_xml}</string>
  <key>WorkingDirectory</key>
  <string>${repo_root_xml}</string>
</dict>
</plist>
EOF
}

print_launchd_instructions() {
  cat <<EOF
macOS launchd setup
Skill source: $REPO_ROOT
Data root:    $DATA_ROOT  (override with LIFEOS_DATA_ROOT)
LaunchAgents directory: $LAUNCHD_DIR
Logs: $LAUNCHD_LOG_DIR

This script can install automatically on macOS:
  bash scripts/setup-cron.sh

It will create/update these Life OS-owned plists:
  com.lifeos.hermes-local.reindex.plist          daily 03:00
  com.lifeos.hermes-local.daily-briefing.plist   daily 08:00
  com.lifeos.hermes-local.backup.plist           Sunday 02:00

Manual commands, if preferred:
  mkdir -p $(shell_quote "$LAUNCHD_DIR") $(shell_quote "$LAUNCHD_LOG_DIR")
  bash scripts/setup-cron.sh --print
  launchctl bootstrap "gui/\$(id -u)" $(shell_quote "${LAUNCHD_DIR}/com.lifeos.hermes-local.reindex.plist")
  launchctl bootstrap "gui/\$(id -u)" $(shell_quote "${LAUNCHD_DIR}/com.lifeos.hermes-local.daily-briefing.plist")
  launchctl bootstrap "gui/\$(id -u)" $(shell_quote "${LAUNCHD_DIR}/com.lifeos.hermes-local.backup.plist")
EOF
}

print_crontab_instructions() {
  cat <<EOF
Linux/WSL crontab setup
Skill source: $REPO_ROOT
Data root:    $DATA_ROOT  (override with LIFEOS_DATA_ROOT)
Logs: $CRON_LOG_DIR

This script can install automatically when crontab is available:
  bash scripts/setup-cron.sh

Manual setup:
  mkdir -p $(shell_quote "$CRON_LOG_DIR")
  crontab -l > /tmp/lifeos-cron.txt 2>/dev/null || true
  Edit /tmp/lifeos-cron.txt and add this block:

$(print_crontab_block "$CRON_LOG_DIR")

  Then install it:
  crontab /tmp/lifeos-cron.txt

WSL note:
  Cron must be running for jobs to fire. Depending on your distro, start it with
  "sudo service cron start" or enable systemd and use "sudo systemctl enable --now cron".
EOF
}

print_all_instructions() {
  print_launchd_instructions
  echo ""
  print_crontab_instructions
}

write_launchd_plist() {
  local label="$1"
  local hour="$2"
  local minute="$3"
  local weekday="$4"
  local tool_command="$5"
  local log_file="$6"
  local plist="$LAUNCHD_DIR/${label}.plist"
  local tmp="${plist}.tmp"

  print_launchd_plist "$label" "$hour" "$minute" "$weekday" "$tool_command" "$log_file" > "$tmp"
  mv "$tmp" "$plist"
  echo "Wrote $plist"
}

load_launchd_plist() {
  local label="$1"
  local plist="$LAUNCHD_DIR/${label}.plist"
  local domain="gui/$(id -u)"

  if launchctl print "${domain}/${label}" >/dev/null 2>&1; then
    launchctl bootout "$domain" "$plist" >/dev/null 2>&1 || true
  fi

  if launchctl bootstrap "$domain" "$plist" >/dev/null 2>&1; then
    echo "Loaded ${label}"
  else
    echo "Could not load ${label}; plist was written. Try manually:"
    echo "  launchctl bootstrap ${domain} $(shell_quote "$plist")"
  fi
}

install_launchd() {
  command -v launchctl >/dev/null 2>&1 || {
    echo "launchctl not found; printing macOS instructions instead."
    print_launchd_instructions
    return 0
  }

  mkdir -p "$LAUNCHD_DIR" "$LAUNCHD_LOG_DIR"

  # v1.7.x base jobs (python via tools/cli.py)
  write_launchd_plist "com.lifeos.hermes-local.reindex" "3" "0" "" \
    "reindex" "${LAUNCHD_LOG_DIR}/reindex.log"
  write_launchd_plist "com.lifeos.hermes-local.daily-briefing" "8" "0" "" \
    "daily-briefing" "${LAUNCHD_LOG_DIR}/daily_briefing.log"
  write_launchd_plist "com.lifeos.hermes-local.backup" "2" "0" "0" \
    "backup" "${LAUNCHD_LOG_DIR}/backup.log"

  # v1.8.0 python-module jobs
  write_launchd_pymod "com.lifeos.hermes-local.spec-compliance" "22" "0" "0" \
    "tools.spec_compliance_report" "${LAUNCHD_LOG_DIR}/spec_compliance.log"
  write_launchd_pymod_day "com.lifeos.hermes-local.wiki-decay" "2" "0" "15" \
    "tools.wiki_decay" "${LAUNCHD_LOG_DIR}/wiki_decay.log"

  # v1.8.0 prompt-based jobs (claude -p)
  write_launchd_prompt "com.lifeos.hermes-local.archiver-recovery" "23" "30" "" \
    "archiver-recovery" "${LAUNCHD_LOG_DIR}/archiver_recovery.log"
  write_launchd_prompt "com.lifeos.hermes-local.auditor-mode-2" "21" "0" "0" \
    "auditor-mode-2" "${LAUNCHD_LOG_DIR}/auditor_mode_2.log"
  write_launchd_prompt_day "com.lifeos.hermes-local.advisor-monthly" "6" "0" "1" \
    "advisor-monthly" "${LAUNCHD_LOG_DIR}/advisor_monthly.log"
  write_launchd_prompt_day "com.lifeos.hermes-local.eval-history-monthly" "7" "0" "1" \
    "eval-history-monthly" "${LAUNCHD_LOG_DIR}/eval_history_monthly.log"
  write_launchd_prompt_day "com.lifeos.hermes-local.strategic-consistency" "8" "0" "1" \
    "strategic-consistency" "${LAUNCHD_LOG_DIR}/strategic_consistency.log"

  # v1.8.0 RunAtLoad (boot/wake catch-up)
  write_launchd_runatload "com.lifeos.hermes-local.missed-cron-check" \
    "tools.missed_cron_check" "${LAUNCHD_LOG_DIR}/missed_cron_check.log"

  # Load all
  load_launchd_plist "com.lifeos.hermes-local.reindex"
  load_launchd_plist "com.lifeos.hermes-local.daily-briefing"
  load_launchd_plist "com.lifeos.hermes-local.backup"
  load_launchd_plist "com.lifeos.hermes-local.spec-compliance"
  load_launchd_plist "com.lifeos.hermes-local.wiki-decay"
  load_launchd_plist "com.lifeos.hermes-local.archiver-recovery"
  load_launchd_plist "com.lifeos.hermes-local.auditor-mode-2"
  load_launchd_plist "com.lifeos.hermes-local.advisor-monthly"
  load_launchd_plist "com.lifeos.hermes-local.eval-history-monthly"
  load_launchd_plist "com.lifeos.hermes-local.strategic-consistency"
  load_launchd_plist "com.lifeos.hermes-local.missed-cron-check"

  echo "Life OS Hermes Local launchd jobs (v1.8.0: 10 cron + 1 RunAtLoad) are installed."
}

# v1.8.0 helpers: write launchd plists for python-module / prompt jobs
# (mirror write_launchd_plist but use repo_command_pymod / repo_command_prompt)

write_launchd_pymod() {
  local label="$1"; local hour="$2"; local minute="$3"; local weekday="$4"
  local module="$5"; local log_file="$6"
  local plist="$LAUNCHD_DIR/${label}.plist"
  local tmp="${plist}.tmp"
  print_launchd_plist_pymod "$label" "$hour" "$minute" "$weekday" "$module" "$log_file" > "$tmp"
  mv "$tmp" "$plist"
  echo "Wrote $plist"
}

write_launchd_pymod_day() {
  local label="$1"; local hour="$2"; local minute="$3"; local day="$4"
  local module="$5"; local log_file="$6"
  local plist="$LAUNCHD_DIR/${label}.plist"
  local tmp="${plist}.tmp"
  print_launchd_plist_pymod_day "$label" "$hour" "$minute" "$day" "$module" "$log_file" > "$tmp"
  mv "$tmp" "$plist"
  echo "Wrote $plist"
}

write_launchd_prompt() {
  local label="$1"; local hour="$2"; local minute="$3"; local weekday="$4"
  local prompt="$5"; local log_file="$6"
  local plist="$LAUNCHD_DIR/${label}.plist"
  local tmp="${plist}.tmp"
  print_launchd_plist_prompt "$label" "$hour" "$minute" "$weekday" "$prompt" "$log_file" > "$tmp"
  mv "$tmp" "$plist"
  echo "Wrote $plist"
}

write_launchd_prompt_day() {
  local label="$1"; local hour="$2"; local minute="$3"; local day="$4"
  local prompt="$5"; local log_file="$6"
  local plist="$LAUNCHD_DIR/${label}.plist"
  local tmp="${plist}.tmp"
  print_launchd_plist_prompt_day "$label" "$hour" "$minute" "$day" "$prompt" "$log_file" > "$tmp"
  mv "$tmp" "$plist"
  echo "Wrote $plist"
}

write_launchd_runatload() {
  local label="$1"; local module="$2"; local log_file="$3"
  local plist="$LAUNCHD_DIR/${label}.plist"
  local tmp="${plist}.tmp"
  print_launchd_plist_runatload "$label" "$module" "$log_file" > "$tmp"
  mv "$tmp" "$plist"
  echo "Wrote $plist"
}

# Plist printers for v1.8.0 job types
print_launchd_plist_pymod() {
  local label="$1"; local hour="$2"; local minute="$3"; local weekday="$4"
  local module="$5"; local log_file="$6"
  local command_xml; command_xml="$(xml_escape "$(repo_command_pymod "$module")")"
  local label_xml; label_xml="$(xml_escape "$label")"
  local log_file_xml; log_file_xml="$(xml_escape "$log_file")"
  local repo_root_xml; repo_root_xml="$(xml_escape "$DATA_ROOT")"
  local weekday_xml=""
  if [ -n "$weekday" ]; then
    weekday_xml="    <key>Weekday</key>
    <integer>${weekday}</integer>"
  fi
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${label_xml}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>${command_xml}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${hour}</integer>
    <key>Minute</key>
    <integer>${minute}</integer>
${weekday_xml}
  </dict>
  <key>StandardOutPath</key>
  <string>${log_file_xml}</string>
  <key>StandardErrorPath</key>
  <string>${log_file_xml}</string>
  <key>WorkingDirectory</key>
  <string>${repo_root_xml}</string>
</dict>
</plist>
EOF
}

print_launchd_plist_pymod_day() {
  local label="$1"; local hour="$2"; local minute="$3"; local day="$4"
  local module="$5"; local log_file="$6"
  local command_xml; command_xml="$(xml_escape "$(repo_command_pymod "$module")")"
  local label_xml; label_xml="$(xml_escape "$label")"
  local log_file_xml; log_file_xml="$(xml_escape "$log_file")"
  local repo_root_xml; repo_root_xml="$(xml_escape "$DATA_ROOT")"
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${label_xml}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>${command_xml}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Day</key>
    <integer>${day}</integer>
    <key>Hour</key>
    <integer>${hour}</integer>
    <key>Minute</key>
    <integer>${minute}</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${log_file_xml}</string>
  <key>StandardErrorPath</key>
  <string>${log_file_xml}</string>
  <key>WorkingDirectory</key>
  <string>${repo_root_xml}</string>
</dict>
</plist>
EOF
}

print_launchd_plist_prompt() {
  local label="$1"; local hour="$2"; local minute="$3"; local weekday="$4"
  local prompt="$5"; local log_file="$6"
  local command_xml; command_xml="$(xml_escape "$(repo_command_prompt "$prompt")")"
  local label_xml; label_xml="$(xml_escape "$label")"
  local log_file_xml; log_file_xml="$(xml_escape "$log_file")"
  local repo_root_xml; repo_root_xml="$(xml_escape "$DATA_ROOT")"
  local weekday_xml=""
  if [ -n "$weekday" ]; then
    weekday_xml="    <key>Weekday</key>
    <integer>${weekday}</integer>"
  fi
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${label_xml}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>${command_xml}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${hour}</integer>
    <key>Minute</key>
    <integer>${minute}</integer>
${weekday_xml}
  </dict>
  <key>StandardOutPath</key>
  <string>${log_file_xml}</string>
  <key>StandardErrorPath</key>
  <string>${log_file_xml}</string>
  <key>WorkingDirectory</key>
  <string>${repo_root_xml}</string>
</dict>
</plist>
EOF
}

print_launchd_plist_prompt_day() {
  local label="$1"; local hour="$2"; local minute="$3"; local day="$4"
  local prompt="$5"; local log_file="$6"
  local command_xml; command_xml="$(xml_escape "$(repo_command_prompt "$prompt")")"
  local label_xml; label_xml="$(xml_escape "$label")"
  local log_file_xml; log_file_xml="$(xml_escape "$log_file")"
  local repo_root_xml; repo_root_xml="$(xml_escape "$DATA_ROOT")"
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${label_xml}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>${command_xml}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Day</key>
    <integer>${day}</integer>
    <key>Hour</key>
    <integer>${hour}</integer>
    <key>Minute</key>
    <integer>${minute}</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${log_file_xml}</string>
  <key>StandardErrorPath</key>
  <string>${log_file_xml}</string>
  <key>WorkingDirectory</key>
  <string>${repo_root_xml}</string>
</dict>
</plist>
EOF
}

print_launchd_plist_runatload() {
  local label="$1"; local module="$2"; local log_file="$3"
  local command_xml; command_xml="$(xml_escape "$(repo_command_pymod "$module")")"
  local label_xml; label_xml="$(xml_escape "$label")"
  local log_file_xml; log_file_xml="$(xml_escape "$log_file")"
  local repo_root_xml; repo_root_xml="$(xml_escape "$DATA_ROOT")"
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${label_xml}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>${command_xml}</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${log_file_xml}</string>
  <key>StandardErrorPath</key>
  <string>${log_file_xml}</string>
  <key>WorkingDirectory</key>
  <string>${repo_root_xml}</string>
</dict>
</plist>
EOF
}

install_crontab() {
  command -v crontab >/dev/null 2>&1 || {
    echo "crontab not found; printing Linux/WSL instructions instead."
    print_crontab_instructions
    return 0
  }

  mkdir -p "$CRON_LOG_DIR"

  local current
  local managed_block
  local next
  local begin_count
  local end_count

  current="$(crontab -l 2>/dev/null || true)"
  managed_block="$(print_crontab_block "$CRON_LOG_DIR")"
  begin_count="$(printf "%s\n" "$current" | grep -F -c "$CRON_MARKER_BEGIN" || true)"
  end_count="$(printf "%s\n" "$current" | grep -F -c "$CRON_MARKER_END" || true)"

  if [ "$begin_count" -eq 1 ] && [ "$end_count" -eq 1 ]; then
    next="$(printf "%s\n" "$current" | awk \
      -v begin="$CRON_MARKER_BEGIN" \
      -v end="$CRON_MARKER_END" \
      -v block="$managed_block" '
        $0 == begin {
          print block
          in_block = 1
          next
        }
        $0 == end {
          in_block = 0
          next
        }
        !in_block { print }
      ')"
  elif [ "$begin_count" -eq 0 ] && [ "$end_count" -eq 0 ]; then
    if [ -n "$current" ]; then
      next="$(printf "%s\n\n%s\n" "$current" "$managed_block")"
    else
      next="$managed_block"
    fi
  else
    die "existing crontab has mismatched or duplicate Life OS markers; refusing to edit"
  fi

  printf "%s\n" "$next" | crontab -
  echo "Life OS Hermes Local crontab block is installed."
}

main() {
  case "$MODE" in
    install)
      ;;
    --print|print)
      ensure_repo
      print_all_instructions
      exit 0
      ;;
    --help|-h|help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 2
      ;;
  esac

  ensure_repo
  require_data_root
  bootstrap_repo_dirs

  case "$(detect_platform)" in
    macos)
      install_launchd
      ;;
    linux|wsl)
      install_crontab
      ;;
    *)
      echo "Unsupported platform for automatic install: $(uname -s 2>/dev/null || echo unknown)"
      echo "Printing setup instructions instead."
      print_all_instructions
      ;;
  esac
}

main "$@"
