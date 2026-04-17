# 数据层架构

所有代理在读写数据时参考此文件。

## 设计原则

1. **全覆盖**：第二大脑涵盖生活、家庭、购物、兴趣、本职工作、副业——无所不包
2. **LLM 无关**：不绑定任何特定模型。所有"智能"编码在 markdown 文件中，而非模型权重
3. **无 AI 可用**：在 Obsidian 中打开 markdown 文件，即可正常阅读、写入和导航。LLM 是加速器，而非前提
4. **Markdown 是唯一真实来源**：所有知识最终落地为 .md 文件。Notion 是传输层（收件箱），不是存储层
5. **Obsidian 是查看层**：在本地克隆 GitHub 仓库，用 Obsidian 打开。Wikilink 和标准 markdown 链接自动构建知识图谱可视化

## 模型独立性

**CLAUDE.md 是唯一绑定到特定模型的文件。** 其他一切——提取规则、lint 规则、角色定义、知识网络、目录结构——都是纯 markdown，任何模型均可读取。切换模型只需更新 CLAUDE.md 的引用。

---

## 认知管线

信息经过六个阶段流转，每个阶段对应一种方法论：

```
感知 → 捕获 → 判断 → 沉淀 → 关联 → 战略化 → 涌现
 ↑       ↑      ↑     ↓   ↘      ↑        ↑         ↑
手机    GTD    3D6M  SOUL  Wiki  ROUTER+Wiki  战略      DREAM REM
体验   inbox/  桌面  (人)  (知识) INDEX匹配    MAP      跨域碰撞
```

### 各阶段详情

**感知 → 捕获（GTD）**：移动端零摩擦捕获。用户说些什么，手机 AI 存入收件箱。此阶段不分类——收件箱就是 GTD 的收集篮。

**捕获 → 判断（Draft-Review-Execute）**：桌面 CC 从收件箱拉取。不是所有信息都需要决策。只有涉及重大资源分配、多选项权衡或难以逆转的后果时，才激活Draft-Review-Execute决策模式。

**判断 → 沉淀（SOUL + Wiki）**：决策的结论沉淀到两个池——SOUL（关于人：价值观、人格、行为模式）和 Wiki（关于事：可复用的知识、已确立的结论）。两者都**在严格标准下自动写入**（v1.6.2）：起居郎和 DREAM 自动写入通过 6 项 wiki 标准 + 隐私过滤器（wiki）或 SOUL 标准 + 低初始置信度（SOUL）的条目。用户事后调整——删除文件即废弃，说"撤销最近 wiki/SOUL"即回滚。**快照**：archiver 在每次会话结束时捕获 SOUL 状态，供 RETROSPECTIVE 用于趋势计算。

**沉淀 → 关联（ROUTER + Wiki INDEX）**：ROUTER在每次会话开始时读取 wiki/INDEX.md。当新请求到来时，已有知识被自动匹配——"我们在这个领域已经知道 X"。这将积累的知识转化为活跃的上下文。

**关联 → 战略化（战略地图）**：ROUTER在每次会话开始时读取 `_meta/STRATEGIC-MAP.md`。当请求涉及具有战略关系的项目时，系统自动浮现下游依赖、瓶颈状态和决策传播警告。这将项目级分析转化为战略线感知的分析。参见 `references/strategic-map-spec.md`。

**战略化 → 涌现（DREAM REM）**：当 wiki 条目和战略关系积累时，DREAM 的 REM 阶段以流动图为脚手架发现跨域连接——检查 SOUL x 战略一致性、wiki x 流动完整性、行为模式 x 战略优先级一致性。知识和关系沉淀得越多，涌现就越多。AUDITOR巡查也检测 wiki 矛盾、知识空白和项目间的战略矛盾。

### 移动 vs 桌面分工

移动端只负责感知和捕获（偶尔轻量关联，如网络搜索）。桌面负责判断、沉淀、关联和涌现——所有重活。移动端可以读取管道产出（STATUS.md、归档），但只在捕获阶段写入。

---

## GitHub 目录结构

```
second-brain/
│
├── SOUL.md                            # 🔮 用户人格档案（价值观、信念、身份认同——从零成长）
├── user-patterns.md                   # 📊 行为模式（你的行为——ADVISOR维护）
│
├── inbox/                             # 📥 未处理（移动端捕获、材料、读书笔记、原始研究）
│
├── _meta/                             # 🔧 系统元数据
│   ├── STATUS.md                      # 全局状态仪表板（从 index.md 文件编译）
│   ├── STRATEGIC-MAP.md               # 战略地图（从项目战略字段编译）
│   ├── strategic-lines.md             # 战略线定义（用户定义）
│   ├── MAP.md                         # 知识地图（所有领域入口）
│   ├── decisions/                     # 跨领域重大决策
│   ├── journal/                       # 早朝晨报、AUDITOR/ADVISOR报告、DREAM 报告
│   ├── outbox/                        # 📮 Session 输出暂存区（每个 session 一个子目录）
│   │   └── {session-id}/             # 每个 session 在退朝时写入此处，下次上朝时合并
│   ├── snapshots/                     # 📸 用于趋势计算的状态快照
│   │   └── soul/                      # 每 session 的 SOUL 快照（YYYY-MM-DD-HHMM.md）
│   │       └── _archive/              # 30 天以上的快照
│   ├── extraction-rules.md            # 知识提取规则（用户训练）
│   ├── extraction-log.md              # 提取历史
│   ├── lint-rules.md                  # 巡查规则
│   ├── lint-state.md                  # 巡查状态（上次运行时间等）
│   ├── lint-reports/                  # 历史巡查报告
│   └── roles/                         # 常驻角色定义
│       ├── censor.md                  # AUDITOR（巡察模式）
│       ├── historian.md               # 史官（可选：自动记录每日工作）
│       └── reviewer.md               # REVIEWER值班（可选：写入时审查内容质量）
│
├── projects/                          # 🎯 有终点的事项（PARA-P）
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
├── wiki/                              # 📚 跨领域知识网络（Zettelkasten + wikilink）
│
├── archive/                           # 🗄️ 已完成项目归档（PARA-Archive）
│
└── templates/
```

## 知识分类（7 种类型）

| 类型 | 存储位置 | 示例 |
|------|---------|------|
| 实体知识 | wiki/ | 某公司停产了某产品线 |
| 经验知识 | wiki/（标注主观） | 材料 X 手感优于材料 Y |
| 关系知识 | wiki/（反向链接） | A 君通过活动 B 认识 |
| 决策记录 | areas/ 或 projects/ | 项目从工具 A 换到工具 B |
| 待办/意向 | tasks/ | 下次试用产品 X |
| 灵感/直觉 | inbox/（临时） | X 和 Y 之间存在机会 |
| 流程知识 | wiki/ | 在日本注册公司的步骤 |

这 7 种类型可能随实际使用情况不断扩展。

---

## 知识提取：四步训练

1. **用户决定**：桌面 CC 生成"提取提案"，用户确认/修改
2. **积累样本**：记录至 `_meta/extraction-log.md`
3. **LLM 归纳规则**：从日志中归纳偏好，写入 `_meta/extraction-rules.md`（纯 markdown，模型无关）
4. **定期校正**：用户每月审查，报告误分类，CC 更新规则

核心："学习"的载体是 markdown 文件，而非模型权重。切换模型只需读取这些文件。

---

## AUDITOR：两种运行模式

AUDITOR在Draft-Review-Execute系统中有两种模式：

### 模式 1：决策审查（现有）

每次Draft-Review-Execute工作流结束后审查官员工作质量。已在 `pro/agents/auditor.md` 中定义。

### 模式 2：巡察（新增）

空闲时，各部自查职责范围。定义在 `_meta/roles/censor.md`。

#### 触发等级

| 触发 | 时机 | 深度 |
|------|------|------|
| **启动巡查** | 每次桌面 CC session 启动，若 `lint-state.md` 显示距上次运行 >4h | 轻量，3 行简报 |
| **同步后巡查** | 收件箱同步完成后 | 检查新内容与 wiki 一致性、需要建立 wiki 文章的新实体、STATUS.md 更新 |
| **深度巡查** | 每周或手动触发 | 六领域完整巡察 |

#### 六领域巡察职责

| 部门 | 职责范围 | 检查内容 |
|------|---------|---------|
| FINANCE | areas/finance/ | 投资策略是否过时、财务数据是否需要更新 |
| EXECUTION | projects/ | 项目活跃度、TODO 完成情况、资源冲突 |
| GROWTH | wiki/（关系） | 未兑现的社交承诺、需记录的新联系人 |
| INFRA | wiki/ + _meta/ | 孤立文件、断开的链接、规则有效性 |
| PEOPLE | areas/career/ | 职业方向与实际行动是否一致 |
| GOVERNANCE | 跨领域 | 项目间策略矛盾、决策缺少风险评估 |

#### 问题分级

| 级别 | 处理方式 | 示例 |
|------|---------|------|
| **自动修复** | AUDITOR直接处理 | 缺少 index 条目、缺少反向链接、格式问题 |
| **建议** | 发送至收件箱供用户处理 | 数据不一致、项目可能停滞、wiki 建议 |
| **上报** | 激活Draft-Review-Execute决策模式 | 财务矛盾 >¥100 万、多项目策略冲突、人际风险 |

#### 实现

- 角色定义存储在 `_meta/roles/censor.md`，CLAUDE.md 只引用它
- 巡查状态持久化在 `_meta/lint-state.md`（解决 LLM 无跨 session 记忆的问题）
- 巡查报告存储在 `_meta/lint-reports/`，摘要也发送至收件箱
- 切换模型：角色文件不变，只更改 CLAUDE.md 中的引用

---

## 可扩展常驻角色

| 角色 | 文件 | 功能 |
|------|------|------|
| AUDITOR | `_meta/roles/censor.md` | 巡察（必需） |
| 史官 | `_meta/roles/historian.md` | session 结束时自动记录每日工作（可选） |
| REVIEWER值班 | `_meta/roles/reviewer.md` | 写入时审查内容质量（可选） |

---

## Draft-Review-Execute产出去向

所有产出使用 `references/data-model.md` 中的标准操作。用户所选后端的适配器将这些操作翻译为平台特定的调用。

| 产出 | 标准操作 |
|------|---------|
| 决策奏折 | Save Decision |
| 行动项 | Save Task |
| 早朝 / AUDITOR / ADVISOR报告 | Save JournalEntry |
| 巡查报告 | Save JournalEntry（type: inspection） |
| 调研 / 知识 | Save WikiNote |
| 目标 | Update Area（goals 字段） |
| 全局状态 | 通过适配器特定的 STATUS 机制 Update |

---

## 存储后端

Life OS 支持三种存储后端。用户可选 1 个、2 个或全部 3 个。

| 后端 | 最适用于 | 适配器 | 格式 |
|------|---------|--------|------|
| GitHub | 技术用户、Claude Code | `references/adapter-github.md` | .md + front matter |
| Google Drive | 普通用户、零配置 | `references/adapter-gdrive.md` | .md + front matter |
| Notion | Notion 用户 | `references/adapter-notion.md` | Notion 数据库 |

标准数据类型和操作：`references/data-model.md`

多后端规则（同步、冲突、删除、故障处理）：`references/data-model.md`

---

## RETROSPECTIVE数据操作

所有操作使用标准接口。根据用户配置的后端适配调用。

### 家政模式（对话开始时）

```
0. 读取 _meta/config.md → 获取后端列表和本平台的上次同步时间戳
0. 数据层检查：若 _meta/config.md 不存在 → 首次运行模式：
   - 询问用户存储后端选择（GitHub / GDrive / Notion）
   - 创建最小目录结构：_meta/（config.md、STATUS.md、journal/、outbox/）、projects/、areas/、wiki/、inbox/、archive/、templates/
   - 写入 _meta/config.md 并记录所选后端
   - 跳过步骤 1-8，直接进入晨报
1. 读取 _meta/config.md → 获取后端列表和本平台的上次同步时间戳
2. 探测每个已配置后端的 MCP 可用性（标记不可用为 SKIPPED）
3. 多后端同步（如已配置多个后端且可用）：
   - 查询每个可用同步后端自本平台 last_sync_time 以来的变更
   - 比较，解决冲突（见 data-model.md）
   - 将变更应用到主后端
   - 推送至同步后端
4. OUTBOX 合并：扫描 _meta/outbox/ 中未合并的 session
   - 若 _meta/.merge-lock 存在且时间 < 5 分钟 → 跳过合并
   - 写入 .merge-lock → 合并每个 outbox → 编译 STATUS.md → commit + push → 删除 .merge-lock
   - 在晨报中汇报已合并的 session
5. 读取收件箱（未处理条目）—— 通过主后端
6. 读取 _meta/STATUS.md（全局状态）
7. 读取 _meta/lint-state.md（检查是否需要巡查：距上次运行 >4h）
8. ReadProjectContext（绑定项目）—— 任务、决策、日志
9. 读取 user-patterns.md
10. 全局概览：列出项目 + 列出领域（仅标题 + 状态）
11. 战略地图编译：若 `_meta/strategic-lines.md` 存在 → 编译 `_meta/STRATEGIC-MAP.md`。参见 `references/strategic-map-spec.md`。
12. 若 lint-state.md 显示 >4h → 触发AUDITOR轻量巡查
13. 平台感知 + 版本检查
```

### 收朝模式（流程结束时）

```
1. 生成 session-id：执行 date 命令获取实际时间戳，格式为 {platform}-{YYYYMMDD}-{HHMM}。禁止编造——必须使用系统时钟。硬规则。
2. 创建 _meta/outbox/{session-id}/
3. Save Decision / Save Task / Save JournalEntry → 写入 _meta/outbox/{session-id}/（不写入主目录）
4. 写入 index-delta.md（projects/{p}/index.md 的变更）
5. 写入 patterns-delta.md（若ADVISOR有建议，追加 user-patterns.md 内容）
6. 写入 manifest.md（session 元数据）
7. git add _meta/outbox/{session-id}/ → commit → push（仅 outbox 目录）
8. 同步 outbox 至 Notion（如已配置）
9. 在 _meta/config.md 中更新本平台的 last_sync_time
10. 任何后端失败 → 记录至 _meta/sync-log.md，不阻塞流程

注意：不得直接写入 projects/、STATUS.md 或 user-patterns.md。合并在下次上朝时进行。
```

### 复盘模式

```
1. 读取 _meta/STATUS.md 获取全局状态
2. List Task（所有项目）→ 计算完成率
3. List Area → 读取目标
4. List JournalEntry（近期）→ 日志和巡查报告
5. 从结果计算指标仪表板
```

## ADVISOR数据获取

```
1. 读取 user-patterns.md
2. List JournalEntry（type: remonstrator，limit: 3）→ 最近 3 份报告
3. List Decision（limit: 5）→ 近期决策
4. List Task → 计算完成率
```

## 唯一真实来源规则

**`projects/{p}/index.md` 是每个项目版本、阶段和状态的权威来源。** `_meta/STATUS.md` 是编译后的仪表板——必须从 index.md 文件生成，不可手工填写。

| 数据 | 权威来源 | 汇总视图 |
|------|---------|---------|
| 项目版本 / 阶段 / 状态 | `projects/{p}/index.md` | `_meta/STATUS.md` |
| 领域目标 / 状态 | `areas/{a}/index.md` | `_meta/STATUS.md` |
| 任务完成情况 | `projects/{p}/tasks/*.md` | 指标仪表板 |
| 行为模式 | `user-patterns.md` | ADVISOR报告 |
| 战略关系 | `projects/{p}/index.md` strategic 字段 + `_meta/strategic-lines.md` | `_meta/STRATEGIC-MAP.md` |

**写入顺序强制执行**：始终先更新权威来源，再编译仪表板。不得直接向 STATUS.md 写入项目级信息。

**AUDITOR lint 规则**：巡察时，检查 `_meta/STATUS.md` 中每个项目的版本/状态是否与 `projects/{p}/index.md` 一致。若不一致 → 报告 🔴，以权威来源为准。

---

## 降级规则

- 主后端不可达 → 标注"⚠️ 主后端不可用"
- 同步后端不可达 → 标注 ⚠️，记录，下次 session 重试
- 所有后端不可用 → 正常运行，产出显示在对话中但不持久化
