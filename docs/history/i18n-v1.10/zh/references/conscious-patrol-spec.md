---
spec_id: conscious-patrol-spec.v1
description: "lifeos 的 Conscious Patrol —— OpenHuman Subconscious Loop 的路径 D 适配。不做 idle autonomous daemon；改做 session-start user-in-loop checkpoint。retrospective Mode 0 读 system tasks 列表（lifeos 默认）+ user tasks（second-brain HEARTBEAT.md），对当前 workspace 评估每个，向用户报告推荐。用户显式批准每个 act/skip/escalate。与 v1.8.0 cron 退役协调：本方案非倒退，因为用户始终在 loop 内。"
status: active
authoritative: true
source_attribution: "tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/subconscious.md (idle autonomous Subconscious Loop)。lifeos 按 RFC v1.8.7 DR-11 选路径 D（Conscious Patrol —— user-in-loop）。"
introduced_in: v1.8.7（2026-05-26 加入，按 DR-11）
referenced_by:
  - SKILL.md (E10 HARD RULE)
  - agents/retrospective.md (Mode 0 系统化 Conscious Patrol)
  - agents/auditor.md (Mode 8 patrol 合规)
  - references/status-line-spec.md（每个 patrol task 输出 status line）
---

# Conscious Patrol 规范 v1

lifeos 对 OpenHuman Subconscious Loop 的适配。**关键命名区分**：

- **OpenHuman Subconscious** = idle 线程，autonomous daemon，用户不在也跑，local model 自决 act/skip/escalate
- **lifeos Conscious Patrol** = session-start checkpoint，user-in-loop，ROUTER 推荐 + 用户决策，无 daemon

这是 v1.8.7 RFC §1.3 E10 分析的路径 D。选路径 D 是因为 lifeos 是 md-only skill（无 daemon 层）+ v1.8.0 明确退役了 cron 式自治。

## 为什么是 "Conscious" 而非 "Subconscious"

| 属性 | OpenHuman Subconscious | lifeos Conscious Patrol |
|------|----------------------|------------------------|
| 触发 | 周期 heartbeat tick（每 N 分钟） | retrospective Mode 0（session 开始） |
| 意识 | 跑时用户不察觉 | 用户显式开启了 session |
| 决策权 | local model autonomous | ROUTER 推荐，用户决策 |
| 写动作 | 默认自动执行（除非未经请求） | 所有 act 都需用户显式 OK |
| 失败模式 | 可能静默数据丢失（cron 式） | 用户在屏幕前看到每个 error |
| 架构载体 | Tauri daemon 进程 | retrospective subagent 运行 |

命名诚实很重要：把 lifeos 路径 D 叫 "Subconscious" 会误导用户期待并不存在的 idle 自治。**Conscious Patrol** 准确描述实际发生的：用户在场，ROUTER 巡查，用户决策。

## 为什么这不是 v1.8.0 cron 的倒退

v1.8.0 退役了 `setup-cron.sh` + 所有 launchd plists + 5 个在 cron 上下文跑 LLM 的 Python tools。退役理由：

1. "不可靠" —— cron 静默失败，无 surfacing
2. "不可见" —— 输出到用户不读的日志文件
3. "静默数据丢失" —— cron 上下文跑 LLM 的 Python tools 产生错误输出覆盖好数据

**Conscious Patrol 无一违反**：

1. **可靠** —— 作为 retrospective Mode 0 的一部分运行，每次 session 开始都跑；若失败用户在 briefing 中看到失败
2. **可见** —— 输出就是早朝 briefing 本身，session 开始用户最先看到的最显眼内容
3. **无静默数据丢失** —— 每个 act 需用户 OK；无显式确认不写任何东西

v1.8.0 退役对当时的技术（Python tools + 系统 cron）来说是正确的。v1.8.7 Conscious Patrol 用根本不同的机制（LLM-driven retrospective + 用户审批）。路径 D **不是**路径 C/F（外部 cron 触发 Claude Code headless）—— 那些会重新引入 v1.8.0 的关切。路径 D 留在 lifeos 一直主张的 user-in-loop 模型里。

## System tasks（默认 seeded，不能删只能 disable）

retrospective Mode 0 把以下作为默认 patrol items 每次 session 跑：

### lifeos-001 · Maintenance overdue 检查

- **来源**：lifeos 已在 v1.8.0 实施（`scripts/prompts/auditor-mode-2.md` + 10 个 maintenance jobs）
- **检查内容**：`reindex / daily-briefing / backup / spec-compliance / wiki-decay / archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency` 的时间戳 —— 标记 overdue
- **输出**：status line + overdue 项数量
- **用户决策**：挑本 session 跑哪些 overdue jobs

### lifeos-002 · Review queue overdue

- **来源**：lifeos R-1.8.0-013 review-queue.md prompt
- **检查内容**：扫 review queue 找 P0/P1/P2 在预期窗口内未处理
- **输出**：status line + N P0 / M P1 / K P2 计数
- **用户决策**：现在走 queue 或延后

### lifeos-003 · SOUL drift 检查

- **来源**：lifeos advisor-monthly.md prompt（既有）
- **检查内容**：SOUL.md 信心度漂移 / 未挑战的 dimensions / 矛盾证据
- **输出**：status line + N 个 dimensions 标记
- **用户决策**：现在 review 或安排月度 slot

### lifeos-004 · Wiki decay 扫描

- **来源**：lifeos wiki-decay.md prompt（既有）
- **检查内容**：`last_reviewed` 陈旧 / 被近期 session 矛盾的 wiki 条目
- **输出**：status line + N 个条目标记
- **用户决策**：确认 decay、退役条目，或刷新

### lifeos-005 · Strategic 一致性

- **来源**：lifeos strategic-consistency.md prompt（既有）
- **检查内容**：跨项目战略流冲突 / SOUL ↔ flow 错位
- **输出**：status line + N 个冲突
- **用户决策**：现在处理或留待下次规划 session

### lifeos-006 · Compliance Watch

- **来源**：lifeos AUDITOR Mode 3（既有）
- **检查内容**：30 天滚动 violation 计数；升级阈值（同类 ≥3 → hook 加严；≥5 → briefing 顶部；≥10 → AUDITOR Mode 3 每次 Start Session 都跑）
- **输出**：status line + violation 摘要
- **用户决策**：review violations.md、调整行为，或确认

### lifeos-007 · Gotchas review（v1.8.7 新）

- **来源**：lifeos v1.8.7 C6 —— `gotchas.md`
- **检查内容**：引用近 7 天碰过的文件/代码的 gotcha（相关性信号）；已解决的 gotcha（代码修了但 gotcha 还列着）
- **输出**：status line + N 个相关 gotcha 浮现
- **用户决策**：ROUTER 扫当前任务的相关 gotcha；用户确认 / 撤销

## User tasks（HEARTBEAT.md 机制）

用户在 second-brain 根可创建 `HEARTBEAT.md`：

```markdown
# Patrol Items

## daily
- 检查未解决决定超过 14 天
- 浮现近 3 天 mood-tagged 日志

## weekly
- review 标 "review-needed" 的 wiki 条目
- 跨核项目优先级 vs 季度 OKR

## monthly
- 审计金融决策类别
- review SOUL.md "应该是的我" vs "现在的我" delta
```

retrospective Mode 0 读 `HEARTBEAT.md`（如存在），按 frequency-since-last-run 过滤，把匹配项加入 patrol 清单。每个 user task 按标准契约发 status line。

### HEARTBEAT.md frontmatter（可选）

```yaml
---
patrol_enabled: true
frequency_default: weekly
disabled_system_tasks: []   # 例 ["lifeos-005"] 跳过 strategic 一致性
---
```

`disabled_system_tasks` 让用户 opt-out 特定默认（不能删，但能 disable，按 OpenHuman 模式）。

## Tick 语义（lifeos vs OpenHuman）

OpenHuman 不管用户活动每 N 分钟跑 tick。lifeos 仅在 retrospective Mode 0 触发时跑"tick"（每次 session 开始）。频率比较：

| 频率 | OpenHuman | lifeos Conscious Patrol |
|------|-----------|------------------------|
| 用户一天开多次 session | Patrol N 次/天（用户开 N session） | 同 —— N 次/天 |
| 用户度假（2 周无 session） | OpenHuman 2 周每 N 分钟 tick（336+ tick） | lifeos 不 tick —— patrol 在 session 恢复时跑 |
| 长期问题（如 90 天 SOUL drift） | OpenHuman 逐步抓 drift | lifeos 在下次 session 开始抓 drift（非实时关切可接受） |

**权衡**：lifeos 牺牲实时检测换 user-in-loop 安全。对 lifeos 领域（个人决策引擎而非运维监控）来说，权衡正确。

## Status line 集成（E9）

每个 patrol task 按 `references/status-line-spec.md` 输出 status line：

```
🔍 evaluating · retrospective · Conscious Patrol —— 检查 lifeos-001 maintenance overdue
⏭️ skipped · retrospective · lifeos-001 —— 全 10 jobs 在窗口内
🔍 evaluating · retrospective · lifeos-002 review queue
🟡 awaiting_user · retrospective · lifeos-002 —— 3 P0 / 1 P1 overdue，跑 /process-queue？
✅ acted · retrospective · lifeos-003 SOUL drift —— 1 dimension 标记，已浮现到 briefing
🟢 silent_pass · retrospective · lifeos-004 / lifeos-005 / lifeos-006 / lifeos-007 —— 干净
```

每行可被 AUDITOR Mode 8 grep。

## 决策流（路径 D 核心）

对每个 patrol task，retrospective Mode 0 发以下之一：

| 决策 | 发生什么 |
|------|---------|
| `silent_pass` | Task 跑了，无相关内容，不需 surfacing（高频低噪场景） |
| `skipped` | Task 跑了，无可操作项，briefing 简提（低频信息） |
| `awaiting_user` | Task 找到可操作项，ROUTER 报告 + 问用户。用户响应："yes，跑 X" / "skip" / "later" |

**无静默 act**。每个 act 都是用户显式。这是区分路径 D 与路径 A-F 替代方案的 lifeos 核心承诺。

## AUDITOR Mode 8 patrol 合规（status line 之外）

Mode 8 额外验证 Conscious Patrol 行为：

| 检查 | 描述 | 失败 class |
|------|------|-----------|
| M8-7 | 每次 session-start retrospective Mode 0 含 patrol 段（briefing 中 `## Conscious Patrol`） | `F4 SCOPE_FAILURE: retrospective Mode 0 缺 patrol 段` |
| M8-8 | 每个 lifeos-001 到 lifeos-007 system task 发 status line（或按 HEARTBEAT.md 显式标 disabled） | `F3 SCHEMA_FAILURE: system task <id> 输出缺失` |
| M8-9 | 未检测到 "auto-act"（每个 act 前必有 `awaiting_user` 行） | `F10 RESPONSIBILITY_FAILURE: 静默 act 绕过用户审批` |
| M8-10 | HEARTBEAT.md 的 user tasks 实际扫描（audit trail 证据） | `F8 SILENT_FAILURE: HEARTBEAT.md 存在但 user tasks 未浮现` |

## v1.8.7 **不**做什么（路径 D 范围诚实）

明确 Conscious Patrol 不是什么：

- ❌ 无后台 daemon / cron / launchd
- ❌ 无外部触发机制（用户 OS cron / GitHub Actions 等）—— 那是路径 C/F 领域，延后
- ❌ 无 autonomous act（每个 act 需用户显式 OK）
- ❌ 无实时检测（仅 session-start patrol；用户离开期 blind）
- ❌ 无 headless Claude Code 调用
- ❌ 无 `claude --headless -p "..."` 集成

v1.8.7 **做**：
- ✅ 系统化 retrospective Mode 0 patrol 为显式 7 system tasks + user-defined HEARTBEAT.md
- ✅ 集成 E9 status line 统一可观测
- ✅ 通过 AUDITOR Mode 8 M8-9 强制 user-in-loop
- ✅ 与 v1.8.0 cron 退役协调（本 spec 显式 "why not regression" 段）

## 未来方向（v1.8.7 之后）

如用户实际需要实时 patrol（vacation 模式检测 / 隔夜 SOUL drift），下一步选项：

- **v1.9 / v2.0 路径 C**：文档化 external-cron 模板（launchd plist / GitHub Actions workflow）给想要的用户。lifeos 留作 spec 提供者，不打包
- **v2.0 路径 F**：用户 second-brain repo 承载 cron 逻辑（用户 repo 中的 GitHub Actions）。lifeos 提供 workflow 模板

这些延后 —— v1.8.7 路径 D 明确范围为仅 user-in-loop。

## 引用

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.9 E10 路径 D + DR-11
- 模式来源：`tinyhumansai/openhuman` `gitbooks/features/subconscious.md`（idle autonomous Subconscious Loop，基于 daemon）
- 配套：`references/status-line-spec.md`（每 patrol task 用 8 enum status）
- 配套：`agents/retrospective.md` Mode 0（Conscious Patrol 运行处）
- 配套：`agents/auditor.md` Mode 8（验证）
- 相关但**不同**：lifeos v1.8.0 cron 退役（`hosts/CLAUDE.md` §"Mode 1 · Business session" —— 解释为何 daemon 式自治被拒）
