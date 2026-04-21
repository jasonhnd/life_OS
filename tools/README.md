# Life OS Python Tools

> Layer 4 of the Life OS execution stack. Optional. v1.7 onward.

This directory contains Python tools that operate on the user's second-brain markdown files for batch and background tasks that don't fit naturally inside a Claude Code session.

## Status

**v1.7 Phase 1 bootstrap.** Only the project skeleton exists in this commit — no tools implemented yet. Tools will land in subsequent commits per `references/tools-spec.md`.

## Authoritative Spec

See [`references/tools-spec.md`](../references/tools-spec.md) for the full contract: directory structure, runtime requirements, dataclass schemas, and per-tool contracts.

## Runtime

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) as package manager and runner

## Usage

```bash
# Install dependencies
uv sync

# Run any tool
uv run tools/{tool_name}.py [args]

# Or via the unified CLI (when available)
uv run life-os-tool {command} [args]
```

## Why Optional

Tools add maintenance automation, not core functionality. A new Life OS user who never installs Python still has the full decision-engine experience inside Claude Code. Tools handle:

- Long-running batch tasks (rebuild concept INDEX, archive old snapshots, compute escalation ladder thresholds)
- Systematic scans of every file (no LLM creativity needed)
- LLM-free pure parsing + YAML generation + markdown I/O

## Planned Modules (per tools-spec.md)

| Module | Purpose | Phase |
|--------|---------|-------|
| `tools/lib/second_brain.py` | Dataclasses for all second-brain types | 1 |
| `tools/lib/cortex/hippocampus.py` | Helpers for `_meta/sessions/INDEX.md` operations | 1 |
| `tools/lib/cortex/concept.py` | Concept file CRUD + Hebbian update | 1 |
| `tools/stats.py` | Read `pro/compliance/violations.md` + compute escalation thresholds | 2 |
| `tools/backup.py` | Quarterly archival of violations.md, snapshots, etc. | 2 |
| `tools/rebuild_indexes.py` | Recompile INDEX.md files (concepts, methods, sessions, wiki) | 2 |

## Locality Constraint

Per user decision (md + git storage rule, see `pro/compliance/2026-04-19-court-start-violation.md`), all tools run **locally** — invoked from the Claude Code Bash tool or manually. No GitHub Actions, no cron-on-VPS, no external API calls.

## See Also

- `references/tools-spec.md` — authoritative contract
- `references/data-model.md` — types tools manipulate
- `references/cortex-spec.md` — Cortex layer this toolkit primarily supports
- `references/compliance-spec.md` — violations log spec consumed by `tools/stats.py`
