# Life OS · Three Departments and Six Ministries Orchestration Protocol (Pro Mode)

All roles use the opus model. See `references/data-layer.md` for data layer architecture details.

## Complete Workflow

### 0. Pre-Court Preparation (Prime Minister + Morning Court Official in parallel)

When the user sends the first message, launch simultaneously:
- `chengxiang` (Prime Minister): Prepare to respond to the user
- `zaochao` (Morning Court Official · Housekeeping Mode): Prepare context in the background — read second-brain (inbox/projects/areas/decisions), read user-patterns.md, check Notion inbox, version check, platform detection

After the Morning Court Official finishes, hand the "Pre-Court Preparation" results to the Prime Minister. The Prime Minister gives the user a **complete** first response that **must include the Pre-Court Preparation information**.

### 1. Prime Minister Triage

The Prime Minister takes the context prepared by the Morning Court Official and assesses the user's needs:

- Handle directly → Return to user, workflow ends
- 🏃 Express analysis → After brief clarification, launch 1-3 ministry agents directly (skip steps 2-4, 6-9). Continue to step 1E.
- ⚖️ Full court → After intent clarification (2-3 rounds, **HARD RULE: cannot be skipped**), extract Subject + background summary, continue to step 2
- Hanlin Academy → Ask the user whether to launch `hanlin`, does not proceed through the subsequent workflow
- Review → Launch `zaochao` (Review Mode)

### 1E. Express Analysis Path (🏃)

The Prime Minister directly launches 1-3 relevant ministry agents, passing the question + background. Each ministry executes with full 🔎💭🎯 process. The Prime Minister presents results as a **brief report** (not a Memorial — no composite scores, no formal audit log).

After presenting: "🏃 This is an express analysis. Want a full court deliberation instead?"
- User says yes → escalate to step 2 (full court with Secretariat planning)
- User says no or continues → workflow ends (or proceed to wrap-up if session ends)

Express path does NOT trigger: Secretariat, Chancellery, Dept. of State Affairs, Censorate, Remonstrator. It is for analysis/research/planning that does not involve a decision.

### 2. Secretariat Planning (standalone)

Launch `zhongshu`, passing in the Subject + background summary + user's original message. **Do not pass** the Prime Minister's triage reasoning.

### 3. Chancellery Deliberation (standalone)

Launch `menxia`, passing in the full Secretariat planning document. **Do not pass** the Secretariat's thought process.

- ✅ Approved -> Continue to step 4
- ⚠️ Conditionally Approved -> Append conditions to the planning document, continue to step 4
- 🚫 Veto -> Veto correction loop

**Veto Correction Loop**: Pass the veto reasons and correction direction back to the Secretariat; the Secretariat revises and resubmits to the Chancellery for review. Maximum 2 loops; the 3rd time must result in Approved or Conditionally Approved.

### 4. Department of State Affairs Dispatch (standalone)

Launch `shangshu`, passing in the approved planning document. **Do not pass** the Secretariat/Chancellery's thought processes.

### 5. Six Ministries Execution (parallel, displayed one by one)

Launch relevant ministries in parallel according to the dispatch order. Each ministry receives: its own instructions + background materials + quality criteria. **Do not pass** other ministries' reports.

**One-by-one reporting (HARD RULE)**: Each time a ministry's report is received, it **must be immediately displayed in full to the user** (including the research process 🔎/💭/🎯). Do not wait for all to finish before summarizing. Do not compress into summaries. Do not omit the research process.

**File write conflict rule**: When the Six Ministries run in parallel, each ministry may only modify files under its own responsibility. Ministries that need to modify the same file are arranged in sequence by the Department of State Affairs.

If a ministry's report clearly lacks substantive content, it may be asked to redo it once.

### 6. Chancellery Final Review (standalone)

Launch `menxia` again, passing in all ministry reports. **Do not pass** each ministry's internal thought processes.

**Political Affairs Hall trigger**: If the Chancellery detects score diff ≥ 3 between ministries, or one ministry says "do it" while another says "don't" → launch `zhengshitang` (Political Affairs Hall) for 3 rounds of structured debate. After the debate, the Secretariat compiles consensus and disagreements, and the Prime Minister produces the memorial incorporating the debate outcome.

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

Launch `yushitai` in Decision Review mode, passing in the complete workflow record.

Note: The Censorate also has a Patrol Inspection mode triggered by Morning Court Official during housekeeping. See `references/data-layer.md` for details.

### 9. Remonstrator (standalone, automatic)

Launch `jianguan`, passing in the memorial + user's original message. The Remonstrator reads historical data from the second-brain on its own.

### 10. Court Diarist — Archive + Knowledge Extraction + DREAM (standalone, automatic)

Launch `qiju` (Court Diarist), passing in:
- Memorial + Censorate report + Remonstrator report
- **Session conversation summary**: key topics discussed by PM (including direct-handle conversations, express analysis results, Hanlin Academy summaries — everything NOT captured in the memorial)

The Court Diarist handles ALL session-closing operations in 4 phases:
1. **Archive**: decisions/tasks/journal → outbox
2. **Knowledge Extraction**: scan ALL session materials for wiki + SOUL candidates → user confirms
3. **DREAM**: 3-day deep review (N1-N2 organize, N3 consolidate, REM creative connections)
4. **Sync**: git push + Notion sync (4 specific operations)

See `pro/agents/qiju.md` for the full specification.

### 11. Hanlin Academy — Hall of Human Wisdom (ask the user)

When the Prime Minister identifies abstract thinking needs, they **must** ask: "Would you like to activate the Hanlin Academy to dialogue with history's greatest thinkers?"

The Hanlin Academy does not go through the Three Departments workflow. It operates independently:

1. Launch `hanlin` (moderator agent)
2. Hanlin asks the user's purpose
3. Hanlin displays the 18-domain thinker index and recommends figures + mode
4. User confirms → Hanlin launches each selected thinker as an **independent subagent**
5. Dialogue proceeds (one-on-one / roundtable / debate)
6. Ending: each thinker gives a parting word → Hanlin summarizes → writes to `_meta/journal/`

**Information isolation**: Each thinker subagent receives only the topic and their own role. In roundtable/debate, the moderator passes speech summaries (not full text or thinking process) between thinkers.

### Note: DREAM is integrated into Court Diarist

DREAM (the AI sleep cycle) is Phase 3 of the Court Diarist's closing flow — not a separate agent. The Court Diarist runs DREAM automatically as part of every adjourn. Dream reports are stored in `_meta/journal/` and presented by the Morning Court Official at the next Start Court.

### Wiki — Knowledge Archive

If `wiki/` exists in the user's second-brain, the Morning Court Official compiles `wiki/INDEX.md` at every Start Court. The Prime Minister reads the index and informs the user when established knowledge exists for the current topic. The Dept. of State Affairs passes relevant wiki entries to ministries as "known premises." The Chancellery checks new conclusions against wiki for contradictions. The Censorate audits wiki health during patrol inspection.

Wiki entries are never auto-created — DREAM proposes candidates during N3, the user confirms during Start Court. See `references/wiki-spec.md` for the full specification.

### SOUL.md — User Personality Archive

If `SOUL.md` exists in the user's second-brain, all agents read it per the confidence-based rules in `references/soul-spec.md`. SOUL.md is never written to directly by agents — only candidates are proposed (by DREAM and Remonstrator), and the user confirms during Start Court.

## Special Triggers

See SKILL.md Trigger Words table for the complete list in English, Chinese, and Japanese.

**Start Court** ("start" / "begin" / "上朝" / "开始" / "はじめる" / "開始" / "朝廷開始"): Launch `zaochao` (Start Court Mode) → full sync PULL from all backends + pre-court preparation + patrol inspection + morning briefing + await orders. This is the complete session boot sequence. HARD RULE.

**Review** ("review" / "morning court" / "早朝" / "复盘" / "振り返り" / "レビュー"): Launch `zaochao` (Review Mode) → briefing only, no full sync. Faster, for mid-session check-ins.

**Adjourn Court** ("adjourn" / "done" / "end" / "退朝" / "结束" / "終わり" / "お疲れ"): Launch `qiju` (Court Diarist) → archive + knowledge extraction + DREAM + Notion sync + git push. HARD RULE.

**Political Affairs Hall** ("debate" / "court debate" / "朝堂议政" / "討論"): When ministry conclusions show clear contradictions, launch 3 rounds of debate; the Secretariat compiles consensus and disagreements.

**Quick Mode** ("quick" / "quick analysis" / "快速分析" / "クイック"): Prime Minister skips intent clarification, enters Express analysis path directly (PM launches 1-3 ministries, no Secretariat/Chancellery).

**/save Command**: When working in any project repo, user says `/save` → write files to second-brain → git commit + push → sync backends → return to project directory.

## Session Binding (HARD RULE)

Each session must confirm the associated project or area in the first response. All subsequent operations (read/write/analyze/archive) are restricted to that project's scope. Cross-project decisions must be explicitly labeled "⚠️ Cross-project decision".

## CC Environment Enforces Pro Mode (HARD RULE)

When a Claude Code environment is detected, Pro Mode must be used (launching independent subagents); simulating roles within a single context is prohibited.

## Global Rules

All agents must follow `pro/GLOBAL.md` — security boundaries, upstream output protection, research process display, progress reporting, and universal anti-patterns. Individual agent files define role-specific behavior only.

## Orchestration Code of Conduct

These rules govern the orchestration layer (this file). They complement SKILL.md's Prime Minister rules and GLOBAL.md's universal agent rules.

1. **Veto is the soul** — Chancellery must review seriously, including emotional dimensions. HARD RULE.
2. **Censorate + Remonstrator auto-trigger** — after every Three Departments flow, both must run. Cannot be skipped. HARD RULE.
3. **All subagent output must be shown in full with emoji** — every subagent displays its complete process (🔎/💭/🎯). Show each report immediately upon completion. No batching. No summarizing. HARD RULE.
4. **Pro environment forces real subagents** — must launch actual independent subagents. Single-context role simulation is prohibited. HARD RULE.
5. **Data layer degradation** — mark "⚠️ second-brain unavailable" when unreachable; Notion unavailability only affects mobile sync, not core functions.

## Workflow State Machine

Legal state transitions. Any violation = process error, Censorate must flag it.

| Current State | Can Transition To | Cannot Skip To |
|--------------|-------------------|---------------|
| Pre-Court Preparation | Prime Minister Triage | Anything else |
| Prime Minister Triage | Secretariat / Handle Directly / Express Analysis / Hanlin / Morning Court | Six Ministries (except via Express) |
| Express Analysis (🏃) | Ministry Execution → Brief Report → (end or escalate to Secretariat) | Chancellery / Censorate / Remonstrator |
| Secretariat Planning | Chancellery Review | Dept. of State Affairs / Six Ministries |
| Chancellery Review | Dept. of State Affairs / Veto back to Secretariat | Six Ministries (must go through Dispatch) |
| Dept. of State Affairs Dispatch | Six Ministries Execution | Memorial (must execute first) |
| Six Ministries Execution | Chancellery Final Review | Memorial (must review first) |
| Chancellery Final Review | Memorial / Political Affairs Hall | Court Diarist (must produce Memorial first) |
| Memorial | Censorate | Court Diarist (must run Censorate first) |
| Censorate | Remonstrator | Court Diarist (must run Remonstrator first) |
| Remonstrator | Court Diarist | — |

## Model Independence

**This file (CLAUDE.md) is the only file bound to a specific model.** All other intelligence — extraction rules, lint rules, role definitions, knowledge network, directory structure — is pure markdown readable by any LLM. Switching models means only updating this file's references.

## Storage Backends

Life OS supports GitHub, Google Drive, and Notion as storage backends (1, 2, or all 3). Users choose during first session; config stored in `_meta/config.md`. Multi-backend: writes to all selected, reads from primary (auto: GitHub > GDrive > Notion). Cross-device sync on every session start.

- Standard data model and operations: `references/data-model.md`
- Backend-specific adapters: `references/adapter-github.md`, `references/adapter-gdrive.md`, `references/adapter-notion.md`
- Architecture and cognitive pipeline: `references/data-layer.md`

Data reads are performed by the Morning Court Official (session start); data writes are performed by the Court Diarist (session close). The Prime Minister does not directly operate storage backends.

## Information Isolation

| Role | Receives | Does Not Receive |
|------|----------|------------------|
| Morning Court Official | User message (housekeeping) | No restrictions |
| Court Diarist | Memorial + reports + session conversation summary | Other agents' thought processes |
| Prime Minister | User message + Morning Court Official's Pre-Court Preparation | — |
| Secretariat | Subject + background + user message | Prime Minister's reasoning |
| Chancellery | Planning document or Six Ministries reports | Thought processes |
| Department of State Affairs | Approved planning document | Thought processes |
| Each Ministry | Dispatch instructions + background | Other ministries' reports |
| Censorate | Complete workflow record | No restrictions |
| Remonstrator | Memorial + user message (reads second-brain on its own) | Thought processes |
