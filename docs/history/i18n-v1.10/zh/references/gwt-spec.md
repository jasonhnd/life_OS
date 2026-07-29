---
title: "GWT Arbitrator Spec · Cortex Layer"
version: 1.7
status: pre-implementation
audience: Life OS implementers
scope: Cortex Pre-Router Cognitive Layer — signal arbitration
related:
  - references/cortex-spec.md
  - references/hippocampus-spec.md
  - references/concept-spec.md
  - references/soul-spec.md
  - devdocs/brainstorm/2026-04-19-cortex-architecture.md
  - devdocs/architecture/cortex-integration.md
translated_from: references/gwt-spec.md
translator_note: auto-translated 2026-04-22, 待人工校对
---

# GWT Arbitrator 规范（GWT Arbitrator Spec）

## 1. 目的（Purpose）

**GWT（Global Workspace Theory，全局工作空间理论）Arbitrator** 整合 Pre-Router Cognitive Layer 子 agent 发出的信号，并生成 ROUTER 接收到的**带注释输入**（annotated input）。

它以 Stanislas Dehaene 的**全局神经元工作空间**（Global Neuronal Workspace）理论为基础：许多专门化的模块并行运行，它们的输出竞争中央工作空间，只有最强的信号被全局广播。在此框架下，意识（consciousness）就是"点燃"（ignition）的瞬间 —— 某个信号赢得竞争并被发布给其他所有模块。

在 Life OS 中，竞争发生在以下三者之间：

- 来自 hippocampus 的已检索记忆
- 来自 concept store 的直接概念匹配
- SOUL 维度信号（身份对齐或冲突）

Arbitrator 是**瓶颈点**（choke point），防止 ROUTER 信息过载，同时保留与决策最相关的上下文。

---

## 2. 触发（Trigger）

- 在当前会话轮次中，所有 Pre-Router 并行子 agent（hippocampus、concept lookup、SOUL dimension check）完成工作**之后**运行。
- **每会话轮次只调用一次**（Single invocation per session turn）。从不循环。从不在轮次中重新触发。
- **超时预算**：5 秒软目标（soft target），10 秒硬上限（hard ceiling）。
- 若触及硬上限，arbitrator 使用已评分过的信号发出部分结果（参见 §13）。

---

## 3. Agent 定义（Agent Definition）

```yaml
---
name: gwt-arbitrator
description: "Cortex GWT arbitration — consolidates Pre-Router signals into annotated ROUTER input"
tools: [Read]
model: opus
---
```

设计上只读（Read-only by design）。Arbitrator 永远不写入持久化存储。所有变更（Hebbian 更新、概念创建、synapse 强化）都在 ARCHIVER Phase 2 发生。这保持了会话中路径的廉价和无副作用。

---

## 4. 输入契约（Input Contract）

orchestrator 向 arbitrator 传递四项输入：

```
hippocampus_output:      yaml  # retrieved sessions, activated concepts
concept_lookup_output:   yaml  # direct concept matches to current subject
soul_check_output:       yaml  # relevant SOUL dimensions and their status
current_user_message:    string
```

每个上游源生产一组使用统一信封的**信号**（signals）(评分见 §5，信号类型见 §6)。缺失的源可以容忍 —— 首次会话可能没有 hippocampus 输出，arbitrator 用它所拥有的继续推进。

---

## 5. 显著性公式（Salience Formula）（CRITICAL — 明确且固定）

每个信号都用一个称为 `salience` 的**单一标量**打分：

```
salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2
```

此公式在 v1.7 中固定。每个分量是 `[0.0, 1.0]` 区间的浮点数，定义如下。

### 5.1 urgency（紧急度）

| 值 | 条件 |
|-------|-----------|
| 1.0 | 有 7 天内截止的 action item |
| 0.6 | SOUL 冲突警告（`core` 维度正在受到挑战） |
| 0.3 | 检测到重复模式（同一主题最近出现 3 次以上） |
| 0.0 | 无时间压力的背景上下文 |

### 5.2 novelty（新颖度）

| 值 | 条件 |
|-------|-----------|
| 1.0 | 信号从未出现过 |
| 0.6 | 信号先前出现 1–2 次 |
| 0.2 | 信号出现 3 次以上（疲劳 —— 用户已经看过） |
| 0.0 | 已经执行并解决 |

### 5.3 relevance（相关性）

信号载荷（signal payload）与用户消息当前主题之间的关键词 / 概念重叠得分。由 arbitrator 内部的 **LLM 判断**（LLM judgment）计算。

LLM 接收信号内容与当前用户消息，被要求产出 `[0.0, 1.0]` 区间的单个浮点数，代表信号与当前决策的直接相关程度。当 LLM 判断失败时，关键词重叠作为确定性回退（参见 §13）。

### 5.4 importance（重要性）

层级名称与 `references/soul-spec.md` §Tiered Reference by Confidence 和 `references/snapshot-spec.md` §Tier Mapping 一致。所有置信度区间使用半开区间 `[a, b)` —— 下界闭（inclusive），上界开（exclusive）。边界值永远归属**上一层**（例如：置信度恰为 0.3 属于 `secondary`，而非 `emerging`；置信度恰为 0.7 属于 `core`，而非 `secondary`）。

| 值 | 条件 |
|-------|-----------|
| 1.0 | SOUL `core` 维度（置信度 ∈ `[0.7, 1.0]`） |
| 0.7 | SOUL `secondary` 维度（置信度 ∈ `[0.3, 0.7)`） |
| 0.5 | 关联一个关键路径项目（在 concept metadata 中标记） |
| 0.3 | SOUL `emerging` 维度（置信度 ∈ `[0.2, 0.3)`） |
| 0.2 | 无身份或项目关联的一般上下文（或 `dormant` 维度，置信度 ∈ `[0.0, 0.2)`，仅作为上下文包含） |

当多个条件同时适用时，使用**最高**匹配值。

---

## 6. 整合的信号类型（Signal Types Consolidated）

arbitrator 按来源识别以下信号类型：

### 来自 hippocampus

- `decision_analogy` —— 与当前主题模式相似的过往决策
- `value_conflict` —— 过往与 SOUL 冲突的会话，在此相关
- `outcome_lesson` —— 结果具有教益的过往决策

### 来自 concept lookup

- `canonical_concept` —— 直接提及或暗示的已确认概念
- `emerging_concept` —— 同一领域内的 tentative 概念（尚未 canonical）

### 来自 SOUL check

- `tier_1_alignment` —— core 身份维度支持此方向
- `tier_1_conflict` —— core 身份维度冲突（**半否决信号，semi-veto signal**）
- `tier_2_relevant` —— secondary 维度适用于此主题
- `dormant_reactivation` —— 一个 dormant 维度刚刚再次变得相关

对 arbitrator 而言，除了 `signal_type`、`source`、`payload` 与四个评分分量之外，信号都是不透明的。Arbitrator 不会内省 payload 以派生新信号；每个信号必须有具名来源。

---

## 7. 仲裁算法（Arbitration Algorithm）

仲裁由五个确定性步骤加一个 LLM 判断步骤（relevance）组成：

1. **Ingest（摄入）** —— 从 orchestrator 接收所有信号及其元数据。
2. **Score（评分）** —— 使用 §5 的公式为每个信号计算 `salience`。Relevance 使用 LLM 判断；其他分量都是基于规则的。
3. **Rank（排序）** —— 按 salience 降序排序信号。
4. **Cap（封顶）** —— 取总体 top **5** 信号（硬上限，防止信息过载）。
5. **检测冲突**：
   - 任何 `tier_1_conflict` 信号 → **提升**至输出中的 ⚠️ SOUL CONFLICT 头部。
   - 矛盾的 `decision_analogy` 信号（过往决策建议相反方向）→ 在 pattern observations 块中标记为 "inconsistent precedent"。
6. **Compose（组装）** —— 按 §8 渲染带注释的输出。

arbitrator **不得虚构**任何信号。输出中的每一项都必须可追溯到特定的输入信号。

### 7.1 工作示例（Worked Example）

给定来自上游子 agent 的三个信号：

| id | type | urgency | novelty | relevance | importance | salience |
|----|------|---------|---------|-----------|------------|----------|
| s1 | `decision_analogy` | 0.3 | 0.6 | 0.8 | 0.5 | 0.55 |
| s2 | `tier_1_conflict` | 0.6 | 1.0 | 0.9 | 1.0 | 0.85 |
| s3 | `canonical_concept` | 0.0 | 0.2 | 0.7 | 0.5 | 0.35 |

排序后：`[s2, s1, s3]`。`s2` 触发 SOUL CONFLICT 提升。三者都在 top-5 上限内，都被组装到输出中。`s3` 的 salience 0.35 仍能入选，因为单信号下限（per-signal floor）是 0.3。

---

## 8. 输出格式 —— 带注释的 ROUTER 输入（Output Format — Annotated ROUTER Input）

arbitrator 发出一个单独的 Markdown 块，在到达 ROUTER 时**前置**（prepended）到用户消息：

```markdown
[COGNITIVE CONTEXT — reference only, not user input]

⚠️ SOUL CONFLICT: [only if `core` dimension challenged]
This decision challenges your "{dimension_name}" (confidence {X})

📎 Related past decisions:
- {session_id} ({date}): {reason}, score {X}/10

🧬 Active concepts:
- {concept_id} (canonical, weight {X}, last activated {when})

🔮 SOUL dimensions:
- {dimension} ({tier}, {trend}): {support/challenge status}

💡 Pattern observations:
- {any salience ≥ 0.8 signals not covered above}

[END COGNITIVE CONTEXT]

User's actual message: {original}
```

每个项目符号**仅当** top-5 中至少有一个该类别的信号时才发出。空类别折叠（参见 §9）。

---

## 9. 信号抑制规则（Signal Suppression Rules）

为防止注释噪声：

- 若评分后**信号总数为 0**，发出**空标记**（empty marker）—— 而非完整框架文本。ROUTER 只看到 `User's actual message: …`。
- 若**所有信号的 salience < 0.3**，发出 `(no high-salience signals)` 作为单行标记，并跳过类别块。
- 若存在 **SOUL CONFLICT** 但没有相关过往决策，仍然发出 SOUL 块（冲突本身是承重的）。
- **每类别上限**：最多 5 个相关决策、最多 5 个活跃概念、最多 5 个 SOUL 维度。每类别上限是**每块的局部最大值**，而非 §7 全局 top-5 之外的附加槽位。§7 的全局 top-5 是硬天花板，总是最先强制执行。实际表现：当某类别上限先于全局 top-5 预算耗尽时被命中，剩余的全局槽位保持空闲；当全局 top-5 先被填满时，每类别上限被覆盖。"5 个 SOUL 维度填满输出" 这个例子，仅表示全部 5 个全局槽位碰巧在单一类别中得分最高。

---

## 10. 平局打破规则（Tie-Breaking Rules）

当两个信号在评分后**salience 相同**时，按以下顺序打破平局：

1. **更新者优先**（Newer first）—— 偏向 `timestamp` 更近的信号。
2. **importance 更高**（Higher importance）—— 若仍平局，偏向 `importance` 更高的信号。
3. **按 `signal_id` 字母序**（Alphabetical by `signal_id`）—— 完全确定性的回退，保证同样的输入总是产生同样的排序。

平局打破必须确定性（deterministic）。无随机化。同样的输入两次运行必须产生同样的输出排序。

---

## 11. 性能预算（Performance Budget）

| 阶段 | 目标 |
|-------|--------|
| 接收输入（在上下文中传递） | 瞬时 |
| relevance 评分的 LLM 判断 | ~2 秒，~3,000 tokens |
| 组装 | < 1 秒 |
| **总目标** | **< 3 秒** |

软超时（§2）为 5 秒；硬上限为 10 秒。超过硬上限触发 §13 的部分输出失败模式。

---

## 12. 注入位置（Injection Location）（CRITICAL for prompt caching）

认知上下文作为**用户消息的前缀**（prefix to the user message）注入，置于**用户角色**（user role）内。它**不**被加入系统提示（system prompt）。

**原因**：Anthropic 的 prompt cache 只在系统提示稳定时命中。若在系统提示中注入，每一次动态的认知注释都会失效缓存。将动态内容保留在 user role 中可保留跨轮次的缓存命中率。

**实现**：

1. Orchestrator 调用 arbitrator 并捕获其输出。
2. Orchestrator 把 arbitrator 的块**前置**到 ROUTER 的输入用户消息。
3. ROUTER 看到合并后的输入。它将认知上下文用作**参考**（reference），而不是字面的用户请求。
4. ROUTER 的系统提示不受触及。

ROUTER 的分诊规则不变。它把 COGNITIVE CONTEXT 块视为**可能**在决定派遣哪些领域 agent 时参考的辅助信息。

---

## 13. 失败模式（Failure Modes）

| 失败 | 行为 |
|---------|----------|
| **无 Pre-Router 输入**（有史以来第一次会话） | 发出空标记。ROUTER 只看到原始用户消息。 |
| **单一输入源**（例如 hippocampus 未返回任何内容） | 用确实返回信号的源继续推进。 |
| **relevance 的 LLM 判断失败或超时** | 回退到信号 payload 与用户消息之间的**关键词重叠**（keyword overlap）作为 relevance 得分。 |
| **Arbitrator 总超时**（硬上限） | 使用目前获得的最佳评分信号发出部分输出，上限为 top-5。向块追加单行 `(partial — timed out)`。 |
| **上游传来的格式异常信号** | 跳过该信号。不崩溃。内部记录日志以供 AUDITOR 审查。 |

优雅降级（Graceful degradation）不可妥协：arbitrator 失败**不得**阻塞 ROUTER。当存疑时，orchestrator 退回到 v1.6.2a 行为（原始用户消息直入 ROUTER）。

---

## 13.1 降级层次（Degradation Hierarchy）

当多个失败叠加时，按以下顺序应用：

1. 缺失源 → 用存在的源继续。
2. LLM relevance 失败 → 关键词重叠回退。
3. 硬超时 → 部分输出。
4. 灾难性 arbitrator 失败 → 空标记 + 落回到原始 ROUTER 行为。

在每一步，输出仍然是一个有效的注释块（即使为空）。ROUTER 必须绝不接收到格式错误或半封闭的块。

---

## 14. 质量指标（Quality Metrics）

用于 AUDITOR 的 `eval-history` 轨道：

- **`cognitive_annotation_quality`（0–10）** —— ROUTER 是否有成效地引用了注释？
  - 具体而言：REVIEWER 是否引用了注释？任何领域 agent 在讨论中是否引用了它？
- **`annotation_utilization_rate`** —— 至少有一个下游 agent 使用了注释中的 `signal_id` 的会话比例。
- **`suppression_precision`** —— 当 arbitrator 发出 SOUL CONFLICT 警告时，REVIEWER 独立标记同一问题的频率。

AUDITOR 将低分会话浮现供审查。若注释质量在 30 天内趋势下降，AUDITOR 的巡检（patrol inspection）会在 eval-history 中标记该模式，模块级的范围变更按正常 spec 修订流程推进。

---

## 15. 反模式（Anti-patterns）

- **不要虚构信号**。输出中的每个信号必须有具名来源和上游 payload。
- **不要仅按 SOUL 层级排序**。Importance 只是四个 salience 分量之一。urgency 和 novelty 都高的 `emerging` 信号，可以合法地胜过 urgency 低的 `core` 信号。
- **不要在注释中包含原始子 agent 输出**。整合为概念引用和简短摘要。完整 payload 保留在 frame md 中以供可追溯。
- **不要修改系统提示**。所有动态内容都位于 user role 消息中（参见 §12）。
- **每类别不超过 5 个信号、总体不超过 5 个信号**。信息过载是失败模式，不是特性。
- **不要从 arbitrator 内部调用 hippocampus 或 concept lookup**。上游子 agent 是事实来源；arbitrator 是纯消费者。

---

## 16. 相关规范（Related Specs）

- `references/cortex-spec.md` —— 完整 Cortex 架构
- `references/hippocampus-spec.md` —— 信号来源：跨会话检索
- `references/concept-spec.md` —— 信号来源：concept store 与 synapse graph
- `references/soul-spec.md` —— SOUL 层级定义与置信度带
- `devdocs/brainstorm/2026-04-19-cortex-architecture.md` —— 设计原理（§3 schema、§4 salience 辩论）
- `devdocs/architecture/cortex-integration.md` —— arbitrator 如何在 Step 0.5 插入 11 步工作流

---

**文档状态**：pre-implementation 规范，v1.7。此处编码的行为为规范性（normative）。偏离需要先更新本规范再改代码。

---

> ℹ️ **2026-04-22 更新**：同步 EN R3.2 修复 §5.4 tier 边界 + §9 per-category cap 措辞

> 译注：本文译自英文版 2026-04-22 snapshot；英文为权威源，歧义以英文为准。
