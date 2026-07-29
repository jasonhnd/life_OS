---
spec_id: soul.v2
description: SOUL.md schema v2。借鉴 eou-foundry domain_values + values-over-rules 的宪法层设计——X-over-Y formulation、优先级总序 {1..N} 无并列无间隙、3-8 维度数量上限、6 问 inclusion test gate、必填 outlier role slot。取代 v1 confidence-band-only schema。v1 entry 与 v2 共存 12 个月（按 D3 RFC）。
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, dev-docs/06-values-over-rules.md + schemas/captured-workflow.schema.yml
introduced_in: v1.8.5
supersedes: soul.v1 (v1.8.4 及更早；v1 entry 2027-05-23 自动标 deprecated 按 D3)
---

# SOUL 规范 v2

SOUL.md 是用户人格档案——一份活的宪法价值层，记录用户是谁、重视什么，以及规则冲突时价值如何决断。它存放在第二大脑根目录中。

> **v1.8.5 SOUL v2 pivot——借鉴自 eou-foundry**: SOUL 不再是 confidence band 的自由 dim 列表。它现在是有优先级总序、X-over-Y formulation、outlier role slot 的结构化价值栈。按 RFC `meta/rfc/v1.8.5-cleanup-and-hardening.md` Stage 4。

## 为什么 v2

v1 SOUL 有 3 个问题，eou-foundry 帮助暴露：

1. **无冲突解析器**: 当两个 SOUL 维度指向相反方向（如"职业成长" vs "家庭时间"），schema 里没有谁赢。解析是隐式的。
2. **无反 confirmation-bias**: SOUL 朝着"我已经同意的事"增长，因为无字段强制"违背我偏好但现实成功"的案例。
3. **无宪法门**: 任何都可成 SOUL dim ——"我喜欢冷咖啡"与"认知完整性不可妥协"同等地位。无过滤。

v2 通过从 eou-foundry 借的 5 个 schema 修复：
- **优先级 {1..N}** 总序——严格排名，无并列无间隙。高优先级在冲突中胜。
- **X-over-Y formulation** ——每个 dim 是真实 trade-off，不是含糊偏好。Y 不能是 strawman。
- **Inclusion test** —— dim 进入 SOUL 前 6 问 gate。
- **Outlier role slot** ——必含用户不喜欢但承认成功的参考案例。
- **3-8 维度数量上限** ——宪法不能膨胀成 wishlist。

## 原则（v1 保留）

1. **从零生长** — SOUL.md 初始为空，无需初始化。
2. **基于证据** —— 每条条目链接支持它的决策/行为。
3. **严格标准下自动写入** —— ADVISOR 每次决策后自动更新。新维度积累 ≥2 evidence 时以低 confidence (0.3) 自动写入，须过 v2 inclusion test 才能晋升。
4. **矛盾有价值** —— 不消解；呈现出来。

## Entry 格式 v2

每个 SOUL 维度是一个 YAML 块：

```yaml
- id: dv-{slug}                          # canonical，如 dv-truth-over-comfort
  formulation: "X over Y"                # HARD: 必须 "X over Y" 形式，Y 不能 strawman
  priority: 1                            # int，总序 1..N，无并列无间隙
  canonical_or_personal: canonical|personal
  lifecycle_stage: tentative|confirmed|dormant|deprecated  # v1 entry 默认 confirmed 但标记待迁移
  source: dream|advisor|strategist|user
  created: YYYY-MM-DD
  last_validated: YYYY-MM-DD

  # v2 新增: Inclusion test (6 问，至少 ≥1 实质回答)
  inclusion_test:
    failure_prevented: "<此 value 防止什么失败?>"
    rule_conflict_resolved: "<此 value 解决什么规则冲突?>"
    hidden_judgment_exposed: "<此 value 暴露什么隐含判断?>"
    false_success_resisted: "<此 value 抵抗什么虚假成功?>"
    architectural_invariant: "<此 value 保护 life_OS 哪个不变量?>"
    danger_if_removed: "<移除此 value 系统会变危险吗?>"

  # v2 新增: Failure modes
  failure_modes:
    known: []          # 此 value 被误用的方式
    warning_signs: []  # 此 value 漂移的可观察信号
    repair_actions: [] # 此 value 失火时怎么修

  # v1 字段 (向后兼容保留)
  confidence: 0.0
  evidence_count: 0
  challenges: 0

  # v1 prose 字段 (保留)
  what_is: "<观察到的行为模式>"
  what_should_be: "<用户陈述的期望>"
  gap: "<实然与应然的差距>"
  evidence: []
  challenges_log: []
```

## 必需 Schema 约束 (v2 HARD)

### 1. 维度数量: 总共 3-8

- 最少 3 ——少于 3 意味着 SOUL 还不是价值层
- 最多 8 ——超过 8 意味着 SOUL 膨胀成 wishlist
- 含 tentative + confirmed（不含 dormant/deprecated）
- **由 AUDITOR Mode 4 强制**（Stage 4 Day 9）

### 2. 优先级: 总序 {1..N}，无并列无间隙

- 每个 dim 有整数 priority 字段
- 优先级必须 1, 2, 3, ..., N（连续无跳）
- 两个 dim 不可共享优先级
- 冲突解析: 高优先级（小数字）胜
- **由 AUDITOR Mode 4 强制**

### 3. Formulation: "X over Y" 形式

- "Truth over comfort" ✅
- "Honesty over fluency" ✅
- "诚实是好的" ❌ (无 Y，无 trade-off)
- "Speed over slowness" ❌ (Y 是 strawman，无人偏好 slowness)
- Y 必须是用户真的可能选的另一面
- **由 AUDITOR Mode 4 + `/migrate-soul-v2` 强制**（拒绝坏 formulation）

### 4. Inclusion test: ≥1 实质回答

- 6 问，至少 1 个非平凡回答
- "Speed"、"elegance"、"output volume"、"fewer warnings" **不通过** ——这些是局部优化，不是宪法价值
- **由 AUDITOR Mode 4 + `/migrate-soul-v2` 强制**

### 5. SOUL.md 顶部必填 reference_set role slots

```yaml
soul_reference_set:
  aspirational: []         # 用户向往的人/作品
  anti_reference: []       # 用户明确不想变成的人/作品
  boundary_case: []        # 测试价值系统的边缘案例
  mainstream_baseline: []  # 用户所在 context 的"正常"（作对比）
  outlier: []              # 必填: "我不喜欢但它成功了" —— 反 confirmation-bias
```

- 5 个 slot 全部必需（初始可空 list 但结构必须存在）
- `outlier` slot **应当**30 天内非空 —— DREAM N3 会标记空
- **由 AUDITOR Mode 4 + archiver Phase 2 wiki-candidate gate 强制**（Stage 5）

## 生命周期 (v2)

```
1. 🌱 tentative —— 低 confidence (0.3) 自动创建，待过 inclusion test
2. ✅ confirmed —— 过 inclusion test + ≥2 evidence + 用户确认
3. 💤 dormant —— 90 天无 evidence 累积（不删，仅 inactive）
4. 🗄️ deprecated —— 被另一 dim 取代或用户显式删除
```

晋升门按 `references/lifecycle-gates.md`:
- tentative → confirmed: 过 inclusion_test 6Q + evidence_count ≥ 2 + challenges == 0 + 用户确认
- confirmed → dormant: evidence_count 90 天无 delta（DREAM N3 自动检测）
- any → deprecated: 用户显式删除或冲突解析中矛盾 dim 决出胜者

## Confidence 计算 (v1 保留)

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| Confidence | 状况 | 系统行为 |
|------------|-----|---------|
| < 0.3 | tentative，少数据点 | 仅 ADVISOR 引用 |
| 0.3 – 0.6 | 中等证据 | ADVISOR + REVIEWER 引用 |
| 0.6 – 0.8 | 强证据 | + PLANNER 引用 |
| > 0.8 | 深度验证，低矛盾 | 全系统引用（含 ROUTER）|

**注意**: 优先级字段独立于 confidence。priority-1 dim 在 confidence 0.4 仍胜 priority-3 dim 在 confidence 0.95 —— confidence 影响**谁读** dim，priority 影响**冲突中哪个胜**。

## 各角色如何使用 SOUL v2

| 角色 | 读 | 用 |
|------|-----|-----|
| **ROUTER** | priority 1-3 dim + red lines + reference_set | 更精准的意图厘清；风险领域 triage（按 `references/risk-domains.md`）|
| **PLANNER** | confidence ≥ 0.6 dim + priority 序 | 自动加相关 dim 到规划；规划必须声明运营哪些 top-3 priority dim |
| **REVIEWER** | 所有 confirmed dim + priority + inclusion_test | 价值一致性检查；verdict 引用 priority；必须在 R12 trail 填 `value_invocations[]` 按 Stage 7（避免 F14）|
| **ADVISOR** | 所有 entry + evidence/challenge 计数 | 行为审计；强化或挑战；提议 priority 调换 |
| **STRATEGIST** | 未解矛盾 + worldview | 推荐处理特定张力的思想家 |
| **ARCHIVER (DREAM)** | 所有 entry | DREAM N3 发现 candidate、更新计数、提议 lifecycle 转换、标记 outlier 30+ 天空 |

## 自动写入机制 v2

ADVISOR 提议新维度时:

1. **Pre-flight**: 检查当前 dim 数量。如已达 8 → 建议先弃用一个低优先级 dim 再加。
2. **Auto-formulation**: ADVISOR 提议 `X over Y` 形式。如只有 X 清楚（无真实 Y）→ 标"偏好不是价值"并跳过。
3. **Inclusion test**: ADVISOR 起草 6 问回答。必须 ≥1 产出实质回答。
4. **Priority slot**: 新 dim 默认 priority N+1（底）。用户可在下一 session 重排。
5. **写入 tentative**: confidence 0.3, lifecycle_stage tentative。
6. **晋升**: ≥2 evidence + 用户确认 → 翻 confirmed。

## Legacy v1 entry (12 个月共存按 D3)

v1.8.5 ship `references/soul-spec.md` v2 为权威。现有 v1 SOUL entry:

- 所有角色可读（legacy 模式）
- DREAM N3 报告中自动标记: "🔄 v1 entry: 'risk attitude' —— 考虑通过 /migrate-soul-v2 迁移到 v2"
- 默认 `priority` 字段按创建顺序分配（最老 = priority 1）用于 legacy 读
- 默认 `lifecycle_stage` = confirmed（因过了 v1 confidence 阈值）
- 默认 `formulation` 字段 = 空（**不过** v2 inclusion test —— 标记但容忍）
- **2027-05-23** 后剩余 v1 entry 自动标 `lifecycle_stage: deprecated`

用户可在方便时通过 `/migrate-soul-v2` slash command 迁移。无强制迁移。

## 通过 `/migrate-soul-v2` 迁移

详见 `.claude/commands/migrate-soul-v2.md`。Slash command:
1. 读现有 SOUL.md
2. 对每个 v1 dim，问用户: formulate 为 "X over Y"；分配 priority；答 1+ inclusion test 问题
3. 在 v1 prose 旁写 v2 YAML 块（保留）
4. 通过 AUDITOR Mode 4 验证后再 commit

## 使用场景

- **REVIEWER 否决**: 检测到 contested case 时必须引用 `value_invocations[]` 含 SOUL 的 `domain_value_id`。Contested case 上 value_invocations 空 = F14 silent judgment 按 `references/failure-taxonomy.md`。
- **PLANNER trade-off**: 两个 domain 报告冲突时，PLANNER 读 SOUL 优先级序，提议引用获胜 dim 的 `id` + `priority` 的解析。
- **archiver Phase 2 candidate gate**: 触及价值的新 wiki entry 必须运营 ≥1 个 top-3 SOUL dim（Stage 5 wiki schema 要求）。
- **AUDITOR Mode 4 (v1.8.5 新)**: 审计 SOUL.md schema 合规 —— 数量 3-8、优先级总序无间隙、formulation X-over-Y、inclusion_test ≥1 答、reference_set 5 slot 存在。

## 来源出处

eou-foundry @ e4b12ce。借鉴:
- 3-8 上限 + 优先级总序: `schemas/captured-workflow.schema.yml` domain_values_minimum_count / maximum_count / priority 约束
- X-over-Y formulation: `schemas/captured-workflow.schema.yml` `formulation_rule`
- Inclusion test 6Q: `dev-docs/06-values-over-rules.md` "Inclusion test" 段
- Outlier role slot: `schemas/captured-workflow.schema.yml` `reference_set_required_role_slots`（outlier 描述: "I dislike this but it succeeds"）
- Failure modes 三件套: `engine/eou-contract.md` failure_modes.known/warning_signs/repair_actions

为 life_OS 适配: SOUL 是 person-scope（非 captured_workflow 那种 app-scope）；lifecycle_stage 简化为 4 状态（vs eou 9）；confidence band 系统与 priority 并存。
