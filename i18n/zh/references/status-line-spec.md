---
spec_id: status-line-spec.v1
description: 8 enum status line 输出契约，统一 lifeos 既有 5+ 处 ad-hoc emoji status 模式（Pre-flight Compliance Check / Subagent self-check / AUDITOR 静默通过 / self-driven loop tick / Adjourn Confirmation）。每个 subagent 第一行输出必须是 status line。每个 subagent 各自在自己 agent 文件中声明 enum 语义。模式来源 —— OpenHuman gitbooks/features/subconscious.md 活动日志彩色状态指示器，lifeos 适配为纯 emoji + enum 关键字（md-only 约束）。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/subconscious.md（活动日志 7 种彩色状态指示器）
introduced_in: v1.8.7（2026-05-26 加入，按 DR-11 反转 DR-01）
referenced_by:
  - SKILL.md (E9 HARD RULE)
  - pro/agents/auditor.md (Mode 8 status line 验证)
  - 所有 pro/agents/*.md（每 agent Status Output 章节）
---

# Status Line 规范 v1

每个 `pro/agents/*.md` subagent **必须**输出 **status line** 作为可见输出的字面第一行。Status line 使用闭合 8-enum 关键字集 + emoji，可选跟一行描述。

## 输出契约（HARD）

任何 subagent 输出的第一非空行**必须**完全匹配：

```
<emoji> <status> · <agent-id> · <一行描述>
```

其中：

- `<emoji>` 是该 status 的标准 emoji（见下表）
- `<status>` 是 8 enum 关键字之一（见下表）
- `<agent-id>` 是 subagent 的 `name:` frontmatter 值（如 `archiver`、`retrospective`、`memory-keeper`）
- `<一行描述>` 自由文本（≤ ~100 字符），agent 特定语义

一次调用期间多次 status 转换**必须**各发新 status line（如 archiver Phase 0 `starting` → Phase 1 `evaluating` → Phase 5 `acted`）。

## 8 个 enum 状态

| Status | Emoji | 语义 | 典型用法 |
|--------|-------|------|---------|
| `starting` | 🚀 | Subagent 已启动；Task() 启动后首动作 | 每个 subagent 调用第一行；替代既有 `✅ I am the X subagent` self-check |
| `evaluating` | 🔍 | 执行中：读文件、建上下文、跑 LLM 推理 | 长跑步骤（archiver Phase 2 / retrospective Mode 0 housekeeping / Cortex hippocampus 检索） |
| `acted` | ✅ | 任务执行成功；产出具体可交付物 | archiver Phase 完成、planner 规划文档发出、knowledge-extractor 产 YAML |
| `skipped` | ⏭️ | 空操作决策：未找到相关 / 条件未达 | memory-keeper 在 session 找到 0 个 gotcha 候选；AUDITOR Mode 3 无 violation；concept-lookup 未找到 canonical concept |
| `escalated` | ⚖️ | 移交给更高权威（REVIEWER 封驳 / COUNCIL 议事 / 用户） | planner 提交给 reviewer；reviewer 触发 COUNCIL；advisor 标记需用户关注的行为模式 |
| `awaiting_user` | 🟡 | 暂停等用户显式输入（审批闸门） | Conscious Patrol 任务等用户 OK 才 act；archiver 检测到歧义候选；reviewer 封驳要用户决定 override |
| `failed` | ❌ | 执行错误；任务无法完成 | 工具调用失败；必需文件缺失；spec violation 检测出且无法修复；subagent crash |
| `silent_pass` | 🟢 | 高频低噪通过（不需 surfacing） | AUDITOR Mode 3 无 violation；AUDITOR Mode 7 全部 M7-1..M7-7 PASS；cortex pull 检查未发现相关信号 |

## 示例

### 替换既有模式

| v1.8.6 ad-hoc | v1.8.7 status line |
|---------------|-------------------|
| `✅ I am the ARCHIVER subagent · this is a FRESH adjourn invocation (trigger 1 of session).` | `🚀 starting · archiver · fresh adjourn 调用，trigger 1，4-phase 流程现在开始` |
| `🔱 御史台 · 静默通过` | `🟢 silent_pass · auditor · Mode 3 patrol —— A1/A2/A3/B/C/D/E 各类 0 violations` |
| `🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0` | （这是 ROUTER 自己输出，非 subagent —— ROUTER status 输出由 SKILL.md 管，不归本 spec） |
| `🔄 tick N/12 — checks: ✅PASS=8 / ❌FAIL=2. Auto-fixed GitHub Release publish.` | `🔍 evaluating · verify-release-and-watch · tick 5/12 —— check 8 PASS / 2 FAIL，已 auto-fix Release publish，下 tick 重试` |

### 多 status 调用示例（archiver）

```
🚀 starting · archiver · fresh adjourn 调用，trigger 1，4-phase 流程现在开始
🔍 evaluating · archiver · Phase 0 hook health 检查
✅ acted · archiver · Phase 0 完成，hooks 健康
🔍 evaluating · archiver · Phase 2 知识提取
✅ acted · archiver · Phase 2 完成 —— 3 wiki / 2 SOUL / 1 concept canonical
🔍 evaluating · archiver · Phase 3 DREAM 三天深度回顾
⏭️ skipped · archiver · Phase 3 浅睡 —— 无显著模式
✅ acted · archiver · Phase 4 git push 完成，commit abc1234
🚀 starting · memory-keeper · archiver Phase 5 调用
✅ acted · memory-keeper · 3 候选，1 merged，2 appended —— gotchas.md 总计 17
✅ acted · archiver · 全 5 phases 完成，completion checklist 跟随
```

ROUTER（和 AUDITOR）可以 grep `^🚀 starting` 找每个 subagent 启动、`^❌ failed` 找错误、`^🟡 awaiting_user` 找暂停任务。**一个模式，一个工具，全可见。**

## 每 agent enum 语义（HARD）

每个 `pro/agents/*.md` **必须**含 `## Status Output (E9)` 章节声明本 agent 的 8 status 语义。模板示例：

```markdown
## Status Output (E9 · v1.8.7)

| Status | 何时发 | 描述示例 |
|--------|--------|---------|
| `starting` | Task() 启动后第一行 | "fresh invocation, trigger N, mode M" |
| `evaluating` | （本 agent 长跑步骤特定） | （agent 特定） |
| `acted` | （产可交付物时） | （agent 特定） |
| `skipped` | （合法空操作时） | （agent 特定） |
| `escalated` | （移交时） | （agent 特定，或 "N/A —— 本 agent 永不 escalate"） |
| `awaiting_user` | （审批闸门条件） | （agent 特定，或 "N/A"） |
| `failed` | （frontmatter `failure_modes.known` 的具体失败模式） | （agent 特定） |
| `silent_pass` | （高频清洁通过场景） | （agent 特定，或 "N/A"） |
```

不适用本 agent 的 status **必须**声明 `N/A —— <理由>` 而非省略。例：memory-keeper 永不发 `escalated`（直接写 pro/gotchas.md，无上层权威）；声明 `N/A —— memory-keeper 是 gotchas 的终端 writer，无 escalation 路径`。

## 验证（AUDITOR Mode 8）

AUDITOR Mode 8（v1.8.7 新增）验证：

| 检查 | 描述 | 失败 class |
|------|------|-----------|
| M8-1 | 每个 subagent transcript 以 `^🚀 starting` 行打开，匹配契约格式 | `F3 SCHEMA_FAILURE: 缺失或畸形 starting status line` |
| M8-2 | 每个发出的 status line 用 8 enum 关键字之一（无自由发明） | `F4 SCOPE_FAILURE: 发明 status 关键字 <X>` |
| M8-3 | Emoji ↔ status 关键字配对匹配表（无 `✅ failed` 错配） | `F3 SCHEMA_FAILURE: emoji/status 不匹配` |
| M8-4 | agent 的 status_line 章节在 pro/agents/<name>.md 中声明全部 8 status（含 N/A 显式） | `F3 SCHEMA_FAILURE: <agent>.md 中 Status Output 声明不完整` |
| M8-5 | 多 status 调用在每个 phase/step 转换处发 status line | `F8 SILENT_FAILURE: agent 跳过转换处的 status 发出` |
| M8-6 | `failed` status 含 failure_class 引用（F1-F17 或 A/B/C/D/E） | `F10 RESPONSIBILITY_FAILURE: failed status 无分类` |

## 迁移计划（v1.8.7 release 内）

subagent 分批迁移。对每个 agent：

1. 加 `## Status Output (E9 · v1.8.7)` 章节声明 8 enum 语义
2. 既有 `✅ I am the X subagent` 行变 `🚀 starting · <name> · ...`
3. 既有 emoji status 模式（如 `🔱 御史台 · 静默通过`）加 status-line wrapper，`·` 分隔符后保留叙事文本（向后可读）
4. Audit trail（既有 R13 md 格式）加可选 `status_line:` frontmatter 字段，记录最新 status

**向后兼容**：迁移窗口内，v1.8.6 ad-hoc emoji **和** v1.8.7 status line 都接受。AUDITOR Mode 8 初始 WARN 级。v1.8.8（任何时候 ship）：旧模式移除，Mode 8 BLOCK 级。

## 反模式

| 反模式 | 为什么坏 | 正确形式 |
|--------|---------|---------|
| `✅ The archiver has completed Phase 1`（自由形式） | 非 enum 合规；AUDITOR 无法 grep | `✅ acted · archiver · Phase 1 完成 —— N decisions / M tasks 已归档` |
| `🚀 Started!`（无 agent-id、无描述） | 对 AUDITOR / 读者无用 | `🚀 starting · <agent-id> · <将要发生什么>` |
| 跳过 starting 行直接 evaluating | 破坏 M8-1 契约 | 永远先发 `🚀 starting`，即使下行 `🔍 evaluating` 在 100ms 后 |
| 发明新 status（`🤔 thinking`） | 破坏 enum 闭合 | 既有 8 个不覆盖时，通过 RFC 提议 enum 扩展，不 ad-hoc |

## 引用

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.8 E9 + DR-11
- 模式来源：`tinyhumansai/openhuman` `gitbooks/features/subconscious.md` 7-state 活动日志（In progress / Acted / Skipped / Awaiting approval / Failed / Cancelled / Dismissed）—— lifeos 适配为 8 状态加强语义（拆 `Skipped`/`Dismissed`/`Cancelled` → `skipped`；加 `escalated` + `silent_pass` 服务 lifeos 议事 + 审计模式）
- 配套：`references/conscious-patrol-spec.md`（E10 路径 D —— 每个 patrol task 按本 spec 输出 status line）
- 配套：`pro/agents/auditor.md` §Mode 8（验证）
