---
title: "Hermes Local"
scope: "local execution surface"
audience: "maintainers"
status: "normative naming note"
last_updated: 2026-04-26
related:
  - docs/architecture/execution-layer.md
  - docs/architecture/prompt-cache-strategy.md
  - docs/architecture/mcp-server.md
  - tools/context_compressor.py
---

# Hermes Local

> User-facing name for the Life OS local execution surface. Internal specs and
> agent contracts still use `execution layer`, `Layer 3`, and `Layer 4`.

## Naming Contract

`Hermes Local` is the public label for the local safeguards and automation that
make Life OS enforceable outside the LLM prompt. It combines:

- `Layer 3`: host/runtime backstops such as shell hooks and pre-tool guards.
- `Layer 4`: local Python tools for deterministic batch work, indexing, memory,
  compression, search, and method management.
- `execution layer`: the internal architecture term for Layer 3 + Layer 4
  together.

Use `Hermes Local` in user-facing release notes and README copy. Keep
`execution layer`, `Layer 3`, and `Layer 4` in specs, implementation notes,
compliance rules, and code comments where stable internal labels matter.

## Attribution

Hermes Local borrows design patterns and forks selected local-tool components
from [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
under the MIT License, currently attributed in source headers to commit
`59b56d445c34e1d4bf797f5345b802c7b5986c72`.

Life OS does not embed the full Hermes gateway/runtime. The borrowed pieces are
adapted for Life OS's markdown-first second-brain, host-agnostic orchestration,
and local-only execution model.

The context compression module follows the Hermes v0.11 upstream naming:
`context_compressor` is the renamed successor of `trajectory_compressor`. Life
OS docs and wrappers should use `tools/context_compressor.py` and avoid
reintroducing the old `trajectory_compressor` filename as the public reference.

## Current Borrow/Fork Surface

- `tools/approval.py`: dangerous-command approval patterns and approval-flow
  structure, adapted to Life OS escalation.
- `tools/context_compressor.py` and
  `tools/manual_compression_feedback.py`: context compression primitives and
  user-facing compression summaries.
- `tools/prompt_cache.py`: prompt-cache breakpoint strategy helpers.
- `tools/memory.py`: bounded local memory with injection/exfiltration checks.
- `tools/session_search.py`: SQLite FTS session search adapted for Life OS
  markdown sources.
- `tools/skill_manager.py`: method/skill management adapted to the Life OS
  method library.

Each forked or borrowed file in `tools/` should keep a top-of-file attribution
comment naming `NousResearch/hermes-agent`, the MIT License, and the source
commit or upstream module.

## Cortex Boundary

Hermes Local supports Cortex with local tooling, but it is not an activation
gate. In v1.7.2 Cortex is always-on at the orchestration layer and degrades
inside the workflow when indexes, subagents, or local tools are unavailable.

Runtime thresholds and host settings belong in `_meta/config.md`. Do not add or
document a separate Cortex config file under `_meta/cortex/`; that directory is
reserved for compiled/log artifacts such as `bootstrap-status.md` and
`decay-log.md`.
