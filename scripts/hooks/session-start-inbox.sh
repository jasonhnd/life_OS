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
#
# task_name MUST match an existing scripts/prompts/<task_name>.md file
# AND the canonical 10-job table in pro/CLAUDE.md `Maintenance jobs`.
# When user says "跑 <task_name>" / "run <task_name>" / "都跑", ROUTER reads
# scripts/prompts/<task_name>.md and executes it. If the name here doesn't
# match a real prompt file, ROUTER cannot resolve the user's request.
#
# review-queue is intentionally OMITTED from this array — it's handled by a
# dedicated parser further down (REVIEW_QUEUE_FILE block) because it needs
# priority-bucket counts, not just an age check. migrate-to-wikilinks is also
# omitted — it's a one-time migration job, not an ongoing maintenance check.
TASKS_LINE=(
  "reindex|_meta/sessions/INDEX.md|2"
  "daily-briefing|_meta/eval-history/daily-briefing-*.md|2"
  "backup|_meta/snapshots/backup-*.tar.gz|7"
  "spec-compliance|_meta/eval-history/spec-compliance-*.md|14"
  "wiki-decay|_meta/eval-history/wiki-decay-*.md|30"
  "archiver-recovery|_meta/eval-history/recovery/*.md|2"
  "auditor-mode-2|_meta/eval-history/auditor-patrol/*.md|14"
  "advisor-monthly|_meta/eval-history/advisor-monthly-*.md|35"
  "eval-history-monthly|_meta/eval-history/monthly-summary-*.md|35"
  "strategic-consistency|_meta/eval-history/strategic-consistency-*.md|35"
)

OVERDUE=""
NEVER_RUN=""
for entry in "${TASKS_LINE[@]}"; do
  IFS='|' read -r name glob max <<< "$entry"
  age="$(age_days "$glob")"
  if [ -z "$age" ]; then
    # Differentiate "never run" from "overdue". Without a baseline, "never
    # run" is NOT debt — the user simply hasn't asked for this maintenance
    # job yet. Reporting it as overdue every session causes the LLM to
    # repeatedly suggest jobs the user never opted into (UX noise).
    # Tracked separately so ROUTER can present it as on-demand availability,
    # not as something to proactively remind about.
    NEVER_RUN="${NEVER_RUN}  · ${name}\n"
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

# v1.8.1 F3: Count items in _meta/inbox/to-process/ (user-drop pipeline).
# Items with `defer_until: <future-date>` in frontmatter are skipped (still
# parked, not yet eligible for triage). Output: a single one-line summary
# the LLM surfaces if non-zero ("📥 Inbox: N items waiting (run /inbox-process)").
INBOX_TO_PROCESS_DIR="_meta/inbox/to-process"
INBOX_PENDING_COUNT=0
INBOX_DEFERRED_COUNT=0
if [ -d "$INBOX_TO_PROCESS_DIR" ]; then
  today_iso="$(date +%Y-%m-%d)"
  for f in "$INBOX_TO_PROCESS_DIR"/*.md; do
    [ -e "$f" ] || continue
    # Skip the README (it's documentation, not a drop)
    case "$(basename "$f")" in
      README.md|readme.md|.gitkeep) continue ;;
    esac
    # Check frontmatter `defer_until: YYYY-MM-DD`. If present and future,
    # count as deferred (still parked, not eligible). Otherwise pending.
    defer_date="$(head -n 30 "$f" 2>/dev/null \
      | awk '/^---/{n++; next} n==1 && /^defer_until:/ {gsub(/^defer_until:[[:space:]]*/, "", $0); gsub(/[[:space:]]+$/, "", $0); gsub(/"|'\''/, "", $0); print; exit}' \
      || true)"
    if [ -n "$defer_date" ] && [ "$defer_date" \> "$today_iso" ]; then
      INBOX_DEFERRED_COUNT=$((INBOX_DEFERRED_COUNT + 1))
    else
      INBOX_PENDING_COUNT=$((INBOX_PENDING_COUNT + 1))
    fi
  done
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

# Skip output if nothing to surface. NEVER_RUN is intentionally NOT in this
# guard — never-run-only output would be pure noise (no user action needed),
# so the hook stays silent if OVERDUE / MEMORY / REVIEW_QUEUE / INBOX are
# all empty. Inbox pending IS in the guard because it represents user-drop
# items waiting for triage — actionable signal, not noise.
if [ -z "$OVERDUE" ] && [ -z "$MEMORY_TAIL" ] && [ -z "$REVIEW_QUEUE_SUMMARY" ] && [ "$INBOX_PENDING_COUNT" -eq 0 ]; then
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

if [ -n "$NEVER_RUN" ]; then
  # R-1.8.0-022 token-budget fix: collapse the never-run list to a single
  # comma-separated line. Previous multi-line printf wasted ~10 lines of
  # LLM context on a list the LLM is explicitly told NOT to mention.
  # Format: comma-joined task names, no leading bullets.
  NEVER_RUN_FLAT="$(printf "%b" "$NEVER_RUN" | sed 's/^[[:space:]]*·[[:space:]]*//' | tr '\n' ',' | sed 's/,$//; s/,/, /g')"
  echo "## Available on-demand (do NOT proactively offer): $NEVER_RUN_FLAT"
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

if [ "$INBOX_PENDING_COUNT" -gt 0 ]; then
  # v1.8.1 F3: surface inbox to-process count as ONE LINE. Do not list
  # filenames — that's /inbox-process's job. Just signal "there's work
  # waiting" so the user knows to invoke the triage flow.
  if [ "$INBOX_DEFERRED_COUNT" -gt 0 ]; then
    echo "## 📥 Inbox: $INBOX_PENDING_COUNT items waiting (+ $INBOX_DEFERRED_COUNT deferred). Run /inbox-process or say \"处理 inbox\"."
  else
    echo "## 📥 Inbox: $INBOX_PENDING_COUNT items waiting. Run /inbox-process or say \"处理 inbox\"."
  fi
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

Example one-liners — only mention items from the "Overdue maintenance"
section, NOT items from "Available on-demand":

- "维护待办：reindex 5d / archiver 漏 04-28 / wiki 31d。要跑哪个？"
- "Heads-up: backup 12 days old, spec-compliance 14 days old. Want me to
  run either?"  (only because both have a baseline that's actually overdue)
- (if nothing overdue and user opens with their own topic) → just answer
  their question, do NOT volunteer the on-demand list.

If user says "ignore" or proceeds with their own topic, drop this thread.

Spec source: pro/CLAUDE.md → Maintenance (v1.8.0 user-invoked) + scripts/prompts/*.md
</system-reminder>
EOF

exit 0
