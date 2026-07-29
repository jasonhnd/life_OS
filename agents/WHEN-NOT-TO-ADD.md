---
title: Agent Template Boundary
status: guidance
authoritative: false
runtime_authority: SKILL.md
---

# Agent Template Boundary

Agent files are optional perspectives. They are not an organization chart the
runtime must reproduce.

Do not add or invoke an agent when:

- direct work is sufficient;
- the perspective is already covered by the current model;
- delegation would add coordination cost without independent value;
- the host cannot provide the claimed isolation or capability;
- the task is too small to benefit from a separate context.

A task-specific temporary agent is preferable to a permanent template when the
need is narrow or unlikely to recur.

Every template:

- remains subordinate to `SKILL.md`;
- may be skipped, combined, adapted, or replaced;
- inherits user scope and privacy boundaries;
- returns useful conclusions and evidence rather than compliance receipts;
- does not require a status line, audit file, tool set, or nested launch.
