# Life OS Python Tools

> Layer 4 of the Life OS execution stack. Optional. v1.7 onward.

This directory contains Python tools that operate on the user's second-brain markdown files for batch and background tasks that don't fit naturally inside a Claude Code session.

## Status

**v1.8.0 (post R-1.8.0-011 / R-1.8.0-013).** Pull-based toolkit; modules are invoked on demand by the orchestrator (no cron). The historical v1.7 layout (cortex helpers under `tools/lib/cortex/`, the `tools/cli.py` dispatcher, scheduled `tools/backup.py` / `tools/rebuild_indexes.py` / `tools/migrate.py`) was retired in R-1.8.0-011 and replaced by the modules listed below.

## Authoritative Spec

`references/tools-spec.md` is marked **legacy** (v1.7 Cortex era); it is kept for historical context only and is **not** the active contract. The active per-module contract lives in this README plus each module's docstring.

## Runtime

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) as package manager and runner

## Usage

```bash
# Install dependencies
uv sync

# Run any tool directly via Python module syntax
uv run python -m tools.{tool_name} [args]

# Examples:
uv run python -m tools.search "your query"
uv run python -m tools.export --scope decisions --format pdf
uv run python -m tools.skill_manager list
```

> The previous `life-os-tool {command}` console-script entry point was removed in R-1.8.0-011 along with `tools/cli.py`. The dispatcher pattern was replaced by direct module invocation — same functionality, fewer indirection layers.

## Why Optional

Tools add maintenance automation, not core functionality. A new Life OS user who never installs Python still has the full decision-engine experience inside Claude Code. Tools handle:

- Long-running batch tasks (rebuild concept INDEX, archive old snapshots, compute escalation ladder thresholds)
- Systematic scans of every file (no LLM creativity needed)
- LLM-free pure parsing + YAML generation + markdown I/O

## Currently Shipped Modules

| Module | Purpose |
|--------|---------|
| `tools/approval.py` | Adapter approval / governance flow |
| `tools/embed.py` | Concept / hippocampus vector rebuild (on demand) |
| `tools/export.py` | Batch export of sessions / SOUL snapshots |
| `tools/reconcile.py` | Detect contradictory wiki entries; emit conflict list |
| `tools/research.py` | LLM-free research helpers (HTTP fetch + markdownify) |
| `tools/search.py` | Cross-source search over SOUL / wiki / sessions |
| `tools/seed.py` | Bootstrap helpers for new repos |
| `tools/sync_notion.py` | Two-way sync to Notion mirror |
| `tools/skill_manager.py` | Local skill catalog management |
| `tools/stats.py` | Read `pro/compliance/violations.md` + compute escalation thresholds |
| `tools/lib/` | Shared helpers (HTTP guard, redaction, types) — not invoked directly |

> Removed in R-1.8.0-011 (kept here only as historical context — do not call): the deleted dispatcher / cron scripts (formerly under `tools/cli.py`, `tools/migrate.py`, `tools/backup.py`, `tools/rebuild_indexes.py`) and the deleted Cortex helper layer (formerly `tools/lib/cortex/`).

## Locality Constraint

Per user decision (md + git storage rule, see `pro/compliance/2026-04-19-court-start-violation.md`), all tools run **locally** — invoked from the Claude Code Bash tool or manually. No GitHub Actions, no cron-on-VPS.

## See Also

- `references/data-model.md` — types tools manipulate
- `references/compliance-spec.md` — violations log spec consumed by `tools/stats.py`
- The **legacy** `references/tools-spec.md` and `references/cortex-spec.md` describe the v1.7 Cortex-era contract and are no longer authoritative.
