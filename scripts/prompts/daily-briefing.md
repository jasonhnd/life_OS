# User-invoked prompt · daily-briefing (v1.8.0)

> Replaces the deleted `tools/daily_briefing.py`. ROUTER reads this when the
> user wants a morning briefing.

## Trigger keywords

- `早朝` / `daily briefing` / `今天的简报`
- `给我看今天的状态` / `morning status`
- session-start-inbox hook reports `daily-briefing Nd` and user says "跑一下"

## Goal

Compile a one-page briefing of the second-brain state today, so the user
starts the session knowing what's active, what's pending, what changed.

## Steps

### 1. Gather inputs (Read these in parallel)

```
- SOUL.md                                    → core dimensions + recent updates
- _meta/sessions/INDEX.md (last 5 rows)      → recent sessions
- _meta/snapshots/soul/ (latest snapshot)    → SOUL trajectory
- inbox/*.md                                  → unprocessed items
- projects/*/index.md (status: active)        → active projects
- areas/*/index.md                            → ongoing areas
- _meta/eval-history/recovery/ (last 7 days)  → recent archiver activity
```

### 2. Compose briefing

Write `_meta/eval-history/daily-briefing-{YYYY-MM-DD}.md`:

```markdown
# Daily briefing · {YYYY-MM-DD}

## At a glance
- {N} active projects, {M} inbox items, {K} sessions in last 7d
- SOUL: {top 3 active dimensions with last-update age}

## Active projects
- {project_name} · last touched {age} · {one-line status}
- ...

## Inbox ({N} items)
- {one-line per inbox item}

## SOUL state
- {dimension}: {confidence}, {evidence}/{challenges}, last validated {age}
- ...

## Recent sessions
- {sid} · {title} · score {score}
- ...

## Suggested actions for today
- {derived from inbox + project staleness + SOUL drift signals}
```

### 3. Report to user

```
☀️ daily-briefing ready · _meta/eval-history/daily-briefing-{date}.md
   ({N} active projects · {M} inbox items · {K} suggested actions)
```

## Output path

- `_meta/eval-history/daily-briefing-{YYYY-MM-DD}.md`

## Notes

- This is summarization, not analysis. Don't moralize, don't recommend
  big strategy shifts (that's ADVISOR's job).
- If a section has no data (e.g., empty inbox), write "(none)" not "TBD".
- No git push.
