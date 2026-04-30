---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# 11 步编排协议 (文档)

这是 `pro/CLAUDE.md` / `pro/GEMINI.md` / `pro/AGENTS.md` 里 11 步工作流的**文档化讲解**, 不是指令本身。每步做什么、输入是什么、输出是什么、由哪个 agent 执行。

源文件是 `pro/CLAUDE.md`(Claude)/ `pro/GEMINI.md`(Gemini)/ `pro/AGENTS.md`(Codex),三份结构等价。

---

## 流程全图

```
用户发消息
    ↓
[Step 0] ROUTER + RETROSPECTIVE 并发启动
    ↓
[Step 1] ROUTER 分诊 → 5 种走向
    ↓
    ├─ 直接回 → 流程结束
    ├─ Express (1E) → 1-3 部并发 → 简报 → 流程结束
    ├─ 完整决策 (意图澄清 2-3 轮后) → Step 2
    ├─ STRATEGIST (询问用户) → strategist 独立流程
    └─ Review → retrospective Mode 2
    ↓
[Step 2] PLANNER 规划
    ↓
[Step 3] REVIEWER 审议 (审规划)
    ↓
    ├─ Approved → Step 4
    ├─ Conditionally Approved → 附加条件, Step 4
    └─ Veto → 回 PLANNER 改(最多 2 次, 第 3 次必须过)
    ↓
[Step 4] DISPATCHER 调度
    ↓
[Step 5] 六部并行执行 (逐部展示, 不等全部完成)
    ↓
[Step 6] REVIEWER 终审 (审执行)
    ↓
    └─ 若部门评分差 ≥3 或正反对立 → COUNCIL 3 轮辩论
    ↓
[Step 7] Summary Report (ROUTER 汇总)
    ↓
[Step 8] AUDITOR (Decision Review)
    ↓
[Step 9] ADVISOR (行为观察)
    ↓
[Step 10] ARCHIVER 4 阶段 (subagent 独立运行)
    ↓
[Step 10a] Notion Sync (回到 orchestrator 主上下文)
    ↓
会话结束

[Step 11] STRATEGIST 独立分支 — 与决策流程并列, 不参与上述链路
```

---

## Step 0: Pre-Session Preparation

**触发**: 用户发送会话第一条消息。

**执行**: 同时启动两个 agent(并发):
- `router` — 准备回复用户
- `retrospective` (Mode 1 Housekeeping) — 在后台准备 context

**RETROSPECTIVE 做的事**:
- 读 `_meta/config.md` 取后端列表和上次同步时间戳
- 对每个可用后端做 full sync pull
- 扫 `_meta/outbox/` 合并未合并的会话
- 读 `user-patterns.md`, `wiki/INDEX.md`, `_meta/STRATEGIC-MAP.md`, `_meta/STATUS.md`
- 读 `_meta/lint-state.md` — 如果 >4h, 触发 AUDITOR 轻量巡视
- ReadProjectContext(绑定项目)
- 版本检查 + 平台检测

**输出**: "Pre-Session Preparation" 包交给 ROUTER。

**HARD RULE**: ROUTER 的第一条回复**必须包含** Pre-Session Preparation 块。

---

## Step 1: ROUTER Triage

**输入**: 用户消息 + RETROSPECTIVE 准备的 context。

**执行**: ROUTER 评估用户需求, 做 5 选 1 分诊。

**5 种走向**:

| 走向 | 条件 | 后续 |
|------|------|------|
| 直接回 | 闲聊、情绪、翻译、简单问题、单步任务 | 流程结束 |
| Express (1E) | 需要专业分析但**不涉及决策** | 跳到 Step 1E, 启动 1-3 部, 不走 Step 2-4/6-9 |
| 完整决策 | 有选择、有权衡、大额钱、不可逆 | 2-3 轮意图澄清 (HARD RULE), 然后 Step 2 |
| STRATEGIST | 用户表达抽象思考需求 | 问用户要不要启动, 用户 yes 才启动, 独立于主流程 |
| Review | 用户说「复盘」 | Launch retrospective Mode 2 |

**意图澄清 (HARD RULE 不可跳过)**:
- Round 1: 一句话复述核心问题, 问「我这样理解对吗?」
- Round 2: 针对该问题类型最关键的空白提一个尖锐问题
- Round 3 (如需): 确认约束

**情绪分离协议**: 当情绪和决策纠缠时, 先承认情绪 (1 句话), 然后「先把焦虑放一边, 单看事实是什么」。用户情绪激动时**不启动**完整决策。

---

## Step 1E: Express Analysis Path

**输入**: 用户问题 + 背景 (ROUTER 判断后确认)。

**执行**: ROUTER 直接 Launch 1-3 个相关领域 subagent, 各自跑完整研究流程 (🔎/💭/🎯)。

**不触发**: PLANNER / REVIEWER / DISPATCHER / AUDITOR / ADVISOR。

**输出**: ROUTER 汇总为**简报** (不是 Summary Report — 无评分、无审计日志)。

**询问升格**: 简报后 ROUTER 问「这是快速分析, 要不要走完整决策?」 用户 yes 升格到 Step 2。

---

## Step 2: PLANNER Planning

**输入**: Subject + 背景摘要 + 用户原消息 (**不传** ROUTER 的分诊思路)。

**执行**: `planner` subagent 独立运行。
- 理解 Subject 真正的 intent
- 分解 3-6 个维度 (不超过 6)
- 指派领域 (主责 / 协助), 每部必须有一行理由
- 定义质量标准 (可测量)
- 检查 SOUL.md (confidence ≥ 0.6), 若高置信维度相关但用户没提, 加为强制维度
- 检查 Strategic Map, 若项目有 flows_to, 加「跨项目影响评估」维度

**输出**: 规划文件 (列出维度 + 主责领域 + 质量标准 + 风险提示 + 建议执行方式)。

---

## Step 3: REVIEWER Deliberation (审规划)

**输入**: PLANNER 的完整规划文件 (**不传** PLANNER 的思考过程)。

**执行**: `reviewer` subagent 独立运行。
- 维度是否完整
- 分工是否合理
- 有无明显盲点
- 情感维度审查 (情绪/关系/价值观/10-10-10 regret test)
- SOUL Reference 3 层引用 (core 全引, secondary top 3, emerging 只计数)
- Wiki 一致性检查
- Strategic Map 一致性检查
- Red Team Review (假设计划会失败, 找最脆弱假设 / 最靠运气的步骤 / 被淡化的风险)

**三种结果**:
- ✅ Approved → Step 4
- ⚠️ Conditionally Approved → 附加条件到规划文件, Step 4
- 🚫 Veto → 回 PLANNER 改

**Veto Correction Loop**: 最多 2 次封驳, 第 3 次必须批准或有条件批准。

**Veto 格式** (必须 4 字段):
- Failed dimension
- Core problem (1 句)
- Revision direction (具体)
- Missing information

---

## Step 4: DISPATCHER Dispatch

**输入**: 已批准的规划文件 (**不传** PLANNER/REVIEWER 的思考过程)。

**执行**: `dispatcher` subagent 独立运行。
- 扫描 planner 的规划, 检测跨部数据依赖
- 无依赖 → 全部并行 (Group A)
- 有依赖 → Group A 先跑, Group B 依赖 Group A 完成后的数据点 (非全文)
- 如果 router 标记过相关 wiki 条目 → 注入领域 context, 标「📚 已知前提 (wiki 已有知识, 从此出发, 不用重新推导)」

**输出**: 调度令 (每部具体指令 + 可交付物格式 + 质量标准)。

---

## Step 5: Six Domains Execution

**输入**: DISPATCHER 的调度令 + 各部自己的指令 + 背景材料 (**不传** 其他部的报告)。

**执行**: 各部作为独立 subagent 并行跑。

**HARD RULE · 逐部展示**: 每部报告返回后, **立即全文展示给用户** (含研究过程 🔎/💭/🎯)。不等全部完成、不压缩、不省研究过程。

**文件写入冲突规则**: 六部并行时, 每部只能改自己辖区的文件。需要改同一文件的部, DISPATCHER 安排串行。

**重做机制**: 如果某部报告明显没实质内容, 可以让它重做一次 (最多 1 次)。

---

## Step 6: REVIEWER Final Review (审执行)

**输入**: 六部全部报告 (**不传** 各部内部思考过程)。

**执行**: `reviewer` subagent 第二次调用。
- 分析是否有实质内容
- 评分是否与分析一致 (说「严重风险」却打 7 分 → 标记)
- 有无未解决的矛盾
- SOUL 一致性再次检查

**COUNCIL trigger**: 若检测到部门评分差 ≥3 或一部说「做」另一部说「不做」 → 启动 `council` 3 轮辩论。

---

## Step 7: Summary Report

**执行**: ROUTER 汇总。

**格式**:
```
Summary Report: [Subject]

Overall Rating: [X]/10 — [一句结论]

Must Address: [各部发现的汇总]
Needs Attention: [...]
Room for Improvement: [...]

Domain Ratings:
| Domain | Dimension | Score | One-liner |

Action Items:
1. [具体行动] — 截止日 — 主责领域

Audit Log: [各阶段简记]

Operations Report:
- Total Time
- Model
- Agent Calls
- Vetoes
- COUNCIL: 触发/未触发
```

---

## Step 8: AUDITOR (Decision Review, 自动)

**输入**: 完整工作流记录。

**执行**: `auditor` subagent, Decision Review Mode。
- 不评决策本身, 只评 agent 工作质量
- planner 分解质量、reviewer 审议深度、各部报告实质性、评分诚实度、有无跳步
- 重点抓: 全 7-8 的面子分、分析 vs 评分不一致、REVIEWER 从不封驳

**输出**: 整体评估 + 表现好的角色 + 表现差的角色 + 过程问题 + 改进建议。

---

## Step 9: ADVISOR (自动)

**输入**: Summary Report + 用户原消息 (ADVISOR **自己从 second-brain 读** 历史数据)。

**执行**: `advisor` subagent。
- 认知偏差扫描
- 情绪/状态检测
- 行为模式追踪 (承诺跟进、维度回避、决策速度、矛盾行为、目标漂移)
- 决策质量信号 (外归因、信息茧房、备选盲区、缺他者视角、沉默维度)
- 正向信号 (至少 1 条正面观察 per 3 条批评)

**SOUL Runtime**:
- 每个 SOUL 维度评 support/challenge/neutral
- 写 evidence/challenge delta 到 outbox
- 检测新维度 (≥2 证据 + 不被覆盖 → auto-write, confidence 0.3, What SHOULD BE 留空)
- 冲突检测 (最近 3 决策都被 challenge → 标 conflict)

**输出**: 行为建议 + 量化信号 + 模式更新建议 + SOUL Delta 块。

---

## Step 10: ARCHIVER (subagent, HARD RULE)

**HARD RULE**: ARCHIVER 只能作为 subagent 运行,**永远不能**在主上下文执行。

**ROUTER 输出模板 (必须严格遵守)**:
```
📝 [theme: archiver display name] — Starting archive flow (4 phases)...
[Launch archiver subagent here]
```

ROUTER **禁止**:
- 在主上下文扫描 wiki/SOUL/strategic 候选
- 问用户「要保存哪些?」
- 在 Phase 之间插入对话
- 在主上下文做文件移动 / git commit / Notion 写入

**输入**: Summary Report + AUDITOR 报告 + ADVISOR 报告 + 会话对话摘要 (ROUTER 处理过的话题 + Express 分析结果 + STRATEGIST 摘要)。

**4 个 Phase**:

1. **Phase 1 · Archive**: decisions/tasks/journal → `_meta/outbox/{session_id}/`
2. **Phase 2 · Knowledge Extraction**: 扫全部会话材料, auto-write wiki (6 criteria + 隐私过滤) + SOUL (criteria + confidence 0.3)
3. **Phase 3 · DREAM**: 最近 3 天深度回溯 (N1-N2 整理, N3 固化, REM 创造性连接 + 10 个 auto-trigger 检测)
4. **Phase 4 · Sync**: git add outbox + commit + push (**不做** Notion sync)

**输出**: Completion Checklist (每一项必须有具体值, 不接受 "TBD" / 空白)。

---

## Step 10a: Notion Sync (Orchestrator, HARD RULE)

**为什么在 orchestrator 做**: archiver subagent 无法访问 Notion MCP 工具 (环境相关, 不能在 agent frontmatter 声明)。

**执行**: ARCHIVER 返回 Completion Checklist 后, **orchestrator (主上下文)** 用该 session 可用的 Notion MCP 工具执行:

```
a. 🧠 Current Status page: 用最新 STATUS.md 内容覆盖
b. 📋 Todo Board: 同步本会话 tasks (new → create, completed → check off)
c. 📝 Working Memory: 写本会话摘要 (subject, conclusions, action items)
d. 📬 Inbox: 标记已处理项为 "Synced"
e. Notion MCP 不可用 → 报告: "⚠️ Notion sync failed — mobile will not see updates"
f. 某一项失败 → 报告具体哪项, 继续其他
```

**HARD RULE**: 不能静默跳过。不能说「Notion MCP 未连接」而不真的尝试调用工具。

---

## Step 11: STRATEGIST (独立分支, 询问用户)

**不走决策流程**。ROUTER 识别到抽象思考需求时, 必须问「要不要启动翰林院?」用户 yes 才启动。

**流程**:
1. Launch `strategist` (moderator)
2. 询问用户目的
3. 展示 18 领域思想家索引 + 推荐
4. 用户确认 → 把每个选中思想家作为**独立 subagent** 启动
5. 对话模式 (一对一 / 圆桌 / 辩论)
6. 结束: 每位思想家给 parting word → STRATEGIST 汇总 → 写 `_meta/journal/{date}-strategist-{slug}.md`

**信息隔离**: 每个思想家 subagent 只拿话题 + 自己的角色。圆桌/辩论时, moderator 在思想家之间传**发言摘要** (不是全文、不是思考过程)。

---

## Wiki / SOUL / Strategic Map 融入流程

这三个系统在多步里都会被读写, 不是一个单独的 step:

- **Wiki**: RETROSPECTIVE 在 start 时编译 `wiki/INDEX.md`; ROUTER 在路由时读 index; DISPATCHER 把相关 wiki 条目作为已知前提传给领域; REVIEWER 检查冲突; AUDITOR 巡视 wiki 健康
- **SOUL**: REVIEWER 每个决策必引 (HARD RULE); ADVISOR 每次决策更新 evidence/challenge; ARCHIVER 结束时 auto-write 新维度 (confidence 0.3, What SHOULD BE 留空); RETROSPECTIVE 下次 start 读最新 snapshot 算 trend
- **Strategic Map**: RETROSPECTIVE 在 start 时从 `_meta/strategic-lines.md` + 各项目 index.md 的 strategic 字段编译 `_meta/STRATEGIC-MAP.md`; ROUTER/PLANNER/REVIEWER 读这份编译产物
