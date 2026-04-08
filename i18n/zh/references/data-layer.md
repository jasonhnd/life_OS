# 数据层架构

所有角色在读写数据时参考本文件。

## 设计原则

1. **全覆盖**：第二大脑覆盖生活、家庭、购物、兴趣、本职工作、副业——一切
2. **模型无关**：不绑定任何特定模型。所有"智能"编码在 markdown 文件中，而非模型权重
3. **无 AI 也能用**：在 Obsidian 中打开 markdown 文件就能读、写、导航。LLM 是加速器，不是前提条件
4. **Markdown 是唯一事实来源**：所有知识最终以 .md 文件落地。Notion 是传输层（收件箱），不是存储层
5. **Obsidian 是查看层**：将 GitHub 仓库克隆到本地，用 Obsidian 打开。Wikilinks 和标准 markdown 链接实现自动知识图谱可视化

## 模型无关

**CLAUDE.md 是唯一绑定特定模型的文件。** 其他一切——提取规则、巡检规则、角色定义、知识网络、目录结构——都是纯 markdown，任何模型都可读取。切换模型只需更新 CLAUDE.md 的引用。

---

## 认知管线

信息经过五个阶段流转，每个阶段对应一种方法论：

```
感知 → 捕获 → 关联 → 判断 → 沉淀 → 涌现
  ↑       ↑       ↑       ↑       ↑       ↑
手机    GTD   Zettelkasten  三省六部  PARA   巡检/御史台
体验    inbox/   wiki/     桌面端    目录    健康检查
```

### 阶段详解

**感知 → 捕获（GTD）**：在移动端零摩擦捕获。用户说了什么，手机 AI 存入 inbox。此阶段不做分类——inbox 就是 GTD 的收集篮。

**捕获 → 关联（Zettelkasten）**：桌面端 CC 从 inbox 拉取内容，第一步是建立关联——有哪些已有的 wiki 文章相关？提到了哪些实体？实体之间有什么关系？用 wikilinks 构建反向链接网络。

**关联 → 判断（三省）**：并非所有信息都需要决策。只有涉及重大资源分配、多选项权衡、难以逆转的后果时，才激活三省决策模式。

**判断 → 沉淀（PARA）**：决策结论按 PARA 存储——Projects（有终点的事）、Areas（持续领域）、Wiki（跨领域知识）、Archive（已完成的归档）。

**沉淀 → 涌现（巡检/御史台）**：当知识网络密度达到临界质量时，涌现自然发生。巡检扫描发现跨领域关联，建议新概念文章，发现矛盾。

### 移动端 vs 桌面端分工

移动端只处理感知和捕获（偶尔进行轻量级关联如网页搜索）。桌面端处理关联、判断、沉淀和涌现——所有重活。移动端可以读取管线输出（STATUS.md、归档），但只在捕获阶段写入。

---

## GitHub 目录结构

```
second-brain/
│
├── inbox/                             # 📥 未处理（移动端捕获、素材、读书笔记、原始研究）
│
├── _meta/                             # 🔧 系统元数据
│   ├── STATUS.md                      # 全局状态仪表盘（镜像到 Notion）
│   ├── MAP.md                         # 知识地图（所有领域入口点）
│   ├── decisions/                     # 跨领域重大决策
│   ├── journal/                       # 早朝简报、御史台/谏官报告
│   ├── extraction-rules.md            # 知识提取规则（由用户训练）
│   ├── extraction-log.md              # 提取历史记录
│   ├── lint-rules.md                  # 巡检规则
│   ├── lint-state.md                  # 巡检状态（上次运行时间等）
│   ├── lint-reports/                  # 历史巡检报告
│   └── roles/                         # 常驻角色定义
│       ├── censor.md                  # 御史台（巡检模式）
│       ├── historian.md               # 史官（可选：自动记录每日工作）
│       └── reviewer.md               # 门下省值班（可选：写入时审查内容质量）
│
├── projects/                          # 🎯 有终点的事（PARA-P）
│   └── {name}/
│       ├── index.md
│       ├── tasks/
│       ├── decisions/
│       ├── research/
│       └── journal/
│
├── areas/                             # 🌊 持续生活领域（PARA-A）
│   └── {name}/
│       ├── index.md
│       ├── goals.md
│       ├── tasks/
│       └── notes/
│
├── wiki/                              # 📚 跨领域知识网络（Zettelkasten + wikilinks）
│
├── archive/                           # 🗄️ 已完成项目归档（PARA-Archive）
│
└── templates/
```

## 知识分类（7 类）

| 类型 | 存储位置 | 示例 |
|------|---------|------|
| 实体知识 | wiki/ | 某公司停产了某产品线 |
| 经验知识 | wiki/（标记主观） | 材料 X 比材料 Y 手感好 |
| 关系知识 | wiki/（反向链接） | A 通过事件 B 认识 |
| 决策记录 | areas/ 或 projects/ | 项目从工具 A 换到工具 B |
| 待办/意向 | tasks/ | 下次试试产品 X |
| 灵感/直觉 | inbox/（临时） | X 和 Y 之间有机会 |
| 流程知识 | wiki/ | 在日本注册公司的步骤 |

这 7 类可能根据实际使用情况随时间扩展。

---

## 知识提取：四步训练法

1. **用户决定**：桌面端 CC 生成"提取提案"，用户确认/修改
2. **积累样本**：记录到 `_meta/extraction-log.md`
3. **LLM 归纳规则**：从日志中归纳偏好，写入 `_meta/extraction-rules.md`（纯 markdown，模型无关）
4. **定期纠偏**：用户每月审查，反馈误分类，CC 更新规则

核心：这里的"学习"载体是 markdown 文件，而非模型权重。切换模型只需读取这些文件。

---

## 御史台：两种运行模式

御史台在三省体系中以两种模式运行：

### 模式一：决策审查（已有）

每次三省工作流结束后，审查官员工作质量。已在 `pro/agents/yushitai.md` 中定义。

### 模式二：巡检（新增）

空闲时，各部巡查自己的管辖范围。在 `_meta/roles/censor.md` 中定义。

#### 触发级别

| 触发条件 | 时机 | 深度 |
|---------|------|------|
| **启动巡检** | 每次桌面端 CC 会话开始时，若 `lint-state.md` 显示距上次运行 >4 小时 | 轻量级，3 行简报 |
| **同步后巡检** | inbox 同步完成后 | 检查新内容与 wiki 一致性、需要新建 wiki 文章的实体、STATUS.md 更新 |
| **深度巡检** | 每周或手动触发 | 六部全面巡查 |

#### 六部巡查职责

| 部门 | 管辖范围 | 检查内容 |
|------|---------|---------|
| 户部 | areas/finance/ | 投资策略是否过时、财务数据是否需要更新 |
| 兵部 | projects/ | 项目活跃度、TODO 完成率、资源冲突 |
| 礼部 | wiki/（人际关系） | 未兑现的社交承诺、需要记录的新联系人 |
| 工部 | wiki/ + _meta/ | 孤立文件、断链、规则有效性 |
| 吏部 | areas/career/ | 职业方向与实际行动是否一致 |
| 刑部 | 跨领域 | 项目间策略矛盾、决策缺少风险评估 |

#### 问题分级

| 级别 | 处理方式 | 示例 |
|------|---------|------|
| **自动修复** | 御史台直接处理 | 缺失索引条目、缺失反向链接、格式问题 |
| **建议** | 发送到 inbox 供用户处理 | 数据不一致、项目可能停滞、wiki 建议 |
| **上报** | 激活三省决策模式 | 财务矛盾 >¥1M、多项目策略冲突、人际关系风险 |

#### 实现方式

- 角色定义存储在 `_meta/roles/censor.md` 中，CLAUDE.md 只引用它
- 巡检状态持久化在 `_meta/lint-state.md` 中（解决 LLM 缺乏跨会话记忆的问题）
- 巡检报告存储在 `_meta/lint-reports/` 中，摘要也发送到 inbox
- 切换模型：角色文件不变，只需更改 CLAUDE.md 的引用

---

## 可扩展常驻角色

| 角色 | 文件 | 功能 |
|------|------|------|
| 御史台 | `_meta/roles/censor.md` | 巡检（必选） |
| 史官 | `_meta/roles/historian.md` | 会话结束时自动记录每日工作（可选） |
| 门下省值班 | `_meta/roles/reviewer.md` | 写入时审查内容质量（可选） |

---

## 三省输出去向

| 输出 | GitHub 路径 |
|------|------------|
| 决策奏折（项目专属） | `projects/{p}/decisions/` |
| 决策奏折（跨领域） | `_meta/decisions/` |
| 行动项（项目） | `projects/{p}/tasks/` |
| 行动项（领域） | `areas/{a}/tasks/` |
| 早朝简报 | `_meta/journal/` |
| 御史台 / 谏官报告 | `_meta/journal/` |
| 巡检报告 | `_meta/lint-reports/` |
| 项目研究 | `projects/{p}/research/` |
| 跨领域知识 | `wiki/` |
| 目标 | `areas/{a}/goals.md` |
| 全局状态快照 | `_meta/STATUS.md` |

---

## Notion（传输层，3 个组件）

Notion 仅作为传输层，不是存储层。

### 📬 收件箱（数据库）

在移动端和桌面端之间传递信息的消息队列。

| 字段 | 类型 | 描述 |
|------|------|------|
| Content | Title | 一句话或关键要点 |
| Source | Select | Mobile / Desktop |
| Status | Select | Pending / Synced |
| Time | Created time | 自动 |

### 🧠 状态仪表盘（页面）

`_meta/STATUS.md` 的镜像。每次会话结束时由 CC 覆盖写入。

### 🗄️ 归档

移动端的只读归档访问。

---

## 早朝官数据操作

### 家务模式（对话开始时）

```
1. 读取 ~/second-brain/inbox/（未处理条目）
2. 读取 ~/second-brain/_meta/STATUS.md（全局状态）
3. 读取 ~/second-brain/_meta/lint-state.md（检查是否需要巡检：距上次运行 >4 小时）
4. 读取 ~/second-brain/projects/{bound}/index.md（绑定项目状态）
5. 读取 ~/second-brain/projects/{bound}/decisions/（历史决策）
6. 读取 ~/second-brain/projects/{bound}/tasks/（活跃任务）
7. 读取 user-patterns.md
8. 全局概览：列出所有 projects/ 和 areas/ 的 index.md 标题 + 状态
9. 检查 Notion 📬 收件箱（来自移动端的新消息）→ 拉入 second-brain/inbox/
10. 若 lint-state.md 显示距上次运行 >4 小时 → 触发御史台轻量巡检
11. 平台检测 + 版本检查
```

### 收尾模式（流程结束时）

```
1. 奏折 → projects/{p}/decisions/ 或 _meta/decisions/（跨领域）
2. 行动项 → projects/{p}/tasks/ 或 areas/{a}/tasks/
3. 御史台报告 → _meta/journal/
4. 谏官报告 → _meta/journal/
5. 更新 _meta/STATUS.md（全局状态快照）
6. 更新 _meta/lint-state.md（上次巡检时间）
7. 更新 user-patterns.md
8. git add + commit + push（到 second-brain 仓库）
9. 同步 Notion：更新 🧠 状态仪表盘
```

### 审视模式

```
1. 读取 _meta/STATUS.md 获取全局状态
2. 遍历 projects/*/tasks/ 计算完成率
3. 读取 areas/*/goals.md 获取目标进度
4. 读取 _meta/journal/ 近期日志
5. 读取 _meta/lint-reports/ 近期巡检报告
6. 从文件计算指标仪表盘
```

## 谏官数据检索

```
1. 读取 user-patterns.md
2. 读取 _meta/journal/ 最近 3 份谏官报告
3. 读取 projects/*/decisions/ + _meta/decisions/ 最近 5 条决策
4. 遍历 projects/*/tasks/ 计算完成率
```

## 降级规则

- second-brain 仓库不可达 → 标注"⚠️ second-brain 不可用"
- Notion 不可用 → 只影响移动端同步，不影响核心功能
- 两者均不可用 → 正常运行，输出显示在对话中但不持久化
