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

## 存储后端（单一 git repo）

存储是**单一后端：一个 git repo**——本地工作副本（在硬盘上，也是用户的 Obsidian vault）+ 一个 GitHub remote 用于备份和跨设备同步。没有 primary/sync 之分，没有多后端，没有跨后端冲突逻辑。

- 读：直接读本地工作副本的 `.md` 文件
- 写：直接写本地工作副本，会话结束 commit
- 同步：普通 git —— 会话开始 `git pull`，会话结束 `git push`

---

## 同步协议（普通 git）

### 会话开始（RETROSPECTIVE 整理）

```
0. 读 meta/config.md → 获取 git remote 配置
1. git health check：
   - 确认 repo 可访问（git status）
   - 检查 remote 是否可达；不可达则降级为纯本地（记录 "⚠️ remote unavailable"），不阻塞
2. git pull（若配置了 remote 且可达）：
   - 拉回远端自上次以来的变更（含手机经 git 写入 inbox/ 的条目）
3. 冲突就是普通的 git 合并冲突，按常规 git 流程解决
```

### 会话结束（RETROSPECTIVE 收尾）

```
1. 写所有输出到本地工作副本（经 outbox）
2. git add + commit + push 到 GitHub remote
3. push 失败（无 remote / 网络断 / 需先 pull）→ 本地 commit 已写好，下次会话 pull 后再 push，不阻塞
```

---

## 冲突解决

跨设备改同一文件 = 普通的 git 合并冲突。下次 `git pull` 时 git 标出冲突，按平常解决 git 冲突的方式处理。没有跨后端的特殊冲突逻辑。

---

## 删除规则

删除文件就是删除文件，由 git 追踪。`git pull` / `git push` 把删除像任何改动一样在设备间同步。

---

## 失败处理

| 场景 | 处理 |
|------|------|
| `git push` 时无 remote / 离线 | 本地 commit 已写好，记录提示，下次会话 pull 后再 push |
| remote 有未拉取的新提交 | push 被拒 → 先 `git pull` 合并（可能解决冲突）再 push |
| 新设备 | `git clone` 仓库 → 配置就绪 |

---

## 配置

存储在 `meta/config.md`（second-brain repo 中）：

```yaml
storage:
  type: git
  remote: "git@github.com:user/second-brain.git"   # 可选；纯本地用法可省略
```

跨设备同步通过普通 git remote 完成 —— 任何机器 `git clone` 后即可参与，会话开始 `git pull`、结束 `git push`。

无 second-brain → 配置存于会话上下文，ROUTER 每次新会话询问。

---

## 约束清单

- **多个会话可以同时操作 second-brain**，使用 outbox 模式。每个会话写入自己的 outbox 目录（`meta/outbox/{session_id}/`）。下次 Start Court 合并所有 outbox 到主结构。对共享文件（STATUS.md、meta/user-patterns.md、index.md）的直接写入只发生在 Start Court 的 outbox 合并步骤
- **Session-id 格式**：`{platform}-{YYYYMMDD}-{HHMM}`，在 adjourn 时生成（不是会话开始时）。示例：`claude-20260412-1700`、`gemini-20260412-1900`
- **Outbox 合并锁**：合并期间写 `meta/.merge-lock`。若存在且 <5 分钟，跳过合并照常进入。合并完成后删除
- **空会话**：若会话无输出（无决策、任务、日志条目），不创建 outbox
- 移动设备通过 git 把 markdown 提交进 `inbox/`（用手机 git 客户端或同步文件夹），不直接写结构化数据；下次桌面会话处理
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
