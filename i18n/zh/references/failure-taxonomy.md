---
spec_id: failure-taxonomy.v1
description: 借鉴自 eou-foundry 的架构层失败分类法 F1-F17。补充 life_OS 的流程违规分类法（A1/A2/A3/B/C/D/E/F 在 pro/compliance/violations.md）。v1.8.5 起每条 violations.md 条目必须同时带 A-F 标签和 F1-F17 标签。
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/failure-taxonomy.yml
introduced_in: v1.8.5
---

# 失败分类法 F1-F17

> AI agent 治理系统的架构级失败类别。每个类别有 definition + canonical repair。life_OS 从 eou-foundry 借鉴此分类法（Stage 3 Day 6 交付物，参考 `_meta/rfc/v1.8.5-cleanup-and-hardening.md`）。

## 与现有 life_OS 分类法的关系

| 分类法 | 层次 | 示例 | 记录位置 |
|---|---|---|---|
| **A1/A2/A3/B/C/D/E/F**（`references/compliance-spec.md`）| **流程违规**（人/流程层）| A1: 跳过 retrospective Subagent; B: 编造路径; C: 跳步骤; D: 自批; E: 漏 publish; F: 出站 PII 泄露 | `pro/compliance/violations.md` |
| **F1-F17**（本文档）| **架构失败**（系统设计层）| F11: 生命周期阶段错配; F12: spec 漂移; F14: 沉默判断 | 同 `violations.md`（Stage 8 加 F-code 列）|

**两个分类法可叠加用于同一事件**。示例："ROUTER 跳过 retrospective Subagent 并编造路径" = `A1`（流程）+ `F12_DRIFT_FAILURE`（架构）。

## F1-F17 参考

### F1 — INPUT FAILURE
- **定义**: 必需输入缺失、格式错误、过期或含糊。
- **修复**: 收紧输入 schema 或修复上游输入。
- **life_OS 示例**: ROUTER 收到空 `$ARGUMENTS` 但 slash command 要求 `--sid`。

### F2 — CONTEXT FAILURE
- **定义**: 加载了错误 context 或遗漏权威源。
- **修复**: 修 `context_manifest`。
- **示例**: REVIEWER 决策但未读 SOUL.md；archiver Phase 4 读取过期的 `_meta/config.md`。

### F3 — SCHEMA FAILURE
- **定义**: spec/输入/输出/validator schema 之间发散。
- **修复**: 规范化 schema 并更新 validator。
- **示例**: `references/soul-spec.md` v1 与 SOUL.md 实际字段漂移。

### F4 — SCOPE FAILURE
- **定义**: agent/EOU/skill 范围过宽、过窄或混合不兼容任务。
- **修复**: 拆分、合并或重定义。
- **示例**: v1.7.3 carve-out 之前 archiver 同时做 Phase 2 知识提取 + Phase 1 归档，造成 v1.7.2 placeholder 违规。

### F5 — INSTRUCTION FAILURE
- **定义**: 步骤不清晰、矛盾或不可执行。
- **修复**: 重写执行流程。
- **示例**: pro/agents/retrospective.md 18 步中 step 12 与 step 7 矛盾。

### F6 — JUDGMENT FAILURE（子类型）

#### F6a — STRUCTURAL_JUDGMENT
- **定义**: agent 混淆两个有不同成功标准或不同责任方的判断。架构错误。
- **修复**: 责任分离或拆分重构。
- **示例**: REVIEWER 在一次调用中同时做否决判断 + 审计判断。

#### F6b — COVERAGE
- **定义**: 判断框架正确但无验证标准。架构对但边界不可验证。
- **修复**: 加判断谓词、显式成功标准、回归用例。
- **示例**: AUDITOR Mode 3 有 scenario 列表但无预期输出 schema。

### F7 — VALIDATION FAILURE
- **定义**: Validator 通过无效输出或拒绝有效输出。
- **修复**: 改进验证逻辑；在边界加回归用例。
- **示例**: `/check-spec-drift` 漏掉 broken-path 引用；或对合法 legacy 文件假阳性。

### F8 — TOOL FAILURE
- **定义**: 脚本、模型、API 或外部工具硬失败。
- **修复**: 隔离依赖、加 fallback、加 stop condition。
- **示例**: Notion MCP 在 Phase 4 中途不可用；gh CLI 返回 502。

### F9 — TRACE FAILURE
- **定义**: 运行无法重建；trace 缺失或与声明步骤矛盾。
- **修复**: 改进 trace 捕获；每步写入 `_meta/runtime/<sid>/`。
- **示例**: archiver Phase 4 完成但未写 `notion-sync-*.json` 审计 trail。

### F10 — RESPONSIBILITY FAILURE
- **定义**: 无明确 owner、审批门或升级路径；或同一方既执行又审批。
- **修复**: 加责任映射；分离 executor/approver。
- **示例**: ROUTER 既提议又自动执行 wiki write（无 REVIEWER 否决检查）。

### F11 — LIFECYCLE FAILURE
- **定义**: agent/EOU/entry 被错误成熟度标准评判。
- **修复**: 显式声明 lifecycle_stage；应用对应验证级别。
- **示例**: SOUL dim 处于 `tentative` 但被 REVIEWER 当 `confirmed` 引用。**A1 COURT-START 类违规也映射到这里**（Start Session 触发跳过 retrospective Subagent = 错的生命周期门）。

### F12 — DRIFT FAILURE
- **定义**: spec/scripts/docs/validator 已发散；一层的改动未传播到其他层。
- **修复**: 识别权威层（`schemas/` 或 `references/`），协调依赖层，CI/audit 加词汇同步检查。
- **示例**: pro/agents/router.md 引用已删除的 `pro/agents/narrator-validator.md`。**B 编造路径违规映射到这里**。

### F13 — PERFORMANCE FAILURE
- **定义**: 执行正确但规模化时退化。
- **修复**: 分析、限制瓶颈、加预算/超时、tier-down automation_mode、拆分或升级到更快工具。
- **示例**: v1.8.1 Wave 2 删除 Bash skeleton 后 archiver Adjourn 耗时 25-30 min（按架构纯粹接受的 trade，但边缘 F13）。

### F14 — SILENT_JUDGMENT_FAILURE（v1.8.5 新增）
- **定义**: agent 做出 contested choice 但未调用 `SOUL.md` 任何 domain_value。选择可能是对的但不可追责——无 trace 记录什么推理解决了冲突。**按 V1（认知完整性）是最危险的 agentic-judgment 失败模式。**
- **修复**: 每个 contested case 必须有 `value_invocations[]` 条目（按 Stage 7 R12 trail 更新）。更新 agent 执行流程，显式暴露 contested case；要求调用或升级。
- **示例**: REVIEWER 否决"职业转换去新加坡"但未引用驱动决策的 SOUL 维度。

### F15 — VALUE_HIERARCHY_FAILURE（v1.8.5 新增）
- **定义**: agent 对同一 contested case 调用了低优先级 SOUL 维度而非高优先级。
- **修复**: 检查 value_invocations 条目中的 `rule_conflict`；要么修订 SOUL 优先级（通过显式编辑 + RFC）要么将调用视为错（加回归用例）。
- **示例**: REVIEWER 对高风险决策引用"舒适"（优先级 6）压过"认知完整性"（优先级 1）。

### F16 — VALUE_DRIFT_FAILURE（v1.8.5 新增）
- **定义**: agent 多次运行的调用模式已偏离 SOUL 声明的优先级顺序，但无任何 SOUL 修订。**系统在通过先例悄悄重写自己的宪法。**
- **修复**: 分诊漂移——要么重置 agent 调用行为（回归套件）要么将漂移正式化为 SOUL 修订。永不允许漂移无文档地持续。
- **示例**: 连续 3 次 REVIEWER 决策对相似 case 都偏向优先级-5 维度而非优先级-1，未标记此模式。

### F17 — VALUE_HALLUCINATION_FAILURE（v1.8.5 新增）
- **定义**: agent 调用了 SOUL.md 未声明的 value。调用引用的 `domain_value_id` 无法解析。
- **修复**: 调用时验证 `domain_value_id` 是否在 SOUL.md；拒绝未知 id 的调用。为特定虚构 id 模式加回归用例。调查是否 prompt/训练数据引入了虚构 value。
- **示例**: ARCHIVER 引用 `dv-tradition-over-novelty` 但 SOUL 只有 `dv-truth-over-comfort`。（直接 B confabulation，也映射 F17）

## 诊断结果（参考 eou-foundry governance.yml）

并非每个诊断失败都变成改动。按 Stage 7 `no_change_record` 协议显式记录决策：

- **change**: 已开 ECP（Edit-Change-Proposal）。详见 `_meta/incidents/{id}.change.md`。
- **no_change**: 决定接受当前行为。按 Stage 7 §1 schema 记录到 `_meta/incidents/{id}.no-change.yml`（7 必填字段：incident_id / eou_id / diagnosis_summary / decision:no_change / rationale / reviewed_by / reviewed_at / reopen_condition）。**缺记录看上去与未调查事件无异。**

## 使用场景

- v1.8.5 起每条 `pro/compliance/violations.md` 条目除 A/B/C/D/E/F 标签外还带 F1-F17 标签（Stage 8 Day 24）。
- AUDITOR Mode 3 按 F-code 分类发现（Stage 7 Day 19 F14 scenario）。
- DREAM REM 周期使用 agent/entry v2 frontmatter 的 failure_modes.known/warning_signs（Stage 6）检测早期警告模式。

## 来源出处

eou-foundry @ e4b12ce — `engine/failure-taxonomy.yml` 98 行。为 life_OS 适配：F14-F17 使用 SOUL.md domain_values 而非 captured_workflow.domain_values；加上映射到现有 A/B/C/D/E/F 流程分类法。
