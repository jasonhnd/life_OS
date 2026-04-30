---
translated_from: references/method-library-spec.md
translator_note: auto-translated 2026-04-22, 待人工校对
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Method Library 规范（Method Library Specification）

Method Library 是 Life OS 的**程序性记忆（procedural memory）**—— "你如何工作最顺手"那一层。它位于 second-brain 的 `_meta/methods/` 目录下，存放跨会话复现的可复用工作流。

## 1. 目的（Purpose）

Life OS 维护三个独立的记忆层：

| 层（Layer） | 回答的问题 | 示例 |
|-------|--------------------|---------|
| Wiki | "关于世界有什么是真的？" | "日本的 NPO 贷款不享有贷金业法（貸金業法）豁免" |
| SOUL | "你是谁？" | "风险偏好：中高" |
| Methods | "你如何工作最顺手？" | "文档精炼分 5 轮升阶质量：结构 → 内容 → 精度 → 润色 → 发版审计" |

Methods 是**可复用的工作流（reusable workflows）**—— 适用于跨决策场景的程序性模式。它与 wiki 相邻（两者都是跨项目知识），但形态不同：wiki 回答事实问题，methods 描述动作序列。

灵感来自 Hermes Skills（参见 `devdocs/research/2026-04-19-hermes-analysis.md`），但针对 Life OS 的决策引擎上下文作了适配。Hermes skills 编码工具使用程序；Life OS methods 编码决策制定程序。

---

## 2. 什么符合 Method 的标准（What Qualifies as a Method）

**是**：
- "5 轮升阶质量的迭代式文档精炼"
- "创业融资时机：12 个月 runway 是触发线"
- "向团队委派：责任 × 授权矩阵"
- "谈判涨价：用数据锚定，给出三个选项"

**否**（应放在别处）：
- 具体事实 → `wiki/`
- 个人偏好或价值观 → `SOUL.md`
- 项目特定的计划 → `projects/{name}/`
- 一次性小贴士 → `inbox/` 或 `user-patterns.md`

**标准**：method 是一个可复用工作流，能跨不同项目的不同决策应用。如果该模式只在一个项目里才说得通，它应属于该项目，而不是 method library。

---

## 3. 文件位置（File Location）

按用户决策 #11（method library 在 v1.7 引入）：

```
_meta/methods/
├── INDEX.md                        # 编译摘要（auto-generated）
├── _tentative/                     # 等待用户确认的候选 method
│   └── {method_id}.md
├── _archive/                       # dormant method（闲置 12+ 月）
│   └── {method_id}.md
└── {domain}/
    └── {method_id}.md
```

Methods 不在 `wiki/` 之下。独立概念，独立根目录。与 `wiki/` 的平行关系是刻意为之：两者都是跨项目知识，都自动编译进 INDEX，都由用户事后确认。

Domain 目录镜像系统级 domain 列表（与 `references/concept-spec.md §Domain partitions` 和 `references/wiki-spec.md §Positioning` 对齐）：`finance`、`startup`、`personal`、`technical`、`method`、`relationship`、`health`、`legal`，加上任何用户自定义 domain。

---

## 4. YAML Frontmatter 模式（YAML Frontmatter Schema）

每个 method 文件以如下 frontmatter 块开头：

```yaml
---
method_id: string                     # 小写、连字符、唯一（例如 iterative-document-refinement）
name: string                          # 显示名称（例如 "Iterative Document Refinement"）
description: string                   # INDEX 里的一行描述
domain: string                        # finance | startup | personal | technical | method | relationship | ...
status: enum                          # tentative | confirmed | canonical
confidence: float                     # 0-1，与 SOUL/wiki 使用相同公式
times_used: integer                   # 每次应用该 method 的会话都会 +1
last_used: string                     # ISO 8601 时间戳
applicable_when:
  - condition: string                 # 自然语言条件
    signal: string                    # 触发该条件的具体 signal
not_applicable_when:
  - condition: string                 # method 失效的反条件
source_sessions: [string]             # 贡献过该 method 的 session_id
evidence_count: integer               # method 起作用的会话数
challenges: integer                   # method 失败的会话数
related_concepts: [string]            # 来自 concept-spec 的 concept_id
related_methods: [string]             # method_id —— 启用组合（见第 16 节）
---
```

`confidence` 由 SOUL 与 wiki 所使用的同一个公式推导：

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

下限 0，上限 1。该公式在各记忆层保持一致，这样 agent 不必在不同尺度之间翻译。

---

## 5. 正文格式（Body Format）

frontmatter 之后，每个 method 遵循如下形状：

```markdown
# Method Name

## Summary
一段话描述 method 做什么以及为什么有效。

## Steps
1. Step 1 —— 做什么，为什么重要
2. Step 2 —— 做什么，为什么重要
3. ...

## When to Use
- 指示该 method 适用的条件
- 当前主题中要留意的 signal

## When NOT to Use
- method 失效或误导的反条件
- 已知反例

## Evolution Log
- 2026-04-15: 首次在 4 轮文档精炼流程中观察到
- 2026-04-19: 在 5 轮流程中确认，新增 step 5（发版审计）

## Warnings
- 常见陷阱与失效模式

## Related
- [[concept-link]] —— 该 method 引用或细化的 concept
- [[other-method-id]] —— 相关 method（同胞或组合）
```

长度目标：每个 method 30–80 行。超出通常意味着该 method 该被拆分，或者一个假扮为 method 的项目计划。

---

## 6. 自动创建（由 archiver）（Auto-Creation by archiver）

Method 候选由 `archiver` Phase 2（参见 `pro/agents/archiver.md`）探测，使用与产出 wiki 和 SOUL 候选项相同的基础设施。

**触发条件**：当前会话工作流中观察到的一个可重复模式匹配已有 method 签名，或一个净新（net-new）的模式满足启发规则。

**净新候选的启发规则**：
- 会话工作流中的 5+ 个连续动作构成一个连贯程序
- 相同模式已在 ≥2 个历史会话中观察到（经 hippocampus / session index 查询）
- 用户用诸如 "approach"、"pattern"、"framework"、"process"、"流れ"、"やり方" 这样的语言描述过它

**反启发规则**（取消候选资格）：
- 模式恰好只在一个会话出现、无跨会话回声
- 模式特属于某一个项目的上下文
- 模式与某个现有 canonical method 重复

**检测到候选时**：

1. 生成一份 method 草稿，带：
   - `status: tentative`
   - `confidence: 0.3`
   - `times_used: 1`
   - `source_sessions: [current_session_id]`
   - `evidence_count: 1`
2. 与现有 methods 比对（先按 `method_id` 精确匹配，再按描述相似度 ≥ 0.7 与 INDEX 比对）
3. 若重复 → 在已有 method 上 `evidence_count += 1`，更新 `last_used`，写入 Evolution Log —— 不创建新候选
4. 若新 → 写入 `_meta/methods/_tentative/{method_id}.md`
5. 记入会话的 Completion Checklist，以便 RETROSPECTIVE 在下次 Start Session 提出

archiver 自己不会把候选提升过 `tentative`。提升需要用户输入（第 7 节）或证据累积（第 8 节）。

---

## 7. 用户确认工作流（User Confirmation Workflow）

在下次 Start Session，RETROSPECTIVE 会在晨报中包含 method 候选块：

```
Method candidates detected:
"Iterative Document Refinement" (observed in 2 sessions)
  Summary: 5-round escalating quality process
  (c) Confirm — move to confirmed, start applying
  (r) Reject — delete
  (e) Edit — open for user editing
  (s) Skip — decide later
```

用户响应：
- `c` 或 "confirm X" → 将文件从 `_meta/methods/_tentative/` 移到 `_meta/methods/{domain}/`，翻转 `status: tentative` → `confirmed`，confidence 提升到 0.5（若 source_sessions 已有 3+ 则为 0.6）
- `r` 或 "reject X" → 删除文件
- `e` 或 "edit X" → 打印文件路径，用户编辑，状态不变
- `s` 或 "skip" → 留在 `_tentative/`，下次 Start Session 再次浮现

若一个候选在 `_tentative/` 里连续 5 次 Start Session 都没有用户响应，archiver 自动归档它。沉默 ≠ 同意，但无限待定状态比让它离开更糟。

---

## 8. 提升阶梯（Promotion Ladder）

Methods 经过三个成熟度 tier。提升遵循证据，不遵循时间。

| Status | 要求 | Confidence 范围 | 系统行为 |
|--------|-------------|------------------|-----------------|
| tentative | 1 次会话观察 | 0.3 | 对 dispatcher 隐藏。住在 `_tentative/`。 |
| confirmed | ≥2 次会话 + 用户确认 | 0.5–0.6 | 适用时由 dispatcher 注入。 |
| canonical | ≥5 次使用 + confidence ≥ 0.7 | 0.7–1.0 | 全量 dispatcher 注入 + 可在 Summary Report 中按名引用。 |

**自动提升**：
- tentative → confirmed：需要用户输入（第 7 节）。永不自动。
- confirmed → canonical：当 `times_used ≥ 5` 且 `confidence ≥ 0.7` 且近 3 次使用无 challenges 时自动。

**降级（Demotion）**：
- 任何 method 若因累积的 challenges 使其 confidence 跌破 0.3，会被标记请用户审阅，而不是自动降级。
- 用户可随时在 frontmatter 手动设置 status。

---

## 9. DISPATCHER 的使用（Use by DISPATCHER）

当 Draft-Review-Execute 工作流到达 Step 4（DISPATCHER Dispatch）时，dispatcher 执行一次 method 查找：

```
1. 读取 _meta/methods/INDEX.md
2. 对每个 confirmed/canonical method，用当前主题评估 applicable_when 条件
3. 若某 method 匹配 → 将其完整正文作为 "Known Method" 包含在相关 domain 的 dispatch 上下文中
4. 明确标注："Known Method '{name}' applies — here is the established approach, use it unless the subject contradicts."
```

例子：一个关于精炼商业计划书的会话到达 dispatcher。`iterative-document-refinement` method 匹配。DISPATCHER 将其正文注入执行 domain 的 brief。执行 domain 开始分析时就知道用户已经有一套验证过的 5 轮精炼模式 —— 与其重新发明一套 approach，不如应用已知 method 并回报。

这防止 domain agent 重复推导用户已经通过经验换来的工作流。

**多个匹配**：若 2+ 个 method 适用，DISPATCHER 把它们全部传递并加备注："Multiple known methods apply — use in sequence or as alternatives, domain to judge fit."

**无匹配**：DISPATCHER 照常进行 —— domain 从头推导 approach。

---

## 10. 演化 / 更新（Evolution / Updates）

每个应用了 method 的会话都会更新它的状态：

- `times_used += 1`
- `last_used` = 会话时间戳
- Evolution Log 新增一行：`{date}: {一句话结果 —— 起作用、失败、修订}`
- 若会话显示 method 起了作用（AUDITOR 未标记流程问题，REVIEWER 首轮通过）：`evidence_count += 1`
- 若会话显示 method 失败（用户推翻、REVIEWER 以 method 相关理由否决、AUDITOR 标记不匹配）：`challenges += 1`
- `confidence` 用标准公式重新计算

**小修订**（措辞澄清、增加警告）由 archiver Phase 2 在无用户确认下直接应用。

**重大修订**（增删步骤、条件变更）需在下次 Start Session 取得用户确认。archiver 把拟议变更写到 `_meta/methods/_tentative/_revisions/{method_id}-{date}.md`，并与新候选一起浮现。

---

## 11. 衰减（Decay）

Methods 使用 `permanence: skill` 衰减 —— 对数衰减到一个下限，而不是完全蒸发。挣来的程序性知识应当难以遗忘。

| 自 last_used 起经过 | 状态 | 动作 |
|--------------------------|-------|--------|
| ≤ 6 个月 | Active | 无动作 |
| 6–12 个月 | Dormant | RETROSPECTIVE 在 briefing 中标记："Method '{name}' has been dormant for N months." |
| ≥ 12 个月 | Archived | archiver 将文件移到 `_meta/methods/_archive/{method_id}.md`。 |
| Archived + 用户明确删除 | Retired | 文件消失。即使该模式重新出现也不自动重建。 |

Methods 从不自动删除。Methods 是挣来的；归档是系统采取的最强自动动作。最终删除始终由用户决定。

---

## 12. 范围守卫（隐私）（Scope Guards · Privacy）

与 wiki 条目相同的隐私过滤器（见 `references/wiki-spec.md` 第 "Privacy Filter" 节）也适用于 method 正文：

- 不得在 method 文本中包含人名 —— 写入前剥离
- 不得在 method 正文中引用具体项目 —— 项目引用只能出现在 `source_sessions` 里
- 不得包含具体金额、账号或 ID 号 —— 所有数字示例保持泛化（用 "~12 months runway"，而不是 "¥8,400,000"）
- 不得包含可追踪的 日期 + 地点 组合
- 不得包含具体公司名，除非 method 真的关于那家公司（罕见）

若剥离这些引用后 method 变得没意义 → 该模式其实不可复用，丢弃这个候选。

Methods 仅本地存储。永不同步到 Notion（用户决策 #12）。

---

## 13. INDEX.md 格式（INDEX.md Format）

`_meta/methods/INDEX.md` 由 RETROSPECTIVE 在每次 Start Session 基于实际 method 文件编译。绝不手工编辑。

```markdown
# Method Library Index
compiled: YYYY-MM-DD

## canonical (5)
- iterative-document-refinement | Refine documents in 5 escalating quality rounds | used 12 times | 0.85
- runway-fundraise-trigger | Start fundraising when runway drops below 12 months | used 7 times | 0.78
- ...

## confirmed (8)
- responsibility-authority-matrix | Delegate by mapping responsibility × authority | used 3 times | 0.55
- ...

## tentative (3)  [awaiting user confirmation in _tentative/]
- weekly-review-reset | Reset every Friday by listing completions and drops | observed 2 sessions | 0.30
- ...

## dormant (1)  [≥6 months since last use]
- quarterly-strategic-review | Quarterly strategic reset framework | last used 2025-10-14 | 0.62
```

每行 ≤ 100 字符。整个 INDEX 通常 30–120 行。加载便宜，扫描容易。

---

## 14. 与 Hermes Skills 的交互（Interaction with Hermes Skills）

Hermes Skills 是工具使用的程序性记忆（如何调用 API、如何格式化 shell 命令）。Life OS methods 是决策制定的程序性记忆（如何评估一个选项、如何精炼一份文档、如何把握融资时机）。

| 维度 | Hermes Skill | Life OS Method |
|-----------|--------------|----------------|
| 范围 | 工具操作 | 决策工作流 |
| 激活 | 显式语法（`@skill:name`） | 由 dispatcher 条件匹配自动触发 |
| 安全扫描 | 必需（可执行代码） | 不需要（仅用户确认过的文本） |
| 生命周期 | Skills 显式版本 | Methods 通过 Evolution Log 演化 |

method library 借用了 Hermes 的 YAML + markdown + evolution log 模式，但去掉了 Hermes 在工具使用上下文中所需的部分（激活语法、安全扫描、版本锁定）。

---

## 15. 从 v1.6.x 迁移（Migration from v1.6.x）

v1.6.2a 没有 method library。`tools/migrate.py` 从已有会话历史回填：

1. 扫描 `_meta/journal/*.md` 和回填的决策，查找描述 approach 的语言："approach"、"pattern"、"framework"、"process"、"流れ"、"やり方"、"手順"。
2. 抽取被跨会话提及次数最多的前 5 个模式。
3. 把每一个作为候选写到 `_meta/methods/_tentative/{method_id}.md`，`status: tentative`、`confidence: 0.3`。
4. 在下次 Start Session 标记给用户审阅。

迁移是一次性（one-shot）的。之后的模式探测由 archiver Phase 2 在活会话上进行。

迁移脚本不会把任何东西提升过 tentative。用户决定任一回填模式是否真的变成 confirmed method。

---

## 16. v1.7 明确不在范围内（Out of Scope for v1.7）

明确不在 v1.7 范围内：

- **参数化 methods** —— "iterative refinement with N rounds" 到底是一个参数化 method 还是 N 个 method？v1.7 仅采用原子 methods。
- **版本化历史** —— methods **不**携带版本字符串。Evolution Log 足以捕获变更历史。
- **组合** —— 硬组合（自动链式执行）不在 v1.7 范围。通过 `related_methods` 的软组合是 v1.7 的答案。
- **跨语言正文** —— v1.7 全部 method 正文用英文书写；theme 仅在 Summary Report 层影响显示。

---

## 17. 反模式（Anti-patterns）

- 不得在没有显式用户输入下自动提升过 `confirmed`
- 不得从单会话观察创建 method
- 不得把项目特定战术存成 methods —— 它们属于 `projects/{name}/`
- 不得把 methods 同步到 Notion —— 仅本地
- 不得让 tentative 队列无限增长 —— 5 次沉默 Start Session = 自动归档
- 不得编写引用具体姓名、金额、ID、公司或地点的 methods
- 不得让 archiver 在未走 Major Revision 工作流下编辑 confirmed/canonical methods
- 不得手工编译 INDEX.md —— 它是生成产物
- 不得把 `permanence: skill` 当作永久性 —— dormant methods 依然老化，只是慢一点

---

## 18. 每个角色如何使用 Method Library（How Each Role Uses the Method Library）

所有角色在引用前检查 `_meta/methods/INDEX.md` 是否存在。若不存在或为空，该角色在无 method 输入下运作。

| 角色 | 读取什么 | 如何使用 |
|------|---------------|-----------------|
| RETROSPECTIVE | `_meta/methods/INDEX.md` + `_tentative/` | 在 Start Session 编译 INDEX。浮现候选供确认。标记 dormant methods。 |
| ROUTER | INDEX（表头） | 分诊时扫描 domain 相关 methods。可提示用户 "you have a known approach for this." |
| PLANNER | INDEX（完整） | 起草规划文档前审视哪些 methods 适用。可按名引用。 |
| DISPATCHER | 相关 method 正文 | 作为 "Known Method" 注入 domain brief（第 9 节）。 |
| Six Domains | dispatch 上下文中的 method 正文 | 应用已知 method 而不是重导工作流。汇报遵从或偏离。 |
| REVIEWER | INDEX | 一致性检查 —— 若某规划文档忽略了一个适用的 method，标记之。 |
| AUDITOR | `_meta/methods/` 目录 | 巡检 —— 陈旧 methods、矛盾、滞留太久的候选。 |
| ARCHIVER | INDEX + 所有 method 文件 | Phase 2：探测候选、更新 evolution log、提议修订。 |
| DREAM | INDEX | REM 阶段使用 method 模式作为跨 domain 洞察的连接组织。 |

---

## 19. 相关规范（Related Specs）

- `references/wiki-spec.md` —— 相邻的知识层（陈述性 vs 程序性）
- `references/soul-spec.md` —— 身份层
- `references/dream-spec.md` —— REM 阶段探测 method 模式
- `references/concept-spec.md` —— methods 通过 `related_concepts` 链接到 concepts
- `references/hippocampus-spec.md` —— 为跨会话回声启发规则提供历史会话检索
- `pro/agents/archiver.md` —— 写入 method 候选（Phase 2）
- `pro/agents/dispatcher.md` —— 将 methods 注入 domain brief
- `devdocs/research/2026-04-19-hermes-analysis.md` —— Hermes 灵感来源

---

## 20. 约束摘要（Constraints Summary）

- 仅在候选启发规则通过时由 archiver 自动创建
- 离开 `_tentative/` 需要用户确认；达到 5 次使用 + 0.7 confidence 时自动提升为 canonical，但不会自动提升为 confirmed
- 写入前应用隐私过滤器；methods 仅本地（永不同步到 Notion）
- INDEX.md 是编译的，不是手写的
- 一个文件一个工作流 —— 不要创建 method 合集
- Methods 永不自动删除 —— 只在 dormant 12 个月后自动归档
- 重大修订需要用户确认
- Methods 使用与 SOUL 和 wiki 相同的 confidence 公式

---

*本文译自英文版 2026-04-22 snapshot；英文为权威源。*
