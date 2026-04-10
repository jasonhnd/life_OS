# Life OS · Three Departments and Six Ministries Orchestration Protocol (Pro Mode — Codex)

This file is the OpenAI Codex CLI equivalent of CLAUDE.md / GEMINI.md. It defines how to orchestrate the 14 subagents on the Codex platform, following the AGENTS.md open standard.

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

**Invocation pattern**: Spawn a new agent with the agent file's content as its system prompt, passing only the specified input data. The agent operates independently and returns its output. Codex supports parallel spawning — use it for Six Ministries execution.

**Information isolation**: Each subagent receives ONLY the data specified in the workflow below. Do not pass the parent agent's full context or other agents' outputs unless explicitly stated.

## Architecture

```
Build & Test: N/A (this is a prompt-based system, not a compiled project)
Security: See pro/GLOBAL.md — 4 inviolable security boundaries
Conventions: Modern, direct language. No archaic tone. Honest scores.
```

## Complete Workflow

### 0. Pre-Court Preparation (Prime Minister + Morning Court Official in parallel)

When the user sends the first message, spawn simultaneously:
- `chengxiang` (Prime Minister): Prepare to respond to the user
- `zaochao` (Morning Court Official · Housekeeping Mode): Prepare context in the background — read second-brain (inbox/projects/areas/decisions), read user-patterns.md, check Notion inbox, version check, platform detection

After the Morning Court Official finishes, hand the "Pre-Court Preparation" results to the Prime Minister. The Prime Minister gives the user a **complete** first response that **must include the Pre-Court Preparation information**.

### 1. Prime Minister Triage

The Prime Minister takes the context prepared by the Morning Court Official and assesses the user's needs:

- Handle directly -> Return to user, workflow ends
- Escalate -> After intent clarification (2-3 rounds, **HARD RULE: cannot be skipped**), extract Subject + background summary, continue to step 2
- Hanlin Academy -> Ask the user whether to launch `hanlin`, does not proceed through the subsequent workflow
- Review -> Launch `zaochao` (Review Mode)

### 2. Secretariat Planning (standalone)

Spawn `zhongshu`, passing in the Subject + background summary + user's original message. **Do not pass** the Prime Minister's triage reasoning.

### 3. Chancellery Deliberation (standalone)

Spawn `menxia`, passing in the full Secretariat planning document. **Do not pass** the Secretariat's thought process.

- ✅ Approved -> Continue to step 4
- ⚠️ Conditionally Approved -> Append conditions to the planning document, continue to step 4
- 🚫 Veto -> Veto correction loop

**Veto Correction Loop**: Pass the veto reasons and correction direction back to the Secretariat; the Secretariat revises and resubmits to the Chancellery for review. Maximum 2 loops; the 3rd time must result in Approved or Conditionally Approved.

### 4. Department of State Affairs Dispatch (standalone)

Spawn `shangshu`, passing in the approved planning document. **Do not pass** the Secretariat/Chancellery's thought processes.

### 5. Six Ministries Execution (parallel, displayed one by one)

Spawn relevant ministries in parallel according to the dispatch order. Each ministry receives: its own instructions + background materials + quality criteria. **Do not pass** other ministries' reports.

**One-by-one reporting (HARD RULE)**: Each time a ministry's report is received, it **must be immediately displayed in full to the user** (including the research process 🔎/💭/🎯). Do not wait for all to finish before summarizing. Do not compress into summaries. Do not omit the research process.

**File write conflict rule**: When the Six Ministries run in parallel, each ministry may only modify files under its own responsibility. Ministries that need to modify the same file are arranged in sequence by the Department of State Affairs.

If a ministry's report clearly lacks substantive content, it may be asked to redo it once.

### 6. Chancellery Final Review (standalone)

Spawn `menxia` again, passing in all ministry reports. **Do not pass** each ministry's internal thought processes.

### 7. Memorial (Prime Minister Summary)

```
📋 Memorial: [Subject]

Overall Rating: [X]/10 — [One-sentence conclusion]

🔴 Must Address: [Consolidated 🔴 findings from all ministries]
🟡 Needs Attention: [Consolidated 🟡 findings from all ministries]
🟢 Room for Improvement: [Consolidated 🟢 findings from all ministries]

Ministry Ratings:
| Ministry | Dimension | Score | One-liner |
|----------|-----------|-------|-----------|

Action Items:
1. [Specific action] — Deadline — Responsible ministry

Audit Log: [Brief record of each stage]

📊 Operations Report:
- Total Time: [From user's message to memorial completion]
- Model: [Current model in use]
- Agent Calls: [N total]
- Vetoes: [X times]
- Political Affairs Hall: [Triggered / Not triggered]
```

### 8. Censorate — Decision Review (standalone, automatic)

Spawn `yushitai` in Decision Review mode, passing in the complete workflow record.

### 9. Remonstrator (standalone, automatic)

Spawn `jianguan`, passing in the memorial + user's original message. The Remonstrator reads historical data from the second-brain on its own.

### 10. Wrap-up Archival (Morning Court Official · Wrap-up Mode)

Spawn `zaochao` (Wrap-up Mode), passing in the memorial + Censorate report + Remonstrator report. The Morning Court Official is responsible for:
1. Writing to second-brain: decisions → `projects/{p}/decisions/` or `_meta/decisions/`, tasks → `projects/{p}/tasks/`, reports → `_meta/journal/`
2. Updating `_meta/STATUS.md` (global status snapshot)
3. Updating user-patterns.md (if the Remonstrator has pattern update suggestions)
4. git add + commit + push
5. Syncing Notion (🧠 Current Status from STATUS.md + 📝 working memory + 📋 todo board)
6. If the second-brain is unreachable, note "⚠️ second-brain unavailable, this session's output was not archived"

### 11. Hanlin Academy (ask the user)

When the Prime Minister identifies a need for abstract thinking, they **must** ask the user whether to launch `hanlin`. This does not go through the above workflow.

## Special Triggers

See SKILL.md Trigger Words table for the complete list in English, Chinese, and Japanese.

**Start Court** ("start" / "begin" / "上朝" / "开始" / "はじめる"): Launch `zaochao` (Start Court Mode) → full sync PULL + prep + briefing. HARD RULE.

**Review** ("review" / "morning court" / "早朝" / "复盘" / "振り返り"): Launch `zaochao` (Review Mode) → briefing only.

**Adjourn Court** ("adjourn" / "done" / "end" / "退朝" / "结束" / "終わり"): Launch `zaochao` (Adjourn Court Mode) → archive + full sync PUSH. HARD RULE.

**Political Affairs Hall** ("debate" / "court debate" / "朝堂议政" / "討論"): 3 rounds of debate when ministry conclusions conflict.

**Quick Mode** ("quick" / "quick analysis" / "快速分析" / "クイック"): Skip Prime Minister, go to Secretariat directly.

## Session Binding (HARD RULE)

Each session must confirm the associated project or area in the first response. All subsequent operations are scoped to that project.

## Codex Environment Enforces Pro Mode (HARD RULE)

When Codex CLI is detected, Pro Mode must be used (spawning independent subagents); simulating roles within a single context is prohibited.

## Global Rules

All agents must follow `pro/GLOBAL.md` — security boundaries, upstream output protection, research process display, progress reporting, and universal anti-patterns.

## Workflow State Machine

Legal state transitions. Any violation = process error, Censorate must flag it.

| Current State | Can Transition To | Cannot Skip To |
|--------------|-------------------|---------------|
| Pre-Court Preparation | Prime Minister Triage | Anything else |
| Prime Minister Triage | Secretariat / Handle Directly / Hanlin / Morning Court | Six Ministries |
| Secretariat Planning | Chancellery Review | Dept. of State Affairs / Six Ministries |
| Chancellery Review | Dept. of State Affairs / Veto back to Secretariat | Six Ministries |
| Dept. of State Affairs Dispatch | Six Ministries Execution | Memorial |
| Six Ministries Execution | Chancellery Final Review | Memorial |
| Chancellery Final Review | Memorial / Political Affairs Hall | Wrap-up |
| Memorial | Censorate | Wrap-up |
| Censorate | Remonstrator | Wrap-up |
| Remonstrator | Wrap-up Archival | — |

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
| Morning Court Official | User message (housekeeping) / Memorial + reports (wrap-up) | No restrictions |
| Prime Minister | User message + Morning Court Official's Pre-Court Preparation | — |
| Secretariat | Subject + background + user message | Prime Minister's reasoning |
| Chancellery | Planning document or Six Ministries reports | Thought processes |
| Department of State Affairs | Approved planning document | Thought processes |
| Each Ministry | Dispatch instructions + background | Other ministries' reports |
| Censorate | Complete workflow record | No restrictions |
| Remonstrator | Memorial + user message (reads second-brain on its own) | Thought processes |
