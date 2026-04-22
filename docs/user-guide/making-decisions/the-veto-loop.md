# 封驳机制 · REVIEWER 的 Veto Loop

> 本文档是作者自用参考。写给懂系统内部的人看。

## 封驳是什么

封驳（Veto）是 REVIEWER 对 PLANNER 或六领域输出说"不通过"的权力。源自中国古代门下省驳回诏书的制度——皇帝颁诏，门下省有权拒绝。Life OS 里 REVIEWER 的这个角色就是防止 PLANNER 的规划或领域报告有明显缺陷时被强行推进。

`pro/CLAUDE.md` 里写的 Orchestration Code of Conduct 第一条：

> Veto is the soul — REVIEWER must review seriously, including emotional dimensions. HARD RULE.

**封驳是系统的灵魂**。这不是夸张——如果 REVIEWER 只会 Approve，整个 Draft-Review-Execute 架构就退化成单向流水线，失去了信息隔离和独立评审的全部价值。

## REVIEWER 的两种审核时机

| 时机 | 审什么 | 标准 |
|------|--------|------|
| 第 3 步（初审） | PLANNER 提交的规划文档 | 维度全不全？分工合理吗？有没有明显盲区？ |
| 第 6 步（终审） | 六领域提交的报告 | 分析有实质内容吗？评分和分析一致吗？有未解决的矛盾吗？ |

两种时机都可能封驳，但**封驳循环只发生在第 3 步（初审）**。第 6 步如果发现问题，REVIEWER 可能触发 COUNCIL（辩论），但不会让六领域重跑。

## 三种评审结果

REVIEWER 可以给出的三种结论：

### ✅ Approved

计划/报告完全通过。直接进入下一阶段。

### ⚠️ Conditionally Approved

带条件通过。REVIEWER 附加一组条件，条件写进规划文档，DISPATCHER 在派单时必须把条件反映到领域指令里。

典型条件：
- "必须包含 10/10/10 Regret Test"
- "finance 分析必须涵盖总损失情境下的生活质量"
- "execution 必须评估没有联创的替代路径"

Conditionally Approved 的流程效果：**不回炉 PLANNER，向前走但带约束**。

### 🚫 Veto

封驳。规划文档被打回 PLANNER 重写。

## 什么触发封驳

`pro/agents/reviewer.md` 没给出"封驳规则清单"，因为 REVIEWER 是**判断**而不是"规则执行机"。但实战中触发封驳的典型信号：

1. **维度缺失** — 关键维度没被覆盖。例如"换工作决策"没考虑家庭影响。
2. **分工不合理** — 该由 finance 做的事指派给了 execution。
3. **SOUL 冲突但没被识别** — core 维度被挑战但 PLANNER 没标出。
4. **情感维度敷衍** — 规划里没有情感考虑或用"建议用户自行考虑"糊弄。
5. **Red Team 测试失败** — REVIEWER 假设计划会失败，找到 3 个失败点但 PLANNER 都没防。
6. **战略地图冲突** — 决策会打断上游依赖或阻断下游项目，但 PLANNER 没提。
7. **wiki 矛盾** — 结论和既有高置信度 wiki 条目矛盾，但 PLANNER 没处理。

## 封驳格式（必须四字段）

REVIEWER 封驳时必须给出四个字段（`pro/agents/reviewer.md` HARD RULE）：

```
🚫 Veto
- Failed dimension: [哪个具体维度没过]
- Core problem: [一句话，为什么没过的本质]
- Revision direction: [具体怎么改——不是"请重新考虑"]
- Missing information: [还需要什么数据（如有）]
```

**为什么要四字段**：给 PLANNER 可操作的指引。如果 REVIEWER 只说"不通过"，PLANNER 不知道怎么改——重写后还是会被再次封驳，浪费轮次。

## 封驳循环 · 最多 2 次

`pro/CLAUDE.md` 第 3 步：

> Veto Correction Loop: Pass the veto reasons and correction direction back to the PLANNER; the PLANNER revises and resubmits to the REVIEWER for review. Maximum 2 loops; the 3rd time must result in Approved or Conditionally Approved.

流程：

```
PLANNER 规划 v1 → REVIEWER 审 → 🚫 Veto
                                   ↓
                         封驳原因 + 修正方向
                                   ↓
PLANNER 规划 v2 → REVIEWER 审 → 🚫 Veto (第 2 次)
                                   ↓
                         封驳原因 + 修正方向
                                   ↓
PLANNER 规划 v3 → REVIEWER 审 → ✅ Approved 或 ⚠️ Conditionally Approved
                               (绝对不能再 🚫)
```

**为什么限制 2 次**：
- 防止死循环——REVIEWER 和 PLANNER 卡在分歧里用户干等
- 强制质量闭环——第 3 次必须过，REVIEWER 要么接受当前方案，要么用 Conditionally Approved 把不完美的地方写进条件
- 保护 token 预算——每轮封驳 = 一次 PLANNER 重跑

**第 3 次还想封驳怎么办**：
- 必须改用 Conditionally Approved
- 把无法达成共识的要求写成条件
- 让条件在 DISPATCHER 派单时传递给领域

## 封驳循环的信息隔离

REVIEWER 封驳时**只传回必要信息**：

| 从 REVIEWER 传给 PLANNER | 内容 |
|--------------------------|------|
| 传 | Veto 的四个字段（Failed dimension / Core problem / Revision direction / Missing information） |
| 不传 | REVIEWER 的完整思考过程 |
| 不传 | 其他领域的报告（初审时领域还没跑）|
| 不传 | REVIEWER 的 Red Team 详细推演 |

PLANNER 重写时：
- 聚焦在 REVIEWER 指出的问题上
- 不扩大范围（如果原来是 4 维度，不要改成 6 维度除非 REVIEWER 要求）
- 保留之前没被封驳的部分

## Conditionally Approved 的具体含义

**Conditionally Approved ≠ Approved**。这是一个信号：REVIEWER 觉得整体 OK 但有保留。条件必须被严格执行。

例子：

```
⚠️ Conditionally Approved
Conditions:
1. finance 必须包含 18 个月现金流压力测试（下行场景）
2. people 必须评估"配偶未充分沟通"的关系风险
3. REVIEWER 终审时会重点审这两项
```

DISPATCHER 看到这份规划文档，派单给 finance 和 people 时必须把条件变成具体指令：

```
-> finance: [原任务] + 必须包含 18 个月现金流压力测试
-> people: [原任务] + 必须评估"配偶未充分沟通"的关系风险
```

REVIEWER 在第 6 步终审时，会专门验证这两项是否被履行。没履行 = 领域报告被打回重做。

## 情感维度的封驳

`pro/agents/reviewer.md` 明确要求：**所有决策都要审情感维度**，包括工作决策。不能敷衍。

四类情感审查：
1. **情绪**：用户当前状态是否影响判断？
2. **关系**：这个决策怎么影响最重要的人？
3. **价值观**：和用户长期愿望一致还是冲突？
4. **Regret Test（10/10/10）**：
   - 10 分钟后：冲动会消退吗？这是瞬间反应还是考量判断？
   - 10 个月后：半年到一年的尺度，更可能后悔"做了"还是"没做"？
   - 10 年后：人生长河里，这个决定还重要吗？还是根本不会记得？

每个维度要给出**具体判断**，不能"建议用户自己考虑"。

Reviewer anti-pattern 第二条：
> Do not use "suggest the user consider on their own" to brush off the emotional dimension.

情感维度敷衍 → 封驳。这是硬规则。

## SOUL 对齐检查

每次决策 REVIEWER 必须输出 SOUL Reference 块（HARD RULE）。三档策略：

### core · Core Identity（confidence ≥ 0.7）

**全部引用**。高置信度维度代表用户核心身份，每个决策都必须考虑。

### secondary · Active Values（0.3 ≤ confidence < 0.7）

**引用与决策最相关的前 3 个**。REVIEWER 评估相关性：
- Strong match（直接相关）→ 优先
- Weak match（间接相关）→ 按置信度排，取前几个
- No match → 跳过

### emerging · Emerging Dimensions（confidence < 0.3）

**只计数、不展示**。ADVISOR 的 Delta 块会跟踪，REVIEWER 不引用。

### SOUL CONFLICT · 半封驳信号

如果决策挑战 core 维度，REVIEWER 必须在 Summary Report 顶部加：

```
⚠️ SOUL CONFLICT: this decision challenges core identity dimension [X]. Re-examine?
```

这是**半封驳信号**——不触发封驳循环，但强烈提示用户重新审视。

## Red Team Review · 假设计划会失败

REVIEWER 发 verdict 前必须做一次 Red Team（`pro/agents/reviewer.md`）：

> Before issuing your verdict, assume the plan WILL fail. Identify:
> - What is the most fragile assumption?
> - Which step relies most heavily on luck?
> - Which risk was deliberately downplayed?
>
> State the top 3 failure points. If the plan survives this scrutiny, it is stronger for it. If not, veto.

这是 REVIEWER 的**压力测试方法**。假设计划注定失败，找失败点——如果找到 3 个关键失败点且 PLANNER 都没防，封驳。

这个机制特别能防"过度乐观偏差"——PLANNER 可能从"能做成"的视角规划，REVIEWER 强制切换到"会失败"的视角审视。

## 封驳的实战例子

### 例子 1 · 维度缺失

```
用户：要不要搬去东京。
PLANNER 规划：finance + execution + governance（3 维度）
REVIEWER 审：
  ❌ 没有 people（家庭意见？当地人脉？）
  ❌ 没有 infra（住房？气候？孩子上学？）
  ❌ 没有 growth（日语？文化适应？）

🚫 Veto
- Failed dimension: 域选择严重不足
- Core problem: "搬家"是全维度决策，不能只考虑钱和行动
- Revision direction: 至少加 people / infra / growth 三个领域
- Missing information: 无
```

PLANNER 重写 v2 加 6 维度，Approved。

### 例子 2 · 情感敷衍

```
用户：该不该辞职。
PLANNER v1：
  [列出财务、执行、法律、人脉四维度]
  情感维度：建议用户自行考虑
  
REVIEWER 审：
🚫 Veto
- Failed dimension: 情感维度
- Core problem: "辞职"是高情感权重决策，PLANNER 不能让渡情感判断给用户本人
- Revision direction: 情感维度必须指派给 people（关系影响）和 infra（情绪健康），给出 10/10/10 Regret Test
- Missing information: 无
```

PLANNER 重写 v2 补上情感维度具体分析路径，Approved。

### 例子 3 · SOUL 冲突未识别

```
用户：要不要接这个大项目。
PLANNER 规划：没有考虑 SOUL.md 里"家庭优先于事业"的 0.82 置信度维度

REVIEWER 审：
🚫 Veto
- Failed dimension: SOUL 对齐
- Core problem: 决策直接影响 core 核心维度（家庭优先于事业 0.82），但 PLANNER 没识别
- Revision direction: 加一维"家庭时间影响评估"，指派 people
- Missing information: 用户这个项目预期要多少周末时间？
```

PLANNER 重写 v2 加维度 + 让 ROUTER 补问用户时间问题。

### 例子 4 · 第 2 次封驳后强制 Conditionally Approved

```
v1 规划 → Veto（维度不全）
v2 规划 → Veto（Red Team 找到漏洞：如果合同条款变，整套规划废）

第 3 次 REVIEWER 不能再 Veto（限制）。做法：
v3 规划 → ⚠️ Conditionally Approved
Conditions:
1. execution 必须加一维"合同条款变更应急预案"
2. 领域终审时重点验证
```

## 读奏折时怎么看封驳信号

奏折的 Audit Log 会写：

```
- REVIEWER round 1: Conditionally Approved (condition: include 10/10/10)
```

或者：

```
- REVIEWER round 1: Veto → PLANNER revision
- REVIEWER round 2: Approved
```

**有过封驳是好事**。说明 REVIEWER 真的在审核，没走过场。运营报告里的 `Vetoes: N` 是流程健康度指标——长期 `Vetoes: 0` 可能说明 REVIEWER 失职。

## 反模式 · REVIEWER 不要做什么

`pro/agents/reviewer.md` anti-patterns：

1. **每次都 Approve** — 就该封驳时要封驳
2. **用"建议用户自己考虑"糊弄情感维度** — 要给判断
3. **只因为报告长就认为高质量** — 长≠好
4. **报告里说"风险显著"但给 7/10 分不标记** — 必须标记这种不一致

## 封驳之外：REVIEWER 的其他硬责任

- **Wiki Consistency Check**：新结论如果和高置信度 wiki 条目矛盾，flag 出来
- **Strategic Map Consistency**：决策会打断流图（flows_to / flows_from）的话，flag 出来
- **SOUL × Strategy Alignment**：战略线的 driving_force 和 SOUL 维度冲突的话，flag 出来

这些 flag 不直接封驳，但会出现在奏折里，让用户看到。

## 总结 · 封驳机制的核心价值

- 封驳是系统的**质量保障机制**，不是烦人的拖延
- 最多 2 次循环，保护 token 和时间
- Conditionally Approved 是妥协方案，让不完美的地方成为可追踪条件
- REVIEWER 的独立性来自信息隔离——只看规划/报告，不看其他角色思考
- Red Team + SOUL 对齐 + 情感审查共同构成 REVIEWER 的判断基础

没有封驳的决策引擎不叫决策引擎，叫意见生成器。
