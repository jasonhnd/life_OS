# 全部 Agent 索引（24 个）

> Life OS 全部 subagent 的查表索引。**权威定义**在 [`agents/*.md`](../../../agents/)（每个 agent 的岗位说明书：功能边界、工具权限、触发条件）。
>
> 下面分组列出。**业务层 agent** 在本目录有详细文档（直接链到对应页）；**Cortex 认知层 + 工具/内部 agent** 只链到权威定义，不在本目录单独展开——它们是内部机制，单独写文档只会制造双份漂移。

## 编排层（8）

| Agent | 职能 | 详细文档 |
|-------|------|---------|
| router | 入口分诊：理解意图、决定路径（直接处理 / 快速 / 完整审议 / 智库） | [router.md](router.md) |
| planner | 把议题拆成可执行规划 | [planner.md](planner.md) |
| reviewer | 审议 + 封驳权 + 感性维度审查 | [reviewer.md](reviewer.md) |
| dispatcher | 把规划转成执行指令、定并行/串行顺序 | [dispatcher.md](dispatcher.md) |
| retrospective | 会话生命周期：上朝 / 复盘 / 上下文准备 | [retrospective.md](retrospective.md) |
| archiver | 退朝归档 + 知识提取 + DREAM + git 同步 | [archiver.md](archiver.md) |
| advisor | 行为模式顾问（读第二大脑历史） | [advisor.md](advisor.md) |
| auditor | 监察百官 + 合规巡检（Mode 3） | [auditor.md](auditor.md) |

## 六领域（6）

| Agent | 职能 | 详细文档 |
|-------|------|---------|
| finance | 财务：收入结构、预算、投资、税务、保险 | [finance.md](finance.md) |
| execution | 执行：项目分解、工具选型、精力管理 | [execution.md](execution.md) |
| governance | 治理：风险评估、合规、决策复盘、安全 | [governance.md](governance.md) |
| growth | 成长：学习规划、个人品牌、内容、社交礼仪 | [growth.md](growth.md) |
| infra | 基建：健康、居住环境、数字基建、生活流程 | [infra.md](infra.md) |
| people | 人际：关系评估、团队组建、委派决策 | [people.md](people.md) |

## 特殊（2）

| Agent | 职能 | 详细文档 |
|-------|------|---------|
| council | 跨域辩论：结论严重冲突时的 3 轮结构化辩论 | [council.md](council.md) |
| strategist | 智库 Hall of Wisdom：与历史思想家对话 | [strategist.md](strategist.md) |

## Cortex 认知层（5 · 内部，权威定义见 `agents/`）

| Agent | 职能 | 权威定义 |
|-------|------|---------|
| hippocampus | 跨会话记忆检索（3 波扩散激活） | [agents/hippocampus.md](../../../agents/hippocampus.md) |
| concept-lookup | 概念图直接匹配 | [agents/concept-lookup.md](../../../agents/concept-lookup.md) |
| soul-check | 相关 SOUL 维度检查 | [agents/soul-check.md](../../../agents/soul-check.md) |
| gwt-arbitrator | GWT 显著性仲裁，合并 Cortex 信号 | [agents/gwt-arbitrator.md](../../../agents/gwt-arbitrator.md) |
| narrator | 给 Summary Report 加引用（ROUTER 内部模式，非独立 spawn） | [agents/narrator.md](../../../agents/narrator.md) |

> Cortex 自 v1.8.0 起为 pull-based（ROUTER 按需启动），当前行为见 `hosts/CLAUDE.md` §0.5；v1.7 时代的用户指南已归档到 `docs/history/cortex/`。

## 工具 / 内部（3 · 权威定义见 `agents/`）

| Agent | 职能 | 权威定义 |
|-------|------|---------|
| knowledge-extractor | archiver Phase 2 知识提取 carve-out | [agents/knowledge-extractor.md](../../../agents/knowledge-extractor.md) |
| memory-keeper | archiver Phase 5 gotchas 提炼 | [agents/memory-keeper.md](../../../agents/memory-keeper.md) |
| monitor | 运维控制台（看维护任务时间戳 + 报告） | [agents/monitor.md](../../../agents/monitor.md) |

---

> 注：`agents/WHEN-NOT-TO-ADD.md` 不是 agent，而是「何时**不要**新增 agent」的边界守则，故不在本索引内。
