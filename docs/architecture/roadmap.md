---
title: Life OS · v1.7 推进计划
date: 2026-04-20
status: active
owner: Jason
tags: [roadmap, versioning, cortex, execution-layer]
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Life OS · v1.7 推进计划

> v1.7 是一个大版本 — 把 Cortex 认知架构和 Hermes 风格的执行层，在同一个版本里全部交付完毕。本文档是 v1.7 内部推进计划，不分切到后续版本。

---

## 1. 总览

Life OS 当前向四个方向并行发展，其中两个已稳定维护，两个是 v1.7 主线：

| 方向 | 状态 | 说明 |
|---|---|---|
| **第二大脑** | 已有，持续维护 | 本地 markdown + iCloud + GitHub；SOUL / Wiki / Strategic Map 运转中 |
| **决策引擎** | 已有，持续维护 | multiple agents 架构 + 9 主题 + 三语言，三省六部 / 霞が関 / C-Suite 随选 |
| **Cortex 认知架构** | v1.7 主线 | 突触 + 海马体 + GWT + 叙事层，跨 session 记忆与联想 |
| **执行层** | v1.7 主线 | Shell hook 守卫 + Python 工具脚本,让 Life OS 能主动做事 |

两条主线（Cortex 和执行层）并行推进，全部在 v1.7 内合流成完整的 **"认知执行智能体"**——既懂你，又能替你干活，而且干活的过程被 hook 守住不偷懒。

**核心原则**（贯穿整个推进计划）：
- **Markdown-first**：真理源永远是 markdown 文件，任何数据库只能作加速索引（见 `devdocs/research/2026-04-20-storage-decision.md`）
- **云服务可选不强制**：无任何 vendor lock-in；GitHub / iCloud / Notion 都是可选加持，不是依赖
- **v1.7 一次性交付**：不把大计划切成多个版本，全部在 v1.7 内交付；内部按阶段推进

---

## 2. 当前状态 · v1.6.2a

**已完成的能力**：

- **multiple agents 决策引擎稳定**：ROUTER / PLANNER / REVIEWER / DISPATCHER + 6 domain + AUDITOR / ADVISOR / COUNCIL / RETROSPECTIVE / ARCHIVER / STRATEGIST
- **9 主题系统**：三语 × 3 风格（经典 / 政府 / 企业），Engine / Theme / Locale 三层分离
- **SOUL 灵魂层**：六维人格自动写入 + 趋势箭头 + 冲突检测 + 3 层引用策略
- **Wiki 自动写入**：6 条严格标准 + Privacy Filter，跨项目可复用的结论沉淀
- **Strategic Map**：战略线 + 驱动力 + 流图 + 叙事化健康评估
- **DREAM 10 触发器**：REM 阶段自动识别模式 + 硬阈值 + 软信号双通道
- **3 存储后端**：GitHub（主）/ Google Drive / Notion（移动端）适配器
- **基础 hook**：`setup-hooks.sh` + `lifeos-version-check.sh`
- **审计制度**：违规日志 `compliance/`、court-start-violation 等案例归档

**已确立的架构决策**（ADR 级别，不可回退）：

1. **Markdown-first 架构**：不上数据库作真理源（2026-04-19 brainstorm + 2026-04-20 ADR）
2. **4 层架构**：数据（markdown）/ Skill（agent 定义）/ Shell Hook（守卫）/ Python 工具（脚本）
3. **云服务可选不强制**：无任何平台绑定，任何用户 fork 仓库都能跑完整系统

**当前短板**（v1.7 要解决的）：

- **LLM 偷懒问题**：已出现 `court-start-violation`，ROUTER 跳过 Phase 1/2 逻辑；纯 prompt 级约束不可靠
- **无主动执行能力**：系统只在用户打开对话时响应；不能定时提醒、不能主动扫描 stale commitment
- **跨 session 认知缺失**：记忆只在 SOUL / Wiki / STRATEGIC-MAP 里；概念之间没有连接；海马体未实现
- **概念图谱未建立**：`_meta/concepts/` 目录不存在；Hebbian 强化 / sub-threshold pre-activation 还没落地

---

## 3. v1.7 推进计划

**v1.7 是一个大版本**，把 Cortex 认知架构、叙事层、撤销机制、Hermes 执行层**全部在一个版本里做完**，不切分到多个版本。内部按四个阶段推进；每个阶段交付时 v1.7 还没完，整个 v1.7 完成后再一次性发布 `git tag v1.7.0`。

### 阶段 A · 基础强化（堵住 LLM 偷懒 + 铺 Cortex 数据结构）

**主题**：让守卫机制全链路上线，让 Life OS 能主动做事，为 Cortex 铺设数据结构。

**Shell Hook 完整化**：

- `pre-prompt-guard.sh` — 用户输入进来时检查：触发词是否已经进入正确 agent 文件读取流程
- `post-response-verify.sh` — LLM 响应完成后扫描：是否有 Phase 跳过 / 任务分配错层 / 三语同步遗漏
- `pre-write-scan.sh` — 写文件前校验：是否违反 markdown-first 原则 / 是否越权写 canonical 文件
- `stop-session-verify.sh` — session 结束前最终检查：outbox 是否合并 / INDEX 是否更新 / git 状态
- `setup-hooks.sh` 扩展 — 新增 hook 统一配置入口，向后兼容现有安装

**Python 工具第一批**（纯读写，不改真理源，只做"编译产物"）：

- `reindex.py` — 从 markdown 源重建 `INDEX.md`（项目索引 + Wiki 索引 + SOUL 索引）
- `reconcile.py` — 健康检查：orphan 文件、断链、YAML 格式错误、三语不同步
- `stats.py` — 统计报告：session 数 / 决策数 / SOUL 维度数 / Wiki 条目数 / 趋势
- `daily_briefing.py` — 每日简报（脚本 + 本地 launchd / cron 任一接通；用户决策 #1：v1.7 不用 GitHub Actions / 远程调度）

**Cortex 数据结构**（目录结构就绪，但**暂不激活**）：

- `_meta/concepts/` — 概念目录（Hebbian 突触网络的素材）
- `_meta/sessions/` — 结构化 session summaries（带 concepts_fired 字段）
- `_meta/snapshots/soul/` — SOUL 快照（趋势计算用，v1.6.2 已引入）
- `_meta/eval-history/` — 评估历史（Strategic Map 的时间序列）

**阶段 A 出口判据**：

- COURT-START-001 同类违规 hook 能拦截；人工复现 3 次违规场景都被捕
- `reindex.py` 能从 markdown 重建 INDEX，校验和对账一致
- Cortex 数据结构目录存在、文档就绪、但 agent 尚未读取它

### 阶段 B · Cortex 认知前置开机

**主题**：Pre-Router 认知前置层上线 — 让"上朝"自动触发历史记忆浮现。

**新 agent（2 个）**：

- `pro/agents/hippocampus.md` — **海马体**：三波激活扩散（直接匹配 → 强连接 → 弱连接），按相关度 + 权重取 top 5-7 注入 ROUTER 输入
- `pro/agents/gwt-arbitrator.md` — **GWT 仲裁**：收集并行模块的信号 → 按 salience 竞争 → 最强信号进入"意识层"广播

**现有 agent 扩展**：

- `archiver.md` Phase 2 加三件事：
  1. **概念抽取**：session 结论里提取新概念，写入 `_meta/concepts/_tentative/`
  2. **赫布强化**：共同激活的概念对，边权重 +1；长期未激活 → 衰减
  3. **SOUL snapshot dump**：已有（v1.6.2 引入），合入 Phase 2 统一批次
- `router.md` — 改为接收"带认知标注的输入"（annotated input），不再是原始 user message
- `retrospective.md` Mode 0 — 加认知前置层触发：读 active_concepts + 沿 synapse 扩散一度邻居预激活

**Python 工具扩展**：

- `embed.py` — **语义搜索（可选）**：为 concept 生成 embedding 存 YAML；不强制，断网不可用时降级为关键词
- `research.py` — **后台研究**：长耗时任务后台跑，结果写入 outbox 下次 session 消费
- `backup.py` — 完整备份：markdown + concepts + snapshots 压缩到 tarball

**编排协议更新**：

- `pro/CLAUDE.md` 加 **Step 0.5 认知前置**：ROUTER 处理前先 spawn hippocampus 子 agent
- `pro/GEMINI.md` / `pro/AGENTS.md` 同步（跨平台一致性）

**阶段 B 出口判据**：

- "上朝"时能自动浮现 5-7 条相关历史决策（曾经在类似场景做过什么）
- 概念图在 second-brain 里持续增长：每次 session 末 `_meta/concepts/` 有新增或权重变化
- SOUL 趋势箭头计算可用（基于阶段 A 的 snapshot 基础设施）
- 评估场景通过：给定一个"你之前说过类似的话"情境，hippocampus 能命中

### 阶段 C · 叙事层 + 撤销机制

**主题**：防止 Cortex 叙事层自欺 + 三层撤销机制。

**叙事层实施**（核心问题：Gazzaniga 的左脑解释器是 bug，如果不防，Life OS 会变成自欺系统）：

- **ROUTER 最终输出阶段加 citation**：每个 substantive claim 必须带 `signal_id` 引用到底层竞争结果
- **Substantive vs Connective 分层**：meta-comment（"让我们看看..."）无需 citation；实质叙述（"历史上你在类似决策偏保守"）必须有
- **narrator-validator 校验**（Sonnet Claude Code subagent，不是外部 Haiku API — 用户决策 #9）：Opus 生成叙述 → narrator-validator 在当前 session 内核查 citation → 不一致则重生成
- **Trace 默认隐藏**：用户问"为什么这么想"时展开完整认知轨迹

**三层撤销机制**（不可撤销的系统会单向腐化）：

1. **被动衰减**（时间机制，无需人触发）
   - 90 天未激活的 canonical concept → 降级回 confirmed
   - 90 天未激活的 confirmed → 降级回 tentative
   - 持续未激活的 tentative → 清除
   - 按 permanence 分档：identity 不衰减 / skill 对数衰减 / fact 指数衰减 / transient 断崖衰减

2. **用户显性纠正**（主动机制）
   - 用户说"你搞错了，A 和 B 不是同一个东西" → `concept_demotion` → split concept
   - cascade：拆分影响所有相关 synapse 边 → 标记为"待复核"（不立刻删）

3. **元认知审计**（被动扫描）
   - 每周一次审计：冲突 salience / 激活频率大幅下降 / 用户反复纠正的领域
   - 生成 `_meta/audit/suspicious.md` 可疑清单，用户确认才执行 demotion

**Python 工具**：

- `migrate.py` — schema 迁移（Cortex 数据结构变了，老 concept md 格式需要升级）
- `search.py` — 真正语义搜索（基于阶段 B 的 embed.py 基础）

**阶段 C 出口判据**：

- 奏折里每句 substantive claim 可溯源到底层 signal
- 用户能撤销错误的概念合并，cascade 到相关 synapse
- 概念自动衰减按 permanence 分档，identity 类永不衰减
- 元认知审计每周跑一次，生成可疑清单

### 阶段 D · 本地执行层 + 方法库完整

**主题**：Life OS 在本地 Claude Code 内尽可能主动——但**不做独立 bot / 常驻 agent**（用户决策明确剥离 v1.7 scope）。

**执行扩展**（本地化，不跨平台）：

- **本地 launchd / crontab**（用户决策 #1：v1.7 从 Claude Code Bash 本地触发；不做 Telegram bot / GitHub Actions / 远程 cron / 独立常驻 agent）
- **家里 Mac 定时任务**（可选）— launchd 跑 daily briefing / 周复盘 / stale commitment 扫描，输出到 `_meta/briefings/{date}.md` 供下次 session 消化
- **本地通知**（可选）— macOS `osascript` / `terminal-notifier` 等原生通道推送 SOUL 冲突 / stale commitment / DREAM 触发器信号，**不做跨平台消息 bot**

**方法库**（v1.7 核心交付之一）：

- `_meta/methods/` 目录结构：每个方法一个 md 文件，YAML frontmatter 标 domain / trigger / evidence_count（详见 `references/method-library-spec.md`）
- 自动沉淀：ARCHIVER Phase 2 识别"这次 session 用的方法和过去相似" → 写入 method
- 使用回路：DISPATCHER 分配任务时检查方法库，命中则"按已有方法执行"而不是从头推理

**Cortex 完善**：

- 10 个 DMN 触发器全部落地（v1.6.2 已完成 spec，阶段 C 完成核心，阶段 D 补完剩余软信号路径）
- 突触网络成熟：sub-threshold pre-activation 投产，每次 session 打开时预热 top-50 概念
- 意识流（sub-threshold pre-activation 的自然延伸）：前一轮广播的概念预激活下一轮的邻居
- **不做**：amygdala-lite / 预测引擎 / 注意力雷达（用户决策明确剥离 v1.7 scope——这些属于 post-v1.7 方向，不强行补齐）

**阶段 D 出口判据**：

- 本地 launchd / crontab 任一方案接通每日 briefing，输出到 `_meta/briefings/`
- 本地通知通道接通（macOS 原生 / 等价机制），SOUL 冲突 / stale commitment 能主动提醒
- 方法库累计 ≥ 10 条自动沉淀的方法
- 整套系统在 1000 session 规模下流畅运行（2-5 秒 INDEX 扫描可接受）

### v1.7 发布判据（四阶段全部完成）

只有阶段 A-D 全部完成，才推送 `git tag v1.7.0`：

- 五个 hook 上线并拦截测试通过（pre-prompt-guard / post-response-verify / pre-write-scan / stop-session-verify / pre-read-allowlist）
- Python 工具可跑（reindex / reconcile / stats / daily_briefing / research / backup / migrate / search / export / seed / sync_notion / embed 占位——embed 在 v1.7 为 out-of-scope placeholder）
- Cortex 完整闭环（数据结构 + 海马体 + GWT + 叙事层 + 撤销机制 + 方法库）已激活
- 本地 launchd / crontab 任一方案接通（daily briefing + 本地通知）
- 方法库沉淀机制上线
- README 架构图更新为完整 Cortex + 本地执行层
- 三语文档同步完整（README × 3 / CHANGELOG × 3 / SKILL.md version / readme badge）

---

## 4. 版本节奏

Life OS 遵循 **Strict SemVer**。**v1.7 是一个大版本**，在其内部按四个阶段推进（阶段 A-D），最后一次性发布。

| 层级 | 示例 | 内容 |
|---|---|---|
| **PATCH**（小版本） | 1.7.0 → 1.7.3 | Bug 修复、三语同步补漏、文档更新、hook 微调 |
| **MINOR**（中版本） | 1.6.2a → 1.7 | 一个大功能族的交付（v1.7 本身即是一个 MINOR） |
| **MAJOR**（大版本） | 1.x → 2.x | 架构层面的断代变化（v1.7 之后再看） |

**v1.7 发布的硬条件**（缺一不可）：

1. 阶段 A-D 的代码改动全部完毕（agent / references / hooks / scripts 全部 ready）
2. 三语文档同步（README × 3 / CHANGELOG × 3 / SKILL.md version / readme badge）
3. CHANGELOG 完整（标题三语对齐 / 每个 breaking change 单独列）
4. 评估场景通过（至少覆盖 Cortex 闭环 + 执行层各一个 eval 场景）
5. `git tag v1.7.0` 推送

任何一条缺失 = 不能宣布版本发布。这是 `CLAUDE.md` 里的 HARD RULE。

---

## 5. 已知风险

与其掩盖，不如列出来 + 缓解方案：

### 风险 1 · Cortex 海马体在 5000+ session 后变慢

LLM 扫描 INDEX.md 作语义检索，在小规模（< 1000 session）下 2-5 秒可接受，但 5000+ session 时 token 成本和响应时间都会爆。

**缓解**：到那时加 **SQLite 作索引层**（不作真理源）。markdown 仍是 source of truth，SQLite 只是查询加速器。触发条件见 `devdocs/research/2026-04-20-storage-decision.md` 的 "Trigger for Revisit"。

### 风险 2 · Shell hook 仅 Claude Code 有

Gemini CLI / Codex CLI 目前无对等 hook 机制，守卫不能跨平台。

**缓解**：Gemini / Codex 用 **prompt 级约束** 弥补（在 pro/GEMINI.md / pro/AGENTS.md 里加更严格的 HARD RULE 提示）。长期看，Anthropic 以外的平台也在向 hook 生态靠拢，等外部条件成熟再打平。

### 风险 3 · v1.7 内容太多，可能一次做不完

Cortex 4 阶段 + 执行层从 14 层精简到 7 层后仍然复杂，全量落地可能拖长周期。

**缓解**：v1.7 内部按阶段 A-D 推进，每个阶段有独立出口判据。某个阶段卡住时可以暂停、打磨、再推进下一个，但**不切分到多个版本发布**——全部完成才推送 `v1.7.0`。如果某一块实测没有价值，在 v1.7 内部就砍掉或降级，不带进发布。

**Stage D 产品形态的 scope 边界**：

- **不做**：Telegram bot、跨平台消息 gateway、独立常驻 agent（非 Claude Code）、远程 cron / GitHub Actions、amygdala-lite / 预测引擎 / 注意力雷达。
- **做**：本地 launchd / crontab 调度、本地通知（macOS 原生等）、方法库 Stage D 完整交付。
- **v1.7 核心 spec**：cortex-spec / hippocampus-spec / gwt-spec / narrator-spec / concept-spec / session-index-spec / snapshot-spec / eval-history-spec / method-library-spec / hooks-spec / tools-spec（11 个）已经覆盖 v1.7 所有承诺的机制和数据结构。
- **本地通知的 spec**：在 tools-spec `daily_briefing.py` 段描述（输出 markdown 文件 + 可选本地通知 hook），不单独起 spec 文件。

Stage D 的 scope 是**本地化**而非**全天候网络服务**。v1.7 坚持"从 Claude Code Bash 本地触发"（用户决策 #1），任何需要网络常驻、secret 管理、跨设备同步的形态都 out of scope。

### 风险 4 · 用户自己的沉没成本心理

Cortex 某些功能（如叙事层 grounded generation）增加了每次 session 的成本。如果实测下来没达到预期，用户可能因沉没成本不愿砍。

**缓解**（用户决策 #4：不预设硬性 kill criteria 门槛）：通过 AUDITOR 的 eval-history 持续监测质量信号（`cognitive_annotation_quality`、`citation_groundedness` 等，见 `references/eval-history-spec.md`）。任何模块级变更走正常 spec 修订流程——持续低分由 AUDITOR patrol 浮现，用户决策是否调整。不预设"到期必砍"门槛，避免"3 个月到了我还没想清楚，仓促砍错"的反模式。

---

## 6. 相关文档

- **架构决策** · `devdocs/research/2026-04-20-storage-decision.md` — markdown-first 决策的完整论证
- **Cortex brainstorm** · `devdocs/brainstorm/2026-04-19-cortex-architecture.md` — 14 层 → 7 层的完整讨论轨迹
- **当前变更历史** · `CHANGELOG.md` — v1.0.0 → v1.6.2a 的完整演进
- **系统能力** · `SKILL.md` — 当前版本的权威定义
- **编排协议** · `pro/CLAUDE.md` — Pro 模式的信息隔离 + 封驳循环 + Notion 存档

---

*本文档是 Life OS 作者 v1.7 推进的个人规划参考。方向可能随实测结果调整；每次重大调整请新开一份带日期的版本，不覆盖历史版本，便于追溯决策轨迹。v1.7 之后的版本不在本文档讨论范围。*
