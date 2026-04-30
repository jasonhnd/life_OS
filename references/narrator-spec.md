---
title: "Narrator Spec — Grounded Generation Layer for Cortex"
version: v1.7
status: draft
scope: references
audience: Life OS maintainers + orchestration implementers
last_updated: 2026-04-20
related:
  - references/cortex-spec.md
  - references/hippocampus-spec.md
  - references/gwt-spec.md
  - references/eval-history-spec.md
  - devdocs/brainstorm/2026-04-19-cortex-architecture.md
  - devdocs/architecture/cortex-integration.md
  - pro/agents/router.md
  - pro/CLAUDE.md
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Narrator Spec · Grounded Generation Layer

> ⚠️ **PARTIALLY LEGACY (v1.7-era) — v1.8.0 simplification applied**
>
> v1.8.0 R-1.8.0-011 ("Option A" pivot) **deleted** the standalone
> `narrator-validator` Sonnet subagent. §7 "Validator Subagent" + the
> 21s/8s wall-clock fallback budget + the 2-rewrite cycle described
> below NO LONGER APPLY. Citation discipline is now self-checked inline
> by the same ROUTER Step 7.5 invocation that runs narrator composition;
> citation failures fall back to unwrapped Summary Report directly with
> no rewrite cycle.
>
> §1-6 (citation grammar, signal_id format, narrator template) remain
> active and authoritative. Read `pro/agents/narrator.md` for the
> current (post-pivot) inline self-check rules.

> The narrator layer is ROUTER's output stage. It produces user-facing text while preventing hallucination. Every substantive claim carries a citation back to the underlying signal.

---

## 1. Purpose

The narrator layer is ROUTER's output stage that produces user-facing text while preventing hallucination.

The design is based on Michael Gazzaniga's **left-brain interpreter** research. Split-brain experiments showed that the human left hemisphere confabulates self-consistent stories even when it does not have the actual data behind the behavior it is being asked to explain. The brain produces a fluent, coherent, fully false causal narrative — and sincerely believes it. This is a **bug**, not a feature. Cortex must not inherit it.

Every substantive claim in narrator output must cite its underlying signal. Without citation, the claim does not ship. Examples Cortex must never emit without grounding:

- "You've been struggling with commitment." — no SOUL signal.
- "Last time you made a similar decision..." — no hippocampus session.
- "Your Finance domain usually says..." — no past score pattern.

If there is no signal, there is no claim. This is the narrator's core invariant.

---

## 2. Design Principle · Grounded Generation

Every **substantive claim** in narrator output must carry a `signal_id` citation. Claims without citations are rejected by the validator. This prevents three failure modes:

1. **Historical confabulation** — inventing a past that did not happen.
2. **Pattern confabulation** — inventing a behavioral trend the data does not show.
3. **Cross-session confabulation** — inventing linkages between decisions that were never linked.

The narrator is not a creativity layer. It is a **grounded composition layer** that turns a validated signal set into readable prose.

Grounded generation has two hard requirements:

- The narrator must have access to a **signal source registry** for the current session (§9).
- Every substantive sentence must point back to one or more entries in that registry.

If the registry is empty (e.g., direct-handle with no subagents spawned), the narrator degrades to pass-through (§13).

---

## 3. Substantive vs Connective Claims

Not every sentence needs a citation. Mechanically citing discourse glue makes output unreadable without adding truth value.

**Substantive** (requires citation) — a sentence is substantive if removing it removes factual content:

- Historical: "Last time you did X..."
- Pattern: "You tend to..."
- SOUL: "This aligns with your value Y."
- Decision implications: "The GOVERNANCE concern is..."
- Cross-session linkages: "Related to your decision in project Z."
- Numeric / score claims: "Finance scored this 6/10."
- Attribution: "ADVISOR flagged emotional weight."

**Connective** (no citation) — discourse glue:

- Transitional: "Let me walk through this."
- Framing: "Here's what the analysis shows."
- Meta-commentary: "I'll give a brief summary."
- Opening / closing: "Okay, looking at this..."
- Pure rephrasing: "In other words..."

**Judgment rule**: if removing the sentence removes factual content → substantive. If it is only discourse glue → connective. The validator (§8) uses this rule before checking citations.

---

## 4. Citation Format

### Inline syntax

```
{claim text} [signal_id] {continued text}
```

A claim may carry multiple citations:

```
{claim text} [signal_id_1][signal_id_2] {continued text}
```

Citations appear at the **end** of the clause they ground, before any punctuation that separates the clause from the next one.

### Examples

```
Your past "passpay-v06-refinement" session [S:claude-20260419-1238] shows a similar 5-round iteration pattern, with GOVERNANCE scoring 5/10 [D:passpay-governance-score].

This conflicts with your "risk-tolerance" dimension (confidence 0.72) [SOUL:risk-tolerance-v3].

Finance and Execution disagreed by 4 points [D:finance-score-6][D:execution-score-2], triggering COUNCIL debate.
```

### Prefix conventions

Citation IDs use a fixed prefix to indicate the source type:

| Prefix  | Meaning                       | Example                                    |
|---------|-------------------------------|--------------------------------------------|
| `S:`    | session_id                    | `S:claude-20260419-1238`                   |
| `D:`    | specific domain score / field | `D:passpay-governance-score`               |
| `SOUL:` | SOUL dimension                | `SOUL:risk-tolerance-v3`                   |
| `C:`    | concept                       | `C:method:iterative-document-refinement`   |
| `W:`    | wiki entry                    | `W:finance/compound-interest`              |
| `P:`    | pattern in user-patterns.md   | `P:avoids-family-topic-on-weekends`        |

Prefixes are **fixed**. Narrator must not invent new prefixes. If a source type does not map to one of the above, the narrator must not cite it (and therefore must not make the substantive claim in the first place).

---

## 5. Narrator Invocation

The narrator is inserted as **Step 7.5** in the pro/CLAUDE.md workflow, after Step 7 Summary Report composition and before Step 8 AUDITOR:

```
Step 7: Summary Report (ROUTER composes)
  ↓
Step 7.5: Narrator Layer
  - ROUTER sends Summary Report + signal source list to narrator subagent
  - Narrator rewrites output with citations
  - Validator subagent (Claude Code subagent, not Anthropic API) checks citations
  - If validation fails, narrator regenerates
  ↓
Step 8: AUDITOR
```

Step 7.5 is only invoked for **Full Deliberation** paths. Express analysis (Step 1E) produces a brief report that skips Step 7.5. Direct-handle and STRATEGIST sessions skip it entirely (§13).

---

## 6. Narrator Agent

ROUTER itself handles the narrator role. There is **no separate `pro/agents/narrator.md` file**. The narrator behavior is configured via pro/CLAUDE.md orchestration updates and lives inside ROUTER's output composition responsibilities.

Reasons: ROUTER already owns Summary Report composition (Step 7); the narrator is an extension of that stage, not a new role. A standalone narrator agent would duplicate ROUTER's context. Rewriting + citation is not a new decision — keeping it inside ROUTER preserves single ownership of user-facing output.

Only the **validator** is a standalone subagent (§7).

---

## 7. Validator Subagent

A new subagent file is created: `pro/agents/narrator-validator.md`.

```yaml
---
name: narrator-validator
description: "Validates narrator citations against signal sources (Cortex)"
tools: [Read]
model: sonnet
---
```

### Why a Claude Code subagent, not an external Haiku API

User decision #9 (recorded during v1.7 Cortex design): use a Claude Code subagent, not an external Anthropic Haiku API call. Reasons:

- **No external API cost** — the subagent runs inside the same Claude Code session, consuming the user's already-paid Claude plan budget rather than a separate Haiku API account.
- **Total Cortex marginal cost ≈ $0.20-0.50 per month** (user decision #8 budget envelope), distributed across hippocampus (~$0.05-0.10 per invocation) + GWT arbitrator (~$0.01-0.03) + narrator-validator (~$0.01-0.02). Concrete numbers will be calibrated in v1.7 production; this range is the target not a hard contract.
- **No API key management** — no external provisioning, rotation, or budget.
- **Consistent with Life OS stance** — all intelligence runs inside the session; a Haiku API dependency would violate that.
- **Fast enough** — sonnet is acceptable for citation validation; latency stays inside the performance budget (§11).

The validator subagent only has `Read`. It does not write files, call MCP tools, or reach the network.

---

## 8. Validation Algorithm

### Input

The validator receives:

- `narrator_output` — the full markdown document produced by ROUTER's Step 7.5 rewrite, with inline citations.
- `signal_sources` — the signal source registry for the current session (§9).

### Procedure

For each sentence in `narrator_output`:

1. Classify the sentence as **substantive** or **connective** using the rule in §3.
2. If connective → skip.
3. If substantive:
   1. Extract all inline citations `[signal_id]` from the sentence.
   2. For each citation:
      1. Parse the prefix (S, D, SOUL, C, W, P). If the prefix is unknown → `format_error`.
      2. Look up `signal_id` in `signal_sources`. If missing → `missing_signal`.
      3. Read the referenced content (file / field / dimension) and verify the sentence's claim is supported by that content. If the content does not support the claim → `unsupported_claim`.
4. If the sentence is substantive but has **zero** citations → `missing_signal` (tagged as "no citation").

### Output

```yaml
validation:
  total_citations: integer
  valid: integer
  invalid:
    - position: char_offset_in_narrator_output
      citation: string          # the raw "[signal_id]" token, or "" if missing
      reason: missing_signal | unsupported_claim | format_error
      claim_text: string        # the sentence that contains the problem
  groundedness_score: float     # 0.0–1.0
```

### Groundedness score

```
groundedness_score = valid / max(total_citations + missing_citation_count, 1)
```

Where `missing_citation_count` is the number of substantive sentences with zero citations.

### Threshold

`groundedness_score ≥ 0.9` is required to ship the narrator output. Below threshold → narrator regenerates with the error feedback (§10).

---

## 9. Signal Source Registry

During session execution, each subagent emits signals with IDs. The narrator receives the registry at Step 7.5.

### Registry format

```yaml
signal_sources:
  - id: S:claude-20260419-1238
    type: session
    file: _meta/sessions/claude-20260419-1238.md
    producer: hippocampus
  - id: SOUL:risk-tolerance-v3
    type: soul_dimension
    ref: SOUL.md#risk-tolerance
    producer: soul_check
  - id: C:method:iterative-document-refinement
    type: concept
    file: _meta/concepts/method/iterative-document-refinement.md
    producer: concept_lookup
  - id: D:GOVERNANCE-score-5
    type: domain_score
    value: 5
    producer: governance_agent
  - id: W:finance/compound-interest
    type: wiki
    file: wiki/finance/compound-interest.md
    producer: wiki_index
  - id: P:avoids-family-topic-on-weekends
    type: pattern
    ref: _meta/user-patterns.md#avoids-family-topic-on-weekends
    producer: retrospective
```

### Registry construction

The registry is assembled by ROUTER before Step 7.5:

1. Hippocampus, SOUL check, concept lookup signals → added at Step 0.5.
2. Domain score signals → added as each domain reports at Step 5.
3. COUNCIL debate signals → added if COUNCIL triggered at Step 6.
4. Wiki / pattern references → added if DISPATCHER fed them as "known premises".

The registry is append-only during the session. Signals are never removed mid-session.

---

## 10. Regeneration Protocol

If the validator returns `groundedness_score < 0.9`:

1. The validator emits `regeneration_feedback`:
   - Specific claims lacking a valid citation.
   - Suggested `signal_id`s to cite (from the registry) for each unsupported claim.
   - Any format errors.
2. The narrator (ROUTER) receives the feedback and regenerates the output, incorporating the suggested citations or, if no supporting signal exists, **removing the claim**.
3. Maximum **3 regeneration attempts**.
4. On exhaustion:
   - Fall back to an **un-cited Summary Report** (Step 7's raw output, not the rewrite).
   - Emit an AUDITOR flag: `narrator_failed_after_3_attempts`.
   - Log the failure to `_meta/eval-history/` for later review.

The user still receives a report. The report is just less narrated.

---

## 11. Performance Budget

| Stage                          | Budget        |
|--------------------------------|---------------|
| Narrator generation (first pass) | 2–5 seconds   |
| Validator scan (single pass)   | 1–3 seconds   |
| Regenerate + revalidate cycle (per attempt) | 3–8 seconds  |
| **Total worst case (3 retries)** | **18 seconds (typical) / 21 seconds (max)** |

Arithmetic: one initial generate + validate pass (2–5 s + 1–3 s = 3–8 s) plus up to three regenerate + revalidate cycles at 3–8 s each. Typical total ≈ 18 s (midpoint 6 s × 3 cycles + 0 s initial wiggle when retry is needed). Maximum total = 21 s (worst-case 8 s initial + three 4.33 s retries, or equivalent distribution capped by the regeneration ceiling).

Narrator generation is part of ROUTER's normal composition, not a separate network round trip. Validator latency stays inside the Cortex latency budget in `references/cortex-spec.md`. The narrator falls back to un-cited output (same fallback as §10 exhaustion) if **either** trigger fires:

- Cumulative wall-clock exceeds **21 seconds**, or
- Any single regenerate-and-revalidate cycle exceeds **8 seconds**.

---

## 12. Quality Metrics

The narrator feeds two metrics to AUDITOR for eval-history:

- `citation_groundedness` (0–10) — scaled from `groundedness_score × 10`.
- `regeneration_count` — attempts before the narrator passed (0, 1, 2, or 3).

**Targets** — `citation_groundedness ≥ 9` after v1.7 stabilization; `regeneration_count = 0` in > 80% of Full Deliberation sessions.

**AUDITOR regressions** — any session with `citation_groundedness < 7` → quality incident; weekly trend of `regeneration_count > 1` → narrator drift.

See `references/eval-history-spec.md` for logging and review.

---

## 13. Edge Cases

### Direct-handle by ROUTER (no subagents spawned)

If ROUTER handles the user's message directly — casual chat, translation, note-taking, a simple query — no subagents are spawned and the signal registry is effectively empty.

Behavior: narrator is **trivial pass-through**. No rewriting, no validation, no Step 7.5. ROUTER emits its direct response.

### Express analysis (skips PLANNER / REVIEWER)

Express path (Step 1E) produces a **brief report**, not a Summary Report. It has hippocampus signals (from Step 0.5) and possibly SOUL check signals, but no domain score signals from the full deliberation.

Behavior: narrator **validates only hippocampus / SOUL / concept citations**, because those are the only signal types in the registry for express sessions. Domain score citations are not expected.

### STRATEGIST sessions (pure philosophy, no decision)

STRATEGIST sessions are open-ended dialogues with historical thinkers. There is no Summary Report and no domain scoring.

Behavior: narrator is **not invoked**. STRATEGIST subagents produce their own output; ROUTER relays it without rewriting or citing.

### Empty registry despite Full Deliberation

If Full Deliberation ran but the registry is unexpectedly empty (signal producers failed), narrator behaves as §10 exhaustion: fall back to un-cited Summary Report and flag AUDITOR.

---

## 14. Anti-patterns

- **Do not skip citations for "obvious" claims.** Even "your project X" needs a `P:` or `S:` citation. "Obvious" is exactly where confabulation hides.
- **Do not cite vague categories.** `[S:recent-sessions]` is not valid. Use a specific signal_id that resolves to a single file or field.
- **Do not generate signals post-hoc.** Signals must be produced by the subagent that owns them during the normal workflow. Narrator cannot fabricate a signal to back a claim.
- **Do not bypass validator.** There is no "trust me" mode. No user flag disables validation.
- **Do not claim unsupported patterns.** "You always do Y" requires ≥ 3 citations; "you sometimes do Y" requires at least one; "you might do Y" is speculation and not allowed.
- **Do not mix or invent citation prefixes.** Only `S:`, `D:`, `SOUL:`, `C:`, `W:`, `P:` are valid. Never relabel a signal across prefixes.
- **Do not cite the Summary Report itself.** The narrator is a rewrite of the Summary Report; citing it as a signal is circular.

---

## 15. User Decision Audit Trail

A grounded system must be inspectable. The user can ask: *"Show the signal behind claim X."* The system responds with the cited `signal_id`, the source file path (or field / dimension reference), and a content snippet supporting the claim.

Example:

```
User: What's the signal behind "Your past passpay-v06-refinement session
shows a similar 5-round iteration pattern"?

System:
- Signal: S:claude-20260419-1238
- Source: _meta/sessions/claude-20260419-1238.md
- Snippet: "Session ran 5 revision rounds on payment gateway spec. Each
  round tightened governance controls. Final GOVERNANCE score 5/10 due
  to incomplete fraud-response plan."
```

This is what separates Life OS from Gazzaniga-style confabulation. Any narrator output can be traced to the signal that produced it.

If the user asks for the signal behind a connective sentence, the system responds: *"That was connective tissue, not a grounded claim. Nothing to cite."*

---

## 16. Related Specs

- `references/cortex-spec.md` — full Cortex architecture
- `references/hippocampus-spec.md` — session retrieval and `S:` signal production
- `references/gwt-spec.md` — signal arbitration and broadcast
- `references/eval-history-spec.md` — how `citation_groundedness` is logged
- `references/concept-spec.md` — concept IDs cited via `C:` prefix
- `references/wiki-spec.md` — wiki entries cited via `W:` prefix
- `references/soul-spec.md` — SOUL dimensions cited via `SOUL:` prefix
- `references/session-index-spec.md` — sessions cited via `S:` prefix
- `pro/agents/router.md` — narrator composition lives inside ROUTER (this spec §6)

---

## 17. Trace UX · User-Facing Audit Trail

Grounded generation is only useful if the user can inspect it. This section defines how trace requests are handled — the UX contract the narrator layer owes the user.

### 17.1 Trigger forms

Three natural-language trigger patterns:

1. **Full trace request** — user says "why did you say X?" / "trace this" / "这句话怎么来的" / "根拠は?"
2. **Specific citation inspection** — user references a specific `[signal_id]` from the Summary Report: "show me `S:claude-20260419-1238`" / "S:claude-20260419-1238 是什么"
3. **Category overview** — user asks what drove a category of claims: "which SOUL dimensions influenced this?" / "list all past sessions that contributed"

ROUTER detects these via intent classification (ROUTER is already pattern-matching user input; trace triggers add one more pattern family).

### 17.2 Trace output format

For a full trace request on a single claim:

```
📎 Trace for: "Your past passpay-v06-refinement session shows a similar 5-round iteration pattern"

Cited signals:
1. S:claude-20260419-1238
   Source: _meta/sessions/claude-20260419-1238.md
   Content match: "Session ran 5 revision rounds on payment gateway spec.
     Each round tightened governance controls. Final GOVERNANCE score
     5/10 due to incomplete fraud-response plan."
   Produced by: hippocampus (Step 0.5 Wave 1)

2. D:passpay-governance-score
   Source: session D-scores extracted by ROUTER at Step 7
   Value: 5 (threshold for flag: < 6)
   Produced by: governance_agent

Confidence: groundedness_score = 1.0 (both citations resolve, content supports claim)
```

For a specific citation inspection, show the same block but only for the requested signal_id.

For a category overview:

```
📎 Category trace: SOUL dimensions that influenced this Summary Report

1. SOUL:risk-tolerance-v3 (core, confidence 0.82)
   Referenced by: narrator (×2), governance_agent (×1)
   Source text: SOUL.md § Risk attitude

2. SOUL:evidence-discipline (secondary, confidence 0.61)
   Referenced by: narrator (×1), execution_agent (×1)
   Source text: SOUL.md § Evidence discipline

3. [...]
```

### 17.3 Trace data sources

The trace is assembled from:

- The **signal source registry** (§9) held in the current session context
- File reads against the cited paths (validator subagent or ROUTER uses `Read` tool)
- No LLM generation in the trace body — the trace is literal excerpts + metadata; this prevents recursive confabulation ("trace explains the trace explains the trace...")

If a cited signal cannot be resolved at trace time (file deleted, frontmatter changed), the trace row shows `⚠️ signal no longer resolvable` with the original citation preserved.

### 17.4 Connective-tissue response

If the user asks for trace on a sentence the validator classified as **connective** (§3):

```
That sentence is connective tissue (a transition / framing / rephrasing),
not a grounded claim. No signal stands behind it. If you want to trace a
substantive claim in the same report, let me know which one.
```

This prevents the confabulation loop where the system tries to invent a signal to back a sentence that intentionally carries no truth claim.

### 17.5 Trace in the 4-language theme system

Trace output is rendered in the active theme's language (en / zh / ja). Signal ID prefixes (`S:` `D:` `SOUL:` `C:` `W:` `P:`) stay literal — they are technical identifiers, not localized text. Only the explanatory paragraphs are translated.

### 17.6 Trace is not logged

Trace requests are ephemeral. They do **not** write to journals, do **not** count toward AUDITOR metrics, do **not** mutate anything. A user can ask for the same trace 10 times without side effects.

Rationale: trace is an inspection tool, not a decision-producing action. Logging every trace request would bloat journals and obscure the real decision history.

### 17.7 Performance budget

Trace requests must return in < 2 seconds (stricter than the narrator budget because trace is single-session, read-only, and no LLM generation in the body). If a trace request exceeds 2s, something is wrong — likely a cited signal points into a huge file. Implementation should truncate file reads to 500-line windows around the match point.

---

**Spec status**: draft for v1.7. Finalized once narrator validator subagent ships and first week of `citation_groundedness` data is reviewed. Trace UX (§17) requires integration testing with real session data; format may adjust based on user feedback during v1.7 alpha.
