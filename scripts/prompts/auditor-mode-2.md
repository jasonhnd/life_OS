# User-invoked prompt · auditor-mode-2 Patrol Inspection (v1.8.0)

> v1.8.0 pivot: this used to fire from launchd cron weekly Sunday 21:00. Cron
> is gone. ROUTER reads this when the user asks for a jurisdiction patrol,
> then launches the `auditor` subagent directly.

## Trigger keywords

- `巡检` / `patrol` / `auditor 巡检`
- `检查 jurisdiction` / `健康检查 wiki/SOUL/methods`
- session-start-inbox hook reports `auditor-patrol Nd` and user says "跑一下"

## Context

AUDITOR Mode 2 = jurisdiction health check. Inspect system state, surface
action items, do NOT auto-fix (user must approve).

## Required actions

Launch the `auditor` subagent with Mode 2 input. Pass:
- `mode: 2_patrol`
- `jurisdiction_targets: [wiki/, SOUL.md, _meta/methods/, _meta/sessions/, _meta/concepts/]`
- `cron_triggered: true`
- `output_dir: _meta/eval-history/auditor-patrol/{YYYY-MM-DD}.md`

The auditor subagent will:

1. **wiki/ health check**:
   - Find entries with `confidence < 0.3` AND no update in 90+ days → flag as `stale`
   - Find broken concept links (referenced concept file missing) → flag as `broken-link`
   - Find duplicate entries (same slug or near-duplicate body) → flag as `duplicate`

2. **SOUL.md health check**:
   - Dimensions where `challenges >= evidence` → flag as `challenge-dominant`
   - Dimensions with `confidence < 0.3` AND no validation in 90+ days → flag as `stale-low-confidence`
   - Dimensions never referenced in any session in 60+ days → flag as `unused`

3. **_meta/methods/ health check**:
   - Tentative methods with `evidence_count > 5` AND `challenges < 2` → flag as `promotion-candidate`
   - Confirmed methods with `challenges >= evidence` → flag as `re-evaluation-candidate`
   - Methods never used in 90+ days → flag as `dormant`

4. **_meta/sessions/INDEX.md integrity**:
   - Entries pointing to missing session files → flag as `broken-pointer`
   - Sessions with `outcome_score: null` (incomplete archiver) older than 7 days → flag as `pending-completion`

5. **_meta/concepts/ Hebbian decay**:
   - Concepts with weight decay below threshold not pruned → flag as `decay-candidate`
   - Concepts never co-activated in 60+ days → flag as `cold`

## Output

Write `_meta/eval-history/auditor-patrol/{YYYY-MM-DD}.md`:

```markdown
# AUDITOR Mode 2 Patrol · {YYYY-MM-DD}

## Summary
- Total flags: N
- Critical (need user decision): M
- Auto-fixable (deferred to next cron): K

## wiki/ ({N} entries scanned)
- {N} stale, {M} broken-link, {K} duplicate
- Action items list (each with file path + recommendation)

## SOUL.md ({N} dimensions scanned)
- {N} challenge-dominant, {M} stale-low-confidence, {K} unused
- Action items list

## _meta/methods/ ({N} methods scanned)
[...]

## _meta/sessions/INDEX.md
[...]

## _meta/concepts/
[...]

## Recommended actions for user
1. Review {wiki entries} → /method create or delete (manual)
2. Decide on {SOUL dimensions} → retire or commit-restart
3. Promote {method candidates} → /method update --status confirmed

## Audit trail
- _meta/runtime/{sid}/auditor-mode-2.json (R11 HARD RULE)
```

## Notification

If `Critical (need user decision) > 0`:
- Append to `_meta/inbox/notifications.md`: `[{ISO8601}] 🔱 AUDITOR Patrol: {N} action items need your review · see _meta/eval-history/auditor-patrol/{date}.md`
- macOS notification: `osascript -e 'display notification "{N} jurisdiction items need review" with title "🔱 AUDITOR weekly patrol"' 2>/dev/null`

If `Critical == 0`: silent (write report file, no notification).

## HARD RULES

- **Read-only on jurisdiction targets**. Auditor never modifies wiki/, SOUL.md, methods, concepts.
- **Audit trail**: write `_meta/runtime/{sid}/auditor-mode-2.json` (R11 HARD RULE).
- **Git push** the patrol report at end.
- **Respect session lock** (5 min retry, max 3).

## v1.8.0 R-1.8.0-013 · Review Queue Append (HARD RULE)

After writing the patrol report, for EACH `Critical (need user decision)` finding, append a YAML item to `_meta/review-queue.md` under `## Open items`. Spec: `references/review-queue-spec.md`.

Use Edit tool (NOT Write — would overwrite). Pattern:

```yaml
- id: r{YYYY-MM-DD}-{NNN}            # NNN = next sequence within today; read existing queue to find max+1
  created: <ISO8601 with TZ>
  source: auditor-patrol
  type: stale-wiki | drift | violation | action-item | other
  priority: P0 | P1 | P2              # P0=data corruption/security; P1=stale wiki/orphan; P2=nice-to-have
  summary: <one line, max 100 chars>
  detail_path: _meta/eval-history/auditor-patrol/{YYYY-MM-DD}.md
  related:
    - "[[<concept-or-wiki-id>]]"
  suggested_action: <what user can do>
  status: open
  closed_at: null
  closed_by: null
```

Then in your final report to user, mention: "Added N items to review queue (P0=X / P1=Y / P2=Z). Say '处理 queue' to walk through."
