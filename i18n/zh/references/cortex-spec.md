---
translated_from: references/cortex-spec.md
translator_note: auto-translated 2026-04-21, 待人工校对
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Cortex 规范（Cortex Specification）

Cortex 是 Life OS 的认知层 —— pre-router 机制，负责将跨会话记忆、概念图与多源信号加载到每一次决策工作流中。它是第 2 层的架构升级（Layer 2 architectural upgrade），而不是新层。于 v1.7 引入。

## 定位（Positioning）

在 Life OS 的命名体系中，Cortex 与其他个人档案模块并列：

| 模块 | 记录什么 | 作用范围 |
|--------|----------------|-------|
| SOUL | 你是谁（身份、价值观） | 人格 |
| Wiki | 你对世界的知识 | 知识 |
| DREAM | 离线发现到的内容 | 睡眠阶段处理 |
| STRATEGIC-MAP | 你的位置所在 | 跨项目战略 |
| **Cortex** | **你如何思考** | **Pre-router 认知** |

Cortex 不替代任何现有模块。它为 ROUTER 提供带注释的输入 —— 用户消息加上记忆信号、概念信号与 SOUL 信号 —— 让下游 agent 在上下文中运作，而不是凭空运作。

---

## 原则（Principles）

1. **第 2 层升级，而非新层**（Layer-2 upgrade, not a new layer）—— Life OS 已经有三层（Engine + Theme + Locale）。Cortex 是第 2 层内部的能力扩展。
2. **ROUTER 接收带注释的输入，而非原始消息**（ROUTER receives annotated input, not raw message）—— Cortex 生成认知注释；ROUTER 的分诊规则保持不变。
3. **Markdown 优先，始终如一**（Markdown-first, always）—— 每个 Cortex artefact 都是 `.md + YAML frontmatter`。无 SQLite、无 Python 运行时、无 cron、无外部密钥。
4. **基于证据的生成**（Grounded generation）—— Cortex 输出中每个实质性声明都必须引用一个 signal_id。不允许虚构。
5. **优雅降级**（Graceful degradation）—— 如果任何 Cortex 子 agent 失败，系统回退到 v1.6.2a 行为（向 ROUTER 传递原始消息）。
6. **仅通用版**（Universal edition only）—— 不存在高级版或家用版变体。所有用户统一行为。

---

## Cortex 解决的问题（Problem Cortex Solves）

在 v1.7 之前，Life OS 仅在会话边界接触长期记忆 —— RETROSPECTIVE 在开始时读取，ARCHIVER 在结束时写入。两者之间的所有决策都只基于当前对话。16 个子 agent 的权衡制衡结构很强大，但这些 agent 共享的认知基底是空的：

- PLANNER 规划时不知道用户过去是如何决定类似主题的。
- 六个领域分析时不知道哪些概念彼此相连。
- REVIEWER 检查当前决策内部的一致性，而非跨会话的一致性。
- 散朝之后，只有 SOUL 和 Wiki 的自动写入留下痕迹 —— 没有概念图、没有 synapse 强化。

用户感受到的是"AI 在会话内很谨慎，但会话之间就忘了"。Cortex 通过让跨会话记忆与概念图成为每个工作流的一等输入，修复了这个问题。

失败模式不是任何单个 agent 弱 —— 16 个 agent 各自都做得很好。失败模式是 agent 从来看不到其他会话学到了什么。PLANNER 在 session 412 面对一个财务决策时，并不知道 session 198 已经对同一实体得出过结论，因为没有任何东西把那个结论往前传，除了原始的 `_meta/journal/*.md` 文件，而除非用户明确请求，没人会读这些文件。Cortex 让这种向前传递变为自动。

---

## 四个核心机制（Four Core Mechanisms）

Cortex 由四个机制构成。每个都有自己的 spec 文件。本文档是整体架构。

### 1. Hippocampus —— 实时跨会话检索（Real-time cross-session retrieval）

每条用户消息都会触发一个 hippocampus 子 agent（不是按需，而是始终开启）。三波扩散激活（three-wave spreading activation）：

- Wave 1：直接匹配（关键词或 concept_id 命中）
- Wave 2：强连接（synapse 权重 ≥ 3）
- Wave 3：弱连接作为阈下预激活（权重 < 3）

输出：top 5-7 个相关历史会话作为 memory signal，发送给 GWT arbitrator。

实现依赖两阶段扫描：ripgrep 把 `_meta/sessions/INDEX.md`（一个编译好的扁平文件，每行一条会话摘要）过滤到毫秒级的候选会话；然后子 agent 只读取匹配到的摘要（通常 15-20 行），返回最终的 top 5-7。在 1000 会话 × 每条 200 字符的规模下（UTF-8 编码下一条中日韩摘要约 600 字节、纯 ASCII 摘要约 200 字节），整个 index 视语种约 200KB–600KB —— 两种情况下扫描成本都微不足道。

完整 spec：`references/hippocampus-spec.md`。

### 2. GWT Arbitrator —— 显著性竞争（Salience competition）

基于 Stanislas Dehaene 的全局神经元工作空间理论（Global Neuronal Workspace theory）。多个并行模块产生信号；arbitrator 为每个信号计算显著性并广播 top-K。最强的信号"点燃"（ignite）并进入传递给 ROUTER 的认知注释。

显著性公式（Phase 1，四维度加权和）：

```
salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2
```

显著性不是自报的。模块发射原始分数；arbitrator 根据跨信号一致性进行调整。信号也是分类型的 —— `memory`、`concept_link`、`identity_check`，以及后续阶段的 `emotion` 和 `prediction` —— 每种类型都有一个置信度下限，低于该下限 arbitrator 会直接丢弃信号。抑制信号（否决）遵循更严格的 schema，要求提供 reasoning_chain。

完整 spec：`references/gwt-spec.md`。

### 3. Narrator Layer —— 带引用的基于证据生成（Grounded generation with citations）

在 Summary Report 呈现给用户之前，narrator 层用 signal_id 引用包裹实质性声明。这避免了 Gazzaniga 左脑解释器（left-brain-interpreter）的失败模式（为决策虚构貌似合理的解释）。

两类输出：

- **实质性声明**（Substantive claim）—— 必须带 signal_id 引用。例子："历史上在类似决策中你倾向于保守。"
- **连接性内容**（Connective tissue）—— 不需要引用。例子："让我们一起来看看这个。"

一个 validator 子 agent（Sonnet 层级的 Claude Code 子 agent —— 无外部 API）在报告发布前检查引用。无效引用触发重写。

实质性与连接性之间的划分是务实的，不是理论的。要求每个句子都带引用会产生像法律文书一样的机器盖章式输出。引用纪律针对的是承重声明 —— 用户可以质疑的那些断言 —— 而不是对话粘合剂。Phase 2 以单声明粒度运行；如果实际输出感觉注释过多，粒度可以粗化到段落级，而不会削弱抗虚构保证。

完整 spec：`references/narrator-spec.md`。

### 4. Synapses + Hebbian —— 带用进废退强化的概念图（Concept graph with use-it-or-lose-it reinforcement）

每个概念是 `_meta/concepts/{domain}/{concept}.md` 下的 markdown 文件。边（synapses）存在该概念自身的 frontmatter 中。共同激活使边权重 +1（Hebbian 规则）；长期未使用的边衰减。

四个永久性层级 —— identity、skill、fact、transient —— 决定衰减曲线的形状。衰减在每次散朝运行，由 ARCHIVER Phase 2 驱动。

每个概念带有三层状态：`tentative`（首次见到，未确认）、`confirmed`（多次激活，身份稳定）、`canonical`（高激活、广泛交叉引用）。常规使用下晋升是单向的，但三层撤销机制（参见 Design Principles）允许降级。反向边索引（`SYNAPSES-INDEX.md`）在每次 Hebbian 更新时重建；它是编译产物，从不手工编辑。

完整 spec：`references/concept-spec.md`。

---

## 工作流集成（Workflow Integration）

Cortex 在现有的 11 步工作流中增加两步。现有步骤编号不变。

```
Step 0:    Pre-Session Preparation (ROUTER + RETROSPECTIVE parallel) — 不变
Step 0.5:  Pre-Router Cognitive Layer — 新增
Step 1:    ROUTER Triage — 接收带注释的输入
Step 2-6:  不变
Step 7:    Summary Report — 不变
Step 7.5:  Narrator validation — 新增（仅 Phase 2、Full Deliberation）
Step 8-9:  不变
Step 10:   ARCHIVER Phase 2 — 扩展（见下文）
Step 11:   STRATEGIST (optional) — 不变
```

### Step 0.5 —— Pre-Router 认知层（Pre-Router Cognitive Layer）

在 Pre-Session Preparation 之后、ROUTER Triage 之前立即派发。三个子 agent 并行运行：

1. **hippocampus** —— 扫描 `_meta/sessions/INDEX.md`，返回 top 5-7 memory signals
2. **concept lookup** —— 扫描 `_meta/concepts/` 查找直接匹配的概念节点
3. **SOUL dimension check** —— 复用 RETROSPECTIVE 的 SOUL Health Report，发射一个 identity_check signal

三个输出流馈入 **gwt-arbitrator**，后者应用显著性公式、给信号排序，并为 ROUTER 产出一个带注释的输入块：

```
[USER MESSAGE]
[COGNITIVE ANNOTATION]
- Relevant history: [5-7 session summaries with signal_ids]
- Concept graph: [matched concepts + 1-hop neighbours]
- SOUL context: [tier-1 dimensions + any conflict warnings]
```

ROUTER 可以参考或忽略该注释 —— 它的分诊规则保持不变。如果 Step 0.5 在任何环节失败（子 agent 超时、文件不可达），orchestrator 回退到原始消息输入，以 v1.6.2a 行为继续。

**快速路径交互**（Express path interaction）。当 ROUTER 走快速路径（1-3 个领域 agent，不含 PLANNER / REVIEWER）时，Step 0.5 仍然运行但以精简形式进行：只派发 hippocampus 子 agent。Concept lookup 和 SOUL check 被跳过，以保留 Express 的速度预算。快速路径的带注释输入是单行的 memory 摘要，而不是完整的三段式块。当只存在一个信号源时不调用 gwt-arbitrator。

**直接应答交互**（Direct-handle interaction）。当 ROUTER 直接回答一条琐碎消息（例如 "thank you"、"ok"）且工作流在 Step 1 结束时，Step 0.5 完全跳过。Orchestrator 通过检查 ROUTER 的分诊决策来检测这种情况 —— 直接应答的响应不需要认知注释。

### Step 7.5 —— Narrator 校验（Narrator Validation，仅 Phase 2）

在 Summary Report 显示之前，narrator-validator（Sonnet 层级 Claude Code 子 agent —— 在当前会话内运行，无外部 API）对照信号存储检查每一个实质性声明。无效或未引用的声明返回给 narrator 重写。连接性内容被忽略。此步骤仅在 Full Deliberation 下运行 —— 快速路径和直接应答响应跳过它。

### Step 10 —— ARCHIVER Phase 2 扩展（ARCHIVER Phase 2 extended）

ARCHIVER Phase 2 已处理 wiki 和 SOUL 自动写入。在 v1.7 中它还执行：

- **概念提取**（Concept extraction）—— 扫描会话材料寻找新概念，分类永久性层级，写入 `_meta/concepts/{domain}/{concept}.md`
- **Hebbian 更新**（Hebbian update）—— 对会话中每对共同激活 (A, B)，使 A→B 的边权重 +1；若不存在则以权重 1 创建新边
- **SYNAPSES-INDEX.md 重建**（SYNAPSES-INDEX.md regeneration）—— 在权重更新后重建反向索引
- **SOUL 快照写入**（SOUL snapshot dump）—— 沿用 v1.6.2 既有机制，在 Cortex 下保持
- **会话摘要写入**（Session summary write）—— 发射 `_meta/sessions/{session_id}.md`，含主题、关键决策、激活概念，以及供 hippocampus 后续读取的单行 YAML 摘要字段

所有写入发生在单次 ARCHIVER 调用内。Orchestrator 不在阶段之间交错写入。这保留了在 `pro/CLAUDE.md` 中定义的散朝状态机 —— ARCHIVER 在所有阶段完成时发射一份 Completion Checklist，会话结束。

### Step 0 保留，Step 11 保留（Step 0 preserved, Step 11 preserved）

Pre-Session Preparation 和 STRATEGIST 都不被修改。SOUL Health Report 继续由 RETROSPECTIVE 编译。STRATEGIST 仅在用户明确同意时调用。

---

## 数据结构（Data Structures）

所有 Cortex 数据驻留在 markdown 中。v1.7 引入的新目录：

```
_meta/
├── concepts/
│   ├── INDEX.md                         ← 编译好的单行摘要索引
│   ├── SYNAPSES-INDEX.md                ← 编译好的反向边索引
│   ├── _tentative/                      ← 待确认的概念
│   ├── _archive/                        ← 退役的概念
│   ├── finance/
│   │   └── {concept_id}.md
│   ├── career/
│   └── personal/
├── sessions/
│   ├── INDEX.md                         ← 编译好的会话摘要索引
│   └── {platform}-{YYYYMMDD-HHMM}.md    ← 单会话摘要，含 YAML
├── snapshots/
│   └── soul/                            ← SOUL 快照（v1.6.2，沿用）
├── eval-history/                        ← AUDITOR 评估历史
└── cortex/
    ├── config.md                        ← 阈值与开关
    ├── bootstrap-status.md              ← 迁移状态
    └── decay-log.md                     ← 衰减动作
```

每个机制的数据格式在其自己的 spec 文件中定义。本文档不重复这些定义。

- 概念文件格式 → `references/concept-spec.md`
- 会话摘要格式 → `references/session-index-spec.md`
- 信号与仲裁记录格式 → `references/gwt-spec.md`
- Hippocampus 输出格式 → `references/hippocampus-spec.md`
- SOUL 快照格式 → `references/snapshot-spec.md`（自 v1.6.2 沿用）

### Cortex 运行时文件（schemas）

四个 markdown artefact 跟踪 Cortex 运行时状态。它们都不是真实来源 —— 要么是配置（用户可编辑），要么是编译/日志 artefact（由 archiver 写入）。全部驻留在 `_meta/cortex/`（前三个）或 `_meta/ambiguous_corrections/`（第四个）。

#### `_meta/config.md`

用户可编辑的阈值与开关。由 hippocampus、gwt-arbitrator、narrator-validator 以及衰减过程读取。如缺失，每个消费者回退到硬编码默认值（内联列在下方）。

```yaml
---
file: _meta/config.md
version: 1.7
---

# Cortex Config

## Feature switches
cortex_enabled: true              # master switch; false degrades to v1.6.2a behaviour
hippocampus_enabled: true
gwt_arbitrator_enabled: true
narrator_validator_enabled: true
concept_extraction_enabled: true

## Salience formula (gwt-arbitrator)
salience_weights:
  urgency: 0.3
  novelty: 0.2
  relevance: 0.3
  importance: 0.2
per_signal_floor: 0.3             # signals with salience < floor are dropped
top_k_signals: 5                  # hard cap of signals broadcast to ROUTER

## Decay curves (archiver Phase 2 decay pass)
decay_curves:
  identity: none                  # no decay
  skill: logarithmic              # decays to a steady baseline, never zero
  fact: exponential               # half-life 90 days
  transient: cliff                # zero at expiry

## Three-tier undo thresholds
escalate_rate_limit: 5            # per rolling 7-day window
ambiguous_correction_confidence_bands:
  high: 0.85                      # ≥ apply immediately
  mid_low: 0.5                    # mid-band lower bound (write to _meta/ambiguous_corrections/)
  low_floor: 0.0                  # logged but not acted

## Performance budgets (seconds, soft/hard)
hippocampus_timeout: [5, 15]
gwt_timeout: [5, 10]
narrator_validator_timeout: [3, 10]
```

编辑此文件的用户应 commit 到 git，以便跨设备漂移被追踪。改动在下一次会话开始时生效（retrospective Mode 0 读取该配置）。

#### `_meta/cortex/bootstrap-status.md`

由 `tools/migrate.py` 写入一次。由 retrospective Mode 0 读取以判断 Cortex 是否就绪。

```yaml
---
file: _meta/cortex/bootstrap-status.md
---

# Cortex Bootstrap Status

migration_completed_at: 2026-04-20T14:32:10+09:00
from_version: v1.6.2a
to_version: v1.7
scope_months: 3

journal_entries_scanned: 127
sessions_synthesized: 38
concepts_extracted:
  tentative: 42
  confirmed: 18
  canonical: 7
snapshots_synthesized: 15
methods_extracted: 5
eval_history_backfilled: 0        # per spec: no backfill

errors: []                        # list of per-file parse failures
warnings:
  - "4 journal entries missing platform metadata; defaulted to 'claude'"
```

如此文件缺失，retrospective Mode 0 会在 Start Session 简报顶部警告 "Cortex not bootstrapped — run `uv run tools/migrate.py`"。Cortex 仍可工作但图为空（冷启动模式）。

#### `_meta/cortex/decay-log.md`

只追加日志，由 archiver Phase 2 在每次散朝结束时写入。每次会话贡献一个带日期的块。

```yaml
---
file: _meta/cortex/decay-log.md
rolling_window_days: 90
---

# Cortex Decay Log

## 2026-04-20 session claude-20260420-1432
edges_decayed: 14
edges_pruned: 2                   # weight reached 0
concepts_demoted:
  - C:finance:quarterly-yield     # canonical → confirmed (90-day dormancy)
concepts_retired:
  - C:transient:2026-q1-event     # transient cliff
new_tentative: 3
new_confirmed: 1
new_canonical: 0

## 2026-04-19 session claude-20260419-1238
...
```

超过 90 天的块在下一次散朝写入时压实到尾部 `# Archive` 节。过往存档存在 git 历史中 —— 不删除，不与 Notion 同步。

#### `_meta/ambiguous_corrections/{correction_id}.md`

每个待处理的中置信度用户纠正对应一个文件。当三层撤销机制（§Design Principles → Three-tier undo）检测到置信度落在 0.5–0.85 区间的纠正时创建：不够高到立即应用、不够低到仅记录忽略。

```yaml
---
correction_id: 2026-04-20-concept-company-a-merge
target: C:finance:company-a-holding
target_type: concept              # concept | soul_dimension | method
correction_type: demotion | merge | split | alias_add | permanence_change
proposed_change: "demote from canonical to confirmed; merge alias 'Company-A HK'"
user_confidence: 0.72             # from correction heuristic (0.5-0.85 band)
signal_refs:
  - S:claude-20260420-1034
detected_at: 2026-04-20T10:34:12+09:00
surfaces_when: "next activation of C:finance:company-a-holding"
status: pending                   # pending | applied | dismissed
---

# Context

{One short paragraph quoting the user's language that triggered the
correction, plus a one-line archiver note explaining why confidence
landed in the mid-band rather than the high band. Max 30 lines.}
```

**浮现**（Surfacing）：下一次目标被激活时（hippocampus 输出中的 concept、check 中的 SOUL dimension、dispatcher lookup 中的 method），retrospective Mode 0 或 ROUTER 暂停以在继续前显示待处理的纠正。用户确认 → `status: applied`，纠正通过常规三层撤销机制传播。用户驳回 → `status: dismissed`，文件删除，`decay-log.md` 中落下一行记录驳回。

**保留**（Retention）：applied/dismissed 文件被移除；pending 文件在 30 天未激活（用户再没命中目标 —— 该纠正已过期）后压实为 `decay-log.md` 中的一行摘要。

---

## 执行模型（Execution Model）

每个 Cortex 组件都是 `pro/agents/*.md` 中定义的 Claude Code 子 agent。执行规则与现有 16 个子 agent 相同。

- **无外部 API 调用**（No external API calls）—— 所有 LLM 工作发生在当前 Claude Code 会话内。无 Anthropic API 密钥、无 Claude API 代理、无 OpenAI SDK。
- **无数据库**（No database）—— 存储决策 ADR（`docs/architecture/markdown-first.md`）具有权威性。Markdown 是真实来源。SQLite 和任何其他数据库都在范围之外。
- **无独立后台作业**（No separate background jobs）—— 无 cron、无守护进程、无定时 worker。数据更新发生在 ARCHIVER Phase 2 写入内。
- **无外部密钥**（No external secrets）—— 不需要 Claude Code 已提供之外的环境变量。无 Vercel、无 GitHub Actions、无 CI/CD 管道。
- **概念衰减在每次散朝运行**（Concept decay runs every adjourn）—— 不由定时器驱动。散朝流程是规范的维护窗口。
- **按需运行的 Bash Python 工具在本地运行**（Bash-run Python tools, when needed, run locally）—— 迁移辅助（`tools/migrate.py`）从 Claude Code 会话通过 Bash 调用。它不是一个服务。

v1.7 引入的新 agent 文件：

| Agent | 用途 |
|-------|---------|
| `pro/agents/hippocampus.md` | 跨会话检索，发射 memory signals |
| `pro/agents/gwt-arbitrator.md` | 显著性竞争，发射带注释的输入 |
| `pro/agents/narrator-validator.md` | Sonnet Claude Code 子 agent —— 引用校验器（Phase 2） |

Narrator 不是新 agent 文件 —— narrator 行为驻留在 ROUTER 内部（见 `references/narrator-spec.md` §6）。Concept extraction 不是新 agent 文件 —— 它驻留在 ARCHIVER Phase 2 内部（见 `references/concept-spec.md` §Hebbian Update Algorithm）。

对现有 agent 的扩展：

- `pro/agents/archiver.md` Phase 2 —— 新增概念提取、Hebbian 更新、method-candidate 检测、衰减过程、会话摘要写入、索引重建
- `pro/agents/retrospective.md` Mode 0 —— 重新生成 `_meta/concepts/INDEX.md` 与 `_meta/sessions/INDEX.md`；标记休眠概念
- `pro/agents/router.md` —— 在其输入中接受认知注释；在 Step 7.5 掌管 narrator 组合

Claude Code 在派生时读取每个 agent 定义；调用之间不持久化任何运行时状态。

### 信息隔离扩展（Information isolation additions）

`pro/CLAUDE.md` 中现有的 Information Isolation 表在 v1.7 新增三行，保持同一原则 —— 每个 agent 只收到其工作所需的内容：

| 角色 | 接收 | 不接收 |
|------|----------|------------------|
| hippocampus | 用户消息 + `_meta/sessions/INDEX.md` + 当前会话上下文 | 其他 agent 的思考过程、完整概念图 |
| gwt-arbitrator | 来自 hippocampus / concept-lookup / soul-check 的信号文件 | 用户的原始消息（仅对信号运作） |
| narrator-validator | Summary Report 草稿 + 信号存储 | Agent 的思考过程、用户的私密数据 |

gwt-arbitrator 对原始消息的隔离是刻意的 —— 显著性计算应基于结构化信号，不应被对话表面偏置。narrator-validator 对思考过程的隔离则防止循环校验。

---

## 设计原则（Design Principles）

### 基于证据的生成（Grounded generation）

任何 Cortex 输出中的任何声明都不能没有 signal_id 引用。这是对抗虚构的首要防线。validator 子 agent 通过取回被引用的信号并检查 narrator 的转述是否忠实来强制执行。若任何实质性声明缺少引用或引用不支持该声明，narrator 重写。

Gazzaniga 左脑解释器实验显示人类会为自己并非有意识做出的决策虚构貌似合理的解释。若 Cortex 重现这一机制，它将是一个自欺的系统 —— 决策由碰巧最响亮的信号驱动，事后被合理化为一套看起来连贯的叙事。Grounded generation 是结构性答案：validator 无法被绕过，因为它作为独立子 agent 运行，对信号存储只读访问。虚构 signal_id 的 narrator 将在取回时校验失败。

### 三层概念永久性加一层瞬态（Three-tier concept permanence with a fourth for transient state）

| 永久性 | 衰减形态 | 例子 |
|-----------|-------------|----------|
| Identity | 不衰减 | SOUL 核心价值观、长期关系 |
| Skill | 对数衰减到稳定基线 | "如何写 Python" |
| Fact | 指数衰减 | "去年 Q2 项目 X 预算为 Y" |
| Transient | 悬崖式衰减到零（到期后） | 事件特定的、一次性引用 |

永久性在 ARCHIVER Phase 2 概念提取的首次激活时分配。用户可以显式钉住永久性。元认知可以在概念抵抗衰减（尽管被"尝试"降级）时升级永久性。

### 扩散激活，非穷举检索（Spreading activation, not exhaustive retrieval）

Hippocampus 不扫描每个会话文件。它对 Wave 1 使用 ripgrep，对 Wave 2 使用 1 跳 synapse 遍历，对 Wave 3 使用阈下预激活。每次查询总范围有界：最多 top-50 个概念节点。这与大脑中扩散激活的工作方式一致 —— 强度随图距离下降。

Wave 3 是预激活（pre-activation），不是检索。阈下概念不出现在输出中，除非同一会话中稍后的帧把它们抬升到阈值以上。这重现了大脑的启动（priming）行为：最近激活过的概念的邻居在下一帧更容易被触发，即便没有直接证据。其运作效果是：一次以"company-A holding"问题开场的会话，在稍后关于"company-A subsidiary"的问题上更敏感，即使用户没有再次提到父级名称。

### 显著性竞争，而非规则式优先级（Salience competition, not rule-based priority）

信号没有固定优先级。它们在每一帧通过显著性公式竞争。上下文允许时，高紧迫性的 memory signal 可以胜过高重要性的 identity signal。Arbitrator 是唯一决定哪些信号点燃的组件。

### 带 reasoning chain 的结构化否决（Structured veto with reasoning chain）

这是 brainstorm 的路径 B。抑制信号（否决）不是单纯基于强度的压制 —— 它们必须携带带 claims、evidence_signals 和 confidence 的 reasoning_chain。这使拒绝可审计。当同一对信号两次产出相同竞争（没有新证据的反驳回路）时，系统自动上升到用户。

备选路径 A（按强度压制）被否决，因为软件系统中的抑制信号没有演化启发式背书。大脑可以容忍不透明否决，因为数十亿年演化调校了否决神经元。软件模块没有这样的基底；模块的不透明否决只是一种 Opus 的直觉。通过要求 reasoning_chain，每一次拒绝都变成用户可以检视、必要时推翻的东西。这保留了 Life OS 的原则：系统是用户的工具，而非凌驾于用户之上的权威。

### 三层撤销（Three-tier undo）

不能被纠正的系统是无用的。Cortex 提供三条纠正路径：

1. **被动衰减**（Passive decay）—— 未使用的 canonical 概念随时间降级（90 天后到 fact 层）。无需用户动作。
2. **用户纠正**（User correction）—— "你这个弄错了" 触发 concept_demotion 修改，对所有受影响 synapse 加级联标记。
3. **元认知审计**（Meta-cognitive audit）—— 每周审计浮现可疑漂移（冲突显著性、频率下降、反复用户纠正）到 `_meta/audit/suspicious.md`；用户在降级前确认。

用户纠正的置信度分层：高置信度（>0.85）纠正立即应用；中置信度（0.5-0.85）纠正写入 `_meta/ambiguous_corrections/`，在下一次相关激活时浮现以获取显式确认；低置信度（<0.5）纠正记录但不采取行动。初始阈值刻意保守 —— 假阴性（漏掉一次纠正）的代价低于假阳性（降级了用户不想降级的东西）。

元认知审计有速率限制：**滚动 7 天窗口内超过 5 次上升** 触发对模块质量本身的二级审计。假设是一个运作良好的系统应极少需要把冲突浮现给用户；频繁上升表明模块级漂移，而非个别纠正需求。

#### `_meta/audit/suspicious.md` 格式

元认知审计写入单个滚动 markdown 文件。Archiver Phase 2 追加候选；retrospective Mode 0 在 Start Session 简报中浮现未解决行；用户确认或驳回。格式：

```yaml
---
file: _meta/audit/suspicious.md
rolling_window_days: 30
last_compacted: ISO 8601
---

# Audit · Suspicious Drift

| Detected | Candidate | Reason | Signal refs | Status |
|----------|-----------|--------|-------------|--------|
| 2026-04-18 | C:finance:company-a-holding | 4 user corrections in 2 weeks; salience stable | S:claude-20260418-0934, S:claude-20260416-1520 | open |
| 2026-04-17 | C:method:iterative-refinement | Activation dropped 80% vs 90-day baseline | S:claude-20260417-1400 | dismissed 2026-04-19 |
```

列：

- **Detected** —— archiver 标记漂移的 ISO 日期
- **Candidate** —— 被质疑的 concept / SOUL dimension / method 的完整前缀 signal_id
- **Reason** —— 来自四个启发式之一的单行描述：`conflicting_salience`、`frequency_drop`、`repeated_user_correction`、`canonical_contradiction`
- **Signal refs** —— 支撑检测的 signal_id 逗号分隔列表（供 `narrator-validator` 式校验）
- **Status** —— `open` / `confirmed YYYY-MM-DD` / `dismissed YYYY-MM-DD`

`status: open` 且超过 30 天的行在 archiver Phase 2 运行时压实到尾部 "# Archive" 节。Dismissed/confirmed 行在 90 天后压实。该文件活动行从不超过 ~300 行；压实保持读延迟有界。

#### 上升速率限制（Escalate rate limit）

每周 5 次的阈值由 AUDITOR 在巡查时监控（不是 hook 或 Python 工具 —— 保留在会话内）。超过时，AUDITOR 写入一条高优先级条目到 `_meta/eval-history/{date}-{project}.md`，带 `violations[].type: escalate_rate_exceeded`，并在 retrospective Mode 0 下一次简报中浮现该模式。没有模块会自动被砍（用户决策 #4 —— 无预先承诺的终止准则）；由用户决定底层机制是否需要调整。

---

## 与现有组件的关系（Relationship to Existing Components）

Cortex 不替代任何现有 Life OS 组件 —— 它增强它们。下表总结每个现有表面在 v1.7 下如何获得（或保持）其形态。

| 现有组件 | 在 Cortex 下的角色 | 变化性质 |
|-------------------|-------------------|------------------|
| SOUL.md | 身份层，identity_check 信号源 | 不变。SOUL 自动写入继续；Health Report 馈入 Step 0.5。 |
| wiki/ | 概念锚材料，ARCHIVER Phase 2 概念提取的证据源 | 不变。Wiki 条目与概念节点保持分离但可以锚定它们。 |
| DREAM | 离线睡眠阶段模式处理器 | 结构上不变。可消费概念图做 REM 跨域跳跃。 |
| RETROSPECTIVE | 会话开始的家务 + SOUL Health Report | Mode 0 扩展加入衰减检查与概念 INDEX 重建。 |
| ARCHIVER | 会话关闭，4 阶段收尾 | Phase 2 扩展加入概念提取、Hebbian 更新、会话摘要写入。 |
| ROUTER | 分诊与报告编排 | 输入格式改变（带注释输入而非原始），分诊规则不变。 |
| 16 个子 agent | 审议班底（PLANNER / REVIEWER / 六个领域等） | 不变。当 ROUTER 转发带注释输入时消费更丰富的上下文。 |

三个不变量成立：(1) Cortex 给 ROUTER 更好的输入但不代替 ROUTER 解读消息；(2) Cortex 给 ARCHIVER 额外的写入目标但不绕过 ARCHIVER 的单次调用纪律；(3) Cortex 围绕 16-agent 审议添加认知但不改变制衡结构。Agent 仍只看到其工作所需。

---

## Archiver 候选路由（Phase 2 消歧义）（Archiver Candidate Routing）

当 archiver Phase 2 从会话内容中提取候选时，它必须决定**每个候选属于哪一个知识层**。这个决定不是任意的 —— 每一层回答一个不同的问题，误路由会造成静默漂移（事实被存为价值、流程被存为概念、身份被存为 wiki）。

这是权威决策树。当任何 spec 与此树不一致时，此树为准。

### 4 个知识层 + 1 个身份层（The 4 knowledge layers + 1 identity layer）

| 层 | 回答 | 示例候选 | 路径 |
|-------|---------|-------------------|------|
| SOUL | 你是谁（身份/价值观/偏好） | "用户始终优先家庭超过事业增长" | `SOUL.md`（单文件，内含维度） |
| Wiki | 你对世界的知识（陈述性） | "日本 NPO 借贷无貸金業法豁免" | `wiki/{domain}/{slug}.md` |
| Concept | 想法如何连接（联想图节点） | "Company-A" 作为通过加权边连接到其他概念的实体 | `_meta/concepts/{domain}/{concept_id}.md` |
| Method | 你如何最佳工作（程序性记忆） | "用 5 轮递进质量润色文档" | `_meta/methods/{domain}/{method_id}.md` |
| user-patterns | 你做什么（观察到的行为模式，ADVISOR 领域） | "在首轮澄清后决策变快" | `user-patterns.md`（单文件，内含条目） |

### 决策树（Decision tree）

Archiver Phase 2 让每个候选走一遍此树。第一个匹配分支胜出 —— 候选从不路由到多个主层。

```
候选是否关于用户的身份、价值观、偏好或红线?
├── 是 → SOUL
│         (证据来自当前会话或最近 30 天内 ≥2 次决策；
│          新维度以 confidence 0.3 自动写入，What SHOULD BE 留空)
│
└── 否 → 它是行为模式吗（用户做什么，而非他们是谁）?
    ├── 是 → user-patterns.md (通过 patterns-delta 追加)
    │         (ADVISOR 浮现这些；不是 SOUL)
    │
    └── 否 → 它是可复用的 WORKFLOW（动作序列、类似方法）吗?
        ├── 是 → Method
        │         (5+ 顺序动作，在 ≥2 个会话中跨会话回响，
        │          用户语言如 "approach/pattern/framework/流れ/やり方/手順"；
        │          落入 _meta/methods/_tentative/，status: tentative)
        │
        └── 否 → 它是反复出现的、连接到其他的 ENTITY / CONCEPT 吗?
            ├── 是 → Concept
            │         (≥2 次激活 + ≥2 个独立证据点;
            │          落入 _meta/concepts/_tentative/ 直到晋升;
            │          个人 → 跳过,或路由到 SOUL(由其隐私过滤决定))
            │
            └── 否 → 它是关于世界的 FACTUAL 结论吗?
                ├── 是 → Wiki
                │         (6 项准则:跨项目可复用、关于世界、
                │          零隐私、事实或方法论、≥2 证据、
                │          与现有无矛盾；见 wiki-spec §Auto-Write Criteria)
                │
                └── 否 → 丢弃（不可复用；仅留在会话 journal）
```

### 消歧义示例（Disambiguation examples）

| 候选 | 路由 | 原因 |
|-----------|-------|-----|
| "用户偏好质量胜于速度" | SOUL | 身份/价值观陈述 |
| "用户倾向周一避免财务讨论" | user-patterns | 行为模式（他们做什么），非身份 |
| "MVP 验证用 5 轮递进质量" | Method | 可复用程序化工作流 |
| "Company-A 和 Company-B 共享一位董事，此人也坐在 Project-X 的董事会" | Concept（+ 边） | 带实体的图结构 |
| "日本 NPO 借贷无貸金業法豁免" | Wiki | 关于世界的事实结论 |
| "当每轮聚焦一个焦点时迭代文档润色最有效" | Method | 程序性 how-to |
| "治理关切在跨境产品决策中应权重 30%" | Wiki | 陈述性结论 |
| "Finance 与 Execution agent 上次会话相差 4 分" | 丢弃 | 单会话观察，非跨会话可复用 |
| "用户特定家庭成员 A 的偏好" | 跳过（或 SOUL 配隐私过滤） | 个人不路由到 Concept；由 SOUL 的隐私过滤决定 SOUL 是否接收，或整条丢弃 |

### 歧义情形（Ambiguous cases）

**带程序边缘的事实**（Fact with procedural edge）："协商涨价时先用数据锚定" 可以读作 method（流程）或 wiki 结论（关于世界的事实）。规则：若候选描述的是**用户动作的序列**，则它是 method。若描述的是**世界的一种属性**，则它是 wiki。真正歧义时默认 **wiki** —— method 需要更强证据（≥5 个顺序步骤，跨 ≥2 个会话）。

**概念与 SOUL 重叠**（Concept with SOUL overlap）："trust"（信任）作为一种关系维度可能是 SOUL（一种价值）或概念（关系实体类型）。规则：概念是关于**世界中与其他事物相连的事物**；SOUL 是关于**用户对事物的取向**。"用户重视商业关系中的信任" → SOUL。"信任是一种在项目之间流动的关系资本类型" → 概念（在 `_meta/concepts/relationship/`）。

**带方法味的 wiki**（Wiki with method flavour）：一份逐步食谱，若它是对世界的事实描述（不是用户选择的工作流）→ wiki。若用户有意识地把它采纳为自己的方法 → method。启发式：archiver 问 "用户是否拥有这个工作流？" —— 是则 method；否（只是一种已知技术）则 wiki。

### 路由置信度与待处理状态（Routing confidence and pending state）

Archiver Phase 2 为每个候选分配路由置信度：

- **高**（>0.85）—— 带 `status: tentative` 进入目标层（适用 concepts/methods），或以 confidence 0.3 自动写入 SOUL / 以 confidence 0.3-0.5 写入 wiki
- **中**（0.5-0.85）—— 作为路由决策纠正写入 `_meta/ambiguous_corrections/`，等待下一次相关激活时用户确认
- **低**（<0.5）—— 以 "routing-rejected candidate" 和原因记录到 `_meta/cortex/decay-log.md`，不写入任何地方

这与三层撤销机制（§Design Principles → Three-tier undo）平行 —— archiver 在不确定时偏向谨慎。假阴性（漏掉候选）的代价低于假阳性（错误层写入，之后需要外科式反转）。

### 反模式（Anti-patterns）

- **把同一候选路由到两层** —— 精确一个主目标。概念 MAY 通过 `anchors_in_wiki: [slug]` 引用 wiki 条目，但那是交叉引用，不是重复写入。
- **为个人创建概念** —— 违反 concept-spec §9（隐私）。个人属于带隐私过滤的 SOUL。
- **在没有 ≥2 个独立会话显示模式时写入 method** —— 违反 method-library-spec §6（启发式）。跨会话回响是最低证据门槛。
- **写入未通过任一 6 项准则的 wiki 条目** —— 违反 wiki-spec §Auto-Write Criteria。全部 6 项或丢弃。
- **在路由时直接变更 SOUL** —— SOUL 自动写入用自己的 3 条门槛（身份范围 + ≥2 证据 + 无既有维度）。路由提议；SOUL 自动写入接受。

---

## 反模式（Anti-patterns）

Cortex MUST NOT 做以下任何事：

- **以数据库为真实来源**（Database as source of truth）—— 权威存储是 markdown。SQLite、Postgres 或任何关系索引都在范围之外。
- **把 Cortex 数据同步到 Notion**（Sync Cortex data to Notion）—— 概念节点、synapses 和帧记录不经 Notion 往返。Notion 仅接收会话摘要与决策记录，与 v1.6.2a 一致。
- **要求外部 API 密钥**（Require external API keys）—— 无 Claude API、无 OpenAI SDK、无第三方 embedding。所有智能在 Claude Code 内运行。
- **发明没有数据源的信号**（Invent signals without a data source）—— 任何模块发射的每个信号都必须引用其负载来源。无合成证据。
- **让 narrator 在没有引用的情况下作声明**（Let the narrator make claims without citations）—— 实质性声明引用是必须的。Validator 执行不是可选。
- **作为常驻守护进程运行**（Run as a persistent daemon）—— Cortex 在当前会话内运行。会话之间除了 markdown 不持久化任何东西。
- **构建高级版**（Build a premium edition）—— 只有一个通用版本。不基于用户层级做功能门控。

---

## 版本与迁移（Version & Migration）

Cortex 在 **v1.7** 引入。brainstorm 将其发布分为四个内部阶段（A 到 D），其中第一个阶段（A）进一步拆分为三个子阶段（A1/A2/A3），但它们全部落在 v1.7 内 —— 不跨 v1.8 / v1.9 / v2.0。版本号统一。

v1.7 内部阶段：

| 阶段 | 范围 |
|-------|-------|
| A —— 数据结构 | `_meta/concepts/`、`_meta/sessions/INDEX.md`，ARCHIVER Phase 2 加入概念提取（Hebbian 关闭） |
| B —— 认知 pre-router 上线 | hippocampus + gwt-arbitrator 子 agent 上线，Step 0.5 接通，Hebbian 开启 |
| C —— Narrator + 撤销机制 | Step 7.5 活动、三层撤销上线、上升速率限制 |
| D —— 完整 cortex + Hermes 执行层 | 回填被降级模块，完整执行层 |

所有四个阶段都在 v1.7 内发布。分阶段是内部排序，不是增量发布。分阶段之所以存在，是因为每个阶段都是后续阶段的天然检查点：B 阶段在 A 阶段产出足够概念与会话数据之前无法有意义地运作；C 阶段的 narrator 无法校验 B 阶段尚未产出的信号；D 阶段改进 B 和 C 已经证明奏效的部分。阶段是天然依赖门 —— 不是外部发布点。

A 阶段进一步拆分为三个子阶段：A1（数据结构落地）、A2（migrate.py 回填）、A3（seed.py 引导）；A2 与 A3 在 A1 落地后可并行。B、C、D 阶段保持单子阶段。完整内部序列为 A1 → (A2+A3 并行) → B → (C+D 并行)，且一切仍以 v1.7 发布。

AUDITOR 通过 `eval-history` 条目（`references/eval-history-spec.md`）跟踪发布后质量。质量回归作为 eval-history 模式浮现；模块级范围变更通过常规 spec 修订发生，而不是通过预先承诺的数值阈值。

### 从 v1.6.2a 迁移（Migration from v1.6.2a）

Cortex 要求在 hippocampus 能检索到任何东西之前回填会话索引。迁移拉取最近 3 个月的 `_meta/journal/*.md` 并产出每会话摘要。

```
Script: tools/migrate.py
Input:  _meta/journal/*.md           (existing session journals)
Output:
  - _meta/sessions/{session_id}.md   (one file per historical session)
  - _meta/sessions/INDEX.md          (compiled one-liner index)
  - _meta/concepts/**/*.md           (seed concepts from journal entities)
  - _meta/snapshots/soul/**          (backfilled SOUL snapshots when possible)
```

迁移脚本从 Claude Code 通过 Bash 调用。它幂等 —— 重新运行覆盖已编译索引而不重复概念。迁移后，用户运行一次启用 Cortex 的会话；若带注释输入感觉正确，Cortex 晋升到稳态。

若迁移失败，orchestrator 回退到原始消息输入并记录警告。用户像在 v1.6.2a 中一样操作，直到迁移被重试。

三个月范围是刻意的默认：更旧的 journal 通常包含过时上下文（已退役的项目、被降级的价值、pre-SOUL 的决策），会污染概念图。历史更丰富的用户可以通过把 `--since YYYY-MM-DD` 传给迁移脚本来覆盖范围。没有 journal 历史的首次用户以"冷启动"模式运行 Cortex —— 带注释输入在累积足够会话之前是最小的；没有任何东西阻塞系统使用。

---

## 悬而未决的问题（Open Questions）

以下规范刻意留给实现期间解决 —— 不是因为被忘记，而是因为需要具体数据才能正确调校。

- **显著性公式权重调校**（Salience formula weight tuning）—— Phase 1 权重（urgency 0.3, novelty 0.2, relevance 0.3, importance 0.2）是占位。需要三个月的真实带注释输入数据来验证。
- **概念永久性分类启发式**（Concept permanence classification heuristics）—— ARCHIVER Phase 2 概念提取在首次激活时使用启发式规则。skill 与 fact 之间的边界模糊。预计在 3 个月真实使用后修订。
- **Narrator 引用密度**（Narrator citation density）—— 单句 vs 单段。Phase 2 以单实质性声明开始；若输出感觉机器盖章式，粒度可能粗化。
- **多设备并发**（Multi-device concurrency）—— 单设备 / 分布式同步 / 主动锁 —— 三个选项，在 Phase 1 启动时选择一个。
- **帧触发策略**（Frame trigger policy）—— 在 v1.7 中每条用户消息触发 Step 0.5。外部事件（定时提示、收件箱到达）在 v1.7 帧触发范围之外 —— 仅用户消息触发 Step 0.5。
- **冷启动行为**（Cold-start behaviour）—— 无 journal 历史的新用户在降级模式下运行 Cortex。Cortex 从冷启动转入稳态的确切点（会话数、概念数或启发式）尚未选定。

---

## 引用（References）

- 总体架构讨论 → `devdocs/brainstorm/2026-04-19-cortex-architecture.md`
- 集成桥接文档 → `devdocs/architecture/cortex-integration.md`
- Markdown-first ADR → `docs/architecture/markdown-first.md`
- Hippocampus 机制 → `references/hippocampus-spec.md`
- GWT arbitrator 机制 → `references/gwt-spec.md`
- Narrator 层机制 → `references/narrator-spec.md`
- 概念图 + Hebbian 规则 → `references/concept-spec.md`
- 会话索引格式 → `references/session-index-spec.md`
- SOUL 快照格式 → `references/snapshot-spec.md`
- AUDITOR 评估历史 → `references/eval-history-spec.md`
- 工作流编排 → `pro/CLAUDE.md`
- 数据层边界 → `references/data-layer.md`
- SOUL 机制 → `references/soul-spec.md`
- Wiki 机制 → `references/wiki-spec.md`
- DREAM 机制 → `references/dream-spec.md`

---

> ℹ️ **2026-04-22 更新**：同步 EN R1 修复的 3 处段落（Archiver Candidate Routing / Hippocampus size arithmetic / Stage A 递归结构）

> 译注：本文译自 [英文版](../../../references/cortex-spec.md) 2026-04-21 snapshot。英文版为权威源，若有歧义以英文为准。
