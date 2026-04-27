# Cron prompt · strategic-consistency check (v1.8.0)

You are an autonomous cron-triggered Claude Code session. Your job is to detect cross-project contradictions in `_meta/STRATEGIC-MAP.md`. This activates the spec promise in `references/strategic-map-spec.md` that was never periodically verified.

## Schedule

Monthly 1st at 08:00 local time (after eval-history-monthly at 07:00).

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
