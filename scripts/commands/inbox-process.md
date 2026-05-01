---
description: 走查 _meta/inbox/to-process/ — 对每个待处理项判断是否入 wiki / archive / defer / reject
argument-hint: [可选 focus，例如 wiki / fintech / methodology]
allowed-tools: Read, Bash, Glob, Grep, Write, Edit
---

# /inbox-process · Inbox ingest pipeline (v1.8.1 F3)

User invoked: `/inbox-process $ARGUMENTS`

## What this does

Walks every `*.md` in `_meta/inbox/to-process/` and proposes one of four
dispositions per item:

| Disposition | Action |
|---|---|
| **accept** | Write a new `wiki/<domain>/<slug>.md` entry per `wiki/SCHEMA.md`, append `wiki/log.md` (action=created), move source file to `_meta/inbox/archive/` |
| **update** | Edit an existing `wiki/<domain>/<slug>.md` entry in place, append `wiki/log.md` (action=updated), move source file to `_meta/inbox/archive/` |
| **archive** | Source has lasting reference value but doesn't merit a wiki entry; move to `_meta/inbox/archive/` only |
| **reject** | One-off / no future value; move to `_meta/inbox/archive/` and append `wiki/log.md` (action=rejected) |
| **defer** | Worth processing later; leave in to-process/ and add `defer_until: YYYY-MM-DD` to its frontmatter |

## Backup mode

**Slash command is backup mode**. Primary path: user says "处理 inbox" /
"扫一下 inbox" / "process inbox" — `pre-prompt-guard` hook auto-detects
and ROUTER reads `scripts/prompts/inbox-process.md`. The slash command
exists for explicit invocation, focus narrowing, and audit/test.

## Execution

Read and follow `scripts/prompts/inbox-process.md` step-by-step. That
prompt defines the full workflow (scan → triage → propose → user-confirm
→ execute → log). Do not invent your own flow.

If `$ARGUMENTS` is non-empty, treat it as a focus hint:
- domain name (`fintech`, `methodology`) → only process items that look like they belong to that domain
- `wiki` → only propose accept/update; auto-defer anything ambiguous
- `clean` → propose reject for any item older than 30 days that hasn't been touched

After execution, the user MUST see:
1. A per-item disposition table with their accept/reject choices
2. Counts (N accepted, M updated, K archived, L rejected, P deferred)
3. Updated `wiki/log.md` excerpt (last 10 lines) confirming entries landed
