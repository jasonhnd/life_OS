# 盲点检测（Blind Spot Detection）

基于 **Predictive Coding** (Friston 2005) 和 Kahneman 的 **Absence Neglect** 研究：最危险的认知失败不是看错东西，而是**没注意到缺失的东西**。

健康原型（health-archetypes.md）告诉你"在图上的东西是什么状态"。盲点检测告诉你"图上应该有但没有的东西是什么"。

## 5 类盲点

### 1. 无归属项目（Undefined relationships）

**是什么**：在 `projects/` 下存在，但没有任何 `strategic.line` 字段的项目。

**怎么检测**：
- RETROSPECTIVE Step 15f 扫描所有 `projects/*/index.md`
- 找出 `strategic:` frontmatter 缺失或 `line: null` 的项目
- 放到 "📌 Unaffiliated" 区域

**晨报里怎么显示**：

```
📌 Unaffiliated
   project-x — active, high priority
   → 这是疏忽还是故意独立？
```

**含义**：每个"我在投入的项目"都应该要么属于某条战略线，要么明确标为独立项目。如果你不知道它属于哪——可能是战略线定义得不够清楚，也可能是这个项目不该存在。

**用户的选择**：
- 加到某条战略线 → 编辑该项目 index.md 的 `strategic.line`
- 明确标为独立 → 加上 `strategic: { independent: true }`（简报会把它移到 "Intentionally Independent" 区）
- 或者决定归档掉

**为什么这是盲点**：Unaffiliated 项目往往在消耗时间和精力却没给任何战略线贡献——而你每周还在"更新它的进度"。看见它，才能决定。

---

### 2. 断流（Broken flows）

**是什么**：`flows_to` / `flows_from` 定义了，但实际上知识/资源/决策没在流动。

**怎么检测**：

对每条 flow 定义（A →(type)→ B）：

- **cognition 流**：检查 B 项目的最近 5 个 decisions 有没有引用过 A 所属 domain 的 wiki 条目
  - 如果 0 次引用 → 断流
- **resource 流**：检查 B 的 task 描述或 decision 是否提到 A 的交付物
  - 如果提到的交付物状态是 stale / 过期 → 断流
- **decision 流**：检查 A 的最新 decision 和 B 的最新 index.md 的前提是否一致
  - 如果 A 改了重要 decision 但 B 的前提没 update → 断流
- **trust 流**：检查 A 项目最近 60 天是否有关系维护活动
  - 如果长期无活动 → trust 在蒸发

**晨报里怎么显示**：

```
🕳️ Blind Spots
   · cognition 断流: project-alpha → project-beta
     - alpha 在 wiki 里发布了 3 条合规方法论
     - beta 最近 5 个 decision 里 0 次引用
     - 含义：beta 可能在重推导 alpha 已经解决的东西
   · decision 断流: project-alpha → project-delta
     - alpha 上周改了 "只进中国市场" 的决策
     - delta 的 index.md 前提还是"全球发行"
     - 建议：立刻同步
```

**含义**：flow 定义是"意图"——实际在流才是"事实"。意图没兑现就是浪费。

**用户的选择**：
- cognition 断流：在 next session 的决策里引用 wiki / 或者删除 flow（如果其实不需要）
- resource 断流：check 下游是否还需要那个交付物
- decision 断流：立刻同步下游 / 通知相关决策者
- trust 断流：做一次关系维护

**为什么这是盲点**：flow 定义了之后会被认为"在运作"——但定义不等于运作。需要主动检查。

---

### 3. driving-force 被忽视（Driving force neglect）

**是什么**：你的行为（最近 3-7 天的决策/任务）和你声明的 driving_force 不一致。

**怎么检测**：

- ADVISOR 在每次 Draft-Review-Execute 之后检查（retrospective 不做这个，ADVISOR 做）
- 最近决策与 driving_force 维度交叉比对
- DREAM 的 #2 触发器（behavior-mismatch-driving-force）也监控这个，阈值：≥2 个最近 decision 与 driving_force 矛盾

**晨报里怎么显示**：

```
🕳️ Blind Spots
   · driving_force neglect: "Market Expansion Pipeline"
     - 你说 driving_force 是 "抢先占据市场"
     - 最近 3 天 5 个决策，0 个是关于时间窗/竞品动态，5 个是关于产品细节打磨
     - 含义：你可能在用"精致"替代"速度"
```

**含义**：driving_force 是你投入这条线的真实原因。如果行为和它不一致，早晚会发生以下之一——
- 你放弃这条线（因为底层动力没被满足）
- driving_force 其实在变化（需要更新）
- 你在逃避（把精力投向容易的地方，回避真正该做的）

**用户的选择**：
- 下一个决策对齐 driving_force
- 或者承认 driving_force 在变——更新 `_meta/strategic-lines.md`
- 或者承认这条线其实该降级/终止

**为什么这是盲点**：行为一次不一致不明显；累积 5 次你自己都看不见。系统的价值就是"机械地数"。

---

### 4. 维度缺口（Dimension gaps）

**是什么**：某个生活维度在所有战略线里都缺席。

**怎么检测**：

- DREAM REM 的 3 天扫描
- 读所有战略线的 `area` 字段
- 读所有项目的 `domain` 或 `area`
- 对比 "典型生活维度"（health / relationships / learning / finance / career / creative 等，来自 areas/ 目录）
- 找出完全没有战略线覆盖的维度

**晨报里怎么显示**：

```
🕳️ Blind Spots
   · dimension gap: Health 维度 0 条战略线
     - 3 条活跃战略线都在 career 相关维度
     - Health areas 有 2 个 active projects，但都 unaffiliated
     - 含义：你的战略精力全部在事业上，Health 只是在"维持"，不在"战略推进"
```

**含义**：不是每个维度都需要战略线——但如果一个维度长期无战略线，要么是它已经稳定（不需要特别关注），要么是它在被系统性忽视。

**用户的选择**：
- 如果维度稳定（比如健康状况很好）→ 接受盲点标记，不做动作
- 如果维度被忽视 → 考虑加一条战略线

**为什么这是盲点**：人的关注会自然向"最近投入最多的地方"集中，其他维度会静悄悄萎缩。系统是中立的观察者。

---

### 5. 临近 deadline 无准备（Approaching time windows）

**是什么**：战略线的 `time_window` 正在逼近，但 critical-path 项目没在推进。

**怎么检测**：

- RETROSPECTIVE Step 15d 编译每条线时检查
- 计算 time_window - today = 剩余周数
- 如果 < 4 周 → warning
- 如果 < 2 周 且 critical-path 项目 on-hold → alert
- EXECUTION 域（六领域之一）在做决策评估时也会检查这个

**晨报里怎么显示**：

```
🕳️ Blind Spots
   · approaching deadline without preparation: Market Expansion Pipeline
     - time_window: 2026-05-10 (2 周剩余)
     - critical-path project-alpha: on-hold (等法务)
     - status_reason 预计窗口是 "月底"（5-01）—— 如果按预期解锁，还有 9 天可用
     - 风险：如果法务拖到 5-10 之后，整条线失败
     - 建议：立刻跟法务确认时间表 / 或准备 plan B
```

**含义**：deadline 是可预测的——不该在最后一周才发现"时间不够了"。

**用户的选择**：
- 立刻和 blocker 确认时间表
- 启动 insurance 项目（如果有）
- 重新谈判 deadline
- 或者承认会 miss，及时通知相关方

**为什么这是盲点**：time_window 写进去之后，人会假设"到时候总会搞定"——直到最后一周才发现不会。

---

## 在晨报里怎么显示

所有盲点统一出现在 `_meta/STRATEGIC-MAP.md` 的 **🕳️ Blind Spots** 区域，位于每条战略线的叙事之后、"⚡ Today" 之前。

简报结构：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗺️ Strategic Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[emoji] [line-name]                    [archetype]
   [details...]

📌 Unaffiliated
   [无归属项目]

🕳️ Blind Spots                  ← 盲点检测结果
   · [断流]
   · [driving-force 忽视]
   · [维度缺口]
   · [临近 deadline]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Today
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 [最高杠杆]
🥈 [值得关注]
🟢 Safe to ignore
❓ Decisions needed
```

盲点数量：每次编译通常 0-5 个。如果 >5，说明结构本身需要重新整理。

盲点和决策建议的关系：盲点描述"什么不对"，🥇/🥈 描述"今天做什么"——盲点会影响 🥇/🥈 的优先级。比如"临近 deadline 无准备"通常会成为 🥇。

---

## 谁在检测

| 盲点类型 | 检测者 | 时机 |
|----------|--------|------|
| 无归属项目 | RETROSPECTIVE | Start Session Step 15f |
| 断流 · cognition | RETROSPECTIVE + REVIEWER | Start Session + 每次决策审议 |
| 断流 · resource | ARCHIVER | 退朝时，在 outbox 注记 |
| 断流 · decision | REVIEWER | 每次决策审议（必须 veto） |
| 断流 · trust | DREAM REM | 3 天扫描 |
| driving-force 忽视 | ADVISOR + DREAM #2 触发器 | 每次决策后 + 3 天扫描 |
| 维度缺口 | DREAM REM | 3 天扫描 |
| 临近 deadline | RETROSPECTIVE + EXECUTION 域 | Start Session + 决策评估 |

盲点检测分布在多个 agent 上——这是有意的。每个 agent 有自己的扫描范围和时机，让盲点从不同角度被发现。

---

## 盲点 vs 健康原型

一条战略线可以：

- 是 🟢 Steady progress（健康原型）
- 同时有 🕳️ 断流（cognition 未实际流动）

两者不冲突。原型看"状态"，盲点看"缺失"。一条线可以推进得很好，但某条定义的 flow 没真的在流——两者都要看。

---

## 相关文件

- `references/strategic-map-spec.md`——Blind Spot Detection 章节
- `pro/agents/retrospective.md`——编译时的盲点扫描
- `docs/user-guide/strategic-map/project-roles.md`——flow 定义（断流的前提）
- `docs/user-guide/strategic-map/cross-layer-integration.md`——盲点在跨层面的体现
- `docs/user-guide/dream/10-auto-triggers.md`——DREAM 的盲点相关触发器（#2、#5、#8）
