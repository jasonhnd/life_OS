# Life OS Compliance Violations Log · Dev Repo

> Append-only log of HARD RULE violations detected by hooks, AUDITOR Compliance Patrol, and eval scenarios. Format defined in `references/compliance-spec.md`. Rolling 90-day window; older entries archived to `pro/compliance/archive/YYYY-QN.md`.

## Format

```
| Timestamp (ISO 8601) | Trigger | Type | Severity | Details | Resolved |
```

## Violations

| Timestamp | Trigger | Type | Severity | Details | Resolved |
|-----------|---------|------|----------|---------|----------|
| 2026-04-19T22:47+09:00 | 上朝 | A1 | P0 | ROUTER simulated 18 steps in main context, skipped retrospective subagent launch. Evidence: main-context output contained "执行轻量巡检" + Bash/Read/Glob calls before any Task() invocation. | partial (v1.6.3 shipped · L2+L3 production-verified 2026-04-21 in user repo · awaiting eval regression + 30d obs) |
| 2026-04-19T22:52+09:00 | 上朝 | B | P0 | Referenced non-existent `_meta/roles/CLAUDE.md § 0 Pre-Court Preparation` as authority source. Verified: `ls _meta/roles/` returns "No such file or directory". | partial (v1.6.3 hook + AUDITOR Compliance Patrol block this · L2 production-verified 2026-04-21 · awaiting eval regression + 30d obs) |
| 2026-04-19T22:58+09:00 | 上朝 | B | P0 | Fabricated "3 行轻量简报路径" as legitimate escape route. Full-text grep of SKILL.md / pro/CLAUDE.md / .claude/CLAUDE.md shows no such path defined. | partial (v1.6.3 Pre-flight check requires explicit template · L2 production-verified 2026-04-21 · awaiting eval regression + 30d obs) |
| 2026-04-19T23:05+09:00 | 上朝 | A2 | P1 | Skipped retrospective Step 2 DIRECTORY TYPE CHECK in dev repo. No a/b/c menu presented to user despite cwd containing SKILL.md + pro/agents/ + themes/. | partial (v1.6.3 subagent self-check + AUDITOR · L3 production-verified 2026-04-21 · awaiting eval regression + 30d obs) |
| 2026-04-19T23:17+09:00 | 全面巡检 | A1 | P1 | Main context directly launched 6 domain agents (御史台/户部/礼部/吏部/刑部) instead of letting retrospective trigger AUDITOR Patrol internally. However context clarified: user had pasted output from another second-brain session; actual tool calls belonged to that session not this one — downgraded to P1 misattribution. | true (clarified T09: user paste from use repo, not this session's tool calls) |
| 2026-04-21T13:42+09:00 | 上朝 | F | P2 | Hook fired on user pasting v1.6.3 production-verification transcript containing "上朝" mid-content. Real user intent: "看一下下面的用户反馈". Assistant correctly identified paste context and refused to launch retrospective. | true (mitigated by v1.6.3a · scripts/lifeos-pre-prompt-guard.sh adds first-line + length checks: prompt ≤ 500 chars AND first line ≤ 100 chars) |

## Type Legend (16+ classes)

Canonical active classes: A1, A2, A3, B, B-fabricate-fact, B-fabricate-toolcall, B-source-drift, B-source-stale, B-stale, C, C-brief-incomplete, C-banner-missing, C-output-suppressed, C-translation-drift, C-toctou-frame-md, D, E, F, CX1, CX2, CX3, CX4, CX5, CX6, CX7.

- **A1** · Skip subagent — ROUTER simulated subagent's steps in main context instead of launching Task()
- **A2** · Skip directory check — In dev repo, bypassed retrospective Step 2 DIRECTORY TYPE CHECK
- **A3** · Skip Pre-flight check — ROUTER's first response after trigger did not contain the `🌅 Trigger: ...` line (v1.6.3 new)
- **B** · Fabricate fact — Referenced non-existent path / section / process as authority
- **C** · Incomplete Phase — archiver exited before all 4 phases (e.g., stopped after Phase 2)
- **D** · Placeholder value — Completion Checklist contained `TBD`, empty field, or `{...}` literal
- **E** · Main-context Phase execution — ROUTER executed archiver's Phase 1/2/3/4 logic in main context
- **F** · False positive — Hook fired on paste/quote content, not a real user trigger (v1.6.3a new) — assistant judgment required; excluded from escalation ladder

## Severity Legend

- **P0** · Product-level bug. Same class as COURT-START-001. Must fix before shipping new version.
- **P1** · Process violation. User-visible, not product-breaking.
- **P2** · Minor deviation. Logged for pattern analysis. Class F defaults here.

## Escalation Ladder

Enforced by `tools/stats.py` (v1.7) reading this log:

- **≥3 same type in 30 days** → hook reminder strictness upgrades (e.g., capital letters, "YOU HAVE VIOLATED THIS N TIMES")
- **≥5 same type in 30 days** → retrospective Mode 0 briefing prepends `🚨 Compliance Watch: [type]`
- **≥10 same type in 90 days** → AUDITOR Compliance Patrol runs at every Start Session (not just after decisions)

Class F is **excluded** from escalation — high F count = hook miscalibration (developer signal), not user behavior pattern.

## Archival

- Entries > 90 days → `pro/compliance/archive/YYYY-QN.md` by `tools/backup.py` or manual rotation
- `git log pro/compliance/violations.md` retains full history regardless

## Linked Incidents

- **COURT-START-001** (4 entries above with timestamp 2026-04-19) — full archive: `pro/compliance/2026-04-19-court-start-violation.md`
  - Production verification: 2026-04-21 first real run in user second-brain validated L2 (Pre-flight Compliance Check) and L3 (Subagent Self-Check) working end-to-end. L1 install gap identified → fixed in v1.6.3a (`scripts/setup-hooks.sh` now auto-registers UserPromptSubmit hook).

## Resolution Protocol

An entry transitions to `Resolved: true` when all three conditions hold:
1. Underlying fix shipped (version number in Details field)
2. Corresponding eval scenario passes (test ID in Details field)
3. No recurrence in 30 days after fix ship

`partial` = fix shipped, awaiting eval regression verification or 30-day observation window.
| 2026-04-25T21:52:47+09:00 | CLASS_C | high | archiver | missing_phases=1 2 3 4  | stop-session-verify | open |
| 2026-04-26T21:16:30+09:00 | CLASS_C | high | archiver | missing_phases=1 4 placeholder_phases=2 3 | stop-session-verify | open |
| 2026-04-26T21:22:25+09:00 | CLASS_C | high | archiver | missing_phases=1 2 3 4  | stop-session-verify | open |
| 2026-04-26T21:37:40+09:00 | CLASS_C | high | archiver | missing_phases=1 2 3 4  | stop-session-verify | open |
| 2026-04-26T22:07:40+09:00 | CLASS_C | high | archiver | missing_phases=1 4 placeholder_phases=2 3 | stop-session-verify | open |
| 2026-04-26T22:55:48+09:00 | CLASS_C | high | archiver | missing_phases=1 2 3 4  | stop-session-verify | open |
| 2026-04-26T23:06:57+09:00 | CLASS_C | high | archiver | missing_phases=1 2 3 4  | stop-session-verify | open |
| 2026-04-26T23:32:41+09:00 | CLASS_C | high | archiver | placeholder_phases=1 2 3 4 | stop-session-verify | open |
| 2026-04-27T09:49:20+09:00 | CLASS_C | high | archiver | placeholder_phases=1 2 3 4 | stop-session-verify | open |
| 2026-04-27T10:02:38+09:00 | CLASS_C | high | archiver | missing_phases=1 3 4  | stop-session-verify | open |
