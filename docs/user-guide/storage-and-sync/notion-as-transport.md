# Notion as Transport · 传输模式 vs 完整后端

**本地备忘。不推送 GitHub。给自己看的技术参考。**

Notion 在 Life OS 里有两个截然不同的角色。混淆了这两个，你会误以为自己的数据在同步，实际上一半根本没同步。

权威源：`references/adapter-notion.md`（"As Full Backend" vs "As Transport Layer"）、`pro/CLAUDE.md`（Step 10a Notion sync）。

---

## 两种模式

### 模式 1 · 完整后端（Full Backend）

Notion 是主存储。所有 6 种数据类型都存在 Notion 数据库：

| 数据类型 | Notion 数据库 |
|---------|--------------|
| Decision | 🤔 Decisions |
| Task | ✅ Tasks |
| JournalEntry | 📓 Journal |
| WikiNote | 📚 Wiki |
| Project | 🎯 Projects |
| Area | 🌊 Areas |

适用：你的工作流完全锚定 Notion，不想要 GitHub / GDrive。

**不推荐**（见下方"为什么不推荐完整后端"）。

### 模式 2 · 传输层（Transport Layer）

Notion 只存 4 个组件，负责手机和桌面之间传话：

| 组件 | 类型 | 作用 |
|------|------|------|
| 📬 Inbox | 数据库 | 手机 ↔ 桌面的消息队列 |
| 🧠 Current Status | 页面 | 镜像 `_meta/STATUS.md` |
| 📝 Working Memory | 话题页 | 当前活跃的 5-10 个话题 |
| 📋 Todo Board | 数据库 | 活跃任务供手机勾选 |

Primary backend 是 GitHub 或 GDrive — 所有 .md 文件的真源。Notion 只是桥。

**推荐**。大部分用户应该用这个模式。

---

## 怎么判断自己是哪种模式

看 `_meta/config.md`：

```yaml
# 模式 1 · Notion 完整后端
storage:
  backends:
    - type: notion
      role: primary
```

```yaml
# 模式 2 · Notion 传输层
storage:
  backends:
    - type: github       # 或 gdrive
      role: primary
    - type: notion
      role: sync         # 关键：role 是 sync，不是 primary
```

`role: primary` → 完整后端。`role: sync` → 传输层。

---

## 传输模式下的 4 个 Notion 组件

### 📬 Inbox 数据库

手机端捕获的入口。字段：

| 字段 | 类型 | 值 |
|------|------|-----|
| Content | Title | 用户说的话或写的内容 |
| Source | Select | Mobile / Desktop |
| Status | Select | Pending / Synced |
| Time | Date | 创建时间 |

工作流：

```
手机上说"想明年学德语"
  ↓
Claude.ai 手机端调用 notion-create-pages
  ↓
Notion Inbox 数据库新增一行：
  Content: "想明年学德语"
  Source: Mobile
  Status: Pending
  Time: 2026-04-08 14:32
  ↓
下次桌面上朝 RETROSPECTIVE 读到
  ↓
分流到 areas/learning/notes/ 或开项目
  ↓
ARCHIVER 把 Status 改成 Synced
```

### 🧠 Current Status 页面

是一整页，不是数据库。里面是 Markdown，镜像了 `_meta/STATUS.md`。

每次退朝 orchestrator 在 Step 10a 覆写这一页：

```
读 _meta/STATUS.md 最新内容
  ↓
notion-update-page(status_page_id, content)
  ↓
手机打开 Notion 看到最新的全局状态
```

手机上看 STATUS 页面就能知道：有哪些活跃项目、各项目什么阶段、当前焦点是什么。不需要开电脑。

### 📝 Working Memory

活跃话题。一个话题一页。通常 5-10 个。

例如：

```
📝 Working Memory/
├── 日本创业签证进展
├── Life OS v1.7 规划
├── 2026 财务目标
├── 亲子关系
├── 搬家到东京
```

每次退朝 orchestrator 写会话总结到对应页面：

- 会话讨论了"日本创业签证进展" → 更新那一页。
- 如果是全新话题（没对应页面）→ 创建新页。
- 话题连续 30 天没活动 → archiver 会提示"要不要归档到 GitHub 并从 Notion 删掉？"

### 📋 Todo Board

活跃任务。从 `projects/*/tasks/` 和 `areas/*/tasks/` 同步过来。

字段：

| 字段 | 来自 |
|------|------|
| Title | task 文件里的 title |
| Status | `todo` / `in-progress` / `waiting` / `done` / `cancelled` |
| Priority | p0 / p1 / p2 / p3 |
| Due Date | 任务的 due_date |
| Project | 关联项目 |
| Area | 关联领域 |

手机上勾一个任务为 done → 同步回桌面。下次上朝 orchestrator 检测 Notion 上 status 变了 → 更新对应的 .md 文件。

---

## 传输模式下 Notion 不能同步什么

这是最容易被误解的点。

### 能同步

- 📬 Inbox（双向）
- 🧠 Status（桌面→Notion 单向，每次退朝覆写）
- 📝 Working Memory（桌面→Notion，ARCHIVER 写）
- 📋 Todos（双向：桌面新增 → Notion 出现；Notion 勾完成 → 桌面更新）

### 不能同步

- ❌ Decisions — 都在 GitHub / GDrive。Notion 上看不到决策纪要。
- ❌ Journal entries — 同上。
- ❌ Wiki — 同上。
- ❌ 项目 index.md 的完整细节 — 只有 STATUS 里的摘要。
- ❌ 战略地图 — 同上。

**如果你在手机 Notion 上直接创建一个"决策"、写一个"wiki 条目"，系统看不到。**它只认 Inbox / Status / Memory / Todo 四个地方。

这不是 bug，是设计取舍：

- 完整同步 decisions / wiki = 要在 Notion 建 Decisions / Wiki 数据库 + 双向同步机制 = 复杂且容易冲突。
- 保持 Notion 角色最小化 = 4 个组件清晰不混淆 = 符合"Notion 是传输层不是存储层"的定位。

---

## 为什么不推荐完整后端

Notion 作为 primary backend 能用，但不推荐。原因：

### 1. 数据格式锁死

Notion 里所有东西是数据库 + 页面 + property。不是文件。想换工具：

- 导出 Notion → HTML / Markdown / CSV
- 格式转换成 Life OS 的 `.md + YAML front matter`
- Property 映射关系、relation 字段、Subpage 结构都要手工处理

vs GitHub：直接 clone 就是 `.md` 文件，换 Obsidian / VSCode / 任何 markdown 工具都能用。

### 2. 没有 git 历史

Notion 有版本历史但只能看，不能 diff 不能 revert 不能 bisect。GitHub 的 git history 是 Life OS 调试复杂决策、追溯错误、理解演化路径的关键能力。

### 3. 无法 Obsidian 集成

Obsidian 是 Life OS 的官方查看层（见 `obsidian-integration.md`）。Obsidian 打不开 Notion 数据库。

### 4. MCP 性能

Notion MCP 每次调用有网络往返。一次会话可能要读 50 个决策。GitHub / GDrive 的本地文件 I/O 快几个数量级。

Notion 作为 primary 的唯一理由：**你的工作流 95% 都在 Notion，换 GitHub 会让你每天少开 Life OS**。如果不是这种人，选 GitHub 或 GDrive 作为 primary。

---

## 设置 Notion MCP

### Claude.ai（手机）

1. 打开 Claude.ai → Settings → Connected Apps → Notion。
2. 授权。
3. 选择允许访问哪些 Notion 页面（至少包括存 Life OS 组件的那些）。

### Claude Code（桌面）

在 `~/.claude/mcp_servers.json` 或项目级配置里加 Notion MCP server。具体依赖你的 MCP 版本。

### 数据库创建

两个选项：

**A · Life OS 自动创建**

首次 Session Start 选 Notion 时，RETROSPECTIVE 会自动建 4 个组件（传输模式）或 6 个数据库（完整后端）。Notion workspace 根目录下出现 🏛️ Life OS 页面，下面挂所有组件。

**B · 手工创建 + Life OS 自动发现**

你自己在 Notion 先建好组件，命名按规范（📬 Inbox / 🧠 Current Status / 📝 Working Memory / 📋 Todo Board）。Life OS 运行时用 `notion-search` 按名字找数据库 ID，不硬编码。

推荐 A — 少出错。

---

## Step 10a · 退朝时 Notion sync

`pro/CLAUDE.md` Step 10a 定义了 orchestrator 在 ARCHIVER 返回后必须执行的 Notion 同步。

### 为什么 orchestrator 做，不是 ARCHIVER

ARCHIVER 是 subagent，只能用 subagent 能访问的工具。Notion MCP 是环境特定工具（session 级），subagent 拿不到。

所以分工：

- ARCHIVER 在 subagent 里做 Phase 1-3（Archive + Extraction + DREAM）。
- ARCHIVER 返回 Completion Checklist 给 orchestrator。
- Orchestrator 在主 context 里调 Notion MCP 做 Phase 4 的 Notion sync。

### 同步流程

```
ARCHIVER 返回后，orchestrator 执行：

a. 🧠 Current Status page:
   - 读 _meta/STATUS.md 最新内容
   - notion-update-page 覆写对应页面

b. 📋 Todo Board:
   - 本会话新建的 task → notion-create-pages
   - 本会话完成的 task → notion-update-page（status = Done）

c. 📝 Working Memory:
   - 本会话主题 → 找对应的 Notion 页面
   - 存在 → notion-update-page 追加会话总结
   - 不存在 → notion-create-pages 建新页

d. 📬 Inbox:
   - 本会话处理过的 inbox 条目 → notion-update-page（Status = Synced）
```

### 输出

完成后 orchestrator 在主 context 输出这一块：

```
🔄 Notion sync:
- 🧠 Status: [updated / failed: {reason}]
- 📋 Todo: [synced {N} items / failed: {reason}]
- 📝 Working Memory: [written / failed: {reason}]
- 📬 Inbox: [marked synced / no items / failed: {reason}]
```

### 失败处理

- Notion MCP 未连接 → 报告 "⚠️ Notion sync failed — mobile will not see updates"
- 某一项写入失败 → 报告具体哪项，继续其他项
- 绝对不能静默跳过 Notion sync。绝对不能"MCP 没连上就当作完成了"。

这是 HARD RULE。违反 = AUDITOR 会在下一次会话标为 Pattern 违规。
