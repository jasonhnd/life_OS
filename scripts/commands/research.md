---
description: 多 agent 并行调研一个 topic，综合后产出 wiki entry 草稿（含反 confirmation bias）
argument-hint: <topic> [--depth deep] [--thesis "<hypothesis>"]
allowed-tools: Read, Bash, Glob, Grep, Write, Edit, WebSearch, WebFetch, Task
---

# /research · Multi-agent research → wiki draft (v1.8.1 F4)

User invoked: `/research $ARGUMENTS`

## What this does

Spawns parallel `general-purpose` subagents to research a topic from
multiple angles, synthesizes results into a single `wiki/<domain>/<slug>.md`
draft (per `wiki/SCHEMA.md`), and presents it for user accept/edit/reject.

Default: 5 agents (academic / practitioner / contrarian / origin / adjacent).
With `--depth deep`: 8 agents (adds mechanistic / data-statistics / meta-review).
With `--thesis "<hypothesis>"`: thesis-driven mode — agents weight evidence
for and against the stated hypothesis.

Total wall time target: **≤ 7 minutes** (5 min parallel agents + 2 min
synthesis).

## Backup mode

**Slash command is backup mode**. Primary path: user says "调研一下 X" /
"research X" / "深挖 X" — pre-prompt-guard hook auto-detects and ROUTER
reads `scripts/prompts/research.md`. Slash command exists for explicit
arguments (`--depth`, `--thesis`).

## Execution

Read and follow `scripts/prompts/research.md` step-by-step. That prompt
defines the 5-phase workflow (decompose → parallel → synthesize →
counter-bias → user-review → write). Do not invent your own flow.

Argument parsing:
- First positional non-flag = `<topic>` (required; reject if missing)
- `--depth deep` = use 8 agents instead of 5
- `--thesis "<...>"` = thesis-driven mode; treat thesis as the working
  hypothesis to test

After execution, the user MUST see:
1. The 5-or-8 agent summaries (≤ 500 words each)
2. The synthesized wiki draft with full frontmatter
3. The Counterpoints section (always — even if "none found, all sources
   converge")
4. Explicit accept / edit / reject prompt
5. On accept: `wiki/log.md` updated, file written, `wiki/INDEX.md` patched

## Cost note

This command is expensive (5-8 parallel WebSearch+WebFetch agents). Use it
only when:
- The topic genuinely needs multi-perspective coverage
- You're seeding a wiki entry from scratch (vs updating)
- A single-source draft would carry too much confirmation bias

For quick lookups, use `/search` or just talk to the orchestrator.
