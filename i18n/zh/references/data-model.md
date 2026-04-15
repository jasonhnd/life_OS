# 标准数据模型

所有 Life OS 数据操作使用这些标准类型和接口。适配器将它们翻译为平台特定的调用。

## 数据类型

### Decision（决策）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 自动 | 唯一标识符（文件名或数据库 ID） |
| title | string | 是 | 主题（≤20 字） |
| type | enum | 是 | `simple` / `3d6m`（三省六部制） |
| ministries | string[] | 否 | 已激活的部门 |
| score | number | 否 | 综合评分（1-10） |
| veto_count | number | 否 | 门下省封驳次数 |
| status | enum | 是 | `considering` / `decided` / `reversed` |
| category | enum | 否 | `career` / `finance` / `product` / `tech` / `family` / `life` / `health` |
| outcome | enum | 否 | `good` / `neutral` / `bad` / `tbd` |
| date | date | 是 | 决策日期 |
| project | string | 否 | 关联项目 |
| area | string | 否 | 关联领域 |
| last_modified | datetime | 自动 | 最后修改时间戳 |
| content | text | 是 | 奏折正文（正文内容） |

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

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 自动 | |
| title | string | 是 | 条目标题 |
| date | date | 是 | 条目日期 |
| type | enum | 是 | `morning-court` / `censorate` / `remonstrator` / `inspection` / `manual` |
| mood | enum | 否 | `great` / `good` / `neutral` / `low` / `bad` |
| energy | enum | 否 | `high` / `medium` / `low` |
| tags | string[] | 否 | |
| last_modified | datetime | 自动 | |
| content | text | 是 | 报告正文（正文内容） |

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

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 自动 | |
| name | string | 是 | 项目名称 |
| status | enum | 是 | `planning` / `active` / `on-hold` / `done` / `dropped` |
| priority | enum | 否 | `p0` / `p1` / `p2` / `p3` |
| deadline | date | 否 | |
| area | string | 否 | 关联领域 |
| last_modified | datetime | 自动 | |
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

存储在 `_meta/strategic-lines.md`（用户的第二大脑中）。多条线以 `---` 分隔。

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
| strategic.line | string | 否 | 战略线 ID（引用 `_meta/strategic-lines.md`） |
| strategic.role | enum | 否 | `critical-path` / `enabler` / `accelerator` / `insurance` |
| strategic.flows_to[] | array | 否 | 输出流：[{target, type, description}] |
| strategic.flows_from[] | array | 否 | 输入流：[{source, type, description}] |
| strategic.last_activity | date | 自动 | 最后修改日期（起居郎自动更新） |
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
3. 若某同步后端失败 → 标注 `⚠️ [backend] write failed`，记录至 `_meta/sync-log.md`，继续处理其他后端
4. 下次 session 自动重试失败的写入

### 读取顺序

1. 从主后端读取
2. 若主后端不可用或搜索无结果 → 依次尝试同步后端
3. 搜索结果标注数据来自哪个后端

---

## 同步协议

### Session 开始（早朝官家政）

```
0. 读取 _meta/config.md → 获取后端列表和上次同步时间戳
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
6. 将同步结果写入 _meta/sync-log.md
7. 在 _meta/config.md 中更新本平台的 last_sync_time（不修改其他平台的时间戳）
```

### Session 结束（早朝官收朝）

```
1. 将所有产出写入主后端
2. 将所有产出写入每个同步后端
3. 更新 _meta/config.md 中的 last_sync_time
4. 任何后端失败 → 记录，不阻塞流程
```

---

## 冲突解决

| 情况 | 处理方式 |
|------|---------|
| 只有一个后端发生变更 | 采用该变更 |
| 两个后端修改了同一条目，时间差 > 1 分钟 | last_modified 获胜（最后写入获胜） |
| 两个后端修改了同一条目，时间差 ≤ 1 分钟 | CONFLICT：保留两个版本，丞相询问用户选择 |
| 用户解决冲突 | 获胜版本推送至所有后端 |

---

## 删除规则

- **删除操作不跨后端同步**
- 在某个后端删除条目后 → 其他后端将其标记为 `_deleted: true`（软删除）
- 下次 session，丞相询问用户："条目 X 在 [后端] 上已被删除。是否从所有后端删除？"
- 用户确认 → 所有后端硬删除
- 用户拒绝 → 在被删除的后端上恢复该条目

---

## 故障处理

| 场景 | 处理方式 |
|------|---------|
| 写入时后端离线 | 跳过该后端，标注 ⚠️，记录至 sync-log.md。下次 session 自动重试。 |
| 同步中途崩溃 | 下次启动时：比较所有后端的 last_modified，检测不一致性，从最新版本自动修复。 |
| 某后端数据损坏 | 丞相检测到异常，询问用户："是否从 [其他后端] 恢复？" |
| 新设备 | 配置存储在 _meta/config.md。git clone → 配置就绪。无 second-brain → session 级别配置。 |
| 添加新后端 | 丞相询问："是否将现有数据从 [主后端] 同步至 [新后端]？" |
| 移除后端 | 丞相询问："保留 [被移除后端] 上的数据还是清理？" |

---

## 配置

存储在 `_meta/config.md`（在 second-brain 仓库中）：

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

无 second-brain → 配置存储在 session 上下文中，丞相在每次新 session 时询问。

---

## 约束条件

- **多个 session 可同时操作 second-brain**，使用 outbox 模式。每个 session 写入各自的 outbox 目录（`_meta/outbox/{session-id}/`）。下一个上朝的 session 将所有 outbox 合并到主结构中。直接写入共享文件（STATUS.md、user-patterns.md、index.md）只在上朝时的 Outbox 合并步骤中发生。
- **session-id 格式**：`{platform}-{YYYYMMDD}-{HHMM}`，在退朝时生成（非 session 开始时）。时间戳必须通过 date 命令从系统时钟获取，禁止编造。示例：`claude-20260412-1700`、`gemini-20260412-1900`。
- **Outbox merge lock**：合并期间写入 `_meta/.merge-lock`。若该文件存在且时间 < 5 分钟，跳过合并正常进行。合并完成后删除。
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
projects: [gcsb, eip]
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

## 目标：projects/gcsb/index.md
## 需更新的字段：
- Phase: "v5.4 deployed"
- Current focus: "打磨计划书到对外版本"
```

### Patterns Delta 格式

`patterns-delta.md` 记录需追加到 `user-patterns.md` 的内容：

```markdown
# Patterns Delta — 追加到 user-patterns.md

### [2026-04-12] 新模式：决策速度加快
来源：谏官
观察：最近 3 次决策均在第一轮澄清后完成。
```
