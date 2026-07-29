---
spec_id: conscious-patrol-spec.v1
description: "lifeos's Conscious Patrol — the path-D adaptation of OpenHuman's Subconscious Loop. NOT idle autonomous daemon; instead session-start user-in-loop checkpoint. retrospective Mode 0 reads system tasks list (lifeos defaults) + user tasks (second-brain HEARTBEAT.md), evaluates each against current workspace, and reports recommendations to user. User explicitly approves each act/skip/escalate. Reconciled with v1.8.0 cron retirement: this is NOT a regression because user is always in the loop."
status: active
authoritative: true
source_attribution: "tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/subconscious.md (idle autonomous Subconscious Loop). lifeos chose path D (Conscious Patrol — user-in-loop) per RFC v1.8.7 DR-11."
introduced_in: v1.8.7 (added 2026-05-26 per DR-11)
referenced_by:
  - SKILL.md (E10 HARD RULE)
  - agents/retrospective.md (Mode 0 systematizes Conscious Patrol)
  - agents/auditor.md (Mode 8 patrol compliance)
  - references/status-line-spec.md (every patrol task outputs status line)
---

# Conscious Patrol Specification v1

lifeos's adaptation of OpenHuman's Subconscious Loop. **Crucial naming distinction**:

- **OpenHuman Subconscious** = idle thread, autonomous daemon, runs while user is away, local model auto-decides act/skip/escalate
- **lifeos Conscious Patrol** = session-start checkpoint, user-in-loop, ROUTER recommends + user decides, no daemon

This is path D from v1.8.7 RFC §1.3 E10 analysis. Path D was selected because lifeos is md-only skill (no daemon layer) and v1.8.0 explicitly retired cron-style autonomy.

## Why "Conscious" not "Subconscious"

| Attribute | OpenHuman Subconscious | lifeos Conscious Patrol |
|-----------|------------------------|------------------------|
| Trigger | Periodic heartbeat tick (every N min) | retrospective Mode 0 (session start) |
| Awareness | User unaware while it runs | User explicitly invoked the session |
| Decision authority | local model autonomous | ROUTER recommends, user decides |
| Write actions | Auto-execute unless unsolicited | All acts need user explicit OK |
| Failure mode | Silent data loss possible (cron-style) | User in front of screen sees every error |
| Architectural carrier | Tauri daemon process | retrospective subagent run |

Naming honesty matters: calling lifeos's path D "Subconscious" would mislead users to expect idle autonomy that isn't there. **Conscious Patrol** accurately describes what happens — user is conscious, ROUTER patrols, user decides.

## Why this isn't a regression to v1.8.0 cron

v1.8.0 retired `setup-cron.sh` + all launchd plists + 5 Python tools that ran LLM in cron context. The retirement rationale:

1. "Unreliable" — cron silently fails, no surface
2. "Invisible" — output goes to log file user doesn't read
3. "Silent data loss" — Python tools running LLM in cron context produced wrong outputs that overwrote good data

**Conscious Patrol violates none of these**:

1. **Reliable** — runs as part of retrospective Mode 0, which runs every session start; if it fails, user sees the failure in the briefing
2. **Visible** — output is the morning briefing itself, the most prominent thing user sees at session start
3. **No silent data loss** — every act requires user OK; nothing writes without explicit confirmation

The v1.8.0 retirement was correct for the technology of the time (Python tools + system cron). v1.8.7 Conscious Patrol uses a fundamentally different mechanism (LLM-driven retrospective + user approval). Path D is **not** path C/F (external cron triggering Claude Code headless) — those would re-introduce the v1.8.0 concerns. Path D stays in the user-in-loop model lifeos has always advocated.

## System tasks (default seeded, cannot delete only disable)

retrospective Mode 0 includes these as default patrol items every session:

### lifeos-001 · Maintenance overdue check

- **Source**: lifeos already implemented in v1.8.0 (`scripts/prompts/auditor-mode-2.md` + 10 maintenance jobs)
- **What it checks**: timestamps of `reindex / daily-briefing / backup / spec-compliance / wiki-decay / archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency` — flag overdue
- **Output**: status line + count of overdue items
- **User decision**: pick which overdue jobs to run this session

### lifeos-002 · Review queue overdue

- **Source**: lifeos R-1.8.0-013 review-queue.md prompt
- **What it checks**: scan review queue for P0/P1/P2 items not handled in expected window
- **Output**: status line + N P0 / M P1 / K P2 counts
- **User decision**: walk queue now or defer

### lifeos-003 · SOUL drift check

- **Source**: lifeos advisor-monthly.md prompt (existing)
- **What it checks**: SOUL.md confidence drift / unchallenged dimensions / contradictory evidence
- **Output**: status line + N dimensions flagged
- **User decision**: review now or schedule monthly slot

### lifeos-004 · Wiki decay scan

- **Source**: lifeos wiki-decay.md prompt (existing)
- **What it checks**: wiki entries with stale `last_reviewed` or contradicted by recent sessions
- **Output**: status line + N entries flagged
- **User decision**: confirm decay, retire entries, or refresh

### lifeos-005 · Strategic consistency

- **Source**: lifeos strategic-consistency.md prompt (existing)
- **What it checks**: cross-project conflicts in strategic flows / SOUL ↔ flow misalignment
- **Output**: status line + N conflicts
- **User decision**: address now or note for next planning session

### lifeos-006 · Compliance Watch

- **Source**: lifeos AUDITOR Mode 3 (existing)
- **What it checks**: 30-day rolling violation counts; escalation thresholds (≥3 same-class → hook stricter; ≥5 → briefing top; ≥10 → AUDITOR Mode 3 every Start Session)
- **Output**: status line + violation summary
- **User decision**: review violations.md, adjust behavior, or acknowledge

### lifeos-007 · Gotchas review (v1.8.7 new)

- **Source**: lifeos v1.8.7 C6 — `gotchas.md`
- **What it checks**: any gotcha referencing files/code touched in last 7 days (relevance signal); any gotcha resolved (codebase fixed but gotcha still listed)
- **Output**: status line + N relevant gotchas surfaced
- **User decision**: ROUTER scans relevant gotchas for current task; user confirms / dismisses

## User tasks (HEARTBEAT.md mechanism)

Users in their second-brain root can create `HEARTBEAT.md`:

```markdown
# Patrol Items

## daily
- Check unresolved decisions older than 14 days
- Surface mood-tagged journal entries from last 3 days

## weekly
- Review wiki entries tagged "review-needed"
- Cross-check project priorities against quarterly OKR

## monthly
- Audit financial decision categories
- Review SOUL.md "What I should be" vs "What I am" delta
```

retrospective Mode 0 reads `HEARTBEAT.md` (if exists), filters by frequency-since-last-run, and adds matching items to patrol list. Each user task gets a status line per the standard contract.

### HEARTBEAT.md frontmatter (optional)

```yaml
---
patrol_enabled: true
frequency_default: weekly
disabled_system_tasks: []   # e.g. ["lifeos-005"] to skip strategic consistency
---
```

`disabled_system_tasks` lets user opt out of specific defaults (cannot delete, but can disable per OpenHuman pattern).

## Tick semantics (lifeos vs OpenHuman)

OpenHuman runs ticks every N minutes regardless of user activity. lifeos runs the "tick" only when retrospective Mode 0 fires (every session start). Frequency comparison:

| Frequency | OpenHuman | lifeos Conscious Patrol |
|-----------|-----------|------------------------|
| User opens session multiple times/day | Patrol N times/day if user opens N sessions | Same — N times/day |
| User on vacation (no sessions for 2 weeks) | OpenHuman ticks every N min for 2 weeks (336+ ticks) | lifeos doesn't tick — patrol runs at session resume |
| Long-running concern (e.g. SOUL drift over 90 days) | OpenHuman catches drift incrementally | lifeos catches drift at next session start (acceptable for non-realtime concerns) |

**Trade-off**: lifeos sacrifices realtime detection for user-in-loop safety. For lifeos's domain (personal decision engine, not operational monitoring), the trade is correct.

## Status line integration (E9)

Every patrol task outputs a status line per `references/status-line-spec.md`:

```
🔍 evaluating · retrospective · Conscious Patrol — checking lifeos-001 maintenance overdue
⏭️ skipped · retrospective · lifeos-001 — all 10 jobs within window
🔍 evaluating · retrospective · lifeos-002 review queue
🟡 awaiting_user · retrospective · lifeos-002 — 3 P0 / 1 P1 items overdue, run /process-queue?
✅ acted · retrospective · lifeos-003 SOUL drift — 1 dimension flagged, surfaced in briefing
🟢 silent_pass · retrospective · lifeos-004 / lifeos-005 / lifeos-006 / lifeos-007 — clean
```

Each line is grep-able by AUDITOR Mode 8.

## Decision flow (path D core)

For each patrol task, retrospective Mode 0 emits one of three:

| Decision | What happens |
|----------|--------------|
| `silent_pass` | Task ran, found nothing relevant, no surfacing needed (high-frequency low-noise scenario) |
| `skipped` | Task ran, found nothing actionable, brief mention in briefing (low-frequency informational) |
| `awaiting_user` | Task found actionable item, ROUTER reports + asks user. User responses: "yes, run X" / "skip" / "later" |

**No silent act**. Every act is user-explicit. This is the central lifeos commitment that distinguishes path D from path A-F alternatives.

## AUDITOR Mode 8 patrol compliance (besides status line)

Mode 8 additionally validates Conscious Patrol behavior:

| Check | Description | Failure class |
|-------|-------------|---------------|
| M8-7 | Every session-start retrospective Mode 0 includes patrol section (`## Conscious Patrol`) in briefing | `F4 SCOPE_FAILURE: retrospective Mode 0 missing patrol section` |
| M8-8 | Each lifeos-001 to lifeos-007 system task emits status line (or explicitly marked disabled per HEARTBEAT.md) | `F3 SCHEMA_FAILURE: system task <id> output missing` |
| M8-9 | No "auto-act" detected (every act has accompanying `awaiting_user` line first) | `F10 RESPONSIBILITY_FAILURE: silent act bypassed user approval` |
| M8-10 | User tasks from HEARTBEAT.md actually scanned (audit trail evidence) | `F8 SILENT_FAILURE: HEARTBEAT.md exists but user tasks not surfaced` |

## What v1.8.7 does NOT do (path D scope honesty)

To be explicit about what Conscious Patrol is NOT:

- ❌ No background daemon / cron / launchd
- ❌ No external trigger mechanism (user's OS cron / GitHub Actions / etc.) — that's path C/F territory, deferred
- ❌ No autonomous act (every act requires user explicit OK)
- ❌ No realtime detection (only session-start patrols; user-away periods are blind)
- ❌ No headless Claude Code invocation
- ❌ No `claude --headless -p "..."` integration

What v1.8.7 DOES do:
- ✅ Systematize retrospective Mode 0 patrol into explicit 7 system tasks + user-defined HEARTBEAT.md
- ✅ Integrate with E9 status line for unified observability
- ✅ Enforce user-in-loop via AUDITOR Mode 8 M8-9
- ✅ Reconcile with v1.8.0 cron retirement (explicit "why this isn't regression" section in this spec)

## Future direction (post-v1.8.7)

If users actually demand realtime patrol (vacation-mode detection / overnight SOUL drift), the next options:

- **v1.9 / v2.0 path C**: Document external-cron templates (launchd plist / GitHub Actions workflow) for users who want it. lifeos remains spec provider, doesn't bundle.
- **v2.0 path F**: User's second-brain repo carries the cron logic (GitHub Actions in their repo). lifeos provides workflow template.

These are deferred — v1.8.7 path D explicitly scopes to user-in-loop only.

## Reference

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.9 E10 path D + DR-11
- Pattern source: `tinyhumansai/openhuman` `gitbooks/features/subconscious.md` (idle autonomous Subconscious Loop, daemon-based)
- Companion: `references/status-line-spec.md` (each patrol task uses 8 enum status)
- Companion: `agents/retrospective.md` Mode 0 (where Conscious Patrol runs)
- Companion: `agents/auditor.md` Mode 8 (validation)
- Related to but DIFFERENT from: lifeos v1.8.0 cron retirement (`hosts/CLAUDE.md` §"Mode 1 · Business session" — explains why daemon-style autonomy was rejected)
