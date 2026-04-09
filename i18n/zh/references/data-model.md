# 标准数据模型

所有 Life OS 数据操作使用这些标准类型和接口。适配器将它们翻译为平台特定的调用。

## 数据类型

### Decision（决策）

| 字段 | 类型 | 必填 | 描述 |
|-------|------|----------|-------------|
| id | string | 自动 | 唯一标识符（文件名或数据库 ID） |
| title | string | 是 | 主题（≤20 字符） |
| type | enum | 是 | `simple` / `3d6m`（三省六部） |
| ministries | string[] | 否 | 启用的部门 |
| score | number | 否 | 综合评分（1-10） |
| veto_count | number | 否 | 门下省封驳次数 |
| status | enum | 是 | `considering` / `decided` / `reversed` |
| category | enum | 否 | `career` / `finance` / `product` / `tech` / `family` / `life` / `health` |
| outcome | enum | 否 | `good` / `neutral` / `bad` / `tbd` |
| date | date | 是 | 决策日期 |
| project | string | 否 | 关联项目 |
| area | string | 否 | 关联领域 |
| last_modified | datetime | 自动 | 最后修改时间戳 |
| content | text | 是 | 奏折全文（正文） |

### Task（任务）

| 字段 | 类型 | 必填 | 描述 |
|-------|------|----------|-------------|
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

| 字段 | 类型 | 必填 | 描述 |
|-------|------|----------|-------------|
| id | string | 自动 | |
| title | string | 是 | 条目标题 |
| date | date | 是 | 条目日期 |
| type | enum | 是 | `morning-court` / `censorate` / `remonstrator` / `inspection` / `manual` |
| mood | enum | 否 | `great` / `good` / `neutral` / `low` / `bad` |
| energy | enum | 否 | `high` / `medium` / `low` |
| tags | string[] | 否 | |
| last_modified | datetime | 自动 | |
| content | text | 是 | 报告全文（正文） |

### WikiNote（知识条目）

| 字段 | 类型 | 必填 | 描述 |
|-------|------|----------|-------------|
| id | string | 自动 | |
| title | string | 是 | 笔记标题 |
| tags | string[] | 否 | |
| links | string[] | 否 | 指向其他笔记的 Wikilinks |
| last_modified | datetime | 自动 | |
| content | text | 是 | 笔记正文 |

### Project（项目）

| 字段 | 类型 | 必填 | 描述 |
|-------|------|----------|-------------|
| id | string | 自动 | |
| name | string | 是 | 项目名称 |
| status | enum | 是 | `planning` / `active` / `on-hold` / `done` / `dropped` |
| priority | enum | 否 | `p0` / `p1` / `p2` / `p3` |
| deadline | date | 否 | |
| area | string | 否 | 关联领域 |
| last_modified | datetime | 自动 | |
| outcome | text | 否 | 结果描述 |

### Area（领域）

| 字段 | 类型 | 必填 | 描述 |
|-------|------|----------|-------------|
| id | string | 自动 | |
| name | string | 是 | 领域名称 |
| description | text | 否 | |
| status | enum | 是 | `active` / `inactive` |
| review_cycle | enum | 否 | `weekly` / `monthly` / `quarterly` |
| last_modified | datetime | 自动 | |
| goals | text | 否 | 目标描述 |

---

## 标准操作

所有代理使用这些操作。适配器将它们翻译为平台特定的调用。

| 操作 | 签名 | 描述 |
|-----------|-----------|-------------|
| **Save** | `Save(type, data)` | 创建一条新记录 |
| **Update** | `Update(type, id, data)` | 修改一条已有记录 |
| **Archive** | `Archive(type, id)` | 移至归档 |
| **Read** | `Read(type, id)` | 获取单条记录 |
| **List** | `List(type, filters)` | 获取符合筛选条件的记录 |
| **Search** | `Search(keyword)` | 跨所有类型全文搜索 |
| **ReadProjectContext** | `ReadProjectContext(project_id)` | 批量读取：项目索引 + 任务 + 决策 + 日志 |

---

## 多后端规则

### 后端选择

用户选择 1、2 或 3 个后端。当选择多个时，自动指定一个为**主后端**（读+写），其他为**同步后端**（仅写入）。

**自动选择规则**：GitHub > Google Drive > Notion

| 配置 | 主后端 | 同步后端 |
|--------|---------|------|
| 仅 GitHub | GitHub | — |
| 仅 GDrive | GDrive | — |
| 仅 Notion | Notion | — |
| GitHub + Notion | GitHub | Notion |
| GitHub + GDrive | GitHub | GDrive |
| GDrive + Notion | GDrive | Notion |
| 全部三个 | GitHub | GDrive + Notion |

### 写入顺序

1. 先写入主后端
2. 然后按顺序写入每个同步后端
3. 如果任何同步后端失败 → 标注 `⚠️ [后端] 写入失败`，记录到 `_meta/sync-log.md`，继续处理其他后端
4. 下次会话自动重试失败的写入

### 读取顺序

1. 从主后端读取
2. 如果主后端不可用或搜索无结果 → 按顺序尝试同步后端
3. 搜索结果标注来源后端

---

## 同步协议

### 会话开始（早朝官管家模式）

```
1. 读取 _meta/config.md → 获取后端列表和上次同步时间戳
2. 对每个同步后端：
   - 查询"自 [last_sync_time] 以来修改的项目"
   - GitHub: git log --since
   - GDrive: modifiedTime > last_sync_time
   - Notion: last_edited_time > last_sync_time
3. 比较变更：
   - 仅一个后端修改了某项目 → 采纳
   - 两个后端修改了同一项目 → last_modified 胜出
   - 时间差 < 1 分钟 → 标记为 CONFLICT，保留两个版本
4. 将胜出的变更应用到主后端
5. 将主后端状态推送到所有同步后端
6. 更新 _meta/sync-log.md 记录同步结果
7. 更新 _meta/config.md 中的 last_sync_time
```

### 会话结束（早朝官收尾模式）

```
1. 将所有输出写入主后端
2. 将所有输出写入每个同步后端
3. 更新 _meta/config.md 的 last_sync_time
4. 任何后端失败 → 记录，不阻塞
```

---

## 冲突处理

| 情况 | 操作 |
|-----------|--------|
| 一个后端有变更 | 采纳该变更 |
| 两个后端修改了同一项目，时间差 > 1 分钟 | last_modified 胜出（最后写入胜出） |
| 两个后端修改了同一项目，时间差 ≤ 1 分钟 | CONFLICT：保留两个版本，丞相请用户选择 |
| 用户解决冲突 | 胜出版本推送到所有后端 |

---

## 删除规则

- **删除不跨后端同步**
- 当某项目在一个后端被删除 → 其他后端标记 `_deleted: true`（软删除）
- 下次会话，丞相询问用户："项目 X 已在 [后端] 被删除。是否从所有后端删除？"
- 用户确认 → 全部硬删除
- 用户拒绝 → 在被删除的后端恢复

---

## 故障处理

| 场景 | 处理方式 |
|----------|---------|
| 写入时后端离线 | 跳过该后端，标注 ⚠️，记录到 sync-log.md。下次会话自动重试。 |
| 同步中途崩溃 | 下次启动：比较所有后端的 last_modified，检测不一致，从最新版本自动修复。 |
| 某后端数据损坏 | 丞相检测到异常，询问用户："是否从 [其他后端] 恢复？" |
| 新设备 | 配置存于 _meta/config.md。Git clone → 配置就绪。无第二大脑 → 会话级配置。 |
| 新增后端 | 丞相询问："是否将现有数据从 [主后端] 同步到 [新后端]？" |
| 移除后端 | 丞相询问："保留 [被移除后端] 上的数据还是清理？" |

---

## 配置

存储在 `_meta/config.md`（第二大脑仓库中）：

```yaml
storage:
  backends:
    - type: github
      role: primary
    - type: notion
      role: sync
  last_sync: "2026-04-08T15:30:00Z"
```

无第二大脑 → 配置存储在会话上下文中，丞相每次新会话询问。

---

## 约束

- 同一时间只能有一个 CC 会话操作第二大脑
- 移动设备通过 Notion 收件箱或 GDrive 收件箱写入，不直接写入结构化数据（除非使用方案 B 全量同步）
- 所有适配器必须支持 7 种标准操作
