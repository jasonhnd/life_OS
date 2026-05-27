# `references/` 不该加什么

> **故意保持近空原则**：本目录放**权威规范**（`*-spec.md`）和**共享参考表**（如 `domains.md`、`failure-taxonomy.md`）。不是"任何我想让 agent 读的文档都丢这里"的杂物间。

## 什么 **不** 属于这里

1. **单次会话报告、运行时工件、audit trail** —— 如"2026-05-25 archiver 的输出"。→ 去：`meta/runtime/<sid>/` 或 `meta/sessions/<sid>.md`。
2. **面向用户的教程或快速上手** —— 如"如何安装 lifeos"。→ 去：`README.md` / `docs/` / `gitbooks/`。
3. **内部设计笔记 / 头脑风暴 / 草稿** —— 如"v2.0 cascade seal 的想法"。→ 去：`meta/rfc/v<X.Y>-*.md`（RFC）或 `meta/workpad/`（若引入）。
4. **Agent 定义或 theme 文件** —— 那是 `pro/agents/` 和 `themes/` 专属领域。
5. **纯叙事无规范内容** —— 如"lifeos 各版本历史"。→ 去：`CHANGELOG.md` / RFC 引用段。
6. **没有三语镜像的 spec** —— 每个 `references/*-spec.md` 合入前必须先准备好 `i18n/zh/references/<同名>.md` 和 `i18n/ja/references/<同名>.md`。不允许残缺 spec。
7. **没有 `spec_id` / `status` / `authoritative` frontmatter 的 spec** —— 参考现有 spec 文件看必需 schema。

## 什么 **属于** 这里

满足以下的权威规范：
- 定义 ≥2 个 agent 会引用的 schema、格式或契约
- 含 `spec_id: <name>.v<N>`、`status: active|legacy|proposal`、`authoritative: true|false`、`introduced_in: v<X.Y>` frontmatter
- 三语镜像就位（`i18n/zh/references/` + `i18n/ja/references/`）
- 有 `referenced_by:`（前向引用至少一个 agent / 命令 / SKILL.md）
- 是该话题的**单一真相源**（不与他处 spec 重复）

## 加新 spec 前 — Minimality Rule 检查

按 `pro/CLAUDE.md` Minimality Rule（v1.8.5 Stage 7），先问 6 个问题：

1. 一条**规则**（在 `pro/CLAUDE.md` 或 SKILL.md 中）能解决吗？
2. 既有 spec 加一个 **schema 字段**能解决吗？
3. 既有 spec 加**一个章节**能解决吗？
4. 一个**回归用例**（`evals/scenarios/*.md`）能解决吗？
5. **AUDITOR audit rule** 能解决吗？
6. `pro/CLAUDE.md` 加个**人工 checklist** 能解决吗？

任何一个答案为是，优先低成本选项。新 spec = 三个文件（EN + zh + ja）+ 永久 referenced_by 图维护 + i18n diff parity 检查义务。

## 引用

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- 模式来源：`tinyhumansai/openhuman` `.claude/rules/README.md`
- 配套：`references/i18n-diff-parity-spec.md`（v1.8.7 保证本目录所有文件三语对齐）
