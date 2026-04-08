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

- Handle directly -> Return to user, workflow ends
- Escalate -> After intent clarification (2-3 rounds, **HARD RULE: cannot be skipped**), extract Subject + background summary, continue to step 2
- Hanlin Academy -> Ask the user whether to launch `hanlin`, does not proceed through the subsequent workflow
- Review -> Launch `zaochao` (Review Mode)

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

### 8. Censorate (standalone, automatic)

Launch `yushitai`, passing in the complete workflow record.

### 9. Remonstrator (standalone, automatic)

Launch `jianguan`, passing in the memorial + user's original message. The Remonstrator reads historical data from the second-brain on its own.

### 10. Wrap-up Archival (Morning Court Official · Wrap-up Mode)

Launch `zaochao` (Wrap-up Mode), passing in the memorial + Censorate report + Remonstrator report. The Morning Court Official is responsible for:
1. Writing to the second-brain repo (decisions/tasks/logs)
2. git add + commit + push
3. Syncing Notion (update 🧠 Current State + 📝 related topic working memory)
4. Updating user-patterns.md (if the Remonstrator has pattern update suggestions)
5. If the second-brain is unreachable, note "⚠️ second-brain unavailable, this session's output was not archived"

### 11. Hanlin Academy (ask the user)

When the Prime Minister identifies a need for abstract thinking, they **must** ask the user whether to launch `hanlin`. This does not go through the above workflow.

## Special Triggers

**Political Affairs Hall**: When ministry conclusions show clear contradictions, launch 3 rounds of debate among the relevant ministries; the Secretariat compiles the consensus and disagreements.

**Morning Court**: User says "review" / "morning court" -> Launch `zaochao` (Review Mode).

**Quick Mode**: User says "quick analysis" -> Skip Prime Minister intent clarification, launch the Secretariat directly.

**Adjourn Court**: User says "adjourn court" -> Launch `zaochao` (Wrap-up Mode). Even if there is no Three Departments and Six Ministries workflow output, execute git push + Notion sync to ensure all changes from this session are persisted.

**/save Command**: When working in any project repo, user says `/save` -> Write files to second-brain -> git commit + push -> Sync Notion -> Return to project directory.

## Session Binding (HARD RULE)

Each session must confirm the associated project or area in the first response. All subsequent operations (read/write/analyze/archive) are restricted to that project's scope. Cross-project decisions must be explicitly labeled "⚠️ Cross-project decision".

## CC Environment Enforces Pro Mode (HARD RULE)

When a Claude Code environment is detected, Pro Mode must be used (launching independent subagents); simulating roles within a single context is prohibited.

## Data Layer

GitHub second-brain is the primary data store; Notion is working memory. See `references/data-layer.md` for details.

All data reads and writes are performed by the Morning Court Official; the Prime Minister does not directly operate the file system or Notion.

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
