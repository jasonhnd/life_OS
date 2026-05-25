---
spec_id: self-driven-loops-spec.v1
description: Specification for ScheduleWakeup-based self-driven command loops. Defines the 270s interval rationale (Anthropic prompt cache window), 12-tick hard cap (60 min), exit conditions, host compatibility (Claude Code only), and degradation paths for non-supporting hosts. Pattern borrowed from tinyhumansai/openhuman `.claude/commands/ship-and-babysit.md`.
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, .claude/commands/ship-and-babysit.md (ScheduleWakeup 270s + 12 tick pattern)
introduced_in: v1.8.7
referenced_by:
  - .claude/commands/verify-release-and-watch.md
  - .claude/commands/notion-sync-and-watch.md
  - SKILL.md (Self-driven loops section)
---

# Self-Driven Loops Specification v1

Specification for slash commands that use `ScheduleWakeup` to self-pace iterative checks (poll → fix → recheck) without user intervention until a terminal state or a hard cap is reached.

## When to use self-driven loops

Self-driven loops are appropriate when ALL of these hold:

1. **The task has a clear terminal state** (e.g. "all 9 verify-release checks PASS", "all Notion items synced"). Vague "monitor forever" is not a valid use case
2. **Each iteration is cheap** (one or two tool calls + brief LLM reasoning, not a full subagent launch)
3. **External state can change between iterations** (CI completes, GitHub Release publishes, Notion sync finishes, user pushes a fix)
4. **The user has explicitly invoked the loop** (e.g. typed `/verify-release-and-watch v1.8.7`) — never auto-invoke a self-driven loop from another command

Inappropriate use cases (do NOT build self-driven loops for):

- ❌ Pure monitoring with no clear exit (e.g. "watch the queue forever")
- ❌ Tasks that need user input mid-loop (use a regular interactive command)
- ❌ Tasks where each iteration is expensive (heavy LLM work) — those are better as one-shot commands
- ❌ Cron-style scheduled tasks (lifeos pivoted away from cron in v1.8.0; do not reintroduce)

## Interval choice: 270s (HARD)

Use `delaySeconds: 270` for every `ScheduleWakeup` call inside a self-driven loop. The rationale (from Anthropic Claude Code behavior):

- Anthropic prompt cache TTL is **5 minutes (300s)**
- Sleeping past 300s means the next wake-up reads full conversation context **uncached** — slower and more expensive
- 270s stays **inside** the cache window with 30s safety margin
- Stop trying to think of it as "5 minutes" or any other round-minute value — 270s is a cache-window optimization, not a calendar interval

**Exceptions** (use longer delay only when justified):

- Tasks where external state changes on a known cadence longer than 5 min (e.g. waiting for a GitHub Release CDN propagation that takes ~10 min): use 600s, accept the cache miss
- Idle fallback heartbeats (no specific signal to watch): use 1200-1800s, accept the cache miss in exchange for not burning context every 4.5 min

Picking values between 300 and 1200s is anti-optimization — pay the cache miss without amortizing it.

## Hard cap: 12 ticks (60 minutes)

Every self-driven loop MUST track `tickCount` (incremented on every loop entry, regardless of whether work was done or only waiting). After 12 ticks:

- **Stop the loop** (do NOT call ScheduleWakeup again)
- **Output a status snapshot** to the user: current state, what's still pending, why timeout hit
- **Ask the user** how to proceed (rerun? abandon? escalate?)

The 60-minute cap reflects: if external state hasn't reached terminal in an hour, something is wrong (CI hanging / Release stuck Draft / Notion auth expired) and human eyes are needed.

`tickCount` MUST be visible in the `ScheduleWakeup` `reason` field for every call (e.g. `"tick 5/12: waiting for GitHub Release publish"`) so it's recoverable across ticks and can't drift.

## Exit conditions

Each self-driven loop defines its own exit condition. Common patterns:

| Pattern | Example |
|---------|---------|
| All-checks-pass | "All 9 verify-release checks PASS" → exit |
| Empty-queue | "Notion sync items queue empty" → exit |
| User-resolved | "User has manually completed the blocker" → exit |
| Hard-cap | "tickCount > 12" → exit with status snapshot |

Mixed exit conditions are allowed but must be enumerated explicitly in each command's spec.

When exit condition holds:
- Do NOT call `ScheduleWakeup`
- Output a final one-line summary including any URLs / artifact paths
- The transcript ends naturally — user sees the final result

## Host compatibility (Claude Code only)

`ScheduleWakeup` is a Claude Code-specific tool. Other lifeos-supported hosts (Gemini CLI / OpenAI Codex CLI) do NOT have an equivalent capability as of v1.8.7.

Every self-driven loop command MUST declare:

```yaml
---
description: <one-liner>
argument-hint: <args>
requires_host: claude-code
allowed-tools:
  - Bash
  - Read
  - Edit
  - ScheduleWakeup
---
```

When invoked on a non-Claude-Code host:

1. ROUTER MUST detect the host (via existing host detection in SKILL.md)
2. Output a single error message:
   ```
   ⚠️ `/<command>` requires Claude Code (uses ScheduleWakeup for self-driven loops).
      You're on <host>. Run `/<base-command>` instead (manual reruns).
   ```
3. Do NOT proceed with the loop body

Manual fallback path: every self-driven loop should have a non-watch sibling command (e.g. `/verify-release` is the non-watch version of `/verify-release-and-watch`). The non-watch version works on any host and the user reruns manually.

## Required command structure

A self-driven loop command file (`.claude/commands/<name>-and-watch.md`) MUST contain these sections:

```markdown
---
description: <one-liner>
argument-hint: <args>
requires_host: claude-code
allowed-tools: [Bash, Read, Edit, ScheduleWakeup, ...]
---

# /<command>-and-watch

<Purpose paragraph: what this loop achieves, what terminal state it exits on>

## Inputs

- `$ARGUMENTS` (optional/required) — description

## Loop body (one tick)

1. **Read tickCount** — extract from previous ScheduleWakeup reason if present, else 1
2. **Check exit condition** — if exit, output final summary and STOP (do not call ScheduleWakeup)
3. **Perform iteration work** — run checks, fix issues found
4. **Decide next state** — exit / continue / hit hard-cap
5. **Pacing**:
   - If exit → stop
   - If hit hard-cap (tickCount ≥ 12) → output status snapshot, ask user, STOP
   - Otherwise → call `ScheduleWakeup({delaySeconds: 270, prompt: "/<command>-and-watch <args>", reason: "tick <N+1>/12: <what's pending>"})`

## Exit conditions (enumerate)

- All checks PASS → exit with link
- Hard cap → exit with snapshot
- User-cancel signal → exit
- Critical error → exit with error (do not retry)

## Failure handling

- <command-specific failure modes and recovery>

## Host compatibility

If non-Claude-Code host: error out per spec, point to `/<base-command>` for manual reruns.
```

## Audit trail

Every iteration of a self-driven loop SHOULD write to `_meta/runtime/<sid>/<command>-tick-<N>.md` with:

- tickCount (current)
- timestamp
- checks run + their results
- decisions made (continue / exit / fix applied)
- next action (sleep until / final exit)

The audit trail allows post-hoc reconstruction of why a loop took N ticks or why it bailed out.

## Reference

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.2 B4
- Pattern source: `tinyhumansai/openhuman` `.claude/commands/ship-and-babysit.md` (Phase 4 babysit loop)
- Companion: `SKILL.md` "Self-driven loops with ScheduleWakeup" section
