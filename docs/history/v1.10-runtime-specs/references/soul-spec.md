---
spec_id: soul.v2
description: SOUL.md schema v2. Borrows constitutional layer design from eou-foundry domain_values + values-over-rules — X-over-Y formulation, priority total order {1..N} no ties no gaps, 3-8 dimension count cap, inclusion test 6-question gate, mandatory outlier role slot. Replaces v1 confidence-band-only schema. v1 entries coexist with v2 for 12 months (D3 per RFC).
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, dev-docs/06-values-over-rules.md + schemas/captured-workflow.schema.yml
introduced_in: v1.8.5
supersedes: soul.v1 (v1.8.4 and earlier; v1 entries auto-deprecate 2027-05-23 per D3)
---

# SOUL Specification v2

SOUL.md is the user's personality archive — a living constitutional value layer that records who the user is, what they value, and how value conflicts get resolved when rules collide. It lives in the second-brain root directory.

> **v1.8.5 SOUL v2 pivot — borrowed from eou-foundry**: SOUL is no longer a free-form list of dimensions with confidence bands. It is now a structured value stack with priority total order, X-over-Y formulation, and outlier role slot. Per Stage 4 of RFC `meta/rfc/v1.8.5-cleanup-and-hardening.md`.

## Why v2

v1 SOUL had three problems eou-foundry helped surface:

1. **No conflict resolver**: When two SOUL dimensions pointed in opposite directions (e.g. "career growth" vs "family time"), nothing in the schema said which won. Resolution was implicit.
2. **No anti-confirmation-bias**: SOUL grew toward "things I already agree with" because no field forced "things that contradict my preference but succeed in reality".
3. **No constitutional gate**: Anything could become a SOUL dim — "I prefer cold coffee" had the same status as "epistemic integrity is non-negotiable". No filter.

v2 fixes these via 5 schema borrowed from eou-foundry:
- **Priority {1..N}** total order — strict ranking, no ties, no gaps. Higher priority wins in conflict.
- **X-over-Y formulation** — every dim is a real trade-off, not a vague preference. Y cannot be a strawman.
- **Inclusion test** — 6-question gate before a dim enters SOUL.
- **Outlier role slot** — must contain reference cases the user dislikes but admits succeed.
- **3-8 dimension cap** — constitution cannot bloat into a wishlist.

## Principles (unchanged from v1)

1. **Grows from zero** — SOUL.md starts empty. No initialization required.
2. **Evidence-based** — Every entry links to decisions/behaviors that support it.
3. **Auto-written under strict criteria** — ADVISOR auto-updates after every decision. New dimensions auto-write at low confidence (0.3) when ≥2 evidence accumulate, then must pass v2 inclusion test before promotion.
4. **Contradictions are valuable** — Don't resolve them; surface them.

## Entry Format v2

Each SOUL dimension is a YAML block:

```yaml
- id: dv-{slug}                          # canonical, e.g. dv-truth-over-comfort
  formulation: "X over Y"                # HARD: must be "X over Y" form, Y not strawman
  priority: 1                            # int, total order 1..N, no ties, no gaps
  canonical_or_personal: canonical|personal
  lifecycle_stage: tentative|confirmed|dormant|deprecated  # v1 entries default to "confirmed" but flagged for migration
  source: dream|advisor|strategist|user
  created: YYYY-MM-DD
  last_validated: YYYY-MM-DD

  # v2 NEW: Inclusion test (6 questions, must answer ≥1 substantively)
  inclusion_test:
    failure_prevented: "<what failure does this value prevent?>"
    rule_conflict_resolved: "<what rule conflict does this value resolve?>"
    hidden_judgment_exposed: "<what hidden judgment does this value expose?>"
    false_success_resisted: "<what kind of false success does this resist?>"
    architectural_invariant: "<which life_OS invariant does this protect?>"
    danger_if_removed: "<would the system become dangerous if this value were removed?>"

  # v2 NEW: Failure modes
  failure_modes:
    known: []          # ways this value gets misapplied
    warning_signs: []  # observable signals the value is drifting
    repair_actions: [] # what to do when the value misfires

  # v1 fields (preserved for backward compat)
  confidence: 0.0
  evidence_count: 0
  challenges: 0

  # v1 prose fields (preserved)
  what_is: "<observed behavioral pattern>"
  what_should_be: "<user's stated aspiration>"
  gap: "<reality vs aspiration gap>"
  evidence: []
  challenges_log: []
```

## Required Schema Constraints (v2 HARD)

### 1. Dimension count: 3-8 total

- Minimum 3 — fewer than 3 means SOUL is not yet a value layer
- Maximum 8 — more than 8 means SOUL has bloated into a wishlist
- Includes tentative + confirmed (excludes dormant/deprecated)
- **Enforced by**: AUDITOR Mode 4 (Stage 4 Day 9)

### 2. Priority: total order {1..N}, no ties, no gaps

- Each dim has integer priority field
- Priorities must be 1, 2, 3, ..., N (consecutive, no skips)
- Two dims cannot share the same priority
- Conflict resolution: higher-priority (lower number) wins
- **Enforced by**: AUDITOR Mode 4

### 3. Formulation: "X over Y" form

- "Truth over comfort" ✅
- "Honesty over fluency" ✅
- "诚实是好的" ❌ (no Y, no trade-off)
- "Speed over slowness" ❌ (Y is strawman, no one prefers slowness)
- Y must be something the user genuinely could have chosen instead
- **Enforced by**: AUDITOR Mode 4 + `/migrate-soul-v2` rejects bad formulations

### 4. Inclusion test: ≥1 substantive answer

- 6 questions, at least 1 answered non-trivially
- "Speed", "elegance", "output volume", "fewer warnings" do NOT pass — these are local optimizations, not constitutional values
- **Enforced by**: AUDITOR Mode 4 + `/migrate-soul-v2`

### 5. Required role slots in reference_set (at top of SOUL.md)

```yaml
soul_reference_set:
  aspirational: []         # people/works the user aspires toward
  anti_reference: []       # people/works the user explicitly does NOT want to become
  boundary_case: []        # edge cases that test the value system
  mainstream_baseline: []  # what's "normal" in the user's context (for contrast)
  outlier: []              # MANDATORY: "I dislike this but it succeeds" — anti-confirmation-bias
```

- All 5 slots required (each list MAY be empty initially but the structure must exist)
- `outlier` slot SHOULD be non-empty within 30 days — DREAM N3 will flag if empty
- **Enforced by**: AUDITOR Mode 4 + archiver Phase 2 wiki-candidate gate (Stage 5)

## Lifecycle (v2)

```
1. 🌱 tentative — auto-created at low confidence (0.3), pending inclusion test
2. ✅ confirmed — passed inclusion test + ≥2 evidence + user acknowledged
3. 💤 dormant — no evidence accumulated in 90 days (not deleted, just inactive)
4. 🗄️ deprecated — superseded by another dim OR user explicitly removed
```

Promotion gates per `references/lifecycle-gates.md`:
- tentative → confirmed: passed inclusion_test 6Q gate + evidence_count ≥ 2 + challenges == 0 + user acknowledged
- confirmed → dormant: no evidence_count delta in 90 days (DREAM N3 auto-detects)
- any → deprecated: user explicit removal OR conflict resolution declared a winner among contradicting dims

## Confidence Calculation (v1 preserved)

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| Confidence | Condition | System Behavior |
|------------|-----------|----------------|
| < 0.3 | tentative, few data points | Only ADVISOR references |
| 0.3 – 0.6 | Moderate evidence | ADVISOR + REVIEWER reference |
| 0.6 – 0.8 | Strong evidence | + PLANNER references |
| > 0.8 | Deeply validated, low contradiction | Full system reference (including ROUTER) |

**Note**: Priority field is independent of confidence. A priority-1 dim at confidence 0.4 still wins conflicts against a priority-3 dim at confidence 0.95 — confidence affects WHO reads the dim, priority affects WHICH dim wins in conflict.

## How Roles Use SOUL v2

| Role | Reads | Uses |
|------|-------|------|
| **ROUTER** | priority 1-3 dims + red lines + reference_set | Sharper intent clarification; risk-domain triage (per `references/risk-domains.md`) |
| **PLANNER** | confidence ≥ 0.6 dims + priority order | Auto-adds relevant dims to planning; planning must declare which top-3 priority dims it operationalizes |
| **REVIEWER** | All confirmed dims + priority + inclusion_test | Value consistency check; cites priorities in verdict; must populate `value_invocations[]` in R12 trail per Stage 7 (avoids F14) |
| **ADVISOR** | All entries + evidence/challenge counts | Behavioral audit; reinforces or challenges; proposes priority swaps |
| **STRATEGIST** | unresolved contradictions + worldview | Recommends thinkers addressing specific tensions |
| **ARCHIVER (DREAM)** | All entries | DREAM N3 discovers candidates, updates counts, proposes lifecycle transitions, flags outlier-empty for 30+ days |

## Auto-Write Mechanism v2

When ADVISOR proposes a new dimension:

1. **Pre-flight**: Check current dim count. If already at 8 → suggest deprecating a low-priority dim before adding.
2. **Auto-formulation**: ADVISOR proposes `X over Y` form. If only X is clear (no real Y) → flag as "preference, not value" and skip.
3. **Inclusion test**: ADVISOR drafts answers to 6 questions. Must produce substantive answer to ≥1.
4. **Priority slot**: New dim defaults to priority N+1 (bottom). User may re-rank during next session.
5. **Write at tentative**: confidence 0.3, lifecycle_stage tentative.
6. **Promotion**: After ≥2 evidence + user acknowledges → flip to confirmed.

## Legacy v1 entries (12-month coexistence per D3)

v1.8.5 ships with `references/soul-spec.md` v2 as authoritative. Existing v1 SOUL entries:

- Remain readable by all roles (legacy mode)
- Auto-flagged in DREAM N3 reports: "🔄 v1 entry: 'risk attitude' — consider v2 migration via /migrate-soul-v2"
- Default `priority` field assigned by creation order (oldest = priority 1) for legacy reads
- Default `lifecycle_stage` = confirmed (since they passed v1 confidence threshold)
- Default `formulation` field = empty (does NOT pass v2 inclusion test — flagged but tolerated)
- After **2027-05-23**, remaining v1 entries auto-marked `lifecycle_stage: deprecated`

User can migrate at convenience via `/migrate-soul-v2` slash command. No forced migration.

## Migration via `/migrate-soul-v2`

See `.claude/commands/migrate-soul-v2.md`. Slash command:
1. Reads existing SOUL.md
2. For each v1 dim, asks user: formulate as "X over Y"; assign priority; answer 1+ inclusion test question
3. Writes v2 YAML block alongside v1 prose (preserved)
4. Validates via AUDITOR Mode 4 before committing

## Use cases

- **REVIEWER veto**: MUST cite `value_invocations[]` with `domain_value_id` from SOUL when contested case detected. Empty value_invocations on contested case = F14 silent judgment per `references/failure-taxonomy.md`.
- **PLANNER trade-off**: When two domain reports conflict, PLANNER reads SOUL priority order and proposes resolution citing winning dim's `id` + `priority`.
- **archiver Phase 2 candidate gate**: New wiki entries that touch values MUST operationalize ≥1 top-3 SOUL dim (Stage 5 wiki schema requirement).
- **AUDITOR Mode 4 (NEW v1.8.5)**: Audits SOUL.md schema compliance — count 3-8, priority total order no gaps, formulation X-over-Y, inclusion_test ≥1 answer, reference_set 5 slots present.

## Source attribution

eou-foundry @ e4b12ce. Borrowed:
- 3-8 cap + priority total order: `schemas/captured-workflow.schema.yml` domain_values_minimum_count / maximum_count / priority constraints
- X-over-Y formulation: `schemas/captured-workflow.schema.yml` `formulation_rule`
- Inclusion test 6Q: `dev-docs/06-values-over-rules.md` "Inclusion test" section
- Outlier role slot: `schemas/captured-workflow.schema.yml` `reference_set_required_role_slots` (outlier description: "I dislike this but it succeeds")
- Failure modes 三件套: `engine/eou-contract.md` failure_modes.known/warning_signs/repair_actions

Adapted for life_OS: SOUL is person-scope (not app-scope like captured_workflow); lifecycle_stage simplified to 4 states (vs eou's 9); confidence-band system preserved alongside priority.
