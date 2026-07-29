---
id: router
status: optional-template
authoritative: false
runtime_authority: SKILL.md
purpose: Clarify the real objective and select a proportionate path.
---

# Router

## Useful when

A request contains several possible objectives, workspaces, targets, or levels
of effort and choosing the wrong one would materially change the result.

## Skip when

The objective and authorized scope are already clear enough to act directly.

## Suggested inputs

- the user's actual message;
- current authorized workspace and exclusions;
- relevant task state already established in the conversation.

## Useful questions

- What result is the user actually asking for?
- What scope is already authorized?
- Is any material ambiguity blocking useful action?
- Can the task be handled directly?
- Would a tool or independent perspective materially improve the result?

## Possible output

A direct answer, one focused clarification, or a concise route naming the next
useful action and why.

## Safety

Do not manufacture ambiguity, expand the workspace, or require a fixed
workflow, theme, agent chain, or number of clarification rounds.
