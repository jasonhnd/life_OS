#!/bin/bash
# Life OS · session-start-inbox.sh (v1.8.0)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   SessionStart
# Matcher: *
# Exit:    0 always (a session start cannot be blocked — only annotated)
# Timeout: 5s
#
# Purpose
#   Bridge cron-driven autonomy into reactive Claude Code sessions. Every new
#   session reads recent cron output (_meta/inbox/notifications.md and
#   _meta/eval-history/cron-runs/ in last 24h) and injects a system-reminder
#   so Claude can proactively tell the user what happened in the background.
#
#   This is the v1.8.0 hybrid model's main "cron → session" channel.
# ─────────────────────────────────────────────────────────────────────────────

set -u

# Detect we're in a user second-brain repo (has _meta/), not a dev repo
if [ ! -d "_meta" ] && [ ! -d "$PWD/_meta" ]; then
  exit 0
fi

INBOX_FILE="_meta/inbox/notifications.md"
CRON_RUNS_DIR="_meta/eval-history/cron-runs"
EVAL_HISTORY_DIR="_meta/eval-history"

NEW_NOTIFICATIONS=""
RECENT_CRON_RUNS=""
PENDING_REPORTS=""

if [ -f "$INBOX_FILE" ]; then
  NEW_NOTIFICATIONS="$(tail -30 "$INBOX_FILE" 2>/dev/null | grep -v '^$' || true)"
fi

if [ -d "$CRON_RUNS_DIR" ]; then
  if command -v find >/dev/null 2>&1; then
    RECENT_CRON_RUNS="$(find "$CRON_RUNS_DIR" -type f -mtime -1 2>/dev/null | head -20 || true)"
  fi
fi

if [ -d "$EVAL_HISTORY_DIR" ]; then
  if command -v find >/dev/null 2>&1; then
    PENDING_REPORTS="$(find "$EVAL_HISTORY_DIR" -maxdepth 2 -type f -name '*.md' -mtime -7 2>/dev/null \
      | grep -E '(auditor-patrol|advisor-monthly|strategic-consistency|monthly-summary|spec-compliance|wiki-decay|recovery)' \
      | head -10 || true)"
  fi
fi

if [ -z "$NEW_NOTIFICATIONS" ] && [ -z "$RECENT_CRON_RUNS" ] && [ -z "$PENDING_REPORTS" ]; then
  exit 0
fi

cat <<EOF
<system-reminder>
📡 LIFE OS · cron activity since last session (v1.8.0 hybrid model)

The Life OS background cron layer wrote new content. ROUTER MUST proactively
mention this to the user in your first response (before they ask), so they
know what happened while they were away. Do NOT just dump these — translate
them into a brief summary.

EOF

if [ -n "$NEW_NOTIFICATIONS" ]; then
  echo "## Recent inbox notifications (tail of _meta/inbox/notifications.md)"
  echo ""
  echo "$NEW_NOTIFICATIONS"
  echo ""
fi

if [ -n "$RECENT_CRON_RUNS" ]; then
  echo "## Cron runs in last 24h ($CRON_RUNS_DIR)"
  echo ""
  echo "$RECENT_CRON_RUNS"
  echo ""
fi

if [ -n "$PENDING_REPORTS" ]; then
  echo "## Pending action-item reports (last 7 days, $EVAL_HISTORY_DIR)"
  echo ""
  echo "$PENDING_REPORTS"
  echo ""
fi

cat <<EOF

## How to surface this to the user

In your FIRST response, briefly mention what's new (max 2-3 sentences). Then
let the user decide what to look at. Examples:

- "Heads-up: cron auto-recovered last night's missed adjourn (see
  recovery/{file}). Also AUDITOR Patrol from Sunday found 3 stale wiki
  entries. Want to handle them now or later?"

- "Quick note: monthly ADVISOR review ran on the 1st — flagged SOUL drift
  on '专注产品' dimension. Full report at advisor-monthly-{date}.md."

If user says "show me" / "open X" → use Read tool to show the report.
If user says "deal with it later" / proceeds with other topic → drop the
notification thread, focus on user's actual ask.

If you're in /monitor mode, format this as a dashboard instead of inline
mention.

Spec source: pro/CLAUDE.md → Session Modes (v1.8.0) → cron-to-session bridge
</system-reminder>
EOF

exit 0
