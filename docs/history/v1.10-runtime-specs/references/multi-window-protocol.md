---
spec_id: multi-window-protocol.v1
description: Protocol for multiple concurrent terminal windows sharing one vault — outbox claim discipline (no item survives two session starts undecided), per-session commit scope declaration (never repo-wide git add -A on a shared vault), and a cross-window awareness line in the pre-session display. Closes the implicit "one session owns the vault" assumption (issue #3 C2).
status: active
authoritative: true
introduced_in: v1.10.0
referenced_by:
  - agents/retrospective.md (Mode 0 step 7 outbox merge + pre-session display)
  - agents/archiver.md (Phase 4 commit scoping)
  - references/data-model.md (§Constraints, outbox pattern)
---

# Multi-Window Protocol v1

Real usage runs several terminal windows against the same vault concurrently. The outbox pattern (`references/data-model.md` §Constraints) already prevents write conflicts on shared files, but production exposed three failure modes it did not cover: outbox packages sitting unclaimed across multiple session starts ("some other session's business"), cross-window handoffs lost entirely, and one window's commit sweeping another window's in-progress files. This spec closes all three.

## Rule 1 · Outbox claim discipline

At every session start (retrospective Mode 0 step 7), after the normal merge pass:

1. Any outbox directory that was NOT merged this boot (merge-lock held by another window, manifest incomplete, or merge error) is an **unclaimed item**. Record its `<sid>` + age (from the manifest's `adjourned` timestamp, or the directory mtime when the manifest is unreadable).
2. Unclaimed items older than **4 hours** MUST be surfaced in the briefing:

   ```
   📮 Unclaimed outbox: <sid> (age 26h) — adopt (merge now) or archive (move to meta/outbox/.archived/)? [awaiting your decision]
   ```

3. **HARD RULE — no item survives two consecutive session starts without an explicit decision.** Track survivals by appending `seen_by: <this-session-start-date>` lines to the item's manifest. On the second sighting, the briefing escalates the item to `## 4. Today's Focus / decisions needed` — the session does not treat it as "someone else's business" a second time.
4. `adopt` = run the normal merge for that directory now. `archive` = move it to `meta/outbox/.archived/<sid>/` (kept, not deleted — Security Boundary #1). Both outcomes are decisions; skipping is not.

## Rule 2 · Commit scope declaration

1. At session start, each session declares its **write paths** — one line written into `meta/runtime/<sid>/scope.md`:

   ```
   write_scope: [meta/outbox/<sid>/, projects/<bound-project>/, meta/runtime/<sid>/]
   ```

   The default scope is exactly the paths the outbox pattern already implies (own outbox + bound project + own runtime dir); the declaration makes it greppable by other windows.
2. **Commits stage only declared paths.** `git add -A` / `git add .` on a shared vault is FORBIDDEN in session flows (archiver Phase 4, /save, outbox-merge commit). Stage explicit paths: `git add meta/outbox/<sid>/ meta/methods/...`.
   - The one exception: the session-start **outbox merge commit** (retrospective step 7) stages the specific files the merge itself moved — enumerated, not `-A`.
3. A commit that would stage files outside the session's declared scope → stop, list the out-of-scope paths, ask the user. Another window's in-progress work must never ride along in an unrelated commit.

## Rule 3 · Cross-window awareness line

The pre-session display (retrospective Mode 0 / Mode 1 output) includes one line when the working tree contains uncommitted changes outside this session's declared scope:

```
🪟 Other work areas: N uncommitted path groups not in this session's scope (projects/other-proj/, meta/runtime/claude-.../) — not yours, do not stage.
```

Computed mechanically: `git status --porcelain` → strip paths within own `write_scope` → group remainder by top-level dir. Zero remainder → no line (silence on the healthy path).

## What this spec does NOT do

- No locking beyond the existing 5-minute `meta/.merge-lock` — git remains the concurrency backstop.
- No cross-window messaging bus — handoffs go through the outbox (durable), never `git stash` (production evidence: stash/patch handoffs between windows were lost entirely; stash is per-clone working-tree state, invisible to other windows' flows and to sync).
- No change to the Session Binding rule (`hosts/CLAUDE.md`) — discussion scope stays unrestricted; this spec constrains only data writes and staging.

## Eval anchor

`evals/scenarios/v1.10-multi-window.md` — two simulated sessions with overlapping dirty trees → no cross-staging; unclaimed outbox surfaced on first start, forced to decision on second.
