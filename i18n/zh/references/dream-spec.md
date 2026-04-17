# DREAM 规范

DREAM 是系统的离线记忆处理机制——灵感来自人类的睡眠周期。它作为 **ARCHIVER（`pro/agents/archiver.md`）的 Phase 3** 在每次散朝时运行，扫描过去 3 天的活动，进行整理、巩固和发现。

> **注意**：DREAM 不是独立 agent。它在 v1.4.4 被并入 ARCHIVER。本规范定义三个阶段；ARCHIVER 将其集成到收尾流程中。

## 触发条件

```
用户说 "退朝" / "adjourn" / "終わり"
    ↓
ARCHIVER：Phase 1 归档 → Phase 2 知识提取
    ↓
ARCHIVER：Phase 3 DREAM（运行下方三个阶段）
    ↓
梦境报告写入 _meta/journal/{date}-dream.md
    ↓
ARCHIVER：Phase 4 同步（git + Notion）→ 会话结束
```

如果 DREAM 失败或超时 → 记录警告到 `_meta/sync-log.md`，不阻塞会话结束。

---

## 范围

**默认：过去 3 天（72 小时）内修改的文件。** 如果 3 天内无任何变动，自动扩大到"上次做梦以来"（读取最近一份 `_meta/journal/*-dream.md` 的日期）。如果没有梦境报告，回退到最近 7 天。

检测方法：
- GitHub 后端：`git log --since="3 days ago" --name-only --format=""` → 如为空，`git log --since="{上次做梦日期}" --name-only --format=""`
- GDrive 后端：`modifiedTime > 3_days_ago` → 如为空，`modifiedTime > 上次做梦日期`
- Notion 后端：`last_edited_time > 3_days_ago` → 如为空，`last_edited_time > 上次做梦日期`

---

## 三个阶段

灵感来自人类的睡眠结构：

### Stage N1-N2：整理与归档

**人类等效**：浅睡眠——大脑将当天的经历分类整理。

扫描最近 3 天的未完成事项：
- `inbox/` 中尚未分类的条目 → 建议目标项目/领域/wiki
- `_meta/journal/` 中可提取洞见的条目 → 建议更新 `user-patterns.md`
- `projects/*/tasks/` 中已过期或重复的任务 → 标记清理
- 孤立文件（已创建但未从任何 index.md 链接） → 标记

对每项发现进行分类：
- **可自动修复**（如缺失的 index 条目）→ 记录在报告中
- **需要用户决策**（如分类这条 inbox 条目）→ 添加到建议行动

### Stage N3：深度巩固

**人类等效**：深度睡眠——重要记忆从短期转移到长期存储。

N3 提出两个问题：
- **Q1（关于人）**：本次 session 有没有关于用户本人的新发现？→ SOUL 候选
- **Q2（关于事）**：本次 session 有没有下次遇到同类问题可以直接复用的结论？→ Wiki 候选

从最近 3 天提取更深层的模式：
- 决策中的可复用结论 → 提出 wiki 候选（见下方 Wiki 候选格式）
  **去重**：检查最近的 outbox manifest——如果 `wiki: N`（N > 0），该 session 的散朝流程已提取了 wiki 候选。只关注散朝流程可能遗漏的结论。不要重复提议。
- 扫描 wiki/INDEX.md（若存在）：新证据支持已有条目 → 提出 evidence_count 更新；新证据反驳已有条目 → 提出 challenges 更新
- 需根据新证据更新的 `user-patterns.md` 条目 → 提议变更
- **SOUL.md 候选条目** → 提议新条目或更新现有条目（见下方 SOUL 候选格式）

### Stage REM：创意连接

**人类等效**：REM 睡眠——大脑在不相关的记忆之间建立意外连接。这是梦境发生的地方，也是洞见涌现的地方。

此阶段没有检查清单——让数据自己说话：
- **跨项目关联**：在项目 A 中学到的东西是否适用于项目 B？
- **行为-价值对齐**：如果 SOUL.md 存在，近期行为是否与陈述的价值观一致？
- **维度盲点**：哪些生活维度在近期决策中完全缺席？
- **意外洞见**：什么模式或连接会让用户感到惊讶？

质量优于数量。1-3 个真实洞见。如果没有非显而易见的发现，如实说明——不要捏造。

---

## 自动触发的行动 (REM)

当 REM 发现模式时，DREAM 自动执行以下行动——无需用户确认。每个触发器都有**硬性阈值**（定量规则）和**软性信号**（LLM 定性线索）。`mode: hard` 表示阈值自动满足；`mode: soft` 表示 LLM 检测到超出阈值的定性信号，自动行动需要 AUDITOR 审核。

所有触发器均受 **24 小时反重复抑制**——如果相同触发器在过去 24 小时内已触发（查 `_meta/journal/*-dream.md`），则跳过。

#### 1. new-project-relationship

- **数据源**：`projects/*/index.md` 战略字段，`_meta/strategic-lines.md`
- **硬性阈值**：自上次梦境报告以来检测到新的跨项目依赖或瓶颈边
- **软性信号**：近期决策隐式引用了另一个项目，但无正式战略关联
- **自动行动**：写 STRATEGIC-MAP 候选 + 下次简报显眼位置展示
- **反重复**：若过去 24 小时内已触发则抑制

#### 2. behavior-mismatch-driving-force

- **数据源**：过去 3 天的决策 + SOUL.md driving_force 维度
- **硬性阈值**：≥2 个近期决策与陈述的 driving_force 矛盾
- **软性信号**：用户在执行 driving_force 对齐路径时表达不适或犹豫
- **自动行动**：注入下次 ADVISOR 简报输入
- **反重复**：若过去 24 小时内已触发则抑制

#### 3. wiki-contradicted

- **数据源**：`wiki/**/*.md`、近期决策、新证据笔记
- **硬性阈值**：≥1 条新证据直接反驳现有 wiki 结论
- **软性信号**：用户语气从确定转为怀疑，主题涉及 wiki 已覆盖内容
- **自动行动**：该 wiki 条目 `challenges: +1`
- **反重复**：若同一条目在过去 24 小时内已被挑战则抑制

#### 4. soul-dormant-30d

- **数据源**：SOUL.md `last_validated` 时间戳
- **硬性阈值**：`last_validated` 超过 30 天的维度且 `confidence ≥ 0.5`
- **软性信号**：（无——纯基于时间）
- **自动行动**：简报警告（"⚠️ [维度] 30+ 天未激活"）
- **反重复**：若过去 24 小时内已触发则抑制

#### 5. cross-project-cognition-unused

- **数据源**：`wiki/INDEX.md`、跨项目的近期决策
- **硬性阈值**：≥1 条直接适用于近期决策的 wiki 条目未被引用
- **软性信号**：用户在重新推导已在其他项目 wiki 中确立的结论
- **自动行动**：下次 DISPATCHER 强制注入相关 wiki 条目
- **反重复**：若同一条目在过去 24 小时内已被标记则抑制

#### 6. decision-fatigue

- **数据源**：过去 3 天的决策时间戳 + REVIEWER 评分
- **硬性阈值**：24 小时内 ≥5 个决策 且 后半段平均分 ≤ 前半段 - 2
- **软性信号**：用户在会话中表达疲劳（"whatever" / "fine" / "随便" / "まあいい"）
- **自动行动**：下次简报标记"今日不做重大决策"建议
- **反重复**：若过去 24 小时内已触发则抑制

#### 7. value-drift

- **数据源**：SOUL.md 证据/挑战历史 + 过去 30 天的决策
- **硬性阈值**：维度在 30 天内累积 ≥3 挑战且 ≤1 新支持证据
- **软性信号**：用户对某个价值的表述随时间转变（如"安全感"→"自由"）
- **自动行动**：自动提议 SOUL 维度修订
- **反重复**：若同一维度在过去 24 小时内已被修订则抑制

#### 8. stale-commitment

- **数据源**：用户说"我会 X"的决策 + 任务完成状态
- **硬性阈值**：承诺发言 ≥30 天前 且 无关联任务完成 / 无后续决策
- **软性信号**：用户在后续会话中回避提及该主题
- **自动行动**：下次简报唤起（"你说过要做 X——进展如何？"）
- **反重复**：若同一承诺在过去 24 小时内已被唤起则抑制

#### 9. emotional-decision

- **数据源**：决策会话日志 + 用户表达模式
- **硬性阈值**：≥2 个近期决策在带有强情绪标记的会话中做出
- **软性信号**：决策阶段标点夸张、回复简短、话题快速切换
- **自动行动**：下次 REVIEWER 强制加"情绪状态检查"维度
- **反重复**：若过去 24 小时内已触发则抑制

#### 10. repeated-decisions

- **数据源**：`_meta/decisions/*.md` + 项目决策历史
- **硬性阈值**：同一问题/主题决定 ≥3 次且中间无执行
- **软性信号**：用户改写问题措辞以避免识别为重复
- **自动行动**：下次简报提示（"你又在决定 X——是在回避承诺吗？"）
- **反重复**：若过去 24 小时内已触发则抑制

所有标志都以结构化的 `triggered_actions` YAML 块写入 `_meta/journal/{date}-dream.md`。RETROSPECTIVE 在下次上朝时读取并在晨报中呈现相关标志。

---

## SOUL 候选格式

当 DREAM 发现值得记录在 SOUL.md 中的价值模式时：

```
🌱 SOUL Candidate:
- Dimension: [名称]
- Observation: [在数据中观察到的内容]
- Evidence:
  - [日期] [决策/行为]
  - [日期] [决策/行为]
- Proposed entry:
  - What IS: [观察到的模式]
  - What SHOULD BE: [待用户确认]
  - Gap: [如果从数据中可以看出]
```

通过的候选以置信度 0.3 自动写入 SOUL.md，"What SHOULD BE"字段留空等用户后续填写。用户可随时自由编辑或删除，或在下次上朝说"撤销最近 SOUL"回滚。

---

## Wiki 自动写入（无需用户确认）

当 DREAM 在 N3 阶段发现可复用结论时，应用 `references/wiki-spec.md` 中定义的 6 项自动写入标准与隐私过滤器：

1. 跨项目可复用
2. 关于世界而非关于你
3. 零个人隐私
4. 事实或方法论
5. 多个证据点（≥2 个独立）
6. 与现有 wiki 不矛盾

如果全部 6 项通过 → 直接自动写入 `wiki/{domain}/{topic}.md`。主上下文中不需要用户确认。

**用于评估的内部候选结构**：

```
📚 Wiki 自动写入（内部）：
- Domain: [领域名]
- Topic: [简短标识]
- Conclusion: [一句话——可复用的结论]
- Evidence:
  - [日期] [决策/行为] — [描述]
  - [日期] [决策/行为] — [描述]
- Applicable when: [在什么场景下应想起这条]
- Criteria check: [6/6 通过，或 X/6 → 丢弃并注明原因]
- Privacy filter: [剥离了什么，或"无需剥离"]
```

**初始置信度**：
- 3+ 个独立证据点 → 0.5
- 恰好 2 个证据点 → 0.3
- 1 个或更少证据 → 丢弃

对已有 wiki 条目，直接自动更新：

```
📚 Wiki 更新（自动）：
- Entry: wiki/[domain]/[file].md
- Change: evidence_count +1（或 challenges +1）
- New evidence: [日期] [发生了什么]
```

用户事后调整 wiki（删除文件 = 废弃；"撤销最近 wiki" = 回滚）。完整的自动写入规范见 `references/wiki-spec.md`。

---

## 输出格式

写入 `_meta/journal/{date}-dream.md`：

```yaml
---
type: journal
journal_type: dream
date: YYYY-MM-DD
scope_files: N
stages: [N1-N2, N3, REM]
soul_candidates: N
wiki_candidates: N
triggered_actions:
  - trigger_id: 6
    trigger_name: "decision-fatigue"
    mode: "hard"          # or "soft"
    detection:
      hard_signals:
        - "6 decisions in 18 hours"
        - "avg score 7.5 → 4.2"
      soft_signals: []
    action: "flag-next-briefing"
    surfaces_at: "next-start-session"
    auditor_review: false  # true if mode=soft
---
```

`mode` = **hard** 表示阈值自动满足；**soft** 表示 LLM 检测到超出阈值的定性信号，需要 AUDITOR 审核后自动行动才在下次简报中呈现。

```markdown
## 💤 Dream Report · YYYY-MM-DD

### N1-N2 · Organize & Archive
- [发现及建议行动]

### N3 · Deep Consolidation
- [提取的模式、wiki 建议、模式更新]

### REM · Creative Connections
- [跨领域洞见、价值-行为观察]

### 🌱 SOUL Candidates
- [提议的条目，如有——或"无新候选条目"]

### 📚 Wiki Candidates
- [提议的条目或更新，如有——或"无新知识候选"]

### 📋 Suggested Actions
- [具体行动，供用户在下次上朝时审阅]
```

---

## 晨报集成

下次上朝，RETROSPECTIVE 读取最新未呈现的梦境报告，并在晨报中包含：

```
💤 上次会话系统做了一个梦：
- [1-3 行关键发现摘要]
- [自动写入的 SOUL 维度，如有，等待"What SHOULD BE"输入]
- [自动写入的 Wiki 条目路径，如有；用户可删除废弃]
```

呈现后，将梦境报告标记为"已呈现"，使其不再显示。

---

## 约束

- **3 天范围是硬性限制** — 不扫描更早的文件，即使它们看起来相关
- **不直接修改 SOUL.md** — 只提议候选条目（SOUL 自动写入属于 archiver Phase 2，不属于 DREAM）
- **Wiki 在严格标准下自动写入** — 全部 6 项自动写入标准通过时直接写入（见 wiki-spec.md）；否则丢弃
- **不直接修改 user-patterns.md** — 只提议更新
- **简洁** — 梦境报告应为 20-50 行，而非 500 行
- **诚实** — "无重大发现"是一个有效的梦境。不要捏造洞见
- **不阻塞** — 如果 DREAM 失败，会话仍正常结束
