---
spec_id: model-dispatch-policy.v1
description: Task↔model-tier dispatch policy. Declares three capability tiers (judgment / execution / batch), maps every agent and maintenance job to its minimum tier, defines the weak-model dispatch order format, and centralizes tier→model binding in a single mapping table. Closes the "frontier model is always available" assumption (issue #1 A1).
status: active
authoritative: true
introduced_in: v1.10.0
referenced_by:
  - hosts/CLAUDE.md (model statement + fallback)
  - hosts/GEMINI.md (model mapping table)
  - hosts/AGENTS.md (model mapping table)
  - agents/dispatcher.md (§Weak-Model Dispatch Mode)
  - references/agent-spec.md (frontmatter `model:` field)
  - .claude/commands/run-eval.md (--tier flag, per issue #4 D2)
---

# Model Dispatch Policy v1

Life OS was written at frontier-model reading level, and 23 of 24 agent definitions bound `model: opus` with no degradation path — when a frontier model was unavailable (quota window, plan change, provider incident, cheaper setup), the system degraded from "fully works" straight to "not usable". This spec introduces the missing middle: a declared **capability floor** per task, separate from `authority_level` (which governs write permission, not required intelligence).

## The three tiers

| Tier | What it covers | Failure cost of a weaker model | Frontier required? |
|------|----------------|--------------------------------|--------------------|
| **judgment** | Router triage, planning, review/veto, domain scoring, council debate, behavioral/value analysis | Plausible-but-wrong conclusions that steer real decisions — worse than no output | **Yes — frontier-locked** |
| **execution** | Archiver mechanics, session boot, index maintenance, format normalization, retrieval scans, translation first drafts | Recoverable mechanical errors, caught by checks/patrols | No — mid tier acceptable |
| **batch** | Grep sweeps, link audits, file moves, count reconciliation, ledger stamping | Trivially detectable; job is re-runnable | No — weakest tier acceptable |

## HARD RULE · No silent fall-through

**Judgment-tier work MUST NOT silently run on a below-frontier model.** When the required tier is unavailable, the correct behavior is to say `⚠️ this requires a frontier session — deferring <task>` and stop. A plausible-but-wrong veto, domain score, or triage decision is strictly worse than a deferred one. Silent degradation is an F12 DRIFT_FAILURE; AUDITOR flags it.

Execution- and batch-tier work MAY run on any tier at or above its floor. Running batch work on a frontier model is allowed (just wasteful); running judgment work on a batch model is forbidden.

## Tier → model mapping (the ONLY place model bindings live)

| Tier | Claude Code binding (`model:` frontmatter alias) | Gemini CLI / Antigravity | Codex CLI |
|------|--------------------------------------------------|--------------------------|-----------|
| judgment | `opus` | strongest available (auto-select) | strongest available (auto-select) |
| execution | `sonnet` | mid tier | mid tier |
| batch | `haiku` | cheapest/fastest tier | cheapest/fastest tier |

Rules:

- `opus` / `sonnet` / `haiku` are **host aliases** (tier indirection), not versioned model names. Hosts resolve them to whatever the current generation is.
- **Versioned model IDs (e.g. `claude-*-4-*`, dated snapshots) MUST NOT appear anywhere in this repo** — not in agent frontmatter, not in docs examples, not in specs. Model names churn every few months; this table is the single point of change. `/check-spec-drift` treats a versioned model ID outside this file as drift.
- Agent frontmatter `model:` values are the compiled Claude Code binding of the table below. Changing a binding means changing the agent's row here FIRST, then the frontmatter.

## Agent → minimum tier table (complete, 24 agents)

`min_tier` is the capability **floor** — the weakest tier at which the agent's output is still safe. The Claude Code `model:` frontmatter binds the *default*; it may sit above the floor (never below).

| Agent | min_tier | Default binding | Notes |
|-------|----------|-----------------|-------|
| router | judgment | opus | Triage errors misroute everything downstream |
| planner | judgment | opus | |
| reviewer | judgment | opus | Veto power; emotional audit |
| dispatcher | judgment | opus | Dependency detection + B5 gate; authors weak-model orders |
| council | judgment | opus | Structured debate |
| auditor | judgment | opus | Violation judgment across 8 modes |
| advisor | judgment | opus | Behavioral pattern analysis |
| strategist | judgment | opus | Thinker voices |
| people / finance / growth / execution / governance / infra | judgment | opus | Independent domain scoring (6 agents) |
| gwt-arbitrator | judgment | opus | Salience arbitration |
| soul-check | judgment | opus | Value-alignment classification |
| knowledge-extractor | judgment | opus | Auto-writes SOUL/wiki — gate quality is identity-critical |
| narrator | judgment | (router-internal) | ROUTER-internal template; follows router's tier |
| retrospective | execution | opus | Mode 0 is mostly mechanical reads + assembly; Steps 15-18 narrative degrades gracefully (advisory, not decisions) |
| archiver | execution | opus | Outbox moves, git sync, report assembly; DREAM findings are candidates, not decisions |
| hippocampus | execution | opus | Mechanical spreading-activation scan over INDEX |
| concept-lookup | execution | opus | INDEX direct match |
| monitor | execution | opus | View-and-invoke ops console |
| memory-keeper | execution | sonnet | Already bound to mid tier (the one pre-v1.10 exception) |

## Maintenance job → minimum tier table (complete, scripts/prompts/ + scripts/commands/)

| Job (`scripts/prompts/`) | min_tier | Cadence (for `meta/maintenance-ledger.md`) |
|--------------------------|----------|--------------------------------------------|
| advisor-monthly | judgment | 30d |
| research | judgment | on-demand |
| strategic-consistency | judgment | 30d |
| archiver-recovery | execution | on-demand |
| auditor-mode-2 | execution | 7d |
| bulk-ingest (v1.10.0) | execution | on-demand |
| daily-briefing | execution | on-demand |
| doctor | execution | on-demand |
| extract-concepts | execution | on-demand |
| inbox-process | execution | 7d |
| migrate-from-v1.6 / migrate-v1.9 | execution | once |
| review-queue | execution | 7d |
| spec-compliance | execution | 30d |
| wiki-decay | execution | 30d |
| backup | batch | 7d |
| eval-history-monthly | batch | 30d |
| migrate-confidence / migrate-to-wikilinks / wiki-obsidian-upgrade | batch | once |
| rebuild-concept-index | batch | 30d |
| rebuild-session-index | batch | on-demand |
| reindex | batch | 7d |
| snapshot-cleanup | batch | 30d |
| verify-v1.9 | batch | once |

| Command (`scripts/commands/`) | min_tier |
|-------------------------------|----------|
| research | judgment |
| compress / inbox-process / method / monitor | execution |
| memory / search | batch |

## Weak-model dispatch order format (below-frontier orders)

When work is dispatched to a below-frontier tier (execution or batch), the dispatch order MUST be narrowed to **lookup-table form**:

1. **Explicit file list** — every file to read or write is enumerated by path. No "scan the relevant files".
2. **Mechanical numbered steps** — each step is a concrete tool action (Read X, Grep pattern P in Y, Write Z) with its expected shape stated.
3. **Zero open judgment** — the phrases "use your judgment", "as appropriate", "if it seems", "decide whether" MUST NOT appear. Any decision point is either pre-decided in the order or listed as "STOP and report" .
4. **Hard mechanical acceptance checks** — completion is defined by grep-verifiable / countable conditions (e.g. "0 lines match pattern P", "row count == manifest count"), never by "looks complete".
5. **Escalation clause** — one line stating what the weak model must do when a step's precondition fails: stop and report, never improvise.

See `agents/dispatcher.md` §"Weak-Model Dispatch Mode" for the dispatcher-side contract.

## Fallback behavior when the required tier is unavailable

| Situation | Behavior |
|-----------|----------|
| Frontier unavailable, judgment-tier task requested | Say `⚠️ this requires a frontier session` and stop (HARD RULE above). Offer the user the list of execution/batch work that CAN proceed. |
| Frontier unavailable, execution/batch task requested | Proceed on the available tier at or above the task's floor. |
| Mid tier also unavailable (batch model only) | Only batch-tier rows from the tables above may run. Everything else defers. |
| Uncertain which tier the current model is | Treat it as batch (most conservative floor). |

## Degradation-safety evidence (issue #4 D2 link)

Tier claims in the tables above are validated empirically, not by intuition: eval scenarios carry a `min_model_tier:` frontmatter field, `/run-eval --tier <tier>` runs them at the tier's mapped model, and `docs/evals/tier-matrix.md` is regenerated from real runs. A scenario failing at its declared tier is a spec bug — either this table is too optimistic or the prompt needs simplification.
