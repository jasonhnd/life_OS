# SOUL 规范

SOUL.md 是用户的人格档案——一份记录用户是谁、重视什么、如何思考的活文档。它存放在第二大脑根目录中。

## 原则

1. **从零生长** — SOUL.md 初始为空，无需初始化。
2. **基于证据** — 每条条目都链接到支持它的决策/行为。
3. **严格标准下的自动写入** — ADVISOR 在每次决策后自动更新现有维度。积累 ≥2 个证据点时，新维度以低初始置信度 (0.3) 自动写入。用户事后调整：自由编辑、删除维度、准备好时填写"What SHOULD BE"。
4. **矛盾有价值** — 不要消解矛盾；将它们呈现出来。

---

## 条目格式

SOUL.md 中每条条目遵循以下结构：

```yaml
---
dimension: "[维度名称]"
confidence: 0.0          # 0-1，自动计算
evidence_count: 0         # 支持的决策/行为数量
challenges: 0             # 矛盾的行为数量
source: dream             # dream / advisor / strategist / user
created: YYYY-MM-DD
last_validated: YYYY-MM-DD
---
```

### 实然（What IS）
[基于数据的观察到的行为模式]

### 应然（What SHOULD BE）
[用户陈述的愿望或偏好]

### 差距（Gap）
[对现实与愿望之间差距的描述]

### 证据（Evidence）
- [日期] [决策/行为] — [描述]

### 矛盾（Challenges）
- [日期] [矛盾行为] — [描述]

---

## 条目生命周期

```
1. 🌱 候选 — DREAM 或 ADVISOR 提议
2. ✅ 已确认 — 用户批准（可修改措辞）
3. 📈 已强化 — 积累更多证据（confidence 上升）
4. ⚠️ 受挑战 — 检测到矛盾行为
5. 🔄 已演化 — 用户根据新证据或 DREAM 建议更新
6. 🗄️ 已退役 — 用户明确移除（移入档案）
```

---

## Confidence 计算

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

Confidence 决定 SOUL 条目对系统的影响程度：

| Confidence | 条件 | 系统行为 |
|------------|------|----------|
| < 0.3 | 新写入，数据点少 | 仅 ADVISOR 引用 |
| 0.3 – 0.6 | 中等证据 | ADVISOR + REVIEWER 引用 |
| 0.6 – 0.8 | 充分证据 | + PLANNER 引用 |
| > 0.8 | 深度验证，低矛盾率 | 全系统引用（含 ROUTER） |

Confidence 自动计算——用户无需管理。

---

## 维度

SOUL 条目按维度组织。常见维度包括：

- **风险态度** — 保守 ↔ 激进
- **决策风格** — 数据驱动 ↔ 直觉
- **优先级** — 家庭 ↔ 事业 ↔ 自由 ↔ 安全感 ↔ 成长
- **沟通风格** — 直接 ↔ 外交式
- **冲突处理** — 对抗型 ↔ 回避型
- **时间取向** — 当下聚焦 ↔ 未来聚焦
- **红线** — 绝对边界（用户绝不会做的事）
- **核心信念** — 基本的世界观假设

用户可以自定义维度。系统不强加分类。

---

## 四种来源

| 来源 | 方式 | 示例 |
|------|------|------|
| **DREAM** | 在梦境中，从 3 天行为数据中发现模式 | "最近 5 次决策中有 4 次优先控制权而非收益" |
| **ADVISOR** | 工作流结束后，观察到反复出现的价值信号 | "你总是先问家庭影响" |
| **STRATEGIST** | 深度对话中，用户通过交谈透露价值观 | 用户告诉苏格拉底"稳定比冒险更重要" |
| **用户** | 随时直接输入 | "记住：我在 X 上绝不妥协" |

---

## 各角色如何使用 SOUL.md

所有角色在引用 SOUL.md 之前先检查它是否存在。如果不存在或为空，角色正常运作，不使用 SOUL 输入。

| 角色 | 读取内容 | 使用方式 |
|------|---------|----------|
| **ROUTER** | 偏好、红线 | 更精准的意图澄清——即使用户未提及，也会就其关心的维度提问 |
| **PLANNER** | 价值优先级（confidence ≥ 0.6） | 如果用户未提及相关维度，自动将其添加为必要维度 |
| **REVIEWER** | 实然与应然的差距（confidence ≥ 0.3） | 价值一致性检查——当决策与陈述的愿望矛盾时发出提示 |
| **ADVISOR** | 所有条目，证据与矛盾数量 | 行为审计——强化或挑战 SOUL 条目，提议更新 |
| **STRATEGIST** | 世界观、未解决的矛盾 | 推荐能够应对用户特定张力的思想家 |
| **DREAM** | 所有条目（完整读写提议） | 发现新候选条目，更新证据/矛盾数量，提议演化 |

---

## 首次初始化

当 SOUL.md 不存在时：

1. 系统正常运行——所有角色跳过 SOUL 引用
2. 首次散朝时，DREAM 的 N3 阶段扫描可用数据：
   a. `user-patterns.md`（如果存在）——行为模式 → 作为 SOUL 候选提出
   b. 近期决策——价值信号 → 作为 SOUL 候选提出
3. 下次上朝呈现候选："🌱 SOUL.md 尚未创建。根据你的行为模式，以下是建议的初始条目："
4. 用户确认 → 创建 SOUL.md 并写入确认的条目
5. 如果没有可用数据 → 跳过，等待更多 session 积累证据

SOUL.md 永远不会用假设预填充。它只从观察到的证据中成长。

### 从 user-patterns.md 引导启动

如果 `user-patterns.md` 存在但 SOUL.md 不存在，DREAM 可以通过读取行为模式来提出初始 SOUL 条目：
- 行为模式 → 作为"实然"（What IS）提出
- "应然"（What SHOULD BE）留空让用户填写
- 初始置信度较低（evidence_count: 1, challenges: 0 → confidence: 1.0 但标记为 🌱 单源）

---

## 自动写入机制（v1.6.2）

SOUL 维度由 ADVISOR 在每次决策工作流中自动创建和自动更新。用户通过编辑/删除来调整系统，而非预先批准。

### 自动创建标准

ADVISOR 在以下条件全部满足时创建新的 SOUL 维度：
1. 观察与身份/价值观/原则相关（而非行为模式）
2. 有 ≥2 个决策作为证据（本次会话或过去 30 天内）
3. 没有现有维度涵盖它

初始值：
- `confidence: 0.3`
- `What IS`：自动根据证据填写
- `What SHOULD BE`：留空（由用户填写）

### 自动更新（每次决策）

每次三省工作流结束后，ADVISOR：
- 对每个现有维度（confidence ≥ 0.3）：如被支持则 evidence_count +1，如被反驳则 challenges +1
- 重新计算 `confidence = evidence_count / (evidence_count + 2 × challenges)`

### 用户事后调整

用户不预先批准，但可以：
- 编辑 `What SHOULD BE` 字段（愿望——系统永远不填写此字段）
- 删除某个维度（移除条目）
- 说"撤销最近 SOUL" → ADVISOR 回滚最近的新增
- 手动编辑 confidence 以覆盖

### 为什么改为自动而非确认

此前版本要求确认。v1.6.2 移除了此要求，因为：
- 用户看不见 SOUL 在"运作"——候选每周才出现一次
- Confidence 增长太慢（每次会话仅 1 个证据点）
- 模式检测被用户审核开销拖慢

事后调整 + 实时演化让用户拥有一份**活的** SOUL 档案。

---

## 快照机制（v1.6.2）

为了在 SOUL 健康报告中计算趋势箭头（↗↘→），archiver 在每次会话结束时（Phase 2，delta 合并之后）导出一份 SOUL 快照。

### 存储

- 活跃快照：`_meta/snapshots/soul/YYYY-MM-DD-HHMM.md`
- 归档（>30 天）：`_meta/snapshots/soul/_archive/YYYY-MM-DD-HHMM.md`
- 删除（>90 天）：从文件系统移除（git + Notion 中保留）

### 快照格式

```yaml
---
type: soul-snapshot
taken_at: ISO 8601 timestamp
session_id: {session UUID}
previous_snapshot: {prior filename, or null if first}
---

# SOUL Snapshot · YYYY-MM-DD

## Dimensions (count: N)

| dimension | confidence | evidence | challenges | last_validated |
|-----------|-----------|----------|------------|----------------|
```

### 读取方：RETROSPECTIVE Mode 0 Step 11

下次上朝时，RETROSPECTIVE 读取最新快照，将逐维指标与当前 SOUL.md 对比，并计算：
- `confidence_Δ > +0.05` → ↗
- `confidence_Δ < -0.05` → ↘
- `|confidence_Δ| ≤ 0.05` → →

新增维度（当前有但快照无）→ 🌱 NEW
移除维度（快照有但当前无）→ 🗑️ REMOVED（用户删除）

### 归档策略

archiver Phase 2 Step 4 也执行家政：
- 将 30 天以上的快照移入 `_archive/`
- 从 `_archive/` 删除 90 天以上的快照
- 两项操作均为幂等

### 为什么采用快照（而非替代方案）

- 单文件 frontmatter（`last_session_evidence`）：否决——缺乏长期趋势数据
- 仅 session 内对比：否决——丢失跨 session 进程
- 完整快照：选中——小文件（SOUL 很小）、全历史、读取逻辑简单

---

## 健康报告格式（每次会话晨报）

每次上朝都会包含一份 SOUL 健康报告，位于晨报的固定显眼位置（非可选）。

### 格式

```
🔮 SOUL 健康报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 当前画像：
   活跃维度（confidence > 0.5）：N
   · [维度 A] 0.8 🟢 ↗（自上次会话以来 +2 证据）
   · [维度 B] 0.6 🟢 →（无变化）
   · [维度 C] 0.5 🟡 ↘（+1 挑战——上次决策与之矛盾）

🌱 新维度（自上次会话以来自动检测到）：
   · [维度 D] 0.3（基于 2 次决策）
     What IS：[系统观察]
     What SHOULD BE：[等待你的输入——准备好后再填写]

⚠️ 冲突警告：
   · [维度 X] 最近 3 次决策全部受到挑战 → 需要反思或修订

💤 休眠维度（30+ 天未激活）：
   · [维度 Y] — 近期无相关决策

📈 本期轨迹：
   净证据 +N，净挑战 +M，新维度 +K
```

### 显示规则

- 始终出现在 Mode 0 晨报（上朝）中，无论 SOUL 规模大小
- 如果 SOUL 为空 → 显示"SOUL 仍在收集初始观察。经过若干次决策后，你的首批维度将会浮现。"
- 应位于晨报**顶部**，在 STATUS/项目详情之前
- RETROSPECTIVE 代理负责根据当前 SOUL.md 状态生成此报告

---

## 第二大脑中的 SOUL.md

SOUL.md 位于第二大脑目录的根目录：

```
second-brain/
├── SOUL.md              ← 人格档案
├── user-patterns.md     ← 行为模式（不同之处：记录你做了什么）
├── _meta/
├── projects/
├── areas/
└── ...
```

**SOUL.md 与 user-patterns.md 的区别**：
- `user-patterns.md` 记录**你做了什么**——ADVISOR 观察到的行为模式
- `SOUL.md` 记录**你是谁**——你已确认的价值观、信念和愿望
- 一个是描述性的（模式），另一个是身份性的（灵魂）
- 它们相互滋养：模式揭示价值观，价值观赋予模式以情境

---

## 按置信度分层引用（v1.6.2）

REVIEWER 在每次决策中都引用 SOUL（HARD RULE）。为避免 SOUL 维度众多时产生噪音，采用 3 层策略：

| 层级 | 置信度 | 引用策略 | 上限 |
|------|--------|---------|------|
| **Tier 1 · 核心身份** | ≥ 0.7 | 全部引用 | 无上限 |
| **Tier 2 · 活跃价值** | 0.3 – 0.7 | 引用语义最相关的前 N 条 | 最多 3 条 |
| **Tier 3 · 萌芽期** | < 0.3 | 仅统计，不呈现（ADVISOR 在 Delta 中跟踪） | 0 |

### 相关性判断（Tier 2）

REVIEWER 读取决策的 Subject + Summary + PLANNER 提案，然后对每个 Tier 2 维度评级：
- **强匹配**（直接相关）→ 优先纳入
- **弱匹配**（间接相关）→ 按置信度排序，取头部
- **无匹配**→ 跳过

REVIEWER 报告必须列出所有被评估的 Tier 2 维度及纳入理由 → AUDITOR 审核质量。

### 特殊状态

- 决策挑战 Tier 1 维度 → REVIEWER 在 Summary Report 顶部加 ⚠️ SOUL CONFLICT 警告（半否决信号）
- 自上次快照以来维度跨过 0.7 向上 → 🌟 "新晋核心"
- 维度跨过 0.7 向下 → ⚠️ "从核心降级"
- 所有维度都在 Tier 3 → REVIEWER 输出 "SOUL 追踪中，尚未引用"
- >20 个维度 → Tier 1 无上限但压缩显示：前 5 个详写，其余按名称列出
