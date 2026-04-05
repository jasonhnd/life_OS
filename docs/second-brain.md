# 第二大脑 — 架构与搭建

## 核心架构

```
GitHub second-brain（硬盘）= Source of truth，完整记录
Notion（内存）= 轻量工作内存，手机端活跃话题
CC（丞相/早朝官）= 唯一同时碰两边的角色
```

### 数据通道

```
手机：Claude.ai ↔ Notion MCP
桌面：CC ↔ GitHub second-brain + Notion MCP
```

### 同步规则

**git commit = Notion 更新，机械绑定。** 有文件变更就同步，纯聊天不触发。

---

## GitHub second-brain 目录

三套方法论融合：**GTD 驱动行动，PARA 组织结构，Zettelkasten 让知识生长。**

```
second-brain/
├── inbox/                    # GTD 入口：未处理的先到这里
├── projects/{project}/       # PARA·P：有目标有截止的事
│   ├── index.md             # 目标、状态、关联领域
│   ├── tasks/               # next actions
│   ├── decisions/           # 三省六部奏折
│   ├── notes/               # 工作笔记
│   └── research/            # 项目专属调研
├── areas/{area}/             # PARA·A：持续维护的生活领域
│   ├── index.md             # 方向、关联项目
│   ├── goals.md             # 目标
│   └── tasks/               # 不属于项目的领域任务
├── zettelkasten/             # 知识生长
│   ├── fleeting/            # 碎片想法
│   ├── literature/          # 输入（读了什么）
│   └── permanent/           # 输出（自己的洞察，互相链接）
├── records/                  # 生活数据
│   ├── journal/             # 日志、早朝简报、御史台/谏官报告
│   ├── meetings/
│   ├── contacts/
│   ├── finance/
│   └── health/
├── gtd/                      # GTD 系统
│   ├── waiting/             # 等别人
│   ├── someday/             # 将来也许
│   └── reviews/             # 复盘记录
├── archive/                  # 项目结束搬到这里
└── templates/
```

## 领域列表（areas/）

```
career/    product/    finance/    health/    family/
social/    learning/   ops/        creation/  spirit/    ndfg/
```

---

## GTD 流转

```
脑子里想到什么 → inbox/
  ├── 有行动，属于项目 → projects/{p}/tasks/
  ├── 有行动，属于领域 → areas/{a}/tasks/
  ├── 等别人 → gtd/waiting/
  ├── 以后再说 → gtd/someday/
  ├── 是知识不是任务 → zettelkasten/
  └── 没用 → 删掉
```

## Zettelkasten 生长

```
碎片想法 → zettelkasten/fleeting/
读了篇文章 → zettelkasten/literature/
  → 提炼出洞察 → zettelkasten/permanent/（链接已有笔记）
```

## 项目→知识桥梁

项目归档时工作笔记跟着走，永续笔记留在 zettelkasten 继续生长。

---

## Notion 内存（3 个组件）

### 📬 信箱（数据库）

手机和桌面互传消息的队列。字段：内容 / 来源（手机/桌面）/ 状态（待处理/已同步）/ 时间。

### 🧠 当前状态（页面）

全局快照，CC 每次 session 结束覆写。包含：正在推进的事、最近决策、开放问题、本周重点。

### 📝 工作内存（话题页面）

每个活跃话题一个页面（约 5-10 个）。包含：背景、当前阶段、关键决策、技术思路、开放问题、下一步。不再活跃时归档到 GitHub，从 Notion 删掉。

---

## 多 Repo 工作方式

- **项目代码**（EIP、life_OS 等）→ 各自独立 repo
- **关于项目的思考**（决策、笔记、任务）→ second-brain repo

同一个 CC 对话中连接两个目录。`/save` 命令：写文件 → cd ~/second-brain → git commit/push → 回到项目。

---

## 三省六部产出去向

| 产出 | GitHub 路径 |
|------|------------|
| 决策奏折 | `projects/{p}/decisions/` |
| 行动项 | `projects/{p}/tasks/` |
| 复盘/御史台/谏官 | `records/journal/` |
| 调研 | `zettelkasten/literature/` |
| 通用洞察 | `zettelkasten/permanent/` |
| 目标 | `areas/{a}/goals.md` |

---

## 不连接数据层

不建 second-brain 时所有功能照常工作，只是没有持久化和跨会话记忆。
