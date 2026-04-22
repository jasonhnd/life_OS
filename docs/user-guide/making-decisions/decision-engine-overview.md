# 决策引擎总览 · Draft-Review-Execute 十一步工作流

> 本文档是作者自用参考。写给懂系统内部的人看，不铺垫，直接讲。

## 为什么要 11 步

Life OS 的核心不是"跟 AI 聊天"，而是**把一次决策拆成独立、隔离、可审计的多个环节**。这样做的理由只有一个：防止单一视角的偏见污染整个决策链。

传统和 AI 对话：你说一句 → AI 回一段 → 你觉得有道理 → 做了。问题在于 AI 的整条推理链都在同一个上下文里，前面的假设会偷偷塑造后面的结论。

Life OS 的做法：每个角色是独立 subagent，信息只在必要处传递，角色之间看不到对方的思考过程。这就是三阶段工作流（Draft / Review / Execute）的本质：不是"流程仪式"，而是**信息隔离**。

## 三阶段结构

```
┌─────────── Draft（起草） ───────────┐
│ 0. 预备会（ROUTER + RETROSPECTIVE 并行）
│ 1. ROUTER 分诊
│ 1E. 快车道 (Express Analysis · 可选)
│ 2. PLANNER 规划
│ 3. REVIEWER 初审（含封驳循环）
└────────────────────────────────────┘
             ↓
┌─────────── Execute（执行） ──────────┐
│ 4. DISPATCHER 分配
│ 5. 六领域并行执行
└────────────────────────────────────┘
             ↓
┌─────────── Review（复审） ──────────┐
│ 6. REVIEWER 终审（可能触发 COUNCIL）
│ 7. ROUTER 奏折
│ 8. AUDITOR 审计
│ 9. ADVISOR 建议
│ 10. ARCHIVER 归档（归档+知识提取+DREAM+同步）
│ 11. STRATEGIST（可选，问你要不要）
└────────────────────────────────────┘
```

每一步存在都有理由。下面逐一讲。

## 11 步各自存在的理由

### 0. 预备会 · ROUTER + RETROSPECTIVE 并行启动

**为什么并行不串行**：ROUTER 需要响应用户，RETROSPECTIVE 需要读 second-brain / Notion / user-patterns / wiki / 版本检查 / 平台检测。如果串行，用户要等整个 I/O 链路。并行后 ROUTER 拿到上下文再回话，首次响应含完整 Pre-Session Preparation。

**为什么不能跳过**：这是会话绑定的时机。没有 Pre-Session Preparation，ROUTER 就不知道绑定到哪个项目，后续所有读写都可能越界。

### 1. ROUTER 分诊

**存在理由**：不是所有请求都值得开全套朝议。ROUTER 判断五种路径之一：
- 直接处理（聊天、查询、翻译、记笔记）
- 快车道（域级分析但不涉及决策）
- 全朝议（有决策、有权衡、有不可逆）
- STRATEGIST（迷茫、价值观、存在问题）
- 复盘（RETROSPECTIVE · Review Mode）

**隔离**：ROUTER 的"分诊理由"不传给 PLANNER。PLANNER 只拿到 Subject + 背景摘要 + 用户原话。为什么？因为 ROUTER 可能猜错了用户真正在问什么——不让 PLANNER 继承这个猜测，PLANNER 就能独立判断。

### 1E. 快车道（Express Analysis）

**存在理由**：不是所有分析请求都需要决策。"帮我分析这份合同的风险"、"总结下项目进度"，这类请求不需要 PLANNER / REVIEWER / DISPATCHER / AUDITOR / ADVISOR。直接拉 1-3 个领域 agent 做分析，报告以**简报**形式呈现（不是奏折——没有评分、没有正式审计日志）。

**判断标准**：有没有要做的决策？有 → 全朝议。没有 → 快车道。

完成后 ROUTER 会问："这是快车道分析。要不要升级成全朝议？" 用户说要 → 进入第 2 步。

### 2. PLANNER 规划

**存在理由**：把 Subject 拆成 3-6 个维度，指派给对应领域，定义质量标准。不是所有决策都用六领域全套——PLANNER 根据场景选领域。

**隔离**：PLANNER **只**收到 Subject + 背景摘要 + 用户原话。拿不到 ROUTER 的推理过程。这样 PLANNER 可以自己判断哪些维度被忽略了、有没有隐性风险。

SOUL.md 参考：如果存在高置信度维度（≥0.6）且与本次 Subject 相关但用户没提，PLANNER 会主动加一个维度，标注"📌 Added based on SOUL.md"。

### 3. REVIEWER 初审

**存在理由**：这是**封驳机制**。REVIEWER 只有 Read 权限，专职判断。REVIEWER 审 PLANNER 的规划文档：维度全不全？分工合不合理？有没有明显盲区？情感维度考虑了吗？

三种结果：
- ✅ Approved → 进入第 4 步
- ⚠️ Conditionally Approved（附加条件）→ 条件写进规划文档，进入第 4 步
- 🚫 Veto → 封驳循环（最多 2 次）

**隔离**：REVIEWER 拿不到 PLANNER 的思考过程，只看最终规划文档。封驳机制最多 2 轮，第 3 轮必须出 Approved 或 Conditionally Approved——防止陷入死循环。

### 4. DISPATCHER 分配

**存在理由**：PLANNER 规划是战略，DISPATCHER 把它变成执行指令。关键工作是**依赖检测**——哪些领域之间有数据依赖（如 finance → execution 需要预算上限），把它们分到 Group A / Group B 按顺序跑；没依赖的全扔到 Group A 并行跑。

还负责**文件写入冲突规则**：多个领域并行时，每个只能改自己负责的文件；要改同一个文件的，DISPATCHER 排成串行。

**隔离**：DISPATCHER 只看已批准的规划文档，不碰 PLANNER / REVIEWER 的思考过程。

### 5. 六领域并行执行

**六领域功能 ID**：
- `people` — 人际（人脉、团队、关系）
- `finance` — 财务（钱、预算、投资）
- `growth` — 成长（学习、表达、品牌）
- `execution` — 执行（行动、调度、运营）
- `governance` — 治理（规则、风控、法务）
- `infra` — 基建（硬件、健康、住所）

**HARD RULE**：每个领域报告到达时**必须立即完整展示给用户**（包括研究过程 🔎/💭/🎯）。不能等全部完成再汇总。不能压缩成摘要。不能省略研究过程。

理由：用户要看每个领域**独立**的思路，不是合成的"AI 观点"。如果压缩了，权重判断、分歧点都看不到了。

**隔离**：每个领域只拿到自己的指令 + 背景材料 + 质量标准，看不到其他领域的报告。这样同领域专家才是真的"独立"判断。

### 6. REVIEWER 终审

**存在理由**：再审一次，但这次看的是执行结果。重点：分析有没有实质内容？评分和分析一致吗？有没有未解决的矛盾？

**触发 COUNCIL**：如果两个领域分差 ≥ 3（比如 finance 给 4/10，execution 给 8/10），或者一个说"做"另一个说"不做"——自动拉 COUNCIL 做 3 轮辩论。

详见 [the-veto-loop.md](./the-veto-loop.md) 和 [the-council.md](./the-council.md)。

### 7. ROUTER 奏折（Summary Report）

**存在理由**：把六份领域报告 + REVIEWER 判断 + （可选）COUNCIL 辩论结果，合成一份**整体评分 + 分层结论 + 领域评分表 + 行动项 + 审计日志 + 运营报告**的奏折。

这是用户主要的决策依据。结构详见 [reading-the-summary-report.md](./reading-the-summary-report.md)。

### 8. AUDITOR 审计

**存在理由**：自动触发，不能跳过。AUDITOR 审整个流程记录：有没有违反状态机？有没有跳步骤？有没有偷懒（比如 REVIEWER 应该封驳但没封）？违规会记录进 user-patterns.md。

AUDITOR 还有另一个模式：Patrol Inspection，由 RETROSPECTIVE 在 housekeeping 时触发，巡查 wiki / SOUL / 决策历史的健康度。

### 9. ADVISOR 建议

**存在理由**：自动触发。ADVISOR 读 Summary Report + 用户原话，再自己读 second-brain 历史数据，给一句简短、基于历史模式的建议。重点是**和 SOUL.md 的 evidence_count / challenges 联动**——每次决策后更新 SOUL 的证据积累，高置信度维度持续加固，被挑战的维度降权。

### 10. ARCHIVER 归档（四阶段）

**存在理由**：把会话成果封存到 second-brain + 同步到各后端。HARD RULE：作为一个 subagent 端到端跑完 4 个阶段，主上下文不插嘴。

四个阶段：
1. **归档** — decisions / tasks / journal → outbox
2. **知识提取** — 扫描所有会话材料，符合严格条件的 wiki 和 SOUL 条目自动写入（6 wiki 条件 + 隐私过滤；SOUL 条件 + 低初始置信度）
3. **DREAM** — 3 晚深度回顾（N1-N2 整理，N3 巩固，REM 创造性连接）
4. **同步** — git push + Notion 同步（4 个具体操作）

Notion 同步在第 10a 步由 orchestrator（主上下文）执行，因为 archiver 无法访问 Notion MCP 工具。

### 11. STRATEGIST · 群贤堂（问你要不要）

**存在理由**：当 ROUTER 检测到**抽象思考需求**（迷茫、价值观、"我到底想要什么"），必须问用户："要不要启动 STRATEGIST 跟历史思想家对话？" 不擅自启动，只问。

STRATEGIST 不走 Draft-Review-Execute，独立运作：18 领域思想家索引 → 用户选人选模式（一对一 / 圆桌 / 辩论）→ 每位思想家是独立 subagent → 结束时每人赠言 → STRATEGIST 总结 → 写入 journal。

## 信息隔离原则 · 谁看得到什么

| 角色 | 能看到 | 看不到 |
|------|--------|--------|
| RETROSPECTIVE | 用户原话、所有项目战略字段 | 无限制 |
| ROUTER | 用户原话 + RETROSPECTIVE 预备 + STRATEGIC-MAP 编译品 | — |
| PLANNER | Subject + 背景 + 用户原话 + 绑定项目的战略上下文（仅流） | ROUTER 的推理、完整战略地图 |
| REVIEWER | 规划文档或六领域报告 + 当前决策相关流图 | 其他角色的思考过程、完整战略地图 |
| DISPATCHER | 已批准的规划文档 | 思考过程 |
| 各领域 | 自己的指令 + 背景 + 绑定项目的战略角色（如果有） | 其他领域的报告、完整战略地图 |
| AUDITOR | 完整流程记录 | 无限制 |
| ADVISOR | Summary Report + 用户原话（自己读 second-brain） | 思考过程 |
| ARCHIVER | Summary Report + 所有报告 + 会话摘要 + 所有战略字段 | 其他角色的思考过程 |

**这张表就是决策引擎的安全模型**。任何违反都会被 AUDITOR 标红。

## 状态机 · 哪些跳转合法

| 当前状态 | 可转入 | 不能跳到 |
|----------|--------|----------|
| 预备会 | ROUTER 分诊 | 其他一切 |
| ROUTER 分诊 | PLANNER / 直接处理 / 快车道 / STRATEGIST / 复盘 | 六领域（除非走快车道） |
| 快车道 | 域执行 → 简报 → 结束或升级到 PLANNER | REVIEWER / AUDITOR / ADVISOR |
| PLANNER 规划 | REVIEWER 初审 | DISPATCHER / 六领域 |
| REVIEWER 初审 | DISPATCHER / 封驳回 PLANNER | 六领域（必须过分配） |
| DISPATCHER 分配 | 六领域执行 | Summary Report（必须先执行） |
| 六领域执行 | REVIEWER 终审 | Summary Report（必须先复审） |
| REVIEWER 终审 | Summary Report / COUNCIL | ARCHIVER（必须先出奏折） |
| Summary Report | AUDITOR | ARCHIVER（必须先跑 AUDITOR） |
| AUDITOR | ADVISOR | ARCHIVER（必须先跑 ADVISOR） |
| ADVISOR | ARCHIVER | — |

任何违规都是 process error，AUDITOR 必须标记。这张表就是防止"随意跳步"的形式化保障。

## 真实例子 · 一次"是否辞职创业"的全流程

1. **预备会**：RETROSPECTIVE 拉出历史 — Notion 里有 3 篇相关笔记，user-patterns 显示你过去半年提过 4 次"不想干了"
2. **ROUTER 分诊**：这是决策问题（A 或 B + 不可逆 + 情绪强）→ 全朝议。启动意图澄清，3 轮。
3. **PLANNER 规划**：拆成 6 维度（财务安全、技能匹配、家庭影响、创业方向、法律风险、健康承受）。指派六领域全部启动。SOUL 参考加一维"家庭优先于事业（0.8 confidence）"。
4. **REVIEWER 初审**：Conditionally Approved — 附加条件"必须包含 10/10/10 Regret Test"
5. **DISPATCHER 分配**：finance + growth + people 并行 Group A；execution + governance + infra 并行 Group B（依赖 finance 的现金流结果）
6. **六领域执行**：6 份报告逐一展示。finance 说"存款能撑 18 个月，可接受"，execution 说"你缺一个联合创始人，单干风险高"
7. **REVIEWER 终审**：finance 给 7/10，execution 给 3/10 — 分差 4 分，触发 COUNCIL
8. **COUNCIL**：3 轮辩论，finance vs execution。裁决："财务可承受，但执行端风险集中在'单干'这一点，不是'能不能创业'，是'现在还是再等半年'"
9. **ROUTER 奏折**：整体评分 6/10，"条件成熟度 70%，建议延迟 3-6 个月找联创"
10. **AUDITOR**：流程无违规
11. **ADVISOR**：基于历史"你 4 次提过想辞职但都没动，这次的触发是什么？" — 建议先列"不辞职时每天最难受的 3 件事"
12. **ARCHIVER**：归档决策文件、自动写入一条 SOUL 维度候选（confidence 0.3）、DREAM 触发、同步到 Notion

这就是 11 步干完的事。

## 什么时候需要读哪一篇

- 不清楚为什么要澄清三轮 → [intent-clarification.md](./intent-clarification.md)
- 想知道什么时候走快车道 → [express-vs-full-analysis.md](./express-vs-full-analysis.md)
- 收到奏折不知道看哪里 → [reading-the-summary-report.md](./reading-the-summary-report.md)
- 被 REVIEWER 封驳了不知道什么意思 → [the-veto-loop.md](./the-veto-loop.md)
- COUNCIL 自动拉起来了想知道发生什么 → [the-council.md](./the-council.md)
- 不知道自己这个问题属于哪个场景 → [12-standard-scenarios.md](./12-standard-scenarios.md)
