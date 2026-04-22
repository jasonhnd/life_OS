# SOUL 如何影响每次决策

> REVIEWER 在每次决策中都必须引用 SOUL——这是 HARD RULE。但为了避免维度多了以后噪音过大，v1.6.2 引入了 3 层引用策略。

## HARD RULE：每次决策都引用

SKILL.md 和 `pro/agents/reviewer.md` 定义了这条硬规则：

**REVIEWER 在每次决策的 Summary Report 前，必须输出一块 "🔮 SOUL Reference"**。

无论决策是大是小、是否涉及价值观，都要出。

- **如果 SOUL.md 不存在** → 输出"🔮 SOUL：尚未建立。这个决策可能开启一个新维度：[推测的维度名和简述]"
- **如果 SOUL 存在但全部是 emerging**（confidence < 0.3）→ 输出"🔮 SOUL：N 个维度都低于 0.3 阈值。追踪中，暂未引用"
- **其他所有情况** → 走下面的 3 层策略

为什么硬性要求？因为如果让 REVIEWER 自己决定"这次要不要看 SOUL"，它会在不该偷懒的时候偷懒。硬规则把这个选择从 REVIEWER 手里拿走。

---

## 3 层引用策略

```
core · 核心身份（confidence ≥ 0.7）  → 全部引用，无上限
secondary · 活跃价值观（0.3 ≤ c < 0.7）   → 按语义相关性取前 3
emerging · 新兴维度（confidence < 0.3）   → 仅计数，不浮现
```

### core：核心身份

**策略**：全部引用，没有上限。

高 confidence 维度代表你的**核心身份**——系统已经看见很多次，这些维度必须在每个决策中都被考虑。

即使有 10 个 core 维度，REVIEWER 也会全部过一遍，对每个维度问：
- 这个决策**支持** / **挑战** / **无关**于这个维度？
- 为什么？

例：

```
【core · 核心身份（必须考虑）】
  · 家庭优先 (0.85) — 这个决策会占用周末时间吗？
    → 支持：方案把执行窗口放在工作日，不侵占家庭时间

  · 风险保守 (0.78) — 这个决策的最坏情况损失是什么？
    → 挑战：方案涉及 40% 自有资金，一旦失败回不了本。与你的风险保守倾向有张力

  · 数据驱动 (0.72) — 决策依据是数据还是直觉？
    → 支持：方案基于过去 6 个月市场数据，非直觉判断
```

### secondary：活跃价值观

**策略**：取**前 3 个语义相关**的维度。

secondary 维度还没固化，不是每个都该在每个决策中出现。REVIEWER 根据决策的 Subject + Summary + PLANNER 方案判断相关性：

- **强相关**（直接相关）→ 优先收录
- **弱相关**（间接相关）→ 按 confidence 排序取前 3
- **不相关** → 跳过

**REVIEWER 的报告必须列出所有被评估的 secondary 维度 + 收录理由**，这样 AUDITOR 可以审查选择质量。

例：

```
【secondary · 活跃价值观（取前 3 相关）】
  · 长期视角 (0.58) [强相关] — 这个决策的 10 年后影响是什么？
    → 支持：方案有明确的 3 年退出路径

  · 过程透明 (0.52) [弱相关] — 执行过程是否可追溯？
    → 支持：每月更新，节点清晰

  · 自主决策 (0.45) [弱相关] — 这是你主动选的还是被推的？
    → 支持：没有外部压力，纯属主动选择

  [评估未收录：社交活跃度 (0.40)、早起偏好 (0.35) — 无相关性]
```

### emerging：新兴维度

**策略**：仅计数，不在 REVIEWER 报告中浮现。

emerging 维度证据还不够（< 0.3），贸然引用会误导。它们由 ADVISOR 在 Delta 块中追踪，等积累够了升到 secondary 再参与。

```
【emerging · 新兴维度】
  不直接引用。ADVISOR Delta 追踪 4 个新兴维度。
```

---

## ⚠️ SOUL CONFLICT：半否决信号

当决策**挑战**一个 core 维度时，REVIEWER 会在 Summary Report 顶部加一条醒目警告：

```
⚠️ SOUL CONFLICT：这个决策挑战了核心身份维度 [家庭优先 (0.85)]。重新审视？
```

这是**半否决信号**——REVIEWER 不会强制否决，但你应该停下来问自己：

- 我是真的要违背核心价值观吗？
- 还是这个维度过时了，该修订？
- 还是这个决策没看清楚，有更好的方案？

**半否决比全否决更有信息量**。全否决告诉你"不行"，半否决告诉你"你可能不是你以为的你"。

---

## 特殊状态

### 🌟 新晋核心

某个维度 confidence 刚跨过 0.7，成为 core：

```
· 控制权偏好 (0.72) 🌟 新晋核心 — [question]
```

这次决策开始，它会被"全部引用"。你应该知道它升级了。

### ⚠️ 核心维度被挑战（可能降级）

某个 core 维度最近累积了多个 challenge，confidence 接近 0.7 阈值：

```
· 风险保守 (0.71) ⚠️ 核心维度受挑战，可能降级 — [question]
```

系统在告诉你：这个核心维度正在动摇。

### > 20 个维度：压缩展示

如果 core 有超过 20 个维度（罕见），REVIEWER 仍然全部评估，但显示时压缩：

```
【core · 核心身份（N 个核心维度；最相关前 5 个详细讨论，剩余 [N-5] 按名称列出）】
```

---

## 快照用于趋势计算

REVIEWER 只看**当前**SOUL 状态。要计算"自上次 session 以来的变化"（↗↘→），需要**快照机制**。

### 快照时机

每次 session 结束时，archiver 的 Phase 2 Step 4 会在 `_meta/snapshots/soul/YYYY-MM-DD-HHMM.md` 写一份 SOUL 快照：

```yaml
---
type: soul-snapshot
captured_at: 2026-04-18T23:45:00+09:00
session_id: cc-20260418-2340
previous_snapshot: 2026-04-17-1850.md
---

# SOUL Snapshot · 2026-04-18

## Dimensions (count: 6)

| dimension | confidence | evidence | challenges | last_validated |
|-----------|-----------|----------|------------|----------------|
| 家庭优先 | 0.85 | 12 | 1 | 2026-04-18 |
| 控制权偏好 | 0.72 | 5 | 1 | 2026-04-18 |
| ...
```

### 快照读取

下次 Start Session，RETROSPECTIVE（Mode 0 Step 11）读最新快照，对每个维度比较 confidence：

- `confidence_Δ > +0.05` → ↗
- `confidence_Δ < -0.05` → ↘
- `|confidence_Δ| ≤ 0.05` → →

**新维度**（当前有快照没有）→ 🌱 NEW
**被删除维度**（快照有当前没有）→ 🗑️ REMOVED（用户手动删除）

### 归档策略

- > 30 天：移到 `_meta/snapshots/soul/_archive/`
- > 90 天：从文件系统删除（git + Notion 已保留）

---

## 信息隔离

按 `pro/CLAUDE.md` 的信息隔离表：

- **REVIEWER** 收到：计划文档 或 六部报告 + 当前 SOUL.md（通过主动读取）
- **REVIEWER** 不收到：其他 agent 的思考过程

REVIEWER 自己读 SOUL.md——不会有其他 agent 把"筛选过的 SOUL 内容"喂给它。这样避免了中间层的曲解。

---

## 何时你会看到 SOUL Reference

- **完整决策工作流**（Full deliberation）→ 每次都出
- **Express analysis**（快速分析）→ 不走 REVIEWER，不出
- **Direct handle**（ROUTER 直接处理）→ 不出
- **STRATEGIST 对话** → 不出（STRATEGIST 有自己的 SOUL 使用方式——读取 worldview 和 unresolved contradictions 给思想家推荐）

所以只有**真正的决策**（经过三省六部的 Draft-Review-Execute）才会产生 SOUL Reference。这是设计上的节制——避免每条对话都被 SOUL 重锤。
