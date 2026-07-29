---
spec_id: changelog.v1
description: CHANGELOG.md entry schema v1（v1.8.5+ 生效）。借鉴 eou-foundry ECP YAML frontmatter 模式 —— 每个 release entry 有结构化 YAML frontmatter（version、breaking_changes、alternatives_considered、ordering_dependency、regression_cases_added）+ markdown body 用于叙事 release notes。v1.8.5 前的 entry 保持叙事性（legacy）。
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, self-evolution/ecp/ YAML schema
introduced_in: v1.8.5
---

# CHANGELOG 规范 v1

CHANGELOG.md entry v1.8.5 起有结构化 YAML frontmatter + markdown body。v1.8.5 前的 entry 是叙事性的，保持不变（legacy）。

## 为什么结构化 frontmatter

v1.8.4 CHANGELOG entry 是叙事性的 —— 对人类有用但机器不可解析。eou-foundry 帮助暴露 3 个问题：

1. **无 alternatives_considered**: entry 记录做了什么，没记录考虑了什么并拒绝了什么。"为什么没做 X" 失去历史。
2. **无 ordering_dependency**: cohort releases（如 ECPs 0015-0017 必须一起 land）没有显式声明。cherry-pick 造成问题。
3. **无 regression_cases_added**: 从"修了这个"到"加了回归测试防复发"的链接是隐式的，常缺失。

v1.8.5+ schema 修复这些。

## v1.8.5+ Entry Schema

```markdown
---
version: 1.8.5
date: 2026-05-23
type: major | minor | patch | prerelease
breaking_changes:                          # 项目列表
  - "SOUL.md schema v1 → v2（X-over-Y formulation 必填）"
  - "wiki entry schema v1 → v2（active+ entry outlier slot 必填）"
  - "agent frontmatter v1 → v2（authority_level / blast_radius 必填）"
new_features:                              # 项目列表
  - "F1-F17 失败分类法（references/failure-taxonomy.md）"
  - "..."
fixes:                                     # 项目列表
  - "..."

# v1.8.5+ 必需: 至少 1 个被拒选项及原因
alternatives_considered:
  - option: "保持 v1.8，分 6 个月做 30 个 minor patch"
    rejected_because: "30 个独立 release = 30 个迁移路径；用户要一次升级"
  - option: "保持叙事 CHANGELOG（无 YAML frontmatter）"
    rejected_because: "失去 grep-ability + cohort dependency 追踪"

# v1.8.5+ 必需: 跨 release 依赖声明
ordering_dependency:
  blocked_by: []                           # 必须先 land 的 SHA / version ref
  must_coexist_with:                       # 必须一起 ship 的其他 commits/refs
    - Stage 0（failure-taxonomy + refactoring-patterns）
    - Stage 1（SOUL v2）
    - Stage 2（wiki v2）
    # ... 等

# v1.8.5+ 必需: 此次 release 加的回归用例
regression_cases_added:
  - rc-soul-no-priority
  - rc-soul-no-outlier
  - rc-soul-strawman-y
  - rc-wiki-no-outlier
  - rc-wiki-no-hypothesis
  - rc-agent-no-authority
  - rc-agent-blast-radius-violation
---

## v1.8.5 — Hook Retirement + EOU Hardening · 2026-05-23

> 1 段 release 总结。

### 亮点

- 用户可见亮点项目列表
- ...

### 迁移

- 用户如何从之前版本升级
- 跑哪些 slash command（如 `/migrate-soul-v2`）
- 向后兼容说明（D3 12 个月 legacy 共存）

### 致谢 / 背景

- （可选叙事段）
```

## v1.8.5+ 必需 YAML 字段

v1.8.5 起每个 release entry:

1. **version**: semver 字符串，如 `"1.8.5"`
2. **date**: ISO YYYY-MM-DD
3. **type**: `major | minor | patch | prerelease` 之一
4. **breaking_changes**: 数组（非破坏性 release 可空；即使空也必需字段）
5. **alternatives_considered**: ≥1 entry 含 `option` + `rejected_because`。"我们没考虑别的" 不是有效值。
6. **ordering_dependency**: `blocked_by` 数组 + `must_coexist_with` 数组（独立 patch 可空）
7. **regression_cases_added**: `rc-*` id 数组（无回归用例可空，但应 review —— 多数修复值得回归覆盖）

`new_features` 和 `fixes` 推荐但非必需。

## 验证

AUDITOR Mode 7（Stage 10 添加，v1.8.5 release 规划中）将验证:
- v1.8.5+ 每个 release entry 有所有 7 个必需字段
- `alternatives_considered` 有 ≥1 实质条目（LLM 启发式: rejected_because ≥20 字符 + 非平凡）
- `ordering_dependency.must_coexist_with` 引用解析到实际 commits/PRs/Stages
- `regression_cases_added` 引用存在于 `evals/regression-fixtures/`

## Legacy entries（v1.8.5 前）

v1.8.5 前的 CHANGELOG entry（v1.0.0 到 v1.8.4）保持叙事性。无需追溯迁移。Schema 从 v1.8.5 entry 开始适用。

## 三语同步

按 HARD RULE `三语文档同步`，YAML frontmatter schema 适用所有 3 个 CHANGELOG 文件:
- `CHANGELOG.md`（EN）
- `i18n/zh/CHANGELOG.md`（ZH）
- `i18n/ja/CHANGELOG.md`（JA）

3 个都必须有同一 v1.8.5+ entry 含同一 YAML frontmatter（body 翻译但结构化字段相同）。

## 来源出处

eou-foundry @ e4b12ce — `self-evolution/ecp/*.yml` YAML schema（每个 ECP 有 id / target_eou / target_version_from / target_version_to / problem / proposed_change / alternatives_considered / ordering_dependency）。为 life_OS CHANGELOG 适配（release-level vs ECP-level）：简化到 7 字段，保留 3 个最关键（alternatives_considered / ordering_dependency / regression_cases_added）。
