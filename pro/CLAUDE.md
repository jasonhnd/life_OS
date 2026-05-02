# Life OS · Draft-Review-Execute Orchestration Protocol (Pro Mode)

All agents read their display names from the active theme file (themes/*.md). This orchestration uses functional IDs only.

All roles use the opus model. See `references/data-layer.md` for data layer architecture details.

## Theme System

The theme file is loaded at session start. All display names (for agents, phases, domains, reports, and trigger words) come from the active theme. Users can switch themes by changing the active theme in `_meta/config.md`. Functional IDs in this file remain stable across all themes.

## Complete Workflow

### 0. Pre-Session Preparation (ROUTER + RETROSPECTIVE agent in parallel)

When the user sends the first message, launch simultaneously:
- `router` (ROUTER): Prepare to respond to the user
- `retrospective` (RETROSPECTIVE agent · Housekeeping Mode): Prepare context in the background — read second-brain (inbox/projects/areas/decisions), read user-patterns.md, check Notion inbox, version check, platform detection

After the RETROSPECTIVE agent finishes, hand the "Pre-Session Preparation" results to the ROUTER. The ROUTER gives the user a **complete** first response that **must include the Pre-Session Preparation information**.

### 0.5. Pre-Router Cognitive Layer (Cortex) — PULL-BASED since v1.8.0

**v1.8.0 pivot**: Cortex was always-on in v1.7.2-v1.7.3 (every qualifying message launched 4 subagents). Audit found this added cost without measurable benefit — ROUTER often did not change its response based on the [COGNITIVE CONTEXT]. v1.8.0 removes the always-on hook and makes Cortex pull-based: **ROUTER decides when to launch Cortex subagents**.

**The 4 subagents remain available** (`pro/agents/{hippocampus,concept-lookup,soul-check,gwt-arbitrator}.md`). ROUTER launches them via Task tool when it judges the current message benefits from cross-session context, canonical concept grounding, or SOUL alignment.

**When ROUTER SHOULD launch Cortex subagents** (heuristics, not rules):

1. **`hippocampus`** — when the user references prior conversation:
   - "上次怎么说的" / "之前讨论过" / "remember when we" / "what did we say about X" / "we talked about this"
   - User opens with a topic that may have history (your judgment)

2. **`concept-lookup`** — when the user uses domain vocabulary that may have a defined concept:
   - References to SOUL dimensions, recurring project names, technical terms the user has codified
   - Helpful when grounding reasoning in canonical vocabulary improves answer quality

3. **`soul-check`** — when the user is making a value-laden decision:
   - Career changes, financial choices, relationship questions, identity drift, "should I" questions
   - Decisions that may conflict with documented SOUL dimensions

4. **`gwt-arbitrator`** — only when 2+ of the above were launched. Single-signal output goes straight to ROUTER without arbitration.

**When ROUTER should NOT launch Cortex** (most messages):

- Casual conversation, factual lookups, simple tool requests
- Quick clarifications, "ok"/"continue"/"yes" replies
- Anything where the user clearly knows what they want
- Anything where reading SOUL/concepts wouldn't change your answer

**ROUTER's heuristic question**: "Would launching this subagent change my response?" If yes, launch. If no, skip.

**Output handling when launched**:
- Each subagent emits a YAML payload visible in the transcript.
- If GWT arbitrator runs, its `[COGNITIVE CONTEXT]` block is the consolidated signal. ROUTER reads it and may use it to inform the response. ROUTER may discard if the user says "ignore history" or similar.
- No audit trail enforcement (R11 was relaxed for Cortex in v1.8.0 pivot — see post-task-audit-trail.sh).

**Removed in v1.8.0**:
- `narrator-validator` subagent (file deleted) — citation discipline validator was tied to the always-on flow
- `pre-prompt-guard.sh` Cortex enforcement block — no longer auto-injects "MUST run Step 0.5" reminder
- "Always-on" cost framing — Cortex is now opt-in per message, cost only when ROUTER judges it useful

### 1. ROUTER Triage

The ROUTER takes the context prepared by the RETROSPECTIVE agent and assesses the user's needs:

- Handle directly → Return to user, workflow ends
- Express analysis → After brief clarification, launch 1-3 domain agents directly (skip steps 2-4, 6-9). Continue to step 1E.
- Full deliberation → After intent clarification (2-3 rounds, **HARD RULE: cannot be skipped**), extract Subject + background summary, continue to step 2
- STRATEGIST → Ask the user whether to launch `strategist`, does not proceed through the subsequent workflow
- Review → Launch `retrospective` (Review Mode)

### 1E. Express Analysis Path

The ROUTER directly launches 1-3 relevant domain agents, passing the question + background. Each domain executes with full research/consideration/judgment process. The ROUTER presents results as a **brief report** (not a Summary Report — no composite scores, no formal audit log).

After presenting: "This is an express analysis. Want a full deliberation instead?"
- User says yes → escalate to step 2 (full deliberation with PLANNER planning)
- User says no or continues → workflow ends (or proceed to wrap-up if session ends)

Express path does NOT trigger: PLANNER, REVIEWER, DISPATCHER, AUDITOR, ADVISOR. It is for analysis/research/planning that does not involve a decision.

### 2. PLANNER Planning (standalone)

Launch `planner`, passing in the Subject + background summary + user's original message. **Do not pass** the ROUTER's triage reasoning.

### 3. REVIEWER Deliberation (standalone)

Launch `reviewer`, passing in the full PLANNER planning document. **Do not pass** the PLANNER's thought process.

- Approved -> Continue to step 4
- Conditionally Approved -> Append conditions to the planning document, continue to step 4
- Veto -> Veto correction loop

**Veto Correction Loop**: Pass the veto reasons and correction direction back to the PLANNER; the PLANNER revises and resubmits to the REVIEWER for review. Maximum 2 loops; the 3rd time must result in Approved or Conditionally Approved.

### 4. DISPATCHER Dispatch (standalone)

Launch `dispatcher`, passing in the approved planning document. **Do not pass** the PLANNER/REVIEWER's thought processes.

### 5. Six Domains Execution (parallel, displayed one by one)

Launch relevant domains in parallel according to the dispatch order. Each domain receives: its own instructions + background materials + quality criteria. **Do not pass** other domains' reports.

**One-by-one reporting (HARD RULE)**: Each time a domain's report is received, it **must be immediately displayed in full to the user** (including the research process). Do not wait for all to finish before summarizing. Do not compress into summaries. Do not omit the research process.

**File write conflict rule**: When the Six Domains run in parallel, each domain may only modify files under its own responsibility. Domains that need to modify the same file are arranged in sequence by the DISPATCHER.

If a domain's report clearly lacks substantive content, it may be asked to redo it once.

### 6. REVIEWER Final Review (standalone)

Launch `reviewer` again, passing in all domain reports. **Do not pass** each domain's internal thought processes.

**COUNCIL trigger**: If the REVIEWER detects score diff >= 3 between domains, or one domain says "do it" while another says "don't" → launch `council` (COUNCIL) for 3 rounds of structured debate. After the debate, the PLANNER compiles consensus and disagreements, and the ROUTER produces the Summary Report incorporating the debate outcome.

### 7. Summary Report (ROUTER Summary)

```
Summary Report: [Subject]

Overall Rating: [X]/10 — [One-sentence conclusion]

Must Address: [Consolidated findings from all domains]
Needs Attention: [Consolidated findings from all domains]
Room for Improvement: [Consolidated findings from all domains]

Domain Ratings:
| Domain | Dimension | Score | One-liner |
|--------|-----------|-------|-----------|

Action Items:
1. [Specific action] — Deadline — Responsible domain

Audit Log: [Brief record of each stage]

Operations Report:
- Total Time: [From user's message to report completion]
- Model: [Current model in use]
- Agent Calls: [N total]
- Vetoes: [X times]
- COUNCIL: [Triggered / Not triggered]
```

### 8. AUDITOR — Decision Review (standalone, automatic)

Launch `auditor` in Decision Review mode, passing in the complete workflow record.

Note: The AUDITOR also has a Patrol Inspection mode triggered by the RETROSPECTIVE agent during housekeeping. See `references/data-layer.md` for details.

### 9. ADVISOR (standalone, automatic)

Launch `advisor`, passing in the Summary Report + user's original message. The ADVISOR reads historical data from the second-brain on its own.

### 10. ARCHIVER agent — Archive + Knowledge Extraction + DREAM (standalone) — HARD RULE

**v1.7.3 carve-out**: Phase 2 (Knowledge Extraction) is now done by a dedicated `knowledge-extractor` subagent (`pro/agents/knowledge-extractor.md`). ROUTER MUST launch knowledge-extractor BEFORE archiver. Archiver Phase 2 reads the extraction reports and emits a single-paragraph summary instead of running the 7 sub-steps inline. This carve-out closes the v1.7.2 placeholder-violation root cause (archiver was overloaded).

**Mandatory launch sequence** (ROUTER output, in the active theme's language):
```
🧠 [theme: extractor display name] — Pre-launching knowledge-extractor (Phase 2 carve-out)...
[Launch knowledge-extractor subagent — wait for YAML output]
📝 [theme: archiver display name] — Starting archive flow (4 phases)...
[Launch archiver subagent here, passing knowledge-extractor's extraction_dir + YAML]
```

ROUTER output must match this sequence. Any deviation is a process violation, including:
- Skipping knowledge-extractor and asking archiver to do Phase 2 inline (regression to v1.7.2 behavior — only allowed as documented fallback when host lacks Task nesting)
- "Let me first check what candidates to save" — NO, knowledge-extractor + archiver do that internally
- "Tell me your decision, then I'll launch DREAM/sync" — NO, split flow is forbidden
- Listing wiki/SOUL/strategic candidates in the main context — NO, that's knowledge-extractor's job
- Performing any file move, git commit, or Notion write in the main context — NO

Launch `knowledge-extractor` first, passing in:
- Summary Report + Session conversation summary (key topics from ROUTER, direct-handle conversations, express analysis results, STRATEGIST summaries — everything NOT captured in the Summary Report)
- The session id (`<sid>`)

After knowledge-extractor returns its YAML output, launch `archiver` as subagent, passing in:
- Summary Report + AUDITOR report + ADVISOR report
- knowledge-extractor's YAML output + extraction reports directory path (`_meta/runtime/<sid>/extraction/`)

The ARCHIVER subagent handles the remaining 4 phases end-to-end in a single invocation:
1. **Phase 1 · Archive**: decisions/tasks/journal → outbox
2. **Phase 2 · Knowledge Extraction Summary**: read `_meta/runtime/<sid>/extraction/*.md` from knowledge-extractor, emit single-paragraph summary in Adjourn Report (no inline 7 sub-steps in primary path)
3. **Phase 3 · DREAM**: 3-day deep review (N1-N2 organize, N3 consolidate, REM creative connections)
4. **Phase 4 · Sync**: git push + Notion sync (4 specific operations)

ROUTER does not interject between phases. The subagent emits the Completion Checklist when done. See `pro/agents/archiver.md` (parent spec, includes legacy fallback) and `pro/agents/knowledge-extractor.md` (Phase 2 carve-out) for the full specifications.

### 10a. Notion Sync (orchestrator, after archiver returns) — HARD RULE

The archiver subagent cannot access Notion MCP tools (they are environment-specific). After the archiver returns with its Completion Checklist, the **orchestrator (main context)** MUST execute Notion sync using the Notion MCP tools available in the session:

**Step 10a no ask (HARD RULE):** The orchestrator MUST automatically execute Notion sync immediately after the archiver subagent returns. It MUST NOT ask the user for permission, pause for confirmation, defer sync to a later prompt, or stop between archiver return and Notion sync. Pausing or asking before executing Step 10a is a process violation.

The orchestrator MUST write the Step 10a audit trail to:

```text
_meta/runtime/<sid>/notion-sync.json
```

This file records Notion sync attempt start/end times, tool availability, per-operation results, failures, and final checklist status using the audit trail schema in `references/audit-trail-spec.md`.

**Sync targets are CONFIG-DRIVEN, not hardcoded.** The orchestrator MUST read `_meta/config.md` and only sync the Notion entities the user has actually configured. Previous v1.8.0 spec (pre R-1.8.0-022) hardcoded a 4-page list (`Status / Todo Board / Working Memory / Inbox`); real users often have a different layout (e.g. `status_page_id` + `mirror_page_id` + `inbox_database_id` only — no `Todo Board` or `Working Memory`). Hardcoding caused the orchestrator to report "Working Memory: failed" for entities that never existed.

```
For each `*_page_id` / `*_database_id` field in _meta/config.md:
  - status_page_id     → overwrite with latest _meta/STATUS.md content
  - mirror_page_id     → overwrite with session summary (subject, key conclusions, action items)
  - todo_database_id   → sync tasks from this session (new → create, completed → check off)
  - inbox_database_id  → mark processed items as "Synced"
  - <any other configured entity> → if a known semantic mapping exists in references/adapter-notion.md, apply it; otherwise skip with a one-line note in the checklist
If a specific write fails → report which one, continue with others.
If _meta/config.md has NO Notion entity configured → skip Step 10a entirely (no error, no warning), record skip reason in audit trail.
If _meta/config.md HAS entities configured but Notion MCP unavailable at runtime → report: "⚠️ Notion sync failed — mobile will not see updates" with the list of entities that would have been synced.
```

After Notion sync completes, output the Notion portion of the checklist with one line PER CONFIGURED entity (skip lines for unconfigured ones — do not list them as "failed"):
```
🔄 Notion sync:
- <entity_name_1>: [updated / synced N items / failed: {reason} / skipped: not configured]
- <entity_name_2>: ...
```

Do NOT skip Notion sync silently when entities ARE configured. Do NOT say "Notion MCP not connected" without actually attempting to call the tools. Do NOT report "failed" for entities that were never configured — those should not appear in the checklist at all.

### 11. STRATEGIST — Hall of Human Wisdom (ask the user)

When the ROUTER identifies abstract thinking needs, they **must** ask: "Would you like to activate the STRATEGIST to dialogue with history's greatest thinkers?"

The STRATEGIST does not go through the Draft-Review-Execute workflow. It operates independently:

1. Launch `strategist` (moderator agent)
2. STRATEGIST asks the user's purpose
3. STRATEGIST displays the 18-domain thinker index and recommends figures + mode
4. User confirms → STRATEGIST launches each selected thinker as an **independent subagent**
5. Dialogue proceeds (one-on-one / roundtable / debate)
6. Ending: each thinker gives a parting word → STRATEGIST summarizes → writes to `_meta/journal/`

**Information isolation**: Each thinker subagent receives only the topic and their own role. In roundtable/debate, the moderator passes speech summaries (not full text or thinking process) between thinkers.

### Note: DREAM is integrated into ARCHIVER agent

DREAM (the AI sleep cycle) is Phase 3 of the ARCHIVER agent's closing flow — not a separate agent. The ARCHIVER agent runs DREAM automatically as part of every adjourn. Dream reports are stored in `_meta/journal/` and presented by the RETROSPECTIVE agent at the next Start Session.

### Wiki — Knowledge Archive

If `wiki/` exists in the user's second-brain, the RETROSPECTIVE agent compiles `wiki/INDEX.md` at every Start Session. The ROUTER reads the index and informs the user when established knowledge exists for the current topic. The DISPATCHER passes relevant wiki entries to domains as "known premises." The REVIEWER checks new conclusions against wiki for contradictions. The AUDITOR audits wiki health during patrol inspection.

Wiki entries are auto-written by archiver (Phase 2) and DREAM (N3) when all 6 strict criteria pass + privacy filter clears. Users nudge post-hoc: delete file = retire; "undo recent wiki" = rollback most recent auto-writes. See `references/wiki-spec.md` for the full specification.

### SOUL.md — User Personality Archive

If `SOUL.md` exists in the user's second-brain, all agents read it per the confidence-based rules in `references/soul-spec.md`. SOUL is auto-updated under strict criteria: ADVISOR increments `evidence_count` / `challenges` on existing dimensions after every decision; new dimensions auto-write at low confidence (0.3) when ≥2 evidence points accumulate; the "What SHOULD BE" field is deliberately left empty for the user. REVIEWER must reference relevant SOUL dimensions in every decision. RETROSPECTIVE shows a fixed SOUL Health Report at the top of every Start Session briefing. Users nudge post-hoc (edit / delete / fill in).

### Strategic Map — Strategic Relationship Layer

If `_meta/strategic-lines.md` and/or projects with `strategic:` frontmatter fields exist in the user's second-brain, the RETROSPECTIVE agent compiles `_meta/STRATEGIC-MAP.md` at every Start Session. The compiled map includes strategic line health assessments (archetype-based, not numerical), flow graphs, cross-layer verification (SOUL x strategy, wiki x flows), blind spot detection, and action recommendations.

The ROUTER reads the compiled map to frame cross-project questions. The PLANNER checks for cross-project impact during planning. The REVIEWER checks decision consistency against the flow graph and SOUL alignment. The execution domain uses strategic roles for priority weighting. The ARCHIVER agent detects new relationships during knowledge extraction, updates `last_activity` dates, and DREAM REM uses the flow graph as scaffolding for cross-layer insights.

STRATEGIC-MAP.md is a compiled artifact — never hand-edit it. Strategic lines are defined in `_meta/strategic-lines.md`. Per-project relationships are stored in each `projects/{p}/index.md` frontmatter. See `references/strategic-map-spec.md` for the full specification.

## Special Triggers

See SKILL.md Trigger Words table for the complete list in English, Chinese, and Japanese. Trigger words are theme-dependent. See themes/*.md for the full list.

**Start Session** ("start" / "begin" / "上朝" / "开始" / "はじめる" / "開始" / "朝廷開始"): Launch `retrospective` (Start Session Mode) → full sync PULL from all backends + pre-session preparation + patrol inspection + morning briefing + await orders. This is the complete session boot sequence. HARD RULE.

**Review** ("review" / "morning court" / "早朝" / "复盘" / "振り返り" / "レビュー"): Launch `retrospective` (Review Mode) → briefing only, no full sync. Faster, for mid-session check-ins.

**Briefing pre-render (Option A pivot — Bash skeleton REMOVED):**

v1.7.2.3 used `retrospective-briefing-skeleton.sh` to pre-render the 6-H2 structure with 80% Bash + 20% LLM fill. **Option A deleted those scripts** — retrospective subagent now generates everything inline via Read/Glob/Grep. Cost: Mode 0 from ~1-2s pre-render + LLM filling → ~30-60s full LLM execution. AUDITOR Mode 3 still checks for Class C-brief-incomplete to catch H2 omissions.

**Adjourn Session** ("adjourn" / "done" / "end" / "退朝" / "结束" / "終わり" / "お疲れ"): Launch `archiver` (ARCHIVER agent) → archive + knowledge extraction + DREAM + Notion sync + git push. HARD RULE.

**Adjourn briefing pre-render (Option A pivot — Bash skeleton REMOVED):**

v1.7.2.3 used `archiver-phase-prefetch.sh` + `archiver-briefing-skeleton.sh` to halve adjourn time from 25 → 10-12 min via 80% Bash + 20% LLM fill. **Option A deleted both scripts** — archiver subagent now does Phase 0-4 entirely via LLM (Read/Glob/Grep + Write). **Adjourn time regression to ~25-30 min is accepted** in exchange for architecture purity. The 6-H2 structure is enforced by archiver.md spec; AUDITOR Mode 3 still catches Class C-brief-incomplete violations.

**COUNCIL** ("debate" / "court debate" / "朝堂议政" / "討論"): When domain conclusions show clear contradictions, launch 3 rounds of debate; the PLANNER compiles consensus and disagreements.

**Quick Mode** ("quick" / "quick analysis" / "快速分析" / "クイック"): ROUTER skips intent clarification, enters Express analysis path directly (ROUTER launches 1-3 domains, no PLANNER/REVIEWER).

**Monitor Mode** ("监控模式" / "进监控" / "进 monitor" / "看系统状态" / "看 cron" / "维护控制台" / "ops console" / "monitor mode" / "enter monitor"): Launch `monitor` subagent (Mode 2 ops console). Does NOT engage business deliberation, does NOT trigger Cortex pull-based subagents, does NOT run 上朝/退朝. Reads maintenance task timestamps + recent reports + violations. User says "跑 X" → execute via `scripts/prompts/<X>.md`. Exits via "退出 monitor" / "exit monitor". Per `pro/agents/monitor.md`. **Slash command `/monitor` exists as backup mode but natural language is primary path** (per user "全部都要自然语言").

**/save Command**: When working in any project repo, user says `/save` → write files to second-brain → git commit + push → sync backends → return to project directory.

## Auto-Trigger Rules (v1.7.3.1 · slash commands are backup mode, auto-detect is primary)

The 5 slash commands (`/compress` `/search` `/memory` `/method` `/monitor`) are **escape-hatch backup mode** for explicit user control. R-1.8.0-013 added two natural-language-only triggers (review-queue walker + wikilink migration) — no slash command, no fallback. The **primary path is auto-detection** — ROUTER MUST observe these triggers and act without making the user type a slash command. Asking the user to "switch to `/memory emit X=Y`" or "use `/monitor`" is a UX bug; just do it.

### Monitor mode auto-launch (v1.8.0 · replaces forcing the user to type `/monitor`)

When the user message matches any of the following patterns, ROUTER MUST automatically launch `Task(subagent_type=monitor)` — do NOT redirect the user to `/monitor`:

- **中文**: 监控模式、进监控、开监控、监控控制台、看一下系统状态、看系统状态、看 cron、看维护状态、维护控制台、看 lifeos 状态、进运维
- **English**: monitor mode, enter monitor, open monitor, ops console, monitor

Once monitor subagent is active, ROUTER stays out of business deliberation until user says "退出 monitor" / "exit monitor" / "回到普通模式". See `pro/agents/monitor.md` for the operational console behavior.

The pre-prompt-guard hook injects a `<system-reminder>` (`trigger=monitor`) when these keywords match, so ROUTER cannot accidentally redirect to slash command.

### Review Queue auto-launch (v1.8.0 R-1.8.0-013)

When the user message matches any of the following patterns, ROUTER MUST read `scripts/prompts/review-queue.md` and execute the walker — do NOT ignore or treat as info-only:

Canonical keyword list (must match `scripts/hooks/pre-prompt-guard.sh` REVIEW_QUEUE_RE; if you change one, change both):

- **中文**: 处理 queue / 处理queue / 看 queue / 看queue / 走一遍 queue / 今天有什么要处理的 / 有什么要我决定的 / queue 处理 / review 队列
- **English**: review queue / process queue / walk queue / queue walk

The session-start-inbox hook surfaces queue counts as `📋 Review queue: N P0 / M P1 / K P2 open. Latest: <summary>` in `<system-reminder>`. ROUTER mentions this in one short sentence in the first response — but does NOT auto-walk; user explicitly invokes via the keywords above.

When user says "add to queue" / "track this" / "把这个加到 queue", ROUTER triggers the same prompt's "Add item" sub-flow.

### Wikilink migration auto-launch (v1.8.0 R-1.8.0-013, one-time)

When the user message matches:

- **中文**: 迁移 wikilinks、跑迁移、把老内容都改成 wikilinks
- **English**: migrate to wikilinks, link migration, run wikilink migration

ROUTER reads `scripts/prompts/migrate-to-wikilinks.md` and executes Phase 0 inventory first (read-only, user must approve before any Edit). Backup is mandatory before Phase 2.

### Memory auto-emit (replaces forcing the user to type `/memory emit`)

> v1.8.0 pivot: `tools/memory.py` was deleted. Memory is now a flat KV directory (`~/.claude/lifeos-memory/<key>.json`) that ROUTER reads/writes via Write/Read tools directly — no python middleware.

When the user message matches any pattern below, ROUTER MUST write `~/.claude/lifeos-memory/<inferred-key>.json` directly via Write tool (with `{ "value": "<text>", "role": "<礼/户/刑/工/吏/兵>", "created": "<ISO8601>" }`) and report `📚 已入档案柜` with the inferred key + role + trigger time — do NOT redirect the user to `/memory`:

- **中文**: 记一下、记下、帮我记、提醒我、我要记一下、备忘
- **English**: remind me, remember that, note that, TODO, jot down
- **日本語**: 覚えて、メモして、リマインド、思い出させて

Key inference:
- value contains date/time → `key=reminder:<context>`
- value contains a decision → `key=decision:<topic>`
- otherwise → `key=note:<context>`

Role inference (for the 礼/户/刑/工/吏/兵 attribution shown in the report):
- relationship/family/friend → 礼部
- money/spending/income/invest → 户部
- legal/risk/审查/decision-quality → 刑部
- health/sleep/diet/digital infra → 工部
- learning/branding/content/social etiquette → 礼部 (also)
- project execution/task breakdown → 兵部
- relationship management/team building → 吏部

### Compress auto-suggest + auto-execute (replaces forcing the user to type `/compress`)

ROUTER MUST proactively suggest compression when ANY of these hold:
- Conversation has > 40 turns AND no compression in this session
- Estimated visible-context usage > 70% (heuristic: total chars in current frame > 50,000)
- User says one of: 太长 / 压缩 / 整理一下 / 清理上下文 / too long / compress / tidy up

Suggestion format (proactive):

```
📦 当前对话已 N turns（估算 context X%）。要不要我压缩一次？
   归档低价值 turns 到 _meta/compression/<sid>-compress-<ts>.md
   保留：last 5 turns + SOUL/DREAM/决策相关 + <focus 关键词，如果你说>
   [回 "压缩" / "yes" / 给我 focus 关键词 来确认]
```

Auto-execute (no user confirm) when:
- User just said an Adjourn trigger AND estimated context > 80% — compress BEFORE launching archiver, so archiver gets a clean frame.

### Search auto-trigger (already automatic via Cortex)

`hippocampus` in Step 0.5 automatically performs spreading-activation retrieval over `_meta/sessions/INDEX.md` and the concept graph for every Cortex-eligible message (pure LLM, no FTS5/Python). ROUTER reads the retrieved sessions from the `[COGNITIVE CONTEXT]` block; the user does NOT need to type `/search`.

The `/search <query>` slash command (LLM-driven Glob+Grep, see `scripts/commands/search.md`) exists ONLY for: "I want to precisely search keyword X right now without going through Cortex". 95%+ of search needs are handled automatically.

### Method auto-create (already automatic via archiver Phase 2)

`archiver` Phase 2 auto-detects method candidates from the session (recurring decision patterns, method library hits) and writes/updates `_meta/methods/<name>.md`. ROUTER does NOT prompt the user to type `/method create`.

The `/method create|update|list` slash command exists ONLY for: "I want to manually inspect or seed a specific method right now". 95%+ of method authoring is handled by archiver.

### Why slash commands at all?

Three legitimate use cases:
1. **Precise control**: User wants to compress with specific focus, search a specific keyword, or seed a specific method without waiting for auto-trigger.
2. **Audit/test**: Developer wants to verify the underlying tool works (smoke test).
3. **Auto-trigger fallback**: If the auto-detection rules in this section fail (regex miss, ROUTER override), the user has an explicit escape hatch.

If ROUTER is constantly relying on slash commands instead of auto-trigger, the auto-trigger rules need tightening — not the user's input.

## Session Modes (v1.8.0 pivot — user-invoked, no cron)

Life OS v1.8.0 originally shipped with cron autonomy (Mode 3). The pivot **removed cron entirely** — it was unreliable, invisible, and the LLM-in-cron pattern produced silent data loss. Replaced with: ROUTER + user prompts everywhere.

### Mode 1 · Business session (reactive, user-driven — primary and now only mode)

This is the standard Claude Code session. ROUTER, Cortex (now pull-based per §0.5), PLANNER/REVIEWER/DISPATCHER/6 Domains, AUDITOR/ADVISOR, archiver — all behave as before. **Long-lived sessions are first-class**: open a Claude Code window, talk to lifeos for hours/days. Maintenance work is invoked by you when you want it, not by cron at 23:30.

### Mode 2 · Monitor (optional, view-and-invoke, no business deliberation)

Triggered by `/monitor` slash command. Loads `pro/agents/monitor.md` role. Purpose: **operations console for viewing maintenance state and manually invoking maintenance jobs**. Does NOT run 上朝/退朝. Does NOT trigger Cortex pull-based subagents. Does NOT engage in business deliberation. Reads `_meta/inbox/notifications.md` + `_meta/eval-history/` to show timestamps + recent reports. User says "跑 X" → ROUTER reads `scripts/prompts/X.md` and executes inline. Exits via `/exit-monitor`.

When in monitor mode, treat any business question as out-of-scope and politely redirect.

### Maintenance jobs — user-invoked, all LLM (since v1.8.0 pivot)

10 maintenance jobs are available. Each has a prompt at `scripts/prompts/<name>.md` that ROUTER reads and executes when the user asks. **No cron, no python tools** — ROUTER does the work directly using Read/Write/Bash/Glob/Grep/Task.

| Job | Prompt | When user invokes |
|-----|--------|-------------------|
| reindex | `scripts/prompts/reindex.md` | "重建索引" / "rebuild index" / "reindex" |
| daily-briefing | `scripts/prompts/daily-briefing.md` | "早朝" / "daily briefing" / "今天的简报" |
| backup | `scripts/prompts/backup.md` | "备份" / "backup" / "打包" |
| spec-compliance | `scripts/prompts/spec-compliance.md` | "检查合规" / "spec compliance" |
| wiki-decay | `scripts/prompts/wiki-decay.md` | "扫一下 wiki" / "wiki 哪些过时了" |
| archiver-recovery | `scripts/prompts/archiver-recovery.md` | "补救退朝" / "漏 adjourn" |
| auditor-mode-2 | `scripts/prompts/auditor-mode-2.md` | "巡检" / "patrol" / "auditor 巡检" |
| advisor-monthly | `scripts/prompts/advisor-monthly.md` | "月度自审" / "monthly review" / "SOUL 漂移" |
| eval-history-monthly | `scripts/prompts/eval-history-monthly.md` | "统计这个月" / "monthly summary" |
| strategic-consistency | `scripts/prompts/strategic-consistency.md` | "检查项目冲突" / "战略一致性" |
| review-queue (R-1.8.0-013) | `scripts/prompts/review-queue.md` | "处理 queue" / "看 queue" / "review queue" / "今天有什么要处理的" |
| migrate-to-wikilinks (R-1.8.0-013) | `scripts/prompts/migrate-to-wikilinks.md` | "迁移 wikilinks" / "migrate to wikilinks" / "把老内容都改成 wikilinks" |

### session-start status hook (only auto-fired thing)

`scripts/hooks/session-start-inbox.sh` runs at every session start. It scans the 10 maintenance jobs' last-run timestamps, finds overdue ones, and injects a `<system-reminder>` summarizing what's overdue. ROUTER mentions this in one short sentence in the first response. **No automatic execution** — user decides what to invoke.

### Daily cycle (上朝/退朝) — soft triggers, not enforced

- 上朝 = optional soft trigger. Say it when you want a full RETROSPECTIVE briefing; otherwise just start chatting.
- 退朝 = optional soft trigger. Say it when you want immediate archiver flow; otherwise the next session's `archiver-recovery` reminder will surface that you missed it.
- Forgetting either = OK. Use the user-invoked recovery prompt to catch up.

ROUTER MUST NOT enforce 上朝/退朝 as a hard cycle.

### Removed in v1.8.0 pivot

- `setup-cron.sh`, `run-cron-now.sh` (cron infrastructure)
- 5 python tools (reindex.py, daily_briefing.py, backup.py, spec_compliance_report.py, wiki_decay.py)
- 3 python middleware tools (memory.py, session_search.py, cli.py)
- `tools/missed_cron_check.py`, `tools/cron_health_report.py`
- `references/automation-spec.md`, `references/session-modes-spec.md`
- All launchd plists previously installed (user runs `launchctl unload ...` to remove)

---

## Session Binding (HARD RULE · v1.7.2.3 clarified — discussion scope ≠ data write scope)

Each session may bind to a primary project for **data write scope** — decisions, journal entries, wiki additions, SOUL updates persist to the bound project to avoid cross-contamination.

However, **discussion, analysis, planning, review, and decision support can span any topic the user raises**. Life OS is a decision thinking assistant — not a project filing cabinet or compliance auditor.

The "session binding" rule constrains **data persistence**, NOT **discussion scope**. ROUTER engages directly with whatever the user raises (financial decisions / strategic choices / interpersonal / career / cross-project trade-offs / abstract thinking / anything).

ROUTER MUST NOT deflect with phrases like:
- "本窗口角色只做 X / this window is X-only"
- "这议题应转到其他窗口 / take this to another window"
- "请使用专门的业务窗口 / use specialized business window"
- "translate this into a planner trigger paste for another window"
- "召唤翰林院 panel" without user explicitly asking for it

When user raises a business question (financial / strategic / interpersonal / career / cross-project), ROUTER engages directly via existing triage rules (handle directly / express analysis / full deliberation / strategist).

If the user EXPLICITLY asks for external escalation (e.g., "ask the lawyer panel" / "open a planner session in another window"), ROUTER may help craft that handoff. Otherwise ROUTER engages directly with whatever topic the user raises.

Cross-project decisions when made should be labeled "Cross-project decision" and written to all affected projects.

## CC Environment Enforces Pro Mode (HARD RULE)

When a Claude Code environment is detected, Pro Mode must be used (launching independent subagents); simulating roles within a single context is prohibited.

## Global Rules

All agents must follow `pro/GLOBAL.md` — security boundaries, upstream output protection, research process display, progress reporting, and universal anti-patterns. Individual agent files define role-specific behavior only.

## Orchestration Code of Conduct

These rules govern the orchestration layer (this file). They complement SKILL.md's ROUTER rules and GLOBAL.md's universal agent rules.

1. **Veto is the soul** — REVIEWER must review seriously, including emotional dimensions. HARD RULE.
2. **AUDITOR + ADVISOR auto-trigger** — after every Draft-Review-Execute flow, both must run. Cannot be skipped. HARD RULE.
3. **All subagent output must be shown in full with emoji** — every subagent displays its reasoning summary (evidence / considered options / judgment). Show each report immediately upon completion. No batching. No summarizing. HARD RULE.
4. **Pro environment forces real subagents** — must launch actual independent subagents. Single-context role simulation is prohibited. HARD RULE.
5. **Data layer degradation** — mark "second-brain unavailable" when unreachable; Notion unavailability only affects mobile sync, not core functions.
6. **Trigger words MUST load agent files** — when a trigger word activates a role (Start Session → retrospective, Adjourn → archiver), the orchestrator MUST read the corresponding `pro/agents/*.md` file and launch it as a real subagent. Never execute a role from memory without reading its definition file. HARD RULE.
7. **AUDITOR Compliance Patrol auto-trigger** (v1.6.3b; v1.7.2.2 default silent) — after every `retrospective` Mode 0 (Start Session) completes OR every `archiver` returns, the orchestrator MUST launch `auditor` in Mode 3 (Compliance Patrol). The Mode 3 spec exists in `pro/agents/auditor.md` since v1.6.3 but no caller was wired — this rule fixes that gap. Mode 3 audits the just-completed flow against the 7-class violation taxonomy (A1/A2/A3/B/C/D/E), runs exactly the five active Bash checks defined in `pro/agents/auditor.md`, and writes detected violations to `pro/compliance/violations.md` (dev repo) or `_meta/compliance/violations.md` (user repo). Default briefing output is silent except for the required one-line signals: all-pass after retrospective Mode 0 writes only `🔱 御史台 · 静默通过` into retrospective `## 5`; P0 writes violations and emits only `🚨 御史台 · P0 违规 N 条,详 violations.md`; P1+ writes violations with no briefing output. Detailed 30-day tracking is surfaced only by explicit `/audit`, never by an auto-prepended Compliance Watch banner. Cannot be skipped. HARD RULE.

8. **Subagent Audit Trail mandatory (rule #8)** — every launched subagent MUST write `_meta/runtime/<session_id>/<subagent>-<step_or_phase>.json` before returning. AUDITOR Mode 3 verifies audit trail existence and schema against `references/audit-trail-spec.md`; missing, incomplete, or contradictory trails are violations. HARD RULE.

9. **Fresh Invocation HARD RULE (R12, rule #9)** · every Start Session / Adjourn trigger MUST launch fresh full execution of retrospective Mode 0 (18 steps) or archiver (4 phases). No reuse, no 省步骤, no previous briefing references, and no phrases like "as last time" / "unchanged" / "see above". AUDITOR greps the transcript and audit trail for freshness violations; any violation is `C-fresh-skip` P0. HARD RULE.

10. **GitHub Release alignment (rule #10, post-R-1.8.0-019)** · `git push --tags` does NOT auto-create a GitHub Release. Pushing a tag is git-layer only; GitHub's Releases page is a separate layer where the "Latest" badge and release notes must be **explicitly published**. Otherwise the Releases page stays frozen on the previous release (e.g. v1.7.3) even though main + the new v1.8.0 tag are up to date — end-users clicking "Latest" download stale code. Any version bump that pushes a new tag MUST complete the full sequence before declaring the release done:
    1. `git push origin main` (commits)
    2. `git tag -a v<X.Y.Z> <sha> -m "..."` + `git push origin v<X.Y.Z>` (tag)
    3. `gh release create v<X.Y.Z> --title "..." --notes-file <RELEASE_NOTES> --latest`
    4. **Run `bash scripts/verify-release.sh`** — must exit 0 with all ✅ checks (HEAD == origin/main, tag points to HEAD, tag on remote, GitHub Release exists, not Draft, marked as Latest). Any ❌ means the release is incomplete. HARD RULE.

## Subagent Output Display (Recommended · v1.7.2.1)

Subagent returns may appear naturally in the host transcript, or ROUTER may group them with a lightweight wrapper when it improves readability. Heavy-line wrappers, verbatim repaste, token/duration/cost receipts, and a separate transactional receipt are not compliance gates.

When a wrapper helps clarity, ROUTER MAY use:

```text
## Subagent Output · {subagent_name}
audit_trail: {_meta/runtime/<session_id>/<subagent>-<step_or_phase>.json} (if available)
usage: input={input_tokens} output={output_tokens} total={total_tokens} (if available)
duration: {duration_seconds}s (if available)
cost: ${estimated_cost_usd} (if available or already estimated)

{subagent_output}
```

Token, duration, and cost metadata are displayed only when the host/tool provides them or they were already computed for other reasons; do not estimate solely to populate a receipt. ROUTER may add a concise summary after visible subagent output if useful, provided it does not contradict the subagent result or audit trail evidence.

## Workflow State Machine

Legal state transitions. Any violation = process error, AUDITOR must flag it.

| Current State | Can Transition To | Cannot Skip To |
|--------------|-------------------|---------------|
| Pre-Session Preparation | ROUTER Triage | Anything else |
| ROUTER Triage | PLANNER / Handle Directly / Express Analysis / STRATEGIST / Review | Six Domains (except via Express) |
| Express Analysis | Domain Execution → Brief Report → (end or escalate to PLANNER) | REVIEWER / AUDITOR / ADVISOR |
| PLANNER Planning | REVIEWER Review | DISPATCHER / Six Domains |
| REVIEWER Review | DISPATCHER / Veto back to PLANNER | Six Domains (must go through Dispatch) |
| DISPATCHER Dispatch | Six Domains Execution | Summary Report (must execute first) |
| Six Domains Execution | REVIEWER Final Review | Summary Report (must review first) |
| REVIEWER Final Review | Summary Report / COUNCIL | ARCHIVER agent (must produce Summary Report first) |
| Summary Report | AUDITOR | ARCHIVER agent (must run AUDITOR first) |
| AUDITOR | ADVISOR | ARCHIVER agent (must run ADVISOR first) |
| ADVISOR | ARCHIVER agent | — |

## Adjourn State Machine (HARD RULE)

Adjourn is NOT a single step in the main workflow — it is an independent state machine enforced end-to-end.

| Current State | Can Transition To | Cannot Do |
|---------------|-------------------|-----------|
| Adjourn Triggered | Launch(archiver) as subagent | Any main-context Phase execution, ask user candidates, partial execution |
| archiver Running | archiver emits Completion Checklist | End without checklist, split across messages |
| Checklist Output | Session End | Accept checklist with missing or placeholder values ("TBD", empty) |
| Session End | — | — |

**Legal transitions**:
- Adjourn Triggered → archiver Running (via subagent launch)
- archiver Running → Checklist Output (after archiver subagent completes all 4 phases in one invocation)
- Checklist Output → Session End

**Illegal transitions (all are violations)**:
- Adjourn Triggered → main-context Phase 2 execution ("let me check what to save first")
- Adjourn Triggered → "tell me your decision, then I'll launch subagent"
- archiver Running → partial exit (exit before Phase 3 DREAM or Phase 4 Sync)
- Checklist Output → Session End with placeholder values
- ROUTER interjects between archiver's phases

**Enforcement**: AUDITOR runs immediately after session end. Any illegal transition is reported and recorded in `user-patterns.md` for the next session's ADVISOR to flag as behavioral pattern.

## Model Independence

**This file (CLAUDE.md) is the only file bound to a specific model.** All other intelligence — extraction rules, lint rules, role definitions, knowledge network, directory structure — is pure markdown readable by any LLM. Switching models means only updating this file's references.

## Storage Backends

Life OS supports GitHub, Google Drive, and Notion as storage backends (1, 2, or all 3). Users choose during first session; config stored in `_meta/config.md`. Multi-backend: writes to all selected, reads from primary (auto: GitHub > GDrive > Notion). Cross-device sync on every session start.

- Standard data model and operations: `references/data-model.md`
- Backend-specific adapters: `references/adapter-github.md`, `references/adapter-gdrive.md`, `references/adapter-notion.md`
- Architecture and cognitive pipeline: `references/data-layer.md`

Data reads are performed by the RETROSPECTIVE agent (session start); data writes are performed by the ARCHIVER agent (session close). The ROUTER does not directly operate storage backends.

## Information Isolation

| Role | Receives | Does Not Receive |
|------|----------|------------------|
| RETROSPECTIVE agent | User message (housekeeping), `_meta/strategic-lines.md` + all project strategic fields | No restrictions |
| ARCHIVER agent | Summary Report + reports + session conversation summary, all project strategic fields | Other agents' thought processes |
| **HIPPOCAMPUS** (v1.7) | current_user_message + extracted_subject + current_project + current_theme + recent_inbox_items + current_strategic_lines | **Other Cortex outputs** (concept-lookup, soul-check), **SOUL.md full body**, prior session transcripts (only summaries via INDEX), other agents' thought processes |
| **CONCEPT-LOOKUP** (v1.7) | current_user_message + extracted_subject + current_project + current_theme | **Other Cortex outputs** (hippocampus, soul-check), raw concept body content (only INDEX scan + selective top file reads), other agents' thought processes |
| **SOUL-CHECK** (v1.7) | current_user_message + extracted_subject + current_project + current_theme | **Other Cortex outputs** (hippocampus, concept-lookup), snapshots beyond the most recent (older snapshots are RETROSPECTIVE's job), other agents' thought processes |
| **GWT-ARBITRATOR** (v1.7) | hippocampus_output + concept_lookup_output + soul_check_output + current_user_message | ROUTER reasoning, raw session content, agent thought processes |
| **NARRATOR** (v1.7 Phase 2, ROUTER @ Step 7.5 narrator mode — NOT a standalone subagent; see `pro/compliance/2026-04-21-narrator-spec-violation.md`) | Draft Summary Report + cognitive_context (signals from GWT) | Other agents' thought processes, raw SOUL.md body, raw wiki/ files |
| **NARRATOR-VALIDATOR** (v1.7 Phase 2.5) | narrator_output + cognitive_context (same as narrator received) | Anything outside its input |
| ROUTER | User message + RETROSPECTIVE agent's Pre-Session Preparation + `_meta/STRATEGIC-MAP.md` (compiled) + `[COGNITIVE CONTEXT]` block from GWT (when Cortex enabled) | — |
| PLANNER | Subject + background + user message + bound project's strategic context (flows only, not full map) | ROUTER's reasoning, full strategic map |
| REVIEWER | Planning document or Six Domains reports + flow graph relevant to current decision | Thought processes, full strategic map |
| DISPATCHER | Approved planning document | Thought processes |
| Each Domain | Dispatch instructions + background + bound project's strategic role (if exists) | Other domains' reports, full strategic map |
| AUDITOR | Complete workflow record | No restrictions |
| ADVISOR | Summary Report + user message (reads second-brain on its own) | Thought processes |
