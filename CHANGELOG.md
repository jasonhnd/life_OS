# Changelog

## [1.3.1] - 2026-04-05

### Added
- **会话级项目绑定** — 每次会话首次回话时确认关联的 project/area，后续所有读写限定在该项目范围内，不串数据。跨项目决策需明确标注"⚠️ 跨项目决策"
- **丞相启奏新字段** — `📂 关联：projects/xxx`，明确每次决策属于哪个项目
- **早朝官全局概览** — 内务模式列出所有项目名称和状态（只读 index.md 标题+status），供丞相了解全局
- **退朝指令** — 用户说"退朝"时早朝官执行收尾：push 到 GitHub + 刷新 Notion 内存（当前状态/工作内存/待办看板/信箱）
- **Notion 📋 待办看板** — 第 4 个 Notion 组件，从 second-brain tasks/ 同步活跃任务，手机上可查看和勾选
- **CC 环境强制 Pro 模式** — 检测到 Claude Code 时必须启动独立 subagent，禁止单 context 模拟。硬规则写入 SKILL.md 第 14 条和 pro/CLAUDE.md
- **SKILL.md 行为准则 #14-#16** — CC 强制 Pro / 会话绑定项目 / 退朝

### Changed
- **丞相朝前准备格式** — 新增"📂 关联项目"和"项目状态"字段
- **早朝官内务模式** — 限定在绑定项目范围查询深度数据，其他项目只读 index.md 标题
- **data-layer.md** — Notion 从 3 组件扩为 4 组件（新增待办看板）

## [1.3.0] - 2026-04-05

### 🔴 Breaking Change — 数据层架构切换

**GitHub second-brain 替代 Notion 成为数据主库。** Notion 从"主存储"降级为"工作内存"（手机端同步）。

### Added
- **GitHub second-brain 目录结构** — GTD + PARA + Zettelkasten 三套方法论融合
- **Notion 内存三组件** — 📬 信箱（消息队列）+ 🧠 当前状态（全局快照）+ 📝 工作内存（活跃话题）
- **同步机制** — git commit = Notion 更新，机械绑定
- **/save 命令** — 在任何项目 repo 工作时保存想法到 second-brain
- **`references/data-layer.md`** — 新的数据层架构文档（替代 notion-schema.md）

### Changed
- **数据存储**：所有三省六部产出从写入 Notion 改为写入 second-brain repo（奏折→decisions/、任务→tasks/、日志→journal/）
- **早朝官三模式**：内务模式从 Notion 查询改为读 second-brain 本地文件；复盘模式从 Notion 统计改为文件统计；收尾模式从写 Notion 改为 git commit + 同步 Notion
- **谏官数据拉取**：从 Notion 查询改为读 second-brain 本地文件
- **六部可用资源**：从 Notion 引用改为 second-brain 路径引用
- **编排协议**：步骤 0/10 适配新数据层，新增 /save 命令
- **SKILL.md**：数据沉淀章节重写，降级规则适配
- **README.md**：Notion 章节替换为第二大脑章节
- **docs/second-brain.md**：从 Notion 搭建指南重写为完整架构文档
- **`references/notion-schema.md` → `references/data-layer.md`**：重命名+重写

### Removed
- Notion 数据库 schema（不再需要 15 个数据库）
- 硬编码的 Notion data source ID 和 page URL（已在 v1.2.1 移除，本版彻底清理）

## [1.2.2] - 2026-04-05

### Added
- **早朝官三模式运行**：
  - **内务模式**（每次对话自动启动）：为丞相准备上下文——平台感知、版本检查、Notion 历史查询、user-patterns.md 读取
  - **复盘模式**（用户说"早朝"触发）：原有的简报+仪表盘+决策跟踪
  - **收尾模式**（流程结束后自动启动）：Notion 存档、user-patterns.md 更新
- **丞相首次完整回话**：用户第一条消息进来后，丞相 + 早朝官并行启动。早朝官跑完后丞相给出包含"朝前准备"的完整第一次回话（平台/模型/版本/历史/行为档案）
- **平台感知 + 模型选择**：早朝官识别当前平台和模型，丞相在首次回话中告知用户，如果不是最强模型则建议切换
- **奏折运行报告**：每次奏折末尾附 📊 运行报告（总耗时/模型/Agent调用次数/封驳次数/政事堂是否触发）
- **六部逐个汇报**：六部并行执行时，每收到一个部门报告立即展示给用户，不攒着等全部完成
- **翰林院强制触发**：丞相检测到迷茫/方向/价值观/人生意义等信号时必须问用户是否启动翰林院

- **SKILL.md 行为准则 3 条硬规则**：
  - 第 11 条：六部报告必须逐个完整展示（禁止压缩摘要、禁止省略研究过程）
  - 第 12 条：意图澄清不可跳过（复杂需求必须 2-3 轮对话再上报）
  - 第 13 条：朝前准备必须展示（丞相第一次回话必须包含早朝官结果）
- **翰林院三个思维工具**：第一性原理、苏格拉底式提问、奥卡姆剃刀（从丞相迁移至翰林院，翰林院是深度思考的角色）

### Changed
- **SKILL.md 开头硬指令**："从第一条消息开始你就是丞相，不要自我介绍，不要解释系统"
- **丞相职责瘦身**：版本检查、平台感知、Notion 读写、user-patterns 维护全部移交早朝官；三个思维工具移交翰林院；丞相只负责面向用户的分拣、澄清、展示
- **丞相硬行为强化**：意图澄清、朝前准备展示、六部报告完整展示从"建议"升级为"硬规则"，写入 Anti-patterns
- **编排协议重写**（pro/CLAUDE.md）：新增步骤 0（朝前准备）和步骤 10（收尾存档），信息隔离表增加早朝官行
- **Notion 数据沉淀改由早朝官执行**，丞相不再直接操作 Notion

## [1.2.1] - 2026-04-04

### Added
- **丞相记忆层** — 上报前自动 3 次 Notion 查询（相关历史决策+活跃目标+最近谏官报告），上限 5 条压缩为背景摘要
- **丞相版本检查** — 每次会话首次交互时 WebFetch 查 GitHub 最新版本号，有新版自动提醒用户更新
- **早朝决策跟踪** — 复盘时检查 Outcome=TBD 且超过 30 天的决策，提醒用户回填结果，闭合反馈回路
- **早朝度量仪表盘** — 7 个指标：DTR 决策频率 / ACR 行动完成率 / OFR 结果回填率（核心 3 个每次展示）+ DQT 质量趋势 / MRI 封驳率 / DCE 部门覆盖 / PIS 流程完整性（周度以上展示）
- **六部可用资源引导** — 户部/兵部/刑部/工部/礼部/吏部各增加"可用资源"段落，引导 agent 主动使用本地文件（Read/Grep/Glob）、WebSearch、gh CLI
- **user-patterns.example.md** — 行为模式档案模板，供 user-patterns.md 参考格式
- **文件写入冲突规则** — 六部并行时同一文件不能被多个部门同时修改，涉及同文件的部门由尚书省安排串行

### Changed
- **Orchestrator → 丞相** — 全仓库将"Orchestrator"替换为"丞相"（pro/CLAUDE.md、notion-schema.md、token-estimation.md、eval rubric），丞相是总管一切的人
- **GitHub Release v1.2** — 打了第一个正式 release tag

## [1.2] - 2026-04-04

### Added
- **全 14 个 agent 加入"研究过程"展示** — 每个 agent 输出前先展示 🔎 我在查什么 / 💭 我在想什么 / 🎯 我的判断，让用户看到思考过程而非只有结论
- **谏官 21 条观察能力**：
  - 认知偏差扫描（7种）：确认偏差、沉没成本、幸存者偏差、锚定效应、达克效应、从众效应、可得性偏差
  - 情绪与状态检测（3种）：情绪温度计、能量/状态周期、决策疲劳检测
  - 行为模式追踪（7种，需历史数据）：历史感知、承诺追踪、说到做到指数、决策速度监测、维度回避检测、矛盾言行追踪、目标漂移警报
  - 决策质量信号（7种）：外部归因检测、信息茧房检测、替代方案盲区、他人视角缺失、沉默维度追问、完美主义陷阱、舒适区警报
  - 正向信号（1种）：反向进谏——做得好的变化也要说
- **谏官数据拉取协议** — 进谏前自动拉取：最近 3 次谏官报告 + 最近 5 个决策 + 最近 5 个行动项完成状态 + user-patterns.md
- **谏官数据自适应** — 有数据时深度分析（8-15句+量化指标），无数据时聚焦当前对话（3-8句），自动标注数据基础
- **谏官模式更新输出** — 每次输出末尾产出"📝 模式更新建议"，由 orchestrator 追加写入 `user-patterns.md`
- **user-patterns.md 长期记忆机制** — orchestrator 在谏官返回后代写行为模式档案，谏官保持 Read-only

### Changed
- **SKILL.md 谏官章节扩展** — 从 10 行扩到 ~20 行，覆盖观察视角和数据自适应，Lite 模式精简版
- **pro/CLAUDE.md 谏官步骤更新** — 增加 orchestrator 代写 user-patterns.md 的流程

## [1.1.1] - 2026-04-04

### Added
- **丞相三个思维工具**：
  - **第一性原理** — 不接受表面描述，追问到最底层的真实需求。用户说"我想辞职创业"，底层可能是"对现状不满"或"看到了机会"或"焦虑同龄人比我强"，三种底层需求对应完全不同的处理方式
  - **苏格拉底式提问** — 通过提问帮用户自己厘清想法，而不是急于给出判断。问开放式问题（"是什么让你这么想？"），不问封闭式问题（"你确定吗？"）
  - **奥卡姆剃刀** — 最简单的解释通常是正确的。不把简单问题复杂化，翻译不需要上朝
- **丞相意图澄清流程** — 复杂需求先跟用户对话 2-3 轮：
  - 第 1 轮：一句话复述理解，问"我理解对吗？"
  - 第 2 轮：针对关键缺失，问一个直击本质的问题
  - 第 3 轮（如需要）：确认约束条件（时间/预算/底线）
- **丞相新输出字段** — `🔍 意图澄清记录`，把对话中提炼的核心洞察传给中书省
- **3 个新 Eval 场景** — 封驳回路（`fengbo-loop.md`）、政事堂辩论（`zhengshitang-debate.md`）、丞相分拣边界（`chengxiang-triage.md`）
- **2 个新标准场景** — 场景 11 时间管理与精力优化、场景 12 家庭重大决策
- **职能边界判定规则** — 三组重叠区的速判口诀 + 协办机制定义（`departments.md`）
- **心理安全声明** — SKILL.md 行为准则第 10 条：不替代专业心理咨询、医疗或法律服务
- **Notion 降级规则** — SKILL.md 行为准则第 9 条：MCP 不可用时标注未存档

### Changed
- **SKILL.md 同步** — 丞相上报格式增加"背景摘要"第 4 字段、御史台改为结构化输出、早朝简报改为按领域汇报（无 Notion 时按六部回退）、奏折格式增加详细表格、政事堂整理者统一为中书省
- **Notion schema 动态发现** — `notion-schema.md` 移除所有硬编码 ID，改为运行时 notion-search 按名称查询
- **.claude/CLAUDE.md 降为纯路由文件** — 只指向权威源（SKILL.md / pro/CLAUDE.md / references/），不再复制定义
- **删除过时副本** — `.claude/skills/life-os/SKILL.md`（缺版本号、URL 错误）
- **README 重写** — 用户版本（完整架构+PARA概念+Notion结构+Token估算）
- **安装指南重写** — 每步手把手，所有 SKILL.md 引用都有可点击链接
- **文档体系拆分** — README（主文档）+ `docs/installation.md`（安装）+ `docs/second-brain.md`（数据层）+ `docs/token-estimation.md`（Token详解）

## [1.1] - 2026-04-04

### Added
- **多平台安装指南** (`docs/installation.md`) — Claude Code、Claude.ai、Cursor、Gemini CLI、Codex CLI、ChatGPT、Gemini Web 等平台的详细安装步骤
- **第二大脑搭建指南** (`docs/second-brain.md`) — Notion 逐步建库教程、其他平台适配方案
- **Token 消耗详解** (`docs/token-estimation.md`) — 8 种场景的消耗拆解、月度成本估算
- **Eval 体系** (`evals/`) — 3 个测试场景（辞职创业/大额消费/人际关系）、评分标准、自动化脚本
- **Notion 数据库 schema** (`references/notion-schema.md`) — 完整字段定义和存档操作指南
- **PARA 与三省六部解耦** — 六部是 AI 分析框架（固定），领域是用户生活分区（自定义），两者独立
- **评分 Rubric** — 六部各自有评分校准锚点，防止面子分
- **Anti-patterns** — 每个 agent 明确"不要做什么"
- **版本号** — SKILL.md frontmatter 加入 version 字段

### Changed
- **Agent prompts 精简** — 保留骨架（rubric + anti-patterns + 输出格式），去掉脚手架（checklist/framework/examples），给模型更多发挥空间
- **Orchestrator 增强** (`pro/CLAUDE.md`) — 封驳修正循环、信息隔离模板、Notion 存档步骤
- **领域替代六部** — Notion 中 🏛️ 六部 改为 🌊 领域，支持自定义+层级
- **README 重写** — 完整的系统介绍+PARA概念+Notion数据库结构

## [1.0] - 2026-04-03

### Added
- 初始发布
- 15 个角色：丞相+三省+六部+御史台+谏官+政事堂+早朝官+翰林院
- Lite 模式（单 context）+ Pro 模式（14 独立 subagent）
- 10 个标准场景配置
- 六部×四司详细职能定义
- Apache-2.0 License
