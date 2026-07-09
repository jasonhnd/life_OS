---
spec_id: maintenance-ledger-spec.v1
description: meta/maintenance-ledger.md 的格式与协议——记录每个维护任务上次运行时间的唯一 vault 文件。每个 scripts/prompts/*.md 任务在完成时盖戳；session 启动时把戳记与声明的节奏对比，最多浮出 3 行过期提示（仅提醒，绝不自动运行）。关闭"节奏规则只存在于纸面、漂移静默累积"的缺口（issue #1 A2）。
status: active
authoritative: true
introduced_in: v1.10.0
referenced_by:
  - agents/retrospective.md (Step 0.5 maintenance-overdue marker + Mode 2 item 7)
  - hosts/CLAUDE.md (§session-start status scan)
  - scripts/prompts/*.md (final "ledger stamp" step in every job)
  - references/model-dispatch-policy.md (cadence column source)
---

# 维护台账规范 v1（Maintenance Ledger Specification v1）

自 v1.8.0 pivot 移除 cron 以来，所有维护均由用户手动调用。没有任何东西记录某任务上次何时运行，也没有任何东西在任务过期时提醒——生产证据：一条">4h → 轻巡查"规则与 7 天以上的空窗并存，一次月度深巡查晚了约 13 天，wiki 索引漂移累积到 +60 条才被巡查发现。本 spec 让陈旧度**在人类必然在场的唯一时刻——session 启动时——可见**，同时不复活 cron、不违背 v1.8.0 的"无自驾维护"立场。

## 文件格式

每个 vault 一个文件：`meta/maintenance-ledger.md`。一张 markdown 表格，每个任务一行，按任务名字母序排序：

```markdown
# Maintenance Ledger

Stamped by each `scripts/prompts/<job>.md` on completion. Read by session start
(retrospective Step 0.5). Cadences per `references/maintenance-ledger-spec.md`.

| job | cadence | last_run |
|-----|---------|----------|
| auditor-mode-2 | 7d | 2026-07-01 |
| backup | 7d | 2026-06-28 |
| wiki-link-audit | 7d | 2026-06-20 |
```

字段规则：

- **job**——prompt 的 basename 去掉 `.md`（如 `wiki-link-audit`）。
- **cadence**——`<N>d`（按天计）、`on-demand` 或 `once` 三者之一。每个任务的权威节奏来自 `references/model-dispatch-policy.md` §"Maintenance job → minimum tier table"；ledger 行复制它，使过期计算只需这一个文件。
- **last_run**——来自真实 `date` 命令的 `YYYY-MM-DD`（禁止编造——与 SOUL 快照同一合约）。

## 盖戳协议（每个任务的最后一步）

每个 `scripts/prompts/*.md` 任务都以 ledger 盖戳步骤收尾：

1. 读 `meta/maintenance-ledger.md`。若缺失，用上文 header 创建、零行。
2. **Upsert 自己的行**——若本任务的行已存在，就地替换；否则按字母序插入。绝不重复某任务的行。
3. 写入 `| <job> | <cadence> | <today> |`。

盖戳是幂等的，代价为一次 Read + 一次 Write。`cadence: once` 或 `on-demand` 的任务同样盖戳——它们的行记录任务运行过，只是永远不会过期。

## Session 启动过期检查（仅提醒）

在 session 启动时（retrospective Mode 0 Step 0.5；也在 Mode 2 Review item 7）：

1. 读 `meta/maintenance-ledger.md`。文件缺失 → 输出 `Maintenance ledger: not yet initialized (jobs stamp it on completion)` 并跳过——不要在读取时创建它。
2. 对每个按天计节奏 `<N>d` 的行：`days_overdue = (today - last_run) - N`。`on-demand` / `once` 节奏的行永不过期。
3. 若存在 `days_overdue > 0`：输出一个 `## Overdue maintenance` 块，**最多 3 行**（HARD CAP），按过期比 `(today - last_run) / N` 降序排列：

   ```
   ⚠️ overdue: wiki-link-audit (12d since last run, cadence 7d)
   ⚠️ overdue: auditor-mode-2 (9d since last run, cadence 7d)
   (+2 more — see meta/maintenance-ledger.md)
   ```

   当过期任务超过 3 个时，第 3 行是 `(+N more …)` 汇总行。
4. 若无任何过期：**沉默**（无块、无"全部新鲜"行——健康路径零噪音）。

**过期 = 仅提醒。绝不从过期检查中自动运行维护任务。**由用户决定调用什么。自动执行会恰好重新引入 v1.8.0 pivot 移除的那种自驾维护。

## 与 v1.10 之前机制的关系

v1.10 之前，retrospective Step 0.5 读的是"10 个维护任务的上次运行时间戳所在的存储位置"——即每个任务的报告路径（如 `meta/eval-history/wiki-link-audit-*.md` 的 mtime），只覆盖恰好写带日期报告的任务，且每次启动需要 N 次 glob。ledger 取代了它：**一个文件、一次 Read、写时维护**——与 v1.9.2 session INDEX 改动相同的"写时优于扫描时"策略。旧的按任务报告路径作为证据保留，但不再是过期检查的真实来源。

## Eval 锚点

`evals/scenarios/v1.10-maintenance-ledger.md`——陈旧 ledger → 出现提醒块（≤3 行）；新鲜 ledger → 不输出任何块。
