---
title: Agents and Hosts
version: 1.11.0
status: current
---

# Agents and Hosts

## Agents

The 24 files under `agents/` are reusable perspectives. They are optional and
open-ended. The model may work directly, adapt one, combine several, or create
an ad hoc specialist.

An agent inherits the same user scope, privacy boundary, and completion
standard as the parent. It should return useful evidence and conclusions, not a
compliance receipt.

## Hosts

Files under `hosts/` describe capabilities and limitations of individual AI
hosts. They do not define different Life OS products.

Shell, applications, connectors, and subagents may be used when available and
useful. A missing capability causes a fallback or a stated limitation, not a
different authority model.
