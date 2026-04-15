# 战略地图规格说明

战略地图是项目之间的关系层——记录项目如何分组、流转和相互影响。它使 Life OS 能在投资组合层面思考，而不仅仅是项目层面。

设计基于认知科学研究：Goal Systems Theory (Kruglanski 2002)、Recognition-Primed Decision model (Klein 1998) 和 Predictive Coding framework (Friston 2005)。

## 设计原则

1. **双层架构**：结构层（用户定义，缓慢变化）+ 动态层（系统计算，每次上朝刷新）
2. **唯一真实来源**：`projects/{p}/index.md` frontmatter 存储项目级战略数据；`_meta/strategic-lines.md` 存储战略线定义；`_meta/STRATEGIC-MAP.md` 为编译产出（不可手工编辑）
3. **从零成长**：若不存在战略数据，系统正常运行——该功能处于休眠状态，直到用户定义关系
4. **用户确认结构变更**：新战略线、项目角色和流动关系需要用户确认（类似 SOUL/wiki 候选机制）
5. **模式匹配 + 叙事评估**：不使用数值评分——匹配健康原型并撰写关于正在发生什么、意味着什么、应该做什么的叙事
6. **跨层集成**：战略地图与 SOUL.md、wiki/、DREAM 协同工作，构成统一的认知系统

## 数据结构

### 战略线（`_meta/strategic-lines.md`）

存储在用户的第二大脑中（不在 Life OS 仓库中）。多条战略线以 `---` 分隔。在用户首次定义战略分组时创建。

```yaml
---
type: strategic-line
id: "crypto-compliance"
name: "Crypto Compliance Pipeline"
purpose: "Build regulated crypto service infrastructure"
driving_force: "Establish first-mover advantage in regulated crypto services before market consolidation"
health_signals:
  - "Regulatory filings progressing"
  - "Partner onboarding on track"
  - "Legal review turnaround within expected windows"
time_window: 2026-09-30
area: "ventures"
created: 2026-04-15
---
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识符（kebab-case） |
| name | string | 是 | 显示名称 |
| purpose | text | 是 | 一句话正式目的 |
| driving_force | text | 否 | 真正驱动你对此战略线投入的动力（可能与 purpose 不同） |
| health_signals | text[] | 否 | 哪些信号表明此战略线是健康的（AI 基于 driving_force 提议，用户确认） |
| time_window | date | 否 | 影响整条线的截止日期 |
| area | string | 否 | 关联的生活领域 |
| created | date | 自动 | 创建日期 |

#### 关于 `driving_force`

基于 Goal Systems Theory (Kruglanski 2002) 和自我欺骗研究 (von Hippel & Trivers 2011)：人类常常怀着公开理由和更深层驱动力来追求目标。`purpose` 是正式定位；`driving_force` 是实际驱动你资源分配的因素。

- 若 driving_force = purpose，留空即可（系统视为相同）
- driving_force 影响哪些健康信号重要——由"关系"驱动的战略线应关注社交活动，而非代码提交
- 谏官检查你的行为是否与 driving_force 一致，而不仅仅是 purpose

#### 关于 `health_signals`

- 首次创建战略线时，早朝官基于 driving_force 提议健康信号
- 用户确认或修改
- 确认后的信号被存储并用于后续评估
- DREAM 可在战略线演变时提议信号更新

### 项目级战略字段（`projects/{p}/index.md`）

添加到现有 frontmatter 中。所有字段可选，默认为空/null。

```yaml
strategic:
  line: "crypto-compliance"
  role: "critical-path"
  flows_to:
    - target: "bittrade-jetro"
      type: "cognition"
      description: "Certification results reused"
  flows_from:
    - source: "ndfg"
      type: "cognition"
      description: "Industry knowledge input"
  last_activity: 2026-04-12
  status_reason: "Waiting for legal review, expected mid-May"
```

| 字段 | 类型 | 取值 | 说明 |
|------|------|------|------|
| strategic.line | string | 引用 strategic-line id | 此项目所属的战略线 |
| strategic.role | enum | `critical-path` / `enabler` / `accelerator` / `insurance` | 在战略线中的角色 |
| strategic.flows_to[] | array | 对象：{target, type, description} | 流向其他项目的输出流 |
| strategic.flows_from[] | array | 对象：{source, type, description} | 来自其他项目的输入流 |
| strategic.last_activity | date | ISO 日期 | 最后修改日期（起居郎自动更新） |
| strategic.status_reason | text | 自由文本 | 此项目处于当前状态的原因（区分可控等待与失控停滞的关键） |

### 角色定义

| 角色 | 含义 | 约束 |
|------|------|------|
| `critical-path` | 若此项目停滞，整条线停滞 | 每条线恰好一个 |
| `enabler` | 必须在关键路径推进前完成 | 允许多个 |
| `accelerator` | 加速战略线但非阻塞项 | 允许多个 |
| `insurance` | 在主要方案失败时降低风险 | 允许多个 |

### 流动类型定义

| 类型 | 含义 | 被阻塞时的紧迫度 |
|------|------|-----------------|
| `cognition` | 结论或知识为另一个项目的决策提供信息 | 中等（异步，通过 wiki 条目传递） |
| `resource` | 制品、资产、代码或交付物流向另一个项目 | 高（具体依赖） |
| `decision` | 一个决策约束或使另一个项目的选择失效 | 关键（必须立即同步） |
| `trust` | 在一个项目中建立的关系资本惠及另一个项目 | 低（长期积累） |

## 评估方法

### 健康原型（非数值评分）

基于 Klein 的 Recognition-Primed Decision model：专家通过将情境与经验案例进行模式匹配来评估，生成叙事评估——而非计算加权平均值。

| 原型 | 信号 | 含义 |
|------|------|------|
| 🟢 稳步推进 | active + 近期有活动 + 任务按计划 | 无需干预 |
| 🟡 可控等待 | on-hold + 有 status_reason + 在预期窗口内 | 正常，但监控时间窗口 |
| 🟡 动量衰减 | active 但活动递减 + 任务堆积 | 可能注意力漂移 |
| 🔴 失控停滞 | on-hold + 无 status_reason 或超出预期窗口 | 需要干预 |
| 🔴 方向偏移 | active 但行为与 driving_force 不一致 | 做了错误的事 |
| ⚪ 休眠 | insurance 角色 + 长期不活跃 | 预期中，不令人担忧 |

每条战略线的评估流程：
1. 读取所有信号（status、activity、tasks、status_reason、driving_force、health_signals）
2. 匹配原型
3. 心理模拟：若继续如此，3 周后此战略线将在哪里？
4. 撰写叙事：当前状态 + 意味着什么 + 需要关注什么
5. 标记盲点：缺少什么信息？

### 衰减阈值

| 角色 | 警告 | 告警 |
|------|------|------|
| critical-path | 7 天无活动 | 14 天 |
| enabler | 14 天 | 30 天 |
| accelerator | 30 天 | 60 天 |
| insurance | 60 天 | 无告警（预期休眠） |

### 决策传播

当某项目作出决策时，检查 flows_to 以了解下游影响：

| 流动类型 | 下游影响 | 严重程度 |
|---------|---------|---------|
| `decision` | 下游项目的前提假设可能被推翻 | 关键——立即标记 |
| `cognition` | 变更的结论影响下游分析 | 中等——标记待审查 |
| `resource` | 交付物变更影响下游输入 | 中等——验证下游是否仍有所需 |
| `trust` | 关系变化影响下游信任资本 | 低——标记以知晓 |

由以下角色检查：
- **门下省**：在审议期间（决策前，作为封驳标准）
- **起居郎**：在第二阶段（决策后，作为 outbox 中的警告）
- **早朝官**：在编译期间（来自前序 session 的过时警告）

### 盲点检测

基于 Predictive Coding (Friston 2005) 和 Kahneman 关于缺席忽视的研究：最危险的认知失败不是发现错误，而是没注意到缺失的东西。

| 盲点类型 | 检测者 | 时机 |
|---------|--------|------|
| 未定义关系（未纳入任何战略线的项目） | 早朝官 | 上朝——扫描未关联项目 |
| 驱动力忽视（行为与 driving_force 不一致） | 谏官 | 每次三省六部流程后 |
| 维度缺口（所有战略线中缺失的生活领域） | DREAM REM | 3 天扫描——检查生活维度覆盖 |
| 逼近的时间窗口但无准备 | 早朝官 + 兵部 | 上朝简报 + 执行评估 |
| 断裂的流动（已定义但实际未流通） | 门下省 + 起居郎 | 审议——检查 wiki 引用；退朝——检查 session 材料 |

## 跨层集成

### SOUL x 战略地图

`driving_force` 本质上是"此战略线服务于 SOUL 的哪个部分"。

- 若 SOUL.md 表明"家庭 > 事业"（置信度 0.8），但所有战略线都有事业相关的 driving force → 标记为 SOUL-战略不一致
- 门下省检查：此决策所属战略线是否与 SOUL 维度一致？
- DREAM REM 检查：driving force 是否随时间与 SOUL 保持一致？

### wiki x 战略地图

项目间的认知流通过 wiki 内容承载。

- 若定义了认知流（A → B）且 wiki 中有来自 A 领域的条目，那些条目就是该流的实质内容
- 早朝官交叉检查：认知流的 wiki 领域是否有内容？下游项目是否引用了它？
- "断裂的流" = wiki 条目存在但下游项目从未引用

### DREAM x 战略地图

DREAM 是跨三个知识层的综合引擎。

无战略地图时：DREAM REM 提出开放式的"有跨项目关联吗？"
有战略地图时：DREAM REM 有了脚手架：
- **结构检查**：已定义的流是否仍然有效？是否有过时或断裂的？
- **SOUL x 战略**：driving force 是否与 SOUL 维度一致？
- **模式 x 战略**：用户行为是否与战略优先级一致？
- **wiki x 流动**：知识是否确实在项目之间传递？
- **超越结构**：存在哪些战略地图尚未捕获的关联？

## 编译产出：`_meta/STRATEGIC-MAP.md`

由早朝官在每次上朝时编译（步骤 8.5）。不可手工编辑。

### 编译算法

```
1. 读取 _meta/strategic-lines.md → 所有线定义
2. 读取所有 projects/*/index.md → 收集战略字段
3. 对每条线：
   a. 收集 strategic.line 匹配的项目，按角色排序
   b. 匹配健康原型（使用 status + activity + tasks + status_reason + health_signals）
   c. 撰写叙事评估
   d. 检测线级盲点
4. 跨层验证：
   a. SOUL x driving_force 一致性
   b. wiki x 认知流完整性
   c. 用户模式 x 战略优先级
5. 列出未关联项目
6. 从所有 flows_to/flows_from 构建流动图
7. 生成行动建议（杠杆排序 + 可安全忽略 + 需要决策）
8. 写入 _meta/STRATEGIC-MAP.md
```

### 输出格式

```markdown
# Strategic Map
compiled: YYYY-MM-DD

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗺️ 战略概览
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[emoji] [线名]                    [原型指标]
   Window: [截止日期或开放式] ([剩余 N 周])
   Driving: [driving_force]

   [项目]   [角色]   [状态指标]
   [项目]   [角色]   [状态指标]

   叙事：
     [正在发生什么 + 意味着什么 + 需要关注什么]

   → 行动含义：[这对今天意味着什么]


📌 未关联
   [项目] — [状态] [优先级]
   → 疏忽还是有意独立？

🕳️ 盲点
   · [维度缺口]
   · [断裂的流]
   · [SOUL-战略不一致]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ 今日
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 [最高杠杆行动]
   杠杆：[为什么这最重要]
   精力：[预估时间] | 不行动的代价：[如果不做会怎样]

🥈 [值得关注]
   杠杆：[原因]
   不行动的代价：[会怎样]

🟢 可安全忽略
   · [项目] — [原因]

❓ 需要决策
   · [用户需回答的结构性问题]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
流动图
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[项目-a] →([流动类型])→ [项目-b]
...
```

## 行动建议逻辑

基于 Shenhav, Botvinick & Cohen (2013)：大脑计算"控制的期望价值"——不仅是重要性，而是重要性经精力成本和机会成本加权。

### 最高杠杆选择

```
1. 是否有时间窗口即将关闭（< 4 周）的战略线？
   → 该线的未完成工作获得最高优先级

2. 是否有关键路径项目已停滞？
   → 在等待期间，能否推进该线的其他项目？
   → 若可以 → 推进 enabler/accelerator（利用等待期）

3. 是否有被忽视的 driving_force？
   → 行为模式显示对某战略优先级的回避 → 标记

4. 以上均无 → 推进最健康战略线的下一步
   （动量是有价值的——不要浪费好势头）
```

### 可安全忽略

对低优先级项目的主动抑制（Desimone & Duncan 1995：注意力主要通过抑制无关信号来运作）。

项目在以下情况下可安全忽略：
- 状态良好（🟢 原型）且不在关键路径上
- insurance 角色且主要方案未显示失败迹象
- 处于另一条健康的战略线中

### 需要决策

当系统检测到结构性缺口时生成：
- 未分配到任何战略线的项目
- 有流动但无角色的项目
- 没有 critical-path 项目的战略线
- 用户尚未确认的 health_signals

## 冷启动

若 `_meta/strategic-lines.md` 不存在：
- 早朝官静默跳过战略编译
- 简报退回到原始的领域状态平面列表格式
- 在 3 次以上包含多个项目的 session 后，DREAM REM 可能提议："您有 N 个活跃项目但未定义战略关系。是否想要映射它们之间的关系？"
- 用户可随时通过告诉丞相来定义关系

首次设置流程：
1. 用户说"来映射我的项目"（或 DREAM 提议）
2. 丞相引导对话："哪些项目服务于同一目的？" → "它们之间流动什么？" → "真正驱动你做这件事的是什么？"
3. 起居郎写入 strategic-lines.md + index-delta.md 的战略字段
4. 早朝官基于 driving_force 提议 health_signals → 用户确认
5. 下次上朝 → 首次战略地图编译

## 优雅降级

- 无 strategic-lines.md → 完全跳过，退回到平面领域状态
- strategic-lines.md 存在但无项目有战略字段 → 编译空地图，简报中跳过
- 流引用了不再存在的项目 → 在警告中标记为过时
- 战略线只有一个项目 → 非错误，标注"单项目线"
- 关键路径项目变为完成 → 标记："该线可能需要新的关键路径分配"
- SOUL.md 不存在 → 跳过 SOUL x 战略一致性检查
- wiki/ 不存在 → 跳过 wiki x 流动验证
