# Async Review Queue Spec (v1.8.0 R-1.8.0-013)

> Borrowed from llm_wiki async review pattern. Single source of truth for
> "things that need user attention." Replaces the scattered notifications.md
> + violations.md + per-report action items as the **unified entry point**.

## Why

Before R-1.8.0-013, "things needing user attention" lived in 7 places:

| Source | File |
|---|---|
| AUDITOR Mode 2 patrol | `_meta/eval-history/auditor-patrol/<date>.md` action items |
| ADVISOR monthly | `_meta/eval-history/advisor-monthly-<month>.md` SOUL drift |
| Strategic Consistency | `_meta/eval-history/strategic-consistency-<month>.md` conflicts |
| Archiver recovery | `_meta/eval-history/recovery/<date>.md` results |
| AUDITOR Mode 3 violations | `pro/compliance/violations.md` |
| Cron notifications (deleted) | `_meta/inbox/notifications.md` |
| Summary Reports | scattered in session files |

User had to integrate 7 sources mentally. Review queue consolidates all into
one ordered, actionable list.

## File path

```
_meta/review-queue.md         (active queue, append + in-place status update)
_meta/review-queue/archive/   (resolved items archived monthly)
```

## Item schema

YAML list inside the markdown file. Each item:

```yaml
- id: r2026-04-29-001                 # r{YYYY-MM-DD}-{NNN sequence within day}
  created: 2026-04-29T09:00:00+09:00  # ISO8601 with TZ
  source: auditor-patrol              # auditor-patrol|advisor-monthly|strategic-consistency|archiver-recovery|eval-history-monthly|router|user
  type: stale-wiki                    # stale-wiki|drift|conflict|violation|action-item|decision-due|outcome-unmeasured|other
  priority: P1                        # P0 (urgent) | P1 (this week) | P2 (whenever)
  summary: "wiki entry X 90+ 天没更新且 confidence < 0.4"  # one-line, max 100 chars
  detail_path: _meta/eval-history/auditor-patrol/2026-04-29.md  # full report or null
  related:                            # Obsidian wikilinks to related pages
    - "[[concept-foo]]"
    - "[[wiki-bar]]"
  suggested_action: "review and decide keep / delete / re-validate"
  status: open                        # open | reviewed | resolved | dismissed
  closed_at: null                     # ISO8601 when status != open, else null
  closed_by: null                     # user-resolved | auto-archived | superseded
```

## File layout

```markdown
# Life OS · Async Review Queue (v1.8.0 R-1.8.0-013)

## Open items

- id: r2026-04-29-001
  created: ...
  source: auditor-patrol
  ...
  status: open

- id: r2026-04-29-002
  ...
  status: open

## Recently resolved (last 30 days)

- id: r2026-04-15-003
  ...
  status: resolved
  closed_at: 2026-04-29T10:00:00+09:00
  closed_by: user-resolved
```

When `## Recently resolved` exceeds 100 entries, the oldest are moved to
`_meta/review-queue/archive/{YYYY-MM}.md` (append-only monthly file).

## Sources — what each appends

### auditor-patrol (weekly via user invocation)
Appends one item per `Critical (need user decision)` finding. priority by severity:
- P0 = data corruption / security violation
- P1 = stale wiki / orphan link
- P2 = nice-to-have improvement

### advisor-monthly (monthly via user invocation)
Appends one item per:
- SOUL drift detected → priority P1, type `drift`
- Contradictory pattern flagged → P1, type `conflict`
- Regret accumulation > 3 → P0, type `action-item`

### strategic-consistency (monthly via user invocation)
Appends per project conflict found:
- HIGH severity → P0
- MEDIUM → P1
- LOW → P2

### archiver-recovery (when invoked)
Appends if recovery found data inconsistencies (rare):
- Missing audit trail → P1
- Phase failed → P0

### eval-history-monthly (monthly via user invocation)
Appends ONLY anomalies (not regular metrics):
- Compliance drop > 20% → P0
- Archiver fail rate > 20% → P1

### router (real-time during sessions)
Appends per Summary Report action item with explicit deadline:
- type: `decision-due`
- priority based on deadline urgency

### user (manual)
User can manually append via `scripts/prompts/review-queue.md` "add item" flow.

## Append rules (HARD RULE for prompts)

When a maintenance prompt finds an action item:

1. Read current `_meta/review-queue.md`
2. Find the highest existing `r{TODAY}-{N}` id, increment N (start at 001 if no items today)
3. Construct new item per schema
4. Append to `## Open items` section (Edit tool, before "## Recently resolved")
5. Report to user: "Added N items to review queue (priority: P0=X / P1=Y / P2=Z)"

DO NOT use Write tool (would overwrite). Use Edit with append pattern.

### Id zero-padding rule

**`{NNN}` is ALWAYS zero-padded to 3 digits** (`001`, `002`, ..., `099`,
`100`, `101`, ...). This makes ids sort lexicographically the same as
numerically. Do NOT use natural integers (`1`, `2`, `10`, `11` would sort as
`1, 10, 11, 2`).

Beyond 999 items in a single day (vanishingly unlikely), use 4 digits:
`r2026-04-29-1000`. Documented but never expected to fire.

### Concurrency / lock-free append protocol

Multiple prompts may try to append simultaneously (e.g., user manually
invokes `auditor-mode-2` while `advisor-monthly` is mid-run from earlier).
Without locking, two appends in parallel could:
- collide on id (both compute `r2026-04-29-007` independently)
- one Edit overwrite the other's change

**Mitigation (lock-free, optimistic):**

1. Each appender re-reads `_meta/review-queue.md` IMMEDIATELY before
   constructing its Edit (not 30 seconds before).
2. Compute next id from re-read content.
3. After Edit, re-read to verify the new id appears exactly once. If it
   appears twice (collision), DELETE the duplicate (keep first writer's
   item, discard second writer's), then re-attempt with id+1.
4. If verify-and-retry fails 3 times, abort with `_meta/review-queue/lock-conflicts/{ISO}.md`
   recording the conflict for user inspection.

**Note**: lifeos is single-user single-session today, so collisions are
theoretical. Documenting protocol for future multi-process cron resurrection.

### Archive ordering source-of-truth

When `## Recently resolved` exceeds 100 entries, oldest items move to
`_meta/review-queue/archive/{YYYY-MM}.md` where `{YYYY-MM}` is parsed from
each item's `closed_at` field (NOT `created` — items can sit open for
months). Within the monthly archive file, items are appended in
**`closed_at` ASC order** (oldest first). Items with null `closed_at` are
never archived (they're still open and should not be in `## Recently
resolved` anyway — that's a data inconsistency to flag).

## Status transitions

```
open → reviewed       # user looked at it, didn't act yet
open → resolved       # user took action (deleted wiki / updated SOUL / etc)
open → dismissed      # user explicitly said "don't track this"
reviewed → resolved
reviewed → dismissed
```

**Status transitions are MONOTONE / one-way** (DAG, no back-edges):
- `dismissed → open` is INVALID — dismissed items stay dismissed
- `resolved → open` is INVALID — re-opening means creating a new queue item
  with `related: ["[[r-id-of-resolved-item]]"]` referencing the prior one
- `reviewed → open` is INVALID — same reasoning

A walker prompt that detects an attempted back-transition MUST refuse and
log to `_meta/runtime/{sid}/review-queue-walk.json`. Out-of-band YAML edits
(user manually edits `_meta/review-queue.md` to re-open) are tolerated but
flagged at next walker run.

When status changes from `open`:
- Set `closed_at` to current ISO8601 (REQUIRED non-null when status != open)
- Set `closed_by` to who/how (REQUIRED non-null when status != open):
  `user-resolved` | `auto-archived` | `superseded` | `auto-dismissed-stale`
- Move from `## Open items` to `## Recently resolved` section

**Required-field invariant**: items with `status: open` MUST have
`closed_at: null` and `closed_by: null`. Items with status != open MUST
have both non-null. A validator (planned, not yet implemented) MUST flag
items violating this.

## Hook integration

`scripts/hooks/session-start-inbox.sh`:
- Reads first 50 lines under `## Open items`
- Counts by priority
- Outputs `<system-reminder>` like:
  ```
  📋 Review queue: 3 P0 / 5 P1 / 2 P2 open. Latest: <summary of newest>.
     Say "看 queue" / "处理 queue" to walk through.
  ```

## Monitor mode integration

`pro/agents/monitor.md` dashboard shows full queue grouped by:
- Priority (P0 first)
- Source (group by maintenance task)
- Age (oldest first within priority)

## "处理 queue" flow

User says "处理 queue" / "看 queue" / "review queue" → ROUTER reads
`scripts/prompts/review-queue.md` and walks user through each open item:
1. Show item summary + detail_path content (Read)
2. Ask: "(A) act / (R) reviewed-no-act / (D) dismiss / (S) skip"
3. Update status accordingly
4. Move to next

User can quit anytime; partial walk-through saves progress (status
transitions are persistent).

## Anti-patterns

- DON'T append items for things that are FYI (not actionable). FYI goes
  in `_meta/eval-history/` reports only.
- DON'T let queue grow past ~100 open items — that means the system is
  surfacing too much. ADVISOR-monthly should flag this.
- DON'T archive resolved items < 30 days old — user may want to review
  recent decisions.
- DON'T use IDs from outside the `r{YYYY-MM-DD}-{NNN}` namespace.
