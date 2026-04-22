# 战略线（Strategic Lines）

战略线是 Strategic Map 的"骨架"——把多个项目组织成一个有意图的集合。

## 存在哪

`_meta/strategic-lines.md`

**注意**：这个文件放在你的 second-brain 里，不是放在 Life OS 代码库里。多条战略线用 `---` 分隔。

## 一条战略线长什么样

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

字段解释：

| 字段 | 必需 | 说明 |
|------|-----|------|
| `id` | 是 | 唯一标识（kebab-case），项目 frontmatter 里用这个引用 |
| `name` | 是 | 展示名 |
| `purpose` | 是 | 一句话的正式目的 |
| `driving_force` | 否 | 真正驱动你投入这条线的东西（可以和 purpose 不同） |
| `health_signals` | 否 | 什么信号表示这条线健康（AI 基于 driving_force 提议，用户确认）|
| `time_window` | 否 | 影响整条线的截止日期 |
| `area` | 否 | 关联的生活领域 |
| `created` | 自动 | 创建日期 |

---

## `purpose` vs `driving_force`：为什么要分两个

这是 Strategic Map 最重要的设计决策。基于 **Goal Systems Theory**（Kruglanski 2002）和自我欺骗研究（von Hippel & Trivers 2011）：

**人在追求目标时，常常有一个"声明的原因"和一个"真实的驱动力"，两者常常不一致。**

### purpose（形式目的）

- 你会对别人说的版本
- 正式、合规、易于解释
- 出现在简历、愿景陈述、社交媒体
- 例：`"Build market presence in target segment"`

### driving_force（真实驱动力）

- 你真正投入精力的原因
- 有时候是情绪、有时候是恐惧、有时候是 ego
- 通常不会对别人说
- 例：`"Establish first-mover advantage before market consolidation"`（焦虑驱动）

或者完全不同：

- purpose：`"Build healthy habits"`
- driving_force：`"Prove to myself that I can finish something"`

### 两者不一致时会怎样

驱动力如果和形式目的不一致，**决定了哪些 health signals 真正重要**。

- 一条**被"关系"驱动**的战略线，应该观察社交活动、回访频率、关系深度——而不是代码 commit 数。
- 一条**被"安全"驱动**的战略线，应该观察风险敞口、冗余度——而不是增长速度。

如果 driving_force 与 purpose 相同，留空——系统当作相同。

ADVISOR 会检查"行为 vs driving_force"，不是"行为 vs purpose"。因为只有和真实驱动力一致，你才会持续投入；和形式目的一致但和真实驱动力不一致，早晚会垮。

这就是 DREAM 的 #2 触发器（behavior-mismatch-driving-force）在监控的东西。

---

## `health_signals`：怎么来

系统不要求你一开始就想清楚"什么信号表示这条线健康"——因为大部分人想不清楚。

流程是：

1. 你定义一条战略线，填了 `driving_force`
2. **第一次** RETROSPECTIVE 编译时，基于 `driving_force` 提议 health_signals
3. 你确认或修改
4. 确认后的 signals 存回 `_meta/strategic-lines.md`
5. 以后的每次编译都用这些确认过的 signals
6. DREAM 可能会提议更新（比如某个 signal 从来不出现，或新 signal 出现）

### 例子

```yaml
driving_force: "Establish first-mover advantage in target segment before market consolidation"
```

AI 提议的 signals：

- "Key milestones progressing"（目的驱动——进度是核心）
- "Partner onboarding on track"（竞争驱动——抢在对手前面）
- "Legal review turnaround within expected windows"（时间驱动——不能拖）
- "Competitor activity stable or slowing"（反向信号——对手慢下来才是利好）

你可能确认前三个，拒绝第四个（因为你觉得竞品动态你监控不过来）。存下来的就是前三个。

### 例子 2（关系驱动）

```yaml
driving_force: "Build a deep circle of trusted allies in this industry"
```

AI 提议的 signals：

- "Monthly 1:1s with 3+ key people happening"
- "Reciprocal help flowing in both directions"
- "New warm introductions happening monthly"
- "Conversations deepening in topic range"

这和 market-expansion 的 signals 完全不同——因为驱动力不同。

---

## `time_window`：截止日期

```yaml
time_window: 2026-09-30
```

可选字段。填了之后：

- 简报会显示"Window: 2026-09-30 (N 周剩余)"
- 接近 window 时（< 4 周），这条线的未完成项目自动成为 🥇 最高杠杆候选
- 盲点检测：如果 window < 2 周但 critical-path 项目还在 on-hold → 报警

不是所有战略线都需要。"建立长期关系网"这种就不该有 window。

---

## `area`：关联领域

```yaml
area: "ventures"
```

关联到你的 `areas/` 目录下的某个领域。让简报的 Area Status 视图和 Strategic Overview 视图能对齐。

不关联也行，系统会在 "Unaffiliated" 里展示。

---

## 第一次怎么写

如果你在看这份文档，可能就是准备写第一条战略线。流程：

### 方法 1：让 ROUTER 引导你

直接说："帮我把项目关联起来"，或者"let me define strategic lines"。

ROUTER 会问三个问题：

1. **"哪些项目在服务同一个目的？"**——聚类
2. **"它们之间有什么在流动？"**——定义 flow
3. **"真正驱动你投入这条线的是什么？"**——挖 driving_force

ARCHIVER 退朝时会把答案写成 `_meta/strategic-lines.md` + 各项目的 `strategic:` frontmatter。

### 方法 2：自己写

打开 `_meta/strategic-lines.md`，按上面的 YAML 格式写。先填 id / name / purpose / driving_force，其他字段留空——第一次 RETROSPECTIVE 编译会补 health_signals 提议。

### 新手常见误区

1. **一上来定义 5 条战略线**——通常你大脑里真正在想的只有 1-2 条。先写 1 条，跑 2 周，再加第二条。
2. **purpose 写得像简历文案**——"打造世界领先的 X 平台"。这不对——这是对外的，不是驱动你的。
3. **driving_force 想不出来就乱填**——如果真的 = purpose，**留空**。乱填的驱动力会把 health signals 也带偏。
4. **一条线塞 10 个项目**——战略线是"服务同一目的的紧密项目组"，一般 3-5 个。超过 6 个你自己都管不过来，系统帮不了你。
5. **不填 time_window**——不是所有线都要 window，但"有明确截止日期"的战略，一定要填。不填系统就没法帮你算"接近 deadline 但没准备"这个盲点。

---

## 查看已定义的战略线

下次 session start，你会在简报顶部看到：

```
🗺️ Strategic Overview

🟢 Market Expansion Pipeline                [Steady progress]
   Window: 2026-09-30 (24 周剩余) | Driving: first-mover advantage
   ...

🟡 Industry Relationships                    [Controlled wait]
   Window: open-ended | Driving: trusted allies circle
   ...
```

想看原始定义：直接打开 `_meta/strategic-lines.md`。

想看编译后的完整视图：打开 `_meta/STRATEGIC-MAP.md`（只读参考，不要手改）。

---

## 相关文件

- `_meta/strategic-lines.md`——你的战略线定义
- `_meta/STRATEGIC-MAP.md`——编译产物（只读）
- `references/strategic-map-spec.md`——字段完整 spec
- `docs/user-guide/strategic-map/project-roles.md`——项目在战略线里的角色
- `docs/user-guide/strategic-map/health-archetypes.md`——6 种健康原型
