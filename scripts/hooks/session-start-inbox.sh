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

# v1.8.0 R-1.8.0-013: Async review queue (replaces scattered notifications)
# Read _meta/review-queue.md and count open items by priority + capture latest summary.
# Anchored regex: ^[[:space:]]*priority:[[:space:]]*P[012]\b — prevents false positives
# from prose like `summary: "escalated because priority: P0 was missed"`.
# Section ordering guard: do NOT count anything until ## Open items has been seen
# (in_open starts undefined, only set to 1 when we hit the header).
REVIEW_QUEUE_FILE="_meta/review-queue.md"
REVIEW_QUEUE_SUMMARY=""
REVIEW_QUEUE_LATEST=""
if [ -f "$REVIEW_QUEUE_FILE" ]; then
  if command -v awk >/dev/null 2>&1; then
    # Note: awk stderr deliberately NOT suppressed — surfaces parser regressions
    # to the user via SessionStart hook log instead of silently producing empty output.
    REVIEW_QUEUE_RAW="$(awk '
      # Always strip CRLF + UTF-8 BOM first — Windows editors save CRLF and
      # may prepend BOM. Without these, ^anchored regexes silently miss matches.
      { sub(/\r$/, "") }
      NR == 1 { sub(/^\xef\xbb\xbf/, "") }
      BEGIN { in_open = 0; latest = "" }
      /^## Open items/         { in_open = 1; next }
      /^## Recently resolved/  { in_open = 0; next }
      /^## /                   { in_open = 0; next }   # any other H2 ends section
      in_open && /^[[:space:]]*priority:[[:space:]]*P0([^0-9]|$)/ { p0++ }
      in_open && /^[[:space:]]*priority:[[:space:]]*P1([^0-9]|$)/ { p1++ }
      in_open && /^[[:space:]]*priority:[[:space:]]*P2([^0-9]|$)/ { p2++ }
      in_open && latest == "" && /^[[:space:]]*summary:[[:space:]]*/ {
        sub(/^[[:space:]]*summary:[[:space:]]*/, "", $0)
        gsub(/^"|"$/, "", $0)
        # Skip block-scalar indicators (`summary: |` or `>`); next line will be captured
        if ($0 ~ /^[|>][-+]?[[:space:]]*$/) { next }
        # Truncate at 70 BYTES (not chars) — POSIX awk substr is byte-indexed.
        # 70 leaves margin so a Chinese char (3 bytes) cannot be split mid-byte
        # within the visible ~22-char Chinese / 70-char ASCII budget.
        if (length($0) > 70) { latest = substr($0, 1, 67) "..." } else { latest = $0 }
      }
      END {
        if (p0 + p1 + p2 > 0) {
          printf "P0=%d / P1=%d / P2=%d (total %d open)\t%s", p0+0, p1+0, p2+0, p0+p1+p2, latest
        }
      }
    ' "$REVIEW_QUEUE_FILE" || true)"
    # Split on tab: counts before tab, latest after.
    if [ -n "$REVIEW_QUEUE_RAW" ]; then
      REVIEW_QUEUE_SUMMARY="${REVIEW_QUEUE_RAW%%	*}"
      REVIEW_QUEUE_LATEST="${REVIEW_QUEUE_RAW#*	}"
      [ "$REVIEW_QUEUE_LATEST" = "$REVIEW_QUEUE_RAW" ] && REVIEW_QUEUE_LATEST=""
    fi
  fi
fi

# Skip output if nothing to surface
if [ -z "$OVERDUE" ] && [ -z "$MEMORY_TAIL" ] && [ -z "$REVIEW_QUEUE_SUMMARY" ]; then
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

if [ -n "$REVIEW_QUEUE_SUMMARY" ]; then
  echo "## 📋 Open Review Queue (v1.8.0 R-1.8.0-013)"
  echo ""
  echo "  ${REVIEW_QUEUE_SUMMARY}"
  if [ -n "$REVIEW_QUEUE_LATEST" ]; then
    echo "  Latest: ${REVIEW_QUEUE_LATEST}"
  fi
  echo ""
  echo "If user says \"看 queue\" / \"处理 queue\" / \"review queue\":"
  echo "  → Read scripts/prompts/review-queue.md and walk through items."
  echo "If user says \"看 r{id} 详情\":"
  echo "  → Read the detail_path field from that queue item and show user."
  echo "If user mentions ANY business topic, surface ONE-LINE summary first:"
  echo "  → e.g. \"📋 You have 3 P0 items in review queue (latest: ${REVIEW_QUEUE_LATEST:-...}). Want to handle now or later?\""
  echo "  → Then proceed with their actual ask."
  echo "Privacy filter: if any related [[person-*]] item has privacy_tier: high,"
  echo "  redact aliases before displaying to user (per references/people-spec.md)."
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
