---
spec_id: maintenance-ledger-spec.v1
description: Format and protocol for meta/maintenance-ledger.md — the single vault file recording when each maintenance job last ran. Every scripts/prompts/*.md job stamps it on completion; session start compares stamps against declared cadences and surfaces at most 3 overdue lines (nudge-only, never auto-run). Closes the "cadence rules exist on paper, drift compounds silently" gap (issue #1 A2).
status: active
authoritative: true
introduced_in: v1.10.0
referenced_by:
  - agents/retrospective.md (Step 0.5 maintenance-overdue marker + Mode 2 item 7)
  - hosts/CLAUDE.md (§session-start status scan)
  - scripts/prompts/*.md (final "ledger stamp" step in every job)
---

# Maintenance Ledger Specification v1

Since the v1.8.0 pivot removed cron, all maintenance is user-invoked. Nothing recorded when a job last ran, and nothing nudged when one was overdue — production evidence: a ">4h → light patrol" rule coexisted with 7+ day gaps, a monthly deep patrol ran ~13 days late, and wiki index drift reached +60 entries before a patrol caught it. This spec makes staleness **visible at the one moment a human is guaranteed present — session start** — without resurrecting cron or violating the v1.8.0 "no self-driving maintenance" stance.

## File format

One file per vault: `meta/maintenance-ledger.md`. A single markdown table, one row per job, sorted alphabetically by job name:

```markdown
# Maintenance Ledger

Stamped by each `scripts/prompts/<job>.md` on completion. Read by session start
(retrospective Step 0.5). Cadences per `references/maintenance-ledger-spec.md`.

| job | cadence | last_run |
|-----|---------|----------|
| auditor-mode-2 | 7d | 2026-07-01 |
| backup | 7d | 2026-06-28 |
| wiki-link-audit | 7d | 2026-06-20 |
```

Field rules:

- **job** — the prompt's basename without `.md` (e.g. `wiki-link-audit`).
- **cadence** — one of `<N>d` (day-valued), `on-demand`, or `once`. Each job's prompt declares the cadence it stamps; the ledger row copies it so overdue math needs only this one file.
- **last_run** — `YYYY-MM-DD` from a real `date` command (no fabrication — same contract as SOUL snapshots).

## Stamping protocol (every job, final step)

Every `scripts/prompts/*.md` job ends with a ledger stamp step:

1. Read `meta/maintenance-ledger.md`. If missing, create it with the header above and zero rows.
2. **Upsert own row** — if a row for this job exists, replace it in place; otherwise insert keeping alphabetical order. Never duplicate a job's row.
3. Write `| <job> | <cadence> | <today> |`.

The stamp is idempotent and costs one Read + one Write. Jobs with `cadence: once` or `on-demand` still stamp — their rows document that the job ran, they just never go overdue.

## Session-start overdue check (nudge-only)

At session start (retrospective Mode 0 Step 0.5; also Mode 2 Review item 7):

1. Read `meta/maintenance-ledger.md`. Missing file → emit `Maintenance ledger: not yet initialized (jobs stamp it on completion)` and skip — do NOT create it at read time.
2. For each row with day-valued cadence `<N>d`: `days_overdue = (today - last_run) - N`. Rows with `on-demand` / `once` cadence are never overdue.
3. If any `days_overdue > 0`: emit an `## Overdue maintenance` block of **at most 3 lines** (HARD CAP), sorted by overdue ratio `(today - last_run) / N` descending:

   ```
   ⚠️ overdue: wiki-link-audit (12d since last run, cadence 7d)
   ⚠️ overdue: auditor-mode-2 (9d since last run, cadence 7d)
   (+2 more — see meta/maintenance-ledger.md)
   ```

   When more than 3 jobs are overdue, the 3rd line is the `(+N more …)` rollup.
4. If nothing is overdue: **silence** (no block, no "all fresh" line — zero noise on the healthy path).

**Overdue = nudge only. NEVER auto-run a maintenance job from the overdue check.** The user decides what to invoke. Auto-execution would reintroduce exactly the self-driving maintenance the v1.8.0 pivot removed.

## Relationship to the pre-v1.10 mechanism

Pre-v1.10, retrospective Step 0.5 read "the 10 maintenance job last-run timestamps from their stored locations" — i.e. each job's report path (e.g. `meta/eval-history/wiki-link-audit-*.md` mtimes), which only covered jobs that happen to write dated reports and required N globs per boot. The ledger replaces that: **one file, one Read, write-time maintained** — the same write-time-over-scan-time move as the v1.9.2 session INDEX change. The old per-job report paths remain as evidence but are no longer the overdue-check source of truth.

## Eval anchor

`evals/scenarios/v1.10-maintenance-ledger.md` — stale ledger → nudge block appears (≤3 lines); fresh ledger → no block emitted.
