---
spec_id: feature-workflow-spec.v1
description: Feature design workflow for lifeos — Specify → Evals scenarios defined → Implement → Verify (4-stage). The "evals scenarios defined" stage is HARD — planner regardless of complexity MUST list evals scenarios in the planning frontmatter before dispatcher accepts. Borrowed from tinyhumansai/openhuman AGENTS.md §"Feature design workflow" planning rule.
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, AGENTS.md:507-521 (Feature design workflow + Planning rule "E2E scenarios up front")
introduced_in: v1.8.7
referenced_by:
  - pro/agents/planner.md (evals_scenarios required field)
  - pro/agents/dispatcher.md (pre-dispatch validation)
  - pro/agents/reviewer.md (verify scenarios complete before approving)
---

# Feature Workflow Specification v1

lifeos's feature/change design follows a 4-stage workflow. The hard requirement: **scenarios are defined BEFORE implementation starts**, not after. A planning document without scenarios is incomplete; dispatcher rejects it.

## Background

Previously lifeos's planning convention was: planner writes planning doc → reviewer approves → dispatcher dispatches to domains → reviewer final → archiver. The eval-first principle was implicit: planner SHOULD define test scenarios, but it wasn't enforced via frontmatter field.

Result: complex planning docs sometimes shipped without evals; the lifeos eval-first philosophy stayed aspirational. v1.8.7 makes it a contract.

## The 4 stages

```
1. Specify          → write planning doc with Subject + background + scope
2. Evals defined    → frontmatter evals_scenarios: [...] non-empty (HARD)
3. Implement        → 6 domains execute per dispatcher's order
4. Verify           → reviewer final + AUDITOR Mode 3 cross-check against scenarios
```

Stage 2 is the new HARD requirement.

## evals_scenarios frontmatter field (HARD)

Every planning document (a doc that goes through dispatcher → domains → reviewer-final) MUST have in its frontmatter:

```yaml
---
subject: <one-line>
background: |
  <multi-line context>
scope: [...]
evals_scenarios:
  - <path or N/A: reason>
  - <path or N/A: reason>
---
```

**Acceptable values for each scenario entry**:

1. **Path to existing fixture**: `evals/scenarios/<name>.md` — the fixture file MUST exist and reference this planning doc back
2. **N/A with reason**: `N/A: docs-only` / `N/A: pure-translation` / `N/A: i18n-mirror-update` — for changes that genuinely don't need a runtime test (the reason MUST be one of the allowed enums; arbitrary "N/A: see below" is rejected)
3. **Future commitment**: `TBD: evals/scenarios/<name>.md (commit-by: <PR/issue/date>)` — escape hatch with a deadline; dispatcher accepts but reviewer-final ALWAYS rejects until TBD resolved

**Unacceptable values**:

- Empty list `[]` — implementation cannot proceed without test definition
- Missing `evals_scenarios:` key entirely — same as empty
- `N/A: see below` / `N/A: TBD` without an enumerated reason
- Path to non-existent fixture (dispatcher verifies path exists)

## Allowed N/A reason enum

```yaml
N/A: docs-only           # pure documentation, no behavior change
N/A: pure-translation    # i18n/zh or i18n/ja translation of existing EN content
N/A: i18n-mirror-update  # restoring drifted mirror to EN content (no new behavior)
N/A: typo-fix            # single-word or single-line correction with no semantic change
N/A: cleanup-only        # removing dead code / unused references with no behavior change
```

Any reason outside this enum → dispatcher rejects with `F4 SCOPE_FAILURE: invalid N/A reason; pick from enum or write scenario`.

## When the spec applies (and when not)

### Applies (HARD enforcement)

- Any planning doc that ROUTER escalates to PLANNER (full deliberation path)
- Any RFC under `_meta/rfc/v<X.Y>-*.md` for features touching agent behavior or spec semantics
- Any new agent (`pro/agents/<new>.md`) — requires at least 1 fixture verifying the agent's primary behavior
- Any new HARD RULE introduced to SKILL.md or pro/CLAUDE.md

### Does NOT apply (out of scope)

- ROUTER "Handle Directly" path — short conversational responses
- Express Analysis path — domains run but no PLANNER step (covered by ROUTER's brief report)
- Notes / journal entries / SOUL snapshots / sessions
- Bug fixes that exercise an already-tested code path (existing fixture covers it; planner just references existing path)

## Dispatcher validation

Before dispatcher accepts the planning document for downstream execution:

1. Read planning doc frontmatter
2. Find `evals_scenarios:` key
3. Validate per the rules above:
   - Non-empty list
   - Each entry is path-to-existing OR allowed-N/A OR TBD-with-deadline
4. If validation fails:
   - Output `F4 SCOPE_FAILURE: planning doc <path> missing or invalid evals_scenarios`
   - Halt dispatch
   - Return to planner with the specific failure (planner re-attempts; max 3 cycles before escalating to user)

## Reviewer-final validation

After 6 domains complete and reviewer-final runs:

1. Read planning doc frontmatter `evals_scenarios:`
2. For each `evals/scenarios/<name>.md` entry: verify the fixture exists AND that its expected behaviors are demonstrated by the execution this session
3. For `TBD:` entries: reject with `F10 RESPONSIBILITY_FAILURE: TBD scenarios not resolved before release; either land the fixture this session or split into follow-up issue`
4. For `N/A:` entries: accept but log in audit trail for AUDITOR Mode 3 review

## Anti-patterns

Things that look correct but are actually evasion:

### Anti-pattern 1: catch-all "smoke" fixture

```yaml
evals_scenarios:
  - evals/scenarios/smoke-test.md   # actually empty / says "TODO"
```

Dispatcher MUST check the fixture file has non-trivial content (≥30 lines or ≥1 acceptance criterion) — otherwise treat as empty.

### Anti-pattern 2: reusing unrelated fixture

```yaml
evals_scenarios:
  - evals/scenarios/start-session-compliance.md   # but this PR is about archiver, not start session
```

Reviewer-final SHOULD detect mismatch by checking the fixture's `applies_to:` frontmatter against the PR scope. Mismatch → reject.

### Anti-pattern 3: vague N/A

```yaml
evals_scenarios:
  - N/A: trust me
```

Not in allowed enum → dispatcher rejects.

### Anti-pattern 4: missing the field entirely

```yaml
subject: ...
background: ...
# evals_scenarios not present
```

Missing field = missing eval. Dispatcher treats as empty list → reject.

## Examples (correct)

### Example 1: new feature with new fixture

```yaml
subject: v1.8.7 C6 — gotchas + memory-keeper
evals_scenarios:
  - evals/scenarios/v1.8.7-c6-memory-keeper-seed.md
  - evals/scenarios/v1.8.7-c6-archiver-phase5.md
```

### Example 2: pure docs change

```yaml
subject: Fix typo in references/concept-spec.md
evals_scenarios:
  - N/A: typo-fix
```

### Example 3: i18n mirror update

```yaml
subject: Restore i18n/zh/references/agent-spec.md to match EN after section reorder
evals_scenarios:
  - N/A: i18n-mirror-update
```

### Example 4: scenarios committed but fixtures land same session

```yaml
subject: v1.8.7 F11 — i18n diff parity
evals_scenarios:
  - evals/scenarios/v1.8.7-f11-check-9-pass.md
  - evals/scenarios/v1.8.7-f11-check-9-warn-drift.md
  - evals/scenarios/v1.8.7-f11-check-9-block-future.md (TBD: this release adds WARN only, BLOCK case lands v1.8.8)
```

The TBD entry has explicit deadline (v1.8.8). Dispatcher accepts; reviewer-final flags the TBD for v1.8.8 follow-up.

## Reference

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.5 B5
- Pattern source: `tinyhumansai/openhuman` AGENTS.md:507-521 (Feature design workflow + Planning rule)
- Companion: `pro/agents/planner.md` (template definition), `pro/agents/dispatcher.md` (validation logic)
- Related: `references/agent-spec.md` (agent definitions also benefit from this discipline)
