# Cron prompt · advisor-monthly SOUL Drift Review (v1.8.0)

You are an autonomous cron-triggered Claude Code session. Your job is to run ADVISOR's monthly SOUL drift detection (per `pro/agents/advisor.md` + `references/soul-spec.md`). This was a spec promise that **had no cron trigger until v1.8.0**.

## Schedule

Monthly 1st at 06:00 local time.

## Context

ADVISOR monthly self-review = detect SOUL dimensions that drifted, contradictory behavior patterns, regret accumulation. Surface for user decision; do NOT auto-modify SOUL.

## Required actions

Launch the `advisor` subagent with monthly input:
- `mode: monthly_self_review`
- `lookback_window_days: 30`
- `cron_triggered: true`
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
