# User-invoked prompt · daily-briefing (v1.8.2 · Obsidian-style)

> Replaces the deleted `tools/daily_briefing.py`. ROUTER reads this when the
> user wants a morning briefing.
>
> **v1.8.2 HARD RULE #11**: Output renders in Obsidian. Apply
> `references/obsidian-style.md` — callouts for semantic blocks, `[[wikilinks]]`
> for in-vault references, nested tags.

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

### 2. Compose briefing (v1.8.2 Obsidian-style)

Write `_meta/eval-history/daily-briefing-{YYYY-MM-DD}.md` per `references/obsidian-style.md`:

```markdown
---
title: "Daily briefing · {YYYY-MM-DD}"
tags: [eval-history/daily-briefing]
created: {YYYY-MM-DD}
---

# Daily briefing · {YYYY-MM-DD}

> [!info] At a glance
> - {N} active projects · {M} inbox items · {K} sessions in last 7d
> - SOUL top 3 active: {dim-1} ({age}) · {dim-2} ({age}) · {dim-3} ({age})

## Active projects

- [[{project-name}]] · last touched {age} · {one-line status}
- [[{project-name}]] · ...

## Inbox ({N} items)

> [!tip] Drop-zone surfacing
> Run `/inbox-process` to triage. Items here haven't been categorized yet.

- {one-line per inbox item}

## SOUL state

- {dimension}: {confidence}, {evidence}/{challenges}, last validated {age}
- ...

## Recent sessions

- [[{sid}]] · {title} · score {score}
- [[{sid}]] · ...

## Suggested actions for today

> [!tip] Derived signals
> Pulled from inbox volume + project staleness + SOUL drift markers. Not commands; just suggestions.

- {action-1}
- {action-2}
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
