# 三阶段详解

DREAM 的三个阶段对应人类睡眠的三个阶段。每一段都有明确的职责、输入、输出，以及**反重复规则**——保证阶段之间不抢活、不漏活。

## Stage N1-N2 · 整理与归档（Light Sleep）

**人类对应**：浅睡——大脑把当天的经验分类、打标签、放回正确的位置。

### 职责

在最近 3 天的变更集里，找出"还没归位"的东西。

### 扫描清单

1. **`inbox/` 里未分类的项**
   - 这是什么？——你快速丢进来的想法、链接、片段
   - N1-N2 问：这东西属于哪个 project？area？或者该进 wiki？
   - 输出：建议目标位置，等你下次 session 确认

   例子：`inbox/2026-04-18-book-idea.md` → "可能属于 projects/writing/new-book"

2. **`_meta/journal/` 里有提取价值的条目**
   - 你或 ADVISOR 写过的反思、观察
   - N1-N2 问：里面有没有可以抽出来的行为模式？
   - 输出：建议 `user-patterns.md` 更新（**只是建议，不直接改**）

3. **`projects/*/tasks/` 里过期或重复的任务**
   - 过了 due date 的任务
   - 同一件事写了两遍
   - 明显已经完成但状态还是 pending
   - 输出：标记清理列表

4. **孤立文件（orphan files）**
   - 文件在那里，但没有任何 index.md 引用它
   - 典型例子：你在项目里开了一个 `notes.md`，但 `projects/x/index.md` 不知道它存在
   - 输出：标记出来，让你下次决定：加入索引 or 归档 or 删除

### 分类

每条发现，N1-N2 打一个标签：

- **Auto-fixable**（可自动修复）：比如"index 里漏了一个引用" → 记录在报告里
- **Needs user input**（需要用户输入）：比如"这个 inbox item 该归到哪" → 进入下次 session 的 Suggested Actions

### 不做的事情

- 不提取 wiki 候选（那是 N3 的活）
- 不做跨项目联想（那是 REM 的活）
- 不直接动 `user-patterns.md`、`SOUL.md`（只提议）

---

## Stage N3 · 深度固化（Deep Sleep）

**人类对应**：深睡——神经科学研究表明，这个阶段是记忆从海马体（短期）迁移到皮层（长期）的关键窗口。

### 职责

从最近 3 天的数据里抽出两类东西：

- **关于"这个人"**的价值/原则观察 → SOUL 候选
- **关于"世界"**的可复用结论 → Wiki 候选

### 读取

- 最近 3 天所有新/改的 decisions
- 当前的 `user-patterns.md` 和 `SOUL.md`
- `wiki/INDEX.md`（如果存在）

### N3 的两个问题

#### Q1（关于这个人）：这次 session 揭示了什么？

扫描 decisions 里反复出现的模式，寻找：
- 价值倾向（"我更看重 X 而不是 Y"）
- 原则表达（"我宁可 X，也不 Y"）
- 生活优先级的新信号

如果发现一个维度，且有 ≥2 个 decisions 作为证据 → 写一个 SOUL 候选。

**SOUL 候选格式**：

```
🌱 SOUL Candidate:
- Dimension: [名称]
- Observation: [在数据里观察到了什么]
- Evidence:
  - [date] [decision 或行为]
  - [date] [decision 或行为]
- Proposed entry:
  - What IS: [观察到的模式]
  - What SHOULD BE: [留空 — 由用户填]
```

通过的候选会自动写入 SOUL.md，初始置信度 **0.3**（低位开始——让证据/挑战随时间调整）。"What SHOULD BE" **故意留空**——这是关于"想成为什么样的人"，必须由用户自己填。

#### Q2（关于世界）：这次 session 产出了什么可复用的东西？

扫描 decisions、advisor 报告、auditor 报告，寻找"下次遇到类似情况可以复用的结论"。

**反重复规则**：

Phase 2 已经扫描过当前 session 的材料，把符合条件的 wiki 候选自动写入了。N3 的任务是**补充 Phase 2 遗漏的部分**——通常是需要 3 天跨度才能看出的模式。

验证方式：读取 `_meta/outbox/{session_id}/manifest.md`，如果 `wiki: N` 且 N > 0，说明 Phase 2 已经处理过，N3 只做增量。

Wiki 候选走 `references/wiki-spec.md` 的 6 条自动写入标准：

1. 跨项目可复用
2. 关于世界，不是关于你
3. 零个人隐私
4. 事实或方法（不是感受/观点）
5. ≥2 条独立证据
6. 不与现有 wiki 条目冲突

6 条全过 → 直接写入 `wiki/{domain}/{topic}.md`，无需用户确认。
不过 → 丢弃，不保留"低置信度 wiki"。

#### Q3（补充）：现有条目需要更新吗？

扫描 `wiki/INDEX.md`：
- 新证据支持现有条目 → `evidence_count +1`
- 新证据挑战现有条目 → `challenges +1`
- `user-patterns.md` 里的条目有新证据 → 提议更新

### 不做的事情

- 不重复 Phase 2 已经提取的东西
- 不直接改 SOUL.md 的 "What SHOULD BE"（留空让用户填）
- 不提议低于 2 条证据的 wiki（丢弃，不存"低置信候选"）

---

## Stage REM · 创意连接（Dream Sleep）

**人类对应**：REM 睡眠——大脑在不相关的记忆之间建立出人意料的连接。这是梦发生的阶段，也是灵感涌现的阶段。

### 职责

让数据说话。没有检查清单——**这是有意的**。检查清单会诱导系统"凑数"，REM 的价值在于发现未被预设的东西。

### 四个内部提问

REM 不是 open-ended——有四个方向：

1. **跨项目联想**（cross-project association）
   - 项目 A 学到的东西，能不能用到项目 B？
   - 例：在 "创业" 项目里学到"用户访谈优先选 5 个极端用户"，能不能用到 "写书" 项目的读者调研？

2. **行为 × 价值**（behavior-value alignment）
   - 如果 SOUL.md 存在，最近的行为和 SOUL 里声明的价值一致吗？
   - 例：SOUL 说"家庭优先"，但最近 3 天所有决策都围绕工作 → 冲突信号

3. **维度盲点**（dimension blind spots）
   - 最近的决策完全忽视了哪个生活维度？
   - 例：最近 3 天没有任何关于健康/关系/学习的决策 → 盲点

4. **意外洞察**（unexpected insight）
   - 什么模式或连接会让用户惊讶？
   - 例：你在项目 A 里做决策速度很快，在项目 B 里反复拖延 → 模式

### 10 个自动触发器

REM 还会机械地评估 10 个触发器（详见 `10-auto-triggers.md`）。每一个都有硬阈值（数学公式）+ 软信号（LLM 定性观察）。

硬阈值触发 → `mode: hard`，直接执行。
软信号触发 → `mode: soft`，需要 AUDITOR review 才生效。

所有触发受 **24 小时反垃圾抑制**——同一触发器 24 小时内不重复触发。

### 诚实原则

**质量 > 数量。**

- 1-3 个真实洞察
- 如果没有非显然的发现 → 直接说"light sleep — no significant patterns"
- **绝对不允许编造洞察来充场面**

这是硬规则。REM 的价值在于它愿意说"没发现"。一个会编故事的 REM 反而会污染 SOUL、污染 wiki。

---

## 阶段之间的反重复规则

| 阶段 | 主要职责 | 避免抢 |
|------|---------|--------|
| Phase 2（archiver）| 当前 session 的 wiki/SOUL 自动写入 | - |
| N1-N2 | 整理归档（inbox/任务/孤立文件）| 不提取 wiki/SOUL |
| N3 | 深度固化（3 天范围的 wiki/SOUL 候选）| 不做 Phase 2 已经做过的（读 manifest 确认）|
| REM | 创意连接 + 10 个触发器 | 不重复 N3 已经提议的候选 |

核心机制：**读取 outbox manifest**。Phase 2 写完之后，manifest.md 记录了 `wiki: N, soul: M, strategic: K`。N3/REM 读这个数字，只做增量。

---

## 最终写出

三阶段跑完之后，ARCHIVER 把结果写进 `_meta/journal/{date}-dream.md`，同时把 `triggered_actions` YAML 块暴露给下一次 RETROSPECTIVE 读取。

接下来就是 Phase 4（git 同步 + Notion 同步）→ session 结束。

下次 session start 时，这些结果会出现在简报的固定位置。怎么读，看 `reading-dream-reports.md`。
