# 同步协议 · 会话开始拉、结束写

**本地备忘。不推送 GitHub。给自己看的技术参考。**

Life OS 的多后端同步发生在两个明确的时刻 — Session Start（全量拉取）和 Session Close（输出写入）。会话中间不做同步。这是故意的设计。

权威源：`references/data-model.md`（Sync Protocol）、`references/data-layer.md`（RETROSPECTIVE Housekeeping Mode）。

---

## 为什么只在两端同步

### 不是每 N 分钟轮询

传统同步工具（Dropbox、Google Drive 桌面）每几秒扫一次文件系统。这在文件数少、变化频繁的场景合适。

但 second-brain 不是那种场景：

- 一次会话可能写几十个文件。中间同步 = 写一个拉一个，刷爆网络。
- 决策类文件不应该"部分状态"被其他设备看到。要么完整要么没有。
- 中间同步打乱"会话是原子单位"的心智模型。

所以 Life OS 只在 Session Start 和 Session Close 两端同步。会话中间本地写，会话结束一次 push。

---

## Session Start · 全量拉取

触发词：`上朝` / `start` / `begin` / `はじめる` 等。

由 RETROSPECTIVE 子代理在 Mode 0（Housekeeping）执行。同步是 18 步流程里的步骤 4-7。

### Step 4 · 读 config

读 `_meta/config.md` 拿到：

- 配置的后端列表（`[github, notion]` 等）。
- 本平台的 `last_sync_time`（例如 Claude Code 和 Gemini CLI 各自存一个）。

### Step 5 · Git 健康检查

同步前扫一眼本地状态：

- `git worktree list` 有没有 prunable entries。
- `.claude/worktrees/` 有没有残留。
- `core.hooksPath` 是否指向不存在路径。

有问题 → 报告给用户确认后再修复（不自动执行破坏性操作，见 Security Boundary #1）。

### Step 6 · Full Sync Pull

对每个**可用的** backend：

1. 查询"自本平台 last_sync_time 之后有变更的 items"。
   - GitHub: `git log --since="{last_sync_time}" --name-only`
   - GDrive: MCP 查询 `modifiedTime > last_sync_time`
   - Notion: MCP 查询 `last_edited_time > last_sync_time`
2. 比对各 backend 的变更。
3. 解决冲突（规则见下方）。
4. 把获胜版本写入 primary backend。
5. 把 primary 状态推送到所有 sync backends。
6. 更新 `_meta/sync-log.md`。
7. 更新本平台 `last_sync_time`。

### Step 7 · Outbox merge

扫 `_meta/outbox/` 下的未合并会话目录（之前会话退朝时写的 outbox）。按时间顺序合并到主目录。详见 `parallel-sessions.md`。

---

## 冲突解决规则

两个后端在上次同步后都改了同一个 item。怎么办？

### 规则（last-write-wins + timestamp）

| 情况 | 动作 |
|------|------|
| 只有一个后端改了 | 采用那个 |
| 两个都改了，`last_modified` 时间差 > 1 分钟 | 新的赢 |
| 两个都改了，时间差 ≤ 1 分钟 | **CONFLICT**：保留两个版本，ROUTER 让用户选 |
| 用户选了 A | A 写入 primary + 推到所有 sync |
| 用户选了 B | B 写入 primary + 推到所有 sync |

### 为什么容忍 1 分钟差

时钟偏差。不同设备、不同时区、NTP 偶尔失同步。1 分钟是一个安全的"可能是真的同时"阈值。

真实场景里，两个人/两台设备在 1 分钟内同时改同一个决策的概率极低 — 出现了就问你。

### 冲突文件长啥样

CONFLICT 情况下在 outbox 里保留两份：

```
_meta/conflicts/2026-04-08-career-decision-A.md
_meta/conflicts/2026-04-08-career-decision-B.md
```

下次 Session Start RETROSPECTIVE 检测到 `_meta/conflicts/` 里有东西 → 在晨报里提示：

```
⚠️ 未解决冲突: 1
  - career-decision: GitHub 版本 A vs Notion 版本 B
    A 的 last_modified: 2026-04-08T15:30:00+09:00
    B 的 last_modified: 2026-04-08T15:30:22+09:00
    两者写了不同的 score（6.8 vs 7.2）。
    选哪个？
```

你选了 → 赢家写入 primary，推到所有 backend，clonflicts 目录清掉。

---

## Session Close · 输出写入

触发词：`退朝` / `adjourn` / `done` / `end` / `お疲れ` 等。

由 ARCHIVER 子代理执行。写入是 ARCHIVER Phase 4（Sync）的内容。

### 写入顺序

```
1. 写所有输出到 primary backend（_meta/outbox/{session_id}/）
2. 写所有输出到每个 sync backend
3. 更新 _meta/config.md last_sync_time
4. 任何 backend 失败 → 记录到 _meta/sync-log.md，不阻塞
```

### Outbox 模式

ARCHIVER **不直接写主目录**。先写进 outbox：

```
_meta/outbox/claude-20260408-2200/
├── manifest.md         ← 会话元信息
├── decisions/          ← 本会话的决策
├── tasks/              ← 本会话的任务
├── journal/            ← 本会话的日志
├── wiki/               ← 本会话抽出的 wiki 条目
├── index-delta.md      ← projects/{project}/index.md 要改的字段
└── patterns-delta.md   ← user-patterns.md 要追加的内容
```

为什么：`parallel-sessions.md` 讲得更细。核心是 — 多个会话同时写共享文件会互相踩，outbox 让每个会话只写自己的一份，合并动作原子化由下一次 Start Session 独占执行。

### git commit · 只 stage outbox

```bash
git add _meta/outbox/{session_id}/
git commit -m "[life-os] session {session_id} output"
git push
```

**绝不用 `git add -A` 或 `git add .`**。那些会误加：

- `.env` 里的密钥
- `.claude/` 下的会话日志
- 各种临时文件

Life OS 永远只提交自己写的东西。

### Step 10a · Notion Sync（orchestrator）

ARCHIVER 不能访问 Notion MCP（那是环境特定的工具）。所以 Notion 同步在 ARCHIVER 完成后，由 orchestrator（主 context）执行：

```
a. 🧠 Current Status page: 用最新 STATUS.md 覆写
b. 📋 Todo Board: 本会话的 tasks（新任务→创建，完成任务→勾掉）
c. 📝 Working Memory: 写会话总结（主题、关键结论、action items）
d. 📬 Inbox: 把已处理的条目标为 Synced
e. Notion MCP 不可用 → 报告 "⚠️ Notion sync failed"
f. 单个写入失败 → 报告具体哪个，继续其他
```

详见 `docs/user-guide/storage-and-sync/notion-as-transport.md` 和 `pro/CLAUDE.md` 的 Step 10a。

---

## .merge-lock 机制详解

**问题**：两个会话同时 Start Session，同时要合并 outbox。谁先谁后？

**答案**：用 `.merge-lock` 文件做 mutex。

### 锁的写入和清理

```
Session X 开始合并 outbox：
  1. 检查 _meta/.merge-lock 存在吗？
     - 不存在 → 走步骤 2
     - 存在但 > 5 分钟 → stale（上次崩溃了），清掉，走步骤 2
     - 存在且 < 5 分钟 → 跳过合并，假定另一个会话在做
  2. 写 .merge-lock：
     {
       "session_id": "claude-20260408-2200",
       "locked_at": "2026-04-08T22:00:30+09:00"
     }
  3. 合并所有 outbox 到主目录
  4. 编译 STATUS.md
  5. git commit + push
  6. 删 .merge-lock
```

### 5 分钟阈值怎么定的

- 正常合并 10-30 秒完成。
- 网络慢 / 大量 outbox → 可能 2-3 分钟。
- 极端情况下 5 分钟绰绰有余。
- 超过 5 分钟还没释放 → 高概率进程崩了，应该强制接管。

### 锁冲突发生了怎么办

Session A 在合并（写了 lock）。Session B 上朝看到 lock 跳过合并。Session B 正常跑完会话，退朝时只写自己的 outbox，不影响 A 的合并。

Session A 合并完 → 删 lock。Session B 下次再上朝时看到 lock 没了，自己触发合并（把 B 之前退朝写的 outbox 合并掉）。

整个流程 race-free，哪怕 A 和 B 完全同时触发 lock 检查也没问题（文件系统的 exclusive-create 语义保证）。

---

## Per-platform last_sync_time

不同平台独立维护自己的 `last_sync_time`。

```yaml
# _meta/config.md
storage:
  backends:
    - type: github
      role: primary
    - type: notion
      role: sync
  sync_log:
    - platform: claude-code
      last_sync: "2026-04-08T22:00:00+09:00"
    - platform: gemini-cli
      last_sync: "2026-04-08T18:30:00+09:00"
    - platform: codex-cli
      last_sync: "2026-04-07T14:00:00+09:00"
```

### 为什么按平台存

场景：你用 Claude Code 跑一个会话（22:00），然后切到 Gemini CLI 跑另一个（23:00）。

Gemini CLI 上朝时查"自 Gemini 上次 sync 18:30 以来有啥变化" → 包括 Claude Code 在 22:00 推的内容。

如果只维护一个全局 `last_sync_time`，Gemini 会查"自 22:00 以来" → 漏掉自己 18:30 之前 Claude Code 的变化？不，但会造成"A 同步之后 B 再同步时重复处理 A 同步的内容"。按平台存解决这个问题。

---

## 降级规则

### 一个 backend 不可用

| 情况 | 处理 |
|------|------|
| Primary 不可用 | 临时提升下一个可用 backend 为 primary，晨报标"⚠️ primary backend unavailable" |
| Sync backend 不可用 | 继续其他，记录到 `_meta/sync-log.md`，下次会话自动重试 |
| 所有都不可用 | 继续会话，输出只显示不持久化 |

### 网络断了

ARCHIVER 写本地（outbox）能成功。git push 失败 → 记录。下次上朝：

```
Step 6 Full Sync Pull 之前，RETROSPECTIVE 检查本地是否有未推送的 commits：
  - 有 → 尝试 push
  - push 成功 → 继续
  - push 失败 → 晨报"⚠️ 有 N 个本地 commits 未推送，网络问题持续"
```

---

## sync-log.md · 审计

`_meta/sync-log.md` 记录每次同步的结果：

```markdown
## 2026-04-08T22:00:00+09:00 · claude-code · Session End

Backends:
- github: ✅ pushed 3 decisions, 2 tasks, 1 journal
- notion: ⚠️ inbox sync failed — MCP timeout
  will retry next session

## 2026-04-09T07:30:00+09:00 · claude-code · Session Start

Pulled:
- github: 2 new items since 2026-04-08T22:00
- notion: 1 new inbox item

Merged: 1 outbox (claude-20260408-2200)
.merge-lock acquired + released successfully.
```

这个 log 很少看，但出故障时关键。AUDITOR 巡查时也会读它看有没有积压的失败同步。

---

## 实战节奏

### 正常节奏

```
早上 上朝
  → Session Start 拉取所有 backend 的变更
  → 合并昨晚的 outbox（如果有）
  → 晨报
一整天 开会话、跑决策、写 wiki
  → 所有写入在本地 / outbox
夜里 退朝
  → ARCHIVER 写本会话 outbox
  → git commit + push
  → Notion sync（orchestrator）
```

### 飞机模式

```
飞机起飞前 上朝（有网）→ 拉取成功
飞行中 开会话 → 所有写入本地 + outbox
落地 退朝（还没网）
  → outbox 写到本地 git
  → push 失败 → 记录
到酒店 (下次上朝)
  → Step 6 尝试 push pending commits → 成功
  → 继续正常流程
```

系统对无网容忍。关键是你要 Session Start + Session Close 的触发词敲对。
