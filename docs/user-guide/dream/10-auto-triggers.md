# 10 个自动触发器

DREAM 的 REM 阶段会机械地评估 10 个触发器。每个触发器有**硬阈值**（量化公式）和**软信号**（LLM 定性观察）两种检测模式。

- **Hard mode**：硬阈值达成 → 自动执行，不需要用户确认
- **Soft mode**：硬阈值没达成，但 LLM 检测到定性信号 → 触发并标记 `auditor_review: true`，下次 AUDITOR 审核通过后才生效

所有触发器都受 **24 小时反垃圾抑制**——同一触发器 24 小时内不重复触发（读取上一份 `_meta/journal/*-dream.md` 的 `triggered_actions` 确认）。

所有触发器的结果写进 dream 报告的 `triggered_actions` YAML 块，下次 session start 时由 RETROSPECTIVE 在简报的"💤 DREAM Auto-Triggers"固定位置显示。

---

## 1. new-project-relationship · 新项目关系

**数据源**：`projects/*/index.md` 的 strategic 字段、`_meta/strategic-lines.md`

**硬阈值**：自上次 dream 报告以来，检测到新的跨项目依赖或瓶颈边

**软信号**：最近决策隐式引用另一个项目，但没有正式的 strategic link

**自动动作**：写 STRATEGIC-MAP 候选 + 标记下次简报醒目位置显示

**下次在哪里浮现**：next-start-session 的 DREAM Auto-Triggers 块（项目 A →(cognition)→ 项目 B）

**例子**：你在 project-alpha 的决策里提到"这个结论要告诉 project-beta 的人"，但两个项目之间没有定义 flow。触发器记录一条 cognition 流候选。

---

## 2. behavior-mismatch-driving-force · 行为与 driving_force 不符

**数据源**：最近 3 天的 decisions + SOUL.md driving_force 维度

**硬阈值**：≥2 个最近 decision 与声明的 driving_force 矛盾

**软信号**：用户在执行 driving_force 对齐的路径时表达不适或犹豫

**自动动作**：注入下次 ADVISOR 的 briefing 输入

**下次在哪里浮现**：next-start-session 的 ADVISOR 提醒：「你说 driving_force 是 X，但最近 5 个 session 焦点都在 Y...」

**例子**：SOUL 说 driving_force 是"家庭 > 事业"，但最近 3 天的 5 个决策全部围绕工作——ADVISOR 下次会提问。

---

## 3. wiki-contradicted · Wiki 被新证据反驳

**数据源**：`wiki/**/*.md`、最近的 decisions、新证据笔记

**硬阈值**：≥1 条新证据直接反驳现有 wiki 结论

**软信号**：用户在 wiki 覆盖的话题上，语气从确信转向怀疑

**自动动作**：该 wiki 条目 `challenges: +1`

**下次在哪里浮现**：简报里显示"⚠️ 条目 X 被挑战 N 次，考虑重新审视"

**例子**：wiki 里有"凌晨工作效率最高"的结论，最近 3 天连续出现"凌晨犯错"的 decision → challenges +1。如果 challenges 堆积到超过 evidence，下次 session 会提示用户重审。

---

## 4. soul-dormant-30d · SOUL 维度休眠 30 天

**数据源**：SOUL.md 的 `last_validated` 时间戳

**硬阈值**：维度的 `last_validated` 早于 30 天前，且 `confidence ≥ 0.5`

**软信号**：（无——纯时间判定）

**自动动作**：简报警告（"⚠️ [维度] 30+ 天未激活"）

**下次在哪里浮现**：SOUL Health Report 的 💤 Dormant 区域

**例子**：SOUL 里"创造力"维度 45 天没有新证据——不一定是问题，但值得提醒：这个维度是不是在生活里边缘化了？

---

## 5. cross-project-cognition-unused · 跨项目认知未使用

**数据源**：`wiki/INDEX.md`、跨项目最近 decisions

**硬阈值**：≥1 条 wiki 条目直接适用于最近某个决策，但决策中未引用

**软信号**：用户在重新推导另一个项目的 wiki 中已经确立的结论

**自动动作**：标记给下次 DISPATCHER，强制注入相关 wiki 条目

**下次在哪里浮现**：下次做类似决策时，DISPATCHER 会把相关 wiki 条目作为"已知前提"发给每个领域

**例子**：你在 wiki 里写过"创业早期用户访谈的 5 个极端用户原则"，但昨天在 new-product 项目里又重新推导了一遍——下次再聊 new-product，系统会主动提醒。

---

## 6. decision-fatigue · 决策疲劳

**数据源**：最近 3 天的决策时间戳 + REVIEWER 评分

**硬阈值**：24 小时内 ≥5 个决策，且后半段平均评分 ≤ 前半段 -2

**软信号**：用户在 session 里表达疲惫（"whatever" / "fine" / "随便" / "まあいい"）

**自动动作**：下次简报标记"建议今天不做重大决策"

**下次在哪里浮现**：简报顶部的 ⚠️ Recommendation 块

**例子**：昨天你做了 7 个决策，前 3 个评分 8.0 / 7.5 / 7.2，后 4 个评分 5.0 / 4.3 / 4.0 / 3.8——明显的认知疲劳曲线。今天开 session，第一件事系统提醒你："先缓一天再做重大决策"。

---

## 7. value-drift · 价值漂移

**数据源**：SOUL.md 的 evidence/challenges 历史 + 最近 30 天决策

**硬阈值**：某维度在 30 天内累积 ≥3 条 challenges，但支持证据 ≤1 条

**软信号**：用户对某个价值的 framing 随时间变化（例："安全" → "自由"）

**自动动作**：自动提议 SOUL 维度修订

**下次在哪里浮现**：SOUL Health Report 的 ❗ Conflict zone 区域

**例子**：SOUL 里"稳定优先"这个维度，最近 30 天有 4 个 decision 挑战它（都选了高风险选项），只有 1 个 decision 支持它——系统提议："你可能正在从 stability-first 迁移到 growth-first，要不要更新维度？"

---

## 8. stale-commitment · 陈旧承诺

**数据源**：用户说过"I will X" / "我会 X" / "X する" 的 decisions + 任务完成状态

**硬阈值**：承诺陈述 ≥30 天之前，且无相关任务完成 / 无后续 decision

**软信号**：用户在后续 session 里回避提起该话题

**自动动作**：下次简报唤起（"你说你会 X——后来呢？"）

**下次在哪里浮现**：简报的 🔄 Resurface 块

**例子**：40 天前你说"我会把 blog 重开起来"——没开。DREAM 每 24 小时最多唤起 1 次（反垃圾）。不是催，是镜子。

---

## 9. emotional-decision · 情绪化决策

**数据源**：决策 session journal + 用户表达模式

**硬阈值**：≥2 个最近 decision 在 session 中被标记了强情绪信号

**软信号**：标点增多、回复变短、决策阶段主题快速切换

**自动动作**：下次 REVIEWER 添加强制的"情绪状态检查"维度

**下次在哪里浮现**：下次 REVIEWER 的审议里会多一个维度——「这个决策现在做的情绪状态适合吗？」

**例子**：昨天晚上你在一个 session 里连续做了 3 个决策，ADVISOR 标记"high emotional state"，REVIEWER 建议 cool-off 但决策还是推进了——今天 REVIEWER 会在每个决策上多问一次："冷静下来看还这样想吗？"

---

## 10. repeated-decisions · 重复决策

**数据源**：`_meta/decisions/*.md` + 项目 decisions 历史

**硬阈值**：同一问题/主题在中间没有执行的情况下被决策 ≥3 次

**软信号**：用户重新表述问题以避免识别它是重复

**自动动作**：下次简报提示（"你在决定 X 第 3 次了——在回避承诺吗？"）

**下次在哪里浮现**：简报的 🤔 块

**例子**：
- 3/1：决策"要不要学日语"，选 yes
- 3/15：决策"每周 3 次日语课还是每周 1 次集中 3 小时"，选每周 3 次
- 4/1：决策"要不要暂停日语专注其他项目"

三次决策，中间没有"实际上过课"的执行记录——系统问你："是不是在用决策代替行动？"

---

## `triggered_actions` YAML 块格式

所有触发器的结果写进 dream 报告的 YAML 块：

```yaml
triggered_actions:
  - trigger_id: 6
    trigger_name: "decision-fatigue"
    mode: "hard"          # 或 "soft"
    detection:
      hard_signals:
        - "6 decisions in 18 hours"
        - "avg score 7.5 → 4.2 (Δ=-3.3)"
      soft_signals: []
    action: "flag-next-briefing-no-major-decisions-today"
    surfaces_at: "next-start-session"
    auditor_review: false  # true if mode=soft
```

- `trigger_id` + `trigger_name`：触发器标识
- `mode`：hard（硬阈值自动通过）或 soft（LLM 定性信号）
- `detection`：详细的信号列表
- `action`：自动执行的动作
- `surfaces_at`：下次在哪里显示
- `auditor_review`：soft 模式需要 AUDITOR 审核，hard 模式为 false

---

## 反垃圾抑制

每个触发器都有**同类型 24 小时抑制**。检测方式：读取最新的 `_meta/journal/*-dream.md`，看 `triggered_actions` 里是否在过去 24 小时内已经触发过同一 `trigger_name`。

这防止每天都重复提醒"你 SOUL 的 X 维度 30+ 天休眠"——提醒一次就够，过了 24 小时还没处理再提一次。

---

## 为什么是这 10 个

这 10 个触发器覆盖了三类潜在问题：

- **认知盲点**（1, 3, 5）：系统知道但你没看到
- **价值漂移**（2, 4, 7）：你说的和做的在分叉
- **执行失灵**（6, 8, 9, 10）：决策质量或执行质量下降

它们是**机械的**（纯数据判定），不是"AI 灵感"。硬阈值公式保证不会莫名其妙触发；24 小时抑制保证不会变成噪音。
