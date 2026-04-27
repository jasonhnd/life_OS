# Session Modes Spec (v1.8.0)

Defines the three orthogonal session/process modes in Life OS v1.8.0. See `references/automation-spec.md` for the broader autonomy architecture.

## Mode 1 · Business session

**What**: Standard Claude Code chat. User talks to ROUTER → Cortex / 6 Domains / ADVISOR / AUDITOR / archiver.

**Activation**: User opens Claude Code window in a Life OS second-brain repo.

**Lifecycle**:
- No mandatory start (no required 上朝)
- No mandatory end (no required 退朝)
- Long-lived: a single session can span hours, days, or weeks
- Implicit close: when user closes the window or Claude Code is restarted

**Active subagents** (depending on user message):
- Cortex Pre-Router (hippocampus / concept-lookup / soul-check / gwt-arbitrator) — every qualifying message
- ROUTER triage
- PLANNER → REVIEWER → DISPATCHER → 6 Domains (full deliberation)
- AUDITOR Mode 1 (decision review) + ADVISOR — after every full deliberation
- knowledge-extractor → archiver — when user says 退朝 (or daily 23:30 cron auto-runs if not)
- narrator-validator — when narrator emits Summary Report

**Hooks active**:
- SessionStart (lifeos-version-check + session-start-inbox)
- UserPromptSubmit (pre-prompt-guard + lifeos-pre-prompt-guard)
- PreToolUse Bash (pre-bash-approval)
- PreToolUse Read (pre-read-allowlist)
- PreToolUse Write|Edit (pre-write-scan)
- PreToolUse Task (pre-task-launch)
- PostToolUse Task|Bash|Write|Edit (post-response-verify + post-task-audit-trail)
- Stop (stop-session-verify)

## Mode 2 · Monitor session

**What**: Operations console mode for cron management, system health, action items processing.

**Activation**: In any business session, run `/monitor` slash command. Loads `pro/agents/monitor.md` role. Subsequent message handling switches to monitor scope.

**Lifecycle**:
- Started by `/monitor`
- Ended by `/exit-monitor` (returns to business session) OR by closing Claude Code

**What monitor does**:
- Reads `_meta/eval-history/cron-runs/`, `_meta/inbox/notifications.md`
- Reads action item reports (auditor-patrol, advisor-monthly, strategic-consistency, wiki-decay, monthly-summary)
- Triggers cron manually (`bash scripts/run-cron-now.sh <job>`)
- Pauses/resumes cron jobs (`launchctl unload/load` / crontab edit)
- Edits cron schedules (plist edit)
- Walks user through action items (wiki stale entries / SOUL drift / strategic conflicts)
- Applies user-confirmed changes to wiki/, SOUL.md, _meta/methods/

**What monitor does NOT do**:
- Business deliberation (PLANNER / REVIEWER / DISPATCHER / 6 Domains / COUNCIL / STRATEGIST)
- Cortex Pre-Router (hippocampus / concept-lookup / soul-check / gwt-arbitrator)
- 上朝 retrospective subagent (use /run-cron daily-briefing instead)
- 退朝 archiver subagent (use /run-cron archiver-recovery instead)
- Cross-session memory writes (no SOUL/wiki edits without user explicit confirmation per action item)

**Audit trail**:
- Single audit trail per monitor session: `_meta/runtime/<sid>/monitor.json`
- Written before /exit-monitor or session end

## Mode 3 · Cron autonomy

**What**: Background scheduled execution. No user attention. Runs on macOS launchd / Linux cron.

**Activation**: `bash scripts/setup-cron.sh install` (one-time setup per machine).

**Lifecycle**:
- Each job is a separate process invocation
- Per-job timeout (default 600s for prompt jobs, shorter for python-tool jobs)
- Jobs do not share state in-memory; only via filesystem + git

**Coordination**:
- Mutual exclusion: each cron job checks `~/.claude/lifeos-active-session.lock` (planned)
- Git contention: `pull --rebase` → work → `add + commit + push`
- Failure isolation: one job's failure does not block others

**Job types**:

| Type | Invocation | Use case |
|------|-----------|---------|
| **Python tool** | `python -m tools.<name>` | Pure deterministic work (reindex, backup, decay scan, compliance report) |
| **Prompt-driven** | `claude -p "$(cat scripts/prompts/<name>.md)"` | Needs LLM judgment (archiver-recovery, auditor-mode-2, advisor-monthly, etc) |
| **RunAtLoad** | macOS launchd RunAtLoad / cron @reboot | Boot/wake catch-up (missed-cron-check) |

**Outputs**:
- Reports: `_meta/eval-history/<category>/<date>.md`
- Notifications: `_meta/inbox/notifications.md` (append-only)
- Audit trails: `_meta/runtime/<sid>/<name>.json`
- Logs: `~/Library/Logs/LifeOS/hermes-local/<job>.log` or `~/.local/state/lifeos/hermes-local/<job>.log`

## Mode interaction matrix

| | Business session | Monitor session | Cron |
|---|---|---|---|
| **Business session** | (one window = one session) | `/monitor` switches to | independent |
| **Monitor session** | `/exit-monitor` switches back | (one window = one session) | independent |
| **Cron** | sees cron output via SessionStart hook + retrospective | reads cron output as primary purpose | (parallel jobs are independent) |

## State sharing

All three modes share state through the filesystem:
- `_meta/`: session indexes, runtime audit trails, eval history, inbox notifications
- `wiki/`: knowledge layer
- `SOUL.md`: identity layer
- `_meta/methods/`: method library
- `_meta/STRATEGIC-MAP.md`: project relationships
- `_meta/concepts/`: concept graph

git is the synchronization mechanism. cron jobs always pull/push. business sessions push at end of significant flows (archiver Phase 4 syncs).

## Migration from v1.7.x

v1.7.x: only Mode 1 (business) existed. Mode 3 cron only had 3 jobs (reindex/daily-briefing/backup) and was disconnected from spec.

v1.8.0 migration:
1. `bash scripts/setup-cron.sh install` — installs 10 cron + 1 RunAtLoad
2. `bash scripts/setup-hooks.sh` — re-runs to register 3 new hooks (SessionStart inbox + PreToolUse Task + PostToolUse Task)
3. Existing business session behavior unchanged
4. New: SessionStart now injects cron summary; `/monitor` available for ops; `/run-cron <job>` for manual trigger

No second-brain data migration required. v1.7.x sessions/wiki/SOUL/methods data fully compatible.

## Related specs

- `references/automation-spec.md` (3-layer architecture)
- `pro/CLAUDE.md` Session Modes section (orchestration)
- `pro/agents/monitor.md` (Mode 2 subagent spec)
- `scripts/prompts/*.md` (Mode 3 cron prompts)
- `scripts/setup-cron.sh` (Mode 3 install)
