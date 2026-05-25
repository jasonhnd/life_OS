---
description: Self-driven version of /verify-release. Runs verify-release every 270s until all checks PASS or hard cap (12 ticks / 60 min) hits. Auto-fixes missing GitHub Release publish if detected. Requires Claude Code (uses ScheduleWakeup).
argument-hint: "[tag-name]  (default: latest tag)"
requires_host: claude-code
allowed-tools:
  - Bash
  - Read
  - Edit
  - ScheduleWakeup
---

# /verify-release-and-watch

Self-driven loop wrapping `/verify-release`. Re-checks every 270s until all 10 release checks PASS, or hits the 12-tick (60 min) hard cap. Use after `git push --tags` to verify the release is fully shipped (not just tagged) without manually rerunning checks.

**Pattern source**: tinyhumansai/openhuman `.claude/commands/ship-and-babysit.md`. **Spec**: `references/self-driven-loops-spec.md`.

## Inputs

- `$ARGUMENTS` (optional) — specific tag name (e.g. `v1.8.7`). If empty, check the latest annotated tag.

## Host check (first action)

If host is NOT Claude Code:

```
⚠️ /verify-release-and-watch requires Claude Code (uses ScheduleWakeup for self-driven loops).
   You're on <host>. Run /verify-release manually instead (re-run every few minutes until green).
```

Then STOP. Do not proceed.

## Loop body (one tick)

### Step 1 · Extract or initialize tickCount

If invoked via ScheduleWakeup, the previous `reason` contains `tick N/12: ...`. Extract N. Set `tickCount = N + 1`.

If this is the first invocation (no prior tick marker), set `tickCount = 1`.

### Step 2 · Run /verify-release checks

Inline-execute the same procedure as `.claude/commands/verify-release.md`. Run all 10 checks:

1. Working tree clean (`git status --short`)
2. HEAD == origin/main
3. Determine target tag
4. Tag exists locally + pushed to remote
5. GitHub Release exists for the tag
6. Release is not Draft
7. Release marked as Latest
8. No forbidden file extensions in repo (md-only check #8)
9. **NEW v1.8.7**: i18n diff parity (changed references/*.md sections mirrored in i18n/zh + i18n/ja)
10. **NEW v1.8.7**: diff-scoped forbidden extensions (no `.sql / .json / .sh / .bash / .py / .yml / .yaml / .db / .sqlite` in commit diff since last tag)

Collect results: which checks PASS, which FAIL, which WARN.

### Step 3 · Auto-fix paths

For these specific FAIL types, attempt auto-fix before next tick:

| FAIL | Auto-fix action |
|------|-----------------|
| GitHub Release does NOT exist for tag | Run `gh release create <tag> --title "..." --notes-file _meta/release-notes/<tag>.md --latest` |
| Release exists but is Draft | Run `gh release edit <tag> --draft=false` |
| Release not marked as Latest | Run `gh release edit <tag> --latest` |

After auto-fix, re-run the failed check immediately (do not wait for next tick) to confirm fixed.

For other FAIL types (working tree dirty, HEAD != origin/main, missing tag, forbidden extensions): do NOT auto-fix — these require human judgment. Record the FAIL in the tick output and continue to Step 4.

### Step 4 · Decide exit / continue / hard-cap

| Condition | Action |
|-----------|--------|
| All 10 checks PASS (after any auto-fixes) | **EXIT** — output final summary with Release URL, STOP (do NOT call ScheduleWakeup) |
| tickCount ≥ 12 | **EXIT with status snapshot** — list all current FAIL/WARN, ask user how to proceed, STOP |
| Any FAIL that auto-fix couldn't resolve | Continue to next tick (maybe CI is mid-run, maybe Release is propagating CDN) |
| Only WARN-level findings, no FAIL | Same as PASS → EXIT (WARN doesn't block) |

### Step 5 · Output tick result

Always output one short line for the user this tick:

```
🔄 tick N/12 — checks: ✅PASS=X / ⚠️WARN=Y / ❌FAIL=Z. <one-line about what's pending>
```

If FAIL count > 0 and auto-fix attempted, mention the auto-fix:

```
🔄 tick N/12 — checks: ✅PASS=8 / ❌FAIL=2. Auto-fixed: GitHub Release publish. Re-checking next tick.
```

### Step 6 · Audit trail (per tick)

Write `_meta/runtime/<sid>/verify-release-and-watch-tick-<N>.md` with frontmatter:

```yaml
---
command: verify-release-and-watch
tick: <N>
total_ticks_cap: 12
tag_checked: <tag>
started_at: <iso>
ended_at: <iso>
checks_pass: <count>
checks_warn: <count>
checks_fail: <count>
auto_fixes_applied: [<list>]
next_action: continue|exit|hard_cap_exit
---
```

### Step 7 · Pacing

If EXIT (all PASS or hard cap):
- Do NOT call ScheduleWakeup
- Output final summary:

```
✅ Release v<X.Y.Z> fully shipped after N ticks.
   URL: <release-url>
   All 10 checks PASS.
```

Or for hard-cap exit:

```
⚠️ /verify-release-and-watch hit 12-tick cap (60 min) without all checks passing.
   Current FAIL: <list>
   Current WARN: <list>
   Release URL (if exists): <url>
   Decide: rerun manually / abandon / escalate?
```

If CONTINUE:
- Call ScheduleWakeup:
  ```
  ScheduleWakeup({
    delaySeconds: 270,
    prompt: "/verify-release-and-watch <tag>",
    reason: "tick <N+1>/12: <what's pending, e.g. 'waiting for GitHub Release CDN propagation'>"
  })
  ```

## Exit conditions (enumerated)

1. **All 10 checks PASS** → exit with success summary + Release URL
2. **All FAIL resolved by auto-fix, only WARN left** → exit (WARN is informational not blocking in v1.8.7)
3. **tickCount ≥ 12** → exit with status snapshot, ask user
4. **Critical error** (e.g. tag doesn't exist, repo not git, gh CLI not auth'd) → exit with error
5. **User-cancel** (Ctrl-C / abort) → not applicable — ScheduleWakeup honors session interrupts

## Failure handling

- **gh CLI not authenticated** → exit immediately with `gh auth login` instructions
- **Network failure during auto-fix** → record in audit trail, retry next tick (not immediate retry)
- **Repo working tree becomes dirty mid-loop** (user edited files) → exit with notice; user should `git stash` and rerun

## Reference

- Base command: `.claude/commands/verify-release.md` (the 10 individual checks)
- Spec: `references/self-driven-loops-spec.md`
- RFC: `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.2 B4
- Pattern: `tinyhumansai/openhuman` `.claude/commands/ship-and-babysit.md`
