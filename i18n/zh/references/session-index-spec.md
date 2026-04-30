---
translated_from: references/session-index-spec.md
translator_note: auto-translated 2026-04-22, 待人工校对
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Session Index 规范（Session Index Specification）

Session index 是 Cortex 的 hippocampus（跨会话检索）的数据源。产出两份 artifact，**写入者（archiver）与编译者（retrospective）严格分离**。

## 1. 目的（Purpose）

session index 存在的意义是：让 hippocampus 子 agent 能在没有向量数据库、没有 SQLite、没有任何非 markdown 运行时的情况下，在每条消息上执行跨会话检索。按 `devdocs/architecture/cortex-integration.md` §3.1，检索由 LLM 驱动、读取一份编译好的纯文本索引 —— 扫描快、重建便宜、全 markdown 优先。

两份 artifact 分担负载：

- **`INDEX.md`** —— 每会话一行，由 retrospective 在 Start Session 编译。这是 hippocampus 首先读取的快扫面。
- **`{session_id}.md`** —— 带 YAML frontmatter 的结构化会话摘要，由 archiver 在会话结束时写入。仅在 `INDEX.md` 已缩小候选集之后，才会被 hippocampus 加载。

这种两层设计匹配大脑类比：`INDEX.md` 是 "会话梗概"，`{session_id}.md` 是 "完整的情节痕迹（episodic trace）"。hippocampus 先扫梗概，按需再取痕迹。

## 2. 文件位置（File Locations）

```
_meta/sessions/
├── INDEX.md                    # 由 retrospective 编译（Mode 0，在 Start Session）
└── {session_id}.md             # 由 archiver 写入（Phase 1，在会话结束时）
```

**session-id 格式**：`{platform}-{YYYYMMDD}-{HHMM}`

示例：
- `claude-20260419-1238`
- `gemini-20260420-0915`
- `codex-20260420-1403`

**HARD RULE（继承自 v1.4.4b）**：archiver MUST 执行 `date` 命令获取真实时间戳。伪造时间戳是流程违规。archiver 已经在 Phase 1 Step 2 强制这一点 —— session index 把同一个 session-id 复用为文件名。

## 3. 会话摘要模式（Session Summary Schema · `{session_id}.md`）

archiver 每会话恰好写一个文件。该文件写入后不可变。

### YAML Frontmatter（完整模式）

```yaml
---
session_id: string                      # required，格式 {platform}-{YYYYMMDD}-{HHMM}
date: ISO 8601 date                     # YYYY-MM-DD
started_at: ISO 8601 timestamp          # 带时区
ended_at: ISO 8601 timestamp            # 带时区
duration_minutes: integer
platform: claude | gemini | codex
theme: en-roman | en-us-gov | en-corporate | zh-classical | zh-cn-gov | zh-corporate | ja-meiji | ja-kasumigaseki | ja-corporate
project: string                         # 绑定的项目范围；会话绑定 HARD RULE 强制这一点
workflow: full_deliberation | express_analysis | direct_handle | strategist | review
subject: string                         # 在意图澄清时抽取，最多 200 字符
domains_activated:                      # 六个 domain 中哪些运行了
  - PEOPLE
  - FINANCE
  - GROWTH
  - EXECUTION
  - GOVERNANCE
  - INFRA
overall_score: float                    # 0-10，来自 Summary Report
domain_scores:
  FINANCE: float
  GOVERNANCE: float
  # ...只包含真正运行了的 domain
veto_count: integer                     # REVIEWER 否决事件次数（首轮通过为 0）
council_triggered: boolean              # COUNCIL 辩论是否触发？
soul_dimensions_touched:                # 被 REVIEWER 引用或被 ADVISOR 更新的维度
  - string
wiki_written:                           # 本会话自动写入的 wiki 条目 ID
  - entry_id
methods_used:                           # 本会话应用的 method library 中的 method ID
  - method_id
methods_discovered:                     # archiver 新添的 method
  - method_id
concepts_activated:                     # 会话期间引用的 concept ID
  - concept_id
concepts_discovered:                    # archiver Phase 2 写入的新 concept
  - concept_id
dream_triggers:                         # Phase 3 REM 中触发的 trigger 名
  - trigger_name
keywords:                               # 最多 10 个，用于 hippocampus Wave 1 扫描
  - string
action_items:
  - text: string
    deadline: ISO 8601 date
    status: pending | completed | dropped
compliance_violations: integer          # AUDITOR 标记的违规次数，干净为 0
---
```

### 正文（Body）

正文短、结构化、可读。不含原始消息内容。

```markdown
## Subject

{一段展开的主题。这是 "这个会话关于什么" 的答案。
必须独立成段 —— 只读这一段的读者应理解会话范围。最多 500 字符。}

## Key Decisions

1. {决策一 —— 一句话、以动作为导向}
2. {决策二}
3. {决策三}

## Outcome

{一段话总结决定了什么或达成了什么。包含 Summary Report 的 overall 评级。
最多 400 字符。}

## Notable Signals

- {narrator 层标记为对未来有参考意义的内容}
- {archiver 浮现的跨会话模式}
- {值得日后回看的未解张力}
```

**正文规则**：
- 不含原始消息引语
- 不含 PII（姓名、金额、账号）—— 遵循 archiver Phase 2 的隐私过滤器
- 不含任何 agent 的思考过程转储

## 4. INDEX.md 格式（INDEX.md Format）

每会话一行，最近在前，按月分组。这是 hippocampus 的扫描面。

### 行格式

```
{date} | {project} | {subject-truncated-80chars} | {overall_score}/10 | [{keywords-top3}] | {session_id}
```

### 示例

```markdown
# Session Index

## 2026-04

2026-04-19 | passpay | Technical whitepaper v0.5 to v0.6 refinement | 8.2/10 | [whitepaper, refinement, evidence] | claude-20260419-1238
2026-04-17 | life-os | v1.6.2 SOUL auto-write and DREAM 10 triggers design | 9.1/10 | [architecture, soul, dream] | claude-20260417-0902
2026-04-15 | passpay | Go-to-market positioning for Q3 launch | 7.8/10 | [gtm, positioning, launch] | claude-20260415-1510

## 2026-03

2026-03-28 | ledger-io | Schema migration risk review | 8.0/10 | [schema, migration, risk] | claude-20260328-1143
2026-03-22 | life-os | Theme system expansion to 9 themes | 8.6/10 | [theme, i18n, design] | claude-20260322-0834
```

### 格式规则

- 月份标题 `## YYYY-MM` —— 便于跳转导航与将来分片
- 月内按 `date desc` 排序（最近在上）
- `subject` 截断到 80 字符，截断则追加省略号
- Keywords 以逗号分隔列表置于方括号中，最多 3 个（完整 keyword 集位于会话摘要）
- 无行尾空白；月份区块之间一个空行

## 5. 写入流程（Write Flow）

### 会话摘要创建（archiver Phase 1 生成 session-id；Phase 2 写文件）

archiver 拥有写入的两端。session-id 生成留在 **Phase 1**（会话结束时需要一次真实 `date` 调用）。**文件写入移到 Phase 2 末尾**，因为摘要的 YAML frontmatter 引用了 Phase 2 输出（`wiki_written`、`methods_used`、`methods_discovered`、`concepts_activated`、`concepts_discovered`），这些在 Phase 1 运行时还不存在。Phase 2 的步骤列表见 `references/cortex-spec.md` Step 10。

```
Phase 1:
1. 会话结束 → orchestrator 启动 archiver 子 agent
2. archiver Phase 1 通过真实 `date` 命令生成 session-id
3. archiver 暂存已可收集的 metadata：
   - 时间戳（started_at / ended_at / duration_minutes）
   - 来自 orchestrator 追踪的 workflow 类型
   - 来自 Summary Report 的 domain scores 与 overall_score
   - 来自 AUDITOR 追踪的 veto_count 与 council_triggered
   - 来自 ADVISOR 报告的 SOUL 维度触达
   - 触发的 DREAM triggers（来自 Phase 3 triggered_actions YAML 块 —— Phase 3 在 Phase 2 之前运行）

Phase 2（在 wiki/SOUL 自动写入、concept 抽取 + Hebbian 更新、
method 候选探测、SYNAPSES-INDEX 重建、SOUL snapshot dump 之后）：
4. archiver 把 Phase 2 的输出填入暂存 metadata：
   - wiki_written 条目（来自 wiki 自动写入）
   - methods_used, methods_discovered（来自 method 候选探测）
   - concepts_activated, concepts_discovered（来自 concept 抽取）
5. archiver 抽取 keywords（§7）—— 最多 10 个
6. archiver 写入 _meta/outbox/{session_id}/sessions/{session_id}.md
7. 文件被加入 outbox 目录，与其他会话 artifact 一起做原子 git 提交
```

**不可变性（Immutability）**：archiver 写入后，文件永不再被编辑。若需更正（罕见），追加一份 `corrections/{session_id}.md` 备注，而不是改动原件。这与 journal 条目的不可变性相呼应 —— 仅追加，不重写。

**放在 outbox 下**：在 archiver Phase 1，新文件最初落在 `_meta/outbox/{session_id}/sessions/{session_id}.md`。outbox merge（retrospective Mode 0 Step 7）把它移到规范位置 `_meta/sessions/{session_id}.md`。这与决策、任务、journal 条目的现有 outbox 模式一致。

**失败模式**：

- `date` 命令不可用（极罕见）→ archiver 终止 Phase 1 并报清晰错误；没有真实时间戳就无法安全归档会话
- outbox 目录写入失败（磁盘满、权限）→ archiver 记录到 `_meta/sync-log.md`，不创建会话摘要文件，后续 retrospective 编译步骤直接把该会话从 INDEX 省略
- 部分 frontmatter（如 Summary Report 缺失）→ archiver 用哨兵值填入必填字段（`overall_score: null`、空数组）并继续；retrospective 解析器把 null 分数在 INDEX 中当作 `n/a`

### INDEX 编译（retrospective Mode 0）（INDEX compilation）

retrospective 只编译 —— 绝不写单会话文件。扩展既有 Mode 0 流程（见 `pro/agents/retrospective.md`）：

```
1. Start Session 触发
2. retrospective 枚举 _meta/sessions/*.md（glob 模式：*.md 排除 INDEX.md）
3. 对每个文件，解析 YAML frontmatter —— 抽取：
   - date
   - project
   - subject（截断到 80 字符）
   - overall_score（null 则渲染为 n/a）
   - keywords（取前 3）
   - session_id
4. 按 date desc 排序（同日次级排序：started_at desc）
5. 按从 date 字段派生的 YYYY-MM 分组
6. 以编译结果覆盖写入 _meta/sessions/INDEX.md
7. 若本次编译在结构上产生不同输出，在 retrospective 的 Start Session 报告中
   记下差异规模（"📚 Session Index: N sessions indexed"）
```

**编译是幂等的（idempotent）**。运行两次（给同样的输入文件）产生字节相同的输出。这点很重要，因为 retrospective 每次 Start Session 都运行 —— 不需要增量逻辑。幂等性也简化了调试：如果 index 看起来不对，删了重编不会丢数据。

**解析失败**：若某个 `{session_id}.md` 文件 YAML 格式错误，retrospective 把文件名记入 `_meta/sync-log.md` 并继续。损坏的会话被从 INDEX 省略，但文件本身保留以便人工检查。这与 v1.6.2 对 snapshot 损坏的姿态一致 —— 优雅降级，永不阻塞 Start Session 晨报。

## 6. 读取流程（Hippocampus）（Read Flow · Hippocampus）

hippocampus 子 agent 消费 session index。按 `devdocs/architecture/cortex-integration.md` §3.1 与三波激活模型：

```
1. Hippocampus 收到当前主题（来自 Step 0.5）
2. Hippocampus 读取 _meta/sessions/INDEX.md（一个文件，快）
3. LLM 判断识别语义上最相关的 top 5-7 会话
   - Wave 1：直接关键词匹配 keywords 列
   - Wave 2：与主题的语义邻近（LLM 对 80 字符主题短语作判断）
   - Wave 3：来自强 synapse 邻居的阈下激活（若 concept graph 可用）
4. 对每个入选会话，hippocampus 读取完整的 {session_id}.md
5. 返回 concept 级摘要给 GWT arbitrator（不直接给 ROUTER）
```

**每条消息的读取预算**：1 次 `INDEX.md` 读取（总是）+ 最多 7 次 `{session_id}.md` 读取（仅对存活候选）。按典型大小，每条消息 < 50KB 上下文、< 3 秒 LLM 扫描时间，满足 §8 的规模目标。

**本架构刻意不使用的东西**（来自 cortex brainstorm 的用户决策 #3）：

- **不使用 embeddings** —— 语义相似由 LLM 判断，不由向量计算。这避免了 embedding 模型漂移、embedding 提供商锁定、以及每次 schema 变更都要重建 embedding 的需要。
- **不使用 FTS5 或任何数据库** —— markdown 优先是 HARD RULE（见 `docs/architecture/markdown-first.md`）。所有检索基底都是纯文本并受 git 版本控制。
- **无后台索引守护进程** —— index 只在 Start Session 编译；读取按消息进行但限于 markdown I/O。无 cron、无 watchdog、无长驻进程。

性能演算（见 §8）确认这套方案可扩展到数千会话之后才需要分片。

**失败回退**：若 hippocampus 无法读取 `INDEX.md`（文件缺失、损坏、为空），它返回给 GWT arbitrator 一个空信号（`confidence: 0`），工作流降级为 v1.6.2a 行为 —— ROUTER 看到未加跨会话注释的原始用户消息。这匹配 `devdocs/architecture/cortex-integration.md` §5 Phase 1 kill-switch 设计中的 Cortex 降级策略。

## 7. Keyword 抽取规则（Keyword Extraction Rules）

Keywords 是 hippocampus 的 Wave 1 过滤器。archiver Phase 1 用如下程序选最多 10 个 keyword：

1. **项目名** —— 始终包含（1 个槽位）
2. **Domain 名** —— 包含 `domains_activated` 的每一项（最多 6 个槽位）
3. **主题内容词** —— LLM 从 subject 字符串抽取 top 3 内容词；排除停用词、动词、泛化名词（最多 3 个槽位）
4. **新颖 concept** —— 从 `concepts_discovered` 包含最多 3 项（最多 3 个槽位）
5. **总上限** —— 最多 10 个 keyword。若 1-4 步产出超 10 个，按以下顺序丢弃：新颖 concept（最旧优先）、主题词（显著性最低优先）、domain 名（分数最低优先）。项目名永不丢弃。

**输出形态**：小写字符串、单个 keyword 内无空格（用连字符）、每类内部按字母顺序。示例：`[passpay, finance, governance, whitepaper, refinement, evidence, zk-proof]`。

## 8. 规模上限（Scale Limits）

性能是本设计的承重部分 —— hippocampus 在每条用户消息上运行。规模预算匹配 `docs/architecture/markdown-first.md` §2：

| 会话数量 | INDEX.md 大小  | LLM 扫描时间 | 决策                                       |
|---------------|----------------|---------------|------------------------------------------------|
| 500           | ~500 行, 30KB  | <3 秒    | 快扫，无需优化           |
| 2000          | ~2000 行, 120KB | ~10 秒   | 仍可管理，监控尾延迟     |
| 5000+         | ~5000+ 行, 300KB+ | >10 秒   | 按年份对 INDEX 分片；触发数据库讨论 |

**分片触发**：当 `INDEX.md` 逼近 300KB，引入 `INDEX-{YYYY}.md` 文件（每年一份），再加一份 `INDEX.md` 清单链到它们。hippocampus 先读当年，若 Wave 1 失败才读更早年份。

**数据库升级触发**：若分片仍无法在极端规模下把扫描延迟恢复到 10 秒以下（每年成百上千会话、Wave 1 命中率下降），浮现给用户做显式决策。v1.7 不会自动引入数据库；markdown 优先规则成立，除非用户明确选择另作决定。

## 9. 从 v1.6.2a 迁移（Migration from v1.6.2a）

v1.7 之前不存在 `_meta/sessions/` 目录。迁移是尽力而为、一次性的，按 cortex brainstorm 的用户决策 #7：

`tools/migrate.py` 扫描近 3 个月的 `_meta/journal/`：

```
1. 枚举近 90 天创建的 _meta/journal/*.md
2. 对每份 journal 条目：
   a. 解析 metadata（日期、项目、决策标题）
   b. 合成 YAML frontmatter —— 尽力而为，承认缺口：
      - overall_score：存在则从 Summary Report 标题抽取，否则 null
      - domain_scores：存在则从 Summary Report 表抽取，否则空
      - veto_count, council_triggered：解析 trace 节，默认 0/false
      - soul_dimensions_touched, wiki_written, methods_used：留空
        （pre-v1.7 会话没有这些）
      - concepts_activated, concepts_discovered：留空（仅 v1.7）
      - dream_triggers：若时间戳匹配，从 -dream.md journals 抽取
      - keywords：LLM 从决策标题 + 项目抽取
   c. 从决策摘要与结果行合成正文节
   d. 写入 _meta/sessions/{synthesized-session-id}.md
3. 所有文件写完后，重编 _meta/sessions/INDEX.md
```

**迁移条目的 session-id**：`{platform}-{YYYYMMDD}-{HHMM}`，使用 journal 的修改时间戳。若无法推断原平台，默认 `claude`。

**超过 3 个月的会话不回填**。用户决策 #7 权衡：一旦会话 ≥3 个月，作为检索目标的价值已边际，而且合成质量会低（pre-v1.7 journals 缺少 schema 期望的结构化字段）。

迁移是幂等的：运行两次会用同样 session-id 覆盖任何先前迁移过的文件，因此重运行是安全的。

## 10. 反模式（Anti-patterns）

不要：

- **编辑既有会话摘要文件** —— archiver 写入后不可变。更正住在 `corrections/{session_id}.md`。改动会话摘要会使任何下游分析（趋势报告、DREAM 期模式探测）失效，因为它们从原件读取。
- **跳过 keyword 抽取** —— 零 keyword 的会话对 hippocampus Wave 1 扫描不可见。Phase 1 archiver 必须总是至少产出一个 keyword（项目名兜底）。
- **在 archiver 期间编译 INDEX** —— 编译是 retrospective 的职责。拆分职责会在两个平台并发结束会话时产生竞态，并把散朝延迟耦合到编译成本。
- **把原始消息内容放进会话摘要** —— 只放结构化抽取（subject、key decisions、outcome、signals）。原始消息属于 `_meta/journal/`，不属于这里。面向检索的摘要应比 journal 条目短，而不是它的拷贝。
- **把 `_meta/sessions/` 同步到 Notion** —— 按用户决策 #12，Cortex 数据留本地。Notion 承载用户的手机友好视图（STATUS、Todo、Working Memory、Inbox）；它不承载认知基底。
- **让 archiver 重试 session-id 生成** —— `date` HARD RULE 意味着每会话只调用一次 `date`。重试有使文件名与 `started_at` 时间戳漂移的风险。
- **增量编译 INDEX** —— 始终覆盖。幂等性是设计属性；不得为少量性能收益而交换它。
- **依赖文件修改时间排序** —— 按 frontmatter 的 `date` 字段排序。文件 mtime 可能因 git 操作或跨设备同步而漂移。
- **嵌入 §3 schema 之外的任意 metadata** —— 若新 signal 值得跟踪，就同步更新本 spec 与 archiver。自由形式的 frontmatter 扩展会破坏 retrospective 解析器、在 agent 之间造成静默漂移。
- **把 `{session_id}.md` 当作 journal 的替代** —— journal 条目记录详细的每角色报告（AUDITOR、ADVISOR、dream）；会话摘要是检索诱饵。两者共存。
- **不同平台采用不同的 session-id 格式** —— `{platform}-{YYYYMMDD}-{HHMM}` 方案在 claude / gemini / codex 间固定。平台特定前缀编码在第一段，而不是在格式本身。

## 11. 跨平台与并发（Cross-Platform and Concurrency）

Life OS 跑在 Claude、Gemini、Codex 上 —— 并且一个用户可能有多台设备。当两个平台几乎同时结束会话时，session index 必须表现得合理。

### 碰撞规避

`{platform}-{YYYYMMDD}-{HHMM}` session-id 是分钟级分辨率。同平台两个会话在同一分钟关闭会碰撞。实际中非常罕见（一个用户、一个平台上一次一个活跃会话），但规则是：

- archiver 不得覆盖既有文件。`Write` 之前，它检查文件名碰撞。
- 碰撞时，archiver 追加秒级后缀：`{platform}-{YYYYMMDD}-{HHMMSS}`。
- 碰撞情况记入 `_meta/sync-log.md` 以便后续审阅。

### outbox 合并并发

下次 Start Session 开始时，可能两台设备都在归档。Retrospective Mode 0 Step 7 已经用 `_meta/.merge-lock` 处理此情形。session index 随之搭车：

- 每个 outbox 目录自带 `sessions/{session_id}.md`。
- 合并逐个把它们移入 `_meta/sessions/`。
- 若两个 outbox 不知何故产出相同 session-id，合并通过追溯性追加秒级后缀保留两者，然后记录冲突。

### 跨设备 git 冲突

由于每份会话摘要各自独立成文件，两台设备并发写入产出独立文件 —— git 合并无冲突。这与使 journal 条目可安全共同书写的设计原则相同。

两个边缘情况：

- **`INDEX.md` 合并冲突** —— 始终通过重建解决。Retrospective Mode 0 把 `INDEX.md` 当作编译产物；绝不手编、绝不尝试三方合并。检测到冲突，删掉文件，让下次 Start Session 重编。
- **设备间时钟漂移** —— 若两台设备时钟不同步，session-id 在 INDEX 中可能乱序。§5 Step 4 的排序使用 `date` 字段（`started_at` 为破局者），小幅漂移被吸收。大漂移（>1 小时）是设备配置问题，超出本 spec 范围。

## 12. 完整示例（Worked Example）

用户就 `passpay` 项目关于白皮书精炼进行 90 分钟商讨。archiver 产出：

文件名：`_meta/outbox/claude-20260419-1238/sessions/claude-20260419-1238.md`

```yaml
---
session_id: claude-20260419-1238
date: 2026-04-19
started_at: 2026-04-19T12:38:04+09:00
ended_at: 2026-04-19T14:09:17+09:00
duration_minutes: 91
platform: claude
theme: zh-classical
project: passpay
workflow: full_deliberation
subject: Technical whitepaper v0.5 to v0.6 refinement — evidence chain tightening
domains_activated: [FINANCE, GROWTH, GOVERNANCE]
overall_score: 8.2
domain_scores:
  FINANCE: 7.8
  GROWTH: 8.4
  GOVERNANCE: 8.4
veto_count: 1
council_triggered: false
soul_dimensions_touched: [evidence-discipline, quality-over-speed]
wiki_written: [finance/zk-proof-verification-cost]
methods_used: [evidence-laddering-v2]
methods_discovered: []
concepts_activated: [zk-proof, whitepaper, evidence-chain]
concepts_discovered: [modular-evidence-scaffolding]
dream_triggers: []
keywords: [passpay, finance, governance, growth, whitepaper, refinement, evidence, zk-proof]
action_items:
  - text: Tighten Section 4.2 evidence chain with three concrete citations
    deadline: 2026-04-22
    status: pending
  - text: Replace Figure 3 with simpler proof-cost chart
    deadline: 2026-04-21
    status: pending
compliance_violations: 0
---
```

retrospective 编译步骤随后产出 `INDEX.md` 行：

```
2026-04-19 | passpay | Technical whitepaper v0.5 to v0.6 refinement — evidence chain | 8.2/10 | [passpay, finance, governance] | claude-20260419-1238
```

次日清晨，用户问及白皮书证据严谨性。hippocampus 读 INDEX，经 Wave 1 关键词匹配 `whitepaper` + `evidence` 识别该会话，加载完整摘要以告知 GWT arbitrator。

## 13. 操作手册（Operational Playbook）

常见操作的快查表：

| 情境 | 动作 |
|-----------|--------|
| 新会话正常关闭 | archiver Phase 1 写 `{session_id}.md`；retrospective 下次 Start Session 重编 INDEX |
| 用户编辑会话摘要（禁止） | AUDITOR 标记变更；用户通过 git 回滚；回滚前系统行为未定义 |
| 用户删除会话摘要 | 文件从 git 移除；下次 Start Session 编译会把该行从 INDEX 丢弃；该会话不再可检索 |
| 从 v1.6.2a 迁移 | 运行 `tools/migrate.py` 一次；对 journal 抽查核验；以一个 "v1.7 session index backfill" 提交落地结果 |
| 时钟 bug 产生错误时间戳 | 不要编辑；在 `corrections/{session_id}.md` 备注；可选追加指向纠正时间的手动更正条目 |
| INDEX.md 损坏 | 删掉文件；下次 Start Session 从权威源 `{session_id}.md` 重编 |
| 磁盘压力临近 | 见 §8 分片触发；没有明确用户决定不要删旧会话摘要 |

## 14. 相关规范（Related Specs）

- `references/soul-spec.md` —— SOUL 维度生命周期、snapshot 机制（平行模式：每会话文件 + INDEX 编译）
- `references/concept-spec.md` —— concept 在 `_meta/concepts/` 的存储，hippocampus 与 session index 一同查询
- `references/hippocampus-spec.md` —— 本 artifact 的消费者；定义三波激活
- `references/gwt-spec.md` —— 接收 hippocampus 输出的 GWT arbitrator
- `devdocs/architecture/cortex-integration.md` §3.1 —— 架构背景与扫描成本估算
- `docs/architecture/markdown-first.md` §2 与 §4 —— 性能基线与文件布局规则
- `pro/agents/archiver.md` —— `{session_id}.md` 的写入者，Phase 1 范围
- `pro/agents/retrospective.md` —— `INDEX.md` 的编译者，Mode 0 Start Session 职责

---

*本文译自英文版 2026-04-22 snapshot；英文为权威源。*
