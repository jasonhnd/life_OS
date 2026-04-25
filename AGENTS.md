# Life OS · 三省六部制个人内阁系统

本项目使用三省六部制个人内阁系统。

## 权威文件索引

- **系统定义**：`SKILL.md`（根目录）— 角色、流程、格式、行为准则的权威源
- **Pro 模式编排协议（按 host 拆分）**：
  - Claude Code: `pro/CLAUDE.md`
  - Gemini CLI / Antigravity: `pro/GEMINI.md`
  - OpenAI Codex CLI: `pro/AGENTS.md`
- **16 个 subagent 定义**：`pro/agents/*.md` — 各角色的岗位说明书（跨 host 共享）
- **六领域职能详解**：`references/domains.md`
- **标准场景配置**：`references/scene-configs.md`
- **数据模型与 Notion 适配器**：`references/data-model.md`、`references/adapter-notion.md`

## Host-Agnostic 语义合同（v1.7）

本文件定义 Life OS 在任何 host（Claude Code / Gemini / Codex）上都必须满足的**语义合同**。具体 host 调用语法、子代理 spawn 方式、工具映射见 `pro/{CLAUDE,GEMINI,AGENTS}.md`。

### Step 0.5 · Pre-Router Cognitive Layer（v1.7 Cortex Phase 1）· OPTIONAL

当用户发送非 Start-Session 消息 **且** 绑定的 second-brain 中存在 `_meta/sessions/INDEX.md` 时，orchestrator **可以**在 ROUTER 介入之前启动认知前置层。激活由 `_meta/config.md` 中 `cortex_enabled: true|false` 控制，v1.7 默认 **opt-out**（关闭，需用户显式开启）。

**语义合同**：
1. 并行启动 3 个独立的 subagent（互相信息隔离，严格按 Information Isolation 表接收输入）：
   - `hippocampus` — 跨会话记忆检索，基于 `_meta/sessions/INDEX.md` 和概念图做 3-wave spreading activation
   - `concept-lookup`（Phase 1.5）— 直接概念图匹配，返回 Top 5-10 相关概念
   - `soul-check` — 通过当前 SOUL Health Report 提供相关 SOUL 维度信号；orchestrator 把 RETROSPECTIVE housekeeping 输出的 SOUL Health block 传给它
2. 3 个 subagent 返回后（5s soft / 15s hard 超时），启动 `gwt-arbitrator` 仲裁并合成 `[COGNITIVE CONTEXT]` 块
3. Orchestrator 将 `[COGNITIVE CONTEXT]` 块**前置**到用户消息之上，再交给 ROUTER
4. ROUTER 按分隔符识别"顾问信息"与"真实用户输入"；此 context 是**建议性**而非权威性的

**降级规则**（任一触发，Step 0.5 完全跳过，回退到 v1.6.3 行为）：
- INDEX 文件缺失或为空
- 任一 subagent 超时 → 该槽位置 `null`，GWT 基于可用信号继续
- GWT 超时 → 发出空 `[COGNITIVE CONTEXT]` 块
- `cortex_enabled: false`

**成本预算**：每次调用约 $0.05-0.10。用户累积 ≥30 session 后开启收益较大。

**Host 实现**：
- Claude Code: `pro/CLAUDE.md` §0.5（Task tool + Shell Hook 双层防御）
- Gemini CLI:  `pro/GEMINI.md` §0.5（prompt-level only, no hook backstop）
- Codex CLI:   `pro/AGENTS.md` §0.5（prompt-level only, no hook backstop）

### Step 7.5 · Narrator + Narrator-Validator（v1.7 Cortex Phase 2）· OPTIONAL

当 Step 0.5 已激活 Cortex，在 REVIEWER Final Review（step 6）之后、ROUTER Summary Report（step 7）展示之前，orchestrator **可以**触发 **ROUTER Step 7.5（narrator mode）**——一个 ROUTER-internal narrator composition 步骤（**不是**独立 subagent；见 `pro/compliance/2026-04-21-narrator-spec-violation.md`），对 Summary Report 的**实质性论断**（substantive claims）包裹 `signal_id` 引用。这是为了防止 Gazzaniga 式的"左脑解释者"虚构（confabulation）。

**语义合同**：
1. ROUTER 进入 Step 7.5（narrator mode），`Read` 模板 `pro/agents/narrator.md`（ROUTER-internal composition template，**不**通过 Task spawn），传入 Draft Summary Report + GWT 输出的 `[COGNITIVE CONTEXT]` 信号存储
2. ROUTER（narrator mode）对每条实质性论断挂接 `signal_id` 引用（连接性/修辞性文字免引用）
3. 启动 `narrator-validator` 子代理（spec-compliant standalone Sonnet subagent，比 Opus 便宜），读 narrator mode 输出 + 信号存储，核验每条引用是否指向真实信号且论断与信号语义一致
4. 如 validator 失败 → 反馈给 ROUTER Step 7.5 重写，最多 2 次重写
5. 2 次重写仍失败 → 非阻塞降级到 v1.6.3 未包裹的 Summary Report，并记录到 `_meta/eval-history/narrator-{date}.md`

**预算（依据 `references/narrator-spec.md §11`，R3.1 commit `04e3498`）**：narrator + validator 循环的**累积**挂钟时间超过 **21 秒**，或**单次** regenerate-and-revalidate 循环超过 **8 秒** → 任一触发即降级（典型总时 ≈ 18 秒）。

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
