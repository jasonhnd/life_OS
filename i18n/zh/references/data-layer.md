# 数据层架构

所有代理在读写数据时参考此文件。

## 设计原则

1. **全覆盖**：第二大脑覆盖生活、家庭、购物、爱好、本职工作、副业——一切
2. **LLM 无关**：不绑定任何特定模型。所有"智能"编码在 markdown 文件中，而非模型权重中
3. **无 AI 也能工作**：在 Obsidian 中打开 markdown 文件就能读、写、导航。LLM 是加速器，不是前提
4. **Markdown 是唯一事实来源**：所有知识最终落地为 .md 文件。Notion 是传输层（收件箱），不是存储层
5. **Obsidian 是查看层**：将 GitHub 仓库克隆到本地，在 Obsidian 中打开。Wikilinks 和标准 markdown 链接实现自动知识图谱可视化

## 模型无关

**CLAUDE.md 是唯一绑定到特定模型的文件。** 其他一切——提取规则、lint 规则、角色定义、知识网络、目录结构——都是纯 markdown，任何模型都可读取。切换模型只需更新 CLAUDE.md 引用。

---

## 认知管线

信息流经五个阶段，每个阶段对应一种方法论：

```
感知 → 捕获 → 关联 → 判断 → 沉淀 → 涌现
   ↑         ↑          ↑          ↑        ↑         ↑
 手机      GTD      Zettelkasten  三省六部    PARA    Lint/御史台
 体验      inbox/    wiki/      桌面端       dirs    健康检查
```

### 阶段详情

**感知 → 捕获（GTD）**：手机端零摩擦捕获。用户说了什么，手机 AI 存入 inbox。此阶段不分类——inbox 就是 GTD 收集篮。

**捕获 → 关联（Zettelkasten）**：桌面端 CC 从 inbox 拉取，第一步是建立关联——哪些现有 wiki 文章相关？提到了哪些实体？实体间有什么关系？用 wikilinks 建立反向链接网络。

**关联 → 判断（三省）**：不是所有信息都需要决策。只有涉及重大资源分配、多选项权衡或难以逆转的后果时，才激活三省决策模式。

**判断 → 沉淀（PARA）**：决策结论按 PARA 存储——Projects（有终点的事）、Areas（持续的领域）、Wiki（跨领域知识）、Archive（已完成的）。

**沉淀 → 涌现（Lint/御史台）**：当知识网络密度达到临界质量，涌现自动发生。Lint 扫描发现跨领域关联、建议新概念文章、发现矛盾。

### 手机端与桌面端分工

手机端只处理感知和捕获（偶尔轻量关联如网页搜索）。桌面端处理关联、判断、沉淀和涌现——所有重活。手机端可以阅读管线输出（STATUS.md、归档），但只在捕获阶段写入。

---

## GitHub 目录结构

```
second-brain/
│
├── inbox/                             # 📥 未处理（手机端捕获、素材、读书笔记、原始研究）
│
├── _meta/                             # 🔧 系统元数据
│   ├── STATUS.md                      # 全局状态仪表盘（镜像至 Notion）
│   ├── MAP.md                         # 知识地图（所有领域入口点）
│   ├── decisions/                     # 跨领域重大决策
│   ├── journal/                       # 早朝简报、御史台/谏官报告
│   ├── extraction-rules.md            # 知识提取规则（用户训练）
│   ├── extraction-log.md              # 提取历史
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
├── areas/                             # 🌊 持续的生活领域（PARA-A）
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

## 知识分类（7 种类型）

| 类型 | 存储 | 示例 |
|------|---------|---------|
| 实体知识 | wiki/ | 某公司停产了某产品线 |
| 经验知识 | wiki/（标记主观） | 材料 X 手感比材料 Y 好 |
| 关系知识 | wiki/（反向链接） | 甲是通过活动乙认识的 |
| 决策记录 | areas/ 或 projects/ | 项目从工具 A 切换到工具 B |
| 待办/意向 | tasks/ | 下次试试产品 X |
| 灵感/直觉 | inbox/（临时） | X 和 Y 之间有机会 |
| 流程知识 | wiki/ | 在日本注册公司的步骤 |

这 7 种类型可能根据实际使用情况扩展。

---

## 知识提取：四步训练

1. **用户定夺**：桌面端 CC 生成"提取提案"，用户确认/修改
2. **积累样本**：记录到 `_meta/extraction-log.md`
3. **LLM 归纳规则**：从日志中归纳偏好，写入 `_meta/extraction-rules.md`（纯 markdown，模型无关）
4. **定期纠偏**：用户每月审查，报告误分类，CC 更新规则

核心：学习的"载体"是 markdown 文件，不是模型权重。切换模型只需读取这些文件。

---

## 御史台：两种运行模式

御史台在三省体系中以两种模式运行：

### 模式 1：决策审查（已有）

每次三省六部流程后，审查公务工作质量。已在 `pro/agents/yushitai.md` 中定义。

### 模式 2：巡检（新增）

空闲时，各部巡检自己的辖区。定义在 `_meta/roles/censor.md`。

#### 触发级别

| 触发条件 | 时机 | 深度 |
|---------|------|-------|
| **启动巡检** | 每次桌面端 CC 会话开始时，如 `lint-state.md` 显示距上次运行 >4 小时 | 轻量级，3 行简报 |
| **同步后巡检** | inbox 同步完成后 | 检查新内容与 wiki 一致性、需要 wiki 文章的新实体、STATUS.md 更新 |
| **深度巡检** | 每周或手动触发 | 六部全面巡查 |

#### 六部巡查职责

| 部门 | 辖区 | 检查内容 |
|----------|-------------|--------|
| 户部 | areas/finance/ | 投资策略过时、财务数字需更新 |
| 兵部 | projects/ | 项目活跃度、TODO 完成率、资源冲突 |
| 礼部 | wiki/（人际关系） | 未兑现的社交承诺、需记录的新联系人 |
| 工部 | wiki/ + _meta/ | 孤立文件、断裂链接、规则有效性 |
| 吏部 | areas/career/ | 职业方向与行动是否一致 |
| 刑部 | 跨领域 | 项目间策略矛盾、缺少风险评估的决策 |

#### 问题分级

| 级别 | 操作 | 示例 |
|-------|--------|---------|
| **自动修复** | 御史台直接处理 | 缺失索引条目、缺失反向链接、格式问题 |
| **建议** | 发送到 inbox 给用户 | 数据不一致、项目可能停滞、wiki 建议 |
| **升级** | 激活三省决策模式 | 财务矛盾 >¥1M、多项目策略冲突、人际风险 |

#### 实现

- 角色定义存储在 `_meta/roles/censor.md`，CLAUDE.md 仅引用它
- 巡检状态持久化在 `_meta/lint-state.md`（解决 LLM 无跨会话记忆的问题）
- 巡检报告存储在 `_meta/lint-reports/`，摘要也发送到 inbox
- 切换模型：角色文件不变，只有 CLAUDE.md 引用变化

---

## 可扩展常驻角色

| 角色 | 文件 | 功能 |
|------|------|----------|
| 御史台 | `_meta/roles/censor.md` | 巡检（必选） |
| 史官 | `_meta/roles/historian.md` | 会话结束时自动记录每日工作（可选） |
| 门下省值班 | `_meta/roles/reviewer.md` | 写入时审查内容质量（可选） |

---

## 三省输出目标

所有输出使用 `references/data-model.md` 中的标准操作。用户所选后端的适配器将这些翻译为平台特定的调用。

| 输出 | 标准操作 |
|--------|-------------------|
| 决策奏折 | Save Decision |
| 行动项 | Save Task |
| 早朝/御史台/谏官报告 | Save JournalEntry |
| 巡检报告 | Save JournalEntry (type: inspection) |
| 研究/知识 | Save WikiNote |
| 目标 | Update Area (goals 字段) |
| 全局状态 | 通过适配器特定的 STATUS 机制更新 |

---

## 存储后端

Life OS 支持三种存储后端。用户选择 1、2 或全部 3 个。

| 后端 | 最适用于 | 适配器 | 格式 |
|---------|----------|---------|--------|
| GitHub | 技术用户、Claude Code | `references/adapter-github.md` | .md + front matter |
| Google Drive | 普通用户、零设置 | `references/adapter-gdrive.md` | .md + front matter |
| Notion | Notion 用户 | `references/adapter-notion.md` | Notion 数据库 |

标准数据类型和操作：`references/data-model.md`

多后端规则（同步、冲突、删除、故障处理）：`references/data-model.md`

---

## 早朝官数据操作

所有操作使用标准接口。根据用户配置的后端调整调用。

### 管家模式（会话开始）

```
1. 读取 _meta/config.md → 获取后端列表和上次同步时间戳
2. 多后端同步（如配置了多个后端）：
   - 查询每个同步后端自 last_sync_time 以来的变更
   - 比较、解决冲突（见 data-model.md）
   - 将变更应用到主后端
   - 推送到同步后端
3. 读取 inbox（未处理项目）— 通过主后端
4. 读取 _meta/STATUS.md（全局状态）
5. 读取 _meta/lint-state.md（检查是否需要巡检：距上次运行 >4 小时）
6. ReadProjectContext（绑定项目）— 任务、决策、日志
7. 读取 user-patterns.md
8. 全局概览：List Project + List Area（仅标题 + 状态）
9. 如 lint-state.md 显示 >4 小时 → 触发轻量级御史台巡检
10. 平台感知 + 版本检查
```

### 收尾模式（流程结束）

```
1. Save Decision / Save Task / Save JournalEntry → 通过主后端
2. 更新 _meta/STATUS.md
3. 更新 _meta/lint-state.md
4. 更新 user-patterns.md
5. 提交（如 GitHub 后端：git add + commit + push）
6. 同步到所有同步后端（写入输出 + STATUS）
7. 任何后端失败 → 记录到 _meta/sync-log.md，不阻塞
8. 更新 _meta/config.md 中的 last_sync_time
```

### 审查模式

```
1. 读取 _meta/STATUS.md 获取全局状态
2. List Task（所有项目）→ 计算完成率
3. List Area → 读取目标
4. List JournalEntry（近期）→ 日志和巡检报告
5. 从结果计算指标仪表盘
```

## 谏官数据检索

```
1. 读取 user-patterns.md
2. List JournalEntry (type: remonstrator, limit: 3) → 最近 3 份报告
3. List Decision (limit: 5) → 近期决策
4. List Task → 计算完成率
```

## 降级规则

- 主后端不可达 → 标注"⚠️ 主后端不可用"
- 同步后端不可达 → 标注 ⚠️，记录，下次会话重试
- 所有后端不可用 → 正常运行，输出在对话中显示但不持久化
