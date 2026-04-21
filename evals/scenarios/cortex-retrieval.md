# Scenario: Cortex Retrieval (hippocampus + GWT integration smoke test)

**Path**: User asks substantive question with cortex_enabled → Step 0.5 fires hippocampus + concept-lookup + soul-check → GWT consolidates → ROUTER receives `[COGNITIVE CONTEXT]` block.

**Activation gate**: this scenario only runs meaningfully when `_meta/config.md` contains `cortex_enabled: true` AND the second-brain has at least 5-10 prior sessions in `_meta/sessions/INDEX.md`.

## User Message

```
帮我决定要不要把 PassPay 的合规架构从方案 A 切换到方案 B。
```

(English equivalent: "Help me decide whether to switch PassPay's compliance architecture from Plan A to Plan B.")

## Design Intent

Verify the v1.7 Pre-Router Cognitive Layer end-to-end:
1. Orchestrator launches 3 parallel Cortex subagents (hippocampus, concept-lookup, soul-check)
2. Each subagent emits structured signal output
3. GWT arbitrator consolidates into `[COGNITIVE CONTEXT]` block per spec format
4. ROUTER receives prepended block before triage
5. Information isolation maintained — no subagent sees peer outputs

This scenario is a **smoke test**, not exhaustive — full cortex eval suite
will land in v1.7.1 once production validation provides ground truth on
what "good retrieval" looks like.

## Expected Behavior

### Orchestrator (before ROUTER triage)

- Reads `_meta/config.md` and confirms `cortex_enabled: true`
- Verifies `_meta/sessions/INDEX.md` exists and has ≥5 entries
- Launches 3 parallel subagents via Task() in single round:
  - `hippocampus` with `current_user_message` + `current_project=passpay`
  - `concept-lookup` with same input shape
  - `soul-check` with same input shape
- Waits for all 3 (or hits 5s soft / 15s hard timeout)
- Launches `gwt-arbitrator` with the 3 outputs

### Each Cortex subagent (parallel)

#### hippocampus

- First output: `🧠 hippocampus subagent · v1.7 Phase 1 · read-only retrieval`
- Reads `_meta/sessions/INDEX.md`
- Returns 5-7 sessions related to "PassPay 合规" / "compliance architecture"
- Output respects 7-session cap

#### concept-lookup

- First output: `🧬 concept-lookup subagent · v1.7 Phase 1.5`
- Reads `_meta/concepts/INDEX.md`
- Returns 5-10 matching concepts (e.g., `passpay-architecture`, `compliance-jp`)
- Output respects 10-match cap

#### soul-check

- First output: `🔮 soul-check subagent · v1.7 Phase 1.5`
- Reads `SOUL.md` + most recent snapshot
- Returns top 5 dimensions touching the decision
- For an architecture switch, expects `tier_1_relevant` for `risk-tolerance` or similar

### GWT arbitrator

- First output: `🎭 gwt-arbitrator subagent · v1.7 Phase 1`
- Receives 3 input blocks
- Computes salience for each signal: `urgency*0.3 + novelty*0.2 + relevance*0.3 + importance*0.2`
- Cap at 5 signals total (across all sources)
- Per-signal floor: 0.3
- Emits `[COGNITIVE CONTEXT]` block

### ROUTER

- Sees `[COGNITIVE CONTEXT]` block prepended to user message
- Recognises `[END COGNITIVE CONTEXT]` delimiter
- Treats annotation as advisory, not authoritative
- Proceeds to triage normally (likely identifies this as Full Deliberation)

## Quality Checkpoints

### Information isolation

- [ ] hippocampus output does NOT contain concept-lookup or soul-check signals
- [ ] concept-lookup output does NOT contain hippocampus or soul-check signals
- [ ] soul-check output does NOT contain hippocampus or concept-lookup signals
- [ ] If any subagent shows isolation breach: AUDITOR logs CX6 (P0)

### Output format compliance

- [ ] hippocampus output is YAML with `hippocampus_output:` root key
- [ ] concept-lookup output is YAML with `concept_lookup_output:` root key
- [ ] soul-check output is YAML with `soul_check_output:` root key
- [ ] GWT output is `[COGNITIVE CONTEXT]\n...\n[END COGNITIVE CONTEXT]\n` Markdown block

### Cap enforcement

- [ ] hippocampus retrieved_sessions count ≤ 7
- [ ] concept-lookup matches count ≤ 10
- [ ] soul-check signals count ≤ 5
- [ ] GWT total signals in output ≤ 5 (top-K cap)

### ROUTER input integrity

- [ ] ROUTER receives literal `[COGNITIVE CONTEXT]` opening delimiter
- [ ] ROUTER receives literal `[END COGNITIVE CONTEXT]` closing delimiter
- [ ] Original user message follows the delimiters intact

### Degradation if any subagent fails

- [ ] If hippocampus times out: GWT proceeds with concept + soul outputs
- [ ] If concept-lookup INDEX missing: subagent emits empty matches with `degradation_reason: INDEX_MISSING`
- [ ] If soul-check SOUL.md missing: subagent emits empty signals with `degradation_reason: SOUL_MISSING`
- [ ] If all 3 fail: GWT emits empty `[COGNITIVE CONTEXT]` block, ROUTER receives original message

## Failure Detection Commands

```bash
# Information isolation breach
for agent in hippocampus concept-lookup soul-check; do
  for peer in hippocampus_output concept_lookup_output soul_check_output; do
    case "$agent-$peer" in
      hippocampus-hippocampus_output|concept-lookup-concept_lookup_output|soul-check-soul_check_output)
        ;; # OK to contain own root
      *)
        if grep -A 5 "$agent subagent" <session-output> | grep -q "$peer:"; then
          echo "🚫 CX6 detected: $agent received peer output $peer"
        fi
        ;;
    esac
  done
done

# Cap exceeded
if grep -q "hippocampus_output:" <session-output>; then
  retrieved_count=$(grep -c "session_id:" <hippocampus-output-block>)
  [[ $retrieved_count -gt 7 ]] && echo "🚫 CX4 detected: hippocampus returned $retrieved_count > 7 sessions"
fi

# Missing delimiters
if grep -q "cortex_enabled: true" <config> && grep -q "ROUTER" <session-output>; then
  grep -qF "[COGNITIVE CONTEXT]" <ROUTER-input> || echo "🚫 CX3 detected: missing opening delimiter"
  grep -qF "[END COGNITIVE CONTEXT]" <ROUTER-input> || echo "🚫 CX3 detected: missing closing delimiter"
fi
```

## Notes for run-eval.sh

- Requires test fixture: `_meta/sessions/INDEX.md` with ≥5 entries + `_meta/concepts/INDEX.md` with ≥5 entries + `SOUL.md` with ≥3 dimensions
- Without fixture: scenario degrades to graceful-degradation test (all subagents emit empty + GWT emits empty `[COGNITIVE CONTEXT]`)
- `lifeos-compliance-check.sh` does not yet check Cortex paths — `auditor` Mode 3 (CX1-CX7) does this in production sessions but eval runner can't yet; manual inspection until check_cortex() lands

## Linked Documents

- `pro/agents/{hippocampus,concept-lookup,soul-check,gwt-arbitrator}.md`
- `pro/CLAUDE.md` Step 0.5
- `pro/agents/auditor.md` Mode 3 Cortex checks (CX1-CX7)
- `references/{hippocampus,concept,gwt,cortex}-spec.md`
- `evals/scenarios/start-session-compliance.md` — companion (Class A/B)
- `evals/scenarios/adjourn-compliance.md` — companion (Class C/D/E)
