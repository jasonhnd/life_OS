# Life OS · Draft-Review-Execute Orchestration Protocol (Pro Mode — Codex)

> **Codex CLI host note (v1.7)**: The Shell Hook layer (Layer 3) described in `references/hooks-spec.md §2` is Claude-Code-only in v1.7. Codex CLI users get Layer 1 (documentation HARD RULE) + Layer 2 (subagent isolation) enforcement; no runtime hook backstop. When Codex publishes a compatible hook surface, the same 5 scripts under `scripts/hooks/` can be registered. Until then, treat all HARD RULE in this file as prompt-level enforcement.

All agents read their display names from the active theme file (themes/*.md). This orchestration uses functional IDs only.

This file is the OpenAI Codex CLI equivalent of CLAUDE.md / GEMINI.md. It defines how to orchestrate the 16 subagents on the Codex platform, following the AGENTS.md open standard.

All roles use the platform's strongest available model. See `references/data-layer.md` for data layer architecture details.

## Platform Mapping

When reading agent files from `pro/agents/*.md`, apply these mappings:

| Agent Frontmatter Field | Original (Claude) | Codex Equivalent |
|------------------------|-------------------|------------------|
| `model: opus` | Claude's strongest model | Codex's strongest available model (auto-select) |
| Tool: `Read` | Read file | `read_file` |
| Tool: `Write` | Write file | `write_file` |
| Tool: `Edit` | Edit file | `edit_file` |
| Tool: `Grep` | Search content | `grep` |
| Tool: `Glob` | Find files by pattern | `glob` |
| Tool: `Bash` | Execute shell command | `shell` |
| Tool: `WebSearch` | Web search | `web_search` |
| Tool: `WebFetch` | Fetch URL | `web_fetch` |
| Tool: `Agent` | Spawn subagent | Spawn subagent (see below) |

## Subagent Invocation

On Codex CLI, subagents are spawned as independent parallel agents. Each agent file in `pro/agents/` is a self-contained subagent definition.

**Invocation pattern**: Spawn a new agent with the agent file's content as its system prompt, passing only the specified input data. The agent operates independently and returns its output. Codex supports parallel spawning — use it for Six Domains execution.

**Information isolation**: Each subagent receives ONLY the data specified in the workflow below. Do not pass the parent agent's full context or other agents' outputs unless explicitly stated.

## Architecture

```
Build & Test: N/A (this is a prompt-based system, not a compiled project)
Security: See pro/GLOBAL.md — 4 inviolable security boundaries
Conventions: Modern, direct language. No archaic tone. Honest scores.
```

## Theme System

The theme file is loaded at session start. All display names (for agents, phases, domains, reports, and trigger words) come from the active theme. Users can switch themes by changing the active theme in `_meta/config.md`. Functional IDs in this file remain stable across all themes.

## Complete Workflow

### 0. Pre-Session Preparation (ROUTER + RETROSPECTIVE agent in parallel)

When the user sends the first message, spawn simultaneously:
- `router` (ROUTER): Prepare to respond to the user
- `retrospective` (RETROSPECTIVE agent · Housekeeping Mode): Prepare context in the background — read second-brain (inbox/projects/areas/decisions), read user-patterns.md, check Notion inbox, version check, platform detection

After the RETROSPECTIVE agent finishes, hand the "Pre-Session Preparation" results to the ROUTER. The ROUTER gives the user a **complete** first response that **must include the Pre-Session Preparation information**.

### 0.5. Pre-Router Cognitive Layer (Cortex Phase 1, v1.7) — OPTIONAL

When the user sends a non-Start-Session message AND `_meta/sessions/INDEX.md` exists in the bound second-brain, the orchestrator MAY spawn the Pre-Router Cognitive Layer to produce annotated input for ROUTER. Activation is per-session (controlled by `_meta/config.md` `cortex_enabled: true|false`); default is **opt-out** for v1.7 (off until explicitly enabled).

**3 parallel subagents** (each independent, information-isolated from each other):

1. `hippocampus` — cross-session memory retrieval via 3-wave spreading activation over `_meta/sessions/INDEX.md` and the concept graph. Reads only its dedicated inputs. See `pro/agents/hippocampus.md`.
2. `concept-lookup` (v1.7 Phase 1.5) — direct concept-graph match via `_meta/concepts/INDEX.md`, returns top 5-10 concepts directly mentioned/implied by current message. See `pro/agents/concept-lookup.md`.
3. `soul-check` (TBD — reuses RETROSPECTIVE's SOUL Health Report) — relevant SOUL dimensions. Until standalone implementation, orchestrator passes the SOUL Health block from RETROSPECTIVE's housekeeping output.

After GWT arbitrator returns `[COGNITIVE CONTEXT]`, the orchestrator MAY also trigger **ROUTER Step 7.5 (narrator mode)** — a ROUTER-internal narrator composition step (NOT a standalone subagent; see `pro/compliance/2026-04-21-narrator-spec-violation.md`) that runs AFTER REVIEWER Final Review (between step 6 and step 7) to wrap Summary Report substantive claims with `signal_id` citations from the cognitive context. Narrator-mode failure is non-blocking — falls back to v1.6.3 unwrapped Summary Report. The composition template lives at `pro/agents/narrator.md` (ROUTER-internal template, NOT spawnable via Task).

When ROUTER Step 7.5 (narrator mode) runs, the orchestrator chains the `narrator-validator` subagent (a real standalone Sonnet subagent — cheaper than Opus) to audit citation discipline. Validator failures trigger up to 2 rewrite cycles inside ROUTER Step 7.5; after 2 failed rewrites, fall back to v1.6.3 unwrapped report and log to `_meta/eval-history/narrator-{date}.md`. See `pro/agents/narrator-validator.md`.

After all 3 return (with 5s soft timeout, 15s hard timeout per individual subagent), spawn `gwt-arbitrator` with the consolidated outputs. See `pro/agents/gwt-arbitrator.md`.

**GWT arbitrator output** is a `[COGNITIVE CONTEXT]` Markdown block. Orchestrator **prepends** it to the user message before ROUTER sees it:

```
[COGNITIVE CONTEXT — reference only, not user input]
{annotations from GWT}
[END COGNITIVE CONTEXT]

{original user message}
```

**ROUTER behaviour**: ROUTER parses the `[COGNITIVE CONTEXT]` ... `[END COGNITIVE CONTEXT]` delimiters to separate advisory content from real user input. The cognitive context is **advisory, not authoritative** — ROUTER may discard it if the user explicitly says "ignore history" or similar.

**Failure modes** (all degrade to v1.6.3 behaviour):
- INDEX missing or empty → skip Step 0.5 entirely, ROUTER receives raw message
- Any subagent times out → its slot becomes `null`, GWT proceeds with available signals
- GWT timeout → orchestrator emits empty `[COGNITIVE CONTEXT]` block, ROUTER receives original message
- `cortex_enabled: false` in config → skip Step 0.5

**Cost**: ~$0.05-0.10 per invocation. Worth it on substantive decisions; wasteful on trivial chat. The opt-out default reflects this — users enable Cortex when they have ≥30 sessions of accumulated history.

### 1. ROUTER Triage

The ROUTER takes the context prepared by the RETROSPECTIVE agent and assesses the user's needs:

- Handle directly -> Return to user, workflow ends
- Express analysis -> After brief clarification, launch 1-3 domain agents directly (skip steps 2-4, 6-9). Continue to step 1E.
- Full deliberation -> After intent clarification (2-3 rounds, **HARD RULE: cannot be skipped**), extract Subject + background summary, continue to step 2
- STRATEGIST -> Ask the user whether to launch `strategist`, does not proceed through the subsequent workflow
- Review -> Launch `retrospective` (Review Mode)

### 1E. Express Analysis Path

The ROUTER directly launches 1-3 relevant domain agents, passing the question + background. Each domain executes with full research/consideration/judgment process. The ROUTER presents results as a **brief report** (not a Summary Report — no composite scores, no formal audit log).

After presenting: "This is an express analysis. Want a full deliberation instead?"
- User says yes → escalate to step 2 (full deliberation with PLANNER planning)
- User says no or continues → workflow ends (or proceed to wrap-up if session ends)

Express path does NOT trigger: PLANNER, REVIEWER, DISPATCHER, AUDITOR, ADVISOR. It is for analysis/research/planning that does not involve a decision.

### 2. PLANNER Planning (standalone)

Spawn `planner`, passing in the Subject + background summary + user's original message. **Do not pass** the ROUTER's triage reasoning.

### 3. REVIEWER Deliberation (standalone)

Spawn `reviewer`, passing in the full PLANNER planning document. **Do not pass** the PLANNER's thought process.

- Approved -> Continue to step 4
- Conditionally Approved -> Append conditions to the planning document, continue to step 4
- Veto -> Veto correction loop

**Veto Correction Loop**: Pass the veto reasons and correction direction back to the PLANNER; the PLANNER revises and resubmits to the REVIEWER for review. Maximum 2 loops; the 3rd time must result in Approved or Conditionally Approved.

### 4. DISPATCHER Dispatch (standalone)

Spawn `dispatcher`, passing in the approved planning document. **Do not pass** the PLANNER/REVIEWER's thought processes.

### 5. Six Domains Execution (parallel, displayed one by one)

Spawn relevant domains in parallel according to the dispatch order. Each domain receives: its own instructions + background materials + quality criteria. **Do not pass** other domains' reports.

**One-by-one reporting (HARD RULE)**: Each time a domain's report is received, it **must be immediately displayed in full to the user** (including the research process). Do not wait for all to finish before summarizing. Do not compress into summaries. Do not omit the research process.

**File write conflict rule**: When the Six Domains run in parallel, each domain may only modify files under its own responsibility. Domains that need to modify the same file are arranged in sequence by the DISPATCHER.

If a domain's report clearly lacks substantive content, it may be asked to redo it once.

### 6. REVIEWER Final Review (standalone)

Spawn `reviewer` again, passing in all domain reports. **Do not pass** each domain's internal thought processes.

**COUNCIL trigger**: If the REVIEWER detects score diff >= 3 between domains, or one domain says "do it" while another says "don't" → spawn `council` (COUNCIL) for 3 rounds of structured debate. After the debate, the PLANNER compiles consensus and disagreements, and the ROUTER produces the Summary Report incorporating the debate outcome.

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

Spawn `auditor` in Decision Review mode, passing in the complete workflow record.

Note: The AUDITOR also has a Patrol Inspection mode triggered by the RETROSPECTIVE agent during housekeeping. See `references/data-layer.md` for details.

### 9. ADVISOR (standalone, automatic)

Spawn `advisor`, passing in the Summary Report + user's original message. The ADVISOR reads historical data from the second-brain on its own.

### 10. ARCHIVER agent — Archive + Knowledge Extraction + DREAM (standalone) — HARD RULE

**Mandatory launch template** (ROUTER output, in the active theme's language):
```
📝 [theme: archiver display name] — Starting archive flow (4 phases)...
[Spawn archiver subagent here]
```

ROUTER output must match this template. Any deviation is a process violation, including:
- "Let me first check what candidates to save" — NO, archiver does that internally
- "Tell me your decision, then I'll launch DREAM/sync" — NO, split flow is forbidden
- Listing wiki/SOUL/strategic candidates in the main context — NO, that's Phase 2's job
- Performing any file move, git commit, or Notion write in the main context — NO

Spawn `archiver` as subagent, passing in:
- Summary Report + AUDITOR report + ADVISOR report
- **Session conversation summary**: key topics discussed by ROUTER (including direct-handle conversations, express analysis results, STRATEGIST summaries — everything NOT captured in the Summary Report)

The ARCHIVER subagent handles ALL session-closing operations in 4 phases end-to-end in a single invocation:
1. **Archive**: decisions/tasks/journal → outbox
2. **Knowledge Extraction**: scan ALL session materials for wiki + SOUL + strategic candidates. Archiver auto-writes wiki and SOUL entries when strict criteria are met (6 wiki criteria + privacy filter; SOUL criteria + low initial confidence). Users nudge post-hoc by deletion ("undo recent wiki" rolls back).
3. **DREAM**: 3-day deep review (N1-N2 organize, N3 consolidate, REM creative connections)
4. **Sync**: git push + Notion sync (4 specific operations)

ROUTER does not interject between phases. The subagent emits the Completion Checklist when done. See `pro/agents/archiver.md` for the full specification.

### 10a. Notion Sync (orchestrator, after archiver returns) — HARD RULE

The archiver subagent cannot access Notion MCP tools (they are environment-specific). After the archiver returns with its Completion Checklist, the **orchestrator (main context)** MUST execute Notion sync using the Notion MCP tools available in the session:

```
a. 🧠 Current Status page: overwrite with latest STATUS.md content
b. 📋 Todo Board: sync tasks from this session (new → create, completed → check off)
c. 📝 Working Memory: write session summary (subject, key conclusions, action items)
d. 📬 Inbox: mark processed items as "Synced"
e. If Notion MCP unavailable → report: "⚠️ Notion sync failed — mobile will not see updates"
f. If a specific write fails → report which one, continue with others
```

After Notion sync completes, output the Notion portion of the checklist:
```
🔄 Notion sync:
- 🧠 Status: [updated / failed: {reason}]
- 📋 Todo: [synced {N} items / failed: {reason}]
- 📝 Working Memory: [written / failed: {reason}]
- 📬 Inbox: [marked synced / no items / failed: {reason}]
```

Do NOT skip Notion sync silently. Do NOT say "Notion MCP not connected" without actually attempting to call the tools.

### 11. STRATEGIST — Hall of Human Wisdom (ask the user)

When the ROUTER identifies abstract thinking needs, they **must** ask: "Would you like to activate the STRATEGIST to dialogue with history's greatest thinkers?"

The STRATEGIST does not go through the Draft-Review-Execute workflow. It operates independently:

1. Spawn `strategist` (moderator agent)
2. STRATEGIST asks the user's purpose
3. STRATEGIST displays the 18-domain thinker index and recommends figures + mode
4. User confirms → STRATEGIST spawns each selected thinker as an **independent subagent**
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

**Start Session** ("start" / "begin" / "上朝" / "开始" / "はじめる" / "開始" / "朝廷開始"): Launch `retrospective` (Start Session Mode) → full sync PULL + prep + briefing. HARD RULE.

**Review** ("review" / "morning court" / "早朝" / "复盘" / "振り返り" / "レビュー"): Launch `retrospective` (Review Mode) → briefing only.

**Adjourn Session** ("adjourn" / "done" / "end" / "退朝" / "结束" / "終わり" / "お疲れ"): Launch `archiver` (ARCHIVER agent) → archive + knowledge extraction + DREAM + Notion sync + git push. HARD RULE.

**COUNCIL** ("debate" / "court debate" / "朝堂议政" / "討論"): 3 rounds of debate when domain conclusions conflict.

**Quick Mode** ("quick" / "quick analysis" / "快速分析" / "クイック"): ROUTER skips intent clarification, enters Express analysis path directly (ROUTER launches 1-3 domains, no PLANNER/REVIEWER).

**/save Command**: When working in any project repo, user says `/save` → write files to second-brain → git commit + push → sync backends → return to project directory.

## Session Binding (HARD RULE)

Each session must confirm the associated project or area in the first response. All subsequent operations are scoped to that project. Cross-project decisions must be explicitly labeled "Cross-project decision".

## Codex Environment Enforces Pro Mode (HARD RULE)

When Codex CLI is detected, Pro Mode must be used (spawning independent subagents); simulating roles within a single context is prohibited.

## Global Rules

All agents must follow `pro/GLOBAL.md` — security boundaries, upstream output protection, research process display, progress reporting, and universal anti-patterns.

## Orchestration Code of Conduct

These rules govern the orchestration layer (this file). They complement SKILL.md's ROUTER rules and GLOBAL.md's universal agent rules.

1. **Veto is the soul** — REVIEWER must review seriously, including emotional dimensions. HARD RULE.
2. **AUDITOR + ADVISOR auto-trigger** — after every Draft-Review-Execute flow, both must run. Cannot be skipped. HARD RULE.
3. **All subagent output must be shown in full with emoji** — every subagent displays its reasoning summary (evidence / considered options / judgment). Show each report immediately upon completion. No batching. No summarizing. HARD RULE.
4. **Pro environment forces real subagents** — must spawn actual independent subagents. Single-context role simulation is prohibited. HARD RULE.
5. **Data layer degradation** — mark "second-brain unavailable" when unreachable; Notion unavailability only affects mobile sync, not core functions.
6. **Trigger words MUST load agent files** — when a trigger word activates a role (Start Session → retrospective, Adjourn → archiver), the orchestrator MUST read the corresponding `pro/agents/*.md` file and spawn it as a real subagent. Never execute a role from memory without reading its definition file. HARD RULE.
7. **AUDITOR Compliance Patrol auto-trigger** (v1.6.3b) — after every `retrospective` Mode 0 (Start Session) completes OR every `archiver` returns, the orchestrator MUST spawn `auditor` in Mode 3 (Compliance Patrol). Mode 3 audits the just-completed flow against the 7-class violation taxonomy (A1/A2/A3/B/C/D/E) and writes detected violations to `pro/compliance/violations.md` (dev repo) or `_meta/compliance/violations.md` (user repo). All-pass output: `🔱 [theme: auditor] · ✅ Compliance Patrol passed`. Cannot be skipped. HARD RULE.

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
| Adjourn Triggered | Spawn(archiver) as subagent | Any main-context Phase execution, ask user candidates, partial execution |
| archiver Running | archiver emits Completion Checklist | End without checklist, split across messages |
| Checklist Output | Session End | Accept checklist with missing or placeholder values ("TBD", empty) |
| Session End | — | — |

**Legal transitions**:
- Adjourn Triggered → archiver Running (via subagent spawn)
- archiver Running → Checklist Output (after archiver subagent completes all 4 phases in one invocation)
- Checklist Output → Session End

**Illegal transitions (all are violations)**:
- Adjourn Triggered → main-context Phase 2 execution ("let me check what to save first")
- Adjourn Triggered → "tell me your decision, then I'll spawn subagent"
- archiver Running → partial exit (exit before Phase 3 DREAM or Phase 4 Sync)
- Checklist Output → Session End with placeholder values
- ROUTER interjects between archiver's phases

**Enforcement**: AUDITOR runs immediately after session end. Any illegal transition is reported and recorded in `user-patterns.md` for the next session's ADVISOR to flag as behavioral pattern.

## Model Independence

**This file (AGENTS.md) is the Codex-specific orchestration file.** All other intelligence is pure markdown shared across Claude, Gemini, and Codex platforms.

## Storage Backends

Life OS supports GitHub, Google Drive, and Notion as storage backends (1, 2, or all 3). Config in `_meta/config.md`. Multi-backend: writes to all, reads from primary (GitHub > GDrive > Notion).

- Data model: `references/data-model.md`
- Adapters: `references/adapter-github.md`, `references/adapter-gdrive.md`, `references/adapter-notion.md`
- Architecture: `references/data-layer.md`

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
