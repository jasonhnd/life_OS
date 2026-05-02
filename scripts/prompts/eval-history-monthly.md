# User-invoked prompt · eval-history-monthly summary (v1.8.1 · zero-python)

> v1.8.0 pivot: this used to fire from launchd cron monthly 1st at 07:00.
> Cron is gone. v1.8.1 also dropped the `tools/stats.py` middleware —
> ROUTER now reads this prompt and does the aggregation 100% via LLM
> tools (Read/Glob/Grep/Write).

## Trigger keywords

- `统计这个月` / `monthly summary` / `月度统计`
- `eval history` / `系统表现总结`
- session-start-inbox hook reports `eval-history-monthly Nd` and user says "跑一下"

## Context

`_meta/eval-history/` accumulates per-session evaluation data: AUDITOR
scores, REVIEWER decisions, archiver completions, etc. This prompt
aggregates them into a one-file monthly view, doing all the counting
inline via Glob + Read + simple text scan.

## Required actions (100% LLM, no python)

1. Determine the target month: `YYYY-MM` of the previous calendar month
   (or current month if user explicitly says "这个月").
2. `Glob` `_meta/eval-history/**/*.md` and `_meta/journal/**/*.md`
   filtering to the target month by mtime (use `Bash` with `find ...
   -newermt "$YYYY-MM-01" ! -newermt "$YYYY-MM+1-01"` to get the
   filtered file list — this is the ONLY shell call needed).
3. For each file, `Read` the frontmatter and key sections; tally:
   - `outcome_score` values (sum + count for average)
   - `archiver_phase_4_completed: true|false` (completion rate)
   - `auditor_violations:` count by class (A/B/C/D/E)
   - REVIEWER veto count (search "veto" / "封驳" in journal)
   - decision count by domain (frontmatter `domain:`)
4. Also `Glob` `pro/compliance/violations.md` (single file) and `Read`
   it; tally violation rows that fall within the target month.
5. Aggregate into the report below; write directly to output path.

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
