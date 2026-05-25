---
spec_id: feature-workflow-spec.v1
description: lifeos 功能设计工作流 —— Specify → Evals scenarios 定义 → Implement → Verify（4 阶段）。"Evals scenarios 定义"阶段是硬性 —— planner 无论复杂度都必须在规划 frontmatter 列出 evals scenarios，dispatcher 才接受。借鉴自 tinyhumansai/openhuman AGENTS.md §"Feature design workflow" 规划规则。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, AGENTS.md:507-521 (Feature design workflow + 规划规则 "E2E scenarios up front")
introduced_in: v1.8.7
referenced_by:
  - pro/agents/planner.md (evals_scenarios 必填字段)
  - pro/agents/dispatcher.md (dispatch 前校验)
  - pro/agents/reviewer.md (批准前验证 scenarios 完整)
---

# 功能工作流规范 v1

lifeos 的功能/变更设计遵循 4 阶段工作流。硬性要求：**scenarios 在实施开始前定义**，不是事后。无 scenarios 的规划文档是不完整的；dispatcher 拒绝。

## 背景

之前 lifeos 的规划约定是：planner 写规划文档 → reviewer 批准 → dispatcher 派到 domains → reviewer final → archiver。eval-first 原则是隐式的：planner **应该**定义测试 scenarios，但未通过 frontmatter 字段强制。

结果：复杂规划文档有时无 evals 就 ship；lifeos 的 eval-first 哲学停留在愿景。v1.8.7 把它变成契约。

## 4 个阶段

```
1. Specify          → 写规划文档含 Subject + 背景 + 范围
2. Evals 定义       → frontmatter evals_scenarios: [...] 非空（硬性）
3. Implement        → 6 domains 按 dispatcher 顺序执行
4. Verify           → reviewer final + AUDITOR Mode 3 对 scenarios 交叉检查
```

阶段 2 是新硬性要求。

## evals_scenarios frontmatter 字段（硬性）

每个规划文档（走 dispatcher → domains → reviewer-final 的文档）frontmatter 必须含：

```yaml
---
subject: <一行>
background: |
  <多行上下文>
scope: [...]
evals_scenarios:
  - <路径 or N/A: 原因>
  - <路径 or N/A: 原因>
---
```

**每个 scenario 条目可接受的值**：

1. **指向既有 fixture 的路径**：`evals/scenarios/<name>.md` —— fixture 文件必须存在且反向引用本规划文档
2. **N/A 带原因**：`N/A: docs-only` / `N/A: pure-translation` / `N/A: i18n-mirror-update` —— 用于真的不需要运行时测试的改动（原因必须是允许枚举之一；随意的 "N/A: 见下文" 被拒）
3. **未来承诺**：`TBD: evals/scenarios/<name>.md (commit-by: <PR/issue/日期>)` —— 带截止的 escape hatch；dispatcher 接受但 reviewer-final 永远拒绝直到 TBD 解决

**不可接受的值**：

- 空列表 `[]` —— 实施不能在无测试定义下进行
- 整个缺 `evals_scenarios:` key —— 同空
- `N/A: see below` / `N/A: TBD` 无枚举原因
- 指向不存在 fixture 的路径（dispatcher 验证路径存在）

## 允许的 N/A 原因枚举

```yaml
N/A: docs-only           # 纯文档，无行为变化
N/A: pure-translation    # 既有 EN 内容的 i18n/zh 或 i18n/ja 翻译
N/A: i18n-mirror-update  # 把漂移的镜像恢复到 EN 内容（无新行为）
N/A: typo-fix            # 单词/单行修正，无语义变化
N/A: cleanup-only        # 移除死代码/无用引用，无行为变化
```

枚举外的任何原因 → dispatcher 拒绝 `F4 SCOPE_FAILURE: invalid N/A reason；从枚举选或写 scenario`。

## 何时适用（何时不适用）

### 适用（硬性强制）

- ROUTER 升级到 PLANNER 的任何规划文档（full deliberation 路径）
- 任何 `_meta/rfc/v<X.Y>-*.md` 中触及 agent 行为或 spec 语义的 RFC
- 任何新 agent（`pro/agents/<new>.md`）—— 至少需 1 个 fixture 验证 agent 主要行为
- 任何引入 SKILL.md 或 pro/CLAUDE.md 的新 HARD RULE

### 不适用（范围外）

- ROUTER "Handle Directly" 路径 —— 短对话响应
- Express Analysis 路径 —— domains 跑但无 PLANNER 步骤（由 ROUTER 简报覆盖）
- 笔记 / 日志条目 / SOUL 快照 / sessions
- 已测试代码路径上的 bug 修复（既有 fixture 覆盖；planner 引用既有路径即可）

## Dispatcher 校验

Dispatcher 接受规划文档前往下游执行前：

1. 读规划文档 frontmatter
2. 找 `evals_scenarios:` key
3. 按上述规则验证：
   - 非空列表
   - 每条是路径-存在 OR 允许-N/A OR TBD-带截止
4. 验证失败：
   - 输出 `F4 SCOPE_FAILURE: planning doc <path> missing or invalid evals_scenarios`
   - 暂停 dispatch
   - 返回 planner 含具体失败（planner 重试；升级到用户前最多 3 轮）

## Reviewer-final 校验

6 domains 完成 + reviewer-final 跑后：

1. 读规划文档 frontmatter `evals_scenarios:`
2. 对每个 `evals/scenarios/<name>.md` 条目：验证 fixture 存在且其期望行为本 session 已演示
3. 对 `TBD:` 条目：拒绝 `F10 RESPONSIBILITY_FAILURE: TBD scenarios 在 release 前未解决；本 session 落地 fixture 或拆 follow-up issue`
4. 对 `N/A:` 条目：接受但记 audit trail 供 AUDITOR Mode 3 review

## 反模式

看上去对但实际逃避的：

### 反模式 1：万能 "smoke" fixture

```yaml
evals_scenarios:
  - evals/scenarios/smoke-test.md   # 实际为空 / 写着 "TODO"
```

Dispatcher 必须检查 fixture 文件有非平凡内容（≥30 行或 ≥1 接受标准）—— 否则视为空。

### 反模式 2：复用不相关 fixture

```yaml
evals_scenarios:
  - evals/scenarios/start-session-compliance.md   # 但本 PR 关于 archiver，不是 start session
```

Reviewer-final 应检查 fixture 的 `applies_to:` frontmatter 与 PR 范围对比检测不匹配。不匹配 → 拒绝。

### 反模式 3：模糊 N/A

```yaml
evals_scenarios:
  - N/A: trust me
```

不在允许枚举内 → dispatcher 拒绝。

### 反模式 4：整个缺字段

```yaml
subject: ...
background: ...
# evals_scenarios 未出现
```

缺字段 = 缺 eval。Dispatcher 视为空列表 → 拒绝。

## 例（正确）

### 例 1：新功能带新 fixture

```yaml
subject: v1.8.7 C6 — gotchas + memory-keeper
evals_scenarios:
  - evals/scenarios/v1.8.7-c6-memory-keeper-seed.md
  - evals/scenarios/v1.8.7-c6-archiver-phase5.md
```

### 例 2：纯文档改动

```yaml
subject: 修 references/concept-spec.md 的 typo
evals_scenarios:
  - N/A: typo-fix
```

### 例 3：i18n 镜像更新

```yaml
subject: 章节重排后恢复 i18n/zh/references/agent-spec.md 到 EN
evals_scenarios:
  - N/A: i18n-mirror-update
```

### 例 4：scenarios 承诺但 fixture 同 session 落地

```yaml
subject: v1.8.7 F11 — i18n diff parity
evals_scenarios:
  - evals/scenarios/v1.8.7-f11-check-9-pass.md
  - evals/scenarios/v1.8.7-f11-check-9-warn-drift.md
  - evals/scenarios/v1.8.7-f11-check-9-block-future.md (TBD: 本 release 仅加 WARN，BLOCK 场景 v1.8.8 落地)
```

TBD 条目有明确截止（v1.8.8）。Dispatcher 接受；reviewer-final flag TBD 作 v1.8.8 follow-up。

## 引用

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.5 B5
- 模式来源：`tinyhumansai/openhuman` AGENTS.md:507-521（Feature design workflow + 规划规则）
- 配套：`pro/agents/planner.md`（模板定义）、`pro/agents/dispatcher.md`（校验逻辑）
- 相关：`references/agent-spec.md`（agent 定义也得益于此纪律）
