---
spec_id: failure-taxonomy.v1
description: Architecture-level failure taxonomy F1-F17 borrowed from eou-foundry. Complements life_OS process-violation taxonomy (A1/A2/A3/B/C/D/E/F in pro/compliance/violations.md). Every violations.md entry MUST carry both an A-F class tag and an F1-F17 tag from v1.8.5 onwards.
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/failure-taxonomy.yml
introduced_in: v1.8.5
---

# Failure Taxonomy F1-F17

> Architecture-level failure classes for AI agent governance systems. Each class has a definition + canonical repair. life_OS borrows this taxonomy from eou-foundry (Stage 3 Day 6 deliverable per RFC `meta/rfc/v1.8.5-cleanup-and-hardening.md`).

## How this relates to existing life_OS taxonomy

| Taxonomy | Layer | Examples | Where logged |
|---|---|---|---|
| **A1/A2/A3/B/C/D/E/F** (`references/compliance-spec.md`) | **Process violation** (人/流程层) | A1: skip retrospective Subagent; B: confabulated path; C: skip step; D: self-approve; E: missing publish; F: outbound PII leak | `pro/compliance/violations.md` |
| **F1-F17** (this doc) | **Architecture failure** (系统设计层) | F11: lifecycle stage mismatch; F12: spec drift; F14: silent judgment | Same `violations.md` (Stage 8 adds F-code column) |

**Both taxonomies apply to the same incident**. Example: "ROUTER skipped retrospective Subagent and confabulated a path" = `A1` (process) + `F12_DRIFT_FAILURE` (architecture).

## F1-F17 Reference

### F1 — INPUT FAILURE
- **Definition**: Required input is missing, malformed, stale, or ambiguous.
- **Repair**: Tighten input schema or repair input upstream.
- **Example in life_OS**: ROUTER receives `$ARGUMENTS` empty when slash command requires `--sid`.

### F2 — CONTEXT FAILURE
- **Definition**: Wrong context loaded or source of truth omitted.
- **Repair**: Repair `context_manifest`.
- **Example**: REVIEWER decides without reading SOUL.md; archiver Phase 4 reads stale `meta/config.md`.

### F3 — SCHEMA FAILURE
- **Definition**: Spec, input, output, or validator schemas diverge.
- **Repair**: Canonicalize schema and update validators.
- **Example**: `references/soul-spec.md` v1 vs SOUL.md actual fields drift.

### F4 — SCOPE FAILURE
- **Definition**: Agent/EOU/skill is too broad, too narrow, or mixes incompatible tasks.
- **Repair**: Split, merge, or redefine.
- **Example**: archiver doing both Phase 2 knowledge extraction AND Phase 1 archive before v1.7.3 carve-out.

### F5 — INSTRUCTION FAILURE
- **Definition**: Steps are unclear, contradictory, or non-executable.
- **Repair**: Rewrite execution procedure.
- **Example**: pro/agents/retrospective.md 18 steps where step 12 contradicts step 7.

### F6 — JUDGMENT FAILURE (subtypes)

#### F6a — STRUCTURAL_JUDGMENT
- **Definition**: Agent conflates two distinct judgments with different success criteria or responsible parties. Architecturally wrong.
- **Repair**: Responsibility-separation or split refactor.
- **Example**: REVIEWER doing both veto judgment AND audit judgment in one invocation.

#### F6b — COVERAGE
- **Definition**: Right judgment framed, no validation criteria to confirm it. Architecture correct, boundary unverifiable.
- **Repair**: Add judgment predicates, explicit success criteria, regression cases.
- **Example**: AUDITOR Mode 3 has scenario list but no expected output schema.

### F7 — VALIDATION FAILURE
- **Definition**: Validator passes invalid output or rejects valid output.
- **Repair**: Improve validation logic; add regression case at the boundary.
- **Example**: `/check-spec-drift` misses a broken-path reference; or false-positive on a valid legacy file.

### F8 — TOOL FAILURE
- **Definition**: Script, model, API, or external tool fails hard.
- **Repair**: Isolate dependency, add fallback, add stop condition.
- **Example**: `git push` fails mid-Phase-4 (remote unreachable); gh CLI returns 502.

### F9 — TRACE FAILURE
- **Definition**: Run cannot be reconstructed; trace missing or contradicts declared steps.
- **Repair**: Improve trace capture; every step writes to `meta/runtime/<sid>/`.
- **Example**: archiver Phase 4 completes but writes no `archiver-*.md` audit trail.

### F10 — RESPONSIBILITY FAILURE
- **Definition**: No clear owner, approval gate, or escalation path; OR same party executes and approves.
- **Repair**: Add responsibility mapping; separate executor/approver.
- **Example**: ROUTER both proposes and auto-applies a wiki write (no REVIEWER veto check).

### F11 — LIFECYCLE FAILURE
- **Definition**: Agent/EOU/entry judged by wrong maturity standard.
- **Repair**: Declare lifecycle_stage explicitly; apply matching validation level.
- **Example**: SOUL dim at `tentative` confidence treated as `confirmed` by REVIEWER reference. **A1 COURT-START class violations also map here** (Start Session trigger skipped retrospective Subagent = wrong lifecycle gate).

### F12 — DRIFT FAILURE
- **Definition**: Specs, scripts, docs, validators diverged; a change in one layer not propagated.
- **Repair**: Identify canonical layer (`schemas/` or `references/`), reconcile dependents, add vocabulary-sync check to CI/audit.
- **Example**: pro/agents/router.md references `pro/agents/narrator-validator.md` which was deleted. **B confabulated-path violations map here**.

### F13 — PERFORMANCE FAILURE
- **Definition**: Executes correctly but degrades at scale.
- **Repair**: Profile, bound bottleneck, add budget/timeout, tier-down automation_mode, split or promote to faster tool.
- **Example**: archiver Adjourn taking 25-30 min after v1.8.1 Wave 2 删除 Bash skeleton (accepted trade per architecture purity but borderline F13).

### F14 — SILENT_JUDGMENT_FAILURE (v1.8.5 new)
- **Definition**: Agent made contested choice without invoking any value from `SOUL.md` domain_values. Choice may have been correct but is unaccountable — no trace records what reasoning resolved the conflict. **Most dangerous agentic-judgment failure mode per V1 (Epistemic Integrity).**
- **Repair**: Require `value_invocations[]` entry for every contested case (per Stage 7 R12 trail update). Update agent execution to surface contested cases explicitly; require invocation or escalation.
- **Example**: REVIEWER veto on "career change to Singapore" without citing which SOUL dimension(s) drove the decision.

### F15 — VALUE_HIERARCHY_FAILURE (v1.8.5 new)
- **Definition**: Agent invoked a lower-priority SOUL dimension over a higher-priority one for the same contested case.
- **Repair**: Examine the `rule_conflict` in value_invocations entry; either revise SOUL priority order (via explicit edit + RFC) or treat invocation as wrong (add regression case).
- **Example**: REVIEWER cited "comfort" (priority 6) over "epistemic integrity" (priority 1) for a high-stakes decision.

### F16 — VALUE_DRIFT_FAILURE (v1.8.5 new)
- **Definition**: Agent's invocation pattern over multiple runs has diverged from SOUL's declared priority order without any SOUL amendment. **The system is silently rewriting its own constitution by precedent.**
- **Repair**: Triage the drift — either reset agent invocation behavior (regression suite) or formalize the drift as explicit SOUL amendment. Never let drift continue undocumented.
- **Example**: 3 consecutive REVIEWER decisions all favor priority-5 dim over priority-1 dim for similar cases without flagging the pattern.

### F17 — VALUE_HALLUCINATION_FAILURE (v1.8.5 new)
- **Definition**: Agent invoked a value not declared in SOUL.md. The invocation cites a `domain_value_id` that does not resolve.
- **Repair**: Validate `domain_value_id` against SOUL.md at invocation time; reject invocations with unknown ids. Add regression case for the specific hallucinated id pattern. Investigate whether prompt/training data introduced fabricated value.
- **Example**: ARCHIVER cites `dv-tradition-over-novelty` when SOUL only has `dv-truth-over-comfort`. (Direct B confabulation, also maps F17.)

## Diagnosis outcome (per eou-foundry governance.yml)

Not every diagnosed failure becomes a change. Record decisions explicitly per Stage 7 `no_change_record` protocol:

- **change**: A decision to change behavior. Record at `meta/decisions/<YYYY-MM>/dec-<YYYY-MM-DD>-<NNN>.md` with `type: change` (v1.9 schema).
- **no_change**: Decision made to accept current behavior. Record at `meta/decisions/<YYYY-MM>/dec-<YYYY-MM-DD>-<NNN>.md` with `type: no_change` (v1.9 schema — .md not .yml per DR-1.9.2; see `pro/CLAUDE.md` §"Decision Records" for full frontmatter). `reopen_condition` is mandatory. **A missing record looks identical to an uninvestigated incident.**

## Use cases

- Every `pro/compliance/violations.md` entry from v1.8.5 onwards carries F1-F17 tag in addition to A/B/C/D/E/F tag (Stage 8 Day 24).
- AUDITOR Mode 3 emits findings classified by F-code (Stage 7 Day 19 F14 scenario).
- DREAM REM cycle uses failure_modes.known/warning_signs from agent/entry v2 frontmatter (Stage 6) to detect early-warning patterns.

## Source attribution

eou-foundry @ e4b12ce — `engine/failure-taxonomy.yml` 98 lines. Adapted for life_OS: F14-F17 use SOUL.md domain_values instead of captured_workflow.domain_values; mapping to existing A/B/C/D/E/F process taxonomy added.
