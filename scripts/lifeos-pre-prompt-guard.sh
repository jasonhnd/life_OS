#!/bin/bash
# Life OS Pre-Prompt Guard Hook
# ─────────────────────────────────────────────────────────────────────────────
# Detects Start Session / Adjourn / Review / Debate trigger words in user input.
# Injects HARD RULE reminder as <system-reminder> to prevent ROUTER from:
#   - Skipping subagent launch (Class A1)
#   - Skipping DIRECTORY TYPE CHECK in dev repo (Class A2)
#   - Skipping Pre-flight Compliance Check (Class A3)
#   - Fabricating non-existent paths as authority (Class B)
#   - Running archiver phases in main context (Class E)
#
# Created: 2026-04-21 (v1.6.3, COURT-START-001 fix)
# Installed by: scripts/setup-hooks.sh or manual .claude/settings.json
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ─── Input ───────────────────────────────────────────────────────────────────
# Claude Code passes hook payload as JSON via stdin.
# Expected shape: {"prompt": "...", "session_id": "...", ...}
INPUT=$(cat)

# Extract prompt text. Tolerate missing jq gracefully (pass-through).
if command -v jq >/dev/null 2>&1; then
  PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty' 2>/dev/null || echo "")
else
  # Fallback: naive grep (good enough for detecting leading trigger word)
  PROMPT=$(echo "$INPUT" | grep -oE '"prompt"\s*:\s*"[^"]*"' | sed 's/"prompt"\s*:\s*"\(.*\)"/\1/' || echo "")
fi

# If no prompt, pass through and exit.
if [[ -z "$PROMPT" ]]; then
  echo "$INPUT"
  exit 0
fi

# ─── Conservative false-positive guard (v1.6.3a) ────────────────────────────
# Reduces Class F false positives when user pastes content (transcripts, code,
# long quotes) containing trigger words mid-content.
#
# Two checks:
#   1. Whole prompt length ≤ 500 chars (long prompts = conversational/paste)
#   2. First non-empty line ≤ 100 chars (filters paste blocks with intros)
#
# Trigger regex then runs against the FIRST LINE only (was multiline before).
# See references/compliance-spec.md Class F.

PROMPT_LEN=${#PROMPT}
if [[ $PROMPT_LEN -gt 500 ]]; then
  echo "$INPUT"
  exit 0
fi

FIRST_LINE=$(echo "$PROMPT" | sed -n '/[^[:space:]]/{p;q;}')
LINE_LEN=${#FIRST_LINE}
if [[ $LINE_LEN -gt 100 ]]; then
  echo "$INPUT"
  exit 0
fi

# Use FIRST_LINE for trigger matching (not full multiline PROMPT).
PROMPT="$FIRST_LINE"

# ─── Trigger word taxonomy ───────────────────────────────────────────────────
# Covers all 9 themes' Start Session / Review / Adjourn / Debate triggers,
# plus the universal English words that work in any theme.
#
# Start Session: 上朝 开始 start begin はじめる 初める 開始 朝廷開始 閣議開始 朝礼 开会
# Review: 复盘 早朝 review 振り返り レビュー 報告 汇报 morning-court
# Adjourn: 退朝 散会 結束 adjourn done end 終わり お疲れ 閣議終了
# Debate: 朝堂议政 討論 讨论 debate comitia cabinet-session board-discussion 御前会議

START_RE='^[[:space:]]*(上朝|开会|开始|はじめる|初める|開始|朝廷開始|閣議開始|朝礼|start|begin|convene|open[[:space:]]session)'
REVIEW_RE='^[[:space:]]*(复盘|早朝|振り返り|レビュー|報告|汇报|review|report|brief[[:space:]]me|standup|morning[[:space:]]court)'
ADJOURN_RE='^[[:space:]]*(退朝|散会|结束|終わり|お疲れ|閣議終了|adjourn|done|end|dismiss|close[[:space:]]session)'
DEBATE_RE='^[[:space:]]*(朝堂议政|讨论|討論|御前会議|debate|comitia|cabinet[[:space:]]session|board[[:space:]]discussion|plenary[[:space:]]debate)'

# ─── Classify ────────────────────────────────────────────────────────────────
TRIGGER=""
AGENT=""
MODE=""
TEMPLATE=""

if echo "$PROMPT" | grep -qiE "$START_RE"; then
  TRIGGER=$(echo "$PROMPT" | grep -ioE "$START_RE" | head -1 | sed 's/^[[:space:]]*//')
  AGENT="retrospective"
  MODE="Start Session Mode (Mode 0)"
  TEMPLATE="🌅 Trigger: $TRIGGER → Theme: [auto-inferred] → Action: Launch(retrospective) Mode 0"
elif echo "$PROMPT" | grep -qiE "$ADJOURN_RE"; then
  TRIGGER=$(echo "$PROMPT" | grep -ioE "$ADJOURN_RE" | head -1 | sed 's/^[[:space:]]*//')
  AGENT="archiver"
  MODE="Adjourn 4-phase flow (archive → extract → DREAM → sync)"
  TEMPLATE="📝 Trigger: $TRIGGER → Action: Launch(archiver) subagent (4 phases end-to-end)"
elif echo "$PROMPT" | grep -qiE "$REVIEW_RE"; then
  TRIGGER=$(echo "$PROMPT" | grep -ioE "$REVIEW_RE" | head -1 | sed 's/^[[:space:]]*//')
  AGENT="retrospective"
  MODE="Review Mode (Mode 2, briefing only, no full sync)"
  TEMPLATE="🌅 Trigger: $TRIGGER → Action: Launch(retrospective) Mode 2"
elif echo "$PROMPT" | grep -qiE "$DEBATE_RE"; then
  TRIGGER=$(echo "$PROMPT" | grep -ioE "$DEBATE_RE" | head -1 | sed 's/^[[:space:]]*//')
  AGENT="council"
  MODE="3-round structured debate"
  TEMPLATE="🏛️ Trigger: $TRIGGER → Action: Launch(council) for 3-round debate"
else
  # No trigger detected, pass through silently.
  echo "$INPUT"
  exit 0
fi

# ─── Detect repo type for violations.md path ─────────────────────────────────
# Dev repo = has pro/agents/retrospective.md
# User repo = has _meta/config.md
# Other = no log
CWD=$(pwd)
VIOLATIONS_PATH=""
REPO_TYPE=""

if [[ -f "$CWD/pro/agents/retrospective.md" ]]; then
  VIOLATIONS_PATH="$CWD/pro/compliance/violations.md"
  REPO_TYPE="dev"
elif [[ -f "$CWD/_meta/config.md" ]]; then
  VIOLATIONS_PATH="$CWD/_meta/compliance/violations.md"
  REPO_TYPE="user"
else
  VIOLATIONS_PATH=""
  REPO_TYPE="other"
fi

# ─── Emit reminder (v1.6.3 five-layer defense, injected layer) ────────────────
# This output becomes part of the assistant's context before generating a response.
# Claude Code interprets stdout from UserPromptSubmit hooks as context injection.
cat <<EOF
<system-reminder>
🚨 LIFE OS HARD RULE · Trigger "$TRIGGER" detected (v1.6.3 COURT-START-001 fix · $REPO_TYPE repo)

REQUIRED (NOT optional — skipping any of these = violation logged to $VIOLATIONS_PATH):

1. Read pro/agents/${AGENT}.md BEFORE any other tool call. Do not use memory — read the file now.
2. Launch(${AGENT}) as independent subagent via Task tool, in: $MODE
3. Do NOT execute any step/phase in main context (no Read/Grep/Bash pretending to be the subagent)
4. Do NOT simulate subagent output by describing what it would do
5. Do NOT reference file paths you cannot verify exist. Verify via Glob/Read before citing.

Pre-flight Compliance Check (output this line BEFORE any tool call):

    ${TEMPLATE}

Then call Task(${AGENT}) as your first tool use.

─── Precedent ───────────────────────────────────────────────────────────────
COURT-START-001 (2026-04-19): ROUTER skipped retrospective subagent, simulated
18 steps inline, fabricated non-existent _meta/roles/CLAUDE.md path. Archived
in pro/compliance/2026-04-19-court-start-violation.md.

Five-layer defense against recurrence:
  1. This hook (you are reading the reminder now)
  2. SKILL.md Pre-flight Compliance Check (orchestrator-level gate)
  3. ${AGENT}.md Subagent Self-Check (agent-level gate)
  4. AUDITOR Compliance Patrol Mode (post-hoc audit)
  5. evals/scenarios/start-session-compliance.md (regression test)

Violation taxonomy (see references/compliance-spec.md):
  A1 · skip subagent | A2 · skip directory check | A3 · skip Pre-flight
  B · fabricate fact | C · incomplete phase | D · placeholder value
  E · main-context phase execution
</system-reminder>
EOF

# Pass through original input so Claude Code receives both reminder and prompt.
echo "$INPUT"
exit 0
