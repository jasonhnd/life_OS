---
spec_id: wiki.v2
description: Wiki entry schema v2。从 eou-foundry 借鉴 6 facets classification + operating_hypothesis + context_manifest 三层 + reference_set 5 role slots（含 outlier）+ failure_modes + arguments_against。取代 v1 free-form prose schema。v1 entry 与 v2 共存 12 个月（按 D3）。
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, schemas/eou.schema.yml + captured-workflow.schema.yml + engine/eou-contract.md
introduced_in: v1.8.5
supersedes: wiki.v1 (v1.8.4 及更早；v1 entry 2027-05-23 自动标 deprecated 按 D3)
---

# Wiki 规范 v2

Wiki 是系统的知识档案——关于世界的可复用结论的活集合。位于 second-brain 的 `wiki/` 目录下。

> **v1.8.5 wiki v2 pivot —— 借鉴自 eou-foundry**: Wiki entry 不再是 free-form prose 加 confidence/evidence metadata。v2 entry 有结构化 frontmatter（6 facets classification + operating_hypothesis + context_manifest + reference_set + failure_modes + arguments_against）。按 RFC `meta/rfc/v1.8.5-cleanup-and-hardening.md` Stage 5。

> **v2.0 未来方向（v1.8.7 A1 spec 提案）**：`references/memory-tree-spec.md`（status: proposal）定义 wiki + sessions 的 L0 → L1 → L2 → L3 cascade seal 架构，借鉴自 `tinyhumansai/openhuman` Memory Tree。v1.8.7 不实施 —— 详见该 spec 的未来方向与理由。

## 定位（v1 保留）

| 存储 | 记录 | 示例 |
|------|------|------|
| `decisions/` | 你决定了什么（具体、有时间戳）| "2026-04-01: 决定用信托结构" |
| `user-patterns.md` | 你做什么（行为模式）| "倾向回避金融维度" |
| `SOUL.md` | 你是谁（价值观、人格）—— **v2 schema 见 `references/soul-spec.md`** | "Truth over comfort"（priority 1）|
| `wiki/` | 你知道什么 —— 陈述性知识 —— **v2 schema 本文档** | "日本 NPO 贷款无貸金業法豁免" |
| `meta/concepts/` | 突触图 —— 概念如何连接 | "company-a-holding" 节点带加权边 |
| `meta/methods/` | 程序性记忆 —— 可复用工作流 | "5 轮渐进质量文档优化" |

**非 wiki 材料**（去别处）：
- 身份 / 价值 / 个人偏好 → `SOUL.md` v2
- 行为模式 → `user-patterns.md`
- 程序性工作流 → `meta/methods/`
- 概念级关联 → `meta/concepts/`

## 原则（v1 保留）

1. **从零生长** — wiki/ 初始为空。
2. **基于证据** —— 每条 entry 链接支持的决策/经验。
3. **严格标准下自动写入** —— archiver 和 DREAM 在标准过时自动创建。用户通过删除调整。
4. **标题 = 结论** —— 每个 entry 的标题就是结论本身，不是话题。
5. **一个文件一个结论** —— 不要多主题合编。

## v2 Entry Frontmatter（HARD schema）

v1.8.5 起每个新 wiki entry **必须**有 YAML frontmatter，符合：

```yaml
---
# 身份
id: wn-{slug}                       # canonical，如 wn-japan-npo-lending-no-exemption
name: "<人类可读名称>"
version: "0.1.0"                    # semver；实质改动 bump

# v2 新增: 6 facets classification（借鉴自 eou-foundry eou.schema.yml）
classification:
  function: generate|specify|validate|diagnose|promote|refactor|audit|propose|activate|implement|retire
  target_object: "<此 entry 关于什么>"
  automation_mode: deterministic|LLM_assisted|human_executed|hybrid
  authority_level: suggest_only|draft_only|write_candidate|write_inactive|mutate_active|approve|publish
  risk_level: low|medium|high|critical
  lifecycle_stage: candidate|draft|simulated|pilot|active|monitored|stable|deprecated|retired

# v2 新增: operating_hypothesis（Given/can/within 格式）
operating_hypothesis: |
  Given <输入/触发>, under context <c>, this knowledge entry should
  produce <输出/效果> within risk <r>.

# v2 新增: context_manifest（eou eou-contract.md §context_manifest）
context_manifest:
  source_of_truth: []   # 此 entry 读/引用的权威工件
  supporting: []        # 次要 context
  forbidden: []         # 不能用作 context 的（显式排除）

# v2 新增: reference_set 5 role slots（eou captured-workflow.schema.yml）
reference_set:
  aspirational: []         # ref + why; entry 向往的作品/人
  anti_reference: []       # ref + why; 显式反例
  boundary_case: []        # ref + why; 边缘案例
  mainstream_baseline: []  # ref + why; 典型情况（对比）
  outlier: []              # active+ 必填: "我不喜欢但成功了"；反 confirmation-bias

# v2 新增: failure_modes（eou eou-contract.md §failure_modes）
failure_modes:
  known: []          # 此知识被误用的方式
  warning_signs: []  # 知识错或漂移的可观察信号
  repair_actions: [] # 知识失火时怎么修

# v2 新增: arguments_against（eou generating_eou_candidate_required）
arguments_against: |
  This entry might be wrong because <原因>. Counter-evidence to watch for:
  <可观察信号>.

# 现有 v1 metadata（保留）
confidence: 0.5
evidence_count: 3
challenges: 0
created: YYYY-MM-DD
last_validated: YYYY-MM-DD
source: archiver|dream|user
---

# <Entry 标题 = 结论>

<正文：1-3 段陈述性知识>

## Evidence

- [YYYY-MM-DD] [decision/case] — [link]

## Challenges（如有）

- [YYYY-MM-DD] [contradicting case] — [link]
```

## v2 HARD Schema 约束

### 1. Frontmatter 7 个必需字段组

- `id`（canonical wn-* slug）
- `classification`（6 facets 全填；`target_object` 非空字符串）
- `operating_hypothesis`（Given/can/within 形式；≥30 字符）
- `context_manifest`（块存在；active+ entry 的 `source_of_truth` 非空）
- `reference_set`（5 keys 存在；candidate/draft 可空 list）
- `failure_modes`（块存在；初始可空 lists）
- `arguments_against`（非空字符串；≥20 字符；非平凡）

**由 AUDITOR Mode 5 强制**（Stage 5 Day 13 添加）。

### 2. Reference_set `outlier` 在 active+ entry 必填

`lifecycle_stage: active | monitored | stable` 的 entry：
- `outlier` list **必须**含 ≥1 entry
- 每个 outlier: `ref`（工件/人/作品）+ `why`（为什么用户不喜欢 + 为什么它仍成功）

`candidate | draft | pilot`：
- `outlier` 可初始为空
- 晋升到 `active` 被阻挡如 outlier 仍空（按 `references/lifecycle-gates.md` 转换 4）

### 3. `arguments_against` 不能平凡

- ✅ "此 entry 可能错因为日本税法 2024 改了我们未验证 post-change。Counter-evidence: 任何 2024+ 判决引用 法 17。"
- ❌ "可能错" / "无 counter-evidence" / "<TBD>"

LLM 启发式检查: 必须提到具体失败模式 + 具体可观察反信号。

## 生命周期（v2 对齐 `references/lifecycle-gates.md`）

```
1. 🌱 candidate — archiver Phase 2 / DREAM N3 提议
2. 📝 draft — frontmatter 填好；body 编辑
3. 🧪 simulated — 实际决策中被 ≥1 次引用
4. ✈️ pilot — 2+ 独立决策引用；无矛盾
5. ✅ active — outlier slot 非空；reviewed
6. 📊 monitored — 经常引用，上轮无 challenge
7. 💎 stable — 长期验证，改动不太可能
8. 🗄️ deprecated — 被取代或矛盾；理由有文档
9. 📦 retired — 无消费者引用
```

## Archiver Phase 2 candidate gate（v2 强化）

archiver Phase 2 写 wiki candidate 前**必须**验证：

### 现有 6 criteria（v1 保留）
1. 跨项目可复用
2. 关于世界，不关于你
3. 零个人隐私
4. 事实性或方法论
5. ≥2 独立证据
6. 不与现有 wiki 矛盾（否则递增 challenges）

### v2 新增 4 个 gate

7. **可起草 operating hypothesis**: archiver 尝试 Given/can/within 形式 ≥30 字符。如太含糊 → 弃（是印象不是知识）。
8. **可识别 ≥1 outlier**: archiver 尝试 "我不喜欢但成功了" 示例。如不能 → 写 candidate 但标 outlier-warn。
9. **可写 arguments_against**: archiver 写出什么会证伪此 entry。如不能（"显然对无失败模式"）→ 弃或降级到 journal（epistemic-hygiene fail）。
10. **6 facets 可分类**: archiver 分配 6 facets。任一含糊 → 标待用户消歧。

## Legacy v1 entries（12 个月共存按 D3）

v1.8.5 前的 v1 wiki entries：
- 所有角色可读
- DREAM N3 自动标记: "🔄 v1 wiki entry: '<title>' —— 考虑 /migrate-wiki-v2"
- 默认 `lifecycle_stage` = `active`
- 默认 `arguments_against` = 空（**不过** v2 gate —— 标记但容忍）
- 默认 `outlier` = 空（标记但容忍）
- **2027-05-23** 后剩余 v1 entry 自动标 `lifecycle_stage: deprecated`

## 通过 `/migrate-wiki-v2` 迁移

详见 `.claude/commands/migrate-wiki-v2.md`。Slash command:
1. 读每个 v1 wiki entry
2. 问用户填: 6 facets, operating_hypothesis, outlier reference, arguments_against
3. 在 v1 body 上方写 v2 frontmatter（保留 body）
4. AUDITOR Mode 5 验证后再 commit

用户随时跑。无强制迁移。

## Confidence 计算（v1 保留）

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| Confidence | 状况 | 谁用 |
|------------|------|------|
| < 0.3 | candidate，少证据 | 仅 archiver / DREAM |
| 0.3 – 0.5 | draft 到 pilot | + REVIEWER 引用 |
| 0.5 – 0.7 | pilot 到 active | + PLANNER 引用 |
| > 0.7 | active+，低 challenge | 全系统引用（含 ROUTER）|

**注意**: v2 中 confidence 独立于 lifecycle_stage。高 confidence 的 candidate 仍是 candidate；晋升需 `references/lifecycle-gates.md` 门，不仅 confidence。

## 角色如何使用 wiki v2

| 角色 | 读 | 用 |
|------|-----|-----|
| **ROUTER** | INDEX.md + 相关 entry 标题 | 提到当前话题有已建知识时 |
| **PLANNER** | 匹配主题的 active+ entry + outlier slot | "已知前提"输入；outlier 作对抗性检查 |
| **REVIEWER** | Entry `operating_hypothesis` + `arguments_against` | 引用矛盾的 entry；矛盾时否决 |
| **ADVISOR** | Entry 使用模式 + challenges 数 | 标记 6 个月未引用的 entry（→ dormant 候选）|
| **STRATEGIST** | Entry body + reference_set | 用 boundary_case + outlier 作对话提示 |
| **ARCHIVER** | 所有 entry（INDEX 重建）| Phase 2 candidate gate（10 标准）；矛盾时更新 challenges |
| **AUDITOR Mode 5（新）** | 所有 entry frontmatter | Schema 审计（4 个 v2 hard check）|

## 来源出处

eou-foundry @ e4b12ce。借鉴:
- 6 facets classification: `schemas/eou.schema.yml` 22-76 行
- operating_hypothesis: `engine/eou-contract.md` 34 行
- context_manifest 三层: `engine/eou-contract.md` 39-42 行
- reference_set 5 role slots: `schemas/captured-workflow.schema.yml`
- failure_modes 三件套: `engine/eou-contract.md` 60-63 行
- arguments_against: `schemas/eou.schema.yml` 143 行

为 life_OS 适配: wiki entry 是知识工件（非 EOU）；v1 prose 与 v2 frontmatter 共存 12 个月。
