# Changelog

## [1.1.0] - 2026-04-04

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

## [1.0.0] - 2026-04-03

### Added
- 初始发布
- 15 个角色：丞相+三省+六部+御史台+谏官+政事堂+早朝官+翰林院
- Lite 模式（单 context）+ Pro 模式（14 独立 subagent）
- 10 个标准场景配置
- 六部×四司详细职能定义
- Apache-2.0 License
