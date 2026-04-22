# 战略地图规范（Strategic Map）

战略地图是项目之间的关系层——记录它们如何分组、流动、相互影响。让 Life OS 能够在组合（portfolio）层面推理，而不只是单项目层面。

基于认知科学研究：Goal Systems Theory（Kruglanski 2002）、Recognition-Primed Decision 模型（Klein 1998）、Predictive Coding 框架（Friston 2005）。

## 设计原则

1. **两层架构**：结构层（用户定义、缓变）+ 动态层（系统计算、每次 Start Court 刷新）
2. **单一真相源**：`projects/{project}/index.md` frontmatter 存每项目战略数据；`_meta/strategic-lines.md` 存战略线定义；`_meta/STRATEGIC-MAP.md` 是编译产物（从不手工编辑）
3. **从零生长**：若无战略数据，系统正常运行——功能处于休眠状态，直到用户定义关系
4. **结构变更由用户确认**：新战略线、项目角色、流动关系需要用户确认（类似 SOUL/wiki 候选）
5. **模式匹配 + 叙事评估**：不使用数字评分——匹配健康原型并写出"发生什么 / 意味着什么 / 怎么办"的叙事
6. **跨层整合**：战略地图与 SOUL.md、wiki/、DREAM 作为一个认知系统协同工作

## 数据结构

### 战略线（`_meta/strategic-lines.md`）

存于用户的 second-brain（不在 Life OS repo）。多条战略线用 `---` 分隔。用户首次定义战略分组时创建。

```yaml
---
type: strategic-line
id: "market-expansion"
name: "Market Expansion Pipeline"
purpose: "Build market presence in target segment"
driving_force: "Establish first-mover advantage in target segment before market consolidation"
health_signals:
  - "Key milestones progressing"
  - "Partner onboarding on track"
  - "Legal review turnaround within expected windows"
time_window: 2026-09-30
area: "ventures"
created: 2026-04-15
---
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识（kebab-case） |
| name | string | 是 | 显示名 |
| purpose | text | 是 | 一句话正式目的 |
| driving_force | text | 否 | 真正驱动你投入这条线的动力（可与 purpose 不同） |
| health_signals | text[] | 否 | 哪些信号表明这条线健康（AI 基于 driving_force 提议，用户确认） |
| time_window | date | 否 | 影响整条线的截止日期 |
| area | string | 否 | 关联生活 area |
| created | date | auto | 创建日期 |

#### 关于 `driving_force`

基于 Goal Systems Theory（Kruglanski 2002）和自欺研究（von Hippel & Trivers 2011）：人们追求目标时通常有一个陈述理由和一个更深层的驱动力。`purpose` 是正式定位；`driving_force` 是实际驱动你投入的动力。

- 若 driving_force = purpose，留空（系统视两者相同）
- driving_force 影响哪些 health signals 才重要——由"关系"驱动的线应关注社交活动，而不是代码提交
- ADVISOR 检查你的行为是否与 driving_force（而非仅 purpose）对齐

#### 关于 `health_signals`

- 战略线首次创建时，RETROSPECTIVE 基于 driving_force 提议 health signals
- 用户确认或修改
- 确认后存储，用于后续评估
- DREAM 可能在线演化时提议信号更新

### 每项目战略字段（`projects/{project}/index.md`）

添加到既有 frontmatter。所有字段都是可选的，默认为空/null。

```yaml
strategic:
  line: "market-expansion"
  role: "critical-path"
  flows_to:
    - target: "project-beta"
      type: "cognition"
      description: "Certification results reused"
  flows_from:
    - source: "project-gamma"
      type: "cognition"
      description: "Industry knowledge input"
  last_activity: 2026-04-12
  status_reason: "Waiting for legal review, expected next month"
```

| 字段 | 类型 | 值 | 说明 |
|------|------|---|------|
| strategic.line | string | 引用战略线 id | 这个项目属于哪条战略线 |
| strategic.role | enum | `critical-path` / `enabler` / `accelerator` / `insurance` | 在战略线中的角色 |
| strategic.flows_to[] | array | 对象：{target, type, description} | 流向其他项目 |
| strategic.flows_from[] | array | 对象：{source, type, description} | 来自其他项目 |
| strategic.last_activity | date | ISO 日期 | 最后修改日期（ARCHIVER 自动更新） |
| strategic.status_reason | text | 自由文本 | 项目为何处于当前状态（关键——区分"可控等待" vs "失控停滞"） |

### 角色定义

| 角色 | 含义 | 约束 |
|------|------|------|
| `critical-path` | 此项目停滞，整条线停滞 | 每条线**恰好一个** |
| `enabler` | 必须完成 critical-path 才能继续 | 可多 |
| `accelerator` | 让线更快但不阻塞 | 可多 |
| `insurance` | 主路径失败时降低风险 | 可多 |

### 流动类型定义

| 类型 | 含义 | 被阻塞时的紧迫度 |
|------|------|-----------------|
| `cognition` | 结论或知识指导另一项目的决策 | 中（异步，通过 wiki 条目承载） |
| `resource` | 产物、资产、代码或交付物流向另一项目 | 高（具体依赖） |
| `decision` | 一个决策约束或失效另一项目的选项 | 严重（必须立即同步） |
| `trust` | 一个项目积累的关系资本惠及另一项目 | 低（长期累积） |

## 评估方法

### 健康原型（不是数字评分）

基于 Klein 的 Recognition-Primed Decision 模型：专家通过把情境与经验案例匹配来评估，产生叙事判断——而不是计算加权平均。

| 原型 | 信号 | 含义 |
|------|------|------|
| 🟢 Steady progress | active + 近期活动 + 任务推进 | 无需干预 |
| 🟡 Controlled wait | on-hold + 有 status_reason + 在预期窗口内 | 正常，但监视时间窗 |
| 🟡 Momentum decay | active 但活动下降 + 任务积压 | 可能注意力分散 |
| 🔴 Uncontrolled stall | on-hold + 无 status_reason 或过了预期窗 | 需要干预 |
| 🔴 Direction drift | active 但行为偏离 driving_force | 做错了事 |
| ⚪ Dormant | insurance 角色 + 长期不动 | 预期内，不报警 |

每条战略线的评估流程：
1. 读所有信号（status、activity、tasks、status_reason、driving_force、health_signals）
2. 匹配原型
3. 心理模拟：若继续这样，3 周后这条线会在哪？
4. 写叙事：当前状态 + 意味着什么 + 要警惕什么
5. 标记盲点：哪些信息缺失？

### 衰减阈值

| 角色 | Warn | Alert |
|------|------|-------|
| critical-path | 7 天不动 | 14 天 |
| enabler | 14 天 | 30 天 |
| accelerator | 30 天 | 60 天 |
| insurance | 60 天 | 不报警（预期休眠） |

### 决策传播

当某项目做决策时，检查 flows_to 下游影响：

| 流动类型 | 下游影响 | 严重度 |
|---------|---------|--------|
| `decision` | 下游项目的前提可能失效 | 严重——立即标记 |
| `cognition` | 结论变化影响下游分析 | 中——记为需审查 |
| `resource` | 产物变化影响下游输入 | 中——确认下游仍有所需 |
| `trust` | 关系变化影响下游信任资本 | 低——记为需觉察 |

由以下角色检查：
- **REVIEWER**：审查时（决策前，作为否决标准）
- **ARCHIVER**：Phase 2（决策后，作为 outbox 警告）
- **RETROSPECTIVE**：编译时（上次会话的陈旧警告）

### 盲点检测

基于 Predictive Coding（Friston 2005）和 Kahneman 关于缺失盲点（absence neglect）的研究：最危险的认知失败是没注意到缺少什么。

| 盲点类型 | 检测者 | 时机 |
|---------|--------|------|
| 未定义的关系（项目不在任何线中） | RETROSPECTIVE | Start Court——扫描未归属项目 |
| 驱动力忽视（行为不对齐 driving_force） | ADVISOR | 每次 Draft-Review-Execute 之后 |
| 维度缺口（某生活领域在所有战略线中缺席） | DREAM REM | 3 天扫描——检查生活维度覆盖 |
| 时间窗临近但无准备 | RETROSPECTIVE + EXECUTION 领域 | Start Court 简报 + 执行评估 |
| 破损流动（定义了但实际不流） | REVIEWER + ARCHIVER | 审查——检查 wiki 引用；Adjourn——检查会话材料 |

## 跨层整合

### SOUL × 战略地图

`driving_force` 本质上是"这条战略线服务于 SOUL 的哪部分"。

- 若 SOUL.md 说"家庭 > 事业"（置信度 0.8）但所有战略线都是事业驱动 → 标记为 SOUL-策略错配
- REVIEWER 检查：这个决策的战略线是否与 SOUL 维度对齐？
- DREAM REM 检查：driving force 在时间上是否与 SOUL 保持一致？

### wiki × 战略地图

项目间的 cognition 流动由 wiki 内容承载。

- 若 cognition 流动已定义（A → B）且 A domain 的 wiki 有条目，那些条目就是流动的实质
- RETROSPECTIVE 交叉检查：cognition 流动的 wiki domain 是否有内容？下游项目是否引用？
- "破损流动" = wiki 条目存在但下游项目从未引用

### DREAM × 战略地图

DREAM 是跨三层知识（SOUL/wiki/strategic）的综合引擎。

没有战略地图：DREAM REM 问开放式的"有什么跨项目关联？"
有战略地图：DREAM REM 有脚手架：
- **结构检查**：已定义流动是否仍有效？是否陈旧或破损？
- **SOUL × 策略**：driving force 是否与 SOUL 维度一致？
- **模式 × 策略**：用户行为是否与战略优先级对齐？
- **wiki × 流动**：知识是否真的在项目间传递？
- **超越结构**：战略地图还没捕获的连接？

## 编译输出：`_meta/STRATEGIC-MAP.md`

每次 Start Court 由 RETROSPECTIVE 编译（step 8.5）。从不手工编辑。

### 编译算法

```
1. 读 _meta/strategic-lines.md → 所有线定义
2. 读 projects/*/index.md → 收集战略字段
3. 对每条线：
   a. 收集 strategic.line 匹配的项目，按角色排序
   b. 匹配健康原型（用 status + activity + tasks + status_reason + health_signals）
   c. 写叙事评估
   d. 检测线级盲点
4. 跨层验证：
   a. SOUL × driving_force 对齐
   b. wiki × cognition 流动完整性
   c. user-patterns × 战略优先级
5. 列出未归属项目
6. 从所有 flows_to/flows_from 构建流动图
7. 生成操作建议（leverage 排序 + 可忽略 + 需决策）
8. 写 _meta/STRATEGIC-MAP.md
```

### 输出格式

```markdown
# Strategic Map
compiled: YYYY-MM-DD

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗺️ Strategic Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[emoji] [line-name]                    [archetype indicator]
   Window: [deadline 或 open-ended] ([N weeks remaining])
   Driving: [driving_force]

   [project]   [role]   [status indicator]
   [project]   [role]   [status indicator]

   Narrative:
     [发生什么 + 意味着什么 + 要警惕什么]

   → Action implication: [这对今天意味着什么]


📌 Unaffiliated
   [project] — [status] [priority]
   → Oversight 还是故意独立？

🕳️ Blind Spots
   · [维度缺口]
   · [破损流动]
   · [SOUL-策略错配]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Today
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 [最高 leverage 行动]
   Leverage: [为什么这最重要]
   Effort: [预估时间] | Cost of inaction: [不做会怎样]

🥈 [值得关注]
   Leverage: [为什么]
   Cost of inaction: [会怎样]

🟢 Safe to ignore
   · [project] — [原因]

❓ Decisions needed
   · [用户需回答的结构性问题]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flow Graph
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[project-a] →([flow-type])→ [project-b]
...
```

## 操作建议逻辑

基于 Shenhav, Botvinick & Cohen（2013）：大脑计算"控制的期望价值"——不只是重要性，而是重要性经过努力成本和机会成本加权。

### 最高 leverage 选择

```
1. 是否有战略线时间窗即将关闭（< 4 周）？
   → 该线的未完成工作优先级最高

2. 是否有 critical-path 项目停滞？
   → 等待期间能否推进同线其他项目？
   → 若能 → 推进 enabler/accelerator（利用等待期）

3. 是否有 driving_force 被忽视？
   → 行为模式显示回避某战略优先级 → 标记

4. 以上都没 → 推进最健康线的下一步
   （势头有价值——别浪费好的连胜）
```

### 可安全忽略

主动抑制低优先级项（Desimone & Duncan 1995：注意力主要通过抑制无关信号工作）。

项目可以被安全忽略当：
- 它在 🟢 原型 **且** 不在 critical path
- 它是 insurance 角色 **且** 主路径无失败迹象
- 它在另一条健康的战略线

### 需决策

当系统检测到结构缺口时生成：
- 未归属任何线的项目
- 有流动但无角色的项目
- 无 critical-path 的战略线
- 用户尚未确认的 health_signals

## 冷启动

若 `_meta/strategic-lines.md` 不存在：
- RETROSPECTIVE 静默跳过战略编译
- 简报 fallback 到原本的扁平 Area Status 列表格式
- 3+ 次会话后，若有多个项目，DREAM REM 可能提议："你有 N 个活跃项目但未定义战略关系。想梳理它们如何关联吗？"
- 用户可随时通过告诉 ROUTER 定义关系

首次设置流程：
1. 用户说 "let's map my projects"（或 DREAM 提议）
2. ROUTER 引导对话："哪些项目服务于相同目的？" → "它们之间流动什么？" → "真正驱动你的是什么？"
3. ARCHIVER 写 strategic-lines.md + index-delta.md 带战略字段
4. RETROSPECTIVE 基于 driving_force 提议 health_signals → 用户确认
5. 下次 Start Court → 首次战略地图编译

## 优雅降级

- 无 strategic-lines.md → 完全跳过，fallback 到扁平 Area Status
- strategic-lines.md 存在但无项目有战略字段 → 编译空地图，简报中跳过
- 流动引用的项目已不存在 → 在 Warnings 中标记为陈旧
- 战略线只有一个项目 → 不报错，记为 "single-project line"
- Critical-path 项目变为 done → 标记："线可能需要新 critical-path 指派"
- SOUL.md 不存在 → 跳过 SOUL × 策略对齐检查
- wiki/ 不存在 → 跳过 wiki × 流动验证
