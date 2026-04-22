# 让 SOUL 从零长起来

SOUL 是系统对你这个人的理解。它不是配置文件——你不用填一堆问卷。它是**一张你给自己画的像，系统帮你涂色**。

本文告诉你：第一次上朝的时候 SOUL 为什么是空的、什么时候第一条维度会冒出来、怎么填 What SHOULD BE、哪些维度你应该删掉。

---

## 首次上朝 SOUL 是空的

你第一次上朝，简报里的 SOUL Health Report 长这样：

```
🔮 SOUL Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Current Profile: SOUL 尚未建立

SOUL is gathering initial observations.
After a few decisions, first dimensions will emerge.

📈 First session — no trend data yet.
```

这**不是 bug**。SOUL 的设计是**不预设**——每一条维度都必须基于你真实的行为证据。没做决策前，系统没话可说。

你不需要做任何事。继续正常工作。

---

## 第一条维度什么时候出现

两个触发点：

### 触发点 1：ADVISOR 在每次决策后自动写入

当你在一次议程中暴露出 **≥2 条关于身份/价值观/原则** 的证据，ADVISOR（谏官）会自动写一个新维度到 SOUL.md。

**真实例子**：

你的第一次决策是"要不要接硅谷 offer"。在议程中你说过：
- "我主要担心的是老婆和父母"
- "钱不是问题"（在 REVIEWER 封驳后你补充的）
- 最终你要求议程改为"先和妻子结构化对话"

谏官看到这 3 条信号，识别出一个维度：

```yaml
---
dimension: "决策时对家庭意见的权重"
confidence: 0.3
evidence_count: 2
challenges: 0
source: advisor
created: 2026-04-20
last_validated: 2026-04-20
---

### What IS (实然)
在涉及家庭的重大决策中，倾向于先自己想清楚再与家人沟通；
但最终会把家庭意见放在高权重。

### What SHOULD BE (应然)
(awaiting your input)

### Gap (差距)
(待你填完 What SHOULD BE 后系统自动计算)

### Evidence (证据)
- 2026-04-20 硅谷 offer 决策 — 先自己想再找配偶
- 2026-04-20 硅谷 offer 决策 — 封驳后主动要求改议程，先做夫妻对话

### Challenges (矛盾)
(无)
```

**关键**：`What SHOULD BE` 是空的。系统**永远不会替你填这个字段**——它是你的主观愿望，只有你能写。

### 触发点 2：DREAM 在 N3 阶段扫三天数据

如果你连续 3 天的决策都展现出同一个模式，DREAM 会在退朝时的 N3 阶段提议 SOUL 候选。

**例子**：

连续 3 天你做了 3 个决策：
- 周一：要不要接 offer → 选"先和老婆谈"
- 周二：要不要投资 → 选"先问财务顾问"
- 周三：要不要接项目 → 选"先问团队"

DREAM 发现："3 次决策都有'先咨询他人'的模式"，提议：

```
🌱 SOUL Candidate (DREAM N3):
- Dimension: "决策前的外部验证需求"
- Observation: 3/3 最近决策包含"先咨询"步骤
- Evidence:
  - 2026-04-20 offer 决策 → 夫妻对话
  - 2026-04-21 投资决策 → 财务顾问
  - 2026-04-22 项目决策 → 团队意见
```

这条会在下次上朝的简报里显示为"🌱 New"，confidence 0.3，What SHOULD BE 留空。

---

## 下次上朝你会看到什么

上朝时 SOUL Health Report 变成：

```
🔮 SOUL Health Report

📊 Current Profile:
   · 决策时对家庭意见的权重 0.3 🌱 (1 evidence, no delta computed)

🌱 New dimensions (auto-detected since last snapshot):
   · 决策前的外部验证需求 0.3
     What IS: 倾向于决策前向外部人员咨询意见
     What SHOULD BE: (awaiting your input)

📈 First session — no trend data yet.
```

两条了。都是 0.3。都等你填 What SHOULD BE。

---

## 怎么填 What SHOULD BE

这是整个 SOUL 系统里**唯一需要你手动做的事**。其他都自动。

打开 `~/second-brain/SOUL.md`（或在 Notion 里找到 SOUL 页面），找到那个维度，编辑 What SHOULD BE 区块。

### 例子 A：你认同这个观察

"决策时对家庭意见的权重"——你觉得系统观察得对，你也认同家庭应该被优先考虑。

```markdown
### What SHOULD BE (应然)
家人意见是我的一票否决权。职业决策如果配偶明确反对，我会放弃。
父母意见权重次之，作为约束不作为决定。

### Gap (差距)
当前模式是"先自己想再沟通"，应该前置——大决策启动前就先对齐家人。
```

### 例子 B：你部分认同

"决策前的外部验证需求"——你觉得系统观察对，但**你不想这样**。你希望更自主。

```markdown
### What SHOULD BE (应然)
我希望决策主要由自己做出。咨询他人是信息补充，不是决策依据。
如果发现某次决策完全由外部意见决定，应该警觉。

### Gap (差距)
实然是"先咨询后决定"，应然是"自己先成形再验证"。
这是一个需要警惕的模式。
```

这种 Gap 很有价值——它暴露了你理想和现实的差距。未来每次决策，REVIEWER 都会拿这个 Gap 来质问你。

### 例子 C：你不认同，删掉

你看到 "决策前的外部验证需求" 这条，觉得系统误读了——你那 3 次决策都是因为特殊情况（涉及专业领域），不代表你有这个模式。

**直接删除**这个维度。在文件里删掉整块，或者说：

```
我不认同"决策前的外部验证需求"这个维度，删掉
```

丞相会执行删除。下次上朝的 Health Report 会显示：

```
🗑️ Removed dimensions (deleted by user since last snapshot):
   · 决策前的外部验证需求
```

系统**记得你删过**——它不会再次自动写入同样的维度，除非你改变行为模式。

---

## 成熟的 SOUL.md 长什么样

假设用了 6 个月，累积了 40 次决策、12 次翰林院对话。你的 SOUL.md 大概这样：

```markdown
# SOUL — 你是谁

---
dimension: "长期主义"
confidence: 0.82
evidence_count: 14
challenges: 3
source: user
created: 2026-01-15
last_validated: 2026-04-18
---

### What IS
在 70% 的决策中选择长期回报高但短期痛苦的选项。
例外：涉及家人时会切换为短期风险规避。

### What SHOULD BE
长期主义是我的默认设置，但不是唯一准则。涉及不可逆的风险时
必须覆盖它。

### Gap
较小。核心是在"涉及家人的短期决策"和"涉及自己的长期决策"中
保持清晰的切换。

### Evidence
- 2026-01-15 拒绝短期外包项目，选择继续深耕 life-os
- 2026-02-03 选择延长 MVP 测试期而非提前发布
- 2026-02-20 投资偏向 5 年以上视角
- [...11 条省略]

### Challenges
- 2026-03-01 在 deadline 压力下接受了一个短期项目
- 2026-03-15 更改了原本 5 年的学习计划
- 2026-04-10 推迟了"每天写 500 字"的长期承诺

---
dimension: "决策时对家庭意见的权重"
confidence: 0.76
evidence_count: 9
challenges: 2
source: advisor
created: 2026-02-10
last_validated: 2026-04-18
---

### What IS
家庭意见在我决策中具有一票否决权，但我倾向于自己先形成判断再征询。

### What SHOULD BE
家庭对齐应该前置，不是最后确认。

### Gap
执行层面没跟上。6 次决策中 4 次是"先想后谈"。

### Evidence
- [...]

---
dimension: "创作时的完美主义门槛"
confidence: 0.58
evidence_count: 5
challenges: 1
source: dream
created: 2026-03-08
last_validated: 2026-04-15
---

### What IS
倾向于在发布前进行第 N 轮打磨，多次错过发布窗口。

### What SHOULD BE
发布是验证，不是交付。先发后迭。

### Gap
**大**。这是最需要干预的维度。

### Evidence
[...]

---
dimension: "风险偏好（中等偏高）"
confidence: 0.72
evidence_count: 11
challenges: 3
source: advisor
created: 2026-01-28
last_validated: 2026-04-19
---

[...]

---
dimension: "避免低信号活动"
confidence: 0.41
evidence_count: 4
challenges: 2
source: advisor
created: 2026-03-25
last_validated: 2026-04-12
---

### What IS
社交、闲聊、无主题会议的参与度偏低。

### What SHOULD BE
(awaiting your input)  ← 你还没决定这是好事还是坏事

### Gap
TBD

---
```

**观察**：
- 5 个维度，不是 50 个。SOUL 不求全，求真
- confidence 分布 0.41-0.82，高的几个已经被系统引用
- 有一个还没填 What SHOULD BE（是你主动留白的观察点）
- Challenges 都是真事——你反复失败的点也诚实记下了

---

## 系统怎么用这些维度

根据 [soul-spec.md](../../references/soul-spec.md) 的 3 层引用策略，不同 confidence 的维度被不同角色引用：

| Confidence | 谁引用 | 效果 |
|------------|--------|------|
| > 0.8 | ROUTER 也引用 | 丞相在澄清时主动问你关于这个维度 |
| 0.6-0.8 | + PLANNER 引用 | 中书省在规划中自动加入这个维度 |
| 0.3-0.6 | REVIEWER 引用 | 门下省封驳时拿它审核一致性 |
| < 0.3 | 仅 ADVISOR 引用 | 谏官跟踪，不影响决策流程 |

**真实案例**——一个月后你又面对 offer 决策：

你的"长期主义"是 0.82（core）。**ROUTER 直接在第一轮澄清问**：

```
🏛️ 丞相

你的 SOUL 显示"长期主义"是你的核心维度 (0.82)。
这个决策你的长期主义是站在哪一边？
接 offer = 3-5 年价值  vs  留现职 = 10 年深耕
```

系统开始**替你带上你自己**。你不用每次重新解释你是谁。

---

## 维度冲突了怎么办

你可能发现两个维度打架：
- "长期主义" 0.82 → 倾向于深耕
- "风险偏好中等偏高" 0.72 → 倾向于冒险

冲突是好事——SOUL 的规则是 **不消解矛盾，只暴露它**。

REVIEWER 会在下次决策时写：

```
🔮 SOUL Reference

【core · Core Identity】
  · 长期主义 (0.82) — 这个决定是长期投资吗？
    → 支持（5 年跨度）
  · 风险偏好 (0.72) — 这个风险量级在你接受范围吗？
    → 挑战（超出 30%）

【Integrated Conclusion】
  SOUL 兼容性: 🟡 mixed
  Focus callout: 你的长期主义推你做这个，但量级超出了风险偏好
  需要你主动决定今天哪个优先
```

系统不替你解。它显示矛盾，让你意识到**你是谁**这件事本身有张力。

---

## 删除一个你不想要的维度

不是删 confidence 低的就对。有时候高 confidence 的维度你也不想要——因为它是**坏习惯被系统当成你的本性**。

例子：

```yaml
dimension: "避免冲突"
confidence: 0.78
```

这条 confidence 很高，系统会在决策里频繁引用。但你知道这是你想改的坏习惯，不是你的身份。

**删除它。**

下次系统会把它加回来吗？取决于你的行为。如果 7 天内你的决策还是 "避免冲突"，DREAM 会再次识别出这个模式。这次它会标记：

```
🌱 Candidate: 避免冲突 (已删除过)
System note: 用户删除过这个维度。再次提议请用户确认。
```

**系统记得被删除过。** 再次出现时是警示信号——你要么行为变了让系统重写，要么你承认这确实是你但不想承认。

---

## 用户 Nudges 全集

| 动作 | 用法 |
|------|------|
| 填 What SHOULD BE | 直接编辑文件，或"把 X 维度的 What SHOULD BE 填为 Y" |
| 删除一个维度 | 删文件块，或"删掉 X 维度" |
| 覆盖 confidence | 编辑 yaml 里的 `confidence:` 字段 |
| 撤销最近自动写入 | "undo recent SOUL" |
| 强制写入新维度 | "记下来：我 X"——作为 user source 写入 |

---

## Anti-pattern：新手常见错误

1. **第一天就填一堆** — SOUL 的价值在基于行为证据。你自己说的"我重视家庭"和行动可能不一样。提前填满 = 把自我认知强加给系统。如果一定要写，用 `source: user` 但别调高 confidence。
2. **看到低 confidence 就想删** — 新写入都是 0.3，不代表错。删除标准是"我不认同这个观察"，不是 confidence 低。
3. **What SHOULD BE 填成"我想做好人"** — 太抽象。好的是可验证 + 有情境 + 可能含例外。差"我想长期主义"，好"不涉及家人时默认 5 年回报高的方案；涉及家人切换"。
4. **忽略 Challenges** — 矛盾证据是 SOUL 最有价值的部分。它让你知道实际和理想差多远。别删。

---

## 如果 SOUL 变得太大

50 个维度是失控。好的 SOUL 应该是 5-15 个核心维度。

定期审查（每季度）：
- 合并近似维度（"重视家庭" 和 "决策时对家庭意见的权重" → 合成一个）
- 归档 dormant 的（>30 天没活跃过的）
- 删除你已经成长出的（5 年前的模式现在不再是你）

---

## 下一步

- SOUL 成熟后开始看 [building-your-wiki.md](building-your-wiki.md)——wiki 是"关于世界"的知识，SOUL 是"关于你"的知识
- 当你发现一个 SOUL 维度内部有矛盾，用 [using-the-strategist.md](using-the-strategist.md) 找翰林院聊
- 每年一次大回顾时，SOUL 的演变图是核心材料 —— [annual-planning-session.md](annual-planning-session.md)
