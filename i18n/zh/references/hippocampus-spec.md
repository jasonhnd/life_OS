---
title: "Hippocampus · Agent Contract Spec"
scope: v1.7 Cortex Phase 1
audience: Life OS developers + orchestrator
status: spec
version: v1.7
layer: Cortex Phase 1 (cognitive retrieval)
related:
  - devdocs/brainstorm/2026-04-19-cortex-architecture.md
  - devdocs/architecture/cortex-integration.md
  - references/cortex-spec.md
  - references/concept-spec.md
  - references/session-index-spec.md
  - references/gwt-spec.md
  - pro/agents/hippocampus.md
translated_from: references/hippocampus-spec.md
translator_note: auto-translated 2026-04-21, 待人工校对
---

# Hippocampus · Agent Contract Spec（Agent 契约规范）

> 本文档规定 **hippocampus 子 agent** 的契约：它接收什么、返回什么、如何检索、以及如何失败。Agent 本身位于 `pro/agents/hippocampus.md`；本规范是其行为的权威来源。

---

## 1. 目的（Purpose）

**Hippocampus** 是一个 Claude Code 子 agent，为 Pre-Router Cognitive Layer（v1.7 工作流中的 Step 0.5）执行**跨会话记忆检索**（cross-session memory retrieval）。

它的单一职责：给定用户当前消息，产出一份**相关历史会话的概念级摘要**，使 GWT arbitrator 能够将其与其他 Pre-Router 认知信号合并，形成 ROUTER 的带注释输入。

它以生物学上的**海马体**（hippocampus）为原型 —— 大脑中负责把新体验绑定到情景记忆、按需取回情景的区域。在 Life OS 中，它在"用户刚才说了什么"与"系统已经从之前会话知道什么"之间架设桥梁。

Hippocampus **不做**：

- 替代 ROUTER 分诊
- 修改会话文件或概念文件（只读）
- 将检索结果持久化到当前帧之外
- 知晓其他 Pre-Router Cognitive Layer 输出（强制隔离）

---

## 2. 触发（Trigger）

**频率**：每条进入 ROUTER 的用户消息，在 RETROSPECTIVE 家务完成之后。

**并行性**：与 Pre-Router Cognitive Layer 的另外两个组件并行运行：

- Concept lookup（读取 `_meta/concepts/INDEX.md`）
- SOUL dimension health check（复用 RETROSPECTIVE 的 SOUL Health Report）

**执行预算**：

- 软超时（Soft timeout）：**5 秒** —— GWT arbitrator 等待的上限，到此点之后它会带着部分结果推进。这并**不**强制 hippocampus 返回；hippocampus 可以继续运行直到硬超时。任何在 5s 到 15s 之间到达的结果会被记录到 session trace 供事后复盘，但**不会**注入到当前 session 的 ROUTER 输入（GWT 已经整合并交棒了）。
- 硬超时（Hard timeout）：**15 秒** —— hippocampus 必须返回它已有的东西并终止。5s–15s 之间返回的结果只进 trace。

**不触发**：

- Start Session 调用（RETROSPECTIVE Mode 0 已加载近期上下文）
- Review Mode（无待决用户决策）
- 当 orchestrator 显式请求 `--no-cortex` 时（降级模式，用于调试）

---

## 3. Agent 定义 Frontmatter（Agent Definition Frontmatter）

实际 agent 文件（`pro/agents/hippocampus.md`）必须声明：

```yaml
---
name: hippocampus
description: "Cortex hippocampal retrieval — cross-session memory activation for Pre-Router Cognitive Layer"
tools: [Read, Grep, Glob]
model: opus
---
```

**工具约束理由**：

- `Read`：加载 INDEX.md 与单个会话 markdown 文件
- `Grep`：在 LLM 判断之前快速预过滤 INDEX.md
- `Glob`：枚举 `_meta/concepts/{domain}/*.md` 用于 Wave 2/3 查找
- **无 Write / Edit**：强制只读契约；概念文件修改仅发生在 ARCHIVER Phase 2

**模型**：`opus`。检索涉及跨可变措辞的语义匹配；Haiku 对 Wave 1 相关性评分的判断不足。v1.7 在 Opus 上运行整个 Wave 1 过程。

---

## 4. 输入契约（Input Contract）

Hippocampus 从 orchestrator 接收（作为结构化输入传入子 agent 提示）：

```yaml
hippocampus_input:
  current_user_message: string           # raw text, as typed
  extracted_subject: string | null       # non-null if ROUTER already performed intent clarification
  current_project: string                # bound project scope, e.g. "passpay"
  current_theme: string                  # e.g. "zh-classical", "ja-kasumigaseki"
  session_context:
    recent_inbox_items: [string]         # top 3-5 items from _meta/inbox/
    current_strategic_lines: [string]    # line IDs from _meta/strategic-lines.md
  meta:
    invocation_id: string                # UUID for tracing
    timestamp: ISO 8601
    soft_timeout_ms: 5000
    hard_timeout_ms: 15000
```

**明确不接收**（由 orchestrator 强制执行 —— 违反 = 信息隔离泄露）：

- 其他 Pre-Router Cognitive Layer 输出（concept lookup 结果、SOUL check 结果）
- 之前会话的转录（只有通过 INDEX.md 的摘要）
- SOUL.md 完整内容（隐私边界 —— hippocampus 看到概念标签，不看身份叙事）
- 超出 `current_theme` 的用户平台/环境细节
- 其他 agent 的思考过程（依 `pro/CLAUDE.md` Information Isolation 表）

为什么这种隔离重要：hippocampus 必须产出一个**独立信号**，让 GWT 能够与其他信号相衡量。若它已经看到 SOUL check 输出，它就失去了浮现互补但不同检索视角的能力。竞争需要独立。

---

## 5. 检索算法（3-Wave 扩散激活）（Retrieval Algorithm — 3-Wave Spreading Activation）

算法以生物学上的**扩散激活**（spreading activation，Collins & Loftus, 1975）为原型，适配于 Life OS 的 markdown-first 约束。三波，每波逐步扩大检索范围但置信度递减。

### Wave 1 —— 直接匹配（Direct Match）

1. **读取** `_meta/sessions/INDEX.md`（编辑器生成的每行一会话索引；格式见 `references/session-index-spec.md`）。
2. **Grep 预过滤**：若 `extracted_subject` 可用，对 INDEX.md 运行一次大小写不敏感正则过滤，将 1000+ 条目削到 <50 候选。若不可用，跳到 LLM 步骤，使用完整 INDEX。
3. **LLM 判断**（用户决策 #3 —— 无 embedding、无向量 DB）：把预过滤的索引行喂给 Opus，用如下提示：
   > "Current subject: `{subject}`. Below are past session summaries. Return the top 3-5 whose subject is semantically related to the current one. Return JSON only."
4. 从 `_meta/sessions/{session_id}.md` **读取完整内容** 每个候选。
5. **评分**：`score_wave1 = 0.6 * subject_similarity + 0.4 * keyword_overlap`，两个子分数均由 Opus 在 0-1 之间判断。
6. 保留 top 3-5 会话。

**Wave 1 输出**：`[{session_id, score, matched_concepts}]` —— 下游波的种子集。

### Wave 2 —— 强邻居（Strong Neighbors）

从 Wave 1 会话出发，沿**概念图**扩展以找到 Wave 1 因无共享表面关键词而错过的相关会话。

1. 对每个 Wave 1 会话，从其 YAML frontmatter 中提取 `concepts_activated` 与 `concepts_discovered` 列表。
2. 对每个 concept ID，**读取** `_meta/concepts/{domain}/{concept}.md`。
3. 从该概念的 `outgoing_edges` 列表中，**沿权重 ≥ 3 的边跟随**（强 synapse —— 见 `references/concept-spec.md` 权重语义）。
4. 对每个邻居概念，查其 `provenance.source_sessions` 字段 —— 这产出邻居概念被激活过的会话。
5. **去重** 对照 Wave 1 集合，保留**前 2-3 个新会话**，按复合分数排序：
   ```
   score_wave2 = 0.5 * edge_weight_normalized + 0.3 * concept_overlap + 0.2 * recency_decay
   ```
   其中 `recency_decay = exp(-days_since_session / 90)`。

**设计上有界**：Wave 2 最多增加 3 个会话。这防止概念图扇出爆炸检索预算。

### Wave 3 —— 弱邻居（Weak Neighbors）

再把图扩展一次，降低权重阈值。这捕捉"意外但有用"的连接，该连接 Wave 1（表面）和 Wave 2（强边）都不浮现。

1. 从 Wave 2 会话的概念出发，沿**权重 ≥ 1** 的边跟随（任何活跃边）。
2. 应用与 Wave 2 相同的 provenance 查找。
3. 去重，保留 top 1-2。
4. 评分：
   ```
   score_wave3 = 0.3 * edge_weight_normalized + 0.4 * concept_overlap + 0.3 * recency_decay
   ```
   原始边强度权重较低，语义重叠权重较高。

**显式上限**：Wave 3 最多贡献 2 个会话，整个检索集合总共不得超过 **5-7 个会话**。超出该上限会降低 GWT 仲裁质量（太多信号要相衡量）。

### 最终输出（Final Output）

将所有检索到的会话按其波内分数排序，但**注明每个来自哪一波** —— GWT 需要该 provenance 来校准显著性。

---

## 6. 输出契约（Output Contract）

Hippocampus 作为给 orchestrator 的最终消息返回一个结构化 YAML 块：

```yaml
hippocampus_output:
  current_subject: string
  retrieved_sessions:
    - session_id: string
      date: ISO 8601
      relevance_score: float              # 0-1, wave-calibrated
      reason: string                      # one sentence, why this matched
      wave: 1 | 2 | 3
      summary: string                     # 1-2 sentences, the session's core substance
      key_decisions: [string]             # 1-3 decision titles from the session
      applicable_signals:
        - signal_type: "decision_analogy" | "value_conflict" | "pattern_match"
          detail: string
  activated_concepts:
    - concept_id: string
      activation_strength: float          # 0-1, how strongly this retrieval activated the concept
  meta:
    sessions_scanned: integer             # total INDEX lines considered
    llm_tokens_used: integer              # estimated
    execution_time_ms: integer
    waves_completed: [1, 2, 3]            # partial if hard-timeout hit
    degraded: boolean                     # true if any wave skipped
    degradation_reason: string | null
```

**信号类型语义**：

- `decision_analogy` —— 过去会话面对过结构相似的决策（"你之前考虑过 X vs Y"）
- `value_conflict` —— 过去会话浮现过与此处相关的 SOUL 级张力
- `pattern_match` —— 过去会话表现出用户应再次注意的行为模式

---

## 7. 输出注入（Output Injection）

Hippocampus 输出**不**直接送达 ROUTER。它流向 **GWT arbitrator**，后者把它与 concept lookup 输出以及 SOUL check 输出合并为一份"带注释输入"。

最终带注释输入作为用户消息的一部分到达 ROUTER，界限清晰划分：

```markdown
[COGNITIVE CONTEXT — reference only, not user input]

Related past decisions (hippocampus):
- 2026-04-19 | passpay | 技术白皮书 v0.6 (score 8.2) — similar refinement pattern
- 2026-03-28 | passpay | 合规架构评估 (score 6.5) — GOVERNANCE scored low, may repeat
- 2026-04-15 | passpay | 商业白皮书 v1.0 (score 7.8) — same project cluster, recent

[END COGNITIVE CONTEXT]

User's actual message: {original_message}
```

**放置理由**（重要 —— 未经协商不得修改）：

- 认知上下文放在**用户消息**中，不是系统提示。系统提示会被缓存；易变的按会话检索会在每轮破坏提示缓存。
- ROUTER 可以选择忽略认知上下文（例如，用户显式说 "ignore history, reconsider from scratch"）。该注释**是建议性的，非权威性的**。
- `[COGNITIVE CONTEXT]` 分隔符是字面的 —— ROUTER 解析它们以把建议性内容与真实用户输入分开。

---

## 8. 性能预算（Performance Budget）

| 步骤 | 目标 | 备注 |
|------|--------|-------|
| 读取 `INDEX.md` | <100ms | 2000 会话时文件大小 <1MB |
| Grep 预过滤 | <50ms | 对 INDEX.md 的 Ripgrep |
| 对过滤后索引的 LLM 判断 | 2-3s | Opus 上约 5000 tokens |
| 读取 3-5 个会话文件 | <300ms | 并行读取 |
| Wave 2 概念查找 | 1-2s | Opus 判断边相关性 |
| Wave 3 扩展 | 1s | 范围更窄 |
| **总目标** | **<7 秒** | 远在 15s 硬超时之内 |

**关于超时语义的说明**：<7s 总数是**常规情况目标**——即流水线在一次典型调用中设计要达到的预算。§2 的 5s 软超时 / 15s 硬超时描述的是**尾部行为**：软超时是 GWT 停止等待的时点（而不是 hippocampus 停止运行的时点），硬超时是 hippocampus 无论如何都必须终止的绝对上限。任何超过 5s 的运行仍然会完成并记录到 session trace，但它的输出不会重新进入当前 ROUTER 循环。

**可扩展性备注**：在 2000+ 会话下，INDEX.md 将增长到接近 2MB。考虑按月分页（`INDEX-2026-04.md`），并在该规模下默认只读最近 6 个月。Phase 1 不实现分页。

**Token 预算**：

- LLM 判断调用：约 5000 tokens 输入 + 约 500 输出
- Wave 2 边相关性：约 1500 tokens 输入 + 约 200 输出
- 每次调用总计：不超过 8000 tokens

单次调用成本（Opus 定价下）：大约 $0.05-0.10，取决于会话上下文大小。这与 brainstorm §10 中的通用版本成本目标相符。

---

## 9. 失败模式（Failure Modes）

Hippocampus 必须优雅降级 —— 失败的检索不应阻塞决策工作流。

| 失败 | 行为 |
|---------|----------|
| `_meta/sessions/INDEX.md` 不存在 | 若可用则通过 Bash 运行 `tools/reindex.py`；否则返回空输出并 `degraded: true, degradation_reason: "INDEX_MISSING"` |
| INDEX.md 存在但为空（新 second-brain） | 返回空 `retrieved_sessions`，注明 "first session — no cross-session memory yet" |
| LLM 判断调用失败（API 错误、限流） | 回退到对 INDEX.md 的纯关键词匹配（无语义评分），置 `degraded: true` |
| Wave 2 目标概念文件缺失 | 跳过该特定分支，用剩余分支继续 Wave 2 |
| 整个概念图缺失 | 跳过 Wave 2-3，返回 Wave 1 结果并 `waves_completed: [1]` |
| 硬超时（>15s） | 返回部分结果（完成了什么波），把事件记录到 `_meta/eval-history/hippocampus-{date}.md` |
| 会话文件读取错误 | 跳过该会话，在 `degradation_reason` 中注明 |

**所有失败都记录到 `_meta/eval-history/`**，AUDITOR 在会话结束巡查时读取。同类失败反复发生触发"模块质量降级"旗标 —— 与 brainstorm §6 的 Escalate rate limit 同一机制。

---

## 10. 缓存（v1.7 范围之外）（Caching — Out of Scope for v1.7）

每次调用都重新扫描 INDEX.md 并重读概念文件。在 2000 会话下这仍是不到 2MB 的 I/O 和不到 7s 的总延迟，因此 **v1.7 无缓存**。

缓存在 v1.7 范围之外。若 INDEX.md 超过 5MB，或在 v1.7 运行期间 hippocampus p95 延迟超过 10s，`session-index-spec.md` §8 中的扩容触发器点火（先按月分片 INDEX，再把缓存视为独立的 spec 修订）。

---

## 11. 质量指标（Quality Metrics）

Hippocampus 沿三个维度评估。每个由 AUDITOR 在会话结束时计算并追加到 `_meta/eval-history/cognitive-annotation-{date}.md`。

### 11.1 `retrieved_session_count`

它找到了什么东西吗？一旦 second-brain 有 >30 个会话，健康基线是每次调用 3-5 次检索。在有足够历史的情况下持续零检索 = bug 信号。

### 11.2 `relevance_score_distribution`

top 排名结果真的相关吗？由 AUDITOR 用启发式自评：「ROUTER 是否在其推理中引用了这个会话？」

健康：top-1 相关性分数中位数 ≥ 0.7。若中位数持续 2 周 < 0.5，Wave 1 LLM 提示需要重新调校。

### 11.3 `user_signals_used`

ROUTER / 下游 agent 是否**真的引用**了检索到的内容？AUDITOR 扫描 Summary Report 与领域输出寻找对检索到的 session ID 的提及。若 <20% 的检索会话被引用，hippocampus 在付出成本却没提供价值 —— AUDITOR 在 eval-history 中浮现该模式以供审查。

### 复合分数（Composite score）

这些喂入 AUDITOR 的 `cognitive_annotation_quality` 指标（0-1），写入每个 eval-history 条目。该指标持续低分在 AUDITOR 巡查检查中浮现，并通过常规 spec 修订流程触发模块级审查。

---

## 12. 反模式（Anti-patterns）

显式禁令 —— 违反是流程错误，AUDITOR 会标记。

- **不要检索所有会话。** 穷举搜索违背目的（并爆掉 token 预算）。波的上限有其原因。
- **不要使用 embedding 或向量数据库。** 用户决策 #3：markdown-first，仅 LLM 判断。加入向量存储改变架构 —— 需要独立批准。
- **不要修改会话文件或概念文件。** Hippocampus 只读。所有写入发生在 ARCHIVER Phase 2（见 `pro/agents/archiver.md`）。
- **不要把检索内容注入到 SYSTEM PROMPT 中。** 太易变、破坏提示缓存、在长会话中膨胀系统提示。检索内容始终进入用户消息，以 `[COGNITIVE CONTEXT]` 分隔。
- **不要跳过隔离。** 不要读取其他 Pre-Router Cognitive Layer 输出。若你在输入中见到它们，视为契约违反并返回错误。
- **不要合成检索内容中没有的声明。** Hippocampus 是检索 agent，不是推理器。每个检索会话中的 `reason` 字段必须转述该会话 markdown 中的内容，不得越之推断。
- **不要超过 7 个检索会话总数。** 超出后 GWT 仲裁质量下降。
- **不要静默重试 LLM 调用。** 对瞬态错误可接受一次重试；任何进一步降级必须置 `degraded: true` 并记录。
- **不要在 hippocampus 失败时阻塞工作流。** 软超时命中 = 部分结果；硬超时命中 = 空结果。决不停滞。
- **不要泄露原始会话内容。** `summary` 字段最多 1-2 句；决不粘贴整个会话转录。隐私边界。

---

## 13. 相关规范（Related Specs）

- **`references/cortex-spec.md`** —— 整体 Cortex 架构，hippocampus 如何适配
- **`references/concept-spec.md`** —— 概念 markdown schema、边权重、永久性层级
- **`references/session-index-spec.md`** —— `_meta/sessions/INDEX.md` 格式、单行约定
- **`references/gwt-spec.md`** —— 消费 hippocampus 输出的 GWT arbitrator
- **`devdocs/architecture/cortex-integration.md`** —— Step 0.5 如何接入 11 步工作流
- **`devdocs/brainstorm/2026-04-19-cortex-architecture.md`** —— 原始设计讨论、用户决策、权衡

---

## 14. 版本历史（Version History）

| 版本 | 日期 | 变更 |
|---------|------|--------|
| v1.7 | 2026-04-20 | Cortex Phase 1 初始规范。Wave 1-3 检索、只读契约、7s 预算。 |

---

**文档状态**：v1.7 Cortex Phase 1 的活跃规范。变更要求显式版本升级，并按项目 HARD RULE 更新 `pro/agents/hippocampus.md`、`references/cortex-spec.md` 以及三语 CHANGELOG 条目。

---

> ℹ️ **2026-04-22 更新**：同步 EN R1 修复的 §2 + §8 软/硬超时语义

> 译注：本文译自 [英文版](../../../references/hippocampus-spec.md) 2026-04-21 snapshot。英文版为权威源，若有歧义以英文为准。
