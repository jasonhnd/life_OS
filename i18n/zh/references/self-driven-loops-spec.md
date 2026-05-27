---
spec_id: self-driven-loops-spec.v1
description: 基于 ScheduleWakeup 的自驱命令循环规范。定义 270s 间隔理由（Anthropic prompt cache 窗口）、12-tick 硬上限（60 分钟）、退出条件、host 兼容性（仅 Claude Code）、不支持 host 的降级路径。模式借鉴自 tinyhumansai/openhuman `.claude/commands/ship-and-babysit.md`。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, .claude/commands/ship-and-babysit.md (ScheduleWakeup 270s + 12 tick 模式)
introduced_in: v1.8.7
referenced_by:
  - .claude/commands/verify-release-and-watch.md
  - .claude/commands/notion-sync-and-watch.md
  - SKILL.md (Self-driven loops 章节)
---

# 自驱循环规范 v1

slash 命令使用 `ScheduleWakeup` 自调步骤进行迭代检查（轮询 → 修复 → 复查）的规范，无需用户介入直到达到终态或硬上限。

## 何时使用自驱循环

自驱循环适合当**全部**满足：

1. **任务有清楚的终态**（如"所有 9 个 verify-release check PASS"、"所有 Notion 项已同步"）。模糊的"永远监控"不是有效用例
2. **每次迭代廉价**（一两个工具调用 + 简短 LLM 推理，不是完整 subagent 启动）
3. **外部状态会在迭代间变化**（CI 完成、GitHub Release publish、Notion sync 完成、用户推了修复）
4. **用户显式调用了循环**（如键入 `/verify-release-and-watch v1.8.7`）—— 永不从另一个命令自动调用自驱循环

不适合用例（**不要**为以下场景建自驱循环）：

- ❌ 纯监控无明确退出（如"永远看 queue"）
- ❌ 中途需要用户输入的任务（用常规交互命令）
- ❌ 每次迭代昂贵（重 LLM 工作）的任务 —— 更适合做成一次性命令
- ❌ 类 cron 定时任务（lifeos 在 v1.8.0 弃用 cron；不要重引入）

## 间隔选 270s（硬性）

每次自驱循环内的 `ScheduleWakeup` 调用都用 `delaySeconds: 270`。理由（来自 Anthropic Claude Code 行为）：

- Anthropic prompt cache TTL 是 **5 分钟（300s）**
- 睡过 300s 意味着下次唤醒读完整对话 context **没命中缓存** —— 更慢更贵
- 270s 留在缓存窗口 **内**，留 30s 安全余量
- 别把它当 "5 分钟"或其他整分钟数 —— 270s 是缓存窗优化，不是日历间隔

**例外**（仅当有正当理由用更长延迟）：

- 外部状态变化频率明确长于 5 分钟（如等 GitHub Release CDN 传播约 10 分钟）：用 600s，接受缓存丢失
- 空闲 fallback 心跳（没特定信号要看）：用 1200-1800s，接受缓存丢失换不烧 context

300 到 1200s 之间是反优化 —— 付了缓存丢失成本却没摊薄。

## 硬上限：12 ticks（60 分钟）

每个自驱循环必须跟踪 `tickCount`（每次循环进入都递增，无论是干活还是只等待）。12 ticks 之后：

- **停止循环**（**不**再调 ScheduleWakeup）
- **输出状态快照**给用户：当前状态、剩什么待办、为什么超时
- **问用户**怎么办（重跑？放弃？升级？）

60 分钟上限反映了：如果外部状态一小时还没到终态，肯定有问题（CI 卡死 / Release 卡 Draft / Notion 授权过期），需要人眼。

`tickCount` 必须每次都在 `ScheduleWakeup` `reason` 字段可见（如 `"tick 5/12: waiting for GitHub Release publish"`），跨 tick 可恢复不漂移。

## 退出条件

每个自驱循环定义自己的退出条件。常见模式：

| 模式 | 例 |
|------|----|
| 所有检查通过 | "全部 9 个 verify-release check PASS" → 退出 |
| 空队列 | "Notion sync 项队列空" → 退出 |
| 用户解决 | "用户手动完成了阻塞项" → 退出 |
| 硬上限 | "tickCount > 12" → 带状态快照退出 |

允许混合退出条件，但每个命令的 spec 必须明确列举。

退出条件成立时：
- **不**调 `ScheduleWakeup`
- 输出最终一行总结含任何 URL / 工件路径
- 对话自然结束 —— 用户看到最终结果

## Host 兼容性（仅 Claude Code）

`ScheduleWakeup` 是 Claude Code 特定工具。其他 lifeos 支持的 host（Gemini CLI / OpenAI Codex CLI）截至 v1.8.7 **没有**等价能力。

每个自驱循环命令必须声明：

```yaml
---
description: <one-liner>
argument-hint: <args>
requires_host: claude-code
allowed-tools:
  - Bash
  - Read
  - Edit
  - ScheduleWakeup
---
```

在非 Claude Code host 调用时：

1. ROUTER 必须检测 host（用 SKILL.md 既有 host 检测）
2. 输出单条错误：
   ```
   ⚠️ `/<command>` 需要 Claude Code（用 ScheduleWakeup 实现自驱循环）。
      你在 <host>。改跑 `/<base-command>`（手动重跑）。
   ```
3. **不**执行循环体

手动 fallback 路径：每个自驱循环都应该有非-watch 同伴命令（如 `/verify-release` 是 `/verify-release-and-watch` 的非 watch 版本）。非 watch 版本任何 host 都能跑，用户手动重跑。

## 必需的命令结构

自驱循环命令文件（`.claude/commands/<name>-and-watch.md`）必须含以下章节：

```markdown
---
description: <one-liner>
argument-hint: <args>
requires_host: claude-code
allowed-tools: [Bash, Read, Edit, ScheduleWakeup, ...]
---

# /<command>-and-watch

<目的段：本循环达成什么、退出在什么终态>

## 输入

- `$ARGUMENTS`（可选/必需）—— 描述

## 循环体（单 tick）

1. **读 tickCount** —— 从前次 ScheduleWakeup reason 提取，否则 1
2. **检查退出条件** —— 退出则输出最终总结并 STOP（不调 ScheduleWakeup）
3. **执行迭代工作** —— 跑检查、修发现的问题
4. **决定下一状态** —— 退出 / 继续 / 撞硬上限
5. **调步**：
   - 退出 → 停
   - 撞硬上限（tickCount ≥ 12）→ 输出状态快照、问用户、STOP
   - 否则 → 调 `ScheduleWakeup({delaySeconds: 270, prompt: "/<command>-and-watch <args>", reason: "tick <N+1>/12: <剩什么>"})`

## 退出条件（列举）

- 所有检查 PASS → 带链接退出
- 硬上限 → 带快照退出
- 用户取消信号 → 退出
- 关键错误 → 带错误退出（不重试）

## 失败处理

- <命令特定失败模式与恢复>

## Host 兼容性

非 Claude Code host：按 spec 报错，指向 `/<base-command>` 手动重跑。
```

## Audit trail

自驱循环每次迭代**应**写 `meta/runtime/<sid>/<command>-tick-<N>.md`，含：

- tickCount（当前）
- 时间戳
- 跑的检查 + 结果
- 做的决策（继续 / 退出 / 修了哪个）
- 下一动作（睡多久 / 最终退出）

audit trail 允许事后重构循环用了 N tick 的原因，或为何中途退出。

## 引用

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.2 B4
- 模式来源：`tinyhumansai/openhuman` `.claude/commands/ship-and-babysit.md`（Phase 4 babysit 循环）
- 配套：`SKILL.md` "Self-driven loops with ScheduleWakeup" 章节
