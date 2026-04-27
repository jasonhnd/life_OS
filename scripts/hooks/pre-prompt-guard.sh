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
📚 LIFE OS · MEMORY auto-emit detected (v1.8.0 pivot · LLM-direct · spec since v1.7.3.1)

The user message contains a memory-record keyword (记一下 / remind me / 覚えて / TODO / etc).
ROUTER MUST automatically write a memory file using the Write tool. DO NOT redirect the
user to `/memory emit ...` — that is a UX bug. DO NOT call `python -m tools.memory` —
that module was deleted in v1.8.0 pivot.

Steps:
1. Infer key (one of):
   - value contains date/time → `key=reminder:<context>`
   - value contains a decision → `key=decision:<topic>`
   - otherwise → `key=note:<context>`
2. Sanitize key for filename: `:` → `__`, `/` → `_`
3. Infer role: 户 (money) / 刑 (risk) / 工 (health/infra) / 礼 (relations/learning) / 吏 (people) / 兵 (execution)
4. Write file at `~/.claude/lifeos-memory/<sanitized-key>.json`:
   ```json
   {
     "value": "<original text>",
     "role": "<inferred>",
     "created": "<ISO8601>",
     "trigger_time": "<if value contains date/time, else omit>"
   }
   ```
5. Report exactly:

  📚 已入档案柜
    · key: <inferred>
    · role: <inferred>
    · trigger time: <if any>
    · 24h 后未完成会出现在状态行

Spec source: pro/CLAUDE.md → Auto-Trigger Rules → Memory auto-emit + scripts/commands/memory.md
</system-reminder>
MEMORY_EOF
  fi

# ─── Monitor mode auto-detection (v1.8.0 pivot · natural language only) ─────
# Per user feedback "这个不能要任何命令全部都要自然语言", monitor mode must be
# triggered by natural language, not slash command. The /monitor slash command
# remains as backup mode but is no longer the primary path.
  MONITOR_KEYWORD_RE='(监控模式|进监控|进 monitor|开监控|监控控制台|看一下系统状态|看系统状态|看 cron|看cron|看维护状态|维护控制台|ops console|monitor mode|enter monitor|open monitor|看 lifeos 状态|进运维)'
  if printf '%s' "$PROMPT" | grep -qiE "$MONITOR_KEYWORD_RE"; then
    ACTIVITY_TRIGGER="monitor"
    ACTIVITY_REMINDER="yes"
    cat <<'MONITOR_EOF'
<system-reminder>
📡 LIFE OS · MONITOR mode auto-detected (v1.8.0 pivot · natural language)

The user message contains a monitor-mode keyword (监控模式 / 进 monitor / 看系统状态 /
ops console / etc). ROUTER MUST launch the `monitor` subagent via Task tool. DO NOT
redirect the user to `/monitor` — that is a UX bug.

Steps:
1. Launch `Task(subagent_type=monitor)` with the user's original message
2. Monitor subagent reads `pro/agents/monitor.md` and behaves per spec:
   - Scans 10 maintenance task timestamps
   - Reads inbox notifications + recent reports
   - Reads recent violations
   - Generates dashboard for user
3. While in monitor mode (until user says "退出 monitor" / "exit monitor"):
   - DO NOT engage business deliberation
   - DO NOT trigger Cortex pull-based subagents
   - DO NOT run 上朝/退朝
   - DO accept "跑 X" / "看 X 详情" / "都跑" / "处理 wiki stale" → execute via prompts
4. On exit ("退出 monitor" / "exit monitor"), tell user: "monitor 模式已退出，回到普通 session 模式"

Spec source: pro/agents/monitor.md + scripts/commands/monitor.md (backup mode)
</system-reminder>
MONITOR_EOF
  fi

# ─── Cortex always-on enforcement REMOVED in v1.8.0 pivot ───────────────────
# v1.7.3 forced 4-subagent launch (hippocampus/concept-lookup/soul-check/
# gwt-arbitrator) on every qualifying message. v1.8.0 pivot moves Cortex to
# pull-based: ROUTER decides when to launch them via Task tool. No more
# always-on hook injection. See pro/CLAUDE.md §0.5 (rewritten) for the new
# pull-based ROUTER guidance.
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
