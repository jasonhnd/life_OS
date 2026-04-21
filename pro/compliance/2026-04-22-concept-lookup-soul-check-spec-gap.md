---
incident_id: CORTEX-SPEC-002
date: 2026-04-22
severity: P2 · spec-code mismatch
status: resolved-2026-04-22
affects: pro/agents/concept-lookup.md + pro/agents/soul-check.md
---

# Concept-lookup + Soul-check standalone agent files · spec-code gap

## Conflict

- `docs/architecture/v1.7-spec-map.md §6 · Create 3 new agent files` 明确只许 create 3 文件:
  1. pro/agents/hippocampus.md
  2. pro/agents/gwt-arbitrator.md
  3. pro/agents/narrator-validator.md
- **事实**: `pro/agents/concept-lookup.md` 和 `pro/agents/soul-check.md` 均已存在且被 `pro/CLAUDE.md` Step 0.5 wired in 作为独立 subagent
- `references/concept-spec.md` 表示 concept 提取是 archiver Phase 2 逻辑；但 concept-lookup 作为 Step 0.5 的 READ-ONLY 检索 agent 和 archiver Phase 2 的 WRITE 职责是正交的
- `references/soul-spec.md` + Cortex brainstorm 提到 soul-check "TBD — reuses RETROSPECTIVE's SOUL Health Report"；但实际实现 standalone

## Resolution: expand whitelist to 5 (chosen)

Per `v1.7-spec-map.md §4` precedence rules: user decision + implementation reality take precedence over spec wording when the spec was written before implementation solidified. Both agent files provide information-isolated Cortex pre-router signals, which matches the cortex architecture intent.

Action:
- Update `docs/architecture/v1.7-spec-map.md §6` "Create 3 new agent files" → "Create 5 new agent files" and add concept-lookup + soul-check to the list
- Update §9.1 checklist (3 new agents → 5 new agents)
- Add rationale paragraph: "concept-lookup and soul-check are read-only Pre-Router signal producers, information-isolated from each other and from hippocampus; their standalone form matches the GWT arbitrator's consolidation contract (§Step 0.5)"

## Related

- `pro/compliance/2026-04-21-narrator-spec-violation.md` — narrator handled separately via Option C (ROUTER-internal template, not a subagent)
- `pro/CLAUDE.md §0.5` / `pro/GEMINI.md §0.5` / `pro/AGENTS.md §0.5` — Step 0.5 wiring (unchanged)

## Not in scope

- Rewriting `references/concept-spec.md` or `references/soul-spec.md` — they describe the underlying mechanisms, not the Pre-Router agent wrapping layer. No spec bug there.
