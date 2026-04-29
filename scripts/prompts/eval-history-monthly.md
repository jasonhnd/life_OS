# User-invoked prompt · eval-history-monthly summary (v1.8.0)

> v1.8.0 pivot: this used to fire from launchd cron monthly 1st at 07:00.
> Cron is gone. ROUTER reads this when the user asks for a monthly system
> performance summary, then runs the aggregation directly.

## Trigger keywords

- `统计这个月` / `monthly summary` / `月度统计`
- `eval history` / `系统表现总结`
- session-start-inbox hook reports `monthly-summary Nd` and user says "跑一下"

## Context

`_meta/eval-history/` accumulates per-session evaluation data: AUDITOR scores, REVIEWER decisions, archiver completions, cron runs, etc. This prompt aggregates them into a one-file monthly view.

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

## v1.8.0 R-1.8.0-013 · Review Queue Append (HARD RULE)

Append review-queue items ONLY when monthly summary surfaces ANOMALIES (not regular metrics). Spec: `references/review-queue-spec.md`.

Anomaly thresholds:
- Compliance index drop > 20% MoM → P0
- Archiver fail rate > 20% → P1
- Session count drop > 50% MoM → P1
- Decision count zero (user not deciding anything) → P2

Use Edit tool (NOT Write). Pattern per anomaly:

```yaml
- id: r{YYYY-MM-DD}-{NNN}
  created: <ISO8601 with TZ>
  source: eval-history-monthly
  type: action-item | violation
  priority: P0 | P1 | P2
  summary: <one line — what anomaly, by how much>
  detail_path: _meta/eval-history/monthly-summary-{YYYY-MM}.md
  related: []
  suggested_action: <investigate cause, restore baseline, etc>
  status: open
  closed_at: null
  closed_by: null
```

If no anomalies (regular month), DO NOT append. Then in final report: "Monthly summary clean — no anomalies, no queue additions" OR "Added N anomaly items to review queue. Say '处理 queue' to walk through."
