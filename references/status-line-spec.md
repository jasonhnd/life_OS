---
spec_id: status-line-spec.v1
description: 8-enum status line output contract unifying lifeos's 5+ ad-hoc emoji status patterns (Pre-flight Compliance Check / Subagent self-check / AUDITOR silent-pass / self-driven loop tick / Adjourn Confirmation). Every subagent's first output line MUST be a status line. Each of 22 subagents declares its own enum semantics in its agent file. Pattern source — OpenHuman gitbooks/features/subconscious.md activity-log colored status indicators, adapted to lifeos as plain emoji + enum keyword (md-only constraint).
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/subconscious.md (7 colored status indicators in activity log)
introduced_in: v1.8.7 (added 2026-05-26 per DR-11 reversal of DR-01)
referenced_by:
  - SKILL.md (E9 HARD RULE)
  - pro/agents/auditor.md (Mode 8 status line verification)
  - all 22 pro/agents/*.md (Status Output section per agent)
---

# Status Line Specification v1

Every `pro/agents/*.md` subagent MUST emit a **status line** as the literal first line of its visible output. The status line uses a closed 8-enum keyword set + emoji, optionally followed by a single-line description.

## Output contract (HARD)

The first non-blank line of any subagent output MUST match exactly:

```
<emoji> <status> · <agent-id> · <one-line description>
```

Where:

- `<emoji>` is the canonical emoji for the status (table below)
- `<status>` is one of 8 enum keywords (table below)
- `<agent-id>` is the subagent's `name:` frontmatter value (e.g. `archiver`, `retrospective`, `memory-keeper`)
- `<one-line description>` is free-text (≤ ~100 chars), agent-specific semantic

Multiple status transitions during one invocation MUST each emit a new status line (e.g. archiver Phase 0 `starting` → Phase 1 `evaluating` → Phase 5 `acted`).

## The 8 enum statuses

| Status | Emoji | Semantics | Typical use |
|--------|-------|-----------|-------------|
| `starting` | 🚀 | Subagent has started; first action after Task() launch | First line of every subagent invocation; replaces existing `✅ I am the X subagent` self-check |
| `evaluating` | 🔍 | Mid-execution: reading files, building context, running LLM reasoning | Long-running steps (archiver Phase 2 / retrospective Mode 0 housekeeping / Cortex hippocampus retrieval) |
| `acted` | ✅ | Task executed successfully; concrete deliverable produced | archiver Phase complete, planner planning document emitted, knowledge-extractor produced YAML output |
| `skipped` | ⏭️ | No-op decision: nothing relevant found, or condition not met | memory-keeper found 0 gotcha candidates in session; AUDITOR Mode 3 found no violations; concept-lookup found no canonical concept |
| `escalated` | ⚖️ | Handing off to higher authority (REVIEWER veto / COUNCIL debate / user) | planner emitting to reviewer; reviewer triggering COUNCIL; advisor flagging behavior pattern requiring user attention |
| `awaiting_user` | 🟡 | Paused for explicit user input (approval gate) | Conscious Patrol task awaiting user OK to act; archiver detected ambiguous candidate; reviewer veto requiring user override decision |
| `failed` | ❌ | Execution error; cannot complete the task | Tool call failed; required file missing; spec violation detected and unfixable; subagent crash |
| `silent_pass` | 🟢 | High-frequency low-noise pass (no surfacing needed) | AUDITOR Mode 3 found no violations; AUDITOR Mode 7 all M7-1..M7-7 PASS; cortex pull check found no relevant signal |

## Examples

### Replacing existing patterns

| v1.8.6 ad-hoc | v1.8.7 status line |
|---------------|-------------------|
| `✅ I am the ARCHIVER subagent · this is a FRESH adjourn invocation (trigger 1 of session).` | `🚀 starting · archiver · fresh adjourn invocation, trigger 1, 4-phase flow starting now` |
| `🔱 御史台 · 静默通过` | `🟢 silent_pass · auditor · Mode 3 patrol — 0 violations across A1/A2/A3/B/C/D/E classes` |
| `🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0` | (this is ROUTER's own output, not a subagent — ROUTER status output covered in SKILL.md, not this spec) |
| `🔄 tick N/12 — checks: ✅PASS=8 / ❌FAIL=2. Auto-fixed GitHub Release publish.` | `🔍 evaluating · verify-release-and-watch · tick 5/12 — checks 8 PASS / 2 FAIL, auto-fixed Release publish, retrying next tick` |

### Multi-status invocation example (archiver)

```
🚀 starting · archiver · fresh adjourn invocation, trigger 1, 4-phase flow starting now
🔍 evaluating · archiver · Phase 0 hook health check
✅ acted · archiver · Phase 0 complete, hooks healthy
🔍 evaluating · archiver · Phase 2 knowledge extraction
✅ acted · archiver · Phase 2 complete — 3 wiki / 2 SOUL / 1 concept canonical
🔍 evaluating · archiver · Phase 3 DREAM 3-day deep review
⏭️ skipped · archiver · Phase 3 light sleep — no significant patterns
✅ acted · archiver · Phase 4 git push complete, commit abc1234
🚀 starting · memory-keeper · Phase 5 invoked by archiver
✅ acted · memory-keeper · 3 candidates, 1 merged, 2 appended — gotchas.md total 17
✅ acted · archiver · all 5 phases complete, completion checklist follows
```

ROUTER (and AUDITOR) can grep for `^🚀 starting` to find each subagent launch, `^❌ failed` for errors, `^🟡 awaiting_user` for paused tasks. **One pattern, one tool, full visibility.**

## Per-agent enum semantics (HARD)

Each `pro/agents/*.md` MUST contain a `## Status Output (E9)` section declaring its own semantics for the 8 statuses. Example template:

```markdown
## Status Output (E9 · v1.8.7)

| Status | When emitted | Example description |
|--------|--------------|-------------------|
| `starting` | First line after Task() launch | "fresh invocation, trigger N, mode M" |
| `evaluating` | (specific to this agent's long-running steps) | (agent-specific) |
| `acted` | (deliverable produced) | (agent-specific) |
| `skipped` | (when no-op is legitimate) | (agent-specific) |
| `escalated` | (when handing off) | (agent-specific or "N/A — this agent never escalates") |
| `awaiting_user` | (approval gate condition) | (agent-specific or "N/A") |
| `failed` | (specific failure modes from frontmatter `failure_modes.known`) | (agent-specific) |
| `silent_pass` | (high-frequency clean-pass cases) | (agent-specific or "N/A") |
```

Status that doesn't apply to an agent MUST be declared `N/A — <reason>` rather than omitted. Example: memory-keeper never emits `escalated` (it writes to pro/gotchas.md directly, no higher authority); declared as `N/A — memory-keeper is terminal writer for gotchas, no escalation path`.

## Validation (AUDITOR Mode 8)

AUDITOR Mode 8 (new in v1.8.7) validates:

| Check | Description | Failure class |
|-------|-------------|---------------|
| M8-1 | Every subagent transcript opens with `^🚀 starting` line matching contract format | `F3 SCHEMA_FAILURE: missing or malformed starting status line` |
| M8-2 | Every emitted status line uses one of 8 enum keywords (no free-form invention) | `F4 SCOPE_FAILURE: invented status keyword <X>` |
| M8-3 | Emoji ↔ status keyword pairing matches table (no `✅ failed` mismatch) | `F3 SCHEMA_FAILURE: emoji/status mismatch` |
| M8-4 | agent's status_line section in pro/agents/<name>.md declares all 8 statuses (with N/A explicit) | `F3 SCHEMA_FAILURE: incomplete Status Output declaration in <agent>.md` |
| M8-5 | Multi-status invocation emits status line at each phase/step transition | `F8 SILENT_FAILURE: agent skipped status emission at transition` |
| M8-6 | `failed` status includes a failure_class reference (F1-F17 or A/B/C/D/E) | `F10 RESPONSIBILITY_FAILURE: failure status without classification` |

## Migration plan (v1.8.7 within-release)

22 subagents migrate in batches. For each agent:

1. Add `## Status Output (E9 · v1.8.7)` section declaring 8 enum semantics
2. Existing `✅ I am the X subagent` line becomes `🚀 starting · <name> · ...`
3. Existing emoji status patterns (e.g. `🔱 御史台 · 静默通过`) get a status-line wrapper but keep narrative text after the `·` separator for backward readability
4. Audit trail (existing R13 md format) gains optional `status_line:` frontmatter field recording the latest status

**Backward compatibility**: during migration window, both v1.8.6 ad-hoc emoji AND v1.8.7 status line acceptable. AUDITOR Mode 8 WARN-level initially. v1.8.8 (whenever that ships): old patterns removed, Mode 8 BLOCK level.

## Anti-patterns

| Anti-pattern | Why bad | Correct form |
|--------------|---------|--------------|
| `✅ The archiver has completed Phase 1` (free-form) | Not enum-compliant; AUDITOR can't grep | `✅ acted · archiver · Phase 1 complete — N decisions / M tasks archived` |
| `🚀 Started!` (no agent-id, no description) | Useless to AUDITOR / reader | `🚀 starting · <agent-id> · <what's about to happen>` |
| Skipping starting line and going straight to evaluating | Breaks M8-1 contract | Always emit `🚀 starting` first, even if next line is `🔍 evaluating` 100ms later |
| Inventing new status (`🤔 thinking`) | Breaks enum closure | If existing 8 don't cover, propose enum extension via RFC, not ad-hoc |

## Reference

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.8 E9 + DR-11
- Pattern source: `tinyhumansai/openhuman` `gitbooks/features/subconscious.md` 7-state activity log (In progress / Acted / Skipped / Awaiting approval / Failed / Cancelled / Dismissed) — lifeos adapted to 8 states with stronger semantics (split `Skipped`/`Dismissed`/`Cancelled` → `skipped`; added `escalated` + `silent_pass` for lifeos's deliberation + audit patterns)
- Companion: `references/conscious-patrol-spec.md` (E10 path D — each patrol task outputs status line per this spec)
- Companion: `pro/agents/auditor.md` §Mode 8 (validation)
