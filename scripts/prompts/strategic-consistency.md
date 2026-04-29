# User-invoked prompt · strategic-consistency check (v1.8.0)

> v1.8.0 pivot: this used to fire from launchd cron monthly 1st at 08:00.
> Cron is gone. ROUTER reads this when the user asks for a strategic
> consistency check, then performs the analysis directly.

## Trigger keywords

- `检查项目冲突` / `strategic consistency` / `战略一致性`
- `项目矛盾` / `跨项目检查`
- session-start-inbox hook reports `strategic-consistency Nd` and user says "跑一下"

## Context

Users pursue multiple projects/goals simultaneously. STRATEGIC-MAP tracks them. Conflicts arise:
- Resource conflict (time, money, attention)
- Value conflict (project A's goal contradicts project B's value)
- Sequencing conflict (X requires Y first, but Y blocked by Z)
- Identity conflict (project drifts from user's SOUL)

This cron surfaces them for user review.

## Required actions

Read these files:
1. `_meta/STRATEGIC-MAP.md` (the strategic relationships layer)
2. `SOUL.md` (current dimensions and confidence)
3. `_meta/sessions/INDEX.md` last 90 days (recent project activity)
4. `wiki/` entries tagged with project IDs

Run cross-project analysis:

### 1. Resource conflict detection
For each project in STRATEGIC-MAP:
- Estimated weekly hour commitment (from session frequency in last 90d)
- Sum of all projects' commitments
- If sum > 168 - sleep(56) - work(40) - meta(10) = 62 weekly hours available → flag overload

### 2. Value conflict detection
For each pair of active projects (active = touched in last 30d):
- Identify primary SOUL dimension served
- Check if dimensions contradict
- Flag explicit conflicts found in past sessions

### 3. Sequencing conflict
- Identify project dependencies
- Check if blockers were addressed (project B had progress in last 30d)
- Flag stalled chains

### 4. Identity drift
For each project:
- Compare current direction (from recent sessions) vs SOUL.md primary dimensions
- If divergence > threshold → flag drift candidate
- Recommend: realign / spinoff / retire

## Output

Write `_meta/eval-history/strategic-consistency-{YYYY-MM}.md` with sections: Active projects / Resource conflicts / Value conflicts / Sequencing conflicts / Identity drift / User action items / Audit trail.

## Notification

Notify if any critical flag:
- Append to `_meta/inbox/notifications.md`: `[{ISO8601}] 🗺️ Strategic consistency: {N} conflicts need resolution · see _meta/eval-history/strategic-consistency-{date}.md`

If 0 critical flags: silent (file-only).

## HARD RULES

- **Read-only on STRATEGIC-MAP, SOUL, wiki/, sessions/**.
- **Audit trail**: `_meta/runtime/{sid}/strategic-consistency.json` (R11)
- **Git push** report at end

## v1.8.0 R-1.8.0-013 · Review Queue Append (HARD RULE)

After writing the report, append a YAML item to `_meta/review-queue.md` under `## Open items` for EACH project conflict found. Spec: `references/review-queue-spec.md`.

Use Edit tool (NOT Write). Pattern per conflict:

```yaml
- id: r{YYYY-MM-DD}-{NNN}
  created: <ISO8601 with TZ>
  source: strategic-consistency
  type: conflict
  priority: P0 | P1 | P2                # HIGH=P0 / MEDIUM=P1 / LOW=P2
  summary: <one line, max 100 chars>
  detail_path: _meta/eval-history/strategic-consistency-{YYYY-MM}.md
  related:
    - "[[<project-id-1>]]"
    - "[[<project-id-2>]]"
  suggested_action: <which project to deprioritize / merge / kill / etc>
  status: open
  closed_at: null
  closed_by: null
```

Then in final report: "Added N items to review queue (P0=X / P1=Y / P2=Z). Say '处理 queue' to walk through."
