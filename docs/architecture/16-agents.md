# 16 个 Agent 完整清单

全部 16 个 subagent 的 engine ID、职能、触发条件、工具权限、model、文件路径。

**所有 agent 都用 `model: opus`**(pro/agents/*.md 里 frontmatter 固定是 opus;跨平台时由各自的编排文件映射到该平台最强模型)。

---

## 总表

| # | Engine ID | 中文名(三省六部主题) | 功能 | 触发方式 | 工具权限 | Agent 文件 |
|---|-----------|-------------------|------|---------|---------|-----------|
| 1 | `router` | 丞相 | 入口路由、意图澄清、收件箱 | 每条消息 | Read, Grep, Glob, WebSearch, Write | `pro/agents/router.md` |
| 2 | `planner` | 中书令 | 规划 + 任务分解 | ROUTER 升格 | Read, Grep, Glob, WebSearch | `pro/agents/planner.md` |
| 3 | `reviewer` | 门下侍中 | 审议 + 情感审查 + 封驳权 | 规划后 + 执行后 | Read | `pro/agents/reviewer.md` |
| 4 | `dispatcher` | 尚书令 | 下达执行令 | 审议通过后 | Read, Grep, Glob | `pro/agents/dispatcher.md` |
| 5 | `people` | 吏部尚书 | 人事关系 | 按需 | Read, Grep, Glob, WebSearch | `pro/agents/people.md` |
| 6 | `finance` | 户部尚书 | 金钱 + 资产 | 按需 | Read, Grep, Glob, Bash | `pro/agents/finance.md` |
| 7 | `growth` | 礼部尚书 | 学习 + 表达 | 按需 | Read, Grep, Glob, WebSearch | `pro/agents/growth.md` |
| 8 | `execution` | 兵部尚书 | 行动 + 执行 | 按需 | Read, Grep, Glob, Bash, WebSearch | `pro/agents/execution.md` |
| 9 | `governance` | 刑部尚书 | 规矩 + 风险 | 按需 | Read, Grep, Glob, WebSearch | `pro/agents/governance.md` |
| 10 | `infra` | 工部尚书 | 基础设施 + 健康 | 按需 | Read, Grep, Glob, Bash | `pro/agents/infra.md` |
| 11 | `auditor` | 御史大夫 | 检查 agent 工作质量 | 每次流程后自动 | Read, Grep, Glob, Write | `pro/agents/auditor.md` |
| 12 | `advisor` | 谏议大夫 | 观察用户行为模式 | 每次流程后自动 | Read | `pro/agents/advisor.md` |
| 13 | `council` | 朝堂议政 | 跨部辩论 | 部门结论冲突时 | Read, Grep, Glob | `pro/agents/council.md` |
| 14 | `retrospective` | 起居郎 | 开朝、同步 pull、晨报、巡视 | "开始" / 主题触发词 | Read, Grep, Glob, WebSearch, Write, Bash | `pro/agents/retrospective.md` |
| 15 | `archiver` | 史官 | 退朝、知识提取、DREAM、sync | "退朝" / 流程后自动 | Read, Grep, Glob, WebSearch, Write, Bash | `pro/agents/archiver.md` |
| 16 | `strategist` | 翰林院 | 人类智库 · 93 思想家 · 18 领域 | 需要时询问用户 | Read, Grep, Glob, WebSearch, Agent, Bash | `pro/agents/strategist.md` |

---

## 触发分类

### 自动触发 (流程内部)

这些 agent 在决策流程中自动运行,不需要用户/ROUTER 提示:

- `retrospective` · Mode 1 (Housekeeping) — 每个 session 第一条消息时与 ROUTER 并发启动
- `reviewer` — 规划后、执行后各触发一次
- `dispatcher` — 审议通过后立即
- `auditor` · Decision Review Mode — 每次完整流程结束后
- `auditor` · Patrol Inspection Mode — `_meta/lint-state.md` 显示 >4h 未巡视时,RETROSPECTIVE 触发
- `advisor` — Summary Report 后
- `archiver` — 完整决策流程结束后 (主动 adjourn 或流程完结)
- `council` — REVIEWER 检测到跨部分差 ≥3 或结论直接对立时

### 按需启动 (ROUTER/DISPATCHER 调度)

这些 agent 根据当前主题决定是否启动:

- `planner` — 用户请求升格为完整决策时
- `finance`, `execution`, `growth`, `people`, `governance`, `infra` — PLANNER 判断哪些领域相关就派哪些
- `retrospective` · Mode 0 (Start Session) / Mode 2 (Review Mode) — 用户说特定触发词时

### 询问用户才启动

- `strategist` — ROUTER 检测到用户有「不知道要什么 / 价值困惑 / 人生方向」信号时,**必须问**用户「要不要启用翰林院」; 用户说是才启动

---

## agent 分组与职责说明

### 1. 入口层

**router** (丞相): 所有消息的第一道关。决定三种走向:
- 直接回 (闲聊、情绪、简单问题)
- Express Analysis (🏃): 启动 1-3 个领域 subagent 做专业分析, 不走完整决策流程
- Full Deliberation (⚖️): 2-3 轮意图澄清后 → 升格到 PLANNER

ROUTER 还管理触发词模板 (上朝 / 退朝 / 复盘 / 辩论 / 快速 / 更新 / 切主题)。

### 2. 决策层 (核心 4 角色)

**planner** (中书令): 把 Subject 分解成 3-6 个维度,指派给领域 subagent,定义输出标准。不评分、不决策。

**reviewer** (门下侍中): 只有 Read 权限 — 强迫他专心判断。拥有**封驳权**(veto)。所有决策必须过「情感维度」审查(情绪/关系/价值观/10/10/10 regret test)。每个决策必须引用 SOUL 相关维度(HARD RULE)。最多 2 次封驳,第 3 次必须批准或有条件批准。

**dispatcher** (尚书令): 把已批准的规划文件转换成执行令。判断哪些领域可以并行、哪些需要串行(依赖检测)。传递 wiki 已有知识作为「已知前提」。

**reviewer** 会被调用两次: 审规划、审执行。

### 3. 六部(领域 Agents)

各自有自己的四个分部 (四司), 以 finance 为例: Income / Spending / Assets / Reserves。

| 领域 | 四分部 | 评分校准特殊规则 |
|-----|--------|---------------|
| `people` | 识人 / 评估 / 关系 / 任免 | — |
| `finance` | 收入 / 支出 / 投资 / 储备 | runway <6 个月且无其他收入 → 不能 >7 |
| `growth` | 教育 / 品牌 / 创作 / 跨文化 | — |
| `execution` | 运营 / 装备 / 情报 / 后勤 | — |
| `governance` | 法律 / 审计 / 纪律 / 防御 | 有不可逆法律风险 → 不能 >7 |
| `infra` | 健康 / 居住 / 数字 / 日常 | 方案会导致严重睡眠不足或完全无运动 → 不能 >7 |

每个领域分析完毕后输出: 评分(1-10) + 🔴🟡🟢 发现 + 研究过程(🔎/💭/🎯) + 结论。

### 4. 监督层

**auditor** (御史大夫): 双模式。
- Decision Review: 每次完整决策后评审 agent 工作质量 (不评决策本身)。抓面子分(全 7-8 可疑)、抓分析说「严重风险」但评分 ≥6 的不一致、抓 REVIEWER 从不封驳的走过场。
- Patrol Inspection: 巡视模式, 每个领域巡查自己的辖区。触发条件: RETROSPECTIVE 看 `_meta/lint-state.md` >4h 时自动 trigger。

**advisor** (谏议大夫): 不评规划, 只观察用户行为模式。检测认知偏差、情绪信号、承诺跟进、维度回避。每次决策后自动跑, 更新 SOUL 的 evidence/challenges 计数。

### 5. 辩论与战略

**council** (朝堂议政): 跨部辩论。3 轮 (立场 → 反驳 → 终陈)。触发条件:
- REVIEWER 检测到部门评分差 ≥3
- 一部说「去做」另一部说「不要」
- REVIEWER 认为有不可调和的结论矛盾

信息隔离: 各辩论方作为独立 subagent, 只看到自己的报告 + 对方的「立场摘要」, 看不到对方的完整报告或思考过程。

**strategist** (翰林院): 人类智库 — 93 位思想家横跨 18 个领域。一对一、圆桌、辩论三种模式。每位思想家作为**独立 subagent** 启动(HARD RULE)。不走决策流程, 不评分、不汇总报告。最后写一份 `_meta/journal/{date}-strategist-{slug}.md` 归档。

**council 和 strategist 的区别**:
- council 解决**数据驱动的部门冲突**
- strategist 探索**价值观与身份认同**

### 6. 生命周期层

**retrospective** (起居郎): 会话起点管理。三模式:
- Mode 0 (Start Session): 用户说「上朝」/ "start" 等 → 完整 18 步序列,包括主题解析、sync pull、outbox merge、版本检查、项目绑定、SOUL Health Report、DREAM Auto-Triggers、Strategic Overview
- Mode 1 (Housekeeping): 用户发第一条普通消息时自动启动 → 轻量 context 准备
- Mode 2 (Review): 用户说「复盘」 → 仅晨报, 不做 full sync

**archiver** (史官): 会话终点管理。4 个 Phase, 只能作为 subagent 启动(HARD RULE):
- Phase 1: Archive — decisions/tasks/journal 写进 outbox
- Phase 2: Knowledge Extraction — 扫描会话材料, 自动写 wiki / SOUL 候选(严格标准 + 隐私过滤)
- Phase 3: DREAM — 最近 3 天的深度回溯, 10 个 auto-trigger 检测
- Phase 4: Sync — git commit + push (Notion sync 由 orchestrator 在主上下文做, 因为 archiver subagent 无法访问 Notion MCP)

---

## model 字段说明

全部 16 个 agent 的 frontmatter 都是 `model: opus`。这是一个**平台无关的意图标记**,意思是「用最强可用模型」。

在 Claude 平台: 直接映射到 Claude opus。

在 Gemini 平台: `pro/GEMINI.md` 把 `model: opus` 翻译成 Gemini 平台最强可用模型 (auto-select)。

在 Codex 平台: `pro/AGENTS.md` 把 `model: opus` 翻译成 Codex 平台最强可用模型 (auto-select)。

这样做的好处: 换模型时不用改 16 个 agent 文件,只改对应平台的编排文件里的映射表。

---

## 为什么只用 opus

理论上可以对轻量 agent (如 dispatcher 只做数据传递) 用更便宜的 haiku。但目前没这样做,原因:

1. **决策质量一致性**: 全链路同模型,输出格式、研究过程、判断标准统一
2. **信息隔离很严格**: 每个 subagent 的 context 本来就很窄, 不存在「轻量 agent 拖慢重 agent」的情况
3. **用户场景是决策**: 任何一步降级都可能导致连锁质量下降
4. **成本不是主要约束**: 单次完整决策 = 10-15 次 agent 调用, 每月 <10 次完整决策的用户,成本不敏感

如果未来要做成本优化,最可能的切口是:
- `dispatcher` (纯规则, 不需要深度推理)
- `council` 的 moderator 部分 (参与方仍用 opus)
- `auditor` 的巡视 Mode (可以用 haiku 做格式检查)

改的时候只动对应 agent 文件的 `model:` 字段 + 对应平台编排文件的映射表。
