# 积累你的 Wiki

Wiki 是系统里 "关于世界的知识" 这一层。跟 SOUL 的区别：SOUL 是你这个人，wiki 是你学到的事实、规律、方法。

两层**不能混**。"我习惯早起" 是 SOUL；"早起 1 小时相当于周末多出半天" 也不是 wiki（这是个人偏好）。"日本 NPO 做借贷无法律豁免" 才是 wiki。

本文告诉你：wiki 怎么自动增长、哪些结论能通过 6 条标准、成熟的 wiki 怎么用、哪些条目你应该废弃。

---

## Wiki 自动写入的 6 条硬标准

起居郎（ARCHIVER）在退朝时扫会话，每一个候选结论都要过 6 道关：

1. **跨项目可复用** — 不只在这个项目有用
2. **关于世界，不关于你** — 事实/规则/方法，不是价值观、不是行为习惯
3. **零隐私** — 没有人名、金额、公司名、账号、具体日期+地点组合
4. **事实或方法** — "发生了什么" 或 "怎么做 X"，不是 "我觉得"
5. **≥2 独立证据** — 至少两个来源/案例/数据点
6. **不和现有 wiki 冲突** — 冲突的话增加 `challenges: +1` 到现有条目，不新建

全部通过才自动写入。**差一条就丢弃**。不写"低 confidence 版本"。

---

## 真实例子：一个合格的 wiki 条目

你在某次议程里，刑部研究了日本 NPO 的贷款法律。它引用了两部法律（贷金业法 + NPO 法人法）。

起居郎 Phase 2 扫这段内容：

| 检查 | 结果 |
|------|------|
| 跨项目复用？ | ✅ 你以后创业、投资、给朋友建议都可能用到 |
| 关于世界？ | ✅ 法律事实 |
| 零隐私？ | ✅ 不涉及具体人/公司/金额 |
| 事实型？ | ✅ 纯法律条款 |
| ≥2 证据？ | ✅ 贷金业法 + NPO 法人法 |
| 冲突现有？ | ✅ 无相关现有条目 |

**全过**。自动写入：

```markdown
---
domain: "finance"
topic: "lending-law-npo"
confidence: 0.3
evidence_count: 2
challenges: 0
source: session
created: 2026-04-20
last_validated: 2026-04-20
---

### Conclusion
日本 NPO 法人从事贷款业务不享有贷金业法豁免。

### Reasoning
- 贷金业法（令和元年修正）要求纯资产 500 万以上 + 资格人员
- NPO 法人法规定的 20 类特定非营利活动中不包含借贷
- 地方自治体例外仅限极小规模生活资金贷款

### Applicable When
- 设立 NPO 并希望通过借贷实现使命时
- 对比商业贷金业与 NPO 路径时
- 任何涉及日本非营利组织金融业务的讨论

### Source
- Session: 2026-04-20 快车道分析 "NPO 能否做借贷"
```

路径：`wiki/finance/lending-law-npo.md`

**注意**：`confidence: 0.3` 是因为 2 个证据点。3 个以上会起步在 0.5。

---

## 真实例子：一个不合格的候选

同一次议程里还有另一个结论："用户对家庭意见权重较高"。

| 检查 | 结果 |
|------|------|
| 跨项目复用？ | ❌ 这是关于你的，不是关于世界 |

**第 2 条直接否掉**。这条会进 SOUL（不是 wiki）。

另一个例子："我在 NPO 法律研究中发现日本行政效率低于想象"——

| 检查 | 结果 |
|------|------|
| 关于世界？ | ❌ "低于想象" 是感受不是事实 |

否掉。这条不进 wiki 也不进 SOUL，就在本次 journal 里留个痕迹。

---

## 隐私过滤最严格

这条是硬规矩。起居郎在写入前会过**隐私过滤器**：

- 剥离人名（除非公开人物且与结论直接相关）
- 剥离具体金额、账号、ID
- 剥离具体公司名（除非公开案例）
- 剥离家人朋友称谓
- 剥离可追踪的 日期+地点 组合

**例子**：

候选结论："2026 年 4 月在涩谷区某 X 公司面试后，我发现日本科技公司招聘流程普遍长于美国"。

过滤后："日本科技公司招聘流程普遍长于美国"。

然后再判：结论还有意义吗？如果过滤后剩"科技公司招聘流程有文化差异"这种废话，**丢弃**。

---

## 积累 3 个月后 wiki 长什么样

```
wiki/
├── INDEX.md          ← 自动编译，每次上朝刷新
├── finance/
│   ├── lending-law-npo.md       (0.6)
│   ├── jp-tax-rsu.md            (0.8)
│   ├── rsu-cliff-rules.md       (0.5)
│   └── jp-insurance-basics.md   (0.3)
├── startup/
│   ├── mvp-validation.md        (0.7)
│   ├── biz-plan-versions.md     (0.5)
│   └── cofounder-equity-split.md (0.4)
├── health/
│   ├── fasting-16-8-evidence.md  (0.6)
│   └── cardio-zone2-protocol.md  (0.3)
├── legal/
│   ├── jp-visa-h1b.md           (0.7)
│   └── non-compete-jp.md        (0.5)
└── _archive/
    └── old-framework-x.md
```

**INDEX.md** 由系统编译，长这样：

```markdown
# Wiki Index · 2026-04-20

Total: 10 entries across 4 domains

## finance (4)
- 🟢 [0.8] jp-tax-rsu — 日本对 RSU 行权按所得税征税，时点为 vest 日
- 🟡 [0.6] lending-law-npo — 日本 NPO 法人从事贷款业务不享有豁免
- 🟡 [0.5] rsu-cliff-rules — 1 年 cliff 前离职 RSU 归零
- 🟠 [0.3] jp-insurance-basics — 日本国民健康保险 vs 公司保险

## startup (3)
- 🟢 [0.7] mvp-validation — MVP 验证需求不是验证产品质量
- 🟡 [0.5] biz-plan-versions — BP 至少 3 版：投资人版、操作版、宣传版
- 🟠 [0.4] cofounder-equity-split — 联创股权应锁定 vesting，最少 2 年

## health (2)
- 🟡 [0.6] fasting-16-8 — 16:8 间歇断食对代谢指标改善有效 (meta 分析 2023)
- 🟠 [0.3] cardio-zone2 — Zone 2 心率区间 (60-70% HRmax) 改善有氧基础

## legal (2)
- 🟢 [0.7] jp-visa-h1b — 日本工作签证与 H1B 不兼容，需先弃一方
- 🟡 [0.5] non-compete-jp — 日本竞业条款需对价，无对价通常无效
```

---

## 系统怎么用 wiki

### ROUTER（丞相）层面

上朝时丞相读 INDEX.md。你问一个问题时：

```
你：我在考虑在东京开公司做小额贷款
```

丞相扫 INDEX，发现 `lending-law-npo` 和你相关：

```
🏛️ 丞相

📚 我发现相关已有知识：
- lending-law-npo (confidence 0.6) — NPO 路径无法律豁免

你想：
a) 从这条已有结论出发（可能跳过刑部重复研究）
b) 让刑部从头再研究一次（情况变了或你不信任之前的结论）
```

你选 a，议程**跳过**了刑部的基础研究，直接讨论"既然 NPO 不行，那走普通贷金业还是其他路径"。

**节省时间** = wiki 的核心价值。

### DISPATCHER（尚书省）层面

派遣令里会明示相关 wiki：

```
📨 派遣令

→ 刑部：
  Known premises (from wiki):
  - lending-law-npo (0.6): NPO 路径无豁免
  - non-compete-jp (0.5): 竞业需对价
  
  Focus areas:
  - 贷金业登录所需条件
  - 与现有东京雇主合同的冲突
```

刑部不需要从"日本贷款法律是什么"开始研究，直接进深水区。

### REVIEWER（门下省）层面

门下省审议时会查一致性：

```
🔍 门下省

Wiki 一致性检查:
- 本次结论说"用 NPO 形式可以规避贷款监管" 
- 与已有 wiki/finance/lending-law-npo.md (0.6) 冲突
- 建议：要么修订本次分析，要么修订 wiki 条目

⚠️ 标记但不自动否决
```

如果本次分析是对的（法律改了），你可以要求系统：

```
更新 wiki/finance/lending-law-npo.md 为"2026 年 X 月修法后增加了豁免"
```

原条目会 `challenges: +1`，confidence 下降。如果证据充分，你可以手动调整。

---

## 识别一个结论是否合格 · 判断流程图

面对一个结论，问自己这 6 个问题。**只要一个 No 就不该进 wiki。**

```
1. 在另一个项目会用到吗？  →  No → 这是本项目笔记，留 journal
2. 是关于外部世界吗？      →  No → 关于你 → SOUL；关于行为 → user-patterns
3. 无隐私吗？              →  No → journal 或 decisions
4. 是事实或方法吗？        →  No → 感受或观点 → journal
5. 有 ≥2 独立证据吗？       →  No → 单点观察 → journal，等累积
6. 和现有 wiki 一致吗？    →  No → 去更新现有条目，不新建
```

每一条都过，才写 wiki。

---

## 审查和废弃条目

### 审查（自动）

- 每次上朝时，丞相读 INDEX，若某条 wiki confidence 从 0.7 降到 0.3（因为 challenges 累积），会警示你
- 起居郎每次 Phase 2 后检查 wiki 间的冲突
- AUDITOR 巡检时会报告低 confidence 长期未验证的条目

### 废弃（主动）

三种方式：

**方式 1：直接删文件**

在硬盘上删掉 `wiki/finance/lending-law-npo.md`。下次上朝 INDEX 会刷新，条目消失。

**方式 2：对话里 "undo recent wiki"**

```
undo recent wiki
```

起居郎下一次调用时会回滚最近自动写入（注意是最近的一批）。

**方式 3：调 confidence 到 0**

打开文件，把 `confidence: 0.6` 改成 `confidence: 0`。条目还在但系统不会引用。

---

## 常见的 wiki 误解

### 误解 1："我要把所有知识都写进 wiki"

不是。wiki 只放**反复可用的结论**，不是读书笔记。

**反例**：你读了一本 Power of Now，做了 50 页笔记——这不进 wiki。进 `areas/learning/books/` 或 `projects/*/notes/`。

**正例**：你从 Power of Now 和其他 3 本书提炼出"情绪识别早于情绪反应能减少冲动决策 60%"——这可能进 wiki（如果你有 ≥2 个实际案例验证）。

### 误解 2："wiki 越多越好"

不。质量 > 数量。10 个 0.6+ 的条目胜过 100 个 0.2 的条目。

系统的设计就是**拒绝低 confidence**——候选 1 条证据 = 直接丢弃。

### 误解 3："我的人生经验能进 wiki"

"我发现健身房早上 6 点人少" = 个人经验 = 不进 wiki。

"健身房非高峰时段（早 6 点/晚 10 点）器械等待时间 < 2 分钟" 在加上 ≥2 个源支持后**可能**进 wiki——但这已经接近边界。更安全的是写 `areas/fitness/notes/`。

### 误解 4："我不同意的结论要删"

不对。

- 如果你觉得**事实不对**（系统总结错了）→ 删
- 如果你觉得**结论对但你不喜欢** → 保留。wiki 不是你的信念展示区，是你验证过的事实记录

---

## 和 SOUL 的区别复习

| 区别点 | SOUL | Wiki |
|--------|------|------|
| 关于什么 | 你是谁 | 世界是什么样 |
| 隐私 | 高（你的价值观） | 零（去个人化） |
| 主观/客观 | 主观偏好 + 行为 | 客观事实 |
| 触发写入 | 2 次行为证据 | 2 次来源证据 |
| What SHOULD BE | 你填 | 不存在 |
| 删除意味着 | "这不是我" | "这不是事实" |

---

## 成熟系统的 wiki 使用模式

6 个月后，一个典型议程的开头会变成：

```
你：我要决定 X

🏛️ 丞相
📚 相关 wiki:
- entry-A (0.8) — ...
- entry-B (0.6) — ...
- entry-C (0.5) — ...

从这些结论出发，我的澄清问题是：你的情况和 
entry-A 的 Applicable When 是否完全吻合？还是有差异？
```

**你的议程速度会加快 3-5 倍**——很多"基础研究" 不再需要重复。

这就是积累 wiki 的复利回报。前 3 个月看起来"就写了 10 条东西"，第 4 个月开始你发现决策变快了、参考框架丰富了、你的判断力在可见地增长。

---

## 下一步

- 读 [setting-up-your-soul.md](setting-up-your-soul.md) 理解 SOUL 和 wiki 的边界
- 当你发现两个项目开始共享 wiki 条目时，读 [mapping-your-strategy.md](mapping-your-strategy.md) 把它们连成 cognition flow
- 每年回顾时，wiki 的增长是重要度量 —— [annual-planning-session.md](annual-planning-session.md)
