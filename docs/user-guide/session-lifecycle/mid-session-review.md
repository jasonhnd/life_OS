# 复盘 · 会话中途回顾

**本地备忘。不推送 GitHub。**

复盘 = Review = Mode 2。由 RETROSPECTIVE 子代理执行，但和上朝（Mode 0）不一样：**只生成晨报，不做全量同步，不做 outbox 合并**。

权威源：`pro/agents/retrospective.md` Mode 2 + `pro/CLAUDE.md` Review trigger。

---

## 触发词

| 语言 | 触发词 |
|------|-------|
| 英文 | `review` / `morning court` |
| 中文 | `复盘` / `早朝` |
| 日文 | `振り返り` / `レビュー` |

用户说任一个 → ROUTER 输出：

```
Line 1: "🌅 开始 review — 仅晨报..."
Line 2: Launch(retrospective) as subagent in Mode 2
```

---

## Mode 2 vs Mode 0 对比

| 行为 | Mode 0（上朝） | Mode 2（复盘） |
|------|--------------|--------------|
| 主题解析 | ✅ 有 | ❌ 沿用当前 |
| 目录检测 | ✅ 有 | ❌ 无 |
| 数据层检查 | ✅ 有 | ❌ 无 |
| 全量 PULL | ✅ 有 | ❌ 无 |
| Outbox 合并 | ✅ 有 | ❌ 无 |
| 版本检查 | ✅ 有 | ❌ 无 |
| 项目绑定 | ✅ 有 | 沿用 |
| Context 加载 | ✅ 深度 | ✅ 读现状 |
| Strategic Map 编译 | ✅ 重新编译 | ❌ 读已有 |
| DREAM 报告展示 | ✅ 有 | ❌ 无 |
| Wiki 健康检查 | ✅ 有 | ❌ 无 |
| 晨报输出 | ✅ 完整 | ✅ 精简 |

**核心差异**：Mode 2 不 touch backend，不 touch git，不 touch 版本，不 touch 同步。只读现状、算指标、出晨报。

---

## Mode 2 的数据源

```
1. 读 ~/second-brain/_meta/STATUS.md — 全局状态
2. 遍历 ~/second-brain/projects/*/tasks/ — 算完成率
3. 读 ~/second-brain/areas/*/goals.md — 目标进度
4. 读 ~/second-brain/_meta/journal/ — 最近 log
5. 读 ~/second-brain/projects/*/journal/ — 项目级 log
6. 读 _meta/STRATEGIC-MAP.md — 战略线健康趋势（如存在）
```

注意：**读已有的 STRATEGIC-MAP.md，不重新编译**。Mode 0 会 recompile；Mode 2 不会。

---

## Decision Tracking

Mode 2 要检查 `projects/*/decisions/`，找 front matter `status: pending` 且创建时间 >30 天的决策。这些是"pending backfill"——需要用户回填"后来怎样了"。

---

## Metrics Dashboard

**Core 3 指标**（每次都跑）：
- DTR — Decision Throughput Rate
- ACR — Action Completion Rate
- OFR — Outcome Feedback Rate

**Extended 4 指标**（仅周/月级）：
- DQT — Decision Quality Trend
- MRI — Multi-perspective Rigor Index
- DCE — Domain Contribution Evenness
- PIS — Pattern-Implementation Sync

---

## Mode 2 输出格式

```
🌅 Session Briefing · [Period]

📊 Overview: [一句话]

Area Status: (按 areas/ 下每个 area 报告)
[Area name]: [Status]
...

🗺️ Strategic Health (如 STRATEGIC-MAP.md 存在):
[emoji] [line-name] ([archetype]): [趋势 vs 上次 review]
  🚧 Bottleneck: [project] — [原因]（如有）
  🔴 Decay: [project] — [N 天未动]（如有）

📈 Decision Dashboard:
DTR [====------] X/week    [GREEN/YELLOW/RED]
ACR [=======---] X%        [GREEN/YELLOW/RED]
OFR [======----] X%        [GREEN/YELLOW/RED]

⏰ Decisions Pending Backfill:
- [Decision title] — [Date] — 后来怎样了？

🔴 Immediate Attention: [...]
🟡 This Period's Focus: [...]
💡 Suggestions: [...]
```

**比 Mode 0 晨报少**：
- 没有 Pre-Session Preparation（没同步）
- 没有 SOUL Health Report（不算 delta）
- 没有 DREAM Auto-Triggers（没有新 dream）
- 没有 Today's Focus（period 是用户指定的范围，不是"今天"）
- 没有 Wiki 健康
- 没有版本信息

---

## 什么时候用 Review vs Start Session

### 用 Start Session（上朝）

- 新一天开始
- 换了设备（桌面 → 手机）
- 离开一段时间回来
- 做了离线会话回来了（需要合并 outbox）
- 不知道用哪个的时候默认这个

### 用 Review（复盘）

- 已经上过朝了，同一会话中想再看一次状态
- 想要 period view（本周/本月进度）
- 想要指标仪表盘但不想重新同步
- 想要 pending decisions 列表来回填
- 快节奏，不想等同步

### 真实场景

- **早上打开** → 上朝。拿新鲜数据，看 SOUL 演化，看 DREAM 触发。
- **中午查进度** → 复盘。看本周 DTR/ACR/OFR，看 area status。
- **刚做完一个决策想看累积影响** → 复盘。
- **做了 3 小时想看还剩啥** → 复盘。
- **离线 half day 回来** → 上朝。需要合并 outbox。

---

## Anti-patterns

`retrospective.md` Mode 2 明确写了几条反模式：

- 不要对每个 area 都说"progressing normally"。不是洞察，是填空。
- 月度或更长的 review 必须包含趋势对比。没趋势数据 = 没信号。
- Mode 1（Housekeeping）必须快 — 不做深度分析。Mode 2 也偏快。深度交给 Mode 0。

---

## 实现细节

### Mode 2 是否写 snapshot

**不写**。SOUL snapshot 只在 archiver Phase 2 末尾 dump。Review 不 touch SOUL，也不 dump snapshot。

### Mode 2 是否触发 AUDITOR

不自动触发。AUDITOR 只在：
- 每个 Draft-Review-Execute 流程后自动跑
- lint-state >4h 时由 retrospective Mode 0/1 触发轻量巡查
- session end 时检查非法状态转换

Mode 2 不属于以上任一。

### Mode 2 期间用户做决策

Mode 2 不阻塞。用户复盘完可以继续做任何事。ROUTER 接手正常工作流。

### Mode 2 的文件写入

**零文件写入**。纯读。这是和 Mode 0 最大的区别 — Mode 0 要写 `_meta/STRATEGIC-MAP.md`、`wiki/INDEX.md`、`_meta/sync-log.md`，Mode 2 都不写。

---

## 为什么要分 Mode 0 和 Mode 2

早期版本只有一个 start session，结果：

- 用户一个会话里想查 3 次状态 → 每次都触发全量同步 → 浪费
- 用户手机上已经同步过了 → 桌面再上朝又同步一次 → 冗余
- 用户想要快速查"本周完成率" → 被迫等完整 18 步

解法：分成 Mode 0（完整启动）+ Mode 2（仅报告）。用户根据需要选。

### Mode 1 是什么

Mode 1 = Housekeeping。ROUTER 在**用户没说启动词**的普通会话第一条消息时，**自动** 并行启动 retrospective 做背景准备。

Mode 1 的输出给 ROUTER 用，**不直接给用户看**。ROUTER 把 Mode 1 的结果组织进第一条回应里。

| Mode | 触发 | 目标读者 | 输出 |
|------|------|---------|------|
| 0 | 用户说启动词 | 用户 | 完整晨报 |
| 1 | 普通消息自动 | ROUTER | Pre-Session Preparation |
| 2 | 用户说复盘词 | 用户 | 精简晨报 |

三者都是 retrospective 的不同 mode，读同一个 agent 定义文件。
