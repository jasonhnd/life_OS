# 标准数据模型

所有 Life OS 数据操作使用这些标准类型和接口。适配器将它们翻译为平台特定的调用。

## 数据类型

### Decision（决策）

> ⚠️ **v1.9 schema 取代下表**（见 RFC §3.3.2 / §11.2.1 + `pro/CLAUDE.md` §"Decision Records"）。v1.9 是决策记录 frontmatter 的权威源；下方 pre-v1.9 字段保留用于历史参考 / 遗留文件解析。**字段名冲突提示**：v1.9 把 `type` 复用为决策记录种类（`change` / `no_change` / `escalation` / `superseded`），**不是** pre-v1.9 的 workflow 种类（`simple` / `3d6m`）。写新决策时用 v1.9 schema。

**v1.9 权威 schema**（`meta/decisions/<YYYY-MM>/dec-<YYYY-MM-DD>-<NNN>.md`）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | `dec-<YYYY-MM-DD>-<NNN>`（按天序号） |
| title | string | 是 | 短标题 |
| type | enum | 是 | `change` / `no_change` / `escalation` / `superseded` |
| projects | string[] | 是 | 所属项目；`[]` = 跨项目 |
| domains | string[] | 是 | 6 functional IDs 的子集：governance/execution/finance/infra/people/growth |
| reviewed_by | string | 是 | agent 或 human |
| reviewed_at | date | 是 | ISO 日期 |
| decision | text | 是 | 一句话决策 |
| rationale | text | 是 | 理由 |
| reopen_condition | text | 条件 | 当 `type: no_change` 时必填 |
| supersedes / superseded_by | string[] / string | 否 | 决策谱系 |
| applied_methods | string[] | 否 | 应用的方法（列表；Opt #8） |
| journal_date | date | 否 | 当天的 journal 文件（Opt #8） |
| content | text | 是 | Summary report 全文（正文） |

<details><summary>Pre-v1.9 字段（遗留，新决策勿用）</summary>

| 字段 | 类型 | 说明 |
|------|------|------|
| type | enum | `simple` / `3d6m`（workflow —— 被 v1.9 `type` 取代） |
| status | enum | `considering` / `decided` / `reversed` |
| category | enum | `career` / `finance` / `product` / `tech` / `family` / `life` / `health` |
| outcome | enum | `good` / `neutral` / `bad` / `tbd` |
| score / veto_count | number | 综合评分 / 封驳事件 |
| date / project / area | — | 被 `reviewed_at` / `projects` /（area 经由 project）取代 |

</details>

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

## v1.7 Cortex 数据类型

以下类型在 v1.7 为 Cortex 认知层引入。每个都有自己的权威 spec 文件；下表是其简表形式。

### SessionSummary

权威 spec：`references/session-index-spec.md` §3。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 格式 `{platform}-{YYYYMMDD}-{HHMM}` |
| date | date | 是 | ISO 8601 日期 |
| started_at | datetime | 是 | 带时区的时间戳 |
| ended_at | datetime | 是 | 带时区的时间戳 |
| duration_minutes | integer | 是 | |
| platform | enum | 是 | `claude` / `gemini` / `codex` |
| theme | enum | 是 | 主题 ID（如 `zh-classical`、`ja-kasumigaseki`） |
| project | string | 是 | 绑定的项目（强制 session-binding HARD RULE） |
| workflow | enum | 是 | `full_deliberation` / `express_analysis` / `direct_handle` / `strategist` / `review` |
| subject | string | 是 | 提取的主题（≤200 字符） |
| domains_activated | string[] | 否 | PEOPLE/FINANCE/GROWTH/EXECUTION/GOVERNANCE/INFRA 的子集 |
| overall_score | number | 否 | 来自 Summary Report 的 0-10 |
| domain_scores | map | 否 | 各领域 0-10 分 |
| veto_count | integer | 否 | REVIEWER 封驳事件 |
| council_triggered | boolean | 否 | 是否触发 COUNCIL 辩论？ |
| soul_dimensions_touched | string[] | 否 | 引用的 SOUL 维度 ID |
| wiki_written | string[] | 否 | 本 session 自动写入的 wiki 条目 ID |
| methods_used | string[] | 否 | 应用的 Method ID |
| methods_discovered | string[] | 否 | 新归档的 Method ID |
| concepts_activated | string[] | 否 | 引用的 Concept ID |
| concepts_discovered | string[] | 否 | archiver Phase 2 写入的新 Concept ID |
| dream_triggers | string[] | 否 | 触发的 DREAM REM trigger 名 |
| keywords | string[] | 否 | 最多 10 个，供 hippocampus Wave 1 扫描 |
| action_items | array | 否 | `[{text, deadline, status}]` |
| compliance_violations | integer | 否 | AUDITOR 标记的违规 |

存储：`meta/sessions/{session_id}.md`。archiver 写入后不可变。

### Concept

权威 spec：`references/concept-spec.md` §YAML Frontmatter Schema。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| concept_id | string | 是 | 小写 + 连字符，≤64 字符，唯一 |
| canonical_name | string | 是 | 人类可读的显示名 |
| aliases | string[] | 否 | 其他表面形式 |
| domain | enum | 是 | `finance` / `startup` / `personal` / `technical` / `method` / `relationship` / `health` / `legal` / 用户可扩展 |
| status | enum | 是 | `tentative` / `confirmed` / `canonical` |
| permanence | enum | 是 | `identity` / `skill` / `fact` / `transient` |
| activation_count | integer | 是 | 活跃期内单调递增 |
| last_activated | datetime | 是 | 供 decay pass 使用 |
| created | datetime | 是 | 创建时间戳 |
| outgoing_edges | array | 否 | `[{to: concept_id, weight: 1-100, via: [tag], last_reinforced: ISO}]` |
| provenance.source_sessions | string[] | 否 | 证据出现的 session ID |
| provenance.extracted_by | enum | 否 | `archiver` / `manual` / `dream` |
| decay_policy | enum | 是 | 匹配 `permanence` 层级 |

存储：`meta/concepts/{domain}/{concept_id}.md`（confirmed/canonical）或 `meta/concepts/_tentative/{concept_id}.md`（tentative）。

### SoulSnapshot

权威 spec：`references/snapshot-spec.md` §YAML Frontmatter Schema。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| snapshot_id | string | 是 | `{YYYY-MM-DD-HHMM}`，与文件名一致 |
| captured_at | datetime | 是 | 来自系统时钟的真实 ISO 8601 时间戳 |
| session_id | string | 是 | 引用 `meta/sessions/{session_id}.md` |
| previous_snapshot | string \| null | 是 | 上一个文件名，首个快照为 null |
| dimensions | array | 是 | `[{name, confidence: 0-1, evidence_count, challenges, tier}]`，其中 tier ∈ `core`/`secondary`/`emerging` |

存储：`meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md`。仅元数据 —— 无 SOUL 正文内容。不可变。

### EvalEntry

权威 spec：`references/eval-history-spec.md` §3。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| eval_id | string | 是 | `{YYYY-MM-DD-HHMM}-{project}` |
| session_id | string | 是 | 引用 `meta/sessions/` 条目 |
| evaluator | enum | 是 | `auditor` / `auditor-patrol` |
| evaluation_mode | enum | 是 | `decision-review` / `patrol-inspection` |
| date | datetime | 是 | |
| scores | map | 是 | 10 个维度，每个 0-10 整数（见 eval-history-spec §5） |
| violations | array | 否 | `[{type, agent, severity, detail}]` |
| agent_quality_notes | map | 否 | 各 agent 一行观察 |

存储：`meta/eval-history/{YYYY-MM-DD}-{project}.md`。仅本地。创建后不可变。无迁移回填。

### Soul

权威 spec：`references/soul-spec.md`。与其他 v1.7 类型不同，`Soul` 是**实时 `SOUL.md` 文件的内存视图**，不是 per-record 文件。工具读取整个 SOUL.md，解析为此结构，并（对 archiver 侧自动写入）写回。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | Path | 是 | `SOUL.md` 的绝对路径 |
| dimensions | `List[SoulDimension]` | 是 | 所有解析出的维度（新用户可能为空） |
| raw_body | str | 是 | 完整 markdown 正文（供基于 diff 的写入） |

`SoulDimension` 子记录：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | 是 | 维度名（如 "risk-tolerance"） |
| confidence | float | 是 | 0-1，经 `evidence_count / (evidence_count + challenges × 2)` 自动计算 |
| evidence_count | int | 是 | |
| challenges | int | 是 | |
| source | enum | 是 | `dream` / `advisor` / `strategist` / `user` |
| created | date | 是 | YYYY-MM-DD |
| last_validated | date | 是 | YYYY-MM-DD |
| tier | enum | 自动 | `core`（≥0.7）/ `secondary`（0.3-0.7）/ `emerging`（0.2-0.3）/ `dormant`（<0.2）—— 读取时派生 |
| what_is | str | 否 | 正文段落 "What IS (实然)" |
| what_should_be | str | 否 | 正文段落 "What SHOULD BE (应然)" |
| gap | str | 否 | 正文段落 "Gap (差距)" |
| evidence | `List[str]` | 否 | 正文 "Evidence" 项 |
| challenges_list | `List[str]` | 否 | 正文 "Challenges" 项 |

存储：second-brain 根目录的单一文件 `SOUL.md`。被每个主要角色读取；由 ARCHIVER Phase 2（soul-spec 中的自动写入标准）和用户直接写入。

### Method

权威 spec：`references/method-library-spec.md` §4。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| method_id | string | 是 | 小写 + 连字符，唯一 |
| name | string | 是 | 显示名 |
| description | string | 是 | INDEX.md 用的一句话 |
| domain | enum | 是 | 与 Concept 相同的 domain 词汇 |
| status | enum | 是 | `tentative` / `confirmed` / `canonical` |
| confidence | number | 是 | 0-1，公式 `evidence_count / (evidence_count + challenges × 2)` |
| times_used | integer | 是 | 每次应用该方法的 session 递增 |
| last_used | datetime | 否 | ISO 8601 |
| applicable_when | array | 否 | `[{condition, signal}]` |
| not_applicable_when | array | 否 | `[{condition}]` |
| source_sessions | string[] | 否 | 贡献的 session_id |
| evidence_count | integer | 是 | 方法生效的 session 数 |
| challenges | integer | 是 | 方法失败的 session 数 |
| related_concepts | string[] | 否 | concept_id |
| related_methods | string[] | 否 | method_id（软组合） |

存储：`meta/methods/{domain}/{method_id}.md` 或 `meta/methods/_tentative/{method_id}.md`。仅本地。

---

## 标准操作

所有代理使用这些操作。适配器将它们翻译为平台特定的调用。

| 操作 | 签名 | 说明 |
|------|------|------|
| **Save** | `Save(type, data)` | 创建新记录 |
| **Update** | `Update(type, id, data)` | 修改现有记录 |
| **Archive** | `Archive(type, id)` | **v1.9 语义变更**（DR-1.9.4）：对项目，在 frontmatter 设置 `lifecycle_stage: archived` + `archived_at` + `archived_at_source`；**不**物理移动目录（保留 wikilink）。对其他类型（decisions/sessions），仍沿用旧的归档语义。 |
| **Read** | `Read(type, id)` | 获取单条记录 |
| **List** | `List(type, filters)` | 获取符合过滤条件的记录。**v1.9**：`List(Project, ...)` 默认过滤 `lifecycle_stage != archived`；传 `include_archived: true` 可覆盖。 |
| **Search** | `Search(keyword)` | 跨所有类型全文搜索 |
| **ReadProjectContext** | `ReadProjectContext(project_id)` | 批量读取：项目 index + 任务 +（v1.9 更新）经 projects 字段从 `meta/decisions/<YYYY-MM>/` 交叉引用的决策 + 经 projects 字段从 `meta/journal/` 的日志 |

### v1.9 archive 语义（见 RFC §3.4 + DR-1.9.4）

Pre-v1.9：`Archive(Project, id)` = `mv projects/{id}/ archive/{id}/` —— 破坏所有指向 `[[projects/{id}/...]]` 的 wikilink。

v1.9：`Archive(Project, id)` = `Update(Project, id, {lifecycle_stage: archived, archived_at: <today>, archived_at_source: auto, archived_reason: <description>})`。项目仍留在 `projects/{id}/`。所有 wikilink 保持可解析。

Index 编译器（retrospective Mode 0 → STATUS.md / STRATEGIC-MAP.md，archiver Phase 1 → STATUS 更新）默认过滤 `lifecycle_stage: archived`。Obsidian graph view 用 colorGroup 把归档项目显示为灰暗色。wiki/INDEX **不**过滤（历史知识保持可见）。

`archived_at_source` enum（4 值，见 DR-1.9.26）：
- `git-log` —— `/migrate-v1.9` Stage 3 从 git log 时间戳推导
- `migrated-unknown` —— `/migrate-v1.9` 当 git log 无返回时的兜底
- `manual` —— 用户手改 frontmatter
- `auto` —— archiver/REVIEWER 在正常 session 流程中自动归档

---

## 存储后端（GitHub + 本地工作副本）

Life OS 使用**单一存储后端**：一个 git 仓库。second-brain 以磁盘上的本地工作副本形式存在（同时也是你的 Obsidian vault）；GitHub 是为其做备份并跨设备同步的远端。没有主/同步之分、没有按后端探测、没有跨后端冲突层 —— git 原生提供版本、备份和多设备同步。

> 以前还提供 Google Drive 和 Notion 作为可选后端，配有多后端同步协议；两者已移除——存储仅 GitHub。

### 读 / 写

- **读** —— 从本地工作副本（磁盘上的文件）。
- **写** —— 写入本地工作副本。向 GitHub 远端的持久化在 session 结束时经由 git 完成（ARCHIVER Phase 4）。

---

## 同步协议

同步就是纯 git —— 没有 MCP 探测、没有 primary/sync 之分、没有按平台的 `last_sync` 记账。git 历史就是"自上次以来改了什么"的记录。

### Session 开始（RETROSPECTIVE 家政）

```
1. `git pull`（fetch + merge）second-brain 仓库，吸收其他设备推送的变更。
2. 非 git 仓库 / 未配置远端 → 仅在本地工作副本上操作；标注"💾 存储：仅本地（无远端）"。
3. pull 时 merge 冲突 → 把冲突文件呈现给用户解决（单用户 vault 极少发生）。
```

### Session 结束（ARCHIVER Phase 4）

```
1. 将 session outbox 合并到主结构（见 约束条件 · outbox 模式）。
2. `git add` + `git commit` session 的变更。
3. `git push` 到远端。push 失败（离线 / 无远端）→ 标注"⚠️ 未推送 —— 下次 session 同步"，提交保留在本地。
```

---

## 冲突解决

单一后端意味着没有跨后端分叉。唯一的冲突来源是两台设备在两次同步之间编辑了同一文件，它在 `git pull` 时表现为 **git merge 冲突**：

| 情况 | 处理方式 |
|------|---------|
| 干净 pull（无重叠） | 快进 / 自动合并，继续 |
| 同一文件在两台设备被编辑 | git merge 冲突 → ROUTER 呈现冲突文件，用户解决，提交解决结果 |

outbox 模式（每个 session 一个目录）让同一文件冲突即使在并发本地 session 下也极少发生。

---

## 删除规则

- 删除是普通的 git 操作（`git rm` / 删文件 + 提交）。它像任何其他变更一样在下次 push/pull 时传播。
- 没有软删除 `_deleted: true` 墓碑，也没有跨后端删除提示 —— 那些只是为了协调多个后端而存在。

---

## 故障处理

| 场景 | 处理方式 |
|------|---------|
| session 结束时远端不可达 | 本地提交，跳过 push，标注 ⚠️。下次 session 的 `git push` 补上。 |
| pull 时 merge 冲突 | 呈现冲突文件；用户解决后再继续。 |
| 非 git 仓库 / 无远端 | 仅在本地工作副本上操作；不推送任何东西。产出仍在对话中显示。 |
| 新设备 | `git clone` second-brain 仓库 → 就绪。无 second-brain → session 级别配置。 |

---

## 配置

git 远端存在仓库自己的 `.git/config` 里 —— Life OS 不重复存储它。`meta/config.md` 不再携带 `storage.backends` 列表或按平台的 `last_sync` 时间戳（git 历史就是"自上次以来改了什么"的真实来源）。

```yaml
# meta/config.md（storage 段）
storage:
  remote: github          # 单一后端；"none" = 仅本地工作副本
```

无 second-brain → ROUTER 在 session 本地操作（不持久化）。

---

## 约束条件

- **多个 session 可同时操作 second-brain**，使用 outbox 模式。每个 session 写入各自的 outbox 目录（`meta/outbox/{session-id}/`）。下一个上朝的 session 将所有 outbox 合并到主结构中。直接写入共享文件（STATUS.md、meta/user-patterns.md、index.md）只在上朝时的 Outbox 合并步骤中发生。
- **session-id 格式**：`{platform}-{YYYYMMDD}-{HHMM}`，在退朝时生成（非 session 开始时）。时间戳必须通过 date 命令从系统时钟获取，禁止编造。示例：`claude-20260412-1700`、`gemini-20260412-1900`。
- **Outbox merge lock**：合并期间写入 `meta/.merge-lock`。若该文件存在且时间 < 5 分钟，跳过合并正常进行。合并完成后删除。
- **空 session**：若 session 无任何产出（无决策、任务或日志），不创建 outbox。
- 移动端捕获经由用户自己的 git 工作流（移动 git 客户端 / 同步文件夹）落入 `inbox/`，不直接写入结构化数据；在下一次桌面 session 处理
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
