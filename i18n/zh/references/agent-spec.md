---
spec_id: agent-spec.v2
description: 所有 agents/*.md subagent 定义文件的标准 frontmatter schema。从 eou-foundry 借鉴 6 facets classification + operating_hypothesis + context_manifest + blast_radius + failure_modes。适用所有 agents/*.md subagent 定义文件（router、retrospective、archiver、planner、reviewer、dispatcher、advisor、auditor、strategist、monitor、council、hippocampus、gwt-arbitrator、concept-lookup、soul-check、narrator、knowledge-extractor、memory-keeper + 6 个 domain agent）。
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, schemas/eou.schema.yml + engine/eou-contract.md
introduced_in: v1.8.5
---

# Agent 规范 v2

每个 `agents/*.md` subagent 定义文件**必须**有符合 v2 标准的 YAML frontmatter。v1.8.5 Stage 6 迁移全部现有 agent。

> **为什么 v2**: v1 agent frontmatter 只有 `name + description + tools + model`（4 字段）。v2 加 6 个结构性字段（借鉴 eou-foundry），让 agent 边界 grep-able、blast radius 显式、failure modes 有文档。按 RFC `meta/rfc/v1.8.5-cleanup-and-hardening.md` Stage 6。

## v2 标准 Frontmatter

```yaml
---
# v1 字段（保留 — Claude Code Task() 工具读取这些）
name: <agent-id>                       # 小写，连字符分隔，如 retrospective
description: "<一段角色描述>"
tools: Read, Grep, Glob, Bash, Write, Edit, Task   # 工具允许列表
model: opus|sonnet|haiku            # 档位别名，见 references/model-dispatch-policy.md（judgment|execution|batch）；禁止版本化模型 ID

# v2 新增: 身份 & 版本
id: agent-<name>                       # canonical，如 agent-retrospective
version: "1.0.0"                       # semver；实质角色变更 bump

# v2 新增: 6 facets classification（借鉴自 eou-foundry eou.schema.yml）
classification:
  function: generate|specify|validate|diagnose|promote|refactor|audit|propose|activate|implement|retire
  target_object: "<此 agent 作用于什么，如 'user decision workflow' 或 'session archive'>"
  automation_mode: deterministic|LLM_assisted|human_executed|hybrid
  authority_level: suggest_only|draft_only|write_candidate|write_inactive|mutate_active|approve|publish
  risk_level: low|medium|high|critical
  lifecycle_stage: candidate|draft|simulated|pilot|active|monitored|stable|deprecated|retired

# v2 新增: operating_hypothesis（Given/can/within）
operating_hypothesis: |
  Given <触发条件>, this agent should produce <输出类型> within <risk r>.

# v2 新增: context_manifest（eou eou-contract.md §context_manifest）
context_manifest:
  source_of_truth:     # 此 agent 作为权威读的文件
    - hosts/CLAUDE.md
    - hosts/GLOBAL.md
  supporting:          # 次要 context
    - references/relevant-spec.md
  forbidden:           # 不能读 — 按 hosts/CLAUDE.md §Information Isolation 信息隔离
    - agents/other-peer.md

# v2 新增: blast_radius（eou eou-contract.md §blast_radius）
blast_radius:
  allowed_scope:       # 此 agent 可写的文件/路径
    - meta/runtime/<sid>/<name>-*.md
    - <wiki/SOUL/specific-output-path>
  forbidden_scope:     # 此 agent 不可修改的文件
    - SOUL.md          # 仅 ARCHIVER Phase 2 写 SOUL candidate
    - foundry/eous/    # 如适用
    - agents/      # agent 定义不可自修改

# v2 新增: failure_modes（eou eou-contract.md §failure_modes）
failure_modes:
  known:              # 此 agent 已记录的失败方式
    - "用户消息简短时跳过必需步骤"
    - "上下文模糊时编造路径引用"
  warning_signs:      # 失败正发生的可观察信号
    - "输出含 'as discussed before' 但无具体引用"
    - "输出步骤数 < 预期步骤数"
  repair_actions:     # 失败时怎么做
    - "重新启动 agent 并显式列出步骤提醒"
    - "跑 AUDITOR Mode 3 记录违规"
---
```

## 必需 v2 字段（HARD）

每个 `agents/*.md` frontmatter **必须**有:

1. **所有 v1 字段**: `name`, `description`, `tools`, `model`
2. **身份**: `id`, `version`
3. **classification**: 6 facets 全部填；`target_object` 非空字符串
4. **operating_hypothesis**: 非空，≥30 字符，Given/can/within 形式
5. **context_manifest**: 3 keys 存在；`source_of_truth` 非空
6. **blast_radius**: `allowed_scope` 和 `forbidden_scope` 都非空
7. **failure_modes**: 3 keys 存在；list 可初始为空但应通过 DREAM / AUDITOR 观察累积

## 验证（AUDITOR Mode 6 —— Stage 6 添加）

Stage 6 Day 17 添加新 AUDITOR mode。检查:
- **A1**: 每个 agent 有所有 v2 必需字段
- **A2**: `tools` 列表与 agent 实际使用匹配（tools 无 `Read` 但 agent 做 Read 调用 = drift）
- **A3**: `forbidden_scope` 未被绕过（agent `meta/runtime/<sid>/` 输出 trail 显示无写到 forbidden 路径）
- **A4**: agent 的 `failure_modes.known` 包含 `compliance/violations.md` 中涉及此 agent 的任何违规类

发现按 `references/failure-taxonomy.md` 分类。

## A/B Test Day 15（按 RFC Stage 6 Day 15）

按 D4，批量更新其余 agent 前，在 3 个关键 agent 上测试:
- `retrospective.md`（最重的 agent，18 步）
- `archiver.md`（4 phases，breaking changes 易发）
- `reviewer.md`（否决权，judgment 重）

跑 eval scenarios:
- `evals/scenarios/start-session-compliance.md`（retrospective Mode 0）
- `evals/scenarios/adjourn-compliance.md`（archiver 4 phases）
- `evals/scenarios/reviewer-veto.md`（reviewer judgment 质量）

通过率标准（D4）:
- ≥ 95% baseline: 在其余 agent 上批量更新
- 90-95%: 精简 frontmatter（去掉最重字段，重试）
- < 90%: 回滚该 agent 的 v2 frontmatter，在 `meta/rfc/v1.8.5-stage6-rollback.md` 文档化原因

## 每个 agent 的 authority_level 指南

| Agent | function | authority_level | risk_level |
|---|---|---|---|
| router | propose | suggest_only + write_inactive | medium |
| retrospective | specify | suggest_only + write_inactive | low |
| archiver | publish | publish（最高 — 做 git push）| medium |
| planner | specify | write_candidate | low |
| reviewer | validate | approve（否决权）| high（judgment）|
| dispatcher | implement | mutate_active（dispatch 到 domain）| medium |
| advisor | diagnose | suggest_only | low |
| auditor | audit | suggest_only + write_inactive（写 violations.md）| low |
| strategist | propose | suggest_only | low |
| monitor | audit | suggest_only（只读 ops console）| low |
| council | diagnose | suggest_only | low |
| hippocampus | propose | suggest_only（只读检索）| low |
| gwt-arbitrator | propose | suggest_only | low |
| concept-lookup | propose | suggest_only | low |
| soul-check | audit | suggest_only | low |
| narrator | specify | suggest_only（ROUTER-internal，仅模板）| low |
| knowledge-extractor | propose | write_candidate（写 `meta/runtime/<sid>/extraction/`）| medium |
| memory-keeper | refactor | write_inactive（追加到 `gotchas.md`）| low |
| 6 domain agents（people/finance/growth/execution/governance/infra）| diagnose | write_candidate（写 domain report）| medium |

risk_level 理由: 产出最终输出无 REVIEWER 门的 agent 风险更高（archiver publish、reviewer veto）。仅提议/读取的 agent 风险更低。

## 每个 agent 的 `lifecycle_stage`（v1.8.5 初始）

所有 agent 在 v1.8.5 release 默认为 `active`。例外:
- `narrator.md` 按 v1.8.0 R-1.8.0-011 pivot 是 `deprecated`（citation discipline 已内联到 ROUTER）；仅作为 ROUTER-internal 模板保留（`narrator-validator.md` 在同一 pivot 已删除——文件不存在）

## 迁移

每个 agent 手动迁移。无 slash command —— agent 定义足够稳定，用户/maintainer 单 agent 交互式编辑即可。

每个 agent 模板:
1. 读当前 agent 文件
2. 用 v2 标准替换 frontmatter（保留 v1 字段，加 v2 字段）
3. 按 agent 实际行为填 `classification`、`operating_hypothesis`、`context_manifest`、`blast_radius`、`failure_modes`
4. 跑 AUDITOR Mode 6 验证

## 默认反模式（v1.8.7 Karpathy 借鉴 within-release · Karpathy 准则 3 "Surgical Changes"）

> **Tradeoff:** 本章节让 agent 偏向保守编辑而非热心清理。明确做清理工作的 agent（如 wiki-decay / archiver Phase 5 memory-keeper / 假想的 refactor-cleaner），通过显式 `allowed_scope` 声明覆盖这些默认。
> **The test:** *如果我打算删除用户未让我碰的代码/注释/文件，删除是否在我的 agent `blast_radius.allowed_scope` 内？不确定就 mention 但不删。*

以下行为默认适用 **所有 lifeos subagent**，除非 agent 角色 spec 显式覆盖。借鉴自 `multica-ai/andrej-karpathy-skills`（MIT）准则 3 "Surgical Changes" + lifeos 适配到 v2 frontmatter `blast_radius` 系统。

### DA-1 · 注意但不删除无关 dead code

任何 subagent 正常工作中遇到 dead code / 陈旧注释 / 孤立 import / 未使用函数 / 过时 config 在 **其 `blast_radius.allowed_scope` 之外**：

1. **DO** 在 agent 输出中 mention（"注意到 `<path>:<line>` 自 `<context>` 似乎未使用 —— 标记供用户 review"）
2. **DO NOT** 删除或重构所注意的内容
3. **DO** 继续用户的实际请求，不要 scope creep

**例外**（需在 agent 角色 spec 中显式覆盖）：
- `wiki-decay` prompt：cleanup 是其工作；声明更宽 scope
- `archiver` Phase 5 memory-keeper：仅 gotchas-spec 写入
- 未来 `refactor-cleaner` agent 若引入：声明 deletion-allowed scope

**为何此规则**：Karpathy 观察到 "models change/remove comments and code they don't sufficiently understand as side effects, even if orthogonal to the task." lifeos `blast_radius` 系统防 agent 越界写，但**不防**agent "热心" 删除其 scope 旁边的东西。DA-1 补这个空白。

**强制**：AUDITOR Mode 6 扩展（M6-A3' 增补）：交叉检查 agent 的 audit trail 对其声明 `allowed_scope` 之外文件的 delete/remove 操作 → 发 `F10 RESPONSIBILITY_FAILURE: agent deleted unrelated content outside blast_radius (DA-1 violated)`。

### DA-2 · 匹配既有风格即使你会另写

编辑既有代码/spec/文档时：

1. **DO** 镜像文件既有缩进、命名、注释风格、frontmatter 约定
2. **DO NOT** 跨文件应用 "一致性" 重格式化
3. **DO** 把你的编辑隔离到变更下的章节

**The test:** *我编辑的 diff 是否包含逻辑上不需要变的行？*

**强制**：AUDITOR Mode 6 扩展：agent transcript 含变更 scope 外大量无关 re-indentation / re-naming / re-formatting → 发 `F12 DRIFT_FAILURE: agent reformatted unrelated content (DA-2 violated)`。

### DA-3 · 提议变更时显式 surface tradeoffs

任何 subagent 提议有显著权衡（谨慎 vs 速度 / 简单 vs 灵活 / 安全 vs 自治 / 等）的行动方案时：

1. **DO** 在 agent 输出中显式声明 tradeoff
2. **DO NOT** 静默挑一边
3. **DO** 邀请用户 override 若默认选择的一边在其上下文中不对

**为何此规则**：Karpathy 观察 LLM "don't present tradeoffs, don't push back when they should." spec 写作中的 `Tradeoff:` 行（按 SKILL.md "Spec writing conventions"）覆盖 spec 级；DA-3 把它扩展到 agent runtime 输出。

**强制**：这是软契约；AUDITOR Mode 1（Decision Review）flag 推荐有显著 tradeoff 行动但不 surface 的 decision 输出。

### 覆盖机制

合法违反 DA-1/DA-2/DA-3 的 agent 必须在其 `agents/<name>.md` frontmatter 声明覆盖：

```yaml
default_anti_patterns_override:
  - DA-1: "wiki-decay 的工作就是删除不达标的陈旧 wiki 条目；cleanup 在 scope 内按 wiki-spec §Decay"
  - DA-2: N/A
  - DA-3: N/A
```

无理由的覆盖 = `F4 SCOPE_FAILURE: agent 声明 override 无角色 spec 依据`。

---

## 来源出处

eou-foundry @ e4b12ce。借鉴:
- 6 facets classification: `schemas/eou.schema.yml` 22-76 行
- operating_hypothesis: `engine/eou-contract.md` 34 行
- context_manifest 三层: `engine/eou-contract.md` 39-42 行
- blast_radius: `engine/eou-contract.md` 75-77 行（allowed_scope/forbidden_scope）
- failure_modes 三件套: `engine/eou-contract.md` 60-63 行

为 life_OS 适配: agent 是 Claude Code Task()-spawnable subagent（非 EOU）；`tools` 字段从 v1 保留（Claude Code 用于 tool gating）；A/B test 过程从 `references/lifecycle-gates.md` pilot→active 门。
