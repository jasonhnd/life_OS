# `_meta/` 不该加什么

> **故意保持近空原则**：本目录放**运行时工件** + **历史快照** + **RFC 文档**。是系统的工作记忆，不是权威 spec 或 agent 定义的归宿。

## 什么 **不** 属于这里

1. **权威规范** —— 如"audit trail 工作方式定义"。→ 去：`references/<name>-spec.md`（含三语镜像）。
2. **Agent 定义** —— 那是 `pro/agents/` 专属。
3. **用户决策或知识** —— 如"用信托结构的决定"。→ 去（用户的 second-brain）：`decisions/` 或 `_meta/wiki/`。
4. **SOUL.md 或 theme 文件** —— SOUL 放用户 second-brain 根；theme 放 `themes/`。
5. **构建产物 / 编译工件** —— lifeos 无构建步骤（md-only）。若你想加 `_meta/dist/` 或 `_meta/build/`，是在解决错的问题。
6. **任何匹配 forbidden_extensions 的文件** —— `.sql / .json / .sh / .bash / .py / .yml / .yaml / .db / .sqlite`（见 `SKILL.md` md-only 本体论约束）。按 DR-10 v1.8.7，不可妥协。

## 什么 **属于** 这里

- `_meta/runtime/<sid>/*.md` —— 单 session audit trails（R12 + R13 schema）
- `_meta/rfc/v<X.Y>-*.md` —— 各发版 RFC 文档
- `_meta/sessions/<sid>.md` —— 单 session 归档
- `_meta/wiki/` —— 用户知识库（用户 second-brain，不在 dev repo）
- `_meta/concepts/` —— Cortex 突触图（用户 second-brain）
- `_meta/snapshots/soul/<sid>.md` —— adjourn 时的 SOUL 快照
- `_meta/journal/` —— DREAM 报告
- `_meta/outbox/<sid>/` —— git sync 前的暂存写入
- `_meta/compression/<sid>-compress-<ts>.md` —— 手动 `/compress` 输出
- `_meta/release-notes/v<X.Y>.md` —— 发版说明
- `_meta/incidents/<id>.md` —— 事件决策记录（`no-change` 等）

## Dev-repo vs 用户 second-brain 区分

lifeos **dev repo** 的 `_meta/` 含：`rfc/` + `release-notes/` + `methods/` + 历史 `v1.8.4-snapshot/`。**不含** `sessions/` / `concepts/` / `wiki/` —— 这些只存在于用户 second-brain 的运行时。

写新 spec 或功能涉及 `_meta/` 时，明确路径活在：
- **dev repo** 的 `_meta/`（lifeos 源码）—— 如 `_meta/rfc/`、`_meta/release-notes/`
- **用户 second-brain** 的 `_meta/`（用户运行数据）—— 如 `_meta/sessions/`、`_meta/runtime/`、`_meta/wiki/`

两者混淆是反复出现的坑（见 seed 后的 `pro/gotchas.md`）。

## 引用

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- 模式来源：`tinyhumansai/openhuman` `.claude/rules/README.md`
- 配套：`SKILL.md` HARD RULE md-only 本体论约束（DR-10）
