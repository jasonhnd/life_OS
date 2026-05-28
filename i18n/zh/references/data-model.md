# 标准数据模型

所有 Life OS 数据操作使用这些标准类型和接口。适配器将它们翻译为平台特定的调用。

## 数据类型

### Decision（决策）

> ⚠️ **v1.9 schema 取代下表**（见 RFC §3.3.2 / §11.2.1 + `pro/CLAUDE.md` §"Decision Records"）。v1.9 写入 `meta/decisions/<YYYY-MM>/dec-<YYYY-MM-DD>-<NNN>.md`；`type` 复用为决策记录种类 `change`/`no_change`/`escalation`/`superseded`（**不是**下表的 `simple`/`3d6m`）+ `projects` / `domains`（6 functional IDs）/ `reopen_condition`（no_change 必填）/ `applied_methods`（列表）/ `journal_date`。下表为 pre-v1.9 字段，仅供历史。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 自动 | 唯一标识符（文件名或数据库 ID） |
| title | string | 是 | 主题（≤20 字） |
| type | enum | 是 | （pre-v1.9）`simple` / `3d6m`（Draft-Review-Execute）—— v1.9 已改为 change/no_change/escalation/superseded |
| ministries | string[] | 否 | 已激活的部门 |
| score | number | 否 | 综合评分（1-10） |
| veto_count | number | 否 | REVIEWER封驳次数 |
| status | enum | 是 | `considering` / `decided` / `reversed` |
| category | enum | 否 | `career` / `finance` / `product` / `tech` / `family` / `life` / `health` |
| outcome | enum | 否 | `good` / `neutral` / `bad` / `tbd` |
| date | date | 是 | 决策日期 |
| project | string | 否 | 关联项目 |
| area | string | 否 | 关联领域 |
| last_modified | datetime | 自动 | 最后修改时间戳 |
| content | text | 是 | 报告正文（正文内容） |

### Task（任务）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 自动 | |
| title | string | 是 | 任务名称 |
| status | enum | 是 | `todo` / `in-progress` / `waiting` / `done` / `cancelled` |
| priority | enum | 否 | `p0` / `p1` / `p2` / `p3` |
| due_date | date | 否 | 截止日期 |
| context | enum | 否 | `computer` / `phone` / `home` / `office` / `call` / `errand` |
| energy | enum | 否 | `high` / `medium` / `low` |
| project | string | 否 | 关联项目 |
| area | string | 否 | 关联领域 |
| last_modified | datetime | 自动 | |

### JournalEntry（日志条目）

> ⚠️ **v1.9 schema 取代下表**（见 RFC §3.5 Opt #5 时间轴 + §3.8 Opt #8 交叉引用）。v1.9 日志是**每天一个文件** `meta/journal/<YYYY-MM-DD>.md`（时间轴为权威源；同一天的多条 entry 追加在当天文件内，已存在时按 `projects:` 合并）。下表 pre-v1.9 的 per-entry 字段为遗留。

**v1.9 权威 schema**（`meta/journal/<YYYY-MM-DD>.md`）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | date | 是 | 当天（也是文件名） |
| projects | string[] | 是 | 当天提及的项目；`[]` = 无 |
| session_ids | string[] | 否 | 当天贡献 entry 的 session id |
| type_tags | string[] | 是 | 当天出现的 entry 种类：`briefing` / `dream` / `advisor` / `auditor` / `migration` / … |
| referenced_decisions | string[] | 否 | 当天引用的 decision id（Opt #8） |
| referenced_methods | string[] | 否 | 当天应用的 method 名（Opt #8） |
| content | text | 是 | 当天的 entry（正文；多个 section 追加） |

<details><summary>Pre-v1.9 字段（遗留 per-entry 模型，新日志勿用）</summary>

| 字段 | 类型 | 说明 |
|------|------|------|
| id / title | string | 已废弃 —— 每日文件以 `date` 为键 |
| type | enum | `morning-court` / `censorate` / `remonstrator` / `inspection` / `manual` —— 被 `type_tags`（列表）取代 |
| mood / energy | enum | 在 v1.9 每日聚合模型中已删除 |
| tags | string[] | 折叠进 `type_tags` |
| last_modified | datetime | 已废弃 |

</details>

### WikiNote（知识笔记）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 自动 | |
| title | string | 是 | 笔记标题 |
| tags | string[] | 否 | |
| links | string[] | 否 | 指向其他笔记的 Wikilink |
| last_modified | datetime | 自动 | |
| content | text | 是 | 笔记正文 |

### Project（项目）

`projects/{p}/index.md` frontmatter。**v1.9 新增 `lifecycle_stage`（+ `paused_until` / `archived_*` / `created_at`）**，用于 PARA 归档状态（见 RFC §3.4 Opt #4 + DR-1.9.20 —— 取代旧的 `archive/` 目录；归档项目仍留在 `projects/{p}/`，wikilink 因此得以保留）。这是与 workflow `status` **彼此独立的另一个轴**：`lifecycle_stage` 回答"在活跃的 PARA 集合中，还是已归档？"，而 `status` + `strategic.status_reason` 驱动 workflow 与战略图谱的停滞检测。两者并存。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project / name | string | 是 | 项目名（也是目录名） |
| lifecycle_stage | enum | 是 | **v1.9** · 归档轴 —— `candidate` / `active` / `archived` / `superseded` |
| paused_until | date \| null | 否 | **v1.9** · 有时限的暂停（替代 "dormant"）；`> today` = 暂停但仍活跃 |
| created_at | date | 是 | **v1.9** · 创建日期 |
| archived_at | date \| null | 条件 | **v1.9** · 当 `lifecycle_stage: archived` 时设置 |
| archived_at_source | enum \| null | 条件 | **v1.9** · `git-log` / `migrated-unknown` / `manual` / `auto` |
| archived_reason | text | 条件 | **v1.9** · 当 `lifecycle_stage: archived` 时必填 |
| superseded_by | string | 条件 | **v1.9** · 当 `lifecycle_stage: superseded` 时必填 |
| status | enum | 否 | Workflow 轴 —— `planning` / `active` / `on-hold` / `done` / `dropped`；战略图谱停滞检测读取此字段 + `strategic.status_reason` |
| strategic | object | 否 | 战略图谱字段（`line` / `role` / `flows_to` / `flows_from` / `last_activity` / `status_reason`）—— 见 `references/strategic-map-spec.md` |
| related_wiki | wikilink[] | 否 | **v1.9** · `[[wiki/<entry>]]` 链接 |
| priority | enum | 否 | `p0` / `p1` / `p2` / `p3` |
| deadline | date | 否 | |
| area | string | 否 | 关联领域 |
| outcome | text | 否 | 结果描述 |

### Area（领域）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 自动 | |
| name | string | 是 | 领域名称 |
| description | text | 否 | |
| status | enum | 是 | `active` / `inactive` |
| review_cycle | enum | 否 | `weekly` / `monthly` / `quarterly` |
| last_modified | datetime | 自动 | |
| goals | text | 否 | 目标描述 |

### StrategicLine（战略线）

存储在 `meta/strategic-lines.md`（用户的第二大脑中）。多条线以 `---` 分隔。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识符（kebab-case） |
| name | string | 是 | 显示名称 |
| purpose | text | 是 | 一句话正式目的 |
| driving_force | text | 否 | 真正驱动对此线投入的动力（可能与 purpose 不同） |
| health_signals | text[] | 否 | 哪些信号表明此线是健康的（AI 提议，用户确认） |
| time_window | date | 否 | 影响整条线的截止日期 |
| area | string | 否 | 关联的生活领域 |
| created | date | 自动 | 创建日期 |

### 项目级战略字段

`projects/{p}/index.md` frontmatter 的可选扩展。所有字段默认为空/null。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| strategic.line | string | 否 | 战略线 ID（引用 `meta/strategic-lines.md`） |
| strategic.role | enum | 否 | `critical-path` / `enabler` / `accelerator` / `insurance` |
| strategic.flows_to[] | array | 否 | 输出流：[{target, type, description}] |
| strategic.flows_from[] | array | 否 | 输入流：[{source, type, description}] |
| strategic.last_activity | date | 自动 | 最后修改日期（ARCHIVER自动更新） |
| strategic.status_reason | text | 否 | 此项目处于当前状态的原因 |

流动类型：`cognition` / `resource` / `decision` / `trust`。角色和流动定义：`references/strategic-map-spec.md`。

---

## 标准操作

所有代理使用这些操作。适配器将它们翻译为平台特定的调用。

| 操作 | 签名 | 说明 |
|------|------|------|
| **Save** | `Save(type, data)` | 创建新记录 |
| **Update** | `Update(type, id, data)` | 修改现有记录 |
| **Archive** | `Archive(type, id)` | 移至归档 |
| **Read** | `Read(type, id)` | 获取单条记录 |
| **List** | `List(type, filters)` | 获取符合过滤条件的记录 |
| **Search** | `Search(keyword)` | 跨所有类型全文搜索 |
| **ReadProjectContext** | `ReadProjectContext(project_id)` | 批量读取：项目 index + 任务 + 决策 + 日志 |

---

## 多后端规则

### 后端选择

用户可选 1 个、2 个或全部 3 个后端。选择多个时，系统自动指定一个为**主后端**（读写），其余为**同步后端**（仅写）。

**自动选择规则**：GitHub > Google Drive > Notion

| 配置 | 主后端 | 同步后端 |
|------|--------|---------|
| 仅 GitHub | GitHub | — |
| 仅 GDrive | GDrive | — |
| 仅 Notion | Notion | — |
| GitHub + Notion | GitHub | Notion |
| GitHub + GDrive | GitHub | GDrive |
| GDrive + Notion | GDrive | Notion |
| 全部三个 | GitHub | GDrive + Notion |

### 写入顺序

1. 先写入主后端
2. 再依次写入每个同步后端
3. 若某同步后端失败 → 标注 `⚠️ [backend] write failed`，记录至 `meta/sync-log.md`，继续处理其他后端
4. 下次 session 自动重试失败的写入

### 读取顺序

1. 从主后端读取
2. 若主后端不可用或搜索无结果 → 依次尝试同步后端
3. 搜索结果标注数据来自哪个后端

---

## 同步协议

### Session 开始（RETROSPECTIVE家政）

```
0. 读取 meta/config.md → 获取后端列表和上次同步时间戳
1. 探测每个已配置后端的可用性：
   - GitHub：检查 git 仓库是否可访问（git status）
   - GDrive：检查 Google Drive MCP 是否已连接（尝试 list）
   - Notion：检查 Notion MCP 是否已连接（尝试 search）
   将不可用后端标记为本次 session SKIPPED。
   若主后端不可用，临时提升下一个可用后端。
   记录："💾 后端：GitHub ✅ | GDrive ❌（MCP 未连接）| Notion ✅"
2. 对每个可用同步后端：
   - 查询"自 [本平台 last_sync_time] 以来修改的条目"
   - GitHub：git log --since
   - GDrive：modifiedTime > last_sync_time
   - Notion：last_edited_time > last_sync_time
3. 比较变更：
   - 只有一个后端修改了某条目 → 采用该修改
   - 两个后端修改了同一条目 → last_modified 获胜
   - 时间差 < 1 分钟 → 标记为 CONFLICT，保留两个版本
4. 将获胜变更应用到主后端
5. 将主后端状态推送至所有同步后端
6. 将同步结果写入 meta/sync-log.md
7. 在 meta/config.md 中更新本平台的 last_sync_time（不修改其他平台的时间戳）
```

### Session 结束（RETROSPECTIVE收朝）

```
1. 将所有产出写入主后端
2. 将所有产出写入每个同步后端
3. 更新 meta/config.md 中的 last_sync_time
4. 任何后端失败 → 记录，不阻塞流程
```

---

## 冲突解决

| 情况 | 处理方式 |
|------|---------|
| 只有一个后端发生变更 | 采用该变更 |
| 两个后端修改了同一条目，时间差 > 1 分钟 | last_modified 获胜（最后写入获胜） |
| 两个后端修改了同一条目，时间差 ≤ 1 分钟 | CONFLICT：保留两个版本，ROUTER询问用户选择 |
| 用户解决冲突 | 获胜版本推送至所有后端 |

---

## 删除规则

- **删除操作不跨后端同步**
- 在某个后端删除条目后 → 其他后端将其标记为 `_deleted: true`（软删除）
- 下次 session，ROUTER询问用户："条目 X 在 [后端] 上已被删除。是否从所有后端删除？"
- 用户确认 → 所有后端硬删除
- 用户拒绝 → 在被删除的后端上恢复该条目

---

## 故障处理

| 场景 | 处理方式 |
|------|---------|
| 写入时后端离线 | 跳过该后端，标注 ⚠️，记录至 sync-log.md。下次 session 自动重试。 |
| 同步中途崩溃 | 下次启动时：比较所有后端的 last_modified，检测不一致性，从最新版本自动修复。 |
| 某后端数据损坏 | ROUTER检测到异常，询问用户："是否从 [其他后端] 恢复？" |
| 新设备 | 配置存储在 meta/config.md。git clone → 配置就绪。无 second-brain → session 级别配置。 |
| 添加新后端 | ROUTER询问："是否将现有数据从 [主后端] 同步至 [新后端]？" |
| 移除后端 | ROUTER询问："保留 [被移除后端] 上的数据还是清理？" |

---

## 配置

存储在 `meta/config.md`（在 second-brain 仓库中）：

```yaml
storage:
  backends:
    - type: github
      role: primary
    - type: notion
      role: sync
  sync_log:
    - platform: claude-code
      last_sync: "2026-04-10T15:30:00Z"
    - platform: gemini-cli
      last_sync: "2026-04-10T14:00:00Z"
```

**按平台记录同步时间戳**：每个平台记录各自的 `last_sync` 时间。Gemini CLI 启动 session 时，读取**自己的** `last_sync` 并查询该时间以来的变更——而非 Claude Code 的上次同步时间。这样可防止用户在多平台间交替使用时遗漏变更。

无 second-brain → 配置存储在 session 上下文中，ROUTER在每次新 session 时询问。

---

## 约束条件

- **多个 session 可同时操作 second-brain**，使用 outbox 模式。每个 session 写入各自的 outbox 目录（`meta/outbox/{session-id}/`）。下一个上朝的 session 将所有 outbox 合并到主结构中。直接写入共享文件（STATUS.md、meta/user-patterns.md、index.md）只在上朝时的 Outbox 合并步骤中发生。
- **session-id 格式**：`{platform}-{YYYYMMDD}-{HHMM}`，在退朝时生成（非 session 开始时）。时间戳必须通过 date 命令从系统时钟获取，禁止编造。示例：`claude-20260412-1700`、`gemini-20260412-1900`。
- **Outbox merge lock**：合并期间写入 `meta/.merge-lock`。若该文件存在且时间 < 5 分钟，跳过合并正常进行。合并完成后删除。
- **空 session**：若 session 无任何产出（无决策、任务或日志），不创建 outbox。
- 移动设备通过 Notion 收件箱或 GDrive 收件箱写入，不直接写入结构化数据
- 所有适配器必须支持 7 个标准操作

### Outbox Manifest 格式

每个 outbox 目录包含一个 `manifest.md`：

```yaml
---
session_id: "claude-20260412-1700"
platform: claude-code
model: opus
projects: [project-a, project-b]
adjourned: "2026-04-12T17:00:00+09:00"
outputs:
  decisions: 2
  tasks: 5
  journal: 3
  dream: 1
  index_delta: true
  patterns_delta: true
---
```

### Index Delta 格式

`index-delta.md` 记录需应用到 `projects/{p}/index.md` 的变更：

```markdown
# Index Delta

## 目标：projects/my-project/index.md
## 需更新的字段：
- Phase: "v5.4 deployed"
- Current focus: "打磨计划书到对外版本"
```

### Patterns Delta 格式

`patterns-delta.md` 记录需追加到 `meta/user-patterns.md` 的内容：

```markdown
# Patterns Delta — 追加到 meta/user-patterns.md

### [2026-04-12] 新模式：决策速度加快
来源：ADVISOR
观察：最近 3 次决策均在第一轮澄清后完成。
```
