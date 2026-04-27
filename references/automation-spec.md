# Automation Spec (v1.8.0)

The v1.8.0 hybrid (reactive + autonomous) layer architecture. This document is the **canonical reference** for cron + hook + monitor coordination in Life OS.

## Three layers

```
┌──────────────────────────────────────────────────────────────┐
│ User-facing surfaces (what user sees)                         │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  💬 Business session  (long-lived Claude Code chat)           │
│     - reactive, user-driven                                    │
│     - ROUTER + Cortex + 6 Domains + ADVISOR/AUDITOR + archiver │
│                                                                │
│  📡 Monitor session  (one-off ops console, /monitor)           │
│     - reactive, system-management focused                      │
│     - reads cron output, triggers manual catch-up,             │
│       processes action items                                   │
│                                                                │
│  🔔 macOS notifications  (osascript, optional)                 │
│     - cron emits these for important events                    │
│                                                                │
└──────────────────────────────────────────────┬─────────────────┘
                                                │
                          (file + git layer is the bus between layers)
                                                │
┌──────────────────────────────────────────────▼─────────────────┐
│ Cron autonomy (background, no user, scheduler-driven)          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  10 scheduled jobs + 1 RunAtLoad:                              │
│                                                                │
│   Python-tool jobs (`python -m tools.<name>`):                 │
│   - reindex                  daily 03:00                        │
│   - daily-briefing           daily 08:00                        │
│   - backup                   weekly Sun 02:00                   │
│   - spec-compliance          weekly Sun 22:00 (NEW v1.8.0)      │
│   - wiki-decay               monthly 15th 02:00 (NEW)           │
│                                                                │
│   Prompt-driven jobs (`claude -p "$(cat scripts/prompts/X.md)"`):│
│   - archiver-recovery        daily 23:30 (NEW)                  │
│   - auditor-mode-2           weekly Sun 21:00 (NEW)             │
│   - advisor-monthly          monthly 1st 06:00 (NEW)            │
│   - eval-history-monthly     monthly 1st 07:00 (NEW)            │
│   - strategic-consistency    monthly 1st 08:00 (NEW)            │
│                                                                │
│   RunAtLoad / @reboot:                                         │
│   - missed-cron-check        on Mac wake / boot                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Layer responsibilities

### Business session
- Talk to Life OS about decisions, plans, life
- Trigger reactive subagent flow (PLANNER, REVIEWER, 6 Domains, ADVISOR, AUDITOR)
- Cortex Pre-Router fires on every qualifying user message
- Optional 上朝/退朝 soft triggers for explicit briefing/archiver

### Monitor session
- Open via `/monitor` slash command → loads `pro/agents/monitor.md` role
- Read cron output (`_meta/eval-history/`, `_meta/inbox/notifications.md`)
- Manual cron triggers via `/run-cron <job>` or `bash scripts/run-cron-now.sh`
- Pause/resume/edit cron schedules (`launchctl unload` / plist edit)
- Process action items from AUDITOR Patrol / ADVISOR monthly / strategic-consistency / wiki-decay reports
- Exit via `/exit-monitor`

### Cron autonomy
- macOS launchd plists (`~/Library/LaunchAgents/com.lifeos.hermes-local.*.plist`)
- Linux/WSL crontab marked block
- Each job is independent; no inter-cron dependencies
- Logs to `~/Library/Logs/LifeOS/hermes-local/<job>.log` (macOS) or `~/.local/state/lifeos/hermes-local/<job>.log` (Linux)

## Cron-to-session bridge

The bridge from cron output to user awareness:

1. **Cron writes**:
   - Reports to `_meta/eval-history/<category>/<date>.md`
   - Notifications to `_meta/inbox/notifications.md` (one-line append per notification-worthy event)
   - macOS notification via osascript (best-effort, optional)

2. **Sessions read**:
   - **SessionStart hook** (`scripts/hooks/session-start-inbox.sh`) reads inbox + recent cron runs at session start; injects `<system-reminder>` to Claude
   - Claude proactively mentions in first response
   - **Monitor session** (via `/monitor`) reads cron output as primary purpose
   - **Retrospective subagent** (上朝) reads recent cron output and integrates into Mode 0 briefing

3. **User awareness flow**:

```
Cron runs → file (eval-history + inbox + macOS notif)
       → SessionStart hook reads (next time user opens Claude Code)
       → injected as system-reminder
       → Claude mentions "heads-up: cron did X overnight"
       → user decides next step (look details / handle action items / ignore)
```

## Mutual exclusion (cron vs sessions)

- Cron runs check `~/.claude/lifeos-active-session.lock` before starting (planned, future patch)
- If lock present → sleep 5 min, retry up to 3 times
- If still locked after 3 retries → log "deferred" to cron-runs/ and exit
- Lock written by Claude Code SessionStart, removed at SessionStop

## Git contention

- Cron jobs always: `git pull --rebase` before, do work, `git add + commit + push` after
- If `pull` fails (conflict) → abort, log to `_meta/eval-history/cron-runs/<job>-<ts>-CONFLICT.log`
- If `push` fails → log to same, leave commits local for next run to push
- Sessions interactively resolve conflicts via user prompt

## Daily cycle (上朝/退朝) softened

Pre-v1.8.0: 上朝 mandatory at session start, 退朝 mandatory at session end. Failure to comply = data loss.

v1.8.0 onwards:
- 上朝 = optional explicit "give me full briefing" trigger
- 退朝 = optional explicit "archive now" trigger
- If user forgets either, the cron tier (daily-briefing / archiver-recovery) handles them automatically

This means **a single Claude Code session can span days or weeks**, with cron tier catching up periodic concerns. ROUTER MUST NOT enforce 上朝/退朝 as hard cycle.

## Observability

`tools/spec_compliance_report.py` (weekly cron) measures:
- Each spec promise in `pro/agents/*.md` and `references/*.md`
- vs actual evidence in `_meta/eval-history/cron-runs/` and `_meta/runtime/<sid>/*.json`
- Outputs `_meta/eval-history/spec-compliance-<date>.md`

`tools/cron_health_report.py` (called from `/monitor`) measures:
- Each cron job's success/failure rate vs expected runs in window
- Outputs to stdout (markdown table or JSON)

## Failure modes

| Failure | Recovery |
|---------|----------|
| Cron job timeout | macOS launchd / cron auto-retry next schedule; missed-cron-check at boot picks up |
| `claude` CLI not on PATH (prompt-driven cron) | Cron job logs error, exits silently. User sees in cron health report. |
| Network failure during git push | Job logs to cron-runs/, leaves commits local; next cron retries push |
| Session lock contention | 5-min retry × 3 → defer to next schedule |
| `_meta/sessions/INDEX.md` missing | `tools/migrate.py` auto-bootstrap on first user message OR cron job logs and skips |
| `claude -p` exits non-zero | Cron logs failure; missed-cron-check on next boot may auto-recover (for critical jobs only) |

## v1.8.0 invariants

- All 10 cron jobs are **idempotent** (re-running same day = no harmful side effects)
- All 10 cron jobs are **independent** (no inter-cron sequencing requirement; each handles missing preconditions)
- All `claude -p` cron prompts are **scoped** (do NOT engage business deliberation)
- All cron writes go through `git push` for sync (no local-only state)

## Related specs

- `pro/CLAUDE.md` Session Modes (v1.8.0)
- `references/session-modes-spec.md` (Mode 1/2/3 detailed)
- `pro/agents/monitor.md` (Mode 2 spec)
- `scripts/setup-cron.sh` (install)
- `scripts/run-cron-now.sh` (manual trigger)
- `scripts/prompts/*.md` (5 cron-driven Claude Code prompts)
- `scripts/hooks/session-start-inbox.sh` (cron→session bridge)
- `tools/{spec_compliance_report,cron_health_report,wiki_decay,missed_cron_check}.py`
