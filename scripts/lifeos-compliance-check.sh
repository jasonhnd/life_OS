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

# ─── Detection: Cortex path (7 v1.7 failure modes — CX1-CX7) ────────────────
# Only meaningful when cortex_enabled: true in _meta/config.md. When the flag
# is false (v1.7.0-alpha default), CX checks are skipped entirely.
check_cortex() {
  local file="$1"
  local config_path="${2:-_meta/config.md}"

  # Cortex disabled? Skip silently.
  if [[ -f "$config_path" ]]; then
    if ! grep -qE '^cortex_enabled:[[:space:]]*true' "$config_path"; then
      return 0
    fi
  else
    # No config → assume disabled (default)
    return 0
  fi

  # CX1: Skip Pre-Router subagents (must launch all 3 before ROUTER triage)
  for agent in hippocampus concept-lookup soul-check; do
    if ! grep -qE "${agent} subagent" "$file"; then
      VIOLATIONS+=("CX1 (P1): Pre-Router subagent '${agent}' not invoked (Cortex enabled but agent absent)")
    fi
  done

  # CX2: Skip GWT arbitrator (must run after the 3 Cortex modules)
  if ! grep -qE 'gwt-arbitrator subagent' "$file"; then
    VIOLATIONS+=("CX2 (P1): GWT arbitrator not invoked (Cortex enabled but consolidation step missing)")
  fi

  # CX3: Missing [COGNITIVE CONTEXT] delimiters
  if ! grep -qF '[COGNITIVE CONTEXT' "$file"; then
    VIOLATIONS+=("CX3 (P1): [COGNITIVE CONTEXT] opening delimiter missing in ROUTER input")
  fi
  if ! grep -qF '[END COGNITIVE CONTEXT]' "$file"; then
    VIOLATIONS+=("CX3 (P1): [END COGNITIVE CONTEXT] closing delimiter missing in ROUTER input")
  fi

  # CX4: Hippocampus session cap exceeded — count session_id lines in hippocampus output
  # Note: `|| true` prevents grep -c (exit 1 on no match) from killing script under set -e
  hippo_count=$(awk '/hippocampus_output:/,/^[a-z_]+_output:/' "$file" | grep -cE '^[[:space:]]*- session_id:' || true)
  if [[ ${hippo_count:-0} -gt 7 ]]; then
    VIOLATIONS+=("CX4 (P1): hippocampus returned $hippo_count sessions (cap is 7)")
  fi

  # CX5: GWT signal cap exceeded — count signals in GWT [COGNITIVE CONTEXT] block
  gwt_signal_count=$(awk '/^\[COGNITIVE CONTEXT/,/^\[END COGNITIVE CONTEXT\]/' "$file" | grep -cE '^- ' || true)
  if [[ ${gwt_signal_count:-0} -gt 5 ]]; then
    VIOLATIONS+=("CX5 (P1): GWT composed $gwt_signal_count signals (cap is 5)")
  fi

  # CX6: Cortex isolation breach — peer subagent's root key in another's output
  # E.g., concept_lookup_output: appearing inside hippocampus subagent's response
  for agent in hippocampus concept_lookup soul_check; do
    for peer in hippocampus_output concept_lookup_output soul_check_output; do
      [[ "${agent}_output" == "$peer" ]] && continue
      if awk "/${agent} subagent/,/^[a-z]+_output:/" "$file" | grep -qE "^[[:space:]]*${peer}:"; then
        VIOLATIONS+=("CX6 (P0): isolation breach — $agent subagent received $peer in input")
      fi
    done
  done

  # CX7: Cortex write breach — any of the 4 read-only Cortex agents performed
  # a Write tool call. Heuristic: check transcript for "Write tool" with
  # context that suggests it was inside a Cortex subagent block.
  for agent in hippocampus concept-lookup soul-check gwt-arbitrator; do
    if awk "/${agent} subagent/,/^[a-z]+_output:|^Compliance/" "$file" | grep -qE 'Write\(|file_path.*=.*\.md.*write'; then
      VIOLATIONS+=("CX7 (P0): $agent subagent invoked Write tool (read-only contract violated)")
    fi
  done
}

# ─── Detection: Adjourn path (4 COURT-START-001 / v1.6.2 failure modes) ─────
check_adjourn() {
  local file="$1"

  # Class A3: Adjourn Pre-flight line missing
  if ! grep -qE '📝 Trigger:.*Action: Launch\(archiver\)' "$file"; then
    VIOLATIONS+=("A3 (P1): Adjourn Pre-flight line missing — expected '📝 Trigger: <word> → ... → Action: Launch(archiver) (4 phases)'")
  fi

  # Class C: Incomplete Phase — checklist must mark all 4 phases
  for phase_num in 1 2 3 4; do
    if ! grep -qE "Phase ${phase_num}[^a-zA-Z0-9]" "$file"; then
      VIOLATIONS+=("C (P0): Phase ${phase_num} not present in archiver Completion Checklist")
    fi
  done

  # Class D: Placeholder values
  for placeholder in "TBD" '{...}' '{actual' "pending (TBD)"; do
    if grep -qF "$placeholder" "$file"; then
      VIOLATIONS+=("D (P1): Placeholder value '$placeholder' found in Completion Checklist (should be concrete value)")
    fi
  done

  # Class E: Main-context Phase execution (Phase-specific keywords appearing
  # BEFORE the archiver subagent identity declaration would suggest the
  # orchestrator ran Phase content itself)
  for keyword in "扫描 wiki 候选" "wiki 候选 evidence_count" "scan wiki candidates" "concepts_activated:" "DREAM N1-N2" "DREAM N3 consolidate"; do
    if grep -qF "$keyword" "$file"; then
      # Check if it appears before archiver subagent identity (proxy for main-context exec)
      # Note: this is a content-level proxy; AUDITOR Mode 3 has the authoritative tool-call check
      if ! grep -qE '✅ archiver subagent.*Phase 1' "$file"; then
        VIOLATIONS+=("E (P0): Phase keyword '$keyword' present without archiver subagent identity declaration — likely main-context execution")
      fi
    fi
  done
}

# ─── Dispatch ────────────────────────────────────────────────────────────────
case "$SCENARIO" in
  start-session-compliance)
    check_start_session "$OUTPUT_FILE"
    # Cortex compliance also applies to Start Session (Step 0.5 fires there if enabled)
    check_cortex "$OUTPUT_FILE"
    ;;
  adjourn-compliance)
    check_adjourn "$OUTPUT_FILE"
    ;;
  cortex-retrieval)
    check_cortex "$OUTPUT_FILE"
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
