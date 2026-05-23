---
spec_id: agent-spec.v2
description: Standard frontmatter schema for all pro/agents/*.md subagent definition files. Borrows EOU 6 facets classification + operating_hypothesis + context_manifest + blast_radius + failure_modes from eou-foundry. Applies to all 23 subagents (router, retrospective, archiver, planner, reviewer, dispatcher, advisor, auditor, strategist, monitor, council, hippocampus, gwt-arbitrator, concept-lookup, soul-check, narrator, narrator-validator, knowledge-extractor + 6 domain agents).
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, schemas/eou.schema.yml + engine/eou-contract.md
introduced_in: v1.8.5
---

# Agent Specification v2

Every `pro/agents/*.md` subagent definition file MUST have YAML frontmatter conforming to the v2 standard. v1.8.5 Stage 6 migrates all 23 existing agents.

> **Why v2**: v1 agent frontmatter only had `name + description + tools + model` (4 fields). v2 adds 6 structural fields borrowed from eou-foundry that make agent boundaries grep-able, blast radius explicit, and failure modes documented. Per RFC `_meta/rfc/v1.8.5-cleanup-and-hardening.md` Stage 6.

## v2 Standard Frontmatter

```yaml
---
# v1 fields (preserved — Claude Code Task() tool reads these)
name: <agent-id>                       # lowercase, hyphen-separated, e.g. retrospective
description: "<one-paragraph role description>"
tools: Read, Grep, Glob, Bash, Write, Edit, Task   # tool allowlist
model: opus|sonnet|haiku|haiku-4-5

# v2 NEW: identity & versioning
id: agent-<name>                       # canonical, e.g. agent-retrospective
version: "1.0.0"                       # semver; bump on substantive role change

# v2 NEW: 6 facets classification (borrowed from eou-foundry eou.schema.yml)
classification:
  function: generate|specify|validate|diagnose|promote|refactor|audit|propose|activate|implement|retire
  target_object: "<what this agent acts on, e.g. 'user decision workflow' or 'session archive'>"
  automation_mode: deterministic|LLM_assisted|human_executed|hybrid
  authority_level: suggest_only|draft_only|write_candidate|write_inactive|mutate_active|approve|publish
  risk_level: low|medium|high|critical
  lifecycle_stage: candidate|draft|simulated|pilot|active|monitored|stable|deprecated|retired

# v2 NEW: operating_hypothesis (Given/can/within)
operating_hypothesis: |
  Given <trigger condition>, this agent should produce <output type> within <risk r>.

# v2 NEW: context_manifest (eou eou-contract.md §context_manifest)
context_manifest:
  source_of_truth:     # files this agent reads as authoritative
    - pro/CLAUDE.md
    - pro/GLOBAL.md
  supporting:          # secondary context
    - references/relevant-spec.md
  forbidden:           # MUST NOT read — information isolation per pro/CLAUDE.md §Information Isolation
    - pro/agents/other-peer.md

# v2 NEW: blast_radius (eou eou-contract.md §blast_radius)
blast_radius:
  allowed_scope:       # files/paths this agent may write
    - _meta/runtime/<sid>/<name>-*.json
    - <wiki/SOUL/specific-output-path>
  forbidden_scope:     # files this agent MUST NOT modify
    - SOUL.md          # only ARCHIVER Phase 2 writes SOUL candidates
    - foundry/eous/    # if applicable
    - pro/agents/      # agent definitions never self-modify

# v2 NEW: failure_modes (eou eou-contract.md §failure_modes)
failure_modes:
  known:              # documented ways this agent fails
    - "Skips required step when user message is brief"
    - "Confabulates path reference when context is ambiguous"
  warning_signs:      # observable signals failure is happening
    - "Output contains 'as discussed before' without specific citation"
    - "Step count in output < expected step count"
  repair_actions:     # what to do when failure occurs
    - "Re-launch agent with explicit step list reminder"
    - "Run AUDITOR Mode 3 to log violation"
---
```

## Required v2 Fields (HARD)

For every `pro/agents/*.md`, the frontmatter MUST have:

1. **All v1 fields**: `name`, `description`, `tools`, `model`
2. **identity**: `id`, `version`
3. **classification**: all 6 facets populated; `target_object` non-empty string
4. **operating_hypothesis**: non-empty, ≥30 chars, Given/can/within form
5. **context_manifest**: 3 keys present; `source_of_truth` non-empty
6. **blast_radius**: `allowed_scope` AND `forbidden_scope` both non-empty
7. **failure_modes**: 3 keys present; lists may be empty initially but should accumulate via DREAM / AUDITOR observations

## Validation (AUDITOR Mode 6 — Stage 6 add)

New AUDITOR mode added at Stage 6 Day 17. Checks:
- **A1**: every agent has all v2 required fields
- **A2**: `tools` list matches what agent actually uses (no `Read` in tools but agent does Read calls = drift)
- **A3**: `forbidden_scope` is not bypassed (agent's output trail in `_meta/runtime/<sid>/` shows no write to forbidden paths)
- **A4**: agent's `failure_modes.known` includes any violation classes from `pro/compliance/violations.md` where the agent is implicated

Findings classified per `references/failure-taxonomy.md`.

## A/B Test Day 15 (per RFC Stage 6 Day 15)

Per D4, before batch-updating 20 agents, test on 3 critical:
- `retrospective.md` (heaviest agent, 18 steps)
- `archiver.md` (4 phases, breaking changes prone)
- `reviewer.md` (veto power, judgment-heavy)

Run eval scenarios:
- `evals/scenarios/start-session-compliance.md` (retrospective Mode 0)
- `evals/scenarios/adjourn-compliance.md` (archiver 4 phases)
- `evals/scenarios/reviewer-veto.md` (reviewer judgment quality)

Pass rate criteria (D4):
- ≥ 95% baseline: proceed with batch update on remaining 20 agents
- 90-95%: simplify frontmatter (drop heaviest field, retry)
- < 90%: rollback that agent's v2 frontmatter, document why in `_meta/rfc/v1.8.5-stage6-rollback.md`

## Per-agent authority_level guidance

| Agent | function | authority_level | risk_level |
|---|---|---|---|
| router | propose | suggest_only + write_inactive | medium |
| retrospective | specify | suggest_only + write_inactive | low |
| archiver | publish | publish (highest — does git push + Notion sync) | medium |
| planner | specify | write_candidate | low |
| reviewer | validate | approve (veto power) | high (judgment) |
| dispatcher | implement | mutate_active (dispatches to domains) | medium |
| advisor | diagnose | suggest_only | low |
| auditor | audit | suggest_only + write_inactive (writes violations.md) | low |
| strategist | propose | suggest_only | low |
| monitor | audit | suggest_only (read-only ops console) | low |
| council | diagnose | suggest_only | low |
| hippocampus | propose | suggest_only (read-only retrieval) | low |
| gwt-arbitrator | propose | suggest_only | low |
| concept-lookup | propose | suggest_only | low |
| soul-check | audit | suggest_only | low |
| narrator | specify | suggest_only (ROUTER-internal, template-only) | low |
| narrator-validator | validate | suggest_only (deleted v1.8.0, retained as legacy template) | low |
| knowledge-extractor | propose | write_candidate (writes to `_meta/runtime/<sid>/extraction/`) | medium |
| 6 domain agents (people/finance/growth/execution/governance/infra) | diagnose | write_candidate (writes domain report) | medium |

risk_level rationale: agents that produce final outputs without REVIEWER gate are higher risk (archiver publish, reviewer veto). Agents that only propose / read are lower risk.

## Per-agent `lifecycle_stage` (v1.8.5 initial)

All 23 agents default to `active` for v1.8.5 release. Exception:
- `narrator.md` and `narrator-validator.md` are `deprecated` per v1.8.0 R-1.8.0-011 pivot (citation discipline inlined to ROUTER); retained as templates only

## Migration

Manual migration per agent. No slash command — agent definitions are stable enough that interactive single-agent edit by user/maintainer is fine.

Template for each agent:
1. Read current agent file
2. Replace frontmatter with v2 standard (preserve v1 fields, add v2 fields)
3. Fill `classification`, `operating_hypothesis`, `context_manifest`, `blast_radius`, `failure_modes` per agent's actual behavior
4. Run AUDITOR Mode 6 to validate

## Source attribution

eou-foundry @ e4b12ce. Borrowed:
- 6 facets classification: `schemas/eou.schema.yml` lines 22-76
- operating_hypothesis: `engine/eou-contract.md` line 34
- context_manifest 3-layer: `engine/eou-contract.md` lines 39-42
- blast_radius: `engine/eou-contract.md` lines 75-77 (allowed_scope/forbidden_scope)
- failure_modes 三件套: `engine/eou-contract.md` lines 60-63

Adapted for life_OS: agent is a Claude Code Task()-spawnable subagent (not an EOU); `tools` field preserved from v1 (Claude Code uses for tool gating); A/B test process from `references/lifecycle-gates.md` pilot→active gate.
