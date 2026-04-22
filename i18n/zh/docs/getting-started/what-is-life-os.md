---
translated_from: docs/getting-started/what-is-life-os.md
translator_note: auto-translated 2026-04-22
---

# 什么是 Life OS(What is Life OS)

## 一句话定义

Life OS 是一个装在 AI 终端里的**个人认知操作系统**。

它同时做三件事：

1. **第二大脑** — 持续记录你是谁、你知道什么、你在做什么
2. **决策引擎** — 16 个独立 agent 分权制衡,重大决策有人敢拍桌子
3. **认知执行智能体** — 不只是"能想",还能"记住 + 主动做事"

这三件事不是三个模块可以拆开卖的。拆掉一个,剩下两个就不成立：
- 没有第二大脑,决策引擎每次从零审议,审了也白审
- 没有决策引擎,第二大脑就是一堆整齐但没被加工过的砖头
- 没有智能体,系统只能等你打字,chief of staff 永远不来上班

Life OS 当前状态：第二大脑和决策引擎已稳定跑通(v1.6.2a),智能体层在 v1.7 GA 已落地——Cortex 做认知前置**让系统在 session 之间也有认知**,Hermes 风格执行力做主动执行,两条并行线在 v1.7 已一起交付。

---

## 要解决什么问题(What problems does it solve)

### 问题一：AI 给你答案,但没人审查答案

问 ChatGPT「我该不该辞职创业」,它会给你一个看起来很体面的分析：列出 5 条 pros、5 条 cons、一个看似平衡的建议。你读完觉得很有道理,于是辞了。

三个月后发现：它没问你现金流能撑多久、合伙人有没有谈清楚、你家里人什么反应、你上一次类似冲动决策怎么收场的,甚至没问你这次想创的业和你去年想创的业是不是同一个。它给出的"5 pros 5 cons"是通用模板,不是针对**你**的审议。

单一的、确定的、和气的 AI 回答是一种噪音。你需要的不是一个声音说「可以」,而是一屋子人各抒己见——有人算现金流、有人审合伙人条款、有人盘家庭影响、有人拍桌子说「预算这一项根本没算清楚,打回重拟」。

1400 年前的三省六部就解决过这事。中书省起草、门下省封驳、尚书省执行、御史台监察——四权分立,谁都不能独断。Roman Republic、Westminster、现代内阁——所有真正做大决策的地方,都是分权 + 复核 + 问责。**独裁式 AI 是决策质量的天敌**。

**→ Life OS 用"决策引擎"回答这个问题。**

### 问题二：AI 不记得你

每次开新对话,AI 都在从零开始。它不知道你上次做了什么决策、不知道你的性格偏好、不知道你现在正在做的三个项目之间的关系、不知道你半年来 SOUL 里的"保持灵活性"维度一直在和"追求稳定"维度拉扯。你和它的关系永远停留在"初次见面"。

即使某些 AI 能「记住」一点东西(ChatGPT memory、Claude Projects),也只是一堆零散的事实点——「用户住在东京」「用户在学日语」「用户有一个叫 X 的项目」。没有结构、没有置信度、没有生命周期、没有互相影响的网。三个月前的事实和昨天的核心决策同等权重。

真正的「大脑」不是一叠便签。它有**身份**(我是谁,可变但稳定)、**知识**(我知道什么世界规律)、**计划**(我在做什么当下项目),三者互相关联——身份影响你怎么学知识、知识影响你怎么做计划、计划反过来塑造身份。

**→ Life OS 用"第二大脑"回答这个问题。**

### 问题三：AI 等着你问,不会主动做事

你要 AI 做事,必须打字问它。你不问,它不动。

具体不会的事：
- 不会检查任务截止日期
- 不会提醒你承诺 30 天没跟进
- 不会告诉你最近 3 次决策都在挑战你 SOUL 里的同一个维度
- 不会在你凌晨 3 点做重大决策时说「深夜状态不该做这个」
- 不会在每轮对话前自动翻你的历史,判断"这件事你以前想过吗"
- 不会在合适时机自己跑定时脚本、自动化维护、跨设备同步

一个真正的个人 AI 应该像一个 chief of staff：在你需要时出现、在你忙时替你整理、在你有盲点时主动指出、在后台持续运转。

这件事拆成两个并行的方向：

- **认知前置**(想得对)—— AI 在每轮对话前自动检索记忆、跨 session 关联信号、让中间推理过程也能用上长期记忆,**不只是在入场退场碰一下**。这是 Cortex 要解决的。
- **主动执行**(做得到)—— AI 不等你下指令,在合适时机自己跑文件、命令、脚本、定时任务、强制检查。这是 Hermes 风格执行力要解决的。

**→ Life OS 用"认知执行智能体"回答这个问题。这是 v1.7 GA 的核心工作,两条并行线已同时落地——Cortex 管认知前置,Hermes 风格执行力管主动执行,全部在 v1.7 已交付。**

---

## 三件事的完整展开(The three pillars in detail)

### 3.1 第二大脑(已有,稳定)

所有决策、见解、行为、知识都写成结构化 markdown,存在你选择的后端。

#### 四个长期记忆支柱

1. **SOUL.md** — 你是谁。每条维度有 What IS(从决策里观察到的)和 What SHOULD BE(你声明的理想)。两者差距就是成长发生的地方。ADVISOR 每次决策后自动更新。
2. **Wiki** — 你知道的世界。ARCHIVER 从决策里萃取(6 条严格标准 + 零隐私过滤器)。可复用的知识进这里,关于你个人的进 SOUL。
3. **Strategic Map** — 项目怎么连起来。你手动定义 strategic lines(purpose + driving force),系统自动检测 flow graph、健康原型(steady-progress / momentum-decay 等 6 种)、盲点(5 类)。
4. **user-patterns** — 你怎么做事。ADVISOR 观察你的行为模式写入,跨 session 持续积累。

#### 目录结构

```
second-brain/
├── SOUL.md                 # 你是谁(身份档案)
├── user-patterns.md        # 你怎么做事(行为模式)
├── wiki/                   # 你知道什么(可复用知识)
├── projects/{name}/        # 你在做什么(活跃项目)
├── areas/{name}/           # 你持续关注什么(领域)
├── _meta/
│   ├── STRATEGIC-MAP.md    # 项目之间怎么关联
│   ├── journal/            # 每次会话报告、DREAM 日志
│   ├── outbox/             # 并发会话暂存
│   └── snapshots/soul/     # SOUL 快照(用于趋势计算)
├── inbox/                  # 手机随手记
└── archive/                # 已完结
```

#### 同步与备份

**iCloud(本地主存)+ GitHub(代码版本)+ Notion(跨设备视图)三重同步**。三个后端写入各有侧重,不是冗余：
- iCloud：当前活跃文件系统,Mac 本地直接读写
- GitHub：所有历史版本可追溯,可回滚
- Notion：手机上能看能改(Inbox / Status / Todo / Working Memory 四个组件),Adjourn 时 orchestrator 负责把 markdown 同步进去

#### markdown-first 原则

所有数据永远是 markdown 文件。不依赖数据库、runtime、云服务。任何 LLM(Claude / Gemini / Codex / 未来的新模型)都能读。你停用 Life OS,你的第二大脑仍然是一堆结构化的 markdown,用 Obsidian / VS Code / 任何编辑器都能继续用。

这个原则不是审美选择,是**架构存活条件**：
- LLM 模型在快速迭代(Opus 4.5 → 4.6 → 4.7 → 未来),markdown 不会被任何模型抛弃
- 数据库格式可能过时,markdown 不会
- 云服务可能停运,本地 markdown 文件永远在
- 你的身份、知识、项目是你的,不应该被任何第三方产品锁死

所以 Cortex 的 concept 图、突触权重、GWT 信号——**全部用 markdown + front matter 实现**,不引入 SQLite / Python runtime。即使 Life OS 整个项目消失,你的 `_meta/concepts/*.md` 依然可读可用。

### 3.2 决策引擎(已有,稳定)

不是每次对话都启动。ROUTER 先分诊——简单问答直接答,重大决策才进入这一层。

#### 16 agent 三段式

**Draft → Review → Execute,不允许跳步**：

1. **Draft** — PLANNER 把问题拆成 3-6 个维度
2. **Review** — REVIEWER 独立复核。做情绪审计(「是恐惧还是兴奋在推你？」)、10/10/10 后悔测试、SOUL 一致性检查、红队挑战。发现盲点就 veto,打回重做(最多 2 轮)
3. **Execute** — 六部(People / Finance / Growth / Execution / Governance / Infra)并行打分 1-10,每部 4 个科室共 24 个维度各出报告

所有报告到齐后 REVIEWER 再做一次总复核；不同部门分差 ≥3 分自动触发 COUNCIL 开 3 轮辩论；最后 AUDITOR 审 agent 的工作质量、ADVISOR 审你本人最近几次决策的行为模式。

**信息隔离是硬规则**：PLANNER 看不到 ROUTER 的思路、REVIEWER 看不到 PLANNER 的思考过程、各 domain 看不到彼此的分数。在 Claude Code 里靠真正的 subagent 实现,不是单 context 里的角色扮演。

#### 翰林院 · 93 思想家

没有「正确答案」、只有「换个视角」的问题,STRATEGIST 召集 93 位历史思想家和你对话。一对一 / 圆桌 / 辩论三种模式。18 个领域覆盖：
- 哲学(柏拉图、康德、尼采…)
- 东方思想(孔子、庄子、王阳明…)
- 科学(爱因斯坦、费曼、达尔文…)
- 战略(孙子、克劳塞维茨、博弈论…)
- 商业、心理学、系统思维、人性、文明、逆境、美学、政治、经济、数学、医学、探索、沟通、法律

每个思想家作为独立 subagent 运行,信息隔离——圆桌辩论时,主持人只传"发言摘要"给下一个思想家,不透露思考过程。这避免了"所有人互相抄作业"的 groupthink 陷阱。

STRATEGIST 不走 Draft-Review-Execute 流程,是独立的"思想启发"通道。适合"我的人生方向"、"这件事的意义"、"我卡住了"类问题。

#### DREAM · 睡眠周期反思

会话结束后系统「睡觉」——N1-N2 整理零碎 + N3 深度巩固 + REM 创造性联想。REM 会自动检测 10 种跨 session 模式：
1. 新项目关系(两个原以为独立的项目出现共同 concept)
2. stated value 偏离(你说的和你做的不一致)
3. wiki 矛盾(新决策和 wiki 已有知识冲突)
4. SOUL 休眠维度(某个核心价值 30 天没被激活)
5. 跨项目认知未复用(A 项目学到的教训 B 项目没用上)
6. 决策疲劳(24h 内 ≥5 决策 且 后半段平均分 ≤ 前半段 -2)
7. 价值观漂移(30 天内 ≥3 挑战 且 ≤1 新证据 且 confidence 下降 >30%)
8. stale commitment("我会 X" 正则匹配 + 30 天无对应完成)
9. 情绪态决策簇(ADVISOR 情绪标记 + REVIEWER 建议冷静 + 仍推进)
10. 重复决策(主题关键词与过去 30 天 ≥2 决策重叠 >70%)

每个触发器都有**硬阈值**(定量,自动触发)+ **软信号**(定性,需 AUDITOR 审核)+ 24h 反重复抑制。所有触发的动作进下次晨报固定的「DREAM Auto-Triggers」块。

#### 当前状态

**v1.6.2a 已完整跑通**。具体包括：
- 16 agent 都有独立文件(`pro/agents/*.md`),每个角色的岗位说明书清晰
- 9 个主题可切换(英 / 中 / 日 × 古典 / 政府 / 企业),trigger 词自动识别主题
- DREAM 10 触发器硬阈值 + 软信号并存,24h 反重复抑制
- Adjourn 状态机 AUDITOR 强制执行,非法状态转换自动记录到 user-patterns
- REVIEWER 3 层 SOUL 引用策略(confidence 分层)
- SOUL 快照机制(每次 Adjourn dump,下次 Start Session 计算趋势)
- 翰林院 93 思想家的信息隔离(每个思想家独立 subagent,主持人传递发言摘要)

这部分**稳定**,不再动核心。后续工作集中在认知执行智能体(3.3)。

### 3.3 认知执行智能体(v1.7 GA 已落地)

这是 v1.7 GA 的主要工作,**两条并行线已一起交付**：

#### 3.3.1 Cortex · 认知架构(认知前置)

**问题**：现在的 Life OS 只在入场(RETROSPECTIVE 开场读 SOUL / wiki / user-patterns)和退场(ARCHIVER 写回)时碰记忆层,**中间全程靠当前对话信息做决策**。你问"我该做 X 吗",AI 不会自动去翻：
- 你三个月前类似决策时是怎么想的
- 你最近的 SOUL 变化支持还是反对这件事
- 你两个项目之间有没有隐含冲突
- 你 wiki 里已经写过的世界知识是否和当前假设矛盾

中间是凭空决策的。用户感受不到"展开思维、搜索记忆、关联一切"的智能化——因为系统本来就没做。

**设计**：**Pre-Router 认知前置层**——在 ROUTER 拿到你的消息之前,先跑一套认知模拟流水线。灵感来自神经科学的三个经典模型(Dehaene 的全局工作空间理论、Hebb 的突触学习、Damasio 的躯体标记假说),但**全部用 markdown 实现**,不引入 SQLite / Python runtime：

- **海马体**：每轮对话自动跨 session 检索相关记忆(不是"按需调用",是**默认跑**)。三波激活扩散：直接匹配 → 强连接(weight ≥ 3)→ 弱连接。按相关度 + 权重取 top 5-7 条送给 ROUTER。
- **GWT 全局工作空间**：多模块并行产出信号,每个信号带 salience 向量(urgency / novelty / relevance / importance,四维 0-1)+ confidence。v1.7 先实现 4 维权重求和：`salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2`,情绪维度(杏仁核第 5 维信号)留给未来版本。仲裁层按 salience 竞争中央舞台,最强的进入"意识层"广播给所有模块。ROUTER 收到的是"带认知标注的输入",不是原始 message。
- **叙事层**：底层分布式信号竞争的结论重新包装成"朝廷 / 霞が関 / C-Suite"的文化剧本。**关键约束：grounded generation**——每句话强制附带 signal_id 引用,没有对应 signal 的叙述会被 Sonnet Claude Code 校验子 agent(narrator-validator,在当前 session 内运行,不是外部 Haiku API——用户决策 #9)拦截重生成。这不是为了好看,是为了避免 Gazzaniga 左脑解释器效应(裂脑人实验证明大脑会无中生有编自洽故事并真诚相信,Life OS 绝不能继承这个 bug——否则就成了系统化自欺)。
- **突触 + 赫布强化**：每篇 concept 文件 front matter 带 outgoing_edges 和权重。共同激活 → 权重 +1(赫布学习 "neurons that fire together, wire together")。长期不激活 → 衰减。衰减到 0 → 自动修剪。用进废退。concept 分四档 permanence(identity / skill / fact / transient),衰减曲线各不相同——SOUL 核心价值不衰减,临时事件断崖衰减。

**为什么 v1.7 一定要加这层**：v1.6.2a 的决策引擎已经很稳——分权、审议、veto、六部打分,该有的制衡都有。但这些都发生在**当前对话**内。session 结束,ARCHIVER 把结果写回第二大脑,系统就"睡着了"——直到下次上朝,RETROSPECTIVE 再把 SOUL / wiki / user-patterns 读一遍重新开机。中间那段空白期——**跨 session 的关联、概念之间的消长、哪条知识最近被反复激活、哪个维度在休眠、这次决策和三个月前那次是不是同一件事**——没人管。所以第二大脑存的东西越多,反而越像是"档案室",不是"正在想事的那个脑子"。Cortex 不是再加功能,是**把认知闭环补齐**：记忆 → 联想 → 叙事 → 强化 → 反思,五环都在,系统才算"活着"。

**用户端能看到什么**(6 个新能力,每个都是你实际能感觉到的变化)：

- **跨 session 记忆自动上场**：每次你开口,系统默认在背景翻你的历史 session,按相关度 + 强度取 top 5-7 条送进决策流程。不用你说"对了,我上个月想过类似的事"——它自己会带上来。
- **多信号仲裁代替单线推理**：记忆、概念关联、SOUL 冲突检测几路信号并行产出,按"紧迫性 + 新颖性 + 相关性 + 重要性"四维加权竞争,最强的那条才进入 ROUTER 视野。你不会被淹没在一大堆"可能相关的东西"里,看到的是系统判断过"这几条值得你看"。
- **Summary Report 每句话都带引用**：叙事层写出来的任何实质性论断,必须指向具体的 signal_id,没引用的会被校验 agent 打回重写。所以你读到"你最近 3 次决策都在挑战'保持灵活性'维度"时,能一路追到那 3 次决策的具体 journal 条目,不是 AI 替你编了个听起来像那么回事的故事。
- **概念之间的关系会自己长出来**：你聊的每个主题都会落成一篇 concept 文件,共同出现过就加一条边、长期没激活就衰减、衰到 0 就修剪。半年后回看,`_meta/concepts/` 里不是一堆散乱标签,而是一张能看出"你这个人的思想地图"的网。
- **SOUL 趋势而不只是 SOUL 快照**：每次 Adjourn dump 一张 SOUL 快照,下次 Start Session 自动比对——"过去 30 天'稳定性'维度被激活 8 次、'灵活性'只有 2 次,差距在扩大"之类的趋势会直接出现在晨报里。你看到的是**方向**,不只是**现状**。
- **方法库当作程序性记忆用**：系统会把你反复走过的"怎么做 X"沉淀成可检索的 method 文件。下次遇到类似场景,Cortex 自动激活对应 method,不用你每次重新说"按我之前那个流程走"。至少跨 2 个独立 session 出现同一模式才会写,避免单次行为被当成习惯。

**系统自我调整 · AUDITOR eval-history**：上面这些能力一旦开起来,就必然有"规则和你真实用法脱钩"的风险——衰减曲线是不是太快了、method 是不是识别过热、某条 SOUL 维度是不是其实早就不该是 tier-1。Cortex 不靠你手动调——AUDITOR 把每次决策的评估结果写进 `_meta/eval-history/`,一周一月累积成系统级的自反馈：哪些规则最近被反复违反、哪个 agent 的判断和 eval 分数长期不一致、哪种模式被 escalate 的频率超阈值。这些信号会固定出现在晨报的对应栏位,也会让 ADVISOR 下次 Summary Report 里标红提醒。**规则本身不会自己改**——真要调,你来定；但系统会诚实地把"该调了"这件事摆到你面前,不让"用着用着就跑偏"悄悄发生。

**封驳路径 B**(关键设计决策)：REVIEWER 的 veto 不是简单的 "inhibitory signal 强度高就压制"——必须携带完整论证包(reasoning chain + 被否决的 signal 引用 + rebuttal 机会)。Rebuttal 死循环自动 escalate 给用户。这是**让拒绝可审查**的结构化约束。这里的 "Path B" 定义见 `references/cortex-spec.md` §Structured veto with reasoning chain。

**撤销机制**：concept 从 tentative → confirmed → canonical 不是单向通路。三层撤销源——被动衰减(时间)、用户显性纠正(触发 cascade revalidation)、元认知自动审计(每周生成可疑清单)。不可撤销的系统会单向腐化。

**核心洞察**：Life OS 有 SOUL / Wiki / Strategic Map / 决策引擎,但中间缺"真正的大脑运作"——信号竞争、广播、扩散激活、叙事包装、赫布强化。Cortex 不是新加一层,**是 Skill 层的升级**——在 ROUTER 之前加认知前置流水线,把现有 16 agent 流程包在里面。

**状态**：v1.7 已落地——突触 + 海马体 + GWT 基础版构成最小认知闭环,Markdown-first 实现,全部用 `_meta/concepts/*.md` + agent 定义文件承载,不引入额外 runtime。v1.7 内部分阶段推进,全部在 v1.7 内完成。权威设计详见 `references/cortex-spec.md`。

#### 3.3.2 Hermes 级执行力(v1.7 GA 已落地)

**问题**：Life OS 目前只能在你打字"上朝"时动。不上朝它就沉默。用户必须手动触发所有事情——提醒、审计、归档、同步、维护。

**借鉴对象**：Hermes Agent(Nous Research 开源,GitHub 10 万 stars 的通用智能体)。Hermes 的核心能力：
- 47 个原生工具(terminal / file / browser / cron / TTS / MCP / 消息 / RL 训练)
- 19 个消息平台 gateway(Telegram / Discord / Slack / WhatsApp / Signal / Email …)
- 三层记忆(MEMORY.md + SQLite FTS5 sessions + 8 个插件化记忆 provider)
- 自学习闭环(复杂任务完成后自动创建 skill、使用中自我改进)
- 42 条 dangerous pattern 安全模式(每一条都是具体攻击面,不是喊口号)

**它是业界把"执行力"做到极致的参照物**。Life OS 调研了它的架构(详见 `devdocs/research/2026-04-19-hermes-analysis.md`),得出结论：**架构正交,可以偷教训不必复制**。

**Life OS 已经有的执行能力**(很多人没意识到,Life OS 其实已经能做很多事)：

- **Read/Write** — 第二大脑的任何 markdown 文件都能读写。SOUL、wiki、projects、_meta 每次决策自动更新——ARCHIVER 每次 Adjourn 按 6 条严格准则 + Privacy Filter 自动写 wiki；ADVISOR 每次 Summary Report 后自动更新 SOUL。
- **Bash** — 跑任意本地命令。git 操作、文件整理、脚本调用、shell hook、任何本地 CLI 工具。
- **WebFetch + WebSearch** — 联网抓资料、版本检查、链接验证、后台搜索。比 ChatGPT 的联网更可控——可以指定 URL 深度抓、可以在分析中并行跑多个搜索。
- **16 子 agent 并行** — 同时跑 16 个独立 subagent,彼此信息隔离。六部是这个能力的固定用法,任何复杂任务都可以临时 spawn 多个 subagent(比如翰林院的 93 思想家圆桌)。
- **Notion MCP + Google Drive MCP** — 跨设备同步。手机上改的 inbox 条目 Adjourn 时自动拉回本地；Status / Todo / Working Memory 四个 Notion 组件由 orchestrator 每次退朝时同步。
- **定时任务** — launchd(Mac)/ cron(Linux)/ GitHub Actions 都可以跑,不绑任何特定云服务。你也可以用 Vercel / Cloudflare Workers / 自己的 VPS / 甚至手动跑——**Life OS 不在乎你选哪个**。默认零云依赖。

**v1.7 GA 已落地的两层**(就是 Hermes 思路的本地化)：

- **Layer 3(Shell Hook 强制层)**：本地 shell 脚本在 Claude Code 的 hook 系统里强制执行 HARD RULE。具体能做：
  - trigger 词检测(用户说"上朝"就必须 launch retrospective,不能偷懒在主 context 里假装)
  - 输出格式验证(Summary Report 必须包含 Overall Rating / Must Address / Audit Log,缺一个就阻止提交)
  - Adjourn Completion Checklist 完整性检查(4 phases 全部返回 Checklist 且无 TBD 无空值才允许 session end)
  - SOUL / wiki 写入前安全扫描(Privacy Filter 具体 regex——姓名、金额、账户 ID、具体公司名白名单匹配)
  - git pre-commit hook 拦截敏感信息泄漏
  - 让"应该这样做"变成"必须这样做",LLM 不能偷懒

  Hermes 用 42 条 dangerous pattern 正则保护自己不被 prompt injection 搞崩(`rm -rf /`、fork bomb、`curl | sh`、`git reset --hard` 全覆盖),Life OS 借鉴这个思路做 Privacy Filter 的具体正则列表——不做就永远是"手艺",做了就是"规格"。

- **Layer 4(Python 工具层)**：手动或定时跑,处理批量、后台、维护任务。不是每次对话都跑,是"需要批量扫全部笔记才能做的重型工具"。具体能做：
  - `scripts/session-index.py`：把所有 Summary Report 的 score / domain 抽出来做 SQL 查询(借鉴 Hermes FTS5 思路的轻量版)
  - `scripts/monthly-review.py`：每月跑一次 self-review journal,统计 AUDITOR 召回率、REVIEWER 否决率、COUNCIL 触发率、Express 命中率。数字越诚实越好。
  - `scripts/decay-audit.py`：每周扫 concept 文件,衰减 + 修剪长期不激活的 synapse 边
  - `scripts/wiki-conflict-check.py`:批量扫 wiki 检测互相矛盾的条目
  - `scripts/dream-trigger-check.py`:定时跑 10 种跨 session 模式检测

  这些脚本**不绑云**——你可以放 launchd / cron / GitHub Actions / Vercel Cron / 随便什么。重点是"会自己跑",具体怎么跑你挑。

**方法库**：类似 Hermes Skills 的程序性记忆——把"怎么做 X"本身做成可检索的 skill,Cortex 海马体能在相关场景下自动激活对应 skill。这是 Hermes 自学习闭环的本地版,但不需要 RL 训练,用"规则闭环学习"代替——规则自己不会变,但会被标记"这条规则最近在被违反"。

**和 Hermes 的差距**(诚实说)：Hermes 跑在独立 Python runtime 上,47 原生工具 + 19 消息平台 + RL 训练闭环。Life OS 跑在 Claude Code / Gemini CLI / Codex CLI 里,只能用宿主平台的工具。**差距存在,但补不上也没关系**——Life OS 的架构优势不在"工具数量",而在：
- 16 agent 制衡(Hermes 是单 agent + delegate,没有结构化 veto)
- 三层长期记忆(SOUL + Wiki + Strategic Map,Hermes 是扁平 MEMORY.md)
- Cortex 认知前置(Hermes 没有对应机制)
- DREAM 10 种自动模式检测(Hermes 只有"nudge self to persist knowledge")

Hermes 没有这些。方向是**吸收 Hermes 的执行模式,不抛弃 Life OS 的制衡和记忆架构**。两者最终是互补,不是替代。

---

## 4 层架构(Four-layer architecture)

把上面三件事落到工程上,就是这 4 层：

```
┌─────────────────────────────────────────┐
│  Layer 4: Python 工具层                  │  批量 / 后台 / 维护
│  (手动或定时跑,不绑云服务)              │  状态：v1.7 GA
├─────────────────────────────────────────┤
│  Layer 3: Shell Hook 层                  │  强制 HARD RULE
│  (code-level 约束 LLM 不偷懒)           │  状态：v1.7 GA
├─────────────────────────────────────────┤
│  Layer 2: Skill 层                       │  16 agent 决策引擎
│  └── Cortex 前置认知层(v1.7 GA)         │  状态：决策引擎稳定
│                                          │       Cortex 在 v1.7 已落地
├─────────────────────────────────────────┤
│  Layer 1: 数据层                         │  markdown 文件
│  SOUL / Wiki / Strategic Map /          │  状态：稳定
│  user-patterns / projects / _meta        │
└─────────────────────────────────────────┘
```

**每层职责和对应关系**：

| 层 | 职责 | 对应三个方向 | 当前状态 |
|---|------|-------------|---------|
| Layer 1 · 数据层 | 所有长期记忆的物理存储,纯 markdown,三后端同步 | **第二大脑** | 稳定 |
| Layer 2 · Skill 层 | 16 agent 编排 + Cortex 认知前置 + 9 主题 | **决策引擎** + **认知执行 · Cortex** | 决策引擎稳定；Cortex 在 Layer 2 内部加一层前置模块(不是独立的 Layer 5),v1.7 已加入 cross-session 记忆、概念图谱、eval-history 自反馈 |
| Layer 3 · Shell Hook 层 | trigger 词强制、输出验证、安全扫描、git hook | **认知执行 · Hermes 执行力**(强制约束) | v1.7 GA |
| Layer 4 · Python 工具层 | 批量索引、自动化维护、self-review journal、定时任务 | **认知执行 · Hermes 执行力**(主动执行) | v1.7 GA |

**重要澄清**：

- Cortex **不是** Layer 5。Cortex 是 Layer 2 的内部升级——在 ROUTER 之前加一套认知前置流水线(海马体 + GWT + 叙事层)。从外面看,还是一个 Skill 层。Skill 层的输入从"用户原始 message"变成"带认知标注的 message",16 agent 的编排流程本身不变。
- Vercel / Cloudflare Workers / 任何云服务 **不是必需**。Layer 4 的定时任务可以是 launchd 本地跑、cron 跑、GitHub Actions 跑、Vercel Edge Function 跑、自己 VPS 跑——你挑一个。**默认零云依赖**。Life OS 不绑定任何特定的 serverless 平台。
- 4 层不是"独立的 4 个模块",是"一个系统的 4 层视角"。改一层会影响相邻层。比如 Layer 3 的 Privacy Filter regex 更新,会直接影响 Layer 2 的 ARCHIVER 能写什么到 Layer 1。

**三个方向和 4 层的交叉**：

- **第二大脑**主要活在 Layer 1(数据)+ Layer 2 的读写操作(RETROSPECTIVE 读、ARCHIVER 写)。
- **决策引擎**活在 Layer 2(16 agent 编排)+ Layer 1(读 SOUL / Wiki / Strategic Map)。
- **认知执行智能体**横跨 Layer 2(Cortex 认知前置)+ Layer 3(Shell Hook 强制)+ Layer 4(Python 主动执行)。

所以"智能体层"不是某一层,是跨三层的能力集合。

---

## 一天的完整工作流(真实示例)(A full day workflow · real example)

早上 9:00,Mac 前。场景：昨晚你在手机上用 Notion inbox 记了一条「研究 Japan permanent residency 要求」。

**9:00 · 打开 Claude Code,说"上朝"**

ROUTER 识别到 trigger 词 `上朝` → auto-load 三省六部主题 → 立即 Launch RETROSPECTIVE subagent。

*(Layer 2 的 Skill 层在跑)*

**9:00:05 · Cortex Pre-Router 注入认知标注**(v1.7 GA 已落地)

Pre-Router 认知前置层并行跑：
- 海马体扩散激活："Japan permanent residency" concept → 关联到 "visa status"、"tax residency"、"family planning"、"10-year plan" 四条强边
- GWT 多模块信号竞争：注意力雷达检测到"这是你三个月内第二次提起签证"、预测引擎标注"你上次类似决策低估了准备时间"、社会大脑模块提示"此决策涉及配偶,需 SOUL 社会维度检查"
- 叙事层把这些底层信号打包成："🏛️ 门下省预警：此议题与三个月前议题关联度 78%,请注意重复决策模式"

ROUTER 收到的不是原始消息,是带认知标注的输入。

*(Layer 2 内部的 Cortex 前置层在跑,底下是 Layer 1 的 concept 文件读取)*

**9:00:15 · RETROSPECTIVE 18 步并行**

RETROSPECTIVE 从 Notion 拉回昨晚的 inbox 条目、读 SOUL / user-patterns / Strategic Map、版本检查、巡查、编晨报。

晨报里固定有一块「DREAM Auto-Triggers」——如果昨晚 DREAM 检测到什么跨 session 模式,会出现在这里。

*(Layer 2 Skill + Layer 1 数据读取 + Layer 4 Notion 拉取)*

**9:01 · 决策引擎跑**

你说「这件事值得认真审一下」→ ROUTER 判断这是决策级别 → 进入 Draft-Review-Execute：
- PLANNER 拆成 5 个维度(法律要求、税务影响、时间线、家庭影响、战略关联)
- REVIEWER 做情绪审计 + SOUL 一致性检查 → 发现一个盲点：你的 SOUL 里有"保持灵活性"维度,永居身份可能挑战这个 → 打回 PLANNER 重做
- 第二轮 PLANNER 补上"保持灵活性 vs 稳定性"的 trade-off → REVIEWER 通过
- DISPATCHER 派单 → 六部并行(People / Finance / Growth / Execution / Governance / Infra)
- Governance 部给 6 分 + Finance 部给 9 分,分差 ≥3 → 自动触发 COUNCIL 3 轮辩论
- 最终产出 Summary Report,Overall Rating 7.5/10,3 个 action items

*(Layer 2 Skill 层全程跑,信息隔离由 Claude Code 的真 subagent 保证)*

**9:40 · 你说"退朝"**

ROUTER 立即 Launch ARCHIVER subagent——不在主 context 扫描任何内容,直接进 4 phases：
- Phase 1 Archive：decisions / tasks / journal → outbox
- Phase 2 Knowledge Extraction：扫描整个 session,6 条严格标准 + privacy filter → 自动写 2 条 wiki、更新 SOUL 的"风险承受"维度、Strategic Map 新增一条 Japan-life line
- Phase 3 DREAM：3 天深度复盘,REM 检测到「你最近 3 次决策都在挑战'保持灵活性'维度」→ 写入下次晨报
- Phase 4 Sync：git push + Notion 同步

ARCHIVER 返回 Completion Checklist。Orchestrator 在主 context 执行 Notion MCP 同步(Status page 更新、Todo 同步、Working Memory 写入、Inbox 标 synced)。

*(Layer 2 Skill + Layer 1 数据写入 + Layer 3 git hook 强制 commit)*

**9:45 · Python 脚本后处理**(v1.7 GA 已落地)

Adjourn 后,launchd 触发 `scripts/monthly-review-check.py`——检查是否到月底。如果是,生成 `_meta/self-review-2026-04.md`：
- 统计本月 AUDITOR 召回率、REVIEWER 否决率、COUNCIL 触发率、Express 命中率
- 比对 evals/ 跑出的分数和 AUDITOR 打的分数。如果 AUDITOR 都在打 8+ 但 eval 跑出 3 个 fail → 标记"互相护短"模式写进 user-patterns.md
- 下次 ADVISOR 启动时自动读到这个 pattern,在 Summary Report 里标红提醒

*(Layer 4 Python 工具层,不绑云服务,launchd 本地跑就行)*

**9:46 · Shell hook 审计**

git pre-commit hook 扫描 session 产物：
- 检查 wiki 新文件是否过了 privacy filter(具体 regex 列表：姓名 / 金额 / 账户 ID / 具体公司名白名单)
- 检查 SOUL 更新是否引用了 evidence signals(没引用的更新直接拒绝)
- 检查 Adjourn Completion Checklist 是否完整(4 phases 每个都有返回值,无 TBD 无空值)
- 检查新写的 concept 文件 front matter 是否合法(concept_id / permanence / activation_count 必填)

如果任何一项 fail → 阻止 commit,要求人工确认。不是"提醒你注意",是**硬拒绝**。

*(Layer 3 Shell Hook 层强制执行,code-level 约束 LLM 不偷懒)*

**整个流程**：
- **三个方向都参与**：第二大脑(读写)+ 决策引擎(分析)+ 认知执行(Cortex 前置 + Hermes 级 hook 和脚本)
- **4 层都被调用**：Layer 1 存储 + Layer 2 编排 + Layer 3 强制 + Layer 4 维护
- **你只做了 3 件事**：说"上朝"、选"认真审"、说"退朝"。其余全是系统跑。
- **总时长约 46 分钟**,其中你的键盘操作不超过 5 分钟,剩余 41 分钟系统在并行审议、在写文件、在同步后端、在跑 hook、在做 DREAM 反思——这些都是不打扰你的。

---

## 和其他 AI 工具比(Compared to other AI tools)

**vs ChatGPT / Claude.ai**：日常聊天、代码、翻译、问答——继续用 ChatGPT 或其他通用 AI。Life OS 只在你要做「值得审」的事情时才发挥作用,其余时间 ROUTER 直接返回。Life OS 的独特性不是"更聪明的聊天",是**长期记忆 + 16 agent 制衡 + 认知前置**(认知前置在 v1.7 GA 已上线)。

**vs Obsidian / Notion**：它们做知识管理比 Life OS 强。Life OS 的 wiki 是引擎自动提取的,不是你手敲的。**互补而不是替代**——用 Obsidian 看 Life OS 写的 markdown,体验最好。事实上 Life OS 的 iCloud 第二大脑文件夹就是用 Obsidian vault 的布局,所有 `[[wiki-link]]` 语法能直接跳转。

**vs Todoist / Things**：它们做任务追踪比 Life OS 强太多。Life OS 里的 tasks 是决策流程的副产品——每次决策产生 action items,自动写进 `projects/*/tasks.md`。不是给你手动添加待办的地方。如果你想要纯 GTD 体验,用 Todoist；如果你想要"每个任务背后都有审议过的上下文",用 Life OS。

**vs AI agent 框架(LangGraph / AutoGen / CrewAI)**：它们是给开发者搭 agent 系统的工具。Life OS 是一个**已经搭好的、面向个人生活决策的**具体实例。装一条命令就用,不需要写代码。

**vs Hermes Agent**：最像的参照物,但**架构正交**。

| 维度 | Hermes | Life OS |
|------|--------|---------|
| 定位 | 能做事的通用智能体 | 能思考 + 能记 + 能做事的个人认知系统 |
| 执行力 | 极强(47 原生工具 + 19 平台 + RL 训练) | 中(宿主工具 + MCP + v1.7 的 hook/Python 层) |
| 认知深度 | 弱(单 agent + MEMORY.md 扁平记忆) | 强(16 agent 制衡 + 三层长期记忆 + Cortex 跨 session 记忆 / 概念图谱 / 方法库 / eval-history 自反馈) |
| 学习闭环 | RL 训练 + skills 自学习 | DREAM 反思 + ADVISOR 行为分析 + user-patterns 积累 |
| 运行形态 | 独立 Python runtime,VPS 部署 | 嵌入 Claude Code / Gemini / Codex 的 skill |
| 适合场景 | 执行密集(跑脚本、查资料、跑流程) | 决策密集(权衡、判断、规划) |
| 安装复杂度 | 需要配 Python 环境 + API keys + VPS | 一行命令 `/install-skill` 或 `npx skills add` |

**Life OS 从 Hermes 可以偷的 5 个教训**(已调研记录在 `devdocs/research/2026-04-19-hermes-analysis.md`,v1.7 全部落地)：
1. Shell hook 具体化(v1.7 Layer 3)
2. 结构化会话索引(v1.7 Layer 4 的 `session-index.py`)
3. 方法论作为可插拔 skill(v1.7 Cortex 方法库已实现)
4. 具体安全模式(v1.7 Privacy Filter 改成 regex 清单)
5. 自我评估闭环(v1.7 月度 self-review journal)

Hermes 执行力强认知弱；Life OS 认知强,执行力在 v1.7 GA 已补齐。方向是**吸收 Hermes 的执行模式到 Layer 3 + Layer 4**,保留 Life OS 的 16 agent 制衡和三层记忆。两者不是零和竞争,是互补。

---

## 不支持什么(What Life OS doesn't do)

**单一上下文聊天界面**：ChatGPT、Gemini Web、Claude.ai 的网页版都不行。Life OS 需要 16 个真正独立的 subagent 带信息隔离,一个聊天框做不到。硬塞所有"独立审查"都会变成同一个上下文里的角色扮演,REVIEWER 看得见 PLANNER 的思考过程,veto 就变成走形式。必须在支持真 subagent 的平台上跑：Claude Code / Gemini CLI / OpenAI Codex CLI。

**简单翻译 / 问答 / 单步任务**：「帮我翻译这段日文」「Python 怎么写 list comprehension」「今天东京天气」——ROUTER 直接回,不启动决策流程。硬说「上朝」也没用,ROUTER 会识别出这不是决策。

**你没打算认真听的事**：如果你已经决定要做某件事、只是想让 AI 背书,Life OS 会让你不舒服。REVIEWER 会 veto,ADVISOR 会指出「你上周也做了类似决策、没执行」,AUDITOR 会标记你的强行 override。它是**纠正**确认偏差的工具,不是确认偏差的工具。想要"无条件支持"去找别的 AI。

**多人协作 / 团队决策**：SOUL、user-patterns、strategic map 都是围绕一个人建的。两个人共用一套 second-brain 目前没设计过,会冲突。

**金融、医疗、法律的专业建议**：系统可以帮你思考「这笔投资我该不该做」,但不是持牌顾问。涉及真金白银、健康、法律纠纷,Code of Conduct 第 4 条——**先去找专业人士**。

---

## 为什么要这么复杂(Why so complex)

每次看到 16 agents、9 themes、4 层架构、33 HARD RULEs、Cortex 前置、v1.7 的 Hermes 级执行——都会想：是不是过度工程了？

答案是：**核心原理就 3 个**。

1. **没有一个声音能不受审查地落地**(1400 年前的三省六部原理、Roman Republic、Westminster、现代内阁——所有真正做大决策的地方都是分权)
2. **AI 的判断力再强,也不能替用户决策——只能帮用户看清自己**(ADVISOR 审你,不是审决策；REVIEWER 做情绪审计,不是做结论)
3. **系统必须能学你是谁,否则每次审查都在从零开始**(SOUL + user-patterns + DREAM 自动沉淀；Cortex 让中间过程也能用上记忆,不只是入场退场)

所有复杂度都是这 3 个原理的具体实现：

- **16 agents** 是原理 1 的分权具体化(PLANNER 不能 execute、REVIEWER 只能 veto 不能 rewrite、六部不能互审)
- **9 themes** 是原理 1 的"跨文化表达"——不同文化对"分权制衡"有不同的词汇和美学(三省六部 vs 霞が関 vs C-Suite)
- **三个方向**(第二大脑 / 决策引擎 / 认知执行)是把原理 1-3 拆成可运行的子系统
- **4 层架构** 是把三个方向落到工程上的分层视角
- **Cortex + Hermes 级执行** 是原理 3 在 v1.7 GA 的已落地延伸——让系统不只"在入场退场记",中间过程也能用记忆；让系统不只"能想",还能"主动做"。这是原理 3 从"静态存储"到"动态激活"的延伸
- **33 HARD RULEs** 是这些原理在具体操作上的硬边界(intent clarification 不能跳、SOUL 要引用不能忽略、Notion sync 不能静默失败、Adjourn 不能半途退出、Privacy Filter 不能"人工把关"……)

复杂度是围绕这 3 个核心原理**向外**长的,不是**凭空**堆出来的。想理解系统不用记 33 条规则,只要记住这 3 条原理,规则会从原理里自然推导出来。

也正因为是原理驱动,Life OS 的演化路径是**向外扩展而不是推倒重来**——v1.6.2a 到 v1.7 的 Cortex 不是"重写系统",是"在原理 3 上加更细的实现"。v1.6.2a 到 v1.7 的 Hermes 级执行也不是"改目标",是"把原理 1-2 的规则用 code-level 约束强制下来"。架构在扩,内核不变。

---

> **译注**:本文从 `docs/getting-started/what-is-life-os.md` 同步,2026-04-22 由 auto-translation 流程完成。源文本已为中文,此处保留原文并补齐 i18n frontmatter。技术词(Cortex / Hippocampus / GWT / Narrator / SOUL / Hebbian 等)保留英文。若与 EN 原文出现漂移,以源文件为准。
