---
title: Natural-Language Doctor Reference
status: reference
authoritative: false
runtime_authority: SKILL.md
introduced_in: v1.11.0
---

# Natural-Language Doctor

> [!info] Outcome reference
> Doctor is a natural-language capability defined by `SKILL.md`, not a command
> or fixed procedure.

## Intended Outcome

When the user asks whether Life OS is ready, the model should answer:

- what kind of directory is currently authorized;
- whether the Life OS skill is available;
- whether a local Markdown second-brain is explicitly bound;
- whether Full Mode or Conversation-Only Mode is available;
- whether Git is present, reported separately from Life OS readiness;
- what the user can do next.

## Scope

- Inspect only the current authorized workspace and explicitly configured
  bindings.
- Do not search unrelated directories for a second-brain.
- A directory containing `SKILL.md`, `agents/`, and `themes/` is a Life OS
  system/development repository, not a second-brain.
- A Git repository is not a second-brain without explicit user binding.

## Modes

| Status | Meaning |
|---|---|
| `Full Mode` | An approved local Markdown second-brain is bound and usable |
| `Conversation-Only` | Life OS can assist, but no durable second-brain is bound |
| `Needs binding` | The requested persistent operation requires the user to select or create a local directory |
| `Needs attention` | A known permission, path, or data conflict prevents the requested operation |

Git may be reported as `available`, `not present`, `local only`, or `remote
configured`. None of those values independently determines the Life OS mode.

## Repairs

Doctor is read-only unless the user asks for a repair.

A clear repair request authorizes normal scoped changes. Ask only when there
are materially different targets, destructive consequences, external effects,
or other ambiguity.

After a repair, verify the affected condition and report the observed result.
