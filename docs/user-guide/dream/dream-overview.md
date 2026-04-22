# DREAM 概览

## DREAM 是什么

DREAM 是 Life OS 的"离线记忆处理系统"——灵感来自人类睡眠周期。每次你退朝（adjourn），系统会像大脑在夜里整理记忆那样，扫描最近 3 天的活动，做三件事：整理、巩固、发现。

**重要：DREAM 不是独立的 subagent。** 从 v1.4.4 起，它被并入 ARCHIVER，作为 ARCHIVER 的 **Phase 3** 执行。权威定义在 `references/dream-spec.md` 和 `pro/agents/archiver.md`。

## 为什么叫 DREAM

白天的 session 是"意识"：你做决策、讨论、执行。DREAM 是"潜意识"：在你关闭 session 之后，系统替你做以下事情——

- 把散落的东西归位（N1-N2）
- 把重要的东西从短期搬进长期（N3）
- 把不相关的东西连起来（REM）

这就是人睡着以后大脑在做的事。Life OS 把它 1:1 复刻成一个自动跑的流程。

## 触发

```
用户说"退朝" / "adjourn" / "終わり"
    ↓
ARCHIVER Phase 1: 归档 decisions/tasks/journal → outbox
    ↓
ARCHIVER Phase 2: 当次 session 的 wiki/SOUL 自动写入
    ↓
ARCHIVER Phase 3: DREAM（N1-N2 → N3 → REM）  ← 这里
    ↓
ARCHIVER Phase 4: git 同步 + Notion 同步
    ↓
Session 结束
```

不需要你手动触发 DREAM。只要你说了退朝，它就自动跑。

如果 DREAM 失败或超时：**不会阻断 session 结束**。警告写进 `_meta/sync-log.md`，你下次 session 会看到。

## 扫描范围（硬规则）

**默认：最近 3 天（72 小时）内修改过的文件。**

如果最近 3 天没有文件改动：自动扩展到"上一份 dream 报告之后"（读取最新 `_meta/journal/*-dream.md` 的日期）。

如果从来没有过 dream 报告：扫描最近 7 天作为兜底。

**不会扫描更老的文件，即使看起来相关。** 这是硬规则——DREAM 不是在做全盘分析，它是在做 3 天周期的记忆处理。

检测方式：
- GitHub 后端：`git log --since="3 days ago" --name-only`
- GDrive 后端：`modifiedTime > 3_days_ago`
- Notion 后端：`last_edited_time > 3_days_ago`

## 三阶段（人类睡眠类比）

### Stage N1-N2 · 整理归档

**人类对应**：浅睡——大脑把白天的经验按类别归位。

扫描最近 3 天：
- `inbox/` 里还没分类的东西 → 建议归到哪个项目/领域
- `_meta/journal/` 里有可提取洞察的条目 → 建议更新 `user-patterns.md`
- `projects/*/tasks/` 里过期或重复的任务 → 标记清理
- 创建了但没被任何 index.md 引用的孤立文件 → 标记

### Stage N3 · 深度固化

**人类对应**：深睡——重要记忆从短期存储搬到长期存储。

N3 问两个问题：
- **Q1（关于这个人）**：这次 session 有没有揭示用户新的特质？→ SOUL 候选
- **Q2（关于世界）**：这次 session 产出了哪些可复用的结论？→ Wiki 候选

注意：Phase 2 已经从当前 session 里提取过 wiki/SOUL。N3 **只补充 Phase 2 遗漏的部分**（读取 outbox manifest 的 `wiki: N` 字段确认），不重复提议。

### Stage REM · 创意连接

**人类对应**：快速眼动睡眠——大脑在不相关的记忆之间建立出人意料的连接。这是梦发生的地方，也是灵感涌现的地方。

REM 没有检查清单。让数据说话：
- 跨项目联想：项目 A 学到的东西能不能用到项目 B？
- 行为 × 价值：最近的行为和 SOUL 声明的价值一致吗？
- 维度盲点：最近的决策完全忽视了哪个生活维度？
- 意外洞察：什么模式会让用户惊讶？

REM 也会评估 10 个自动触发器（详见 `10-auto-triggers.md`）。

质量 > 数量。1-3 个真实洞察。如果没有非显然的东西浮现，就说没有——**不编造**。

## Dream 报告格式

写入 `_meta/journal/{date}-dream.md`：

```yaml
---
type: journal
journal_type: dream
date: 2026-04-20
scope_files: 27
stages: [N1-N2, N3, REM]
soul_candidates: 1
wiki_candidates: 0
strategic_candidates: 0
triggered_actions:
  - trigger_id: 6
    trigger_name: "decision-fatigue"
    mode: "hard"
    detection:
      hard_signals:
        - "6 decisions in 18 hours"
        - "avg score 7.5 → 4.2"
    action: "flag-next-briefing"
    surfaces_at: "next-start-session"
    auditor_review: false
---
```

```markdown
## 💤 Dream Report · 2026-04-20

### N1-N2 · Organize & Archive
- inbox/2026-04-19-idea.md 还没分类 → 建议归到 projects/product-x

### N3 · Deep Consolidation
- Phase 2 已提取 2 个 wiki 候选，N3 未发现遗漏

### REM · Creative Connections
- 最近 3 个 session 都在回避"健康"维度的决策

### 🌱 SOUL Candidates
- Dimension: decision-pace | Evidence: 3 次决策都在凌晨 → What IS: "夜间思考更清晰"

### 📚 Wiki Candidates (supplementary)
- All extracted in Phase 2

### 🗺️ Strategic Map Observations
- No changes

### 📋 Suggested Actions
- 下次 session 开始时确认"What SHOULD BE"
```

**保持简短**：20-50 行，不是 500 行。

## 硬规则约束

- **3 天范围是硬规则**——不扫描更老的文件
- **不直接修改 SOUL.md**——只提议候选（SOUL 自动写入属于 archiver Phase 2，不是 DREAM）
- **Wiki 在严格 6 条标准下才自动写入**（详见 `references/wiki-spec.md`）
- **不直接修改 user-patterns.md**——只提议更新
- **简洁性**：20-50 行，不是 500 行
- **诚实性**："没有重大发现"是合法的 dream。**不编造。**
- **不阻断**：DREAM 失败 ≠ session 失败

## 下次 session 怎么看到 DREAM 结果

下一次你说 start / 上朝 / 開始，RETROSPECTIVE 会读取最新的、未展示过的 dream 报告，在简报的固定位置（SOUL Health Report 之后、Strategic Overview 之前）显示：

```
💤 DREAM Auto-Triggers (from last session)

⚠️ Triggered Actions (auto-applied):
   · STRATEGIC-MAP updated: [project-A] →(cognition)→ [project-B]
   · ADVISOR will flag this session: "You said X but last 5 sessions focused on..."

💡 Recommendation: no major decisions today — you made 6 decisions in last 3 days
```

看完之后，这份报告就被标记为"已展示"，不会再出现。

## 相关文件

- `references/dream-spec.md`——权威 spec
- `pro/agents/archiver.md`——Phase 3 执行逻辑
- `docs/user-guide/dream/three-stages.md`——三阶段细节
- `docs/user-guide/dream/10-auto-triggers.md`——10 个自动触发器
- `docs/user-guide/dream/reading-dream-reports.md`——怎么读 dream 报告
