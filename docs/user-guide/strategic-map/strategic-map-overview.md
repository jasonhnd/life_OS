# Strategic Map 概览

## Strategic Map 是什么

Strategic Map 是项目之间的**关系层**——记录多个项目如何分组、流动、相互影响。它让 Life OS 不止能在"项目粒度"推理，还能在"组合粒度"（portfolio level）推理。

传统项目管理工具擅长管单个项目：进度、任务、截止日期。但生活不是一个项目——它是很多项目同时进行，互相影响。Strategic Map 解决的就是这个：

- 项目 A 完成了，项目 B 才能开始
- 项目 A 的结论，要传给项目 B 做前提
- 项目 A 的资源挪过去，项目 B 就慢了
- 项目 A 建立的关系资本，项目 B 可以继承

看不见这些关系，你就只能看见一堆散点，看不见图。

## 两层架构（Structural + Dynamic）

Strategic Map 是两层叠加：

### 结构层（Structural · 用户定义、慢变化）

- **存储位置**：`_meta/strategic-lines.md` + `projects/{project}/index.md` 的 `strategic:` frontmatter
- **变化频率**：每次新项目加入或战略重组时才动
- **来源**：用户明确定义（可以由 DREAM 或对话触发）
- **内容**：
  - 有哪些战略线（strategic lines）
  - 每条线的 purpose / driving_force / health_signals
  - 每个项目属于哪条线、扮演什么角色
  - 项目之间定义的 flow（cognition / resource / decision / trust）

### 动态层（Dynamic · 系统计算、每次刷新）

- **存储位置**：`_meta/STRATEGIC-MAP.md`（**编译产物，绝对不可手改**）
- **刷新时机**：每次 start / 上朝 / begin 时 RETROSPECTIVE 在 Step 15 重新编译
- **来源**：读取结构层 + 项目状态 + 时间 → 算出
- **内容**：
  - 每条战略线的健康原型（6 种之一）
  - 叙事评估（what's happening + what it means + action implication）
  - 盲点检测（broken flow / 未归属项目 / SOUL 与策略不一致等）
  - 今日建议（🥇 最高杠杆 / 🥈 值得关注 / 🟢 可忽略 / ❓ 待决策）
  - Flow graph（完整流图）

两层分开的原因：结构慢变化、动态快刷新。如果混在一起，每次 session 都得重新问用户"这个项目属于哪条线"——无法使用。分开之后，用户只在结构真正改变时才被打扰。

## 从零成长

Strategic Map 不是一次性设定完的——它**随使用增长**。

- **Day 0**：`_meta/strategic-lines.md` 不存在 → Strategic Map 功能休眠。RETROSPECTIVE 静默跳过编译。简报 fallback 到扁平的 Area Status。
- **Day N**：用户说"把项目关联起来"，或 DREAM 在第 3+ 次 session 后提议"你有 N 个活跃项目但没定义关系" → 用户进入首次设置。
- **Day N+1**：第一次 Strategic Map 编译 → 简报顶部出现 🗺️ Strategic Overview。

这是有意的。系统不会一开始就问你 20 个 onboarding 问题——那会让人放弃。它等你自然产生"这些项目到底怎么联系"的感觉，再介入。

首次设置流程：

```
1. 用户（或 DREAM）触发"let's map my projects"
2. ROUTER 引导对话：
   - "哪些项目在服务同一个目的？"
   - "它们之间有什么在流动？"
   - "真正驱动你的是什么？"
3. ARCHIVER 写入 strategic-lines.md + index-delta.md 里的 strategic 字段
4. RETROSPECTIVE 根据 driving_force 提议 health_signals → 用户确认
5. 下次 start → 第一次 STRATEGIC-MAP 编译
```

## 三条硬规则

### 规则 1：STRATEGIC-MAP.md 是编译产物 · 禁止手改

这个文件是 RETROSPECTIVE 每次 session start 时 Step 15 编译出来的。你手动改它没有意义——下次 session start 就被覆盖。

如果你想改 Strategic Map，改**源**：

- 改战略线的 purpose / driving_force / health_signals → 编辑 `_meta/strategic-lines.md`
- 改项目的 role / flows_to / flows_from → 编辑 `projects/{project}/index.md` 的 `strategic:` 字段
- 删除一个战略线 → 从 `_meta/strategic-lines.md` 删除对应 YAML 块

### 规则 2：Structural changes 需要用户确认

DREAM 或 REVIEWER 可能**提议**新的战略线、新的 flow、新的角色分配——但不会自动写进结构层。类似 SOUL/wiki 候选，用户在下次 session 看到提议，确认后再生效。

这保证了用户对结构层有完全控制——结构是用户的意图表达，不是 AI 的猜测。

### 规则 3：叙事评估，不用分数

Strategic Map 不输出"项目健康度 7.3 分"这种东西。它用 **6 种健康原型**（详见 `health-archetypes.md`）做模式匹配，然后写一段叙事：

```
🟡 Market Expansion Pipeline        [Controlled wait]
   Window: 2026-09-30 (24 周剩余) | Driving: first-mover advantage

   project-alpha   critical-path   🟡 on-hold (legal review)
   project-beta    enabler         🟢 active

   Narrative:
     alpha 在等法务，不是失控；beta 可以在等待期推进。
     如果 alpha 6 周后还没 unblock，整条线会滑出窗口。

   → Action implication: 这周主要精力在 beta；留一天跟法务的预期。
```

为什么不用分数？因为分数**骗人**。一个"8 分"的项目可能是"8 分稳定"也可能是"8 分高风险高回报"，完全不同。叙事能承载这种歧义，数字不能。

## 认知科学基础

Strategic Map 不是随便设计的——它基于三条已经被研究过的认知模型：

- **Goal Systems Theory** (Kruglanski 2002)：人同时追多个目标，这些目标构成一个网络。每个目标有"形式原因"和"真实驱动力"，常常不一致。→ 这就是为什么有 `purpose` 和 `driving_force` 两个字段。
- **Recognition-Primed Decision** (Klein 1998)：专家不算权重平均，他们用"模式识别"对照经验库。→ 这就是为什么用健康原型而不是分数。
- **Predictive Coding** (Friston 2005) + **Absence Neglect** (Kahneman)：最危险的认知失败不是看错，而是**没注意到缺失的东西**。→ 这就是为什么有盲点检测（详见 `blind-spot-detection.md`）。
- **Expected Value of Control** (Shenhav, Botvinick & Cohen 2013)：大脑在分配注意力时，算的不只是"重要性"，而是"重要性 × 可控性 - 机会成本"。→ 这就是为什么 "⚡ Today" 的推荐不是按项目重要性排，而是按 "leverage × effort × cost of inaction" 综合判定。
- **Attention as Suppression** (Desimone & Duncan 1995)：注意力主要是通过**抑制无关信号**来工作的，不是通过"增强相关信号"。→ 这就是为什么有 "🟢 Safe to ignore"——系统主动告诉你"今天这些不需要看"，让你把认知带宽省给 🥇。

## 什么时候不需要 Strategic Map

如果你只在管 **1 个项目**——Strategic Map 没意义。单项目没有"关系层"可言。继续用扁平的 Area Status 就行。

如果你管 **2-3 个项目，互不相关**——也不需要。每个独立跑，用 `strategic.independent: true` 标记即可。

Strategic Map 真正产生价值的场景：
- 3+ 个项目 + 至少 2 个项目之间有依赖或共享目的
- 存在 deadline 管理（time_window）
- 存在跨项目知识复用（cognition flow）
- 存在决策的跨项目影响（decision flow）

在达到这个复杂度之前，**系统会沉默**——这是设计。过早引入 Strategic Map 会让用户被结构性问题压垮，而不是从中获益。

## 常见误解

**误解 1**：Strategic Map 是"高级功能"，要先配完整个系统才能用。
→ 不是。它是增量增长的。你可以今天只定义一条战略线、只管 2 个项目——系统仍然工作。

**误解 2**：定义一条战略线后，我就得把所有项目都归到某条线下。
→ 不必。Unaffiliated 项目是正常的。系统会在 "📌 Unaffiliated" 里显示，你可以忽略或归档。不归属 ≠ 错误。

**误解 3**：Strategic Map 会限制我的灵活性，锁死战略方向。
→ 相反。它让你每次看清自己的战略选择。想变方向？改 strategic-lines.md 的 purpose 或 driving_force，下次 session 重新编译。

**误解 4**：我要先想清楚再定义。
→ 想不清楚才是正常的。先定义一个粗糙的版本，跑 2 周，看简报给你的叙事是否准确——不准确就改 driving_force 或 health_signals。它是**对话工具**，不是**规划文档**。

## 相关文件

- `references/strategic-map-spec.md`——权威 spec
- `pro/agents/retrospective.md`——Step 15 编译逻辑
- `docs/user-guide/strategic-map/strategic-lines.md`——怎么写第一条战略线
- `docs/user-guide/strategic-map/project-roles.md`——四种项目角色
- `docs/user-guide/strategic-map/health-archetypes.md`——6 种健康原型
- `docs/user-guide/strategic-map/blind-spot-detection.md`——5 类盲点
- `docs/user-guide/strategic-map/cross-layer-integration.md`——与 SOUL/Wiki/DREAM 的集成
