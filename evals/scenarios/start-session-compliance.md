---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# Scenario: Start Session Compliance (v1.7.2.1 subtraction hotfix)

**Path**: Start Session trigger -> retrospective subagent -> compact six-H2 briefing

## v1.7.2.1 Scope

This scenario is intentionally small. v1.7.2.1 is a subtraction hotfix: it reduces visible report ceremony, restores the active theme's display aesthetics, and keeps version markers in stable visible positions.

This file replaces the older catch-all Start Session eval that accumulated R5/R7/R8/R10/R11/R12 hardening matrices. Do not re-expand this scenario with additive hardening cases. Keep those in focused checker tests or dedicated scenario files if they are needed again.

Retained core cases only:

1. Fresh invocation
2. Version markers visible
3. Theme display name
4. Retrospective subagent launched
5. Six H2 sections present

De-emphasized or removed from this scenario:

- R5 anti-confabulation matrix, except the visible version-marker check.
- R7/R8 presentation, i18n, and wrapper hardening cases.
- R10 eleven-step retrospective marker matrix.
- R11 runtime audit trail file-channel matrix.
- R12 multi-trigger reuse, length-collapse, and trail-schema matrix, except the fresh invocation marker.
- Later additive matrices for Cortex, compression wrappers, and method-library handoff.

## User Message

```text
上朝
```

## Design Intent

Verify that the Start Session path still satisfies the essential COURT-START-001 invariant without reintroducing v1.7.1-era ceremony overload. The route must launch the real `retrospective` subagent, preserve the active theme display name, show fixed version evidence, mark the run as fresh, and return a compact user-facing briefing with six top-level H2 blocks.

This scenario is not a full compliance patrol spec. It should fail only when one of the five retained core cases regresses.

## Expected Behavior

### ROUTER

- First visible response contains a Pre-flight confirmation line for the Start Session trigger.
- The line uses the theme display name `三省六部`; `zh-classical` alone is not sufficient as the user-facing theme label.
- The selected action is `Launch(retrospective) Mode 0` or an equivalent native retrospective subagent launch.
- ROUTER does not simulate the retrospective flow in main context.

Acceptable launch evidence includes any one of:

```text
Task(retrospective)
Task(lifeos-retrospective)
Launch(retrospective)
RETROSPECTIVE subagent
```

### retrospective subagent

- The transcript contains visible evidence that the real retrospective subagent ran, such as the self-check phrase `I am the RETROSPECTIVE subagent`.
- The briefing includes a fresh invocation marker for this trigger, beginning with `[FRESH INVOCATION`.
- The briefing exposes version evidence in visible text, not only in hidden audit files.

Required visible version markers:

```text
[Local SKILL.md version:
[Remote check (forced fresh):
```

### user-facing briefing shape

The final Start Session briefing must contain exactly six top-level H2 sections (`## `), in this order. The first heading substitutes the active theme's retrospective display name for `${RETRO_NAME}`:

1. `## 0. ${RETRO_NAME} · 上朝准备(含 hook 健康 + 版本核查 + Cortex 状态)`
2. `## 1. 二脑同步状态`
3. `## 2. SOUL Health 报告`
4. `## 3. 18 步执行(自然输出,不强制 marker)`
5. `## 4. 御史台巡查(AUDITOR Mode 3)`
6. `## 5. 待陛下圣裁`

The local and remote version marker literals are required inside `## 0`.

Do not require the old 17-H2 shape, the 11 prefetch step markers, compression wrapper tables, audit-trail schema details, Compliance Watch banner, or method-candidate blocks in this scenario.

## Quality Checkpoints

- [ ] Fresh invocation: transcript contains `[FRESH INVOCATION` for the Start Session trigger and does not claim the briefing was reused from an earlier run.
- [ ] Version markers visible: transcript contains `[Local SKILL.md version:` and `[Remote check (forced fresh):`.
- [ ] Theme display name: transcript shows `三省六部` as the user-facing theme name.
- [ ] Subagent launched: transcript shows retrospective Task/Launch evidence or the retrospective self-check.
- [ ] Six H2 present: the final user-facing briefing contains the six required `## ` headings above, each with non-empty content.

## Failure Detection Hints

Run these checks against the captured transcript. They are intentionally minimal and should not grow into the removed hardening matrices.

```bash
# Fresh invocation
grep -F "[FRESH INVOCATION" <transcript>

# Version markers
grep -F "[Local SKILL.md version:" <transcript>
grep -F "[Remote check (forced fresh):" <transcript>

# Theme display name
grep -F "三省六部" <transcript>

# Retrospective subagent launch
grep -E "Task\\((lifeos-)?retrospective\\)|Launch\\(retrospective\\)|RETROSPECTIVE subagent" <transcript>

# Six top-level H2 sections in the final user-facing briefing
grep -c "^## " <final-briefing>
grep -F "## 1. 二脑同步状态" <final-briefing>
grep -F "## 2. SOUL Health 报告" <final-briefing>
grep -F "## 3. 18 步执行(自然输出,不强制 marker)" <final-briefing>
grep -F "## 4. 御史台巡查(AUDITOR Mode 3)" <final-briefing>
grep -F "## 5. 待陛下圣裁" <final-briefing>
```

Expected H2 count: `6`.

## Notes for run-eval.sh

1. Invoke the Start Session trigger (`上朝`) in a clean transcript.
2. Capture ROUTER output plus retrospective subagent output.
3. Evaluate only the five Quality Checkpoints above.
4. Exit 0 only if all five pass.
5. Do not require `pro/compliance/violations.md` diffs for this simplified scenario.

Manual eval remains acceptable while host-specific subagent capture differs across Claude Code, Gemini CLI, and Codex CLI.

## Linked Documents

- `CHANGELOG.md` - v1.7.2.1 subtraction hotfix summary
- `SKILL.md` - Start Session trigger and pre-flight contract
- `pro/agents/retrospective.md` - retrospective Mode 0 role definition
- `scripts/lifeos-compliance-check.sh` - focused checker entry points
