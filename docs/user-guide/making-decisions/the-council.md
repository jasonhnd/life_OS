# 朝堂议政 · COUNCIL 辩论机制

> 本文档是作者自用参考。写给懂系统内部的人看。

## COUNCIL 是什么

COUNCIL 是 Life OS 的**跨领域辩论场**。当六领域的结论出现严重冲突（分差 ≥ 3 或结论直接矛盾），REVIEWER 在终审时自动触发，让冲突的领域进入 **3 轮结构化辩论**，最后由 DISPATCHER 担任 moderator 给出裁决建议。

和 STRATEGIST 的根本区别：
- **COUNCIL** 解决**数据驱动的领域冲突**（finance vs execution 分差大）
- **STRATEGIST** 探索**价值观和身份**（和历史思想家对话，处理迷茫/存在问题）

不要混淆这两个机制——COUNCIL 是决策引擎内部的冲突解决工具；STRATEGIST 是完全独立的抽象思考流程。

## 何时自动触发

`pro/agents/council.md` 写的触发条件：

> **Auto-trigger** (by reviewer during final review):
> - Any two domains' scores differ by ≥ 3 points (e.g., finance gives 4/10, execution gives 8/10)
> - One domain explicitly recommends "do it" while another explicitly recommends "don't"
> - Reviewer identifies an irreconcilable contradiction in domain conclusions

三种自动触发条件：

1. **分差 ≥ 3** — 两个领域评分差 3 分及以上
2. **结论直接矛盾** — 一个说"做"另一个说"不做"
3. **REVIEWER 判断不可调和** — REVIEWER 主观认为冲突无法通过简单合成解决

**不自动触发的情况**：
- 分差 1-2 分 —— 这是正常方差，不辩论
- 细节差异但结论一致 —— 比如两个领域都说"做"，只是具体路径不同
- 仅一个领域有异议 —— 需要至少两个领域明确对立

`pro/agents/council.md` anti-patterns 里明确：

> Do not trigger debate for minor score differences (< 3 points) — those are normal variance

辩论是有成本的（3 轮 × 多领域 × token），小分差自动辩论就是滥用。

## 手动触发

用户可以主动要求 COUNCIL。触发词：
- 英文：`debate` / `court debate`
- 中文：`朝堂议政` / `辩论一下`
- 日文：`討論`

典型场景：
- 用户看完奏折觉得"虽然分差不够触发 COUNCIL，但我还是想听两边具体的争论"
- 用户看到 Must Address 里某几条互相矛盾，想看辩论
- 用户想测试某个假设是否能被某领域站住脚

`pro/agents/router.md` 里写的：当用户在奏折后犹豫时，ROUTER 要分辨：
- **犹豫因为数据冲突** → COUNCIL（可能已经自动触发了）
- **犹豫因为"不知道我到底想要什么"** → 问是否启动 STRATEGIST

## 辩论格式 · 3 轮结构

**Round 1 · Position Statement（立场陈述）**
- Moderator（DISPATCHER）宣布辩论主题和核心分歧
- 每个相关领域用 **≤ 3 句话**陈述立场，附支持证据

**Round 2 · Rebuttal（反驳）**
- Moderator 把每方的核心论据传给对方
- 每方用 **≤ 5 句话**反驳对方论据
- **对事不对人**——反驳的是论据，不是领域本身

**Round 3 · Final Statement（终结陈述）**
- 每方用 **≤ 2 句话**给出最终立场

**句数限制是硬性的**。`pro/agents/council.md` anti-patterns：

> Do not let debates devolve into monologues — enforce sentence limits

限制是为了防止领域自说自话——辩论的价值在交锋，不在陈词冗长。

## 信息隔离 · COUNCIL 里谁看到什么

每个辩论领域都是独立 subagent。它们收到：
- 辩论主题
- **自己的原始报告**
- **对方的立场摘要**（Round 1 开始）

它们**收不到**：
- 对方的完整报告
- 对方的研究过程（🔎/💭/🎯）
- 对方的思考过程

这个隔离设计保证辩论是"立场 vs 立场"，不是"互相搬运完整分析"。如果给每方对方的完整报告，辩论就退化成"合成综合报告"——失去交锋的意义。

## 裁决（Verdict）

3 轮辩论后，Moderator 输出裁决：

```
🏛️ [theme: council] · Verdict

📋 Debate topic: [一句话]
⚔️ Core disagreement: [冲突的根本来源]

Side A ([domain]): [最强论据，1 句话]
Side B ([domain]): [最强论据，1 句话]

🔍 Moderator assessment: [哪一方证据更强、哪一方风险更大、什么信息能化解这个分歧]

📌 Recommendation to router: [综合建议——不是决定，由用户决定]
```

**关键：Moderator 不做最终决定**。`pro/agents/council.md` anti-patterns：

> Do not let the moderator take sides — the moderator summarizes, the user decides

Moderator 的工作是**总结 + 指出化解分歧所需的信息**，不是"我站 Side A"。ROUTER 拿到裁决后写进奏折，**用户看完奏折做决定**。

## PLANNER 辩论后如何整合

COUNCIL 辩论完，输出裁决，接下来的流程：

1. **PLANNER 重新介入**（这是 `pro/CLAUDE.md` 第 6 步的说法）：

   > After the debate, the PLANNER compiles consensus and disagreements, and the ROUTER produces the Summary Report incorporating the debate outcome.

   PLANNER 把辩论的：
   - **共识**（两方都同意的部分）
   - **分歧**（无法调和的部分）
   - **化解条件**（Moderator 指出的所需信息）
   
   写成一份简短说明。

2. **ROUTER 合成奏折**：
   - 整体评分会体现 COUNCIL 的结果（通常被拉低，因为有明确冲突）
   - Must Address 里会出现"获取 Moderator 指出的缺失信息"的条目
   - 奏折顶部或相关段落嵌入 Verdict 块

3. **Action Items 可能新增**：比如 Moderator 说"关键变量是能否 3-6 个月内找到联创"——Action Items 里会加"3 周内联系 2 个潜在联创"。

## 辩论轮次不能省

`pro/agents/council.md` anti-patterns：

> Do not skip rounds — all 3 rounds are mandatory

为什么三轮都要：
- Round 1：摆立场（双方还没互动）
- Round 2：交锋（这里才出真正的信息）
- Round 3：沉淀（摆清楚最终位置，不再被辩论节奏影响）

少一轮：
- 没 Round 1 → 不知道双方原本主张
- 没 Round 2 → 没有交锋，只是两段独白
- 没 Round 3 → 最后的立场被 Round 2 的激烈情绪污染

## 实战例子 · 辞职创业

**背景**：用户问"要不要现在辞职创业"。六领域跑完：
- finance: 7/10（存款撑 18 个月，可以）
- execution: 3/10（单干风险极高）
- 其他领域都在 5-7 之间

分差 4 分，REVIEWER 自动触发 COUNCIL。

### Round 1 · 立场陈述

**Moderator**（DISPATCHER）：
> 辩论主题：用户当前是否应该辞职创业。finance 给 7/10 支持，execution 给 3/10 反对。请各自陈述。

**finance**（3 句话）：
> 用户存款能覆盖 18 个月全部开销，属可承受风险期。即使完全失败，现金流可恢复。财务上的"辞职创业"窗口确实打开。

**execution**（3 句话）：
> 70% 的单人创业 2 年内失败。用户没有联合创始人，没有首批客户，没有验证过的商业模式。执行层面这是一个"赌资金期限"的赌博，不是创业。

### Round 2 · 反驳

**Moderator** 把双方立场传给对方，各自反驳。

**finance**（5 句话）：
> execution 把"现在辞职"和"单干创业"绑在一起讨论，这是混淆。18 个月的现金流意味着可以花 6 个月找联创和验证模式。不是"辞职就必然单干"。执行风险是可以通过时间窗口缓解的，不是恒定值。这个时间窗口恰恰是财务条件给出的。

**execution**（5 句话）：
> finance 的 18 个月假设是"按现在支出"。创业启动后支出会增加——办公、工具、学习、可能的小额投入。实际现金期会短于 18 个月。而且时间窗口假设"找联创"这件事本身成功率高——实际上找到合适联创的成功率和找工作差不多甚至更低。时间窗口存在不等于能被充分利用。

### Round 3 · 终结陈述

**finance**（2 句话）：
> 财务上这是一个"可承受失败"的窗口。在可承受范围内不做就是错过成本。

**execution**（2 句话）：
> 执行层的失败不是"钱烧完"，是精神和时间磨损。即使钱撑住了，人撑不住。

### Moderator 裁决

```
🏛️ Verdict

📋 Debate topic: 现在是否辞职创业？
⚔️ Core disagreement: 风险是"财务承受"还是"执行磨损"——衡量标准不同

Side A (finance): 18 个月现金流给出可承受的失败窗口
Side B (execution): 单干成功率低、精神磨损风险被低估

🔍 Moderator assessment: 
execution 的证据更具体（失败率数据），finance 的框架更正面但依赖"找联创"能成。
关键变量是：6 个月内能不能找到合适联创。
这个信息缺失时，两方立场都站不住。

📌 Recommendation to router:
问题不是"做不做"，是"现在还是再等"。建议增加 Action Item：3 周内联系 2 个潜在联创，
3 个月后复评。
```

PLANNER 整合共识："双方都认可财务可承受"，分歧"执行风险不可忽视"，条件"联创可得性是决定变量"。

ROUTER 在奏折里：
- 整体评分 6/10（中间位置，反映冲突）
- Must Address 新增"先验证联创可得性"
- Action Items 新增"3 周内联系 2 个潜在联创"

## 读奏折时的 COUNCIL 信号

Audit Log 里会出现：

```
- REVIEWER round 2: Triggered COUNCIL (finance 7 vs execution 3, diff 4)
- COUNCIL: 3 rounds, consensus on timing
```

运营报告里：

```
- COUNCIL: Triggered
```

Summary Report 正文里会嵌入 Verdict 块（前面讲过的格式）。

**用户读到 COUNCIL 触发应该做什么**：
1. **不要恐慌** — COUNCIL 触发 = 系统在正常工作，识别了真正的冲突
2. **重点读 Core disagreement** — 这是整个决策的真瓶颈
3. **关注 Moderator assessment 的"信息缺失"** — 补这些信息能化解冲突
4. **把 Recommendation 当建议**，不是最终决定

## 反模式总结

`pro/agents/council.md` 完整 anti-patterns：

1. **不要让辩论变独白** — 强制句数限制
2. **Moderator 不要站队** — Moderator 总结，用户决定
3. **不要跳过任何一轮** — 三轮都要
4. **小分差（< 3）不要触发辩论** — 那是正常方差
5. **不要和 STRATEGIST 混淆** — COUNCIL 解决数据冲突，STRATEGIST 处理价值观和身份

## COUNCIL vs STRATEGIST · 什么时候用哪个

| 信号 | 用 |
|------|-----|
| "finance 说没问题但 execution 说别干，我到底听谁的？" | COUNCIL（数据冲突） |
| "这个决定技术上没问题，但我感觉不对劲" | STRATEGIST（价值观层） |
| 领域分差 ≥ 3 | COUNCIL 自动 |
| "我不知道我到底想要什么" | 问是否启动 STRATEGIST |
| 奏折结论合理但用户不接受 | STRATEGIST |
| 奏折里明确显示两个领域打架 | COUNCIL |

COUNCIL 在决策引擎里，STRATEGIST 在决策引擎外。需求不同，不能替代。

## 总结 · COUNCIL 的核心价值

- **信号**：自动触发代表系统识别了真冲突，不是系统出错
- **结构**：3 轮辩论保证交锋而非独白
- **信息隔离**：领域只看对方立场摘要，不看完整报告
- **裁决是建议**：Moderator 不做决定，用户读奏折后决定
- **价值**：把隐性分歧显式化 → 用户看到真正的决策瓶颈
