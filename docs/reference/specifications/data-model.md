# 标准数据模型（Data Model）

所有 Life OS 的数据操作使用以下标准类型和接口。Adapter 将它们翻译成平台特定的调用。

## 数据类型

### Decision（决策）

> ⚠️ **v1.9 schema 取代下表**（见 RFC §3.3.2 / §11.2.1 + `pro/CLAUDE.md` §"Decision Records"）。v1.9 决策记录写入 `meta/decisions/<YYYY-MM>/dec-<YYYY-MM-DD>-<NNN>.md`，frontmatter：`id` / `title` / `type`（**`change`/`no_change`/`escalation`/`superseded`** —— 注意 v1.9 把 `type` 复用为决策记录种类，**不是**下表的 workflow 种类 `simple`/`3d6m`）/ `projects` / `domains`（6 functional IDs）/ `reviewed_by` / `reviewed_at` / `decision` / `rationale` / `reopen_condition`（no_change 必填）/ `applied_methods`（列表）/ `journal_date`。下表为 pre-v1.9 字段，仅供历史/旧文件解析。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | auto | 唯一标识（文件名或数据库 ID） |
| title | string | 是 | 主题（≤20 字符） |
| type | enum | 是 | （pre-v1.9）`simple` / `3d6m`（Draft-Review-Execute 和六领域）—— v1.9 已改为 change/no_change/escalation/superseded |
| domains | string[] | 否 | 激活的领域 |
| score | number | 否 | 综合评分（1-10） |
| veto_count | number | 否 | REVIEWER 否决次数 |
| status | enum | 是 | `considering` / `decided` / `reversed` |
| category | enum | 否 | `career` / `finance` / `product` / `tech` / `family` / `life` / `health` |
| outcome | enum | 否 | `good` / `neutral` / `bad` / `tbd` |
| date | date | 是 | 决策日期 |
| project | string | 否 | 关联项目 |
| area | string | 否 | 关联 area |
| last_modified | datetime | auto | 最后修改时间 |
| content | text | 是 | 总结报告全文（正文） |

### Task（任务）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | auto | |
| title | string | 是 | 任务名 |
| status | enum | 是 | `todo` / `in-progress` / `waiting` / `done` / `cancelled` |
| priority | enum | 否 | `p0` / `p1` / `p2` / `p3` |
| due_date | date | 否 | 截止日期 |
| context | enum | 否 | `computer` / `phone` / `home` / `office` / `call` / `errand` |
| energy | enum | 否 | `high` / `medium` / `low` |
| project | string | 否 | 关联项目 |
| area | string | 否 | 关联 area |
| last_modified | datetime | auto | |

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

### WikiNote（Wiki 笔记）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | auto | |
| title | string | 是 | 笔记标题 |
| tags | string[] | 否 | |
| links | string[] | 否 | 指向其他笔记的 wikilinks |
| last_modified | datetime | auto | |
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
| area | string | 否 | 关联 area |
| outcome | text | 否 | 结果描述 |

### Area（领域）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | auto | |
| name | string | 是 | 领域名 |
| description | text | 否 | |
| status | enum | 是 | `active` / `inactive` |
| review_cycle | enum | 否 | `weekly` / `monthly` / `quarterly` |
| last_modified | datetime | auto | |
| goals | text | 否 | 目标描述 |

### StrategicLine（战略线）

存储于 `meta/strategic-lines.md`（用户 second-brain）。多条战略线用 `---` 分隔。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识（kebab-case） |
| name | string | 是 | 显示名 |
| purpose | text | 是 | 一句话正式目的 |
| driving_force | text | 否 | 真正驱动你投入这条线的动力（可与 purpose 不同） |
| health_signals | text[] | 否 | 哪些信号表明这条线健康（AI 提议，用户确认） |
| time_window | date | 否 | 影响整条线的截止日期 |
| area | string | 否 | 关联生活 area |
| created | date | auto | 创建日期 |

### 每项目战略字段

对 `projects/{project}/index.md` frontmatter 的可选扩展。所有字段默认为空/null。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| strategic.line | string | 否 | 战略线 ID（引用 `meta/strategic-lines.md`） |
| strategic.role | enum | 否 | `critical-path` / `enabler` / `accelerator` / `insurance` |
| strategic.flows_to[] | array | 否 | 流向：[{target, type, description}] |
| strategic.flows_from[] | array | 否 | 流入：[{source, type, description}] |
| strategic.last_activity | date | auto | 最后修改日期（ARCHIVER 自动更新） |
| strategic.status_reason | text | 否 | 项目为何处于当前状态 |

流动类型：`cognition` / `resource` / `decision` / `trust`。角色和流动定义见 `references/strategic-map-spec.md`。

---

## 标准操作

所有 agent 使用以下操作。Adapter 翻译为平台特定调用。

| 操作 | 签名 | 说明 |
|------|------|------|
| **Save** | `Save(type, data)` | 创建新记录 |
| **Update** | `Update(type, id, data)` | 修改现有记录 |
| **Archive** | `Archive(type, id)` | 移至归档 |
| **Read** | `Read(type, id)` | 获取单条记录 |
| **List** | `List(type, filters)` | 获取匹配过滤条件的记录 |
| **Search** | `Search(keyword)` | 跨所有类型全文搜索 |
| **ReadProjectContext** | `ReadProjectContext(project_id)` | 批量读：项目 index + tasks + decisions + journal |

---

## 多后端规则

### 后端选择

用户选 1、2 或 3 个后端。多选时，一个自动指定为 **primary**（读 + 写），其他是 **sync**（仅写）。

**自动选择规则**：GitHub > Google Drive > Notion

| 配置 | Primary | Sync |
|------|---------|------|
| 仅 GitHub | GitHub | — |
| 仅 GDrive | GDrive | — |
| 仅 Notion | Notion | — |
| GitHub + Notion | GitHub | Notion |
| GitHub + GDrive | GitHub | GDrive |
| GDrive + Notion | GDrive | Notion |
| 全部三个 | GitHub | GDrive + Notion |

### 写入顺序

1. 先写 primary 后端
2. 再按顺序写每个 sync 后端
3. 若任何 sync 失败 → 标注 `⚠️ [backend] write failed`，记入 `meta/sync-log.md`，继续其他
4. 下次会话自动重试失败写入

### 读取顺序

1. 从 primary 读
2. 若 primary 不可用或搜索无结果 → 按顺序尝试 sync 后端
3. 搜索结果标注来自哪个后端

---

## 同步协议

### 会话开始（RETROSPECTIVE 整理）

```
0. 读 meta/config.md → 获取后端列表和上次同步时间
1. 探测每个配置后端是否可用：
   - GitHub：检查 git repo 可访问（git status）
   - GDrive：检查 Google Drive MCP 是否连接（尝试 list）
   - Notion：检查 Notion MCP 是否连接（尝试 search）
   不可用的标记为 SKIPPED 本会话。
   若 primary 不可用，临时晋升下一个可用后端。
   记录："💾 Backends: GitHub ✅ | GDrive ❌ (MCP not connected) | Notion ✅"
2. 对每个可用 sync 后端：
   - 查询"自本平台 last_sync_time 以来修改的项"
   - GitHub: git log --since
   - GDrive: modifiedTime > last_sync_time
   - Notion: last_edited_time > last_sync_time
3. 比较变化：
   - 只有一个后端改了某项 → 采纳
   - 两个后端都改了同一项 → last_modified 胜出
   - 时间差 < 1 分钟 → 标记 CONFLICT，保留两个版本
4. 把胜出的变化应用到 primary
5. 推送 primary 状态到所有 sync 后端
6. 更新 meta/sync-log.md 记录同步结果
7. 更新本平台的 last_sync_time 在 meta/config.md（不动其他平台的时间戳）
```

### 会话结束（RETROSPECTIVE 收尾）

```
1. 写所有输出到 primary 后端
2. 写所有输出到每个 sync 后端
3. 更新 meta/config.md last_sync_time
4. 任何后端失败 → 记录，不阻塞
```

---

## 冲突解决

| 情况 | 动作 |
|------|------|
| 一个后端改了 | 采纳变化 |
| 两个后端改了同一项，时间差 > 1 分钟 | last_modified 胜出（last write wins） |
| 两个后端改了同一项，时间差 ≤ 1 分钟 | CONFLICT：保留两版本，ROUTER 问用户选哪个 |
| 用户解决冲突 | 胜出版本推送到所有后端 |

---

## 删除规则

- **删除不跨后端同步**
- 某后端删除项后 → 其他后端标记为 `_deleted: true`（软删除）
- 下次会话，ROUTER 问用户："Item X 在 [backend] 被删除。从所有后端删除吗？"
- 用户确认 → 全部硬删除
- 用户拒绝 → 在被删除的后端恢复

---

## 失败处理

| 场景 | 处理 |
|------|------|
| 后端写入时离线 | 跳过该后端，标注 ⚠️，记入 sync-log.md。下次会话自动重试 |
| 同步中途崩溃 | 下次启动：比较所有后端的 last_modified，检测不一致，从最新者自动修复 |
| 某后端数据损坏 | ROUTER 检测异常，问用户："从 [其他后端] 恢复？" |
| 新设备 | 配置存于 meta/config.md。Git clone → 配置就绪。无 second-brain → 会话级配置 |
| 新增后端 | ROUTER 问："从 [primary] 同步既有数据到 [new backend] 吗？" |
| 移除后端 | ROUTER 问："保留 [removed backend] 的数据，还是清理？" |

---

## 配置

存储在 `meta/config.md`（second-brain repo 中）：

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

**每平台独立的同步时间戳**：每个平台记录自己的 `last_sync` 时间。当 Gemini CLI 启动会话时，它读**自己的** `last_sync` 并查询自该时间以来的变化——不是 Claude Code 的上次同步时间。这防止用户在平台间切换时丢失变化。

无 second-brain → 配置存于会话上下文，ROUTER 每次新会话询问。

---

## 约束清单

- **多个会话可以同时操作 second-brain**，使用 outbox 模式。每个会话写入自己的 outbox 目录（`meta/outbox/{session_id}/`）。下次 Start Court 合并所有 outbox 到主结构。对共享文件（STATUS.md、meta/user-patterns.md、index.md）的直接写入只发生在 Start Court 的 outbox 合并步骤
- **Session-id 格式**：`{platform}-{YYYYMMDD}-{HHMM}`，在 adjourn 时生成（不是会话开始时）。示例：`claude-20260412-1700`、`gemini-20260412-1900`
- **Outbox 合并锁**：合并期间写 `meta/.merge-lock`。若存在且 <5 分钟，跳过合并照常进入。合并完成后删除
- **空会话**：若会话无输出（无决策、任务、日志条目），不创建 outbox
- 移动设备通过 Notion inbox 或 GDrive inbox 写入，不直接写结构化数据
- 所有 adapter 必须支持 7 个标准操作

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
  wiki: 1
  dream: 1
  index_delta: true
  patterns_delta: true
---
```

### Index Delta 格式

`index-delta.md` 记录应用到 `projects/{project}/index.md` 的变更：

```markdown
# Index Delta

## Target: projects/my-project/index.md
## Fields to update:
- Phase: "v5.4 deployed"
- Current focus: "打磨计划书到对外版本"
```

### Patterns Delta 格式

`patterns-delta.md` 记录要追加到 `meta/user-patterns.md` 的内容：

```markdown
# Patterns Delta — append to meta/user-patterns.md

### [2026-04-12] New pattern: decision speed increasing
Source: ADVISOR
Observation: Last 3 decisions made after first round of clarification.
```
