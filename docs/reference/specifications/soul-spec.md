# SOUL 规范

SOUL.md 是用户的人格档案——一份活的文档，记录用户是谁、重视什么、如何思考。它位于第二大脑（second-brain）的根目录。

## 核心原则

1. **从零生长**——SOUL.md 从空开始，不需要预初始化
2. **基于证据**——每条目条目链接到支持它的决策/行为
3. **在严格条件下自动写入**——ADVISOR 在每次决策后自动更新已有维度。新维度累积 ≥2 条证据后自动写入，初始置信度 0.3。用户事后通过编辑/删除来调整，或在条件成熟时补充 "What SHOULD BE" 字段
4. **矛盾有价值**——不要去消除矛盾，把它们暴露出来

---

## 条目格式

SOUL.md 中的每一条条目遵循以下结构：

```yaml
---
dimension: "[维度名]"
confidence: 0.0          # 0-1，自动计算
evidence_count: 0         # 支持的决策/行为数
challenges: 0             # 相反的行为数
source: dream             # dream / advisor / strategist / user
created: YYYY-MM-DD
last_validated: YYYY-MM-DD
---
```

### What IS（实然）
[基于数据观察到的行为模式]

### What SHOULD BE（应然）
[用户陈述的理想或偏好]

### Gap（差距）
[实然与应然之间的差距描述]

### Evidence（证据）
- [日期] [决策/行为] — [描述]

### Challenges（矛盾）
- [日期] [反向行为] — [描述]

---

## 条目生命周期

```
1. 🌱 候选——DREAM 或 ADVISOR 提出
2. ✅ 确认——用户批准（可能调整措辞）
3. 📈 加强——累积更多证据（置信度上升）
4. ⚠️ 被质疑——检测到相反行为
5. 🔄 演化——用户基于新证据或 DREAM 建议更新
6. 🗄️ 退役——用户明确移除（移入 archive）
```

---

## 置信度计算

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

置信度决定 SOUL 条目在系统中的影响力：

| 置信度 | 条件 | 系统行为 |
|--------|------|---------|
| < 0.3 | 新写入，数据点少 | 只有 ADVISOR 引用 |
| 0.3 – 0.6 | 证据中等 | ADVISOR + REVIEWER 引用 |
| 0.6 – 0.8 | 证据充分 | 加入 PLANNER 引用 |
| > 0.8 | 深度验证、矛盾低 | 系统全面引用（包含 ROUTER） |

**置信度自动计算，用户不管理。**

---

## 维度（Dimensions）

SOUL 条目按"维度"组织。常见维度包括：

- **Risk attitude（风险态度）**——保守 ↔ 激进
- **Decision style（决策风格）**——数据驱动 ↔ 直觉驱动
- **Priority（优先级）**——家庭 ↔ 事业 ↔ 自由 ↔ 安全 ↔ 成长
- **Communication style（沟通风格）**——直接 ↔ 圆融
- **Conflict handling（冲突处理）**——对抗 ↔ 回避
- **Time orientation（时间取向）**——当下聚焦 ↔ 未来聚焦
- **Red lines（红线）**——绝对边界（用户绝不会做的事）
- **Core beliefs（核心信念）**——根本世界观假设

用户可以自定义维度。系统不强制分类。

---

## 四种来源

| Source | 如何产生 | 示例 |
|--------|---------|------|
| **DREAM** | 做梦时，从 3 天行为数据中发现模式 | "最近 5 个决策中有 4 个把控制权看得比利润更重要" |
| **ADVISOR** | 工作流之后，观察到重复的价值信号 | "你总是先问家庭影响" |
| **STRATEGIST** | 深度对话中，用户通过交谈揭示价值观 | 用户告诉苏格拉底"稳定比冒险更重要" |
| **用户** | 任意时刻直接输入 | "记住：我永远不会在 X 上妥协" |

---

## 各角色如何使用 SOUL.md

所有角色在引用 SOUL.md 前都先检查文件是否存在。如果不存在或为空，角色正常运行，不使用 SOUL 输入。

| 角色 | 读取内容 | 使用方式 |
|------|---------|---------|
| **ROUTER** | 偏好、红线 | 更锐利的意图澄清——对用户在乎但没提到的维度主动提问 |
| **PLANNER** | 价值优先级（置信度 ≥ 0.6） | 如果用户没提到相关维度，自动加入规划 |
| **REVIEWER** | What IS vs What SHOULD BE 差距（置信度 ≥ 0.3） | 价值一致性检查——标记违背既有价值宣言的决策 |
| **ADVISOR** | 所有条目，证据与矛盾计数 | 行为审计——强化或挑战 SOUL 条目，提出更新建议 |
| **STRATEGIST** | 世界观、未解决矛盾 | 推荐能讨论用户具体矛盾的思想家 |
| **DREAM** | 所有条目（完整读写建议） | 发现新候选，更新证据/矛盾计数，提议演化 |

---

## 首次初始化

SOUL.md 不存在时：

1. 系统正常运行——所有角色跳过 SOUL 引用
2. 首次 Adjourn Court 时，DREAM 的 N3 阶段扫描可用数据：
   a. `user-patterns.md`（如存在）——行为模式 → 提议为 SOUL 候选
   b. 近期决策——价值信号 → 提议为 SOUL 候选
3. 下一次 Start Court 呈现候选："🌱 SOUL.md 尚未存在。基于你的模式，以下是建议条目："
4. 用户确认 → 用确认的条目创建 SOUL.md
5. 若没有可用数据 → 跳过，等后续会话累积证据

**SOUL.md 永远不会用假设预填充，只从观察到的证据生长。**

### 从 user-patterns.md 引导

如果 `user-patterns.md` 存在但 SOUL.md 不存在，DREAM 可以通过读取模式来提议初始 SOUL 条目：
- 行为模式 → 提议为 "What IS"（实然）
- "What SHOULD BE" 留空由用户填写
- 初始置信度低（evidence_count: 1, challenges: 0 → confidence: 1.0，但标记为 🌱 单来源）

---

## 自动写入机制（v1.6.2）

SOUL 维度由 ADVISOR 在每次决策工作流中自动创建和更新。用户通过编辑/删除来调整，而不是预先批准。

### 自动创建标准

ADVISOR 在以下条件满足时创建新的 SOUL 维度：
1. 观察是关于身份/价值观/原则（而非行为模式）
2. 有 ≥2 个决策作为证据（当前会话内，或最近 30 天内）
3. 没有现有维度覆盖它

初始值：
- `confidence: 0.3`
- `What IS`：从证据自动填入
- `What SHOULD BE`：**留空**（由用户填写）

### 自动更新（每次决策）

在每次三省六部工作流后，ADVISOR：
- 对每个已有维度（置信度 ≥ 0.3）：支持 → `evidence_count +1`；抵触 → `challenges +1`
- 重新计算 `confidence = evidence_count / (evidence_count + 2 × challenges)`

### 用户介入

用户不预先批准，但可以：
- 编辑 `What SHOULD BE` 字段（理想值 — 系统从不填写这一字段）
- 删除维度（移除条目）
- 说 "undo recent SOUL" → ADVISOR 回滚最近一次添加
- 手动编辑 confidence 覆盖系统值

### 为什么从"确认"改成"自动写入"

旧版本需要用户确认。v1.6.2 移除这一步，原因：
- 用户看不到 SOUL 在"运作"——候选一周才出现一次
- 置信度增长太慢（每次会话只 +1 条证据）
- 模式检测被用户审查延迟拖累

事后调整 + 实时演化 = 一份"活的" SOUL 档案。

---

## 快照机制（v1.6.2）

为了在 SOUL 健康报告中计算趋势箭头（↗↘→），archiver 在每次会话结束时（Phase 2 合并后）转储一份 SOUL 快照。

### 存储

- 活跃快照：`_meta/snapshots/soul/YYYY-MM-DD-HHMM.md`
- 归档（>30 天）：`_meta/snapshots/soul/_archive/YYYY-MM-DD-HHMM.md`
- 删除（>90 天）：从文件系统移除（git 和 Notion 中保留）

### 快照格式

```yaml
---
type: soul-snapshot
captured_at: ISO 8601 时间戳
session_id: {session UUID}
previous_snapshot: {上一份快照的文件名，或 null 表示首次}
---

# SOUL Snapshot · YYYY-MM-DD

## Dimensions (count: N)

| dimension | confidence | evidence | challenges | last_validated |
|-----------|-----------|----------|------------|----------------|
```

### 读者：RETROSPECTIVE Mode 0 Step 11

下次 Start Session 时，RETROSPECTIVE 读取最新快照，按维度对比当前 SOUL.md，计算：
- `confidence_Δ > +0.05` → ↗
- `confidence_Δ < -0.05` → ↘
- `|confidence_Δ| ≤ 0.05` → →

新维度（当前有、快照无）→ 🌱 NEW
移除的维度（快照有、当前无）→ 🗑️ REMOVED（用户删除）

### 归档策略

archiver Phase 2 Step 4 同时负责维护：
- 将超过 30 天的快照移入 `_archive/`
- 删除 `_archive/` 中超过 90 天的快照
- 两个操作都是幂等的

### 为什么用快照（而非其他方案）

- 单文件 frontmatter（`last_session_evidence`）：拒绝——没有长期趋势数据
- 只做会话内对比：拒绝——丢失跨会话进程
- 完整快照：选中——文件很小（SOUL 本就很精简），完整历史，读者逻辑简单

---

## SOUL 健康报告格式（每次会话简报）

每次 Start Session 都在简报的固定、显著位置包含一份 SOUL 健康报告（不可省略）。

### 格式

```
🔮 SOUL Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Current Profile:
   Active dimensions (confidence > 0.5): N
   · [Dimension A] 0.8 🟢 ↗ (+2 evidence since last session)
   · [Dimension B] 0.6 🟢 → (no change)
   · [Dimension C] 0.5 🟡 ↘ (+1 challenge — last decision contradicted)

🌱 New dimensions (auto-detected since last session):
   · [Dimension D] 0.3 (based on 2 decisions)
     What IS: [system observation]
     What SHOULD BE: [awaiting your input — fill when you have clarity]

⚠️ Conflict warnings:
   · [Dimension X] last 3 decisions all challenged → needs reflection or revision

💤 Dormant dimensions (30+ days no activation):
   · [Dimension Y] — no related decisions recently

📈 This period's trajectory:
   Net evidence +N, net challenges +M, new dimensions +K
```

### 显示规则

- **始终**在 Mode 0 简报中出现（Start Session），无论 SOUL 大小
- 如果 SOUL 为空 → 显示"SOUL is still gathering initial observations. After a few decisions, your first dimensions will emerge."
- 应出现在简报的**顶部**、在 STATUS/项目细节之前
- RETROSPECTIVE 负责从当前 SOUL.md 状态生成

---

## SOUL.md 在 second-brain 中的位置

SOUL.md 位于 second-brain 根目录：

```
second-brain/
├── SOUL.md              ← 人格档案
├── user-patterns.md     ← 行为模式（不同：你做什么）
├── _meta/
├── projects/
├── areas/
└── ...
```

**SOUL.md vs user-patterns.md**：
- `user-patterns.md` 记录**你做什么**——由 ADVISOR 观察到的行为模式
- `SOUL.md` 记录**你是谁**——由你确认的价值观、信念和理想
- 一个描述性（模式），另一个是身份（灵魂）
- 两者互相喂养：模式揭示价值观，价值观为模式提供语境

---

## 按置信度分层引用（v1.6.2）

REVIEWER 在每次决策时都要引用 SOUL（HARD RULE）。为了避免 SOUL 维度多时产生噪声，采用 3 层策略：

| 层 | 置信度 | 引用策略 | 上限 |
|----|-------|----------|------|
| **core · 核心身份** | ≥ 0.7 | 全部引用 | 无上限 |
| **secondary · 活跃价值** | 0.3 – 0.7 | 按语义相关性引用 TopN | 最多 3 |
| **emerging · 萌芽** | < 0.3 | 只计数、不展示（ADVISOR 在 Delta 中追踪） | 0 |

### 相关性判定（secondary）

REVIEWER 读取决策的 Subject + Summary + PLANNER 提案，对每个 secondary 维度打分：
- **strong match**（直接相关）→ 优先纳入
- **weak match**（间接相关）→ 按置信度排序取 Top
- **no match** → 跳过

REVIEWER 报告必须列出所有评估过的 secondary 维度 + 纳入原因 → AUDITOR 审核质量。

### 特殊状态

- 决策挑战 core 维度 → REVIEWER 在总结报告顶部加入 `⚠️ SOUL CONFLICT` 警告（半否决信号）
- 维度自上次快照后跨过 0.7（上行）→ 🌟 "newly promoted to core"
- 维度跨过 0.7（下行）→ ⚠️ "demoted from core"
- 所有维度都在 emerging → REVIEWER 输出 "SOUL tracking, not yet referencing"
- >20 维度 → core 无上限但压缩：Top5 详述，其余列名
