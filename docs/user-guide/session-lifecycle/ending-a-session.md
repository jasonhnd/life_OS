# 退朝 · 4 阶段归档流程

**本地备忘。不推送 GitHub。**

退朝 = Adjourn Session。由 ARCHIVER 子代理在独立上下文中执行 4 阶段。Notion 同步由 orchestrator 在 archiver 返回后执行（Step 10a，不是 archiver）。

触发词：`退朝` / `结束` / `adjourn` / `done` / `end` / `終わり` / `お疲れ` 等。

权威源：`pro/agents/archiver.md` + `pro/CLAUDE.md` Step 10/10a。

---

## ROUTER 的唯一职责

用户说退朝 → ROUTER 输出 **2 行**，不多不少：

```
Line 1 (active theme language): "📝 开始归档流程 — 4 个阶段..."
Line 2: Launch(archiver) as subagent
```

ROUTER **禁止** 做以下任何事（HARD RULE）：

- 在主上下文扫描会话找 wiki/SOUL/strategic 候选
- 列候选给用户看，问"要保存这些吗？"
- 说"告诉我你的决定，然后我启动 DREAM / Notion sync"
- 执行 Phase 1/2/3/4 里的任何内容
- 在 archiver 的 phase 之间插话

违反 = 流程违规。AUDITOR 会标记，写进 `user-patterns.md`，下次会话 ADVISOR 会 flag 为行为模式。

---

## Phase 1 · Archive（归档）

```
1. 读 _meta/config.md → storage backend 列表
2. 生成 session-id：运行 date 命令取真实时间戳，格式化 {platform}-{YYYYMMDD}-{HHMM}
3. 创建 outbox 目录：_meta/outbox/{session_id}/
4. Decision（summary report）→ _meta/outbox/{session_id}/decisions/
5. Task（action items）→ _meta/outbox/{session_id}/tasks/
6. JournalEntry（auditor + advisor reports）→ _meta/outbox/{session_id}/journal/
7. 写 index-delta.md → projects/{project}/index.md 的变更（version、phase、focus）
8. 如 advisor 有 "📝 Pattern Update Suggestion" → 写 patterns-delta.md
9. 写 manifest.md → 会话元数据
```

### HARD RULE

- **session-id 必须用真实时间戳**。`date` 命令的真实输出。不能编。编造时间戳是 HARD RULE 违反。
- **所有写入必须到 outbox**，不能直接写 `projects/`、`_meta/STATUS.md`、`user-patterns.md`。原子性：全部进 outbox，合并时一起合。

### 每个 decision 文件

必须有 front matter 的 `project` 字段。否则下次合并时无法路由。task 同理。

---

## Phase 2 · Knowledge Extraction（知识提取 — 核心职责）

**Phase 2 之前必须自检**：确认是在 archiver subagent 里跑，不是在主上下文。如果检测到在主上下文 → 立即停，报错"⚠️ archiver 必须作为 subagent 启动，不能 inline 执行"。

Phase 2 产出 **Session Candidates** — 仅从本次会话提取。基于严格准则 **自动写入**，不在主上下文问用户。

扫描所有材料：summary report + auditor/advisor reports + **会话对话摘要**（orchestrator 传来的，包括 ROUTER 直接处理的对话、express 分析结果、STRATEGIST 摘要等 summary report 没覆盖的内容）。

### Wiki 自动写入（6 条准则）

对每个可提取结论，全部 6 条必须过：

1. **跨项目可复用** — 在其他项目/域也有用。
2. **关于世界，不关于你** — 事实、规则、方法。不是价值观/习惯/偏好（这些属于 SOUL）。不是行为模式（这些属于 user-patterns.md）。
3. **零个人隐私** — 无姓名、金额、账号、ID、具体公司、亲友信息、可追溯的日期+地点组合。如果剥光这些后结论没意义 → 不是 wiki 材料，扔掉。
4. **事实性或方法论** — "发生了什么"或"怎么做 X"。不是"我觉得"或观点。
5. **多证据（≥2 独立）** — 至少 2 个案例/数据点/决策/引用。单次观察 → 扔掉。
6. **不与现有 wiki 矛盾** — 矛盾 → `challenges: +1` 到那个条目，不新建。

全过 → 自动写入 `_meta/outbox/{session_id}/wiki/{domain}/{topic}.md`。

**初始 confidence**：
- 3+ 独立证据 → 0.5
- 恰好 2 个证据 → 0.3
- 1 个或以下 → 扔掉

**隐私过滤**（写入前）：
- 剥姓名（除非公众人物且与结论直接相关）
- 剥具体金额、账号、ID
- 剥具体公司名（除非公开 case study）
- 剥亲友指代
- 剥可追溯的日期+地点组合

**不问用户确认**。Completion Checklist 里报告"自动写入 N 条 wiki，丢弃 M 条（原因：...）"。

### SOUL 自动写入

对每个价值/原则观察：

1. **关于身份/价值观/原则** — 不是行为模式。
2. **≥2 决策作为证据** — 单决策观察太薄。本次会话内至少 2 次，或跨会话强化。
3. **未被已有覆盖** — 有覆盖 → `evidence_count +1`，不新建。

通过 → 自动写入 `_meta/outbox/{session_id}/soul/`：
- `confidence: 0.3`（低初始 — 让 evidence/challenges 来养）
- `What IS`：系统基于观察填
- `What SHOULD BE`：**留空** — 用户自己在自己时间填

### Strategic candidates

自动写入 `index-delta.md`（沿用原机制，未变）。

### last_activity

所有接触到的项目 → 自动更新。

### 跨层验证

当前项目如有 cognition flow 定义，检查本次会话是否引用了上游 wiki 知识。未引用 → 记在 Completion Checklist。

### SOUL Snapshot Dump

Phase 2 结束后，dump 当前 SOUL 状态到 `_meta/snapshots/soul/YYYY-MM-DD-HHMM.md`。

格式：

```yaml
---
type: soul-snapshot
captured_at: ISO 8601 + tz
session_id: {UUID}
previous_snapshot: {上一个 snapshot 文件名 / null}
---

# SOUL Snapshot · YYYY-MM-DD

## Dimensions (count: N)

| dimension | confidence | evidence | challenges | last_validated |
|-----------|-----------|----------|------------|----------------|
| ...
```

**目的**：下次上朝 RETROSPECTIVE Step 11.2 读最新 snapshot，算 delta/箭头。只记数值元数据，What IS/What SHOULD BE 留在主 SOUL.md。

**归档策略**：>30 天移 `_meta/snapshots/soul/_archive/`；>90 天删除（git + Notion 已保留）。

---

## Phase 3 · DREAM（深度回顾）

归档完本次会话后，扩大到最近 3 天。系统的"睡眠周期"。

Phase 3 产出 **DREAM Candidates** — 从 3 天扫描发现。**不是现在确认**。存在 dream report 里，**在下次上朝时呈现** 给用户。

### Scope

默认：最近 3 天（72h）修改的文件。

```bash
FILES=$(git log --since="3 days ago" --name-only --format="" | sort -u)
```

- 3 天无变更 → 扩到"上次 dream 之后"（读最近 `_meta/journal/*-dream.md` 的日期）。
- 无 dream report → 扫最近 7 天。

### N1-N2 · Organize & Archive

🔎 扫 3 天变更：
- `inbox/` — 未分类？
- `_meta/journal/` — 有洞察值得提取？
- `projects/*/tasks/` — 过期、重复、陈旧？
- 创建但未 link 到项目 index 的文件？

💭 每个发现：可自动修 vs 需用户决策？

### N3 · Deep Consolidation

读 3 天变更集 + 当前状态：
- 新增/修改的 decisions
- `user-patterns.md` + `SOUL.md`
- `wiki/INDEX.md`

找：
- Phase 2 **遗漏** 的可复用结论（去重 — 不要重复提 Phase 2 已提的）
- 支持/反驳现有 wiki 的新证据 → 提 evidence_count/challenges 更新
- 行为模式 → 提 user-patterns.md 更新
- 价值信号 → 额外 SOUL 候选

### REM · Creative Connections + Auto-Triggered Actions

无 checklist — 让数据说话。

读所有 3 天内接触的项目和域。

问自己：
- 两件无关的事有什么连接会让用户意外？
- 哪个维度最近完全缺席决策？
- SOUL 和最近行为是否一致？
- 用户未来的自己会希望今天注意到什么？

**Auto-Triggered Actions**：评估 `dream-spec.md` 定义的 10 个自动触发模式（见 `the-briefing.md` 触发器表）。任何命中 → 写入 `triggered_actions` YAML。

### DREAM Output

写到 `_meta/outbox/{session_id}/journal/{date}-dream.md`：

```yaml
---
type: journal
journal_type: dream
date: YYYY-MM-DD
scope_files: N
stages: [N1-N2, N3, REM]
soul_candidates: N
wiki_candidates: N
strategic_candidates: N
triggered_actions:
  - trigger_id: 6
    trigger_name: "decision-fatigue"
    mode: "hard"
    detection:
      hard_signals: ["6 decisions in 18 hours", ...]
      soft_signals: []
    action: "flag-next-briefing-no-major-decisions-today"
    surfaces_at: "next-start-session"
    auditor_review: false
---
```

报告本体 20-50 行。不要搞 500 行。

---

## Phase 4 · Sync（仅 git；Notion 由 orchestrator 做）

```
1. git add _meta/outbox/{session_id}/ → commit → push（只加 outbox 目录）
2. 更新 _meta/config.md 的 last_sync_time
3. GitHub backend 失败 → 写 _meta/sync-log.md，标 ⚠️，不阻塞
```

### archiver 不做 Notion sync

archiver 没有 Notion MCP tools（它们是 environment-specific，不能声明在 agent frontmatter）。

archiver 返回后，**orchestrator（主上下文）** 执行 Notion sync。

---

## Step 10a · Notion Sync（orchestrator 做）— HARD RULE

archiver 返回 Completion Checklist 后，orchestrator **必须** 用主上下文的 Notion MCP tools 执行：

```
a. 🧠 Current Status page: 覆盖写最新 STATUS.md 内容
b. 📋 Todo Board: 同步本次会话 tasks（新→建，完成→打勾）
c. 📝 Working Memory: 写会话摘要（subject、关键结论、action items）
d. 📬 Inbox: 标记已处理项为 "Synced"
e. 如 Notion MCP 不可用 → 报告："⚠️ Notion sync failed — 手机端看不到更新"
f. 单项失败 → 报告哪一项，其他继续
```

完成后输出 Notion 部分的 checklist：

```
🔄 Notion sync:
- 🧠 Status: [updated / failed: {reason}]
- 📋 Todo: [synced {N} items / failed: {reason}]
- 📝 Working Memory: [written / failed: {reason}]
- 📬 Inbox: [marked synced / no items / failed: {reason}]
```

**不能静默跳过 Notion sync**。不能不尝试就说 "Notion MCP not connected"。

---

## Completion Checklist（archiver 必须输出）

4 个阶段结束后，archiver 输出：

```
📝 [theme: archiver] · Session Closed

📦 Archived: N decisions, M tasks, K journal entries
📚 Wiki: X 条自动写入
🌱 SOUL: Y 条自动写入
🗺️ Strategic: [新关系 / 无变化 / 未配置]
💤 DREAM: [关键洞察一句话 / 轻睡 — 无模式]
🔄 Git: ✅ {commit hash} | Notion: ⏳ pending (orchestrator will sync)

✅ Completion Checklist:
- Subagent invocation: [✅ / ⚠️ ran in main context — VIOLATION]
- Phase 1 outbox: _meta/outbox/{actual-session-id}/
- Phase 1 archived: {N} decisions, {M} tasks, {K} journal entries
- Phase 2 wiki auto-written: [{list} / 0 this session]
- Phase 2 wiki discarded: [{count} with reasons / none]
- Phase 2 SOUL auto-written: [{list} / 0 this session]
- Phase 2 strategic candidates: [{list} / none this session]
- Phase 2 last_activity updated: [{projects touched}]
- Phase 3 DREAM: [{1-line} / light sleep]
- Phase 4 git: {commit hash}
- Phase 4 Notion: ⏳ deferred to orchestrator (archiver lacks MCP tools)
```

**每项必须有具体值**。不能 "TBD"，不能空。缺项 = 不完整退朝，AUDITOR 会 flag。

---

## 退朝状态机（HARD RULE）

退朝不是主工作流的一步 — 是独立的 end-to-end 状态机。

### 合法转换

| 当前状态 | 可转到 |
|---------|-------|
| Adjourn Triggered | Launch(archiver) as subagent |
| archiver Running | archiver emits Completion Checklist |
| Checklist Output | Session End |

### 非法转换（全是违规）

- Adjourn Triggered → 主上下文执行 Phase 2（"让我先看有什么要保存的"）
- Adjourn Triggered → "告诉我你的决定，然后我再启动 subagent"
- archiver Running → 中途退出（Phase 3 DREAM 或 Phase 4 Sync 之前退）
- Checklist Output → Session End 但 checklist 里有 "TBD" 或空值
- ROUTER 在 archiver 各 phase 之间插话

### 执行

AUDITOR 在 session end 后立即运行。任何非法转换都报告、记到 `user-patterns.md`，下次会话 ADVISOR 会 flag 为行为模式。

---

## 为什么 archiver 必须是 subagent

v1.4.x 之前 ROUTER 经常把 archiver 的 Phase 2 扫描做在主上下文里："让我看看有什么要保存的..."。然后主上下文被候选列表污染，用户被迫选，流程半路卡住。

v1.5 开始强制：**adjourn 触发 = ROUTER 只输出 2 行，其他全部丢给 archiver subagent 一口气做完**。这样：

1. 主上下文保持干净（只知道"触发了归档"）
2. 4 阶段在独立上下文里一次性跑完，不会半路停
3. 扫描/判断/自动写入 的逻辑只在 archiver 里
4. Notion sync 分离出来，因为 MCP tools 是 environment-specific，archiver 拿不到

v1.6.2a 的 "fix: Notion sync returns to orchestrator" 就是这一块。之前 archiver 里 hardcode 说"Notion sync 交给 orchestrator"但 orchestrator 没做，结果手机端永远看不到。现在 CLAUDE.md Step 10a 明确：archiver 返回后，orchestrator 必须做 Notion sync，不能跳。
