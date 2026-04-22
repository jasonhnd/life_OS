---
translated_from: references/snapshot-spec.md
translator_note: auto-translated 2026-04-22, 待人工校对
---

# Snapshot 规范（Snapshot Specification）

SOUL snapshots 是每次会话结束时捕获的小型、不可变的 metadata 快照。它们让下一次 Start Session 的 SOUL Health Report 无需维护单独的状态机，就能在会话间计算出趋势箭头（↗↘→）。一个 snapshot 是一个冻结的瞬间：系统在 T 时刻对用户身份维度的所知。

## 定位（Positioning）

| Artefact | 记录什么 |
|----------|----------------|
| `SOUL.md` | 当前权威身份状态 |
| `_meta/snapshots/soul/` | **用于趋势计算的历史 SOUL 状态（本 spec）** |
| `_meta/concepts/` | synaptic 网络（`references/concept-spec.md`） |
| `wiki/` | 可复用的世界知识 |

snapshots 是仅 metadata —— 永不复制 SOUL 正文内容。它们记录 SOUL 在某一时点的数值形态，以便 retrospective 比较 "当时" 与 "现在"。

---

## 原则（Principles）

1. **不可变（Immutable）** —— 一旦写入，snapshots 永不编辑。更正入 SOUL.md，不入历史 snapshot。
2. **仅 metadata（Metadata-only）** —— snapshots 存维度名、confidence、证据计数、tier。它们不存 SOUL 正文文本。
3. **每会话创建（Created every session）** —— 即使是琐碎会话也要。缺失 snapshot 会破坏趋势计算。
4. **小（Small）** —— 每个 snapshot 典型 <5KB。成千上万个 snapshot 仍代价低廉。
5. **积极归档（Archived aggressively）** —— 活跃 snapshot 保持热存 30 天，然后移入 `_archive/`，90 天后删除。Git 历史保留完整审计链。**Snapshots 不同步到 Notion** —— 按用户决策 #12 与 `cortex-spec.md` §Anti-patterns，所有 Cortex/`_meta/` 数据（concepts、synapses、snapshots）留本地。Notion 只接收会话摘要与决策记录。

---

## 文件位置（File Location）

```
_meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md
```

文件名中的时间戳**必须来自捕获时的真实 `date` 命令** —— 不得伪造（v1.4.4b 的决策）。若系统时钟不可用，中止 snapshot 写入并把失败记入 `_meta/cortex/decay-log.md`。

### 保留路径

- `_meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md` —— 活跃 snapshot（30 天内）
- `_meta/snapshots/soul/_archive/{YYYY-MM-DD-HHMM}.md` —— 已归档 snapshot（30-90 天）
- 超过 90 天的 snapshot 从文件系统删除；审计链只留在 git 历史（按用户决策 #12，snapshot 仅本地）

---

## YAML Frontmatter 模式（YAML Frontmatter Schema）

```yaml
---
snapshot_id: {YYYY-MM-DD-HHMM}      # 与文件名一致，唯一
captured_at: ISO 8601               # 实际捕获时间戳
session_id: string                  # 产出本 snapshot 的会话
previous_snapshot: string | null    # 前一份文件名，或 null（有史以来第一次）
dimensions:
  - name: string                    # SOUL 维度名
    confidence: float               # 0-1，捕获时从 SOUL.md 复制
    evidence_count: integer         # 支撑决策数
    challenges: integer             # 反驳决策数
    tier: enum                      # core | secondary | emerging | dormant
---

# SOUL Snapshot · {YYYY-MM-DD}

（正文可选 —— frontmatter 是权威内容。可选包含人类可读表格用于调试，但不要求。）
```

### 字段约束

| 字段 | 约束 |
|-------|-----------|
| `snapshot_id` | 必须与文件名主干精确一致 |
| `captured_at` | 必须是来自系统时钟的真实 ISO 8601 时间戳 |
| `session_id` | 必须是 `_meta/sessions/` 里一个有效 session ID |
| `previous_snapshot` | 前一份 snapshot 的文件名，或首个为 `null` |
| `dimensions` | 只包含 `confidence > 0.2` 的维度（跳过噪声） |
| `dimensions[].tier` | 从 confidence 派生（见下文 Tier Mapping） |

### Tier 映射（Tier Mapping）

Tier 在捕获时派生，不在 SOUL.md 中单独存储：

所有 confidence 区间都使用半开区间 `[a, b)`——下界包含，上界不包含。边界值永远归入**更高**一层的 tier（例如 confidence 恰好为 0.3 时属于 `secondary` 而不是 `emerging`；恰好为 0.7 时属于 `core` 而不是 `secondary`）。这与 `references/soul-spec.md` §Tiered Reference by Confidence 和 `references/gwt-spec.md` §5.4 保持一致。

| Tier | Confidence 范围 |
|------|------------------|
| `core` | `[0.7, 1.0]` |
| `secondary` | `[0.3, 0.7)` |
| `emerging` | `[0.2, 0.3)` |
| `dormant` | `[0.0, 0.2)`（从 snapshot 中排除） |

snapshot 刻意省略 `dormant` 维度以保持文件小。一个维度在 snapshot 中缺席是有意义的 —— 这是趋势算法检测退休或降级的方式。

---

## 创建（Creation）

snapshot 创建由 `archiver` Phase 2 拥有，在 concept 抽取后执行（这样会话期间强化的 concept 已经持久化）。序列：

```
archiver Phase 2
    ├── Step 1 —— wiki / SOUL 自动写入（既有）
    ├── Step 2 —— concept 抽取 + Hebbian 更新（concept-spec.md）
    ├── Step 3 —— SOUL snapshot dump（本 spec）
    │   1. 运行 `date` 获得实际捕获时间戳
    │   2. 读取当前 SOUL.md
    │   3. 对每个 confidence > 0.2 的维度：
    │        - 从 confidence 决定 tier
    │        - 复制 name、confidence、evidence_count、challenges
    │   4. 找到最新既有 snapshot → 设 `previous_snapshot`
    │   5. 写入 _meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md
    │   6. 写入后文件变只读（不要编辑）
    └── Step 4 —— 清理（见 Archive Policy）
```

### 不变式（Invariants）

- 即使是琐碎会话（没有做决策）也仍然产出一份 snapshot。缺失 snapshot 会破坏趋势计算，视为 bug。
- 同一会话的 snapshot 不会被写两次。若 `archiver` 对一个已有 snapshot 的会话重跑，该写入被跳过并记录。
- snapshot 是追加的 —— 写新 snapshot 永不移除或编辑前一份。

---

## 趋势计算（Trend Computation）

在下次 Start Session，`retrospective` 读取**最近的两份 snapshot**，计算各维度 delta。趋势箭头出现在 SOUL Health Report（见 `soul-spec.md` Health Report Format）。

### Delta 规则

| 条件 | 趋势标记 |
|-----------|--------------|
| `confidence_Δ > +0.05` | ↗ 上升 |
| `confidence_Δ < -0.05` | ↘ 下降 |
| `|confidence_Δ| ≤ 0.05` | → 稳定 |
| 维度在当前 snapshot 有但前一份没有 | 🌱 新 |
| 维度在前一份有但当前没有 | 💤 dormant |

### 特殊状态

retrospective 也发出用于 tier 转变与冲突检测的徽章：

| 转变 | 徽章 | 条件 |
|------------|-------|-----------|
| 向上越过 0.7 | 🌟 promoted to core | 前 tier < `core`，当前 tier = `core` |
| 向下越过 0.7 | ⚠️ demoted from core | 前 tier = `core`，当前 tier < `core` |
| 冲突区 | ❗ evidence ≈ challenges | `|evidence_count − challenges| ≤ 1` **且** `evidence_count ≥ 3` |

徽章与趋势标记叠加 —— 一个维度可以同时是 ↗ 与 🌟（提升的同时上升）。

### 首次 snapshot 的处理

当没有前一份 snapshot 时（bootstrap 之后第一次 Start Session，或全新 second-brain 的有史以来第一个会话），所有维度渲染为 🌱，且不计算趋势箭头。Health Report 表头注明 "First snapshot — trends will appear next session."

---

## 归档策略（Archive Policy）

`archiver` Phase 2 Step 4 在 snapshot 创建后执行清理：

1. 对 `_meta/snapshots/soul/` 中 `captured_at` **超过 30 天**的每个文件：移入 `_meta/snapshots/soul/_archive/`（保留文件名）
2. 对 `_meta/snapshots/soul/_archive/` 中 `captured_at` **超过 90 天**的每个文件：从文件系统删除
3. 清理是幂等的 —— 运行两次结果相同

删除是安全的，因为：
- Git 历史无限期保留所有被删文件
- 趋势计算只需要最近两份 snapshot；更深历史是为了审计，不为活跃算法
- snapshot 仅本地（不同步到 Notion）；完整审计链住在 git 里

---

## 大小约束（Size Constraints）

- 每份 snapshot **典型 < 5KB** —— 一个有 20 个活跃维度的 SOUL 产出 ~2KB YAML
- 1000 份 snapshot（几年日常会话）≈ **5MB 合计** —— 对 git 和 Notion 微不足道
- 正文内容可选；留空可把文件大小减半
- 无图片、无二进制数据、无嵌入附件 —— snapshot 是纯 YAML + 可选 markdown

若 snapshot 超过 10KB，archiver 记录警告 —— 通常意味着 SOUL.md 长到了不寻常形态（>50 活跃维度），这本身也值得用户关注。

---

## 迁移（Migration）

v1.7 之前没有 snapshot（v1.6.2 引入机制；v1.6.2a 把它稳定下来）。对于早于 v1.6.2 的 second-brain：

1. `tools/migrate.py` 扫描 `_meta/journal/` 中的 SOUL delta 块（由 ADVISOR 发出的 `🔮 SOUL Delta` 节）
2. 对每份含 SOUL delta 的 journal 条目，合成一份以该 journal 条目日期为时间戳的 snapshot
3. 合成的 snapshot 在 frontmatter 带 `provenance: synthetic`，以便 retrospective 区分合成与自然 snapshot
4. 迁移止于近 3 个月内最早的 journal 条目（用户决策 #7 —— 与所有其他迁移范围对齐）。更深历史不重建；signal 降得太多。
5. 把迁移结果记入 `_meta/cortex/bootstrap-status.md`

迁移是幂等的。合成 snapshot 被趋势算法视同自然 snapshot —— `provenance` 字段只为审计存在。

---

## 读者职责（Reader Responsibilities）

`retrospective` 是 Start Session 期间 snapshot 的唯一读者。其契约：

1. 按 `captured_at` 降序列出 `_meta/snapshots/soul/` 中文件
2. 取前 2 份（当前与前一份）
3. 若少于 2 份 snapshot，回退到 "首次 snapshot" 行为（所有维度渲染为 🌱）
4. 解析两份 YAML frontmatter
5. 按 §5 规则计算 delta
6. 发出 SOUL Health Report 块（格式定义于 `soul-spec.md`）

retrospective 在正常运行时不读取已归档 snapshot。`_archive/` 仅在用户显式要求长期趋势时才查询（例如 "show me the past year's core identity evolution"）。

---

## 反模式（Anti-patterns）

这些是 spec 禁止的：

1. **创建后编辑 snapshot 文件** —— snapshot 不可变。更正入 SOUL.md，下一份 snapshot 会反映它。
2. **在 snapshot 中存 SOUL 正文内容** —— 只存 metadata。snapshot 文件若超过 10KB 是 bug。
3. **对 "琐碎" 会话跳过 snapshot 创建** —— 每个会话都创建 snapshot。趋势算法依赖连续历史；空缺与 dormant 无法区分。
4. **伪造时间戳** —— 文件名与 `captured_at` 必须来自写入时的真实系统时钟。无手工时间戳、无合成时间，例外仅在迁移（此时要求 `provenance: synthetic`）。
5. **手动删除活跃 snapshot** —— 保留由归档策略拥有。手动删除破坏 "最近两份" 读者契约。
6. **在 retrospective 之外读取 snapshot** —— 其他角色必须经由 retrospective 的 Health Report 输出。其他 agent 直接读取会破坏信息隔离模型。

---

## 约束（Constraints）

- **每会话一份 snapshot** —— 不能两份、不能零份
- **创建后不可变** —— 按只读对待
- **仅 metadata** —— 无 SOUL 正文内容
- **文件名时间戳 = 实际捕获时间** —— 不伪造
- **仅包含 confidence > 0.2 的维度** —— 跳过噪声
- **典型 < 5KB，硬警告阈值 < 10KB**
- **30 天热、30-90 天归档、>90 天删除** —— 归档策略幂等
- **`archiver` Phase 2 拥有写入，`retrospective` Mode 0 拥有读取** —— 无其他角色触碰 snapshot 文件
- **仅本地 —— 无 Notion 同步** —— snapshot 是 Cortex/`_meta/` 数据；审计链住在 git

---

## 相关规范（Related Specs）

- `references/soul-spec.md` —— SOUL 模式、维度生命周期、Health Report 格式的消费者
- `references/session-index-spec.md` —— `session_id` 字段引用 `_meta/sessions/` 中的条目
- `references/cortex-spec.md` —— 整体 Cortex 架构；snapshot 是五个 v1.7 核心 artifact 之一
- `references/concept-spec.md` —— 同胞 `_meta/` 数据层；相同的 markdown 优先原则与仅本地约束
- `references/eval-history-spec.md` —— AUDITOR 的 `soul_reference_quality` 维度消费 snapshot 派生的趋势 signal
- `pro/agents/archiver.md` —— Phase 2 Step 3 拥有 snapshot 写入
- `pro/agents/retrospective.md` —— Mode 0 拥有 Health Report 的 snapshot 读取

---

> ℹ️ **2026-04-22 更新**:同步 EN R4.3 修复 Tier 表半开区间格式(对齐 gwt-spec §5.4)

*本文译自英文版 2026-04-22 snapshot；英文为权威源。*
