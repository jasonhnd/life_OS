# 画出你的战略地图

当你有 3 个以上项目在同时推进，**项目之间的关系**比项目本身更重要。Strategic Map 就是用来管这层关系的。

本文告诉你：什么时候需要战略地图、怎么定义第一条战略线、怎么给项目分配角色、地图成型后简报怎么变化。

---

## 不是每个人都需要

**不需要战略地图的情况**：
- 只有 1 个主项目
- 项目之间没有依赖关系
- 你只是想记录而不想统筹

这些场景用默认的项目列表就够了。系统会正常工作。

**需要战略地图的情况**：
- 你有多个项目（≥3）且它们互相影响
- 你感觉 "我在同时推进 A B C 但总有一个被拖住了" 
- 你想知道 "我今天应该做什么" 而不是自己排优先级

---

## 从零到第一条战略线

### Step 1 · 识别你的战略意图

Strategic line 的核心是 **driving force**——你真正想推进的力量，不是项目本身。

**反例**（太项目化）："发布 Life OS v2.0"
**正例**（driving force）："在 personal decision engine 这个赛道建立早期用户心智"

问自己：**我最近 6 个月最想推进的是什么？不是哪个项目做完，是哪个方向向前？**

### Step 2 · 列出属于这条线的项目

例子——你想推进 "Life OS 市场占位"。可能涉及：
- `projects/life-os` (产品代码)
- `projects/docs-site` (文档站)
- `projects/content-marketing` (内容营销)
- `projects/user-research` (用户访谈)

这 4 个都在 **product-expansion** 这条线上。

### Step 3 · 给每个项目分配角色

四种角色，一条线**只能有一个 critical-path**：

| Role | 含义 | 约束 |
|------|------|------|
| `critical-path` | 这个停了整条线就停 | 每条线 **恰好 1 个** |
| `enabler` | 必须先完成才能解锁 critical-path | 可多个 |
| `accelerator` | 加速但不阻塞 | 可多个 |
| `insurance` | 降低主路径失败的风险 | 可多个 |

真实分配：

```
product-expansion 线:
  - life-os          → critical-path  (代码不动一切白搭)
  - docs-site        → enabler        (没文档用户进不来)
  - content-marketing → accelerator    (加速获客，不阻塞)
  - user-research    → insurance      (如果产品方向错了，访谈能早点发现)
```

### Step 4 · 定义 flows（可选但推荐）

项目之间怎么流动？四种 flow 类型：

| Type | 含义 | 例子 |
|------|------|------|
| `cognition` | 知识/结论流转 | user-research 的洞察 → life-os 的产品决策 |
| `resource` | 产出/资产流转 | life-os 的 CHANGELOG → docs-site 的发布页 |
| `decision` | 决策约束 | life-os 决定不做 Telegram → content-marketing 不宣传 Telegram |
| `trust` | 关系资本 | user-research 建立的用户关系 → 后期推荐测试 |

定义方式（写在各项目 `index.md` 的 frontmatter 里）：

```yaml
# projects/user-research/index.md
strategic:
  line: "product-expansion"
  role: "insurance"
  flows_to:
    - target: "life-os"
      type: "cognition"
      description: "用户洞察指导产品方向"
    - target: "content-marketing"
      type: "cognition"  
      description: "用户语言提供 copy 素材"
  flows_from:
    - source: "life-os"
      type: "decision"
      description: "产品决策限定访谈范围"
  last_activity: 2026-04-18
  status_reason: "正在访谈第 5 批用户，预计 5 月底结束"
```

---

## 定义第一条战略线（对话示例）

你说：

```
我想定义一条战略线，关于 Life OS 的市场推广
```

丞相引导（这是一个 strategic setup 流程）：

```
🏛️ 丞相

好，我们定义一条 strategic line。四个问题：

1. **Name**: 你想怎么叫这条线？（会作为 id 和 display name）
2. **Purpose**: 一句话官方目的
3. **Driving force**: 真正驱动你的是什么？（可以和 purpose 不同）
4. **Time window**: 有 deadline 吗？（可选）
```

你：
```
1. product-expansion
2. 让 Life OS 成为个人决策引擎领域的早期标准
3. 我想证明 "AI 不是取代人做决定，而是让人做更好的决定" 这件事
4. 2027 年初
```

丞相：
```
🏛️ 丞相

3 点关键差异：
- Purpose 是"占领标准"（市场导向）
- Driving force 是"证明观点"（理念导向）

这两个不完全一致——当市场压力出现时（比如有人用更激进
的方式做得更快），你会倾向哪边？这会决定你的 health signals。
```

你：`理念优先`

```
🏛️ 丞相

记下了。基于这个 driving force，我建议的 health signals：

- "Active user 的决策质量指标改善"（而非 只看 user 数量）
- "SOUL/Wiki 系统被用户主动使用"（而非 DAU）
- "用户反馈中出现 '帮我更好地做决定' 的表达"（而非 '好用'）

这些对吗？要改吗？
```

你：`加一条 "用户在决策流程中表现出自主性增强，而非依赖系统"`

```
🏛️ 丞相

记下了。最终版：

📜 Strategic Line Draft
id: product-expansion
name: "产品市场占位"
purpose: "让 Life OS 成为个人决策引擎领域的早期标准"
driving_force: "证明 AI 不是取代人做决定，而是让人做更好的决定"
health_signals:
  - "活跃用户的决策质量指标改善"
  - "SOUL/Wiki 系统被用户主动使用"
  - "用户反馈中出现'帮我更好地做决定'表达"
  - "用户在决策流程中表现出自主性增强"
time_window: 2027-01-01

确认？写到 _meta/strategic-lines.md
```

你：`确认`

文件写入：

```yaml
---
type: strategic-line
id: "product-expansion"
name: "产品市场占位"
purpose: "让 Life OS 成为个人决策引擎领域的早期标准"
driving_force: "证明 AI 不是取代人做决定，而是让人做更好的决定"
health_signals:
  - "活跃用户的决策质量指标改善"
  - "SOUL/Wiki 系统被用户主动使用"
  - "用户反馈中出现'帮我更好地做决定'表达"
  - "用户在决策流程中表现出自主性增强"
time_window: 2027-01-01
area: "ventures"
created: 2026-04-20
---
```

---

## 分配项目角色

丞相接下来问：

```
🏛️ 丞相

你有 4 个项目可能在这条线上:
- life-os
- docs-site
- content-marketing
- user-research

要分配角色吗？规矩是一条线只能有 1 个 critical-path。
```

你：`是的 life-os critical-path，其他按我之前说的`

丞相更新每个项目的 `index.md`：

```yaml
# projects/life-os/index.md
strategic:
  line: "product-expansion"
  role: "critical-path"
  last_activity: 2026-04-20
  status_reason: "v1.6.2a 已发布，下一阶段聚焦 SOUL 智能"
```

其他 3 个类似。

---

## 定义 flows

这一步可以慢慢来，不用第一天就全部定义。

当你意识到 "user-research 的洞察应该影响 life-os 决策" 时，在 `projects/user-research/index.md` 加：

```yaml
strategic:
  line: "product-expansion"
  role: "insurance"
  flows_to:
    - target: "life-os"
      type: "cognition"
      description: "用户洞察指导产品方向"
```

丞相会自动在 life-os 的 frontmatter 里加 `flows_from`，保持双向一致。

---

## 有了 map 后简报怎么变

### 之前（无战略地图）

```
🌅 早朝简报

Area 状态:
  life-os: 🟢 进行中
  docs-site: 🟡 暂停
  content-marketing: 🟠 未启动
  user-research: 🟢 访谈中

⚡ Today's Focus:
  🥇 写 v1.6.3
  🥈 回 inbox
```

这个简报只告诉你每个项目的状态，不告诉你**哪个项目的停滞会牵扯整条线**。

### 之后（有战略地图）

```
🌅 早朝简报

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗺️ Strategic Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟡 产品市场占位                      [Controlled wait]
   Window: 2027-01-01 (36 周) | Driving: 证明 AI 让人做更好的决定
   
   life-os              [critical-path]  🟢 Steady
   docs-site            [enabler]        🟡 Momentum decay
   user-research        [insurance]      🟢 Active
   content-marketing    [accelerator]    🔴 Uncontrolled stall
   
   Narrative:
     Critical path 稳定推进。docs-site 作为 enabler 已 14 天
     无更新，即将进入告警区。content-marketing 更严重——
     30 天无动作，无 status_reason 解释。这意味着即使 critical-path
     做得再好，用户仍然 "看不到" 你——accelerator 缺席使整条线
     进度被稀释。
     
   → Action: 今天花 30 分钟给 docs-site 加 1 个页面，
     content-marketing 需要决策（继续 vs 转 insurance vs 废除）

🕳️ Blind Spots
   · areas/family 和任何战略线都没有关联——这是有意的吗？
   · driving_force 是"证明理念"，但最近 3 次决策都在讨论 DAU 指标
     → 你的行为在漂向 purpose（市场）而非 driving_force（理念）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Today
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 content-marketing 的决策
   Leverage: 这是当前整条线的最大瓶颈
   Effort: 15 分钟 | Cost of inaction: 整条线持续被"不被看见"拖累

🥈 docs-site 推进一页
   Leverage: 阻止 momentum decay 变成 uncontrolled stall
   
🟢 Safe to ignore
   · life-os 的 inbox（critical-path 本周已足够推进）
   
❓ Decisions needed
   · content-marketing 的去留
   · 是否 archive "areas/family" 里的一些老 task（非战略）
```

这种简报给你**一个起点**——不是 4 个并列的项目，是一条线的健康度 + 最需要干预的那个点。

---

## 健康原型（Health Archetype）

系统不用数字评分，用**原型匹配**。6 种：

| Archetype | 信号 | 意义 |
|-----------|------|------|
| 🟢 Steady progress | active + 活跃 + tasks 推进 | 无需干预 |
| 🟡 Controlled wait | on-hold + status_reason + 窗口内 | 正常等待 |
| 🟡 Momentum decay | active 但活动减少 + task 堆积 | 注意力飘了 |
| 🔴 Uncontrolled stall | on-hold + 无 reason 或过期 | 需介入 |
| 🔴 Direction drift | active 但行为与 driving_force 不符 | 方向偏 |
| ⚪ Dormant | insurance 角色 + 长期不活跃 | 预期内 |

这是 Klein 的 Recognition-Primed Decision Model——专家靠模式识别判断，不靠加权打分。

---

## 从零成长路径

- **第 1 周**：只定义线 + role，不定 flow。简报按线聚合够用。
- **第 2-4 周**：议程里发现"A 影响 B" → 加 decision flow。关系自然浮现。
- **第 2-3 月**：系统识别 broken flow — 如 "user-research 有 5 条 wiki 但 life-os 从未引用"。
- **第 6 月**：多条线 + 跨线 insights — DREAM REM 发现"product-expansion 透支 health-baseline"。

---

## 关键注意事项

### 1. 不要给每个项目都配战略线

不是所有项目都是战略性的。"修 blog 的 bug" 就不应该有战略线。留给那些**真正想推进的方向**。

### 2. critical-path 只能一个

很多人想标 2 个 critical-path 因为"都很重要"。不行。

如果你真的觉得有 2 个都不能停，说明你在跑 2 条不同的战略线。拆开定义。

### 3. status_reason 是关键字段

on-hold 的项目必须写 `status_reason`，否则系统无法判断是 controlled wait 还是 uncontrolled stall。

### 4. driving_force 不是 purpose 的装饰

这两个字段故意设计为分离。Purpose 是对外的、可说的；driving_force 是你内心真实想推进的。

很多人第一次设置时会把 driving_force 写得和 purpose 一样漂亮——这是自欺。诚实写 driving_force，系统才能识别 behavior-driving-force mismatch。

---

## 用 strategic map 做决策

一次典型的跨项目决策：

```
你：我要不要在 life-os 里加 Telegram 集成

🏛️ 丞相

⚠️ Cross-project decision. 查了 STRATEGIC-MAP:

- life-os 是 product-expansion 的 critical-path
- Telegram 会分流你 3-4 周（影响 critical-path 进度）
- driving_force 是"证明 AI 让人做更好的决定"——Telegram 加速
  这个吗？还是稀释？
- content-marketing (accelerator) 当前 stall，Telegram 的推广
  需要 accelerator 支撑，但 accelerator 已 broken

我的框架问题:
这个决定是加强 critical-path 还是分流？如果分流，
是不是应该先处理 content-marketing 的 stall？

(继续升堂 → planner/reviewer/六部)
```

**没有 map**，这个问题会单独议：Telegram 好还是不好。

**有 map**，丞相把它放在**整条线的上下文**里问：现在整条线缺的是什么？Telegram 是补还是分？

这就是战略层的价值。

---

## 常见问题

**Q：我现在项目很乱，没法一下定义完美的 map 怎么办？**
A：只定 1 条线，4 个项目，role 不写 flows。够用。随着决策发生，flows 会自然浮现，你补进去。

**Q：角色定错了怎么改？**
A：直接改 index.md frontmatter。下次上朝 STRATEGIC-MAP.md 自动重编译。

**Q：战略线会过期吗？**
A：time_window 到期后，系统会提示"这条线到期，还要延续吗？"你可以续、可以归档、可以转为另一条线的一部分。

**Q：项目可以同时属于多条线吗？**
A：不能。一个项目只能主属一条线。如果它对多条线都有贡献，通过 flows_to 跨线连接。

---

## 下一步

- 定义完战略线后，下次上朝观察简报如何变化（按 [daily-workflow.md](daily-workflow.md) 的节奏）
- 每季度/每年复盘 strategic map 的演变 —— [annual-planning-session.md](annual-planning-session.md)
- wiki 和 strategic map 有交集（cognition flow 需要 wiki 载体）—— [building-your-wiki.md](building-your-wiki.md)
