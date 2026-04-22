# 标准数据模型（Data Model）

所有 Life OS 的数据操作使用以下标准类型和接口。Adapter 将它们翻译成平台特定的调用。

## 数据类型

### Decision（决策）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | auto | 唯一标识（文件名或数据库 ID） |
| title | string | 是 | 主题（≤20 字符） |
| type | enum | 是 | `simple` / `3d6m`（Draft-Review-Execute 和六领域） |
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

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | auto | |
| title | string | 是 | 条目标题 |
| date | date | 是 | 条目日期 |
| type | enum | 是 | `morning-court` / `censorate` / `remonstrator` / `inspection` / `manual` |
| mood | enum | 否 | `great` / `good` / `neutral` / `low` / `bad` |
| energy | enum | 否 | `high` / `medium` / `low` |
| tags | string[] | 否 | |
| last_modified | datetime | auto | |
| content | text | 是 | 报告全文（正文） |

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

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | auto | |
| name | string | 是 | 项目名 |
| status | enum | 是 | `planning` / `active` / `on-hold` / `done` / `dropped` |
| priority | enum | 否 | `p0` / `p1` / `p2` / `p3` |
| deadline | date | 否 | |
| area | string | 否 | 关联 area |
| last_modified | datetime | auto | |
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

存储于 `_meta/strategic-lines.md`（用户 second-brain）。多条战略线用 `---` 分隔。

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
| strategic.line | string | 否 | 战略线 ID（引用 `_meta/strategic-lines.md`） |
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
3. 若任何 sync 失败 → 标注 `⚠️ [backend] write failed`，记入 `_meta/sync-log.md`，继续其他
4. 下次会话自动重试失败写入

### 读取顺序

1. 从 primary 读
2. 若 primary 不可用或搜索无结果 → 按顺序尝试 sync 后端
3. 搜索结果标注来自哪个后端

---

## 同步协议

### 会话开始（RETROSPECTIVE 整理）

```
0. 读 _meta/config.md → 获取后端列表和上次同步时间
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
6. 更新 _meta/sync-log.md 记录同步结果
7. 更新本平台的 last_sync_time 在 _meta/config.md（不动其他平台的时间戳）
```

### 会话结束（RETROSPECTIVE 收尾）

```
1. 写所有输出到 primary 后端
2. 写所有输出到每个 sync 后端
3. 更新 _meta/config.md last_sync_time
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
| 新设备 | 配置存于 _meta/config.md。Git clone → 配置就绪。无 second-brain → 会话级配置 |
| 新增后端 | ROUTER 问："从 [primary] 同步既有数据到 [new backend] 吗？" |
| 移除后端 | ROUTER 问："保留 [removed backend] 的数据，还是清理？" |

---

## 配置

存储在 `_meta/config.md`（second-brain repo 中）：

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

- **多个会话可以同时操作 second-brain**，使用 outbox 模式。每个会话写入自己的 outbox 目录（`_meta/outbox/{session_id}/`）。下次 Start Court 合并所有 outbox 到主结构。对共享文件（STATUS.md、user-patterns.md、index.md）的直接写入只发生在 Start Court 的 outbox 合并步骤
- **Session-id 格式**：`{platform}-{YYYYMMDD}-{HHMM}`，在 adjourn 时生成（不是会话开始时）。示例：`claude-20260412-1700`、`gemini-20260412-1900`
- **Outbox 合并锁**：合并期间写 `_meta/.merge-lock`。若存在且 <5 分钟，跳过合并照常进入。合并完成后删除
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

`patterns-delta.md` 记录要追加到 `user-patterns.md` 的内容：

```markdown
# Patterns Delta — append to user-patterns.md

### [2026-04-12] New pattern: decision speed increasing
Source: ADVISOR
Observation: Last 3 decisions made after first round of clarification.
```
