# DREAM 规范

DREAM 是系统的离线记忆处理——借鉴人类睡眠周期设计。它作为 **ARCHIVER 的 Phase 3**（`pro/agents/archiver.md`）在每次会话结束时运行，扫描最近 3 天的活动进行整理、巩固与发现。

> **注意**：DREAM 不是独立 agent。v1.4.4 中它被合并到 ARCHIVER。本规范定义三个阶段的逻辑；ARCHIVER 将它们整合到收尾流程。

## 触发

```
用户说 "退朝" / "adjourn" / "終わり"
    ↓
ARCHIVER: Phase 1 归档 → Phase 2 知识提取
    ↓
ARCHIVER: Phase 3 DREAM（运行下方三个阶段）
    ↓
Dream 报告写入 _meta/journal/{date}-dream.md
    ↓
ARCHIVER: Phase 4 同步（git + Notion） → 会话结束
```

若 DREAM 失败或超时 → 把警告记入 `_meta/sync-log.md`，不阻塞会话结束。

---

## 范围

**默认：最近 3 天（72 小时）内修改过的文件**。若最近 3 天没有文件修改，自动扩展到"自上次 dream 报告以来"（从最近的 `_meta/journal/*-dream.md` 读取日期）。若没有 dream 报告，fallback 到扫描最近 7 天。

检测方法：
- GitHub 后端：`git log --since="3 days ago" --name-only --format=""` → 若空，`git log --since="{last_dream_date}" --name-only --format=""`
- GDrive 后端：`modifiedTime > 3_days_ago` → 若空，`modifiedTime > last_dream_date`
- Notion 后端：`last_edited_time > 3_days_ago` → 若空，`last_edited_time > last_dream_date`

---

## 三个阶段

灵感来自人类睡眠架构：

### Stage N1-N2：整理与归档

**人类对应**：浅睡——大脑将当天经验分类。

扫描最近 3 天的松散末尾：
- `inbox/` 未分类项 → 建议目标 project / area / wiki
- `_meta/journal/` 有可提取洞察的条目 → 建议 `user-patterns.md` 更新
- `projects/*/tasks/` 过期或重复 → 标记清理
- 孤儿文件（已创建但未被任何 index.md 链接）→ 标记

每个发现分类为：
- **可自动修复**（如缺失的 index 条目）→ 记入报告
- **需用户输入**（如"请分类此 inbox 项"）→ 加入建议操作

### Stage N3：深度巩固

**人类对应**：深睡——重要记忆从短期移入长期。

N3 问两个问题：
- **Q1（关于人）**：这次会话是否揭示了关于用户的新信息？→ SOUL 候选
- **Q2（关于世界）**：这次会话是否产生了下次可复用的结论？→ Wiki 候选

从最近 3 天提取更深层模式：
- 从决策中提取可复用结论 → 提议 wiki 候选（见下方 Wiki Candidate 格式）
  **去重**：查看最近一次 outbox 的 manifest——若 `wiki: N`（N > 0），该会话的 adjourn 流程已提取过 wiki 候选。只关注 adjourn 漏掉的结论，不要重复提议
- 扫描 wiki/INDEX.md（若存在）：支持既有条目的新证据 → 提议 `evidence_count +1`；反对既有条目的新证据 → 提议 `challenges +1`
- 需要基于新证据更新的 `user-patterns.md` 条目 → 提议修改
- **SOUL.md 候选条目** → 提议新条目或对既有条目的更新（见下方 SOUL Candidate 格式）

### Stage REM：创造性连接

**人类对应**：REM 睡眠——大脑在无关记忆间做意外连接。梦在这里发生，洞察由此涌现。

本阶段没有清单——让数据说话：
- **跨项目关联**：在 Project A 学到的东西是否适用于 Project B？
- **行为-价值观对齐**：若 SOUL.md 存在，近期行为是否与既定价值观一致？
- **维度盲点**：最近决策中完全缺席的是哪些生活维度？
- **意外洞察**：什么模式或连接会让用户吃惊？

质重于量。1-3 条真实洞察。若没有非显而易见的发现，就说没有——**不要捏造**。

---

## 自动触发的动作（REM）

当 REM 发现模式时，DREAM 自动执行以下动作——**无需用户确认**。每个触发器有**硬阈值**（定量规则）和**软信号**（LLM 定性线索）。`mode: hard` 表示阈值被自动满足；`mode: soft` 表示 LLM 检测到阈值之外的定性信号，自动动作需 AUDITOR 审核。

所有触发器受 **24h 反垃圾抑制**——若同一触发器在过去 24 小时内已触发（根据 `_meta/journal/*-dream.md`），则跳过。

#### 1. new-project-relationship（新项目关系）

- **数据源**：`projects/*/index.md` 战略字段、`_meta/strategic-lines.md`
- **硬阈值**：自上次 dream 报告以来检测到新的跨项目依赖或瓶颈边
- **软信号**：最近决策隐式引用另一项目但无正式战略链接
- **自动动作**：写入 STRATEGIC-MAP 候选 + 标记下次简报显著显示
- **反垃圾**：24h 内已触发则抑制

#### 2. behavior-mismatch-driving-force（行为与驱动力不匹配）

- **数据源**：最近 3 天的决策 + SOUL.md 的 driving_force 维度
- **硬阈值**：≥2 条近期决策违背既定 driving_force
- **软信号**：用户在执行 driving_force 对齐路径时表达不适或犹豫
- **自动动作**：注入下次 ADVISOR 简报输入
- **反垃圾**：24h 内已触发则抑制

#### 3. wiki-contradicted（wiki 被反驳）

- **数据源**：`wiki/**/*.md`、最近决策、新证据笔记
- **硬阈值**：≥1 条新证据直接反驳既有 wiki 结论
- **软信号**：用户对某个 wiki 覆盖话题的语气从确定转为怀疑
- **自动动作**：给该 wiki 条目 `challenges: +1`
- **反垃圾**：同一条目 24h 内已被挑战则抑制

#### 4. soul-dormant-30d（SOUL 维度休眠 30 天）

- **数据源**：SOUL.md 的 `last_validated` 时间戳
- **硬阈值**：某维度 `last_validated` > 30 天 **且** `confidence ≥ 0.5`
- **软信号**：（无——纯时间判断）
- **自动动作**：标记简报警告（"⚠️ [维度] 30+ 天未激活"）
- **反垃圾**：24h 内已触发则抑制

#### 5. cross-project-cognition-unused（跨项目知识未被使用）

- **数据源**：`wiki/INDEX.md`、跨项目的近期决策
- **硬阈值**：≥1 条与近期决策直接相关的 wiki 条目未被引用
- **软信号**：用户在重新推导另一个项目的 wiki 中已确立的结论
- **自动动作**：标记下次 DISPATCHER 强制注入相关 wiki 条目
- **反垃圾**：同一条目 24h 内已标记则抑制

#### 6. decision-fatigue（决策疲劳）

- **数据源**：最近 3 天的决策时间戳 + REVIEWER 评分
- **硬阈值**：24h 内 ≥5 次决策 **且** 后半段平均分 ≤ 前半段 - 2
- **软信号**：用户在会话中表达疲劳（"whatever" / "fine" / "随便" / "まあいい"）
- **自动动作**：给下次简报加"建议今天不做重大决策"
- **反垃圾**：24h 内已触发则抑制

#### 7. value-drift（价值漂移）

- **数据源**：SOUL.md 的证据/反驳历史 + 最近 30 天的决策
- **硬阈值**：某维度在 30 天内累积 ≥3 条反驳 + ≤1 条新支持证据
- **软信号**：用户对某价值观的措辞随时间变化（如"安全" → "自由"）
- **自动动作**：自动提议 SOUL 维度修订
- **反垃圾**：同一维度 24h 内已修订则抑制

#### 8. stale-commitment（陈旧承诺）

- **数据源**：用户曾说 "I will X" 的决策 + 任务完成状态
- **硬阈值**：承诺声明 ≥30 天 **且** 无对应任务完成 / 无后续决策
- **软信号**：用户在后续会话中回避提及该话题
- **自动动作**：标记下次简报重新浮现（"你说过会做 X——发生了什么？"）
- **反垃圾**：同一承诺 24h 内已重新浮现则抑制

#### 9. emotional-decision（情绪化决策）

- **数据源**：决策会话日志 + 用户表达模式
- **硬阈值**：≥2 条近期决策在标记有强烈情绪标记的会话中做出
- **软信号**：决策阶段标点升级、回复简短、话题跳跃加速
- **自动动作**：标记下次 REVIEWER 加入强制"情绪状态检查"维度
- **反垃圾**：24h 内已触发则抑制

#### 10. repeated-decisions（重复决策）

- **数据源**：`_meta/decisions/*.md` + 项目决策历史
- **硬阈值**：同一问题/主题在中间无执行的情况下被决策 ≥3 次
- **软信号**：用户重新措辞问题以回避识别为重复
- **自动动作**：标记下次简报（"你又在决定 X——是不是在回避承诺？"）
- **反垃圾**：24h 内已触发则抑制

所有标记写入 `_meta/journal/{date}-dream.md` 的结构化 `triggered_actions` YAML 块。RETROSPECTIVE 在下次 Start Session 读取并在简报中呈现相关标记。

---

## SOUL 候选格式

当 DREAM 发现值得记录到 SOUL.md 的价值模式：

```
🌱 SOUL Candidate:
- Dimension: [名称]
- Observation: [数据中观察到的现象]
- Evidence:
  - [日期] [决策/行为]
  - [日期] [决策/行为]
- Proposed entry:
  - What IS: [观察到的模式]
  - What SHOULD BE: [由用户确认]
  - Gap: [若明显可见]
```

通过的候选在 confidence 0.3 自动写入 SOUL.md，"What SHOULD BE" 留空由用户后续填写。用户可任意编辑或删除，或在下次会话说 "undo recent SOUL" 回滚。

---

## Wiki 自动写入（无需用户确认）

当 DREAM 在 N3 阶段发现可复用结论时，应用 `references/wiki-spec.md` 定义的 6 条自动写入标准和隐私过滤器：

1. 跨项目可复用
2. 关于世界、不是关于你
3. 零个人隐私
4. 事实或方法
5. 多证据点（≥2 条独立）
6. 不与既有 wiki 冲突

若全部 6 条通过 → 直接写入 `wiki/{domain}/{topic}.md`。主上下文中无需用户确认。

**内部候选结构**用于评估：

```
📚 Wiki Auto-Write (internal):
- Domain: [domain 名]
- Topic: [短标识]
- Conclusion: [一句话——可复用的要点]
- Evidence:
  - [日期] [决策/行为] — [描述]
  - [日期] [决策/行为] — [描述]
- Applicable when: [什么场景下想起它]
- Criteria check: [6/6 通过 或 X/6 → 丢弃原因]
- Privacy filter: [去除了什么，或 "nothing to strip"]
```

**初始置信度**：
- 3+ 独立证据 → 0.5
- 恰好 2 条证据 → 0.3
- 1 条或以下 → **丢弃**

对于既有 wiki 条目，直接自动更新：

```
📚 Wiki Update (auto):
- Entry: wiki/[domain]/[file].md
- Change: evidence_count +1 （或 challenges +1）
- New evidence: [日期] [发生了什么]
```

用户事后介入（删除文件 = 退役；"undo recent wiki" = 回滚）。完整自动写入规范见 `references/wiki-spec.md`。

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
    mode: "hard"          # 或 "soft"
    detection:
      hard_signals:
        - "6 decisions in 18 hours"
        - "avg score 7.5 → 4.2"
      soft_signals: []
    action: "flag-next-briefing"
    surfaces_at: "next-start-session"
    auditor_review: false  # true 若 mode=soft
---
```

`mode` = **hard** 表示阈值自动满足；**soft** 表示 LLM 检测到阈值之外的定性信号，自动动作在下次简报中呈现前需 AUDITOR 审核。

```markdown
## 💤 Dream Report · YYYY-MM-DD

### N1-N2 · Organize & Archive
- [发现及建议操作]

### N3 · Deep Consolidation
- [抽取的模式、wiki 建议、模式更新]

### REM · Creative Connections
- [跨域洞察、价值-行为观察]

### 🌱 SOUL Candidates
- [提议条目；若无则 "No new candidates"]

### 📚 Wiki Candidates
- [提议条目或更新；若无则 "No new knowledge candidates"]

### 📋 Suggested Actions
- [用户在下次会话开始时可审阅的具体操作]
```

---

## 晨间简报整合

下次会话开始时，RETROSPECTIVE 读取最新未读 dream 报告，并在简报中包含：

```
💤 上次会话系统做了个梦：
- [1-3 行要点摘要]
- [等待用户填写 "What SHOULD BE" 的自动写入 SOUL 维度，如有]
- [自动写入的 Wiki 条目（含路径），如有；用户可删除退役]
```

呈现后标记 dream 报告为 "presented"，不再重复显示。

---

## 约束清单

- **3 天范围是硬性**——不扫描更早的文件，即使看起来相关
- **不直接修改 SOUL.md**——只提议候选（SOUL 自动写入限定在 archiver Phase 2，不在 DREAM）
- **Wiki 在严格条件下自动写入**——6 条标准全通过才直接写入（见 wiki-spec.md）；否则丢弃
- **不直接修改 user-patterns.md**——只提议更新
- **简洁**——dream 报告应为 20-50 行，而不是 500 行
- **诚实**——"无重大发现"是有效的梦。**不要捏造洞察**
- **不阻塞**——若 DREAM 失败，会话仍正常结束
