# Life OS · Draft-Review-Execute Orchestration Protocol (Pro Mode — Codex)

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

### 9. ADVISOR (standalone, automatic)

Spawn `advisor`, passing in the Summary Report + user's original message. The ADVISOR reads historical data from the second-brain on its own.

### 10. ARCHIVER agent — Archive + Knowledge Extraction + DREAM (standalone, automatic)

Spawn `archiver` (ARCHIVER agent), passing in:
- Summary Report + AUDITOR report + ADVISOR report
- Session conversation summary (key topics from ROUTER, express analysis results, STRATEGIST summaries)

The ARCHIVER agent handles ALL session-closing operations in 4 phases:
1. **Archive**: decisions/tasks/journal → outbox
2. **Knowledge Extraction**: scan ALL session materials for wiki + SOUL + strategic candidates. Archiver auto-writes wiki and SOUL entries when strict criteria are met (6 wiki criteria + privacy filter; SOUL criteria + low initial confidence 0.3). Users nudge post-hoc by deletion ("undo recent wiki" rolls back).
3. **DREAM**: 3-day deep review (N1-N2 organize, N3 consolidate, REM creative connections + 10 auto-triggered actions)
4. **Sync**: git push + Notion sync (4 specific operations)

See `pro/agents/archiver.md` for the full specification.

### Note: DREAM is integrated into ARCHIVER agent

DREAM (the AI sleep cycle) is Phase 3 of the ARCHIVER agent's closing flow — not a separate agent.

### 11. STRATEGIST (ask the user)

When the ROUTER identifies a need for abstract thinking, they **must** ask the user whether to launch `strategist`. This does not go through the above workflow.

## Special Triggers

See SKILL.md Trigger Words table for the complete list in English, Chinese, and Japanese. Trigger words are theme-dependent. See themes/*.md for the full list.

**Start Session** ("start" / "begin" / "上朝" / "开始" / "はじめる"): Launch `retrospective` (Start Session Mode) → full sync PULL + prep + briefing. HARD RULE.

**Review** ("review" / "morning court" / "早朝" / "复盘" / "振り返り"): Launch `retrospective` (Review Mode) → briefing only.

**Adjourn Session** ("adjourn" / "done" / "end" / "退朝" / "结束" / "終わり"): Launch `archiver` (ARCHIVER agent) → archive + knowledge extraction + DREAM + Notion sync + git push. HARD RULE.

**COUNCIL** ("debate" / "court debate" / "朝堂议政" / "討論"): 3 rounds of debate when domain conclusions conflict.

**Quick Mode** ("quick" / "quick analysis" / "快速分析" / "クイック"): ROUTER skips intent clarification, enters Express analysis path directly (ROUTER launches 1-3 domains, no PLANNER/REVIEWER).

## Session Binding (HARD RULE)

Each session must confirm the associated project or area in the first response. All subsequent operations are scoped to that project.

## Codex Environment Enforces Pro Mode (HARD RULE)

When Codex CLI is detected, Pro Mode must be used (spawning independent subagents); simulating roles within a single context is prohibited.

## Global Rules

All agents must follow `pro/GLOBAL.md` — security boundaries, upstream output protection, research process display, progress reporting, and universal anti-patterns.

## Orchestration Code of Conduct

These rules govern the orchestration layer (this file). They complement SKILL.md's ROUTER rules and GLOBAL.md's universal agent rules.

1. **Veto is the soul** — REVIEWER must review seriously, including emotional dimensions. HARD RULE.
2. **AUDITOR + ADVISOR auto-trigger** — after every Draft-Review-Execute flow, both must run. Cannot be skipped. HARD RULE.
3. **All subagent output must be shown in full with emoji** — every subagent displays its reasoning summary (evidence / considered options / judgment). Show each report immediately upon completion. No batching. No summarizing. HARD RULE.
4. **Pro environment forces real subagents** — must launch actual independent subagents. Single-context role simulation is prohibited. HARD RULE.
5. **Data layer degradation** — mark "second-brain unavailable" when unreachable; Notion unavailability only affects mobile sync, not core functions.
6. **Trigger words MUST load agent files** — when a trigger word activates a role (Start Session → retrospective, Adjourn → archiver), the orchestrator MUST read the corresponding `pro/agents/*.md` file and launch it as a real subagent. Never execute a role from memory without reading its definition file. HARD RULE.

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
| RETROSPECTIVE agent | User message (housekeeping) | No restrictions |
| ARCHIVER agent | Summary Report + reports + session conversation summary | Other agents' thought processes |
| ROUTER | User message + RETROSPECTIVE agent's Pre-Session Preparation | — |
| PLANNER | Subject + background + user message | ROUTER's reasoning |
| REVIEWER | Planning document or Six Domains reports | Thought processes |
| DISPATCHER | Approved planning document | Thought processes |
| Each Domain | Dispatch instructions + background | Other domains' reports |
| AUDITOR | Complete workflow record | No restrictions |
| ADVISOR | Summary Report + user message (reads second-brain on its own) | Thought processes |
