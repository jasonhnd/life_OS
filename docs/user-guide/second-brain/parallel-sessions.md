# 并行会话 · 多个终端同时跑

**本地备忘。不推送 GitHub。给自己看的技术参考。**

真实场景：你在 A 项目的终端开了个会话，家人在客厅用另一台 Mac 开了一个 CC 讨论家庭事情。或者你在公司用桌面电脑上 Claude Code，手机上同时用 Claude.ai 配合 Notion 记东西。

Life OS 支持这种 **多会话并行**。核心机制：outbox 模式 + .merge-lock。

权威源：`references/data-model.md`（Constraints + Outbox Manifest）、`references/adapter-github.md`（On Adjourn / On Start Court）。

---

## 传统问题

没有 outbox 机制，两个会话同时结束会直接踩对方的文件：

```
Session A 和 Session B 同时运行

Session A 退朝：
  - 写 projects/career/decisions/2026-04-08-foo.md
  - 重写 _meta/STATUS.md
  - 重写 user-patterns.md
  - git push

Session B 退朝（同时）：
  - 写 projects/finance/decisions/2026-04-08-bar.md
  - 重写 _meta/STATUS.md      ← 和 A 冲突
  - 重写 user-patterns.md     ← 和 A 冲突
  - git push                  ← 失败或覆盖

结果：A 的 STATUS.md 更新丢了，或者 git push 失败让用户困惑。
```

Outbox 模式把"写入"和"合并"分开，避开这个问题。

---

## Outbox 工作机制

### 退朝时 · ARCHIVER 只写自己的 outbox

```
_meta/outbox/
├── claude-20260408-2200/       ← Session A 的输出
│   ├── manifest.md
│   ├── decisions/
│   │   └── 2026-04-08-foo.md
│   ├── tasks/
│   │   └── task-1.md
│   ├── journal/
│   │   └── 2026-04-08-session.md
│   ├── wiki/
│   │   └── tech-notes.md
│   ├── index-delta.md          ← 要给 projects/career/index.md 改什么
│   └── patterns-delta.md       ← 要追加到 user-patterns.md 的东西
│
├── claude-20260408-2210/       ← Session B 的输出（同时存在）
│   ├── manifest.md
│   └── ...
│
└── gemini-20260408-1830/       ← 更早在 Gemini CLI 跑的会话
    ├── manifest.md
    └── ...
```

每个会话有**唯一的 session-id**：`{platform}-{YYYYMMDD}-{HHMM}`。

格式例子：
- `claude-20260408-2200` — Claude Code 2026-04-08 22:00
- `gemini-20260408-1830` — Gemini CLI 2026-04-08 18:30
- `codex-20260408-1445` — Codex CLI 2026-04-08 14:45

### 退朝时不碰共享文件

退朝流程（ARCHIVER）**只写 `_meta/outbox/{session_id}/` 目录**。

绝对不碰的文件：

- `projects/{project}/index.md`
- `_meta/STATUS.md`
- `user-patterns.md`
- 其他项目或领域的文件

这些文件的变更以 **delta** 形式记在 outbox：

```markdown
# index-delta.md

## Target: projects/japan-startup-visa/index.md
## Fields to update:
- Phase: "等审批" → "审批通过"
- status_reason: "入管局已批"
```

```markdown
# patterns-delta.md — append to user-patterns.md

### [2026-04-08] New pattern: decision speed increasing
Source: ADVISOR
Observation: 最近 3 个决策都在首轮 clarification 后做出。
```

### git commit 只包含 outbox

```bash
git add _meta/outbox/{session_id}/
git commit -m "[life-os] session {session_id} output"
git push
```

**绝不用 `git add -A`** — 会意外提交其他东西（.env、credentials、临时文件）。只 stage Life OS 自己写的东西。

### 上朝时合并 outbox

下一个 Start Session（任何平台、任何会话）都在步骤 7 做 outbox merge：

```
Step 7. OUTBOX MERGE

扫 _meta/outbox/ 下所有会话目录：
  - 如果 _meta/.merge-lock 存在且 < 5 分钟 → 跳过合并（另一个 session 在做）
  - 写 _meta/.merge-lock 锁
  - 对每个 outbox（按 session-id 时间排序）：
      - 读 manifest.md
      - 移 decisions/ → projects/{project}/decisions/
      - 移 tasks/ → projects/{project}/tasks/
      - 移 journal/ → _meta/journal/
      - 应用 index-delta.md → 更新 projects/{project}/index.md
      - 追加 patterns-delta.md → user-patterns.md
      - 移 wiki/ → wiki/{domain}/{topic}.md
      - 合并成功 → 删掉这个 outbox 目录
  - 全部合并后：编译 _meta/STATUS.md
  - git commit + push
  - 删 _meta/.merge-lock
  - 晨报报告"📮 合并了 N 个离线会话"
```

---

## .merge-lock 机制

**问题**：两个会话同时上朝，同时尝试合并 outbox → 数据损坏。

**解决**：`.merge-lock` 文件 + 5 分钟过期。

### 工作流

```
Session X 上朝到步骤 7：
  1. 检查 _meta/.merge-lock 存在吗？
     - 不存在 → 继续
     - 存在但 > 5 分钟 → 视为 stale（前一个会话崩了），清掉继续
     - 存在且 < 5 分钟 → 跳过合并，假定另一个会话在做
  2. 写 _meta/.merge-lock（包含当前 session-id + 时间戳）
  3. 合并所有 outbox
  4. git commit + push
  5. 删 _meta/.merge-lock
```

### 锁内容

`.merge-lock` 里放：

```
session_id: claude-20260408-2215
locked_at: 2026-04-08T22:15:30+09:00
```

其他会话看到这个就知道是谁在做、从什么时候开始。

### 锁卡住的情况

会话崩溃、网络挂掉、进程被杀 → `.merge-lock` 不被删。下一次上朝：

- 看到 `.merge-lock` > 5 分钟 → stale。
- 清掉并自己做合并。

5 分钟是一个平衡点：正常合并 10 秒完成，5 分钟绝对够。同时太短会误判网络慢的会话为"崩溃"。

---

## 合并顺序 · 按时间

多个 outbox 按 session-id 里的时间戳合并，**老的先合，新的后合**。

理由：新会话可能是基于老会话的结果做的决策。倒过来合并会让新决策基于还没生效的状态。

示例：

```
outbox 里有：
  - claude-20260408-1400    # Session A
  - gemini-20260408-1800    # Session B
  - claude-20260408-2200    # Session C

合并顺序：A → B → C

如果 C 修改了 A 创建的 index，按这个顺序：
  1. A 创建 project_x
  2. B 更新 project_x.status = planning
  3. C 更新 project_x.status = active
  
最终：project_x.status = active（C 赢）
```

如果两个会话修改同一个字段而且时间相近 → 用 `last_modified` 时间戳判断。见 `sync-protocol.md`。

---

## 实战场景

### 场景 A · 桌面 + 手机

你在桌面开会话讨论 career 项目。同时手机上用 Claude.ai 往 Notion inbox 丢东西。

- 桌面会话：正常跑，退朝写 outbox。
- 手机 Notion：实时写入 Inbox 数据库。
- 下次上朝：读 Notion inbox + 合并 outbox → 都吸收。

不会冲突，因为两边写不同的东西。

### 场景 B · 两个桌面会话

你在 MacBook 开 `japan-startup-visa` 会话。爱人借你 iMac 开 `family-trip` 会话。

- 两个会话都绑定不同项目 → 写的 decisions / tasks 不重叠。
- 退朝时刻不一样：MacBook 22:00 退朝，iMac 22:15 退朝。
- 两个 outbox：`claude-20260408-2200` + `claude-20260408-2215`。
- 明天 MacBook 上朝 → 合并两个 outbox → MacBook 拿到 iMac 的更新。

### 场景 C · 多平台（危险但支持）

你在 Claude Code 跑一个会话。同时 Gemini CLI 跑另一个。两个平台独立的 orchestrator。

- 每个平台维护自己的 `last_sync_time`（在 `_meta/config.md` 里）。
- 两个平台都写自己的 outbox。
- 任何一个下次 Start Session 都会合并两个平台的 outbox。

注意：`last_sync_time` 按平台存：

```yaml
storage:
  backends:
    - type: github
      role: primary
  sync_log:
    - platform: claude-code
      last_sync: "2026-04-08T22:00:00+09:00"
    - platform: gemini-cli
      last_sync: "2026-04-08T18:30:00+09:00"
```

Gemini CLI 下次上朝读**自己的** `last_sync`（18:30），查 Claude Code 在 22:00 推的东西。不会漏。

---

## 冲突检测

真正冲突（两个会话改同一个 index 字段、时间差 < 1 分钟）会在合并时被发现。此时：

1. ROUTER 晨报告诉用户："冲突：projects/X/index.md 的 status 字段有两个值。"
2. 保留两个版本在 outbox 里不删。
3. 问用户选哪个。
4. 用户选了 → 写入 primary，推到 sync backends，清掉 outbox。

绝大多数情况下不会冲突 — 因为并行会话通常绑定不同项目。

---

## 失败恢复

### Outbox 目录损坏

某个 outbox 里 `manifest.md` 缺失或格式错：

- 合并时跳过这个 outbox，标黄报告给用户。
- 用户自己决定：修复 + 重试 / 放弃这个会话的数据。

### git push 失败

网络挂了：outbox 已经 commit 但没 push。下次上朝：

- 步骤 6（FULL SYNC PULL）会尝试 push 之前 commit 的东西。
- 如果 push 失败持续，晨报显示"⚠️ 有本地 commits 未推送"。

### 重复 session-id

极少数情况两个会话同时退朝用了一样的时间戳。`outbox/{session_id}/` 冲突：

- ARCHIVER 退朝时检查目标目录是否存在 → 存在 → 追加 `-2` 后缀。
- 合并时照常处理。

---

## 核心心态

Outbox 模式让并行安全的关键：**每个会话只写自己的那份，不碰共享文件。共享文件的合并是单个动作，由最早上朝的会话独占完成。**

如果你只跑单会话 + 单平台，这些机制你永远用不到 — 但它们在那里，让系统可以扩展到 3 台设备 + 2 个家庭成员 + 5 个并行项目。
