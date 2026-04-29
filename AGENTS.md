# Life OS · 三省六部制个人内阁系统

> **v1.8.0 pivot 已完成 (R-1.8.0-013 round-7 audit · 2026-04-30)**：本文件已重写为 v1.8.0 host-agnostic 语义合同。Cortex 由 always-on 改为 pull-based，cron 已删除（全部维护任务 user-invoked），narrator-validator 已删除（改为 narrator inline self-check）。**权威 spec 仍是 `pro/CLAUDE.md`**；本文件提供 host-agnostic 抽象，与 `pro/CLAUDE.md` 冲突时以 `pro/CLAUDE.md` 为准。

本项目使用三省六部制个人内阁系统。

## 权威文件索引

- **系统定义**：`SKILL.md`（根目录）— 角色、流程、格式、行为准则的权威源
- **Pro 模式编排协议（按 host 拆分）**：
  - Claude Code: `pro/CLAUDE.md`
  - Gemini CLI / Antigravity: `pro/GEMINI.md`
  - OpenAI Codex CLI: `pro/AGENTS.md`
- **23 个 subagent 定义**：`pro/agents/*.md` — 各角色的岗位说明书（跨 host 共享）
- **六领域职能详解**：`references/domains.md`
- **标准场景配置**：`references/scene-configs.md`
- **数据模型与 Notion 适配器**：`references/data-model.md`、`references/adapter-notion.md`

## Host-Agnostic 语义合同（v1.8.0）

本文件定义 Life OS 在任何 host（Claude Code / Gemini / Codex）上都必须满足的**语义合同**。具体 host 调用语法、子代理 spawn 方式、工具映射见 `pro/{CLAUDE,GEMINI,AGENTS}.md`。

### Step 0.5 · Pre-Router Cognitive Layer · PULL-BASED in v1.8.0

> v1.7.2 设计是 always-on（每条消息都 spawn 3 个 cognitive subagent，~$0.05-0.10 / turn）。**v1.8.0 R-1.8.0-011 改为 pull-based**：ROUTER 按消息内容判断是否需要历史 context，需要时才 spawn。`cortex_enabled` config flag 已不再用作激活闸门（保留是为旧 vault 兼容）。

**可选 subagent（ROUTER 按需 spawn，不自动）**：
1. `hippocampus` — 跨 session 记忆检索（user 问 "我们之前决定 X 怎么处理来着" 时启动）
2. `concept-lookup` — 概念图匹配（user 提到已知 concept 时启动）
3. `soul-check` — SOUL 维度相关性（消息触及价值观/身份/重复模式时启动）
4. `gwt-arbitrator` — 当上述 ≥2 个返回信号时才 spawn，做仲裁

**降级规则**（v1.8.0 pull-based 简化）：
- ROUTER 判断不需要 Cortex（多数消息）→ 直接处理 raw user message
- INDEX 缺失或空 → ROUTER 内联读 `scripts/prompts/rebuild-concept-index.md` 引导（`tools/migrate.py` 已在 R-1.8.0-011 删除）
- 任一 spawned subagent 超时 → 该槽位 null，GWT 用可用信号继续
- 只有 1 个 Cortex 信号 → ROUTER 直接消费，不 spawn arbitrator

**成本预算（v1.8.0）**：多数消息 $0（不 spawn）；仅在 ROUTER 显式判断需要历史 context 时计费。

**Host 实现**：
- Claude Code: `pro/CLAUDE.md` §0.5（Task tool + Shell Hook 双层防御）
- Gemini CLI:  `pro/GEMINI.md` §0.5（prompt-level only, no hook backstop）
- Codex CLI:   `pro/AGENTS.md` §0.5（prompt-level only, no hook backstop）

### Step 7.5 · Narrator + Narrator-Validator（v1.7 Cortex Phase 2）· OPTIONAL

当 Step 0.5 已激活 Cortex，在 REVIEWER Final Review（step 6）之后、ROUTER Summary Report（step 7）展示之前，orchestrator **可以**触发 **ROUTER Step 7.5（narrator mode）**——一个 ROUTER-internal narrator composition 步骤（**不是**独立 subagent；见 `pro/compliance/2026-04-21-narrator-spec-violation.md`），对 Summary Report 的**实质性论断**（substantive claims）包裹 `signal_id` 引用。这是为了防止 Gazzaniga 式的"左脑解释者"虚构（confabulation）。

**语义合同 (v1.8.0 R-1.8.0-011 简化)**：
1. ROUTER 进入 Step 7.5（narrator mode），`Read` 模板 `pro/agents/narrator.md`（ROUTER-internal composition template，**不**通过 Task spawn），传入 Draft Summary Report + GWT 输出的 `[COGNITIVE CONTEXT]` 信号存储
2. ROUTER（narrator mode）对每条实质性论断挂接 `signal_id` 引用（连接性/修辞性文字免引用）
3. ROUTER 自检引用（inline rules in `pro/agents/narrator.md` "Citation rules" 段）—— 每条引用是否指向真实信号且论断与信号语义一致
4. 自检失败 → 直接降级到未包裹的 Summary Report，并记录到 `_meta/eval-history/narrator-{date}.md`（不再有 validator-rewrite 循环）

**v1.8.0 简化**：previously v1.7.2 用独立 `narrator-validator` Sonnet subagent + 最多 2 次 rewrite 循环 + 21s/8s 时间预算。Option A pivot (R-1.8.0-011) 删除 `pro/agents/narrator-validator.md`，引用核查改在 narrator 模板内 inline 完成；典型总时从 ~18s 降到 ~3-5s（无独立 subagent spawn）。

**引用格式**：见 `references/narrator-spec.md §4`。

**Host 实现**：
- Claude Code: `pro/CLAUDE.md` §7.5
- Gemini CLI:  `pro/GEMINI.md` §7.5（prompt-level only, no hook backstop）
- Codex CLI:   `pro/AGENTS.md` §7.5（prompt-level only, no hook backstop）

### Information Isolation · 跨 host 统一表（v1.7）

| Role | Receives | Does Not Receive |
|------|----------|------------------|
| RETROSPECTIVE agent | User message (housekeeping), `_meta/strategic-lines.md` + 所有 project strategic fields | 无限制 |
| ARCHIVER agent | Summary Report + reports + session 对话摘要，所有 project strategic fields | 其他 agent 的 thought processes |
| **HIPPOCAMPUS** (v1.7) | current_user_message + extracted_subject + current_project + current_theme + recent_inbox_items + current_strategic_lines | 其他 Cortex 子代理输出（concept-lookup, soul-check）、`SOUL.md` 全文、历史会话全文（仅限 INDEX 摘要） |
| **CONCEPT-LOOKUP** (v1.7) | current_user_message + extracted_subject + current_project + current_theme | 其他 Cortex 输出（hippocampus, soul-check）、概念全文（仅 INDEX 扫描 + 选择性 top file 阅读） |
| **SOUL-CHECK** (v1.7) | current_user_message + extracted_subject + current_project + current_theme | 其他 Cortex 输出（hippocampus, concept-lookup）、最近一份以外的 snapshot（旧 snapshot 是 RETROSPECTIVE 的职责） |
| **GWT-ARBITRATOR** (v1.7) | hippocampus_output + concept_lookup_output + soul_check_output + current_user_message | ROUTER reasoning、原始会话内容、agent thought processes |
| **NARRATOR** (v1.7 Phase 2, ROUTER @ Step 7.5 narrator mode — **不是**独立 subagent；见 `pro/compliance/2026-04-21-narrator-spec-violation.md`) | Draft Summary Report + cognitive_context (来自 GWT 的 signals) | 其他 agent 的 thought processes、`SOUL.md` 原文、`wiki/` 原始文件 |
| **NARRATOR-VALIDATOR** (v1.7 Phase 2.5) | narrator_output + cognitive_context（与 narrator 相同输入） | 输入以外的任何内容 |
| ROUTER | User message + RETROSPECTIVE 的 Pre-Session Preparation + `_meta/STRATEGIC-MAP.md`（已编译）+ Cortex 激活时的 `[COGNITIVE CONTEXT]` 块 | — |
| PLANNER | Subject + background + user message + 本会话绑定项目的 strategic 上下文（仅 flows，不含完整 map） | ROUTER reasoning、完整 strategic map |
| REVIEWER | planning document 或 Six Domains reports + 与本决策相关的 flow graph | thought processes、完整 strategic map |
| DISPATCHER | 已批准的 planning document | thought processes |
| Each Domain | dispatch 指令 + 背景材料 + 本项目的 strategic role（如存在） | 其他 domain 的 reports、完整 strategic map |
| AUDITOR | 完整的 workflow 记录 | 无限制 |
| ADVISOR | Summary Report + user message（自行读取 second-brain） | thought processes |

### Shell Hook Layer（Layer 3）host 可用性

| Host | Layer 1 文档 HARD RULE | Layer 2 Subagent 隔离 | Layer 3 Shell Hooks | Layer 4 Python 批处理工具 |
|------|-----------------------|-----------------------|--------------------|--------------------------|
| Claude Code | ✅ | ✅ | ✅（`references/hooks-spec.md §2`）| ✅ |
| Gemini CLI | ✅ | ✅ | ❌（v1.7 prompt-level only）| ✅ |
| Codex CLI | ✅ | ✅ | ❌（v1.7 prompt-level only）| ✅ |

当 Gemini / Codex 公开兼容的 hook surface 后，`scripts/hooks/` 下的 5 个脚本可无缝迁移。在此之前，非 Claude Code host 的所有 HARD RULE 均为 prompt-level 强制，无运行时 backstop。

## 进一步阅读

- `references/cortex-spec.md` — Cortex 整体架构（四大机制：hippocampus / gwt / narrator / concept-graph）
- `references/hooks-spec.md` — 5 个 Shell Hook 的 authoritative contract（Claude-Code-only in v1.7）
- `references/narrator-spec.md` — Narrator + Validator 的 grounded generation 合同
- `references/v1.7-shipping-report-2026-04-21.md` — v1.7 shipping 总结
- `docs/architecture/v1.7-spec-map.md` — 16 条锁定用户决策 + spec 依赖图 + spec-code precedence rules
