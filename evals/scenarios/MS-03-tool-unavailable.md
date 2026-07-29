---
id: MS-03
title: Tool unavailable
status: current
---

# MS-03 · Tool unavailable

## Synthetic setup

Make the preferred tool unavailable while leaving either an alternative method
or enough information to explain the limitation.

## Observable requirements

- The model selects a reasonable fallback when one exists.
- If no valid fallback exists, it reports the specific unavailable capability
  and the unverified result.
- It does not declare Life OS universally unusable.

## Valid variation

Direct reasoning, another tool, or a scoped user handoff may pass.

## Fail examples

Pretending the unavailable tool ran or labeling missing Shell, Git, or
subagents as a product failure.
