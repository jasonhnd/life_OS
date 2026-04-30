---
title: "Narrator Spec — Grounded Generation Layer for Cortex"
version: v1.7
status: legacy
authoritative: false
superseded_by: pro/agents/narrator.md
scope: references
audience: Life OS maintainers + orchestration implementers
last_updated: 2026-04-20
related:
  - references/cortex-spec.md
  - references/hippocampus-spec.md
  - references/gwt-spec.md
  - references/eval-history-spec.md
  - devdocs/brainstorm/2026-04-19-cortex-architecture.md
  - devdocs/architecture/cortex-integration.md
  - pro/agents/router.md
  - pro/CLAUDE.md
translated_from: references/narrator-spec.md
translator_note: auto-translated 2026-04-22, 待人工校对
---

# Narrator 规范 · 基于证据的生成层（Narrator Spec · Grounded Generation Layer）

> narrator 层是 ROUTER 的输出阶段。它产出面向用户的文本，同时防止虚构（hallucination）。每个实质性声明都携带一个回指底层信号的引用。

---

## 1. 目的（Purpose）

narrator 层是 ROUTER 的输出阶段，产出面向用户的文本，同时防止虚构。

其设计基于 Michael Gazzaniga 的**左脑诠释器**（left-brain interpreter）研究。裂脑（split-brain）实验显示，人类的左半球会**编造**自洽的故事，哪怕它并不掌握其被要求解释的行为背后的真实数据。大脑产出流畅、连贯、完全虚假的因果叙事 —— 并真诚地相信它。这是一个**缺陷**（bug），不是特性。Cortex 不得继承它。

narrator 输出中的每个实质性声明（substantive claim）都必须引用其底层信号。没有引用，声明就不能交付。Cortex 绝不得在没有证据支撑的情况下发出的例子：

- "你一直在承诺问题上挣扎。" —— 无 SOUL 信号。
- "上次你做类似决定时……" —— 无 hippocampus 会话。
- "你的 Finance 领域通常认为……" —— 无过往 score 模式。

若没有信号，就没有声明。这是 narrator 的核心不变量（core invariant）。

---

## 2. 设计原则 · 基于证据的生成（Design Principle · Grounded Generation）

narrator 输出中的每个**实质性声明**（substantive claim）都必须携带一个 `signal_id` 引用。没有引用的声明会被验证器（validator）拒绝。这防止三种失败模式：

1. **历史编造**（Historical confabulation）—— 虚构一个未发生的过去。
2. **模式编造**（Pattern confabulation）—— 虚构数据不显示的行为趋势。
3. **跨会话编造**（Cross-session confabulation）—— 虚构决策之间从未存在的链接。

narrator 不是创意层。它是**基于证据的组合层**（grounded composition layer），将经过验证的信号集转化为可读的散文。

基于证据的生成有两个硬性要求：

- narrator 必须能访问当前会话的**信号来源注册表**（signal source registry）(§9)。
- 每个实质性句子必须指回该注册表中的一条或多条条目。

若注册表为空（例如 direct-handle 且无子 agent 被派生），narrator 降级为 pass-through（§13）。

---

## 3. 实质性声明 vs 连接性声明（Substantive vs Connective Claims）

并非每个句子都需要引用。机械地为话语黏合剂（discourse glue）加引用会让输出不可读而不增加真值。

**Substantive（实质性，需要引用）** —— 若删除句子会移除事实内容，则句子为实质性：

- 历史性："上次你做了 X……"
- 模式："你倾向于……"
- SOUL："这与你的价值 Y 一致。"
- 决策含义："GOVERNANCE 关切的是……"
- 跨会话链接："与你在项目 Z 中的决策相关。"
- 数值 / score 声明："Finance 给此打了 6/10。"
- 归因："ADVISOR 标记了情感权重。"

**Connective（连接性，无需引用）** —— 话语黏合剂（discourse glue）：

- 过渡："让我梳理一下。"
- 框架："分析显示如下。"
- 元评论："我会给出一个简短摘要。"
- 开场 / 结语："好的，看一下这个……"
- 纯改写："换句话说……"

**判断规则**：若删除句子会移除事实内容 → substantive。若仅是话语黏合剂 → connective。验证器（§8）在检查引用之前使用此规则。

---

## 4. 引用格式（Citation Format）

### 行内语法（Inline syntax）

```
{claim text} [signal_id] {continued text}
```

一条声明可以携带多个引用：

```
{claim text} [signal_id_1][signal_id_2] {continued text}
```

引用出现在它支撑的子句**末尾**，在任何将子句与下一个子句分隔的标点之前。

### 示例（Examples）

```
Your past "passpay-v06-refinement" session [S:claude-20260419-1238] shows a similar 5-round iteration pattern, with GOVERNANCE scoring 5/10 [D:passpay-governance-score].

This conflicts with your "risk-tolerance" dimension (confidence 0.72) [SOUL:risk-tolerance-v3].

Finance and Execution disagreed by 4 points [D:finance-score-6][D:execution-score-2], triggering COUNCIL debate.
```

### 前缀约定（Prefix conventions）

引用 ID 使用固定前缀以指示来源类型：

| 前缀 | 含义 | 示例 |
|---------|-------------------------------|--------------------------------------------|
| `S:`    | session_id                    | `S:claude-20260419-1238`                   |
| `D:`    | 特定领域 score / 字段         | `D:passpay-governance-score`               |
| `SOUL:` | SOUL 维度                     | `SOUL:risk-tolerance-v3`                   |
| `C:`    | 概念                          | `C:method:iterative-document-refinement`   |
| `W:`    | wiki 条目                     | `W:finance/compound-interest`              |
| `P:`    | user-patterns.md 中的模式     | `P:avoids-family-topic-on-weekends`        |

前缀是**固定的**（fixed）。narrator 不得发明新前缀。若某类来源不能映射到上述之一，narrator 不得引用它（因此必须从一开始就不做该实质性声明）。

---

## 5. Narrator 调用（Narrator Invocation）

narrator 作为 **Step 7.5** 插入到 pro/CLAUDE.md 工作流中，位于 Step 7 Summary Report 组装之后、Step 8 AUDITOR 之前：

```
Step 7: Summary Report (ROUTER composes)
  ↓
Step 7.5: Narrator Layer
  - ROUTER sends Summary Report + signal source list to narrator subagent
  - Narrator rewrites output with citations
  - Validator subagent (Claude Code subagent, not Anthropic API) checks citations
  - If validation fails, narrator regenerates
  ↓
Step 8: AUDITOR
```

Step 7.5 仅在 **Full Deliberation** 路径下被调用。Express 分析（Step 1E）生成简报（brief report），跳过 Step 7.5。Direct-handle 和 STRATEGIST 会话完全跳过它（§13）。

---

## 6. Narrator Agent

ROUTER 自身处理 narrator 角色。**不存在独立的 `pro/agents/narrator.md` 文件**。narrator 行为通过 pro/CLAUDE.md 编排更新来配置，并存在于 ROUTER 的输出组装职责之内。

理由：ROUTER 已经拥有 Summary Report 组装（Step 7）；narrator 是该阶段的延伸，而不是新角色。独立的 narrator agent 会复制 ROUTER 的上下文。改写 + 引用不是新决策 —— 把它保留在 ROUTER 内部保持了面向用户输出的单一所有权。

只有**验证器**（validator）是独立的子 agent（§7）。

---

## 7. 验证器子 agent（Validator Subagent）

创建一个新子 agent 文件：`pro/agents/narrator-validator.md`。

```yaml
---
name: narrator-validator
description: "Validates narrator citations against signal sources (Cortex)"
tools: [Read]
model: sonnet
---
```

### 为何选用 Claude Code 子 agent，而非外部 Haiku API

用户决策 #9（在 v1.7 Cortex 设计期间记录）：使用 Claude Code 子 agent，而非外部 Anthropic Haiku API 调用。原因：

- **无外部 API 成本** —— 子 agent 运行在同一个 Claude Code 会话中，消耗用户已付费的 Claude 计划预算，而不是独立的 Haiku API 账户。
- **Cortex 总边际成本 ≈ 每月 $0.20-0.50**（用户决策 #8 预算范围），分摊到 hippocampus（每次调用 ~$0.05-0.10）+ GWT arbitrator（~$0.01-0.03）+ narrator-validator（~$0.01-0.02）。具体数字将在 v1.7 生产环境中校准；此范围是目标而非硬性合约。
- **无 API key 管理** —— 无外部配置、轮换或预算。
- **与 Life OS 立场一致** —— 所有智能都运行在会话内；依赖 Haiku API 会违背该立场。
- **足够快** —— sonnet 对引用验证而言可以接受；延迟保持在性能预算（§11）之内。

验证器子 agent 只有 `Read`。它不写入文件、不调用 MCP 工具、也不接触网络。

---

## 8. 验证算法（Validation Algorithm）

### 输入（Input）

验证器接收：

- `narrator_output` —— ROUTER 在 Step 7.5 重写所产出的完整 markdown 文档，带有行内引用。
- `signal_sources` —— 当前会话的信号来源注册表（§9）。

### 流程（Procedure）

对 `narrator_output` 中的每个句子：

1. 使用 §3 的规则把句子分类为 **substantive** 或 **connective**。
2. 若为 connective → 跳过。
3. 若为 substantive：
   1. 从句子中提取所有行内引用 `[signal_id]`。
   2. 对每个引用：
      1. 解析前缀（S、D、SOUL、C、W、P）。若前缀未知 → `format_error`。
      2. 在 `signal_sources` 中查找 `signal_id`。若缺失 → `missing_signal`。
      3. 读取所引用的内容（文件 / 字段 / 维度），并核实句子的声明被该内容支撑。若内容不支撑该声明 → `unsupported_claim`。
4. 若句子为 substantive 但**零**引用 → `missing_signal`（标记为 "no citation"）。

### 输出（Output）

```yaml
validation:
  total_citations: integer
  valid: integer
  invalid:
    - position: char_offset_in_narrator_output
      citation: string          # the raw "[signal_id]" token, or "" if missing
      reason: missing_signal | unsupported_claim | format_error
      claim_text: string        # the sentence that contains the problem
  groundedness_score: float     # 0.0–1.0
```

### 基础得分（Groundedness score）

```
groundedness_score = valid / max(total_citations + missing_citation_count, 1)
```

其中 `missing_citation_count` 是零引用的实质性句子数量。

### 阈值（Threshold）

`groundedness_score ≥ 0.9` 才能交付 narrator 输出。低于阈值 → narrator 带着错误反馈重新生成（§10）。

---

## 9. 信号来源注册表（Signal Source Registry）

会话执行期间，每个子 agent 发出带 ID 的信号。narrator 在 Step 7.5 接收该注册表。

### 注册表格式（Registry format）

```yaml
signal_sources:
  - id: S:claude-20260419-1238
    type: session
    file: _meta/sessions/claude-20260419-1238.md
    producer: hippocampus
  - id: SOUL:risk-tolerance-v3
    type: soul_dimension
    ref: SOUL.md#risk-tolerance
    producer: soul_check
  - id: C:method:iterative-document-refinement
    type: concept
    file: _meta/concepts/method/iterative-document-refinement.md
    producer: concept_lookup
  - id: D:GOVERNANCE-score-5
    type: domain_score
    value: 5
    producer: governance_agent
  - id: W:finance/compound-interest
    type: wiki
    file: wiki/finance/compound-interest.md
    producer: wiki_index
  - id: P:avoids-family-topic-on-weekends
    type: pattern
    ref: _meta/user-patterns.md#avoids-family-topic-on-weekends
    producer: retrospective
```

### 注册表构造（Registry construction）

注册表由 ROUTER 在 Step 7.5 之前装配：

1. Hippocampus、SOUL check、concept lookup 信号 → 在 Step 0.5 加入。
2. 领域 score 信号 → 随着每个领域在 Step 5 报告而加入。
3. COUNCIL 辩论信号 → 若 COUNCIL 在 Step 6 触发则加入。
4. Wiki / pattern 引用 → 若 DISPATCHER 将它们作为 "known premises" 输入则加入。

注册表在会话期间只追加（append-only）。信号在会话中从不被删除。

---

## 10. 重新生成协议（Regeneration Protocol）

若验证器返回 `groundedness_score < 0.9`：

1. 验证器发出 `regeneration_feedback`：
   - 缺少有效引用的具体声明。
   - 为每条无支撑声明建议引用的 `signal_id`（从注册表中选取）。
   - 任何格式错误。
2. narrator（ROUTER）接收反馈并重新生成输出，纳入建议的引用，或者，若不存在支撑信号，则**删除该声明**。
3. 最多 **3 次重新生成尝试**。
4. 耗尽时：
   - 回退到**未引用的 Summary Report**（Step 7 的原始输出，而非重写版本）。
   - 发出 AUDITOR 标记：`narrator_failed_after_3_attempts`。
   - 将失败记录到 `_meta/eval-history/` 以供日后审查。

用户仍会收到一份报告。报告只是不那么"被叙述"（less narrated）。

---

## 11. 性能预算（Performance Budget）

| 阶段 | 预算 |
|--------------------------------|---------------|
| Narrator 生成（首次） | 2–5 秒        |
| 验证器扫描（单次） | 1–3 秒        |
| 重新生成 + 重新验证循环（每次尝试） | 3–8 秒       |
| **最坏情况总计（3 次重试）** | **18 秒（典型） / 21 秒（上限）** |

算术：一次初始生成 + 验证（2–5 s + 1–3 s = 3–8 s），加上最多三次重新生成 + 重新验证循环，每次 3–8 s。典型总计 ≈ 18 s（3 次循环取中位 6 s，初始无需额外重试裕量）。上限总计 = 21 s（最差情况 8 s 初始 + 三次 4.33 s 重试，或受重新生成天花板约束的等价分布）。

Narrator 生成是 ROUTER 正常组装的一部分，不是单独的网络往返。验证器延迟保持在 `references/cortex-spec.md` 中的 Cortex 延迟预算内。narrator 回退到未引用的输出（与 §10 耗尽相同的回退），只要**任一**触发条件命中：

- 累计 wall-clock 超过 **21 秒**，或
- 任何单次 "重新生成 + 重新验证" 循环超过 **8 秒**。

---

## 12. 质量指标（Quality Metrics）

narrator 向 AUDITOR 推送两个指标到 eval-history：

- `citation_groundedness`（0–10）—— 由 `groundedness_score × 10` 换算。
- `regeneration_count` —— narrator 通过前的尝试次数（0、1、2 或 3）。

**目标** —— v1.7 稳定后 `citation_groundedness ≥ 9`；Full Deliberation 会话中 > 80% 满足 `regeneration_count = 0`。

**AUDITOR 回归（regressions）** —— 任何 `citation_groundedness < 7` 的会话 → 质量事件；`regeneration_count > 1` 的周度趋势 → narrator 漂移。

参见 `references/eval-history-spec.md` 了解日志和审查。

---

## 13. 边界情况（Edge Cases）

### ROUTER 直接处理（无子 agent 派生）

若 ROUTER 直接处理用户消息 —— 闲聊、翻译、笔记、简单查询 —— 则没有子 agent 被派生，信号注册表实际为空。

行为：narrator 是**trivial pass-through（直通）**。不改写、不验证、不做 Step 7.5。ROUTER 发出其直接响应。

### Express 分析（跳过 PLANNER / REVIEWER）

Express 路径（Step 1E）生成**简报**（brief report），而非 Summary Report。它有 hippocampus 信号（来自 Step 0.5）和可能的 SOUL check 信号，但没有来自完整 deliberation 的领域 score 信号。

行为：narrator **仅验证 hippocampus / SOUL / concept 引用**，因为对 express 会话而言，注册表中只有这些信号类型。不预期领域 score 引用。

### STRATEGIST 会话（纯哲学，无决策）

STRATEGIST 会话是与历史思想家的开放式对话。没有 Summary Report，也没有领域评分。

行为：**不调用** narrator。STRATEGIST 子 agent 产出自己的输出；ROUTER 不经改写或引用地转达。

### 尽管 Full Deliberation 但注册表仍空

若 Full Deliberation 运行了但注册表意外为空（信号生产者失败），narrator 表现如 §10 耗尽：回退到未引用的 Summary Report 并标记 AUDITOR。

---

## 14. 反模式（Anti-patterns）

- **不要为"显而易见"的声明跳过引用**。即使是 "your project X" 也需要 `P:` 或 `S:` 引用。"显而易见"正是编造藏身之处。
- **不要引用模糊类别**。`[S:recent-sessions]` 不合法。使用能解析到单一文件或字段的特定 signal_id。
- **不要事后生成信号**。信号必须由其所属的子 agent 在正常工作流中产出。narrator 不能为支撑声明而伪造信号。
- **不要绕过验证器**。没有 "相信我" 模式。没有用户标志可以禁用验证。
- **不要声明无支撑的模式**。"你总是做 Y" 需要 ≥ 3 个引用；"你有时做 Y" 至少需要一个；"你可能做 Y" 是推测，不允许。
- **不要混用或发明引用前缀**。只有 `S:`、`D:`、`SOUL:`、`C:`、`W:`、`P:` 合法。绝不跨前缀重新标注信号。
- **不要引用 Summary Report 本身**。narrator 是 Summary Report 的改写；把它作为信号引用是循环的。

---

## 15. 用户决策审计轨迹（User Decision Audit Trail）

基于证据的系统必须可检视。用户可以问：*"显示声明 X 背后的信号。"* 系统回复所引用的 `signal_id`、源文件路径（或字段 / 维度引用），以及支撑该声明的内容片段。

示例：

```
User: What's the signal behind "Your past passpay-v06-refinement session
shows a similar 5-round iteration pattern"?

System:
- Signal: S:claude-20260419-1238
- Source: _meta/sessions/claude-20260419-1238.md
- Snippet: "Session ran 5 revision rounds on payment gateway spec. Each
  round tightened governance controls. Final GOVERNANCE score 5/10 due
  to incomplete fraud-response plan."
```

这就是 Life OS 与 Gazzaniga 式编造之间的分水岭。任何 narrator 输出都可追溯到产出它的信号。

若用户请求 connective 句子背后的信号，系统回复：*"那是连接性组织（connective tissue），不是基于证据的声明。没有可引用的东西。"*

---

## 16. 相关规范（Related Specs）

- `references/cortex-spec.md` —— 完整 Cortex 架构
- `references/hippocampus-spec.md` —— 会话检索与 `S:` 信号生产
- `references/gwt-spec.md` —— 信号仲裁与广播
- `references/eval-history-spec.md` —— `citation_groundedness` 如何被记录
- `references/concept-spec.md` —— 通过 `C:` 前缀引用的概念 ID
- `references/wiki-spec.md` —— 通过 `W:` 前缀引用的 wiki 条目
- `references/soul-spec.md` —— 通过 `SOUL:` 前缀引用的 SOUL 维度
- `references/session-index-spec.md` —— 通过 `S:` 前缀引用的会话
- `pro/agents/router.md` —— narrator 组装位于 ROUTER 内部（本规范 §6）

---

## 17. Trace UX · 面向用户的审计轨迹（Trace UX · User-Facing Audit Trail）

基于证据的生成只有在用户能够检视时才有用。本节定义 trace 请求如何被处理 —— narrator 层欠用户的 UX 合约。

### 17.1 触发形式（Trigger forms）

三种自然语言触发模式：

1. **完整 trace 请求** —— 用户说 "why did you say X?" / "trace this" / "这句话怎么来的" / "根拠は?"
2. **特定引用检视** —— 用户从 Summary Report 引用特定 `[signal_id]`："show me `S:claude-20260419-1238`" / "S:claude-20260419-1238 是什么"
3. **类别概览** —— 用户询问哪类声明被什么驱动："which SOUL dimensions influenced this?" / "list all past sessions that contributed"

ROUTER 通过意图分类检测这些（ROUTER 已经在对用户输入做模式匹配；trace 触发增加一个模式族）。

### 17.2 Trace 输出格式（Trace output format）

对单个声明的完整 trace 请求：

```
📎 Trace for: "Your past passpay-v06-refinement session shows a similar 5-round iteration pattern"

Cited signals:
1. S:claude-20260419-1238
   Source: _meta/sessions/claude-20260419-1238.md
   Content match: "Session ran 5 revision rounds on payment gateway spec.
     Each round tightened governance controls. Final GOVERNANCE score
     5/10 due to incomplete fraud-response plan."
   Produced by: hippocampus (Step 0.5 Wave 1)

2. D:passpay-governance-score
   Source: session D-scores extracted by ROUTER at Step 7
   Value: 5 (threshold for flag: < 6)
   Produced by: governance_agent

Confidence: groundedness_score = 1.0 (both citations resolve, content supports claim)
```

对特定引用检视，展示相同的块但仅针对所请求的 signal_id。

对类别概览：

```
📎 Category trace: SOUL dimensions that influenced this Summary Report

1. SOUL:risk-tolerance-v3 (core, confidence 0.82)
   Referenced by: narrator (×2), governance_agent (×1)
   Source text: SOUL.md § Risk attitude

2. SOUL:evidence-discipline (secondary, confidence 0.61)
   Referenced by: narrator (×1), execution_agent (×1)
   Source text: SOUL.md § Evidence discipline

3. [...]
```

### 17.3 Trace 数据源（Trace data sources）

Trace 由以下来源组装：

- 当前会话上下文中保存的**信号来源注册表**（§9）
- 针对所引用路径的文件读取（验证器子 agent 或 ROUTER 使用 `Read` 工具）
- Trace 主体中不做 LLM 生成 —— trace 是字面摘录 + 元数据；这防止递归编造（"trace 解释 trace 解释 trace……"）

若某个被引用的信号在 trace 时不能被解析（文件已删除、frontmatter 改变），trace 行显示 `⚠️ signal no longer resolvable` 同时保留原始引用。

### 17.4 Connective-tissue 响应（Connective-tissue response）

若用户请求对验证器分类为 **connective** 的句子（§3）做 trace：

```
That sentence is connective tissue (a transition / framing / rephrasing),
not a grounded claim. No signal stands behind it. If you want to trace a
substantive claim in the same report, let me know which one.
```

这防止"系统试图为本就不承载真值的句子虚构支撑信号"的编造循环。

### 17.5 Trace 在 4 语言主题系统中的表现（Trace in the 4-language theme system）

Trace 输出以活动主题的语言（en / zh / ja）渲染。Signal ID 前缀（`S:` `D:` `SOUL:` `C:` `W:` `P:`）保持字面 —— 它们是技术标识符，不是本地化文本。只有解释性段落被翻译。

### 17.6 Trace 不记录日志（Trace is not logged）

Trace 请求是瞬态的。它们**不**写入 journal，**不**计入 AUDITOR 指标，**不**变更任何东西。用户可以对同一 trace 请求 10 次而无副作用。

理由：trace 是检视工具，不是产生决策的动作。把每个 trace 请求都记日志会膨胀 journal，并遮蔽真实的决策历史。

### 17.7 性能预算（Performance budget）

Trace 请求必须在 < 2 秒内返回（比 narrator 预算更严格，因为 trace 是单会话、只读、且主体无 LLM 生成）。若 trace 请求超过 2 秒，就出错了 —— 很可能是某个被引用信号指向一个巨大文件。实现应把文件读取截断为匹配点周围 500 行窗口。

---

**Spec 状态**：v1.7 草稿。narrator 验证器子 agent 上线且 `citation_groundedness` 数据的第一周被审查后定稿。Trace UX（§17）需要用真实会话数据做集成测试；格式可能在 v1.7 alpha 期间基于用户反馈调整。

---

> ℹ️ **2026-04-22 更新**：同步 EN R3.1 修复 §11 预算算术

> 译注：本文译自英文版 2026-04-22 snapshot；英文为权威源，歧义以英文为准。
