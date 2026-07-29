---
spec_id: status-line-spec.v1
description: Life OS subagent 的 8 枚举状态行输出合同。它把零散的状态提示统一成可 grep 的首行格式。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/subconscious.md
introduced_in: v1.8.7
referenced_by:
  - SKILL.md (E9 HARD RULE)
  - agents/auditor.md (Mode 8 status line verification)
  - agents/*.md (per-agent Status Output section)
---

# Status Line Specification v1

每个 `agents/*.md` subagent 都必须把 **status line** 作为可见输出的第一行。状态行使用封闭的 8 枚举关键词和规范 emoji；agent id 后面可以跟一行短说明。

## Output Contract

任何 subagent 输出的第一条非空行必须匹配：

```text
<emoji> <status> · <agent-id> · <one-line description>
```

字段含义：

- `<emoji>` 是该状态的规范 emoji。
- `<status>` 是下方 8 个枚举关键词之一。
- `<agent-id>` 是 subagent `name:` frontmatter 的值，例如 `archiver`、`retrospective`、`memory-keeper`。
- `<one-line description>` 是自由文本，建议控制在 100 字符以内，用来说明当前步骤。

一次调用中如果发生多次状态转换，必须各输出一条新的 status line。例如：启动时 `starting`，长时间读取/推理时 `evaluating`，产出具体结果后 `acted`。

## The 8 Statuses

| Status | Emoji | Semantics | Typical use |
|--------|-------|-----------|-------------|
| `starting` | 🚀 | subagent 已启动；launch 后第一动作 | 每次 subagent 调用的第一行 |
| `evaluating` | 🔍 | 正在读取、构建上下文或推理 | 长步骤、检索、检查 |
| `acted` | ✅ | 已产出具体结果 | 阶段完成、计划输出、写入完成 |
| `skipped` | ⏭️ | 合法 no-op | 无相关信号、无候选、条件不满足 |
| `escalated` | ⚖️ | 交给更高权威处理 | REVIEWER veto、COUNCIL debate、用户审批 |
| `awaiting_user` | 🟡 | 等待用户明确输入 | 审批闸门或 override 决策 |
| `failed` | ❌ | 无法完成 | 工具失败、必需文件缺失、阻塞级 spec 违规 |
| `silent_pass` | 🟢 | 低噪音 clean pass | auditor clean pass、无相关 Cortex 信号 |

## Examples

```text
🚀 starting · archiver · fresh adjourn invocation, trigger 1, Phase 1-5 starting
🔍 evaluating · archiver · Phase 0 runtime readiness
✅ acted · archiver · Phase 0 complete, hook layer retired and inline enforcement active
🔍 evaluating · archiver · Phase 2 knowledge extraction
✅ acted · archiver · Phase 2 complete: 3 wiki, 2 SOUL, 1 concept
⏭️ skipped · archiver · Phase 3 light sleep, no significant patterns
✅ acted · archiver · Phase 4 git push complete, commit abc1234
🚀 starting · memory-keeper · Phase 5 invoked by archiver
✅ acted · memory-keeper · 3 candidates, 1 merged, 2 appended, gotchas.md total 17
✅ acted · archiver · all five phases complete, completion checklist follows
```

ROUTER 和 AUDITOR 可以 grep `^🚀 starting` 找 subagent launch，grep `^❌ failed` 找失败，grep `^🟡 awaiting_user` 找等待用户的工作。

## Per-Agent Semantics

每个 `agents/*.md` 文件都必须包含 `## Status Output (E9)` 小节，声明 8 个状态在该 agent 中的具体含义。模板：

```markdown
## Status Output (E9 · v1.8.7)

| Status | When emitted | Example description |
|--------|--------------|---------------------|
| `starting` | First line after launch | "fresh invocation, trigger N, mode M" |
| `evaluating` | Agent-specific long-running steps | "reading source files" |
| `acted` | Deliverable produced | "planning document emitted" |
| `skipped` | Legitimate no-op | "no candidates found" |
| `escalated` | Handing off | "requires reviewer veto loop" |
| `awaiting_user` | Approval gate | "waiting for explicit override" |
| `failed` | Blocking failure | "required file missing" |
| `silent_pass` | Clean pass | "no violations found" |
```

如果某个状态不适用于该 agent，必须写 `N/A · <reason>`，不能直接省略。

## Validation

AUDITOR Mode 8 验证：

| Check | Description | Failure class |
|-------|-------------|---------------|
| M8-1 | 每个 subagent transcript 都以符合格式的 `^🚀 starting` 开头 | `F3 SCHEMA_FAILURE` |
| M8-2 | 每条 status line 都使用 8 个枚举关键词之一 | `F4 SCOPE_FAILURE` |
| M8-3 | emoji 和 status keyword 的配对符合表格 | `F3 SCHEMA_FAILURE` |
| M8-4 | agent 的 Status Output 小节声明全部 8 个状态 | `F3 SCHEMA_FAILURE` |
| M8-5 | 多步骤调用在重要阶段转换处输出 status line | `F8 SILENT_FAILURE` |
| M8-6 | `failed` 包含或指向 failure class | `F10 RESPONSIBILITY_FAILURE` |

## Anti-Patterns

| Anti-pattern | Why bad | Correct form |
|--------------|---------|--------------|
| `The archiver has completed Phase 1` | 不符合枚举，难以 grep | `✅ acted · archiver · Phase 1 complete: N decisions archived` |
| `🚀 Started!` | 缺少 agent id 和说明 | `🚀 starting · archiver · fresh adjourn invocation` |
| 直接以 `evaluating` 开头 | 违反 M8-1 | 永远先输出 `🚀 starting` |
| 发明 `thinking` | 破坏枚举闭包 | 使用 8 个状态之一，或通过 RFC 扩展 |

## Reference

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.8 E9 + DR-11
- `references/conscious-patrol-spec.md`
- `agents/auditor.md` Mode 8
