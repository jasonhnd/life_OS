---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# Cortex Architecture · End-to-End Data Flow (v1.7)

> Quick-reference architecture diagram + sequence for the v1.7 Pre-Router Cognitive Layer. Companion to `references/cortex-spec.md` (theory + decisions) and the per-component specs (hippocampus, gwt, concept, snapshot, narrator, etc).

---

## 1. The Three Lifecycle Phases

Cortex data has three lifecycle phases corresponding to where in a session it gets touched:

| Phase | Who | When | Files touched |
|-------|-----|------|---------------|
| **Write** | archiver | Adjourn (Phase 2) | `_meta/sessions/{id}.md`, `_meta/concepts/{domain}/{id}.md`, `_meta/snapshots/soul/{ts}.md` |
| **Compile** | retrospective | Start Session (Mode 0) | `_meta/sessions/INDEX.md`, `_meta/concepts/{INDEX,SYNAPSES-INDEX}.md` |
| **Read** | hippocampus / concept-lookup / soul-check / GWT | Every user message (Step 0.5) | All compiled INDEX files + selected per-session/per-concept files |

**Strict separation**: writers never compile; compilers never write per-record files; readers never modify anything. Mutations happen only in archiver Phase 2.

---

## 2. End-to-End Sequence (Cortex always-on in v1.7.2)

```
              ┌──────────────────────────────────────────────────┐
              │  ADJOURN PATH (one-time per session)            │
              └──────────────────────────────────────────────────┘

User: "退朝"
     ↓
ROUTER: 📝 Trigger: 退朝 → Action: Launch(archiver) (4 phases)
     ↓
archiver Phase 1 (Archive):
  · session_id from real `date` command
  · stages decisions/tasks/journal → outbox

archiver Phase 2 (Knowledge Extraction):
  ┌─ wiki auto-write (if 6 criteria + privacy filter pass)
  ├─ SOUL auto-write / increment (ADVISOR's evidence deltas)
  ├─ concept extraction (5 sub-steps A-E):
  │   A. extract candidates from session materials
  │   B. match against existing concepts (exact / partial / new)
  │   C. Hebbian update (+1 weight per co-activated pair)
  │   D. promotion check (tentative→confirmed→canonical thresholds)
  │   E. regenerate SYNAPSES-INDEX.md
  ├─ SOUL snapshot dump (immutable, only confidence > 0.2 dimensions)
  └─ SessionSummary write (FINAL — references all above outputs)

archiver Phase 3 (DREAM):
  · N1-N2 organize · N3 consolidate · REM (10 trigger evaluations)

archiver Phase 4 (Sync):
  · git push outbox → main repo
  · (Notion sync handed back to orchestrator step 10a)

orchestrator step 10a: Notion sync via MCP

AUDITOR Mode 3 (auto, per Orchestration rule #7):
  · Audits 4 Adjourn checks (C/D/E/A3) + 7 Cortex checks (CX1-CX7)
  · Logs violations to pro/compliance/violations.md or _meta/compliance/violations.md
```

```
              ┌──────────────────────────────────────────────────┐
              │  COMPILE PATH (next Start Session)              │
              └──────────────────────────────────────────────────┘

User: "上朝"
     ↓
ROUTER: 🌅 Trigger: 上朝 → Action: Launch(retrospective) Mode 0
     ↓
retrospective Mode 0 (18 steps):
  · Step 7 outbox merge (decisions/tasks/journal/sessions move to canonical)
  · NEW: Compile session INDEX.md from _meta/sessions/*.md
  · NEW: Compile concept INDEX.md + SYNAPSES-INDEX.md from _meta/concepts/{domain}/*.md
  · ... rest of 18 steps (SOUL Health Report, Strategic Map, briefing, ...)

AUDITOR Mode 3 (auto): audits Mode 0 for 6 Start Session compliance checks
```

```
              ┌──────────────────────────────────────────────────┐
              │  READ PATH (every user message after Mode 0)    │
              └──────────────────────────────────────────────────┘

User: "..."
     ↓
orchestrator attempts Step 0.5 for every user message:
  · missing/empty INDEX → auto-bootstrap, then continue if successful
  · bootstrap/subagent failure → degrade through empty or partial context
     ↓
Step 0.5 (Pre-Router Cognitive Layer) — 3 PARALLEL subagents:

  ┌─ hippocampus (5-7s budget):
  │   Wave 1: ripgrep INDEX → LLM judgment → top 5 sessions
  │   Wave 2: follow concept edges weight ≥ 3 → +2-3 sessions
  │   Wave 3: follow weight ≥ 1 → +1-2 sessions (cap 5-7 total)
  │   → hippocampus_output: yaml
  │
  ├─ concept-lookup (3s budget):
  │   INDEX scan → LLM judgment → 5-10 concepts → score → read top files
  │   → concept_lookup_output: yaml
  │
  └─ soul-check (3s budget):
      Read SOUL.md → Read latest snapshot → LLM judge dimensions
      → 5 signals classified by tier_1/2/dormant
      → soul_check_output: yaml

  All 3 enforce information isolation: each rejects peer outputs in its input.

     ↓
GWT arbitrator (single invocation, 5s budget):
  · Salience formula: urgency*0.3 + novelty*0.2 + relevance*0.3 + importance*0.2
  · LLM judgment for relevance; rule-based for other 3 components
  · Cap 5 signals; floor 0.3 per signal
  · tier_1_conflict → elevate to ⚠️ SOUL CONFLICT header
     ↓
[COGNITIVE CONTEXT — reference only, not user input]
{annotations}
[END COGNITIVE CONTEXT]

{original user message}
     ↓
ROUTER triage (with annotated input)
     ↓
Steps 2-10 unchanged (PLANNER → REVIEWER → DISPATCHER → 6 domains → REVIEWER → Summary Report → AUDITOR → ADVISOR → ARCHIVER)

     ↓ (between REVIEWER step 6 and Summary Report step 7, when narrator enabled)

narrator (5s budget):
  · Wraps Summary Report substantive claims with [source:signal_id] citations
  · Validator (Sonnet-tier) audits citations
  · Up to 2 rewrite cycles; on failure, fall back to v1.6.3 unwrapped report
```

---

## 3. Information Isolation Matrix (per pro/CLAUDE.md)

| Subagent | Receives | Does NOT receive |
|----------|----------|------------------|
| hippocampus | current_message + project + theme + session_context | concept-lookup output, soul-check output, SOUL.md body, prior transcripts (only summaries) |
| concept-lookup | current_message + project + theme | hippocampus output, soul-check output, raw concept body content |
| soul-check | current_message + project + theme | hippocampus output, concept-lookup output, snapshots > latest |
| gwt-arbitrator | All 3 above outputs + current_message | ROUTER reasoning, raw session/concept content |
| narrator | Draft Summary Report + cognitive_context | Other agents' thought processes |
| narrator-validator | narrator_output + cognitive_context | Anything outside input |

Violations logged as Class CX6 (P0).

---

## 4. Failure Mode Cascade

Cortex is **additive — failure never blocks the workflow**. Each layer's failure is absorbed by the next layer down:

```
Step 0.5 module fails (e.g., hippocampus times out)
  ↓ degrade: GWT proceeds with remaining 2 outputs
GWT timeout
  ↓ degrade: orchestrator emits empty [COGNITIVE CONTEXT] block
[COGNITIVE CONTEXT] block missing entirely
  ↓ degrade: ROUTER sees raw user message (= v1.6.3 behaviour)
narrator fails
  ↓ degrade: Summary Report shown unwrapped (= v1.6.3 behaviour)
narrator-validator finds invalid citations
  ↓ degrade: 2 rewrite chances, then unwrapped report
Cortex completely broken
  ↓ degrade: raw ROUTER input for that turn (= v1.6.3 behaviour)
```

The user always gets a Summary Report. Cortex enhances quality when it works; v1.6.3 baseline is the always-safe floor.

---

## 5. Cost Profile (per substantive decision)

| Layer | Cost (USD, Opus) |
|-------|------------------|
| hippocampus | $0.05-0.10 |
| concept-lookup | $0.02-0.05 |
| soul-check | $0.02-0.05 |
| gwt-arbitrator | $0.02-0.03 |
| narrator + validator (Sonnet) | $0.02-0.04 (validator is cheap) |
| **Total per Cortex turn** | **~$0.13-0.27** |

Without Cortex (v1.6.3 baseline): ROUTER + planner + reviewer + 6 domains + auditor + advisor ≈ $0.50-1.50/decision. Cortex adds 15-25% overhead for cross-session context. In v1.7.2 this is paid through the always-on Step 0.5 path; hosts control cost through Express/direct-handle reductions, timeouts, and graceful degradation rather than a config off-switch.

---

## 6. Compliance Audit (AUDITOR Mode 3 + check_cortex())

| Code | Detected by | When |
|------|-------------|------|
| CX1 | bash hook + AUDITOR Mode 3 | Pre-Router subagent missing in transcript |
| CX2 | bash hook + AUDITOR Mode 3 | GWT arbitrator missing |
| CX3 | bash hook + AUDITOR Mode 3 | [COGNITIVE CONTEXT] delimiters missing in ROUTER input |
| CX4 | bash hook + AUDITOR Mode 3 | hippocampus retrieved > 7 sessions |
| CX5 | bash hook + AUDITOR Mode 3 | GWT composed > 5 signals |
| CX6 | AUDITOR Mode 3 | Information isolation breach (peer output seen) |
| CX7 | AUDITOR Mode 3 | Cortex subagent invoked Write tool |

CX6 + CX7 are P0 (HARD RULE breaches). CX1-CX5 are P1 (process violations, system degrades to v1.6.3 behaviour but should be fixed).

Deprecated `cortex_enabled` values in `_meta/config.md` do not disable CX checks in v1.7.2.

---

## 7. Data Type Reference

Quick map from on-disk path to dataclass + spec:

| File path | Dataclass | Spec |
|-----------|-----------|------|
| `_meta/sessions/{id}.md` | `SessionSummary` | session-index-spec.md §3 |
| `_meta/sessions/INDEX.md` | (compiled artifact) | session-index-spec.md §4 |
| `_meta/concepts/{domain}/{id}.md` | `Concept` | concept-spec.md |
| `_meta/concepts/INDEX.md` | (compiled artifact) | concept-spec.md (INDEX section) |
| `_meta/concepts/SYNAPSES-INDEX.md` | (compiled artifact) | concept-spec.md (SYNAPSES section) |
| `_meta/snapshots/soul/{ts}.md` | `SoulSnapshot` | snapshot-spec.md |
| `_meta/eval-history/{date}-{project}.md` | `EvalEntry` | eval-history-spec.md |
| `_meta/methods/{domain}/{id}.md` | `Method` | method-library-spec.md |

Python dataclasses live in `tools/lib/second_brain.py`. IO helpers in `tools/lib/cortex/{session_index,concept,snapshot}.py`.

---

## 8. CLI Quick Reference

```bash
# Compile artifacts (when retrospective hasn't run / manual recompile)
uv run life-os-tool rebuild-session-index --root ~/second-brain
uv run life-os-tool rebuild-concept-index --root ~/second-brain [--no-synapses]

# Maintenance (run weekly or monthly)
uv run life-os-tool backup --dry-run        # preview
uv run life-os-tool backup                  # rotate snapshots + archive violations

# Compliance analytics
uv run life-os-tool stats                   # human-readable
uv run life-os-tool stats --json            # for hook/AUDITOR consumption
```

All CLI tools are optional — Cortex inference works fine without them; they're for maintenance + analytics.

---

## 9. Related Specs

- `references/cortex-spec.md` — overall architecture (4865 lines of spec)
- `references/hippocampus-spec.md` — cross-session retrieval contract
- `references/concept-spec.md` — concept graph nodes + edges
- `references/gwt-spec.md` — salience formula + arbitration
- `references/narrator-spec.md` — citation discipline
- `references/snapshot-spec.md` — SOUL snapshot lifecycle
- `references/session-index-spec.md` — INDEX.md format + write flow
- `references/tools-spec.md` — Python toolkit contract
- `references/compliance-spec.md` — violation taxonomy (now includes CX1-CX7)
- `pro/CLAUDE.md` Step 0.5 — orchestrator wiring
- `pro/agents/{hippocampus,concept-lookup,soul-check,gwt-arbitrator,narrator,narrator-validator}.md` — subagent contracts
