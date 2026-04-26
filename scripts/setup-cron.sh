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
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
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
  local repo_q
  repo_q="$(shell_quote "$REPO_ROOT")"
  printf "export PATH=\"\$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${PATH:-}\"; "
  printf "cd %s && " "$repo_q"
  printf "if command -v uv >/dev/null 2>&1; then "
  printf "uv run python tools/cli.py %s --root .; " "$tool_command"
  printf "else "
  printf "python3 tools/cli.py %s --root .; " "$tool_command"
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

ensure_repo() {
  [ -f "$REPO_ROOT/tools/cli.py" ] || die "tools/cli.py not found under $REPO_ROOT"
  [ -f "$REPO_ROOT/tools/reindex.py" ] || die "tools/reindex.py not found under $REPO_ROOT"
  [ -f "$REPO_ROOT/tools/daily_briefing.py" ] || die "tools/daily_briefing.py not found under $REPO_ROOT"
  [ -f "$REPO_ROOT/tools/backup.py" ] || die "tools/backup.py not found under $REPO_ROOT"
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

  cat <<EOF
$CRON_MARKER_BEGIN
SHELL=/bin/bash
0 3 * * * $(cron_job_command "reindex" "$log_dir" "$reindex_log")
0 8 * * * $(cron_job_command "daily-briefing" "$log_dir" "$briefing_log")
0 2 * * 0 $(cron_job_command "backup" "$log_dir" "$backup_log")
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
  repo_root_xml="$(xml_escape "$REPO_ROOT")"

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
Repo: $REPO_ROOT
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
Repo: $REPO_ROOT
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

  write_launchd_plist "com.lifeos.hermes-local.reindex" "3" "0" "" \
    "reindex" "${LAUNCHD_LOG_DIR}/reindex.log"
  write_launchd_plist "com.lifeos.hermes-local.daily-briefing" "8" "0" "" \
    "daily-briefing" "${LAUNCHD_LOG_DIR}/daily_briefing.log"
  write_launchd_plist "com.lifeos.hermes-local.backup" "2" "0" "0" \
    "backup" "${LAUNCHD_LOG_DIR}/backup.log"

  load_launchd_plist "com.lifeos.hermes-local.reindex"
  load_launchd_plist "com.lifeos.hermes-local.daily-briefing"
  load_launchd_plist "com.lifeos.hermes-local.backup"

  echo "Life OS Hermes Local launchd jobs are installed."
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
