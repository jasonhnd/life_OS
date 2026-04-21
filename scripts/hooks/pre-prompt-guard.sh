#!/bin/bash
# Life OS · pre-prompt-guard.sh (v1.7 Sprint 1)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   UserPromptSubmit
# Matcher: *
# Exit:    0 always (a prompt cannot be blocked — only annotated)
# Timeout: 5s
#
# Purpose
#   Detect trigger words in first non-empty line of user prompt. When matched,
#   emit a <system-reminder> to stdout that Claude Code injects into the LLM
#   context. Forces subagent launch instead of main-context simulation.
#
# Solves
#   COURT-START-001 (2026-04-19) — ROUTER ran retrospective's 18 steps
#   inline, skipped Task(retrospective), fabricated pro/CLAUDE.md paths.
#
# Contract
#   references/hooks-spec.md §5.1 — trigger table, output format
#   references/compliance-spec.md — violation taxonomy (A1/A2/A3/B/C/D/E/F)
#
# Security
#   - Never treats stdin values as shell tokens
#   - Uses jq when present, bash-regex fallback otherwise
#   - False-positive guard: prompt >500 chars OR first line >100 chars → pass
# ─────────────────────────────────────────────────────────────────────────────

set -u
# Note: no pipefail — hook must never exit non-zero on input quirks.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$HOOK_DIR/_lib.sh"

# ─── Read stdin ─────────────────────────────────────────────────────────────
INPUT="$(cat)"
if [ -z "$INPUT" ]; then
  exit 0
fi

# ─── Extract prompt ─────────────────────────────────────────────────────────
PROMPT="$(lib_json_field "$INPUT" prompt)"
if [ -z "$PROMPT" ]; then
  exit 0
fi

# ─── False-positive guard (v1.6.3a, preserved in v1.7) ─────────────────────
# Long prompts = likely paste/quote content, not a real trigger invocation.
PROMPT_LEN=${#PROMPT}
if [ "$PROMPT_LEN" -gt 500 ]; then
  exit 0
fi

FIRST_LINE="$(printf '%s' "$PROMPT" | sed -n '/[^[:space:]]/{p;q;}')"
LINE_LEN=${#FIRST_LINE}
if [ "$LINE_LEN" -gt 100 ]; then
  exit 0
fi

# ─── Classify trigger ───────────────────────────────────────────────────────
CLASS="$(lib_classify_trigger "$FIRST_LINE")"
if [ -z "$CLASS" ]; then
  exit 0
fi

# Extract the actual matched word for nicer messaging.
case "$CLASS" in
  start)
    RE='^[[:space:]]*(上朝|开会|开始|はじめる|初める|開始|朝廷開始|閣議開始|朝礼|start|begin|convene|open[[:space:]]session)'
    AGENT="retrospective"
    MODE="Start Session Mode (Mode 0)"
    ;;
  adjourn)
    RE='^[[:space:]]*(退朝|散会|结束|終わり|お疲れ|閣議終了|adjourn|done|end|dismiss|close[[:space:]]session)'
    AGENT="archiver"
    MODE="Adjourn 4-phase flow (archive → extract → DREAM → sync)"
    ;;
  review)
    RE='^[[:space:]]*(复盘|早朝|振り返り|レビュー|報告|汇报|review|report|brief[[:space:]]me|standup|morning[[:space:]]court)'
    AGENT="retrospective"
    MODE="Review Mode (Mode 2, briefing only, no full sync)"
    ;;
  debate)
    RE='^[[:space:]]*(朝堂议政|讨论|討論|御前会議|debate|comitia|cabinet[[:space:]]session|board[[:space:]]discussion|plenary[[:space:]]debate)'
    AGENT="council"
    MODE="3-round structured debate"
    ;;
  *)
    exit 0
    ;;
esac

TRIGGER="$(printf '%s' "$FIRST_LINE" | grep -ioE "$RE" | head -1 | sed 's/^[[:space:]]*//')"

# ─── Detect repo type (purely for display in reminder) ──────────────────────
CWD="${PWD}"
REPO_TYPE="other"
if [ -f "$CWD/pro/agents/retrospective.md" ]; then
  REPO_TYPE="dev"
elif [ -f "$CWD/_meta/config.md" ]; then
  REPO_TYPE="user"
fi

VIOLATIONS_PATH="$(lib_detect_compliance_path "$CWD")"

# ─── Emit reminder ──────────────────────────────────────────────────────────
# This stdout is injected as a <system-reminder> by Claude Code.
cat <<EOF
<system-reminder>
🚨 LIFE OS HARD RULE · Trigger "$TRIGGER" detected (v1.7 · $REPO_TYPE repo)

REQUIRED (skipping any of these = violation logged to $VIOLATIONS_PATH):

1. Read pro/agents/${AGENT}.md BEFORE any other tool call. Do not use memory.
2. Launch(${AGENT}) as an independent subagent via the Task tool, in: $MODE
3. Do NOT execute any step/phase in main context (no Read/Grep/Bash pretending to be the subagent)
4. Do NOT simulate subagent output by describing what it would do
5. Do NOT reference file paths you cannot verify. Use Glob/Read to verify before citing.

Pre-flight Compliance Check (output this line BEFORE any tool call):

    🌅 Trigger: ${TRIGGER} → Action: Launch(${AGENT}) — ${MODE}

Then the FIRST tool call MUST be Task(${AGENT}).

─── Precedent ───────────────────────────────────────────────────────────────
COURT-START-001 (2026-04-19): ROUTER skipped retrospective subagent,
simulated 18 steps inline, fabricated _meta/roles/CLAUDE.md path.
Archived: pro/compliance/2026-04-19-court-start-violation.md.

Violation taxonomy (references/compliance-spec.md):
  A1 · skip subagent | A2 · skip directory check | A3 · skip Pre-flight
  B · fabricate fact | C · incomplete phase | D · placeholder value
  E · main-context phase execution
</system-reminder>
EOF

exit 0
