# Cortex Specification

Cortex is the Life OS cognitive layer — the pre-router mechanism that loads cross-session memory, concept graphs, and multi-source signals into every decision workflow. It is a Layer 2 architectural upgrade, not a new layer. Introduced in v1.7.

## Positioning

In the Life OS naming system, Cortex sits alongside the other personal-archive modules:

| Module | What it records | Scope |
|--------|----------------|-------|
| SOUL | Who you are (identity, values) | Personality |
| Wiki | What you know about the world | Knowledge |
| DREAM | What is discovered offline | Sleep-phase processing |
| STRATEGIC-MAP | How you are positioned | Cross-project strategy |
| **Cortex** | **How you think** | **Pre-router cognition** |

Cortex does not replace any existing module. It provides ROUTER with an annotated input — user message plus memory, concept, and SOUL signals — so downstream agents operate in context rather than in a vacuum.

---

## Principles

1. **Layer-2 upgrade, not a new layer** — Life OS already has three layers (Engine + Theme + Locale). Cortex is a capability extension inside Layer 2.
2. **ROUTER receives annotated input, not raw message** — Cortex produces cognitive annotations; ROUTER's triage rules are unchanged.
3. **Markdown-first, always** — every Cortex artefact is `.md + YAML frontmatter`. No SQLite, no Python runtime, no cron, no external secrets.
4. **Grounded generation** — every substantive claim in Cortex output must cite a signal_id. No confabulation.
5. **Graceful degradation** — if any Cortex subagent fails, the system falls back to v1.6.2a behaviour (raw message to ROUTER).
6. **Universal edition only** — there is no premium or home-use variant. One behaviour for all users.

---

## Problem Cortex Solves

Before v1.7, Life OS touched long-term memory only at session boundaries — RETROSPECTIVE reads at the start, ARCHIVER writes at the end. Between those two points, all decisions were made from the current conversation alone. The 16-subagent checks-and-balances structure was strong, but the cognitive substrate those agents shared was empty:

- PLANNER planned without knowing how the user had decided similar subjects in the past.
- Six domains analysed without knowing which concepts connected to which.
- REVIEWER checked consistency inside the current decision, not across sessions.
- After adjourn, only SOUL and Wiki auto-writes left a trace — no concept graph, no synapse reinforcement.

Users felt this as "the AI is careful inside a session but forgets between sessions." Cortex fixes this by making cross-session memory and concept graphs a first-class input to every workflow.

The failure mode is not that any single agent is weak — each of the 16 agents does its job well. The failure mode is that agents never see what other sessions learned. A PLANNER facing a financial decision in session 412 does not know that session 198 already landed on a conclusion about the same entity, because nothing carries that conclusion forward except the raw `_meta/journal/*.md` files, which nobody reads except at explicit user request. Cortex makes that carry-forward automatic.

---

## Four Core Mechanisms

Cortex consists of four mechanisms. Each has its own spec file. This document is the overall architecture.

### 1. Hippocampus — Real-time cross-session retrieval

Cortex is always-on in v1.7.2, so every user message triggers a hippocampus subagent unless the workflow is degrading because required local artifacts or subagents are unavailable. Three-wave spreading activation:

- Wave 1: direct match (keyword or concept_id hits)
- Wave 2: strong connections (synapse weight ≥ 3)
- Wave 3: weak connections as sub-threshold pre-activation (weight < 3)

Output: top 5-7 relevant historical sessions as a memory signal, emitted to the GWT arbitrator.

Implementation relies on a two-stage scan: ripgrep filters `_meta/sessions/INDEX.md` (a compiled flat file of one-line session summaries) down to candidate sessions within milliseconds; the subagent then reads only the matched summaries (typically 15-20 lines) and returns the final top 5-7. At 1000 sessions × 200 characters per summary (≈600 bytes per UTF-8 encoded CJK summary, ≈200 bytes per ASCII-only summary) the full index is roughly 200KB–600KB depending on content language — trivial to scan in either case.

Full spec: `references/hippocampus-spec.md`.

### 2. GWT Arbitrator — Salience competition

Based on Stanislas Dehaene's Global Neuronal Workspace theory. Multiple parallel modules produce signals; the arbitrator computes salience for each and broadcasts the top-K. The strongest signals "ignite" and enter the cognitive annotation passed to ROUTER.

Salience formula (Phase 1, weighted sum of four dimensions):

```
salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2
```

Salience is not self-reported. Modules emit raw scores; the arbitrator adjusts based on cross-signal coherence. Signals are also typed — `memory`, `concept_link`, `identity_check`, and in later phases `emotion` and `prediction` — and each type has a confidence floor below which the arbitrator discards the signal entirely. Inhibitory signals (vetoes) follow a stricter schema with required reasoning_chain.

Full spec: `references/gwt-spec.md`.

### 3. Narrator Layer — Grounded generation with citations

Before the Summary Report is shown to the user, the narrator layer wraps substantive claims with signal_id citations. This prevents the Gazzaniga left-brain-interpreter failure mode (confabulating plausible explanations for decisions).

Two categories of output:

- **Substantive claim** — must carry a signal_id citation. Example: "historically you have been conservative in similar decisions."
- **Connective tissue** — no citation required. Example: "let us look at this together."

A validator subagent (Sonnet-tier Claude Code subagent — no external API) checks citations before the report is released. Invalid citations trigger a rewrite.

The split between substantive and connective is pragmatic, not theoretical. Requiring every sentence to carry a citation would produce machine-stamped output that reads like a legal brief. Citation discipline is about the load-bearing claims — the assertions a user could challenge — not about conversational glue. Phase 2 runs with per-claim granularity; if the output feels over-annotated in practice, granularity can coarsen to per-paragraph without weakening the anti-confabulation guarantee.

Full spec: `references/narrator-spec.md`.

### 4. Synapses + Hebbian — Concept graph with use-it-or-lose-it reinforcement

Each concept is a markdown file under `_meta/concepts/{domain}/{concept}.md`. Edges (synapses) live in the concept's own frontmatter. Co-activation increases edge weight by +1 (Hebbian rule); long unused edges decay.

Four permanence tiers — identity, skill, fact, transient — determine decay curve shape. Decay runs every adjourn, driven by ARCHIVER Phase 2.

Each concept carries a three-tier status: `tentative` (first-seen, not yet confirmed), `confirmed` (multiple activations, stable identity), and `canonical` (high-activation, widely cross-referenced). Promotion is one-directional under normal use, but the three-tier undo mechanism (see Design Principles) allows demotion. The reverse edge index (`SYNAPSES-INDEX.md`) is rebuilt on every Hebbian update; it is a compiled artefact, never hand-edited.

Full spec: `references/concept-spec.md`.

---

## Workflow Integration

Cortex adds two steps to the existing 11-step workflow. Existing step numbers do not change.

```
Step 0:    Pre-Session Preparation (ROUTER + RETROSPECTIVE parallel) — unchanged
Step 0.5:  Pre-Router Cognitive Layer — NEW
Step 1:    ROUTER Triage — receives annotated input
Step 2-6:  unchanged
Step 7:    Summary Report — unchanged
Step 7.5:  Narrator validation — NEW (Phase 2, Full Deliberation only)
Step 8-9:  unchanged
Step 10:   ARCHIVER Phase 2 — extended (see below)
Step 11:   STRATEGIST (optional) — unchanged
```

### Step 0.5 — Pre-Router Cognitive Layer

In v1.7.2, Step 0.5 is attempted for every user message, including Start Session triggers. It runs after RETROSPECTIVE housekeeping / Pre-Session Preparation when those exist and before ROUTER Triage.

Before spawning Cortex subagents, the orchestrator checks `_meta/sessions/INDEX.md`. If the index is missing or empty, the orchestrator runs `tools/migrate.py` to auto-bootstrap before Step 0.5. If bootstrap fails, the workflow does not block: ROUTER receives the original message, and any Cortex failure state is surfaced through the existing `degradation_summary` rules in `[COGNITIVE CONTEXT]`.

Three subagents run in parallel:

1. **hippocampus** — scans `_meta/sessions/INDEX.md`, returns top 5-7 memory signals
2. **concept lookup** — scans `_meta/concepts/` for directly matched concept nodes
3. **SOUL dimension check** — reuses RETROSPECTIVE's SOUL Health Report, emits an identity_check signal

The three output streams feed the **gwt-arbitrator**, which applies the salience formula, ranks signals, and produces a single annotated-input block for ROUTER:

```
[USER MESSAGE]
[COGNITIVE ANNOTATION]
- Relevant history: [5-7 session summaries with signal_ids]
- Concept graph: [matched concepts + 1-hop neighbours]
- SOUL context: [tier-1 dimensions + any conflict warnings]
```

ROUTER may consult or ignore the annotation — its triage rules are unchanged. If Step 0.5 fails at any point (bootstrap failure, subagent timeout, file unreachable), the orchestrator falls back to raw message input and records the partial/failure state through the existing `degradation_summary` rules.

**Traceability emit rule (v1.7.1 R8):** The full YAML payloads from `hippocampus`, `concept lookup`, and `SOUL dimension check`, plus the GWT `[COGNITIVE CONTEXT]`, must be pasted to the user by ROUTER and written to `_meta/journal/{date}-cortex.md`. The journal entry is the traceability surface for Cortex runtime payloads; no `_meta/cortex/frames/...` directory or frame md file is defined or used.

**Express path interaction.** When ROUTER takes the Express path (1-3 domain agents, no PLANNER / REVIEWER), Step 0.5 still runs but in a reduced form: only the hippocampus subagent is spawned. Concept lookup and SOUL check are skipped to preserve Express's speed budget. The express-path annotated input is a single-line memory summary rather than the full three-section block. The gwt-arbitrator is not invoked when only one signal source is present.

**Direct-handle interaction.** Step 0.5 is still attempted before ROUTER sees a trivial message (e.g. "thank you", "ok"). If ROUTER then chooses a direct-handle response and the workflow ends at Step 1, ROUTER may ignore the cognitive context; no later Cortex narrator step is triggered.

### Step 7.5 — Narrator Validation (Phase 2 only)

Before the Summary Report is displayed, narrator-validator (Sonnet-tier Claude Code subagent — runs inside the current session, no external API) checks every substantive claim against the signal store. Invalid or uncited claims are returned to the narrator for rewrite. Connective tissue is ignored. This step runs only on Full Deliberation — Express path and direct-handle responses skip it.

### Step 10 — ARCHIVER Phase 2 extended

ARCHIVER Phase 2 already handles wiki and SOUL auto-writes. In v1.7 it also performs:

- **Concept extraction** — scan session materials for new concepts, classify permanence tier, write to `_meta/concepts/{domain}/{concept}.md`
- **Hebbian update** — for each co-activated pair (A, B) in the session, increment the A→B edge weight; create a new edge at weight 1 if none exists
- **SYNAPSES-INDEX.md regeneration** — rebuild the reverse index after weight updates
- **SOUL snapshot dump** — existing v1.6.2 mechanism, sustained under Cortex
- **Session summary write** — emit `_meta/sessions/{session_id}.md` with subject, key decisions, activated concepts, and one-line YAML summary fields consumed by hippocampus on later reads

All writes happen inside a single ARCHIVER invocation. The orchestrator does not interleave writes between phases. This preserves the Adjourn state machine defined in `pro/CLAUDE.md` — ARCHIVER emits one Completion Checklist when all phases are done, and the session ends.

### Step 0 preserved, Step 11 preserved

Neither Pre-Session Preparation nor STRATEGIST are modified. SOUL Health Report continues to be compiled by RETROSPECTIVE. STRATEGIST is invoked only on explicit user consent.

---

## Data Structures

All Cortex data lives in markdown. New directories introduced in v1.7:

```
_meta/
├── concepts/
│   ├── INDEX.md                         ← compiled one-liner index
│   ├── SYNAPSES-INDEX.md                ← compiled reverse edge index
│   ├── _tentative/                      ← concepts pending confirmation
│   ├── _archive/                        ← retired concepts
│   ├── finance/
│   │   └── {concept_id}.md
│   ├── career/
│   └── personal/
├── sessions/
│   ├── INDEX.md                         ← compiled session summary index
│   └── {platform}-{YYYYMMDD-HHMM}.md    ← per-session summary with YAML
├── snapshots/
│   └── soul/                            ← SOUL snapshots (v1.6.2, sustained)
├── eval-history/                        ← AUDITOR evaluation history
├── config.md                            ← host settings and Cortex thresholds
└── cortex/
    ├── bootstrap-status.md              ← migration state
    └── decay-log.md                     ← decay actions
```

Each mechanism's data format is defined in its own spec file. This document does not duplicate those definitions.

- Concept file format → `references/concept-spec.md`
- Session summary format → `references/session-index-spec.md`
- Signal and arbitration record format → `references/gwt-spec.md`
- Hippocampus output format → `references/hippocampus-spec.md`
- SOUL snapshot format → `references/snapshot-spec.md` (sustained from v1.6.2)

### Cortex Runtime Files (schemas)

Markdown artefacts track Cortex runtime state. None are source of truth — they are either config (user-editable) or compiled/log artefacts (archiver writes). User-editable config lives in `_meta/config.md`; compiled/log artefacts live under `_meta/cortex/` or `_meta/ambiguous_corrections/`. No config file lives under `_meta/cortex/`.

#### `_meta/config.md` (Cortex thresholds and secondary switches)

User-editable thresholds and secondary switches. Read by hippocampus, gwt-arbitrator, narrator-validator, and the decay pass. In v1.7.2, Cortex activation is always-on at the orchestration layer; `cortex_enabled` is deprecated and MUST NOT be used as an activation gate. If the field is present for legacy workspaces, readers ignore it for activation and use the hard-coded defaults listed below for all other settings.

```yaml
---
file: _meta/config.md
version: 1.7
---

# Cortex Config

## Feature switches
hippocampus_enabled: true
gwt_arbitrator_enabled: true
narrator_validator_enabled: true
concept_extraction_enabled: true

## Salience formula (gwt-arbitrator)
salience_weights:
  urgency: 0.3
  novelty: 0.2
  relevance: 0.3
  importance: 0.2
per_signal_floor: 0.3             # signals with salience < floor are dropped
top_k_signals: 5                  # hard cap of signals broadcast to ROUTER

## Decay curves (archiver Phase 2 decay pass)
decay_curves:
  identity: none                  # no decay
  skill: logarithmic              # decays to a steady baseline, never zero
  fact: exponential               # half-life 90 days
  transient: cliff                # zero at expiry

## Three-tier undo thresholds
escalate_rate_limit: 5            # per rolling 7-day window
ambiguous_correction_confidence_bands:
  high: 0.85                      # ≥ apply immediately
  mid_low: 0.5                    # mid-band lower bound (write to _meta/ambiguous_corrections/)
  low_floor: 0.0                  # logged but not acted

## Performance budgets (seconds, soft/hard)
hippocampus_timeout: [5, 15]
gwt_timeout: [5, 10]
narrator_validator_timeout: [3, 10]
```

Users editing this file should commit to git so cross-device drift is tracked. Changes take effect at the next session start (retrospective Mode 0 reads the config).

#### `_meta/cortex/bootstrap-status.md`

Written once by `tools/migrate.py`. Read by retrospective Mode 0 to decide whether Cortex is ready.

```yaml
---
file: _meta/cortex/bootstrap-status.md
---

# Cortex Bootstrap Status

migration_completed_at: 2026-04-20T14:32:10+09:00
from_version: v1.6.2a
to_version: v1.7
scope_months: 3

journal_entries_scanned: 127
sessions_synthesized: 38
concepts_extracted:
  tentative: 42
  confirmed: 18
  canonical: 7
snapshots_synthesized: 15
methods_extracted: 5
eval_history_backfilled: 0        # per spec: no backfill

errors: []                        # list of per-file parse failures
warnings:
  - "4 journal entries missing platform metadata; defaulted to 'claude'"
```

If this file is missing, the orchestrator attempts auto-bootstrap with `tools/migrate.py` before Step 0.5. Retrospective Mode 0 may still surface "Cortex not bootstrapped — run `uv run tools/migrate.py`" in the Start Session briefing when bootstrap has not succeeded. If bootstrap fails, Cortex degrades through the existing `degradation_summary` path and the workflow continues with the original message.

#### `_meta/cortex/decay-log.md`

Append-only log written by archiver Phase 2 at the end of every adjourn. Each session contributes one dated block.

```yaml
---
file: _meta/cortex/decay-log.md
rolling_window_days: 90
---

# Cortex Decay Log

## 2026-04-20 session claude-20260420-1432
edges_decayed: 14
edges_pruned: 2                   # weight reached 0
concepts_demoted:
  - C:finance:quarterly-yield     # canonical → confirmed (90-day dormancy)
concepts_retired:
  - C:transient:2026-q1-event     # transient cliff
new_tentative: 3
new_confirmed: 1
new_canonical: 0

## 2026-04-19 session claude-20260419-1238
...
```

Blocks older than 90 days compact into a trailing `# Archive` section on the next adjourn write. Past archives live in git history — no deletion, no Notion sync.

#### `_meta/ambiguous_corrections/{correction_id}.md`

One file per pending mid-confidence user correction. Created when the three-tier undo mechanism (§Design Principles → Three-tier undo) detects a correction with confidence in the 0.5–0.85 band: not high enough to apply immediately, not low enough to log-and-ignore.

```yaml
---
correction_id: 2026-04-20-concept-company-a-merge
target: C:finance:company-a-holding
target_type: concept              # concept | soul_dimension | method
correction_type: demotion | merge | split | alias_add | permanence_change
proposed_change: "demote from canonical to confirmed; merge alias 'Company-A HK'"
user_confidence: 0.72             # from correction heuristic (0.5-0.85 band)
signal_refs:
  - S:claude-20260420-1034
detected_at: 2026-04-20T10:34:12+09:00
surfaces_when: "next activation of C:finance:company-a-holding"
status: pending                   # pending | applied | dismissed
---

# Context

{One short paragraph quoting the user's language that triggered the
correction, plus a one-line archiver note explaining why confidence
landed in the mid-band rather than the high band. Max 30 lines.}
```

**Surfacing**: the next time the target is activated (concept in hippocampus output, SOUL dimension in check, method in dispatcher lookup), retrospective Mode 0 or ROUTER pauses to show the pending correction before proceeding. User confirms → `status: applied`, correction propagates through the normal three-tier undo machinery. User dismisses → `status: dismissed`, file is deleted, a row lands in `decay-log.md` noting the dismissal.

**Retention**: applied/dismissed files are removed; pending files compact to a summary line in `decay-log.md` after 30 days without activation (user never hit the target again — the correction is stale).

---

## Execution Model

Every Cortex component is a Claude Code subagent defined in `pro/agents/*.md`. The execution rules are the same as the existing 16 subagents.

- **No external API calls** — all LLM work happens inside the current Claude Code session. No Anthropic API key, no Claude API proxy, no OpenAI SDK.
- **No database** — the storage-decision ADR (`docs/architecture/markdown-first.md`) is authoritative. Markdown is the source of truth. SQLite and any other database are out of scope.
- **No separate background jobs** — no cron, no daemons, no scheduled workers. Data updates happen inside ARCHIVER Phase 2 writes.
- **No external secrets** — no environment variables beyond what Claude Code already provides. No Vercel, no GitHub Actions, no CI/CD pipelines.
- **Concept decay runs every adjourn** — not on a timer. The adjourn flow is the canonical maintenance window.
- **Bash-run Python tools, when needed, run locally** — the migration helper (`tools/migrate.py`) is invoked via Bash from the Claude Code session. It is not a service.

New agent files introduced in v1.7:

| Agent | Purpose |
|-------|---------|
| `pro/agents/hippocampus.md` | Cross-session retrieval, emits memory signals |
| `pro/agents/gwt-arbitrator.md` | Salience competition, emits annotated input |
| `pro/agents/narrator-validator.md` | Sonnet Claude Code subagent — citation validator (Phase 2) |

Narrator is NOT a new agent file — narrator behavior lives inside ROUTER (see `references/narrator-spec.md` §6). Concept extraction is NOT a new agent file — it lives inside ARCHIVER Phase 2 (see `references/concept-spec.md` §Hebbian Update Algorithm).

Extensions to existing agents:

- `pro/agents/archiver.md` Phase 2 — add concept extraction, Hebbian update, method-candidate detection, decay pass, session summary write, index rebuild
- `pro/agents/retrospective.md` Mode 0 — regenerate `_meta/concepts/INDEX.md` and `_meta/sessions/INDEX.md`; flag dormant concepts
- `pro/agents/router.md` — accept cognitive annotation in its input; own narrator composition at Step 7.5

Claude Code reads each agent definition at spawn time; no runtime state persists between invocations.

### Information isolation additions

The existing Information Isolation table in `pro/CLAUDE.md` gets three new rows in v1.7, preserving the same principle — each agent receives only what its job requires:

| Role | Receives | Does NOT Receive |
|------|----------|------------------|
| hippocampus | User message + `_meta/sessions/INDEX.md` + current session context | Other agents' thought processes, full concept graph |
| gwt-arbitrator | Signal files from hippocampus / concept-lookup / soul-check | User's raw message (operates on signals only) |
| narrator-validator | Summary Report draft + signal store | Agent thought processes, user's private data |

The gwt-arbitrator's isolation from the raw message is deliberate — salience computation should operate on structured signals, not be biased by the conversational surface. The narrator-validator's isolation from thought processes prevents circular validation.

---

## Design Principles

### Grounded generation

No claim in any Cortex output may be made without a signal_id citation. This is the primary defence against confabulation. The validator subagent enforces it by retrieving the cited signal and checking that the narrator's paraphrase is faithful. If any substantive claim lacks a citation or the citation does not support the claim, the narrator rewrites.

The Gazzaniga left-brain-interpreter experiments show that humans confabulate plausible explanations for decisions they did not consciously make. If Cortex reproduced this mechanism, it would be a self-deceiving system — decisions driven by whichever signal happened to be loudest, rationalised post-hoc into a coherent-looking narrative. Grounded generation is the structural answer: the validator cannot be circumvented because it runs as a separate subagent with read-only access to the signal store. A narrator that fabricates a signal_id will fail validation at retrieval time.

### Three-tier concept permanence with a fourth for transient state

| Permanence | Decay shape | Examples |
|-----------|-------------|----------|
| Identity | does not decay | SOUL core values, long-standing relationships |
| Skill | logarithmic decay to a steady baseline | "how to write Python" |
| Fact | exponential decay | "Q2 last year project X had budget Y" |
| Transient | cliff decay to zero at expiry | event-specific, one-off references |

Permanence is assigned at first activation during ARCHIVER Phase 2 concept extraction. Users can pin permanence explicitly. Meta-cognition can upgrade permanence when a concept resists decay despite being "tried" for downgrade.

### Spreading activation, not exhaustive retrieval

The hippocampus does not scan every session file. It uses ripgrep for Wave 1, then 1-hop synapse traversal for Wave 2, and sub-threshold pre-activation for Wave 3. Total scope per query is bounded: top-50 concept nodes maximum. This matches how spreading activation works in the brain — intensity falls with graph distance.

Wave 3 is pre-activation, not retrieval. Sub-threshold concepts do not appear in the output unless a later frame in the same session lifts them over threshold. This reproduces the brain's priming behaviour: neighbours of a recently activated concept become easier to trigger in the next frame, even without direct evidence. The operational effect is that a session that opens with a question about "company-A holding" is more responsive to later questions about "company-A subsidiary" even when the user does not repeat the parent name.

### Salience competition, not rule-based priority

Signals do not have a fixed priority. They compete via the salience formula at every frame. A high-urgency memory signal can outcompete a high-importance identity signal when context warrants. The arbitrator is the only component that determines which signals ignite.

### Structured veto with reasoning chain

This is Path B from the brainstorm. Inhibitory signals (vetoes) are not mere strength-based suppressions — they must carry a reasoning_chain with claims, evidence_signals, and confidence. This makes rejections auditable. When the same pair of signals produces identical competition twice (a rebuttal loop with no new evidence), the system auto-escalates to the user.

The alternative (Path A — suppression-by-strength) was rejected because inhibitory signals in a software system have no evolutionary heuristics to back them. Brains can tolerate opaque veto because billions of years of evolution tuned the veto neurons. Software modules have no such substrate; an opaque veto from a module is just an Opus hunch. By requiring a reasoning_chain, every rejection becomes something the user can inspect and, if needed, overrule. This preserves the Life OS principle that the system is the user's instrument, not an authority over them.

### Three-tier undo

No system is useful if it cannot be corrected. Cortex provides three corrective pathways:

1. **Passive decay** — unused canonical concepts demote over time (fact-tier after 90 days). No user action required.
2. **User correction** — "you got this wrong" triggers a concept_demotion modification with cascade marking on all affected synapses.
3. **Meta-cognitive audit** — a weekly audit surfaces suspected drift (conflicting salience, frequency drops, repeated user corrections) to `_meta/audit/suspicious.md`; user confirms before demotion.

User correction confidence is tiered: high-confidence (>0.85) corrections apply immediately; mid-confidence (0.5-0.85) corrections are written to `_meta/ambiguous_corrections/` and surface at the next related activation for explicit confirmation; low-confidence (<0.5) corrections are logged but not acted upon. The initial thresholds are deliberately conservative — false negatives (missing a correction) cost less than false positives (demoting something the user did not want demoted).

The meta-cognitive audit is rate-limited: more than **5 escalations per rolling 7-day window** triggers a secondary audit of the module quality itself. The assumption is that a well-functioning system should rarely need to surface conflicts to the user; frequent escalations indicate module-level drift, not individual correction need.

#### `_meta/audit/suspicious.md` format

The meta-cognitive audit writes a single rolling markdown file. Archiver Phase 2 appends candidates; retrospective Mode 0 surfaces unresolved rows in the Start Session briefing; user confirms or dismisses. Format:

```yaml
---
file: _meta/audit/suspicious.md
rolling_window_days: 30
last_compacted: ISO 8601
---

# Audit · Suspicious Drift

| Detected | Candidate | Reason | Signal refs | Status |
|----------|-----------|--------|-------------|--------|
| 2026-04-18 | C:finance:company-a-holding | 4 user corrections in 2 weeks; salience stable | S:claude-20260418-0934, S:claude-20260416-1520 | open |
| 2026-04-17 | C:method:iterative-refinement | Activation dropped 80% vs 90-day baseline | S:claude-20260417-1400 | dismissed 2026-04-19 |
```

Columns:

- **Detected** — ISO date the archiver flagged the drift
- **Candidate** — fully-prefixed signal_id of the concept / SOUL dimension / method being questioned
- **Reason** — one-line description from one of four heuristics: `conflicting_salience`, `frequency_drop`, `repeated_user_correction`, `canonical_contradiction`
- **Signal refs** — comma-separated signal_ids supporting the detection (for `narrator-validator`-style verification)
- **Status** — `open` / `confirmed YYYY-MM-DD` / `dismissed YYYY-MM-DD`

Rows older than 30 days with `status: open` compact into a trailing "# Archive" section when archiver Phase 2 runs. Dismissed/confirmed rows compact after 90 days. The file never exceeds ~300 rows active; compaction keeps read latency bounded.

#### Escalate rate limit

The 5-per-week threshold is monitored by AUDITOR during patrol inspection (not a hook or Python tool — stays in-session). When exceeded, AUDITOR writes a high-priority entry to `_meta/eval-history/{date}-{project}.md` with `violations[].type: escalate_rate_exceeded` and surfaces the pattern in retrospective Mode 0's next briefing. No module is automatically cut (user decision #4 — no pre-committed kill criteria); the user decides whether the underlying mechanism needs tuning.

---

## Relationship to Existing Components

Cortex does not replace any existing Life OS component — it augments them. The table below summarises how each existing surface gains (or keeps) its shape under v1.7.

| Existing component | Role under Cortex | Nature of change |
|-------------------|-------------------|------------------|
| SOUL.md | Identity layer, source of identity_check signals | Unchanged. SOUL auto-write continues; the Health Report feeds into Step 0.5. |
| wiki/ | Concept anchor material, evidence source for ARCHIVER Phase 2 concept extraction | Unchanged. Wiki entries remain separate from concept nodes but can anchor them. |
| DREAM | Offline sleep-phase pattern processor | Unchanged structurally. Can consume the concept graph for REM cross-domain leaps. |
| RETROSPECTIVE | Session start housekeeping + SOUL Health Report | Mode 0 extended with decay check and concept INDEX rebuild. |
| ARCHIVER | Session close, 4-phase closer | Phase 2 extended with concept extraction, Hebbian update, session summary write. |
| ROUTER | Triage and report orchestration | Input format changes (annotated input instead of raw), triage rules unchanged. |
| 16 subagents | Deliberation cast (PLANNER / REVIEWER / six domains / etc.) | Unchanged. Consume richer context when ROUTER forwards annotated input. |

Three invariants hold: (1) Cortex gives ROUTER a better input but does not interpret messages on ROUTER's behalf; (2) Cortex gives ARCHIVER additional write targets but does not bypass ARCHIVER's single-invocation discipline; (3) Cortex adds cognition around the 16-agent deliberation but does not change the checks-and-balances structure. Agents still see only what their job requires.

---

## Archiver Candidate Routing (Phase 2 disambiguation)

When archiver Phase 2 extracts candidates from a session's content, it must decide **which knowledge layer each candidate belongs to**. The decision is not arbitrary — each layer answers a different question, and mis-routing creates silent drift (facts stored as values, procedures stored as concepts, identity stored as wiki).

This is the authoritative decision tree. When any spec disagrees with this tree, this tree wins.

### The 4 knowledge layers + 1 identity layer

| Layer | Answers | Example candidate | Path |
|-------|---------|-------------------|------|
| SOUL | Who you are (identity / values / preferences) | "user consistently prioritizes family over career growth" | `SOUL.md` (one file, dimensions inside) |
| Wiki | What you know about the world (declarative) | "NPO lending in Japan has no 貸金業法 exemption" | `wiki/{domain}/{slug}.md` |
| Concept | How ideas connect (associative graph nodes) | "Company-A" as an entity that connects to other concepts through weighted edges | `_meta/concepts/{domain}/{concept_id}.md` |
| Method | How you work best (procedural memory) | "Refine documents in 5 escalating quality rounds" | `_meta/methods/{domain}/{method_id}.md` |
| user-patterns | What you do (observed behavioural patterns, ADVISOR domain) | "Makes decisions faster after first-round clarification" | `user-patterns.md` (one file, entries inside) |

### Decision tree

Archiver Phase 2 runs each candidate through this tree. First matching branch wins — candidates never route to multiple primary layers.

```
Is the candidate about the user's identity, values, preferences, or red lines?
├── YES → SOUL
│         (evidence from ≥2 decisions in current session or last 30 days;
│          auto-writes new dimensions at confidence 0.3, What SHOULD BE empty)
│
└── NO → Is it a behavioral pattern (what the user DOES, not who they ARE)?
    ├── YES → user-patterns.md (append via patterns-delta)
    │         (ADVISOR surfaces these; not SOUL)
    │
    └── NO → Is it a reusable WORKFLOW (sequence of actions, method-like)?
        ├── YES → Method
        │         (5+ sequential actions, cross-session echo in ≥2 sessions,
        │          user language like "approach/pattern/framework/流れ/やり方/手順";
        │          lands in _meta/methods/_tentative/ with status: tentative)
        │
        └── NO → Is it a recurring ENTITY / CONCEPT that connects to others?
            ├── YES → Concept
            │         (≥2 activations + ≥2 independent evidence points;
            │          lands in _meta/concepts/_tentative/ until promotion;
            │          individuals → skip, OR route to SOUL (privacy filter))
            │
            └── NO → Is it a FACTUAL conclusion about the world?
                ├── YES → Wiki
                │         (6 criteria: cross-project-reusable, about-the-world,
                │          zero-privacy, factual-or-methodological, ≥2 evidence,
                │          no-contradiction-with-existing; see wiki-spec §Auto-Write Criteria)
                │
                └── NO → Discard (not reusable; stays in session journal only)
```

### Disambiguation examples

| Candidate | Route | Why |
|-----------|-------|-----|
| "User prefers quality over speed" | SOUL | Identity / value statement |
| "User tends to avoid financial discussions on Mondays" | user-patterns | Behavioral pattern (what they do), not identity |
| "MVP validation uses 5 escalating quality rounds" | Method | Reusable procedural workflow |
| "Company-A and Company-B share a director who also sits on Project-X's board" | Concept (+ edges) | Graph structure with entities |
| "NPO lending in Japan has no 貸金業法 exemption" | Wiki | Factual conclusion about the world |
| "Iterative document refinement works best when each round has one focus" | Method | Procedural how-to |
| "Governance concerns should weigh 30% in cross-border product decisions" | Wiki | Declarative conclusion |
| "Finance and Execution agents disagreed by 4 points last session" | Discard | Single-session observation, not cross-session reusable |
| "User's specific family member A's preferences" | Skip (or SOUL with privacy filter) | Individuals do not route to Concept; SOUL's privacy filter decides whether SOUL takes them or they are dropped |

### Ambiguous cases

**Fact with procedural edge**: "When negotiating rate increases, anchor with data first" can read as a method (procedure) OR a wiki conclusion (fact about the world). Rule: if the candidate describes a **sequence of user actions**, it's a method. If it describes **a property of the world**, it's wiki. When genuinely ambiguous, default to **wiki** — methods require stronger evidence (≥5 sequential steps across ≥2 sessions).

**Concept with SOUL overlap**: "trust" as a relational dimension could be SOUL (a value) or a concept (relational entity type). Rule: concepts are about **things in the world that connect to other things**; SOUL is about **the user's orientation toward things**. "User values trust in business relationships" → SOUL. "Trust is a relationship capital type that flows between projects" → concept (in `_meta/concepts/relationship/`).

**Wiki with method flavour**: a step-by-step recipe that is a factual description of the world (not user's chosen workflow) → wiki. If the user has consciously adopted it as their own method → method. Heuristic: archiver asks "does the user own this workflow?" — if yes, method; if no (it's just a known technique), wiki.

### Routing confidence and pending state

Archiver Phase 2 assigns each candidate a routing confidence:

- **High (>0.85)** — proceeds to the target layer with `status: tentative` (for concepts/methods) or auto-written to SOUL at confidence 0.3 / wiki at confidence 0.3-0.5
- **Mid (0.5-0.85)** — written to `_meta/ambiguous_corrections/` as a routing-decision correction awaiting user confirmation at next related activation
- **Low (<0.5)** — logged to `_meta/cortex/decay-log.md` as "routing-rejected candidate" with reason, not written anywhere

This mirrors the three-tier undo mechanism (§Design Principles → Three-tier undo) — archiver errs toward caution when uncertain. False negatives (missed candidate) cost less than false positives (wrong-layer write that later needs surgical reversal).

### Anti-patterns

- **Routing the same candidate to two layers** — exactly one primary destination. Concepts MAY reference wiki entries via `anchors_in_wiki: [slug]`, but that is a cross-reference, not a duplicate write.
- **Creating a concept for an individual person** — violates concept-spec §9 (Privacy). Individual people belong in SOUL with privacy filter applied.
- **Writing a method without ≥2 independent sessions showing the pattern** — violates method-library-spec §6 (heuristic). Cross-session echo is the minimum evidence bar.
- **Writing a wiki entry that fails any of 6 criteria** — violates wiki-spec §Auto-Write Criteria. All 6 or discard.
- **Mutating SOUL directly during routing** — SOUL auto-write uses its own 3-criteria gate (identity-scope + ≥2 evidence + no existing dimension). Routing proposes; SOUL auto-write accepts.

---

## Anti-patterns

Cortex MUST NOT do any of the following:

- **Database as source of truth** — the authoritative store is markdown. SQLite, Postgres, or any relational index is out of scope.
- **Sync Cortex data to Notion** — concept nodes, synapses, and frame records do not round-trip through Notion. Notion receives session summaries and decision records only, as in v1.6.2a.
- **Require external API keys** — no Claude API, no OpenAI SDK, no third-party embeddings. All intelligence runs inside Claude Code.
- **Invent signals without a data source** — every signal emitted by any module must cite where its payload came from. No synthesised evidence.
- **Let the narrator make claims without citations** — substantive claims are citation-mandatory. Validator enforcement is not optional.
- **Run as a persistent daemon** — Cortex runs inside the current session. Nothing persists between sessions except markdown.
- **Build a premium edition** — there is one universal version. No feature-gating based on user tier.

---

## Version & Migration

Cortex is introduced in **v1.7**. The brainstorm divided its rollout into four internal stages (A through D), with the first stage (A) further subdivided into three phases (A1/A2/A3), but they all land within v1.7 — not across v1.8 / v1.9 / v2.0. The version number is unified.

v1.7 internal stages:

| Stage | Scope |
|-------|-------|
| A — Data structure | `_meta/concepts/`, `_meta/sessions/INDEX.md`, ARCHIVER Phase 2 gains concept extraction (Hebbian off) |
| B — Cognitive pre-router online | hippocampus + gwt-arbitrator subagents live, Step 0.5 wired, Hebbian on |
| C — Narrator + undo mechanism | Step 7.5 active, three-tier undo live, escalate rate limits |
| D — Complete cortex + Hermes execution layer | downgraded modules backfilled, full execution layer |

All four stages ship inside v1.7. The staging is internal sequencing, not incremental releases. The reason the stages exist at all is that each stage is a natural checkpoint for the ones that follow: stage B cannot function usefully until stage A has produced enough concept and session data; stage C's narrator cannot validate against signals that stage B did not produce; stage D refines what stages B and C have shown to work. Stages are natural dependency gates — not external release points.

Stage A subdivides into three phases: A1 (data structures land), A2 (migrate.py backfill), A3 (seed.py bootstrap); A2 and A3 may run in parallel once A1 lands. Stages B, C, D remain single-phase. The full internal sequence is A1 → (A2+A3 parallel) → B → (C+D parallel), and everything still ships as v1.7.

AUDITOR tracks post-ship quality through `eval-history` entries (`references/eval-history-spec.md`). Quality regressions surface as eval-history patterns; module-level scope changes happen through normal spec revision, not through pre-committed numeric thresholds.

### Migration from v1.6.2a

Cortex requires a backfill of the session index before the hippocampus can retrieve anything. The migration pulls the last 3 months of `_meta/journal/*.md` and produces per-session summaries.

```
Script: tools/migrate.py
Input:  _meta/journal/*.md           (existing session journals)
Output:
  - _meta/sessions/{session_id}.md   (one file per historical session)
  - _meta/sessions/INDEX.md          (compiled one-liner index)
  - _meta/concepts/**/*.md           (seed concepts from journal entities)
  - _meta/snapshots/soul/**          (backfilled SOUL snapshots when possible)
```

The migration script is invoked via Bash from Claude Code. It is idempotent — re-running it overwrites the compiled index without duplicating concepts. The same script is invoked automatically before Step 0.5 when `_meta/sessions/INDEX.md` is missing or empty and Cortex is enabled. After migration, the user runs one session with Cortex enabled; if the annotated input feels correct, Cortex is promoted to steady state.

If migration fails, the orchestrator falls back to raw message input and logs the failure through the existing `degradation_summary` rules. Users operate as in v1.6.2a until migration is retried.

Three-month scope is a deliberate default: older journals often contain outdated context (retired projects, demoted values, pre-SOUL decisions) that would pollute the concept graph. Users with richer histories can override the scope by passing `--since YYYY-MM-DD` to the migration script. First-time users with no journal history run Cortex in "cold start" mode — the annotated input is minimal until enough sessions accumulate; nothing blocks use of the system.

---

## Open Questions

The following specifications are deliberately left to be resolved during implementation — not because they are forgotten, but because they need concrete data to tune correctly.

- **Salience formula weight tuning** — the Phase 1 weights (urgency 0.3, novelty 0.2, relevance 0.3, importance 0.2) are placeholders. Three months of real annotated-input data are needed to validate.
- **Concept permanence classification heuristics** — ARCHIVER Phase 2 concept extraction uses heuristic rules at first activation. The boundary between skill and fact is fuzzy. Expect revision after 3 months of real usage.
- **Narrator citation density** — per sentence vs per paragraph. Phase 2 begins with per-substantive-claim; granularity may coarsen if the output feels machine-stamped.
- **Multi-device concurrency** — single device / distributed sync / active-lock — three options, one is chosen at Phase 1 launch.
- **Frame trigger policy** — when Cortex is enabled, every user message triggers Step 0.5 in v1.7, including Start Session triggers. External events (scheduled prompts, inbox arrivals) are out of scope for v1.7 frame triggers — only user messages trigger Step 0.5.
- **Cold-start behaviour** — new users with no journal history run Cortex in a degraded mode. The exact point at which Cortex transitions from cold-start to steady-state (number of sessions, number of concepts, or a heuristic) has not been chosen.

---

## References

- Overall architecture discussion → `devdocs/brainstorm/2026-04-19-cortex-architecture.md`
- Integration bridge document → `devdocs/architecture/cortex-integration.md`
- Markdown-first ADR → `docs/architecture/markdown-first.md`
- Hippocampus mechanism → `references/hippocampus-spec.md`
- GWT arbitrator mechanism → `references/gwt-spec.md`
- Narrator layer mechanism → `references/narrator-spec.md`
- Concept graph + Hebbian rules → `references/concept-spec.md`
- Session index format → `references/session-index-spec.md`
- SOUL snapshot format → `references/snapshot-spec.md`
- AUDITOR evaluation history → `references/eval-history-spec.md`
- Workflow orchestration → `pro/CLAUDE.md`
- Data layer boundaries → `references/data-layer.md`
- SOUL mechanism → `references/soul-spec.md`
- Wiki mechanism → `references/wiki-spec.md`
- DREAM mechanism → `references/dream-spec.md`
