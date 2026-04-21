---
incident_id: NARRATOR-SPEC-001
date: 2026-04-21
severity: P2 · spec-code inconsistency
status: deferred-to-P5
affects: pro/agents/narrator.md
---

# Narrator spec-code mismatch

## Conflict

- `references/cortex-spec.md §Deliverable List`（via `docs/architecture/v1.7-spec-map.md §6 · v1.7 Deliverable List (new agent files to create)`）明确：
  > **Do NOT create**: `pro/agents/narrator.md` — narrator behavior lives inside ROUTER (`narrator-spec.md §6` is authoritative)
- `references/narrator-spec.md §6 Narrator Agent` confirms:
  > ROUTER itself handles the narrator role. There is **no separate `pro/agents/narrator.md` file**. The narrator behavior is configured via pro/CLAUDE.md orchestration updates and lives inside ROUTER's output composition responsibilities.
- `docs/architecture/v1.7-spec-map.md §5.1 Write ownership invariants`:
  > **ROUTER owns user-facing output** — narrator is part of ROUTER's Step 7.5 composition; no separate `pro/agents/narrator.md` file.
- **Fact on disk (2026-04-21)**：`pro/agents/narrator.md` 已存在（created during v1.7.0-alpha development).

```bash
$ ls pro/agents/ | grep narrator
narrator-validator.md
narrator.md           # <-- 不应存在，per spec
```

同时 `pro/CLAUDE.md §0.5` / `pro/GEMINI.md §0.5` / `pro/AGENTS.md §0.5` 当前措辞为 "orchestrator MAY also launch `narrator` ... See `pro/agents/narrator.md`"，此表述与 spec-authoritative 的"ROUTER-internal"定位矛盾。

## Spec-Code Precedence Resolution

Per `docs/architecture/v1.7-spec-map.md §4 Precedence rules when two specs appear to conflict`, rule 3 applies:

> **Per-mechanism spec wins on its own mechanism's behavior.** For retrieval algorithm → hippocampus-spec. For arbitration formula → gwt-spec. **For citation format → narrator-spec.** For concept graph rules → concept-spec.

Narrator's agent identity (standalone vs ROUTER-internal) is a narrator-mechanism behavior question → `narrator-spec.md §6` wins. **Spec is right, code is wrong.**

Rule 5.1 (Write ownership invariants) independently reaches the same conclusion: "narrator is part of ROUTER's Step 7.5 composition; no separate `pro/agents/narrator.md` file".

## Options (3) — P5 decision

### Option A · Delete `pro/agents/narrator.md`（spec-compliant · cleanest）

**Pro**：
- 匹配 spec authoritative 定义
- 消除 spec-code 分歧，新开发者不再被误导
- ROUTER 已经在 Step 7/7.5 owning composition，narrator 行为本就是 ROUTER 内部职责的一个 named step

**Con**：
- `pro/{CLAUDE,GEMINI,AGENTS}.md §0.5` + §7.5 当前文案提到 "narrator subagent" 和 "See `pro/agents/narrator.md`"，删除后需重写为 "ROUTER internal narrator composition step"
- Information Isolation 表的 NARRATOR 行需改写成 "ROUTER at Step 7.5（narrator mode）" 或彻底移除该行，将其输入合并回 ROUTER 行的 "When Cortex enabled, also receives..."

### Option B · Revise spec to allow standalone narrator subagent

**Pro**：
- Code already exists, 改 spec 比删 code 风险低
- `pro/agents/narrator.md` 内容可作为独立 prompt template 存在

**Con**：
- 需要更新 `references/narrator-spec.md §6`、`references/cortex-spec.md §Deliverable List`、`docs/architecture/v1.7-spec-map.md §5.1 §6` 三处
- 需要 re-run 一致性审计，确认没有其他 spec 依赖"narrator is not a new agent file"这个假设
- 打破了"ROUTER owns user-facing output"的 write-ownership invariant — 这是 §5.1 明确记载的 cross-spec invariant，修订需谨慎

### Option C · Keep both + clarify（最小侵入）

**Pro**：
- 无需删除 code 也无需改 3 个 spec
- 将 `pro/agents/narrator.md` 显式标记为 **ROUTER-internal prompt template stored under `pro/agents/` for locality**，而非 Task-launchable / spawn-able subagent
- ROUTER 在 Step 7.5 可以 `Read` 该文件作为自己的 composition 指南，但不能将其 `Task(narrator)` / `Spawn(narrator)` 启动为独立 subagent

**Con**：
- `pro/agents/` 目录下存在"非标准"文件类型（prompt template vs subagent definition），新开发者可能混淆
- 需要在 `pro/agents/narrator.md` 顶部显著添加 "THIS IS A ROUTER-INTERNAL TEMPLATE, NOT A STANDALONE SUBAGENT" 标记
- 需要审计 pro/agents/*.md 中 frontmatter，如果 narrator.md 有 `name: narrator` frontmatter，会被 Task tool 视为可 spawn agent，需移除或明确声明不用于 spawn

**推荐**：P5 时优先评估 Option C（最小改动）；如果审计发现 Option C 的"非标准 file type"在 pro/agents 目录中造成实际混淆，升级到 Option A（删除，重写 3 个 orchestration 文件）。

## Deferred to

**P5（docs window / release prep）**。P1-P4 does NOT touch this — user explicitly scoped it out of Sprint 7 (see original Sprint brief: "spec-code 矛盾 ... 记录到 compliance 文件即可").

## How to apply at runtime until P5 resolution

- **Orchestrator (ROUTER) SHOULD NOT** `Task(narrator)` / `Spawn(narrator)` / `launch narrator subagent` — keep narrator composition inline inside ROUTER's Step 7.5 flow
- **`pro/agents/narrator.md` content is reference material**, not an independent subagent definition; ROUTER may `Read` it at Step 7.5 as a composition guide
- **Information Isolation table** in `pro/{CLAUDE,GEMINI,AGENTS}.md` + root `AGENTS.md` currently lists a NARRATOR row — this should be interpreted as "ROUTER @ Step 7.5 composition step receives X" not a separate agent
- **`narrator-validator` IS a standalone subagent** per `narrator-spec.md §7` — the validator's `pro/agents/narrator-validator.md` file IS spec-compliant and should be spawned/launched as independent subagent. Do not conflate narrator (ROUTER-internal) with narrator-validator (standalone).

## Related artifacts

- `pro/agents/narrator.md` — the file in question
- `pro/agents/narrator-validator.md` — spec-compliant standalone subagent (keep)
- `references/narrator-spec.md §6-§7` — authoritative narrator vs validator distinction
- `references/cortex-spec.md §Execution Model → Deliverable List`
- `docs/architecture/v1.7-spec-map.md §4 §5.1 §6`
- `pro/CLAUDE.md §0.5 §7.5` — current wording references narrator subagent (to be revised in P5)
- `pro/GEMINI.md §0.5 §7.5` — same
- `pro/AGENTS.md §0.5 §7.5` — same

## Also noted during Sprint 7 audit (out of scope, log only)

Scanning `pro/agents/` surfaced two additional files **not in `v1.7-spec-map.md §6 · Create 3 new agent files` list**:

- `pro/agents/concept-lookup.md` — not in spec's "create" list; spec says concept extraction is archiver Phase 2 logic, not a standalone agent (`concept-spec.md §Hebbian Update Algorithm`). However, Step 0.5 in pro/CLAUDE.md references concept-lookup as a Phase 1.5 subagent. May be a similar spec-code mismatch worth re-checking in P5.
- `pro/agents/soul-check.md` — spec labels it "TBD — reuses RETROSPECTIVE's SOUL Health Report" until standalone implementation. Standalone file exists anyway. Worth confirming whether standalone implementation was intended or if this is a drift.

These are NOT the subject of this incident. Separate audit entries may be warranted in P5.
