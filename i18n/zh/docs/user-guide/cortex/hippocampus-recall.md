---
translated_from: docs/user-guide/cortex/hippocampus-recall.md
translator_note: auto-translated 2026-04-22
---

# Hippocampus · 跨 Session 记忆检索(Cross-Session Memory Recall)

> 面包屑: [← Cortex 总览](./overview.md) · [← 产品入口:用户指南首页](../index.md)

> 每次你打开新 session 说话,Hippocampus 都会在后台自动翻你过去的 session,找出几条和"你现在在问的"相关的——不管用了什么不同的字眼、不管过了多久。ROUTER 拿到你消息的时候,已经附带这些"相关记忆"作为参考。你上朝的体感会变:系统**记得**了。

## 一句话概述(One-line summary)

Hippocampus 是 Cortex 认知层的**跨 session 检索器**。每次你发消息,它在 ROUTER 分诊之前的那 5–7 秒里:扫 session 索引 → 找直接匹配 → 沿概念图谱扩散 → 交出 top 5–7 相关历史 session。ROUTER 看到的不再是你的原话,而是**原话 + 一段 `[COGNITIVE CONTEXT]` 注释**。

名字来自生物学——大脑里负责绑定新经验到"情景记忆"和按需检索的脑区就叫 hippocampus(海马体)。Cortex 这个 subagent 做的事非常相似:**把"你刚说的话"和"系统已经知道的过去"桥接起来**。

---

## 为什么要加这个(Why add it)

### v1.6.2a 的痛点

你开了一个新 session 问:"我上次提到的那个信托结构方案,你觉得在日本合规吗?"

系统:"我没有本次会话的上下文,请提供更多细节。"

你(翻白眼):**我上次已经花了两小时和它讨论过这事**——具体是哪个信托、为什么选它、当时遇到什么顾虑。但新 session 的 ROUTER 从零起步,它只看得见你**这一句话**。

你只有两个选择:
1. 手动去 `decisions/` 里翻出上次的决策文件,贴进对话(繁琐)
2. 从头解释一遍(浪费,而且描述可能不如系统自己看自己的笔记准确)

### Hippocampus 的承诺

**你不需要贴,不需要解释,不需要提醒"我们上次聊过"**。Hippocampus 自动查你的 `_meta/sessions/INDEX.md`——一份编译好的、每个历史 session 一行摘要的索引——找到最相关的 3–5 条、读出详细 summary、再沿概念图谱扩散到另外 1–2 条"表面看不出关联但图谱上相邻"的 session。

**结果**: ROUTER 一上来就知道你在说的"那个信托结构方案"具体指什么,之前你是怎么推理的,GOVERNANCE 领域给了几分——所以 PLANNER 不会重走一遍,六领域不会重新分析同样的维度,REVIEWER 不会问你"这是不可逆决策吗"(它知道,上次就讨论过)。

---

## 用户端看到什么(What the user sees)

### 你能直接看到的:消息前面多了一块 `[COGNITIVE CONTEXT]`

Step 0.5 结束后,ROUTER 收到的**实际输入**长这样(你通常看不到这一层,但你可以要求系统显示):

```markdown
[COGNITIVE CONTEXT — reference only, not user input]

📎 Related past decisions:
- 2026-03-15 | 信托架构 v2 评估 (score 7.8, wave 1) — 讨论过日本 NPO 结构的贷金业法豁免问题,GOVERNANCE 8/10
- 2026-02-28 | 跨境资产隔离 (score 6.5, wave 1) — 同域决策,finance 对信托税务影响有顾虑
- 2026-03-22 | 合伙结构对比 (score 5.1, wave 2) — 概念图谱邻居,via "fiduciary-structure"

🧬 Activated concepts:
- trust-structure-japan (canonical, activation 15)
- npo-lending-exemption (confirmed, activation 7)

[END COGNITIVE CONTEXT]

User's actual message: 我上次提到的那个信托结构方案,你觉得在日本合规吗?
```

**`wave 1`** = 关键词或概念直接匹配
**`wave 2`** = 强连接邻居(synapse 边权 ≥ 3)
**`wave 3`** = 弱连接邻居(边权 < 3,多数情况不进入最终 top 5–7)

### 你间接感受到的:系统"记得"了

ROUTER 奏折里会自然地引用历史:

> 基于你 2026-03-15 的"信托架构 v2 评估"[S:claude-20260315-1432],GOVERNANCE 当时给了 8/10,主要担忧集中在 NPO 豁免条款。本次继续这个话题,建议聚焦……

注意那个 `[S:claude-...-1432]` 的方括号标注——那就是 **narrator 的 citation**。ROUTER 说"你过去怎么怎么"的时候,**它必须指向真实存在的 session 文件**,否则 narrator-validator 会打回重写。

### 你主动要求看到的:trace 机制

你随时可以问:

> 这句"上次 GOVERNANCE 当时给了 8/10"是基于什么?

系统会回:

```
📎 Trace for: "上次 GOVERNANCE 当时给了 8/10"

Cited signal: S:claude-20260315-1432
Source: _meta/sessions/claude-20260315-1432.md
Content match: "GOVERNANCE 8/10 — 日本 NPO 不享受贷金业法豁免但
  对本次信托结构 B 无影响,因为信托本身不放贷。"
Produced by: hippocampus (Step 0.5 Wave 1)
```

**这是 Hippocampus 的核心价值:不是"AI 编出来的听起来有理的历史",而是"AI 指回你本人笔记里的原文"**。

---

## 3 波扩散激活(3-wave spreading activation)

Hippocampus 的检索模型不是"搜索引擎匹配 + 排序"——而是模仿大脑 **spreading activation** 的 3 波扩散:

### Wave 1 · 直接匹配

1. 读 `_meta/sessions/INDEX.md`(一份编译好的一行摘要索引,~1MB at 2000 sessions,秒级扫描)
2. 如果 ROUTER 已经做了 subject 提取,先用 **ripgrep** 快过滤,把 1000+ 条压到 <50 条候选
3. 把候选交给 Opus LLM 做**语义判断**(无 embedding、无 vector DB——用户决策 #3):"以下哪些 session 的 subject 和当前语义相关?"
4. 读 top 3–5 的完整 summary 文件
5. 输出 Wave 1 种子集

### Wave 2 · 强连接邻居

从 Wave 1 的 session 拿到它们的 `concepts_activated` 列表,对每个 concept:
- 读 `_meta/concepts/{domain}/{concept_id}.md`
- 沿 `outgoing_edges` 走——**但只走权重 ≥ 3 的强边**
- 找到每条邻居 concept 的 `provenance.source_sessions`——这些是"通过概念图谱间接相关"的 session
- 去重(和 Wave 1 不重合)、排名、**最多加 2–3 条**

Wave 2 捕捉的场景:你上次讨论"信托架构"的 session,和这次要讨论"合伙结构"的 session,**表面关键词不重合**,但图谱上"fiduciary-structure"这个概念是它们共同的邻居。Wave 1 会漏掉,Wave 2 捞回来。

### Wave 3 · 弱连接邻居(sub-threshold pre-activation)

继续扩散,但这次**接受权重 ≥ 1 的任何边**。Wave 3 不直接进入 top 5–7——它做的是**子阈值预激活**:让这些概念在本次 session 剩余时间里更容易被后续 frame 重新激活。

类比:你今天聊了"company-A holding",Wave 3 会把"company-A subsidiary"预先激活——下一个 frame 如果你不重复提"company-A"但问到它子公司,系统也能响应。这就是脑子里的"priming effect"。

### 最终上限

整套检索**硬上限是 5–7 条 session**。多了不是更好:
- Token 预算会爆
- GWT 仲裁器无法在 4 个维度下对 >7 条信号精细打分
- ROUTER 拿到太多 context 反而不如少而精

---

## 性能与成本(Performance and cost)

| 阶段 | 目标 | 说明 |
|------|------|------|
| 读 INDEX.md | <100ms | 即便 2000 session 索引,~1MB |
| Grep 预过滤 | <50ms | ripgrep on INDEX.md |
| LLM 语义判断(Wave 1) | 2–3s | ~5000 tokens on Opus |
| 读 3–5 个 session 文件 | <300ms | 并行读 |
| Wave 2 概念查找 | 1–2s | Opus 判边相关性 |
| Wave 3 扩散 | 1s | 范围更窄 |
| **总目标** | **< 7 秒** | 硬上限 15 秒 |

**成本**: 一次 hippocampus 调用大概 **$0.05–0.10**(Opus 定价)。整个 Cortex 层一个月加起来目标 $0.20–0.50——和你主 session 的成本相比可忽略。

---

## 用户动作 · 你可以怎么干预(User actions · how to intervene)

### 1. 看 Cognitive Context 是什么

直接要求:

> 给我看这次 ROUTER 拿到的 cognitive context

系统会把 `[COGNITIVE CONTEXT]` 块完整贴出来。

### 2. 要求忽略历史、重新思考

当你怀疑历史检索带偏了 ROUTER 的判断,或你主动想"从零重看"一件事:

> 忽略 cognitive context,重新分析这个问题

ROUTER 会在本次决策里**主动忽略** `[COGNITIVE CONTEXT]` 块——cognitive annotation 是 **advisory**,不是 **authoritative**。

### 3. trace 任何引用

看到奏折里 `[S:claude-...-1432]` 这样的标注,随时可以:

> trace [S:claude-20260315-1432]

系统返回原始 session 文件的摘要段落。

### 4. 主动 reindex(如果索引过时)

理论上 archiver Phase 2 会在每次 adjourn 自动重建 INDEX.md。但如果你手工改动了大量 session 文件,或从别的设备同步下来的索引不一致:

```bash
uv run tools/reindex.py
```

### 5. 调整阈值(谨慎)

`_meta/cortex/config.md` 里:

字段的权威定义见 `references/cortex-spec.md` §`_meta/cortex/config.md`；下面只列与 hippocampus recall 最相关的几个开关。

```yaml
top_k_signals: 5               # 最多播报几条信号到 ROUTER
per_signal_floor: 0.3          # salience 低于此值的信号丢弃
hippocampus_timeout: [5, 15]   # 软超时/硬超时(秒)
```

改动提交 git 以跟踪跨设备漂移。下一次 Start Session 生效。

---

## 常见疑问(FAQ)

### Hippocampus 会把我的隐私数据检索出来吗?

**它只读 `_meta/sessions/*.md` 的 YAML summary**——这些摘要在 archiver Phase 2 写入时已经过隐私过滤。具体的私人细节(人名、金额、账号)**不会出现在 summary 里**,所以也不会进入 cognitive context。

另外 hippocampus 的输出合同里每个 `summary` 字段**最多 1–2 句话**——杜绝把整段 session 原文贴给 ROUTER 的可能。

### 如果 INDEX.md 不存在会怎样?

退化流程(按顺序):

1. Hippocampus 尝试跑 `tools/reindex.py`——如果能跑通,重建索引
2. 跑不通 → 返回空输出,标记 `degraded: true, degradation_reason: "INDEX_MISSING"`
3. GWT 仲裁器拿不到 hippocampus 信号,走空 marker 流程(详见 [gwt-arbitration.md](./gwt-arbitration.md))
4. ROUTER 看到的是**原始消息**,行为退化到 v1.6.2a

**你的 session 不会被 block**——所有 Cortex 组件的原则是"降级而不是崩溃"。

### 检索到的 session 里有的内容已经过时,系统会误导我吗?

两道兜底:

1. **Recency decay 已经参与评分**——Wave 2/3 的打分公式里有 `0.2 * recency_decay` 权重,`recency_decay = exp(-days_since_session / 90)`。90 天前的 session 自动贬权。
2. **Migration 默认只扫最近 3 个月**——更老的 journal 不碰。老项目、已降级的价值观、被重写的决策**天然不进入**概念图谱和 session 索引。

如果你**明确**想让 Cortex 拉进更老的历史:

```bash
uv run tools/migrate.py --since 2024-01-01
```

但一般不推荐——老 context 对当下决策的贡献值通常不如新 session。

### Hippocampus 能不能"主动学习"?为什么不用向量数据库?

用户决策 #3 明确禁止:**markdown-first, LLM-judgment-only**。

原因:
- **可检查性**——每条 session summary、每个 concept 节点都是 `.md` + YAML,你随时打开看。向量数据库是黑盒。
- **可移植性**——你 git clone 你的 second-brain 到新机器,Hippocampus 立即能跑。向量数据库要重建索引。
- **无外部依赖**——没有 Chroma / Pinecone / pgvector 之类的 runtime。
- **LLM 语义判断够用**——2000 session 规模下,Opus 5000 token 扫一次 INDEX.md 完全够,还更准(因为 Opus 真的懂"subject 相关",而 embedding 只懂"向量相似")。

规模触发器在 `session-index-spec.md` 有定义:INDEX.md 超 5MB 或 p95 延迟 >10s 时,**先分片到按月分割**,再谈缓存。向量数据库这条路径明确不考虑。

### 如果同样的 session 被反复检索出来,它会"疲劳"吗?

是的——GWT 仲裁器的 **novelty** 维度专门处理这个(详见 [gwt-arbitration.md](./gwt-arbitration.md)):

| Novelty 值 | 条件 |
|-----------|------|
| 1.0 | 从未出现过的信号 |
| 0.6 | 之前出现 1–2 次 |
| 0.2 | 出现 3+ 次(**fatigue — 你已经看过了**) |
| 0.0 | 已经处理完并解决 |

所以一条历史 session 被反复激活时,它的 salience 会自然衰减,不会刷屏。

### Hippocampus 失败但 GWT 成功,ROUTER 会看到什么?

GWT 仲裁器能容忍**单源失败**——第一次 session、hippocampus 超时、INDEX 文件损坏,都可以。它会用 concept lookup 和 SOUL check 的信号组合出 cognitive annotation。ROUTER 看到的 `[COGNITIVE CONTEXT]` 里可能就**没有 `📎 Related past decisions` 段落**,但会有 `🧬 Active concepts` 和 `🔮 SOUL dimensions`。

---

## Troubleshooting(故障排查)

### "ROUTER 没引用任何历史,但我确信上周做过类似决策"

可能原因(按可能性排序):

1. **你上周那次没走全朝议**——Express 快车道和 direct-handle 都不写 `_meta/sessions/{session_id}.md`,所以 INDEX.md 里没这条。解决: 让系统给那次对话补一个 retrospective,或手工在 `_meta/journal/` 里找到对应记录。
2. **subject 不匹配**——Wave 1 的 LLM 判断可能觉得本次 subject 和上周那次**不够语义相关**(比如上周你问的是"合伙人分工",本周问的是"授权边界")。解决: 直接贴出来——"参考 2026-03-15 合伙人分工的讨论"。
3. **migration 没跑过**——新装 v1.7 后没跑 `uv run tools/migrate.py`,INDEX.md 是空的。解决: 先跑 migration。
4. **时间窗外**——默认 3 个月。上次决策 100 天前,不进入默认扫描范围。解决: `uv run tools/migrate.py --since YYYY-MM-DD` 扩宽范围。

### "检索结果满屏无关历史"

可能原因:

- **Wave 1 LLM judgement 失准**——连续 2 周 median top-1 relevance 跌到 0.5 以下 = Wave 1 prompt 需要重新调优。这是 AUDITOR 的 `cognitive_annotation_quality` 指标会捕捉的模式(详见 [auditor-eval-history.md](./auditor-eval-history.md))。
- **概念图谱存在"hub" 节点**(一个 concept 连了几十条强边)导致 Wave 2 扩散失控。检查 `_meta/concepts/SYNAPSES-INDEX.md`,找 edge count 特别高的节点,考虑拆分。
- **短期内话题重复**——如果你一周问了 5 次类似问题,hippocampus 会反复返回同一批 session。GWT novelty 维度会降权,但如果 fatigue 还没触发,可能看起来很吵。等几次上朝就会平滑。

### "Trace 显示 '⚠️ signal no longer resolvable'"

某个 `signal_id` 指向的文件被删除或改名了。常见原因:

- 你手工在 `_meta/sessions/` 里删了某个历史 session 文件
- Git 分支切换后索引不一致
- 概念被 retire 到 `_meta/concepts/_archive/`

解决: 在 trace 出现这条警告时,原始 citation 仍然保留——你知道它**指向哪**,只是那个文件暂时/永久没了。如果是意外删除,从 git 历史恢复;如果是归档,内容仍在 `_archive/` 里可以手动看。

---

## 深入阅读(Further reading)

产品入口:

- [What is Life OS](../../getting-started/what-is-life-os.md) — Life OS 整体定位
- [Quickstart](../../getting-started/quickstart.md) — 首次上朝流程

同目录用户文档:

- [overview.md](./overview.md) — Cortex 总览,理解 hippocampus 在四机制中的位置
- [concept-graph-and-methods.md](./concept-graph-and-methods.md) — Wave 2/3 依赖的概念图谱
- [gwt-arbitration.md](./gwt-arbitration.md) — hippocampus 信号如何和 SOUL / concept 信号竞争
- [narrator-citations.md](./narrator-citations.md) — `[S:xxx]` 引用格式的完整语义
- [auditor-eval-history.md](./auditor-eval-history.md) — `cognitive_annotation_quality` 怎么评分

Spec 层(最权威,英文):

- `references/hippocampus-spec.md` — Agent 合同、输入输出 schema、性能预算、failure modes
- `references/session-index-spec.md` — `INDEX.md` 一行摘要格式、分片触发器
- `references/concept-spec.md` — Wave 2/3 走的 `outgoing_edges` 权重语义
- `references/gwt-spec.md` — hippocampus 输出如何被下游 arbitrator 消费
- `references/cortex-spec.md` §Hippocampus — 在整体架构里的位置

Agent 定义(深度用户看):

- `pro/agents/hippocampus.md` — 实际的 subagent 定义、tool 约束、model 选择

---

**上一篇**: [overview.md — Cortex 总览](./overview.md)
**下一篇**: [concept-graph-and-methods.md — 概念图谱与方法库](./concept-graph-and-methods.md)

---

> **译注**:本文从 `docs/user-guide/cortex/hippocampus-recall.md` 同步,2026-04-22 由 auto-translation 流程完成。源文本已为中文,此处保留原文并补齐 i18n frontmatter。技术词(Hippocampus / Cortex / GWT / Narrator / ROUTER / Wave 1/2/3 / Step 0.5 / signal_id / session_id / Opus / ripgrep / embedding / vector DB 等)保留英文。若与 EN 原文出现漂移,以源文件为准。
