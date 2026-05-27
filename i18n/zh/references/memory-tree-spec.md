---
spec_id: memory-tree-spec.v1-proposal
status: proposal
authoritative: false
implementation_target: v1.9 或 v2.0（TBD —— 待 Jason second-brain 真实数据验证）
description: 提案 —— lifeos sessions/wiki 内存的 cascade seal 架构。定义 L0（原始，≤30 天）→ L1（周摘要）→ L2（月摘要）→ L3（年摘要）折叠的 bucket-seal cascade。模式借鉴自 tinyhumansai/openhuman Memory Tree（`gitbooks/features/obsidian-wiki/memory-tree.md`）。v1.8.7 不实施 —— spec 冻结作为 v2.0 架构锚点；archiver 行为相对 v1.8.6 不变。
source_attribution: tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/obsidian-wiki/memory-tree.md（三树 / L0→L1 cascade seal / hotness 驱动 topic 物化）
introduced_in: v1.8.7（仅 spec）
referenced_by:
  - references/wiki-spec.md（v2.0 方向引用）
  - references/session-index-spec.md（v2.0 方向引用）
  - meta/rfc/v1.8.7-openhuman-borrowed-patterns.md §2.6 A1
---

# Memory Tree 规范（提案 · v1.9 / v2.0 目标）

> **状态：仅提案**。v1.8.7 ship 本 spec 作为未来方向锚点。`archiver` 行为相对 v1.8.6 不变。用户运行时不存在 L0/L1/L2/L3 目录布局。无 cascade seal 逻辑运行。本 spec 冻结让未来实施有清楚目标 —— 这些数据结构和阈值的验证需要在 Jason 真实 second-brain 中跑数周/月，v1.8.7 dev 周期不包含。

## 为什么 cascade seal 架构（动机）

当前 lifeos sessions/wiki 结构（v1.8.6 时）：

- `meta/sessions/<sid>.md` —— 扁平目录，所有 session 永远累积
- `meta/wiki/<topic>/<entry>.md` —— 每话题扁平，无自动压缩
- `meta/concepts/<concept>.md` —— 扁平带 hotness 计数但无派生摘要文件

多年累积后的问题：

- `archiver` 读"最近 30 天"OK；读"最近 2 年"变贵
- `hippocampus` 在数千 session 上扩散激活线性变慢
- 用户浏览 `meta/sessions/` 看到 1000+ 文件无导航
- 经历 50 个 session 成长的 wiki 条目没有紧凑的"这概念现在啥意思"摘要

OpenHuman 的 Memory Tree 用 L0 → L1 → L2 cascade 摘要解决这个。借鉴模式（不借鉴实现 —— OpenHuman 用 SQLite，lifeos 按 DR-10 保持 md-only）。

## 提案布局

```
meta/sessions/
├── L0/                          # 原始 session，最近 30 天
│   ├── 2026-05-25-<sid>.md
│   └── ...
├── L1-weekly/                   # 周摘要，最近 12 周（~3 个月）
│   ├── 2026-W21.md              # 2026 年第 21 周 —— 该周 L0 sessions 的摘要
│   └── ...
├── L2-monthly/                  # 月摘要，最近 12 个月
│   ├── 2026-05.md
│   └── ...
└── L3-yearly/                   # 年摘要，所有年份
    ├── 2026.md
    └── ...
```

`meta/wiki/`（已 seal wiki 条目）和 `meta/concepts/`（canonical concept 卷积）用同样模式。

## L0 → L1 cascade seal 算法

```
每次 archiver Adjourn（v1.9 / v2.0 时）：

1. 检查 L0 buffer 状态：
   - 计数 meta/sessions/L0/ 中文件
   - 检查最旧文件时间戳

2. "seal L0 → L1" 触发条件：
   - Buffer 数 ≥ 30 sessions，或
   - 最旧 L0 session > 30 天

3. 触发 seal 时：
   a. 确定被 seal 的周（L0 中含 >0 session 的最旧周）
   b. 读该周所有 L0 session 文件
   c. 用 sealing prompt 调 chat model → 产出周摘要
   d. 写 meta/sessions/L1-weekly/<YYYY>-W<NN>.md
   e. 移已 seal 的 L0 文件到 meta/sessions/_archive/L0-pre-seal/
   f.（不删除；保留供审计）

4. L1 buffer 达阈值时 cascade 到 L2：
   - L1 buffer 数 ≥ 12 周摘要（~3 个月），seal 最旧月到 L2
   - 同程序：读该月 L1 weeklies → 生成 L2 monthly → 移已 seal 的 L1 到归档

5. L2 达 12 月摘要时 cascade 到 L3 yearly
```

## Buffer 阈值（理由）

| 层 | 触发下一层 seal 的阈值 | 理由 |
|----|---------------------|------|
| L0 → L1 | 30 sessions 或 最旧 30 天 | 匹配"上个月"认知视野；archiver 自由读 L0 |
| L1 → L2 | 12 周摘要（~3 个月） | 季度是自然 review 单位 |
| L2 → L3 | 12 月摘要 | 年是最大实用认知单位 |
| L3 → (无) | 永不进一步 seal | 年是顶 —— 无 L4 除非 lifeos 变成代际 |

Buffer 计数可在实施时调整；重要的是 cascade 结构。

## Flush_stale（强制 seal 部分 buffer）

如果 buffer 坐太久没达阈值（如用户休假 6 个月，L0 只有 5 sessions），仍然强制 seal：

- L0 → L1 强制 seal：任何 L0 文件超过 60 天（正常阈值 2x）
- L1 → L2 强制 seal：任何 L1 周摘要超过 180 天
- L2 → L3 强制 seal：任何 L2 月摘要超过 24 月

防止 stale-buffer 病态 —— 半个周永远坐在 L0。

## Sealing prompt（LLM 驱动）

每层 seal 用层特定 prompt：

- **L0 → L1（周摘要）**："摘要本周 session。提取：所做决定、反复主题、未解问题、激活的关键概念。目标长度：800-1500 tokens。"
- **L1 → L2（月摘要）**："从这些周摘要写月度回顾。识别：月度主题、硬化/软化的决定、跨过 canonical 阈值的概念激活、反复出现的人。目标：1500-2500 tokens。"
- **L2 → L3（年摘要）**："从月摘要生成年度回顾。识别：年度核心叙事、最长未解线、SOUL 演化证据、战略线变化。目标：3000-5000 tokens。"

Prompt 位于 `pro/seal-prompts/L0-to-L1.md` 等（位置 TBD，v1.8.7 不建）。

## v1.8.7 **不**做什么

明确：

- ❌ 不创建 `meta/sessions/L0/` 目录（既有扁平布局保留）
- ❌ 不加 archiver cascade seal 逻辑
- ❌ 不建 seal prompt 文件
- ❌ 不自动生成 L1/L2/L3
- ❌ 不建既有 session 的迁移脚本

v1.8.7 **做**：
- ✅ 把本 spec 冻结为 `status: proposal`
- ✅ 在 `wiki-spec.md` + `session-index-spec.md` 加引用指向本 spec 作 v2.0 方向
- ✅ 保持可建未来实施目标

## 开放问题（实施 RFC 中解决）

以下故意 **不** 在本提案中解决 —— 它们需要真实数据验证：

1. L3 yearly 应进一步 cascade 吗（十年级？终生）？大概不，但 3 年积累后检查
2. 如何在 cascade 中处理 `meta/snapshots/soul/` SOUL 快照 —— 独立节奏还是集成？
3. L1 周摘要写入 vault（Obsidian 可见）还是留在 `meta/sessions/`（dev 内部）？
4. 当已 seal 的 L1/L2 文件与新上下文 session 冲突（用户引用"那周 5 月"但 L1 已 paraphrase 实际发生），如何恢复 provenance？L0 归档路径必须保持可达
5. 成本校准：~$0.50-$2 一个 L1 周摘要（1500 tokens 在前沿模型费率），~$2-$10 一个 L2 月度。活跃用户年成本：$300-$800/年的 LLM 账单仅 sealing。值吗？

这些问题是 v1.8.7 保持仅 spec 的原因。真实数据试用回答它们。

## 迁移路径（未来 v1.9/v2.0 实施时）

未来版本实施时：

1. 加新目录不动既有扁平布局
2. 跑一次 backfill：`/seal-backfill` slash 命令走既有扁平 `meta/sessions/` 以 append-only 方式产生 L1/L2/L3
3. Backfill 后，未来 archiver Adjourn 跑增量 seal
4. 既有文件留在 `meta/sessions/<sid>.md` 路径（不移动）作向后兼容 —— 只新 session 直接进 L0 buffer

本迁移非破坏性可逆。

## 引用

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.6 A1
- 模式来源：`tinyhumansai/openhuman` `gitbooks/features/obsidian-wiki/memory-tree.md`（三树 / L0→L1 cascade seal）
- 实施说明：OpenHuman 用 SQLite `memory_tree/chunks.db` + tokio task pool。lifeos 按 DR-10（`SKILL.md` HARD RULE）保持 md-only —— 上述目录布局是 lifeos 基底
- 配套：`references/concept-spec.md` §Hotness 阈值（cascade seal 触发 + hotness 物化是姊妹概念）
