# Cron prompt · eval-history-monthly summary (v1.8.0)

You are an autonomous cron-triggered Claude Code session. Your job is to compile a monthly summary of system performance from `_meta/eval-history/`. This activates the spec promise in `references/eval-history-spec.md` that was never automated.

## Schedule

Monthly 1st at 07:00 local time (after advisor-monthly at 06:00, before strategic-consistency at 08:00).

## Context

`_meta/eval-history/` accumulates per-session evaluation data: AUDITOR scores, REVIEWER decisions, archiver completions, cron runs, etc. The spec promised monthly summaries; this cron delivers them.

## Required actions

This is mostly a python-tool-call prompt. Run `tools/stats.py` with monthly aggregation:

```bash
python -m tools.stats --month-summary --output _meta/eval-history/monthly-summary-{YYYY-MM}.md --root .
```

If `tools/stats.py` does not yet support `--month-summary` flag (v1.8.0 may need to add it):

1. Read `_meta/eval-history/` for the past calendar month.
2. Aggregate into the report below.
3. Write directly to the output path.

## Aggregations to compute

### Sessions
- Total sessions / Average length / Adjourn completion rate / Average outcome_score

### Decisions
- Total decisions / By domain / Express vs full deliberation / Regret rate

### Knowledge growth
- Wiki entries new/deleted / SOUL dimensions changed / Methods created / Concepts new / Hebbian edge updates

### System health
- Cron jobs total runs / successes / failures
- Archiver Phase completion rate
- Cortex audit trail completion rate
- Hook fire counts / Approval guard intercepts
- Compliance index trend

### Costs (if telemetry available)
- Total tokens / By subagent / By cron job

## Output

Write `_meta/eval-history/monthly-summary-{YYYY-MM}.md` with sections: At a glance / Sessions / Decisions / Knowledge growth / System health / Costs / Notable events / Audit trail.

## Notification

Notify only if anomaly detected (X% drop in compliance, archiver fail rate > 20%, etc.):

- Append to `_meta/inbox/notifications.md`: `[{ISO8601}] 📅 Monthly summary ready: {key insight or anomaly} · see _meta/eval-history/monthly-summary-{date}.md`

Otherwise silent (file-only).

## HARD RULES

- **Pure aggregation**. No subjective interpretation; that's ADVISOR's job (advisor-monthly already ran at 06:00).
- **Read-only on session and journal data**.
- **Audit trail**: `_meta/runtime/{sid}/eval-history-monthly.json` (R11)
- **Git push** summary at end
