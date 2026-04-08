# 数据层架构

各 agent 读写数据时参考本文件。

## 双层存储

- **GitHub second-brain（硬盘）**：Source of truth，存一切完整记录和历史
- **Notion（内存）**：轻量工作内存，只存当前活跃话题的上下文，支撑手机端深度讨论
- **CC（丞相/早朝官）是唯一同时碰两边的角色**，负责所有同步

## 数据通道

```
手机：Claude.ai ↔ Notion MCP（聊和存都在这）
桌面：CC ↔ GitHub second-brain + Notion MCP（CC 负责所有同步）
```

## 同步规则

**git commit = Notion 更新，机械绑定，不需要判断。**

只要 second-brain repo 有文件变更，就同步 Notion。纯聊天没有产出文件的讨论不触发同步。

---

## GitHub 目录结构

三套方法论融合：**GTD 驱动行动，PARA 组织结构，Zettelkasten 让知识生长。**

```
second-brain/
│
├── inbox/                          # GTD 入口：未处理的东西先到这里
│
├── projects/                       # PARA·P：有目标有截止的事
│   └── {project}/
│       ├── index.md               # 目标、状态、关联领域
│       ├── tasks/                 # next actions
│       ├── decisions/             # 三省六部奏折
│       ├── notes/                 # 工作笔记
│       └── research/              # 项目专属调研
│
├── areas/                          # PARA·A：持续维护的生活领域
│   └── {area}/
│       ├── index.md               # 方向、关联项目、当前状态
│       ├── goals.md               # 目标
│       └── tasks/                 # 不属于任何项目的领域任务
│
├── zettelkasten/                   # 知识生长
│   ├── fleeting/                  # 碎片想法
│   ├── literature/                # 读了什么、学了什么
│   └── permanent/                 # 自己的洞察，互相链接
│
├── records/                        # 生活数据
│   ├── journal/                   # 日志、早朝简报、复盘、御史台/谏官报告
│   ├── meetings/
│   ├── contacts/
│   ├── finance/
│   └── health/
│
├── gtd/                            # GTD 系统
│   ├── waiting/                   # 等别人
│   ├── someday/                   # 将来也许
│   └── reviews/                   # 周次/月度回顾
│
├── archive/                        # 项目结束搬到这里
│
└── templates/
```

## 领域列表（areas/）

```
areas/
├── career/        # 职业发展
├── product/       # 产品与创业
├── finance/       # 财务管理
├── health/        # 健康
├── family/        # 家庭
├── social/        # 社交关系
├── learning/      # 学习
├── ops/           # 生活运营
├── creation/      # 创作
├── spirit/        # 精神
└── work-project/  # 当前工作项目（示例）
```

---

## 三省六部产出去向

| 产出 | GitHub 路径 |
|------|------------|
| 决策奏折 | `projects/{p}/decisions/` 或 `areas/{a}/decisions/` |
| 行动项 | `projects/{p}/tasks/` 或 `areas/{a}/tasks/` |
| 复盘/御史台/谏官报告 | `records/journal/` |
| 调研分析 | `projects/{p}/research/` 或 `zettelkasten/literature/` |
| 通用洞察 | `zettelkasten/permanent/` |
| 目标 | `areas/{a}/goals.md` |

---

## Notion 内存（4 个组件）

### 📬 信箱（数据库）

消息队列，手机和桌面互相传递信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| 内容 | Title | 一句话或一段要点 |
| 来源 | Select | 手机 / 桌面 |
| 状态 | Select | 待处理 / 已同步 |
| 时间 | Created time | 自动 |

### 🧠 当前状态（页面）

全局快照，CC 每次 session 结束时覆写更新。包含：正在推进的事、最近关键决策、开放问题、本周重点。

### 📝 工作内存（话题页面）

每个活跃话题一个页面。包含：背景、当前阶段、关键决策、技术思路、开放问题、下一步。约 5-10 个活跃话题。不再活跃时归档到 GitHub，从 Notion 删掉。

### 📋 待办看板（数据库）

从 second-brain 的 tasks/ 同步过来的活跃任务清单。手机上能看到、能勾选，CC 下次 session 再同步回 GitHub。

| 字段 | 类型 | 说明 |
|------|------|------|
| 任务 | Title | 任务名称 |
| 项目 | Select | 所属 project |
| 状态 | Select | 待办 / 进行中 / 完成 |
| 优先级 | Select | P0 / P1 / P2 |
| 截止 | Date | 截止日期 |

---

## 早朝官数据操作

### 内务模式（对话开始）

```
1. 读 ~/second-brain/inbox/（未处理项）
2. 读 ~/second-brain/projects/ 和 areas/ 下的 index.md（当前状态）
3. 搜索 second-brain/projects/*/decisions/ 获取相关历史决策
4. 读 user-patterns.md
5. 检查 Notion 📬 信箱（手机端新消息）→ 有就拉进 second-brain/inbox/
6. 平台感知 + 版本检查
```

### 收尾模式（流程结束）

```
1. 奏折 → second-brain/projects/{p}/decisions/ 或 areas/{a}/decisions/
2. 行动项 → second-brain/projects/{p}/tasks/ 或 areas/{a}/tasks/
3. 御史台报告 → second-brain/records/journal/
4. 谏官报告 → second-brain/records/journal/
5. user-patterns.md 更新
6. git add + commit + push（到 second-brain repo）
7. 同步 Notion：更新 🧠 当前状态 + 📝 相关话题工作内存
```

### 复盘模式

```
1. 遍历 second-brain/projects/*/tasks/ 统计完成率
2. 读 second-brain/areas/*/goals.md 获取目标进展
3. 读 second-brain/records/journal/ 最近日志
4. 读 second-brain/gtd/reviews/ 上次复盘记录
5. 度量仪表盘从文件统计
```

## 丞相历史查询

丞相不再自己查数据——早朝官内务模式已经准备好所有上下文。

## 谏官数据拉取

```
1. 读 user-patterns.md
2. 读 second-brain/records/journal/ 最近 3 次谏官报告
3. 读 second-brain/projects/*/decisions/ 最近 5 个决策
4. 遍历 second-brain/projects/*/tasks/ 统计完成率
```

## 降级规则

- second-brain repo 不可达 → 标注"⚠️ second-brain 不可用，本次产出未存档"
- Notion 不可用 → 仅影响手机端同步，不影响核心功能
- 两者都不可用 → 正常运行，产出在对话中展示但不持久化
