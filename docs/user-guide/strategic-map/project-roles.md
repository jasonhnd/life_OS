# 项目角色与 Flow Graph

每个属于战略线的项目都要标一个角色——说明它在这条线里承担什么。加上 flow 定义，就构成了一条线的完整拓扑。

## 四种项目角色

存在 `projects/{project}/index.md` 的 `strategic.role` 字段。

```yaml
strategic:
  line: "market-expansion"
  role: "critical-path"   # 或 enabler / accelerator / insurance
```

### critical-path（关键路径）

- **含义**：这个项目停了，整条战略线就停了
- **约束**：**每条战略线只能有 1 个**
- **例子**：market-expansion 战略线里的 "compliance certification"——没拿到证，什么都动不了
- **decay 阈值**：7 天 warn, 14 天 alert（对停滞最敏感）

这个项目是整条战略线的咽喉。监控最严——一旦 7 天没动静，系统会在简报里醒目标记。

### enabler（使能者）

- **含义**：critical-path 能推进之前必须完成的前置项目
- **约束**：多个 allowed
- **例子**：legal-review、partner-onboarding，在 certification 拿到之前必须先完成
- **decay 阈值**：14 天 warn, 30 天 alert

enabler 失败不会立刻让战略线死掉，但会让 critical-path 卡住——间接杀死这条线。

### accelerator（加速器）

- **含义**：让战略线更快完成，但不是阻塞项
- **约束**：多个 allowed
- **例子**：marketing-buildup，不做也能走，做了能加速渗透
- **decay 阈值**：30 天 warn, 60 天 alert

accelerator 可以停一阵子——不会让整条线死。适合在 critical-path 卡住的等待期投入。

### insurance（保险）

- **含义**：主路径失败时的备用方案
- **约束**：多个 allowed
- **例子**：在主要市场之外同时准备一个次要市场作为 Plan B
- **decay 阈值**：60 天 warn, **无 alert**（预期就是 dormant）

insurance 项目长期休眠是正常的——它的价值在于"需要时能启动"，不在于"一直在推进"。系统不会因为它 90 天没动而告警。

---

## 如何选择角色

决策树：

1. **如果这个项目停了，整条战略线会停吗？** → 如果是，`critical-path`（只能有 1 个）
2. **critical-path 能推进之前必须先完成这个项目吗？** → 如果是，`enabler`
3. **这个项目让战略线更快，但不阻塞？** → `accelerator`
4. **这个项目是备胎，主路径失败才启用？** → `insurance`

如果一个项目完全不符合以上任何一个——它可能**不属于这条战略线**，考虑拆出去或不归属。

### 常见误区

- **把多个项目都标为 critical-path**：不行，每条线只能有 1 个。如果你觉得有 3 个"都是最关键的"——你对战略线的定义不够清晰，回去重新想。
- **把 insurance 项目当 accelerator 来催**：然后系统告警你，你又觉得系统烦。角色决定了监控方式——标对了系统才知道什么该催、什么不该催。
- **不标任何 role**：项目 `strategic.line` 填了但 `strategic.role` 没填 → RETROSPECTIVE 会在 "Decisions needed" 里问你。

---

## Flow Graph

Flow 定义项目之间的"资源/信息流动"。存在 `projects/{project}/index.md` 的 `flows_to` 和 `flows_from` 字段。

```yaml
strategic:
  line: "market-expansion"
  role: "critical-path"
  flows_to:
    - target: "project-beta"
      type: "cognition"
      description: "Certification results reused for beta's decisions"
  flows_from:
    - source: "project-gamma"
      type: "cognition"
      description: "Industry knowledge input feeding certification strategy"
```

`flows_to` 写在源项目里；`flows_from` 写在目标项目里（冗余 OK，让两端都能独立查）。

### 四种 Flow 类型

#### cognition · 认知流

- **含义**：结论或知识从一个项目传给另一个项目用于决策
- **载体**：`wiki/` 条目（详见 `cross-layer-integration.md`）
- **阻塞严重度**：中（异步传递）
- **例子**：project-alpha 完成了 certification 流程，总结出的"合规方法论"给 project-beta 省去重走一遍的时间

认知流是最常见的。项目 A 学到的东西，项目 B 作为前提。

#### resource · 资源流

- **含义**：实物/代码/交付物从一个项目流到另一个项目
- **阻塞严重度**：高（具体依赖）
- **例子**：project-alpha 搞出的 SDK，project-beta 的产品要 import 它

resource 流一旦断，下游立刻卡死——比 cognition 严重。

#### decision · 决策流

- **含义**：一个项目的决策约束或否决了另一个项目的选择
- **阻塞严重度**：关键（必须立刻同步）
- **例子**：project-alpha 决定"只进中国市场"，project-beta 的 "海外发行策略" 就失效了

decision 流是最危险的——一个决策做出来，下游项目的前提就变了。REVIEWER 在审议时会专门检查这个（是否无意中否决了下游项目的前提）。

#### trust · 信任流

- **含义**：一个项目建立的关系资本，另一个项目可以继承
- **阻塞严重度**：低（长期累积）
- **例子**：project-alpha 建立了和监管机构的信任关系，project-beta 启动类似流程时不需要从零开始

trust 流是慢累积的——短期看不到价值，长期是护城河。系统不会对它的"断流"告警（因为它本来就不是急事），但会在盲点检测里提醒你"最近 6 个月没在 alpha 上投入，trust 在蒸发"。

---

## Flow 严重度排序

决策影响传播时，严重度顺序（REVIEWER 用这个判断是否 veto）：

1. **decision**（关键）：必须 veto / 强制同步下游
2. **resource**（高）：必须验证下游还有没有它要的
3. **cognition**（中）：标记给下游 review
4. **trust**（低）：记录即可

---

## 断流的样子

Flow 定义了但没真正在流 → "broken flow"。这是盲点检测（详见 `blind-spot-detection.md`）的一类。

### 断流的五种表现

1. **cognition 流断**：
   - 定义：`alpha → (cognition) → beta`
   - 现实：alpha 写了 wiki 条目，但 beta 的最近 5 个 decisions 从来没引用过
   - 意味着：beta 在重新推导 alpha 已经解决的问题——浪费

2. **resource 流断**：
   - 定义：`alpha → (resource) → beta`
   - 现实：alpha 的交付物过期 / 版本对不上，beta 还在用
   - 意味着：隐藏技术债，随时爆

3. **decision 流断**：
   - 定义：`alpha → (decision) → beta`
   - 现实：alpha 改了重要决策，但 beta 的 index 没 update
   - 意味着：beta 在一个已经作废的前提上推进——最危险

4. **trust 流断**：
   - 定义：`alpha → (trust) → beta`
   - 现实：alpha 项目已经 6 个月没动，关系没维护
   - 意味着：beta 启动时以为能继承信任资本，其实已经凉了

5. **flow 指向不存在的项目**：
   - 定义：`alpha → (cognition) → project-x`
   - 现实：`project-x` 已经归档/删除
   - 意味着：定义过期，需要清理

### 断流会怎么处理

- **编译时发现**：RETROSPECTIVE Step 15 编译 STRATEGIC-MAP.md 时，在 "Blind Spots" 里标出来
- **REVIEWER 审议**：做决策时检查相关 flow 是否健康
- **ARCHIVER 退朝**：在 outbox 里注记，next session 关注

---

## 例子：一条完整战略线的 flow graph

```
                   project-gamma
                   (enabler · industry research)
                        │
                        │ cognition: 行业趋势分析
                        ↓
                   project-alpha           →(resource: SDK)→   project-beta
                   (critical-path)                              (accelerator)
                   certification               ↑
                        │                       │
                        │ decision: "只进中国" │ cognition: 合规方法论
                        ↓                       │
                   project-delta  ←─────────────┘
                   (insurance · 海外 Plan B)
```

读这个图：

- **gamma** 把行业洞察传给 **alpha**（cognition）
- **alpha** 是关键路径——拿到 cert 之后把 SDK 传给 **beta**（resource），把合规方法传给 **beta**（cognition）
- **alpha** 的"只进中国"决策直接约束 **delta** 的前提（decision）
- **delta** 是保险——平时休眠，alpha 失败才启动

每一条边在 `alpha/index.md` 里都有定义：

```yaml
strategic:
  line: "market-expansion"
  role: "critical-path"
  flows_to:
    - target: "project-beta"
      type: "resource"
      description: "SDK 供 beta 集成"
    - target: "project-beta"
      type: "cognition"
      description: "合规方法论"
    - target: "project-delta"
      type: "decision"
      description: "市场选择约束 delta 的 Plan B 范围"
  flows_from:
    - source: "project-gamma"
      type: "cognition"
      description: "行业趋势"
```

---

## 相关文件

- `references/strategic-map-spec.md`——Role 和 Flow 的完整 spec
- `docs/user-guide/strategic-map/strategic-lines.md`——先有战略线，才有角色
- `docs/user-guide/strategic-map/health-archetypes.md`——角色的 decay 阈值对应健康判定
- `docs/user-guide/strategic-map/blind-spot-detection.md`——断流检测
- `docs/user-guide/strategic-map/cross-layer-integration.md`——cognition 流和 wiki 的关系
