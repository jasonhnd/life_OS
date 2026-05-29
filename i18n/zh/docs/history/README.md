# 历史存档（冻结的 v1.7 时代文档）

本目录存放**冻结的历史文档**——v1.7 时代的设计快照与用户指南，已被取代，但保留下来用于理解系统如何演进。这里每个文件都带 `status: legacy` / `authoritative: false`。

**这些都不是当前权威。** 当前权威是：

- `pro/CLAUDE.md`（+ `pro/AGENTS.md` / `pro/GEMINI.md`）—— 编排协议
- `pro/agents/*.md` —— 子 agent 定义
- `references/*.md` —— 当前数据模型 + 规范
- `docs/` 里 `history/` **以外**的一切 —— 当前用户文档

## 内容

- **`cortex/`** —— v1.7 Cortex 用户指南（always-on 设计）。Cortex 在 **v1.8.0 改为 pull-based**（当前行为见 `pro/CLAUDE.md` §0.5）。英文版完整存档在 `docs/history/`，另含 `architecture/`、`v1.7-migration.md` 等更多内容。

## 为什么保留（而不是删除）

Git 历史已经保留了每个被删文件，所以删除不会*丢失*任何东西。这里把 v1.7 设计原理作为单一合并存档保留下来，让它无需 `git show` 就能读。

> **入链说明：** 冻结记录—— CHANGELOG 条目、`pro/compliance/*`、`_meta/rfc/*` ——故意仍引用移动*之前*的原始路径。它们是当时路径的历史记录，刻意**不**改写。当前文档与规范用新的 `docs/history/...` 路径链接到这里。
