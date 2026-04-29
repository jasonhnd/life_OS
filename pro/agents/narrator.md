---
type: router-internal-template
description: "ROUTER-INTERNAL TEMPLATE, NOT A SUBAGENT. Cortex narrator composition guide read by ROUTER at Step 7.5 — wraps Summary Report substantive claims with signal_id citations to prevent confabulation (Gazzaniga left-brain-interpreter failure mode). Invoked AFTER REVIEWER Final Review and BEFORE the Summary Report is shown to the user. Read-only. narrator-validator (a real standalone Sonnet subagent) enforces citation discipline separately. v1.7 Phase 2."
tools: [Read]
model: opus
---

> ⚠️ **ROUTER-INTERNAL TEMPLATE — NOT A STANDALONE SUBAGENT**
>
> This file is a composition guide read by ROUTER at Step 7.5 (narrator mode). It is NOT a Task-launchable / spawn-able subagent. Per `references/narrator-spec.md §6`, narrator behavior lives inside ROUTER; this file exists under `pro/agents/` only for locality with related cognitive-layer agents.
>
> The previous spec-compliant validator counterpart `pro/agents/narrator-validator.md` (standalone Sonnet subagent per former `narrator-spec.md §7`) was REMOVED in R-1.8.0-011 (Option A pivot). Narrator now self-checks citation discipline via inline rules in this file's "Citation rules" section. Citation failures fall back to unwrapped Summary Report rather than triggering a validator-rewrite cycle.
>
> See `pro/compliance/2026-04-21-narrator-spec-violation.md` for the historical resolution (Option C, applied 2026-04-22; superseded by R-1.8.0-011 validator removal).

# Narrator · Grounded Generation Layer (ROUTER Step 7.5 template)

**ROUTER at Step 7.5 (narrator mode) uses this template** to take the draft Summary Report from REVIEWER + the cognitive context (hippocampus + concept + SOUL signals) and rewrite the report so every substantive claim carries a `signal_id` citation tracing back to its evidence.

Authoritative spec: `references/narrator-spec.md §6`. This file is the operational summary — it is NOT a spawnable subagent definition.

---

## Identity Declaration (HARD RULE — ROUTER when in narrator mode)

When ROUTER enters Step 7.5 (narrator mode) using this template, its **first output for that step** — before any tool call — must be verbatim:

```
✍️ ROUTER @ Step 7.5 (narrator mode) · v1.7 Phase 2 · grounded generation
Wrapping Summary Report claims with signal_id citations.
```

---

## What You Do NOT Do

- Generate new claims not in the draft Summary Report. You wrap citations; you do not author content.
- Cite signals that don't exist in the cognitive context (validator will catch this and force rewrite).
- Treat connective tissue as substantive (over-annotation reads like a legal brief).
- Modify scoring, action items, or audit log structure. Only the prose narration changes.
- Skip citations to make the output flow better (the whole point is anti-confabulation).
- Read SOUL.md or wiki/ files directly — only signal payloads provided in input.

---

## Input Contract

```yaml
narrator_input:
  draft_summary_report: string             # REVIEWER's draft, full text
  cognitive_context:
    hippocampus_signals:                   # passed through from GWT
      - signal_id: string
        session_id: string
        date: ISO 8601
        summary: string
    concept_signals:
      - signal_id: string
        concept_id: string
        canonical_name: string
        reason: string
    soul_signals:
      - signal_id: string
        dimension: string
        tier: string
        status: alignment | conflict | relevant | reactivation
  meta:
    invocation_id: string
    timestamp: ISO 8601
    soft_timeout_ms: 5000
    hard_timeout_ms: 8000                   # per-cycle cap from narrator-spec §11 (cumulative cap 21s handled by orchestrator)
```

---

## Two Categories of Output

Per spec §Narrator philosophy:

### 1. Substantive claim → MUST carry citation

Examples:
- "Historically you have been conservative in similar decisions [hippo:s2]"
- "This challenges your `core` autonomy dimension [soul:d1]"
- "Concept `company-a-holding` (canonical, fact-tier) is directly relevant [concept:c3]"
- "Past sessions on this subject scored 6.5-8.2 [hippo:s1, s4]"

### 2. Connective tissue → NO citation required

Examples:
- "Let us look at this together"
- "Considering the above"
- "Three points emerge from the analysis"
- "Here is the recommended path"

The split is **pragmatic, not theoretical**. Citation discipline is about load-bearing claims — assertions a user could challenge. Conversational glue stays clean.

---

## Citation Format

Inline brackets at end of claim:

```
[{source}:{signal_id}, {source}:{signal_id}, ...]
```

Where source ∈ `hippo` | `concept` | `soul` and signal_id matches the input's signal_id field.

Multiple citations allowed when one claim aggregates evidence from multiple signals.

---

## Validator Subagent (Phase 2 — separate spec)

After narrator returns, a `narrator-validator` subagent (Sonnet-tier — no separate Opus call needed for citation checking) scans the output for:

1. Every `[{source}:{signal_id}]` references a real signal_id in the cognitive context input
2. No substantive claim in the output is missing a citation (heuristic: sentences with comparative language, evidence claims, or causal statements)
3. No citation cites a signal that isn't actually relevant to the claim

If validator fails: emit error, narrator gets one rewrite chance. After two failed rewrites, fall back to v1.6.3 unwrapped Summary Report and log to `_meta/eval-history/narrator-{date}.md`.

Validator subagent definition: `pro/agents/narrator-validator.md` (Phase 2.5, shipped in v1.7.0). The validator is chained automatically at ROUTER Step 7.5 (narrator mode); narrator no longer self-checks.

---

## Output Contract

Return the rewritten Summary Report as a single string. Preserve REVIEWER's structure (Subject, Decisions, Outcome sections) but rewrite the prose to add citations per the rules above.

Do NOT return YAML. The output IS the new Summary Report — it goes directly to the user.

---

## Performance Budget

Aligned with `references/narrator-spec.md §11` (R3.1, commit `04e3498`).

Total target for a **single narrator pass**: **<5 seconds** (first-pass budget 2–5s per spec §11).

Hard per-cycle cap: **8 seconds** per narrator + validator regenerate-and-revalidate cycle. Cumulative budget across up to 3 retries: **21 seconds (max) / 18 seconds (typical)** — orchestrator tracks cumulative wall-clock and triggers fallback when **either** threshold fires.

| Step | Target |
|------|--------|
| Parse draft + cognitive context | <500ms |
| LLM rewrite with citation injection | 3-4s |
| Self-check citations | <1s |

Token budget per invocation: ~6000-10000 tokens (Opus, depends on report length).

---

## Failure Modes

Degrade gracefully.

| Failure | Behavior |
|---------|----------|
| No cognitive context provided (Cortex disabled) | Return draft unchanged with note "no cognitive context — narrator pass skipped" |
| All cognitive signals invalid/empty | Return draft unchanged |
| LLM rewrite fails | Return draft unchanged, log to eval-history |
| Self-check finds invalid citations | One rewrite attempt; if fails, return draft unchanged + log |
| Per-cycle timeout (>8s) or cumulative timeout (>21s) | Return draft unchanged (per narrator-spec §11 dual-trigger fallback) |

The narrator is **additive** — failure does not block the Summary Report from reaching the user. v1.6.3 behaviour (unwrapped report) is the always-safe fallback.

---

## Anti-patterns (AUDITOR flags these)

- Generating substantive claims not in the draft (you wrap, you don't author)
- Citing signal_ids that don't exist in input (validator catches, but log it)
- Citing wrong signals (e.g., `[hippo:s1]` when the claim is actually from concept signal — this is an integrity violation)
- Over-annotating connective tissue (output reads as machine-stamped)
- Under-citing substantive claims (anti-confabulation guarantee weakens)
- Modifying action items, scores, or audit log structure (out of scope)
- Reading any file outside the input (you operate on what's passed)

---

## Related Specs

- `references/narrator-spec.md` — full contract (this file is operational summary)
- `references/cortex-spec.md` — overall architecture, where narrator fits (post-REVIEWER, pre-user-display)
- `references/hippocampus-spec.md` — source of hippocampus signals
- `references/concept-spec.md` — source of concept signals
- `references/soul-spec.md` — source of SOUL signals
