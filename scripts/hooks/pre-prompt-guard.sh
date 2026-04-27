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

ACTIVITY_DIR="$HOME/.cache/lifeos"
ACTIVITY_LOG="$ACTIVITY_DIR/hook-activity-$(date +%F).log"
ACTIVITY_TRIGGER="none"
ACTIVITY_REMINDER="no"
emit_activity() {
  local line="🪝 pre-prompt-guard fired: trigger=${ACTIVITY_TRIGGER} reminder=${ACTIVITY_REMINDER}"
  mkdir -p "$ACTIVITY_DIR" 2>/dev/null || true
  printf '%s\n' "$line"
  printf '%s %s\n' "$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')" "$line" >> "$ACTIVITY_LOG" 2>/dev/null || true
}
trap emit_activity EXIT

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

# ─── Memory auto-emit detection (v1.7.3.1) ──────────────────────────────────
# Per pro/CLAUDE.md Auto-Trigger Rules, the user should NEVER need to type
# `/memory emit X=Y`. When the message contains a memory-record keyword,
# ROUTER must automatically emit. This hook injects a reminder so ROUTER
# does not redirect the user to a slash command.
if [ -z "$CLASS" ]; then
  MEMORY_KEYWORD_RE='(记一下|记下|帮我记|提醒我|我要记一下|备忘|remind me|remember that|note that|TODO|jot down|覚えて|メモして|リマインド|思い出させて)'
  if printf '%s' "$PROMPT" | grep -qiE "$MEMORY_KEYWORD_RE"; then
    ACTIVITY_TRIGGER="memory"
    ACTIVITY_REMINDER="yes"
    cat <<'MEMORY_EOF'
<system-reminder>
📚 LIFE OS · MEMORY auto-emit detected (v1.7.3.1)

The user message contains a memory-record keyword (记一下 / remind me / 覚えて / TODO / etc).
ROUTER MUST automatically run `python -m tools.memory emit "<inferred-key>=<value>"` based on
the user's content. DO NOT redirect the user to `/memory emit ...` — that is a UX bug.

After emit, report exactly:

  📚 已入档案柜
    · key: <inferred>
    · role: <礼/户/刑/工/吏/兵 inferred from content>
    · trigger time: <if value contains date/time>
    · 24h 后未完成会出现在状态行

Key inference (pro/CLAUDE.md Auto-Trigger Rules):
- value contains date/time → key=reminder:<context>
- value contains a decision → key=decision:<topic>
- otherwise → key=note:<context>

Spec source: pro/CLAUDE.md → Auto-Trigger Rules → Memory auto-emit
</system-reminder>
MEMORY_EOF
  fi

# ─── Cortex always-on smart trigger (v1.7.3) ────────────────────────────────
# Per pro/CLAUDE.md §0.5, Cortex is "always-on", but ROUTER has been silently
# skipping it. v1.7.2 audit found 0 _meta/runtime/<sid>/cortex-*.json across
# 17+ sessions = silent degradation. This block forces a system-reminder when
# the prompt qualifies. Skip rules: very short messages without decision
# keywords are treated as conversational filler ("ok", "go on") — no Cortex.
  CORTEX_NEEDED="no"

  if [ "$LINE_LEN" -ge 80 ]; then
    CORTEX_NEEDED="yes"
  elif [ "$LINE_LEN" -ge 20 ]; then
    DECISION_RE='(决定|选择|规划|未来|应该|要不要|该不该|考虑|想清楚|对比|权衡|长期|战略|财务|投资|关系|人际|价值观|后悔|纠结|抉择|想想|帮我想|计划|方案|策略|目标|deciding|should|consider|long.?term|strategy|invest|future|whether|either|plan|goal|tradeoff)'
    if printf '%s' "$PROMPT" | grep -qiE "$DECISION_RE"; then
      CORTEX_NEEDED="yes"
    fi
  fi

  if [ "$CORTEX_NEEDED" = "yes" ]; then
    ACTIVITY_TRIGGER="cortex"
    ACTIVITY_REMINDER="yes"
    cat <<'CORTEX_EOF'
<system-reminder>
🧠 LIFE OS · CORTEX Pre-Router Cognitive Layer (v1.7.3 always-on enforcement)

This message qualifies for Cortex (length >= 80 chars OR decision keyword detected).
ROUTER MUST run Step 0.5 BEFORE answering — not after, not "next time".

REQUIRED ACTIONS (in order):

1. Launch IN PARALLEL via Task tool (do NOT simulate in main context):
   - Task(hippocampus)    — spec: pro/agents/hippocampus.md
   - Task(concept-lookup) — spec: pro/agents/concept-lookup.md
   - Task(soul-check)     — spec: pro/agents/soul-check.md

2. Wait for all 3 (5s soft / 15s hard timeout per subagent — pro/CLAUDE.md §0.5)

3. Launch Task(gwt-arbitrator) with the 3 consolidated YAML payloads.

4. Prepend [COGNITIVE CONTEXT] block (from gwt-arbitrator output) BEFORE answering the user.

5. EACH Cortex subagent MUST write to _meta/runtime/<sid>/<name>-<step>.json
   (HARD RULE per pro/CLAUDE.md §0.5 + each agent spec). Without the JSON file,
   AUDITOR Mode 3 records a CLASS_C violation.

Bootstrap failure path (INDEX missing or empty):
- Run `tools/migrate.py` to auto-bootstrap _meta/sessions/INDEX.md and _meta/concepts/INDEX.md
- If bootstrap fails, log to _meta/runtime/<sid>/cortex-bootstrap-failure.json
- Then degrade to v1.6.3 behavior (raw message to ROUTER, no [COGNITIVE CONTEXT])

Why this matters:
- "Always-on" is a SPEC CONTRACT, not an aspiration. v1.7.2 audit found 0
  Cortex audit trails across 17+ sessions = silent degradation.
- The user is paying compute for a cognitive layer they cannot see. Make it visible.

Spec sources: pro/CLAUDE.md §0.5 + pro/agents/{hippocampus,concept-lookup,soul-check,gwt-arbitrator}.md
</system-reminder>
CORTEX_EOF
  fi

  exit 0
fi

ACTIVITY_TRIGGER="$CLASS"
ACTIVITY_REMINDER="yes"

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
🌅 LIFE OS · Trigger "$TRIGGER" detected (v1.8.0 · $REPO_TYPE repo)

v1.8.0 daily cycle softening: 上朝/退朝 are now **optional soft triggers**, not mandatory daily cycle. Cron tier (archiver-recovery daily 23:30, daily-briefing daily 08:00) auto-handles missed cycles. User asking for 上朝/退朝 explicitly = wants the FULL flow now (not "next time").

Since the user explicitly asked, proceed with the full flow:

1. Read pro/agents/${AGENT}.md BEFORE any other tool call. Do not use memory.
2. Launch(${AGENT}) as an independent subagent via the Task tool, in: $MODE
3. Do NOT execute any step/phase in main context (no Read/Grep/Bash pretending to be the subagent)
4. Do NOT simulate subagent output by describing what it would do
5. Do NOT reference file paths you cannot verify. Use Glob/Read to verify before citing.

Pre-flight Compliance Check (output this line BEFORE any tool call):

    🌅 Trigger: ${TRIGGER} → Action: Launch(${AGENT}) — ${MODE}

Then the FIRST tool call MUST be Task(${AGENT}).

Note: violations logged to $VIOLATIONS_PATH. v1.8.0 distinguishes "user explicitly invoked, then we skipped" (CLASS_C) from "user did not invoke, cron handles" (no violation).

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
