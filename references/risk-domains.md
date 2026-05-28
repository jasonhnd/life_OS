---
spec_id: risk-domains.v1
description: 8 high-risk domains requiring automatic escalation. When ROUTER triage or REVIEWER veto detects subject matter in any of these domains, the full 5-requirement escalation protocol applies (human approver, evidence audit, decision record, cannot_delegate, trace required).
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/governance.yml lines 67-82
introduced_in: v1.8.5
---

# Risk Domains

> 8 domains where ANY decision must trigger full escalation, regardless of how mundane the surface request looks. ROUTER triage uses these as automatic full-deliberation flags. REVIEWER cannot give "approved" verdict in these domains without all 5 escalation requirements being met.

## The 8 high-risk domains

| ID | Domain | What triggers it |
|---|---|---|
| **R1** | **finance** | Investment decisions, large purchases (>20% monthly income), taking on debt, tax structure changes, business equity decisions |
| **R2** | **health** | Medical procedure choices, medication changes, mental health decisions, chronic condition management, fertility decisions |
| **R3** | **legal** | Contract signing/breaking, lawsuit considerations, regulatory compliance choices, IP transfers, marriage/divorce, custody |
| **R4** | **safety** | Decisions affecting physical safety (travel to high-risk areas, dangerous activities, weapon ownership, security setup) |
| **R5** | **children** | Any decision affecting minor children's life trajectory, education, custody, exposure to risk |
| **R6** | **public claims** | Public statements (social media, press, court testimony, professional reputation claims) — false claim risk |
| **R7** | **publication** | Releasing content/code/data that cannot be unreleased (open-sourcing private repos, blog posts, books, academic papers) |
| **R8** | **governance** | Changes to life_OS itself (HARD RULES, agent definitions, schema versions, defense layers, version pivots) |

## The 5 automatic escalation requirements

When ROUTER detects ANY of R1-R8 in user message OR REVIEWER's verdict involves any of these domains, the following 5 requirements ALL apply:

### Req 1 — Human approver
- AI cannot give final approval. ROUTER and REVIEWER are "suggest_only + write_inactive" in these domains.
- Final go/no-go decision MUST come from the user in the chat interface.
- "User said yes 2 messages ago" is insufficient — current decision needs current confirmation.

### Req 2 — Evidence audit
- All claims supporting the decision MUST be cite-traceable.
- ROUTER must paste literal `gh` / `Bash` / `Read` output for any factual claim (no summarizing).
- REVIEWER must reference specific SOUL dimensions by `id` (no paraphrasing).
- Anything fabricated = F17 VALUE_HALLUCINATION + B confabulated-path violation.

### Req 3 — Decision record
- Outcome MUST be written to `meta/decisions/<YYYY-MM>/dec-<YYYY-MM-DD>-<NNN>.md` (v1.9 month subdir) with:
  - subject
  - alternatives_considered (≥2 rejected options + why)
  - decision rationale
  - SOUL dimensions invoked (with priorities)
  - reviewer name
  - reviewed_at
  - reversal_condition (what would warrant reconsidering)
- If decision is "no_change" / "not now" → use Stage 7 `no_change_record` format (7-field YAML in `meta/decisions/`).

### Req 4 — Cannot_delegate
- The decision MUST NOT be delegated to a subagent or future ROUTER session.
- Subagent reports are inputs; final decision happens in the orchestrator main context with user present.

### Req 5 — Trace required
- Full audit trail MUST exist in `meta/runtime/<sid>/` per R12 spec:
  - Every subagent invocation: `<subagent>-<step>.md`
  - REVIEWER verdict: `reviewer-final-verdict.md` with `value_invocations[]` populated
  - User confirmation message timestamp + literal text

## How ROUTER detects risk domains in triage

ROUTER uses these heuristic patterns. **If any match → escalate to full deliberation, regardless of triage decision otherwise.**

### Keyword-based detection

| Domain | Trigger keywords (中/英/日 examples) |
|---|---|
| finance | 投资 / 买房 / 借钱 / 贷款 / IPO / 持仓 / 期权 / 信用卡分期 / invest / buy house / loan / mortgage / stock / option / equity / 投資 / ローン |
| health | 手术 / 吃药 / 抗生素 / 精神科 / 备孕 / 流产 / 化疗 / 透析 / surgery / medication / psychiatric / fertility / chemo / 手術 / 抗生物質 |
| legal | 签合同 / 离婚 / 起诉 / 仲裁 / 反诉 / 商标 / 专利 / 移民申请 / contract / divorce / lawsuit / arbitration / patent / immigration / 契約 / 離婚 |
| safety | 出差 / 高危地区 / 自驾游 / 极限运动 / 配枪 / 跟踪狂 / travel to / dangerous activity / firearm / stalker / 出張 / 危険 |
| children | 孩子 / 育儿 / 学校选择 / 监护权 / 未成年 / kid / child / school choice / custody / minor / 子供 / 学校 |
| public claims | 发帖 / 公开声明 / 上电视 / 证词 / 简历 / 推特 / blog / press / testify / public statement / resume claim / 公開 |
| publication | 开源 / 出书 / 投稿 / 论文 / 上线 / 公开 repo / open source / publish / submit / release / launch / 公開 |
| governance | 改 SOUL / 改 agent / 新加 HARD RULE / refactor / pivot / breaking change / 退役 hook / SOUL を変更 / pivot |

### Context-based detection

Even without explicit keywords, ROUTER MUST trigger escalation if:
- Subject involves money amounts >$1000 (finance)
- Subject involves any named person's medical condition (health)
- Subject involves any time-bounded commitment >6 months (legal/governance)
- Subject involves modifying any file under `pro/agents/` or `references/` (governance)

### What "escalation" means in practice

- ROUTER MUST NOT use "Handle Directly" or "Express Analysis" path for R1-R8 subjects.
- MUST go through full Draft-Review-Execute (PLANNER → REVIEWER → DISPATCHER → 6 Domains → REVIEWER Final → AUDITOR → ADVISOR → ARCHIVER).
- COUNCIL trigger threshold lowered: score diff ≥ 2 (vs default 3) automatically launches COUNCIL.

## Use cases

- **ROUTER triage** (`pro/agents/router.md` Stage 6 v2 frontmatter): `context_manifest.source_of_truth` includes this file. Triage step MUST check user message against R1-R8.
- **REVIEWER veto** (`pro/agents/reviewer.md`): Verdict MUST cite which risk domains apply; if any, 5 requirements MUST be confirmed.
- **AUDITOR Mode 3** (Stage 7 Day 21): scenario checks every decision-class incident — if subject was in R1-R8 and any of 5 requirements missing → F10 RESPONSIBILITY_FAILURE.

## Source attribution

eou-foundry @ e4b12ce — `engine/governance.yml` lines 67-82 (8 domains + 5 automatic_requirements). Adapted for life_OS personal-use context: examples grounded in personal decisions (finance/health/family) rather than enterprise governance.
