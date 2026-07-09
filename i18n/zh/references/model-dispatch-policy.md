---
spec_id: model-dispatch-policy.v1
description: 任务↔模型档位派发策略。声明三个能力档位（judgment / execution / batch），把每个 agent 与每个维护任务映射到其最低档位，定义弱模型派发指令格式，并把档位→模型绑定集中在唯一一张映射表中。关闭"前沿模型永远可用"的假设（issue #1 A1）。
status: active
authoritative: true
introduced_in: v1.10.0
referenced_by:
  - hosts/CLAUDE.md (model statement + fallback)
  - hosts/GEMINI.md (model mapping table)
  - hosts/AGENTS.md (model mapping table)
  - agents/dispatcher.md (§Weak-Model Dispatch Mode)
  - references/agent-spec.md (frontmatter `model:` field)
  - .claude/commands/run-eval.md (--tier flag, per issue #4 D2)
---

# 模型派发策略 v1（Model Dispatch Policy v1）

Life OS 是按前沿模型的阅读水平写成的，且 24 个 agent 定义中有 23 个绑定 `model: opus` 而无任何降级路径——当前沿模型不可用时（配额窗口、套餐变更、供应商故障、更便宜的部署），系统从"完全可用"直接退化到"不可用"。本 spec 补上缺失的中间层：为每个任务声明一个**能力下限（capability floor）**，与 `authority_level` 分离（后者管的是写权限，不是所需智力）。

## 三个档位

| 档位 | 覆盖范围 | 用更弱模型的失败代价 | 是否必须前沿模型？ |
|------|----------------|--------------------------------|--------------------|
| **judgment** | Router 分诊、规划、审查/否决、领域打分、内阁辩论、行为/价值分析 | 貌似合理实则错误的结论会引导真实决策——比没有产出更糟 | **是——锁定前沿模型** |
| **execution** | Archiver 机械操作、session 启动、索引维护、格式规范化、检索扫描、翻译初稿 | 可恢复的机械错误，会被检查/巡查捕获 | 否——中档可接受 |
| **batch** | Grep 扫描、链接审计、文件移动、计数核对、ledger 盖戳 | 可轻易检测；任务可重跑 | 否——最弱档位可接受 |

## HARD RULE · 禁止静默降级

**judgment 档位的工作绝不允许静默地跑在低于前沿的模型上。**当所需档位不可用时，正确行为是说 `⚠️ this requires a frontier session — deferring <task>` 然后停下。一个貌似合理实则错误的否决、领域评分或分诊决策，严格劣于一个被推迟的决策。静默降级属于 F12 DRIFT_FAILURE；AUDITOR 会标记它。

execution 与 batch 档位的工作可以跑在其下限或以上的任意档位。用前沿模型跑 batch 工作是允许的（只是浪费）；用 batch 模型跑 judgment 工作是禁止的。

## 档位 → 模型映射（模型绑定唯一存放处）

| 档位 | Claude Code 绑定（`model:` frontmatter 别名） | Gemini CLI / Antigravity | Codex CLI |
|------|--------------------------------------------------|--------------------------|-----------|
| judgment | `opus` | 可用的最强档（自动选择） | 可用的最强档（自动选择） |
| execution | `sonnet` | 中档 | 中档 |
| batch | `haiku` | 最便宜/最快档 | 最便宜/最快档 |

规则：

- `opus` / `sonnet` / `haiku` 是**宿主别名**（档位间接层），不是版本化模型名。宿主把它们解析为当前世代对应的模型。
- **版本化模型 ID（如 `claude-*-4-*`、带日期的快照）不得出现在本仓库任何位置**——agent frontmatter、文档示例、spec 都不行。模型名每几个月就换一轮；这张表是唯一的变更点。`/check-spec-drift` 把出现在本文件之外的版本化模型 ID 视为 drift。
- Agent frontmatter 的 `model:` 值是下表的 Claude Code 编译产物。要改绑定，先改这里 agent 对应的行，再改 frontmatter。

## Agent → 最低档位表（完整，24 个 agent）

`min_tier` 是能力**下限**——该 agent 产出仍然安全的最弱档位。Claude Code `model:` frontmatter 绑定的是*默认值*；默认值可以高于下限（绝不能低于）。

| Agent | min_tier | 默认绑定 | 备注 |
|-------|----------|-----------------|-------|
| router | judgment | opus | 分诊错误会误导下游一切 |
| planner | judgment | opus | |
| reviewer | judgment | opus | 否决权；情绪审计 |
| dispatcher | judgment | opus | 依赖检测 + B5 门禁；撰写弱模型派发指令 |
| council | judgment | opus | 结构化辩论 |
| auditor | judgment | opus | 跨 8 个模式的违规判断 |
| advisor | judgment | opus | 行为模式分析 |
| strategist | judgment | opus | 思想家声音 |
| people / finance / growth / execution / governance / infra | judgment | opus | 独立领域打分（6 个 agent） |
| gwt-arbitrator | judgment | opus | 显著性仲裁 |
| soul-check | judgment | opus | 价值对齐分类 |
| knowledge-extractor | judgment | opus | 自动写入 SOUL/wiki——门禁质量关乎身份 |
| narrator | judgment | (router-internal) | ROUTER 内部模板；跟随 router 的档位 |
| retrospective | execution | opus | Mode 0 大多是机械读取 + 组装；Steps 15-18 叙事可优雅降级（属建议，非决策） |
| archiver | execution | opus | Outbox 移动、git 同步、报告组装；DREAM 发现是候选项，不是决策 |
| hippocampus | execution | opus | 对 INDEX 的机械扩散激活扫描 |
| concept-lookup | execution | opus | INDEX 直接匹配 |
| monitor | execution | opus | 查看并调用的运维台 |
| memory-keeper | execution | sonnet | 已绑定中档（v1.10 之前唯一的例外） |

## 维护任务 → 最低档位表（完整，scripts/prompts/ + scripts/commands/）

| 任务（`scripts/prompts/`） | min_tier | 节奏（供 `meta/maintenance-ledger.md` 使用） |
|--------------------------|----------|--------------------------------------------|
| advisor-monthly | judgment | 30d |
| research | judgment | on-demand |
| strategic-consistency | judgment | 30d |
| archiver-recovery | execution | on-demand |
| auditor-mode-2 | execution | 7d |
| bulk-ingest (v1.10.0) | execution | on-demand |
| daily-briefing | execution | on-demand |
| doctor | execution | on-demand |
| extract-concepts | execution | on-demand |
| inbox-process | execution | 7d |
| migrate-from-v1.6 / migrate-v1.9 | execution | once |
| review-queue | execution | 7d |
| spec-compliance | execution | 30d |
| wiki-decay | execution | 30d |
| backup | batch | 7d |
| eval-history-monthly | batch | 30d |
| migrate-confidence / migrate-to-wikilinks / wiki-obsidian-upgrade | batch | once |
| rebuild-concept-index | batch | 30d |
| rebuild-session-index | batch | on-demand |
| reindex | batch | 7d |
| snapshot-cleanup | batch | 30d |
| verify-v1.9 | batch | once |

| 命令（`scripts/commands/`） | min_tier |
|-------------------------------|----------|
| research | judgment |
| compress / inbox-process / method / monitor | execution |
| memory / search | batch |

## 弱模型派发指令格式（低于前沿的派发）

当工作被派发到低于前沿的档位（execution 或 batch）时，派发指令必须收窄为**查表形式（lookup-table form）**：

1. **显式文件清单**——每个要读或写的文件都按路径逐一列出。不允许"扫描相关文件"。
2. **机械化编号步骤**——每一步都是具体的工具动作（Read X、在 Y 中 Grep 模式 P、Write Z），并写明预期形态。
3. **零开放判断**——"use your judgment"、"as appropriate"、"if it seems"、"decide whether" 这类措辞不得出现。任何决策点要么在指令中预先决定，要么列为 "STOP and report"。
4. **硬性机械验收检查**——完成与否由可 grep 验证/可计数的条件定义（如"0 行匹配模式 P"、"行数 == manifest 计数"），绝不用"看起来完成了"。
5. **升级条款**——一行写明当某一步的前置条件不满足时弱模型必须做什么：停下并汇报，绝不即兴发挥。

派发方合约见 `agents/dispatcher.md` §"Weak-Model Dispatch Mode"。

## 所需档位不可用时的回退行为

| 情形 | 行为 |
|-----------|----------|
| 前沿模型不可用，请求的是 judgment 档位任务 | 说 `⚠️ this requires a frontier session` 并停下（上文 HARD RULE）。向用户列出可以继续进行的 execution/batch 工作清单。 |
| 前沿模型不可用，请求的是 execution/batch 任务 | 在不低于任务下限的可用档位上继续。 |
| 中档也不可用（只剩 batch 模型） | 上表中只有 batch 档位的行可以运行。其余全部推迟。 |
| 不确定当前模型属于哪个档位 | 按 batch 处理（最保守的下限）。 |

## 降级安全性证据（issue #4 D2 链接）

上表中的档位声明由实证验证，而非直觉：eval 场景带 `min_model_tier:` frontmatter 字段，`/run-eval --tier <tier>` 用该档位映射的模型运行它们，`docs/evals/tier-matrix.md` 由真实运行结果重新生成。某场景在其声明档位上失败即是 spec bug——要么这张表过于乐观，要么 prompt 需要简化。
