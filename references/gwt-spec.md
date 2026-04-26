---
title: "GWT Arbitrator Spec · Cortex Layer"
version: 1.7
status: pre-implementation
audience: Life OS implementers
scope: Cortex Pre-Router Cognitive Layer — signal arbitration
related:
  - references/cortex-spec.md
  - references/hippocampus-spec.md
  - references/concept-spec.md
  - references/soul-spec.md
  - devdocs/brainstorm/2026-04-19-cortex-architecture.md
  - devdocs/architecture/cortex-integration.md
---

# GWT Arbitrator Spec

## 1. Purpose

The **GWT (Global Workspace Theory) Arbitrator** consolidates signals emitted by the Pre-Router Cognitive Layer subagents and produces the **annotated input** that ROUTER receives.

It is grounded in Stanislas Dehaene's **Global Neuronal Workspace** theory: many specialized modules run in parallel, their outputs compete for the central workspace, and only the strongest signals get broadcast globally. Consciousness, in this framing, is the moment of ignition — the signal wins the competition and is published to every other module.

In Life OS, the competition is between:

- Retrieved memories from the hippocampus
- Direct concept matches from the concept store
- SOUL dimension signals (identity alignment or conflict)

The arbitrator is the **choke point** that prevents information overload on ROUTER while preserving the most decision-relevant context.

---

## 2. Trigger

- Runs **after** all Pre-Router parallel subagents (hippocampus, concept lookup, SOUL dimension check) complete their work for each Cortex-enabled user message, including Start Session triggers.
- **Single invocation per session turn.** Never loops. Never re-fires mid-turn.
- **Timeout budget:** 5 seconds soft target, 10 seconds hard ceiling.
- If the hard ceiling is hit, the arbitrator emits a partial result using whatever signals it has already scored (see §13).

---

## 3. Agent Definition

```yaml
---
name: gwt-arbitrator
description: "Cortex GWT arbitration — consolidates Pre-Router signals into annotated ROUTER input"
tools: [Read]
model: opus
---
```

Read-only by design. The arbitrator never writes to persistent stores. All mutations (Hebbian updates, concept creation, synapse reinforcement) happen in ARCHIVER Phase 2. This keeps the mid-session path cheap and side-effect-free.

---

## 4. Input Contract

The orchestrator passes four inputs to the arbitrator:

```
hippocampus_output:      yaml  # retrieved sessions, activated concepts
concept_lookup_output:   yaml  # direct concept matches to current subject
soul_check_output:       yaml  # relevant SOUL dimensions and their status
current_user_message:    string
```

Each upstream source produces a list of **signals** with a uniform envelope (see §5 for scoring and §6 for signal types). Missing sources are tolerated — a first-ever session may have no hippocampus output, and the arbitrator proceeds with what it has. If every source is null, emit `[COGNITIVE CONTEXT]` with only `degradation_summary`.

---

## 5. Salience Formula (CRITICAL — explicit and fixed)

Every signal is scored with a **single scalar** called `salience`:

```
salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2
```

This formula is fixed for v1.7. Each component is a float in `[0.0, 1.0]`, defined below.

### 5.1 urgency

| Value | Condition |
|-------|-----------|
| 1.0 | action item with a deadline within 7 days |
| 0.6 | SOUL conflict warning (`core` dimension is being challenged) |
| 0.3 | recurring pattern detected (same subject seen 3+ times recently) |
| 0.0 | background context with no time pressure |

### 5.2 novelty

| Value | Condition |
|-------|-----------|
| 1.0 | signal has never surfaced before |
| 0.6 | signal surfaced 1–2 times previously |
| 0.2 | signal surfaced 3+ times (fatigue — user has already seen it) |
| 0.0 | already acted on and resolved |

### 5.3 relevance

Keyword / concept overlap score between the signal payload and the current subject of the user message. Computed by **LLM judgment** inside the arbitrator.

The LLM receives the signal content and the current user message, and is asked to produce a single float in `[0.0, 1.0]` representing how directly the signal pertains to the decision at hand. Keyword overlap is the deterministic fallback when LLM judgment fails (see §13).

### 5.4 importance

Tier names match `references/soul-spec.md` §Tiered Reference by Confidence and `references/snapshot-spec.md` §Tier Mapping. All confidence bands use half-open intervals `[a, b)` — the lower bound is inclusive and the upper bound is exclusive. Boundary values always belong to the **upper** tier (e.g., confidence exactly 0.3 is `secondary`, not `emerging`; confidence exactly 0.7 is `core`, not `secondary`).

| Value | Condition |
|-------|-----------|
| 1.0 | SOUL `core` dimension (confidence ∈ `[0.7, 1.0]`) |
| 0.7 | SOUL `secondary` dimension (confidence ∈ `[0.3, 0.7)`) |
| 0.5 | relates to a critical-path project (tagged in concept metadata) |
| 0.3 | SOUL `emerging` dimension (confidence ∈ `[0.2, 0.3)`) |
| 0.2 | general context with no identity or project tie (or `dormant` dimension with confidence ∈ `[0.0, 0.2)`, included only for context) |

When multiple conditions apply, use the **highest** matching value.

---

## 6. Signal Types Consolidated

The arbitrator recognizes the following signal types grouped by source:

### From hippocampus

- `decision_analogy` — a past decision with a similar pattern to the current subject
- `value_conflict` — a past session that conflicted with SOUL, relevant here
- `outcome_lesson` — a past decision whose outcome is instructive

### From concept lookup

- `canonical_concept` — a confirmed concept directly mentioned or implied
- `emerging_concept` — a tentative concept in the same area (not yet canonical)

### From SOUL check

- `tier_1_alignment` — core identity dimension supports the direction
- `tier_1_conflict` — core identity dimension conflicts (**semi-veto signal**)
- `tier_2_relevant` — secondary dimension applies to the subject
- `dormant_reactivation` — a dormant dimension just became relevant again

A signal is opaque to the arbitrator beyond its `signal_type`, `source`, `payload`, and the four scoring components. The arbitrator does not introspect the payload to derive new signals; each signal must have a named source.

---

## 7. Arbitration Algorithm

The arbitration is five deterministic steps plus one LLM judgment step (relevance):

1. **Ingest** — receive all signals with their metadata from the orchestrator.
2. **Score** — compute `salience` for each signal using the formula in §5. Relevance uses LLM judgment; all other components are rule-based.
3. **Rank** — sort signals descending by salience.
4. **Cap** — take the top **5** signals overall (hard cap, prevents information overload).
5. **Detect conflicts**:
   - Any `tier_1_conflict` signal → **elevate** to the ⚠️ SOUL CONFLICT header in the output.
   - Contradictory `decision_analogy` signals (past decisions suggest opposite directions) → flag as "inconsistent precedent" in the pattern observations block.
6. **Compose** — render the annotated output per §8.

No signal may be **invented** by the arbitrator. Every item in the output traces back to a specific input signal.

### 7.1 Worked Example

Given three signals from upstream subagents:

| id | type | urgency | novelty | relevance | importance | salience |
|----|------|---------|---------|-----------|------------|----------|
| s1 | `decision_analogy` | 0.3 | 0.6 | 0.8 | 0.5 | 0.55 |
| s2 | `tier_1_conflict` | 0.6 | 1.0 | 0.9 | 1.0 | 0.85 |
| s3 | `canonical_concept` | 0.0 | 0.2 | 0.7 | 0.5 | 0.35 |

After ranking: `[s2, s1, s3]`. `s2` triggers the SOUL CONFLICT elevation. All three fit under the top-5 cap and are composed into the output. `s3`, at salience 0.35, still makes it in because the per-signal floor is 0.3.

---

## 8. Output Format — Annotated ROUTER Input

The arbitrator emits a single Markdown block that is **prepended** to the user message when it reaches ROUTER:

```markdown
[COGNITIVE CONTEXT — reference only, not user input]

⚠️ SOUL CONFLICT: [only if `core` dimension challenged]
This decision challenges your "{dimension_name}" (confidence {X})

📎 Related past decisions:
- {session_id} ({date}): {reason}, score {X}/10

🧬 Active concepts:
- {concept_id} (canonical, weight {X}, last activated {when})

🔮 SOUL dimensions:
- {dimension} ({tier}, {trend}): {support/challenge status}

💡 Pattern observations:
- {any salience ≥ 0.8 signals not covered above}

degradation_summary:
- hippocampus: {ok | null | timeout | failed: <reason>}
- concept-lookup: {ok | null | timeout | failed: <reason>}
- soul-check: {ok | null | timeout | failed: <reason>}
- frame_md_path: {written: <path> | not written: <reason>}

[END COGNITIVE CONTEXT]

User's actual message: {original}
```

Each signal bullet must be emitted **only if** there is at least one signal of that category in the top-5. Empty categories collapse (see §9). `degradation_summary` is always emitted so ROUTER can see partial-context risk.

---

## 9. Signal Suppression Rules

To prevent annotation noise:

- If the **total signal count is 0** after scoring, emit only the required `degradation_summary` between `[COGNITIVE CONTEXT]` delimiters. ROUTER still receives the original user message after the context block.
- If **all signals have salience < 0.3**, emit `(no high-salience signals)` as a single-line marker and skip the category blocks.
- If a **SOUL CONFLICT** is present but there are no relevant past decisions, still emit the SOUL block (the conflict is load-bearing on its own).
- **Per-category caps:** max 5 related decisions, max 5 active concepts, max 5 SOUL dimensions. Per-category caps are **local maxima per block**, not additional slots beyond the §7 global top-5. The §7 global top-5 is the hard ceiling and is always enforced first. In practice: when per-category cap is reached before the global top-5 budget is exhausted, the remaining global slots stay free; when the global top-5 fills first, the per-category cap is superseded. The example of "5 SOUL dimensions fill the output" simply means all 5 global slots happened to score highest within a single category.

---

## 10. Tie-Breaking Rules

When two signals have **identical salience** after scoring, break ties in this order:

1. **Newer first** — prefer the signal with the more recent `timestamp`.
2. **Higher importance** — if still tied, prefer the signal with higher `importance`.
3. **Alphabetical by `signal_id`** — fully deterministic fallback so the same inputs always produce the same ranking.

Tie-breaking must be deterministic. No randomization. Two runs with the same inputs must produce the same output ranking.

---

## 11. Performance Budget

| Stage | Target |
|-------|--------|
| Receive inputs (passed in-context) | instant |
| LLM judgment for relevance scoring | ~2 s, ~3,000 tokens |
| Composition | < 1 s |
| **Total target** | **< 3 s** |

The soft timeout (§2) is 5 s; the hard ceiling is 10 s. Exceeding the hard ceiling triggers the partial-output failure mode in §13.

---

## 12. Injection Location (CRITICAL for prompt caching)

The cognitive context is injected as a **prefix to the user message**, inside the **user role**. It is **not** added to the system prompt.

**Why:** Anthropic's prompt cache only hits on a stable system prompt. Every dynamic cognitive annotation would invalidate the cache if injected there. Keeping dynamic content in the user role preserves cache hit rate across turns.

**Implementation:**

1. The orchestrator invokes the arbitrator and captures its output.
2. The orchestrator **prepends** the arbitrator's block to ROUTER's input user message.
3. ROUTER sees the combined input. It uses the cognitive context as **reference**, not as the literal user request.
4. ROUTER's system prompt is untouched.

ROUTER's triage rules do not change. It treats the COGNITIVE CONTEXT block as auxiliary information it **may** consult when deciding which domain agents to dispatch.

---

## 13. Failure Modes

| Failure | Behavior |
|---------|----------|
| **No Pre-Router inputs** (first-ever session or bootstrap failure) | Emit `[COGNITIVE CONTEXT]` with only `degradation_summary`; ROUTER still receives the raw user message. |
| **Single input source** (e.g., hippocampus returned nothing) | Proceed with whatever sources did return signals. |
| **LLM judgment for relevance fails or times out** | Fall back to **keyword overlap** between signal payload and user message as the relevance score. |
| **Arbitrator total timeout** (hard ceiling) | Emit partial output using the best-scored signals obtained so far, capped at top-5. Append a single line `(partial — timed out)` to the block. |
| **Malformed signal from upstream** | Skip that signal. Do not crash. Log internally for AUDITOR review. |

Graceful degradation is non-negotiable: the arbitrator failing **must not** block ROUTER. When in doubt, the orchestrator falls through to v1.6.2a behavior (raw user message straight into ROUTER) and exposes any partial-context risk through `degradation_summary` when a context block is emitted.

---

## 13.1 Degradation Hierarchy

When multiple failures stack, apply them in this order:

1. Missing sources → proceed with what exists.
2. LLM relevance failure → keyword overlap fallback.
3. Hard timeout → partial output.
4. Catastrophic arbitrator failure → `degradation_summary`-only context when possible + fall-through to raw ROUTER behavior.

At every step, the output is still a valid annotation block (even if empty). ROUTER must never receive an ill-formed or half-closed block.

---

## 14. Quality Metrics

For AUDITOR's `eval-history` track:

- **`cognitive_annotation_quality` (0–10)** — did ROUTER reference the annotation productively?
  - Specifically: did REVIEWER cite the annotation? Did any domain agent reference it during deliberation?
- **`annotation_utilization_rate`** — fraction of sessions where at least one downstream agent used a `signal_id` from the annotation.
- **`suppression_precision`** — when the arbitrator emitted a SOUL CONFLICT warning, how often did REVIEWER independently flag the same issue?

AUDITOR surfaces low-scoring sessions for review. If annotation quality trends downward over 30 days, AUDITOR's patrol inspection flags the pattern in eval-history, and module-level scope changes proceed through the normal spec revision process.

---

## 15. Anti-patterns

- **Do not invent signals.** Every signal in the output must have a named source and an upstream payload.
- **Do not rank by SOUL tiers alone.** Importance is one of four salience components. An `emerging` signal with high urgency and high novelty can legitimately outrank a `core` signal with low urgency.
- **Do not include raw subagent output** in the annotation. Consolidate to concept references and short summaries. Full payloads must still be pasted to the user and written to `_meta/journal/{date}-cortex.md` for traceability; no frame md is used.
- **Do not modify the system prompt.** All dynamic content lives in the user role message (see §12).
- **Do not exceed 5 signals per category**, or 5 signals overall. Information overload is a failure mode, not a feature.
- **Do not call hippocampus or concept lookup from inside the arbitrator.** Upstream subagents are the source of truth; the arbitrator is a pure consumer.

---

## 16. Related Specs

- `references/cortex-spec.md` — full Cortex architecture
- `references/hippocampus-spec.md` — signal source: cross-session retrieval
- `references/concept-spec.md` — signal source: concept store and synapse graph
- `references/soul-spec.md` — SOUL tier definitions and confidence bands
- `devdocs/brainstorm/2026-04-19-cortex-architecture.md` — design rationale (§3 schema, §4 salience debate)
- `devdocs/architecture/cortex-integration.md` — how the arbitrator plugs into the 11-step workflow at Step 0.5

---

**Document status:** pre-implementation spec, v1.7. Behaviors encoded here are normative. Deviations require updating this spec before the code.
