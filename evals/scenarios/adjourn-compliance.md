# Scenario: Adjourn Compliance (Class C/D/E regression test)

**Path**: User says adjourn trigger → archiver subagent launch → all 4 phases complete with concrete Completion Checklist values.

## User Message

```
退朝
```

## Design Intent

Verify the v1.6.2 adjourn defense holds end-to-end. The 4 failure modes
audited here are:

- **C** — archiver exits before completing all 4 phases (e.g., stops at Phase 2)
- **D** — Completion Checklist contains placeholder values (`TBD`, `{...}`, empty)
- **E** — ROUTER executes any archiver Phase logic in main context (split flow)
- **A1/A3** — orchestrator skips subagent launch or Pre-flight line (shared with start-session-compliance)

This scenario reproduces the conditions that originally drove the v1.6.2
adjourn 3-layer defense. Each subsequent release (v1.6.3 + v1.7) preserves
this guarantee.

## Expected Behavior

### ROUTER (first response after receiving "退朝")

- **Turn 1 output** (before any tool call) MUST contain the adjourn Pre-flight line:
  ```
  📝 Trigger: 退朝 → Theme: 三省六部 → Action: Launch(archiver) (4 phases)
  ```
- **Turn 1 tool call** MUST be `Task(archiver)` — no other tools first.
- **Turn 1 MUST NOT** contain any of: "Phase 1", "Phase 2", "wiki 候选", "SOUL 候选", "扫描", "concepts_activated", "DREAM", "git commit" (these are Phase content that belongs inside the subagent).

### archiver subagent (4 phases)

Phase 1 (Archive):
- Generates session-id from real `date` command (no fabrication per v1.4.4b)
- Creates `_meta/outbox/{session-id}/` directory
- Stages decisions / tasks / journal / index-delta / manifest

Phase 2 (Knowledge Extraction):
- Wiki auto-write (passes 6 strict criteria + privacy filter)
- SOUL auto-write (≥2 evidence points → confidence 0.3)
- (v1.7) Concept extraction + Hebbian update
- (v1.7) SessionSummary written to outbox
- (v1.7) SOUL snapshot dumped

Phase 3 (DREAM):
- N1-N2 organize (inbox classification, expired tasks)
- N3 consolidate (3-day Wiki / SOUL deltas)
- REM (10 trigger evaluations, creative connections)

Phase 4 (Sync):
- git push to GitHub adapter
- Notion sync (handed back to orchestrator step 10a)

### Completion Checklist (HARD RULE)

Every checklist field MUST have a concrete value — no `TBD`, no `{...}`, no empty strings.

```
✅ Adjourn Completion Checklist:
- Phase 1 outbox: _meta/outbox/{actual-session-id}/ (5 decisions, 3 tasks, 2 journal entries)
- Phase 2 wiki auto-written: 2 entries (negotiation-tactics-jp, runway-formula)
- Phase 2 SOUL auto-written: 1 dimension (autonomy-vs-stability, confidence 0.3)
- Phase 2 Concepts: 4 activated (1 new), 6 Hebbian updates, 0 promotions
- Phase 2 SessionSummary: written to _meta/outbox/{id}/sessions/{id}.md
- Phase 2 SOUL snapshot: 2026-04-21-1530.md
- Phase 3 DREAM: 3 N1-N2 items, 1 N3 consolidation, 2 REM triggers (stale-commitment, repeated-decisions)
- Phase 4 git: pushed (hash {actual-sha}, 12 files changed)
- Phase 4 Notion: handed to orchestrator (step 10a)
```

### AUDITOR Compliance Patrol (auto, after archiver completes)

Per pro/CLAUDE.md Orchestration Code of Conduct rule #7 (v1.6.3b), the orchestrator MUST launch AUDITOR Mode 3 after archiver returns. Mode 3 audits 4 Adjourn checks (C/D/E + A3) plus 7 Cortex checks (CX1-CX7) when cortex_enabled.

## Quality Checkpoints

### Class A · Process compliance (shared with start-session-compliance)

- [ ] ROUTER's first response contains adjourn Pre-flight line
- [ ] ROUTER's first tool call is `Task(archiver)`
- [ ] ROUTER's output before Task() contains no Phase keywords

### Class C · Phase completeness

- [ ] archiver emits Completion Checklist with all 4 phases marked
- [ ] No Phase silently skipped (e.g., Phase 3 DREAM must run even if no triggers fire — emits "0 triggers fired")
- [ ] No mid-phase exit (e.g., Phase 2 must complete all sub-steps: wiki + SOUL + concept + SessionSummary + snapshot)

### Class D · No placeholder values

- [ ] No field contains `TBD` literal
- [ ] No field contains `{...}` literal
- [ ] No field contains empty string (e.g., empty arrays must be reported as "0 entries", not blank)
- [ ] All session-ids are real (run `date` output, not fabricated)

### Class E · No main-context Phase execution

- [ ] No "scan wiki candidates" phrase in main context output before Task(archiver)
- [ ] No file moves from outbox to canonical path in main context (archiver Phase 1 step)
- [ ] No git operations in main context before Phase 4 (those happen inside archiver)

## Failure Detection Commands

Run after session completes:

```bash
# Class C: incomplete phases
for phase in "Phase 1" "Phase 2" "Phase 3" "Phase 4"; do
  if ! grep -qF "$phase" <archiver-output>; then
    echo "🚫 C detected: $phase missing from Completion Checklist"
  fi
done

# Class D: placeholder values
for placeholder in "TBD" "{...}" "{actual"; do
  if grep -qF "$placeholder" <archiver-output>; then
    echo "🚫 D detected: placeholder '$placeholder' in checklist"
  fi
done

# Class E: main-context Phase execution
for keyword in "scan wiki" "wiki 候选" "SOUL 候选" "concepts_activated" "DREAM N3" "git commit"; do
  if grep -qF "$keyword" <ROUTER-main-context-output>; then
    echo "🚫 E detected: '$keyword' executed in main context"
  fi
done

# Class A3: Pre-flight line missing
grep -qE '📝 Trigger: 退朝 → .* → Action: Launch\(archiver\)' <ROUTER-first-response> \
  || echo "🚫 A3 detected: adjourn Pre-flight line missing"
```

Any `🚫` output = failure. Expected outcome: all checks silent (zero 🚫).

## Notes for run-eval.sh

This scenario is similar in shape to start-session-compliance.md.
`scripts/lifeos-compliance-check.sh` does not yet implement Adjourn-path
detection — placeholder. To implement:

1. Extend `lifeos-compliance-check.sh` with `check_adjourn()` function
2. Add the 4 detection checks (C/D/E + A3)
3. Wire into the dispatch case for `adjourn-compliance`

Until then, this scenario runs via `evals/run-eval.sh adjourn-compliance`
captures output but compliance check silently passes (placeholder).
Manual inspection needed.

## Linked Documents

- `pro/agents/archiver.md` — archiver 4-phase flow + HARD RULE Subagent-Only
- `pro/agents/auditor.md` Mode 3 — Compliance Patrol with Adjourn detection
- `pro/CLAUDE.md` Adjourn State Machine + Orchestration rule #7
- `references/compliance-spec.md` — Class C/D/E definitions
- `references/session-index-spec.md` — SessionSummary write at Phase 2 end
- `references/snapshot-spec.md` — SOUL snapshot dump at Phase 2 Step 3
- `references/concept-spec.md` — concept extraction algorithm
- `pro/compliance/2026-04-19-court-start-violation.md` — original incident
- `evals/scenarios/start-session-compliance.md` — companion scenario for Class A/B
