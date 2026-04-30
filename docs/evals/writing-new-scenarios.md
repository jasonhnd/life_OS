# 写新 Eval 场景

新场景 = 一个待测的系统行为。不要为每种决策都写场景——选那些**边界 / 容易退化 / 设计意图容易忘**的地方。

---

## 场景文件的结构

一个 scenario 是一个 `evals/scenarios/{name}.md` 文件。标准结构（6 个 section）：

```markdown
# Scenario: <场景名>

**Path**: <Full Court | Express Analysis | Direct Handle>

## User Message

```
<真人会发给系统的消息原文，完整地放在 fenced code block 里>
```

## Design Intent

<这个场景是为了测什么？设计时想让系统出什么错？2-4 句>

## Expected Behavior

- **Router**: <ROUTER 应该做什么>
- **Planner**: <PLANNER 应该做什么>
- **Reviewer reviews the plan**: <REVIEWER 该标注什么>
- **<DOMAIN> domain**: <某个 domain 应该给出什么样的分析>
- **Reviewer final review**: <最终审议应该出现什么>
- **Advisor**: <ADVISOR 应该抓到什么行为模式>

## Quality Checkpoints

- [ ] <具体可检查条目 1>
- [ ] <具体可检查条目 2>
- [ ] ...
```

这是硬性格式。`run-eval.sh` 靠 `## User Message` 下的 fenced code block 提取输入——少了这个 section 或忘了 code fence，脚本直接 FAIL。

---

## 必需的 frontmatter

**注意**：目前的 scenario 文件**不用 YAML frontmatter**，而是 Markdown 的 H1 + bold-label 元数据。这是刻意选的——人类读起来更顺，脚本也能抽。

必需的三件事：

1. **文件名 = scenario 标识**：`resign-startup.md` → 运行时用 `./run-eval.sh resign-startup`。
2. **H1 标题**：`# Scenario: <描述性名字>`。描述性名字只给人看，脚本不用。
3. **Path 标签**：`**Path**: Full Court` / `**Path**: Express Analysis` / `**Path**: Direct Handle`。明确声明这场景预期走哪条路径。

命名规范：

- 全小写 kebab-case：`large-purchase.md` ✅，`LargePurchase.md` ❌
- 描述动作或主题：`council-debate.md`、`fengbo-loop.md`
- 不要带日期：日期在 git log 里
- 不要带版本号：版本在 git log 里

---

## 用户消息的写法

三条原则：

### 1. 像真人说话

❌ **假**：

> I am a 30-year-old software engineer working at a Japanese company. I earn 8 million JPY per year. I have been considering whether to quit my job to start a SaaS company. I would like your analysis.

这不是真人说话，这是人在写简历。系统拿到这样的输入会做出很干净的分析，**但干净不是真实**——真实场景里人不会这么说。

✅ **真**：

> 我在日本公司做 software engineer 三年了，年薪 800 万日元，最近越来越觉得无聊，想辞职做自己的 SaaS。手上存款大概 500 万日元。没 co-founder，也没想好要做什么产品——就觉得该趁年轻搏一下。

这个版本里有：情绪（"越来越觉得无聊"）、认知偏差（"该趁年轻搏一下"）、关键缺口（"没想好要做什么产品"）。这些才是真正考验系统的地方。

### 2. 包含设计意图对应的触发信号

每个场景有个 "Design Intent"。User Message 必须**在原文里包含那些信号**，不然系统测不到。

**反例**：Design Intent 说要测 COUNCIL 辩论（六部间分数冲突），但 User Message 只说「该不该跳槽」，没有任何家庭 / 财务张力，那 FINANCE 和 PEOPLE 就不会出现分数冲突。

**正例**（council-debate.md）：

> 我收到新加坡的 offer，薪水 double 到 1600 万日元。但老婆怀孕 4 个月，她爸妈在东京，我爸妈在中国。她说支持我，但我能看出来她其实不太愿意。offer 要求下个月就入职。

每一个要素都在为 COUNCIL 的触发条件服务：

- 薪水 double → FINANCE 必然高分
- 怀孕 4 个月 → INFRA 健康风险高
- 双方父母分离 → PEOPLE 低分
- 「她说支持但不愿意」→ GOVERNANCE 的 informed consent 信号
- 下个月入职 → 时间压力

### 3. 不要太长

User Message 控制在 2-4 句。现实里人发消息就这么长。写成一整篇论文会让 ROUTER 跳过澄清直接升格，这样测不到「2-3 轮澄清」的硬规则。

---

## Design Intent 的作用

这段 section 是写给未来自己（和 code reviewer）看的。**不是给 claude -p 看的**——scenario 文件里除了 User Message 部分，其他 section 不进入系统输入。

好的 Design Intent 回答：

1. **这个场景是为了测什么具体行为**？（否决、升格、Express 路由、分数冲突 ...）
2. **系统最容易犯什么错**？（比如 fengbo-loop 的 Design Intent 明说：如果 PLANNER 只听用户要求写「辞职后的安排」而跳过财务风险和情绪评估，REVIEWER 必须否决。）
3. **为什么选这个用户消息**？（哪些触发信号对应哪个预期行为）

两句话版本也行。看 `evals/scenarios/fengbo-loop.md` 的 Design Intent：

> 包含多个应触发否决的要素：(1) runway 极短（3-4 个月），(2) 情绪驱动（"受不了老板"），(3) 用户要求"别劝我"但系统有责任提示风险，(4) 无 backup 直接裸辞。如果 PLANNER 只按用户要求写「辞职后的安排」、跳过财务风险与情绪评估 → REVIEWER 必须否决。

---

## Expected Behavior 的写法

这是 rubric 的上游文档——对每个 agent 写出应该做什么。用这个格式：

```markdown
- **<Agent Name>**: <应该做什么，或应该避免什么>
```

常见的 agent 覆盖：

- **Router**: 升格 / 直接处理 / Express 路由
- **Planner**: 激活哪些 domain，覆盖哪些维度
- **Reviewer reviews the plan**: 对 plan 本身应该标注什么（gap、风险、矛盾）
- **<DOMAIN> domain**: 该 domain 应该给什么量化或质化判断
- **Reviewer final review**: 对 Summary Report 的最终审议
- **Auditor**: 应该抓到什么质量问题
- **Advisor**: 应该抓到什么行为模式或认知偏差

不是每个场景都要写全部 多个 agent。只写**这个场景的设计意图会考验到的那几个**。

---

## Quality Checkpoints 的写法

checkpoint 是最重要的 section——这是**跑完之后用来逐条验证**的。

格式：

```markdown
- [ ] <能被 yes/no 判断的具体声明>
```

几条原则：

### 1. 具体，不能含糊

❌ 「plan 够完整」——太含糊
✅ 「Planner 激活了 ≥5 个 domain」——可数

❌ 「REVIEWER 审议到位」——太主观
✅ 「REVIEWER 质疑了至少一个 domain 的分数」——可查

### 2. 绑定到输出里可以搜到的证据

❌ 「系统情绪识别准确」——没法验
✅ 「REVIEWER 的 sentiment review 提到『友情因素』和『沉没成本』」——grep 能找到

### 3. 涵盖正面和反面

除了「应该做 X」，也写「不应该做 Y」。

正例（router-triage.md 的 Message 3）：

- [ ] Message 3: 没有升格到全朝会议
- [ ] Message 3: 提供了实质性的睡眠改善建议
- [ ] Message 3: 追问不超过 1 轮

前两条说应该做什么，第三条说**不应该做什么**（追问 2 轮就是过度盘问）。

### 4. 能量化的尽量量化

- 分数的用具体数字：「至少一个 domain 得分 < 6」
- 数量用具体数字：「Planner 激活 ≤4 个 domain」
- 条件用具体描述：「在 Round 2 或 Round 3 中出现了 'if...then...' 的条件性建议」

---

## 什么时候加新场景 vs 扩展现有场景

**加新场景**的条件：

1. 测一个**从未覆盖过的流程**。例如「Strategist 激活」现在没有场景——如果要测它，开新文件。
2. 测一个**新的边界条件**。例如「用户在 ROUTER 澄清阶段突然改主题」——现在的场景里没有，且属于 ROUTER 鲁棒性测试。
3. 测一个**新的触发词**。新加了 theme-specific trigger（比如 "閣議開始" 的新变体），要有对应场景验证。

**扩展现有场景**的条件：

1. 同一个设计意图，**多加一个 checkpoint** 就够了。例如 `resign-startup.md` 现在已经测 REVIEWER 否决，但没测 ADVISOR 的「趁年轻认知偏差」识别，可以加一条 checkpoint：`- [ ] Advisor 指出了「趁年轻」的认知偏差`。
2. 同一个场景，**补充 Design Intent 里漏掉的一条**。例如发现某次 session 里 ARCHIVER 没把「500 万日元 runway」这个经验写进 wiki，补一条对应 checkpoint。

**经验判断**：Life OS 目前 6 个场景，覆盖 80% 的常见行为。如果直觉上想加第 7 个场景，先问自己「能不能扩展现有的」。**scenario 数量膨胀是一种反模式**——跑 6 个场景 10 分钟能接受，跑 20 个场景 40 分钟就不会天天跑了。

---

## 加完之后怎么验证

1. **手动跑一次**：把 User Message 粘进 Claude Code，观察是否触发 Design Intent 预期的行为。不预期就改 User Message 加触发信号。
2. **用脚本跑**：`./evals/run-eval.sh <your-scenario-name>`。确认 exit 0 + 输出文件生成。
3. **按 Quality Checkpoints 逐条对照**输出文件，每条能打 ✅ 或 ❌。打不了 → checkpoint 太含糊，改 checkpoint。
4. **commit 时注明**：commit message 写清这个场景是为了测什么（例如：「test: 新增 council-debate scenario，验证 domain 分数冲突触发 3 轮辩论」）。

---

## 参考：现有 6 个场景的分工

| Scenario | 测什么 |
|----------|--------|
| `resign-startup.md` | Full Court 全流程，全六部激活 |
| `large-purchase.md` | Express Analysis，只激活必要 domain（3 个） |
| `relationship.md` | PEOPLE + INFRA 为主，情感和风险纠缠 |
| `council-debate.md` | 分数冲突 → COUNCIL 3 轮辩论 |
| `fengbo-loop.md` | REVIEWER 必须否决，PLANNER 按点改 |
| `router-triage.md` | Router 三种分流（直接处理 / 升格 / 灰色地带）|

写新场景前先过一遍这张表，避免重复。
