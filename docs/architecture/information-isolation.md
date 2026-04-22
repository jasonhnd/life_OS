# 信息隔离原则

Life OS 的 16 个 agent 之间**不是共享上下文的**。每个 agent 作为独立 subagent 启动,只拿到**最小必要信息**。这是核心防 groupthink 和防决策污染的机制。

源: `pro/CLAUDE.md` / `pro/GEMINI.md` / `pro/AGENTS.md` 的 "Information Isolation" 章节。

---

## 完整信息表

每个 agent 收到什么、不收到什么:

| Agent | 收到 | 不收到 |
|-------|------|-------|
| RETROSPECTIVE | 用户消息 (housekeeping), `_meta/strategic-lines.md` + 全部项目的 strategic 字段 | 无限制 (它本身要做全盘扫描) |
| ARCHIVER | Summary Report + 各 agent 报告 + 会话对话摘要, 全部项目的 strategic 字段 | 其他 agent 的思考过程 |
| ROUTER | 用户消息 + RETROSPECTIVE 的 Pre-Session Preparation + `_meta/STRATEGIC-MAP.md` (编译产物) | — |
| PLANNER | Subject + 背景 + 用户消息 + 绑定项目的战略 context (仅 flows, 不含完整 map) | ROUTER 的分诊思路, 完整战略地图 |
| REVIEWER | 规划文件 or 六部报告 + 当前决策相关的 flow graph | 其他 agent 的思考过程, 完整战略地图 |
| DISPATCHER | 已批准的规划文件 | 思考过程 |
| 每个 Domain (六部) | 调度指令 + 背景 + 绑定项目的战略角色 (若存在) | 其他部门的报告, 完整战略地图 |
| AUDITOR | 完整工作流记录 | 无限制 (它要检查全流程) |
| ADVISOR | Summary Report + 用户消息 (自己读二脑历史数据) | 其他 agent 的思考过程 |

---

## 特殊: STRATEGIST 思想家子 subagent

STRATEGIST 启动 2-4 个思想家作为各自独立的 subagent。每个思想家 subagent 收到:
- 话题
- 自己的角色 (扮演指令)
- 在圆桌/辩论中: 上一位发言者的**摘要** (非全文、非思考过程)

思想家 subagent **不收到**:
- 其他思想家的完整输出
- 其他思想家的研究过程 (🔎/💭/🎯)

**为什么**: 如果让苏格拉底看到哲学同行的完整发言, 他会被「污染」,开始互相对话而不是真正用自己的方法思考用户的问题。保持独立,每人用自己的套路对用户的问题。

---

## 特殊: COUNCIL 辩论方 subagent

COUNCIL 里每个辩论部门作为独立 subagent 启动。各自收到:
- 辩论话题
- **自己的**原报告
- 对方的**立场摘要** (第一轮之后)

**不收到**:
- 对方的完整报告
- 对方的研究过程

---

## 为什么思想家 subagent 只得到摘要

核心考虑: **防止 groupthink 和 echo chamber**。

### groupthink 是什么

一群人(或一群 agent)在持续互动中, 逐渐收敛到同一个观点,即使那个观点未必是对的。原因:
- 人倾向于认同权威和多数
- 反对意见的表达成本随时间上升
- 信息同步反而让思维同步

### Life OS 怎么用信息隔离反制

1. **同时同步启动**(parallel), 不让任何 agent 等待其他 agent 的输出。六部分析同时开工,各自从零做研究。
2. **互相看不到研究过程**(🔎/💭/🎯), 只看得到最终结论。这样 AUDITOR 才能真正评各自的工作质量,而不是看到互相借鉴后的「趋同作品」。
3. **REVIEWER 和 DISPATCHER 只拿规划文件,不拿思考**。思考会诱导审议者「理解作者意图」, 但审议的意义就在于**不懂作者意图**也能判断计划是否立得住。

### 具体例子

假设用户问「该不该辞职创业」:

- FINANCE 单独分析: 算 runway、算启动资金、算机会成本 → 打 5 分 🟡
- EXECUTION 单独分析: 算项目可行性、算市场窗口 → 打 8 分 🟢

**如果 FINANCE 看到 EXECUTION 的 8 分**: 会自我怀疑「是不是我太保守」, 把 5 分改成 6 分。
**隔离之后**: FINANCE 坚持 5 分, REVIEWER 看到 3 分差异 → 触发 COUNCIL 3 轮辩论 → 用户看到真实的跨维度冲突 → 决策质量提升。

**groupthink 会抹平冲突, 隔离会放大冲突, 而冲突才是决策的价值所在。**

---

## 如何执行信息隔离

### 技术层面

1. **编排协议文件明确规定传什么**。例如 `pro/CLAUDE.md` Step 4 写明 "Launch dispatcher, passing in the approved planning document. **Do not pass** the PLANNER/REVIEWER's thought processes."
2. **subagent API 本身就隔离**。Claude/Gemini/Codex 的 subagent 都是独立 context window, 不共享父 agent 的 context。只能通过函数参数显式传入。
3. **agent 文件里写 `tools:` 限制**。例如 REVIEWER 只有 `tools: Read`, 不能 Write,强迫它专心做判断,不能偷偷改文件。

### 流程层面

1. **每个 agent 收到的输入是函数式的**, orchestrator 构造输入 → launch → 拿输出。输入不包含历史。
2. **AUDITOR 有权限看全局**。它是「监察者」, 必须能对比各 agent 的独立输入和最终输出, 判断有没有泄漏。
3. **违规可被检测**: 如果 FINANCE 的报告里出现「我看到 EXECUTION 说...」这种话, AUDITOR 会立刻标记 "信息泄漏"。

### 反模式检测

AUDITOR 抓的典型泄漏症状:
- 某部评分莫名其妙一致 (没冲突的跨部决策是反直觉的)
- 某部的报告用了其他部的专业词汇 (说明它看了其他部的内容)
- REVIEWER 的 Veto 理由引用了具体领域细节 (应该只看规划的结构性问题)
- STRATEGIST 的某个思想家引用了另一思想家的原话 (严重违反角色扮演)

---

## 防泄漏的具体设计细节

### SOUL Reference 的 3 层分级

REVIEWER 引用 SOUL 时有严格分级 (参见 `pro/agents/reviewer.md`):
- core (confidence ≥ 0.7): **全部**引用
- secondary (0.3 ≤ c < 0.7): 选语义相关的 **top 3**, 列出评估过但未选的其他维度
- emerging (c < 0.3): 只计数, 不展示

这样设计是为了: ADVISOR 看 REVIEWER 的 SOUL Reference 输出时, 能判断「选择质量」 — 选了哪些、为什么、有没有漏掉相关高优先的。

### wiki 作为「已知前提」注入

DISPATCHER 在分派任务给领域时, 如果 ROUTER 标记过相关 wiki 条目, 会把**那些条目的全文**注入领域 context, 并明确标记「📚 已知前提 (已确立知识, 从此出发, 不用重新推导)」。

这**不是**信息泄漏, 因为 wiki 是所有部共享的「公共知识」, 不是某个具体部的报告。

### strategic context 的分层

三类 agent 看到不同深度的 strategic context:
- ROUTER: 编译过的 `_meta/STRATEGIC-MAP.md` (完整地图)
- PLANNER: 绑定项目的战略 context + 相关 flow (不是完整地图)
- REVIEWER: 当前决策相关的 flow graph (不是完整地图)
- Domain: 绑定项目的战略角色 (如 "critical-path for line X")

越下游的 agent, 看到的战略 context 越聚焦。防止领域 agent 因为战略考虑「把视野扩得太大」, 偏离自己的专业判断。

---

## 隔离失败的场景 (要特别防)

### 场景 1: 主上下文污染

**表现**: 某个 agent 实际上没在 subagent 里跑, 而是在主 context (ROUTER 的上下文) 里被模拟执行。

**后果**: 它看到的是 ROUTER 的全部历史对话,包括其他 agent 的产出, 等于没隔离。

**防范**: 3 份编排文件都写了 "Pro environment forces real subagents. Single-context role simulation is prohibited. HARD RULE."

**检测**: AUDITOR 如果在 workflow 记录里发现某 agent 的输出没有单独 launch 事件, 标记 "single-context simulation violation"。

### 场景 2: archiver 在主上下文执行 Phase

**表现**: 用户说「退朝」, ROUTER 在主上下文开始扫描 wiki 候选、问用户、然后才启动 archiver。

**后果**: Phase 2 的候选扫描被 ROUTER 看到了, ROUTER 可能带着偏见把「用户会喜欢的」候选传给 archiver, 污染 auto-write 决策。

**防范**: `pro/agents/archiver.md` 里有 Subagent-Only Execution 的 HARD RULE, 并且 archiver 自己会在 Phase 2 开始前做 "self-check"。

**检测**: AUDITOR 看 workflow 记录, 如果 ROUTER 在说「退朝」后到 archiver 启动之间有任何内容扫描, 标记违规。

### 场景 3: Notion MCP 意外暴露信息

**表现**: Notion sync 在 orchestrator 上下文执行, 但 orchestrator 不小心在 Notion 写入时包含了其他 agent 的思考过程。

**防范**: Step 10a 的模板明确规定只写 4 类内容: Status / Todo / Working Memory / Inbox。不是整个 session 记录。

---

## 总结: 为什么信息隔离是系统核心

Life OS 不是「16 个 agent 协作」, 而是「16 个独立判断 + 1 个 orchestrator 汇总」。

如果放松隔离, 系统会迅速退化为「1 个主上下文扮演 16 个角色」 —— 看上去工作了, 但失去了跨角色的真实冲突和质量检验。

**信息隔离不是实现细节, 是架构本质。**
