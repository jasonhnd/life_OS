# 健康原型（Health Archetypes）

Strategic Map **不用数字评分**。它用 6 种健康原型做模式匹配，输出叙事。

基于 Klein (1998) 的 Recognition-Primed Decision 模型：专家不是算权重平均，他们对照经验里的案例库做模式识别——然后写一段叙事解释"这是什么情况"。

## 为什么不用分数

分数（比如"这条战略线健康度 7.3/10"）看起来专业，但有两个致命问题：

1. **压缩信息太多**：7.3 可能代表"稳定前进"也可能代表"高风险高回报"，完全不同的状态被压成同一个数字
2. **诱导机械执行**：看到 5.8 → 想把它提到 7.0 → 开始做 activity，而不是看清情况

叙事没有这两个问题。它承载歧义，引导思考。

## 6 种原型

### 🟢 Steady progress · 稳步推进

**信号**：
- status: active
- 最近有活动（last_activity 在合理窗口内）
- tasks 按计划推进

**含义**：不需要干预。继续就好。

**叙事模板**：
> "alpha 在稳步推进。本周完成了 X 和 Y，下周计划 Z。没有需要立刻关注的。"

**典型配色**：🟢 绿色

### 🟡 Controlled wait · 可控等待

**信号**：
- status: on-hold
- 有明确的 `status_reason`（说明在等什么）
- 在预期等待窗口内

**含义**：正常的等待状态——不是失控。监控时间窗口即可。

**叙事模板**：
> "alpha 在等法务审核，预计月底回复。这是预期中的等待。关注点：如果 6 周后还没回复，整条线会滑出 time_window。"

**典型配色**：🟡 黄色（需要监控但不紧急）

**关键区别**：controlled wait 和 uncontrolled stall 的唯一区别是 `status_reason`——前者有清晰的"在等什么"，后者没有。

### 🟡 Momentum decay · 动能衰减

**信号**：
- status: active（没正式 on-hold）
- 但最近活动在变少
- tasks 在累积但不完成

**含义**：可能的注意力漂移。没有正式宣布停，但实际上在停。

**叙事模板**：
> "alpha 名义上在推进，但最近两周只完成了 1 个 task，同期新增 3 个。看起来注意力已经移开了——要么正式 on-hold 它，要么重新投入。"

**典型配色**：🟡 黄色（警告）

这是最需要"诚实面对"的原型。项目在偷偷死掉，但没人愿意承认。

### 🔴 Uncontrolled stall · 失控停滞

**信号**：
- status: on-hold
- 没有 `status_reason`，或 status_reason 过期（预期窗口已过）
- 或已过 decay alert 阈值

**含义**：需要介入。要么 unblock，要么承认这个项目死了。

**叙事模板**：
> "alpha 已经 30 天没动，status_reason 是'等合作伙伴回复'——但合作伙伴上次回复是 45 天前。这是 uncontrolled stall。建议：要么今天主动联系确认，要么正式终止这条线。"

**典型配色**：🔴 红色

### 🔴 Direction drift · 方向漂移

**信号**：
- status: active
- 但行为（决策/任务）和 `driving_force` 不一致

**含义**：在做事，但在做错的事。比 stall 更危险——stall 是没做，drift 是在错方向上加速。

**叙事模板**：
> "alpha 很活跃——最近 3 周有 7 个 decision。但驱动力是"first-mover advantage"，而这 7 个决策里有 5 个是关于"完善产品细节"的内向优化，没有"抢时间窗"的动作。你可能在用 motion 代替 progress。"

**典型配色**：🔴 红色

这是 DREAM 的 #2 触发器（behavior-mismatch-driving-force）在监控的核心场景。

### ⚪ Dormant · 休眠

**信号**：
- role: insurance（或其他预期休眠的角色）
- 长期无活动

**含义**：预期的，不报警。insurance 项目的价值是"需要时能启动"，不是"一直在推进"。

**叙事模板**：
> "delta 休眠中（90 天无活动）。作为 insurance 项目，这是预期状态。alpha 健康推进，delta 暂不需要激活。"

**典型配色**：⚪ 灰色（中性）

---

## 如何匹配

匹配流程（RETROSPECTIVE Step 15d 执行）：

```
对每个战略线：
  对每个项目：
    1. 读 signals：status, activity, tasks, status_reason, driving_force, health_signals
    2. 按以下顺序尝试匹配：
       a. insurance role + 长期无活动 → ⚪ Dormant
       b. active + 行为 ≠ driving_force → 🔴 Direction drift
       c. on-hold + (无 status_reason OR 超过预期窗口) → 🔴 Uncontrolled stall
       d. active + 活动在减少 + tasks 在累积 → 🟡 Momentum decay
       e. on-hold + 有 status_reason + 窗口内 → 🟡 Controlled wait
       f. active + 正常推进 → 🟢 Steady progress
    3. 心理模拟（mental simulation）：
       "如果按现在的节奏继续 3 周，这条线会在哪？"
    4. 写叙事：当前状态 + 这意味着什么 + 要监控什么
    5. 检测盲点：缺什么信息？
```

---

## Decay 阈值（按角色区分）

同一个"多少天无活动"对不同角色意味不同：

| Role | Warn | Alert |
|------|------|-------|
| critical-path | 7 天 | 14 天 |
| enabler | 14 天 | 30 天 |
| accelerator | 30 天 | 60 天 |
| insurance | 60 天 | **无 alert** |

critical-path 最敏感——7 天不动就该注意。insurance 角色根本不告警，因为它就是设计来休眠的。

---

## 叙事输出格式

健康原型的输出不是分数，是一段三部分叙事：

```
[emoji] [line-name]                       [archetype 标签]
   Window: [deadline 或 open-ended] ([N 周剩余])
   Driving: [driving_force]

   [project]   [role]        [status 标签]
   [project]   [role]        [status 标签]

   Narrative:
     [当前状态描述] + [这意味着什么] + [要监控什么]

   → Action implication: [今天该做什么]
```

### 例子 1：Steady progress

```
🟢 Industry Relationships                  [Steady progress]
   Window: open-ended | Driving: trusted allies circle

   project-meetups      critical-path   🟢 active
   project-podcast      accelerator     🟢 active

   Narrative:
     meetups 本月已见 5 个关键人，podcast 已上架 3 期，都在计划节奏上。
     关系网在稳步扩大，没有失衡信号。

   → Action implication: 不需要调整。保持节奏。
```

### 例子 2：Controlled wait

```
🟡 Market Expansion Pipeline               [Controlled wait]
   Window: 2026-09-30 (24 周剩余) | Driving: first-mover advantage

   project-alpha        critical-path   🟡 on-hold (legal review)
   project-beta         enabler         🟢 active

   Narrative:
     alpha 在等法务，预计 4 周回复——这是预期窗口内。
     beta 可以在等待期继续推进——利用等待期。
     监控点：如果 alpha 6 周后还没 unblock，整条线会滑出 time_window。

   → Action implication: 本周主要精力在 beta；留一次跟法务的 check-in。
```

### 例子 3：Momentum decay

```
🟡 Health & Fitness                        [Momentum decay]
   Window: open-ended | Driving: long-term vitality

   project-gym          critical-path   🟡 active (decay)
   project-diet         enabler         🟢 active

   Narrative:
     gym 名义上在推进——但最近 14 天只完成了 2 次训练（目标每周 3 次）。
     同期 diet 推进正常。gym 在偷偷衰减。

   → Action implication: 今天去一次，或者正式宣布 "缩减到每周 2 次" 把期望重置。
                        继续假装每周 3 次会让整条线慢慢失去信号价值。
```

### 例子 4：Uncontrolled stall

```
🔴 Writing Book                            [Uncontrolled stall]
   Window: 2026-12-31 (36 周剩余) | Driving: prove I can finish something

   project-manuscript   critical-path   🔴 on-hold (45 天无活动)

   Narrative:
     manuscript 标记 on-hold，status_reason 是 "等灵感"——这不是有效的 reason，
     已经 45 天。driving_force 是 "prove I can finish"——这条线失败会伤到 SOUL
     的相关维度。

   → Action implication: 今天决定：要么设一个强制 output（比如"本周写 500 字 raw"），
                        要么正式关闭这条战略线，避免它持续污染你的"我能完成事情"的信念。
```

### 例子 5：Direction drift

```
🔴 Startup X                               [Direction drift]
   Window: 2026-06-30 (10 周剩余) | Driving: validate product-market fit

   project-mvp          critical-path   🔴 drift
   project-branding     accelerator     🟢 active

   Narrative:
     mvp 很活跃——最近 3 周有 12 个 decision。但 driving_force 是 "validate PMF"，
     这 12 个决策里只有 2 个是关于用户访谈或数据——其余都是产品打磨。
     离 time_window 10 周，你在做 "舒适的细节"，不是"痛苦的 validate"。

   → Action implication: 下一个决策强制关于用户——约谈 5 个潜在用户，或者做一次 pricing test。
                        branding 可以暂停。
```

---

## 心理模拟（mental simulation）

每个原型的叙事里都隐含一个问题：**如果继续这样 3 周，会怎样？**

这是 Klein 模型里的关键一步——专家的判断不止基于现状，还基于"如果不变，未来是什么"。

系统在编译叙事时会做这个模拟：

- Steady progress → 3 周后：完成下一个阶段
- Controlled wait → 3 周后：如果还在等，开始逼近窗口外沿
- Momentum decay → 3 周后：可能正式 stall（或 self-aware 重新投入）
- Uncontrolled stall → 3 周后：基本死了
- Direction drift → 3 周后：窗口丢了，但项目名义上还在
- Dormant → 3 周后：仍休眠，无变化

模拟结果体现在 "what it means" 和 "→ Action implication" 里。

---

## 何时原型会切换

- Steady → Momentum decay：连续 2 周活动低于基线
- Momentum decay → Uncontrolled stall：4 周以上无活动且无 status_reason
- Controlled wait → Uncontrolled stall：超过 status_reason 声明的窗口
- Any → Direction drift：决策和 driving_force 不一致信号累积

切换不是算法判定的——是每次编译时重新匹配的结果。如果你觉得切换过早/过晚，检查 signals 是否还准确（driving_force 可能需要更新，health_signals 可能需要调整）。

---

## 相关文件

- `references/strategic-map-spec.md`——Health Archetypes 表（第 120 行附近）
- `pro/agents/retrospective.md`——Step 15d 匹配逻辑
- `docs/user-guide/strategic-map/project-roles.md`——decay 阈值按 role
- `docs/user-guide/strategic-map/blind-spot-detection.md`——什么时候原型本身也不够（需要盲点检测补充）
