#!/bin/bash
# Life OS · session-start-inbox.sh (v1.8.0 pivot)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   SessionStart
# Matcher: *
# Exit:    0 always (a session start cannot be blocked — only annotated)
# Timeout: 5s
#
# Purpose (v1.8.0 pivot — replaces cron→session bridge)
#   Cron is gone. This hook now scans the second-brain for *user-invoked*
#   maintenance work that's overdue, plus recent memory entries, and shows
#   the user a one-glance status. The user decides what to invoke; nothing
#   runs automatically.
#
#   Display format:
#     📋 Maintenance: reindex 5d / archiver missed 04-28 / wiki 31d
#     📚 Recent memory: 3 entries
#
#   ROUTER reads this and surfaces it to the user in plain language. The
#   user then says "跑一下 X" / "都跑" / "ignore" → ROUTER reads the matching
#   prompt at scripts/prompts/X.md and executes via Read/Write/Bash tools.
# ─────────────────────────────────────────────────────────────────────────────

set -u

# Detect we're in a user second-brain repo (has _meta/), not a dev repo
if [ ! -d "_meta" ] && [ ! -d "$PWD/_meta" ]; then
  exit 0
fi

now_epoch="$(date +%s)"

# Compute "days since latest file matching glob"; echoes integer or empty.
age_days() {
  local glob="$1"
  local latest_epoch=""
  # shellcheck disable=SC2086
  for f in $glob; do
    [ -e "$f" ] || continue
    local m
    m="$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null)"
    if [ -n "$m" ] && { [ -z "$latest_epoch" ] || [ "$m" -gt "$latest_epoch" ]; }; then
      latest_epoch="$m"
    fi
  done
  if [ -z "$latest_epoch" ]; then
    echo ""
    return
  fi
  echo $(( (now_epoch - latest_epoch) / 86400 ))
}

# (task_name, glob_for_latest_report, expected_max_age_days)
TASKS_LINE=(
  "reindex|_meta/sessions/INDEX.md|2"
  "daily-briefing|_meta/eval-history/daily-briefing-*.md|2"
  "backup|_meta/snapshots/backup-*.tar.gz|7"
  "spec-compliance|_meta/eval-history/spec-compliance-*.md|14"
  "wiki-decay|_meta/eval-history/wiki-decay-*.md|30"
  "archiver-recovery|_meta/eval-history/recovery/*.md|2"
  "auditor-patrol|_meta/eval-history/auditor-patrol/*.md|14"
  "advisor-monthly|_meta/eval-history/advisor-monthly-*.md|35"
  "monthly-summary|_meta/eval-history/monthly-summary-*.md|35"
  "strategic-consistency|_meta/eval-history/strategic-consistency-*.md|35"
)

OVERDUE=""
for entry in "${TASKS_LINE[@]}"; do
  IFS='|' read -r name glob max <<< "$entry"
  age="$(age_days "$glob")"
  if [ -z "$age" ]; then
    OVERDUE="${OVERDUE}  · ${name}: never run\n"
  elif [ "$age" -gt "$max" ]; then
    OVERDUE="${OVERDUE}  · ${name}: ${age}d (target ≤ ${max}d)\n"
  fi
done

# Recent memory entries (Hermes-Utilities memory store)
MEMORY_DIR="${HOME}/.claude/lifeos-memory"
MEMORY_TAIL=""
if [ -d "$MEMORY_DIR" ]; then
  if command -v find >/dev/null 2>&1; then
    MEMORY_TAIL="$(find "$MEMORY_DIR" -maxdepth 1 -type f -name '*.json' -mtime -7 2>/dev/null | head -10 || true)"
  fi
fi

# Skip output if nothing to surface
if [ -z "$OVERDUE" ] && [ -z "$MEMORY_TAIL" ]; then
  exit 0
fi

cat <<'EOF'
<system-reminder>
📡 LIFE OS · session-start status (v1.8.0 user-invoked model)

Cron is gone. The user invokes maintenance by talking to you. Below is what's
overdue or recently added; surface this to the user in your FIRST response in
ONE short sentence (don't dump the raw list — translate it).

EOF

if [ -n "$OVERDUE" ]; then
  echo "## Overdue maintenance"
  printf "%b" "$OVERDUE"
  echo ""
  echo "If user says \"跑 X\" / \"run X\" / \"都跑\" / \"全部\":"
  echo "  → Read scripts/prompts/<task-name>.md and execute it."
  echo "If user says \"忽略\" / \"later\" or talks about something else:"
  echo "  → drop this thread, focus on user's actual ask."
  echo ""
fi

if [ -n "$MEMORY_TAIL" ]; then
  echo "## Recent memory entries (last 7 days, ~/.claude/lifeos-memory/)"
  echo ""
  echo "$MEMORY_TAIL"
  echo ""
  echo "Available to recall when relevant. Do not list to user unless asked."
  echo ""
fi

cat <<'EOF'
## How to surface to user

Example one-liners (pick what fits):

- "维护待办：reindex 5d / archiver 漏 04-28 / wiki 31d。要跑哪个？"
- "Heads-up: backup 12 days old, advisor-monthly never run. Want me to run them?"
- (if nothing very urgent and user opens with their own topic) → just answer
  their question, mention status only if relevant.

If user says "ignore" or proceeds with their own topic, drop this thread.

Spec source: pro/CLAUDE.md → Maintenance (v1.8.0 user-invoked) + scripts/prompts/*.md
</system-reminder>
EOF

exit 0
