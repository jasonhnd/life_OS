---
spec_id: refactoring-patterns.v1
description: life_OS agent/spec/skill 演化的规范重构模式库。8 个主模式 + 2 个补充 + 1 个最小化规则。planner、architect 类 subagent 和 ROUTER 在考虑结构性改动时使用。
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/refactoring-patterns.yml
introduced_in: v1.8.5
---

# 重构模式

> 8 个规范重构模式 + 2 个补充 + 1 个最小化规则。每个模式有 `use_when`（诊断条件）和 `output`（产出物）。planner 和 architect 类 agent 在规划结构性改动时**必须**先咨询此目录，再决定是否发明自定义方法。

## 主模式

### 1. SPLIT（拆分）
- **何时使用**: 一个 agent/EOU/spec 有多个主要成功标准，或将两个不同职责打包在一个单元。
- **产出**: 两个或更多更窄的单元，每个有单一成功标准。
- **life_OS 示例**: v1.7.3 carve-out 将 archiver Phase 2 拆分为独立的 `knowledge-extractor` subagent（知识提取）+ 剩余 archiver（4 阶段）。减少了导致 v1.7.2 placeholder 违规的过载。

### 2. MERGE（合并）
- **何时使用**: 两个单元总是一起跑，共享同一成功标准，无独立存在价值。
- **产出**: 一个合并单元，统一成功标准。
- **示例**: 如果 `narrator` + `narrator-validator` 总是一起调用且共享"产出带引用的摘要"标准，合并它们（v1.8.0 做的就是这个——删除 narrator-validator，把检查内联到 ROUTER）减少了协调开销。

### 3. SCOPE-REDUCTION（范围收紧）
- **何时使用**: 单元的 `authority_level`、`blast_radius` 或 `target_object` 比其实际功能所需更宽；或读/写超出声明目的的文件。
- **产出**: 收紧 authority_level、缩小 allowed_scope 或减小 target_object。
- **示例**: ROUTER 原本可以直接 mutate SOUL.md。范围收紧让 ROUTER 对 SOUL 变成 `suggest_only + write_inactive`——只有 ARCHIVER Phase 2 能写 SOUL candidate。

### 4. AUTHORITY-DOWNGRADE（权限降级）
- **何时使用**: `automation_mode` 是 `LLM_assisted` 或 `deterministic`，但该步骤承担应保留 `human_executed` 的责任重型判断；或 authority_level 超过功能所需。
- **产出**: 降低 automation_mode 或 authority_level；加显式 `require_human_when` 条件。
- **示例**: REVIEWER 在高风险领域（`references/risk-domains.md` 的 finance/health/legal）的否决虽然是 `LLM_assisted`，但需要明确人类确认，不可自动执行。

### 5. STEP-EXTRACTION（步骤抽取）
- **何时使用**: agent/EOU 内部某步骤可以做成确定性的（提升为 slash command）或隔离为有自己 blast radius 和治理的子 agent。
- **产出**: 一个新的 slash command（`.claude/commands/*.md`）或子 subagent（`pro/agents/*.md`）处理被抽取步骤；父级引用被抽取单元。
- **示例**: archiver Phase 4 Notion sync 被抽取到 `/notion-sync` slash command（v1.8.5）。Phase 4 现在调用 slash，不再自己实现 audit-trail 写入。

### 6. VALIDATOR-ADDITION（验证器添加）
- **何时使用**: 已知失败模式无验证门；输出质量依赖未验证假设；过去事件无回归用例防止复发。
- **产出**: 新的确定性检查（slash command）、schema 约束（在 `references/*-spec.md` v2 frontmatter）或回归用例（`evals/regression-fixtures/rc-*.yml`）。
- **示例**: v1.8.0 R-1.8.0-019（GitHub Release Latest 错配事件）后，加 `/verify-release` 6 项 check 序列 + pro/CLAUDE.md HARD RULE。

### 7. STOP-CONDITION-INJECTION（停止条件注入）
- **何时使用**: agent/EOU 在无效、含糊或未授权状态下继续执行，而不是停下报告。
- **产出**: `execution.stop_conditions` 中一个或多个新停止条件，含可观察触发标准。
- **示例**: archiver 即使 `meta/config.md` 0 个 Notion entity 也跑 Phase 4 Notion sync。加停止条件：0 entity → 静默跳过 Phase 4，审计 trail 记录跳过原因（按 pro/CLAUDE.md Step 10a R-1.8.0-022 修复）。

### 8. RESPONSIBILITY-SEPARATION（责任分离）
- **何时使用**: 同一方既执行又审批，或两个不同审批权力被一个单元处理。
- **产出**: 分离 executor/approver 角色；每个审批权力有独立 subagent 或人类门。
- **示例**: AUDITOR（Mode 3）审计其他 agent 但不能审计自己。ADVISOR 审视 REVIEWER 决策但绝不重新决策。每个角色都有不能 self-approve 的硬边界。

## 补充模式

### 9. ADD_CONTEXT_MANIFEST（添加 context 清单）
- **何时使用**: agent 性能依赖于隐式或跨 run 不一致加载的 context（project state、SOUL、schema 版本）。
- **产出**: 在 agent v2 frontmatter（Stage 6）中显式列出 `context_manifest.source_of_truth + supporting + forbidden`。
- **示例**: hippocampus subagent 原本"按需"从 `meta/sessions/` 加载。v2 frontmatter 强制显式列：source_of_truth=[INDEX.md]，supporting=[最近 7 快照]，forbidden=[完整 transcript]。

### 10. RETIRE_UNIT（单元退役）
- **何时使用**: 单元已过时（被更好的替代）、重复（被现有覆盖）或净负面（成本超过运营价值）。
- **产出**: lifecycle 转到 `deprecated` → `retired`；spec frontmatter 标 `status: legacy`；为所有消费者记录迁移路径。
- **示例**: v1.8.0 退役 `narrator-validator.md` subagent（引用规则现在内联到 ROUTER）。v1.8.5 退役整个 hook 层（11 hook → 0）。

## 最小化规则（新建 agent/spec/skill 的 HARD RULE）

在创建新 agent、spec、skill 或 HARD RULE 前，必须回答以下 6 个问题：

1. 一条**规则**（在 pro/AGENTS.md 或 pro/CLAUDE.md 中）能否完成？
2. 一个**schema 字段**（在 references/*-spec.md frontmatter 中）能否完成？
3. 一个**验证器**（slash command 或 AUDITOR Mode 3 scenario）能否完成？
4. 一个**回归用例**（evals/regression-fixtures/*.yml）能否完成？
5. 一个**停止条件**（在现有 agent 执行流程中）能否完成？
6. 一个**人类 checklist**（加到相关文档中）能否完成？

如果**任一**答案为是，优先选低成本选项，不要创建新单元。创建新 agent/spec/skill 是最贵选项——只在 1-6 全部答"否，这需要新一等公民单元"时才使用。

## 何时调用此目录

- **planner subagent**: Phase 1 检查——提议结构性改动前必须按名字引用至少一个模式（或显式解释为何不适用）。
- **架构级决策**: 任何触及 agent 定义、spec schema 或 HARD RULES 的改动。
- **DREAM REM 周期**: 检测到反复摩擦（3+ 相似事件）时，按模式 1-10 匹配并提议重构。
- **ECP/RFC 起草**: 在 `proposed_change` 段引用相关模式。

## 来源出处

eou-foundry @ e4b12ce — `engine/refactoring-patterns.yml` 53 行（8 模式 + 2 补充 + minimality_rule）。已适配：示例替换为 life_OS 特定 case；"EOU" 术语映射到"agent/EOU/spec/skill"因 life_OS 有多种一等公民单元类型。
