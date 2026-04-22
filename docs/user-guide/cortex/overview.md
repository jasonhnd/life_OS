# Cortex 总览 · v1.7 认知层总览

> 面包屑: [← 产品入口:用户指南首页](../index.md)

> v1.7 给 Life OS 加了一层"认知基底"——Cortex。它不是一个新角色,也不是一个新命令。它让系统在你每次开口之前,就自动去翻历史、激活相关概念、比对你的 SOUL。本文是 Cortex 六篇用户指南的入口。

## Cortex 是什么

Cortex 是 v1.7 新引入的 **Pre-Router Cognitive Layer**(预路由认知层),定位在 Life OS 命名体系里和 SOUL / Wiki / DREAM / STRATEGIC-MAP 并列:

| 模块 | 记录什么 | 范围 |
|------|---------|------|
| SOUL | 你是谁(身份、价值观) | 人格 |
| Wiki | 你知道什么(世界的事实) | 知识 |
| DREAM | 离线睡眠阶段发现什么 | 深度处理 |
| STRATEGIC-MAP | 你现在怎么布局 | 跨项目战略 |
| **Cortex** | **你怎么思考** | **上朝前的认知** |

Cortex 不替代任何模块。它做的事只有一件:**在 ROUTER 看到你消息之前,先给消息贴一层"认知注释"**——把相关的历史、概念图谱里点亮的节点、SOUL 冲突信号一起捎上,让后续所有角色(PLANNER、六领域、REVIEWER……)**不再从零起步**。

---

## 为什么要加 Cortex

v1.7 之前,Life OS 的长期记忆只在两个节点被触碰:

- **Start Session**——RETROSPECTIVE 读一次
- **Adjourn**——ARCHIVER 写一次

**中间这段所有的决策都是凭当前对话在做**。16 个 subagent 的 checks-and-balances 再严密,大家脑子里的"共享底板"是空的:

- PLANNER 不知道你上个月做过一个几乎一模一样的决策
- 六领域分析时看不到概念之间的关联
- REVIEWER 只检查本次决策的内部一致性,不检查跨 session
- Adjourn 之后,除了 SOUL 和 Wiki 的自动写入,没有任何痕迹留下

用户的体感是:**"这个 AI 在一次会话里挺小心,但开新 session 就全忘了。"**

Cortex 要解决的就是这件事——把跨 session 记忆、概念图谱、自我反馈变成每次 workflow 的"一等公民输入"。

---

## 用户端体验变化总览

升级到 v1.7 之后,**你不需要改任何使用习惯**。所有新能力都在后台自动运行。但有 6 个可见变化,会出现在你下一次上朝:

### 1. 上朝时多了一块"Cognitive Context"

ROUTER 拿到你消息的同时,会先看到一段 `[COGNITIVE CONTEXT]` 注释——相关的历史 session、点亮的概念、SOUL 冲突提醒。你在奏折里会间接感受到它:建议更贴心、维度更全、很少问"你以前是怎么处理类似事情的"(因为系统已经自己查过了)。

→ 详见 [hippocampus-recall.md](./hippocampus-recall.md)

### 2. Adjourn 之后,系统开始自动攒"概念"和"方法"

每次 session 结束,ARCHIVER Phase 2 会扫描对话,发现反复出现的概念节点、5+ 步的工作流程就抽成候选。下一次 Start Session 的简报里,RETROSPECTIVE 会问你:"检测到 2 个候选概念和 1 个候选方法,要不要确认?"

→ 详见 [concept-graph-and-methods.md](./concept-graph-and-methods.md)

### 3. 奏折里开始出现 `[S:xxx][D:yyy][SOUL:zzz]` 这样的引用

Narrator 层会给奏折里的"实质性断言"(比如"你过去也遇到过这个问题")强制加引用。这不是装饰——你可以说"trace 这句话",系统会把原始 signal 和支持文本给你看。目的:**防止 AI 编造貌似合理的历史**。

→ 详见 [narrator-citations.md](./narrator-citations.md)

### 4. 多源信号打架时,系统按"显著性"(salience)挑最重要的呈现

GWT 仲裁器(Global Workspace Theory arbitrator)用 4 个维度打分—— **urgency / novelty / relevance / importance**——从可能几十条信号里挑出 top-5 呈现。分值最高的那条如果是 SOUL 核心冲突,会被专门标红。

→ 详见 [gwt-arbitration.md](./gwt-arbitration.md)

### 5. Start Session 简报可能出现"系统性问题检测"块

AUDITOR 每次 session 结束都给自己打 10 维度的分,写进 `_meta/eval-history/`。RETROSPECTIVE 每次 Start Session 读最近 10 份。如果检测到"连续 3 次 adjourn 不完整""narrator 引用失败 >20%"之类的模式,会在简报 DREAM 区块后面放一条警告。

→ 详见 [auditor-eval-history.md](./auditor-eval-history.md)

### 6. 概念节点会"赫布式"(Hebbian)强化或衰退

你每次在 session 里用到某个概念,它的激活计数 +1、相关边权 +1。连续不用,按 permanence 分级(identity 不衰退 / skill 对数衰退 / fact 指数衰退 / transient 到期清零)。**用得越多越强,不用会慢慢淡出**——和脑子一样。

→ 详见 [concept-graph-and-methods.md](./concept-graph-and-methods.md)

---

## 推荐阅读顺序

如果你是 v1.6.2a 升级过来、**第一次听说 Cortex**,按这个顺序读效率最高:

1. **本文**(总览 + 体验变化)← 你在这里
2. [**hippocampus-recall.md**](./hippocampus-recall.md) — 跨 session 检索(理解 Cortex 干了啥最直观的入口)
3. [**concept-graph-and-methods.md**](./concept-graph-and-methods.md) — 概念图谱和方法库(理解系统怎么"攒智慧")
4. [**narrator-citations.md**](./narrator-citations.md) — Narrator 引用机制(理解为什么奏折多了方括号标注)
5. [**gwt-arbitration.md**](./gwt-arbitration.md) — GWT 仲裁(理解多源信号怎么打架、怎么挑赢家)
6. [**auditor-eval-history.md**](./auditor-eval-history.md) — AUDITOR 自评数据(理解系统怎么自我监控)

---

## Cortex 不改变什么

为了打消顾虑,先把**不变的事**列清楚:

- **11 步 workflow 没改**——Cortex 加的是 Step 0.5(在 ROUTER 之前)和 Step 7.5(Narrator 验证),老的 Step 1–11 编号完全不动
- **ROUTER 的分诊逻辑没改**——Cortex 只给 ROUTER 更好的输入,ROUTER 可以参考、也可以忽略
- **信息隔离没改**——PLANNER 依旧看不到 ROUTER 的推理、REVIEWER 依旧只看规划文档,这张安全模型表在 v1.7 只是**加了 3 行**(hippocampus、gwt-arbitrator、narrator-validator 各一行),没动旧行
- **Markdown-first 没改**——所有新数据都是 `.md + YAML frontmatter`。没有新数据库、没有 Python runtime、没有 cron、没有外部 API key
- **Notion 同步范围没改**——Cortex 数据**不同步到 Notion**。概念图谱、session 摘要、eval-history 都是本地 `_meta/` 下的内省资产
- **降级兜底**——Cortex 任何 subagent 失败(超时、文件读不到),orchestrator 自动退化到 v1.6.2a 行为(原始消息直送 ROUTER),session 照常进行

**换句话说:Cortex 是一个加法层,不是一次破坏性升级**。哪怕 Cortex 全部跑炸了,你的 Life OS 依然是你熟悉的那个 Life OS,只是少了历史检索和引用。

---

## 初次升级你要做什么

短答:**跑一个 migrate,就完事了**。

```
uv run tools/migrate.py
```

这个脚本会:

1. 扫你**最近 3 个月**的 `_meta/journal/*.md`——更老的内容**不碰**(老 journal 里常含过时项目和被降级价值观,拖进来只会污染概念图谱)
2. 为每个历史 session 生成一份摘要写到 `_meta/sessions/{session_id}.md`
3. 把反复出现的实体和方法抽成候选 concept,扔到 `_meta/concepts/_tentative/`
4. 重建 `SYNAPSES-INDEX.md` 和 `INDEX.md`
5. 补全一些 SOUL snapshot
6. 把过程写到 `_meta/cortex/bootstrap-status.md`

脚本是**幂等的**——跑两遍不会重复创建。如果 migrate 失败,orchestrator 退化到 v1.6.2a 行为,你可以稍后重试。

### 如果你是零 journal 的新用户

Cortex 会进入 **cold-start mode**——`[COGNITIVE CONTEXT]` 基本是空的,直到你攒够足够 session 才开始有料。没有任何东西阻止你使用系统,就是前几十次上朝拿不到跨 session 记忆的增益。

---

## 何时 Cortex 会"安静"(不工作)

三种场景,**Step 0.5 会跳过或简化**:

| 场景 | Cortex 行为 |
|------|-----------|
| **ROUTER 直接处理**(问候、翻译、简单查询) | **完全跳过**——没有 cognitive annotation,没有 narrator 验证,ROUTER 直接回 |
| **Express 快车道**(域级分析,无决策) | **简化**——只跑 hippocampus,不跑 concept lookup 和 SOUL check;输出是一行,不是三段 |
| **STRATEGIST 群贤堂** | **完全跳过**——STRATEGIST 不走 Draft-Review-Execute,narrator 也不介入 |

理由:这些场景不需要花时间翻历史。Cortex 的设计目标是"在**全朝议**决策时把记忆拉进来",不是每次输入都重扫一遍。

---

## 四个核心机制一句话

Cortex 内部由四个机制组成。每个都有自己的 spec 和 user-guide 页面:

1. **Hippocampus** — 跨 session 检索。3 波扩散激活:直接匹配 → 强边邻居 → 弱边邻居。top 5–7 相关 session 作为"记忆信号"。
2. **GWT Arbitrator** — 多源信号的显著性竞争。4 维打分、top-5 播报、`tier_1_conflict` 升格到 SOUL CONFLICT 警告。
3. **Narrator Layer** — 有据生成。奏折的实质性断言必须带 `signal_id` 引用。validator subagent 强制检查,不过 3 次重写、仍不过则退化到无引用版本。
4. **Synapses + Hebbian** — 概念图谱 + 用得越多越强的边权。4 级 permanence 决定衰退曲线。每次 Adjourn 由 ARCHIVER Phase 2 跑一次 decay。

---

## 常见疑问

### Cortex 会变慢吗?

Step 0.5 的总预算是 **< 7 秒**(hippocampus 5s 软超时 + concept lookup 和 SOUL check 并行)。Step 7.5 的 narrator 验证是 **2–5 秒**(重写一次加 2–5 秒,最多 3 次重试,硬上限 15 秒)。

**全朝议一次决策本来就要跑六领域 + COUNCIL,多这几秒几乎感觉不到**。Express 和 direct-handle 要么只跑 hippocampus、要么完全跳过,不会变慢。

### 我可以关掉 Cortex 吗?

可以。编辑 `_meta/cortex/config.md`,把 `cortex_enabled: true` 改成 `false`,下一次 Start Session 就退化到 v1.6.2a 行为。每个子能力也有单独开关:`hippocampus_enabled`、`gwt_arbitrator_enabled`、`narrator_validator_enabled`、`concept_extraction_enabled`。

但**不推荐长期关闭**——几次上朝下来,你会发现系统对"你以前怎么决定过"的敏感度显著提升,关了反而觉得 AI 退化。

### Cortex 会不会记错?我的历史被错误总结怎么办?

两个兜底:

1. **Narrator 层的 citation 强制引用真实 signal**——如果 narrator 说"你过去 5 次决策都保守",它必须指向 5 个真实 session 文件,否则 validator 直接打回重写。你可以对任何带括号引用的断言说"trace 这句",系统把原文给你看。
2. **Three-tier 撤销机制**——如果某个概念被错误升级了,你说"撤销最近的 concept"或直接删除 `_meta/concepts/{domain}/{concept_id}.md`,archiver 下一次会重建 SYNAPSES-INDEX 并剪掉悬挂边。

更严重的矛盾(比如 SOUL 维度被错误写入)走 SOUL 本身的撤销流程,不是 Cortex 层的事。

### 我的隐私数据会被写进概念图谱吗?

不会。ARCHIVER Phase 2 在抽概念之前跑**隐私过滤器**(和 wiki 的那套一致):

- 人名(除非是公众人物且与结论直接相关)→ 剥离
- 具体金额、账号、ID → 剥离
- 具体公司名(除非是公开案例)→ 剥离
- 家人朋友 → 剥离
- 可追溯的日期+地点组合 → 剥离
- 过滤完之后如果概念没意义了 → **丢弃**(说明它本来就是个人笔记,不是可复用概念)

另外,**个人(人)不能成为 concept**——那是 SOUL 的领地,概念图谱里连 `personal/{someone}.md` 都不允许。

---

## 深入阅读

产品入口:

- [What is Life OS](../../getting-started/what-is-life-os.md) — Life OS 是什么,Cortex 在其中的定位
- [Quickstart](../../getting-started/quickstart.md) — 首次上朝流程

用户文档(本目录 5 个 siblings):

- [hippocampus-recall.md](./hippocampus-recall.md) — 跨 session 记忆检索的用户体验
- [concept-graph-and-methods.md](./concept-graph-and-methods.md) — 概念图谱 + 方法库
- [narrator-citations.md](./narrator-citations.md) — 引用格式和 trace UX
- [gwt-arbitration.md](./gwt-arbitration.md) — 显著性竞争
- [auditor-eval-history.md](./auditor-eval-history.md) — 自反馈数据

架构层(给想看 Cortex 是怎么搭出来的读者):

- `devdocs/architecture/cortex-integration.md` — 11 步 workflow 里 Step 0.5 / Step 7.5 的插入点
- `docs/architecture/markdown-first.md` — 为什么坚持 `.md + YAML`,不引入数据库

Spec 层(最权威,但是英文、技术向):

- `references/cortex-spec.md` — 整体架构、四机制定位、数据结构
- `references/hippocampus-spec.md` — 检索算法 3 波扩散
- `references/concept-spec.md` — 概念文件 schema、Hebbian 更新算法
- `references/method-library-spec.md` — 方法库 schema、三级 maturity ladder
- `references/narrator-spec.md` — 引用格式、validator 算法、trace UX
- `references/gwt-spec.md` — 显著性公式、仲裁算法
- `references/eval-history-spec.md` — 10 维度打分表、系统性问题检测

---

## 一个真实示例

你决定问:"这一季度要不要把新产品线交给合伙人 A 负责?"

### v1.6.2a 的流程

```
你 → ROUTER 分诊 → PLANNER 规划(六维度)→ ...
```

PLANNER 从零开始思考。它知道本次主题、知道 SOUL、知道绑定项目——**但不知道**:
- 你上一季度问过一个几乎一样的问题,答案是"再观察 3 个月"
- "合伙人 A" 这个概念在系统里出现过 12 次,edge weight 和"控制权"极强
- 你的"家庭优先于事业"(confidence 0.82)和"单干风险"(SOUL tier-1)可能冲突

### v1.7 的流程

```
你 → Step 0.5 (Cortex) → ROUTER 分诊 → PLANNER 规划 → ...
```

Step 0.5 在你按回车到 ROUTER 看到消息的**< 7 秒**之内:
- Hippocampus 找到上一季度那次决策 → `S:claude-20260115-1020`
- Concept lookup 找到"合伙人 A"节点和强边 → `C:relationship:partner-a-control`
- SOUL check 找到"家庭优先"维度的 tier_1_conflict 信号
- GWT arbitrator 按显著性排序,`tier_1_conflict` salience 0.85 → 升格 SOUL CONFLICT 警告

ROUTER 看到的消息是:

```
[COGNITIVE CONTEXT]
⚠️ SOUL CONFLICT: 这个决策挑战你的"家庭优先"(confidence 0.82)
📎 Related past decisions:
- 2026-01-15 | 合伙人授权 (score 8.2) — 上次你的结论是"再观察 3 个月"
🧬 Active concepts:
- partner-a-control (canonical, weight 42, last activated 4d ago)
🔮 SOUL dimensions:
- 家庭优先于事业 (core, ↘ stable): tier_1_conflict
- 单干风险 (secondary, ↗ up): tier_2_relevant
[END COGNITIVE CONTEXT]

User's actual message: 这一季度要不要把新产品线交给合伙人 A 负责?
```

PLANNER 拿到的是**有 context 的规划输入**。它不会忘记你上季度的结论,不会忽略 SOUL 冲突,也不会重新发现"合伙人 A"是谁。

这就是 Cortex 存在的全部理由。

---

**下一篇**: [hippocampus-recall.md — 跨 session 记忆检索](./hippocampus-recall.md)
