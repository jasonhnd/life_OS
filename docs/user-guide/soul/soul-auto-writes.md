# SOUL 自动写入机制（v1.6.2）

> v1.6.2 起，SOUL 维度由 ADVISOR 在每次决策后自动创建和更新——你不用预先审批，通过事后编辑/删除来引导。

## 为什么改成自动

v1.6.2 之前的版本需要你每次确认候选条目。结果是：

- 你看不到 SOUL 在"工作"——候选一周才出现一次
- Confidence 增长太慢（每次 session 只 +1 evidence）
- 模式识别被你的审批节奏拖慢

v1.6.2 把审批环节去掉，让 SOUL 实时演化。代价是会有一些你不认可的条目，收益是你拥有一个**活着的、真实反映你的**人格档案。

**你对系统的引导方式从"预先批准"变成"事后修剪"**。

---

## 每次决策后发生什么

每次决策工作流（三省六部 Draft-Review-Execute）结束后，ADVISOR 会跑一遍 **SOUL Runtime**：

### Step 1：影响评估

对每个 confidence ≥ 0.3 的现有维度，判断这次决策是：
- **SUPPORT**（支持）→ `evidence_count +1`
- **CHALLENGE**（矛盾）→ `challenges +1`
- **NEUTRAL**（无关）→ 不变

### Step 2：写入 Delta

把增量写到 `_meta/outbox/{session_id}/patterns-delta.md`。archiver 在 session 结束时合并进 SOUL.md。

### Step 3：新维度检测

扫描本次 session + 最近 30 天的决策，找**尚未被现有维度覆盖的新价值/原则模式**。如果：

1. 这是关于身份/价值观/原则的（不是行为模式——那些归 user-patterns.md）
2. 有 ≥2 个决策作证据（本次 session + 最近历史）
3. 现有维度中没有覆盖它（即便是低 confidence 的也算覆盖，那种情况下增加 evidence 而不是新建）

**三个条件都满足** → 自动写入新维度：
- `confidence: 0.3`（低初始值，让证据慢慢长）
- `What IS`：根据观察自动填写
- `What SHOULD BE`：**留空**——等你想清楚再填

### Step 4：冲突检测

如果某个维度的最近 3 个决策**全部**被标记为 CHALLENGE，标记为"冲突"。下一次 REVIEWER 会重点关注。

### Step 5：输出 🔮 SOUL Delta

ADVISOR 在报告中输出本次变化：

```
🔮 SOUL Delta（本次决策）：

【受影响的现有维度】
  · 家庭优先 0.72 🟢 支持 (+1 evidence) — 你再次把家庭影响放在首位
  · 冒险偏好 0.35 🟡 挑战 (+1 challenge) — 你选择了更保守的方案

【新维度候选】
  · 🌱 "过程透明"
    confidence 0.3（证据：本次 session 2 个决策 + 最近 1 个）
    What IS：你在 3 个决策中都要求所有步骤可追溯
    What SHOULD BE：[留空——等你自己填]

【冲突提醒】
  · 冒险偏好 最近 3 个决策都被挑战 → 下次 REVIEWER 重点关注

【写入】
  _meta/outbox/{session_id}/patterns-delta.md
  _meta/outbox/{session_id}/soul-new-dimensions.md
```

你在报告里就能看到 SOUL **在你眼前移动**。

---

## What SHOULD BE 为什么故意留空

这是设计中最重要的一条。

系统可以观察 What IS——你做了什么、说了什么，都是数据。

但 What SHOULD BE 是**你对自己的愿望**。系统不知道你希望自己是什么样——只有你知道。

如果系统替你填了：
- 要么填得像你（那只是把 What IS 复制一遍，毫无意义）
- 要么填得不像你（那是系统在告诉你该成为什么样，越权了）

**留空是一种尊重**。当你看到某个维度的 What SHOULD BE 为空，那是系统在说："我观察到了你，但我不会告诉你应该成为谁。"

你什么时候想清楚了，就去填。不着急。

---

## 撤销方式

### 方式 1：说"undo recent SOUL"

在任何一次 session 中说"undo recent SOUL"或"撤销最近的 SOUL 变更"。ADVISOR 在下次运行时会回滚最近的自动新增。

### 方式 2：直接编辑文件

SOUL.md 就是普通的 markdown 文件。打开它，删掉你不认可的维度整段，保存，就完了。

系统下次读 SOUL 时会看到新状态，不会质疑你的编辑。

### 方式 3：手动改 confidence

如果你不想删除某个维度但想让它不被引用，把 `confidence` 改成 0 或低于 0.3。维度会保留，但 REVIEWER 和 PLANNER 都不会再看它。

---

## 举个完整例子

**Session 1**：你决定在创业项目上用自有资金而不是融资，理由是"不想失去控制权"。

ADVISOR 观察到：关于控制权的关心（1 个决策，不够触发）。

**Session 2**（两天后）：你决定拒绝一个合作机会，因为对方要求 51% 控股。

ADVISOR 观察到：又是关于控制权（2 个决策了），现在触发自动写入：

```yaml
---
dimension: "控制权偏好"
confidence: 0.3
evidence_count: 2
challenges: 0
source: advisor
created: 2026-04-18
last_validated: 2026-04-18
---

### What IS
你在近期 2 个决策中都选择了保有控制权而非最大化收益：拒绝融资、拒绝 51% 控股合作。

### What SHOULD BE
[留空——等你自己填]

### Evidence
- 2026-04-16 创业项目融资决策 — 选择自有资金，保留 100% 股权
- 2026-04-18 合作决策 — 拒绝 51% 控股
```

**下次 Start Session**，你在 SOUL Health Report 看到：

```
🌱 新维度（自上次 session 以来自动检测）：
   · 控制权偏好 0.3（基于 2 个决策）
     What IS：你在近期 2 个决策中都选择了保有控制权而非最大化收益
     What SHOULD BE：[等你填写——当你想清楚]
```

你可以选择：

1. **认可并填 What SHOULD BE**：打开文件写"我愿意在信任的合伙人面前让渡到 40%，但不低于这个底线"
2. **不认可，撤销**：说"undo recent SOUL"
3. **先放着**：继续做决策，看 evidence 是否继续累积。如果后续决策挑战这个维度，confidence 会下降。

**SOUL 不强迫你接受任何结论**。它只如实记录，等你回应。
