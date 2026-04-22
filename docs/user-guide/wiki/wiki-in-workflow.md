# Wiki 在工作流中的流转

> Wiki 不是一个孤立的知识库——它在 Life OS 的决策引擎中被多个角色读取和使用。本文讲它如何流经整个系统。

## 流转路径概览

```
  每次 Start Session
       ↓
  RETROSPECTIVE 编译 wiki/INDEX.md
       ↓
  ROUTER 读 INDEX 作为 context
       ↓
  DISPATCHER 把相关条目注入给 Six Domains
       ↓
  Six Domains 从已知前提出发分析
       ↓
  REVIEWER 检查新结论和 wiki 是否矛盾
       ↓
  archiver 在 session 结束时补充 wiki
       ↓
  AUDITOR 在巡检时审计 wiki 健康度
```

每次会话都会走一遍这个循环。Wiki 既是**被读取的输入**，也是**被写入的输出**。

---

## 1. RETROSPECTIVE：编译 INDEX.md

**时机**：每次 Start Session（Mode 0）

**做什么**：

- 扫描 `wiki/` 目录下所有带 front matter 的 markdown 文件
- 按 `domain` 字段分组
- 从每个文件读取标题（= 结论）+ confidence
- 生成 `wiki/INDEX.md`：

```markdown
# Wiki Index
compiled: 2026-04-18

## Finance
- NPO 贷款无贷金业法豁免 (0.95) → wiki/finance/lending-law-npo.md
- NPO 税收减免的 3 个条件 (0.82) → wiki/finance/npo-tax-deduction.md

## Startup
- MVP 验证需求，不是产品 (0.88) → wiki/startup/mvp-validation.md
- 商业计划书内外版本根本不同 (0.72) → wiki/startup/biz-plan-versions.md

## Health
- 16:8 间歇性断食对我有效 (0.80) → wiki/health/intermittent-fasting.md
```

### 为什么要编译

因为单独读每个文件太贵了。INDEX.md 是一个**轻量索引**——通常 20-100 行，每行 ≤ 80 字符——加载成本极低。

各个 agent 先读 INDEX，判断是否需要打开具体文件，再按需读。这是"粗筛 → 细读"的两层策略。

**INDEX.md 永远不要手动编辑**。你的改动会被下次 Start Session 的编译覆盖。

---

## 2. ROUTER：读 INDEX 作为 context

**时机**：接到用户消息时

**做什么**：

ROUTER 在澄清用户意图时，会扫一眼 wiki/INDEX.md：

- 当前话题的领域里，有高 confidence 的条目吗？
- 如果有 → 告诉用户"关于这个话题，我们已经知道 X（confidence 0.95）"
- 如果结论和用户正要问的问题直接相关 → "你想在此基础上继续，还是重新验证？"

### 举个例子

用户问："我想了解一下在日本用 NPO 结构做小额贷款的法律风险"

ROUTER 扫 INDEX：
```
## Finance
- NPO 贷款无贷金业法豁免 (0.95) → wiki/finance/lending-law-npo.md
```

ROUTER 回复：
> 关于这个话题，系统已经确立（confidence 0.95）："日本 NPO 贷款无贷金业法豁免"。这个结论基于 3 个独立证据。你想：
>
> 1. 在这个前提上继续深入（具体方案设计）
> 2. 重新验证这个结论（当前有新的法规变化）

这避免了**重复研究已知问题**，把用户的时间花在真正的新问题上。

---

## 3. DISPATCHER：注入"已知前提"

**时机**：ROUTER 决定走完整决策工作流后，DISPATCHER 分派任务给六部

**做什么**：

DISPATCHER 从 ROUTER 接到 PLANNER 批准的计划后，查找和计划相关的 wiki 条目（confidence ≥ 0.5），把它们作为"已知前提"注入每个六部的 dispatch context：

```
【Dispatch 给 Finance 部】
任务：评估这个 NPO 小额贷款方案的财务可行性
背景：[用户提供的信息]

已知前提（wiki）：
- "NPO 贷款无贷金业法豁免"（confidence 0.95）
  出处：wiki/finance/lending-law-npo.md
  含义：即使是 NPO 形式，贷款业务仍需遵守贷金业法

从这个前提出发分析，不要重复研究。
```

### 为什么这么做

因为六部默认从零开始研究。如果不告诉他们已知前提，他们会重新查一遍"NPO 是否有豁免"，浪费 context 和时间，而且可能因为证据不同得出和 wiki 不一致的结论。

**"已知前提"让系统保持知识一致性**。

---

## 4. Six Domains：从已知前提出发分析

**时机**：六部执行阶段

**做什么**：

每个六部收到 dispatch context 时会看到"已知前提"部分。他们**必须**从这些前提出发，不能重新论证已确立的结论。

如果某个六部在研究中发现**新证据和 wiki 条目矛盾**，他们在报告中标注：

```
⚠️ Wiki conflict：
wiki 条目 "NPO 贷款无贷金业法豁免"（confidence 0.95）可能需要重新验证。
本次研究中发现新法规草案（2026-03 金融厅发布）提出了对符合特定条件 NPO 的部分豁免。
建议：在做本决策前，单独 session 验证该条目。
```

REVIEWER 看到这种标注会在总结报告中强调——这是**严重信号**，意味着系统知识过时了。

---

## 5. REVIEWER：一致性检查

**时机**：REVIEWER 在审六部报告时、审 PLANNER 计划时

**做什么**：

REVIEWER 检查**新结论**和现有 wiki 条目是否矛盾。

- **一致** → 不做处理
- **矛盾现有 wiki 条目（confidence < 0.5）** → 标注"建议更新 wiki 条目"
- **矛盾现有 wiki 条目（confidence ≥ 0.5）** → 在 Summary Report 中加警告：

```
⚠️ Wiki consistency：本决策的结论和已有知识矛盾：
[条目标题]（confidence [X]）at wiki/[path]
要么本次分析需要修订，要么 wiki 条目需要更新
```

REVIEWER **不会**自动否决（wiki 可能过时），但会把矛盾浮现出来让你意识到。

---

## 6. archiver：补充写入

**时机**：session adjourn（archiver Phase 2）

**做什么**：

archiver 在 session 结束时扫所有材料，对每个候选结论跑 6 条标准 + 隐私过滤器。通过的自动写入：

```
_meta/outbox/{session_id}/wiki/{domain}/{topic}.md
```

session 结束 git push 后，下次 Start Session RETROSPECTIVE 会把 outbox 的 wiki 文件移到正式的 `wiki/{domain}/` 目录，然后重新编译 INDEX.md。

### archiver 的特殊情况

- **矛盾现有条目** → 不新建文件，给被挑战条目 `challenges +1`
- **同 domain 同 topic 已存在** → 不覆盖，给旧条目 `evidence_count +1`
- **剥离隐私后结论塌了** → 丢弃，在 checklist 报告原因

---

## 7. AUDITOR：巡检 wiki 健康度

**时机**：RETROSPECTIVE 的 Housekeeping Mode 触发 AUDITOR 巡检（不是每次 session，是定期）

**做什么**：

AUDITOR 扫 `wiki/` 目录，查找：

- **过时条目**：`last_validated` > 180 天没被激活
- **低 confidence 长期停滞**：条目超过 60 天 confidence < 0.3 且无 evidence 增长 → 建议归档
- **矛盾积累**：条目 `challenges` 连续增长 → 建议你重新审视
- **知识盲区**：多个 session 都在研究同一领域但没产出 wiki 条目 → 可能有隐性共识没被抽取
- **标题违反"Title = Conclusion"原则** → 建议修订

AUDITOR 不修改 wiki，只在巡检报告中列出建议，由你在下次 session 决定处理。

---

## 8. DREAM：补充和深度连接

**时机**：session adjourn（archiver Phase 3）

**做什么**：

DREAM 在 3 天回顾中：

- **N3 阶段**：扫描 3 天活动，找 archiver Phase 2 遗漏的可复用结论
- **N3 阶段**：给现有 wiki 条目找新证据（update `evidence_count`）
- **REM 阶段**：跨 domain 连接——两个看起来无关的 wiki 条目之间有什么意外联系？

REM 的输出通常是 journal 中的洞察，不直接产出 wiki 条目（因为"连接"本身不符合 wiki 的"一结论一文件"原则）。但如果某个连接被反复印证，DREAM 可能提议把它写成新的 wiki 条目。

---

## 完整例子：一个决策从头到尾怎么用 wiki

**用户问**："我想评估在日本用 NPO 做小额贷款的可行性"

**Start Session（昨天）**：RETROSPECTIVE 编译 INDEX.md，其中有 `NPO 贷款无贷金业法豁免 (0.95)`

**ROUTER**：读 INDEX，发现高相关条目，告诉用户"已知此前提，你想：1. 在此基础上继续 2. 重新验证"。用户选 1。

**PLANNER**：规划详细评估步骤。

**REVIEWER**：审 PLANNER 方案，没有矛盾，通过。

**DISPATCHER**：把 `wiki/finance/lending-law-npo.md` 作为已知前提，分给 Finance / Legal / Risk Management 三个部。

**Six Domains 执行**：每个部都从"贷金业法必须遵守"出发，不再研究法律基础问题，专注于设计可执行的结构。

**REVIEWER 最终审查**：检查所有部的结论和现有 wiki 无矛盾。

**Summary Report**：给出决策建议，引用了 wiki 条目作为基础。

**archiver Phase 2**：从本次 session 提取候选结论——"NPO 小额贷款需要设立独立贷款子法人"是一个新的可复用结论，6 条标准都过、隐私过滤通过、2 个独立证据（本次方案 + 上次一个类似讨论），写入 `wiki/finance/npo-lending-structure.md`（confidence 0.3）。

**DREAM Phase 3**：回顾 3 天，发现本次讨论还印证了一个既有条目 "信托结构提供有限责任保护"，给那个条目 `evidence_count +1`。

**下次 Start Session**：INDEX.md 重新编译，新增 `NPO 小额贷款需要独立贷款子法人 (0.3)`。

**几个月后**：类似问题再次出现，ROUTER 扫 INDEX，发现 `NPO 小额贷款需要独立贷款子法人 (0.65)`（confidence 经过多次 session 累积上升），不用再讨论结构选择，直接进入细节。

**系统在积累经验**。这就是 wiki 的价值。
