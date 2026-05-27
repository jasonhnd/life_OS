---
description: Self-driven version of /notion-sync. Polls Notion sync status every 270s until all configured entities are synced or hard cap (12 ticks / 60 min) hits. Resumes from checkpoint on crash. Requires Claude Code (uses ScheduleWakeup).
argument-hint: "[--resume]  (default: full sync from scratch)"
requires_host: claude-code
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - ScheduleWakeup
---

# /notion-sync-and-watch

Self-driven loop wrapping `/notion-sync`. Long-running Notion sync (large outbox / many entities) often hits transient failures (rate limit, network blip, auth refresh). Instead of asking the user to manually retry, this loop ticks every 270s, picks up where it left off via checkpoint file, and only exits when sync is complete or 12 ticks (60 min) hit.

**Pattern source**: tinyhumansai/openhuman `.claude/commands/ship-and-babysit.md` (270s tick + checkpoint resume). **Spec**: `references/self-driven-loops-spec.md`.

## Inputs

- `$ARGUMENTS` (optional)
  - `--resume` — continue from `meta/runtime/<sid>/notion-sync-checkpoint.md` (set by previous failed tick)
  - empty — full sync, start fresh

## Host check (first action)

If host is NOT Claude Code:

```
⚠️ /notion-sync-and-watch requires Claude Code (uses ScheduleWakeup for self-driven loops).
   You're on <host>. Run /notion-sync manually instead (rerun until sync queue is empty).
```

Then STOP. Do not proceed.

## Loop body (one tick)

### Step 1 · Extract or initialize tickCount

If invoked via ScheduleWakeup, extract tickCount from prior `reason` field. Else 1.

### Step 2 · Load checkpoint (if --resume)

If `--resume` flag OR prior tick produced a checkpoint:
- Read `meta/runtime/<sid>/notion-sync-checkpoint.md`
- Restore: which entities are already synced, which pending, last error if any
- Skip entities marked done in checkpoint

If fresh start (no `--resume`, no prior checkpoint):
- Read `meta/config.md` for the list of configured Notion entities (`status_page_id` / `mirror_page_id` / `todo_database_id` / `inbox_database_id` / others)
- Initialize pending list = all configured entities

### Step 3 · Run sync iteration

For each pending entity:

1. Run the corresponding Notion MCP call (per `pro/CLAUDE.md` Step 10a)
2. On success → mark entity done in checkpoint
3. On failure:
   - **Rate limit (429)** → defer this entity to next tick, do not mark failed
   - **Auth refresh needed (401)** → exit immediately, ask user to refresh auth
   - **PII boundary violation** (`scripts/hooks/pre-notion-write.sh` `block`) → exit immediately, surface leak per Step 10a outbound boundary gate
   - **Other error** → record in checkpoint, defer to next tick

### Step 4 · Write checkpoint

After processing all pending entities this tick (whether all succeed or some defer):

```markdown
---
command: notion-sync-and-watch
session_id: <sid>
last_tick: <N>
entities_done: [<list>]
entities_pending: [<list>]
entities_failed: [<list with reasons>]
last_error: <if any>
---

# Notion Sync Checkpoint

<tick history table>
```

Write to `meta/runtime/<sid>/notion-sync-checkpoint.md`. Overwrites the previous tick's checkpoint (single rolling checkpoint).

### Step 5 · Decide exit / continue / hard-cap

| Condition | Action |
|-----------|--------|
| All entities done | **EXIT** — output success summary, STOP |
| Auth refresh needed | **EXIT immediately** — ask user to refresh, STOP (no ScheduleWakeup) |
| PII block | **EXIT immediately** — surface leak, STOP |
| tickCount ≥ 12 | **EXIT with status snapshot** — list pending + failed, ask user, STOP |
| Some entities pending (rate limit deferral / transient error) | **CONTINUE** — schedule next tick |

### Step 6 · Output tick result

Always output one line:

```
🔄 tick N/12 — Notion sync: ✅done=X / ⏳pending=Y / ❌failed=Z. <one-line about what's pending>
```

### Step 7 · Audit trail (per tick)

Write `meta/runtime/<sid>/notion-sync-and-watch-tick-<N>.md` with frontmatter mirroring verify-release-and-watch's audit trail schema (but command name changed).

### Step 8 · Pacing

If EXIT:
- Do NOT call ScheduleWakeup
- Output final summary:

```
✅ Notion sync complete after N ticks.
   Entities synced: <list>
   Total time: <minutes>
```

If CONTINUE:
- Call ScheduleWakeup:
  ```
  ScheduleWakeup({
    delaySeconds: 270,
    prompt: "/notion-sync-and-watch --resume",
    reason: "tick <N+1>/12: <Y entities pending, Z failed transient>"
  })
  ```

## Exit conditions (enumerated)

1. **All entities done** → exit with success summary
2. **Auth refresh needed** → exit immediately, ask user
3. **PII block detected** → exit immediately, surface leak
4. **tickCount ≥ 12** → exit with status snapshot
5. **Notion MCP unavailable** (config has Notion but tools missing) → exit with `⚠️ Notion sync failed — mobile will not see updates`

## Failure handling

- **Checkpoint file corrupt** → fall back to fresh sync (warn user, do not block)
- **Network total failure** → record in checkpoint, continue to next tick (not immediate retry)
- **lifeos config (`meta/config.md`) has NO Notion entity** → exit immediately with `Skipped: no Notion entity configured` (per Step 10a)

## Reference

- Base command: `.claude/commands/notion-sync.md` (the single-iteration sync)
- Spec: `references/self-driven-loops-spec.md`
- RFC: `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.2 B4
- Step 10a contract: `pro/CLAUDE.md` Step 10a (Notion sync responsibilities)
- PII boundary: `references/outbound-pii-patterns.md`
