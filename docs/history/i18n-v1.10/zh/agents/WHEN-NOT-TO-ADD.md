# `agents/` 不该加什么

> **故意保持近空原则**：本目录仅放 **subagent 定义**。每个 `*.md` 定义一个 Task 可启动的角色，含 v2 agent-spec frontmatter。加非 agent 文件会稀释目录用途、误导 ROUTER 的角色发现。

## 什么 **不** 属于这里

1. **通用助手 / 工具 prompt** —— 如"帮我起 commit message 的 markdown"。→ 去：`.claude/commands/`（slash 命令）或 `scripts/prompts/`（维护 prompt）。
2. **Spec / schema 文档** —— 如"audit trail 文件长什么样"。→ 去：`references/<topic>-spec.md`。
3. **用户用的参考文档** —— 如"如何使用 auditor agent"。→ 去：`docs/` 或 `gitbooks/`（如果再引入）。
4. **单次会话状态、audit trail、踩坑记录** —— 如"本次 session 的 archiver 输出"。→ 去：`meta/runtime/<sid>/`（audit trails）或 `gotchas.md`（经验教训）。
5. **Theme 文件（display name / emoji / tone）** —— 如"中世纪设定的新主题"。→ 去：`themes/<name>.md`。
6. **没有 v2 agent-spec frontmatter 的 agent** —— 即使角色合理，也必须先符合 `references/agent-spec.md` v2（6 facets + operating_hypothesis + context_manifest + blast_radius + failure_modes）才能进来。

## 什么 **属于** 这里

满足以下全部的 subagent 定义：
- Task 可启动（Claude Code 能 `Task(<name>)`）
- 责任唯一且不重叠（对照本目录现有 agent 检查）
- v2 agent-spec frontmatter 完整
- blast radius 清楚（声明可写 / 不可写文件）
- 失败模式 + 恢复动作有文档

## 加新 agent 前 — Minimality Rule 检查

按 `hosts/CLAUDE.md` Minimality Rule（v1.8.5 Stage 7），先问 6 个问题：

1. 一条**规则**（在 `hosts/CLAUDE.md` 中）能解决吗？
2. 一个 **schema 字段**（在 `references/*-spec.md` frontmatter 中）能解决吗？
3. 一个**验证器**（slash 命令或 AUDITOR mode）能解决吗？
4. 一个**回归用例**（`evals/scenarios/*.md`）能解决吗？
5. **既有 agent 执行流程中的一个 stop condition** 能解决吗？
6. **相关文档加个人工 checklist** 能解决吗？

任何一个答案为是，优先低成本选项。新 agent = 昂贵（永久维护、AUDITOR 目标、9 个 theme 中的名字、三语 spec、audit trail schema、blast radius 强制）。成本-收益门槛要高。

## 引用

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- 模式来源：`tinyhumansai/openhuman` `.claude/rules/README.md`（"This directory is intentionally near-empty. Stale rules actively mislead agents."）
- 配套 spec：`references/agent-spec.md`（v2 frontmatter 标准）
