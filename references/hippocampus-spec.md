---
title: "Hippocampus · Agent Contract Spec"
scope: v1.7 Cortex Phase 1
audience: Life OS developers + orchestrator
status: spec
version: v1.7
layer: Cortex Phase 1 (cognitive retrieval)
related:
  - devdocs/brainstorm/2026-04-19-cortex-architecture.md
  - devdocs/architecture/cortex-integration.md
  - references/cortex-spec.md
  - references/concept-spec.md
  - references/session-index-spec.md
  - references/gwt-spec.md
  - pro/agents/hippocampus.md
---

# Hippocampus · Agent Contract Spec

> This document specifies the **hippocampus subagent** contract: what it receives, what it returns, how it retrieves, and how it fails. The agent itself lives at `pro/agents/hippocampus.md`; this spec is the authoritative source for its behavior.

---

## 1. Purpose

**Hippocampus** is a Claude Code subagent that performs **cross-session memory retrieval** for the Pre-Router Cognitive Layer (Step 0.5 in the v1.7 workflow).

Its single responsibility: given the user's current message, produce a **concept-level summary of relevant past sessions** so that the GWT arbitrator can consolidate it with other Pre-Router cognitive signals into an annotated input for ROUTER.

It is modeled after the biological **hippocampus** — the brain region responsible for binding new experiences to episodic memory and retrieving episodes on demand. In Life OS, it bridges the gap between "what the user just said" and "what the system already knows from prior sessions."

Hippocampus does **not**:

- Replace ROUTER triage
- Modify session files or concept files (read-only)
- Persist retrieval results outside the current frame
- Know about other Pre-Router cognitive layer outputs (enforced isolation)

---

## 2. Trigger

**Frequency**: Every Cortex-enabled user message that enters ROUTER, including Start Session triggers, after RETROSPECTIVE housekeeping completes when applicable.

**Parallelism**: Runs in parallel with two other Pre-Router Cognitive Layer components:

- Concept lookup (reads `_meta/concepts/INDEX.md`)
- SOUL dimension health check (reuses RETROSPECTIVE's SOUL Health Report)

**Execution budget**:

- Soft timeout: **5 seconds** — the upper bound GWT arbitrator waits before proceeding with partial results. This does NOT force hippocampus to return; hippocampus may keep running until hard timeout. Any result arriving between 5s and 15s is logged to the session trace for post-hoc review but is NOT injected into the current session's ROUTER input (GWT already consolidated and handed off).
- Hard timeout: **15 seconds** — hippocampus must return whatever it has and terminate. Results returned between 5s–15s enter the trace only.

**Skipped only when**:

- Review Mode (no user decision pending)
- When the orchestrator explicitly requests `--no-cortex` (degraded mode, for debugging)

---

## 3. Agent Definition Frontmatter

The actual agent file (`pro/agents/hippocampus.md`) must declare:

```yaml
---
name: hippocampus
description: "Cortex hippocampal retrieval — cross-session memory activation for Pre-Router Cognitive Layer"
tools: [Read, Grep, Glob]
model: opus
---
```

**Tool constraint rationale**:

- `Read`: load INDEX.md and individual session markdown files
- `Grep`: fast pre-filter of INDEX.md before LLM judgment
- `Glob`: enumerate `_meta/concepts/{domain}/*.md` for Wave 2/3 lookup
- **No Write / Edit**: enforces read-only contract; modifications to concept files happen in ARCHIVER Phase 2 only

**Model**: `opus`. The retrieval involves semantic matching across variable phrasing; Haiku does not have sufficient judgment for Wave 1 relevance scoring. v1.7 runs the entire Wave 1 pass on Opus.

---

## 4. Input Contract

Hippocampus receives from the orchestrator (passed as structured input in the subagent prompt):

```yaml
hippocampus_input:
  current_user_message: string           # raw text, as typed
  extracted_subject: string | null       # non-null if ROUTER already performed intent clarification
  current_project: string                # bound project scope, e.g. "passpay"
  current_theme: string                  # e.g. "zh-classical", "ja-kasumigaseki"
  session_context:
    recent_inbox_items: [string]         # top 3-5 items from _meta/inbox/
    current_strategic_lines: [string]    # line IDs from _meta/strategic-lines.md
  meta:
    invocation_id: string                # UUID for tracing
    timestamp: ISO 8601
    soft_timeout_ms: 5000
    hard_timeout_ms: 15000
```

**Explicitly NOT received** (enforced by the orchestrator — violation = information isolation breach):

- Other Pre-Router Cognitive Layer outputs (concept lookup results, SOUL check results)
- Previous session transcripts (only summaries via INDEX.md)
- SOUL.md full content (privacy boundary — hippocampus sees concept tags, not identity narrative)
- User's platform / environment details beyond `current_theme`
- Other agents' thought processes (per `pro/CLAUDE.md` Information Isolation table)

Why this isolation matters: hippocampus must produce an **independent signal** that GWT can weigh against other signals. If it already sees SOUL check output, it loses the ability to surface complementary-but-different retrieval angles. Competition requires independence.

---

## 5. Retrieval Algorithm (3-Wave Spreading Activation)

The algorithm is modeled on biological **spreading activation** (Collins & Loftus, 1975) adapted to Life OS's markdown-first constraints. Three waves, each widening the retrieval net but with decaying confidence.

### Wave 1 — Direct Match

1. **Read** `_meta/sessions/INDEX.md` (editor-generated one-line-per-session index; see `references/session-index-spec.md` for format).
2. **Grep pre-filter**: if `extracted_subject` is available, run a case-insensitive regex pass across INDEX.md to cut 1000+ entries down to <50 candidates. If not, skip to LLM step with full INDEX.
3. **LLM judgment** (user decision #3 — no embeddings, no vector DB): feed the pre-filtered index lines to Opus with the prompt:
   > "Current subject: `{subject}`. Below are past session summaries. Return the top 3-5 whose subject is semantically related to the current one. Return JSON only."
4. **Read full content** of each candidate from `_meta/sessions/{session_id}.md`.
5. **Score**: `score_wave1 = 0.6 * subject_similarity + 0.4 * keyword_overlap` where both sub-scores are Opus-judged on 0-1.
6. Keep the top 3-5 sessions.

**Output of Wave 1**: `[{session_id, score, matched_concepts}]` — the seed set for downstream waves.

### Wave 2 — Strong Neighbors

From Wave 1 sessions, expand along the **concept graph** to find related sessions that Wave 1 missed because they shared no surface keywords.

1. For each Wave 1 session, extract the `concepts_activated` and `concepts_discovered` lists from its YAML frontmatter.
2. For each concept ID, **Read** `_meta/concepts/{domain}/{concept}.md`.
3. From that concept's `outgoing_edges` list, **follow edges with weight ≥ 3** (strong synapse — see `references/concept-spec.md` for weight semantics).
4. For each neighbor concept, look up its `provenance.source_sessions` field — this yields sessions where the neighbor concept was activated.
5. **Deduplicate** against the Wave 1 set, keep the **top 2-3 new sessions** ranked by the **4-signal relevance model** (v1.8.0 R-1.8.0-013, borrowed from llm_wiki, simplified for LLM-friendly computation):
   ```
   relevance(candidate, current) =
     3 × direct_link_count(candidate, current)
   + 4 × source_overlap_count(candidate, current)
   + 2 × common_neighbor_count(candidate, current)
   + 1 × type_affinity(candidate, current)
   ```
   - **direct_link_count**: number of `[[wikilinks]]` from candidate body/frontmatter to current message's referenced pages (Grep candidate file for `[[<id>]]` patterns)
   - **source_overlap_count**: number of `concepts_activated` shared between candidate's session and current message's inferred concepts
   - **common_neighbor_count**: simplified Adamic-Adar — count of concepts that appear in both candidate's `outgoing_edges` and current's referenced concept set. (Original Adamic-Adar uses `1/log(degree)` but LLM cannot reliably compute log; we use plain count.)
   - **type_affinity**: 1.0 if candidate page type == current message's primary referenced page type (e.g., both about a person, both comparisons); 0.5 if related — pairs in the related set are: `concept ↔ wiki`, `concept ↔ person`, `concept ↔ method`, `wiki ↔ method`, `person ↔ comparison`; 0.0 otherwise. Page types per `references/wiki-spec.md` § Page Taxonomy.

**Why these weights**: source_overlap (×4) dominates because shared sessions = strong evidence of co-relevance. direct_link (×3) is high-precision but lower-recall. common_neighbor (×2) catches indirect via concept graph. type_affinity (×1) is a tie-breaker.

**Pre-R-1.8.0-013 fallback**: if candidate concept files lack the new wikilink format and `type:` frontmatter, the formula degrades gracefully: missing signals contribute 0, others still score. Migrate via `scripts/prompts/migrate-to-wikilinks.md` to enable full scoring.

**Bounded by design**: Wave 2 adds at most 3 sessions. This prevents concept-graph fan-out from exploding the retrieval budget.

### Wave 3 — Weak Neighbors

Extend the graph once more, at lower weight threshold. This catches the "unexpected but useful" connection that neither Wave 1 (surface) nor Wave 2 (strong edges) surfaces.

1. From Wave 2 sessions' concepts, follow edges with **weight ≥ 1** (any active edge).
2. Apply the same provenance lookup as Wave 2.
3. Deduplicate, keep top 1-2.
4. Score:
   ```
   score_wave3 = 0.3 * edge_weight_normalized + 0.4 * concept_overlap + 0.3 * recency_decay
   ```
   Weaker weight on raw edge strength, more weight on semantic overlap.

**Explicit cap**: Wave 3 contributes at most 2 sessions, and the entire retrieved set must not exceed **5-7 sessions total**. Anything beyond that degrades GWT arbitration quality (too many signals to weigh against).

### Final Output

Rank all retrieved sessions by their within-wave score, but **annotate which wave** each came from — GWT needs that provenance to calibrate salience.

---

## 6. Output Contract

Hippocampus returns a structured YAML block as its final message to the orchestrator:

```yaml
hippocampus_output:
  current_subject: string
  retrieved_sessions:
    - session_id: string
      date: ISO 8601
      relevance_score: float              # 0-1, wave-calibrated
      reason: string                      # one sentence, why this matched
      wave: 1 | 2 | 3
      summary: string                     # 1-2 sentences, the session's core substance
      key_decisions: [string]             # 1-3 decision titles from the session
      applicable_signals:
        - signal_type: "decision_analogy" | "value_conflict" | "pattern_match"
          detail: string
  activated_concepts:
    - concept_id: string
      activation_strength: float          # 0-1, how strongly this retrieval activated the concept
  meta:
    sessions_scanned: integer             # total INDEX lines considered
    llm_tokens_used: integer              # estimated
    execution_time_ms: integer
    waves_completed: [1, 2, 3]            # partial if hard-timeout hit
    degraded: boolean                     # true if any wave skipped
    degradation_reason: string | null
```

**Signal type semantics**:

- `decision_analogy` — the past session faced a structurally similar decision ("you considered X vs Y before")
- `value_conflict` — the past session surfaced a SOUL-level tension relevant here
- `pattern_match` — the past session exhibited a behavioral pattern the user should notice again

---

## 7. Output Injection

Hippocampus output does **not** go directly to ROUTER. It flows to the **GWT arbitrator**, which consolidates it with concept lookup output and SOUL check output into a single "annotated input."

The final annotated input reaches ROUTER as part of the user message, clearly demarcated:

```markdown
[COGNITIVE CONTEXT — reference only, not user input]

Related past decisions (hippocampus):
- 2026-04-19 | passpay | 技术白皮书 v0.6 (score 8.2) — similar refinement pattern
- 2026-03-28 | passpay | 合规架构评估 (score 6.5) — GOVERNANCE scored low, may repeat
- 2026-04-15 | passpay | 商业白皮书 v1.0 (score 7.8) — same project cluster, recent

[END COGNITIVE CONTEXT]

User's actual message: {original_message}
```

**Placement rationale** (important — do not change without consultation):

- Cognitive context goes in the **user message**, not the system prompt. System prompts are cached; volatile per-session retrieval would bust the prompt cache every turn.
- ROUTER may choose to ignore the cognitive context (e.g., if the user explicitly says "ignore history, reconsider from scratch"). The annotation is **advisory, not authoritative**.
- The `[COGNITIVE CONTEXT]` delimiters are literal — ROUTER parses them to separate advisory content from the real user input.

---

## 8. Performance Budget

| Step | Target | Notes |
|------|--------|-------|
| Read `INDEX.md` | <100ms | File size <1MB at 2000 sessions |
| Grep pre-filter | <50ms | Ripgrep on INDEX.md |
| LLM judgment on filtered index | 2-3s | ~5000 tokens on Opus |
| Read 3-5 session files | <300ms | Parallel reads |
| Wave 2 concept lookup | 1-2s | Opus judges edge relevance |
| Wave 3 extension | 1s | Narrower scope |
| **Total target** | **<7 seconds** | Well under 15s hard timeout |

**Note on timeout semantics**: the <7s total is the **normal-case target** — the budget the pipeline is designed to meet on a typical invocation. The 5s soft / 15s hard bounds from §2 describe **tail behavior**: the soft bound is when GWT stops waiting (not when hippocampus stops running), and the hard bound is the absolute ceiling at which hippocampus terminates regardless. Any run longer than 5s still completes and logs to the session trace, but its output does not re-enter the current ROUTER cycle.

**Scalability note**: at 2000+ sessions, INDEX.md grows toward 2MB. Consider paginating by month (`INDEX-2026-04.md`) and reading only the last 6 months by default in that regime. Phase 1 does not implement pagination.

**Token budget**:

- LLM judgment calls: ~5000 tokens input + ~500 output
- Wave 2 edge relevance: ~1500 tokens input + ~200 output
- Total per invocation: under 8000 tokens

Cost per invocation (at Opus pricing): roughly $0.05-0.10 depending on session-context size. This matches the generic-version cost target from brainstorm §10.

---

## 9. Failure Modes

Hippocampus must degrade gracefully — a failed retrieval should never block the decision workflow.

| Failure | Behavior |
|---------|----------|
| `_meta/sessions/INDEX.md` does not exist | Orchestrator runs `tools/migrate.py` to auto-bootstrap before Step 0.5. If hippocampus still sees a missing index, return empty output with `degraded: true, degradation_reason: "INDEX_MISSING"` and let GWT surface it through `degradation_summary`. |
| INDEX.md exists but is empty (new second-brain) | Return empty `retrieved_sessions`, note "first session — no cross-session memory yet" |
| LLM judgment call fails (API error, rate limit) | Fallback to pure keyword match on INDEX.md (no semantic scoring), set `degraded: true` |
| Concept files missing for Wave 2 target | Skip that specific branch, continue Wave 2 with remaining branches |
| Entire concept graph missing | Skip Waves 2-3, return Wave 1 results with `waves_completed: [1]` |
| Hard timeout (>15s) | Return partial results (whatever waves completed), log incident to `_meta/eval-history/hippocampus-{date}.md` |
| Read errors on session files | Skip that session, note in `degradation_reason` |

**All failures log to `_meta/eval-history/`**, which AUDITOR reads during session-end patrol. Repeated failures of the same kind trigger a "module quality degradation" flag — same mechanism as the Escalate rate limit from brainstorm §6.

---

## 10. Caching (Out of Scope for v1.7)

Every invocation re-scans INDEX.md and re-reads concept files. At 2000 sessions this is still under 2MB of I/O and under 7s of total latency, so **no caching in v1.7**.

Caching is out of scope for v1.7. If INDEX.md exceeds 5MB or hippocampus p95 latency exceeds 10s during v1.7 operation, the scale-trigger in `session-index-spec.md` §8 fires (shard INDEX by month first, then consider caching as a separate spec revision).

---

## 11. Quality Metrics

Hippocampus is evaluated along three dimensions. Each is computed by AUDITOR at session-end and appended to `_meta/eval-history/cognitive-annotation-{date}.md`.

### 11.1 `retrieved_session_count`

Did it find anything? A healthy baseline, once the second-brain has >30 sessions, is 3-5 retrievals per invocation. Persistent zero-retrieval despite sufficient history = bug signal.

### 11.2 `relevance_score_distribution`

Are the top-ranked results actually relevant? Self-evaluated by AUDITOR using the heuristic: "did ROUTER cite this session in its reasoning?"

Healthy: median top-1 relevance score ≥ 0.7. If median drops below 0.5 for 2 weeks, Wave 1 LLM prompt needs retuning.

### 11.3 `user_signals_used`

Did ROUTER / downstream agents **actually reference** the retrieved content? AUDITOR scans Summary Report and domain outputs for mentions of retrieved session IDs. If <20% of retrieved sessions are referenced, hippocampus is paying cost without providing value — AUDITOR surfaces the pattern in eval-history for review.

### Composite score

These feed into AUDITOR's `cognitive_annotation_quality` metric (0-1), written to every eval-history entry. Persistent low scores on this metric surface in AUDITOR's patrol inspections and trigger module-level review through the normal spec revision process.

---

## 12. Anti-patterns

Explicit don'ts — violations are process errors, AUDITOR flags them.

- **Do not retrieve all sessions.** Exhaustive search defeats the purpose (and blows the token budget). Wave caps exist for a reason.
- **Do not use embeddings or vector databases.** User decision #3: markdown-first, LLM-judgment-only. Adding a vector store changes the architecture — requires separate approval.
- **Do not modify session files or concept files.** Hippocampus is read-only. All writes happen in ARCHIVER Phase 2 (see `pro/agents/archiver.md`).
- **Do not inject retrieved content into the SYSTEM PROMPT.** Too volatile, breaks the prompt cache, bloats the system prompt over long sessions. Retrieved content always goes into the user message, delimited by `[COGNITIVE CONTEXT]`.
- **Do not skip isolation.** Do not read other Pre-Router Cognitive Layer outputs. If you see them in the input, treat as a contract violation and return an error.
- **Do not synthesize claims that aren't in retrieved content.** Hippocampus is a retrieval agent, not a reasoner. The `reason` field in each retrieved session must paraphrase what's in that session's markdown, not infer beyond it.
- **Do not exceed 7 total retrieved sessions.** GWT arbitration quality degrades beyond that.
- **Do not retry LLM calls silently.** One retry is acceptable on transient errors; any further degradation must set `degraded: true` and log.
- **Do not block the workflow on hippocampus failure.** Soft-timeout hitting = partial result; hard-timeout hitting = empty result. Never stall.
- **Do not leak raw session content.** The `summary` field is 1-2 sentences max; never paste whole session transcripts. Privacy boundary.

---

## 13. Related Specs

- **`references/cortex-spec.md`** — overall Cortex architecture, how hippocampus fits
- **`references/concept-spec.md`** — concept markdown schema, edge weights, permanence tiers
- **`references/session-index-spec.md`** — `_meta/sessions/INDEX.md` format, one-liner conventions
- **`references/gwt-spec.md`** — GWT arbitrator that consumes hippocampus output
- **`devdocs/architecture/cortex-integration.md`** — how Step 0.5 plugs into the 11-step workflow
- **`devdocs/brainstorm/2026-04-19-cortex-architecture.md`** — original design discussion, user decisions, tradeoffs

---

## 14. Version History

| Version | Date | Change |
|---------|------|--------|
| v1.7 | 2026-04-20 | Initial spec for Cortex Phase 1. Wave 1-3 retrieval, read-only contract, 7s budget. |

---

**Document status**: Active spec for v1.7 Cortex Phase 1. Changes require explicit version bump and update to `pro/agents/hippocampus.md`, `references/cortex-spec.md`, and three-language CHANGELOG entries per project HARD RULE.
