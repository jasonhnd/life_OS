# 第二大脑 — 架构与设置

## 核心架构

```
GitHub second-brain（磁盘）= 事实来源，完整记录
Notion（内存）= 轻量工作记忆，移动端活跃话题
CC（丞相/早朝官）= 唯一同时接触两侧的角色
```

### 数据通道

```
移动端：Claude.ai ↔ Notion MCP
桌面端：CC ↔ GitHub second-brain + Notion MCP
```

### 同步规则

**git commit = Notion 更新，机械绑定。** 文件变更触发同步；纯聊天不触发。

---

## GitHub second-brain 目录

```
second-brain/
│
├── inbox/                    # 📥 未处理（捕获、素材、笔记、原始研究）
│
├── SOUL.md                   # 🧬 身份 — 价值观、原则、行为模式
├── user-patterns.md          # 📊 跨会话观察到的行为模式
│
├── _meta/                    # 🔧 系统元数据
│   ├── STATUS.md             # 全局状态快照（编译生成）
│   ├── STRATEGIC-MAP.md      # 🗺️ 战略地图（从项目 strategic 字段编译生成 — v1.5.0）
│   ├── strategic-lines.md    # 战略线定义（用户定义 — v1.5.0）
│   ├── MAP.md                # 知识地图
│   ├── outbox/               # 📤 待同步的外部输出
│   ├── decisions/            # 跨领域重大决策
│   ├── journal/              # 早朝简报、御史台/谏官报告
│   ├── extraction-rules.md
│   ├── extraction-log.md
│   ├── lint-rules.md
│   ├── lint-state.md
│   ├── lint-reports/
│   └── roles/                # 系统角色定义
│
├── projects/{name}/          # 🎯 有终点的事
│   ├── index.md              # 目标、状态、关联领域
│   ├── tasks/                # 下一步行动
│   ├── decisions/            # 项目级奏折
│   ├── research/             # 项目级研究
│   └── journal/              # 项目级日志
│
├── areas/{name}/             # 🌊 持续的生活领域
│   ├── index.md              # 方向、关联项目
│   ├── goals.md              # 目标
│   ├── tasks/                # 领域任务
│   └── notes/                # 领域笔记
│
├── wiki/                     # 📚 知识存档 — 可复用的结论（从 DREAM 中生长）
│   ├── INDEX.md              # Wiki 索引
│   └── {domain}/{topic}.md   # 按领域组织的知识页面
│
├── archive/                  # 🗄️ 已完成项目归档
│
└── templates/                # 📋 模板
```

## 领域列表 (areas/)

```
career/    product/    finance/    health/    family/
social/    learning/   ops/        creation/  spirit/
```

---

## 关键概念

### _meta/ — 系统元数据

关于大脑的大脑。包含：
- **STATUS.md**：跨所有项目和领域的全局快照。由早朝官在会话结束时更新。
- **MAP.md**：跨 wiki/ 的知识地图，连接概念。
- **decisions/**：不属于任何单一项目的跨领域决策。
- **journal/**：系统级日志——早朝简报、御史台和谏官报告。
- **roles/**：质量控制的系统角色定义（御史、史官、审查者）。
- **lint-***：第二大脑自身的质量检查规则和报告。
- **extraction-***：从原始素材中提取洞察的规则和日志。

### projects/ — 有终点的事

每个项目有自己的自包含世界：任务、决策、研究和日志。项目完成后，整个文件夹移至 archive/。提取到 wiki/ 的知识留下并持续增长。

### areas/ — 持续的生活领域

没有终点，没有截止日期。每个领域有目标、任务和笔记。项目可以引用领域；领域可以生成项目。

### wiki/ — 知识存档

取代之前的 zettelkasten 结构。按领域组织的互链笔记 wiki，以 INDEX.md 为入口。不绑定任何项目——项目会结束，知识永存。从 DREAM 中生长：起居郎从会话分析中提取可复用的结论，写入 wiki 页面。

### SOUL.md — 身份档案

记录用户的核心价值观、原则、决策倾向和行为模式。谏官和翰林院参考此文件提供个性化建议。

### DREAM — 知识提取

起居郎的会话结束流程：回顾会话，提取可复用的洞察，以永久知识条目的形式写入 wiki/。这是临时分析如何转化为持久知识的方式。

---

## 三省六部输出目标

| 输出 | GitHub 路径 |
|--------|------------|
| 决策奏折（项目级） | `projects/{p}/decisions/` |
| 决策奏折（跨领域） | `_meta/decisions/` |
| 行动项 | `projects/{p}/tasks/` 或 `areas/{a}/tasks/` |
| 早朝简报 | `_meta/journal/` |
| 御史台/谏官报告 | `_meta/journal/` |
| 研究 | `projects/{p}/research/` |
| 跨领域知识 | `wiki/` |
| 目标 | `areas/{a}/goals.md` |
| 会话日志（会话结束） | `_meta/journal/`（由起居郎写入） |
| Wiki 提取（会话结束） | `wiki/{domain}/{topic}.md`（由起居郎写入） |
| 全局状态 | `_meta/STATUS.md` |

---

## Notion 记忆（4 个组件）

### 📬 Inbox（数据库）

移动端和桌面端之间的消息队列。字段：Content / Source (Mobile/Desktop) / Status (Pending/Synced) / Time。

### 🧠 当前状态（页面）

镜像 `_meta/STATUS.md`。由 CC 在会话结束时覆盖。

### 📝 工作记忆（主题页面）

每个活跃话题一页（约 5-10 个）。不再活跃时，归档到 GitHub 并从 Notion 删除。

### 📋 待办看板（数据库）

从 projects/*/tasks/ 和 areas/*/tasks/ 同步的活跃任务。移动端可查看和勾选。

---

## 多仓库工作流

- **项目代码**（EIP、life_OS 等）→ 各自独立仓库
- **关于项目的思考**（决策、笔记、任务）→ second-brain 仓库

同一个 CC 对话连接两个目录。`/save` 命令：写入文件 → cd ~/second-brain → git commit/push → 返回项目目录。

---

## 没有数据层时

如果你没有设置第二大脑，所有功能正常工作——只是没有持久化和跨会话记忆。
