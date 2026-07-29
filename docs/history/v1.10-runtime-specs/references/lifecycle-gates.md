---
spec_id: lifecycle-gates.v1
description: 8 promotion transitions for any first-class life_OS object (SOUL dim, wiki entry, agent, spec, skill, decision). Each transition lists evidence required to promote. Used by ARCHIVER Phase 2 / DREAM N3 / ADVISOR drift detection.
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/governance.yml lines 16-66
introduced_in: v1.8.5
---

# Lifecycle Gates

> The 9 lifecycle stages from `references/agent-spec.md v2` / `references/wiki-spec.md v2` (and EOU 6 facets vocabulary) are: `candidate → draft → simulated → pilot → active → monitored → stable → deprecated → retired`. (SOUL dimensions use their own 4-state `lifecycle_stage` — `tentative / confirmed / dormant / deprecated` per `references/soul-spec.md` — NOT this 9-stage set.)
>
> Promotion between stages requires evidence. This file lists the 8 transitions + the evidence checklist for each. ARCHIVER Phase 2 promotion proposals MUST cite which evidence items are satisfied before recommending promotion.

## The 8 transitions

### 1. candidate → draft

Required evidence:
- ✅ Frontmatter exists with all required_top_level fields populated (per the relevant `*-spec.md` v2 schema)
- ✅ `purpose.statement` is concrete (names a failure prevented or decision improved, not just a process description)
- ✅ `operating_hypothesis` is stated in Given/can/within format
- ✅ At least one `stop_condition` declared
- ✅ `blast_radius.allowed_scope` and `blast_radius.forbidden_scope` declared
- ✅ `responsibility.{executor, reviewer, approver}` all named

Examples in life_OS:
- SOUL dim auto-created at confidence 0.3 → must have a real evidence count ≥ 2 before promotion to draft (`evidence_count >= 2 AND challenges == 0`).
- Wiki entry written by archiver Phase 2 → must pass 6 strict criteria + outlier reference slot populated.

### 2. draft → simulated

Required evidence:
- ✅ All required schema fields populated (no TBD placeholders except declared `open_questions`)
- ✅ At least one regression case exists in `evals/regression-fixtures/` covering a known failure mode
- ✅ `validation.deterministic` section non-empty (lists checks that can be run mechanically — slash command, AUDITOR scenario, etc.)
- ✅ `/check-spec-drift` returns CLEAN for this artifact
- ✅ Human reviewer has read and acknowledged

### 3. simulated → pilot

Required evidence:
- ✅ Simulation run recorded (`meta/runtime/<sid>/simulation-<artifact>.md`)
- ✅ No critical findings (F1/F3/F6a/F10/F14/F15/F17) from simulation
- ✅ Human reviewer sign-off on simulation results
- ✅ All `open_questions` resolved or explicitly deferred with rationale

### 4. pilot → active

Required evidence:
- ✅ At least 1 successful real-world invocation with trace evidence in `meta/runtime/<sid>/`
- ✅ Audit passed: AUDITOR Mode 3 returned PASS verdict on this artifact
- ✅ Regression suite passing (`/run-regression` clean)
- ✅ Named human owner approval (`approval.approver` is a real person identifier, not a role label like "user")

### 5. active → monitored

Required evidence:
- ✅ Active for at least one governance cycle without incident
- ✅ Incident history clean OR all incidents have diagnosis records + repair records (per `no_change_record` spec when no change made)
- ✅ Regression suite passing with no new failures introduced

### 6. monitored → stable

Required evidence:
- ✅ No structural changes needed for at least one governance cycle
- ✅ Full regression suite passing
- ✅ Maturity evidence at L5 or L6 (informal — life_OS doesn't have eou's L0-L6 hard validator)

### 7. any → deprecated

Required evidence:
- ✅ Documented reason for deprecation (`superseded` / `obsolete` / `net-negative`)
- ✅ Migration path documented for any consumers (e.g. legacy SOUL dim migration → `/migrate-soul-v2`)
- ✅ Successor artifact named (if applicable)
- ✅ Human owner approval

### 8. deprecated → retired

Required evidence:
- ✅ All known consumers have migrated (verified by `/check-spec-drift` → zero broken-path references)
- ✅ Final trace archived (`meta/v1.8.4-snapshot/` or equivalent)
- ✅ Frontmatter updated with `status: legacy` + retirement date

## Special transitions

### "any → deprecated" applies to all stages

A unit at any stage (even `candidate`) can be deprecated if it turns out to be unwanted. Skip the intermediate stages.

### Legacy 12-month coexistence (per D3)

For SOUL/wiki v1 entries during v1.8.5 → v2.0 migration window (2026-05 to 2027-05):
- Old v1 entries remain at their pre-v1.8.5 lifecycle stage
- New entries MUST use v2 schema from creation
- No forced migration; users can `/migrate-soul-v2` or `/migrate-wiki-v2` at their convenience
- After 2027-05-23, remaining v1 entries auto-flagged `lifecycle_stage: deprecated`

## Use cases

- **ARCHIVER Phase 2**: When proposing wiki promotion, must cite which transition + which evidence items satisfied.
- **DREAM N3 cycle**: Detects artifacts overdue for promotion (e.g. SOUL dim at `tentative` for >90 days → propose to confirm or deprecate).
- **ADVISOR drift detection**: Flags artifacts that drifted backward (e.g. `active` artifact with recent incidents but no repair record → recommend demoting to `pilot`).
- **AUDITOR Mode 3 lifecycle scenario** (Stage 7): Checks every artifact's lifecycle_stage matches the evidence available; mismatch = F11 LIFECYCLE_FAILURE.

## Source attribution

eou-foundry @ e4b12ce — `engine/governance.yml` lines 16-66 (`lifecycle_promotion_gates` 8 transitions). Adapted: simplified evidence checklists to fit life_OS LLM-native verification (vs eou's Python validator); added v1.8.5-specific "legacy 12-month coexistence" rule per D3.
