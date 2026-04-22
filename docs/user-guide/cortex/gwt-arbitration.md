# GWT 仲裁 · 多源信号的显著性竞争

> 面包屑: [← Cortex 总览](./overview.md) · [← 产品入口:用户指南首页](../index.md)

> 每次你发消息,Cortex 会并行跑三条信号源:hippocampus(历史 session)、concept lookup(概念图谱)、SOUL check(人格维度检查)。这三条源可能产生**十几条甚至几十条**的候选信号。都塞给 ROUTER 会变成信息洪水。GWT Arbitrator 的工作就是在这堆信号里做**显著性竞争**——按 4 个维度打分,挑 top-5 播报给 ROUTER,其中 SOUL 核心冲突优先升格为警告头部。这一层受 Stanislas Dehaene 的 **Global Neuronal Workspace** 理论启发,中文常译作"全局神经元工作空间"。

## 一句话概述

GWT Arbitrator 是 Cortex 的**信号选择器**——它在 Step 0.5 的最末端接收 hippocampus / concept / SOUL 三个并行 subagent 的输出,用固定公式 `salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2` 打分,排序,截 top-5,处理 SOUL 冲突升格,然后把最终 `[COGNITIVE CONTEXT]` 块交给 ROUTER。

名字的来源: Dehaene 的 GWT 理论说大脑里有很多并行的特化模块同时工作,它们的输出**竞争**进入"中央工作空间",只有最强的信号得以"点火"(ignition)并广播给其他所有模块。意识,在这个框架下,就是竞争胜出的那一刻。

Cortex 借用这个模型: hippocampus、concept、SOUL 是三个"特化模块",GWT Arbitrator 是"竞争仲裁器",ROUTER 是"中央工作空间"——最终进入 ROUTER 的 `[COGNITIVE CONTEXT]` 的,就是本次 session 里**点火**的信号。

---

## 为什么要加这一层

### 问题: 没有仲裁会怎样

假设没有 GWT,直接把三个 subagent 的输出拼起来给 ROUTER:

- hippocampus 返回了 7 条相关 session(每条都有价值但重要性不等)
- concept lookup 激活了 9 个概念(有的是 canonical 核心,有的是 tentative 噪音)
- SOUL check 返回 4 条维度状态(2 条 tier_1 冲突,2 条 tier_2 相关)

ROUTER 看到的 `[COGNITIVE CONTEXT]` 塞了 20 条:

```
[COGNITIVE CONTEXT]
Related past decisions: [7 条]
Active concepts: [9 个]
SOUL dimensions: [4 条]
[END]
```

**问题**:
- **信息过载**——ROUTER 的 triage 是秒级决策,20 条里挑主要矛盾的能力会降
- **噪音淹没信号**——一条 tier_1_conflict 被埋在 15 条无关的 concept 里,REVIEWER 可能根本没看到
- **cache 污染**——prompt cache 被大量低值信息撑大,后续 turn 的 cache hit 率下降
- **token 预算爆炸**——每次 turn 都塞 20 条,六领域每个再拿到一遍,成本乘 6

### 脑科学的答案

大脑处理这个问题的方式: **特化模块并行产生信号,通过显著性竞争选一个或几个广播出去**。视皮质每毫秒都在产生信号,但"你意识到"的只是其中极少数——因为只有最显著的信号赢得 ignition。

这不是"过滤机制",是**竞争机制**——低显著性信号**根本没输**给工作空间,你的意识从来不知道它们存在。Cortex 抄这个模型: GWT Arbitrator 按 salience 排序,**只传 top-5**,其他的记在 frame md 里供 trace,但不进 `[COGNITIVE CONTEXT]`。

---

## 用户端看到什么

### 场景 A: 普通情况下的 `[COGNITIVE CONTEXT]`

你问: "这一季度要不要把新产品线交给合伙人 A?"

GWT Arbitrator 收到三源信号(示例):

| 来源 | 信号 | urgency | novelty | relevance | importance | **salience** |
|------|------|---------|---------|-----------|------------|-----------|
| hippocampus | S:claude-20260115-1020 (过去类似决策) | 0.3 | 0.6 | 0.8 | 0.5 | **0.55** |
| hippocampus | S:claude-20260320-1400 (合伙关系) | 0.3 | 0.6 | 0.7 | 0.5 | **0.50** |
| concept | C:relationship:partner-a-control | 0.0 | 0.2 | 0.9 | 0.5 | **0.41** |
| concept | C:method:partner-evaluation | 0.0 | 0.2 | 0.6 | 0.3 | **0.26** ← 被截 |
| SOUL | 家庭优先于事业 (tier_1_conflict) | 0.6 | 1.0 | 0.9 | 1.0 | **0.85** |
| SOUL | 单干风险 (tier_2_relevant) | 0.3 | 0.6 | 0.7 | 0.7 | **0.55** |

排序 + 截 top 5: `[SOUL 家庭优先, SOUL 单干风险, S:过去类似决策, S:合伙关系, C:partner-a-control]`

**SOUL tier_1_conflict 升格到警告头部**。ROUTER 看到的 `[COGNITIVE CONTEXT]`:

```
[COGNITIVE CONTEXT — reference only, not user input]

⚠️ SOUL CONFLICT: 这个决策挑战你的"家庭优先于事业"(confidence 0.82)

📎 Related past decisions:
- 2026-01-15 | 合伙人授权 (score 8.2) — 结论"再观察 3 个月"
- 2026-03-20 | 合伙关系重构 (score 6.5) — finance 担忧

🧬 Active concepts:
- partner-a-control (canonical, weight 42, last activated 4d ago)

🔮 SOUL dimensions:
- 家庭优先于事业 (core, ↘ stable): tier_1_conflict
- 单干风险 (secondary, ↗ up): tier_2_relevant

[END COGNITIVE CONTEXT]

User's actual message: 这一季度要不要把新产品线交给合伙人 A?
```

**`C:method:partner-evaluation` 在 salience 0.26 被 per-signal floor (0.3) 截掉**。它不会进入 ROUTER 视野,但**会记在本次 session 的 frame md 里**,将来你 trace 时可以看到"这条信号在本次 session 里存在过,但未点火"。

### 场景 B: 第一次上朝 · registry 为空

你第一次装完 Cortex,跑完 migration。第一次 session 开口。hippocampus 返回空,concept lookup 空,SOUL check 可能有 1 条("风险承受度 new"):

GWT 输出:

```
[COGNITIVE CONTEXT]
🔮 SOUL dimensions:
- 风险承受度 (emerging, confidence 0.3): tier_2_relevant
[END]
User's actual message: ...
```

或者更极端,整个 signal registry 空: GWT 不 compose 空模板,直接返回**空 marker** — ROUTER 看到的就是原始用户消息,回退到 v1.6.2a 行为。

### 场景 C: 只有 1 条低 salience 信号

GWT 给所有信号打完分,发现最高那条只有 salience 0.25(低于 floor 0.3)。

输出 `(no high-salience signals)` 单行标记,跳过所有分类块:

```
[COGNITIVE CONTEXT]
(no high-salience signals)
[END]
User's actual message: ...
```

ROUTER 知道"Cortex 跑了,但没产出显著信号"——和"Cortex 没跑"是不同状态。

### 场景 D: 部分超时

hippocampus 在软超时 5 秒时还没返回,但 concept 和 SOUL 都完成了。GWT 有两个选项:

- 等到 hard 超时 10 秒,如果 hippocampus 还没回,发 partial output(只用 concept + SOUL 信号)+ 追加单行 `(partial — timed out)`
- 如果 hippocampus 在 soft timeout 到 hard timeout 之间返回,仍然加进来

输出:

```
[COGNITIVE CONTEXT]
🧬 Active concepts:
- partner-a-control (canonical, weight 42)
🔮 SOUL dimensions:
- 家庭优先于事业 (core, ↘ stable): tier_1_conflict
(partial — timed out)
[END]
User's actual message: ...
```

---

## 显著性公式 · 四个维度

**salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2**

这个公式**在 v1.7 是固定的**。每个维度都是 `[0.0, 1.0]` 的浮点。

### urgency(紧迫度)

| 值 | 条件 |
|---|------|
| **1.0** | 7 天内的 deadline 相关 action item |
| **0.6** | SOUL 冲突警告(core 维度被挑战) |
| **0.3** | 重复模式(同样主题最近出现 3+ 次) |
| **0.0** | 无时间压力的背景 context |

紧迫度权重最高(0.3)——因为**有 deadline 的事一定要先看见**,哪怕它的 importance 不高。

### novelty(新颖度)

| 值 | 条件 |
|---|------|
| **1.0** | 信号从未出现过 |
| **0.6** | 出现过 1–2 次 |
| **0.2** | 出现过 3+ 次(**fatigue — 你已经看过了**) |
| **0.0** | 已经处理完并解决 |

novelty 是"反刷屏"——同一条信号被反复激活,它的 salience 会自然衰减。防止 ROUTER 每次都看到同一批历史。

### relevance(相关度)

**唯一由 LLM 判断的维度**——其他都是规则。

LLM 收到 `(signal content, current user message)` 的对,返回 `[0.0, 1.0]` 的一个浮点,代表"这条信号和当下决策的直接相关度有多高"。

LLM 失败时,**回退到关键词重叠率**作为 deterministic fallback。

relevance 权重 0.3,和 urgency 并列最高。

### importance(重要度)

SOUL 维度等级 + 战略项目标签的映射:

| 值 | 条件 |
|---|------|
| **1.0** | SOUL `core` 维度(confidence ≥ 0.7) |
| **0.7** | SOUL `secondary` 维度(0.3 ≤ confidence < 0.7) |
| **0.5** | 关联 critical-path 项目(concept metadata 里有 tag) |
| **0.3** | SOUL `emerging` 维度(0.2 ≤ confidence < 0.3) |
| **0.2** | 一般 context,无身份或项目绑定 |

多条件同时匹配时,**取最高值**。

---

## 信号类型

GWT 识别 9 种信号类型,按来源分组:

### From hippocampus

- `decision_analogy` — 过去和当前主题结构相似的决策
- `value_conflict` — 过去一次 session 里和 SOUL 冲突,在这里也相关
- `outcome_lesson` — 过去一次决策的结果有教训意义

### From concept lookup

- `canonical_concept` — 直接提到或隐含的 confirmed concept
- `emerging_concept` — 同领域的 tentative concept(尚未 canonical)

### From SOUL check

- `tier_1_alignment` — core 维度支持当前方向
- **`tier_1_conflict`** — core 维度冲突(**半 veto 信号,会升格**)
- `tier_2_relevant` — secondary 维度适用
- `dormant_reactivation` — 休眠维度刚好又相关了

**信号对 arbitrator 是 opaque 的**——它只看 `signal_type`、`source`、`payload`、4 个打分维度。**arbitrator 不会从 payload 里**推导新信号——每条信号必须有命名 source。

---

## 仲裁算法 · 6 步

1. **Ingest** — 接收三源信号(带 metadata)
2. **Score** — 按公式算 salience。relevance 走 LLM,其他走规则
3. **Rank** — 按 salience 降序排序
4. **Cap** — 取 **top 5**(硬上限,防止信息过载)
5. **Detect conflicts**:
   - 任何 `tier_1_conflict` → **升格**到 `⚠️ SOUL CONFLICT` 头部
   - 相反方向的 `decision_analogy`(过去做过互相矛盾的决策)→ flag "inconsistent precedent" 在 pattern observations 块
6. **Compose** — 按 §8 输出格式渲染

**arbitrator 不会"发明"信号**。输出里每一项都**追溯得到**对应的输入信号。

---

## 输出格式 · `[COGNITIVE CONTEXT]` 块

```markdown
[COGNITIVE CONTEXT — reference only, not user input]

⚠️ SOUL CONFLICT: [只在 core 维度被挑战时出现]
This decision challenges your "{dimension_name}" (confidence {X})

📎 Related past decisions:
- {session_id} ({date}): {reason}, score {X}/10

🧬 Active concepts:
- {concept_id} (canonical, weight {X}, last activated {when})

🔮 SOUL dimensions:
- {dimension} ({tier}, {trend}): {support/challenge status}

💡 Pattern observations:
- {salience ≥ 0.8 但未归入其他 category 的信号}

[END COGNITIVE CONTEXT]

User's actual message: {original}
```

**Suppression 规则**:

- **信号总数 0** → 空 marker,ROUTER 只看到 `User's actual message: ...`
- **全部信号 < 0.3** → 单行标记 `(no high-salience signals)`,跳过分类块
- **有 SOUL CONFLICT 但没相关历史** → 依旧 emit SOUL 块(冲突独立有分量)
- **每分类最多 5 条,总体 top 5**——两重上限叠加

---

## 注入位置 · 为什么在 user role 不在 system prompt

**cognitive context 被 prepend 到 user role 消息的开头,不是加到 system prompt**。

**理由**: Anthropic 的 prompt cache 只在 system prompt 稳定时命中。每次 turn 都动态的 cognitive annotation 如果加到 system prompt,**每 turn 都会 bust cache**。保留在 user role 里则 cache 命中不受影响。

**实现**:

1. Orchestrator 调用 arbitrator,接收输出
2. Orchestrator **prepend** 到 ROUTER 的 user-role message 开头
3. ROUTER 看到合成输入,把 `[COGNITIVE CONTEXT]` 块当**参考**,不是字面用户请求
4. ROUTER 的 system prompt 不变

**ROUTER 的 triage 规则不变**——它把 `[COGNITIVE CONTEXT]` 当**辅助信息**,决定派哪些 domain agent 时**可以参考也可以忽略**。

---

## 用户动作 · 你可以怎么干预仲裁结果

### 1. 要求忽略 `[COGNITIVE CONTEXT]`

> 忽略 cognitive context,重新从零分析

ROUTER 在本次决策里**主动忽略** `[COGNITIVE CONTEXT]` 块——cognitive annotation 是 advisory,不是 authoritative。

### 2. 要求展示原始 cognitive context

> 给我看这次的 cognitive context

系统完整贴出 `[COGNITIVE CONTEXT]` 块。

### 3. 用 trace 查每条引用

看到 `📎 Related past decisions: - 2026-01-15 ...`,说:

> trace S:claude-20260115-1020

得到原始 session summary + 相关度评分 + 为什么被选中。详见 [narrator-citations.md](./narrator-citations.md)。

### 4. 反驳 SOUL CONFLICT 升格

系统说"这个决策挑战你的家庭优先维度"——但你觉得本次决策的重点根本不在家庭方向:

> 这次的 SOUL CONFLICT 不适用——本次决策不涉及家庭时间分配

ROUTER 会:
- 在 Summary Report 的修正段记录你的反驳
- AUDITOR 在 eval-history 里记录 `suppression_precision` 失准(详见 [auditor-eval-history.md](./auditor-eval-history.md))
- 如果同类误判多次重复,AUDITOR 会 flag "SOUL check 维度匹配过宽泛",可能需要 retuning

### 5. 调整 salience 阈值

编辑 `_meta/cortex/config.md`:

```yaml
salience_weights:
  urgency: 0.3
  novelty: 0.2
  relevance: 0.3
  importance: 0.2
per_signal_floor: 0.3       # < 此值的信号被丢弃
top_k_signals: 5            # 硬上限播报几条
```

**注意权重总和应为 1.0**(当前 0.3+0.2+0.3+0.2=1.0)。改完提交 git,下次 Start Session 生效。

**不推荐在 v1.7 阶段**调整权重——这几个数是 Phase 1 placeholder,需要 3 个月真实数据才知道该怎么调。如果要调,保守调整(±0.05),观察 eval-history 里 `cognitive_annotation_quality` 的趋势。

---

## 常见疑问

### 为什么是 4 维?不是 5 维?

历史版本讨论过加第 5 维 emotion(情绪加权)——但 v1.7 决定**不加**。原因:

- 情绪评估需要一个额外的 subagent,引入新的 failure mode
- 当 SOUL 里有"情绪敏感度"之类的维度时,已经以 importance 的形式融入了
- Phase 2 可能引入 `emotion` 和 `prediction` 两种信号类型,但仍走 4 维公式(不改 formula,只扩展信号来源)

所以 **v1.7 公式固定为 4 维**。

### Top-5 会不会漏掉重要信号?

有可能,但这是**可接受 tradeoff**:

- v1.6.2a 根本没有信号,20 条信号一条都没进 ROUTER = 100% 漏
- v1.7 保证 top-5 进了,95% 的 salience ≥ 0.6 信号会在 top-5
- 剩下 5% 的边缘 case,AUDITOR 的 `cognitive_annotation_quality` 会捕捉模式(比如某类重要信号长期被截,会 flag retuning)

另外: **截掉的信号依然记在 session frame md 里**,trace 时可以查。只是不进入 ROUTER 看得到的 `[COGNITIVE CONTEXT]`。

### SOUL 维度只是 4 个打分维度之一,为什么 `tier_1_conflict` 要单独升格?

因为**和其他信号的对称性会导致误判**:

- `tier_1_conflict` 如果只是 importance 1.0 的普通信号,其他 4 条高 urgency / 高 novelty 的信号可能共同把它挤出 top-5
- 但 core 冲突是**决策级的警告**——不看到它就可能做出和核心价值观冲突的决定
- 对称排序会让这类"虽重要但不 urgency/novelty"的信号系统性被忽略

升格机制就是针对这一点的结构性修正: **只要 `tier_1_conflict` 存在,无论排第几,都单独 emit 成 `⚠️ SOUL CONFLICT` 头部 block**。这不是"破格",是"类型专属"。

### Arbitrator 自己会不会作弊?

arbitrator 只有 `Read` 权限,**不会写任何文件**。它的失败模式:

- Salience 计算失准(LLM 判 relevance 失灵)→ 走 deterministic fallback(关键词重叠)
- 超时 → partial 输出
- 崩溃 → 空 marker + 退化到 v1.6.2a

没有"作弊"的空间——输入是三个 subagent 的固定输出,输出是 ranked list,中间没有自由裁量。这是**纯 consumer**,不是 producer。

### 如果我相同 subject 反复提问,novelty 会不会让系统"学坏"?

novelty 衰减是反刷屏机制,不是"隐藏相关信息"。具体:

- 同一条信号出现 3+ 次 → novelty 降到 0.2
- 但 urgency / relevance / importance 不变——如果信号本质上高相关 + 高 importance,即使 novelty 低也能进 top-5
- fatigue 是避免"同一条无关历史被反复推荐"的机制,不会让真正重要的信号被埋

例外: 如果你确实在一个话题上无限循环(比如每周问 5 次"要不要跳槽"),novelty 触发 3 次后系统会用 `decision_fatigue` DREAM 触发器 flag 你"最近 3 天已做 N 个同类决策"(详见 DREAM 文档)。

### Tie-breaking 规则是什么?

两条信号 salience 完全相同时,按顺序:

1. **更新优先**——timestamp 更近的赢
2. **importance 更高优先**——如果还打平
3. **alphabetical by signal_id**——完全确定的 fallback,保证"相同输入总产生相同排序"

**no randomization**——Cortex 的仲裁必须**reproducible**。两次相同输入必须产生相同输出,便于 debug 和 eval。

### AUDITOR 怎么评价仲裁质量?

3 个指标(详见 [auditor-eval-history.md](./auditor-eval-history.md)):

- **`cognitive_annotation_quality` (0–10)**——ROUTER 有没有"用上"这个注释?
- **`annotation_utilization_rate`**——多少比例的 session 里,下游 agent 至少引用一条 signal?
- **`suppression_precision`**——arbitrator 发 SOUL CONFLICT 警告时,REVIEWER 有没有独立 flag 同一问题?

低分长期趋势 → RETROSPECTIVE 在 briefing 里 surface "hippocampus retrieval tuning needed" 或 "GWT weight retuning needed"。

### 多源同时失败怎么办?

**Degradation hierarchy**(多 failure 叠加时按顺序处理):

1. 缺 source(hippocampus 空)→ 用现有 source 继续
2. LLM relevance 判断失败 → 回退关键词重叠
3. 硬超时(10s)→ 发 partial output
4. Arbitrator 整体 crash → 空 marker + 退化到 ROUTER 原始模式

**每一步,输出都是一个 valid annotation block**(哪怕是空的)——ROUTER 永远不会收到"半截或畸形"的块。graceful degradation 是不可协商的设计原则。

---

## Troubleshooting

### "每次都没有 `[COGNITIVE CONTEXT]` 显示"

可能原因(按可能性排序):

1. **你通常只用 direct-handle 或 Express**——这些场景根本不走 Step 0.5
2. **migration 没跑过**——INDEX.md / concepts 都空,signal registry 无东西可排,GWT 直接发空 marker
3. **所有信号 salience < 0.3**——GWT 发了 `(no high-salience signals)` 标记但你没看到(ROUTER 可能把这个标记折叠在"其他"里)
4. **cortex_enabled: false**——`_meta/cortex/config.md` 里被关了

诊断:

```bash
# 查本次 session 的 arbitration record (记在 session frame md 里)
grep -l "gwt_arbitration" _meta/sessions/$(ls -t _meta/sessions/ | head -1)
```

### "SOUL CONFLICT 反复误升"

诊断: 查最近 10 次 eval-history 里 `suppression_precision` 的值。如果持续低(<5),说明 GWT 报的 SOUL CONFLICT 和 REVIEWER 自己的判断**不一致**——GWT 报的警告可能是假阳性。

处理:
- 短期: 在每次误升时反驳("这次 SOUL CONFLICT 不适用"),让 AUDITOR 积累证据
- 长期: AUDITOR 标 retuning 需求后,可能需要调整 SOUL check subagent 的维度匹配阈值——那是 `_meta/cortex/config.md` 级别的调整,用户决策 #4 不会自动触发"关掉某个模块",但你可以决定手动调

### "annotation_utilization_rate 长期 <20%"

这说明 cortex 的输出 ROUTER / 六领域 **很少真正用上**——花了 7 秒做 annotation,但下游 agent 几乎不引用。

诊断: 这是 AUDITOR 最关心的"性价比"指标。可能原因:

1. **ROUTER prompt 没充分引导使用 cognitive context**——pro/agents/router.md 可能需要更明确"你应该参考 `[COGNITIVE CONTEXT]` 块"
2. **Hippocampus 质量低**——检索的 session 确实不相关,下游 agent 没法用
3. **你的问题类型本身和历史关联不强**——如果多数问题都是孤立的新问题,cortex 本来就发挥不了作用

处理: 看 AUDITOR 在 eval-history 里具体 flag 的是哪一项,对症处理。

### "Top-5 被无关 concept 挤满"

Concept lookup 可能**过度泛泛匹配**——每个 concept 都激活,拿到 relevance 0.7,把 SOUL 的 0.85 挤到第二,其他重要信号被截。

诊断: 看某次 session 的 arbitration record,检查各个 concept 的 relevance 评分。如果都在 0.7 左右,说明 concept lookup subagent 判相关度太宽松。

处理:
- 短期: 这类问题 AUDITOR 会 flag `cognitive_annotation_quality` 低
- 中期: 等待 concept-lookup 的 prompt 优化(v1.7 spec 明说 open question)
- 临时绕路: `_meta/cortex/config.md` 把 `per_signal_floor` 从 0.3 提到 0.5,过滤掉中等相关度噪音

---

## 深入阅读

产品入口:

- [What is Life OS](../../getting-started/what-is-life-os.md) — Life OS 整体定位
- [Quickstart](../../getting-started/quickstart.md) — 首次上朝流程

同目录用户文档:

- [overview.md](./overview.md) — Cortex 总览
- [hippocampus-recall.md](./hippocampus-recall.md) — hippocampus 产生的 `decision_analogy` / `value_conflict` 信号
- [concept-graph-and-methods.md](./concept-graph-and-methods.md) — concept lookup 产生的 `canonical_concept` / `emerging_concept` 信号
- [narrator-citations.md](./narrator-citations.md) — top-5 信号如何变成 Summary Report 里的 `[signal_id]` 引用
- [auditor-eval-history.md](./auditor-eval-history.md) — `cognitive_annotation_quality` / `suppression_precision` / `annotation_utilization_rate` 的长期监控

Spec 层(英文):

- `references/gwt-spec.md` — 完整 spec: 公式、信号类型、算法、失败模式、tie-breaking
- `references/cortex-spec.md` §GWT Arbitrator — 在整体架构里的位置
- `references/hippocampus-spec.md` — hippocampus 输出格式(GWT 的输入源之一)
- `references/concept-spec.md` — concept 输出格式
- `references/soul-spec.md` §Tiered Reference by Confidence — tier 定义
- `devdocs/architecture/cortex-integration.md` §4 — Step 0.5 三源并行流程

Agent 定义(深度用户):

- `pro/agents/gwt-arbitrator.md` — agent 定义、tool 约束、model 选择

---

**上一篇**: [narrator-citations.md — Narrator 引用与 trace](./narrator-citations.md)
**下一篇**: [auditor-eval-history.md — AUDITOR 自反馈数据](./auditor-eval-history.md)
