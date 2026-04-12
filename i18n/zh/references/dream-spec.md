# DREAM 规范

DREAM 是系统的离线记忆处理机制——灵感来自人类的睡眠周期。它在每次退朝后自动运行，扫描过去 3 天的活动，进行整理、巩固和发现。

## 触发条件

```
用户说 "退朝" / "adjourn" / "終わり"
    ↓
早朝官：归档 + 同步 + 推送（模式 4）
    ↓
早朝官：启动 DREAM agent（最后一步）
    ↓
DREAM 运行三个阶段
    ↓
梦境报告写入 _meta/journal/{date}-dream.md
    ↓
会话结束
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

用户将在下次上朝时确认、编辑或拒绝。

---

## Wiki 候选格式

当 DREAM 发现值得记录到 wiki/ 的可复用结论：

```
📚 Wiki 候选：
- Domain: [领域名]
- Topic: [简短标识]
- Conclusion: [一句话——可复用的结论]
- Evidence:
  - [日期] [决策/行为] — [描述]
  - [日期] [决策/行为] — [描述]
- Applicable when: [在什么场景下应想起这条]
```

对于已有 wiki 条目，提议更新：

```
📚 Wiki 更新：
- Entry: wiki/[domain]/[file].md
- Change: evidence_count +1（或 challenges +1）
- New evidence: [日期] [发生了什么]
```

用户将在下次上朝时确认、编辑或拒绝。

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
---
```

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

下次上朝，早朝官读取最新未呈现的梦境报告，并在晨报中包含：

```
💤 上次会话系统做了一个梦：
- [1-3 行关键发现摘要]
- [SOUL 候选条目，如有，供用户确认]
```

呈现后，将梦境报告标记为"已呈现"，使其不再显示。

---

## 约束

- **3 天范围是硬性限制** — 不扫描更早的文件，即使它们看起来相关
- **不直接修改 SOUL.md** — 只提议候选条目
- **不直接修改 wiki/** — 只提议候选和更新
- **不直接修改 user-patterns.md** — 只提议更新
- **简洁** — 梦境报告应为 20-50 行，而非 500 行
- **诚实** — "无重大发现"是一个有效的梦境。不要捏造洞见
- **不阻塞** — 如果 DREAM 失败，会话仍正常结束
