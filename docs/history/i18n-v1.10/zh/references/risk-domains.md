---
spec_id: risk-domains.v1
description: 8 个高风险领域，需自动升级。当 ROUTER triage 或 REVIEWER 否决在任一领域检测到主题时，完整的 5 项升级协议生效（人类审批者、证据审计、决策记录、cannot_delegate、trace 必需）。
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/governance.yml lines 67-82
introduced_in: v1.8.5
---

# 高风险领域

> 8 个领域，任何决策都必须触发完整升级，不管表面请求多平凡。ROUTER triage 用这些作为自动 full-deliberation 标志。REVIEWER 不能对这些领域给"approved"verdict，除非 5 项升级要求全部满足。

## 8 个高风险领域

| ID | 领域 | 触发条件 |
|---|---|---|
| **R1** | **finance（金融）** | 投资决策、大额采购（>月收入 20%）、负债、税务结构变更、企业股权决策 |
| **R2** | **health（健康）** | 医疗手术选择、用药变更、精神健康决策、慢性病管理、生育决策 |
| **R3** | **legal（法律）** | 签/解约、考虑诉讼、合规选择、知识产权转让、婚姻/离婚、监护权 |
| **R4** | **safety（安全）** | 影响人身安全的决策（去高风险地区、危险活动、武器持有、安防部署）|
| **R5** | **children（儿童）** | 任何影响未成年子女生命轨迹、教育、监护、风险暴露的决策 |
| **R6** | **public claims（公开声明）** | 公开陈述（社交媒体、媒体、证词、专业声誉）—— 虚假陈述风险 |
| **R7** | **publication（公开发布）** | 释放无法收回的内容/代码/数据（开源私有 repo、博客、出书、学术论文）|
| **R8** | **governance（治理）** | 对 life_OS 自身的改动（HARD RULES、agent 定义、schema 版本、防御层、版本 pivot）|

## 5 项自动升级要求

当 ROUTER 在用户消息中检测到 R1-R8 任一，或 REVIEWER 的 verdict 涉及这些领域时，以下 5 项要求**全部**适用：

### Req 1 — 人类审批者
- AI 不能给最终批准。这些领域里 ROUTER 和 REVIEWER 是 "suggest_only + write_inactive"。
- 最终 go/no-go 决策**必须**来自用户在 chat 界面的输入。
- "用户 2 条消息前说 yes"不够——当前决策需要当前确认。

### Req 2 — 证据审计
- 支持决策的所有 claim **必须**可引用追溯。
- ROUTER 必须粘贴 `gh` / `Bash` / `Read` 原始输出来支持任何事实 claim（不允许总结）。
- REVIEWER 必须按 `id` 引用具体 SOUL 维度（不允许 paraphrase）。
- 任何虚构 = F17 VALUE_HALLUCINATION + B confabulated-path 违规。

### Req 3 — 决策记录
- 结果**必须**写入 `meta/decisions/<YYYY-MM>/dec-<YYYY-MM-DD>-<NNN>.md`（v1.9 月子目录），含：
  - subject
  - alternatives_considered（≥2 个被拒选项 + 拒因）
  - 决策理由
  - 调用的 SOUL 维度（含优先级）
  - reviewer 名字
  - reviewed_at
  - reversal_condition（什么情况下值得重新考虑）
- 如果决策是 "no_change" / "not now" → 用 Stage 7 `no_change_record` 格式（`meta/decisions/` 中 7 字段 YAML）。

### Req 4 — Cannot_delegate
- 决策**不可**委派给 subagent 或未来 ROUTER session。
- subagent 报告是输入；最终决策在 orchestrator 主上下文 + 用户在场时做。

### Req 5 — Trace 必需
- 按 R12 spec 必须有完整审计 trail 在 `meta/runtime/<sid>/`：
  - 每次 subagent 调用：`<subagent>-<step>.md`
  - REVIEWER verdict：`reviewer-final-verdict.md`，含填好的 `value_invocations[]`
  - 用户确认消息时间戳 + 原文

## ROUTER 如何在 triage 检测高风险领域

ROUTER 使用以下启发式模式。**任一匹配 → 升级到 full deliberation，不管其他 triage 决策。**

### 基于关键词

| 领域 | 触发关键词（中/英/日 示例）|
|---|---|
| finance | 投资 / 买房 / 借钱 / 贷款 / IPO / 持仓 / 期权 / 信用卡分期 / invest / buy house / loan / mortgage / stock / option / equity / 投資 / ローン |
| health | 手术 / 吃药 / 抗生素 / 精神科 / 备孕 / 流产 / 化疗 / 透析 / surgery / medication / psychiatric / fertility / chemo / 手術 / 抗生物質 |
| legal | 签合同 / 离婚 / 起诉 / 仲裁 / 反诉 / 商标 / 专利 / 移民申请 / contract / divorce / lawsuit / arbitration / patent / immigration / 契約 / 離婚 |
| safety | 出差 / 高危地区 / 自驾游 / 极限运动 / 配枪 / 跟踪狂 / travel to / dangerous activity / firearm / stalker / 出張 / 危険 |
| children | 孩子 / 育儿 / 学校选择 / 监护权 / 未成年 / kid / child / school choice / custody / minor / 子供 / 学校 |
| public claims | 发帖 / 公开声明 / 上电视 / 证词 / 简历 / 推特 / blog / press / testify / public statement / resume claim / 公開 |
| publication | 开源 / 出书 / 投稿 / 论文 / 上线 / 公开 repo / open source / publish / submit / release / launch / 公開 |
| governance | 改 SOUL / 改 agent / 新加 HARD RULE / refactor / pivot / breaking change / 退役 hook / SOUL を変更 / pivot |

### 基于上下文

即使无显式关键词，ROUTER 必须在以下情况触发升级：
- 主题涉及金额 >$1000（finance）
- 主题涉及任何具名人士的医疗状况（health）
- 主题涉及任何时间限定的承诺 >6 个月（legal/governance）
- 主题涉及修改 `agents/` 或 `references/` 下任何文件（governance）

### "升级"的实际含义

- ROUTER **不可**对 R1-R8 主题使用 "Handle Directly" 或 "Express Analysis" 路径。
- 必须走完整 Draft-Review-Execute（PLANNER → REVIEWER → DISPATCHER → 6 Domains → REVIEWER Final → AUDITOR → ADVISOR → ARCHIVER）。
- COUNCIL 触发阈值降低：score diff ≥ 2（默认 3）自动启动 COUNCIL。

## 使用场景

- **ROUTER triage**（`agents/router.md` Stage 6 v2 frontmatter）：`context_manifest.source_of_truth` 含本文件。Triage 步骤必须检查用户消息是否匹配 R1-R8。
- **REVIEWER 否决**（`agents/reviewer.md`）：Verdict 必须引用适用的风险领域；如有，必须确认 5 要求全部。
- **AUDITOR Mode 3**（Stage 7 Day 21）：scenario 检查每个决策类事件——如果主题在 R1-R8 中且 5 要求任一缺失 → F10 RESPONSIBILITY_FAILURE。

## 来源出处

eou-foundry @ e4b12ce — `engine/governance.yml` 67-82 行（8 domains + 5 automatic_requirements）。适配 life_OS 个人使用场景：示例基于个人决策（finance/health/family）而非企业治理。
