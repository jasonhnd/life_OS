# User-invoked prompt · archiver-recovery (v1.8.0)

> v1.8.0 pivot: this used to fire from launchd cron daily 23:30. Cron is gone.
> ROUTER reads this when the user says they missed an adjourn, then performs
> the recovery directly using Read/Write/Bash tools and Task subagents.

## Trigger keywords

- `补救退朝` / `漏 adjourn` / `forgot to adjourn`
- `昨天没退朝` / `archiver 没跑`
- session-start-inbox hook reports `archiver missed {date}` and user says "补一下"

## Context

The user may have:
- (a) Properly said "退朝" / "adjourn" today → no recovery needed; tell user
  and exit.
- (b) Forgotten to say adjourn → no archiver Phase 1-4 ran → recovery needed.
- (c) Said adjourn but archiver failed (CLASS_C violation in
  `pro/compliance/violations.md`) → recovery needed.

## Required actions (in order)

1. **Detect today's adjourn state**:
   - Find archiver-phase-4.json files modified today across `_meta/runtime/`
   - Check today's CLASS_C archiver violations in `pro/compliance/violations.md`

2. **Decision matrix**:
   - Found complete adjourn AND no violations → **silent skip**, write to `_meta/eval-history/cron-runs/archiver-recovery-{date}.log` "no recovery needed", exit 0.
   - No successful adjourn today OR CLASS_C violation present → **proceed to recovery**.

3. **Recovery execution**:
   - Find the most recent session that has `archiver-phase-1.json` but missing 2/3/4: this is the incomplete adjourn to recover.
   - If no incomplete session exists, create a new SID: `cron-recovery-{YYYYMMDD-HHMM}`.
   - Reconstruct context: read latest entries in `_meta/sessions/INDEX.md`, `SOUL.md`, `_meta/journal/`.
   - Launch `knowledge-extractor` subagent (Phase 2 carve-out per pro/agents/knowledge-extractor.md).
   - Wait for YAML output.
   - Launch `archiver` subagent (Phase 1 archive + Phase 3 DREAM + Phase 4 sync; Phase 2 reads knowledge-extractor reports).
   - Wait for completion checklist.

4. **Logging**:
   - Write recovery report to `_meta/eval-history/recovery/{YYYY-MM-DD-HHMM}.md` with: trigger reason, recovered SID, Phase 2 extraction summary, Phase 3 DREAM summary, Phase 4 git push status, total tokens used.
   - Append to `_meta/inbox/notifications.md`: `[{ISO8601}] 🌆 archiver-recovery: auto-recovered SID {sid}, see _meta/eval-history/recovery/{file}.md`

5. **macOS notification** (if osascript available):
   `osascript -e 'display notification "Recovered missed adjourn for {sid}" with title "🌆 Life OS · auto-archive"' 2>/dev/null || true`

## Exit conditions

- Success (recovery complete or silent skip) → exit 0
- Failure (knowledge-extractor or archiver subagent fail) → write failure to `_meta/eval-history/cron-runs/archiver-recovery-{date}-FAIL.md` + macOS notification → exit 1

## HARD RULES

- **Never run business deliberation** (PLANNER / REVIEWER / 6 Domains / COUNCIL / STRATEGIST). This is recovery only.
- **Never modify SOUL.md outside knowledge-extractor's auto-write** (no manual SOUL edits).
- **Never delete files**. Only append + git commit.
- **Always git pull --rebase before starting**. Always git push at end. Conflict → abort + log.
- **Respect session lock**: if `~/.claude/lifeos-active-session.lock` exists, sleep 5 min retry, max 3 times.

## v1.8.0 R-1.8.0-013 · Review Queue Append (HARD RULE)

Recovery normally completes silently if no issues. ONLY append review-queue items if recovery surfaced data inconsistencies that need user attention. Spec: `references/review-queue-spec.md`.

Use Edit tool (NOT Write). Pattern per issue:

```yaml
- id: r{YYYY-MM-DD}-{NNN}
  created: <ISO8601 with TZ>
  source: archiver-recovery
  type: violation | action-item
  priority: P0 | P1                    # P0 = phase failed / data corruption; P1 = missing audit trail / minor inconsistency
  summary: <one line, max 100 chars>
  detail_path: _meta/eval-history/recovery/{YYYY-MM-DD-HHMM}.md
  related:
    - "[[<sid-of-failed-session>]]"
  suggested_action: <re-run X / inspect Y / etc>
  status: open
  closed_at: null
  closed_by: null
```

If recovery silent (no issues), DO NOT append anything. Then in final report: "Recovery clean — no review queue additions" OR "Added N items to review queue (P0=X / P1=Y). Say '处理 queue' to walk through."
