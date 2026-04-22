# 数据层架构（Data Layer）

所有 agent 在读写数据时都参考本文件。

## 设计原则

1. **全覆盖**：第二大脑覆盖生活、家庭、购物、爱好、本职工作、副业——所有领域
2. **不绑定任何 LLM**：所有"智能"都编码在 markdown 文件里，不在模型权重中
3. **无 AI 也能用**：用 Obsidian 打开 markdown 文件就能读写和导航。LLM 是加速器，不是前提
4. **Markdown 是唯一真相源**：所有知识最终落在 .md 文件里。Notion 是传输层（inbox），不是存储层
5. **Obsidian 是查看层**：把 GitHub repo 克隆到本地、用 Obsidian 打开。Wikilinks 和标准 markdown 链接使知识图自动可视化

## 模型独立性

**CLAUDE.md 是唯一绑定特定模型的文件**。其他一切——提取规则、lint 规则、角色定义、知识网络、目录结构——都是纯 markdown，任何模型都能读。切换模型只需要更新 CLAUDE.md 的引用。

---

## 认知管道

信息经过六个阶段，每个阶段对应一种方法论：

```
感知 → 捕获 → 判断 → 沉淀 → 关联 → 战略化 → 涌现
 ↑      ↑     ↑     ↓   ↘      ↑        ↑        ↑
 手机  GTD   3D6M  SOUL  Wiki  Prime+Wiki 战略     DREAM REM
 体验  inbox/ 桌面 （人） （知识）INDEX 匹配 MAP    跨域关联
```

### 阶段详解

**感知 → 捕获（GTD）**：手机零摩擦捕获。用户说一句话，手机 AI 存到 inbox。此阶段不分类——inbox 是 GTD 的收集篮。

**捕获 → 判断（Draft-Review-Execute 循环）**：桌面 CC 从 inbox 拉取。不是所有信息都需要决策。只有涉及重大资源分配、多选项权衡、难以逆转的后果时，才激活 Draft-Review-Execute 决策模式。

**判断 → 沉淀（SOUL + Wiki）**：决策产生的结论沉淀到两个池——SOUL（关于人：价值观、人格、行为模式）和 Wiki（关于世界：可复用知识、既定结论）。两者都是**在严格条件下自动写入**（v1.6.2）：ARCHIVER 和 DREAM 自动写入通过 6 条 wiki 标准 + 隐私过滤器（wiki）或 SOUL 标准 + 低初始置信度（SOUL）的条目。用户事后介入——删除文件退役、说 "undo recent wiki/SOUL" 回滚。**快照**：archiver 在每次会话结束时捕获 SOUL 状态，RETROSPECTIVE 读取以计算趋势。

**沉淀 → 关联（ROUTER + Wiki INDEX）**：ROUTER 在会话开始时读取 wiki/INDEX.md。新请求到达时自动匹配既有知识——"我们已经知道这个领域的 X"。把积累的知识变成主动的上下文。

**关联 → 战略化（战略地图）**：ROUTER 在会话开始时读 `_meta/STRATEGIC-MAP.md`。当请求涉及有战略关系的项目时，系统自动浮现下游依赖、瓶颈状态、决策传播警告。把每项目分析变成战略线感知的分析。见 `references/strategic-map-spec.md`。

**战略化 → 涌现（DREAM REM）**：当 wiki 条目和战略关系积累后，DREAM 的 REM 阶段用流动图作为脚手架发现跨域连接——检查 SOUL × 策略对齐、wiki × 流动完整性、行为模式 × 战略优先级一致性。知识和关系沉淀越多，涌现越多。AUDITOR 巡检还会检测 wiki 矛盾、知识缺口和项目间的策略冲突。

### 手机 vs 桌面分工

手机只负责感知与捕获（偶尔轻量关联如 web search）。桌面负责关联、判断、沉淀、涌现——所有重活。手机可以读管道输出（STATUS.md、归档），但只在捕获阶段写。

---

## GitHub 目录结构

```
second-brain/
│
├── SOUL.md                            # 🔮 用户人格档案（价值观、信念、身份——从零生长）
├── user-patterns.md                   # 📊 行为模式（你做什么——ADVISOR 维护）
│
├── inbox/                             # 📥 未处理（手机捕获、素材、读书笔记、原始研究）
│
├── _meta/                             # 🔧 系统元数据
│   ├── STATUS.md                      # 全局状态仪表盘（从 index.md 文件编译）
│   ├── STRATEGIC-MAP.md               # 战略地图（从项目战略字段编译）
│   ├── strategic-lines.md             # 战略线定义（用户定义）
│   ├── MAP.md                         # 知识地图（所有 area 入口）
│   ├── decisions/                     # 跨域重大决策
│   ├── journal/                       # RETROSPECTIVE 简报、AUDITOR/ADVISOR 报告、DREAM 报告
│   ├── outbox/                        # 📮 会话输出暂存区（每个会话一个子目录）
│   │   └── {session_id}/              # 每个会话在 adjourn 时写入，在下次 start court 合并
│   ├── snapshots/                     # 📸 状态快照用于趋势计算
│   │   └── soul/                      # 每次会话的 SOUL 快照（YYYY-MM-DD-HHMM.md）
│   │       └── _archive/              # 超过 30 天的快照
│   ├── extraction-rules.md            # 知识提取规则（用户训练）
│   ├── extraction-log.md              # 提取历史
│   ├── lint-rules.md                  # 巡检规则
│   ├── lint-state.md                  # 巡检状态（上次运行时间等）
│   ├── lint-reports/                  # 历史巡检报告
│   └── roles/                         # 常驻角色定义
│       ├── censor.md                  # AUDITOR（巡检模式）
│       ├── historian.md               # 史官（可选：自动记录每日工作）
│       └── reviewer.md                # REVIEWER 值班（可选：写入时审查内容质量）
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
├── wiki/                              # 📚 跨域知识网络（Zettelkasten + wikilinks）
│
├── archive/                           # 🗄️ 完成项目归档（PARA-Archive）
│
└── templates/
```

## 知识分类（7 种类型）

| 类型 | 存储 | 示例 |
|------|------|------|
| 实体知识 | wiki/ | 某公司停产了一条产品线 |
| 经验知识 | wiki/（标记主观） | X 材料比 Y 材料手感好 |
| 关系知识 | wiki/（反向链接） | 某人通过 Event B 认识 |
| 决策记录 | areas/ 或 projects/ | 项目从工具 A 切到工具 B |
| Todo / 意图 | tasks/ | 下次尝试产品 X |
| 灵感 / 直觉 | inbox/（临时） | X 和 Y 之间有机会 |
| 流程知识 | wiki/ | 在日本注册公司的步骤 |

这 7 种可能随实际使用扩展。

---

## 知识提取：四步训练

1. **用户决定**：桌面 CC 生成"提取提案"，用户确认/修改
2. **累积样本**：记入 `_meta/extraction-log.md`
3. **LLM 归纳规则**：从 log 中归纳偏好，写入 `_meta/extraction-rules.md`（纯 markdown，模型无关）
4. **定期校正**：用户每月审查、报告误分类、CC 更新规则

核心：**"学习"的载体是 markdown 文件，不是模型权重**。换模型只需读这些文件。

---

## AUDITOR：两种操作模式

AUDITOR 在 Draft-Review-Execute 系统中有两种模式：

### 模式 1：决策审查（既有）

每次 Draft-Review-Execute 工作流后审查正式工作质量。已在 `pro/agents/auditor.md` 定义。

### 模式 2：巡检（新）

空闲时，每个领域审视自己的辖区。定义在 `_meta/roles/censor.md`。

#### 触发等级

| 触发 | 时机 | 深度 |
|------|------|------|
| **启动巡检** | 每次桌面 CC 会话开始，若 `lint-state.md` 显示 >4h 未运行 | 轻量，3 行简报 |
| **同步后巡检** | inbox 同步完成后 | 检查新内容对 wiki 一致性、需 wiki 条目的新实体、STATUS.md 更新 |
| **深度巡检** | 每周或手动触发 | 六领域全面巡检 |

#### 六领域巡检职责

| 领域 | 辖区 | 检查 |
|------|------|------|
| FINANCE | areas/finance/ | 投资策略过时、财务数字需更新 |
| EXECUTION | projects/ | 项目活跃度、TODO 完成、资源冲突 |
| GROWTH | wiki/ | 未履行社交承诺、需记录的新联系人、置信度 < 0.3 且 90+ 天无更新的 wiki 条目（建议退役）、challenges > evidence_count 的条目（建议审查）、有决策但无 wiki 条目的领域（知识缺口） |
| INFRA | wiki/ + _meta/ | 孤儿文件、破损链接、规则有效性 |
| PEOPLE | areas/career/ | 职业方向与行动对齐 |
| GOVERNANCE | 跨域 | 项目间策略冲突、缺少风险评估的决策 |

#### 问题分级

| 级别 | 处理 | 示例 |
|------|------|------|
| **自动修复** | AUDITOR 直接处理 | 缺失 index 条目、缺反向链接、格式问题 |
| **建议** | 发送到 inbox 给用户 | 数据不一致、项目可能停滞、wiki 建议 |
| **升级** | 激活 Draft-Review-Execute 决策模式 | 财务矛盾 >100万、多项目策略冲突、人际风险 |

#### 实现

- 角色定义存于 `_meta/roles/censor.md`，CLAUDE.md 仅引用
- 巡检状态持久化在 `_meta/lint-state.md`（解决 LLM 缺乏跨会话记忆的问题）
- 巡检报告存于 `_meta/lint-reports/`，摘要同步发送到 inbox
- 切换模型：角色文件不变，只改 CLAUDE.md 引用

---

## 可扩展常驻角色

| 角色 | 文件 | 功能 |
|------|------|------|
| AUDITOR | `_meta/roles/censor.md` | 巡检（必需） |
| 史官 | `_meta/roles/historian.md` | 会话结束时自动记录每日工作（可选） |
| REVIEWER 值班 | `_meta/roles/reviewer.md` | 写入时审查内容质量（可选） |

---

## Draft-Review-Execute 输出目的地

所有输出使用 `references/data-model.md` 的标准操作。用户所选后端的 adapter 把这些翻译成平台特定调用。

| 输出 | 标准操作 |
|------|---------|
| 决策摘要报告 | Save Decision |
| 行动项 | Save Task |
| RETROSPECTIVE / AUDITOR / ADVISOR 报告 | Save JournalEntry |
| 巡检报告 | Save JournalEntry（type: inspection） |
| 研究 / 知识 | Save WikiNote |
| 目标 | Update Area（goals 字段） |
| 全局状态 | 通过 adapter 特定的 STATUS 机制更新 |

---

## 存储后端

Life OS 支持三种存储后端。用户选 1、2 或全部 3 个。

| 后端 | 适合 | Adapter | 格式 |
|------|------|---------|------|
| GitHub | 技术用户、Claude Code | `references/adapter-github.md` | .md + front matter |
| Google Drive | 普通用户、零配置 | `references/adapter-gdrive.md` | .md + front matter |
| Notion | Notion 用户 | `references/adapter-notion.md` | Notion 数据库 |

标准数据类型和操作：`references/data-model.md`

多后端规则（同步、冲突、删除、失败处理）：`references/data-model.md`

---

## RETROSPECTIVE 数据操作

所有操作使用标准接口。按用户配置的后端适配调用。

### 整理模式（会话开始）

```
0. 读 _meta/config.md → 获取后端列表和本平台的上次同步时间
0. DATA LAYER CHECK：若 _meta/config.md 不存在 → FIRST-RUN 模式：
   - 问用户选哪个存储后端（GitHub / GDrive / Notion）
   - 创建最小目录结构：_meta/（config.md, STATUS.md, journal/, outbox/）、projects/、areas/、wiki/、inbox/、archive/、templates/
   - 写 _meta/config.md 记录选择
   - 跳过 步骤 1-8，直接进入简报
1. 读 _meta/config.md → 获取后端列表和本平台的上次同步时间
2. 探测每个配置的后端是否可用（不可用标记为 SKIPPED）
3. 多后端同步（若配置多个后端且可用）：
   - 查询每个可用的同步后端，自本平台 last_sync_time 以来的变化
   - 比较、解决冲突（见 data-model.md）
   - 应用变化到主后端
   - 推送到同步后端
4. OUTBOX MERGE：扫描 _meta/outbox/ 未合并会话
   - 若 _meta/.merge-lock 存在且 <5min → 跳过合并
   - 写 .merge-lock → 合并每个 outbox → 编译 STATUS.md → commit + push → 删除 .merge-lock
   - 在简报中报告已合并会话
5. 读 inbox（未处理项）——通过主后端
6. 读 _meta/STATUS.md（全局状态）
7. 读 _meta/lint-state.md（检查是否需要巡检：>4h 未运行）
8. ReadProjectContext（绑定项目）——tasks、decisions、journal
9. 读 user-patterns.md
10. 全局概览：List Project + List Area（只有标题和状态）
11. 战略地图编译：若 `_meta/strategic-lines.md` 存在 → 编译 `_meta/STRATEGIC-MAP.md`。见 `references/strategic-map-spec.md`
12. 若 lint-state.md 显示 >4h → 触发轻量 AUDITOR 巡检
13. 平台识别 + 版本检查
```

### 收尾模式（流程结束）

```
1. 生成 session-id：运行 date 命令获取真实时间戳，格式化为 {platform}-{YYYYMMDD}-{HHMM}。不捏造——用系统时钟。HARD RULE。
2. 创建 _meta/outbox/{session_id}/
3. Save Decision / Save Task / Save JournalEntry → 到 _meta/outbox/{session_id}/（不是主目录）
4. 写 index-delta.md（对 projects/{project}/index.md 的变更）
5. 写 patterns-delta.md（若 ADVISOR 有建议，追加到 user-patterns.md 的内容）
6. 写 manifest.md（会话元数据）
7. git add _meta/outbox/{session_id}/ → commit → push（仅 outbox 目录）
8. 同步 outbox 到 Notion（若配置）
9. 更新本平台的 last_sync_time 在 _meta/config.md
10. 任何后端失败 → 记录到 _meta/sync-log.md，不阻塞

注意：不要直接写入 projects/、STATUS.md 或 user-patterns.md。合并发生在下次 Start Court。
```

### 复盘模式

```
1. 读 _meta/STATUS.md 获取全局状态
2. List Task（所有项目）→ 计算完成率
3. List Area → 读取目标
4. List JournalEntry（近期）→ 日志和巡检报告
5. 从结果计算指标仪表盘
```

## ADVISOR 数据获取

```
1. 读 user-patterns.md
2. List JournalEntry（type: remonstrator, limit: 3）→ 最近 3 份报告
3. List Decision（limit: 5）→ 近期决策
4. List Task → 计算完成率
```

## 单一真相源规则

**`projects/{project}/index.md` 是每项目 version、phase、status 的权威源**。`_meta/STATUS.md` 是编译的仪表盘——必须从 index.md 文件生成，从不手写。

| 数据 | 权威源 | 编译视图 |
|------|-------|---------|
| 项目 version / phase / status | `projects/{project}/index.md` | `_meta/STATUS.md` |
| Area goals / status | `areas/{area}/index.md` | `_meta/STATUS.md` |
| Task 完成 | `projects/{project}/tasks/*.md` | 指标仪表盘 |
| 行为模式 | `user-patterns.md` | ADVISOR 报告 |
| 战略关系 | `projects/{project}/index.md` 战略字段 + `_meta/strategic-lines.md` | `_meta/STRATEGIC-MAP.md` |

**写入顺序是强制的**：先更新权威源，再编译仪表盘。**不要直接写 STATUS.md 的项目级信息**。

**AUDITOR lint 规则**：巡检时检查 `_meta/STATUS.md` 中每项目的 version/status 是否与 `projects/{project}/index.md` 一致。若不一致 → 报告 🔴，标记权威源为正确。

---

## 降级规则

- 主后端不可达 → 标注"⚠️ primary backend unavailable"
- 同步后端不可达 → 标注 ⚠️，记录日志，下次会话重试
- 所有后端都不可用 → 正常运行，输出显示在对话中但不持久化
