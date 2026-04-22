# 触发词全表（Trigger Words）

本文件汇总 Life OS 所有 9 个主题的触发词。每个触发词控制一项关键动作，部分触发词还能自动推断出要加载的主题。

## 通用规则

- **英文触发词始终可用**——无论当前主题是什么，"start" / "review" / "adjourn" 等都会触发对应动作
- **主题特定触发词**——激活某主题后，该主题定义的词（如"上朝"、"閣議開始"、"open session"）也可用
- **触发词识别发生在 ROUTER**——用户输入先经过 ROUTER，ROUTER 根据触发词决定是否载入 `pro/agents/*.md` 并启动对应 subagent
- **HARD RULE**：部分触发词（Start Session、Adjourn、Review）有固定的执行模板，ROUTER 必须严格遵守、不可自己代劳——见 SKILL.md 的 "Trigger Execution Templates (HARD RULE)"

---

## 7 个核心动作的触发词对照表

### 1. Start Session（开始会话）

| 主题 | 触发词 |
|------|--------|
| **通用（始终可用）** | `start` / `begin` |
| 🏛️ Roman Republic | `start` / `begin` / `convene` |
| 🇺🇸 US Government | `start` / `begin` / `convene` |
| 🏢 C-Suite（英文企业） | `start` / `begin` / `open session` |
| 🏛️ 三省六部 | `上朝` / `开始` / `start` / `begin` |
| 🇨🇳 中国政府 | `开始` / `开会` / `start` / `begin` |
| 🏢 公司部门（中文企业） | `开会` / `开始` / `start` / `begin` |
| 🏛️ 明治政府 | `閣議開始` / `はじめる` / `start` / `begin` |
| 🏛️ 霞が関 | `閣議開始` / `はじめる` / `start` / `begin` |
| 🏢 企業（日文企业） | `朝礼` / `はじめる` / `start` / `begin` |

**触发结果**：ROUTER 输出"🌅 [Starting session preparation — 18 steps]..."，并立即 Launch(retrospective) 以 Mode 0 运行。

### 2. Review（回顾）

| 主题 | 触发词 |
|------|--------|
| **通用（始终可用）** | `review` |
| 🏛️ Roman Republic | `review` / `report` |
| 🇺🇸 US Government | `review` / `brief me` |
| 🏢 C-Suite | `review` / `standup` / `check in` |
| 🏛️ 三省六部 | `早朝` / `复盘` / `review` |
| 🇨🇳 中国政府 | `汇报` / `复盘` / `review` |
| 🏢 公司部门 | `汇报` / `复盘` / `review` |
| 🏛️ 明治政府 | `報告` / `振り返り` / `review` |
| 🏛️ 霞が関 | `レビュー` / `振り返り` / `review` |
| 🏢 企業 | `報告` / `振り返り` / `review` |

**触发结果**：ROUTER 输出"🌅 [Starting review — briefing only]..."，并立即 Launch(retrospective) 以 Mode 2 运行（只读、不改数据）。

### 3. Adjourn（结束会话）

| 主题 | 触发词 |
|------|--------|
| **通用（始终可用）** | `adjourn` / `done` / `end` |
| 🏛️ Roman Republic | `adjourn` / `done` / `end` / `dismiss` |
| 🇺🇸 US Government | `adjourn` / `done` / `end` |
| 🏢 C-Suite | `adjourn` / `done` / `end` / `close session` |
| 🏛️ 三省六部 | `退朝` / `结束` / `adjourn` / `done` / `end` |
| 🇨🇳 中国政府 | `散会` / `结束` / `adjourn` / `done` / `end` |
| 🏢 公司部门 | `散会` / `结束` / `adjourn` / `done` / `end` |
| 🏛️ 明治政府 | `閣議終了` / `終わり` / `adjourn` / `done` / `end` |
| 🏛️ 霞が関 | `閣議終了` / `お疲れ` / `終わり` / `adjourn` / `end` |
| 🏢 企業 | `お疲れ` / `終わり` / `adjourn` / `done` / `end` |

**触发结果**：ROUTER 输出"📝 [Starting archive flow — 4 phases]..."，并立即 Launch(archiver) 以完整 4 阶段运行。archiver 返回后，编排器执行 Notion 同步（Step 10a）→ 会话结束。

**HARD RULE**：ROUTER 绝不能自己扫描会话提取 wiki/SOUL 候选，绝不能问用户"要保存哪些候选"——这些都是 archiver subagent 的内部工作。违反则 AUDITOR 会标记为流程违规。

### 4. Quick Analysis（快速分析）

| 主题 | 触发词 |
|------|--------|
| **通用（始终可用）** | `quick` / `quick analysis` |
| 🏛️ Roman Republic | `quick` / `quick analysis` |
| 🇺🇸 US Government | `quick` / `quick analysis` |
| 🏢 C-Suite | `quick` / `quick analysis` |
| 🏛️ 三省六部 | `快速分析` / `quick` |
| 🇨🇳 中国政府 | `快速分析` / `quick` |
| 🏢 公司部门 | `快速分析` / `quick` |
| 🏛️ 明治政府 | `至急` / `quick` |
| 🏛️ 霞が関 | `クイック` / `すぐ分析` / `quick` |
| 🏢 企業 | `至急` / `すぐ分析` / `quick` |

**触发结果**：ROUTER 跳过 PLANNER/REVIEWER/AUDITOR/ADVISOR，直接启动 1-3 个领域 agent，产出简要报告。适合不涉及决策的分析、研究、规划任务。

### 5. Debate（辩论）

| 主题 | 触发词 |
|------|--------|
| **通用（始终可用）** | `debate` |
| 🏛️ Roman Republic | `debate` / `comitia` |
| 🇺🇸 US Government | `debate` / `cabinet session` |
| 🏢 C-Suite | `debate` / `board discussion` |
| 🏛️ 三省六部 | `朝堂议政` / `debate` |
| 🇨🇳 中国政府 | `讨论` / `debate` |
| 🏢 公司部门 | `讨论` / `debate` |
| 🏛️ 明治政府 | `御前会議` / `debate` |
| 🏛️ 霞が関 | `討論` / `debate` |
| 🏢 企業 | `討論` / `debate` |

**触发结果**：启动 COUNCIL（跨域辩论）。通常在两个领域得分相差 ≥3 或结论互斥时自动触发，也可由用户手动触发。

### 6. Update（更新）

| 主题 | 触发词 |
|------|--------|
| **通用（始终可用）** | `update` |
| 所有主题 | 通用触发词 + 各自翻译（"更新" / "アップデート"） |

**触发结果**：执行当前平台的更新命令：
- Claude Code：`cd ~/.claude/skills/life_OS && git pull`
- Gemini / Codex：`npx skills add jasonhnd/life_OS`

### 7. Switch Theme（切换主题）

| 主题 | 触发词 |
|------|--------|
| **通用（始终可用）** | `switch theme` |
| 中文主题 | `切换主题` / `switch theme` |
| 日文主题 | `テーマ切り替え` / `switch theme` |

**触发结果**：系统重新显示 a/b/c/d/e/f/g/h/i 选择菜单，用户选后立即切换语言和角色名。

---

## 主题自动推断规则

用户首次输入时，若没有明确选择主题，ROUTER 会尝试自动推断：

### 1. 唯一主题触发词 → 直接载入该主题

| 触发词 | 推断主题 |
|--------|---------|
| `上朝` | 🏛️ 三省六部（唐朝专属词） |
| `朝堂议政` | 🏛️ 三省六部 |
| `御前会議` | 🏛️ 明治政府 |
| `convene`（英文古典语气词） | 优先 🏛️ Roman Republic |

检测到唯一主题触发词时，系统直接载入该主题，并回复 `🎨 Theme: 三省六部` / `🎨 テーマ: 明治政府` 等确认。

### 2. 语言专属但主题不唯一 → 展示该语言的分支选择

| 触发词 | 检测到的语言 | 展示分支 |
|--------|------------|---------|
| `开始` / `开会` | 中文 | d) 三省六部 / e) 中国政府 / f) 公司部门 |
| `はじめる` | 日语 | g) 明治政府 / h) 霞が関 / i) 企業 |
| `start` / `begin` | 英文 | a) Roman Republic / b) US Government / c) C-Suite |

### 3. 混合或不确定 → 展示完整 9 个主题选择

```
🎨 Choose your theme:

English:
  a) 🏛️ Roman Republic — Consul, Tribune, Senate
  b) 🇺🇸 US Government — Chief of Staff, Attorney General, Treasury
  c) 🏢 Corporate — CEO, General Counsel, CFO

中文：
  d) 🏛️ 三省六部 — 丞相、中书省、门下省
  e) 🇨🇳 中国政府 — 国务院、发改委、审计署
  f) 🏢 公司部门 — 总经理、法务部、财务部

日本語：
  g) 🏛️ 明治政府 — 内閣総理大臣、枢密院、大蔵省
  h) 🏛️ 霞が関 — 内閣官房長官、内閣法制局、財務省
  i) 🏢 企業 — 社長室、法務部、経理部

Type a-i
```

---

## 会话中切换主题

任意时刻用户说 `switch theme` / `切换主题` / `テーマ切り替え` 都可以切换：

1. 系统重新展示 a/b/c 选择菜单（当前主题会标注）
2. 用户选新主题 → 立即载入
3. **从这一刻起**输出语言立即切换到新主题的语言
4. 用**新语言**确认切换成功

## 主题决定输出语言（HARD RULE）

载入主题后，该会话的**所有输出**必须使用该主题的语言：
- zh-classical / zh-gov / zh-corp = **中文**
- ja-meiji / ja-kasumigaseki / ja-corp = **日语**
- en-roman / en-usgov / en-csuite = **英语**

适用于每个 agent、每份报告、每次回复。**不得混用、不得例外**。

---

## 触发词是如何被识别的

技术实现（供开发者参考）：

1. 每次用户输入进入 ROUTER
2. ROUTER 读取当前活跃主题的 `themes/{theme}.md`
3. 从 "Session Commands" 部分解析触发词
4. 对用户输入做字符串/模糊匹配
5. 若匹配 Start Session / Adjourn / Review → 执行 "Trigger Execution Templates (HARD RULE)" 中的固定模板
6. 若匹配 Quick Analysis / Debate / Update / Switch Theme → 执行对应简化流程
7. 若无匹配 → ROUTER 按普通请求处理（直接回应、Express Analysis 或 Escalate）

---

## 特殊情况

- **朝礼 vs 閣議開始**：日文主题中，`朝礼` 仅在 ja-corp（企業）中出现，`閣議開始` 同时存在于 ja-meiji 和 ja-kasumigaseki。系统无法从 `閣議開始` 区分明治和霞が関——默认载入霞が関（更常见），用户可手动切到明治
- **開会 / 开会** 跨主题重叠——中文三个主题的 Start Session 都可用，无法自动区分具体是哪个。系统会展示中文分支选项让用户选
- **"start" 极宽泛**——用户说"start"仅表示启动会话，不表示主题偏好。系统展示 a-i 完整选择
- 触发词不区分大小写，但建议使用文档中的原始大小写
