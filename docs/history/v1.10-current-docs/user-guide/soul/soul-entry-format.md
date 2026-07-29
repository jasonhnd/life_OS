# SOUL 条目格式

> SOUL.md 里每个维度都是一个独立的条目，遵循固定的 YAML schema + markdown 结构。本文详解字段含义、生命周期、confidence 计算。

## 完整 Schema

每个条目都长这样：

```yaml
---
dimension: "家庭优先"
confidence: 0.85          # 0-1，自动计算
evidence_count: 12        # 支持证据数
challenges: 1             # 矛盾证据数
source: advisor           # dream / advisor / strategist / user
created: 2026-03-15
last_validated: 2026-04-18
---

### What IS（实然）
你在 12 个决策中都把家庭影响作为首要考虑因素。其中 6 次因家庭原因改变了原定方案。

### What SHOULD BE（应然）
我希望家庭是所有决策的基础，不是被牺牲的变量。但我也需要承认，有些职业机会需要暂时让家庭做出调整。

### Gap（差距）
陈述上想"坚持家庭优先"，但在 3 月份的工作决策中接受了高强度出差安排。实际行为和陈述之间有 ~25% 的张力。

### Evidence（证据）
- 2026-03-15 拒绝海外差旅机会 — 选择留在家处理孩子入学
- 2026-03-22 调整项目排期 — 为配偶生日预留整天
- 2026-04-01 选择合伙人 — 优先选家庭所在城市的人
- ... (共 12 条)

### Challenges（矛盾）
- 2026-03-28 接受 6 周高强度出差 — 与家庭优先维度冲突
```

---

## 字段详解

### `dimension`（必填）

维度名。一个短词或短语。

命名原则：
- ✅ **简短具体**：`家庭优先` / `风险保守` / `过程透明`
- ❌ 避免长句：`我觉得家庭比工作重要` ← 太啰嗦
- ❌ 避免模糊：`生活态度` ← 不够具体

同一个 SOUL.md 里不允许同名维度。系统在自动写入前会检查。

### `confidence`（自动计算）

0 到 1 之间的浮点数，**你不管理**。

计算公式：

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

challenges 的权重是 2 倍 evidence——一个矛盾事件比一个支持事件更"重"。这个不对称是故意的：

- 100 个小支持 + 0 矛盾 → confidence 1.0
- 100 个小支持 + 1 矛盾 → confidence 0.98
- 2 个支持 + 1 矛盾 → confidence 0.5
- 2 个支持 + 2 矛盾 → confidence 0.33

**为什么 challenges 权重更大？**

因为人在矛盾中显露真实。一个人做了 100 次符合"风险保守"的事，说明他可能**只是习惯**保守；但他做了一次违反的事，更有信息量——那一次揭示了边界和动摇。

### `evidence_count` / `challenges`

- `evidence_count`：支持该维度的决策或行为数
- `challenges`：矛盾该维度的决策或行为数

ADVISOR 在每次决策后自动 +1 对应字段。你不用管。

如果你手动在文件里改这两个数，下次 ADVISOR 会以你的数为基础继续累加（系统不会回滚你的编辑）。

### `source`

条目的来源：

| 值 | 含义 |
|----|------|
| `dream` | DREAM 阶段从 3 天数据发现 |
| `advisor` | ADVISOR 在工作流后观察到 |
| `strategist` | STRATEGIST 对话中用户透露 |
| `user` | 用户直接添加 |

这是元信息。系统不根据 source 做差别对待，只用于你追溯"这个维度是怎么来的"。

### `created` / `last_validated`

- `created`：条目首次写入的日期
- `last_validated`：最近一次被决策激活（支持或挑战）的日期

`last_validated` 和当前日期差 > 30 天 → 健康报告中标记为 💤 休眠。

---

## 生命周期

```
1. 🌱 Candidate — DREAM 或 ADVISOR 提出（v1.6.2 后不再有显式 candidate 阶段，
                   直接进入 Confirmed，但初始 confidence 很低）
2. ✅ Confirmed — 写入 SOUL.md
3. 📈 Strengthened — 更多证据累积（confidence 上升）
4. ⚠️ Challenged — 检测到矛盾行为
5. 🔄 Evolved — 用户根据新证据或 DREAM 建议更新
6. 🗄️ Retired — 用户明确删除（归档到 _archive/）
```

### Candidate → Confirmed

v1.6.2 后，自动写入机制让 Candidate 和 Confirmed 合并了——一旦满足"≥ 2 个决策证据 + 未被覆盖 + 关于价值观"，直接写入 SOUL.md 为 Confirmed（但 confidence = 0.3）。

用户的角色从"事前批准候选"变为"事后修剪不认可的"。

### Strengthened

每次决策支持该维度 → `evidence_count +1` → confidence 上升。

跨过关键阈值时的含义变化：

- 跨过 0.3：从 emerging 升到 secondary，REVIEWER 开始引用
- 跨过 0.6：PLANNER 开始引用
- 跨过 0.7：secondary 升到 core（🌟 新晋核心）
- 跨过 0.8：全系统引用

### Challenged

每次决策矛盾该维度 → `challenges +1` → confidence 下降。

如果连续 3 次决策都挑战 → 健康报告标记 ❗ 冲突区 → REVIEWER 下次把它放首位警告。

### Evolved

用户的干预：

- 编辑 `What SHOULD BE`（系统不会替你改）
- 编辑 `What IS`（系统下次会用新版）
- 改名（dimension 字段重命名）→ 注意保留 evidence/challenges 数
- 调 confidence（手动覆盖）

DREAM 也可能提出"这个维度应该拆成两个"或"这两个维度其实是一个"的建议，但**不会自动合并/拆分**——需要你确认。

### Retired

用户直接删除维度的整段。系统下次读 SOUL 时看到少了一个维度，在健康报告里标记 🗑️ REMOVED。

如果你想保留历史但不再被系统引用，可以把 `confidence` 改成 0。条目保留，但所有 agent 都跳过。

---

## 阈值参考表

这张表决定了不同 confidence 下的系统行为：

| Confidence | 阶段 | 影响范围 |
|------------|------|---------|
| < 0.3 | emerging · 新兴 | 仅 ADVISOR 追踪（Delta 块） |
| 0.3 – 0.6 | secondary · 活跃 | ADVISOR + REVIEWER |
| 0.6 – 0.7 | secondary · 高活跃 | + PLANNER |
| 0.7 – 0.8 | core · 核心 | + 全系统（ROUTER 也看） |
| > 0.8 | core · 深度稳固 | 全引用，决策挑战时必发 ⚠️ SOUL CONFLICT |

跨越阈值时健康报告会标记：
- 从 secondary → core = 🌟 新晋核心
- 从 core → secondary = ⚠️ 从核心降级

---

## 命名冲突与覆盖

当 ADVISOR 要自动写入新维度时，会检查是否已有**覆盖相同概念**的维度（不只是同名，还包括语义覆盖）。

例：已有"风险保守"维度，ADVISOR 观察到"你每次都避免激进方案"——这已经被"风险保守"覆盖，不会新建"避免激进倾向"，而是给"风险保守" +1 evidence。

判断覆盖的标准是语义相似度，由 ADVISOR（Opus 模型）自己判断。如果你觉得它漏判了，可以手动合并：

1. 把重复维度的 evidence/challenges 加到你想保留的那个上
2. 删除重复维度
3. 下次 session 系统接受新状态

---

## 条目健康度自检

偶尔你可以手动检查 SOUL.md 的健康度：

- **是否有 confidence 超高但实际已经过时的维度？**（比如 2 年前的想法）
  → 考虑调低 confidence 或删除
- **是否有维度互相矛盾？**（比如"极度冒险"和"风险保守"同时高 confidence）
  → 这是系统在告诉你你有内部张力。不用消除，但可以在 STRATEGIST 对话中深挖
- **What SHOULD BE 是否有太久没填的？**
  → 如果一个维度创建了 3 个月还没填 What SHOULD BE，可能它不值得有
- **是否有太多低 confidence 的噪音维度？**
  → 删除 confidence < 0.2 且创建超过 30 天的

系统会在 AUDITOR 巡检时做类似的检查，但自检更有意义——**SOUL 是你的，不是系统的**。
