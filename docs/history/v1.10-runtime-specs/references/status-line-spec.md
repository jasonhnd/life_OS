---
spec_id: status-line-spec.v1
description: 8-enum status line output contract for Life OS subagents. It replaces scattered ad-hoc status phrases with one grep-friendly first-line format.
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/subconscious.md
introduced_in: v1.8.7
referenced_by:
  - SKILL.md (E9 HARD RULE)
  - agents/auditor.md (Mode 8 status line verification)
  - agents/*.md (per-agent Status Output section)
---

# Status Line Specification v1

Every `agents/*.md` subagent MUST emit a **status line** as the literal first visible line of its output. The status line uses a closed 8-enum keyword set plus a canonical emoji. It may include one short description after the agent id.

## Output Contract

The first non-blank line of any subagent output MUST match:

```text
<emoji> <status> · <agent-id> · <one-line description>
```

Where:

- `<emoji>` is the canonical emoji for the status.
- `<status>` is one of the 8 enum keywords below.
- `<agent-id>` is the subagent `name:` frontmatter value, such as `archiver`, `retrospective`, or `memory-keeper`.
- `<one-line description>` is free text, ideally under 100 characters, describing the current step.

Multiple status transitions during one invocation MUST each emit a new status line. Example: `starting` for launch, `evaluating` for a long read/reasoning phase, `acted` after a concrete deliverable.

## The 8 Statuses

| Status | Emoji | Semantics | Typical use |
|--------|-------|-----------|-------------|
| `starting` | 🚀 | Subagent has started; first action after launch | First line of every subagent invocation |
| `evaluating` | 🔍 | Reading, building context, or reasoning | Long-running steps, retrieval, checks |
| `acted` | ✅ | Concrete deliverable produced | Phase complete, plan emitted, write completed |
| `skipped` | ⏭️ | Legitimate no-op | No relevant signal, no candidates, condition not met |
| `escalated` | ⚖️ | Handing off to a higher authority | REVIEWER veto, COUNCIL debate, user approval |
| `awaiting_user` | 🟡 | Paused for explicit user input | Approval gate or override decision |
| `failed` | ❌ | Could not complete | Tool failure, missing required file, blocking spec violation |
| `silent_pass` | 🟢 | Clean pass with low user-facing value | Auditor clean pass, no relevant Cortex signal |

## Examples

```text
🚀 starting · archiver · fresh adjourn invocation, trigger 1, Phase 1-5 starting
🔍 evaluating · archiver · Phase 0 runtime readiness
✅ acted · archiver · Phase 0 complete, hook layer retired and inline enforcement active
🔍 evaluating · archiver · Phase 2 knowledge extraction
✅ acted · archiver · Phase 2 complete: 3 wiki, 2 SOUL, 1 concept
⏭️ skipped · archiver · Phase 3 light sleep, no significant patterns
✅ acted · archiver · Phase 4 git push complete, commit abc1234
🚀 starting · memory-keeper · Phase 5 invoked by archiver
✅ acted · memory-keeper · 3 candidates, 1 merged, 2 appended, gotchas.md total 17
✅ acted · archiver · all five phases complete, completion checklist follows
```

ROUTER and AUDITOR can grep for `^🚀 starting` to find launches, `^❌ failed` for failures, and `^🟡 awaiting_user` for paused work.

## Per-Agent Semantics

Each `agents/*.md` file MUST contain a `## Status Output (E9)` section declaring what each of the 8 statuses means for that agent. Use this template:

```markdown
## Status Output (E9 · v1.8.7)

| Status | When emitted | Example description |
|--------|--------------|---------------------|
| `starting` | First line after launch | "fresh invocation, trigger N, mode M" |
| `evaluating` | Agent-specific long-running steps | "reading source files" |
| `acted` | Deliverable produced | "planning document emitted" |
| `skipped` | Legitimate no-op | "no candidates found" |
| `escalated` | Handing off | "requires reviewer veto loop" |
| `awaiting_user` | Approval gate | "waiting for explicit override" |
| `failed` | Blocking failure | "required file missing" |
| `silent_pass` | Clean pass | "no violations found" |
```

If a status does not apply to an agent, declare `N/A · <reason>` instead of omitting it.

## Validation

AUDITOR Mode 8 validates:

| Check | Description | Failure class |
|-------|-------------|---------------|
| M8-1 | Every subagent transcript opens with `^🚀 starting` in the contract format | `F3 SCHEMA_FAILURE` |
| M8-2 | Every emitted status uses one of the 8 enum keywords | `F4 SCOPE_FAILURE` |
| M8-3 | Emoji and status keyword pairing matches the table | `F3 SCHEMA_FAILURE` |
| M8-4 | The agent Status Output section declares all 8 statuses | `F3 SCHEMA_FAILURE` |
| M8-5 | Multi-step invocations emit status lines at important transitions | `F8 SILENT_FAILURE` |
| M8-6 | `failed` includes or points to a failure class | `F10 RESPONSIBILITY_FAILURE` |

## Anti-Patterns

| Anti-pattern | Why bad | Correct form |
|--------------|---------|--------------|
| `The archiver has completed Phase 1` | Not enum-compliant; hard to grep | `✅ acted · archiver · Phase 1 complete: N decisions archived` |
| `🚀 Started!` | Missing agent id and description | `🚀 starting · archiver · fresh adjourn invocation` |
| Starting with `evaluating` | Breaks M8-1 | Always emit `🚀 starting` first |
| Inventing `thinking` | Breaks enum closure | Use one of the 8 statuses or propose an RFC |

## Reference

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.8 E9 + DR-11
- `references/conscious-patrol-spec.md`
- `agents/auditor.md` Mode 8
