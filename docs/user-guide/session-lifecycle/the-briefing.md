# 晨报 · 各区块详解

**本地备忘。不推送 GitHub。**

晨报 = 上朝 18 步结束后的最终输出。由 RETROSPECTIVE Mode 0 在 Step 18 生成。

设计原则（v1.6.2 开始）：**SOUL Health Report 和 DREAM Auto-Triggers 固定在顶部**。不是可选的脚注。每次都显示（或显式标"空"）。

权威源：`pro/agents/retrospective.md` Mode 0 Output Format。

---

## 区块顺序（固定）

```
1. 📋 Pre-Session Preparation
2. 🔮 SOUL Health Report         ← 固定，永远第一
3. 💤 DREAM Auto-Triggers        ← 固定，永远第二
4. 🗺️ Strategic Overview
5. ⚡ Today's Focus
6. 📈 Metrics dashboard
7. ⏰ Pending decisions
8. 🔴🟡💡 Immediate / Priorities / Suggestions
```

1、2、3 不能颠倒。不能省略。可以标"空"。

---

## 区块 1 · Pre-Session Preparation

```
📋 Pre-Session Preparation:
- 📂 Session Scope: [projects/xxx or areas/xxx]
- 💾 Storage: [GitHub(primary) + Notion(sync)]
- 🔄 Sync: [Pulled N changes from Notion, M from GDrive / no changes]
- Platform: [name] | Model: [name]
- 🏛️ Life OS: v[local] | Latest: v[remote]
  [✅ Up to date / ⬆️ Update available — 命令]
- Project Status: [summary]
- Behavior Profile: [loaded / not established]
```

字段含义：

- **Session Scope**：本次会话绑定的项目。HARD RULE。所有读写都限制在此 scope。
- **Storage**：primary + sync backend。primary 是权威源，sync 是镜像。
- **Sync**：这次上朝拉了几条变更。"no changes" 是正常的，不是失败。
- **Platform**：Claude Code / Gemini / Codex。影响 update 命令。
- **Life OS version**：本地 vs 远程。如果远程大于本地 → 提示 update。
- **Behavior Profile**：`user-patterns.md` 是否存在且已加载。

---

## 区块 2 · 🔮 SOUL Health Report（固定，顶部）

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 SOUL Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Current Profile:
   Active dimensions (confidence > 0.5):
   · [Dimension A] 0.8 🟢 ↗ (+2 evidence since last session)
   · [Dimension B] 0.6 🟢 → (no change)
   · 🌟 [Dimension C] 0.72 newly promoted to core

🌱 New dimensions (auto-detected, no delta):
   · [Dimension D] 0.3 — What IS: [观察] | What SHOULD BE: (等你填)

🗑️ Removed dimensions:
   · [Dimension E]

⚠️ Demoted / ❗ Conflict zone:
   · ⚠️ [Dimension F] demoted from core
   · ❗ [Dimension X] conflict zone — last 3 challenges > last 3 evidence

💤 Dormant dimensions (>30 days since last_validated):
   · [Dimension Y]

📈 Trajectory: evidence +N, challenges +M, new +K, net confidence movement {±X.XX}
```

### 字段详解

**Active dimensions**：confidence > 0.5 的"现役" dimension。每条包含：
- 名字
- 当前 confidence（0.0–1.0）
- 🟢 (core, ≥0.7) / 🟡 (medium, 0.5–0.7) / 🔴 (low)
- 趋势箭头（见下）
- delta 注释（"+2 evidence since last session"）

**趋势箭头**（从 `confidence_Δ` 推导）：
- `↗` = 上升。`confidence_Δ > +0.05`
- `↘` = 下降。`confidence_Δ < −0.05`
- `→` = 稳定。`|Δ| ≤ 0.05`

**特殊状态标记**：
- `🌟` = 新晋核心。本次跨过 0.7 向上。
- `⚠️` = 从核心降级。本次跨过 0.7 向下。
- `💤` = 休眠。`last_validated` >30 天，超过一个月没被验证。
- `❗` = 冲突区。最近 3 次 challenges > 最近 3 次 evidence。证据在反转。
- `🌱` = 新 dimension。自动写入，confidence 0.3，等用户填 What SHOULD BE。
- `🗑️` = 用户删了。上次 snapshot 有，当前没有。

**Trajectory**：本次会话对 SOUL 整体的净变动。不是单个 dimension，是聚合。

### 数据来源

严格对应 retrospective.md Step 11 的 6 个子步骤：
- 11.1 当前 SOUL
- 11.2 最新 snapshot（`_meta/snapshots/soul/`）
- 11.3 delta 计算
- 11.4 箭头推导
- 11.5 特殊状态
- 11.6 trajectory

### Edge cases

如果满足下列情况，晨报底部加脚注：

- **首次会话，无 snapshot** → "首次会话 — 无趋势数据"。所有 dimension 标 🌱。
- **snapshot 损坏** → "⚠️ 趋势对比不可用（上次 snapshot 无法读取）"。退化为"仅当前状态"。
- **snapshot >24 小时** → "趋势相对于 {YYYY-MM-DD HH:MM}"。仍用，但标注。

### 为什么固定在顶部

v1.6.2 之前 SOUL 是被忽略的。写入了但用户看不到。每次会话都在重新累积，但视觉上从未出现。**固定顶部 = 承诺每次会话都让用户看到 SOUL 演化**。

---

## 区块 3 · 💤 DREAM Auto-Triggers（固定，第二位）

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💤 DREAM Auto-Triggers (from last session)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Triggered Actions (auto-applied):
   [From DREAM action #1: new project relationship]
   · STRATEGIC-MAP updated: [project-A] →(cognition)→ [project-B]

   [From DREAM action #2: behavior-driving_force mismatch]
   · ADVISOR will flag this session: "你说[driving_force]但最近 5 次会话都在做..."

   [From DREAM action #4: dormant SOUL dimension]
   · ⚠️ [Dimension] 已休眠 30+ 天

   [From DREAM action #6: decision fatigue]
   · 💡 建议：今天不做重大决策 — 最近 3 天已做 N 个决策

   [From DREAM action #8: stale commitments]
   · 🔄 Resurface: 30 天前你说"我会 [X]" — 后来呢？

   [From DREAM action #10: repeated decisions]
   · 🤔 你已决定 [X] 3+ 次 — 是不是有什么让你无法 commit？

(如无触发：No actions triggered from last session's dream.)
```

### 10 个触发器

DREAM REM 阶段在 archiver 里会评估 10 个触发模式。任何命中都写入 `triggered_actions` YAML。下次上朝 retrospective Step 16 读出来，显示在这个区块。

| # | 触发器 | 硬阈值 |
|---|--------|--------|
| 1 | new-project-relationship | 单次会话里 ≥2 次"A→B"表述 |
| 2 | behavior-mismatch-driving-force | REVIEWER 标出 ≥1 次决策与 driving_force 矛盾 |
| 3 | wiki-contradicted | 本次结论与已有 wiki（confidence≥0.5）直接矛盾 |
| 4 | soul-dormant-30d | SOUL dimension >30 天未验证 |
| 5 | cross-project-cognition-unused | cognition 流 A→B 的下游 5 个决策都没引用上游 wiki |
| 6 | decision-fatigue | 24h 内 ≥5 个决策 AND 后半段平均分 ≤ 前半段-2 |
| 7 | value-drift | 14 天内 `challenges_Δ × 2 > evidence_Δ` AND confidence 下降 >30% |
| 8 | stale-commitment | 30 天前说"我会 X"但至今无对应动作 |
| 9 | emotional-decision | ADVISOR 标了高情绪 AND REVIEWER 建议冷静期 AND 决策照做了 |
| 10 | repeated-decisions | 本次决策与过去 30 天 ≥2 个决策主题重合 >70% |

### Soft mode

硬阈值没达 → LLM 仍可基于定性信号触发。会标 `mode: soft` + `auditor_review: true`。AUDITOR 下次巡查会复查是否误报。

### 防刷屏

同一 trigger 类型 24h 内已触发过 → 抑制。

### 为什么固定在顶部

和 SOUL 同理。DREAM 花了整个 Phase 3 做深度扫描，如果结果埋在晨报中部，用户根本看不到。**顶部 = 强制可见**。

---

## 区块 4 · 🗺️ Strategic Overview

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗺️ Strategic Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[emoji] [line-name]                    [archetype indicator]
   Window: [deadline] ([N weeks]) | Driving: [driving_force]
   [project]   [role]   [status indicator]
   Narrative: [在发生什么 + 意味着什么]
   → Action: [今日含义]
```

只有 `_meta/strategic-lines.md` 存在才显示。否则回退到扁平 Area status 列表。

### archetype indicator

不用数字打分。用原型描述：
- "healthy flow"
- "bottleneck detected"
- "decay"
- "dormant"
- "disconnected"

见 `references/strategic-map-spec.md` 完整定义。

### role

每个项目在这条 line 里扮演什么角色：
- `critical-path` — 关键路径
- `support` — 支持
- `experiment` — 实验
- `dormant` — 休眠
- 等等

critical-path 排在前面。

### Narrative + Action

两段式：先描述（在发生什么），再解读（今日该做什么）。不要只给数据。

---

## 区块 5 · ⚡ Today's Focus

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Today's Focus
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 [最高杠杆]: [原因] | Effort: [时间] | Cost of inaction: [不做会怎样]
🥈 [值得关注]: [原因]
🟢 Safe to ignore: [列表]
❓ Decisions needed: [列表]
```

### 四级分层

- **🥇 金牌** — 最高杠杆。一件事做了，其他都变容易。每次只能有一个。
- **🥈 银牌** — 值得关注。不做不会爆，做了有加成。
- **🟢 可忽略** — 明知有在做，但今日不值得注意。
- **❓ 需决策** — 卡在这里，今日必须给出方向。

每项必须有：
- 原因（为什么是这个优先级）
- Effort（需要多久）— 仅 🥇 必填
- Cost of inaction（不做会怎样）— 仅 🥇 必填

不能只给列表不给原因。

---

## 区块 6 · 📈 Metrics Dashboard

仅当有历史数据时显示。否则跳过。

```
📈 Metrics dashboard:
DTR [====------] X/week    [GREEN/YELLOW/RED]
ACR [=======---] X%        [GREEN/YELLOW/RED]
OFR [======----] X%        [GREEN/YELLOW/RED]
```

核心 3 指标（每次都显示，如有数据）：
- **DTR** — Decision Throughput Rate（决策吞吐率）
- **ACR** — Action Completion Rate（行动完成率）
- **OFR** — Outcome Feedback Rate（结果反馈率）

扩展 4 指标（每周或更长周期）：
- **DQT** — Decision Quality Trend
- **MRI** — Multi-perspective Rigor Index
- **DCE** — Domain Contribution Evenness
- **PIS** — Pattern-Implementation Sync

进度条 + 颜色三档。

---

## 区块 7 · ⏰ Pending

```
⏰ Pending decisions / overdue tasks / inbox items
```

- pending decisions — front matter status 为 "pending" 的决策。
- overdue tasks — 过期但未完成的 task。
- inbox items — `inbox/` 里未分类的内容。

---

## 区块 8 · 🔴🟡💡 三色建议

```
🔴 Immediate attention: [...]
🟡 Current priorities: [...]
💡 Suggestions: [...]
```

- 🔴 立即注意 — 今日必须处理，否则有损失。
- 🟡 当前优先 — 本周要推进。
- 💡 建议 — 值得考虑，不紧迫。

---

## 晨报末尾

固定收尾：

```
The session briefing is ready. What would you like to focus on?
```

（按主题语言输出对应句式。日语主题下是「それでは本日はいかがいたしますか」等。）

---

## 为什么晨报要这么长

每个区块都有读者：
- Pre-Session Preparation → 用户 & 所有后续 agent（验证 scope）
- SOUL Health Report → 用户（看到演化）+ REVIEWER（决策时参考）
- DREAM Auto-Triggers → ADVISOR（flag 行为模式）+ 用户（看到警报）
- Strategic Overview → PLANNER（跨项目影响）+ 用户
- Today's Focus → 用户（今日行动）+ DISPATCHER（优先级）
- Metrics → AUDITOR（巡查数据）+ 用户（趋势）
- Pending → 用户（决策积压）
- 三色 → 用户（快速扫）

如果删掉一个区块，就有一个下游 agent 或用户需求失去输入。v1.6.2 的"SOUL/DREAM 固定顶部"就是因为之前有人试图"精简"把它们移到底部，结果用户永远忽略。
