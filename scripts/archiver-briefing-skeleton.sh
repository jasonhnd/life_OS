#!/usr/bin/env bash
# v1.7.2.3 · archiver briefing skeleton — Bash output, LLM cannot omit.
# Read-only: emits the fixed six-H2 Adjourn Report frame with measured facts.
# Mirrors retrospective-briefing-skeleton.sh design; LLM only fills LLM_FILL placeholders.
# Complementary to archiver-phase-prefetch.sh: prefetch handles R11 audit trail,
# this script handles user-visible 6 H2 briefing framework.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P)"
SCRIPT_ROOT="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd -P)"

PWD_ROOT="${1:-$(pwd -P 2>/dev/null || pwd)}"
cd "$PWD_ROOT" 2>/dev/null || {
  printf 'ERROR: cannot cd to %s\n' "$PWD_ROOT" >&2
  exit 1
}
PWD_ROOT="$(pwd -P 2>/dev/null || pwd)"

trim_count() {
  tr -d '[:space:]'
}

yaml_value() {
  local key="$1"
  local file="$2"
  [[ -f "$file" ]] || return 1
  grep -m1 -E "^[[:space:]]*${key}:" "$file" 2>/dev/null \
    | sed -E 's/^[^:]+:[[:space:]]*//; s/[[:space:]]+#.*$//; s/^[[:space:]]+//; s/[[:space:]]+$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//'
}

count_files() {
  local dir="$1"
  local pattern="$2"
  [[ -d "$dir" ]] || {
    printf '0\n'
    return
  }
  find "$dir" -type f -name "$pattern" 2>/dev/null | wc -l | trim_count
}

ACTIVE_THEME=""
if [[ -f "_meta/config.md" ]]; then
  ACTIVE_THEME="$(yaml_value "active_theme" "_meta/config.md" 2>/dev/null || true)"
  [[ -n "$ACTIVE_THEME" ]] || ACTIVE_THEME="$(yaml_value "theme" "_meta/config.md" 2>/dev/null || true)"
fi
[[ -z "$ACTIVE_THEME" ]] && ACTIVE_THEME="zh-classical"

case "$ACTIVE_THEME" in
  zh-classical)     ARCH_NAME="📝 起居郎" ;;
  zh-government)    ARCH_NAME="📝 文书官" ;;
  zh-gov)           ARCH_NAME="📝 文书官" ;;
  zh-corporate)     ARCH_NAME="📝 会议纪要" ;;
  zh-corp)          ARCH_NAME="📝 会议纪要" ;;
  ja-meiji)         ARCH_NAME="📝 史官" ;;
  ja-kasumigaseki)  ARCH_NAME="📝 議事録官" ;;
  ja-corporate)     ARCH_NAME="📝 議事録係" ;;
  ja-corp)          ARCH_NAME="📝 議事録係" ;;
  en-roman)         ARCH_NAME="📝 Scribe" ;;
  en-usgov)         ARCH_NAME="📝 Recorder" ;;
  en-csuite)        ARCH_NAME="📝 Minutes Keeper" ;;
  *)                ARCH_NAME="📝 ARCHIVER" ;;
esac

# Locate latest outbox session id (best-effort)
LATEST_OUTBOX="$(find _meta/outbox -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -r | head -1)"
[[ -n "$LATEST_OUTBOX" ]] || LATEST_OUTBOX="(no outbox yet)"

# Stop hook health (presence in user settings)
STOP_HOOK_STATUS="unknown"
if [[ -f "$HOME/.claude/settings.json" ]]; then
  if grep -q 'life-os-stop-session-verify' "$HOME/.claude/settings.json" 2>/dev/null; then
    STOP_HOOK_STATUS="installed"
  else
    STOP_HOOK_STATUS="not installed (run setup-hooks.sh)"
  fi
fi

# Phase 1 outbox counts (best-effort, read latest outbox if exists)
DECISION_COUNT=0
TASK_COUNT=0
JOURNAL_COUNT=0
if [[ -d "$LATEST_OUTBOX" ]]; then
  DECISION_COUNT="$(count_files "$LATEST_OUTBOX/decisions" "*.md")"
  TASK_COUNT="$(count_files "$LATEST_OUTBOX/tasks" "*.md")"
  JOURNAL_COUNT="$(count_files "$LATEST_OUTBOX/journal" "*.md")"
fi

# Wiki / SOUL / DREAM stat
WIKI_COUNT="$(count_files "wiki" "*.md")"
SOUL_DIM_COUNT=0
[[ -f "SOUL.md" ]] && SOUL_DIM_COUNT="$(grep -cE '^### ' SOUL.md 2>/dev/null || printf '0')"
DREAM_COUNT="$(count_files "_meta/journal" "*-dream.md")"
LATEST_DREAM="$(find _meta/journal -name '*-dream.md' 2>/dev/null | sort -r | head -1)"
[[ -n "$LATEST_DREAM" ]] || LATEST_DREAM="none (this adjourn will write the first)"

# Git status
GIT_HEAD="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
GIT_STATUS_COUNT="$(git status --short 2>/dev/null | wc -l | trim_count)"

echo "${ARCH_NAME} · 退朝简报 · $(date -Iseconds)"
echo
echo "[FRESH ADJOURN · $(date -Iseconds) · trigger #1 of session · all 4 phases executed from scratch]"
echo
echo "✅ I am the ARCHIVER subagent · audit trail will be written to _meta/runtime/<sid>/archiver-*.json."
echo "✅ I am the ARCHIVER subagent · this is a FRESH adjourn invocation (trigger N of session)."
echo
echo "## Phase 0 · Hook Health"
echo
echo "- Stop hook (life-os-stop-session-verify): ${STOP_HOOK_STATUS}"
echo "- Hook fired evidence: <!-- LLM_FILL: hook_fired_evidence_or_skip -->"
echo
echo "## Phase 1 · Outbox"
echo
echo "- Latest outbox path: ${LATEST_OUTBOX}"
echo "- Archived: ${DECISION_COUNT} decisions · ${TASK_COUNT} tasks · ${JOURNAL_COUNT} journal entries"
echo "- session-id timestamp source: real system clock"
echo
echo "## Phase 2 · Knowledge Extraction (≤ 1500 tokens narrative)"
echo
echo "- Current wiki count: ${WIKI_COUNT} entries"
echo "- Current SOUL dimensions: ${SOUL_DIM_COUNT}"
echo "- LLM_FILL Phase 2 narrative below (combined wiki/SOUL/method/concept/strategic/SessionSummary/snapshot/last_activity, ≤ 1500 tokens):"
echo
echo "<!-- LLM_FILL: phase_2_extraction_narrative_combined -->"
echo
echo "## Phase 3 · DREAM (verbatim paste, no narrative cap on full content)"
echo
echo "- Existing DREAM reports: ${DREAM_COUNT}"
echo "- Most recent DREAM (before this adjourn): ${LATEST_DREAM}"
echo
echo "**LLM_FILL Phase 3 narrative (≤ 800 tokens · summary only)**:"
echo "<!-- LLM_FILL: phase_3_dream_narrative_summary -->"
echo
echo "**Verbatim DREAM journal (no length cap · LLM pastes full new dream report here from this adjourn cycle)**:"
echo "<!-- LLM_FILL: phase_3_dream_verbatim_full_paste -->"
echo
echo "## Phase 4 · Sync (git + Notion handoff)"
echo
echo "- Git HEAD: ${GIT_HEAD}"
echo "- Working tree: ${GIT_STATUS_COUNT} files to handle"
echo "- Git push status: <!-- LLM_FILL: git_push_status_after_archive -->"
echo "- Notion: deferred to orchestrator (archiver lacks MCP tools)"
echo "- Notion handoff payloads: <!-- LLM_FILL: notion_4_payload_receipts_or_deferred -->"
echo "- Step 10a no-ask handoff status: <!-- LLM_FILL: step_10a_handoff_status -->"
echo
echo "## Completion Checklist"
echo
echo "- AUDITOR Mode 3: <!-- LLM_FILL: auditor_mode_3_invoked_or_skipped -->"
echo "- Subagent invocation list: <!-- LLM_FILL: subagent_invocation_list_or_none_beyond_archiver -->"
echo "- Hook fired: see Phase 0 above"
echo "- Total tokens/cost: <!-- LLM_FILL: tokens_cost_if_telemetry_available -->"
echo
echo "📝 Session Closed · 退朝完成"

exit 0
