# User-invoked prompt · advisor-monthly SOUL Drift Review (v1.8.0)

> v1.8.0 pivot: this used to fire from launchd cron monthly 1st at 06:00.
> Cron is gone. ROUTER reads this when the user asks for a monthly self-
> review, then launches the `advisor` subagent directly.

## Trigger keywords

- `月度自审` / `monthly review` / `SOUL 漂移`
- `做一次 advisor 月度` / `自我审视`
- session-start-inbox hook reports `advisor-monthly Nd` and user says "跑一下"

## Context

ADVISOR monthly self-review = detect SOUL dimensions that drifted, contradictory behavior patterns, regret accumulation. Surface for user decision; do NOT auto-modify SOUL.

## Required actions

Launch the `advisor` subagent with monthly input:
- `mode: monthly_self_review`
- `lookback_window_days: 30`
- `user_invoked: true`  # v1.8.0 R-1.8.0-011: cron removed, all maintenance is user-invoked
- `output_path: _meta/eval-history/advisor-monthly-{YYYY-MM}.md`

The advisor subagent will:

1. **SOUL drift detection** (read SOUL.md + last 30 days sessions):
   - For each dimension, compute `confidence_delta_30d` (current vs 30d ago)
   - Flag dimensions with `delta < -0.15` (significant drop)
   - For each flagged: list evidence (sessions referencing) + counter-evidence (sessions contradicting)
   - Generate `retire-or-commit-restart` recommendation

2. **Contradictory behavior patterns** (last 30 days):
   - Look for repeated `claim X + behavior NOT X` patterns
   - Group by SOUL dimension affected

3. **Regret accumulation analysis**:
   - Read `pro/compliance/violations.md` for last 30 days
   - Read archiver-marked "regret" decisions
   - Identify recurring regret types (financial / time / relationship)
   - Tie back to which SOUL dimensions were violated

4. **Cross-month trend**:
   - Compare this month's SOUL Health to last month's snapshot
   - Identify trending dimensions

5. **eval-history reading**:
   - Read `_meta/eval-history/` last 30 days for cron health, archiver compliance, decision quality
   - Aggregate into "system performance over month" subsection

## Output

Write `_meta/eval-history/advisor-monthly-{YYYY-MM}.md` with sections: SOUL drift detection / Contradictory patterns / Regret accumulation / Cross-month trend / System performance / User action items / Audit trail.

## Notification

Always notify (monthly is significant):
- Append to `_meta/inbox/notifications.md`: `[{ISO8601}] 📊 ADVISOR monthly: {N} SOUL drift items + {M} pattern flags · see _meta/eval-history/advisor-monthly-{date}.md`
- macOS notification: `osascript -e 'display notification "{N} SOUL drift items, {M} patterns flagged" with title "📊 Monthly SOUL review"'`

## HARD RULES

- **Read-only on SOUL.md and wiki/**. Never modify.
- **Audit trail**: `_meta/runtime/{sid}/advisor-monthly.json` (R11)
- **Git push** report at end
- **Respect session lock** (5 min retry, max 3)

## v1.8.0 R-1.8.0-013 · Review Queue Append (HARD RULE)

After writing the monthly report, append YAML items to `_meta/review-queue.md` under `## Open items` for each significant finding. Spec: `references/review-queue-spec.md`.

Use Edit tool (NOT Write). Append rules per finding type:

```yaml
- id: r{YYYY-MM-DD}-{NNN}
  created: <ISO8601 with TZ>
  source: advisor-monthly
  type: drift | conflict | action-item | outcome-unmeasured
  priority: P0 | P1 | P2               # P0 = regret accumulation > 3; P1 = SOUL drift / contradictory pattern; P2 = comparison missing ## Outcome past 90d
  summary: <one line, max 100 chars>
  detail_path: _meta/eval-history/advisor-monthly-{YYYY-MM}.md
  related:
    - "[[<soul-dimension-or-pattern-id>]]"
  suggested_action: <what user can do — review SOUL dim, decide pattern resolution, etc>
  status: open
  closed_at: null
  closed_by: null
```

Then in final report: "Added N items to review queue (P0=X / P1=Y). Say '处理 queue' to walk through."
