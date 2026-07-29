# `scripts/` 不该加什么

> **故意保持近空原则**：本目录只放两个子目录 —— `commands/`（slash 命令 md 源，安装到用户 `~/.claude/commands/`）和 `prompts/`（ROUTER 读取并内联执行的维护 prompt）。两个子目录从 v1.8.5/v1.8.6 起均 md-only。

## 什么 **不** 属于这里

1. **任何 `.sh` / `.bash` shell 脚本** —— 按 `SKILL.md` md-only 本体论约束（DR-10 v1.8.7）。v1.8.5 退役整个 bash hook 层；v1.8.7 让那次退役永久化。禁止扩展名：`.sh / .bash / .py / .yml / .yaml / .json / .sql / .db / .sqlite`。
2. **任何 `.py` Python 脚本** —— 同上。
3. **"只给我自己用的"新 slash 命令** —— slash 命令面向用户；必须有清晰名 + argument-hint + description 并作为发版一部分发布。个人一次性自动化直接放你的 `~/.claude/commands/`（不进本 repo）。
4. **没有触发词的新维护 prompt** —— `scripts/prompts/*.md` 由 ROUTER 通过 `hosts/CLAUDE.md` 中文档化的自然语言模式调用。没有文档化触发词的 prompt 是死代码。
5. **用户用的文档** —— `docs/` 和 `gitbooks/` 干这个。
6. **辅助函数 / 库** —— scripts/ 里没有辅助库；命令和 prompt 是自包含的 LLM 驱动 md 文件。

## 什么 **属于** 这里

### `scripts/commands/<name>.md`

面向用户的 slash 命令。每个单 md 文件含 `description:` 和 `argument-hint:` frontmatter。由 `/install-agents` 或类似方式安装到 `~/.claude/commands/<name>.md`。

当前：`compress.md`、`inbox-process.md`、`memory.md`、`method.md`、`monitor.md`、`research.md`、`search.md`。

### `scripts/prompts/<name>.md`

ROUTER 内联读取的内部维护 prompt（无安装步骤）。由 `hosts/CLAUDE.md` §"自动触发规则"文档化的自然语言模式触发。

当前 21+ 个 prompt（advisor-monthly、archiver-recovery、auditor-mode-2、backup、daily-briefing、eval-history-monthly、extract-concepts、inbox-process、migrate-confidence、migrate-from-v1.6、migrate-to-wikilinks、rebuild-concept-index、rebuild-session-index、reindex、research、review-queue、snapshot-cleanup、spec-compliance、strategic-consistency、wiki-decay、wiki-link-audit、wiki-obsidian-upgrade）。

## 加新命令或 prompt 前 — Minimality Rule 检查

按 `hosts/CLAUDE.md` Minimality Rule：

1. **ROUTER 原生处理**就行（不需要新命令）吗？
2. **既有命令/prompt 扩展**能解决吗？
3. **某 agent 既有流程**能吸纳这个吗？
4. **回归 fixture** + AUDITOR mode 能解决吗？

任何一个答案为是，优先那个。新命令 = 永久维护 + 安装/卸载逻辑 + 跨 host 兼容（Claude Code / Gemini CLI / Codex CLI）。

## 引用

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- `SKILL.md` HARD RULE md-only 本体论约束（DR-10）
- 模式来源：`tinyhumansai/openhuman` `.claude/rules/README.md`
