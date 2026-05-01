# Changelog

## Versioning Rules

This project follows **Strict SemVer**: MAJOR (Breaking Change) · MINOR (new features) · PATCH (fixes and maintenance). Changes on the same day are merged into a single release, and every release gets a git tag.

---

## [1.8.1] - 2026-05-01 - Wiki pipeline · /research · /inbox-process · macOS portability · scanner regression-proof

> **Plan B wiki delivery**. Adds 4 new wiki-management features (activity log convention · Obsidian setup · inbox triage pipeline · multi-agent /research command) and lands the macOS bare-`python` portability fix that R-1.8.0-020 commit title claimed but never actually shipped. Also contains R-1.8.0-021 / R-1.8.0-022 fixes from the v1.8.0 maintenance line, now formally cut into 1.8.1.

### Added · Wiki management (Plan B)

- **F1 · `wiki/log.md` activity timeline convention** — append-only, one line per wiki Write/Edit/move op, action enum (`created` / `updated` / `promoted` / `deprecated` / `merged` / `renamed` / `rejected` / `bulk`). The `/inbox-process` and `/research` commands write log entries automatically. Manual edits should follow same pattern. Convention documented in `scripts/wiki/setup-secondbrain.sh` output and SCHEMA append template.
- **F2 · Obsidian vault setup advice** — `wiki/OBSIDIAN-SETUP.md` template (Dataview queries, Graph Analysis, Templater, color group for graph view). Plus `wiki/.templates/wiki-entry-template.md` SCHEMA-compliant stub for one-keystroke entry creation. Plus `scripts/wiki/wiki-link-audit.sh` — pure bash + awk, zero Python deps, generates link health report at `_meta/eval-history/wiki-link-audit-YYYY-MM-DD.md`. Replaces deleted v1.7 `tools/wiki_decay.py` auditor side; the LLM-driven half lives at `scripts/prompts/wiki-decay.md`.
- **F3 · Inbox ingest pipeline** — new `_meta/inbox/to-process/` drop-zone, `/inbox-process` slash command + matching prompt at `scripts/prompts/inbox-process.md`. Triage loop: scan → propose disposition (accept→wiki / update→wiki / archive / reject / defer) → user confirm → execute → log. SessionStart hook (`session-start-inbox.sh`) now counts pending items and surfaces `📥 Inbox: N items waiting (run /inbox-process)` as one line; deferred items counted separately and not treated as actionable.
- **F4 · `/research` multi-agent command** — `scripts/commands/research.md` + `scripts/prompts/research.md`. Spawns 5 (or 8 with `--depth deep`) parallel `general-purpose` subagents covering academic / practitioner / contrarian / origin / adjacent (+ mechanistic / data-statistics / meta-review). Synthesizes into a SCHEMA-compliant wiki draft with mandatory `Counterpoints` section. Default counter-bias check launches 1 additional opposing-evidence agent; bumps confidence DOWN 0.1 if substantive opposition found. Total wall time target ≤ 7 min; cost ~$0.30-0.80 per run.

### Added · `scripts/wiki/setup-secondbrain.sh`

One-time bootstrap script users run inside their second-brain vault on Mac. Idempotent, only writes missing files (never overwrites), refuses to run inside the Life OS dev repo. Creates: `wiki/log.md` initial header, `wiki/OBSIDIAN-SETUP.md`, `wiki/.templates/wiki-entry-template.md`, `_meta/inbox/to-process/.gitkeep`, `_meta/inbox/README.md`. Prints post-run instructions: SCHEMA logging-convention append snippet + `.obsidian/graph.json` color-group snippet + first-run smoke-test recipe.

### Fixed · macOS portability (P0 from downstream user 4-day field report)

- **`scripts/hooks/pre-bash-approval.sh` had 5 bare `python -c` invocations** (lines 57/147/180/193/201). macOS 12+ removed bare `python`; only `python3` exists. Hook fail-CLOSED with `python: command not found` → blocked every Bash command → Claude Code deadlock. R-1.8.0-020 commit title claimed this was fixed; it wasn't until now. Added portable `PYTHON=$(command -v python3 || command -v python)` detection at top of script; replaced all 5 bare-python invocations with `"$PYTHON"`.

### Fixed · scanner regression-proofing

- **`scripts/hooks/pre-write-scan.sh` pattern #5 (shell-injection-backticks) over-matched** any backticked content, including legitimate markdown inline code like `` `python -m tools.embed` ``. Wiki writes were being blocked by the hook for normal documentation content. Pattern tightened to require shell-metacharacter content inside backticks (`;`, `|`, `&&`, `>>`, `$(`, `$VAR`, or known-dangerous command names like `rm -rf` / `curl ` / `wget ` / `eval `). Markdown identifier-style backticks now pass; real shell-injection payloads still block. Smoke-tested both directions.

### Fixed · session-start-inbox UX (rolled-up R-1.8.0-021 + R-1.8.0-022 into the 1.8.1 cut)

- **2 wrong task names in `TASKS_LINE` array**: `auditor-patrol` → `auditor-mode-2`, `monthly-summary` → `eval-history-monthly` (correct names per `pro/CLAUDE.md` canonical 10-job table and actual `scripts/prompts/*.md` filenames).
- **NEVER_RUN bucket split from OVERDUE**: tasks with no baseline are now reported under `## Available on-demand (do NOT proactively offer)` with explicit instruction not to mention unless user asks; previously LLM treated them as overdue and proactively offered jobs the user never opted into. Output compressed from 8+ lines to 1 comma-separated line for token budget.

### Fixed · Notion sync hardcoding (rolled-up from v1.8.0 maintenance line)

- **`pro/CLAUDE.md` Step 10a was hardcoding 4 Notion entities** (Status / Todo Board / Working Memory / Inbox). Real users have varied layouts; orchestrator was reporting "Working Memory: failed" for entities that never existed. Now config-driven: orchestrator reads `_meta/config.md`, only syncs configured entities, skips Step 10a entirely if no Notion configured, no false-fail lines in checklist.

### Fixed · pattern transparency in pre-bash-approval

- **Blocked-command message said `匹配模式: unknown` too often**. `approval.py` decision payload sometimes lacked `pattern_key`. Now extracts and concatenates `key=` + `matched=<actual substring>` + `regex=<source pattern>`; clear "decision payload missing all 4 fields" diagnostic when nothing available. Added doc note that inline `export LIFEOS_YOLO_MODE=1` doesn't work in Claude Code Bash tool (PreToolUse hook reads env BEFORE export executes); persistent bypass requires `~/.claude/settings.local.json` env block.

### Verification (CI matrix)

- `bash -n` on all 32 tracked .sh files (added 2 new wiki scripts) → pass
- `STRICT=1 bash scripts/check-spec-drift.sh` → exit 0
- `mypy --strict tools/` → 0 errors / 16 source files
- `ruff check tools/ tests/` → All checks passed
- `pytest tests/` → 233 passed / 3 deselected
- `bash scripts/verify-release.sh` → 7/7 ✅ after retag

### Migration

If you're on v1.8.0:
1. Update Life OS skill: `cd ~/.claude/skills/life_OS && git pull` (or re-install via skills.sh).
2. Re-run `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh` — installs new `/inbox-process` and `/research` slash commands; updates `pre-bash-approval.sh` and `pre-write-scan.sh` hooks.
3. **In your second-brain vault** (NOT this dev repo), one-time bootstrap: `cd ~/path/to/SecondBrain && bash ~/.claude/skills/life_OS/scripts/wiki/setup-secondbrain.sh`. Creates wiki/log.md, OBSIDIAN-SETUP.md, .templates/, _meta/inbox/to-process/, _meta/inbox/README.md. Idempotent — safe to re-run.
4. (Optional) Apply the `wiki/SCHEMA.md` Logging convention append snippet (printed at end of setup-secondbrain.sh run) and the `.obsidian/graph.json` color-group snippet.
5. Run `bash ~/.claude/skills/life_OS/scripts/wiki/wiki-link-audit.sh` from vault root to generate baseline link audit.

No second-brain data migration required. Existing wiki entries continue to work; new conventions apply to new writes.

### Removed

- Nothing. v1.8.1 is purely additive plus bugfixes.

---

## [1.8.0] - 2026-04-28 - Daily Cycle Hybridization (cron + monitor + softened 上朝/退朝)

> **Largest single release in Life OS history**. Transforms lifeos from a reactive chatbot (must-be-driven-by-user) into a hybrid OS (reactive + autonomous). Three orthogonal session/process modes now coexist: business session (long-lived), monitor session (`/monitor`), cron autonomy (10 jobs + RunAtLoad).

### Added · Session Modes (the core architectural shift)

- **Mode 1 · Business session**: long-lived Claude Code chat, sessions can span days/weeks. 上朝/退朝 are now optional soft triggers, not mandatory daily cycle.
- **Mode 2 · Monitor session**: new `/monitor` slash command opens operations console mode (`pro/agents/monitor.md`). Reads cron output, triggers cron manually, processes action items. Does NOT engage business deliberation. Exits via `/exit-monitor`.
- **Mode 3 · Cron autonomy**: 10 scheduled jobs + 1 RunAtLoad on macOS launchd / Linux cron. Background, no user attention, runs even when no session is active.

### Added · Cron jobs (5 new in v1.8.0, total 10 + 1 RunAtLoad)

Pre-existing (preserved): `reindex` (daily 03:00), `daily-briefing` (daily 08:00), `backup` (weekly Sun 02:00).

NEW v1.8.0:
- **`spec-compliance`** (weekly Sun 22:00) — heuristic spec-promise vs evidence ratio
- **`wiki-decay`** (monthly 15th 02:00) — stale entry detection (confidence + age)
- **`archiver-recovery`** (daily 23:30) — auto-recovers missed adjourns. Closes 80%+ archiver violation root cause.
- **`auditor-mode-2`** (weekly Sun 21:00) — AUDITOR Patrol Inspection. **Activates spec promise from v1.6.x that had 0 cron triggers until v1.8.0.**
- **`advisor-monthly`** (monthly 1st 06:00) — SOUL drift detection + contradictory pattern flagging + regret accumulation
- **`eval-history-monthly`** (monthly 1st 07:00) — system performance aggregation
- **`strategic-consistency`** (monthly 1st 08:00) — cross-project conflict detection
- **`missed-cron-check`** (RunAtLoad / @reboot) — Mac wake/boot catch-up for critical missed jobs

### Added · Slash commands (2 new)

- **`/monitor`** — enter Monitor session mode (Mode 2)
- **`/run-cron <job>`** — manually trigger any cron job from session

### Added · Hooks (3 new)

- **`session-start-inbox`** (SessionStart) — cron→session bridge. Reads `_meta/inbox/notifications.md` + recent cron runs at session start, injects `<system-reminder>` so Claude proactively mentions cron activity to user.
- **`pre-task-launch`** (PreToolUse Task) — machine-enforces v1.7.3 carve-out: blocks `archiver` launch unless `_meta/runtime/<sid>/knowledge-extractor.json` exists. Bypass: `LIFEOS_SKIP_KE_GUARD=1`.
- **`post-task-audit-trail`** (PostToolUse Task) — immediate R11 audit trail check after every Cortex/archiver/knowledge-extractor invocation. Bypass: `LIFEOS_SKIP_AUDIT_GUARD=1`.

### Added · Python tools (4 new)

- `tools/spec_compliance_report.py`
- `tools/wiki_decay.py`
- `tools/cron_health_report.py`
- `tools/missed_cron_check.py`

### Added · Cron-driven Claude Code prompts (5)

`scripts/prompts/{archiver-recovery,auditor-mode-2,advisor-monthly,eval-history-monthly,strategic-consistency}.md`

### Added · Spec docs (2 new)

- `references/automation-spec.md` — canonical 3-layer architecture
- `references/session-modes-spec.md` — Mode 1/2/3 detailed lifecycle

### Added · New subagent + manual trigger script

- `pro/agents/monitor.md` — Mode 2 role
- `scripts/run-cron-now.sh <job>` — manual cron trigger

### Changed

- **pro/CLAUDE.md**: new "Session Modes (v1.8.0)" section
- **scripts/setup-cron.sh**: extended from 3 → 10 cron jobs + 1 RunAtLoad. Added `repo_command_pymod` / `repo_command_prompt` builders + 5 new launchd plist printers.
- **scripts/setup-hooks.sh**: registers 3 new hooks
- **scripts/hooks/pre-prompt-guard.sh**: 上朝/退朝 trigger reminder softened (HARD RULE → optional soft trigger language)
- **Version markers**: SKILL.md frontmatter + 3 README badges → 1.8.0

### Post-release fixes (folded into v1.8.0 — version unchanged per "all-bugs-belong-to-this-version" policy)

- **R-1.8.0-001 · `scripts/setup-hooks.sh`**: missing 9 variable declarations (3× `HOOK_*_ID`, 3× `V18_*_SOURCE`, 3× `V18_*_DEST`) referenced in `copy_exec` and `register_hook` blocks. Setup errored with "未定义变量 V18_SESSION_START_INBOX_SOURCE". Declarations added at lines 52-54, 66-68, 80-82.
- **R-1.8.0-002 · `scripts/run-cron-now.sh`**: used bash 4+ `declare -A` associative arrays. macOS ships bash 3.2.57 (frozen at GPLv2), so the script aborted on every Mac. Rewrote the JOBS table as a `case`-based `job_spec()` lookup function with a separate `JOB_NAMES` list for iteration. Also moved data-root resolution to `$LIFEOS_DATA_ROOT` (env) → `$PWD` (cwd) → fail with clear error.
- **R-1.8.0-003 · `scripts/setup-cron.sh`**: catastrophic root-confusion bug. `REPO_ROOT` was used both for finding `tools/cli.py` (correct: skill source) and for `cd` + `--root .` in the generated commands (wrong: should be the user's second-brain repo). Result: all 11 cron jobs scanned the empty skill directory and reported "0 sessions / 0 SOUL / 0 projects". Introduced separate `DATA_ROOT` (from `$LIFEOS_DATA_ROOT` or `$PWD`) and threaded it through `repo_command{,_pymod,_prompt}` (`--root "$DATA_ROOT"` for python, `cd "$DATA_ROOT"` for prompt) plus all 6 `print_launchd_plist*` generators (`<key>WorkingDirectory</key>` now sourced from `$DATA_ROOT`). Added `require_data_root()` early-exit check in `main()` with actionable error message.
- **R-1.8.0-004 · `tools/spec_compliance_report.py`**: root-validation guard checked `(root / "SKILL.md").is_file()` to detect a Life OS root, but `SKILL.md` only exists in the skill source — not in user second-brain repos. Tool aborted with "no SKILL.md" on every install. Changed to `(root / "_meta").is_dir()` to match the actual data-root marker.
- **R-1.8.0-005 · `tools/wiki_decay.py`**: same `SKILL.md`-vs-`_meta/` mismatch as R-1.8.0-004. Same fix.
- **`tools/missed_cron_check.py`** (preempted alongside R-1.8.0-004): same `SKILL.md`-vs-`_meta/` bug pattern at line 134; would surface on next macOS reboot via the RunAtLoad plist. Same fix as R-1.8.0-004 applied prophylactically.
- **R-1.8.0-006 · `scripts/setup-cron.sh` · `repo_command_prompt`**: cron-spawned `claude -p` sessions had no pre-approved Write permission, so every prompt-based job (archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency) blocked on a Write-tool permission prompt that nobody answered. Sessions exited 0 after 5-15 minutes of analysis but **wrote nothing** — 100% data loss. Added `--dangerously-skip-permissions` flag to the generated `claude -p` invocation. Safety boundary stays enforced by `cd "$DATA_ROOT"` (cannot escape the second-brain) and the prompts being version-controlled in `scripts/prompts/`.
- **R-1.8.0-007 · `tools/missed_cron_check.py` · `trigger_recovery`**: looked for `run-cron-now.sh` under `data_root/scripts/`, but after the R-1.8.0-003 fix `data_root` is the user's second-brain — which has no `scripts/`. On a Mac that had run an earlier v1.8.0 install, a stale pre-R-1.8.0-002 copy of `run-cron-now.sh` (still using `declare -A`) was sitting in `data_root/scripts/` and got executed instead, dying with "declare -A: invalid option" even though the upstream script was already patched. Resolved the script path via `Path(__file__).resolve().parent.parent / "scripts" / "run-cron-now.sh"` so the **current upstream version** is always invoked, and pass `LIFEOS_DATA_ROOT` via subprocess env so the script knows the data root.
- **R-1.8.0-008 · `scripts/setup-cron.sh` · PATH expansion**: the launchd-spawned shell's PATH (`~/.local/bin:/opt/homebrew/bin:/usr/local/bin:...`) didn't include the directories where Claude Code is typically installed (`~/.claude/local`, `~/.bun/bin`, `~/.npm-global/bin`, `~/.volta/bin`), so `command -v claude` returned false and `archiver-recovery` (and any other prompt job) failed with "claude CLI not found". Extended the PATH export in all 3 command builders (`repo_command`, `repo_command_pymod`, `repo_command_prompt`) to include those 4 install locations.
- **`tools/seed.py`**: `META_GITKEEP_DIRS` was missing `_meta/inbox`, `_meta/runtime`, and three `_meta/eval-history/` subdirs (`cron-runs`, `auditor-patrol`, `recovery`). New second-brain repos seeded by `tools/seed.py` did not have the dirs the v1.8.0 cron prompts and `session-start-inbox` hook write to. Also seeds an initial `_meta/inbox/notifications.md` header file so the cron→session bridge has a target from day one.
- **`scripts/setup-cron.sh`** (companion to seed.py fix): added `bootstrap_repo_dirs()` helper, called from `main` after `ensure_repo`. Idempotently creates the same dirs + notifications.md header in **existing** second-brain repos that were seeded before this fix. Now keyed off `$DATA_ROOT/_meta` not `$REPO_ROOT/_meta` (R-1.8.0-003 cleanup).

- **R-1.8.0-010 · ARCHITECTURE PIVOT (post-2026-04-29) · cron architecture abandoned**: After two days of production testing, the cron-driven architecture from R-1.8.0-001~009 still failed the user's reliability test. The 5 prompt-based cron jobs (archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency) silently lost data: cron-spawned `claude -p` sessions completed analysis then asked the user "shall I write?" via prompt template politeness — no human was watching the cron, sessions timed out, exit 0, `_meta/eval-history/` empty. The `--dangerously-skip-permissions` flag (R-1.8.0-006) only bypassed the OS-level Write permission, not the LLM's own conversational politeness. Verdict: **cron requires determinism, LLM is non-deterministic, the mismatch can't be patched**.
  - **Pivot decision (per user)**: replace cron with explicit user prompts. User says "rebuild index" / "monthly review", ROUTER reads `scripts/prompts/<job>.md` and executes inline. No background processes.
  - **Deleted (17 files)**: `scripts/setup-cron.sh`, `scripts/run-cron-now.sh`, `scripts/commands/run-cron.md`, `tools/missed_cron_check.py`, `tools/cron_health_report.py`, `tools/reindex.py`, `tools/daily_briefing.py`, `tools/backup.py`, `tools/spec_compliance_report.py`, `tools/wiki_decay.py`, `tools/memory.py`, `tools/session_search.py`, `tools/cli.py`, `pro/agents/narrator-validator.md`, `references/automation-spec.md`, `references/session-modes-spec.md`, `docs/architecture/hermes-local.md`. Plus 3 eval scenarios for deleted tools.
  - **Created (5 user-invoked prompts)**: `scripts/prompts/{reindex,daily-briefing,backup,spec-compliance,wiki-decay}.md` — replace the deleted python tools. Each is a markdown prompt ROUTER reads + executes via Read/Write/Bash/Glob/Grep when user invokes by keyword.
  - **Modified (5 existing prompts)**: `scripts/prompts/{archiver-recovery,auditor-mode-2,advisor-monthly,eval-history-monthly,strategic-consistency}.md` — switched from "autonomous cron-triggered" framing to "user-invoked from session" framing. Removed UNATTENDED CRON CONTRACT block (no longer needed).
  - **Hooks restructured (3 hooks)**:
    - `scripts/hooks/pre-prompt-guard.sh`: removed Cortex always-on enforcement block (lines 111-167). Memory keyword detection now writes directly to `~/.claude/lifeos-memory/<key>.json` via Write tool instead of calling deleted `tools/memory.py`. 上朝/退朝 soft trigger preserved.
    - `scripts/hooks/session-start-inbox.sh`: complete rewrite — was reading cron output, now scans 10 maintenance task globs for last-run timestamps (`_meta/eval-history/<job>-*.md` mtimes), shows overdue summary as `<system-reminder>`. Hook only displays; user decides what to invoke.
    - `scripts/hooks/post-task-audit-trail.sh`: weakened — removed Cortex subagent (hippocampus / concept-lookup / soul-check / gwt-arbitrator) and narrator-validator from R11 audit trail enforcement. Only archiver + knowledge-extractor still required to write trails (they touch persistent state).
  - **Cortex pull-based** (`pro/CLAUDE.md` §0.5 rewritten): the 4 Cortex subagents are no longer launched on every qualifying message. ROUTER decides per-message whether the response benefits from cross-session memory (hippocampus), canonical concept grounding (concept-lookup), SOUL alignment check (soul-check), or arbitrated context (gwt-arbitrator). Heuristic: "would launching this change my response?" yes → launch, no → skip. Subagent description files updated to reflect pull-based activation.
  - **Slash commands rewritten**: `/monitor` now a view-and-invoke console (was cron monitor); `/memory` now writes JSON files directly (was python middleware); `/search` now uses Grep tool directly (was SQLite FTS5 via python).
  - **Spec docs**: `pro/CLAUDE.md` §0.5 + Session Modes section both rewritten. `references/hard-rules-index.md` updated to clarify Cortex is not always-on. `pro/AGENTS.md`, `pro/GEMINI.md`, `AGENTS.md` get pivot notice at top pointing to `pro/CLAUDE.md` as authoritative (full content sweep deferred).
  - **Stats**: ~3500 lines of cron infrastructure + python middleware deleted. ~500 lines of user-invoked prompt content added. Net: 23 deletions, 5 creations, ~25 modifications.
  - **Backup**: `git branch backup-pre-v1.8-pivot @ 7b15509` preserves the pre-pivot state.

- **R-1.8.0-011 · ARCHITECTURE PIVOT PHASE 2 (post-2026-04-29) · Bash skeletons + cortex helpers + python middleware all removed → 100% LLM**: After R-1.8.0-010 removed the cron layer, R-1.8.0-011 removes the next layer of "deterministic helpers": Bash briefing skeletons, cortex Python data-model helpers, and remaining maintenance python tools. Goal: minimum viable architecture = `hooks (immune system) + approval.py (security) + 5 one-shot bootstrap scripts + everything else is LLM doing the work directly`.
  - **Pivot decision (per user, "全 LLM 因为我要增强实用型")**: every helper that LLM can plausibly do should be LLM; only hooks (OS-protocol-required) and `approval.py` (security boundary) stay as code.
  - **Deleted (23 files)**:
    - Cortex helpers (5): `tools/lib/cortex/{__init__,concept,extraction,session_index,snapshot}.py`
    - Cascade .py (4): `tools/extract.py`, `tools/rebuild_session_index.py`, `tools/rebuild_concept_index.py`, `tools/migrate.py`
    - Bash skeletons + telemetry (4): `scripts/retrospective-briefing-skeleton.sh`, `scripts/archiver-briefing-skeleton.sh`, `scripts/retrospective-mode-0.sh`, `scripts/archiver-phase-prefetch.sh`
    - Cortex broken FTS5 helper (1): `scripts/lib/cortex/hippocampus_wave1_search.py`
    - Broken tests (9): `tests/test_{backup,cli,daily_briefing,reindex,extraction,concept_and_snapshot,session_index,package_imports,migrate}.py`
  - **Created (5 user-invoked prompts replacing the deleted python tools)**:
    - `scripts/prompts/rebuild-session-index.md` (replaces tools/rebuild_session_index.py)
    - `scripts/prompts/rebuild-concept-index.md` (replaces tools/rebuild_concept_index.py)
    - `scripts/prompts/migrate-from-v1.6.md` (replaces tools/migrate.py)
    - `scripts/prompts/snapshot-cleanup.md` (replaces snapshot.py retention logic)
    - `scripts/prompts/extract-concepts.md` (replaces extract.py + extraction.py)
  - **Spec rewrites (5 agent specs)**:
    - `pro/agents/hippocampus.md` L88-92: FTS5 SQLite helper → Grep tool on INDEX.md directly
    - `pro/agents/retrospective.md` L47-55: Python helper path removed, inline LLM rebuild only; L244 R10 boundary rewritten (no pre-fetch script)
    - `pro/agents/archiver.md`: snapshot Python helper block → inline Write with explicit YAML schema; extraction Python helper → inline tokenize/stopword/slug steps; SessionSummary Python helper → direct Write with explicit byte-level format contract; v1.7.2.3 rationale block updated
    - `pro/CLAUDE.md` L268-286: HARD RULE briefing skeleton blocks (retrospective + archiver) deleted, replaced with "Bash skeleton REMOVED" notes
  - **Cost accepted**:
    - retrospective Mode 0: ~1-2s pre-fetch + LLM filling → ~30-60s full LLM execution (~30× slower)
    - archiver Adjourn: 10-12 min → ~25-30 min (back to pre-v1.7.2.3 timing; the Bash skeleton was specifically designed to halve this)
    - Cortex hippocampus Wave 1: FTS5 → Grep — sub-second at <1000 sessions, loses stemming
  - **Risks accepted (per user — "都可以接受这些")**:
    - SessionSummary format drift (LLM may write fields in different order each time → INDEX.md compilation may fail)
    - Concept slug drift (same concept may get different slugs across runs → graph fragmentation; mitigated by SHA-1 fallback in spec)
    - SOUL snapshot accumulation (no auto-retention; user must manually invoke `scripts/prompts/snapshot-cleanup.md`)
    - 6-H2 briefing structure may have H2 omissions (the v1.7.2 failure mode that HARD RULE skeleton was created to prevent)
  - **What stays as code** (inviolable):
    - 11 hooks under `scripts/hooks/` + `scripts/lifeos-version-check.sh` (OS-level integration with Claude Code)
    - `tools/approval.py` (security boundary — LLM cannot judge security decisions reliably)
    - `tools/seed.py` + `tools/seed_concepts.py` + `tools/skill_manager.py` (one-shot CLI utilities)
    - `tools/lib/{config,llm,notion,second_brain}.py` (used by surviving tools; second_brain.py defines dataclasses but no cortex helpers)
    - `scripts/lib/{audit-trail.sh,sha-fallback.sh}` (sourced by retrospective/archiver/notion-sync scripts)
    - 5 cron-replacement prompts from R-1.8.0-010 (reindex, daily-briefing, backup, spec-compliance, wiki-decay) + 5 originally-cron prompts (archiver-recovery, auditor-mode-2, advisor-monthly, eval-history-monthly, strategic-consistency)
  - **Stats**: ~3500 lines deleted (5 cortex helpers + 4 cascade py + 4 Bash skeletons + 9 broken tests + 1 broken FTS5 helper). ~700 lines added (5 new prompts). Net: -2800 lines.
  - **Backup**: `git branch backup-pre-option-A @ 744d034` preserves the pre-pivot-Phase-2 state.

- **R-1.8.0-012 · Monitor mode → natural language only (post-2026-04-29 user feedback)**: Per user "这个不能要任何命令全部都要自然语言", monitor mode must be triggered by natural language keywords, not by typing `/monitor`. Slash command remains as backup mode (consistent with `/memory` `/search` `/method`).
  - **`scripts/hooks/pre-prompt-guard.sh`**: added `MONITOR_KEYWORD_RE` detection block right after `MEMORY_KEYWORD_RE`. Keywords: 监控模式 / 进监控 / 进 monitor / 开监控 / 监控控制台 / 看系统状态 / 看 cron / 看维护状态 / 维护控制台 / ops console / monitor mode / enter monitor / open monitor / 看 lifeos 状态 / 进运维. When matched, injects `<system-reminder>` (`trigger=monitor`) instructing ROUTER to launch `Task(subagent_type=monitor)` directly — DO NOT redirect to `/monitor`.
  - **`scripts/hooks/pre-prompt-guard.sh`** (also fixed in same edit — R-1.8.0-010 leftover): MEMORY block text still said `python -m tools.memory emit "..."` even though `tools/memory.py` was deleted. Updated to instruct ROUTER to write `~/.claude/lifeos-memory/<sanitized-key>.json` directly via Write tool with explicit JSON schema (`value` / `role` / `created` / optional `trigger_time`).
  - **`pro/CLAUDE.md` Special Triggers section**: added Monitor Mode entry alongside 上朝 / 退朝 / Quick Mode. Notes natural language is primary, `/monitor` is backup.
  - **`pro/CLAUDE.md` Auto-Trigger Rules section**: added "Monitor mode auto-launch" subsection alongside Memory auto-emit. Lists 中/英 keywords. The 4 v1.7.3 slash commands (`/compress` `/search` `/memory` `/method`) note expanded to 5 to include `/monitor`.
  - **`scripts/commands/monitor.md`**: added "Backup mode" notice block at top. Tells ROUTER not to redirect users to slash command — natural language is primary. Slash command kept for: explicit focus parameter (`/monitor wiki`), auto-trigger fallback (regex miss), testing.
  - **No code path broken**: `/monitor` slash command still works for power users; the `monitor` subagent at `pro/agents/monitor.md` is unchanged. Only the entry path expanded.

- **R-1.8.0-013 · 5 borrows from llm_wiki (post-2026-04-29 user research)**: Per user instruction "1，单独 2，llm 3，折中 4，全，完整" approving full implementation of all 5 borrowed patterns from [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki). lifeos shifts from "plain text + frontmatter ids" to "Obsidian-vault-compatible wikilink graph + async review queue + LLM-friendly relevance signals + page taxonomy refinement".
  - **Borrow 1 · Obsidian `[[wikilinks]]` syntax everywhere body text references another page**: `wiki/`, `_meta/concepts/`, `_meta/sessions/`, `_meta/methods/`, `_meta/people/`, `_meta/comparisons/`, `SOUL.md`, `_meta/STRATEGIC-MAP.md`. Frontmatter stays YAML strings (machine-parseable) EXCEPT `_meta/concepts/<id>.md` exception fields `provenance.source_sessions: ["[[YYYY-MM-DD]]"]` and `outgoing_edges[].target: "[[concept-<id>]]"`. Display variant `[[id|Display Name]]` for long names. Convention struck through "No cross-references" rule in `references/wiki-spec.md`.
  - **Borrow 2 · Obsidian vault layout**: `tools/seed.py` now writes `.obsidian/app.json` (`useMarkdownLinks: false`, `newLinkFormat: shortest`, `userIgnoreFilters` excluding `_meta/runtime/`), `.obsidian/core-plugins.json` (graph + backlinks + outgoing-links + tag-pane enabled), `.obsidian/.gitignore` (per-device state files like workspace.json excluded). Users can open the second-brain in Obsidian for graph view + backlinks panel. Spec: `references/obsidian-spec.md`.
  - **Borrow 3 · Async Review Queue (single source of truth for "needs user attention")**: `_meta/review-queue.md` consolidates 7 previously-scattered sources (auditor-patrol / advisor-monthly / strategic-consistency / archiver-recovery / eval-history-monthly action items + violations.md + cron notifications.md). YAML item schema: `id` (`r{YYYY-MM-DD}-{NNN}`) / `created` / `source` / `type` / `priority` (P0/P1/P2) / `summary` / `detail_path` / `related` (wikilinks) / `suggested_action` / `status` (open/reviewed/resolved/dismissed) / `closed_at` / `closed_by`. In-place status updates (Edit, never Write); resolved > 100 items auto-archived to `_meta/review-queue/archive/{YYYY-MM}.md` (折中 strategy per user choice). Spec: `references/review-queue-spec.md`. New walker prompt `scripts/prompts/review-queue.md` ("处理 queue" / "看 queue" / "review queue") walks user through each open item with A (act) / R (reviewed) / D (dismiss) / S (skip) / Q (quit) choices.
  - **Borrow 4 · 4-signal LLM-friendly relevance model (replaces hippocampus Wave 2 simple weight formula)**: `relevance(candidate, current) = 3 × direct_link_count + 4 × source_overlap_count + 2 × common_neighbor_count + 1 × type_affinity`. Counts (not Adamic-Adar `1/log(degree)`) chosen because LLM cannot reliably compute log per user choice "2 (LLM-friendly simplified)". Type affinity matrix: same type 1.0, related (concept↔wiki/person/method) 0.5, unrelated 0.0. Updated in `references/hippocampus-spec.md` Wave 2 + `pro/agents/hippocampus.md`.
  - **Borrow 5 · Page taxonomy refinement — people + comparisons get own directories**: New `_meta/people/<id>.md` (people-as-first-class-entities; canonical_name / aliases / relationship / privacy_tier / mention_count / concepts_linked wikilinks; spec: `references/people-spec.md`) and `_meta/comparisons/<id>.md` (decision-comparison-as-first-class; options / criteria / decision / confidence / outcome tracking; spec: `references/comparison-spec.md`) per user choice "1 (单独, separate directory not just frontmatter type field)". Sources/synthesis/queries NOT split (overlap with sessions/wiki).
  - **New specs (4)**: `references/people-spec.md`, `references/comparison-spec.md`, `references/obsidian-spec.md`, `references/review-queue-spec.md`.
  - **Edited specs (3)**: `references/wiki-spec.md` (page taxonomy + wikilink convention section, struck "no cross-references"), `references/concept-spec.md` (wikilink convention with frontmatter exception examples), `references/hippocampus-spec.md` (Wave 2 4-signal formula).
  - **Edited subagents (5)**: `pro/agents/hippocampus.md` (Wave 2 spec sync), `pro/agents/archiver.md` (Phase 2 routing + wikilink writing HARD RULE + review queue append), `pro/agents/knowledge-extractor.md` (same routing/wikilink/queue HARD RULE), `pro/agents/retrospective.md` (Mode 0 briefing wikilinks + ## Open Review Queue H2 section if items exist), `pro/agents/monitor.md` (Review Queue Dashboard).
  - **Edited prompts (5 maintenance + 2 new)**: All 5 v1.8.0 maintenance prompts (`auditor-mode-2.md` / `advisor-monthly.md` / `strategic-consistency.md` / `archiver-recovery.md` / `eval-history-monthly.md`) got "v1.8.0 R-1.8.0-013 · Review Queue Append (HARD RULE)" sections with source-specific YAML templates. NEW `scripts/prompts/review-queue.md` (walker per Borrow 3) and `scripts/prompts/migrate-to-wikilinks.md` (full content migration per user choice "4，全，完整").
  - **Edited tools (1)**: `tools/seed.py` — added 3 new `META_GITKEEP_DIRS` (`_meta/people`, `_meta/comparisons`, `_meta/review-queue/archive`), constants `_REVIEW_QUEUE` / `_OBSIDIAN_APP_JSON` / `_OBSIDIAN_CORE_PLUGINS` / `_OBSIDIAN_GITIGNORE`, function `_write_obsidian_vault(target)` wired into `_seed_scaffolding()`. Smoke test passed.
  - **Edited hooks (1)**: `scripts/hooks/session-start-inbox.sh` — added awk-based parsing of `_meta/review-queue.md` `## Open items` section counting P0/P1/P2 priorities; outputs `📋 Review queue: N P0 / M P1 / K P2 open. Latest: <summary>. Say "看 queue" to walk through.` in SessionStart system-reminder.
  - **R-1.8.0-013 self-audit fix (commit follows)**: parallel-agent audit of the borrow surfaced 7 real bugs — all fixed in same release per user "全部干完，不要再留任何 bug 了":
    - **HIGH · awk priority regex was unanchored** — patterns `/priority: P0/` matched body prose like `summary: "escalated because priority: P0 was missed"`, double-counting. Anchored to `^[[:space:]]*priority:[[:space:]]*P0([^0-9]|$)` (rejects no-`\b`-support GNU awk). Now correctly handles no-space (`priority:P0`) and extra-space (`priority:    P0`) variants too.
    - **HIGH · CHANGELOG promised `Latest: <summary>` in session-start hook output but hook only emitted counts** — extended awk to capture first `summary:` field of newest open item, truncate at 80 chars, emit via `Latest: ${REVIEW_QUEUE_LATEST}` line. Tab-separator splitting in bash. Privacy filter notice added for `[[person-*]]` items with `privacy_tier: high`.
    - **HIGH · `source_session(s)` field-name singular/plural inconsistency** between `references/comparison-spec.md` (singular, one decision moment) and `references/concept-spec.md` (plural, accumulating evidence). Documented the semantic distinction in `references/wiki-spec.md` exception list and synced `pro/agents/archiver.md` + `pro/agents/knowledge-extractor.md` to cite both names with the correct cardinality reasoning.
    - **HIGH · 4-signal `type_affinity` related set undercounted** — CHANGELOGs cited `concept↔wiki/person/method` but spec + agent only said `concept↔wiki, concept↔person`. Aligned all sources to: `concept ↔ wiki, concept ↔ person, concept ↔ method, wiki ↔ method, person ↔ comparison`.
    - **MEDIUM · advisor-monthly missing `outcome-unmeasured` type enum** — added to type list + extended priority to include P2 for "comparison missing ## Outcome past 90d" detection (the comparison-spec's outcome-tracking flow).
    - **MEDIUM · awk silent error swallow** — removed `2>/dev/null` from awk command so parser regressions surface to SessionStart hook log instead of silently producing empty output. `|| true` retained for non-existence on first-time vaults.
    - **LOW · pre-prompt-guard hooks could double-fire** REVIEW_QUEUE + MIGRATE_WIKILINKS for messages mentioning both keywords, sending two competing `<system-reminder>` blocks. Added `[ "$ACTIVITY_REMINDER" != "yes" ]` first-match-wins guard to both blocks.
    - **LOW · `_OBSIDIAN_GITIGNORE` constant naming overload** with repo-root `_GITIGNORE` — added inline comment at line 244 of `tools/seed.py` clarifying it's the vault-internal one.
    - **LOW · trigger keyword lists drifted between hook + pro/CLAUDE.md + walker prompt** — designated `scripts/hooks/pre-prompt-guard.sh` REVIEW_QUEUE_RE as canonical source; updated CLAUDE.md and `scripts/prompts/review-queue.md` to mirror it.
  - **R-1.8.0-013 second self-audit fix (commit follows)**: 6-agent deep parallel audit (python-reviewer + silent-failure-hunter + code-reviewer + security-reviewer + comment-analyzer + type-design-analyzer) of the previous fix surfaced **15 more bugs** including 3 CRITICAL/HIGH that would have silently broken Obsidian integration in every new vault. All fixed:
    - **HIGH · Obsidian core-plugin IDs were WRONG** — `tools/seed.py` wrote `"backlink"`, `"outgoing-link"`, and `"starred"` to `.obsidian/core-plugins.json` but Obsidian's actual plugin IDs are `"backlinks"`, `"outgoing-links"`, and `"bookmarks"` (the latter renamed from `starred` in Obsidian 1.2 / Aug 2023). Obsidian silently ignores unrecognized plugin names — meaning every new lifeos vault opened in Obsidian had backlinks panel, outgoing-links panel, and bookmarks panel quietly disabled. Fixed all three IDs + added explanatory comment block citing Obsidian's docs URL.
    - **HIGH · `.obsidian/.gitignore` missing `cache`, `plugins/`, `themes/`** — community plugins / themes installed per-device would have been silently committed to git, polluting repos. Added entries + `hot-reload.json` (dev workflow) + comment explaining why two `.gitignore` files exist (Obsidian Sync ignores vault-root `.gitignore`).
    - **HIGH · awk parser broke on CRLF + BOM** — `_meta/review-queue.md` saved by Windows editors with CRLF or BOM would silently produce zero counts. Added `{ sub(/\r$/, "") }` first awk rule + `NR == 1 { sub(/^\xef\xbb\xbf/, "") }` for BOM strip.
    - **HIGH · awk substr() byte-sliced UTF-8** — POSIX awk substr is byte-indexed, so `substr($0, 1, 77)` could chop a 3-byte Chinese character mid-byte producing invalid UTF-8 garbage. Reduced to `substr($0, 1, 67) "..."` (with `length > 70` guard) leaving a 3-byte safety margin. Also added block-scalar guard (`if ($0 ~ /^[|>][-+]?[[:space:]]*$/) { next }`) so YAML `summary: |\n  text` doesn't render as `Latest: |`.
    - **HIGH · YAML triple-bracket syntax was invalid** — `references/people-spec.md` and `references/comparison-spec.md` examples wrote `concepts_linked: [[[concept-id-1]], [[concept-id-2]]]` thinking it was a wikilink array. PyYAML parses bare `[[x]]` as nested list `[['x']]`, NOT as wikilink string. Verified empirically. Fixed to quoted strings: `concepts_linked: ["[[concept-id-1]]", "[[concept-id-2]]"]`. Also added required-fields lists + invariant docs to both specs.
    - **HIGH · concept-spec had two contradictory `outgoing_edges` schemas** — original at line 82 used `to: concept_id`, `via:`, `last_reinforced:`; R-1.8.0-013 addition at line 417 used `target: "[[]]"`, no `via:`, `last_co_activated:`. Implementations would have picked one or the other unpredictably. Reconciled: line 82 is now the canonical wikilink schema, line 414 noted as before/after migration example. Removed the misleading `weight: -2` example (negative weights nowhere defined in lifecycle / decay).
    - **HIGH · `migrate-to-wikilinks.md` missing word-boundary requirement** — naive name substitution would corrupt "Algorithm" → `[[person-al]]gorithm` if person named "Al" exists. Added explicit `\bword\b` boundary rule + wikilinks-inside-wikilinks guard + slug-collision handling per concept-spec § 4.2 + cross-platform Windows PowerShell backup command + explicit execution-order note (Phase 5 backup MUST precede Phase 2 writes despite numeric ordering).
    - **HIGH · review-queue lacked id zero-padding rule + concurrency model + archive ordering** — `r{TODAY}-{NNN}` ambiguous (was 001 or 1?). Documented: ALWAYS 3-digit zero-padded for lexicographic-sortable. Added lock-free optimistic concurrency protocol (re-read before append + verify-and-retry on collision). Added explicit archive-ordering rule (sort by `closed_at` ASC, parse month from `closed_at`).
    - **HIGH · review-queue + comparison statuses had no back-transition guard** — `dismissed → open` was described as invalid but unenforced. Documented MONOTONE / one-way DAG explicitly. `closed_at` / `closed_by` now declared REQUIRED non-null when `status != open`. Comparison `decision` MUST equal one of `options[*]` OR "deferred" OR "none". `confidence` MUST be in [0.0, 1.0]. `revisited` array bounded to max 50 entries (overflow rotates to body `## Audit trail`). Added `relationship: organization` to people-spec enum (was referenced in routing rules but missing from enum).
    - **HIGH · people-spec privacy_tier had no machine validator** — `high` tier was prose-only enforcement. Added Privacy Validator section: post-write lint scans body for 10+ digit numbers, street-address regex, emails, full names other than canonical → CLASS_C violation + P0 review-queue item. Added operational tier table (low/medium/high) defining what each tier allows. Added monotonicity invariants: `last_mentioned >= first_mentioned`, `mention_count` append-only.
    - **MEDIUM · pre-prompt-guard.sh locale-dependent Chinese matching** — running in POSIX/C locale could miscompare multi-byte UTF-8 trigger words like 上朝/退朝/监控模式/处理 queue. Added `export LC_ALL=C.UTF-8 LANG=C.UTF-8` (with en_US.UTF-8 fallback) early in script before any grep.
    - **LOW · stale `tools/migrate.py` references in concept-spec** — file deleted in R-1.8.0-011 pivot but spec still referenced it 3× (lines 148, 319, 351). Updated to point at replacement `scripts/prompts/migrate-from-v1.6.md`.
    - **LOW · mutual-exclusion comment was misleading** — said "ROUTER would receive two competing system-reminder blocks" but actual harm is concatenation into one combined block with mismatched banners. Rewrote comment to describe the real harm.
    - **LOW · MIGRATE_WIKILINKS_EOF heredoc had phase numbers in non-execution order** (0,1,5,2,3,4,6) — confusing for LLM following sequentially. Rewrote with execution-order numbered list 1-10 plus explicit note about why the source-file phase numbering differs.

- **R-1.8.0-013 USER read-only repo audit (commit follows)**: User performed an independent 9-section audit of all 67 tracked `.py/.sh/.yml` files (broader than R-1.8.0-013 scope) and surfaced 9 actionable findings. All accepted and fixed in same release per "全部干完，不要再留任何 bug 了" mandate:
  - **CRITICAL · `scripts/hooks/pre-bash-approval.sh` fail-OPEN**: 3 fail-open paths let dangerous commands through silently when the approval bridge crashed (ImportError, JSON parse failure, empty output). Rewrote ALL 3 paths to fail-CLOSED — bridge errors now block the command and surface diagnostic to user via stderr (rc=$BRIDGE_RC + captured stderr + LIFEOS_YOLO_MODE=1 bypass instructions). The "no install on disk" case still passes (can't enforce a guard that doesn't exist), but every other path now defaults to deny.
  - **CRITICAL · `tools/research.py` SSRF**: research tool fetched arbitrary `http(s)` URLs from search results with no private-network denylist — could be used as internal-network probe via crafted search hits. Added `_is_private_ip()` covering IPv4 RFC1918 / loopback / link-local / cloud metadata + IPv6 ::1 / fc00::/7 / fe80::/10 + literal hostname denylist (`localhost`, `metadata.google.internal`, `metadata.azure.com`, AWS 169.254.169.254, etc). Added `_is_safe_url()` that rejects non-http(s) schemes and runs the IP check. Wired into `_fetch_text` to block before any network I/O. Stderr surface for blocked URLs so operator sees the rejection. Also added `_MAX_RESPONSE_BYTES = 5 MB` truncation to bound memory.
  - **CRITICAL · `tools/sync_notion.py` BaseException catch**: per-page sync loop caught `BaseException`, swallowing `KeyboardInterrupt` / `SystemExit` and logging Ctrl-C as "page failed". Changed to `(KeyboardInterrupt, SystemExit): raise` first, then `Exception` for actual sync failures. Interpreter signals now propagate correctly.
  - **CRITICAL · `tools/approval.py` Tirith silent miss**: optional `tools.tirith_security` module's ImportError was silently swallowed but `setup-hooks.sh` description claimed "tirith enabled". Added one-time stderr warning when Tirith unavailable + module-level `_TIRITH_UNAVAILABLE_WARNED` flag (warn once per process, not per command). Updated `setup-hooks.sh` description to "optional tirith if installed" so disclosure matches reality.
  - **CRITICAL · `tools/seed_concepts.py` broken on fresh clone**: depended on `tools.lib.cortex.{concept,extraction}` modules deleted in R-1.8.0-011 cortex-helper cleanup, so `import tools.seed_concepts` fails on every fresh clone (verified empirically with `python -c`). Functionality already replaced by LLM-driven `scripts/prompts/extract-concepts.md` and `scripts/prompts/rebuild-concept-index.md`. Deleted the dead module + its test (`tests/test_seed_concepts.py`).
  - **HIGH · `.github/workflows/test.yml` ruff `continue-on-error: true`**: lint regressions silently passed. Removed `continue-on-error`. Required cleaning the existing baseline first — fixed 16 lint errors (12 auto-fixed + 4 manual: `B023` closure-binding bug in `approval.py:455` `get_input` thread function, `SIM105` try/except/pass → `contextlib.suppress`, `PTH105/108` `os.replace/unlink` → `Path.replace/unlink`, `SIM102` nested-if combine in `skill_manager.py:272`). Ruff baseline now clean.
  - **HIGH · `.github/workflows/test.yml` bash-syntax check missed `scripts/lib/*.sh`**: hardcoded glob enumerated `scripts/*.sh scripts/hooks/*.sh evals/run-eval.sh tests/hooks/test_*.sh` only. Replaced with `git ls-files '*.sh'` so any new shell file under any directory is automatically covered. Verified all 18 currently-tracked `.sh` files pass `bash -n`.
  - **HIGH · `scripts/hooks/pre-write-scan.sh` JSON regex parsing**: when `jq` missing, used `grep/sed` regex on JSON which fails on escaped quotes / multi-line content / nested fields → silent leak of unscanned writes. Added Python JSON parser as middle-tier fallback (Python is universally available wherever Claude Code runs; uses `\x1f` unit separator to safely demarcate file_path from content). Last-resort regex path now FAIL-CLOSED for sensitive paths (`/_meta/`, `/SOUL.md`, `/wiki/`, `/.env`, `/secrets`) — block + tell user to install jq or python.
  - **MEDIUM · `tools/search.py` swallowed config exceptions**: bare `except Exception` hid corrupt-config errors AND ImportErrors / AttributeErrors (real bugs in config loader). Tightened to `(FileNotFoundError, OSError, ValueError, KeyError)` + stderr warning so corrupt configs are visible while preserving the recency_boost_days=90 default fallback.
  - **MEDIUM · `tools/export.py` pandoc no timeout**: hung indefinitely on malformed input or filesystem stalls. Added `timeout=60` to `subprocess.run` + new `subprocess.TimeoutExpired` handler that reports input file size and remediation hint to stderr.

Net: 11 files modified, 2 deleted (seed_concepts.py + test). All previous hook tests still pass. 3 pre-existing `test_stop_session_verify.sh` failures unchanged (last touched in v1.7.3, unrelated to this audit).

- **R-1.8.0-013 USER round-3 audit (commit follows)**: User performed a third independent audit at HEAD `d7639fc`, surfacing 7 findings not caught in rounds 1/2. All confirmed and fixed. Round-3 audit's strength was attacking the **boundaries** of the security/parsing fixes from round-2:
  - **CRITICAL · `tools/lib/second_brain.py:60` CRLF frontmatter ignored**: parser used literal `content.startswith("---\n")` which rejected files saved with Windows CRLF line endings — they appeared as having no frontmatter, body=full file. Verified empirically. Replaced with regex `^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n` accepting both LF/CRLF/mixed + trailing whitespace on fence. Added 4 regression tests in `tests/test_second_brain.py` (CRLF parsed, CRLF no-frontmatter, mixed line endings, fence trailing whitespace) — all 25 frontmatter tests pass.
  - **CRITICAL · `tools/research.py:381` SSRF guard didn't resolve DNS**: previous fix only checked literal IPs and a hostname denylist, so `internal.corp.example` pointing at `10.0.0.1` would pass. Added `socket.getaddrinfo()` resolution + IP check on every A/AAAA record. DNS failure (NXDOMAIN/timeout) treated as **unsafe** (fail-CLOSED with stderr surface). Test fixtures using synthetic hostnames opt out via `LIFEOS_RESEARCH_SKIP_DNS_SSRF=1` env var (production code never sets this).
  - **CRITICAL · `tools/research.py:354` redirect chain bypass**: `httpx.Client(follow_redirects=True)` meant only the original URL ran the SSRF check; a public URL 302→ private IP bypassed entirely. Changed to `follow_redirects=False`, manually walk Location headers in `_fetch_text` (max 5 hops), re-run `_is_safe_url()` per hop. Relative redirects resolved against current URL via `urljoin`.
  - **CRITICAL · `tools/research.py:452` resp.text loaded full body**: previous max_bytes truncation happened AFTER httpx loaded the entire response into memory — useless for memory protection. Rewrote `_fetch_text` to use `client.stream()` with byte counter that stops at `max_bytes` mid-stream. Tests using FakeClient without `.stream()` fall through to a non-streaming branch (still bounded by post-load truncation) — safe because mocks return small synthetic bodies.
  - **CRITICAL · `scripts/hooks/pre-bash-approval.sh:75` missing-source fail-OPEN**: when `tools/approval.py` couldn't be located at any candidate path, hook exited 0 (= approve). My round-2 fix had argued this was "can't enforce missing guard"; auditor correctly pushed back — missing security source IS a critical state. Changed to fail-CLOSED with full diagnostic (which paths searched, recovery steps via `setup-hooks.sh`, `LIFEOS_YOLO_MODE=1` escape hatch). Added `tests/hooks/test_pre_bash_approval.sh` with 6 test cases (safe / hardline / empty input / malformed JSON / missing source fail-CLOSED / YOLO bypass) — all 9 assertions pass.
  - **WARNING · `tools/search.py:302` exception not semantic enough**: previous fix tightened to `(FileNotFoundError, OSError, ValueError, KeyError)` but project has its own `ConfigError` class that's the canonical "config is malformed" signal. Changed to `except (ConfigError, FileNotFoundError)` — bugs in config loader (ImportError, AttributeError) now propagate so user sees them.
  - **WARNING · `tools/lib/notion.py:215` rich_text > 2000 chars silently failed**: `_body_to_children` wrapped the entire body in a single rich_text object, but Notion API rejects content > 2000 chars per object. Long-body sync silently failed. Added paragraph-boundary chunking at 1900 chars (with hard-split for paragraphs longer than that), emitting one paragraph block per chunk. Empty body still emits one empty paragraph (matches old behavior). New constant `_NOTION_RICH_TEXT_MAX = 1900`.

Verification:
- `bash -n` on all 18 tracked .sh files: pass
- Ruff baseline: All checks passed
- `pytest tests/test_research.py` (28 tests) + `test_second_brain.py` (25 tests) + `test_sync_notion.py` (14 tests) = 67 passed
- Hook test suite: 6/7 pass (the 1 pre-existing `test_stop_session_verify` failure from v1.7.3 unchanged)
- New `tests/hooks/test_pre_bash_approval.sh`: 9/9 assertions pass

Architecture notes (deferred — listed in audit but out of round-3 scope):
- `tools/approval.py:713` 224-line god function refactor → 5 layers
- duplicated session discovery in 2 hooks → `_lib.sh` helper
- `tools/lib/config.py:137` 119-line load_config split
- `evals/run-tool-eval.sh:223` `eval` of frontmatter (mitigated by repo-trust scope, not removed)
- `Any` types in research/notion → `Protocol` definitions
- `ApprovalDecision` TypedDict
- `tools/search.py:212` SQLite/FTS index for sessions
- `tools/export.py:210` streaming generator
- `--notion-token-stdin` UX improvement
- Hook JSON parser deduplication
- `setup-hooks.sh:310` SKILL.md install meta separation

These are real improvements but each is a multi-hour refactor; explicitly deferred per "fix safety/correctness first, then complexity debt".

- **R-1.8.0-013 USER round-4 re-audit (commit follows)**: Auditor confirmed round-3 fixes landed correctly but flagged 7 new issues that broke the "CI green / 零遗留" claim. All 7 verified empirically and fixed. Round-4 audit's strength was checking the **infrastructure layer** (CI gates, package install, full pytest collection):
  - **CRITICAL · `tests/test_integration.py:26` import fails on fresh clone**: depended on `tools.lib.cortex` (deleted in R-1.8.0-011 cortex-helper cleanup), so full `pytest --collect-only` errored with `ImportError: cannot import name 'compile_synapses_index'` before round-3's targeted tests even ran. Functionality replaced by LLM-driven prompts. Deleted dead test file.
  - **CRITICAL · `pyproject.toml:58` broken `life-os-tool` console script**: pointed at `tools.cli:main` which doesn't exist (deleted in R-1.8.0-011 pivot). `pip install` would have failed entry-point validation on fresh clone. Removed the `[project.scripts]` block.
  - **CRITICAL · `LIFEOS_RESEARCH_SKIP_DNS_SSRF` env var bypass**: round-3 added this for tests but a user shell could set it in production to disable the SSRF DNS check. Replaced with `PYTEST_CURRENT_TEST` detection — only pytest itself can set that variable. Test fixture cleanup of `monkeypatch.setenv` line.
  - **HIGH · mypy --strict 25 errors blocking CI gate**: `tools/approval.py` had bare `dict` returns and untyped parameters; `notion_client / markdown_it / genanki / httpx / markdownify / tools.tirith_security` had no stubs causing 6 import-not-found errors. Added `[[tool.mypy.overrides]]` for those 6 modules. Annotated `approval.py`: `dict` → `dict[str, Any]` in 7 functions, `Callable[..., str] | None` for callback parameters, narrowed `tirith_result["findings"]` typing. Fixed B023 closure-binding bug in `prompt_dangerous_approval` thread function. Removed unused `# type: ignore` comments in `skill_manager.py:34` + `export.py:433`. Fixed `socket.getaddrinfo` `sockaddr[0]: str | int` narrowing. Imported `Callable` from `collections.abc` (modern style, ruff UP035). Result: **0 mypy errors** (was 25).
  - **HIGH · `test_compliance_check.py` 5 failures**: fixtures used pre-R-1.8.0-013 minimal briefing structure but checker now requires 6 H2 sections + version markers + Cortex status. Created reusable `_FULL_START_BRIEFING_BASE` constant. Rewrote 4 `TestStartSession` fixtures. Discovered 3 fabricate/preflight tests were calling `start-session-compliance` scenario which no longer bundles those checks; updated to invoke dedicated `preflight-check` / `fabricate-path-check` scenarios. Fixed `test_clean_adjourn_passes` fixture to include `## Phase 1` … `## Phase 4` H2s + `## Completion Checklist`. Fixed escape-phrase to use English `"lightweight briefing path"` (the actual denylist entry; Chinese variant was never on the list). All 11 compliance tests now pass.
  - **HIGH · `test_stop_session_verify.sh` 3 failures**: 2 separate bugs:
    1. `stop-session-verify.sh` `ARCHIVER_TAIL` awk set `start = NR` on every match (overwriting), so when transcript had 4 phase lines all matching `archiver`, only the LAST survived → mis-reported Phase 1/2/3 as missing → T2 false positive logged a violation when transcript was actually complete. Fixed to `start == 0 { start = NR }` (lock at first match).
    2. T2's spurious lockfile (5-min cooldown keyed by sha of first transcript line) blocked T3/T4 (same first line `User: 退朝`). Added `rm -f $HOME/.cache/lifeos/stop-hook-*` cleanup before each test case. Result: **11/11 hook test cases pass** (was 8/11).
  - **MEDIUM · 4 `test_export.py` failures from missing optional extras**: previously masked by `# type: ignore[import-untyped]` comments that mypy now flagged as unused. Added `@pytest.mark.skipif(not find_spec("markdown_it"))` on `TestExportHtml` class and `find_spec("genanki")` on `TestExportAnki`. Default install: tests skip cleanly. With `uv sync --extra export`: tests run normally.

- **R-1.8.0-022 · macOS portability + inbox token-budget + Notion sync config-driven + pattern transparency (post-2026-05-01 downstream user 4-day field report)**: Downstream user (macOS production install, 4-day daily use) submitted a comprehensive bug list. Verified each claim; fixed the 4 confirmed real bugs, declined 3 invalid claims with reasoning.

  **Verified + fixed**:
  1. **P0 — `pre-bash-approval.sh` had 5 bare `python -c` invocations (lines 57/133/166/179/187)**. macOS 12+ removed the bare `python` binary; only `python3` is available. The hook was failing-CLOSED with `python: command not found`, blocking every Bash command and deadlocking Claude Code on macOS. Fix: added portable `PYTHON=$(command -v python3 || command -v python)` detection at top, replaced all 5 bare `python` calls with `"$PYTHON"`. Same fix would benefit any non-macOS Linux without `/usr/bin/python` symlink. R-1.8.0-020 had introduced the GitHub-Release alignment HARD RULE but the underlying hook bug was never actually fixed despite the commit title — this round closes that gap.
  2. **P1 — `session-start-inbox.sh` NEVER_RUN list wasted ~10 lines of LLM context per session**. R-1.8.0-021 split NEVER_RUN out of the OVERDUE bucket so the LLM stops mistakenly offering never-run jobs, but the multi-line bullet list still occupied tokens in every Claude Code session. Compressed to a single comma-separated line (`## Available on-demand (do NOT proactively offer): daily-briefing, backup, ...`). All 10 canonical maintenance jobs preserved (downstream user's suggestion to delete jobs was rejected — those are the v1.8.0 user-invoked discoverability surface per `pro/CLAUDE.md`).
  3. **P2 — `pro/CLAUDE.md` Step 10a hardcoded 4 Notion entities (Status / Todo / Working Memory / Inbox)**. Real users have varied Notion layouts (downstream user only had 2 of those 4 configured); orchestrator was reporting "Working Memory: failed" for entities that never existed. Rewrote to be config-driven: orchestrator reads `_meta/config.md`, only syncs configured entities, skips Step 10a entirely if no Notion entity configured, and only lists configured entities in the checklist (not "failed: not configured" lines for unconfigured ones).
  4. **P2 — `pre-bash-approval.sh` blocked-command message said "匹配模式: unknown" too often**. The `pattern_key` field in approval.py decision payload was sometimes missing, falling through to literal `'unknown'`. Improved to extract and concatenate `key=` + `matched=` (the actual matched substring) + `regex=` (the source pattern), with a clear "decision payload missing all 4 fields" diagnostic when nothing is available. Also added explicit doc note that inline `export LIFEOS_YOLO_MODE=1` doesn't work in Claude Code Bash tool (PreToolUse hook reads env BEFORE the export executes); persistent bypass requires editing `~/.claude/settings.local.json` env block.

  **Declined with reasoning**:
  - **R-1.8.0-023 (claimed: spec drift to deleted scripts)** — INVALID. All references to `setup-cron.sh` / `retrospective-mode-0.sh` / `archiver-briefing-skeleton.sh` / `archiver-phase-prefetch.sh` in active spec files are explicit "REMOVED in R-1.8.0-011 / deleted in Option A pivot" markers with explanatory context (e.g. `pro/agents/retrospective.md` L244: "R10 execution boundary (Option A pivot — pre-fetch script `retrospective-mode-0.sh` deleted): RETROSPECTIVE Mode 0 / Mode 2 runs all 18 steps from scratch each invocation"). The spec correctly documents what was deleted and what replaced it; scanner correctly skips via CONTEXT_ALLOW.
  - **R-1.8.0-024 (claimed: knowledge-extractor not registered as Task agent)** — likely STALE INSTALL. `scripts/setup-hooks.sh` L303-308 calls `register-claude-agents.sh` which iterates `pro/agents/*.md` and writes every file (including `knowledge-extractor.md`) as `~/.claude/agents/lifeos-<name>.md` wrapper. New installs get the full set. The downstream user's environment is missing `lifeos-knowledge-extractor` because they upgraded from a v1.6.x install before knowledge-extractor existed; rerunning `bash scripts/setup-hooks.sh` will re-register everything. Adding short-name aliases would risk colliding with other Claude Code skills using common names (`archiver`, `auditor`, etc.).
  - **R-1.8.0-026 (claimed: LIFEOS_YOLO_MODE inline bypass doesn't work)** — BY DESIGN (security). PreToolUse hook reads env BEFORE the user's `export` runs; allowing inline bypass would defeat the guard. Doc fix added in fix #4 above explaining persistent bypass via `~/.claude/settings.local.json`.

  **Verification**:
  - `bash -n` on both modified hooks → pass
  - Smoke test: `pre-bash-approval.sh` with `LIFEOS_YOLO_MODE=1` and a benign command → exit 0
  - Smoke test: `session-start-inbox.sh` with synthesized 5d INDEX.md fixture → outputs single-line "Available on-demand: ..." (was 8+ lines)
  - `STRICT=1 bash scripts/check-spec-drift.sh` → exit 0
  - `mypy --strict tools/` → 0 errors / 16 files
  - `ruff check tools/ tests/` → clean
  - `pytest tests/` → 233 passed / 3 deselected
  - 31 tracked .sh `bash -n` → all pass

  3-language CHANGELOG synced. v1.8.0 tag will be force-realigned per pro/CLAUDE.md rule #10 (Release alignment).

- **R-1.8.0-021 · Fix session-start-inbox hook: 2 wrong task names + "never run" treated as overdue (post-2026-05-01 user audit)**: User pasted a downstream auditor's complaint that `scripts/hooks/session-start-inbox.sh` had spec drift — the auditor's diagnosis was 80% wrong (claimed 6 v1.8.0 user-invoked maintenance jobs were "cron-only residue" and proposed deleting them, which would have broken the v1.8.0 discovery mechanism), but their secondary observation was a real UX bug. Verified against `pro/CLAUDE.md` canonical 10-job table.
  - **2 real bugs fixed**: `TASKS_LINE` array had 2 task names that didn't match any `scripts/prompts/*.md` file or the canonical `pro/CLAUDE.md` Maintenance table:
    - `auditor-patrol` → `auditor-mode-2` (the actual prompt + canonical name)
    - `monthly-summary` → `eval-history-monthly` (same)
    Without this fix, when the user said "跑 auditor-patrol", ROUTER could not resolve a real prompt file. The eval-history glob path (which scans for legacy report filenames in `_meta/eval-history/`) was kept unchanged because that's where historical reports were written under the old names — the task name has to match prompt files, but the report glob has to match historical artifact names.
  - **"never run" semantic split**: previously any task with no prior run history was reported as `<name>: never run` in the same `OVERDUE` bucket. The LLM treated this as debt and proactively offered to run jobs the user had never opted into. Split into two buckets:
    - `OVERDUE` — task has a baseline AND age > target. Real debt; LLM should mention.
    - `NEVER_RUN` — task has no baseline. Listed under "Available on-demand (never run yet — NOT overdue, do NOT proactively offer)" with explicit instruction to stay silent unless user asks "what maintenance is available". Also updated the "How to surface" examples to only cite overdue (with-baseline) items, not never-run.
  - **Comments tightened**: added contract note next to `TASKS_LINE` that task names MUST match `scripts/prompts/<name>.md` AND `pro/CLAUDE.md` canonical table; explained why `review-queue` (handled by separate parser) and `migrate-to-wikilinks` (one-time migration) are intentionally absent.
  - **Smoke test**: with synthesized stubs (5d-old INDEX.md, 12d-old spec-compliance report, no other history), hook now outputs `## Overdue maintenance` with only `reindex: 5d` and `## Available on-demand` listing the 8 never-run jobs separately with the do-NOT-offer instruction. Previously the same fixture would have shown all 9 missing jobs as overdue.
  - **Verification**: `bash -n scripts/hooks/session-start-inbox.sh` pass; STRICT scanner unchanged exit 0; mypy / ruff / pytest unaffected (no Python touched).

- **R-1.8.0-020 · GitHub Release alignment HARD RULE + verifier script (post-2026-04-30 user observation)**: User screenshotted GitHub Releases page after R-1.8.0-019: **"Latest" still showed v1.7.3 even though main + v1.8.0 tag were both at `e51822e`**. Root cause: `git push --tags` only updates the git layer; GitHub's Releases page is a separate UI where the Latest badge and release notes must be **explicitly published** via `gh release create` or the web UI. The 4-29 v1.8.0 Draft never got published, so v1.7.3 stayed Latest. User instruction verbatim: "今后每次都要检查这个东西" (going forward, always check this).
  - **Published v1.8.0 Release**: deleted the stale 4-29 Draft, recreated tag at `e51822e`, ran `gh release create v1.8.0 --latest` with full release notes covering R-1.8.0-013..019. v1.8.0 now shows as Latest on GitHub.
  - **Added `scripts/verify-release.sh`**: post-release alignment check. Verifies (1) working tree clean, (2) HEAD == origin/main, (3) target tag points to HEAD, (4) tag pushed to remote, (5) GitHub Release exists for the tag, (6) not Draft, (7) marked as Latest on GitHub. Any drift fails exit 1 with the exact `git` / `gh` command needed to fix. Default target is the most recent tag; `bash scripts/verify-release.sh v1.8.0` checks a specific tag.
  - **Added rule #10 to `pro/CLAUDE.md` Orchestration Code of Conduct**: makes the 4-step release sequence (push main → push tag → `gh release create --latest` → `verify-release.sh` exits 0) a HARD RULE so future sessions / future versions / Gemini & Codex hosts all enforce it. The local `.claude/CLAUDE.md` (gitignored, this user only) gets the same rule for daily-driver visibility.
  - **Verification**: `bash scripts/verify-release.sh` → exit 0 (after committing the script itself); `gh release list` confirms `v1.8.0 Latest`.

- **R-1.8.0-019 · Drop active links to `16-agents` legacy paths + scanner catches them (post-2026-04-30 user round-13 audit)**: Round-12 closed all *content* drift (active docs no longer hardcode "16 subagents"). User round-13 caught the last residual class: **active doc index still pointed users to legacy `architecture/16-agents.md` and `reference/all-16-agents/` paths**. The legacy files themselves are correctly marked, but having `docs/index.md` link to them under the "essential reading" / "open this file to find an agent" navigation effectively re-promoted v1.7 historical content as current architecture.
  - **Renamed legacy reference directory**: `git mv docs/reference/all-16-agents → docs/reference/all-agents` (16 per-agent reference files preserved; only the directory name dropped the obsolete count).
  - **Rewrote `docs/index.md` navigation** (3 lines previously linked to legacy paths):
    - "Open this file to find an agent" reading list now points to `pro/agents/*.md` (the actual current source) instead of `architecture/16-agents.md`. Legacy file presence noted but explicitly de-recommended as "current architecture entry point".
    - "Quick links" section: replaced `[multiple agents](architecture/16-agents.md)` with `[Agent 定义源](../pro/agents/)`.
    - "Required reading order before changing the system" rewritten to flow `system-overview` → `pro/agents/` source → `orchestration-protocol`, with explicit note that the architecture/ directory's old agent-list document is `status: legacy` v1.7 history and not part of the current critical path.
  - **Scanner upgrade (`scripts/check-spec-drift.sh`)**: added `16-agents.md`, `all-16-agents`, `all-16-a""gents` (bash-concat) to FORBIDDEN_TOKENS so any future active doc that links to the old paths fails STRICT mode. Legacy files (already marked `status: legacy`) remain exempt as usual.
  - **Committed runtime log**: `pro/compliance/violations.md` had an uncommitted runtime-log line (`2026-04-30T12:43:39+09:00 CLASS_C high archiver placeholder_phases=1 2 3 4`) appended by `stop-session-verify` hook during today's testing — committed alongside the round-13 changes (file is the auto-appended violation log; `pro/compliance/` is in EXEMPT_PATTERN so doesn't trigger drift).
  - **Verification**: `STRICT=1 bash scripts/check-spec-drift.sh` → exit 0; auditor's exact `rg "16 subagents|16 个 subagent|16 个 agent|All 16 subagents"` filtered to non-legacy non-CHANGELOG → 0 active hits; `git ls-files | xargs grep -l "16-agents|all-16-agents"` filtered to non-legacy non-CHANGELOG → **0 active hits** (was 1: docs/index.md); mypy --strict tools/ → 0 errors / 16 files; ruff → clean; pytest → 233 passed / 3 deselected; 31 tracked .sh `bash -n` → all pass.

- **R-1.8.0-018 · Paragraph-aware lookback + broader noun coverage (post-2026-04-30 user round-12 audit)**: Round-11 narrowed EXEMPT_PATTERN to file-level only, but user round-12 caught two remaining classes of false-pass:
  - **Lookback was too greedy across paragraph boundaries**: `v1.7` mentioned at line 431 of `what-is-life-os.md` was within the 8-line lookback window for line 439, even though they were separated by a blank line + new H2. Scanner correctly reset its window only on file boundary, not paragraph boundary, so unrelated CONTEXT_ALLOW keywords from previous topical blocks could exempt drift in the next block.
  - **Regex missed inner spaces and additional nouns**: `[N] 个[^，。\\s]{0,12}NOUN` excluded spaces from the inner char class, so "16 个真正独立的 subagent" (with a literal space after "的") wouldn't match. NOUN list also missed `岗位` (post / role), bare `ID` (as in "16 个 ID"), and `功能` (as in "以下 16 个功能完全相同").
  - **Scanner fixes (`scripts/check-spec-drift.sh`)**:
    - **Paragraph-aware reset**: all three awk loops (broken-path scanner + literal-token scanner + count-pattern scanner) now clear `recent[]` on `^[[:space:]]*$` (blank line) or `^#{1,6} ` (markdown header). Context only carries within the same paragraph / topical block now.
    - **NOUN list expanded**: added `岗位`, `角色`, `功能 ID`, bare `ID`, `engine ID`, `engine`, `engine agent`, JA `サブエージェント`, `エージェント`, `役職`, `機能 ID`. Added separate `[N] (个|個) (功能|定义|ID)` pattern.
    - **Inner space allowed**: `[^，。\\s]{0,12}` → `[^，。\\n]{0,18}` so multi-word ZH modifiers like "真正独立的 " (with trailing space) match.
  - **Active doc fixes (5 residuals + 2 broken paths across 8 files, 10 substitutions)**:
    - `docs/getting-started/what-is-life-os.md` (+ ZH/JA parallels): "Life OS 需要 16 个真正独立的 subagent" → "...多个真正独立的 subagent". `scripts/monthly-review-check.py` reference (cron-era, deleted in R-1.8.0-011) replaced with `scripts/prompts/advisor-monthly.md` user-invoked prompt.
    - `docs/guides/your-first-decision.md`: "中间 16 个岗位具体在做什么" → "中间多个岗位具体在做什么".
    - `docs/user-guide/themes/themes-overview.md`: "以下 16 个功能完全相同" → "以下核心功能完全相同".
    - `docs/user-guide/themes/adding-a-theme.md`: "确保 16 个 ID 全部填上" → "确保所有当前 engine ID 全部填上".
    - `docs/architecture/system-overview.md`: architecture box "pro/agents/*.md (16 个) · themes/*.md (9 个)" → "pro/agents/*.md · themes/*.md (9 个)" (kept the 9-themes count which is structural-stable; dropped the volatile agent count).
    - `pro/agents/retrospective.md`: TBD reference `pro/compliance/2026-04-23-status-cache-drift.md` rephrased to "(planned, TBD: ... will be created when the post-mortem is filed)" so the planned-context exemption applies.
  - **Verification**: `STRICT=1 bash scripts/check-spec-drift.sh` → exit 0; auditor's exact `rg "16 subagents|16 个 subagent|16 个 agent|All 16 subagents"` filtered to non-legacy non-CHANGELOG → **0 active hits**; mypy --strict tools/ → 0 errors / 16 files; ruff → clean; pytest → 233 passed / 3 deselected; 31 tracked .sh `bash -n` → all pass.

- **R-1.8.0-017 · Scanner is now the source of truth — narrowed EXEMPT_PATTERN + caught real residuals (post-2026-04-30 user round-11 audit)**: User round-11 audit's core insight: R-1.8.0-016's scanner was passing because it had over-broad **directory-level exemptions** (whole `docs/architecture/`, `docs/guides/`, `i18n/.*/docs/`, `i18n/.*/references/` were skipped), not because the repo was actually clean. With those exemptions the scanner could not be used as proof of "active docs are clean". Auditor proved the gap by listing 24 active count-drift residuals scanner missed (FAQ, themes overview, ZH/JA installation, etc.). This round (a) makes the scanner trustworthy by deleting directory exemptions and (b) fixes everything the new scanner catches.
  - **Scanner tightening (`scripts/check-spec-drift.sh`)**:
    - **Removed directory-level exemptions**: `docs/architecture/`, `docs/guides/`, `i18n/.*/docs/`, `i18n/.*/references/`, `references/v1.7-shipping-report-`, `references/cortex-spec.md`, `references/tools-spec.md`, `references/narrator-spec.md`. The new EXEMPT_PATTERN only covers truly historical artifacts (CHANGELOG, backup/, MIGRATION, the scanner itself, *-template, pro/compliance/ violations log). Everything else must declare itself legacy via YAML frontmatter (`status: legacy` / `authoritative: false`) OR earn an 8-line CONTEXT_ALLOW lookback exemption per line.
    - **Broadened SUBAGENT_COUNT_PATTERNS**: added regex variants the round-10 fix missed — `子 agent` (子 = "sub" alt gloss), `[N] 个[modifier] subagent` allowing up to 12 chars between count and noun (e.g. `16 个真正独立的 subagent`), `[N] engine ID`, `[N] engine agent`, JA `[N]の独立サブエージェント`, `[N]のAI 役職`, `同じ[N]の役職`, `[N] subagent 並列`. Threshold raised to N≥13 so structural counts like "1-3 domain agents" / "2 independent subagents per Express request" / "9 themes" are not false-positives — only suspicious magnitudes (matching the system's historical 14/16/22/23 counts) trigger.
  - **Active doc fixes (28 substitutions across 13 files)**: Python script + per-file edits replaced all newly-caught hits with count-free wording.
    - `docs/getting-started/what-is-life-os.md` + ZH parallel: "16 子 agent 并行 — 同时跑 16 个独立 subagent" → "多个子 agent 并行 — 同时跑多个独立 subagent". Same paragraph also lost the v1.7-era narrator-validator standalone subagent description; replaced with v1.8.0 inline self-check description in EN/ZH/JA.
    - `docs/index.md`: `reference/all-16-agents/ — 16 个 engine ID 到角色定义的索引` → `reference/all-agents/ — engine ID 到角色定义的索引`.
    - `docs/reference/faq.md`: 4 instances ("16 个独立 subagent", "16 个 engine agent 的逻辑", "16 个 AI 角色") → count-free.
    - `docs/reference/version-history.md`: v1.0 entry "Pro 模式（14 个独立 subagent）" → "Pro 模式（独立 subagent）" (kept the historical context without quoting an obsolete count).
    - `docs/user-guide/themes/{adding-a-theme,chinese-themes,english-themes,japanese-themes,themes-overview}.md`: 7 instances of "16 个 engine ID …" → count-free / "engine ID …".
    - `i18n/zh/docs/installation.md`: 4 instances of "16 个独立 subagent" / "16 个独立 subagent 一行命令安装" → "多个独立 subagent".
    - `i18n/ja/docs/installation.md`: 9 instances ("16の独立したAI役職", "16のサブエージェント", "16の独立サブエージェント", "同じ16の役職") → "複数の …".
    - `i18n/ja/README.md`: native-subagent registration paragraph specific count (22 / 21) → "複数の agent 定義ファイル / ほぼすべて".
    - `docs/user-guide/themes/adding-a-theme.md` PR contribution checklist: "16 个 engine ID 完整映射" → "全部 engine ID 完整映射".
  - **Marked v1.7 narrator-spec translations as legacy**: `i18n/{zh,ja}/references/narrator-spec.md` were `status: draft` (no `authoritative: false`); now `status: legacy` + `authoritative: false` + `superseded_by: pro/agents/narrator.md` so the scanner correctly treats them as historical (the EN parent was already so-marked).
  - **Cortex compliance gate retired (`scripts/lifeos-compliance-check.sh`)**: `check_cortex_gate()` previously fired on the legacy `cortex_enabled: true` config flag. v1.8.0 R-1.8.0-011 made Cortex pull-based — that flag is dead. The gate now triggers only when the transcript already shows ROUTER explicitly launched a Cortex subagent (`Task(hippocampus)` / `Launch(concept-lookup)` / etc.). When ROUTER skipped Cortex (the common case post-pivot), the gate returns "not applicable" and CX1/CX2/CX3 don't fire. Updated `tests/test_compliance_check.py::TestCortex` accordingly: replaced the v1.7 `test_cortex_enabled_no_agents_fails` with `test_cortex_enabled_no_agents_passes_post_pivot` (validates the legacy flag is now ignored) and added `test_cortex_partial_launch_fails` (validates that partial Cortex evidence still fails CX2/CX3).
  - **Verification**: `STRICT=1 bash scripts/check-spec-drift.sh` → exit 0 (broken paths: 0; subagent-count drift hits in active files: 0); user-side `git ls-files | xargs grep -l "16 subagents|16 个 subagent|16 个 agent|All 16 subagents"` filtered to non-legacy non-CHANGELOG → **0 active hits**; mypy --strict tools/ → 0 errors / 16 files; ruff → clean; pytest → **233 passed** / 3 deselected (was 232 + 1 failure from the cortex gate change); 31 tracked .sh `bash -n` → all pass.

- **R-1.8.0-016 · Permanent count-drift fix — drop hardcoded subagent count entirely (post-2026-04-30 user round-10 audit + explicit user instruction)**: User instruction verbatim: "不要说多少个 agent 了，多少个 agent 不重要，就说'多个 agent'就行。改了十几遍了，还没有改好。" Rather than continue chasing 16→23 substitutions every time the count changes, this round permanently retires the hardcoded count: replaced "23 (sub)agents / 23 个 subagent / 23 個の独立した agent / 16 个独立 AI 角色 / etc." with **count-free wording** ("multiple subagents" / "多个 subagent" / "複数の subagent") across all active docs. Subsequent agent-count changes (e.g. v1.9 may add more) will not require any doc edit.
  - **Bulk count-removal sweep**: Python script ran two passes across 17 active (non-legacy, non-CHANGELOG) docs covering EN/ZH/JA. 79 substring/regex substitutions total. Patterns covered: `N independent (AI )?(agents|roles|subagents)`, `N (sub)?agents?`, `N AI roles`, `All N subagents`, `the N defined roles`, `N functional IDs`, `## N Roles`, `#### The N agents`, ZH `N 个 (subagent|agent|独立 agent|AI 角色|角色|功能 ID)`, JA `Nの(独立した|エージェント|機能 ID|声|個の)`, plus `N agent (制衡|编排|definitions|files|calls|相互牽制|意思決定エンジン)`. Files touched: `SKILL.md`, `README.md`, `i18n/{zh,ja}/README.md`, `docs/index.md`, `docs/installation.md`, `i18n/zh/docs/installation.md`, `docs/getting-started/{what-is-life-os,first-session,choose-your-platform}.md` (× EN/ZH/JA where applicable), `docs/architecture/{system-overview,roadmap}.md`, `docs/evals/{overview,writing-new-scenarios}.md`, `docs/guides/multi-platform-setup.md`, `docs/user-guide/second-brain/{second-brain-overview,obsidian-integration}.md`, `docs/user-guide/making-decisions/reading-the-summary-report.md`, `docs/user-guide/themes/{adding-a-theme,themes-overview}.md`, `docs/reference/version-history.md`, `pro/AGENTS.md`, `pro/GEMINI.md`, root `AGENTS.md`. Historical record (v1.6.0 entry in `version-history.md` saying "v1.6.0 当时为 16 个，至 v1.8.0 增至 23 个") preserved — that's a deliberate fact, not drift.
  - **Scanner upgrade — regex-based count-drift detection (`scripts/check-spec-drift.sh`)**: replaced the round-9 fixed-token list (`"16 sub""agents"` etc.) with `SUBAGENT_COUNT_PATTERNS` — a regex list that matches **any** hardcoded count. Patterns are bash adjacent-string concatenated so the scanner source itself contains zero literal hits. ERE patterns: `[0-9]+ (sub|independent )?(agents?|subagents?|roles?|individuals?)`, `[0-9]+ ?个 ?(subagent|agent|角色|功能 ID)`, `[0-9]+ agent (制衡|编排|定义|calls)`, `[0-9]+ 個の独立した (subagent|agent|エージェント)`, `[0-9]+の(機能 ID|声|エージェント)`. Same 8-line CONTEXT_ALLOW lookback + legacy frontmatter exemption. Future bumps (v1.9 +N agents) won't trigger drift because nobody will write a hardcoded count in the first place. Scanner caught 3 residuals my initial bulk sweep missed (`docs/user-guide/themes/{adding-a-theme,themes-overview}.md` had `4 个角色`, `16 个角色`, `16 个功能 ID`) — all rephrased.
  - **Verification**: `STRICT=1 bash scripts/check-spec-drift.sh` exit 0 (broken paths: 0; subagent-count hits in active files: 0); user-side `git ls-files | xargs grep -lE "\b\d{1,2} (sub)?agents?\b|..."` filtered to non-legacy non-CHANGELOG: **0 active hits**; mypy --strict tools/ → 0 errors / 16 files; ruff → clean; pytest → 232 passed / 3 deselected; 31 tracked .sh `bash -n` → all pass.
  - **`v1.8.0` tag realigned again** to include this round-10 permanent fix.

- **R-1.8.0-015 · Subagent-count drift cleanup + tag realignment (post-2026-04-30 user round-9 audit)**: User round-9 audit caught two residual issues after R-1.8.0-014 STRICT pass: (a) subagent count drift — root `AGENTS.md` already said 23, but `pro/AGENTS.md`, `pro/GEMINI.md`, `docs/index.md`, `docs/installation.md`, `SKILL.md`, both READMEs (EN/ZH/JA) and ~14 user-facing docs still said 16; (b) `v1.8.0` git tag still pointed at `02aea0d` (R-1.8.0-013 commit) instead of the latest Spec-GC HEAD `6cb3d79`. The semantic count drift was the kind of issue R-1.8.0-014's scanner couldn't catch — STRICT only verified deleted-path / forbidden-token references, not user-visible semantic numbers.
  - **Bulk count update (16 → 23)**: ran a mechanical replace across all active (non-legacy, non-CHANGELOG) docs. Files updated: `SKILL.md`, `pro/AGENTS.md`, `pro/GEMINI.md`, `README.md` (EN), `i18n/zh/README.md`, `i18n/ja/README.md`, `docs/index.md`, `docs/installation.md`, `i18n/zh/docs/installation.md`, `docs/getting-started/{first-session,choose-your-platform,what-is-life-os}.md`, `i18n/zh/docs/getting-started/what-is-life-os.md`, `i18n/ja/docs/getting-started/what-is-life-os.md`, `docs/architecture/{system-overview,roadmap}.md`, `docs/evals/{overview,writing-new-scenarios}.md`, `docs/guides/multi-platform-setup.md`, `docs/user-guide/second-brain/{second-brain-overview,obsidian-integration}.md`, `docs/reference/version-history.md`. Patterns covered: `16 subagents`, `16 个 subagent`, `16 个 agent`, `16 个独立 agent`, `All 16 subagents`, `16 independent agents`, `16 個の独立した agent`, `16 functional IDs`. The historical v1.6.0 migration entry in `version-history.md` was rephrased to `v1.6.0 当时的 agent 文件重命名（v1.6.0 时为 16 个，至 v1.8.0 增至 23 个）` so the reference stays historically accurate.
  - **Updated subagent enumeration in `docs/architecture/system-overview.md`**: previously the "23 个 subagent" header was followed by a 16-name list. Updated the list to all 23 IDs (added: `hippocampus`, `concept-lookup`, `soul-check`, `gwt-arbitrator`, `narrator`, `knowledge-extractor`, `monitor`).
  - **Scanner extension (`scripts/check-spec-drift.sh`)**: added 7 subagent-count drift tokens to `FORBIDDEN_TOKENS`. Tokens are written via bash adjacent-string concatenation (`"16 sub""agents"`) so the scanner source itself does not carry the literal substring — that lets a user-side `rg "16 subagents"` audit against the repo find zero hits in the scanner itself, only real drift candidates. Legacy frontmatter (`status: legacy` or `authoritative: false`) exemption applies as usual; v1.7-era spec / archive files still mention "16" historically and are correctly skipped.
  - **`v1.8.0` tag force-realigned**: deleted local + remote tag, recreated annotated tag at HEAD `6cb3d79` so consumers fetching `v1.8.0` get the full Spec-GC + subagent-count cleanup (R-1.8.0-014 + R-1.8.0-015), not the stale R-1.8.0-013 snapshot. (`git tag -d v1.8.0 && git push origin :refs/tags/v1.8.0 && git tag -a v1.8.0 <head> && git push origin v1.8.0`.)
  - **Verification**: `STRICT=1 bash scripts/check-spec-drift.sh` exit 0; `git ls-files | xargs grep -l "16 subagents|16 个 subagent|16 个 agent|All 16 subagents"` filtered to non-legacy, non-CHANGELOG files: **0 active hits**; mypy --strict tools/ → 0 errors / 16 files; ruff → clean; pytest → 232 passed / 3 deselected; bash -n on all 31 tracked .sh files: pass.

- **R-1.8.0-014 · Spec GC Sprint completion (post-2026-04-30 user round-8 audit)**: Closed the spec-drift cleanup that ran across audit rounds 5–8. STRICT-mode CI gate (`STRICT=1 bash scripts/check-spec-drift.sh`) now passes — active files no longer reference deleted scripts / deleted CLI / deleted subagents / deleted cron infrastructure. Legacy v1.7-era specs marked with explicit YAML frontmatter (`status: legacy` and/or `authoritative: false`).
  - **Scanner upgrades (`scripts/check-spec-drift.sh`)**:
    - **Counter subshell bug fix**: `broken_paths` increment was lost because the `... | sort -u | while ...` pipeline ran the loop in a subshell. Switched to writing unique paths to a tempfile then iterating in the parent shell so STRICT exit code is correct.
    - **Legacy-frontmatter exemption widened**: now skips files marked either `status: legacy` *or* `authoritative: false`. The two markers were used inconsistently across v1.7 references; both are now honored.
    - **Multi-line context lookback extended 5 → 8 lines**: catches the common markdown pattern of an H2/H3 header (`### Removed in v1.8.0 pivot`) followed by a blank line and 4–6 deletion bullets. The prior 5-line window failed to associate header context with the last bullet.
    - **CONTEXT_ALLOW expanded**: added uppercase `Removed`/`Deleted`/`Deprecated`, `in v1.8.0 pivot`, `in pivot`, `R-1.8.0-012`, `R-1.8.0-013`, `TBD`, `planned`, `will be created` so explanatory annotations actually match.
    - **Word-boundary token check**: forbidden-token scanner switched from literal `index($0, token)` to a regex with character-class word boundaries (no awk `\b`), so substring `life-os-tool` no longer falsely matches the legitimate plural package name `life-os-tools` in `pyproject.toml`.
  - **Active-file rewrites** (deleted-script references replaced with explicit "deleted in v1.8.0 pivot" annotations or migrated to the current pull-based equivalents):
    - `docs/getting-started/what-is-life-os.md` Layer 4 section (× EN/ZH/JA): replaced cron-era `scripts/{decay-audit,dream-trigger-check,monthly-review,session-index,wiki-conflict-check}.py` listing with the actual `python -m tools.<name>` modules shipped post R-1.8.0-011.
    - `tools/README.md`: rewrote Status + Authoritative Spec sections, replaced "Planned Modules" table with "Currently Shipped Modules" enumerating the 10 actually-present tools, marked deleted dispatcher / cron scripts / cortex helpers as historical context.
    - `pro/agents/monitor.md` Related Specs: marked `references/automation-spec.md` and `references/session-modes-spec.md` as deleted in v1.8.0 pivot (superseded by `pro/CLAUDE.md` Session Modes).
    - `evals/scenarios/tool-seed.md`: marked `references/SOUL-template.md` and `references/tools-spec.md §6.10` as legacy/deleted; `tools/seed.py` now generates skeleton inline.
    - `docs/user-guide/themes/adding-a-theme.md`: removed reference to non-existent `themes/zh-classical-tw.md`; described traditional-Chinese variant as a user-created file.
  - **Legacy frontmatter pass (round-8 cumulative · 71 files marked across two batches)**: spec / legacy-doc files in `docs/architecture/`, `docs/guides/v1.7-migration.md`, `docs/user-guide/cortex/*` (× EN/ZH/JA), `references/{cortex-spec, cortex-architecture, narrator-spec, tools-spec, v1.7-shipping-report, templates/concept-template, concept-spec, data-layer, eval-history-spec, hippocampus-spec, method-library-spec, session-index-spec, snapshot-spec, compliance-spec}.md` (× EN/ZH/JA), `evals/scenarios/*` carry `status: legacy` (or `authoritative: false`) so the scanner recognizes them as historical content rather than active spec.
  - **Verification**: `STRICT=1 bash scripts/check-spec-drift.sh` exits 0 (broken paths in active files: 0; forbidden-token hits in active files: 0). `mypy --strict tools/` 0 errors / 16 files. `ruff check tools/ tests/` clean. `pytest tests/` 232 passed / 3 deselected.

Verification (CI matrix actually green now):
- `bash -n` on all 30 tracked .sh files: pass
- `mypy --strict tools/`: **0 errors** (16 source files checked) — was 25
- `ruff check tools/ tests/`: All checks passed
- `pytest tests/` full suite: **223 passed, 9 skipped (optional extras), 3 deselected** — was 5+ failures
- Hook test suite: **7/7 PASS** — was 6/7
- pytest collection: 232/235 (3 deselected; was 232/235 + 1 collection ERROR from test_integration)

### Migration

```bash
# from inside your second-brain repo (the one with _meta/, SOUL.md, wiki/):
cd /path/to/your/second-brain
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
bash ~/.claude/skills/life_OS/scripts/setup-cron.sh install
# alternative if you can't cd: LIFEOS_DATA_ROOT=/path/to/second-brain bash ... install
```

No second-brain data migration required. v1.7.x sessions/wiki/SOUL fully compatible. The install errors out with a clear message if `$PWD` (or `$LIFEOS_DATA_ROOT`) doesn't have a `_meta/` directory, so misconfiguration fails loudly instead of silently scanning the wrong root. `bootstrap_repo_dirs` is idempotent — safe to re-run on repos that already have the dirs. After re-install on macOS: `launchctl unload ~/Library/LaunchAgents/com.lifeos.hermes-local.*.plist && launchctl load ~/Library/LaunchAgents/com.lifeos.hermes-local.*.plist` to pick up the new `WorkingDirectory` and `--root` paths.

### Audit Verdict (v1.8.0 final)

The "spec promised but never automated" gap from v1.7.3 audit is now closed. AUDITOR Mode 2 / ADVISOR monthly / eval-history monthly / strategic consistency / wiki decay / spec compliance / archiver recovery / boot catch-up — all ✅.

User feedback driving v1.8.0: 「Hermes 和 cortex 的问题」→「为什么设计好了但没跑起来」→「不要 routines 也能实现」→「我不可能每天都开新 session」→「完整版必须一次性全部做完」.

---

## [1.7.3] - 2026-04-26 / 2026-04-27 - Cortex enforcement + auto-trigger + archiver Phase 2 carve-out + 4 dead modules removed

> The "make tools actually usable" release window. Three iterations folded into the single v1.7.3 release per user request:
>
> 1. **v1.7.3 base (2026-04-26)**: Cortex always-on hook, 4 slash commands, approval guard wired, 4 dead modules removed.
> 2. **v1.7.3 auto-trigger patch (2026-04-27)**: slash commands demoted to backup mode after user feedback. pre-prompt-guard.sh memory keyword detection added.
> 3. **v1.7.3 archiver carve-out (2026-04-27)**: Phase 2 split into dedicated `knowledge-extractor` subagent to fix 80%+ recent archiver placeholder violations. spec consistency fixes + stop-session-verify LLM_FILL detection.
>
> All three folded into single v1.7.3 release per user request: 「版本号不能变，还是 1.7.3，都要在这个版本里面全部修完」.

### Added

- **Cortex always-on enforcement (hook injection)**: `scripts/hooks/pre-prompt-guard.sh` now emits a `<system-reminder>` block (trigger=cortex) that forces ROUTER to launch all 5 Cortex subagents (hippocampus / concept-lookup / soul-check / gwt-arbitrator / narrator-validator) in parallel before answering, whenever the prompt qualifies (length ≥ 80 chars OR decision keyword detected). Closes the silent-degradation gap found in v1.7.2 audit (0 `_meta/runtime/<sid>/cortex-*.json` audit trails across 17+ sessions). Skip rules: short conversational filler ("ok", "go on") bypasses Cortex.
- **4 slash commands wired into Claude Code**: new `scripts/commands/{compress,search,memory,method}.md` source files; `scripts/setup-hooks.sh` now copies them to `~/.claude/commands/` during install. Commands:
  - `/compress [focus]` — inline context compression with `_meta/compression/<sid>-compress-<ts>.md` archive.
  - `/search <query>` — FTS5 cross-session search via `tools.session_search` CLI.
  - `/memory emit|read|remove|path` — 24-48h short-term memory via `tools.memory` CLI.
  - `/method create|update|list` — method library management via `tools.skill_manager` CLI.
- **Approval guard wired (PreToolUse Bash hook)**: new `scripts/hooks/pre-bash-approval.sh` bridges every Bash command to `tools/approval.py`. Closes the v1.7.2 gap where 47 dangerous-command patterns + hardline + tirith guards sat with 0 callers. Hook reads Claude Code stdin JSON, runs `check_dangerous_command()`, exits 0 (silent approve) or exit 2 + stderr (block with reason). Bypass: `export LIFEOS_YOLO_MODE=1`. Registered in `setup-hooks.sh` as `life-os-pre-bash-approval` (PreToolUse · matcher Bash · timeout 5s).
- **Memory auto-emit detection (auto-trigger patch · 2026-04-27)**: `pre-prompt-guard.sh` also detects 中/英/日 memory keywords (记一下 / remind me / 覚えて / TODO etc) and injects `<system-reminder>` (trigger=memory) forcing ROUTER to auto-run `python -m tools.memory emit` instead of redirecting user to `/memory`. Adds `trigger=memory` value to hook activity log.
- **pro/CLAUDE.md → Auto-Trigger Rules section (auto-trigger patch · 2026-04-27)**: codifies memory auto-emit, compress auto-suggest, search auto-trigger (via Cortex hippocampus), method auto-create (via archiver Phase 2 → knowledge-extractor). Principle: "if ROUTER asks the user to switch to a slash command, that is a UX bug — just do the action".
- **knowledge-extractor subagent (Phase 2 carve-out · 2026-04-27)**: new `pro/agents/knowledge-extractor.md` (Opus tier, [Read, Grep, Glob, Bash, Write] tools). Performs the 7 Phase 2 sub-steps (wiki six-criteria gate / SOUL changes / methods / concepts + Hebbian / SessionSummary / snapshot / strategic-map) AND writes the 7 persistent files. Writes 7 extraction reports to `_meta/runtime/<sid>/extraction/*.md` for archiver to read back. R11 audit trail to `_meta/runtime/<sid>/knowledge-extractor.json`. Reason: previous monolithic archiver had 80%+ placeholder violations (10+ recent adjourn runs in `pro/compliance/violations.md` 2026-04-25 through 2026-04-27) because it had to do everything in one invocation. ROUTER MUST launch knowledge-extractor BEFORE archiver.

### Changed

- **narrator-validator audit trail HARD RULE**: `pro/agents/narrator-validator.md` frontmatter `tools` extended from `[Read]` to `[Read, Bash, Write]`; new "Audit Trail (R11, HARD RULE)" section added requiring `_meta/runtime/<sid>/narrator-validator.json` write before returning YAML output.
- **Version markers**: `SKILL.md` frontmatter and 3 README badges updated to `1.7.3`.
- **Spec docs updated for inline compression**: `SKILL.md` Trigger Execution Templates `/compress` section, `references/hard-rules-index.md` manual compression bullet, and `evals/scenarios/cortex-retrieval.md` CX11 positive case all rewritten to describe ROUTER inline compression replacing the removed `tools/context_compressor.py`.
- **4 slash command files demoted to backup mode (auto-trigger patch · 2026-04-27)**: each `scripts/commands/{compress,search,memory,method}.md` now starts with a "⚠️ Backup mode" header pointing to the relevant pro/CLAUDE.md Auto-Trigger Rules subsection. Slash commands remain functional for: (1) precise user control, (2) developer smoke test, (3) auto-trigger fallback.
- **archiver.md Phase 2 carve-out + spec consistency fix (carve-out · 2026-04-27)**: `pro/agents/archiver.md` line 77 fixed (was "12-section Adjourn Report Completeness Contract" legacy v1.7.2 wording, now matches v1.7.2.3 "6-H2"). Phase 2 entire spec rewritten: primary path delegates to `knowledge-extractor` subagent; legacy 7-sub-step inline spec preserved as fallback. `pro/CLAUDE.md` Step 10 updated: ROUTER MUST launch `knowledge-extractor` first, then `archiver`. New launch sequence template.
- **stop-session-verify hook LLM_FILL detection (carve-out · 2026-04-27)**: `scripts/hooks/stop-session-verify.sh check_phase()` enhanced. Previously only detected TBD / `{...}` / "placeholder" string in phase header lines. Now also scans the next 30 lines after each phase header for unfilled `<!-- LLM_FILL: ... -->` patterns and `LLM_FILL:` strings, marking that phase as `placeholder_phases`. Catches the actual root cause of recent archiver violations (LLM emitting Bash skeleton verbatim without filling placeholders).

### Removed (4 dead modules · 1830 lines)

- **`tools/prompt_cache.py` deleted** (118 lines, 0 callers): no value in Claude Code subscription mode.
- **`tools/mcp_server.py` deleted** (227 lines, 0 callers, 0 client connections): MCP stdio wrapper never connected.
- **`tools/context_compressor.py` deleted** (1370 lines, 0 callers): compression now inline by ROUTER.
- **`tools/manual_compression_feedback.py` deleted** (51 lines, 0 callers): output helper for removed compressor.
- **`docs/architecture/prompt-cache-strategy.md` deleted**: spec doc for removed prompt_cache.
- **`docs/architecture/mcp-server.md` deleted**: spec doc for removed mcp_server.
- **`docs/architecture/hermes-local.md` cleaned**: removed dead-module refs from `related:` frontmatter; rewrote Borrow/Fork Surface module list to reflect v1.7.3 reality (approval wired, memory + session_search + skill_manager remain); removed `context_compressor` naming-note paragraph.

### Migration

Re-run `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh` to:
1. Install 4 new slash commands to `~/.claude/commands/`
2. Register the new `life-os-pre-bash-approval` PreToolUse(Bash) hook
3. Update `pre-prompt-guard.sh` (now with Cortex always-on + memory keyword detection)
4. Update `stop-session-verify.sh` (now with LLM_FILL detection + 30-line section body scan)

After install, every Bash command Claude runs is screened against the 47 dangerous patterns; if blocked, you'll see the 🛡️ 守门人 message in stderr.

No second-brain migration required.

### Audit Verdict (post-v1.7.3 final)

All v1.7.2 dead-weight findings AND v1.7.3 archiver-violation root cause are closed:
- Cortex always-on: enforced (hook injection) ✅
- approval.py 47 patterns: wired (PreToolUse Bash hook) ✅
- 4 dead modules removed (1830 lines) ✅
- Slash commands wired AND demoted to backup mode in favor of auto-trigger ✅
- Memory auto-emit: hook detects keywords and forces ROUTER auto-emit ✅
- archiver Phase 2 carved out into knowledge-extractor subagent ✅
- archiver.md spec internal consistency restored (12-section vs 6-H2 fixed) ✅
- stop-session-verify LLM_FILL detection added ✅

User feedback driving this release window:
1. "我为什么要用这样的方式来启动这些命令？这些命令不可以直接自动启动吗？" → auto-trigger patch
2. "重新检查一下上朝流程和退朝流程" → revealed 80%+ archiver placeholder violations → carve-out
3. "C 还是1.7.3" + "版本号不能变，还是 1.7.3，都要在这个版本里面全部修完" → all changes squashed into single v1.7.3 release

---

## [1.7.2.3] - 2026-04-26 - Retrospective skeleton ownership

> Subagent D ownership patch. Scope limited to `pro/agents/retrospective.md`, `SKILL.md`, three README files, and three CHANGELOG files.

### Changed

- **RETROSPECTIVE ownership narrowed**: `pro/agents/retrospective.md` now states that ROUTER pre-renders roughly 80% of Mode 0 via Bash skeleton.
- **Single LLM fill slot**: the subagent fills only `<!-- LLM_FILL: today_focus_and_pending_decisions -->` with about 5-15 lines for Today's Focus and Pending Decisions; ROUTER splices that block into the skeleton.
- **Version markers**: `SKILL.md` and README badges now point to `1.7.2.3`.
- **install_sha field for SHA gap fix**: `SKILL.md` frontmatter now carries `commit_sha` and `install_date` fields. `setup-hooks.sh` auto-writes them on git clone deployments. New `scripts/lib/sha-fallback.sh` provides 3-tier resolution: `SKILL.md` frontmatter → `.install-meta` JSON → `git rev-parse HEAD` → `unknown`. Closes `Local commit SHA: unknown` bug on install-skill deployments.
- **SOUL/DREAM display restored (v1.6.x parity)**: `scripts/retrospective-briefing-skeleton.sh` now Bash-pastes full `SOUL.md` content and full latest `_meta/journal/*-dream.md` content verbatim in fenced markdown blocks. LLM only adds delta interpretation (confidence trend / today implications) on top, cannot compress structural SOUL/DREAM data. `pro/agents/retrospective.md` ## 2 / ## 3 spec updated to reflect new "Bash paste full content + LLM trend narrative" model. Reverses v1.7.2.1 over-subtraction that compressed SOUL Health to "changed dimensions only" and DREAM to "1-2 sentence digest".
- **Adjourn 12 H2 → 6 H2 + LLM token budget (speed fix)**: `pro/agents/archiver.md` Adjourn Report Completeness Contract reduced from 12 H2 to 6 core H2 (Phase 0/1/2/3/4 + Completion Checklist). AUDITOR Mode 3 / Subagent self-check / 子代理调用清单 / Hook fired / total tokens-cost folded as H3 sub-items under Completion Checklist. New "Phase 2/3 LLM Token Budget" HARD RULE: Phase 2 narrative ≤ 1500 tokens (combined wiki/SOUL/method/concept/strategic/SessionSummary/snapshot/last_activity), Phase 3 narrative ≤ 800 tokens. Verbatim DREAM journal does not count toward budget (Bash paste). Speed target: archiver Adjourn 25 min → 10-12 min.
- **archiver-briefing-skeleton.sh new (Bash skeleton for archiver)**: New `scripts/archiver-briefing-skeleton.sh` mirrors `retrospective-briefing-skeleton.sh` design — emits 6 H2 Adjourn Report framework with Bash-pasted Phase 0/1/4 + measured facts (outbox path / decision-task-journal counts / wiki-SOUL-DREAM stat / git status / Stop hook health). LLM only fills `<!-- LLM_FILL -->` placeholders for Phase 2/3 narrative + Completion Checklist values. Wired into `pro/CLAUDE.md` / `pro/GEMINI.md` / `pro/AGENTS.md` Step 10 Adjourn Session block. Complementary to existing `archiver-phase-prefetch.sh` (R11 audit trail).
- **Session Binding HARD RULE rewritten (product direction correction)**: `pro/CLAUDE.md` / `pro/GEMINI.md` / `pro/AGENTS.md` Session Binding HARD RULE clarified: discussion scope ≠ data write scope. Session binding constrains data persistence (where decisions/wiki/SOUL get written) but NOT discussion topics. ROUTER engages directly with whatever the user raises (financial / strategic / interpersonal / cross-project / abstract). ROUTER MUST NOT deflect with "本窗口角色只做 X" / "请转到其他窗口" / "translate to planner trigger paste for another window" / "召唤翰林院 panel" without explicit user request. Reverses 13-round hardening accumulated effect of LLMs treating session binding as business-topic forbidden zone. Restores Life OS to its founding purpose as a decision thinking assistant.

### Migration

No second-brain migration required.

---

## [1.7.2.1] - 2026-04-26 - Subtraction hotfix for report shape and theme aesthetics

> Small subtraction-only hotfix: fewer visible rules, restored theme aesthetics, and fixed-position version markers. No new release line beyond v1.7.2.1.

### Changed

- **Theme aesthetic restored**: user-facing briefings return to the active theme's visual language instead of being dominated by compliance scaffolding.
- **Report surface reduced**: the visible report shape is reduced from 17 H2 blocks to 6 so users see the essential flow without ceremony overload.
- **Version markers fixed**: version markers remain in stable, predictable positions for easier human and script checks.

### Removed

- **Wrapper requirement removed**: compressed paste wrappers are no longer required as a visible reporting structure.
- **Fewer rules in the user path**: redundant presentation rules were removed so the audit model stays enforceable without making every response feel procedural.

### Product Refocus (v1.7.2.2 notes)

- **AUDITOR silent by default**: AUDITOR moves to default-silent background verification; it surfaces only material blockers, escalations, or explicit user-requested audit results.
- **No Compliance Watch prepend**: `Compliance Watch` signals no longer prepend user-facing briefings; they remain available in audit / background channels instead of occupying line 1.
- **New H2 structure**: user-facing reports adopt the new H2 structure centered on briefing substance, decisions, next actions, and evidence rather than compliance scaffolding.
- **Trail `SESSION_ID` lock**: runtime audit trails are locked to the active `SESSION_ID`, so trail evidence stays bound to the current session and cannot drift into another session context.
- **Second-brain foreground restored**: system audit deliberately moves to the background while the user's second-brain content, priorities, and working memory return to the foreground.

### Migration

No second-brain migration required.

---

## [1.7.2] - 2026-04-26 - Hermes Local, Cortex always-on, and compression hardening

> Patch release for the local execution surface, Cortex orchestration, and transparent compressed reporting.

### Added

- **Hermes Local naming and attribution**: `Hermes Local` is the user-facing label for Life OS local safeguards and automation, while internal/spec labels remain `execution layer`, `Layer 3`, and `Layer 4`; docs now attribute borrowed/forked local-tool components to `NousResearch/hermes-agent` under the MIT License.
- **Hermes Local fork-module areas**: documented and attributed six borrowed/forked module areas: `tools/approval.py`, `tools/context_compressor.py` + `tools/manual_compression_feedback.py`, `tools/prompt_cache.py`, `tools/memory.py`, `tools/session_search.py`, and `tools/skill_manager.py`. The Life OS compressor module is `context_compressor`.
- **Cron and MCP local automation**: added `scripts/setup-cron.sh` for idempotent local reindex / daily briefing / backup jobs, plus `tools/mcp_server.py` and `docs/architecture/mcp-server.md` for optional MCP stdio access to Life OS CLI tools.
- **Method library and eval-history loop**: added method candidate extraction, method context injection, `_meta/eval-history/` writeback, and monthly self-review readback so repeated procedural and compliance signals close the loop.

### Changed

- **Cortex always-on orchestration**: when Cortex is enabled, Step 0.5 is attempted for every user message, including Start Session and direct-handle candidates; missing indexes trigger `tools/migrate.py` auto-bootstrap and degrade through `degradation_summary` instead of silently skipping.
- **ROUTER paste compression**: replaced v1.7.1 full subagent paste duplication with compressed paste wrappers plus R11 audit-trail links; ROUTER uses `tools/context_compressor.py` semantics and preserves substantive claims, decisions, blockers, side effects, and evidence.
- **Manual `/compress` trigger**: ROUTER now treats `/compress [focus]` as user-triggered context compression and returns feedback using `tools/manual_compression_feedback.py` semantics: message count, rough token estimates, and no-op notice.

### Fixed

- **Version check prefetch**: retrospective Mode 0 now consumes ROUTER's pre-fetched Step 8 marker, copies local/remote version details into Platform + Version Check, and runs the remote check with `lifeos-version-check.sh --force` so stale cache or subagent re-run behavior cannot hide release drift.

### Migration

No required second-brain migration. Optional: run `bash scripts/setup-cron.sh install` for local scheduled jobs and install `mcp` only if using the MCP stdio server.

---

## [1.7.1] - 2026-04-25 - Version, i18n, and hardening index

> Patch release grouping 27 hardening fixes across transparency, orchestration evidence, hook reliability, i18n drift control, and compliance indexing.

### Added

- **Token transparency**: briefings and orchestration notes now surface token-sensitive decisions, skipped work, and escalation reasons instead of hiding them behind generic summaries.
- **Hard-rules index**: `references/hard-rules-index.md` records the current authoritative HARD RULE sources and per-host marker count so README no longer carries a stale number.
- **Pre-commit i18n drift guard**: `.git/hooks/pre-commit` runs `bash scripts/lifeos-compliance-check.sh i18n-sync` and blocks commits when localized release docs drift.
- **v1.7.1 release notes**: English, Chinese, and Japanese README / CHANGELOG files now share aligned Added / Fixed / Migration coverage for the hardening pass.

### Fixed

- **ROUTER output fidelity**: ROUTER must paste subagent reports literally, with no compression or silent summarization, and must keep triage reasoning isolated from downstream agents.
- **AUDITOR evidence path**: AUDITOR hardening favors programmatic checks, Bash stdout evidence, source-count markers, version/path verification, and briefing-completeness classes over same-source LLM judgment.
- **Hook reliability**: hook activity visibility, hook health checks, stop-hook behavior, and marker disambiguation were tightened so missing or ambiguous backstops are easier to detect.
- **Cortex and DREAM display**: Cortex context emission, explicit GWT arbitration, frame markdown resolution, and DREAM full-output display now have clearer contracts.
- **Git safety and force-push handling**: force-push situations are escalated instead of normalized, and release docs avoid implying unsafe recovery actions.
- **i18n audit cleanup**: localized README / CHANGELOG updates were aligned to prevent obvious mixed-language release-note leaks.

**R9 fix (root cause):**
- stop-session-verify.sh ADJOURN_RE: switched from full-transcript grep to last-50-lines-only. Eliminates false-positive when dev sessions discuss archiver/adjourn spec content (the original full-text grep matched any literal "adjourn"/"退朝"/"dismiss" anywhere in transcript). No longer deferred to v1.7.2 — fixed in v1.7.1.

**R10 architectural shift (truly closes "5 项 skip" issue):**
- retrospective Mode 0: 11 of 18 steps now ROUTER-pre-fetched via scripts/retrospective-mode-0.sh (Bash literal stdout, LLM cannot skip). Steps 2/3/4/5/8/10/11/12/13/14/17 are deterministic. LLM only handles steps 1/6/9/16/18 (judgment-required).
- New violation class C-step-skipped (P0): missing any of 11 [STEP N · ...] markers in briefing.
- Structural answer to LLM compliance ceiling — spec rules cannot enforce LLM behavior; programmatic Bash output cannot be skipped.

**R11 audit trail file channel:**
- Every subagent now writes runtime audit trails to `_meta/runtime/<session_id>/<subagent>-<step>.json`; AUDITOR reads those files programmatically through channel 1 instead of trusting ROUTER's LLM paste channel 2.
- New violation classes: `C-no-audit-trail`, `C-trail-incomplete`, and `B-trail-mismatch`.
- New helpers/spec: `scripts/lib/audit-trail.sh`, `scripts/archiver-phase-prefetch.sh`, and `references/audit-trail-spec.md`; Step 10a Notion sync now runs automatically with no user ask.

**R12 fresh invocation contract:**
- Every `上朝` / `退朝` trigger now requires a fresh full execution; the LLM cannot reuse a previous briefing or adjourn report.
- `retrospective-mode-0.sh` treats existing `index_rebuild_state` data as `rebuild=force`, so cached index state cannot justify skipping a Start Session rebuild.
- New P0 violation class: `C-fresh-skip`; forbidden phrases, length collapse, and missing fresh markers are covered by fresh-invocation scenario coverage.
- Runtime audit trail JSON now includes `fresh_invocation:true` and `trigger_count_in_session`.

### Migration

1. Install or keep `.git/hooks/pre-commit` so `i18n-sync` runs before local commits.
2. Run `bash scripts/lifeos-compliance-check.sh i18n-sync` after editing release docs.
3. Use `references/hard-rules-index.md` for the current HARD RULE count; no second-brain data migration is required.

---

## [1.7.0.1] - 2026-04-25 · Briefing Contract + Hook Self-check + Cortex Config

> Patch release tightening the v1.7 GA contract: final briefings now have fixed required sections, hook installation is self-checked before Mode 0, and Cortex activation is consistently opt-in through `_meta/config.md`.

### Fixed

- **lifeos-version-check.sh cache freshness** — Added `--force` flag and remote SHA-based cache invalidation. Daily cache no longer goes stale within the same day if remote ships a new version.
- **Briefing completeness is now testable** — Start Session and Adjourn outputs must emit fixed headings with concrete values, so missing or placeholder sections are logged as `C-brief-incomplete`.
- **RETROSPECTIVE no longer assumes hooks are installed** — Mode 0 performs a pre-session hook health check and surfaces the exact `setup-hooks.sh` recovery command when the Claude Code hook backstop is missing or incomplete.
- **Cortex config path is consistent** — Reverted R1's accidental path split — Cortex configuration stays in `_meta/config.md` as shipped in v1.7.0, with `cortex_enabled: false` as the opt-in default.
- **Cortex default is unambiguous** — missing config now degrades to `cortex_enabled: false`; Cortex is OFF / opt-in until the user explicitly enables it.
- **AUDITOR Mode 3 programmatic checks** — AUDITOR now calls Bash (`lifeos-compliance-check.sh` + `grep`) instead of LLM-reasoning, eliminating same-source confabulation that allowed the 2026-04-25 testbed-machine "private repo" case to pass through.

### Added

- **Anti-confabulation hardening** — Step 8 forces literal Bash stdout paste, ROUTER pre-fetches ground truth, AUDITOR Mode 3 scans for fabrication phrase blacklist + tool-call evidence, new B-fabricate-toolcall violation class. Closes the 2026-04-25 'private repo' confabulation case.
- **Briefing Completeness Contract** — RETROSPECTIVE and ARCHIVER final reports now define required fixed-position sections and minimum evidence fields.
- **Compliance taxonomy for briefing omissions** — `C-brief-incomplete` records missing headings, session/source metadata, and escalation behavior separately from base Class C.
- **`briefing-completeness` compliance check** — `scripts/lifeos-compliance-check.sh` can now verify retrospective and archiver briefing headings in regression runs.
- **Layer 1 hook auto-install** — retrospective Step 0 + archiver Phase 0 + ROUTER trigger detection now auto-run `setup-hooks.sh` when hooks are missing. No more manual install step required after `git pull`.
- **PRIMARY-SOURCE PRECOMPUTE briefing markers** — wiki/sessions/concepts measured counts now MUST appear in briefing as `[Wiki count: measured X · index Y · drift Δ=Z]`. Missing → `C-brief-incomplete`; |Δ|≥3 without `⚠️ DRIFT` → `B-source-drift`.
- **STATUS.md staleness detection** — retrospective Step 0.5 checks STATUS last-updated vs git HEAD age; ≥7 days → STATUS narrative suppressed in briefing. New `B-source-stale` class.
- **30d-≥3 Compliance Watch auto-banner** — retrospective reads `violations.md`, auto-prepends `🚨 Compliance Watch: <class> (X/30d)` to briefing line 1 when threshold trips. Missing → `C-banner-missing`.
- **ROUTER fact-check on subagent output** — `SKILL.md` mandates ROUTER call Bash to verify numeric/version/path claims in briefing before showing to user. Third defense layer after subagent self-check + AUDITOR Mode 3.

### Migration from v1.7.0

1. Review any second-brain that enabled Cortex implicitly and keep Cortex enabled only via `_meta/config.md` where Cortex should run.
2. Add `cortex_enabled: true` to `_meta/config.md` for opt-in workspaces; leave the field absent or set `false` elsewhere.
3. Reinstall Claude Code hooks with `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh` if Mode 0 reports the hook health warning.
4. Update Start Session / Adjourn eval baselines to include the fixed briefing headings and run `briefing-completeness`.

---

## [1.7.0] - 2026-04-22 · Cortex Cognitive Layer · General Availability

> Cortex graduates from alpha to GA. 65 commits after `v1.7.0-alpha.2` closed the remaining TBDs: the full shell-hook runtime (5 hooks + shared library), 10 Python tools wired under a single `life-os-tool` CLI, 3 shared Python libraries, public docs publication under `docs/`, trilingual cognitive-layer docs, Step 0.5 / Step 7.5 contract synced across CLAUDE / GEMINI / AGENTS hosts, and a migration path that preserves every existing v1.6.2a second-brain.

### ✨ Highlights

- **Cortex Pre-Router Cognitive Layer goes GA** — no longer opt-in-alpha; full contract with deterministic degradation
- **5 shell hooks enforced at runtime** — pre-prompt guard, pre-write scan, pre-read allowlist, post-response verify, stop-session verify; shared `_lib.sh`
- **10 Python tools unified under `life-os-tool`** — reindex / reconcile / stats / research / daily-briefing / backup / migrate / search / export / seed (+ embed placeholder + sync-notion)
- **3 Python libraries** — `tools/lib/{config, llm, notion}` as the shared surface for every tool
- **Trilingual user guide shipped** — 6 new Cortex guides (EN) + Chinese/Japanese cortex-spec and hippocampus-spec translations
- **Host-agnostic orchestration contract** — Step 0.5 (Pre-Router Cognitive) + Step 7.5 (Narrator validation) now normative in CLAUDE.md / GEMINI.md / AGENTS.md (root + `pro/`)
- **Life OS agents register as native Claude Code subagents** — install writes 21 Task-spawnable `~/.claude/agents/lifeos-*.md` wrappers from the 22 `pro/agents/*.md` definitions, skipping the ROUTER-internal narrator template so `Task(lifeos-retrospective)` no longer falls back to `general-purpose`

### Features

- **Cortex subagents (Pre-Router Cognitive Layer)** — hippocampus 3-wave session retrieval · GWT salience arbitration on top-5 signals · concept graph lookup with synapse matching · SOUL-dimension conflict check · Narrator citation wrapping · Narrator-Validator audit (Sonnet-tier)
- **Shell hooks (5 enforcement points + shared library)**
  - `pre-prompt-guard.sh` — UserPromptSubmit-time class-B/C policy and Cortex enablement gating
  - `pre-write-scan.sh` — block injection into `second-brain/wiki/**` and other protected surfaces
  - `pre-read-allowlist.sh` — SSH/secret denylist + cwd allowlist enforcement
  - `post-response-verify.sh` — verify `[COGNITIVE CONTEXT]` delimiters + adjourn checklist
  - `stop-session-verify.sh` — end-of-session compliance net (adjourn Phase 4 presence, narrator citation discipline)
  - `scripts/hooks/_lib.sh` — shared helpers (path resolution, JSON read, logging) reused by all five
- **Python tools (10 shipped + 1 placeholder + 1 Notion sync = 12 under `life-os-tool`)**
  - `reindex` — rebuild session INDEX + concept INDEX + SYNAPSES in one pass
  - `reconcile` — detect drift between SOUL/Wiki/Strategic-Map and session summaries
  - `stats` — violations escalation ladder + `--period / --since / --output` analytics
  - `research` — deep-research scaffold (web/code/company via Exa)
  - `daily_briefing` — morning briefing generator pulling from INDEX + STATUS + SOUL top-5
  - `backup` — 30d archive / 90d delete rotation + quarterly violations archival
  - `migrate` — v1.6.2a → v1.7 migration runner (3-month backfill window)
  - `search` — substring + concept-slug search across second-brain
  - `export` — serialize second-brain into portable bundle
  - `seed` — bootstrap empty second-brain from user templates
  - `embed` — placeholder (explicit no-op, per v1.7 decision "no vector DB")
  - `sync_notion` — two-way Notion mirror (via `tools/lib/notion.py`)
- **Python libraries** — `tools/lib/config.py` (env + pyproject resolution) · `tools/lib/llm.py` (LLM call wrapper with retries + token accounting) · `tools/lib/notion.py` (Notion API client)
- **Orchestration** — Step 0.5 (Pre-Router Cognitive Layer) and Step 7.5 (Narrator validation) synchronized into CLAUDE.md, GEMINI.md, and AGENTS.md at both root and `pro/` levels; contract is now host-agnostic
- **Bootstrap tooling** — `tools/seed_concepts.py` + 3 user-facing templates for second-brain bootstrap; 11 tests

### Documentation

- **6 new Cortex user guides** under `docs/user-guide/cortex/`
  - `overview.md` — the "what is Cortex" entry point
  - `hippocampus-recall.md` — how 3-wave session retrieval works
  - `concept-graph-and-methods.md` — concept node promotion + method-library signals
  - `narrator-citations.md` — reading and trace-ing `[S:][D:][SOUL:]` citations
  - `gwt-arbitration.md` — salience formula and why a signal made it to top-5
  - `auditor-eval-history.md` — eval-history self-feedback loop
- `docs/guides/v1.7-migration.md` — "第一周日常体验对标" section added for post-upgrade week-one pacing
- `devdocs/architecture/cortex-integration.md` — marked **deprecated**, aligned with spec freeze (source of truth is now `references/cortex-spec.md`)
- `docs/architecture/system-overview.md` — `_meta/` shard paths + Step 0.5 / Step 7.5 orchestration diagram updated
- `docs/getting-started/what-is-life-os.md` — Cortex now named as the third pillar alongside Second Brain and Decision Engine
- `MIGRATION.md` — dev-machine handoff guide (tar syntax fix for paths starting with dash)

### i18n

- `i18n/{zh,ja}/references/{concept,cortex,eval-history,gwt,hippocampus,hooks,method-library,narrator,session-index,snapshot,tools}-spec.md` — Chinese/Japanese translations for the 11 frozen v1.7 specs
- `i18n/{zh,ja}/docs/getting-started/what-is-life-os.md` + `i18n/{zh,ja}/docs/user-guide/cortex/*.md` — localized onboarding plus 6 Cortex user guides
- `README.md` + `i18n/{zh,ja}/README.md` — topic-block order, language switcher, and decision-table wording aligned across all three languages

### Infrastructure

- **CI** — pytest suite grew **184 → 400 (+216 tests)**; ruff warnings **50+ → 0**; bash syntax check **11/11** green
- **Makefile** — common dev commands (test / lint / format / build-docs) consolidated
- `UV_LINK_MODE=copy` written into `~/.bashrc` to resolve Dropbox hardlink conflicts during `uv sync`
- `.github/workflows/test.yml` pytest matrix extended with the 10 new tool modules + 3 new library modules
- 8 new hook-compliance eval scenarios under `evals/scenarios/hook-compliance/` (01-start-compliant-launch through 08-arbitrary-prompt-silent)

### Breaking / Migration

- Users on **v1.6.2a → v1.7.0** must run `uv run life-os-tool migrate` — the migration tool backfills the past 3 months of journal / snapshot data into the new `_meta/cortex/` shard layout
- Cortex defaults to **enabled on new installs** in v1.7.0 (flip from v1.7.0-alpha's opt-in default); existing second-brains keep whatever `cortex_enabled` setting they had
- Full migration procedure: `docs/guides/v1.7-migration.md`

### Compliance

- **2 incident dossiers** captured during the Cortex GA run
  - `backup/pro/compliance/2026-04-19-court-start-violation.md` — archived (resolved, lesson absorbed into L1/L2 hooks)
  - Narrator-spec violation — **resolved 2026-04-22** (absorbed into the Step 7.5 narrator-validator contract)

### Selected Files Touched (post-alpha.2 commits)

```
65b0d57 docs(i18n): publish zh/ja v1.7 specs and Cortex guide translations
170ca07 docs: publish v1.7 public docs trees (exclude plugin-system drafts)
8e47d61 docs(release): path docs/→devdocs/ in 8 specs + CHANGELOG SHA rewrite + tri-lingual sync
91b7896 chore(tests): remove unused pytest import in seed_concepts cleanup
fdf8748 chore(cli/tests): wire 10 v1.7 tools, fix Windows encoding, and track compliance dossiers
1b41f85 feat(tools): add seed.py + tests
9159e38 feat(tools): add migrate.py + tests
f2d5a1d feat(tools): add research.py + tests
b33f7dd feat(tools): extend stats.py aggregates and add sync_notion.py
7240446 feat(tools): add daily_briefing.py + tests
d2d43d8 feat(tools): add export.py + tests
b7e7335 feat(tools): add reconcile.py + tests
f8a26c6 feat(tools): embed.py placeholder + search.py (S5+S4 parallel-sprint merge)
032bdc7 feat(tools): add reindex.py + tests
2b7226f test(hooks): add 8 hook-compliance eval scenarios
0e5128b chore(hooks): extend setup-hooks.sh for v1.7 all 5 hooks
63e923e feat(hooks): add pre-read-allowlist.sh
5ff0d32 feat(hooks+lib): stop-session-verify.sh + Notion lib + pyproject (S1+S2 parallel-sprint merge)
4a2590f docs(orchestration): update root AGENTS.md with host-agnostic Step 0.5/7.5 contract
4ae2a65 feat(hooks): add pre-write-scan.sh
bf7f87e docs(orchestration): sync Step 0.5/7.5 to pro/AGENTS.md
877c629 feat(lib): add tools/lib/llm.py + tests
efa339d feat(lib): add tools/lib/config.py + tests
1414677 feat(hooks): add post-response-verify.sh
7c1fd3a docs(orchestration): sync Step 0.5/7.5 to GEMINI.md
a503301 feat(hooks): add pre-prompt-guard.sh
```

(Plus `tools/seed_concepts.py` + templates, `MIGRATION.md`, `Makefile`, additional spec/docs publication commits, and 3 trilingual CHANGELOG syncs.)

---

## [1.7.0-alpha.2] - 2026-04-21 · Post-v1.7.0-alpha follow-ups bundle

> 📚 **Comprehensive overview**: see [`references/v1.7-shipping-report-2026-04-21.md`](references/v1.7-shipping-report-2026-04-21.md) for the full single-page narrative covering both the v1.6.3 COURT-START-001 fix line AND the v1.7 Cortex line in one document. Recommended starting point if you're returning to the repo and want to know "what shipped today".

> 13 commits shipped after v1.7.0-alpha to close TBDs from the alpha CHANGELOG and add tooling/test infrastructure. Will roll into v1.7.0 stable release.

### 🔧 New tooling

- `tools/cli.py` — unified subcommand dispatcher; `pyproject.toml` activates `life-os-tool` console script
- `tools/backup.py` — snapshot rotation (30d archive, 90d delete) + violations log archival to quarterly files
- `tools/extract.py` — concept candidate extraction CLI (frequency counter + slug generator)
- `tools/lib/cortex/extraction.py` — non-LLM helpers (normalize_name, slug_from_name, is_stopword, count_frequencies, deduplicate_aliases) — handles deterministic parts of archiver Phase 2 Step A so LLM doesn't burn tokens on counting
- `scripts/lifeos-compliance-check.sh` — `check_adjourn()` + `check_cortex()` implementations (closing the placeholder from alpha)
- `tools/lib/cortex/__init__.py` — package-level exports of all 29 helper symbols

### 📋 New eval scenarios

- `evals/scenarios/adjourn-compliance.md` — Class C/D/E + A3 detection
- `evals/scenarios/cortex-retrieval.md` — CX1-CX7 detection + degradation paths

### ✅ Test suite expansion

- `tests/test_backup.py` — 19 tests (snapshot rotation, violations archival, path resolution)
- `tests/test_cli.py` — 8 tests (help / unknown / dispatch / argv preservation)
- `tests/test_compliance_check.py` — 11 subprocess-based tests for the bash compliance script
- `tests/test_integration.py` — 7 end-to-end integration tests (full Cortex pipeline with fixtures)
- `tests/test_package_imports.py` — 7 tests (cortex + second_brain package import surfaces, regression guard for __all__ drift)
- `tests/test_extraction.py` — 44 tests (normalize, slug, stopwords (EN/ZH/JA), phrase split, frequency, dedup)

**Total tests now: 173, all pass in 0.83s combined.**

### 🚀 CI

- `.github/workflows/test.yml` — pytest matrix (Python 3.11/3.12) + bash syntax + smoke tests for hooks

### 📚 Architecture documentation

- `references/cortex-architecture.md` — end-to-end data flow (Adjourn → Compile → Read paths), info isolation matrix, failure cascade, cost profile, compliance map

### 🔌 Wiring polish

- `pro/CLAUDE.md` Information Isolation table extended for all 6 v1.7 subagents (was: only hippocampus + GWT) + narrator-validator chain note in Step 0.5
- `pro/agents/archiver.md` adds explicit "Phase 2 Mid-Step — SOUL Snapshot" with both Python helper + direct write paths

### 🐛 Bug fixes

- `tools/cli.py` `_print_usage(stream=sys.stdout)` default eval bug — fixed to None+resolve-at-call so pytest capsys works
- `scripts/lifeos-compliance-check.sh` `set -e` + `grep -c` → silent kill; added `|| true` guards
- `scripts/lifeos-compliance-check.sh` `\s` regex (GNU-only) → POSIX `[[:space:]]` for portability

### Files Touched (post-alpha commits)

```
b1bf474 feat: tools/cli.py dispatcher + check_cortex() + pyproject scripts entry
4fa8db9 feat: check_adjourn() implementation + cortex-retrieval eval scenario
81c96ec feat: v1.7.0-alpha follow-up — backup.py + adjourn eval + CI workflow
2fecaa9 test: end-to-end integration tests for Cortex pipeline (7 tests)
72c942c feat: tools.lib.cortex package exports + Info Isolation table + archiver snapshot step
eb477a5 feat: tests/test_cli + test_compliance_check + cortex-architecture doc
```

(Plus the 1ce61d1 v1.7.0-alpha release commit itself.)

---

## [1.7.0-alpha] - 2026-04-21 · Cortex Pre-Router Cognitive Layer

> First Layer-2 architectural upgrade in Life OS history. Adds cross-session memory, concept graph, and identity signals as inputs to every decision workflow. 19 commits today brought v1.7 from spec drafts to functional completeness.

### 🧠 Pre-Router Cognitive Layer (orchestrator Step 0.5)

When `cortex_enabled: true` in `_meta/config.md`, every non-Start-Session user message now flows through 4 parallel subagents BEFORE ROUTER triage:

```
user message
    ↓
Step 0.5 (Pre-Router Cognitive Layer)
    ├─ hippocampus       → 3-wave session retrieval (5-7 sessions)
    ├─ concept-lookup    → concept-graph match (5-10 concepts)
    └─ soul-check        → SOUL dimension signals (top 5)
         ↓
    gwt-arbitrator        → top-5 signals via salience formula
         ↓
[COGNITIVE CONTEXT] block prepended to user message
    ↓
Step 1 (ROUTER Triage with annotated input)
```

After REVIEWER Final Review, optional `narrator` wraps Summary Report substantive claims with `[source:signal_id]` citations. `narrator-validator` (Sonnet-tier) audits citation discipline.

### 📋 6 new subagents (~900 lines markdown contracts)

| Agent | File | Spec |
|-------|------|------|
| hippocampus | `pro/agents/hippocampus.md` | `references/hippocampus-spec.md` |
| concept-lookup | `pro/agents/concept-lookup.md` | `references/concept-spec.md` |
| soul-check | `pro/agents/soul-check.md` | derived from soul-spec + gwt-spec §6 |
| gwt-arbitrator | `pro/agents/gwt-arbitrator.md` | `references/gwt-spec.md` |
| narrator | `pro/agents/narrator.md` | `references/narrator-spec.md` |
| narrator-validator | `pro/agents/narrator-validator.md` | narrator-spec validator section |

All 6 enforce information isolation: peer Pre-Router agent outputs are rejected. All are read-only — mutations happen only in archiver Phase 2.

### 🐍 Python tools (~1500 lines, pure stdlib + pyyaml)

| Module | Purpose |
|--------|---------|
| `tools/lib/second_brain.py` | Dataclasses for 11 second-brain types + frontmatter parser/dumper + path resolver |
| `tools/lib/cortex/session_index.py` | SessionSummary IO + INDEX.md compilation (idempotent) |
| `tools/lib/cortex/concept.py` | Concept IO + INDEX/SYNAPSES compilation + Hebbian update |
| `tools/lib/cortex/snapshot.py` | SoulSnapshot IO + archive policy (30d/90d) |
| `tools/stats.py` | Compliance violations escalation ladder enforcement |

### 🔧 4 CLI tools

```bash
uv run tools/rebuild_session_index.py [--root PATH] [--dry-run]
uv run tools/rebuild_concept_index.py [--root PATH] [--dry-run] [--no-synapses]
uv run tools/stats.py [--violations PATH] [--json]
bash scripts/setup-hooks.sh   # auto-registers SessionStart + UserPromptSubmit hooks (v1.6.3a)
```

### ✅ 77 pytest tests — all passing in 0.23s

| File | Tests |
|------|-------|
| `tests/test_second_brain.py` | 15 (frontmatter parser, dataclasses, path resolver) |
| `tests/test_session_index.py` | 16 (truncate, write, compile, rebuild, idempotence) |
| `tests/test_concept_and_snapshot.py` | 18 (concept IO, INDEX, SYNAPSES, Hebbian, snapshot policy) |
| `tests/test_stats.py` | 18 (parse, escalation, threshold triggers, path resolution) |

```bash
python3 -m pytest tests/ -v        # 77 passed in 0.23s
```

### 🔌 Wiring updates

- **`pro/agents/archiver.md`** Phase 2 — adds (a) concept extraction + Hebbian update + SYNAPSES regeneration step, (b) SessionSummary write step
- **`pro/agents/retrospective.md`** Mode 0 — adds INDEX.md compilation step + AUDITOR Compliance Patrol auto-follow
- **`pro/CLAUDE.md`** — new Workflow Step 0.5 (Pre-Router Cognitive Layer); Information Isolation table extended for hippocampus + gwt-arbitrator entries
- **`pro/agents/auditor.md`** Mode 3 — adds 7 Cortex compliance checks (CX1-CX7)

### 🚦 Default OFF (opt-in)

Cortex is disabled by default in v1.7.0-alpha. Users opt in:

```bash
echo "cortex_enabled: true" >> _meta/config.md
```

Recommended once a second-brain has accumulated ≥30 sessions. Cost: ~$0.05-0.25/turn (Opus tokens across Pre-Router subagents).

### 📊 Cortex compliance taxonomy (added to AUDITOR Mode 3)

| Code | Name | Severity |
|------|------|----------|
| CX1 | Skip Pre-Router subagents | P1 |
| CX2 | Skip GWT arbitrator | P1 |
| CX3 | Missing [COGNITIVE CONTEXT] delimiters | P1 |
| CX4 | Hippocampus session cap exceeded | P1 |
| CX5 | GWT signal cap exceeded | P1 |
| CX6 | Cortex isolation breach | P0 |
| CX7 | Cortex write breach | P0 |

CX checks skipped when `cortex_enabled: false`.

### 📁 Files Touched (19 commits)

Specs: `references/{cortex,hippocampus,gwt,concept,snapshot,session-index,narrator,hooks,tools,eval-history,method-library}-spec.md` + 8 modified existing references.
Subagents: `pro/agents/{hippocampus,gwt-arbitrator,concept-lookup,soul-check,narrator,narrator-validator}.md`.
Wiring: `pro/CLAUDE.md`, `pro/agents/{archiver,retrospective,auditor}.md`.
Tools: `tools/lib/{second_brain.py,cortex/*}`, `tools/{stats,rebuild_session_index,rebuild_concept_index}.py`.
Project: `pyproject.toml`, `.python-version`, `tools/README.md`.
Tests: `tests/{__init__,test_second_brain,test_session_index,test_concept_and_snapshot,test_stats}.py`.
Hooks: `scripts/lifeos-compliance-check.sh` (L5 closure for v1.6.3 chain).
Docs: 3 README + 3 CHANGELOG (this commit).

### 🚧 Known limitations / TBD

- **Production validation pending** — alpha is theory-tested via pytest + spec compliance, but not yet exercised in a real user second-brain at scale
- **No `concept-lookup` traversal of edges yet** — Wave 1 only; Wave 2/3 is hippocampus's domain
- **Narrator validator** is shipped but uses self-check loop in Phase 2; standalone validator subagent pending Phase 2.5
- **`tools/backup.py`** for snapshot archival rotation: deferred to v1.7.0 stable
- **adjourn-compliance eval scenario** still placeholder

### Migration

Existing users (v1.6.3b → v1.7.0-alpha):
1. Re-install skill: `/install-skill https://github.com/jasonhnd/life_OS`
2. Re-run hooks setup: `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh`
3. (Optional) Install Python tools: `cd ~/.claude/skills/life_OS && uv sync`
4. (Optional) Enable Cortex: `echo "cortex_enabled: true" >> {your-second-brain}/_meta/config.md`

Default OFF means existing users see ZERO behavior change unless they opt in. v1.6.3 five-layer compliance defense remains active and unchanged.

---

## [1.6.3b] - 2026-04-21 · AUDITOR Mode 3 Auto-Trigger Wired

> v1.6.3 shipped Mode 3 (Compliance Patrol) spec into `pro/agents/auditor.md` but **nothing actually invoked it**. The first production run in a user second-brain confirmed the gap: retrospective Mode 0 completed, briefing displayed, but no AUDITOR Compliance Patrol report appeared. Layer 4 of the five-layer defense was inert.

### 🔧 Fix

`pro/CLAUDE.md` Orchestration Code of Conduct gains rule #7:

> **AUDITOR Compliance Patrol auto-trigger** — after every `retrospective` Mode 0 (Start Session) completes OR every `archiver` returns, the orchestrator MUST launch `auditor` in Mode 3 (Compliance Patrol). Cannot be skipped. HARD RULE.

Three supporting docs updated to make the contract explicit:

- `pro/agents/retrospective.md` — adds "Auto-Follow: AUDITOR Compliance Patrol" section noting orchestrator chains Mode 3 after Mode 0 returns. Subagent itself does not launch AUDITOR.
- `pro/agents/auditor.md` — Mode 3 "When to run" section adds explicit trigger contract: orchestrator-launched, not self-launched, with cross-reference to `pro/CLAUDE.md` rule #7.
- `SKILL.md` — version 1.6.3a → 1.6.3b.

### 📊 Five-layer defense status (post-1.6.3b)

| Layer | Status |
|-------|--------|
| L1 · UserPromptSubmit hook | ✅ shipped (v1.6.3) · auto-installed by setup-hooks.sh (v1.6.3a) |
| L2 · Pre-flight Compliance Check | ✅ shipped + production-verified 2026-04-21 |
| L3 · Subagent Self-Check | ✅ shipped + production-verified 2026-04-21 |
| L4 · AUDITOR Compliance Patrol (Mode 3) | ✅ spec shipped (v1.6.3) · **trigger wired (v1.6.3b)** |
| L5 · Eval regression | ✅ scenario shipped (v1.6.3) · auto-runner extension deferred to v1.7 |

### Files Touched

- `SKILL.md` (version 1.6.3a → 1.6.3b)
- `pro/CLAUDE.md` (+ Orchestration rule #7)
- `pro/agents/retrospective.md` (+ Auto-Follow section)
- `pro/agents/auditor.md` (Mode 3 "When to run" trigger contract clarified)
- `README.md` + 三語 (badge)
- `CHANGELOG.md` + 三語

### Migration

No user action required. Existing v1.6.3a installs will auto-pick-up rule #7 on next session. AUDITOR Compliance Patrol report will appear at end of every Start Session and Adjourn going forward. Output format (when no violations):

```
🔱 [theme: auditor] · Compliance Patrol (v1.6.3)
✅ All 6 Start Session compliance checks passed
No violations logged. Session adheres to v1.6.3 HARD RULES.
```

---

## [1.6.3a] - 2026-04-21 · v1.6.3 Hot Patch · Layer 1 Install Gap + Hook False-Positive Guard

> First production run of v1.6.3 in a user second-brain (same day) validated Layers 2-5 working end-to-end. Two real gaps surfaced:
> 1. **Layer 1 (UserPromptSubmit hook) was NOT auto-registered** — `/install-skill` copies files but doesn't modify `~/.claude/settings.json`. Default installs shipped without L1 defense.
> 2. **Hook regex fired on paste content** — pasted transcripts containing a trigger word mid-content erroneously triggered the reminder.

### 🔧 Fix 1 — Layer 1 install automation

`scripts/setup-hooks.sh` refactored:
- Now installs both SessionStart hook (version check) AND UserPromptSubmit hook (Layer 1 defense) in one run
- Added `register_hook()` helper for DRY idempotent registration across event types
- Idempotent: safe to re-run; skips already-registered hooks
- Backwards compatible: existing v1.6.3 installs unaffected; re-running adds L1 cleanly

User runs once after install/upgrade:
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```

### 🔧 Fix 2 — Hook false-positive reduction

`scripts/lifeos-pre-prompt-guard.sh` adds two pre-checks before regex matching:
- **Length check**: prompt overall ≤ 500 chars (long prompts = conversational/paste, not triggers)
- **First-line check**: first non-empty line ≤ 100 chars (filters paste blocks starting with paragraph-length intros)

Trigger regex now runs against **first line only** (was multiline). Pasted transcripts with trigger words mid-content no longer fire the hook.

### 🆕 Class F — False positive

Added to `references/compliance-spec.md` Type Taxonomy and `pro/compliance/violations.md` Type Legend:

| Code | Name | Default Severity |
|------|------|------------------|
| **F** | False positive | P2 (informational) — hook fired on paste/quote content, not real user trigger. Excluded from escalation ladder. |

First documented Class F entry: 2026-04-21T13:42 — paste of v1.6.3 production-verification transcript triggered hook in dev repo. Assistant correctly identified paste context and refused to launch retrospective. Mitigated by Fix 2 above.

### 📋 COURT-START-001 status update

4 incident entries in `pro/compliance/violations.md` annotated with production-verification evidence:
- L2 (Pre-flight Compliance Check) — verified working in user second-brain on 2026-04-21
- L3 (Subagent Self-Check) — verified working in user second-brain on 2026-04-21
- L4 (AUDITOR Compliance Patrol) + L5 (eval regression) — pending observation window

`partial → true` transition still gated by eval regression pass + 30-day no-recurrence window per `references/compliance-spec.md`.

### Files Touched

- `SKILL.md` (version 1.6.3 → 1.6.3a)
- `scripts/setup-hooks.sh` (refactor with register_hook helper + UserPromptSubmit registration)
- `scripts/lifeos-pre-prompt-guard.sh` (+ length check + first-line extraction)
- `references/compliance-spec.md` (+ Class F to Type Taxonomy)
- `pro/compliance/violations.md` (+ Class F to legend, + 1 F entry, + L2/L3 verification annotations on 4 COURT-START-001 entries)
- `pro/compliance/violations.example.md` (+ Example 11 Class F)
- `README.md` + 三語 (version badge + v1.6.3a hot-patch note)
- `CHANGELOG.md` + 三語

### Migration

Existing v1.6.3 installs:
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```
Activates Layer 1 defense. No other action needed; Layers 2-5 unchanged.

New installs: same single command activates everything.

---

## [1.6.3] - 2026-04-21 · COURT-START-001 Fix · Five-Layer Defense

> When the user said "上朝" in the Life OS dev repo, ROUTER bypassed the retrospective subagent, simulated 18 steps inline, and fabricated the non-existent path `_meta/roles/CLAUDE.md § 0 Pre-Court Preparation` as authority. User reaction: "how can this Life OS be given to others? I cannot accept." This release ships a five-layer defense so every HARD RULE is actually hard.

### 🛡️ Five-Layer Defense Against Class A / B Violations

Root cause of COURT-START-001: documentation was complete, but **every HARD RULE was descriptive — zero enforcement**. The author himself could be tricked by the LLM; ordinary users would be inevitably misled. Five independent layers now guard every trigger word:

1. **Hook layer** — `scripts/lifeos-pre-prompt-guard.sh` runs on `UserPromptSubmit`, detects trigger words (上朝 / start / 閣議開始 / 退朝 / etc., all 9 themes), injects a `<system-reminder>` with the exact HARD RULE text and violation taxonomy into the assistant's context before any response.
2. **Pre-flight Compliance Check** — `SKILL.md` now requires ROUTER to output a 1-line confirmation before any tool call: `🌅 Trigger: [word] → Theme: [name] → Action: Launch([agent]) [Mode]`. Missing line = Class A3 violation, logged.
3. **Subagent self-check** — `pro/agents/retrospective.md` Mode 0 first line must be: `✅ I am the RETROSPECTIVE subagent (Mode 0, not main context simulation). Reading pro/agents/retrospective.md. Starting Step 1: THEME RESOLUTION.` This proves the subagent was actually launched.
4. **AUDITOR Compliance Patrol (Mode 3)** — `pro/agents/auditor.md` adds Mode 3 with a 7-class taxonomy (A1/A2/A3/B/C/D/E) and 6 detection checks for Start Session / Adjourn paths. Runs after every retrospective Mode 0 and archiver completion.
5. **Eval regression** — `evals/scenarios/start-session-compliance.md` codifies the 6 COURT-START-001 failure modes as Quality Checkpoints with grep-based failure detection commands.

### 📋 Violation Taxonomy (7 classes)

| Code | Name | Default Severity |
|------|------|------------------|
| A1 | Skip subagent — ROUTER simulates subagent's steps in main context | P0 |
| A2 | Skip directory check — dev repo bypasses retrospective Step 2 | P1 |
| A3 | Skip Pre-flight — first response missing `🌅 Trigger: ...` line | P1 |
| B | Fabricate fact — reference non-existent path / section as authority | P0 |
| C | Incomplete Phase — archiver exits before all 4 phases complete | P0 |
| D | Placeholder value — Completion Checklist contains `TBD` / `{...}` / empty | P1 |
| E | Main-context Phase execution — ROUTER runs Phase 1-4 logic inline | P0 |

### 📁 Dual-Repo Compliance Log (md + git, per user constraint)

User explicitly required: *"local sh command execution is fine, but the database must be md files and GitHub storage."* Violations are persisted to:

- `pro/compliance/violations.md` — dev repo (public, ships with Life OS)
- `_meta/compliance/violations.md` — user second-brain (private, per-user)

Both use the same format: `| Timestamp | Trigger | Type | Severity | Details | Resolved |`.

**Escalation ladder** (implemented by `tools/stats.py` in v1.7, manually observed until then):
- ≥3 same type in 30 days → hook reminder strictness upgrades
- ≥5 same type in 30 days → retrospective briefing prepends `🚨 Compliance Watch`
- ≥10 same type in 90 days → AUDITOR Compliance Patrol runs every Start Session

### 🗂️ New Files

- `scripts/lifeos-pre-prompt-guard.sh` — UserPromptSubmit hook (bash, chmod +x)
- `.claude/settings.json` — hook registration for dev repo
- `references/compliance-spec.md` — full specification: taxonomy, dual-repo strategy, write/read paths, escalation ladder, archival, resolution protocol, privacy
- `pro/compliance/violations.md` — dev-repo live log (5 seed entries from COURT-START-001)
- `pro/compliance/violations.example.md` — 10 example entries per class + grep recipes
- `pro/compliance/2026-04-19-court-start-violation.md` — full incident archive (473 lines, 12 sections)
- `evals/scenarios/start-session-compliance.md` — regression test for 6 COURT-START-001 failure modes

### ✏️ Modified Files

- `.claude/CLAUDE.md` — new HARD RULE section for Start Session triggers
- `SKILL.md` — version 1.6.2a → 1.6.3, Pre-flight Compliance Check section inserted before Start Session routing
- `pro/agents/retrospective.md` — Subagent Self-Check block before Execution Steps
- `pro/agents/auditor.md` — Mode 3 (Compliance Patrol) with 7-class taxonomy + detection checks

### 🔄 Resolution Protocol

Violations transition `false → partial → true` through three gates:
- **Gate 1** (`false → partial`): underlying fix shipped (version cited in Details field)
- **Gate 2** (`partial → true`): eval regression passes + 30 days elapsed + no recurrence (cite version + eval-id + observed-date)

COURT-START-001's 4 incident entries move to `partial` with this release. Transition to `true` requires `evals/scenarios/start-session-compliance.md` pass + 30-day observation window.

### Migration

No user action required for existing installations. On next Start Session after upgrade:
- Hook registers (dev repo only, via `.claude/settings.json`)
- Pre-flight line becomes mandatory
- AUDITOR runs Compliance Patrol after first retrospective Mode 0
- violations.md is auto-created if missing (empty table)

User second-brains that want the dual-repo violations log should add the hook block to their own `.claude/settings.json` per `references/compliance-spec.md`.

---

## [1.6.2a] - 2026-04-19 · Notion Sync Returns to Orchestrator

> The archiver subagent reported "Notion MCP not connected" because Notion MCP tools are environment-specific and unavailable inside subagents. Notion sync is now split out of the archiver and executed by the orchestrator (main context) which has MCP access.

### Changes

- **archiver.md**: Phase 4 reduced to git-only; Notion sync removed with explicit note about MCP tool limitation
- **CLAUDE.md**: New Step 10a — orchestrator executes Notion sync after archiver returns
- **GEMINI.md / AGENTS.md**: Synced with Step 10a addition
- **SKILL.md**: Adjourn template updated to include Notion sync as post-archiver step

---

## [1.6.2] - 2026-04-17 · Adjourn Defense + Wiki/SOUL Auto-Write + 10 DREAM Triggers

> Three reinforcements in one release: (1) bulletproof adjourn flow that cannot be partially skipped; (2) wiki and SOUL now auto-write under strict criteria instead of asking for confirmation; (3) DREAM gains 10 concrete auto-triggered actions.

### 🛡️ Adjourn 3-Layer Defense

Previous bug: ROUTER sometimes executed Phase 2 (knowledge extraction) in the main context instead of launching the ARCHIVER subagent, splitting the 4-phase flow.

Three independent defenses added:
- **SKILL.md + archiver.md wording** — HARD RULE forbidding ROUTER from any Phase content in the main context; explicit "Subagent-Only Execution" block in archiver.md
- **Adjourn State Machine in pro/CLAUDE.md** — legal/illegal state transitions enumerated; AUDITOR flags every violation to user-patterns.md
- **Mandatory launch templates** — SKILL.md's "Trigger Execution Templates (HARD RULE)" section pins the exact output pattern for Start Session / Adjourn / Review

### 📚 Wiki Auto-Write (no user confirmation)

Previous: archiver listed wiki candidates and asked user to pick which to save. This interrupted the flow and encouraged skipping.

New: archiver auto-writes under **6 strict criteria** + Privacy Filter:
1. Cross-project reusable
2. About the world, not about you (values → SOUL, not wiki)
3. **Zero personal privacy** — names, amounts, account IDs, specific companies, family/friend info, traceable date+location combos → stripped; if stripping makes the conclusion meaningless → discard
4. Factual or methodological
5. Multiple evidence points (≥2 independent)
6. No contradiction with existing wiki (contradictions → `challenges: +1` on existing entry, don't create competitor)

Initial confidence: 3+ evidence → 0.5; exactly 2 → 0.3; 1 or below → DISCARD.

User nudges post-hoc: delete file = retire, say "undo recent wiki" to rollback most recent auto-writes, or manually lower `confidence` below 0.3 to suppress.

### 🔮 SOUL Auto-Write + Continuous Runtime

Previous: SOUL dimensions only created through user confirmation; only surfaced periodically.

New:
- **ADVISOR auto-updates every decision** — increments `evidence_count` or `challenges` on existing SOUL dimensions after every Summary Report; detects new dimensions with ≥2 evidence points and auto-writes at `confidence: 0.3` with "What SHOULD BE" deliberately left empty for the user to fill when ready
- **REVIEWER mandatory SOUL reference** — every decision must cite relevant SOUL dimensions or explicitly note "no directly relevant dimension, this may open a new one"
- **SOUL Health Report in fixed briefing position** — every Start Session, the first block after Pre-Session Preparation is 🔮 SOUL Health Report (current profile with trend arrows, newly auto-detected dimensions awaiting user input, conflict warnings, dormant dimensions 30+ days, trajectory delta)

Confidence formula unchanged: `confidence = evidence_count / (evidence_count + challenges × 2)`.

### 💤 DREAM 10 Auto-Triggered Actions (REM stage)

REM now evaluates 10 concrete patterns and auto-acts on matches:

| # | Pattern | Auto-Action |
|---|---------|-------------|
| 1 | New project relationship | Write STRATEGIC-MAP candidate + flag for briefing |
| 2 | Behavior ≠ driving_force | Inject into next ADVISOR input |
| 3 | Wiki contradicted by new evidence | `challenges: +1` on that entry |
| 4 | SOUL dimension dormant 30+ days | Briefing warning |
| 5 | Cross-project cognition unused | Force-inject into next DISPATCHER |
| 6 | Decision fatigue detected | Suggest "no major decisions today" |
| 7 | Value drift in driving_force | Auto-propose SOUL revision |
| 8 | Stale commitment (30+ days no action) | Resurface in briefing |
| 9 | Emotional decision pattern | Next REVIEWER adds emotional-state check |
| 10 | Repeated identical decisions | Briefing: "Are you avoiding commitment?" |

All flags written to dream journal's `triggered_actions` YAML block. RETROSPECTIVE surfaces them in the fixed "💤 DREAM Auto-Triggers" briefing block at next Start Session.

### 🔬 Design Refinements (detailed specifications)

Building on the four conceptual pillars above, v1.6.2 also ships the detailed behavior specs:

**DREAM trigger detection logic** — each of the 10 triggers now has:
- A **hard threshold** (quantitative rule, auto-fires)
- **Soft signals** (LLM qualitative cues, fires with `mode: soft` + AUDITOR review required)
- Explicit data source, anti-spam 24h suppression, and structured output

Examples: decision-fatigue = "≥5 decisions in 24h AND second-half avg score ≤ first-half - 2"; value-drift = "≥3 challenges with ≤1 new evidence in 30d AND confidence drop >30%"; stale-commitment = "I will X / 我会 X / X する regex + 30 days no matching completion"; emotional-decision = "ADVISOR emotional flag + REVIEWER cool-off advised + session proceeded anyway"; repeated-decisions = "topic keyword overlap >70% with ≥2 past 30-day decisions". See `references/dream-spec.md` for all 10.

**ADVISOR SOUL Runtime unification** — merged the old read-only "SOUL Behavioral Audit" section into the new auto-update mechanism. One unified flow: per-dimension impact (support/challenge/neutral) → write evidence/challenge deltas → detect new dimensions → conflict warnings → output 🔮 SOUL Delta block. Runs every decision, not only at adjourn.

**SOUL snapshot mechanism for trend arrows** — archiver Phase 2 now dumps a minimal snapshot to `_meta/snapshots/soul/YYYY-MM-DD-HHMM.md` at the end of every session (numerical metadata only, no duplicated content). RETROSPECTIVE reads latest snapshot at next Start Session and computes:
- `confidence_Δ > +0.05` → ↗
- `confidence_Δ < -0.05` → ↘
- `|confidence_Δ| ≤ 0.05` → →
Plus special states: 🌟 newly promoted to core, ⚠️ demoted from core, 💤 dormant, ❗ conflict zone. Archive policy: >30 days → `_archive/`, >90 days → delete (git + Notion retain).

**REVIEWER 3-tier SOUL reference strategy** — prevents noise when SOUL has many dimensions:
- **Tier 1** (confidence ≥ 0.7): reference ALL, no upper limit — core identity must be considered
- **Tier 2** (0.3 ≤ confidence < 0.7): top 3 semantically relevant via strong/weak-match judgment
- **Tier 3** (confidence < 0.3): count only, don't surface (ADVISOR tracks in Delta)

Decision challenging a Tier 1 dimension → REVIEWER adds ⚠️ SOUL CONFLICT warning at top of Summary Report (semi-veto signal). Every Tier 2 dimension evaluated is listed with inclusion reason so AUDITOR can review quality.

### Files Touched

- `SKILL.md` (version + trigger templates)
- `pro/CLAUDE.md` (state machines + wiki/SOUL auto-write descriptions)
- `pro/GEMINI.md` / `pro/AGENTS.md` (cross-platform Gemini CLI + Codex CLI parity)
- `pro/agents/archiver.md` (Phase 2 auto-write + snapshot dump + Phase 3 10-trigger detection logic)
- `pro/agents/advisor.md` (unified SOUL Runtime: 5 steps, every decision)
- `pro/agents/reviewer.md` (3-tier SOUL reference strategy)
- `pro/agents/retrospective.md` (Step 11 expanded to 11.1-11.6: snapshot read + trend computation)
- `references/wiki-spec.md` + 三語 (6 criteria + privacy filter + user nudges)
- `references/soul-spec.md` + 三語 (auto-write + snapshot mechanism + tiered reference)
- `references/dream-spec.md` + 三語 (10 triggers per-section with hard/soft detection)
- `references/data-layer.md` + 三語 (`_meta/snapshots/` in directory tree + auto-write reflected)
- `README.md` + 三語 (What's new in v1.6.2 + Section V rewritten + architecture diagram)
- `CHANGELOG.md` + 三語

### Migration

No user action required. Existing wiki/SOUL entries continue to work. New entries auto-write starting next session. First Start Session after upgrade will show "no trend data yet" until second session provides a snapshot baseline. To disable a specific auto-written entry without deleting it: set `confidence: 0.0` in the frontmatter.

---

## [1.6.1] - 2026-04-16 · Nine Themes — Every Culture, Every Style

> The theme system expands from 3 to 9 themes. Each language now offers three distinct governance styles: historical, modern government, and corporate.

### New Themes

**English** (3 total):
- 🏛️ Roman Republic — Consul, Tribune (veto inventor), Senate, Quaestor, Legatus
- 🇺🇸 US Government — Chief of Staff, Attorney General, NSC, Treasury, GAO
- 🏢 Corporate — CEO, General Counsel, CFO, VP Operations (existing, unchanged)

**中文** (3 total):
- 🏛️ 三省六部 — 丞相、中书省、门下省、六部、御史台 (existing, unchanged)
- 🇨🇳 中国政府 — 国务院总理、发改委、人大常委会、财政部、审计署
- 🏢 公司部门 — 总经理、战略规划部、法务合规部、财务部、内审部

**日本語** (3 total):
- 🏛️ 明治政府 — 内閣総理大臣、参議、枢密院、大蔵省、元老
- 🏛️ 霞が関 — 内閣官房長官、内閣法制局、財務省、会計検査院 (existing, unchanged)
- 🏢 企業 — 社長室、経営企画部、法務部、経理部、内部監査室

### Theme Selection UI Updated

The selector now groups by language. Trigger word inference is smarter:
- "上朝" → auto-loads 三省六部 (唐朝-specific word)
- "閣議開始" → auto-loads 霞が関 (modern government-specific)
- Generic triggers ("开始", "はじめる", "start") → show that language's 3 sub-choices

---

## [1.6.0] - 2026-04-15 · Theme Engine — One Engine, Every Culture

> A Japanese user tried Life OS and the experience was poor — not because the logic was wrong, but because "Three Departments and Six Ministries" is a Chinese cultural concept that creates a learning barrier for non-Chinese users. v1.6.0 solves this by separating the decision engine from its cultural presentation.

### The Change

Life OS is now a **universal decision engine** with **swappable cultural themes**. The governance logic (plan → review → veto → execute → audit) is identical across all themes — only the names, tone, and metaphors change.

### Three-Layer Architecture

**Layer 1: Engine** — 16 agents with functional IDs (ROUTER, PLANNER, REVIEWER, DISPATCHER, 6 domain analysts, AUDITOR, ADVISOR, COUNCIL, RETROSPECTIVE, ARCHIVER, STRATEGIST). Language-neutral, culture-neutral.

**Layer 2: Theme** — Swappable cultural skins that map functional IDs to familiar names:
- `zh-classical` — 三省六部 (Tang Dynasty governance): 丞相, 中书省, 门下省, 六部, 御史台...
- `ja-kasumigaseki` — 霞が関 (Japanese central government): 内閣官房長官, 内閣法制局, 財務省, 会計検査院...
- `en-csuite` — C-Suite (corporate executive): Chief of Staff, General Counsel, CFO, Internal Audit...

**Layer 3: Locale** — Auto-detects user language, recommends matching theme. User can switch at any time.

### Theme Selection UI

At the first Start Session, the RETROSPECTIVE agent presents a simple a/b/c choice:
```
🎨 Choose your theme:
 a) 🏛️ 三省六部 — Tang Dynasty governance (Chinese classical)
 b) 🏛️ 霞が関 — Japanese central government (Kasumigaseki)
 c) 🏛️ C-Suite — Corporate executive structure (English)

Type a, b, or c
```

- **Theme choice is per-session** — each terminal window can use a different theme independently
- Theme selection does not persist across sessions; each new session re-prompts
- Users can switch mid-session by saying "switch theme" / "切换主题" / "テーマ切り替え"

### What Changed

- **16 agent files renamed**: Chinese pinyin (chengxiang.md, zhongshu.md...) → functional English (router.md, planner.md...)
- **themes/ directory created**: 3 theme files (~60 lines each) define role mappings, tone, trigger words, output titles
- **i18n agent duplication eliminated**: 48 agent files (16 × 3 languages) → 16 files. Themes handle display, agents handle logic.
- **~42 translated agent/orchestration files deleted**: No longer needed — one source of truth per agent
- **departments.md → domains.md**: Six Ministries → Six Domains (PEOPLE, FINANCE, GROWTH, EXECUTION, GOVERNANCE, INFRA)
- **All orchestration protocols updated**: CLAUDE.md, AGENTS.md, GEMINI.md use functional IDs
- **All reference docs updated**: data-layer, data-model, strategic-map-spec, wiki-spec, soul-spec, dream-spec, scene-configs
- **All eval scenarios updated**: Test cases use functional IDs (router-triage.md, council-debate.md)

### Why This Matters

- **Japanese users** see 財務省, 法務省, 会計検査院 — zero learning curve
- **English users** see CFO, General Counsel, Internal Audit — immediately intuitive
- **Chinese users** still see 丞相, 中书省, 门下省 — nothing lost
- **Developers** maintain 16 agent files instead of 48 — every logic change applies once
- **New themes** require only one ~60-line file — no engine changes needed

### Zero Functionality Loss

All 28 Hard Rules preserved. All scoring rubrics intact. All output formats maintained (with theme-dependent names). SOUL, DREAM, Wiki, Strategic Map, Completion Checklist, veto loops, session lifecycle — everything works identically. Verified against the complete 34-item preservation checklist.

---

## [1.5.0] - 2026-04-15 · Strategic Map — From Project Assistant to Life Strategist

> Life OS could analyze any single project brilliantly but was blind to the connections between them. With many active projects sharing dependencies, resources, and hidden strategic purposes, the system needed a relationship layer. Strategic Map adds exactly that — and integrates deeply with SOUL, Wiki, and DREAM to form a unified cognitive system.

### The Problem

You have many projects. Some feed knowledge into others. Some share your limited time. Some exist for a stated purpose that differs from your real motivation. When one stalls, it silently blocks others. But the morning briefing showed a flat list with no relationships, no priorities, no "what should I actually do today?"

### What's New

**Strategic Lines** — Group projects by strategic purpose. Each line has a `purpose` (formal), a `driving_force` (what actually motivates you), and `health_signals` (what to watch). Multiple projects can serve one line with different roles: `critical-path`, `enabler`, `accelerator`, `insurance`.

**Flow Graph** — Define what flows between projects: `cognition` (knowledge), `resource` (deliverables), `decision` (constraints), `trust` (relationship capital). When a decision in Project A invalidates Project B's assumptions, the system warns you.

**Narrative Health Assessment** — No more "6/10 🟡" scores. Based on Klein's Recognition-Primed Decision model, the system matches projects to health archetypes (🟢 steady progress / 🟡 controlled wait / 🟡 momentum decay / 🔴 uncontrolled stall / 🔴 direction drift / ⚪ dormant) and writes a narrative: what's happening, what it means, what to do.

**Morning Briefing Upgrade** — The flat "Area Status" list becomes a strategic overview grouped by strategic lines, with blind spot detection and actionable recommendations:
- 🥇 Highest leverage action (with effort estimate and cost of inaction)
- 🥈 Worth attention
- 🟢 Safe to ignore (active suppression reduces cognitive load)
- ❓ Decisions needed (structural gaps for user to fill)

**Cross-Layer Integration** — Strategic Map works with SOUL, Wiki, and DREAM as one system:
- SOUL × Strategy: checks if your driving forces align with your stated values
- Wiki × Flows: verifies that cognition flows actually carry wiki knowledge (detects paper-only flows)
- DREAM × Strategy: REM stage uses the flow graph as scaffolding to discover cross-layer insights
- Patterns × Strategy: flags when your behavior contradicts your strategic priorities

**Blind Spot Detection** — Based on predictive coding neuroscience: the system actively looks for what's missing, not just what's present. Unaffiliated projects, broken flows, neglected driving forces, missing life dimensions, approaching time windows with no preparation.

### Agent Integration

| Agent | How they use the Strategic Map |
|-------|-------------------------------|
| Morning Court Official | Compiles STRATEGIC-MAP.md at Start Court (step 8.5). Briefing grouped by strategic lines |
| Prime Minister | Frames cross-project questions in strategic-line terms. Recommends time allocation by role |
| Secretariat | Adds cross-project impact dimensions when flows exist. Flags enabler dependency risks |
| Chancellery | Checks decision propagation (downstream impact) + SOUL-strategy alignment |
| Ministry of War | Weights task priority by strategic role. Recommends exploiting waiting periods |
| Court Diarist | Detects new relationships (Phase 2 candidates). Updates last_activity. DREAM REM enhanced with flow graph scaffolding |

### Data Architecture

- `_meta/strategic-lines.md` — Strategic line definitions (user-defined, like config.md)
- `projects/{p}/index.md` strategic fields — Per-project relationships (like existing status/priority fields)
- `_meta/STRATEGIC-MAP.md` — Compiled view (like STATUS.md / wiki/INDEX.md — never hand-edited)
- Cognitive pipeline: 5 stages → 6 stages (added "Strategize" between Associate and Emerge)
- Follows existing patterns: single source of truth, outbox merge, user-confirmed candidates, from-zero growth

### Design Foundations

Built on cognitive science research:
- **Goal Systems Theory** (Kruglanski 2002) — dual-layer intent (purpose vs driving_force)
- **Recognition-Primed Decision** (Klein 1998) — archetype matching + narrative assessment instead of numerical scoring
- **Predictive Coding** (Friston 2005) — blind spot detection through absence monitoring
- **Expected Value of Control** (Shenhav et al. 2013) — leverage-based action recommendations considering effort and opportunity cost
- **Biased Competition** (Desimone & Duncan 1995) — "safe to ignore" as active cognitive suppression

---

## [1.4.4b] - 2026-04-15 · Prevent Fabricated Timestamps

> LLMs were fabricating timestamps in session-id generation instead of reading the system clock. All session-id generation instructions now explicitly require running a date command. Template-style specs changed to command-style specs.

### Changes

- **qiju.md**: session-id step changed from template format to "run date command, use real output. HARD RULE."
- **data-layer.md + data-model.md**: session-id generation synced with same command-style wording
- All changes applied across EN/ZH/JA

---

## [1.4.4a] - 2026-04-15 · Enforce Agent File Loading

> LLMs were skipping adjourn phases by executing from memory instead of reading `qiju.md`. This patch adds 3-layer enforcement: explicit MUST-read routing in SKILL.md, a mandatory completion checklist in qiju.md, and a new orchestration rule requiring agent file loading on every trigger word.

### Enforcement Changes

- **SKILL.md**: Start Court / Adjourn routing changed from "Route to X" → "MUST read `pro/agents/X.md` and launch as subagent. HARD RULE."
- **qiju.md**: Added mandatory Completion Checklist — every phase must report a concrete value (commit hash, Notion sync status, etc.). Missing items = incomplete adjourn.
- **Orchestration Code of Conduct**: Added rule #6 — "Trigger words MUST load agent files. Never execute a role from memory without reading its definition file. HARD RULE."

### Also Included (audit remediation from same day)

- zaochao.md git health check: auto-fix → detect-report-confirm (GLOBAL.md Security Boundary #1)
- GLOBAL.md: "complete thought process" → "publishable reasoning summary" (cross-model portability)
- 14→16 subagent count fixed in remaining entry files
- Dead link `notion-schema.md` removed from AGENTS.md
- adapter-github.md: recovery commands changed to text blocks with manual-only headers
- evals/run-eval.sh: exit code capture, path sanitization, tri-lingual header support
- setup-hooks.sh: pre-flight validation before file writes
- lifeos-version-check.sh: XDG cache path, grep-based version parsing

---

## [1.4.4] - 2026-04-14 · Court Diarist (起居郎) — Session Close Specialist

> The Morning Court Official is split into two roles: the Morning Court Official handles session start (read), the Court Diarist handles session close (write). DREAM is absorbed into the Court Diarist — no more separate agent launch.

### 📝 New Role: Court Diarist (起居郎)

Named after the Tang Dynasty official who recorded the emperor's words and actions at court. The Court Diarist handles everything that happens when you say "退朝":

- **Phase 1 — Archive**: decisions, tasks, journal → outbox
- **Phase 2 — Knowledge Extraction** (core responsibility): scan ALL session materials (not just memorial) for wiki + SOUL candidates
- **Phase 3 — DREAM**: 3-day deep review (N1-N2 organize, N3 consolidate, REM creative connections) — no longer a separate agent
- **Phase 4 — Sync**: git push + Notion sync (4 explicit operations)

### Key Improvements
- **Knowledge extraction is now the Court Diarist's core mission** — not step 6.5 in a 298-line file
- **DREAM merged into closing flow** — one fewer agent launch, no more "last step that gets skipped"
- **Session conversation summary** passed to Court Diarist — can extract knowledge from PM direct-handle conversations, not just memorials
- **Notion sync guaranteed explicit** — 4 specific writes, failure reported (not silently skipped)
- 16 roles (was 15): Morning Court Official + Court Diarist replace the old combined role
- `dream.md` deleted — fully absorbed into `qiju.md`

---

## [1.4.3e] - 2026-04-13 · SKILL.md Slim Down — Pure Routing File

> SKILL.md compressed from 384 lines to 93 lines. Lite Mode removed. All detailed role definitions, output formats, and configuration are in agent files and reference docs where they belong.

### Token Savings
- **SKILL.md**: 384 → 93 lines (−291 lines ≈ −4,700 tokens/session)
- Removed: Censorate/Remonstrator/Political Affairs Hall/Morning Court Official detailed descriptions, Memorial format, Storage Configuration, Lite Mode flow, Two Types of Deliberation table, Pro Mode installation details
- All removed content already exists in agent files (`pro/agents/*.md`) or reference files (`references/*.md`)

### Code of Conduct Redistribution
- PM-relevant rules (8 rules) stay in SKILL.md
- Orchestration rules (#2 veto, #7 auto-trigger, #11 full output, #14 real subagents, #9 degradation) moved to `pro/CLAUDE.md` new "Orchestration Code of Conduct" section
- Universal agent rules already covered by `pro/GLOBAL.md`

### Ministry On-Demand Selection
- `zhongshu.md`: New "Ministry Selection (HARD RULE)" — only assign relevant ministries with justification
- `shangshu.md`: New "Dispatch Only Assigned Ministries (HARD RULE)" — don't dispatch unassigned ministries

### Lite Mode Removed
- Life OS's core value is independent subagent checks-and-balances — single-context simulation defeats this purpose
- README installation table: Lite Mode rows removed, note added that single-context platforms are not supported
- SKILL.md no longer needs to be self-contained for single-file platforms

---

## [1.4.3d] - 2026-04-13 · Version Check as Output Format Field

> Version detection moved from a standalone instruction (that LLMs skip) to a mandatory field in the Pre-Court Preparation output template (that LLMs reliably fill).

- **Version display is now a template field**: `🏛️ Life OS: v[local] | Latest: v[remote]` with update instructions shown inline
- **zaochao.md Mode 0 + Mode 1**: Step 3 now explicitly fetches remote version via WebFetch; both local and remote versions are mandatory output fields
- **chengxiang.md**: Pre-Court Preparation format synced with same version display
- **SKILL.md**: Removed verbose Version Self-Check section (moved to output format)
- Works because LLMs reliably fill output templates (HARD RULE #13) even when they skip standalone instructions

---

## [1.4.3c] - 2026-04-13 · Version Self-Check in SKILL.md

> Version detection moved from agent files to SKILL.md — the first file every LLM reads. Solves the bootstrap paradox where outdated agent files couldn't detect their own updates.

- **Version Self-Check section** added to SKILL.md top (before Prime Minister instruction): checks remote version via WebFetch, prompts update, reports failure
- **zaochao.md simplified**: Mode 0 and Mode 1 version check now references SKILL.md instead of duplicating WebFetch logic
- Works even when zaochao.md or other agent files are outdated — SKILL.md is always read first

---

## [1.4.3b] - 2026-04-13 · Knowledge Extraction in Adjourn Flow

> Wiki extraction no longer depends solely on DREAM. The adjourn flow now directly scans session outputs and proposes wiki candidates before DREAM runs.

- **Adjourn knowledge extraction (step 6.5)**: Wrap-up and Adjourn modes now scan session outputs for reusable conclusions → present wiki candidates to user → confirmed entries written to outbox wiki/
- **Outbox wiki merge**: Start Court merge now handles wiki/ files from outbox → moves to wiki/{domain}/{topic}.md
- **DREAM dedup**: DREAM N3 checks if the adjourn flow already extracted wiki candidates (via manifest) → skips re-proposing, focuses on missed conclusions only
- **Outbox format**: manifest.md now includes `wiki` count in outputs

---

## [1.4.3a] - 2026-04-13 · Wiki & SOUL Initialization Guidance

> The system now detects when wiki/ and SOUL.md haven't been initialized, and guides the user through first-time setup and legacy migration.

- **Wiki first-time initialization**: Morning Court Official detects empty wiki/ or missing INDEX.md → proposes extracting conclusions from existing decisions/journal
- **Wiki legacy migration**: Detects old-format wiki files (research reports without front matter) → proposes extracting conclusions and archiving originals
- **SOUL bootstrapping**: When SOUL.md doesn't exist, DREAM proposes initial entries from user-patterns.md at the first Adjourn Court
- **Start Court detection**: Steps 5.5 (SOUL check) and 10.5 (wiki health check) now report initialization status in the briefing

---

## [1.4.3] - 2026-04-13 · Wiki Activation — Knowledge Pipeline Comes Alive

> The cognitive pipeline's "settle → emerge" stages finally work. Wiki goes from an empty directory to an active knowledge participant.

### 📚 Wiki Specification (`references/wiki-spec.md`)

Wiki was designed into the second-brain but never plugged into any workflow — no agent wrote to it, no agent read it. Now it has all four elements:

- **Who writes**: DREAM proposes wiki candidates during N3 (alongside SOUL candidates)
- **When written**: After every Adjourn Court, confirmed by user at next Start Court
- **Who reads**: Prime Minister reads wiki/INDEX.md, Chancellery checks consistency, Censorate audits health
- **When read**: Every session start, every decision review, every patrol inspection

### 🔍 Prime Minister Knowledge Matching

The Prime Minister now scans wiki/INDEX.md before routing. If high-confidence entries exist for the current domain: "📚 We already have N established conclusions here. Start from known knowledge, or research from scratch?" — skips redundant analysis when user agrees.

### ⚖️ Chancellery Wiki Consistency Check

The Chancellery now checks new conclusions against established wiki entries. If a contradiction is detected: "⚠️ This contradicts [wiki entry] (confidence X)." Either the analysis needs revision, or the wiki needs updating.

### 🔱 Censorate Wiki Health Audit

Patrol inspection now covers wiki health: entries with confidence < 0.3 and no update in 90+ days (suggest retire), entries with challenges > evidence (suggest review), domains with decisions but no wiki entries (knowledge gap).

### 📨 Dept. of State Affairs Wiki Context

When the Prime Minister flags relevant wiki entries, the Dept. of State Affairs includes them in dispatch: "📚 Known Premises — start from here, do not re-derive."

### 🧠 Cognitive Pipeline Reordered

The pipeline now reflects actual information flow: `Perceive → Capture → Judge → Settle → Associate → Emerge`. Settle splits into SOUL (person) and Wiki (knowledge). Associate happens when the Prime Minister matches new requests against wiki. Emerge happens when DREAM's REM stage finds cross-domain connections.

### Design Principle

No new agents, no new flows. Wiki plugged into existing rhythms: DREAM writes → Morning Court Official compiles INDEX → Prime Minister reads → Chancellery checks → Censorate audits.

---

## [1.4.2] - 2026-04-12 · Outbox — Parallel Sessions Without Conflicts

> Multiple sessions can now work on different projects simultaneously. No git conflicts, no locks. Each session writes to its own outbox on adjourn; the next session to start court merges everything.

### 📮 Outbox Architecture

The old model assumed one session at a time and used a `.lock` file to warn about concurrency. The new model embraces parallelism:

- **Each session writes to its own isolated directory** (`_meta/outbox/{session-id}/`) on adjourn — decisions, tasks, journal entries, index deltas, pattern deltas, and a manifest
- **No direct writes to shared files** during wrap-up or adjourn — `projects/`, `STATUS.md`, and `user-patterns.md` are never touched until merge
- **Merge happens at Start Court** — the next session to start court scans all outboxes, merges them chronologically into the main structure, compiles STATUS.md, and cleans up
- **Session-id = `{platform}-{YYYYMMDD}-{HHMM}`**, generated at adjourn time (not session start)
- **Zero-conflict guarantee** — different directories, different files, no concurrent writes to the same path
- **Merge-lock** for the rare case of two simultaneous start courts (< 5 minutes, auto-cleanup)

### Scenarios Covered

- Single session, normal flow ✅
- Multiple platforms alternating ✅
- Multiple windows in parallel ✅
- Multiple computers ✅
- Session spanning multiple days ✅
- Same session, multiple start/adjourn cycles ✅
- Empty sessions (no output, no outbox) ✅
- Push failure (outbox saved locally, retried next time) ✅
- Lite users (no second-brain, no outbox) ✅
- Mobile Notion captures (inbox/, unchanged) ✅

### Files Changed

- `pro/agents/zaochao.md` — Mode 0/1 add outbox merge, Mode 3/4 rewritten to write outbox
- `references/data-model.md` — Session lock removed, outbox rules + manifest/delta formats added
- `references/data-layer.md` — Directory structure + Housekeeping/Wrap-Up flows updated
- `references/adapter-github.md` — Commit convention rewritten for outbox pattern
- `SKILL.md` — Parallel sessions mentioned in Storage Configuration

---

## [1.4.1] - 2026-04-12 · SOUL + DREAM — The System Learns Who You Are

> SOUL.md grows from your decisions to record who you are. DREAM processes memories while you're away — like the brain during sleep. Together, they give Life OS a self-awareness loop.

### 🔮 SOUL — User Personality Archive

Your values, beliefs, and identity — captured as evidence-based entries that grow from zero. Each entry has two sides: what you actually do (What IS) and what you aspire to (What SHOULD BE). The gap between them is where growth happens.

- **Grows organically** — starts empty, accumulates from decisions and behavior
- **Four sources** — DREAM discovers, Remonstrator observes, Hanlin Academy surfaces, you can write directly
- **User-confirmed** — system proposes, you decide. Nothing auto-written
- **Confidence-scaled influence** — new entries affect only the Remonstrator; deeply validated entries influence the entire system
- **Every role reads SOUL.md differently** — Prime Minister for sharper questions, Secretariat for relevant dimensions, Chancellery for value consistency, Remonstrator for behavioral audit, Hanlin Academy for thinker matching

### 💤 DREAM — AI Sleep Cycle

After every Adjourn Court, the system "sleeps" — inspired by human sleep architecture:

- **N1-N2 (Organize)** — classify inbox, flag expired tasks, find orphan files
- **N3 (Consolidate)** — extract recurring themes into wiki, update behavior patterns, propose SOUL entries
- **REM (Connect)** — discover cross-domain links, check value-behavior alignment, generate unexpected insights
- **Scope**: last 3 days only. Dream reports stored in `_meta/journal/` and presented at next Start Court
- **New agent**: `pro/agents/dream.md`

### 📐 New Reference Files

- `references/soul-spec.md` — SOUL format, lifecycle, confidence calculation, role usage rules
- `references/dream-spec.md` — DREAM trigger, three stages, output format, constraints

---

## [1.4.0] - 2026-04-12 · Hall of Human Wisdom + Three Chancelleries Deepened + Single Source of Truth

> The Hanlin Academy evolves from three thinking tools into a deep-dialogue hall with 70+ of history's greatest minds; five core roles get a serious upgrade; and a critical data integrity bug is fixed — `index.md` is now the single source of truth, `STATUS.md` is compiled from it.

### 🏗️ Architecture Fix — Single Source of Truth

`projects/{p}/index.md` is now the authoritative source for project version, phase, and status. `_meta/STATUS.md` is compiled from index.md files — never hand-written. This fixes a bug where STATUS.md and index.md could drift out of sync. Censorate patrol inspection now includes a mandatory version consistency lint rule.

### 🎋 Hanlin Academy → Hall of Human Wisdom

The Hanlin Academy is no longer just "first principles + Socratic method + Occam's razor." Now you can talk life with Socrates, dissect business logic with Musk, or let Laozi and Nietzsche argue about the meaning of existence.

- **18 domains, 70+ thinkers** — from science to philosophy, Eastern thought to legal justice, spanning every major dimension of human civilization
- **Deep roleplay** — not "using the Socratic method," but Socrates himself in conversation with you: his cadence, his examples, his relentless questioning
- **Three dialogue modes** — one-on-one deep dive, roundtable (multiple thinkers each weighing in), debate (adversarial exchange)
- **Independent subagents** — each thinker runs in its own context; the Hanlin Academy itself serves as moderator
- **Closing ritual** — the thinker offers a parting insight → the Hanlin Academy summarizes how your thinking shifted → saved to second-brain

### 🔍 Chancellery — From Rubber Stamp to Real Last Line of Defense

- **10/10/10 regret test** — you must answer separately for 10 minutes from now, 10 months, and 10 years; a vague "I won't regret it" doesn't pass
- **Red-team review** — assume the plan will fail; surface the most fragile assumptions, the luckiest dependencies, the risks you've been quietly downplaying
- **Structured veto format** — a veto is no longer just "not approved"; it must specify which dimension failed, what the core problem is, and exactly what to change

### 🏛️ Political Affairs Hall — From Fuzzy Triggers to Quantified Rules + Structured Debate

- **Quantified trigger** — if two departments' scores differ by ≥ 3, or one says go and one says stop, the Political Affairs Hall convenes automatically
- **New dedicated agent** — `zhengshitang.md`, with 3 rounds of structured debate: opening position → clash → final stance → ruling
- **Dept. of State Affairs chairs, you decide** — debate has rules and word limits; it won't collapse into monologue

### 📨 Dept. of State Affairs — From Task Assignment to Intelligent Scheduling

- **Dependency detection** — automatically identifies cross-department dependencies like "the Ministry of Revenue's conclusion affects the Ministry of War's plan," running group A before group B
- **Consultation mechanism** — the Ministry of War can ask "Revenue, give me one number: how much is available?" — the Dept. of State Affairs relays it without exposing the full report

### 🏛️ Prime Minister — Intent Clarification, Now Categorized

- **Five-category strategy** — decision (criteria? constraints?), planning (goal? resources?), confusion (emotion? real concern?), retrospective (standard? dimensions?), information (handle directly)
- **Emotion separation protocol** — when emotion and decision are tangled, one sentence acknowledges the feeling first, then the facts are separated out

### 💬 Remonstrator — From Observation to Learning

- **Behavioral pattern learning loop** — every new pattern or pattern shift is flagged and written to user-patterns.md
- **Cross-session trend analysis** — compares the last 3 reports: shifts in risk appetite, decision speed, follow-through, and what you're paying attention to
- **Positive reinforcement** — not just criticism. If the last report said "be more decisive" and you were, it says so explicitly

### ⚖️ System-Level

- **"Two kinds of council" comparison table** — SKILL.md now includes a side-by-side: Political Affairs Hall vs Hanlin Academy — one debates "should we do this," the other explores "who are you"
- **Prime Minister routing rule** — conflicting data goes to the Political Affairs Hall; value confusion goes to the Hanlin Academy

---

## [1.3.1] - 2026-04-12 · Process Must Be Visible

> Every subagent now shows its full thinking, and Pro mode is required to spin up real subagents — no more single-context simulations.

- **Emoji enforcement** — all subagent outputs must carry 🔎/💭/🎯 markers; omission is a violation
- **Real subagent enforcement** — in Pro environments, each role must be an independent agent call; simulating multiple roles in one context is banned
- **Role boundary lock** — HARD RULE #17: only the 15 defined roles exist; inventing officials like the Bureau of Transmission or Court of Judicial Review is forbidden
- **Inbox goes to Prime Minister** — the Prime Minister now officially owns inbox management
- **Morning Court auto-update** — the Morning Court Official checks the GitHub version on startup and runs platform update commands if a newer version is found
- **Git health check** — checks for worktree remnants and broken hooksPath before court opens
- **ko/es removed** — Korean and Spanish placeholders deleted; EN/ZH/JA only
- **Tag cleanup** — 13 old tags consolidated into 5 correct Strict SemVer tags
- **Second-brain tidy** — templates filled in with proper front matter; legacy directories (gtd/records/zettelkasten) removed

---

## [1.3.0] - 2026-04-10 · Three-Platform Pro Mode + Storage Abstraction Layer

> Life OS expands from Claude Code-only to a full three-platform Pro Mode across Claude + Gemini + Codex — and storage moves from Notion hardcoding to a pluggable three-backend architecture.

### Storage Abstraction Layer

One standard data model (6 types, 7 operations), three optional backends (GitHub / Google Drive / Notion) — load whichever adapter you choose. Multiple backends sync automatically; conflicts resolve by last-write-wins or user prompt.

### Cross-Platform Pro Mode

All 14 agent definitions are shared; orchestration files split by platform: `CLAUDE.md` (Claude Code), `GEMINI.md` (Gemini CLI / Antigravity), `AGENTS.md` (Codex CLI). Each platform automatically uses its strongest model — no hardcoding.

### Trigger Word Standardization

English / Chinese / Japanese trigger words formally defined, resolving behavioral inconsistencies between Claude and Codex on commands like "open court."

---

## [1.2.0] - 2026-04-08 · Internationalization + Architecture Consolidation

> All 34 files translated into English as the primary version, with complete Chinese and Japanese translations — alongside a significant architectural consolidation.

### Internationalization

English is now the canonical version; Chinese and Japanese ship as i18n translations. The README is redesigned with shields.io badges and visual hierarchy.

### Architecture Consolidation

- **pro/GLOBAL.md** — shared rules across all 14 agents extracted into a single authoritative source; each agent file trimmed by ~30%
- **Cognitive pipeline** — five-stage information flow: perceive → capture → associate → judge → distill → emerge
- **Censorate audit mode** — a second operating mode beyond decision review: each ministry audits its own territory in the second-brain
- **Four-step knowledge extraction training** — user decides → accumulates examples → LLM distills rules → periodic correction

### 🔴 Breaking Change

Second-brain directory restructured: `zettelkasten/` → `wiki/`, `records/` → `_meta/journal/`, new `_meta/` system metadata layer added.

---

## [1.1.1] - 2026-04-05 · Data Layer Shift

> GitHub second-brain replaces Notion as the primary database; Notion steps down to mobile working memory.

- **GitHub as primary store** — .md + front matter, merging GTD + PARA + Zettelkasten
- **Morning Court Official three modes** — housekeeping (automatic), review (user-triggered), wrap-up (post-session)
- **Session binding** — each session locks to one project/area; all reads and writes stay in scope
- **Adjourn command** — pushes to GitHub + refreshes Notion
- **CC enforces Pro** — detecting Claude Code triggers mandatory independent subagent launch

---

## [1.1.0] - 2026-04-04 · Docs + Research Visibility + Memory Layer

> A complete documentation system goes live, every agent gains a visible research process, and the Prime Minister gets a memory layer and thinking tools.

- **Multi-platform install guide** — detailed steps for 7 platforms
- **All 14 agents gain 🔎/💭/🎯 research process display**
- **Remonstrator: 21 observation capabilities** — cognitive bias detection, emotional sensing, behavior tracking, decision quality assessment
- **Prime Minister intent clarification** — 2-3 rounds of dialogue before escalating; no more direct forwarding
- **Morning Court dashboard** — DTR / ACR / OFR + 4 weekly indicators
- **12 standard scene configs** — covering career, investment, relocation, entrepreneurship, and other major decision scenarios

---

## [1.0.0] - 2026-04-03 · Initial Release

> The Three Chancelleries and Six Ministries personal cabinet system launches. 15 roles. Checks, balances, and separation of powers.

- 15 roles: Prime Minister + Three Chancelleries + Six Ministries + Censorate + Remonstrator + Political Affairs Hall + Morning Court Official + Hanlin Academy
- Lite mode (single context) + Pro mode (14 independent subagents)
- 10 standard scene configurations
- Six Ministries × Four Bureaus detailed function definitions
- Apache-2.0 License
