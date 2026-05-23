---
spec_id: refactoring-patterns.v1
description: Canonical refactor patterns library for life_OS agent/spec/skill evolution. 8 primary patterns + 2 supplementary + minimality rule. Used by planner, architect-class subagents, and ROUTER when considering structural changes.
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/refactoring-patterns.yml
introduced_in: v1.8.5
---

# Refactoring Patterns

> 8 canonical refactor patterns + 2 supplementary + 1 minimality rule. Each pattern has `use_when` (the diagnosed condition) and `output` (what the refactor produces). When planning structural changes to subagents, specs, or skills, planner and architect-class agents MUST consult this catalog before inventing a custom approach.

## Primary patterns

### 1. SPLIT
- **Use when**: One agent/EOU/spec has multiple primary success criteria, OR two distinct responsibilities bundled into one unit.
- **Output**: Two or more narrower units, each with a single success criterion.
- **Example in life_OS**: v1.7.3 carve-out split archiver Phase 2 into separate `knowledge-extractor` subagent (knowledge extraction) + remaining archiver (4 phases). Reduced overload that caused v1.7.2 placeholder violations.

### 2. MERGE
- **Use when**: Two units always run together, share the same success criterion, have no useful independent existence.
- **Output**: One combined unit with unified success criterion.
- **Example**: If `narrator` + `narrator-validator` were always invoked together and shared "produce cited summary" criterion, merging them (which v1.8.0 did by deleting narrator-validator and inlining the check) reduced coordination overhead.

### 3. SCOPE-REDUCTION
- **Use when**: Unit's `authority_level`, `blast_radius`, or `target_object` is broader than its actual function requires; OR reads/writes files outside stated purpose.
- **Output**: Tightened authority_level, narrowed allowed_scope, or reduced target_object.
- **Example**: ROUTER originally could mutate SOUL.md directly. Scope reduction made ROUTER `suggest_only + write_inactive` for SOUL — only ARCHIVER Phase 2 can write SOUL candidates.

### 4. AUTHORITY-DOWNGRADE
- **Use when**: `automation_mode` is `LLM_assisted` or `deterministic` for a step that carries responsibility-heavy judgment that should remain `human_executed`; OR authority_level exceeds what function requires.
- **Output**: Lower automation_mode or authority_level; add explicit `require_human_when` condition.
- **Example**: REVIEWER veto in high-risk domains (finance/health/legal per `references/risk-domains.md`) is `LLM_assisted` but requires explicit human confirmation, not auto-execute.

### 5. STEP-EXTRACTION
- **Use when**: A step inside an agent/EOU can be made deterministic (promote to slash command) OR isolated as a sub-agent with its own blast radius and governance.
- **Output**: A new slash command (`.claude/commands/*.md`), or a child subagent (`pro/agents/*.md`) handling the extracted step; parent references the extracted unit.
- **Example**: archiver Phase 4 Notion sync extracted to `/notion-sync` slash command (v1.8.5). Phase 4 now invokes slash, doesn't reimplement audit-trail writing.

### 6. VALIDATOR-ADDITION
- **Use when**: A known failure mode has no validation gate; output quality depends on unverified assumptions; past incident has no regression case preventing recurrence.
- **Output**: A new deterministic check (slash command), schema constraint (in `references/*-spec.md` v2 frontmatter), OR regression case (`evals/regression-fixtures/rc-*.yml`).
- **Example**: After v1.8.0 R-1.8.0-019 (GitHub Release Latest mismatch incident), added `/verify-release` 6-check sequence + HARD RULE in pro/CLAUDE.md.

### 7. STOP-CONDITION-INJECTION
- **Use when**: An agent/EOU continues executing in invalid, ambiguous, or unauthorized states rather than halting and reporting.
- **Output**: One or more new stop conditions in `execution.stop_conditions` with observable trigger criteria.
- **Example**: archiver was running Phase 4 Notion sync even when `_meta/config.md` had 0 Notion entities configured. Added stop condition: if 0 entities → skip Phase 4 silently, log skip reason in audit trail (per pro/CLAUDE.md Step 10a R-1.8.0-022 fix).

### 8. RESPONSIBILITY-SEPARATION
- **Use when**: Same party executes and approves OR two distinct approval authorities handled by one unit.
- **Output**: Separate executor and approver roles; distinct subagent or human gate for each approval authority.
- **Example**: AUDITOR (Mode 3) audits other agents but cannot audit itself. ADVISOR reviews REVIEWER decisions but never re-decides them. Each role has a hard boundary on what it can self-approve.

## Supplementary patterns

### 9. ADD_CONTEXT_MANIFEST
- **Use when**: Agent performance depends on context (project state, SOUL, schema versions) loaded implicitly or inconsistently across runs.
- **Output**: Populated `context_manifest.source_of_truth + supporting + forbidden` lists explicitly in the agent's v2 frontmatter (per Stage 6).
- **Example**: hippocampus subagent originally loaded "whatever it needed" from `_meta/sessions/`. v2 frontmatter forced explicit list: source_of_truth=[INDEX.md], supporting=[recent 7 snapshots], forbidden=[full transcripts].

### 10. RETIRE_UNIT
- **Use when**: A unit is obsolete (superseded by a better one), duplicate (covered by existing), or net-negative (costs exceed operational value).
- **Output**: Lifecycle transitioned to `deprecated` → `retired`; spec frontmatter marked `status: legacy`; migration path documented for any consumers.
- **Example**: v1.8.0 retired `narrator-validator.md` subagent (citation discipline now inlined in ROUTER). v1.8.5 retired entire hook layer (11 hooks → 0).

## Minimality rule (HARD RULE for new agent/spec/skill creation)

Before creating a new agent, spec, skill, or HARD RULE, MUST answer these 6 questions:

1. Could a **rule** (in pro/AGENTS.md or pro/CLAUDE.md) accomplish this?
2. Could a **schema field** (in references/*-spec.md frontmatter) accomplish this?
3. Could a **validator** (slash command or AUDITOR Mode 3 scenario) accomplish this?
4. Could a **regression case** (evals/regression-fixtures/*.yml) accomplish this?
5. Could a **stop condition** (in an existing agent's execution flow) accomplish this?
6. Could a **human checklist** (added to relevant doc) accomplish this?

If ANY answer is yes, prefer that lower-cost option over creating a new unit. Creating a new agent/spec/skill is the most expensive option — only use when 1-6 all answer "no, this needs a new first-class unit."

## When to invoke this catalog

- **planner subagent**: Phase 1 check — before proposing a structural change, must reference at least one pattern by name (or explicitly justify why none apply).
- **architect-class decisions**: Any change touching agent definitions, spec schemas, or HARD RULES.
- **DREAM REM cycle**: When detecting repeated friction (3+ similar incidents), match against patterns 1-10 to propose refactor.
- **ECP/RFC drafting**: Reference relevant pattern in `proposed_change` section.

## Source attribution

eou-foundry @ e4b12ce — `engine/refactoring-patterns.yml` 53 lines (8 patterns + 2 supplementary + minimality_rule). Adapted: examples replaced with life_OS-specific cases; "EOU" terminology mapped to "agent/EOU/spec/skill" since life_OS has multiple first-class unit types.
