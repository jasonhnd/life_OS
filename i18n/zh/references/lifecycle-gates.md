---
spec_id: lifecycle-gates.v1
description: 任何 life_OS 一等公民对象（SOUL dim、wiki entry、agent、spec、skill、decision）的 8 个晋升转换。每个转换列出晋升所需的证据。ARCHIVER Phase 2 / DREAM N3 / ADVISOR 漂移检测使用。
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/governance.yml lines 16-66
introduced_in: v1.8.5
---

# 生命周期门

> `references/agent-spec.md v2` / `references/wiki-spec.md v2` / `references/soul-spec.md v2`（以及 EOU 6 facets 词汇）的 9 个生命周期阶段是：`candidate → draft → simulated → pilot → active → monitored → stable → deprecated → retired`。
>
> 阶段之间晋升需要证据。本文件列出 8 个转换 + 每个转换的证据 checklist。ARCHIVER Phase 2 晋升提议**必须**引用推荐晋升前已满足的证据项。

## 8 个转换

### 1. candidate → draft

所需证据：
- ✅ Frontmatter 存在，所有 required_top_level 字段已填（按相关 `*-spec.md` v2 schema）
- ✅ `purpose.statement` 是具体的（命名了所防止的失败或改进的决策，不只是流程描述）
- ✅ `operating_hypothesis` 以 Given/can/within 格式陈述
- ✅ 至少一个 `stop_condition` 已声明
- ✅ `blast_radius.allowed_scope` 和 `blast_radius.forbidden_scope` 已声明
- ✅ `responsibility.{executor, reviewer, approver}` 都已命名

life_OS 示例：
- SOUL dim 在 confidence 0.3 自动创建 → 晋升到 draft 前必须有真实 evidence count ≥ 2（`evidence_count >= 2 AND challenges == 0`）。
- archiver Phase 2 写的 wiki entry → 必须过 6 strict criteria + outlier reference slot 已填。

### 2. draft → simulated

所需证据：
- ✅ 所有必填 schema 字段已填（除声明的 `open_questions` 外无 TBD placeholder）
- ✅ `evals/regression-fixtures/` 中至少一个回归用例覆盖一个已知失败模式
- ✅ `validation.deterministic` 段非空（列出可机械跑的检查—— slash command、AUDITOR scenario 等）
- ✅ `/check-spec-drift` 对此 artifact 返回 CLEAN
- ✅ 人类 reviewer 已读并确认

### 3. simulated → pilot

所需证据：
- ✅ 仿真 run 已记录（`meta/runtime/<sid>/simulation-<artifact>.json`）
- ✅ 仿真无 critical findings（F1/F3/F6a/F10/F14/F15/F17）
- ✅ 人类 reviewer 在仿真结果上签字
- ✅ 所有 `open_questions` 已解决或显式延期带理由

### 4. pilot → active

所需证据：
- ✅ 至少 1 次成功真实调用，`meta/runtime/<sid>/` 中有 trace evidence
- ✅ 审计通过：AUDITOR Mode 3 对此 artifact 返回 PASS verdict
- ✅ 回归套件通过（`/run-regression` 干净）
- ✅ 命名的人类 owner 批准（`approval.approver` 是真实人物标识符，不是"user"这种角色标签）

### 5. active → monitored

所需证据：
- ✅ active 至少一个治理周期无事件
- ✅ 事件历史干净，或所有事件有诊断记录 + 修复记录（未改动时按 `no_change_record` spec）
- ✅ 回归套件通过，无新失败引入

### 6. monitored → stable

所需证据：
- ✅ 至少一个治理周期无结构性改动需求
- ✅ 完整回归套件通过
- ✅ 成熟度证据达 L5 或 L6（非正式—— life_OS 没有 eou 的 L0-L6 硬 validator）

### 7. any → deprecated

所需证据：
- ✅ 弃用原因有文档（`superseded` / `obsolete` / `net-negative`）
- ✅ 任何消费者的迁移路径有文档（如 legacy SOUL dim 迁移 → `/migrate-soul-v2`）
- ✅ 继任 artifact 已命名（如适用）
- ✅ 人类 owner 批准

### 8. deprecated → retired

所需证据：
- ✅ 所有已知消费者已迁移（`/check-spec-drift` 验证 → 零 broken-path 引用）
- ✅ 最终 trace 已归档（`meta/v1.8.4-snapshot/` 或等价位置）
- ✅ Frontmatter 已更新 `status: legacy` + 退役日期

## 特殊转换

### "any → deprecated" 适用于所有阶段

任何阶段的单元（即使 `candidate`）如果发现不需要可以被弃用。跳过中间阶段。

### Legacy 12 个月共存（按 D3）

v1.8.5 → v2.0 迁移窗口（2026-05 至 2027-05）期间，SOUL/wiki v1 entry：
- 旧 v1 entry 保留在 v1.8.5 前的生命周期阶段
- 新 entry 从创建起必须用 v2 schema
- 不强制迁移；用户可随时 `/migrate-soul-v2` 或 `/migrate-wiki-v2`
- 2027-05-23 后剩余 v1 entry 自动标 `lifecycle_stage: deprecated`

## 使用场景

- **ARCHIVER Phase 2**: 提议 wiki 晋升时，必须引用哪个转换 + 哪些证据项已满足。
- **DREAM N3 周期**: 检测晋升过期的 artifact（如 SOUL dim 处 `tentative` >90 天 → 提议确认或弃用）。
- **ADVISOR 漂移检测**: 标记倒退的 artifact（如 `active` artifact 近期有事件但无修复记录 → 建议降级到 `pilot`）。
- **AUDITOR Mode 3 lifecycle scenario**（Stage 7）：检查每个 artifact 的 lifecycle_stage 是否与可用证据匹配；不匹配 = F11 LIFECYCLE_FAILURE。

## 来源出处

eou-foundry @ e4b12ce — `engine/governance.yml` 16-66 行（`lifecycle_promotion_gates` 8 转换）。已适配：简化证据 checklist 以适合 life_OS LLM-native 验证（vs eou Python validator）；按 D3 加 v1.8.5 特定的"legacy 12 个月共存"规则。
