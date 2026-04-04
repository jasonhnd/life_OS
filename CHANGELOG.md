# Changelog

## [1.1.1] - 2026-04-04

### Added
- **丞相思维工具** — 第一性原理（追问到底层需求）、苏格拉底式提问（用问题帮用户想清楚）、奥卡姆剃刀（不把简单事搞复杂）
- **丞相意图澄清流程** — 复杂需求先跟用户对话 2-3 轮（复述理解→追问本质→确认约束），再上报朝廷
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
