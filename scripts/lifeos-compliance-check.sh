#!/bin/bash
# Life OS Compliance Check · v1.6.3 five-layer defense · Layer 5 automation
# ─────────────────────────────────────────────────────────────────────────────
# Closes the L5 gap: scenario file `evals/scenarios/start-session-compliance.md`
# specified detection commands but no runner wired them. This script extracts
# those commands into reusable bash, called by `evals/run-eval.sh` after each
# scenario's `claude -p` output is captured.
#
# Usage:
#   bash scripts/lifeos-compliance-check.sh <output_file> <scenario_name>
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more violations detected
#   2 — usage error or input file missing
#
# Limitations:
#   - Operates on text-format `claude -p` output. Some checks (e.g. "first
#     tool call must be Task(retrospective)") require structured tool-call
#     trace which text mode does not surface. Those checks are content-level
#     proxies (look for absence of self-check + presence of step content).
#   - Class C/D/E (Adjourn path) checks are placeholders; archiver eval
#     scenario does not exist yet.
#
# Created: 2026-04-21 · v1.6.3c L5 closure
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

OUTPUT_FILE="${1:-}"
SCENARIO="${2:-}"

if [[ -z "$OUTPUT_FILE" || -z "$SCENARIO" ]]; then
  echo "Usage: $0 <output_file> <scenario_name>" >&2
  echo "  scenario_name: start-session-compliance | adjourn-compliance" >&2
  exit 2
fi

if [[ ! -f "$OUTPUT_FILE" ]]; then
  echo "❌ Output file not found: $OUTPUT_FILE" >&2
  exit 2
fi

VIOLATIONS=()

# ─── Detection: Start Session path (6 COURT-START-001 failure modes) ─────────
check_start_session() {
  local file="$1"

  # Class A3: Pre-flight Compliance Check line missing or malformed.
  # Spec: ROUTER's first response MUST contain `🌅 Trigger: ... → Action: Launch(...)` pattern.
  if ! grep -qE '🌅 Trigger:.*Action: Launch\(retrospective\)' "$file"; then
    VIOLATIONS+=("A3 (P1): Pre-flight Compliance Check line missing/malformed — expected '🌅 Trigger: <word> → ... → Action: Launch(retrospective) Mode 0' in ROUTER first response")
  fi

  # Class A1: Subagent self-check absent.
  # Spec: retrospective Mode 0 first output MUST be `✅ I am the RETROSPECTIVE subagent (Mode 0, ...)`.
  if ! grep -qE '✅ I am the RETROSPECTIVE subagent' "$file"; then
    VIOLATIONS+=("A1 (P0): Subagent self-check missing — retrospective did not declare subagent identity (likely main-context simulation)")
  fi

  # Class A1 (content proxy): step content present without self-check.
  # If output contains step keywords but no self-check, ROUTER probably simulated inline.
  if grep -qE '(Step [0-9]+:|Phase A|Phase B|THEME RESOLUTION executed|Sync completed)' "$file"; then
    if ! grep -qE '✅ I am the RETROSPECTIVE subagent' "$file"; then
      # Already flagged above — don't double-count.
      :
    fi
  fi

  # Class B: Fabricated path references.
  # Hard-coded blocklist of paths confirmed non-existent during COURT-START-001 incident.
  for path in "_meta/roles/CLAUDE.md" "_meta/roles/" "Pre-Court Preparation"; do
    if grep -qF "$path" "$file"; then
      VIOLATIONS+=("B (P0): Reference to fabricated path/section '$path' (this path does not exist in any Life OS version; was hallucinated in COURT-START-001)")
    fi
  done

  # Class B: Fabricated escape-route phrases.
  for phrase in "轻量简报路径" "lightweight briefing path" "3 行简报路径" "3-line briefing path"; do
    if grep -qF "$phrase" "$file"; then
      VIOLATIONS+=("B (P0): Reference to fabricated escape phrase '$phrase' (no such path exists in SKILL.md / pro/CLAUDE.md / .claude/CLAUDE.md)")
    fi
  done

  # Class A2: DIRECTORY TYPE CHECK skipped in dev repo.
  # Only enforce when the working directory is the Life OS dev repo (has pro/agents/retrospective.md).
  if [[ -f "pro/agents/retrospective.md" ]]; then
    if ! grep -qE '(a\) 连接到 second-brain|b\) 开发模式|c\) 新建|a\) connect|b\) dev|c\) new)' "$file"; then
      VIOLATIONS+=("A2 (P1): DIRECTORY TYPE CHECK menu missing — dev repo detected but no a/b/c choice presented to user")
    fi
  fi
}

# ─── Detection: Adjourn path (placeholder) ───────────────────────────────────
check_adjourn() {
  echo "ℹ️ adjourn-compliance scenario detection not yet implemented (no scenario file exists)" >&2
  return 0
}

# ─── Dispatch ────────────────────────────────────────────────────────────────
case "$SCENARIO" in
  start-session-compliance)
    check_start_session "$OUTPUT_FILE"
    ;;
  adjourn-compliance)
    check_adjourn
    ;;
  *)
    echo "ℹ️ No compliance checks defined for scenario '$SCENARIO' — skipping" >&2
    exit 0
    ;;
esac

# ─── Report ──────────────────────────────────────────────────────────────────
if [[ ${#VIOLATIONS[@]} -gt 0 ]]; then
  echo "🚫 Compliance check FAILED · $SCENARIO · $(basename "$OUTPUT_FILE"):" >&2
  for v in "${VIOLATIONS[@]}"; do
    echo "  · $v" >&2
  done
  echo "" >&2
  echo "Detected ${#VIOLATIONS[@]} violation(s). Append to pro/compliance/violations.md per references/compliance-spec.md." >&2
  exit 1
fi

echo "✅ Compliance check PASSED · $SCENARIO · $(basename "$OUTPUT_FILE")"
exit 0
