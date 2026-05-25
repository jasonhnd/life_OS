---
spec_id: wiki.v2
description: Wiki entry schema v2. Borrows EOU 6 facets classification + operating_hypothesis + context_manifest 3-layer + reference_set 5 role slots (incl. outlier) + failure_modes + arguments_against from eou-foundry. Replaces v1 free-form prose schema. v1 entries coexist with v2 for 12 months per D3.
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, schemas/eou.schema.yml + captured-workflow.schema.yml + engine/eou-contract.md
introduced_in: v1.8.5
supersedes: wiki.v1 (v1.8.4 and earlier; v1 entries auto-deprecate 2027-05-23 per D3)
---

# Wiki Specification v2

Wiki is the system's knowledge archive — a living collection of reusable conclusions about the world. It lives in the `wiki/` directory of the second-brain.

> **v1.8.5 wiki v2 pivot — borrowed from eou-foundry**: Wiki entries are no longer free-form prose with confidence/evidence metadata. v2 entries have structured frontmatter (6 facets classification + operating_hypothesis + context_manifest + reference_set + failure_modes + arguments_against). Per Stage 5 of RFC `_meta/rfc/v1.8.5-cleanup-and-hardening.md`.

> **v2.0 future direction (v1.8.7 A1 spec proposal)**: `references/memory-tree-spec.md` (status: proposal) defines L0 → L1 → L2 → L3 cascade seal architecture for wiki + sessions, borrowed from `tinyhumansai/openhuman` Memory Tree. NOT implemented in v1.8.7 — see that spec for the future direction and rationale.

## Positioning (unchanged from v1)

| Storage | Records | Example |
|---------|---------|---------|
| `decisions/` | What you decided (specific, timestamped) | "2026-04-01: decided to use trust structure" |
| `user-patterns.md` | What you do (behavioral patterns) | "Tends to avoid financial dimensions" |
| `SOUL.md` | Who you are (values, personality) — **v2 schema per `references/soul-spec.md`** | "Truth over comfort" (priority 1) |
| `wiki/` | What you know — declarative knowledge — **v2 schema this doc** | "NPO lending in Japan has no 貸金業法 exemption" |
| `_meta/concepts/` | Synaptic graph — how ideas connect | "company-a-holding" node with weighted edges |
| `_meta/methods/` | Procedural memory — reusable workflows | "Refine documents in 5 escalating quality rounds" |

**Not wiki material** (goes elsewhere):
- Identity / values / personal preferences → `SOUL.md` v2
- Behavioral patterns → `user-patterns.md`
- Procedural workflows → `_meta/methods/`
- Concept-level associations → `_meta/concepts/`

## Principles (v1 preserved)

1. **Grows from zero** — wiki/ starts empty.
2. **Evidence-based** — Every entry links to supporting decisions/experiences.
3. **Auto-written under strict criteria** — archiver and DREAM auto-create when criteria pass. Users nudge by deletion.
4. **Title = Conclusion** — Title is the conclusion itself, not the topic.
5. **One conclusion per file** — No multi-topic compilations.

## v2 Entry Frontmatter (HARD schema)

Every new wiki entry from v1.8.5 onwards MUST have YAML frontmatter conforming to:

```yaml
---
# Identity
id: wn-{slug}                       # canonical, e.g. wn-japan-npo-lending-no-exemption
name: "<human-readable name>"
version: "0.1.0"                    # semver; bump on substantive changes

# v2 NEW: 6 facets classification (borrowed from eou-foundry eou.schema.yml)
classification:
  function: generate|specify|validate|diagnose|promote|refactor|audit|propose|activate|implement|retire
  target_object: "<what this entry is about>"
  automation_mode: deterministic|LLM_assisted|human_executed|hybrid
  authority_level: suggest_only|draft_only|write_candidate|write_inactive|mutate_active|approve|publish
  risk_level: low|medium|high|critical
  lifecycle_stage: candidate|draft|simulated|pilot|active|monitored|stable|deprecated|retired

# v2 NEW: operating_hypothesis (Given/can/within format)
operating_hypothesis: |
  Given <input/trigger>, under context <c>, this knowledge entry should
  produce <output/effect> within risk <r>.

# v2 NEW: context_manifest (eou eou-contract.md §context_manifest)
context_manifest:
  source_of_truth: []   # canonical artifacts this entry reads/cites
  supporting: []        # secondary context
  forbidden: []         # what must NOT be used as context (explicit exclusion)

# v2 NEW: reference_set 5 role slots (eou captured-workflow.schema.yml)
reference_set:
  aspirational: []         # ref + why; works/people the entry aspires toward
  anti_reference: []       # ref + why; explicit anti-examples
  boundary_case: []        # ref + why; edge cases
  mainstream_baseline: []  # ref + why; what's typical (for contrast)
  outlier: []              # MANDATORY for active+: "I dislike this but it succeeds"; anti-confirmation-bias

# v2 NEW: failure_modes (eou eou-contract.md §failure_modes)
failure_modes:
  known: []          # ways this knowledge gets misapplied
  warning_signs: []  # observable signals the knowledge is wrong or drifting
  repair_actions: [] # what to do when the knowledge misfires

# v2 NEW: arguments_against (eou generating_eou_candidate_required)
arguments_against: |
  This entry might be wrong because <reason>. Counter-evidence to watch for:
  <observable signal>.

# Existing v1 metadata (preserved)
confidence: 0.5         # 0-1, see §Confidence Calculation
evidence_count: 3
challenges: 0
created: YYYY-MM-DD
last_validated: YYYY-MM-DD
source: archiver|dream|user
---

# <Entry title = the conclusion>

<Body: 1-3 paragraphs of declarative knowledge>

## Evidence

- [YYYY-MM-DD] [decision/case] — [link]
- [YYYY-MM-DD] [decision/case] — [link]

## Challenges (if any)

- [YYYY-MM-DD] [contradicting case] — [link]
```

## v2 HARD Schema Constraints

### 1. Frontmatter 7 required field groups

- `id` (canonical wn-* slug)
- `classification` (all 6 facets populated; `target_object` non-empty string)
- `operating_hypothesis` (Given/can/within form; ≥30 chars)
- `context_manifest` (block exists; `source_of_truth` non-empty for active+ entries)
- `reference_set` (5 keys exist; lists may be initially empty for candidate/draft)
- `failure_modes` (block exists; can be empty lists initially)
- `arguments_against` (non-empty string; ≥20 chars; non-trivial)

**Enforced by**: AUDITOR Mode 5 (added in Stage 5 Day 13).

### 2. Reference_set `outlier` mandatory for active+ entries

For entries at `lifecycle_stage: active | monitored | stable`:
- `outlier` list MUST contain ≥1 entry
- Each outlier entry: `ref` (artifact/person/work) + `why` (why user dislikes it + why it nonetheless succeeds)

For `candidate | draft | pilot`:
- `outlier` MAY be empty initially
- Promotion to `active` blocked if outlier still empty (per `references/lifecycle-gates.md` transition 4)

### 3. `arguments_against` cannot be trivial

- ✅ "This entry might be wrong because Japanese tax law changed in 2024 and we haven't verified post-change. Counter-evidence: any 2024+ ruling citing 法 17."
- ❌ "Could be wrong" / "No counter-evidence" / "<TBD>"

LLM heuristic check: must mention specific failure mode + specific observable counter-signal.

## Lifecycle (v2 aligns to `references/lifecycle-gates.md`)

```
1. 🌱 candidate — archiver Phase 2 / DREAM N3 proposes
2. 📝 draft — frontmatter populated; body edited
3. 🧪 simulated — referenced in ≥1 actual decision
4. ✈️ pilot — referenced in 2+ independent decisions; no contradictions
5. ✅ active — outlier slot non-empty; reviewed
6. 📊 monitored — referenced regularly, no challenges last cycle
7. 💎 stable — long-validated, changes unlikely
8. 🗄️ deprecated — superseded or contradicted; reason documented
9. 📦 retired — no consumers reference it
```

## Archiver Phase 2 candidate gate (v2 hardened)

archiver Phase 2 MUST verify before writing a wiki candidate:

### Existing 6 criteria (v1 preserved)
1. Cross-project reusable
2. About the world, not about you
3. Zero personal privacy
4. Factual or methodological
5. ≥2 independent evidence
6. No contradiction with existing wiki (else increment challenges)

### v2 NEW: 4 additional gates

7. **Operating hypothesis can be drafted**: archiver attempts Given/can/within form ≥30 chars. If too vague → discard (impression, not knowledge).
8. **At least one outlier identifiable**: archiver attempts "I dislike this but it succeeds" example. If unable → write candidate but flag outlier-warn.
9. **arguments_against can be written**: archiver articulates what would falsify this entry. If unable ("obviously true with no failure mode") → discard or downgrade to journal (epistemic-hygiene fail).
10. **All 6 facets classifiable**: archiver assigns 6 facets. If any ambiguous → flag for user disambiguation.

## Legacy v1 entries (12-month coexistence per D3)

v1 wiki entries (created before v1.8.5):
- Remain readable by all roles
- Auto-flagged in DREAM N3: "🔄 v1 wiki entry: '<title>' — consider /migrate-wiki-v2"
- Default `lifecycle_stage` = `active`
- Default `arguments_against` = empty (does NOT pass v2 gate — flagged but tolerated)
- Default `outlier` = empty (flagged but tolerated)
- **2027-05-23** remaining v1 entries auto-marked `lifecycle_stage: deprecated`

## Migration via `/migrate-wiki-v2`

See `.claude/commands/migrate-wiki-v2.md`. Slash command:
1. Read each v1 wiki entry
2. Ask user to fill: 6 facets, operating_hypothesis, outlier reference, arguments_against
3. Write v2 frontmatter above v1 body (preserved)
4. Validate via AUDITOR Mode 5 before committing

User runs at convenience. No forced migration.

## Confidence Calculation (v1 preserved)

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| Confidence | Condition | Used by |
|------------|-----------|---------|
| < 0.3 | candidate, few evidence | archiver / DREAM only |
| 0.3 – 0.5 | draft to pilot | + REVIEWER reference |
| 0.5 – 0.7 | pilot to active | + PLANNER reference |
| > 0.7 | active+, low challenge | Full system reference (incl. ROUTER) |

**Note**: confidence is independent of lifecycle_stage in v2. A high-confidence entry at `candidate` is still candidate; promotion requires gates per `references/lifecycle-gates.md`, not confidence alone.

## How roles use wiki v2

| Role | Reads | Uses |
|------|-------|------|
| **ROUTER** | INDEX.md + relevant entry titles | Mentions if established knowledge exists |
| **PLANNER** | Active+ entries matching subject + outlier slot | "Known premise" inputs; outlier as adversarial check |
| **REVIEWER** | Entry `operating_hypothesis` + `arguments_against` | Cite contradicting entries; if contradiction, veto |
| **ADVISOR** | Entry usage patterns + challenges count | Flag entries not referenced in 6 months (→ dormant candidate) |
| **STRATEGIST** | Entry body + reference_set | Use boundary_case + outlier as conversation prompts |
| **ARCHIVER** | All entries (INDEX rebuild) | Phase 2 candidate gate (10 criteria); updates challenges on contradiction |
| **AUDITOR Mode 5 (new)** | All entry frontmatter | Schema audit (4 v2 hard checks) |

## Source attribution

eou-foundry @ e4b12ce. Borrowed:
- 6 facets classification: `schemas/eou.schema.yml` lines 22-76
- operating_hypothesis: `engine/eou-contract.md` line 34
- context_manifest 3-layer: `engine/eou-contract.md` lines 39-42
- reference_set 5 role slots: `schemas/captured-workflow.schema.yml`
- failure_modes 三件套: `engine/eou-contract.md` lines 60-63
- arguments_against: `schemas/eou.schema.yml` line 143

Adapted for life_OS: wiki entry is knowledge artifact (not EOU); v1 prose preserved alongside v2 frontmatter for 12-month coexistence.
