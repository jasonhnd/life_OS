# 读懂奏折 · Summary Report 结构逐段拆解

> 本文档是作者自用参考。写给懂系统内部的人看。

## 奏折是什么

奏折（Summary Report）是 ROUTER 在第 7 步产出的，**整个全朝议工作流的主交付物**。它合成：
- 六领域报告的结论
- REVIEWER 两轮评审的判断
- 可选的 COUNCIL 辩论结果
- SOUL 对齐情况
- 历史数据联动

奏折不是六份报告的简单拼接，也不是"AI 的综合意见"——它是 ROUTER 根据信息隔离原则**精炼出的用户决策依据**。

## 奏折标准结构

源自 `pro/CLAUDE.md` 第 7 步定义：

```
Summary Report: [Subject]

Overall Rating: [X]/10 — [One-sentence conclusion]

Must Address: [Consolidated findings from all domains]
Needs Attention: [Consolidated findings from all domains]
Room for Improvement: [Consolidated findings from all domains]

Domain Ratings:
| Domain | Dimension | Score | One-liner |
|--------|-----------|-------|-----------|

Action Items:
1. [Specific action] — Deadline — Responsible domain

Audit Log: [Brief record of each stage]

Operations Report:
- Total Time: [From user's message to report completion]
- Model: [Current model in use]
- Agent Calls: [N total]
- Vetoes: [X times]
- COUNCIL: [Triggered / Not triggered]
```

下面逐段拆解每一部分怎么读、什么信号该抓、什么是噪声。

## 整体评分 · Overall Rating X/10

**这是奏折最关键的一个数字。** 决定用户是否继续读下去。

评分含义（作者自定口径，不是系统硬性规则）：

| 分数 | 含义 | 典型建议 |
|------|------|----------|
| 9-10 | 条件极好，证据压倒性支持 | 立即行动 |
| 7-8 | 值得做，但有需要先解决的条件 | 解决 Must Address 后行动 |
| 5-6 | 条件一半一半，需要个人判断 | 再等信息 / 找 STRATEGIST 聊 |
| 3-4 | 风险明显大于收益 | 不推荐做 |
| 1-2 | 不该做 | 停 |

如果分数在 5-6 的中间区间，**不要急着执行**。这意味着数据本身没给出明确方向——很可能需要：
- 更多信息（调查、咨询、试点）
- 或者问题本质是价值观选择（→ STRATEGIST）
- 或者 COUNCIL 有未完全化解的分歧

评分后的**一句话结论**很重要。ROUTER 在这一行要说清楚"什么是这次决策的命门"。读奏折时先看这两行，整个报告的基调就定了。

## 三层结论 · Must / Needs / Room

### Must Address · 必须处理的

**这是硬性条件**。奏折里列出的 Must Address 必须在行动前解决——否则即使分数高，行动也会失败。

Must Address 的信号：
- 出现**具体缺失**（"没有应急基金"、"合同里没有退出条款"）
- 出现**硬性风险**（"法律不允许"、"健康指标不达标"）
- 出现**关系层红线**（"配偶强烈反对且没谈过"）

读到 Must Address 要做的事：把每一条当作**待办事项**，先解决再回来。如果 Must 里有 3+ 条，整个决策可能需要推迟。

### Needs Attention · 需要注意的

**软性提醒**。不是 blocker，但忽略了会付出代价。典型内容：
- 潜在风险但概率不大
- 需要持续监控的指标
- 可能的并发症

读到 Needs Attention 的做法：列进行动项的**次优先级**，一次做不完没关系，但要追踪。

### Room for Improvement · 可以更好的

**加分项**。不影响行动，但能让结果更好。通常是：
- 可以优化的执行方式
- 可以补强的准备
- 可以考虑的替代方案

时间紧张时这一层可以先跳过。有余力时再读。

### 三层的实际用法

```
如果 Must Address 非空 → 先解决 Must，再看其他
如果 Must Address 为空但 Needs 有 3+ → 做行动规划时纳入次优先级
如果 Must + Needs 都空 → 看 Room，选一两个优化点
```

## 领域评分表 · Domain Ratings

```
| Domain | Dimension | Score | One-liner |
|--------|-----------|-------|-----------|
| finance | 财务可承受 | 7/10 | 存款撑 18 个月，可接受 |
| execution | 单干风险 | 3/10 | 缺联创，独立执行失败率高 |
| people | 家庭影响 | 6/10 | 配偶中性，但孩子上学阶段 |
| growth | 技能迁移 | 8/10 | 技术栈 70% 可复用 |
| governance | 法律风险 | 9/10 | 竞业条款宽松 |
| infra | 健康承受 | 5/10 | 当前作息已透支 |
```

**这张表是奏折真正的信息密度所在。** 不要只看整体评分——领域之间的分差才是决策线索。

**看领域评分表的方法**：

1. **找最低分** — 最低分领域是整个决策的**瓶颈**。整体评分通常受最低分拖累。
2. **找分差 ≥ 3 的两个领域** — 这是 COUNCIL 应该被触发的信号（如果没触发，可能 REVIEWER 漏判了）。
3. **读每个领域的 One-liner** — 一句话的措辞暴露了该领域的真实态度。"可接受"≠"推荐"；"可行"≠"明智"。
4. **整体评分 ≈ 各领域加权平均？** — 不完全是。ROUTER 会根据领域权重（由 Subject 决定）做非均匀合成。"单干风险 3/10"可能是主瓶颈，整体就被拉到 5-6。

**技能点**：每次读奏折都用 10 秒时间在领域评分表上——分数分布比整体评分更有信息量。

## 行动项 · Action Items

```
Action Items:
1. 开立独立账户转入 6 个月应急基金 — 2026-05-01 — finance
2. 3 周内联系 2 个潜在联创 — 2026-05-15 — people
3. 与配偶安排 1 次 90 分钟深度谈话 — 本周 — people
...
```

**格式要求**：每条必须包含
- 具体动作（动词开头，可执行）
- 截止日期（绝对日期，不是"尽快"）
- 负责领域（后续 AUDITOR 和 ADVISOR 追踪用）

**读 Action Items 的做法**：
- 复制到 TODO 系统（Notion Todo Board / 苹果提醒 / Things 等）
- 每条检查是否**今天就能开始第一步**——不能则要求自己拆成更小的子任务
- 如果超过 5 条，优先级排序，先做 Must Address 相关的

**一个常见错误**：用户读完奏折觉得"都挺有道理的"然后关掉——没有把 Action Items 真正执行。奏折的价值 80% 在行动项里，不是评分里。

## 审计日志 · Audit Log

```
Audit Log:
- ROUTER triage: 决策类、全朝议
- Intent clarification: 3 rounds
- PLANNER planning: 6 dimensions, 4 domains assigned
- REVIEWER round 1: Conditionally Approved (condition: must include 10/10/10)
- DISPATCHER: Group A (finance, growth, people), Group B (execution, governance, infra)
- Six domains execution: 4 reports (people, finance not assigned)
- REVIEWER round 2: Triggered COUNCIL (finance 7 vs execution 3, diff 4)
- COUNCIL: 3 rounds, consensus on timing
```

**审计日志是流程透明度证明**。用户可能大部分时候不看，但它有三个用途：

1. **调试**：如果奏折感觉"不对劲"，查审计日志能找到 ROUTER 哪一步做了奇怪的判断。
2. **追溯**：后续 AUDITOR 审计的依据。
3. **学习**：看 ROUTER 在类似问题上的分诊模式。

**看审计日志该抓的信号**：
- 意图澄清是 3 轮还是 0 轮？（0 轮 = 违规）
- 是否触发了 COUNCIL？触发的分差是多少？
- REVIEWER 封驳过几次？（封驳过是**好事**，说明质量有人把关）
- 是否有"Veto: 2"？（代表经过两次重写才通过，决策依据更扎实）

## 运营报告 · Operations Report

```
- Total Time: 6 分 22 秒
- Model: claude-opus-4-7
- Agent Calls: 14 total
- Vetoes: 1
- COUNCIL: Triggered
```

**这一段主要给作者自己看**。内容：
- 这次会话多久（耗时）
- 用的模型
- 总共调用了几个 subagent
- 封驳几次
- 是否触发 COUNCIL

**可以用来**：
- 判断成本（14 个 agent calls ≈ 大约多少 token）
- 和过往会话对比（平均时间变长/变短）
- 发现流程退化（Agent Calls 突然变少 = 可能跳步）

## SOUL 参考块（可能出现在奏折顶部或 REVIEWER 段）

```
🔮 SOUL Reference

【core · Core Identity】
  · 家庭优先于事业 (0.82) — 这个决策会不会挤占陪伴时间？
    → 会。周末时间从 100% 下降到 ~40%，需要提前沟通。
  · 独立思考 (0.75) — 这个决策是自己想清楚的吗？
    → 大体是，但存在羊群效应风险（受朋友影响）。

【secondary · Active Values】
  · 健康长期主义 (0.52) [strong match] — 会不会透支？
    → 会，初期 6 个月会透支。

【Integrated Conclusion】
  SOUL compatibility: 🟡 mixed
  Focus callout: 家庭维度是本次决策的最大风险源。
```

**SOUL Reference 块是 REVIEWER 的必输出项**（每次决策都必须包含，HARD RULE）。

读法：
- 如果有 core 维度被"challenge"——重点读
- 如果显示 ❌ conflict——这是**半封驳信号**，REVIEWER 在告诉你"这个决定和你的核心身份冲突"
- 如果显示 ✅ high——决策和价值观对齐，可放心

## COUNCIL 裁决块（只在触发 COUNCIL 时出现）

```
🏛️ Council · Verdict

📋 Debate topic: 单干风险 vs 财务可承受
⚔️ Core disagreement: 风险集中在"单干"而不是"创业"本身

Side A (finance): 存款支撑期足够，创业财务风险可承受
Side B (execution): 单干失败率 70%+，有联创前创业是自杀

🔍 Moderator assessment: execution 证据更强，但 finance 的时间窗判断合理。关键变量是"联创能否 3-6 个月内找到"。

📌 Recommendation to router: 不是"做不做"问题，是"现在还是再等半年"问题。
```

**如果奏折里有这一段，说明 ROUTER 是在 COUNCIL 辩论后合成结论的**。读法：
- Core disagreement 是整个决策的**真正瓶颈**
- Moderator assessment 指出**缺失信息**——解决这个信息空白能化解冲突
- Recommendation 是对 ROUTER 的建议，ROUTER 会整合到整体评分和 Must Address 里

## 快车道简报（不是奏折）

走快车道的请求，ROUTER 返回的是简报不是奏折。简报结构：

```
📋 Brief Analysis: [Subject]

[按领域分别列分析结果，每个领域一段，包括研究过程]

---
🏃 This is an express analysis. Want a full court deliberation instead?
```

简报**没有**：整体评分、Must/Needs/Room、领域评分表、审计日志、运营报告。

读简报就按领域段读，重点看领域给出的具体结论和风险。最后一行的升级邀请要**真的考虑**——如果这个话题涉及决策，应该说"是"。

## 使用技巧 · 读奏折的顺序

我自己的读法（3 分钟从奏折拿到决策）：

1. **读 Overall Rating 和那一句话结论**（10 秒）—— 判断整体基调
2. **读领域评分表**（30 秒）—— 找瓶颈和分差
3. **读 Must Address**（30 秒）—— 硬性条件
4. **读 SOUL Reference**（30 秒）—— 价值观对齐
5. **读 Action Items**（30 秒）—— 提取待办
6. **跳过 Needs / Room / Audit Log**，必要时回来读

5 步合计不到 3 分钟。其他内容在需要时再回来读。

## 常见误读

1. **只看整体评分不看领域分差** — 8/10 但某领域 3/10 = 被掩盖的风险
2. **把 Needs Attention 当 Must Address** — 两者严重等级差一个级别
3. **忽略 SOUL Conflict 信号** — REVIEWER 标 ❌ 的时候要当回事
4. **Action Items 不落地** — 奏折价值 80% 在行动项
5. **看到 COUNCIL 就觉得系统"矛盾了所以不可靠"** — COUNCIL 存在**证明系统在正常工作**，而不是失败
